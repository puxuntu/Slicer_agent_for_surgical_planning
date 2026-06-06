from __future__ import annotations

from .cache import *


def reset_workflow_state(extension_name: Optional[str] = None) -> None:
    """Clear accumulated workflow state so a workflow can be re-run cleanly.

    Args:
        extension_name: If provided, only clear state for that extension.
            If None, clear all workflow state.
    """
    if extension_name is not None:
        _workflow_completed_steps.pop(extension_name, None)
        _workflow_choices.pop(extension_name, None)
        _workflow_repeat_state.pop(extension_name, None)
    else:
        _workflow_completed_steps.clear()
        _workflow_choices.clear()
        _workflow_repeat_state.clear()
    try:
        from SlicerAIAgentLib.workflow_state import clear_workflow_state
        clear_workflow_state(extension_name)
    except Exception:
        logger.debug("Failed to clear generated workflow runtime state", exc_info=True)


def reset_workflow_session(extension_name: Optional[str] = None) -> None:
    """Public alias used by deterministic generated-CLI workflow runtime."""
    reset_workflow_state(extension_name)


def get_workflow_graph(extension_name: str) -> Dict:
    """Return the parsed workflow graph for a validated generated extension."""
    _ensure_cache()
    ext_data = _cli_cache.get(extension_name)
    if not ext_data:
        return {}
    workflow_path = os.path.join(ext_data["dir"], "workflow.json")
    if not os.path.isfile(workflow_path):
        return {}
    with open(workflow_path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_next_workflow_step(
    extension_name: str,
    completed_steps: Optional[set] = None,
) -> Optional[Dict]:
    """Return the next workflow step whose dependencies are satisfied."""
    graph = get_workflow_graph(extension_name)
    if not graph:
        return None
    completed = (
        set(completed_steps)
        if completed_steps is not None
        else set(_workflow_completed_steps.get(extension_name, set()))
    )
    return _find_next_step_local(graph, completed)


def mark_workflow_step_completed(extension_name: str, step_id: str) -> None:
    """Record a generated CLI workflow step as completed."""
    if not extension_name or not step_id:
        return
    _workflow_completed_steps.setdefault(extension_name, set()).add(step_id)


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
                "ui_guidance": step.get("ui_guidance", {}),
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
    metadata = ext_data.get("workflow_metadata", {}) or {}

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
        metadata=metadata,
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
