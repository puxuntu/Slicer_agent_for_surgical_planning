from __future__ import annotations

from .cache import *


class _WorkflowContext:
    """Bundles all state needed by a per-type step handler."""
    __slots__ = (
        "ext_name", "ext_dir", "tool_name", "workflow_graph",
        "target_step", "target_gen", "arguments", "user_action", "done",
        "metadata",
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
        metadata: Optional[Dict] = None,
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
        self.metadata = metadata or {}

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
    code = _prepend_choice_prelude(ctx, code)

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
        "ui_guidance": _ui_guidance_for_context(ctx),
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
    node_vars = {
        name for name in node_var_re.findall(code)
        if name != "_workflow_runtime_id"
    }
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
        post_code = _prepend_choice_prelude(ctx, post_code)

    repeat_result = _handle_repeat_after_interaction(ctx)
    if repeat_result:
        repeat_result["post_code"] = post_code
        repeat_result["code"] = post_code
        repeat_result["instruction"] = (
            "Execute the post-interaction code above. "
            + repeat_result["instruction"]
        )
        return repeat_result

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
    pre_code = _prepend_choice_prelude(ctx, pre_code)

    interaction_desc = ctx.target_gen.get("interaction_descriptor", {})
    ui_guidance = _ui_guidance_for_context(ctx, interaction_desc)
    repeat_progress = _repeat_progress_for_context(ctx)
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
            "When the user clicks the workflow Done button or otherwise confirms completion, call this tool again with "
            f"workflow_step='{ctx.workflow_step}' user_action='proceed'. "
            "Do NOT call any more tools until the user confirms they are done."
        ),
        "interaction_instructions": interaction_desc.get("placement_instructions", ""),
        "ui_guidance": ui_guidance,
        "repeat_progress": repeat_progress,
        "interaction_type": _NC_MAP.get(nc, "generic"),
        "step_id": ctx.workflow_step,
        "explanation": ctx.target_step.get("description", ""),
        "display_properties": ctx.target_step.get("display_properties"),
        "interaction": interaction_desc,
    }


def _normalize_branch_value(value):
    """Coerce a Yes/No answer to a bool when possible (mirrors
    WorkflowRuntime._normalize_control_value), else return it stripped."""
    if isinstance(value, str):
        low = value.strip().lower()
        if low in ("true", "yes", "y", "1"):
            return True
        if low in ("false", "no", "n", "0"):
            return False
        return value.strip()
    return value


def _branch_choice_accepts(ctx: _WorkflowContext, choice_value) -> bool:
    """True when the branch_op decision ACCEPTS (runs the optional body / performs
    the action) -- i.e. NOT the decline answer. Mirrors the inverse of
    WorkflowRuntime._loop_should_exit: decline when the value equals the guard's
    ``choice_info.default_value`` (the skip answer); for a boolean guard with no
    default, the negative/No answer declines. So both the handler-side action gate
    and the runtime-side branch routing read the same polarity."""
    info = ctx.target_step.get("choice_info", {}) or {}
    norm = _normalize_branch_value(choice_value)
    default = info.get("default_value")
    if default is not None:
        return norm != _normalize_branch_value(default)
    return norm is not False


def _maybe_attach_branch_action(ctx: _WorkflowContext, result: Dict) -> Dict:
    """On ACCEPT, append the branch_op's captured extension action (e.g. tick the
    checkbox that enables the optional mode) to the choice result's ``code`` so it
    runs before the body. On DECLINE, leave the result code-less (no action)."""
    if not isinstance(result, dict):
        return result
    if not _branch_choice_accepts(ctx, result.get("choice_value")):
        return result
    tpl_rel = ctx.target_step.get("branch_action_template", "")
    if not tpl_rel:
        return result  # no captured action -> plain pre-guard branch
    tpl_path = os.path.join(ctx.ext_dir, tpl_rel)
    if not os.path.isfile(tpl_path):
        return result
    try:
        with open(tpl_path, "r", encoding="utf-8") as f:
            action_code = f.read()
    except Exception:
        return result
    try:
        action_code = _fill_template(action_code, _build_format_kwargs(ctx.arguments))
    except KeyError:
        pass
    action_code = _prepend_choice_prelude(ctx, action_code)
    existing = result.get("code") or ""
    result["code"] = (existing + "\n\n" + action_code) if existing else action_code
    result["instruction"] = (
        "STOP. Do NOT make any more tool calls. Your NEXT response must be an "
        "```agent_plan JSON block followed by a ```python block containing the "
        "'code' field above VERBATIM. Do NOT call any more tools until this code "
        "has been executed."
    )
    return result


def _handle_branch_step(ctx: _WorkflowContext) -> Dict:
    """branch_op: present/record the Yes/No decision exactly like a user_choice,
    then on ACCEPT attach the captured extension action (the on-accept tick). The
    pre-guard repeat_block in WorkflowRuntime routes accept->body / decline->
    jump/stop, reading the same choice_value this handler records."""
    result = _handle_user_choice_step(ctx)
    if ctx.user_action == "choice_made":
        result = _maybe_attach_branch_action(ctx, result)
    return result


def _handle_user_choice_step(ctx: _WorkflowContext) -> Dict:
    """Handle a user_choice workflow step."""
    choice_desc = ctx.target_gen.get("choice_descriptor", {}) if ctx.target_gen else {}
    ui_guidance = _ui_guidance_for_context(ctx, choice_desc)
    question = choice_desc.get("question", ctx.target_step.get("description", "Please make a selection:"))
    choices = choice_desc.get("choices", [])
    param_name = choice_desc.get("parameter_name", "")
    default = choice_desc.get("default_value")

    if ctx.user_action == "choice_made":
        choice_value = ctx.arguments.get("choice_value", default or "")
        binding = (
            choice_desc.get("binding")
            or ctx.target_step.get("choice_binding")
            or ctx.metadata.get("choice_bindings", {}).get(ctx.workflow_step, {})
        )
        if binding and binding.get("parameter_name"):
            _workflow_choices.setdefault(ctx.ext_name, {})[binding["parameter_name"]] = choice_value
        return _record_choice_and_advance(ctx, param_name, choice_value)

    if ctx.user_action == "proceed":
        # Interactive scene-manipulation choice (e.g. a qMRMLSegmentsTableView where
        # the user toggled per-segment visibility directly on the scene). There is
        # no value to record; advance the workflow with an empty choice value, which
        # emits no parameter/node code and proceeds to the next step.
        return _record_choice_and_advance(ctx, param_name, "")

    # Node/option selection is always manual — no automatic node matching.
    # Initial start — return the question/choices for the panel to present.
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
        "ui_guidance": ui_guidance,
        "binding": (
            choice_desc.get("binding")
            or ctx.target_step.get("choice_binding")
            or ctx.metadata.get("choice_bindings", {}).get(ctx.workflow_step, {})
        ),
        "node_class": (
            (
                choice_desc.get("binding")
                or ctx.target_step.get("choice_binding")
                or ctx.metadata.get("choice_bindings", {}).get(ctx.workflow_step, {})
            ) or {}
        ).get("node_class", ""),
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
        # Choice selection is always manual: execute the auto code, then present
        # the choice (no automatic node matching).
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
    binding = (
        choice_desc.get("binding")
        or ctx.target_step.get("choice_binding")
        or ctx.metadata.get("choice_bindings", {}).get(ctx.workflow_step, {})
    )
    if binding and binding.get("parameter_name"):
        _workflow_choices.setdefault(ctx.ext_name, {})[binding["parameter_name"]] = choice_value
    return _record_choice_and_advance(ctx, param_name, choice_value)


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

    pre_code = "\n\n".join(pre_code_parts) if pre_code_parts else None
    return _prepend_choice_prelude(ctx, pre_code)


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
        post_code = _prepend_choice_prelude(ctx, post_code)

    repeat_result = _handle_repeat_after_interaction(ctx)
    if repeat_result:
        repeat_result["post_code"] = post_code
        repeat_result["code"] = post_code
        repeat_result["instruction"] = (
            "Execute the post-interaction code above. "
            + repeat_result["instruction"]
        )
        return repeat_result

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
        "ui_guidance": _ui_guidance_for_context(ctx, choice_desc),
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
    ui_guidance = _ui_guidance_for_context(ctx, interaction_desc)
    repeat_progress = _repeat_progress_for_context(ctx)
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
            "described in 'interaction_instructions' and click Done when finished. "
            f"When the user says they are done, call this tool again with "
            f"workflow_step='{ctx.workflow_step}' user_action='proceed'. "
            "Do NOT call any more tools until the user confirms they are done."
        ),
        "interaction_instructions": interaction_instructions,
        "ui_guidance": ui_guidance,
        "repeat_progress": repeat_progress,
        "interaction_type": interaction_type,
        "step_id": ctx.workflow_step,
        "explanation": ctx.target_step.get("description", ""),
        "display_properties": ctx.target_step.get("display_properties"),
        "sub_operations": sub_ops,
        "interaction": interaction_desc,
    }
