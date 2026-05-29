# Slicer op: Toggle off slice visibility in the 3D view for the Red (R) view.
redSliceWidget = slicer.app.layoutManager().sliceWidget('Red')
if redSliceWidget is not None:
    redSliceNode = redSliceWidget.mrmlSliceNode()
    redSliceNode.SetSliceVisible(False)