# Toggle off slice visibility in 3D view for the Red slice view
layoutManager = slicer.app.layoutManager()
redSliceNode = layoutManager.sliceWidget("Red").mrmlSliceNode()
redSliceNode.SetSliceVisible(False)