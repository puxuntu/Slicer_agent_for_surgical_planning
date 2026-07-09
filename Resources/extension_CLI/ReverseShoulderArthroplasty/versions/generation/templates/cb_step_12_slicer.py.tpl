import slicer

# Create an empty MarkupsFiducial node (Point List) with the specified name
markupsNode = slicer.mrmlScene.AddNewNodeByClass(
    "vtkMRMLMarkupsFiducialNode", "Prosthesis_center_point")

# Verify creation
if markupsNode is None:
    raise RuntimeError("STATE_NOT_APPLIED: Failed to create vtkMRMLMarkupsFiducialNode")

if markupsNode.GetName() != "Prosthesis_center_point":
    raise RuntimeError("STATE_NOT_APPLIED: Node name mismatch - expected 'Prosthesis_center_point', got '%s'" % markupsNode.GetName())

# Create default display nodes so the point list is ready for visualization
markupsNode.CreateDefaultDisplayNodes()

# Verify that the display node was created
if markupsNode.GetDisplayNode() is None:
    raise RuntimeError("STATE_NOT_APPLIED: Display node was not created for MarkupsFiducialNode")

# Verify the node is empty (no control points)
if markupsNode.GetNumberOfControlPoints() != 0:
    raise RuntimeError("STATE_NOT_APPLIED: Node should be empty but has %d control points" % markupsNode.GetNumberOfControlPoints())