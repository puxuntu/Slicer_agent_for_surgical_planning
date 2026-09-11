layoutManager = slicer.app.layoutManager()
redWidget = layoutManager.sliceWidget("Red")
redController = redWidget.sliceController()
# Equivalent to clicking the 'eye' (Show in 3D) icon of the Red slice controller
redController.setSliceVisible(True)

# Read back the state from the MRML slice node
redSliceNode = redWidget.mrmlSliceNode()
if not redSliceNode.GetSliceVisible():
    raise RuntimeError("STATE_NOT_APPLIED: vtkMRMLSliceNode.GetSliceVisible")