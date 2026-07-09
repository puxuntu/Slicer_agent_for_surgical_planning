# --- [Segment Editor session] add or reuse the target segment ---
# Deterministic + IDEMPOTENT: reuse a segment already named 'Bone_Segment' (so a
# re-run / correction never creates a duplicate orphan), else
# AddEmptySegment(id, name) with the correct arg order (a one-arg
# AddEmptySegment auto-names the segment 'Segment_1'). Marks it the session
# TARGET segment so the effect Apply writes into it.
import slicer
_segmentationNode = slicer.mrmlScene.GetFirstNodeByName('Bone_Segmentation')
if _segmentationNode is None:
    raise RuntimeError("STATE_NOT_APPLIED: segmentation 'Bone_Segmentation' not found")
_segmentation = _segmentationNode.GetSegmentation()
_sid = _segmentation.GetSegmentIdBySegmentName("Bone_Segment")
if not _sid:
    _sid = _segmentation.AddEmptySegment("Bone_Segment", "Bone_Segment")
if not _sid:
    raise RuntimeError("STATE_NOT_APPLIED: AddEmptySegment returned empty id")
_segmentationNode.SetAttribute("SlicerAIAgent.SegmentEditorTargetSegmentID", _sid)
segmentId = _sid
print("[SegmentEditor] Segment 'Bone_Segment' ready.")