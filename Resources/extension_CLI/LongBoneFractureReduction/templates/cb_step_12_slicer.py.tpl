# --- [Segment Editor session] add or reuse the target segment ---
# Directly retrieve the segmentation node by name 'Moving_Segmentation' (created in step 11)
import slicer

_ses_seg = slicer.util.getNode('Moving_Segmentation')
if _ses_seg is None:
    raise RuntimeError("STATE_NOT_APPLIED: Segmentation 'Moving_Segmentation' not found.")

_ses_segmentation = _ses_seg.GetSegmentation()
_ses_sid = _ses_segmentation.GetSegmentIdBySegmentName("Moving_Segment")
if not _ses_sid:
    _ses_sid = _ses_segmentation.AddEmptySegment("Moving_Segment", "Moving_Segment")
if not _ses_sid:
    raise RuntimeError("STATE_NOT_APPLIED: AddEmptySegment returned empty id")
_ses_seg.SetAttribute("SlicerAIAgent.SegmentEditorTargetSegmentID", _ses_sid)
segmentId = _ses_sid
print("[SegmentEditor] Segment 'Moving_Segment' ready.")