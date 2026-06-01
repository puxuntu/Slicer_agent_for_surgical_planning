# Toggle FOV/Spacing match 2D for the Red slice view

# Get the Red slice node
sliceNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
if sliceNode is None:
    # Fallback: fuzzy search by name
    sliceNodes = slicer.util.getNodesByClass("vtkMRMLSliceNode")
    for node in sliceNodes:
        if "Red" in node.GetName():
            sliceNode = node
            break

if sliceNode is None:
    raise RuntimeError("Red slice node not found")

# Toggle SliceResolutionMatch2DView mode
if sliceNode.GetSliceResolutionMode() == sliceNode.SliceResolutionMatch2DView:
    # Currently in 2D view match mode, switch to match volumes
    sliceNode.SetSliceResolutionMode(sliceNode.SliceResolutionMatchVolumes)
else:
    # Switch to FOV/Spacing match 2D view
    sliceNode.SetSliceResolutionMode(sliceNode.SliceResolutionMatch2DView)