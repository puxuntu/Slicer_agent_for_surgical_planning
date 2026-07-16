# --- [Segment Editor session] add or reuse the target segment ---
# Directly retrieve the segmentation node by name 'Reference_Segmentation' (created in step 2)
import slicer

_ses_seg = slicer.util.getNode('Reference_Segmentation')
if _ses_seg is None:
    raise RuntimeError("STATE_NOT_APPLIED: Segmentation 'Reference_Segmentation' not found.")

_ses_segmentation = _ses_seg.GetSegmentation()
_ses_sid = _ses_segmentation.GetSegmentIdBySegmentName("Reference_Segment")
if not _ses_sid:
    _ses_sid = _ses_segmentation.AddEmptySegment("Reference_Segment", "Reference_Segment")
if not _ses_sid:
    raise RuntimeError("STATE_NOT_APPLIED: AddEmptySegment returned empty id")
_ses_seg.SetAttribute("SlicerAIAgent.SegmentEditorTargetSegmentID", _ses_sid)
segmentId = _ses_sid
print("[SegmentEditor] Segment 'Reference_Segment' ready.")