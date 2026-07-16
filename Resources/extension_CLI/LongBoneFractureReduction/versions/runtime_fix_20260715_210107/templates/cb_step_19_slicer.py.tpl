"""
Set the moving segment invisible.
"""
import slicer

TARGET_SEGMENT_NAME = "Moving_Segment"

# Retrieve the moving segmentation node by cached ID from prior step
movingSegNode = slicer.mrmlScene.GetNodeByID('{moving_segmentation_id}')
if movingSegNode is None:
    raise RuntimeError("STATE_NOT_APPLIED: Segmentation node not found.")

seg = movingSegNode.GetSegmentation()
segmentId = seg.GetSegmentIdBySegmentName(TARGET_SEGMENT_NAME)
if not segmentId:
    raise RuntimeError("STATE_NOT_APPLIED: Segment '%s' not found in segmentation." % TARGET_SEGMENT_NAME)

# Set invisible
movingSegNode.SetSegmentVisibility(segmentId, False)

# Verify
if movingSegNode.GetSegmentVisibility(segmentId):
    raise RuntimeError("STATE_NOT_APPLIED: SetSegmentVisibility(%s, False) did not take effect." % segmentId)

print("[LongBoneFractureReduction] Segment 'Moving_Segment' set invisible.")