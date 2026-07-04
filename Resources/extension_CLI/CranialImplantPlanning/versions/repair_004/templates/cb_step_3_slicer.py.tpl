# --- [Segment Editor session] add or reuse the target segment ---
# Deterministic + IDEMPOTENT: reuse a segment already named 'Cranial_Segment' (so a
# re-run / correction never creates a duplicate orphan), else
# AddEmptySegment(id, name) with the correct arg order.
import slicer

_ses_seg = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
if _ses_seg is None:
    raise RuntimeError("STATE_NOT_APPLIED: no segmentation found for add-segment")

_ses_segmentation = _ses_seg.GetSegmentation()
_ses_sid = _ses_segmentation.GetSegmentIdBySegmentName("Cranial_Segment")
if not _ses_sid:
    _ses_sid = _ses_segmentation.AddEmptySegment("Cranial_Segment", "Cranial_Segment")
if not _ses_sid:
    raise RuntimeError("STATE_NOT_APPLIED: AddEmptySegment returned empty id")

_ses_seg.SetAttribute("SlicerAIAgent.SegmentEditorTargetSegmentID", _ses_sid)
segmentId = _ses_sid
print("[SegmentEditor] Segment 'Cranial_Segment' ready.")
# --- [end Segment Editor session] ---
