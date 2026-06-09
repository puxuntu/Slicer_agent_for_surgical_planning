# Match FOV and spacing to 2D view for Red slice
redSliceNode = slicer.app.layoutManager().sliceWidget('Red').mrmlSliceNode()
redSliceNode.SetSliceResolutionMode(redSliceNode.SliceResolutionMatch2DView)