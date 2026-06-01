# --- BoneReconstructionPlanner: 16. For the R (red) view, toggle off "slice visibility in 3D view". ---
# Get the Red slice display node and disable intersecting slices visibility (hides slice plane in 3D)
redSliceNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
if redSliceNode:
    sliceDisplayNode = redSliceNode.GetDisplayNode()
    if sliceDisplayNode:
        sliceDisplayNode.SetIntersectingSlicesVisibility(0)
        print("[BoneReconstructionPlanner] Slice visibility in 3D view disabled for Red view.")
    else:
        raise RuntimeError("Red slice display node not found.")
else:
    raise RuntimeError("Red slice node not found.")
