fiducialNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "Prosthesis_center_point")
if fiducialNode is None:
    raise RuntimeError("Failed to create vtkMRMLMarkupsFiducialNode")
if fiducialNode.GetName() != "Prosthesis_center_point":
    raise RuntimeError("STATE_NOT_APPLIED: node name")
if fiducialNode.GetNumberOfControlPoints() != 0:
    raise RuntimeError("STATE_NOT_APPLIED: empty point list")