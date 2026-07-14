# --- [Segment Editor session] add or reuse the target segment ---
# Deterministic + IDEMPOTENT: reuse a segment already named 'Bone_Segment' (so a
# re-run / correction never creates a duplicate orphan).
import slicer

# Find the segmentation named "Bone_Segmentation" created in step 2
_ses_seg = None
for _ses_i in range(slicer.mrmlScene.GetNumberOfNodesByClass("vtkMRMLSegmentationNode")):
    _s_candidate = slicer.mrmlScene.GetNthNodeByClass(_ses_i, "vtkMRMLSegmentationNode")
    if _s_candidate is not None and _s_candidate.GetName() == "Bone_Segmentation":
        _ses_seg = _s_candidate
        break

if _ses_seg is None:
    raise RuntimeError("STATE_NOT_APPLIED: segmentation 'Bone_Segmentation' not found")

_ses_segmentation = _ses_seg.GetSegmentation()
_ses_sid = _ses_segmentation.GetSegmentIdBySegmentName("Bone_Segment")
if not _ses_sid:
    _ses_sid = _ses_segmentation.AddEmptySegment("Bone_Segment", "Bone_Segment")
if not _ses_sid:
    raise RuntimeError("STATE_NOT_APPLIED: AddEmptySegment returned empty id")

# Mark the target segment (safe if called)
_ses_seg.SetAttribute("SlicerAIAgent.SegmentEditorTargetSegmentID", _ses_sid)
segmentId = _ses_sid
print("[SegmentEditor] Segment 'Bone_Segment' ready.")
