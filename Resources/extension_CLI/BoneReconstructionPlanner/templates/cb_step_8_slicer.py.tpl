# Toggle on FOV/Spacing match 2D for the Red slice view
# This sets the slice resolution mode so that both FOV and Spacing match the 2D view.

# Get the Red slice node
sliceNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")

# Set slice resolution mode to match 2D view (FOV and Spacing both match the 2D view)
sliceNode.SetSliceResolutionMode(slicer.vtkMRMLSliceNode.SliceResolutionMatch2DView)