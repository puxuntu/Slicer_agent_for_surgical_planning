# Hide slice in 3D view for Red slice
layoutManager = slicer.app.layoutManager()
redWidget = layoutManager.sliceWidget("Red")
redWidget.sliceController().setSliceVisible(False)