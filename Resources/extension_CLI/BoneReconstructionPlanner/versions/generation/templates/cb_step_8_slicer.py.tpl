"""
Toggle on FOV and spacing match 2D for Red slice.
Sets the Red slice node's resolution mode to SliceResolutionMatch2DView,
which means both FOV and spacing are matched to the 2D view.
"""
import slicer
from vtkMRMLCorePython import vtkMRMLSliceNode
sliceWidget = slicer.app.layoutManager().sliceWidget('Red')
sliceNode = sliceWidget.mrmlSliceNode()
SLICE_RESOLUTION_MATCH_2D_VIEW = slicer.vtkMRMLSliceNode.SliceResolutionMatch2DView
sliceNode.SetSliceResolutionMode(SLICE_RESOLUTION_MATCH_2D_VIEW)
actualMode = sliceNode.GetSliceResolutionMode()
if actualMode != SLICE_RESOLUTION_MATCH_2D_VIEW:
    raise RuntimeError('STATE_NOT_APPLIED: SliceResolutionMode (expected %d, got %d)' % (SLICE_RESOLUTION_MATCH_2D_VIEW, actualMode))