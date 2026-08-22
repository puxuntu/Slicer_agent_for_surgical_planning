# --- LongBoneFractureReduction: Manually click and adjust on the Slice views to create the ROI for the "Longbone_Region". (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# Reuse the markup node created by a previous step (do not create a duplicate).
# Prefer a node THIS extension owns. Slicer extensions tag their own nodes
# with MRML attributes in their module's namespace, so an attribute named
# "LongBoneFractureReduction.*" identifies the step's real target; picking the most
# recent node of the class alone can land on an unrelated node of the same
# type (a scene may hold several).
nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsROINode")
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
    if any(str(_n).startswith("LongBoneFractureReduction.") for _n in _names):
        _owned.append(candidate)
node = (_owned or _candidates)[-1] if (_owned or _candidates) else None
if node is None:
    raise RuntimeError("No vtkMRMLMarkupsROINode found from previous placement step.")

# The ROI node is created by the previous step. Keep it visible when a display
# node already exists; do not attempt to create display nodes here.
displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)
slicer.modules.markups.logic().SetActiveListID(node)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToSinglePlaceMode()
_longbonefracturereduction_cb_step_4_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_4", _longbonefracturereduction_cb_step_4_id, _workflow_runtime_repeat_index)

print("[LongBoneFractureReduction] Please Click and adjust in the Slice views to draw the ROI bounding box around the long bone region.")
print("When finished, press the 'Done' button in the workflow panel.")
