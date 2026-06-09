# Show Red slice in 3D view
layoutManager = slicer.app.layoutManager()
redWidget = layoutManager.sliceWidget("Red")
redWidget.sliceController().setSliceVisible(True)