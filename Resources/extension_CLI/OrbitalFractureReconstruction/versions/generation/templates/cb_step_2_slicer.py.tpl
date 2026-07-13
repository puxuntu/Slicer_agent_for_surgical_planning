import slicer

# Create an empty MarkupsROI node
roiNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode")

# Ensure default display nodes exist
roiNode.CreateDefaultDisplayNodes()

# Set the name as requested
roiNode.SetName("Orbital_Region")

# Verify the name was applied
if roiNode.GetName() != "Orbital_Region":
    raise RuntimeError("STATE_NOT_APPLIED: ROI node name")