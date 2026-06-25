# Toggle on slice visibility in 3D view for Red slice
sliceNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
if sliceNode is None:
    raise RuntimeError("Red slice node not found")
sliceNode.SetSliceVisible(1)
if sliceNode.GetSliceVisible() != 1:
    raise RuntimeError("STATE_NOT_APPLIED: sliceNode.SliceVisible")