# --- BoneReconstructionPlanner: Manually adjust the mandibular cut planes in the mandible 3D view by dragging the visible plane interaction handles until the positions and rotations look correct. (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# Create the markup node for user interaction
node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "Cb Step 29")
displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)

print("[BoneReconstructionPlanner] Please Drag plane interaction handles in mandible 3D view to adjust positions and rotations")
print("When finished, press the 'Done' button in the workflow panel.")

# Enter placement mode
slicer.modules.markups.logic().SetActiveListID(node)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToPersistentPlaceMode()

_bonereconstructionplanner_cb_step_29_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_29", _bonereconstructionplanner_cb_step_29_id, _workflow_runtime_repeat_index)
