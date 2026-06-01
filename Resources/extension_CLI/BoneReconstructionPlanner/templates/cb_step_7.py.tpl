# --- BoneReconstructionPlanner: 7. For the R (red) view, toggle on "slice visibility in 3D view". ---
# Get the Red slice display node and enable intersecting slices visibility (shows slice plane in 3D)
redSliceNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
if redSliceNode:
    sliceDisplayNode = redSliceNode.GetDisplayNode()
    if sliceDisplayNode:
        sliceDisplayNode.SetIntersectingSlicesVisibility(1)
        print("[BoneReconstructionPlanner] Slice visibility in 3D view enabled for Red view.")
    else:
        raise RuntimeError("Red slice display node not found.")
else:
    raise RuntimeError("Red slice node not found.")
