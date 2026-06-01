# --- BoneReconstructionPlanner: 7. For the R (red) view, toggle on "slice visibility in 3D view". ---
# Get the Red slice node
redSliceNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
if redSliceNode is None:
    raise RuntimeError("Red slice node not found")

# Toggle slice visibility in 3D view ON
redSliceNode.SetSliceVisible(True)

print("[BoneReconstructionPlanner] Step cb_step_7 completed: slice visibility in 3D view enabled for Red view.")
