"""
Hide a curve node by making it invisible.
"""

# Find the curve node by name (fuzzy match)
curveNode = None
for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode"):
    if "{curve_name}" in node.GetName():
        curveNode = node
        break

if curveNode is None:
    raise RuntimeError("Curve node containing '{curve_name}' not found in the scene")

# Get the display node and set visibility to False
displayNode = curveNode.GetDisplayNode()
if displayNode is None:
    raise RuntimeError("Curve node has no display node")

displayNode.SetVisibility(False)

# Read back to confirm the state was applied
if displayNode.GetVisibility() != 0:
    raise RuntimeError("STATE_NOT_APPLIED: Visibility")