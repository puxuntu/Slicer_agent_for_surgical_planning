# --- [Segment Editor session] add or reuse the target segment ---
import slicer

# Retrieve or create the segmentation node named 'Bone_Segmentation' (created in step 2)
_segmentationNode = slicer.mrmlScene.GetFirstNodeByName("Bone_Segmentation")
if _segmentationNode is None:
    _segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", "Bone_Segmentation")
    if _segmentationNode is None:
        raise RuntimeError("STATE_NOT_APPLIED: could not create segmentation node 'Bone_Segmentation'")

_segmentation = _segmentationNode.GetSegmentation()
_seg_sid = _segmentation.GetSegmentIdBySegmentName("Bone_Segment")
if not _seg_sid:
    _seg_sid = _segmentation.AddEmptySegment("Bone_Segment", "Bone_Segment")
if not _seg_sid:
    raise RuntimeError("STATE_NOT_APPLIED: AddEmptySegment returned empty id")
_segmentationNode.SetAttribute("SlicerAIAgent.SegmentEditorTargetSegmentID", _seg_sid)
segmentId = _seg_sid
print("[SegmentEditor] Segment 'Bone_Segment' ready.")
# --- [end Segment Editor session] ---