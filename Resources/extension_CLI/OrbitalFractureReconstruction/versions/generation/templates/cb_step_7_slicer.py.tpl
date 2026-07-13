# --- [Segment Editor session] add or reuse the target segment ---
import slicer

# Get or create a segmentation node
segNode = None
segNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
if segNodes.GetNumberOfItems() > 0:
    segNode = segNodes.GetItemAsObject(segNodes.GetNumberOfItems() - 1)
if segNode is None:
    # Create a new segmentation node if none exists
    segNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")

segmentation = segNode.GetSegmentation()
segmentId = segmentation.GetSegmentIdBySegmentName("Bone_Segment")
if not segmentId:
    segmentId = segmentation.AddEmptySegment("Bone_Segment")
if not segmentId:
    raise RuntimeError("STATE_NOT_APPLIED: AddEmptySegment returned empty id")
print("[SegmentEditor] Segment 'Bone_Segment' ready.")