roiNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode", "Longbone_Region")
if not roiNode:
    raise RuntimeError("STATE_NOT_APPLIED: MarkupsROINode creation")
if roiNode.GetName() != "Longbone_Region":
    raise RuntimeError("STATE_NOT_APPLIED: ROI node name")