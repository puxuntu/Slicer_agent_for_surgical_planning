# --- BoneReconstructionPlanner: 7. Manually click and draw on the "Red" view to create a curve along the mandible. (Setup) ---
import slicer

# Create the markup node for user interaction
node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode", "Cb Step 7")
displayNode = node.GetDisplayNode()
if displayNode is None:
    displayNode = node.CreateDefaultDisplayNode()
displayNode.SetVisibility(True)

print("[BoneReconstructionPlanner] Please Click and draw on the Red slice view to create a curve along the mandible.")
print("When finished, press the 'Done' button in the workflow panel.")

# Enter placement mode
slicer.modules.markups.logic().SetActiveListID(node)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToPersistentPlaceMode()

_bonereconstructionplanner_cb_step_7_id = node.GetID()
