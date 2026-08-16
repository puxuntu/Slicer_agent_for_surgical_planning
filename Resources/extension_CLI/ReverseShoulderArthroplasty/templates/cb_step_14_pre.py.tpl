# --- ReverseShoulderArthroplasty: Manually click on the glenoid cavity surface to select a point for the "Prosthesis_center_point". (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# Reuse the markup node created by a previous step (do not create a duplicate).
# Prefer a node THIS extension owns. Slicer extensions tag their own nodes
# with MRML attributes in their module's namespace, so an attribute named
# "ReverseShoulderArthroplasty.*" identifies the step's real target; picking the most
# recent node of the class alone can land on an unrelated node of the same
# type (a scene may hold several).
nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsFiducialNode")
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
    if any(str(_n).startswith("ReverseShoulderArthroplasty.") for _n in _names):
        _owned.append(candidate)
node = (_owned or _candidates)[-1] if (_owned or _candidates) else None
if node is None:
    raise RuntimeError("No vtkMRMLMarkupsFiducialNode found from previous placement step.")

# The display node was created by the previous step; only adjust visibility here.
displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)
slicer.modules.markups.logic().SetActiveListID(node)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToSinglePlaceMode()
_reverseshoulderarthroplasty_cb_step_14_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_14", _reverseshoulderarthroplasty_cb_step_14_id, _workflow_runtime_repeat_index)

print("[ReverseShoulderArthroplasty] Please Place the Prosthesis_center_point fiducial on the glenoid cavity surface.")
print("When finished, press the 'Done' button in the workflow panel.")