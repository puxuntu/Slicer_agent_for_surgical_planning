"""
ExtensionCLILoader - Auto-discovery and dynamic loading of extension CLI tools.

Scans Resources/extension_CLI/*/ for generated extension tool definitions,
loads their schemas, code templates, and prompt fragments at runtime,
and dispatches tool calls from the LLM to the appropriate code generator.
"""

import json
import logging
import os
import threading
from typing import Any, Callable, Dict, List, Optional

try:
    import slicer
except ImportError:
    slicer = None

logger = logging.getLogger(__name__)

# Module-level cache: {extension_name: {"manifest": ..., "schemas": ..., "generators": ..., ...}}
_cli_cache: Dict[str, Dict] = {}
_cache_valid = False
_cache_lock = threading.Lock()


def get_cli_base_dir() -> str:
    """Return the path to Resources/extension_CLI/."""
    module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(module_dir, "Resources", "extension_CLI")


def _ensure_cache():
    """Populate the CLI cache by scanning the extension_CLI directory."""
    global _cache_valid, _cli_cache
    if _cache_valid:
        return

    with _cache_lock:
        # Double-check after acquiring the lock
        if _cache_valid:
            return

        base_dir = get_cli_base_dir()
        if not os.path.isdir(base_dir):
            logger.info("No extension_CLI directory found at %s", base_dir)
            _cache_valid = True
            return

        for entry in os.listdir(base_dir):
            ext_dir = os.path.join(base_dir, entry)
            if not os.path.isdir(ext_dir):
                continue

            manifest_path = os.path.join(ext_dir, "manifest.json")
            if not os.path.isfile(manifest_path):
                continue

            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)

                status = manifest.get("status", "unknown")
                if status != "validated":
                    logger.info(
                        "Skipping %s (status=%s, not validated)", entry, status
                    )
                    continue

                schemas_path = os.path.join(ext_dir, "tool_schemas.json")
                generators_path = os.path.join(ext_dir, "code_generators.json")
                prompt_path = os.path.join(ext_dir, "prompt_fragment.md")

                schemas = []
                if os.path.isfile(schemas_path):
                    with open(schemas_path, "r", encoding="utf-8") as f:
                        schemas = json.load(f)

                generators = []
                if os.path.isfile(generators_path):
                    with open(generators_path, "r", encoding="utf-8") as f:
                        generators = json.load(f)

                prompt_fragment = ""
                if os.path.isfile(prompt_path):
                    with open(prompt_path, "r", encoding="utf-8") as f:
                        prompt_fragment = f.read()

                _cli_cache[entry] = {
                    "manifest": manifest,
                    "schemas": schemas,
                    "generators": generators,
                    "prompt_fragment": prompt_fragment,
                    "dir": ext_dir,
                }

                tool_names = [s.get("function", {}).get("name", "?") for s in schemas]
                logger.info(
                    "Loaded extension CLI: %s (tools=%s)", entry, tool_names
                )

            except Exception as e:
                logger.warning("Failed to load extension CLI %s: %s", entry, e)

        _cache_valid = True


def invalidate_cache():
    """Force a cache refresh on the next access."""
    global _cache_valid
    with _cache_lock:
        _cache_valid = False
        _cli_cache.clear()


def get_validated_extensions() -> Dict[str, Dict]:
    """Return the full cache of validated extension CLI data."""
    _ensure_cache()
    return dict(_cli_cache)


def get_dynamic_extension_tools() -> List[Dict]:
    """Return tool schemas from all validated extension CLIs."""
    _ensure_cache()
    tools = []
    for ext_data in _cli_cache.values():
        tools.extend(ext_data["schemas"])
    return tools


def get_extension_prompt_fragments() -> str:
    """Return concatenated prompt fragments from all validated extension CLIs."""
    _ensure_cache()
    fragments = []
    for ext_name, ext_data in _cli_cache.items():
        fragment = ext_data.get("prompt_fragment", "").strip()
        if fragment:
            fragments.append(fragment)
    return "\n\n".join(fragments)


def dispatch_extension_cli_tool(tool_name: str, arguments: Dict) -> Optional[Dict]:
    """
    Dispatch a tool call to the appropriate extension CLI code generator.

    Returns a result dict with 'tool', 'code', 'instruction', 'explanation' keys,
    or None if the tool_name is not found in any extension CLI.
    """
    _ensure_cache()

    for ext_name, ext_data in _cli_cache.items():
        for schema in ext_data["schemas"]:
            func_info = schema.get("function", {})
            if func_info.get("name") != tool_name:
                continue

            # Found the matching tool — generate code from template
            return _generate_from_template(
                ext_name, ext_data, tool_name, arguments
            )

    return None

def _fill_template(template_str: str, kwargs: Dict[str, str]) -> str:
    """Fill a template supporting both {name} and {name: default_value} syntax.

    - {name}: replaced with kwargs[name], KeyError if missing
    - {name: default}: replaced with kwargs[name] if present, else default
    - {{ and }} are preserved as literal braces
    - Brace pairs inside Python string/f-string literals are left untouched

    Uses a character-by-character scanner with brace-depth tracking to
    correctly handle nested braces in default values (e.g.
    ``{param: {"key": "val"}}``).
    """
    import re

    # Phase 1: Mask out Python string literals so braces inside them are
    # left untouched.  Handles single/double/triple-quoted strings with
    # optional f/r/b prefixes.
    string_ranges = []
    for m in re.finditer(
        r'(?:[fFrRbBuU]{0,2})("""|\'\'\'|"|\')(.*?)\1',
        template_str, re.DOTALL,
    ):
        string_ranges.append((m.start(), m.end()))

    def _in_string(pos):
        return any(s <= pos < e for s, e in string_ranges)

    # Phase 2: Protect escaped double-braces by replacing them with sentinels.
    sentinel_l = "\x00LBRACE\x00"
    sentinel_r = "\x00RBRACE\x00"
    buf = template_str.replace("{{", sentinel_l).replace("}}", sentinel_r)

    # Phase 3: Walk the buffer character-by-character.  When we find a
    # ``{`` that is NOT inside a string literal, scan forward tracking brace
    # depth until we find the matching ``}``.  Then try to parse the content
    # as a placeholder and replace it.
    result_parts = []
    i = 0
    n = len(buf)

    while i < n:
        ch = buf[i]

        # Skip masked string literals entirely
        if _in_string(i):
            # Find the end of this string range and emit it verbatim
            in_any = False
            for s, e in string_ranges:
                if s <= i < e:
                    result_parts.append(buf[i:e])
                    i = e
                    in_any = True
                    break
            if in_any:
                continue

        if ch != '{':
            result_parts.append(ch)
            i += 1
            continue

        # We have a '{'.  Scan forward to find the matching '}' using
        # brace-depth tracking so nested braces in defaults are handled.
        depth = 0
        j = i
        found = False
        while j < n:
            c = buf[j]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    found = True
                    break
            j += 1

        if not found:
            # No matching '}' — emit the '{' literally and move on.
            result_parts.append(ch)
            i += 1
            continue

        # Extract the content between the outermost braces.
        inner = buf[i + 1 : j]

        # Try to parse as a placeholder:  name  or  name: default
        colon_pos = inner.find(":")
        if colon_pos >= 0 and inner[:colon_pos].strip().isidentifier():
            name = inner[:colon_pos].strip()
            default = inner[colon_pos + 1:]  # everything after ":"
            # Strip one leading space from default for readability: {n: val} → val
            if default.startswith(" "):
                default = default[1:]
        elif inner.strip().isidentifier():
            name = inner.strip()
            default = None
        else:
            # Not a valid placeholder — emit the original text literally.
            result_parts.append(buf[i : j + 1])
            i = j + 1
            continue

        # Perform replacement
        if name in kwargs:
            result_parts.append(kwargs[name])
        elif default is not None:
            result_parts.append(default)
        else:
            raise KeyError(name)

        i = j + 1

    # Phase 4: Restore escaped braces
    out = "".join(result_parts)
    out = out.replace(sentinel_l, "{").replace(sentinel_r, "}")
    return out


def _generate_from_template(
    ext_name: str,
    ext_data: Dict,
    tool_name: str,
    arguments: Dict,
) -> Dict:
    """
    Fill a code template with the provided arguments and return the result dict.
    Always delegates to dispatch_workflow_step for cookbook-driven workflows.
    """
    return dispatch_workflow_step(ext_name, ext_data, tool_name, arguments)


# Track completed/skipped steps per workflow so the skip handler can compute
# the next step without needing a reference to the WorkflowOrchestrator.
_workflow_completed_steps: Dict[str, set] = {}

# Store user_choice selections keyed by (extension_name, parameter_name)
_workflow_choices: Dict[str, Dict[str, str]] = {}


def reset_workflow_state(extension_name: Optional[str] = None) -> None:
    """Clear accumulated workflow state so a workflow can be re-run cleanly.

    Args:
        extension_name: If provided, only clear state for that extension.
            If None, clear all workflow state.
    """
    if extension_name is not None:
        _workflow_completed_steps.pop(extension_name, None)
        _workflow_choices.pop(extension_name, None)
    else:
        _workflow_completed_steps.clear()
        _workflow_choices.clear()


def _find_next_step_local(
    workflow_graph: Dict, completed: set
) -> Optional[Dict]:
    """Find the next workflow step whose dependencies are all completed."""
    for step in workflow_graph.get("steps", []):
        sid = step.get("step_id", "")
        if sid in completed:
            continue
        deps = step.get("depends_on", [])
        if all(d in completed for d in deps):
            is_optional = (
                step.get("step_type") == "branch"
                or step.get("is_optional", False)
            )
            return {
                "step_id": sid,
                "step_type": step.get("step_type", "automated"),
                "description": step.get("description", ""),
                "is_optional": is_optional,
            }
    return None


def dispatch_workflow_step(
    ext_name: str,
    ext_data: Dict,
    tool_name: str,
    arguments: Dict,
) -> Dict:
    """
    Dispatch a tool call for an interactive workflow extension.

    Reads the workflow.json, matches the requested step, and delegates to
    the appropriate per-type handler.

    Returns:
        Dict with type-specific fields:
        - type: "interactive" | "automated" | "branch" | "error"
        - For interactive: pre_code, interaction descriptor, instructions
        - For automated: code, instruction
        - For branch: condition, branches
    """
    ext_dir = ext_data["dir"]
    generators = ext_data["generators"]

    # Load workflow graph
    workflow_path = os.path.join(ext_dir, "workflow.json")
    if not os.path.isfile(workflow_path):
        return {"error": f"workflow.json not found for {ext_name}"}

    with open(workflow_path, "r", encoding="utf-8") as f:
        workflow_graph = json.load(f)

    # Get requested step and action
    workflow_step = arguments.get("workflow_step", "")
    user_action = arguments.get("user_action", "start")

    if user_action == "cancel":
        return {
            "tool": tool_name,
            "type": "cancelled",
            "message": "Workflow cancelled.",
        }

    # Find the matching step
    target_step = None
    for step in workflow_graph.get("steps", []):
        if step["step_id"] == workflow_step:
            target_step = step
            break

    if not target_step:
        available = [s["step_id"] for s in workflow_graph.get("steps", [])]
        return {
            "error": f"Unknown workflow step '{workflow_step}'. Available: {available}",
        }

    step_type = target_step.get("step_type", "automated")

    # Track step completion for the local next-step resolver.
    # When start/proceed is called, the current step's depends_on are all done.
    # Add them to the completed set so subsequent skip calls can compute
    # the correct next step.
    done = _workflow_completed_steps.setdefault(ext_name, set())
    for dep in target_step.get("depends_on", []):
        done.add(dep)

    # Find the matching generator entry
    target_gen = None
    for gen in generators:
        gen_step = gen.get("param_signature", {}).get("workflow_step", "")
        if gen_step == workflow_step:
            target_gen = gen
            break

    # Handle skip uniformly for all step types
    if user_action == "skip":
        return _handle_skip(
            ext_name, tool_name, workflow_step, workflow_graph, done,
        )

    # Delegate to per-type handler
    ctx = _WorkflowContext(
        ext_name=ext_name,
        ext_dir=ext_dir,
        tool_name=tool_name,
        workflow_graph=workflow_graph,
        target_step=target_step,
        target_gen=target_gen,
        arguments=arguments,
        user_action=user_action,
        done=done,
    )

    handlers = {
        "automated": _handle_automated_step,
        "interactive": _handle_interactive_step,
        "branch": _handle_branch_step,
        "user_choice": _handle_user_choice_step,
        "mixed": _handle_mixed_step,
    }
    handler = handlers.get(step_type)
    if handler:
        return handler(ctx)

    return {"error": f"Unknown step type: {step_type}"}


# =====================================================================
# Shared helpers used by the per-type handlers
# =====================================================================

def _build_format_kwargs(arguments: Dict) -> Dict[str, str]:
    """Convert tool arguments to template format kwargs (repr-wrapped)."""
    format_kwargs = {}
    for key, value in arguments.items():
        if isinstance(value, str):
            format_kwargs[key] = repr(value)
        elif value is None:
            format_kwargs[key] = "None"
        else:
            format_kwargs[key] = repr(value)
    return format_kwargs


def _build_next_step_instruction(tool_name: str, next_step: Optional[Dict], prefix: str = "") -> str:
    """Build the standard 'next step' instruction string."""
    if not next_step:
        return f"{prefix}All steps complete. Workflow is done." if prefix else "All steps complete. Workflow is done."
    is_opt = next_step.get("is_optional", False)
    if is_opt:
        return (
            f"{prefix}"
            f"Next step '{next_step['step_id']}' is optional: "
            f"{next_step['description']} "
            f"Ask the user if they want to proceed. "
            f"If yes, call {tool_name} with workflow_step='{next_step['step_id']}' user_action='start'. "
            f"If no, call with workflow_step='{next_step['step_id']}' user_action='skip'."
        )
    return (
        f"{prefix}"
        f"Proceed by calling {tool_name} with "
        f"workflow_step='{next_step['step_id']}' user_action='start'."
    )


class _WorkflowContext:
    """Bundles all state needed by a per-type step handler."""
    __slots__ = (
        "ext_name", "ext_dir", "tool_name", "workflow_graph",
        "target_step", "target_gen", "arguments", "user_action", "done",
    )

    def __init__(
        self,
        ext_name: str,
        ext_dir: str,
        tool_name: str,
        workflow_graph: Dict,
        target_step: Dict,
        target_gen: Optional[Dict],
        arguments: Dict,
        user_action: str,
        done: set,
    ):
        self.ext_name = ext_name
        self.ext_dir = ext_dir
        self.tool_name = tool_name
        self.workflow_graph = workflow_graph
        self.target_step = target_step
        self.target_gen = target_gen
        self.arguments = arguments
        self.user_action = user_action
        self.done = done

    @property
    def workflow_step(self) -> str:
        return self.target_step["step_id"]


# =====================================================================
# Per-type step handlers
# =====================================================================

def _handle_skip(
    ext_name: str,
    tool_name: str,
    workflow_step: str,
    workflow_graph: Dict,
    done: set,
) -> Dict:
    """Handle user_action='skip' — mark step done and report next step."""
    done.add(workflow_step)
    next_step = _find_next_step_local(workflow_graph, done)
    result = {
        "tool": tool_name,
        "type": "skipped",
        "step_id": workflow_step,
        "message": f"Step '{workflow_step}' skipped.",
    }
    if next_step:
        result["next_step"] = next_step
        result["instruction"] = _build_next_step_instruction(tool_name, next_step)
    else:
        result["instruction"] = "All remaining optional steps have been handled. Workflow is complete."
    return result


def _handle_automated_step(ctx: _WorkflowContext) -> Dict:
    """Handle an automated workflow step — fill and return the code template."""
    if not ctx.target_gen:
        return {"error": f"No generator for automated step '{ctx.workflow_step}'"}

    template_rel = ctx.target_gen.get("template_file", "")
    template_path = os.path.join(ctx.ext_dir, template_rel)
    if not os.path.isfile(template_path):
        return {"error": f"Template not found: {template_rel}"}

    with open(template_path, "r", encoding="utf-8") as f:
        template_str = f.read()

    format_kwargs = _build_format_kwargs(ctx.arguments)

    try:
        code = _fill_template(template_str, format_kwargs)
    except KeyError as e:
        return {"error": f"Template placeholder not filled: {e}"}

    return {
        "tool": ctx.tool_name,
        "type": "automated",
        "code": code,
        "instruction": (
            "STOP. Do NOT make any more tool calls. "
            "Your NEXT response must be an ```agent_plan JSON block followed by a ```python block "
            "containing the 'code' field above VERBATIM. "
            "Do NOT call any more tools until this code has been executed."
        ),
        "explanation": ctx.target_step.get("description", ""),
        "step_id": ctx.workflow_step,
        "display_properties": ctx.target_step.get("display_properties"),
    }


def _handle_interactive_step(ctx: _WorkflowContext) -> Dict:
    """Handle an interactive workflow step (pre/post interaction templates)."""
    if not ctx.target_gen:
        return {"error": f"No generator for interactive step '{ctx.workflow_step}'"}

    # Handle "proceed" — user completed interaction, run post-template and advance
    if ctx.user_action == "proceed":
        return _handle_interactive_proceed(ctx)

    # "start" — return pre-interaction code for the LLM to output
    return _handle_interactive_start(ctx)


def _inject_node_id_fallback(code: str, workflow_step: str) -> str:
    """Inject NameError fallbacks for node ID variables in post-code.

    If a post-template references _ext_step_id but the pre-template never
    defined it, the code would crash with NameError.  This safety net prepends
    a try/except block that falls back to a scene search by node name.
    """
    if not code:
        return code
    import re as _re
    node_var_re = _re.compile(r'(_\w+_\w+_id)')
    node_vars = set(node_var_re.findall(code))
    if not node_vars:
        return code
    step_name = workflow_step.replace("_", " ").title()
    injections = []
    for nv in sorted(node_vars):
        injections.append(
            f"try:\n"
            f"    {nv}\n"
            f"except NameError:\n"
            f"    {nv} = ''\n"
            f"    try:\n"
            f"        _n = slicer.util.getNode('{step_name}')\n"
            f"        if _n:\n"
            f"            {nv} = _n.GetID()\n"
            f"    except Exception:\n"
            f"        pass\n"
        )
    prefix = (
        "# [Runtime safety] Fallback for missing node ID variables\n"
        + "\n".join(injections) + "\n\n"
    )
    return prefix + code


def _handle_interactive_proceed(ctx: _WorkflowContext) -> Dict:
    """Handle user_action='proceed' for an interactive step."""
    ctx.done.add(ctx.workflow_step)

    # Read and fill post-interaction template
    post_template_rel = ctx.target_gen.get("post_template_file", "")
    post_code = None
    if post_template_rel:
        post_template_path = os.path.join(ctx.ext_dir, post_template_rel)
        if os.path.isfile(post_template_path):
            with open(post_template_path, "r", encoding="utf-8") as f:
                post_template = f.read()
            format_kwargs = _build_format_kwargs(ctx.arguments)
            try:
                post_code = _fill_template(post_template, format_kwargs)
            except KeyError as e:
                return {"error": f"Post-template placeholder not filled: {e}"}

    # Safety net: inject NameError fallbacks for missing node ID variables
    if post_code:
        post_code = _inject_node_id_fallback(post_code, ctx.workflow_step)

    next_step = _find_next_step_local(ctx.workflow_graph, ctx.done)
    result = {
        "tool": ctx.tool_name,
        "type": "interactive_done",
        "step_id": ctx.workflow_step,
        "post_code": post_code,
        "code": post_code,
    }
    result["instruction"] = _build_next_step_instruction(
        ctx.tool_name, next_step, prefix="Execute the post-interaction code above. "
    )
    if next_step:
        result["next_step"] = next_step
    return result


def _handle_interactive_start(ctx: _WorkflowContext) -> Dict:
    """Handle user_action='start' for an interactive step."""
    pre_template_rel = ctx.target_gen.get("pre_template_file", "")
    pre_template = None
    if pre_template_rel:
        pre_template_path = os.path.join(ctx.ext_dir, pre_template_rel)
        if os.path.isfile(pre_template_path):
            with open(pre_template_path, "r", encoding="utf-8") as f:
                pre_template = f.read()

    if pre_template:
        format_kwargs = _build_format_kwargs(ctx.arguments)
        try:
            pre_code = _fill_template(pre_template, format_kwargs)
        except KeyError as e:
            return {"error": f"Pre-template placeholder not filled: {e}"}
    else:
        pre_code = None

    interaction_desc = ctx.target_gen.get("interaction_descriptor", {})
    nc = interaction_desc.get("node_class", "")
    _NC_MAP = {
        "vtkMRMLMarkupsCurveNode": "curve",
        "vtkMRMLMarkupsPlaneNode": "plane",
        "vtkMRMLMarkupsLineNode": "line",
        "vtkMRMLMarkupsFiducialNode": "fiducial",
    }

    return {
        "tool": ctx.tool_name,
        "type": "interactive",
        "pre_code": pre_code,
        "code": pre_code,
        "instruction": (
            "STOP. Do NOT make any more tool calls. "
            "Your NEXT response must be an ```agent_plan JSON block followed by a ```python block "
            "containing the 'code' field above VERBATIM. "
            "After the code executes, tell the user to perform the interaction "
            "described in 'interaction_instructions'. "
            "When the user says they are done (e.g., types 'done'), call this tool again with "
            f"workflow_step='{ctx.workflow_step}' user_action='proceed'. "
            "Do NOT call any more tools until the user confirms they are done."
        ),
        "interaction_instructions": interaction_desc.get("placement_instructions", ""),
        "interaction_type": _NC_MAP.get(nc, "generic"),
        "step_id": ctx.workflow_step,
        "explanation": ctx.target_step.get("description", ""),
        "display_properties": ctx.target_step.get("display_properties"),
    }


def _handle_branch_step(ctx: _WorkflowContext) -> Dict:
    """Handle a branch (optional) workflow step."""
    condition = ctx.target_step.get("condition", "Optional step")
    return {
        "tool": ctx.tool_name,
        "type": "branch",
        "step_id": ctx.workflow_step,
        "condition": condition,
        "branches": ctx.target_step.get("branches", {}),
        "explanation": ctx.target_step.get("description", ""),
        "instruction": (
            f"Ask the user: '{condition}' "
            f"If yes, call {ctx.tool_name} with workflow_step='{ctx.workflow_step}' "
            f"user_action='start'. "
            f"If no, call with workflow_step='{ctx.workflow_step}' "
            f"user_action='skip'."
        ),
    }


def _handle_user_choice_step(ctx: _WorkflowContext) -> Dict:
    """Handle a user_choice workflow step."""
    choice_desc = ctx.target_gen.get("choice_descriptor", {}) if ctx.target_gen else {}
    question = choice_desc.get("question", ctx.target_step.get("description", "Please make a selection:"))
    choices = choice_desc.get("choices", [])
    param_name = choice_desc.get("parameter_name", "")
    default = choice_desc.get("default_value")

    if ctx.user_action == "choice_made":
        choice_value = ctx.arguments.get("choice_value", default or "")
        # Store the choice
        ext_choices = _workflow_choices.setdefault(ctx.ext_name, {})
        if param_name:
            ext_choices[param_name] = choice_value
        # Mark step complete and find next
        ctx.done.add(ctx.workflow_step)
        next_step = _find_next_step_local(ctx.workflow_graph, ctx.done)
        result = {
            "tool": ctx.tool_name,
            "type": "choice_made",
            "step_id": ctx.workflow_step,
            "parameter_name": param_name,
            "choice_value": choice_value,
            "message": f"User selected '{choice_value}' for '{param_name}'.",
        }
        result["instruction"] = _build_next_step_instruction(ctx.tool_name, next_step)
        if next_step:
            result["next_step"] = next_step
        return result

    # Initial start — return the question for the LLM to relay
    options_text = "\n".join(
        f"  {i+1}. {c['label']}" for i, c in enumerate(choices)
    )
    return {
        "tool": ctx.tool_name,
        "type": "user_choice",
        "step_id": ctx.workflow_step,
        "question": question,
        "choices": choices,
        "parameter_name": param_name,
        "default_value": default,
        "instruction": (
            f"Ask the user: '{question}'\n"
            f"Options:\n{options_text}\n"
            f"Wait for the user's response, then call {ctx.tool_name} with "
            f"workflow_step='{ctx.workflow_step}' user_action='choice_made' "
            f"and choice_value='<selected value>'."
        ),
        "explanation": ctx.target_step.get("description", ""),
    }


def _handle_mixed_step(ctx: _WorkflowContext) -> Dict:
    """Handle a mixed (automated + interaction/choice) workflow step."""
    if not ctx.target_gen:
        return {"error": f"No generator for mixed step '{ctx.workflow_step}'"}

    # Determine mixed sub-type: interaction vs choice
    interaction_desc = ctx.target_gen.get("interaction_descriptor", {})
    choice_desc = ctx.target_gen.get("choice_descriptor", {})
    # Use sub_operations as the authoritative signal for user interaction,
    # NOT interaction_type (which may be null for non-markup interactions
    # like slice crosshair adjustment).
    sub_ops = ctx.target_gen.get("sub_operations",
                ctx.target_step.get("sub_operations", []))
    has_interaction = any(
        so.get("op_type") == "user_interaction" for so in sub_ops
    )
    has_choice = bool(choice_desc.get("question"))

    # Handle choice_made for mixed+choice steps
    if ctx.user_action == "choice_made":
        return _handle_mixed_choice_made(ctx, choice_desc)

    # Build pre_code from automated sub-operation templates
    pre_code = _build_mixed_pre_code(ctx)

    # Handle "proceed" for mixed+interaction — user completed 3D interaction
    if ctx.user_action == "proceed" and has_interaction:
        return _handle_mixed_interaction_proceed(ctx, pre_code)

    if has_choice and not has_interaction:
        # Mixed auto+choice: execute auto code, then present choice
        return _build_mixed_choice_response(ctx, pre_code, choice_desc)

    # Pure-automated mixed step (no interaction, no choice) — treat as automated.
    # This handles cases where the pipeline classified a step as "mixed" but
    # all sub-operations are automated (e.g. extension_op + slicer_op).
    if not has_interaction and not has_choice:
        ctx.done.add(ctx.workflow_step)
        next_step = _find_next_step_local(ctx.workflow_graph, ctx.done)
        result = {
            "tool": ctx.tool_name,
            "type": "automated",
            "code": pre_code,
            "step_id": ctx.workflow_step,
            "explanation": ctx.target_step.get("description", ""),
        }
        result["instruction"] = _build_next_step_instruction(ctx.tool_name, next_step)
        if next_step:
            result["next_step"] = next_step
        logger.info(
            "[ExtensionCLILoader] Mixed step '%s' has no interaction/choice — "
            "dispatching as automated", ctx.workflow_step,
        )
        return result

    # Mixed auto+interaction: execute auto code, then wait for 3D interaction
    return _build_mixed_interaction_response(ctx, pre_code, interaction_desc)


def _handle_mixed_choice_made(ctx: _WorkflowContext, choice_desc: Dict) -> Dict:
    """Handle user_action='choice_made' for a mixed step."""
    param_name = choice_desc.get("parameter_name", "")
    default = choice_desc.get("default_value")
    choice_value = ctx.arguments.get("choice_value", default or "")
    ext_choices = _workflow_choices.setdefault(ctx.ext_name, {})
    if param_name:
        ext_choices[param_name] = choice_value
    ctx.done.add(ctx.workflow_step)
    next_step = _find_next_step_local(ctx.workflow_graph, ctx.done)
    result = {
        "tool": ctx.tool_name,
        "type": "choice_made",
        "step_id": ctx.workflow_step,
        "parameter_name": param_name,
        "choice_value": choice_value,
        "message": f"User selected '{choice_value}' for '{param_name}'.",
    }
    result["instruction"] = _build_next_step_instruction(ctx.tool_name, next_step)
    if next_step:
        result["next_step"] = next_step
    return result


def _build_mixed_pre_code(ctx: _WorkflowContext) -> Optional[str]:
    """Build pre_code from automated sub-operation templates for a mixed step."""
    pre_code_parts = []
    sub_ops = ctx.target_step.get("sub_operations", [])
    for so in sub_ops:
        if so.get("op_type") in ("extension_op", "slicer_op"):
            tpl_file = so.get("code_template", "")
            if tpl_file:
                tpl_path = os.path.join(ctx.ext_dir, tpl_file)
                if os.path.isfile(tpl_path):
                    with open(tpl_path, "r", encoding="utf-8") as f:
                        pre_code_parts.append(f"# [{so['op_type']}] {so.get('description', '')}\n{f.read()}")

    # Also use pre_template_file if available (cookbook-generated)
    pre_template_rel = ctx.target_gen.get("pre_template_file", "")
    if pre_template_rel and not pre_code_parts:
        pre_template_path = os.path.join(ctx.ext_dir, pre_template_rel)
        if os.path.isfile(pre_template_path):
            with open(pre_template_path, "r", encoding="utf-8") as f:
                pre_code_parts.append(f.read())

    return "\n\n".join(pre_code_parts) if pre_code_parts else None


def _handle_mixed_interaction_proceed(ctx: _WorkflowContext, pre_code: Optional[str]) -> Dict:
    """Handle user_action='proceed' for a mixed+interaction step."""
    ctx.done.add(ctx.workflow_step)

    # Read post-template
    post_template_rel = ctx.target_gen.get("post_template_file", "")
    post_code = None
    if post_template_rel:
        post_template_path = os.path.join(ctx.ext_dir, post_template_rel)
        if os.path.isfile(post_template_path):
            with open(post_template_path, "r", encoding="utf-8") as f:
                post_template = f.read()
            format_kwargs = _build_format_kwargs(ctx.arguments)
            try:
                post_code = _fill_template(post_template, format_kwargs)
            except KeyError as e:
                return {"error": f"Post-template placeholder not filled: {e}"}

    # Safety net: inject NameError fallbacks for missing node ID variables
    if post_code:
        post_code = _inject_node_id_fallback(post_code, ctx.workflow_step)

    next_step = _find_next_step_local(ctx.workflow_graph, ctx.done)
    result = {
        "tool": ctx.tool_name,
        "type": "mixed_done",
        "step_id": ctx.workflow_step,
        "post_code": post_code,
        "code": post_code,
    }
    result["instruction"] = _build_next_step_instruction(
        ctx.tool_name, next_step, prefix="Execute the post-interaction code above. "
    )
    if next_step:
        result["next_step"] = next_step
    return result


def _build_mixed_choice_response(
    ctx: _WorkflowContext, pre_code: Optional[str], choice_desc: Dict,
) -> Dict:
    """Build the response for a mixed auto+choice step (initial start)."""
    question = choice_desc.get("question", "")
    choices = choice_desc.get("choices", [])
    param_name = choice_desc.get("parameter_name", "")
    default = choice_desc.get("default_value", "")
    sub_ops = ctx.target_step.get("sub_operations", [])

    return {
        "tool": ctx.tool_name,
        "type": "mixed",
        "pre_code": pre_code,
        "code": pre_code,
        "instruction": (
            "Execute the code above, then ask the user the following question "
            "and wait for their response. "
            f"Call this tool again with workflow_step='{ctx.workflow_step}' "
            f"user_action='choice_made' and choice_value='<selected value>'."
        ),
        "question": question,
        "choices": choices,
        "parameter_name": param_name,
        "default_value": default,
        "step_id": ctx.workflow_step,
        "explanation": ctx.target_step.get("description", ""),
        "sub_operations": sub_ops,
    }


def _build_mixed_interaction_response(
    ctx: _WorkflowContext, pre_code: Optional[str], interaction_desc: Dict,
) -> Dict:
    """Build the response for a mixed auto+interaction step (initial start)."""
    sub_ops = ctx.target_step.get("sub_operations", [])
    interaction_instructions = interaction_desc.get("placement_instructions", "")
    node_class = interaction_desc.get("node_class", "")

    # If no interaction_descriptor from generator, check sub_operations
    if not interaction_instructions:
        for so in sub_ops:
            if so.get("op_type") == "user_interaction":
                interaction_instructions = so.get("placement_instructions") or so.get("description", "")
                node_class = so.get("node_class", "") or node_class
                break

    # Derive interaction_type from node_class for display
    _NC_MAP = {
        "vtkMRMLMarkupsCurveNode": "curve",
        "vtkMRMLMarkupsPlaneNode": "plane",
        "vtkMRMLMarkupsLineNode": "line",
        "vtkMRMLMarkupsFiducialNode": "fiducial",
    }
    interaction_type = _NC_MAP.get(node_class, "generic")

    return {
        "tool": ctx.tool_name,
        "type": "mixed",
        "pre_code": pre_code,
        "code": pre_code,
        "instruction": (
            "STOP. Do NOT make any more tool calls. "
            "Your NEXT response must be an ```agent_plan JSON block followed by a ```python block "
            "containing the 'code' field above VERBATIM. "
            "After the code executes, tell the user to perform the interaction "
            "described in 'interaction_instructions' and type 'done' in the chat when finished. "
            f"When the user says they are done, call this tool again with "
            f"workflow_step='{ctx.workflow_step}' user_action='proceed'. "
            "Do NOT call any more tools until the user confirms they are done."
        ),
        "interaction_instructions": interaction_instructions,
        "interaction_type": interaction_type,
        "step_id": ctx.workflow_step,
        "explanation": ctx.target_step.get("description", ""),
        "display_properties": ctx.target_step.get("display_properties"),
        "sub_operations": sub_ops,
    }


def get_workflow_choice(ext_name: str, parameter_name: str) -> Optional[str]:
    """Retrieve a stored user_choice value for a workflow."""
    return _workflow_choices.get(ext_name, {}).get(parameter_name)


def get_all_workflow_choices(ext_name: str) -> Dict[str, str]:
    """Retrieve all stored user_choice values for a workflow."""
    return dict(_workflow_choices.get(ext_name, {}))


def get_all_cli_manifests() -> List[Dict]:
    """Return all extension CLI manifests (for UI display)."""
    _ensure_cache()
    results = []
    for ext_name, ext_data in _cli_cache.items():
        manifest = ext_data["manifest"].copy()
        manifest["cli_dir"] = ext_data["dir"]
        results.append(manifest)

    # Also scan for non-validated CLIs
    base_dir = get_cli_base_dir()
    if os.path.isdir(base_dir):
        for entry in os.listdir(base_dir):
            if entry in _cli_cache:
                continue
            ext_dir = os.path.join(base_dir, entry)
            manifest_path = os.path.join(ext_dir, "manifest.json")
            if os.path.isfile(manifest_path):
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        m = json.load(f)
                    m["cli_dir"] = ext_dir
                    results.append(m)
                except Exception:
                    pass
    return results


def delete_cli(extension_name: str) -> bool:
    """Delete an extension CLI directory."""
    import shutil

    base_dir = get_cli_base_dir()
    ext_dir = os.path.join(base_dir, extension_name)
    if os.path.isdir(ext_dir):
        shutil.rmtree(ext_dir)
        invalidate_cache()
        logger.info("Deleted extension CLI: %s", extension_name)
        return True
    return False


def discover_installed_extensions() -> List[Dict]:
    """
    Discover Slicer extensions from the Extension Manager, additional module
    paths, and loaded scripted modules.

    Returns a list of dicts with:
    - name: extension display name
    - module_name: Python module name
    - install_path: file system path to the extension root
    - source_path: file system path usable for source analysis
    - has_python: whether the extension has Python modules
    - cli_status: 'validated', 'draft', 'failed', or None
    """
    results = []
    seen = set()

    def _add(name, install_path, source_path, source_type="extension_manager"):
        if name in seen:
            return
        seen.add(name)

        has_python = False
        if os.path.isdir(source_path):
            for root, _dirs, files in os.walk(source_path):
                if any(f.endswith(".py") for f in files):
                    has_python = True
                break

        cli_status = None
        cli_dir = os.path.join(get_cli_base_dir(), name)
        manifest_path = os.path.join(cli_dir, "manifest.json")
        if os.path.isfile(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    m = json.load(f)
                cli_status = m.get("status")
            except Exception:
                pass

        results.append({
            "name": name,
            "module_name": name,
            "install_path": install_path,
            "source_path": source_path,
            "has_python": has_python,
            "cli_status": cli_status,
            "source_type": source_type,
        })

    # 1. Extensions installed via Extension Manager
    try:
        em = slicer.app.extensionsManagerModel()
        for ext_name in em.installedExtensions:
            install_path = em.extensionInstallPath(ext_name)
            _add(ext_name, install_path, install_path)
    except Exception as e:
        logger.warning("Failed to scan Extension Manager: %s", e)

    # 2. Additional module paths (loaded via Edit > Application Settings > Modules)
    try:
        settings = slicer.app.revisionUserSettings()
        raw_value = settings.value("Modules/AdditionalPaths")
        if raw_value is None:
            additionalPaths = []
        elif isinstance(raw_value, str):
            additionalPaths = [raw_value]
        elif isinstance(raw_value, (list, tuple)):
            additionalPaths = list(raw_value)
        else:
            additionalPaths = []

        # Convert relative paths to absolute
        absolute_paths = []
        for p in additionalPaths:
            abs_p = slicer.app.toSlicerHomeAbsolutePath(p)
            absolute_paths.append(abs_p)

        for mod_path in absolute_paths:
            if not os.path.isdir(mod_path):
                continue
            # Each additional path may point to a module directory directly,
            # or to a parent containing multiple module directories.
            if any(f.endswith(".py") for f in os.listdir(mod_path)):
                ext_name = os.path.basename(mod_path)
                _add(ext_name, mod_path, mod_path, source_type="additional_paths")
            else:
                # Scan subdirectories for extension-like folders
                for entry in os.listdir(mod_path):
                    subdir = os.path.join(mod_path, entry)
                    if not os.path.isdir(subdir):
                        continue
                    for f in os.listdir(subdir):
                        if f.endswith(".py"):
                            _add(entry, subdir, subdir, source_type="additional_paths")
                            break
    except Exception as e:
        logger.warning("Failed to scan additional module paths: %s", e)

    # 3. Loaded scripted modules (fallback — catches everything that's loaded)
    try:
        loaded_modules = slicer.util.moduleNames()
        for module_name in loaded_modules:
            if module_name in seen:
                continue
            try:
                mod_path = slicer.util.modulePath(module_name)
                if not mod_path or not os.path.isfile(mod_path):
                    continue
                module_dir = os.path.dirname(mod_path)
                parent_dir = os.path.dirname(module_dir)
                _add(module_name, parent_dir, module_dir, source_type="loaded_modules")
            except Exception:
                continue
    except Exception as e:
        logger.warning("Failed to scan loaded modules: %s", e)

    return results


def save_cli_package(
    extension_name: str,
    manifest: Dict,
    tool_schemas: List[Dict],
    code_generators: List[Dict],
    templates: Dict[str, str],
    prompt_fragment: str,
    generation_log_entry: Optional[Dict] = None,
) -> str:
    """
    Save a complete extension CLI package to disk.

    Args:
        extension_name: Name for the CLI directory
        manifest: Manifest dict (will be written as manifest.json)
        tool_schemas: List of OpenAI tool schema dicts
        code_generators: List of generator metadata dicts
        templates: Dict mapping template_file names to template content strings
        prompt_fragment: Markdown prompt fragment
        generation_log_entry: Optional entry to append to generation_log.json

    Returns:
        Path to the created CLI directory
    """
    # Validate extension name (prevent path traversal)
    if not extension_name or not extension_name.strip():
        raise ValueError("Extension name must not be empty.")
    if any(ch in extension_name for ch in ("/", "\\", "\x00")):
        raise ValueError(f"Invalid extension name '{extension_name}': contains path separators.")
    if ".." in extension_name:
        raise ValueError(f"Invalid extension name '{extension_name}': contains '..' traversal.")
    extension_name = extension_name.strip()

    base_dir = get_cli_base_dir()
    os.makedirs(base_dir, exist_ok=True)

    ext_dir = os.path.join(base_dir, extension_name)
    os.makedirs(ext_dir, exist_ok=True)
    os.makedirs(os.path.join(ext_dir, "templates"), exist_ok=True)

    # Write manifest
    with open(os.path.join(ext_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # Write tool schemas
    with open(os.path.join(ext_dir, "tool_schemas.json"), "w", encoding="utf-8") as f:
        json.dump(tool_schemas, f, indent=2, ensure_ascii=False)

    # Write code generators
    with open(os.path.join(ext_dir, "code_generators.json"), "w", encoding="utf-8") as f:
        json.dump(code_generators, f, indent=2, ensure_ascii=False)

    # Write templates
    for tpl_name, tpl_content in templates.items():
        if tpl_name == "workflow.json":
            # Workflow graph goes at CLI root, not in templates/
            tpl_path = os.path.join(ext_dir, tpl_name)
        else:
            # tpl_name may already include "templates/" prefix — strip it
            clean_name = tpl_name.removeprefix("templates/")
            tpl_path = os.path.join(ext_dir, "templates", clean_name)
        os.makedirs(os.path.dirname(tpl_path), exist_ok=True)
        with open(tpl_path, "w", encoding="utf-8") as f:
            f.write(tpl_content)

    # Write prompt fragment
    with open(os.path.join(ext_dir, "prompt_fragment.md"), "w", encoding="utf-8") as f:
        f.write(prompt_fragment)

    # Append generation log entry
    if generation_log_entry:
        log_path = os.path.join(ext_dir, "generation_log.json")
        log_entries = []
        if os.path.isfile(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    log_entries = json.load(f)
            except Exception:
                pass
        log_entries.append(generation_log_entry)
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log_entries, f, indent=2, ensure_ascii=False)

    # Invalidate cache so the new CLI is picked up
    invalidate_cache()

    logger.info("Saved extension CLI package: %s", ext_dir)
    return ext_dir
