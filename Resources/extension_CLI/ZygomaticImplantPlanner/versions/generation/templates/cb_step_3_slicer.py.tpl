# --- [Segment Editor session] add or reuse the target segment ---
import slicer

# Retrieve the segmentation node (created in previous step)
_segmentationNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
if not _segmentationNode:
    raise RuntimeError("STATE_NOT_APPLIED: no segmentation node found for add-segment")

_segmentation = _segmentationNode.GetSegmentation()
_segmentId = _segmentation.GetSegmentIdBySegmentName("Cranial_Segment")
if not _segmentId:
    _segmentId = _segmentation.AddEmptySegment("Cranial_Segment", "Cranial_Segment")
if not _segmentId:
    raise RuntimeError("STATE_NOT_APPLIED: AddEmptySegment returned empty id")

# Mark this segment as target for the session (if needed downstream)
_segmentationNode.SetAttribute("SlicerAIAgent.SegmentEditorTargetSegmentID", _segmentId)
segmentId = _segmentId
print("[SegmentEditor] Segment 'Cranial_Segment' ready.")