# --- PelvicFracturePlanning: Manually click to add a cut point and adjust the position and rotation of the cutting plane. (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# Create the markup node for user interaction
node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "Cb Step 7")
displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)

print("[PelvicFracturePlanning] Please Place a cutting plane by clicking a cut point and adjusting its position and rotation.")
print("When finished, press the 'Done' button in the workflow panel.")

# Enter placement mode
slicer.modules.markups.logic().SetActiveListID(node)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToSinglePlaceMode()

_pelvicfractureplanning_cb_step_7_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_7", _pelvicfractureplanning_cb_step_7_id, _workflow_runtime_repeat_index)
