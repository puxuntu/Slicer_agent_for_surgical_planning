roiNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode")
roiNode.SetName("Longbone_Region")
if roiNode.GetName() != "Longbone_Region":
    raise RuntimeError("STATE_NOT_APPLIED: name")