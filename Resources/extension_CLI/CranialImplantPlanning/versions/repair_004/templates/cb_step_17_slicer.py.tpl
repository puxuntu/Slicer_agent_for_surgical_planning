"""
Hide the curve node by making it invisible.
"""

# Find the curve node - try exact name first, then fallback to class-based lookup
curveNode = slicer.mrmlScene.GetFirstNodeByName("{curve_name}")

if curveNode is None:
    # Fallback: find any closed curve node in the scene
    curveNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLMarkupsClosedCurveNode")

if curveNode is None:
    # Further fallback: find any curve node
    curveNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLMarkupsCurveNode")

if curveNode is None:
    raise RuntimeError("No curve node containing '{curve_name}' found in the scene")

# Get the display node and set visibility to False
displayNode = curveNode.GetDisplayNode()
if displayNode is None:
    raise RuntimeError("Curve node has no display node")

displayNode.SetVisibility(False)

# Read back to confirm the state was applied
if displayNode.GetVisibility() != 0:
    raise RuntimeError("STATE_NOT_APPLIED: Visibility")