# Set FOV/Spacing match 2D for the Red slice view

# Get the Red slice node
sliceNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
if sliceNode is None:
    raise ValueError("Red slice node not found. Make sure a Red slice view exists.")

# Block modified events for efficiency
wasModified = sliceNode.StartModify()

# Set slice resolution mode to match 2D view (FOV matches the 2D view dimensions)
sliceNode.SetSliceResolutionMode(slicer.vtkMRMLSliceNode.SliceResolutionMatch2DView)

# Set slice spacing mode to automatic (spacing computed from the 2D view)
sliceNode.SetSliceSpacingMode(slicer.vtkMRMLSliceNode.AutomaticSliceSpacingMode)

# Re-enable modified events
sliceNode.EndModify(wasModified)