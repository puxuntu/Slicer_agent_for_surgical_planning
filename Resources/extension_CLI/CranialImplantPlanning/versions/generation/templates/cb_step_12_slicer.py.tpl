import numpy as np

#
# Create a new closed curve markup node
#

# Create the closed curve node in the scene
curveNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsClosedCurveNode")

# Optionally assign a custom name
curveNode.SetName("{closed_curve_name:}")

# Verify the node was created
if curveNode is None or not curveNode.IsA("vtkMRMLMarkupsClosedCurveNode"):
    raise RuntimeError("STATE_NOT_APPLIED: vtkMRMLMarkupsClosedCurveNode not created")

# To add control points from a numpy array (shape Nx3, RAS coordinates):
# pointPositions = np.array([
#   [x0, y0, z0],
#   [x1, y1, z1],
#   ...
# ])
# slicer.util.updateMarkupsControlPointsFromArray(curveNode, pointPositions)

# To add individual control points programmatically:
# import random
# for i in range(4):
#     ras = [random.uniform(-50, 50) for _ in range(3)]
#     index = curveNode.AddControlPoint(vtk.vtkVector3d(ras[0], ras[1], ras[2]))
#     curveNode.SetNthControlPointLabel(index, f"P{index + 1}")

# Verify the node is in the scene
if not slicer.mrmlScene.GetNodeByID(curveNode.GetID()):
    raise RuntimeError("STATE_NOT_APPLIED: ClosedCurveNode not found in scene after creation")