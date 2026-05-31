# --- BoneReconstructionPlanner: 14. Manually click and draw on the "Red" view to create a curve along the mandible. (Process) ---
import slicer

node = slicer.mrmlScene.GetNodeByID(_bonereconstructionplanner_cb_step_14_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_14'")

# Validate user input
numPoints = node.GetNumberOfControlPoints()
if numPoints < 3:
    raise RuntimeError("Need at least 3 control points, got %d. Please add more." % numPoints)

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[BoneReconstructionPlanner] Step 'cb_step_14' processed with %d control points." % node.GetNumberOfControlPoints())
