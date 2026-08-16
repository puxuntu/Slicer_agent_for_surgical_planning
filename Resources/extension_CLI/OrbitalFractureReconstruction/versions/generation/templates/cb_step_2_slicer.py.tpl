# Create an empty MarkupsROI node named "Orbital_Region"
roiNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode", "Orbital_Region")
if roiNode is None or roiNode.GetName() != "Orbital_Region":
    raise RuntimeError("STATE_NOT_APPLIED: MarkupsROI node 'Orbital_Region' creation")