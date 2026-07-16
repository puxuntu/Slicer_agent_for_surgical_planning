# [runtime-fixed] Auto-revised by runtime self-correction at 20260715_210155.
# Pre-revision templates backed up under versions/runtime_fix_20260715_210155/.
# Fixed runtime error: 'MRMLCorePython.vtkMRMLSegmentationNode' object has no attribute 'SetSegmentVisibility'
"""
Set the moving segment invisible using the correct API path.
SetSegmentVisibility is on the DisplayNode, not the SegmentationNode directly.
"""
import slicer

TARGET_SEGMENT_NAME = "Moving_Segment"

# Look up the Moving_Segmentation node by name
movingSegNode = slicer.util.getNode("Moving_Segmentation")
if movingSegNode is None:
    raise RuntimeError("STATE_NOT_APPLIED: Segmentation node 'Moving_Segmentation' not found.")

seg = movingSegNode.GetSegmentation()
segmentId = seg.GetSegmentIdBySegmentName(TARGET_SEGMENT_NAME)
if not segmentId:
    raise RuntimeError("STATE_NOT_APPLIED: Segment '%s' not found in segmentation." % TARGET_SEGMENT_NAME)

# Get or create the display node (SetSegmentVisibility lives on the display node)
displayNode = movingSegNode.GetDisplayNode()
if displayNode is None:
    movingSegNode.CreateDefaultDisplayNodes()
    displayNode = movingSegNode.GetDisplayNode()

# Set the segment invisible on the display node
displayNode.SetSegmentVisibility(segmentId, False)

# Verify
if displayNode.GetSegmentVisibility(segmentId):
    raise RuntimeError("STATE_NOT_APPLIED: DisplayNode.SetSegmentVisibility(%s, False) did not take effect." % segmentId)

print("[LongBoneFractureReduction] Segment 'Moving_Segment' set invisible via display node.")
