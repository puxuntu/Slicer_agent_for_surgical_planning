# --- [Segment Editor session] add or reuse the target segment ---
# Deterministic + IDEMPOTENT: reuse a segment already named 'bone_segment', else add one.
import slicer

# Retrieve the segmentation node created in step 2
_segmentation_node = slicer.util.getNode('Bone_Segmentation')
if _segmentation_node is None:
    raise RuntimeError("STATE_NOT_APPLIED: segmentation node 'Bone_Segmentation' not found. Ensure step 2 ran.")

_seg = _segmentation_node.GetSegmentation()
_segment_id = _seg.GetSegmentIdBySegmentName("bone_segment")
if not _segment_id:
    _segment_id = _seg.AddEmptySegment("bone_segment", "bone_segment")
if not _segment_id:
    raise RuntimeError("STATE_NOT_APPLIED: AddEmptySegment returned empty id")
segmentId = _segment_id
print("[SegmentEditor] Segment 'bone_segment' ready.")