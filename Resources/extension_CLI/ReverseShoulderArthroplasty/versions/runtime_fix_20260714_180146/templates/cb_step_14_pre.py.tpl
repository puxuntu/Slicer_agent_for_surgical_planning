# [runtime-fixed] Auto-revised by runtime self-correction at 20260714_180033.
# Pre-revision templates backed up under versions/runtime_fix_20260714_180033/.
# Fixed runtime error: No vtkMRMLMarkupsFiducialNode found from step 13 placement.
import slicer

# The "Prosthesis_center_point" markups node already exists from step 13
node = slicer.util.getNode("Prosthesis_center_point")

# Ensure display is visible
displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)

# Set as active markups list for placement
slicer.modules.markups.logic().SetActiveListID(node)

# Switch to single place mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToSinglePlaceMode()

print("[ReverseShoulderArthroplasty] Please click on the glenoid cavity surface in the 3D view to place the point for 'Prosthesis_center_point'.")
print("When finished, press the 'Done' button in the workflow panel.")
