# Create a new closed curve markups node for the cutting curve
curveNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsClosedCurveNode", "{curve_name: CuttingCurve}")
curveNode.CreateDefaultDisplayNodes()

# Read-back verification
if curveNode is None or curveNode.GetClassName() != "vtkMRMLMarkupsClosedCurveNode":
    raise RuntimeError("STATE_NOT_APPLIED: closed curve node creation")