# Turn off 3D display ("Show in 3D") of the Red slice plane.
layoutManager = slicer.app.layoutManager()
sliceWidget = layoutManager.sliceWidget("Red")

# The controller's setSliceVisible controls the slice node's SliceVisible
# property (the "Show in 3D" checkbox).
controller = sliceWidget.sliceController()
controller.setSliceVisible(False)

# Read back via the MRML node getter to confirm the state took effect.
sliceNode = sliceWidget.mrmlSliceNode()
if sliceNode.GetSliceVisible():
    raise RuntimeError("STATE_NOT_APPLIED: SliceVisible")