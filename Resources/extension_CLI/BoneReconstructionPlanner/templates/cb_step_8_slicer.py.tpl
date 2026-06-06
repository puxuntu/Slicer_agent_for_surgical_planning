# Enable FOV/Spacing match 2D for the Red slice view
layoutManager = slicer.app.layoutManager()
redSliceNode = layoutManager.sliceWidget("Red").mrmlSliceNode()
redSliceNode.SetSliceResolutionMode(slicer.vtkMRMLSliceNode.SliceFOVMatchVolumesSpacingMatch2DView)
