"""Runtime state helpers for generated extension CLI workflows.

Generated workflow templates execute as independent snippets.  This module
keeps the small amount of cross-snippet state that cannot safely live in a
Python global embedded in one generated code block.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

_interaction_nodes: Dict[Tuple[str, str, str, int], str] = {}


def _key(
    extension_name: str,
    workflow_id: str,
    step_id: str,
    repeat_index: Optional[int] = None,
) -> Tuple[str, str, str, int]:
    return (
        str(extension_name or ""),
        str(workflow_id or ""),
        str(step_id or ""),
        int(repeat_index or 0),
    )


def clear_workflow_state(extension_name: Optional[str] = None) -> None:
    """Clear generated workflow runtime state."""
    if not extension_name:
        _interaction_nodes.clear()
        return
    ext = str(extension_name)
    for key in list(_interaction_nodes):
        if key[0] == ext:
            _interaction_nodes.pop(key, None)


def remember_interaction_node(
    extension_name: str,
    workflow_id: str,
    step_id: str,
    node_id: str,
    repeat_index: Optional[int] = None,
) -> str:
    """Remember the MRML node ID produced for a workflow interaction step."""
    if node_id:
        _interaction_nodes[_key(extension_name, workflow_id, step_id, repeat_index)] = str(node_id)
    return str(node_id or "")


def get_interaction_node_id(
    extension_name: str,
    workflow_id: str,
    step_id: str,
    repeat_index: Optional[int] = None,
) -> str:
    """Return a remembered interaction node ID, or an empty string."""
    return _interaction_nodes.get(_key(extension_name, workflow_id, step_id, repeat_index), "")


def resolve_interaction_node(
    extension_name: str,
    workflow_id: str,
    step_id: str,
    node_class: str = "",
    repeat_index: Optional[int] = None,
):
    """Resolve a remembered MRML node and validate its class if requested."""
    node_id = get_interaction_node_id(extension_name, workflow_id, step_id, repeat_index)
    if not node_id:
        return None
    try:
        import slicer
        node = slicer.mrmlScene.GetNodeByID(node_id)
    except Exception:
        return None
    if node is None:
        return None
    if node_class and hasattr(node, "IsA") and not node.IsA(node_class):
        return None
    return node
