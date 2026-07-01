# --- CranialImplantPlanning: Manually draw the curve on the skull model to include the fractured skull part. (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# Create the markup node for user interaction
node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsClosedCurveNode", "Cb Step 13")
displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)

print("[CranialImplantPlanning] Please Manually draw the curve on the skull model to include the fractured skull part.")
print("When finished, press the 'Done' button in the workflow panel.")

# Enter placement mode
slicer.modules.markups.logic().SetActiveListID(node)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToPersistentPlaceMode()

_cranialimplantplanning_cb_step_13_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_13", _cranialimplantplanning_cb_step_13_id, _workflow_runtime_repeat_index)
