import slicer

layoutManager = slicer.app.layoutManager()
redWidget = layoutManager.sliceWidget('Red')
if redWidget is None:
    raise RuntimeError("Red slice widget is not available")
redSliceNode = redWidget.mrmlSliceNode()
redSliceNode.SetSliceSpacingMode(slicer.vtkMRMLSliceNode.SpacingModeMatch2D)

print("[Slicer] Layout/slice view operation completed.")
