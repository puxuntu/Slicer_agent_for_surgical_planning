# Toggle FOV Spacing match 2D for Red view

# Get the Red view slice node
redSliceNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
if redSliceNode is None:
    raise RuntimeError("Red slice node not found")

# Get current resolution mode
currentMode = redSliceNode.GetSliceResolutionMode()

# Toggle: if currently in "FOV, Spacing match 2D" mode, switch to "FOV, Spacing match Volumes";
# otherwise switch to "FOV, Spacing match 2D"
if currentMode == redSliceNode.SliceResolutionMatch2DView:
    redSliceNode.SetSliceResolutionMode(redSliceNode.SliceResolutionMatchVolumes)
else:
    redSliceNode.SetSliceResolutionMode(redSliceNode.SliceResolutionMatch2DView)