# Create a new closed curve markups node
closedCurveNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsClosedCurveNode")

# Verify the node was created
if closedCurveNode is None or closedCurveNode.GetClassName() != "vtkMRMLMarkupsClosedCurveNode":
    raise RuntimeError("STATE_NOT_APPLIED: vtkMRMLMarkupsClosedCurveNode creation")

# Confirm the node is in the scene
if not slicer.mrmlScene.GetNodeByID(closedCurveNode.GetID()):
    raise RuntimeError("STATE_NOT_APPLIED: Node not found in scene after creation")

# Optionally set a custom name (uncomment to use):
# closedCurveNode.SetName("{node_name: ClosedCurveName}")

# Create default display nodes so the curve is visible
closedCurveNode.CreateDefaultDisplayNodes()