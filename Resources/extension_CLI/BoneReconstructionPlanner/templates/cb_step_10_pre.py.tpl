# --- BoneReconstructionPlanner: Manually adjust the slice intersection position by translate and rotate of the cross lines in each view. (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# Create the markup node for user interaction
node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "Cb Step 10")
displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)

print("[BoneReconstructionPlanner] Please Translate and rotate slice intersection cross lines in each view")
print("When finished, press the 'Done' button in the workflow panel.")

# Enter placement mode
slicer.modules.markups.logic().SetActiveListID(node)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToPersistentPlaceMode()

_bonereconstructionplanner_cb_step_10_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_10", _bonereconstructionplanner_cb_step_10_id, _workflow_runtime_repeat_index)