"""
Apply the threshold effect to create initial segmentation.
Requires: a volume node (sourceVolume) loaded in the scene.
"""

import slicer

# ---- Resolve input volume ----
# Find the volume node by name (keyword match)
sourceVolume = None
for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLScalarVolumeNode"):
    if "{volume_name_like}".lower() in node.GetName().lower():
        sourceVolume = node
        break
if sourceVolume is None:
    raise RuntimeError("Source volume not found")

# ---- Create or find segmentation node ----
segmentationNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
if segmentationNode is None:
    segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
if segmentationNode is None:
    raise RuntimeError("Failed to create segmentation node")
segmentationNode.CreateDefaultDisplayNodes()

# ---- Create or find segment editor parameter set node ----
segmentEditorSingletonTag = "SegmentEditor"
segmentEditorNode = slicer.mrmlScene.GetSingletonNode(segmentEditorSingletonTag, "vtkMRMLSegmentEditorNode")
if segmentEditorNode is None:
    segmentEditorNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentEditorNode")
    segmentEditorNode.UnRegister(None)
    segmentEditorNode.SetSingletonTag(segmentEditorSingletonTag)
    slicer.mrmlScene.AddNode(segmentEditorNode)

# Configure the editor node
segmentEditorNode.SetAndObserveSourceVolumeNode(sourceVolume)
segmentEditorNode.SetAndObserveSegmentationNode(segmentationNode)

# ---- Create a segment ----
segmentation = segmentationNode.GetSegmentation()
if segmentation is None:
    raise RuntimeError("Failed to get segmentation object")
segmentId = segmentation.AddEmptySegment("{segment_name:Segment}")

# Select the segment for editing
segmentEditorNode.SetSelectedSegmentID(segmentId)

# ---- Get the threshold effect ----
# Access the segment editor widget and its effects
editorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
thresholdEffect = editorWidget.effectByName("Threshold")
if thresholdEffect is None:
    raise RuntimeError("Threshold effect not found")

# ---- Set threshold parameters ----
thresholdEffect.setParameter("MinimumThreshold", str({min_threshold:100}))
thresholdEffect.setParameter("MaximumThreshold", str({max_threshold:500}))

# ---- Apply the threshold effect ----
# self() returns the underlying Python SegmentEditorThresholdEffect instance
thresholdEffect.self().onApply()

# ---- Verify ----
segment = segmentation.GetSegment(segmentId)
if segment is None:
    raise RuntimeError("STATE_NOT_APPLIED: segment was not created")

# Get the binary labelmap representation to verify content
import vtkSegmentationCorePython as vtkSegmentationCore
labelmap = vtkSegmentationCore.vtkOrientedImageData()
if segmentationNode.GetBinaryLabelmapRepresentation(segmentId, labelmap):
    extent = labelmap.GetExtent()
    if extent[0] > extent[1] or extent[2] > extent[3] or extent[4] > extent[5]:
        raise RuntimeError("STATE_NOT_APPLIED: threshold produced empty segment")
else:
    raise RuntimeError("STATE_NOT_APPLIED: threshold effect did not create labelmap representation")