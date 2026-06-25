# Toggle off slice visibility in 3D view for Red slice

# Get the Red slice node via its named slice widget
sliceNode = slicer.app.layoutManager().sliceWidget("Red").mrmlSliceNode()

# Turn off slice visibility in 3D view (0 = off)
sliceNode.SetSliceVisible(0)

# Verify that the state was applied
if sliceNode.GetSliceVisible() != 0:
    raise RuntimeError("STATE_NOT_APPLIED: SliceVisible on Red slice")