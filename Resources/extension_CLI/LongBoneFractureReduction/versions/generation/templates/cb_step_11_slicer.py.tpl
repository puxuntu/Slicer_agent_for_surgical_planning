# --- [Segment Editor session] add or reuse the target segment ---
# Deterministic + IDEMPOTENT: reuse a segment already named 'Moving_Segment' (so a
# re-run / correction never creates a duplicate orphan), else
# AddEmptySegment(id, name) with the correct arg order (a one-arg
# AddEmptySegment auto-names the segment 'Segment_1'). Marks it the session
# TARGET segment so the effect Apply writes into it.
import slicer
_ses_seg = None
_ses_segs = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
for _ses_i in range(_ses_segs.GetNumberOfItems()):
    _ses_c = _ses_segs.GetItemAsObject(_ses_i)
    if _ses_c is not None and _ses_c.GetAttribute("SlicerAIAgent.SegmentEditorSession") == "1":
        _ses_seg = _ses_c
        break
if _ses_seg is None:
    for _ses_i in range(_ses_segs.GetNumberOfItems() - 1, -1, -1):
        _ses_c = _ses_segs.GetItemAsObject(_ses_i)
        if _ses_c is not None:
            _ses_seg = _ses_c
            break
if _ses_seg is None:
    raise RuntimeError("STATE_NOT_APPLIED: no segmentation found for add-segment")
_ses_segmentation = _ses_seg.GetSegmentation()
_ses_sid = _ses_segmentation.GetSegmentIdBySegmentName("Moving_Segment")
if not _ses_sid:
    _ses_sid = _ses_segmentation.AddEmptySegment("Moving_Segment", "Moving_Segment")
if not _ses_sid:
    raise RuntimeError("STATE_NOT_APPLIED: AddEmptySegment returned empty id")
_ses_segment = _ses_segmentation.GetSegment(_ses_sid)
if _ses_segment is not None:
    _ses_segment.SetColor(0.0, 1.0, 1.0)
_ses_seg.SetAttribute("SlicerAIAgent.SegmentEditorTargetSegmentID", _ses_sid)
segmentId = _ses_sid
print("[SegmentEditor] Segment 'Moving_Segment' ready.")
# --- [end Segment Editor session] ---
