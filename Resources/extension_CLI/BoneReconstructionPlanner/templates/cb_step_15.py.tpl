# --- BoneReconstructionPlanner: 15. For the R (red) view, toggle off "slice visibility in 3D view". ---
# Get the Red slice node
redSliceNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
if redSliceNode is None:
    raise RuntimeError("Red slice node not found")

# Toggle slice visibility in 3D view OFF
redSliceNode.SetSliceVisible(False)

print("[BoneReconstructionPlanner] Step cb_step_15 completed: slice visibility in 3D view disabled for Red view.")
