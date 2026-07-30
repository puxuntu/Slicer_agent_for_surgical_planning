"""Baseline comparison harness for the guided generated-CLI runtime.

Three alternative code producers can be substituted for ONE step of a running
workflow, so that step can be re-executed under a different condition and
compared against what the generated CLI template does:

``pure_llm``
    One bare LLM call. No dense retrieval, no search tools, no knowledge-base
    snippets, no generated extension CLI. The model gets a minimal system
    prompt, the current MRML scene summary, and the prompt the user typed.

``online_only``
    The full online agent -- dense pre-retrieval plus the built-in search tool
    loop (SearchSymbol / Grep / ReadFile / VectorSearch) plus scene context --
    with the generated extension CLI ablated. Neither the CLI tool schemas nor
    the CLI prompt fragments reach the model.

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
# ---------------------------------------------------------------------------

#: Deliberately minimal. The whole point of the pure-LLM condition is that the
#: model gets no Slicer-specific scaffolding beyond the output contract, so
#: this must NOT grow API hints, plan schemas or role protocols -- those all
#: live in Resources/Prompts/system_prompt.md, which this baseline bypasses.
PURE_LLM_SYSTEM_PROMPT = (
    "You are an expert 3D Slicer Python developer. You are operating inside a "
    "running 3D Slicer application.\n\n"
    "Answer with EXACTLY ONE fenced ```python block containing complete, "
    "self-contained, immediately executable Python that performs the requested "
    "task in the current Slicer session. `slicer`, `vtk`, `qt` and `ctk` are "
    "already imported and available.\n\n"
    "You have no tools and no documentation lookup: write the code from your "
    "own knowledge of the Slicer Python API. Do not ask questions, do not "
    "explain, do not emit any other fenced block."
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


def build_pure_llm_messages(
    prompt: str,
    scene: Optional[Dict[str, Any]] = None,
    step_context: str = "",
) -> List[Dict[str, str]]:
    """Build the two-message payload for the pure-LLM baseline.

    ``step_context`` is the workflow step's own description, included so the
    condition is told *which* step it is standing in for -- the same thing the
    generated CLI knows. It is plain prose, never a template or an API hint.
    """
    system = PURE_LLM_SYSTEM_PROMPT + format_scene_block(scene)
    user = str(prompt or "").strip()
    if step_context:
        user = f"Task step: {step_context}\n\n{user}" if user else f"Task step: {step_context}"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def build_online_only_messages(
    llm_client,
    prompt: str,
    context: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, str]]:
    """Build messages for the online-only baseline with the CLI ablated.

    Uses the production system prompt (so retrieval snippets, scene context and
    the agent_plan contract are all present) but with
    ``llm_client.suppress_extension_cli`` set, which drops the EXTENSION CLI
    TOOLS / EXTENSION SOURCE CODE / COOKBOOK-GUIDED WORKFLOW sections. The flag
    is restored in ``finally`` so a failure here cannot leak the ablation into
    the next normal turn.
    """
    previous = getattr(llm_client, "suppress_extension_cli", False)
    llm_client.suppress_extension_cli = True
    try:
        system = llm_client._buildSystemPrompt(context or {})
    finally:
        llm_client.suppress_extension_cli = previous
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": str(prompt or "").strip()},
    ]


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

#: Every baseline run is also appended here (one JSON object per line) so a
#: whole evaluation session can be collected from a single file instead of
#: walking every per-turn run folder.
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
        "code": code,
        "generation": {
            "seconds": generation.get("seconds"),
            "model": generation.get("model"),
            "provider": generation.get("provider"),
            "tokens": generation.get("tokens"),
            "cost": generation.get("cost"),
            "tool_rounds": generation.get("tool_rounds"),
            "tool_calls": generation.get("tool_calls"),
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
    """Write ``record`` into ``log_dir`` and append it to the session log.

    Returns the per-run file path (empty string when the write failed -- a
    recording failure must never abort the run being recorded).
    """
    path = ""
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
    except Exception:
        logger.warning("Failed to write baseline record", exc_info=True)
        path = ""

    if session_root:
        try:
            os.makedirs(session_root, exist_ok=True)
            with open(os.path.join(session_root, SESSION_LOG_NAME), "a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            logger.debug("Failed to append baseline session log", exc_info=True)

    return path
