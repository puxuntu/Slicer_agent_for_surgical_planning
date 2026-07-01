import slicer
from slicer import vtkMRMLSegmentationNode

# Find the segmentation node by name (fuzzy match)
segmentationNode = None
for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode"):
    if {segmentation_name_keyword:""} in node.GetName().lower():
        segmentationNode = node
        break

if segmentationNode is None:
    raise RuntimeError("Segmentation node not found")

# Add an empty segment named 'Cranial_Segment'
# AddEmptySegment(segmentId, segmentName, color)
# When segmentName is empty, segmentId is used as name.
segmentId = segmentationNode.GetSegmentation().AddEmptySegment("Cranial_Segment", "Cranial_Segment")
if not segmentId:
    raise RuntimeError("STATE_NOT_APPLIED: Failed to add segment 'Cranial_Segment'")

# Verify that the segment was created
addedSegment = segmentationNode.GetSegmentation().GetSegment(segmentId)
if addedSegment is None:
    raise RuntimeError("STATE_NOT_APPLIED: Segment 'Cranial_Segment' was not found after addition")
if addedSegment.GetName() != "Cranial_Segment":
    raise RuntimeError("STATE_NOT_APPLIED: Segment name is '%s' instead of 'Cranial_Segment'" % addedSegment.GetName())