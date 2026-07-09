# --- ReverseShoulderArthroplasty: Manually click on the glenoid cavity surface to select a point for the "Prosthesis_center_point". (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# Reuse the markup node created by a previous step (do not create a duplicate).
nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsFiducialNode")
node = None
for i in range(nodes.GetNumberOfItems() - 1, -1, -1):
    candidate = nodes.GetItemAsObject(i)
    if candidate is not None:
        node = candidate
        break
if node is None:
    raise RuntimeError("No vtkMRMLMarkupsFiducialNode found from previous placement step.")

displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)
slicer.modules.markups.logic().SetActiveListID(node)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToSinglePlaceMode()
_reverseshoulderarthroplasty_cb_step_13_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_13", _reverseshoulderarthroplasty_cb_step_13_id, _workflow_runtime_repeat_index)

print("[ReverseShoulderArthroplasty] Please Click on the glenoid cavity surface to place the point")
print("When finished, press the 'Done' button in the workflow panel.")
