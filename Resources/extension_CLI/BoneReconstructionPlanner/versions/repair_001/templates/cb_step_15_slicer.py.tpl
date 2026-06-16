"""
Toggle off slice visibility in 3D for the Red slice view.
"""

layoutManager = slicer.app.layoutManager()
sliceWidget = layoutManager.sliceWidget("Red")
controller = sliceWidget.sliceController()

# Turn off slice visibility in 3D
controller.setSliceVisible(False)

# Read back and verify
sliceNode = controller.mrmlSliceNode()
if sliceNode.GetSliceVisible():
    raise RuntimeError("STATE_NOT_APPLIED: Red slice visibility in 3D")