# --- BoneReconstructionPlanner: Manually click and draw on the "Red" view to create a curve along the mandible. (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# Reuse the markup node created by addMandibularCurve() in the previous step.
# Prefer a node THIS extension owns. Slicer extensions tag their own nodes
# with MRML attributes in their module's namespace, so an attribute named
# "BoneReconstructionPlanner.*" identifies the step's real target; picking the most
# recent node of the class alone can land on an unrelated node of the same
# type (a scene may hold several).
nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode")
_candidates = []
for i in range(nodes.GetNumberOfItems()):
    candidate = nodes.GetItemAsObject(i)
    if candidate is not None:
        _candidates.append(candidate)
_owned = []
for candidate in _candidates:
    try:
        _names = candidate.GetAttributeNames() or []
    except Exception:
        _names = []
    if any(str(_n).startswith("BoneReconstructionPlanner.") for _n in _names):
        _owned.append(candidate)
if _owned:
    node = _owned[-1]
elif _candidates:
    node = _candidates[-1]
else:
    raise RuntimeError("No vtkMRMLMarkupsCurveNode found from previous placement step.")

# The curve node is created by the extension's addMandibularCurve() placement
# workflow, which also creates its display node; here only make it visible
# (never create a second markup node or re-enter place mode).
displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)
_bonereconstructionplanner_cb_step_13_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_13", _bonereconstructionplanner_cb_step_13_id, _workflow_runtime_repeat_index)

print("[BoneReconstructionPlanner] Please In the Red slice view, click along the mandibular bone to place control points of the mandible curve, following the mandible from one end to the other.")
print("When finished, press the 'Done' button in the workflow panel.")
