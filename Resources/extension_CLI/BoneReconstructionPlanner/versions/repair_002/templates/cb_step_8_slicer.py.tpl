"""
Toggle on FOV/Spacing match 2D for Red slice.
Sets the Red slice node's resolution mode to SliceResolutionMatch2DView.
"""
# Get the Red slice node by name through the layout manager
redSliceNode = slicer.app.layoutManager().sliceWidget("Red").mrmlSliceNode()

# Set resolution mode to "FOV, Spacing match 2D" (SliceResolutionMatch2DView)
redSliceNode.SetSliceResolutionMode(redSliceNode.SliceResolutionMatch2DView)

# Verify the state was applied
if redSliceNode.GetSliceResolutionMode() != redSliceNode.SliceResolutionMatch2DView:
    raise RuntimeError("STATE_NOT_APPLIED: SliceResolutionMode did not change to SliceResolutionMatch2DView")