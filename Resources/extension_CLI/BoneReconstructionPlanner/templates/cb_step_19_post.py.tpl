# --- BoneReconstructionPlanner: 19. Click where you want the plane in "3D View 1" to create the first plane. Repeat this process to add as many planes as needed. (Process) ---
import slicer

node = slicer.mrmlScene.GetNodeByID(_bonereconstructionplanner_cb_step_19_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_19'")

# Validate user input
numPoints = node.GetNumberOfControlPoints()
if numPoints < 1:
    raise RuntimeError("Need at least 1 control points, got %d. Please add more." % numPoints)

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[BoneReconstructionPlanner] Step 'cb_step_19' processed with %d control points." % node.GetNumberOfControlPoints())
