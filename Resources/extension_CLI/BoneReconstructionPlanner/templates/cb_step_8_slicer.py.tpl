sliceNode = slicer.app.layoutManager().sliceWidget('Red').mrmlSliceNode()
currentMode = sliceNode.GetSliceResolutionMode()
newMode = slicer.vtkMRMLSliceNode.SliceResolutionMatchVolumes
if currentMode != slicer.vtkMRMLSliceNode.SliceResolutionMatch2DView:
    newMode = slicer.vtkMRMLSliceNode.SliceResolutionMatch2DView
sliceNode.SetSliceResolutionMode(newMode)