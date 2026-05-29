# --- BoneReconstructionPlanner: 14. Move the mandible planes manually to change the position and orientation of the cuts. (Setup) ---
import slicer

# Create the markup node for user interaction
node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "Cb Step 14")
displayNode = node.GetDisplayNode()
if displayNode is None:
    displayNode = node.CreateDefaultDisplayNode()
displayNode.SetVisibility(True)

print("[BoneReconstructionPlanner] Please Drag and rotate the mandible planes in the 3D view to change their position and orientation for optimal cuts.")
print("When finished, press the 'Done' button in the workflow panel.")

# Enter placement mode
slicer.modules.markups.logic().SetActiveListID(node)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToPersistentPlaceMode()

_bonereconstructionplanner_cb_step_14_id = node.GetID()
