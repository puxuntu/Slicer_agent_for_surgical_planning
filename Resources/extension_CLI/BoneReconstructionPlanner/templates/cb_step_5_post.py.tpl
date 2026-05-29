# --- BoneReconstructionPlanner: 5. Change the layout to "Conventional". For the R (red) view, toggle on slice visibility in the 3D view. You should also toggle on slice intersection visibility and enable interaction. Then, you manually adjust the slice intersection position. (Process) ---
import slicer

node = slicer.mrmlScene.GetNodeByID(_bonereconstructionplanner_cb_step_5_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_5'")

# Validate user input
numPoints = node.GetNumberOfControlPoints()
if numPoints < 1:
    raise RuntimeError("Need at least 1 control points, got %d. Please add more." % numPoints)

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[BoneReconstructionPlanner] Step 'cb_step_5' processed with %d control points." % node.GetNumberOfControlPoints())
