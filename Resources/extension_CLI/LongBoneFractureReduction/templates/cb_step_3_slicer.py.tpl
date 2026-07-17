# [runtime-fixed] Auto-revised by runtime self-correction at 20260716_214416.
# Pre-revision templates backed up under versions/runtime_fix_20260716_214416/.
# Fixed runtime error: could not find nodes in the scene by name or id 'Bone_Segmentation'
# --- [Segment Editor session] get existing bone_segmentation node, add segment ---
import slicer

# The segmentation node was created in cb_step_2 with name "bone_segmentation"
_segmentation_node = slicer.util.getNode("bone_segmentation")
print(f"[SegmentEditor] Found segmentation node '{{_segmentation_node.GetName()}}'.")

_seg = _segmentation_node.GetSegmentation()
_segment_id = _seg.GetSegmentIdBySegmentName("bone_segment")
if not _segment_id:
    _segment_id = _seg.AddEmptySegment("bone_segment", "bone_segment")
if not _segment_id:
    raise RuntimeError("STATE_NOT_APPLIED: AddEmptySegment returned empty id")
segmentId = _segment_id
print("[SegmentEditor] Segment 'bone_segment' ready.")
