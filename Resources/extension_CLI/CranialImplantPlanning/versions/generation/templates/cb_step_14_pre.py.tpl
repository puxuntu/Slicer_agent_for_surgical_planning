# --- CranialImplantPlanning: Manually draw the curve on the skull model to enclose the fractured skull portion. (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# Reuse the markup node created by a previous step (do not create a duplicate).
nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsClosedCurveNode")
node = None
for i in range(nodes.GetNumberOfItems() - 1, -1, -1):
    candidate = nodes.GetItemAsObject(i)
    if candidate is not None:
        node = candidate
        break
if node is None:
    raise RuntimeError("No vtkMRMLMarkupsClosedCurveNode found from previous placement step.")

displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)
slicer.modules.markups.logic().SetActiveListID(node)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToPersistentPlaceMode()
_cranialimplantplanning_cb_step_14_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_14", _cranialimplantplanning_cb_step_14_id, _workflow_runtime_repeat_index)

print("[CranialImplantPlanning] Please Manually draw the curve on the skull model to enclose the fractured skull portion.")
print("When finished, press the 'Done' button in the workflow panel.")
