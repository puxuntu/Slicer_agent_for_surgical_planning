"""Which node classes must ALREADY be in the scene before a workflow can start.

REQUIRED = DEMAND - PRODUCTION, over one ordered walk of the shipped
``workflow.json``. A class a pick step asks for is a required INPUT only when no
EARLIER step creates one. ZygomaticImplantPlanner picks a segmentation at
cb_step_7, but cb_step_2 ("create a new segmentation named
'Cranial_Segmentation'") makes it -- so the surgeon must supply a volume and an
entry-point list, and nothing else.

Derived entirely from the generated artifacts, so this needs no regeneration and
no change to the CLI generation pipeline: ``workflow.json`` for the demands and
the declared creations, ``workflow_metadata.parameter_bindings`` for the bound
class, and each step's own emitted template for creations the metadata failed to
type.

**Fails open by construction.** Every uncertainty -- an unreadable graph, an
unresolvable class, an untyped creator, any exception -- yields FEWER
requirements, never more. The gate may refuse only on positive evidence, because
under ``GUIDED_ONLY_MODE`` a false refusal makes a procedure unreachable with no
fallback turn. A missed requirement merely restores today's behaviour (the pick
step opens with an empty picker); a fabricated one blocks a surgeon who has
everything they need.

Qt-free, session-free and MRML-free, so it can run BEFORE ``start_for_extension``
-- a refusal then creates no session, no run folder and no manifest -- and can be
tested headlessly against the shipped packages.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

#: The four fields a step uses to name its own emitted template. Templates are
#: reached ONLY through these, never by globbing ``<step_id>*`` -- that prefix
#: also matches cb_step_15 and cb_step_18 from cb_step_1, which would excuse a
#: demand using production that actually happens later.
_TEMPLATE_KEYS = (
    "code_template", "pre_template", "post_template", "branch_action_template",
)

#: The node-creation idiom the generated templates use. Needed because declared
#: metadata is not always typed: ReverseShoulderArthroplasty cb_step_2 has
#: ``creates_node: true`` with ``node_class: null``, no node_roles, and the
#: step-graph resolver returns "" -- yet its template plainly reads
#: ``AddNewNodeByClass("vtkMRMLSegmentationNode", ...)``. Reading the emitted
#: code is a fact about what the step does, not a guess from its prose.
_CREATE_RE = re.compile(
    r"(?:AddNewNodeByClass|CreateNodeByClass)\s*\(\s*['\"](vtkMRML\w+)['\"]"
)

#: role_kind values that mean "this step produces the node".
_PRODUCING_ROLE_KINDS = ("extension_output", "interaction_output")


def _sub_ops(step: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [s for s in (step.get("sub_operations") or []) if isinstance(s, dict)]


def _roles(step: Dict[str, Any]) -> List[Dict[str, Any]]:
    out = [r for r in (step.get("node_roles") or []) if isinstance(r, dict)]
    for so in _sub_ops(step):
        out.extend(r for r in (so.get("node_roles") or []) if isinstance(r, dict))
    return out


def _specific(node_class: Any) -> str:
    """A concrete class, or "" for a base class that identifies nothing.

    ``vtkMRMLNode`` and friends are what an untyped pick resolves to; requiring
    "some node" would block every workflow on an empty scene for no information.
    Note ``vtkMRMLVolumeNode`` is deliberately NOT in that set -- it is abstract
    but does say "a volume", which two extensions legitimately demand.

    Normalized first, because an unusable class string is the one input that could
    turn this module's fail-open promise into its opposite: a generated
    ``"vtkMRMLVolumeNode (CT scalar volume)"`` matches no node however full the
    scene is, so it becomes a requirement that CANNOT be satisfied and the
    procedure is unreachable. A demand is only positive evidence if the thing
    demanded is nameable.
    """
    try:
        from .WorkflowRuntime import _NONSPECIFIC_NODE_CLASSES, normalize_node_class
    except Exception:
        return ""
    nc = normalize_node_class(node_class)
    return "" if (not nc or nc in _NONSPECIFIC_NODE_CLASSES) else nc


# --------------------------------------------------------------- DEMAND ----
def _demanded_class(step: Dict[str, Any], bindings: Dict[str, Any]) -> str:
    """The class this step's picker would be filtered to, or "".

    Resolved EXACTLY as the panel resolves it -- binding first, then the
    step-graph fallback -- because that is the safety argument: a class this got
    wrong would already be a broken pick step today.

    Two families are excluded that ``_node_class_from_step_meta`` does not
    exclude on its own, mirroring the panel's render precedence where the node
    tree is the LAST family tried: a multi-selector form and a segments table
    both carry a node class but neither picks a node.
    """
    try:
        from .WorkflowRuntime import WorkflowRuntime as RT
    except Exception:
        return ""
    if (step.get("operation_type") or step.get("op_type")) != "user_choice":
        return ""
    try:
        if RT._multi_choice_items(step) or RT._segment_selection_meta(step):
            return ""
    except Exception:
        return ""          # unsure whether it is a node pick -> do not demand
    choice_info = step.get("choice_info") or {}
    if isinstance(choice_info, list):
        choice_info = choice_info[0] if choice_info else {}
    param = str((choice_info or {}).get("parameter_name") or "").strip()
    bound = ((bindings.get(param) or {}) if param else {}).get("node_class")
    try:
        return _specific(bound) or _specific(RT._node_class_from_step_meta(step))
    except Exception:
        return ""


# ----------------------------------------------------------- PRODUCTION ----
def _produced_classes(step: Dict[str, Any], ext_dir: str) -> Dict[str, bool]:
    """Classes this step creates -> mapping class to True, plus the key ``"*"``
    when it creates something whose class cannot be determined.

    The wildcard matters: a step that declares ``creates_node`` but names no
    class is evidence that the procedure makes a node here, and refusing to act
    on it would manufacture a requirement the workflow satisfies itself. Treating
    it as "produces anything" keeps the failure on the fail-open side.
    """
    out: Dict[str, bool] = {}
    untyped = False

    for so in _sub_ops(step):
        if not so.get("creates_node"):
            continue
        nc = _specific(so.get("node_class"))
        if nc:
            out[nc] = True
        else:
            untyped = True
    if step.get("creates_node"):
        nc = _specific(step.get("node_class"))
        if nc:
            out[nc] = True
        else:
            untyped = True
    for role in _roles(step):
        if str(role.get("role_kind") or "") in _PRODUCING_ROLE_KINDS:
            nc = _specific(role.get("node_class"))
            if nc:
                out[nc] = True

    for key in _TEMPLATE_KEYS:
        rel = str(step.get(key) or "").strip()
        if not rel:
            continue
        path = os.path.join(ext_dir, rel)
        try:
            with open(path, "r", encoding="utf-8") as handle:
                for nc in _CREATE_RE.findall(handle.read()):
                    spec = _specific(nc)
                    if spec:
                        out[spec] = True
        except Exception:
            logger.debug("Template unreadable while typing creations: %s", path,
                         exc_info=True)

    if untyped and not out:
        out["*"] = True
    return out


def entry_requirements(extension_name: str) -> List[Dict[str, Any]]:
    """Node classes that must be in the scene before ``extension_name`` starts.

    Returns ``[{node_class, needed, steps: [{step_id, description}]}]``, or ``[]``
    when nothing can be established -- which is also what every failure returns.
    """
    try:
        from .ExtensionCLILoader import get_validated_extensions, get_workflow_graph
    except Exception:
        logger.debug("Extension loader unavailable for input precheck", exc_info=True)
        return []
    try:
        ext_data = (get_validated_extensions() or {}).get(extension_name) or {}
        ext_dir = ext_data.get("dir") or ""
        bindings = ((ext_data.get("workflow_metadata") or {})
                    .get("parameter_bindings") or {})
        graph = get_workflow_graph(extension_name) or {}
        steps = graph.get("steps") or []
    except Exception:
        logger.debug("Workflow graph unreadable for %s", extension_name, exc_info=True)
        return []

    made: Dict[str, bool] = {}
    required: Dict[str, Dict[str, Any]] = {}
    for step in steps:
        if not isinstance(step, dict):
            continue
        demanded = _demanded_class(step, bindings)
        if demanded and "*" not in made and demanded not in made:
            row = required.setdefault(
                demanded, {"node_class": demanded, "needed": 0, "steps": []},
            )
            row["needed"] += 1
            row["steps"].append({
                "step_id": step.get("step_id", ""),
                "description": str(step.get("description") or "").strip(),
            })
        try:
            made.update(_produced_classes(step, ext_dir))
        except Exception:
            logger.debug("Production scan failed for a step of %s",
                         extension_name, exc_info=True)
    return list(required.values())
