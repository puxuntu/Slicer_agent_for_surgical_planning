"""Baseline comparison harness for the guided generated-CLI runtime.

Three alternative code producers can be substituted for ONE step of a running
workflow, so that step can be re-executed under a different condition and
compared against what the generated CLI template does:

``pure_llm``
    One bare LLM call. No dense retrieval, no search tools, no knowledge-base
    snippets, no generated extension CLI. The model gets a comprehensive
    *situational* brief -- output contract, execution environment, the
    validator's blocked list, the live MRML scene, detailed properties of the
    nodes in play, and the step's own clinical description -- and must supply
    the Slicer API knowledge itself. Everything it is told is something a
    surgeon in front of the running application can see; nothing it is told is
    an answer or an artefact of the offline analysis.

``online_only``
    The full online agent -- dense pre-retrieval plus the built-in search tool
    loop (SearchSymbol / Grep / ReadFile / VectorSearch) plus scene context --
    with the generated extension CLI ablated. Neither the CLI tool schemas nor
    the CLI prompt fragments reach the model. It keeps the *raw* extension
    source trees under the ``ext:`` prefix and is told how to derive an API from
    them, because the ablation is of the offline ANALYSIS, not of the code base.

``claude_code``
    Code arrives over MCP from an external Claude Code session running the
    Slicer skill (see :mod:`SlicerAIAgentLib.BaselineMCPServer`). This module
    only records what came in; it does not call any model.

Everything here is Qt-free and free of scene side effects: it builds message
lists, ablates tool lists and serializes records. Execution, scene rewind and
step advancement stay in the widget so a baseline run reuses the exact same
CodeValidator -> SafeExecutor -> WorkflowRuntime path the real pipeline uses.
That shared tail is what makes the comparison a comparison: only the *code
producer* differs between conditions.
"""

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


MODE_PURE_LLM = "pure_llm"
MODE_ONLINE_ONLY = "online_only"
MODE_CLAUDE_CODE = "claude_code"

#: Ordered UI/report metadata for the three baselines.
#:
#: ``needs_prompt_box`` marks the modes where the user types the request into
#: the agent's own prompt box; the claude_code mode takes its prompt in the
#: external Claude Code session instead.
#:
#: ``send_label`` is what the shared Send button reads while that baseline is
#: selected -- the baseline harness drives the EXISTING prompt box + Send
#: button rather than duplicating them, so the button's caption is what tells
#: the user which producer Send will invoke. Two short lines, because the
#: button is ~80 px wide.
BASELINE_MODES = (
    {
        "id": MODE_PURE_LLM,
        "label": "1. Pure LLM (no grounding)",
        "needs_prompt_box": True,
        "send_label": "Run\nPure LLM",
        "description": (
            "One bare LLM call from the model's own knowledge. No retrieval, "
            "no search tools, no knowledge base, no generated CLI. The scene "
            "summary is included so the model can name the nodes it must act on."
        ),
    },
    {
        "id": MODE_ONLINE_ONLY,
        "label": "2. Online only (CLI ablated)",
        "needs_prompt_box": True,
        "send_label": "Run\nOnline",
        "description": (
            "The full online agent: dense pre-retrieval plus the built-in "
            "search tool loop over the Slicer knowledge base. The generated "
            "extension CLI is not loaded -- no CLI tools, no CLI prompt "
            "fragments."
        ),
    },
    {
        "id": MODE_CLAUDE_CODE,
        "label": "3. Claude Code + Slicer skill (MCP)",
        "needs_prompt_box": False,
        # NOT a "send" -- nothing is sent from here in this mode. The button
        # arms the step: it rewinds the scene to the pre-step state, opens the
        # step in the runtime, and attaches to the skill's execute_python. That
        # has to happen BEFORE Claude Code inspects the scene, which is why it
        # cannot be deferred until its code arrives.
        "send_label": "Arm\nthis step",
        "send_label_active": "Stop\nwaiting",
        "description": (
            "Set the skill up exactly as it documents (MCP section in the "
            "Claude Code config, --add-dir the skill directory, paste "
            "slicer-mcp-server.py into Slicer's Python console). Nothing is "
            "sent from this panel: 'Arm this step' rewinds the scene and "
            "attaches to that server, then you type the request in Claude Code "
            "and its code is executed here and advances the step."
        ),
    },
)

MODE_IDS = tuple(mode["id"] for mode in BASELINE_MODES)


def mode_info(mode_id: str) -> Dict[str, Any]:
    """Return the metadata dict for ``mode_id`` (empty dict when unknown)."""
    for mode in BASELINE_MODES:
        if mode["id"] == mode_id:
            return dict(mode)
    return {}


def mode_label(mode_id: str) -> str:
    return mode_info(mode_id).get("label", str(mode_id))


# ---------------------------------------------------------------------------
# Prompt construction
#
# No prompt text is written in this file. Every system prompt is loaded from
# Resources/Prompts (see SlicerAIAgentLib.PromptLibrary) so a prompt -- an
# experimental variable of this comparison -- can be edited, diffed and cited
# without touching code. The constants below are last-resort fallbacks used only
# if a prompt file is missing.
# ---------------------------------------------------------------------------

_PURE_LLM_FALLBACK = (
    "You are an expert 3D Slicer Python developer working inside a running 3D "
    "Slicer application. Answer with EXACTLY ONE fenced ```python block of "
    "complete, immediately executable code. `slicer`, `vtk`, `qt` and `ctk` are "
    "already imported. You have no tools: write the code from your own knowledge."
)

_ONLINE_ONLY_FALLBACK = (
    "## BASELINE CONDITION — NO GENERATED CLI\n"
    "The generated extension CLI is unavailable on this turn. Derive everything "
    "from source you search yourself, including the installed extensions' source "
    "trees under the `ext:` path prefix."
)


def pure_llm_system_prompt() -> str:
    """The pure-LLM baseline's system prompt, from Resources/Prompts."""
    from . import PromptLibrary
    return PromptLibrary.load(PromptLibrary.BASELINE_PURE_LLM_PROMPT, _PURE_LLM_FALLBACK)


def online_only_addendum(source_roots_block: str = "") -> str:
    """The online-only baseline's addendum, from Resources/Prompts."""
    from . import PromptLibrary
    return PromptLibrary.render(
        PromptLibrary.BASELINE_ONLINE_ONLY_PROMPT,
        fallback=_ONLINE_ONLY_FALLBACK,
        extension_source_roots=source_roots_block,
    )


# ---------------------------------------------------------------------------
# Step context
#
# What a baseline may be told about the step it is standing in for.
#
# The comparison is against the OFFLINE ANALYSIS pipeline, so the line is drawn
# there, not at "how much text". A baseline gets everything that describes the
# TASK and the WORLD -- the same things a surgeon following the tutorial in
# front of the running application has -- and nothing that is a product of the
# analysis, which is the artefact under test.
#
# Given (task + world):
#   step description and clinical guidance   the cookbook's own words
#   position in the procedure, what is done  observable from the panel
#   choices the user already made            observable
#   live MRML scene + node properties        observable from the running app
#   which extension the procedure concerns   observable
#
# Withheld (products of the offline analysis):
#   extension_method_hint / extension_function_hint
#   ui_parameter_binding / widget_name / widget_class / value_property
#   api_footprint, operation_model, node_roles, templates, tool schemas
#
# Handing over any of the second group would hand over the answer, and the
# numbers would stop meaning anything. TASK_STEP_KEYS is an ALLOW-list so a
# field added to workflow.json later defaults to withheld.
# ---------------------------------------------------------------------------

#: Keys of a workflow.json step that a baseline may see.
TASK_STEP_KEYS = ("step_id", "operation_type", "description")

#: Keys deliberately withheld, listed so the ablation is legible in review and
#: citable in the write-up rather than implicit in the code.
WITHHELD_STEP_KEYS = (
    "sub_operations", "extension_method_hint", "extension_function_hint",
    "ui_parameter_binding", "widget_name", "widget_class", "value_property",
    "operation_model", "node_roles", "operation_intents", "api_footprint",
    "choice_binding", "slicer_api_keywords", "setup_dependencies",
)

_SCENE_HEADER = (
    "## CURRENT SLICER SCENE\n"
    "The following JSON is a structured summary of every node currently in "
    "the Slicer scene. Each entry includes id, name, class, visibility and a "
    "one-line brief. Refer to nodes by these exact names/ids.\n"
)


def format_scene_block(scene: Optional[Dict[str, Any]]) -> str:
    """Serialize a scene summary the same way the production system prompt does."""
    if not scene:
        return ""
    try:
        body = json.dumps(scene, ensure_ascii=False, indent=2)
    except Exception:
        body = str(scene)
    return "\n\n" + _SCENE_HEADER + "```json\n" + body + "\n```\n"


def format_node_details_block(details: Optional[Dict[str, Any]]) -> str:
    """Detailed properties of the nodes this step is most likely to touch.

    The pipeline's own agent can call ``GetNodeProperties`` mid-turn; the
    pure-LLM condition has no tools and cannot, so the same information is
    pushed to it up front. Observable application state, not analysis.
    """
    if not details:
        return ""
    try:
        body = json.dumps(details, ensure_ascii=False, indent=2)
    except Exception:
        body = str(details)
    return (
        "\n\n## NODE DETAILS\n"
        "Full properties of the scene nodes most relevant to this step "
        "(dimensions, spacing, segment names, control points, transforms):\n"
        "```json\n" + body + "\n```\n"
    )


def build_step_brief(step: Optional[Dict[str, Any]]) -> str:
    """Prose brief of the step a baseline is standing in for.

    ``step`` is assembled by the widget from live runtime state; only the keys
    in TASK_STEP_KEYS are read out of the workflow graph itself.
    """
    if not step:
        return ""
    lines = ["## THE STEP YOU MUST PERFORM"]

    extension = str(step.get("extension") or "").strip()
    step_id = str(step.get("step_id") or "").strip()
    index, total = step.get("index"), step.get("total")
    where = f"step {index} of {total}" if index and total else "one step"
    if extension:
        lines.append(
            f"This is {where} of the **{extension}** surgical-planning procedure, "
            f"performed in 3D Slicer. The extension is installed and its module is "
            f"loaded in this session."
        )
    else:
        lines.append(f"This is {where} of a surgical-planning procedure in 3D Slicer.")
    if step_id:
        lines.append(f"Step id: `{step_id}`  ·  operation type: `{step.get('operation_type') or 'unknown'}`")

    description = str(step.get("description") or "").strip()
    if description:
        lines.append(f"\n**What the procedure says to do here:**\n> {description}")

    for label, key in (("Goal", "title"), ("In short", "simple"), ("Why", "detailed")):
        value = str(step.get(key) or "").strip()
        if value:
            lines.append(f"\n**{label}:** {value}")

    completed = step.get("completed") or []
    if completed:
        lines.append("\n**Already done in this run** (do not repeat these):")
        for entry in completed:
            if isinstance(entry, dict):
                text = str(entry.get("description") or entry.get("step_id") or "").strip()
                marker = str(entry.get("step_id") or "")
            else:
                text, marker = str(entry), ""
            if text:
                lines.append(f"- {marker + ': ' if marker else ''}{text}")

    choices = step.get("choices") or {}
    if choices:
        lines.append("\n**Values and nodes the user already chose in this run:**")
        for name, value in choices.items():
            lines.append(f"- `{name}` = {value!r}")

    remaining = step.get("remaining") or []
    if remaining:
        lines.append(
            "\n**Steps that come after this one** (context only — do NOT do them):"
        )
        for text in remaining:
            lines.append(f"- {text}")

    return "\n".join(lines) + "\n"


#: Filename the Claude Code condition reads its step brief from, inside the
#: MCPConnection workspace.
CLAUDE_CODE_BRIEF_NAME = "current_step.md"


def render_step_brief_document(step: Optional[Dict[str, Any]], armed_at: str = "") -> str:
    """The step brief as a standalone file for the Claude Code condition.

    The other two conditions get ``build_step_brief`` injected into their
    messages by the harness. Claude Code takes its prompt in an external session,
    so without this it would be the only condition working from the user's
    sentence alone -- roughly 1.8 KB of task context poorer than the other two,
    which would make any comparison against it meaningless.

    Same text, same allow-list, delivered as a file it can read instead of a
    message it is handed. Nothing here is an offline-analysis artefact (see
    TASK_STEP_KEYS); it is the task statement, not the answer.
    """
    brief = build_step_brief(step)
    if not brief:
        return (
            "# No step is currently armed\n\n"
            "Arm a step from the SlicerAIAgent panel (Baseline > Claude Code > "
            "**Arm this step**). This file is rewritten each time a step is armed.\n"
        )
    step = step or {}
    header = [
        "# Current step",
        "",
        "*Written by the SlicerAIAgent runtime when the step was armed. It is the "
        "**same brief** the other comparison conditions receive, so all conditions "
        "start from the same task context. Rewritten on every arm — check the step "
        "id below matches the request you were given.*",
        "",
        f"- **Extension:** `{step.get('extension', '?')}`",
        f"- **Step id:** `{step.get('step_id', '?')}`",
    ]
    if armed_at:
        header.append(f"- **Armed at:** {armed_at}")
    header += [
        "",
        "The live scene is *not* reproduced here — read it yourself with "
        "`list_nodes` and `get_node_properties`, which is fresher than any snapshot.",
        "",
        "---",
        "",
    ]
    return "\n".join(header) + brief


def build_pure_llm_messages(
    prompt: str,
    scene: Optional[Dict[str, Any]] = None,
    step: Optional[Dict[str, Any]] = None,
    node_details: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, str]]:
    """Build the two-message payload for the pure-LLM baseline.

    The system message carries everything the model cannot look up -- the output
    contract, the execution environment, the validator's blocked list, the live
    scene and the step brief -- because this condition has no tools and only one
    shot. What it does NOT carry is any Slicer API answer or any artefact of the
    offline analysis: the code still has to come from the model's own knowledge.
    """
    system = (
        pure_llm_system_prompt()
        + format_scene_block(scene)
        + format_node_details_block(node_details)
    )
    brief = build_step_brief(step)
    user = str(prompt or "").strip()
    if brief:
        user = f"{brief}\n{user}" if user else brief
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def build_online_only_messages(
    llm_client,
    prompt: str,
    context: Optional[Dict[str, Any]] = None,
    step: Optional[Dict[str, Any]] = None,
    source_roots_block: str = "",
) -> List[Dict[str, str]]:
    """Build messages for the online-only baseline with the CLI ablated.

    Uses the production system prompt (so retrieval snippets, scene context and
    the agent_plan contract are all present) but with
    ``llm_client.suppress_extension_cli`` set, which drops the EXTENSION CLI
    TOOLS / EXTENSION SOURCE CODE / COOKBOOK-GUIDED WORKFLOW sections. The flag
    is restored in ``finally`` so a failure here cannot leak the ablation into
    the next normal turn.

    The ablated CLI section is then replaced by the online-only addendum, which
    re-states what this condition *does* keep: the raw extension source trees
    (searchable, and not an analysis product) plus a search recipe for deriving
    an extension's API from them. Ablating the analysis must not silently also
    ablate the code base -- the whole point of this condition is that it searches
    the code base for itself.
    """
    previous = getattr(llm_client, "suppress_extension_cli", False)
    llm_client.suppress_extension_cli = True
    try:
        system = llm_client._buildSystemPrompt(context or {})
    finally:
        llm_client.suppress_extension_cli = previous

    system += "\n\n" + online_only_addendum(source_roots_block)
    brief = build_step_brief(step)
    if brief:
        system += "\n\n" + brief

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": str(prompt or "").strip()},
    ]


def extension_source_roots_block() -> str:
    """Bullet list of the installed extension source trees, for the `ext:` prefix.

    Derived from the loader registry because that is where the search roots are
    registered (see ``LogicCoreMixin._initializeComponents``). Only the module
    name and its path are exposed -- no manifest analysis, no logic-class
    shortcut, no workflow graph.
    """
    try:
        from SlicerAIAgentLib.ExtensionCLILoader import get_validated_extensions
        import os as _os
        lines = []
        for ext_name, ext_data in sorted(get_validated_extensions().items()):
            source_path = (ext_data.get("manifest") or {}).get("source_path", "")
            if source_path and _os.path.isdir(source_path):
                lines.append(f"- `ext:{ext_name}/` — source of the **{ext_name}** extension")
        return "\n".join(lines)
    except Exception:
        logger.debug("Could not enumerate extension source roots", exc_info=True)
        return ""


# ---------------------------------------------------------------------------
# Tool ablation
# ---------------------------------------------------------------------------

def _tool_name(tool: Any) -> str:
    """Read a tool schema's name for both OpenAI and flat shapes."""
    if not isinstance(tool, dict):
        return ""
    function = tool.get("function")
    if isinstance(function, dict) and function.get("name"):
        return str(function["name"])
    return str(tool.get("name", ""))


def generated_cli_tool_names() -> set:
    """Names of every tool contributed by a generated extension CLI."""
    try:
        from SlicerAIAgentLib.ExtensionCLILoader import get_dynamic_extension_tools
        return {_tool_name(tool) for tool in get_dynamic_extension_tools() or [] if _tool_name(tool)}
    except Exception:
        logger.debug("Could not enumerate generated CLI tools", exc_info=True)
        return set()


def strip_generated_cli_tools(tools: Optional[List[Dict]]) -> List[Dict]:
    """Return ``tools`` without any schema contributed by a generated CLI.

    Ablation by identity, not by name pattern: the excluded set comes from the
    loader itself, so it stays correct for any extension that is added later.
    """
    if not tools:
        return []
    excluded = generated_cli_tool_names()
    if not excluded:
        return list(tools)
    return [tool for tool in tools if _tool_name(tool) not in excluded]


# ---------------------------------------------------------------------------
# Records
# ---------------------------------------------------------------------------

#: Historical: baseline records used to ALSO be appended to a single
#: ``logs/baseline_runs.jsonl``. That file was byte-identical duplication of the
#: per-run record, and — worse for the comparison — it covered only the three
#: baselines, so a "whole session in one file" that silently omitted the system
#: under test invited analysing whichever three conditions were convenient.
#:
#: The aggregate view is now DERIVED instead of written: ``scripts/collect_runs.py``
#: walks ``logs/`` and emits one row per (run, step) across all four conditions.
#: Deriving it cannot drift from the folders the way a second live writer could.
#: The name is kept only so an existing file is recognisable.
SESSION_LOG_NAME = "baseline_runs.jsonl"


def scene_delta(before: Optional[Dict], after: Optional[Dict]) -> Dict[str, Any]:
    """Compact before/after difference from two ``buildSceneSnapshot`` dicts."""
    if not isinstance(before, dict) or not isinstance(after, dict):
        return {}

    def _ids(snapshot):
        return {
            node.get("id")
            for node in snapshot.get("nodes", []) or []
            if isinstance(node, dict) and node.get("id")
        }

    def _names(snapshot, ids):
        return sorted(
            str(node.get("name") or node.get("id"))
            for node in snapshot.get("nodes", []) or []
            if isinstance(node, dict) and node.get("id") in ids
        )

    before_ids, after_ids = _ids(before), _ids(after)
    created, removed = after_ids - before_ids, before_ids - after_ids
    return {
        "node_count_before": len(before_ids),
        "node_count_after": len(after_ids),
        "created_nodes": _names(after, created),
        "removed_nodes": _names(before, removed),
        "layout_before": before.get("layout"),
        "layout_after": after.get("layout"),
    }


def build_record(
    mode: str,
    extension_name: str,
    step_id: str,
    prompt: str,
    code: str,
    execution: Optional[Dict[str, Any]] = None,
    generation: Optional[Dict[str, Any]] = None,
    delta: Optional[Dict[str, Any]] = None,
    error: str = "",
    attempt: int = 1,
    transport: str = "",
    step_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Assemble one baseline run record (JSON-serializable).

    ``attempt`` counts tries within one baseline of one step. Only the Claude
    Code condition can exceed 1: its MCP endpoint stays armed after a failure so
    the external agent can iterate, and every attempt is recorded separately so
    the number of tries is visible rather than averaged away.
    """
    execution = execution or {}
    generation = generation or {}
    return {
        "schema": "slicer_ai_agent.baseline_run/1",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "epoch": round(time.time(), 3),
        "mode": mode,
        "mode_label": mode_label(mode),
        "extension": extension_name,
        "step_id": step_id,
        "attempt": int(attempt),
        # How the code reached us. Only the Claude Code condition has one; it
        # is recorded so a reader never has to infer which MCP server was used.
        "transport": transport,
        "prompt": prompt,
        # The task/world brief this condition was given. Recorded in full so a
        # reader can check exactly what the baseline knew, and confirm that no
        # offline-analysis artefact was among it (see TASK_STEP_KEYS).
        "step_context": step_context or {},
        "code": code,
        "generation": {
            "seconds": generation.get("seconds"),
            "model": generation.get("model"),
            "provider": generation.get("provider"),
            "tokens": generation.get("tokens"),
            "cost": generation.get("cost"),
            "tool_rounds": generation.get("tool_rounds"),
            "tool_calls": generation.get("tool_calls"),
            # Characters of prompt actually sent, so context size is comparable
            # across conditions rather than inferred from the token count.
            "prompt_chars": generation.get("prompt_chars"),
            "message": generation.get("message"),
        },
        "execution": {
            "attempted": bool(execution),
            "success": execution.get("success"),
            "timed_out": execution.get("timed_out"),
            "seconds": execution.get("execution_time"),
            "output": (execution.get("output") or "")[:8000],
            "error": (execution.get("error") or "")[:4000],
        },
        "scene_delta": delta or {},
        "error": error,
        "advanced": bool(execution.get("success")) and not execution.get("timed_out"),
    }


def write_record(log_dir: str, record: Dict[str, Any], session_root: str = "") -> str:
    """Write ``record`` into ``log_dir``.

    One copy, in the run's own folder — whose name already says which condition,
    procedure, step and attempt it is. ``session_root`` is accepted and ignored
    (see SESSION_LOG_NAME): a second live writer of the same bytes could only
    ever drift from this one.

    Returns the file path (empty string when the write failed -- a recording
    failure must never abort the run being recorded).
    """
    try:
        os.makedirs(log_dir, exist_ok=True)
        stamp = time.strftime("%H%M%S")
        # The attempt number keeps two failures within the same second apart.
        name = (
            f"baseline_{record.get('step_id', 'step')}_{record.get('mode', 'mode')}"
            f"_a{record.get('attempt', 1)}_{stamp}.json"
        )
        path = os.path.join(log_dir, name)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(record, handle, ensure_ascii=False, indent=2)
        return path
    except Exception:
        logger.warning("Failed to write baseline record", exc_info=True)
        return ""
