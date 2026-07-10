import slicer

# Create an empty MarkupsFiducial node with the specified name
markupNode = slicer.mrmlScene.AddNewNodeByClass(
    "vtkMRMLMarkupsFiducialNode", "Prosthesis_center_point"
)

# Create default display nodes so the node is visible in viewers
markupNode.CreateDefaultDisplayNodes()

# Verify the node was created and named correctly
if markupNode.GetName() != "Prosthesis_center_point":
    raise RuntimeError("STATE_NOT_APPLIED: MarkupsFiducialNode name")