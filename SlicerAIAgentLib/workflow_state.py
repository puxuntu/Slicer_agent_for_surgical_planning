"""Runtime state helpers for generated extension CLI workflows.

Generated workflow templates execute as independent snippets.  This module
keeps the small amount of cross-snippet state that cannot safely live in a
Python global embedded in one generated code block.
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

#: Last line of the hidden prelude every dispatched step is prefixed with, and
#: therefore the exact boundary between what the RUNTIME injected and what the
#: TEMPLATE contains.
#:
#: It exists because that boundary has to be found again later. A runtime
#: self-correction is fixed against the dispatched code -- prelude included --
#: and persisting the fix back into the .tpl means removing the prelude first:
#: it carries ``_workflow_runtime_id``, which names ONE run. The boundary used
#: to be guessed by scanning for the template's own ``import slicer`` line,
#: which silently fails for any template that does not have one (a template may
#: rely on ``slicer`` already being bound in ``__main__``, and several do). The
#: write-back then refuses -- correctly, since baking in a run id is worse --
#: and the same step self-corrects again on every future run.
#:
#: Emitted in ONE place (``choice_helpers._prepend_choice_prelude``, the single
#: funnel every dispatch path goes through) and consumed in one place
#: (``widget_execution_flow._stripRuntimePrelude``). Kept here because this
#: module is already the neutral ground between them -- the prelude imports it.
PRELUDE_END_MARKER = "# [Workflow runtime] end of injected prelude -- template body follows"

_interaction_nodes: Dict[Tuple[str, str, str, int], str] = {}


def strip_runtime_prelude(code: str) -> Optional[str]:
    """Drop the runtime-injected workflow prelude, leaving template content.

    The prelude (metadata-apply, hidden runtime globals, input guard) is
    re-added fresh on every dispatch, so it must never be baked into the
    saved template -- it carries `_workflow_runtime_id`, which identifies ONE
    run. Only acts when a distinctive prelude marker is present (the
    corrected code is sometimes already prelude-free).

    Two ways to find the boundary, in this order:

    1. ``PRELUDE_END_MARKER`` -- emitted as the prelude's last line by
       ``choice_helpers._prepend_choice_prelude``. Exact, and independent of
       anything the template happens to contain.
    2. The template's own first Slicer import -- the original heuristic,
       kept for corrected code produced before the marker existed. Broader
       than an exact ``import slicer`` because a repair may rewrite the
       import line (adding vtk, a trailing comment) without that meaning the
       prelude is gone.

    The heuristic alone is what made this necessary: it silently fails for
    any template with no ``import slicer`` line -- and a template may rely on
    ``slicer`` already being bound in ``__main__``, as
    PelvicFracturePlanning's ``cb_step_3_slicer`` does (it opens with
    ``import math``). The write-back then refused on every run, so that step
    self-corrected, advanced, and threw the fix away, forever.

    Returns ``None`` when a prelude IS present and NEITHER resolves. That
    case used to return the code unchanged, which is how a shipped
    CranialImplantPlanning template ended up with
    ``_workflow_runtime_id = 'CranialImplantPlanning_1786919982267'`` at the
    top: the strip silently became a no-op and the whole prelude was
    persisted. Refusing is still the right answer for that case -- the fix
    applies to the run in progress, and the next run regenerates the prelude
    correctly from a clean template.
    """
    markers = (
        "# [Workflow metadata] Apply source-derived defaults",
        "# [Workflow runtime] Hidden generated-CLI workflow context",
        "# [Workflow preconditions]",
        PRELUDE_END_MARKER,
    )
    if not any(m in code for m in markers):
        return code
    # split("\n"), not splitlines(): the latter drops the trailing newline (so the
    # recovered body never equalled the template it came from) and also breaks on
    # \v, \f and \x1c-\x1e, which are ordinary characters inside a string literal.
    lines = code.split("\n")
    # LAST occurrence, not the first: a correction that quotes the failing
    # code inside a comment or docstring would otherwise cut at the quote and
    # keep the real prelude below it.
    for i in range(len(lines) - 1, -1, -1):
        if PRELUDE_END_MARKER in lines[i]:
            return "\n".join(lines[i + 1:])
    for i, line in enumerate(lines):
        stripped = line.strip()
        if (stripped == "import slicer"
                or stripped.startswith("import slicer ")
                or stripped.startswith("import slicer,")
                or stripped.startswith("import slicer #")
                or stripped.startswith("from slicer ")):
            return "\n".join(lines[i:])
    return None


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


def prune_missing_interaction_nodes(extension_name: Optional[str] = None) -> None:
    """Drop remembered interaction nodes whose MRML node no longer exists.

    Called after a replay rewind restores an earlier scene state, which
    removes nodes created by later (now-discarded) steps. Keeping the
    interaction-node memory consistent with the live scene stops the
    placement guard from re-arming on a deleted node. Fail-open.
    """
    try:
        import slicer
    except Exception:
        return
    ext = str(extension_name) if extension_name else None
    for key in list(_interaction_nodes):
        if ext is not None and key[0] != ext:
            continue
        node_id = _interaction_nodes.get(key)
        try:
            missing = not node_id or slicer.mrmlScene.GetNodeByID(node_id) is None
        except Exception:
            missing = True
        if missing:
            _interaction_nodes.pop(key, None)


def latest_interaction_node_for_step(
    step_id: str,
    extension_name: str = "",
    workflow_id: str = "",
    node_class: str = "",
):
    """Most recently remembered MRML node for a step, across iterations.

    Scoped to the session the caller names. ``_interaction_nodes`` is keyed by
    (extension, workflow_id, step, repeat_index), but this lookup used to match
    on the step id ALONE -- and every generated package numbers its steps
    ``cb_step_N``, so ``cb_step_12`` of one procedure would return the markup
    node another procedure's ``cb_step_12`` created. The keys outlive their run
    (a normal completion does not touch them, and ``start_for_extension`` resets
    only its OWN extension's keys), so the wrong node was reachable whenever a
    second, different procedure ran in the same session.

    Used by the runtime placement guard: when an interactive markup step is
    waiting for the user but Slicer is no longer in place mode (a post
    template, an extension callback, or a layout rebuild dropped it), the
    guard re-arms placement on this node. Returns None when nothing is
    remembered, the node is gone, or it is not of ``node_class``.

    An empty ``extension_name`` / ``workflow_id`` means "do not filter on it",
    so a caller with no session in hand keeps the old, wider behaviour.
    """
    step = str(step_id or "")
    if not step:
        return None
    ext = str(extension_name or "")
    wid = str(workflow_id or "")
    node_id = ""
    for key, value in _interaction_nodes.items():  # insertion order = recency
        if key[2] != step:
            continue
        if ext and key[0] != ext:
            continue
        if wid and key[1] != wid:
            continue
        node_id = value
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


# =====================================================================
# Workflow metadata + precondition helpers
#
# These functions back the (small) prelude emitted in front of every
# generated workflow step template. They used to be inlined as Python
# source text in every dispatch result; moving them here lets the
# prelude pass choices/bindings/defaults as Python objects via the
# executor namespace instead of round-tripping them through source
# (which was both bloated and bug-prone — see json.dumps vs Python
# literals).
# =====================================================================

def _workflow_tokens(text):
    """Split a name/label into a lowercased token set, expanding camelCase."""
    import re
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", str(text or ""))
    return set(re.findall(r"[A-Za-z][A-Za-z0-9]+", text.lower()))


def _workflow_find_node(value, node_class, keywords):
    """Find a scene node matching ``value`` restricted to ``node_class``.

    Tries exact-name lookup first, then falls back to token-overlap scoring
    using ``keywords`` from the parameter binding. Returns None if nothing
    matches with positive score.
    """
    if not node_class:
        return None
    try:
        import slicer
    except ImportError:
        return None
    value = str(value or "")
    try:
        node = slicer.util.getNode(value)
        if node and node.IsA(node_class):
            return node
    except Exception:
        pass
    target_tokens = _workflow_tokens(value) | set(keywords or [])
    nodes = slicer.mrmlScene.GetNodesByClass(node_class)
    best_node = None
    best_score = -1
    for _i in range(nodes.GetNumberOfItems()):
        candidate = nodes.GetItemAsObject(_i)
        if candidate is None:
            continue
        score = len(target_tokens & _workflow_tokens(candidate.GetName()))
        if candidate.GetName() == value:
            score += 10
        if score > best_score:
            best_score = score
            best_node = candidate
    return best_node if best_score > 0 else None


def apply_workflow_metadata(parameterNode, choices, bindings, defaults):
    """Apply source-derived defaults and stored user choices to a parameter node.

    Mirrors the two application loops that used to be inlined into every
    generated prelude. Idempotent: only sets defaults when the parameter is
    empty, and only sets choices when an explicit value is stored.
    """
    if parameterNode is None:
        return
    # A @parameterNodeWrapper parameter node exposes typed properties, not the
    # classic SetParameter/SetNodeReferenceID API this helper uses — calling it
    # would raise AttributeError. Wrapper extensions skip this prelude at
    # generation (see choice_helpers._build_choice_prelude); this guard is
    # defense-in-depth for any package/path that still reaches here.
    if not hasattr(parameterNode, "SetParameter"):
        return
    if not bindings:
        return
    # Defaults first — only fill empty slots.
    for _role, _default in (defaults or {}).items():
        _binding = bindings.get(_role, {})
        if _binding.get("node_class", ""):
            continue
        try:
            _current = parameterNode.GetParameter(_role)
        except Exception:
            _current = ""
        if _current in (None, ""):
            parameterNode.SetParameter(_role, str(_default.get("value", "")))
    # Then stored user choices (override defaults).
    for _role, _binding in (bindings or {}).items():
        _value = (choices or {}).get(_role)
        if _value is None:
            continue
        _node_class = _binding.get("node_class", "")
        if _node_class:
            _node = _workflow_find_node(_value, _node_class, _binding.get("keywords", []))
            if _node is not None:
                parameterNode.SetNodeReferenceID(_role, _node.GetID())
        else:
            parameterNode.SetParameter(
                _role,
                "True" if _value is True
                else "False" if _value is False
                else str(_value),
            )


def _workflow_validate_polydata(_node, _role):
    if not hasattr(_node, "GetPolyData"):
        return
    _poly = _node.GetPolyData()
    if _poly is None:
        raise RuntimeError("Model node has no polydata: %s" % _role)
    try:
        if _poly.GetNumberOfPoints() <= 0:
            raise RuntimeError("Model node has empty polydata: %s" % _role)
    except AttributeError:
        pass


def _workflow_validate_markups(_node, _role, _min_points):
    if _min_points <= 0 or not hasattr(_node, "GetNumberOfControlPoints"):
        return
    _count = _node.GetNumberOfControlPoints()
    if _count < _min_points:
        raise RuntimeError(
            "Markup node %s needs at least %d control points, got %d"
            % (_role, _min_points, _count)
        )


def _workflow_condition_is_active(_parameter_node, _condition):
    _parameter = _condition.get("parameter", "")
    if not _parameter:
        return False
    _actual = _parameter_node.GetParameter(_parameter)
    _expected = str(_condition.get("value", ""))
    if _condition.get("operator") == "not_equals":
        return str(_actual) != _expected
    return str(_actual) == _expected


def _workflow_node_is_required(_parameter_node, _binding):
    _requirement = _binding.get("_workflow_requirement") or {"requirement": "optional_unknown"}
    _kind = _requirement.get("requirement", "optional_unknown")
    if _kind == "required":
        return True
    if _kind == "conditional":
        _groups = _requirement.get("condition_groups") or []
        if _groups:
            return any(
                all(_workflow_condition_is_active(_parameter_node, _c) for _c in _group)
                for _group in _groups
            )
        return any(
            _workflow_condition_is_active(_parameter_node, _c)
            for _c in (_requirement.get("conditions") or [])
        )
    return False


def validate_method_preconditions(logic, required_bindings):
    """Validate node references for an extension logic method call.

    Walks ``required_bindings`` (parameter binding dicts annotated with
    ``_workflow_requirement``) and raises ``RuntimeError`` if a required
    node reference is missing, has the wrong type, or is empty. Called
    from the prelude immediately before the corresponding ``logic.<method>()``
    invocation. No-op when ``required_bindings`` is empty.
    """
    if not logic or not required_bindings:
        return
    parameter_node = logic.getParameterNode()
    for _role, _binding in required_bindings.items():
        _node_class = _binding.get("node_class", "")
        if not _node_class:
            continue
        _accesses = set(_binding.get("accesses") or [])
        if "node_reference_read" not in _accesses:
            continue
        _node = parameter_node.GetNodeReference(_role)
        if _node is None:
            if _workflow_node_is_required(parameter_node, _binding):
                _requirement = _binding.get("_workflow_requirement") or {}
                _conditions = _requirement.get("conditions") or []
                if _conditions:
                    raise RuntimeError(
                        "[GeneratedWorkflowPrecondition] Missing conditional node reference: %s; active condition: %s"
                        % (_role, _conditions)
                    )
                raise RuntimeError(
                    "[GeneratedWorkflowPrecondition] Missing required node reference: %s"
                    % _role
                )
            continue
        if hasattr(_node, "IsA") and not _node.IsA(_node_class):
            raise RuntimeError(
                "Node reference %s has wrong type: expected %s" % (_role, _node_class)
            )
        if _node_class == "vtkMRMLModelNode":
            _workflow_validate_polydata(_node, _role)
        if "Markups" in _node_class:
            _workflow_validate_markups(
                _node, _role, int(_binding.get("min_control_points", 0) or 0)
            )
