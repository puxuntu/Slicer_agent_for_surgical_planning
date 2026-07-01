segmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", "Cranial_Segmentation")
if not segmentationNode:
    raise RuntimeError("STATE_NOT_APPLIED: Failed to create vtkMRMLSegmentationNode")
if segmentationNode.GetName() != "Cranial_Segmentation":
    raise RuntimeError("STATE_NOT_APPLIED: segmentationNode.GetName() is '%s' instead of 'Cranial_Segmentation'" % segmentationNode.GetName())