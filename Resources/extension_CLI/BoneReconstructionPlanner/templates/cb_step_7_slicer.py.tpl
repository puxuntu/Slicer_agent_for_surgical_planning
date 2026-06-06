# Enable slice visibility in 3D view for the Red slice view
layoutManager = slicer.app.layoutManager()
redSliceController = layoutManager.sliceWidget("Red").sliceController()
redSliceController.setSliceVisible(True)