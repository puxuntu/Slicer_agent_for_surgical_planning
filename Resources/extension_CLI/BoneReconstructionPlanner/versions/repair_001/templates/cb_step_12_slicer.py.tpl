"""
Configure mandibular curve display views (3D View 1 and Red).
Restricts visibility of the curve markups node to only these two views.
"""

# Find the mandibular curve node by fuzzy name match (case-insensitive)
curveNode = None
for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode"):
    nodeName = node.GetName()
    if nodeName and "mandibular" in nodeName.lower():
        curveNode = node
        break

if curveNode is None:
    raise RuntimeError("MANDIBULAR_CURVE_NOT_FOUND: No markups curve node with 'mandibular' in its name (case-insensitive search)")

# Get the display node
displayNode = curveNode.GetDisplayNode()
if displayNode is None:
    raise RuntimeError("DISPLAY_NODE_NOT_FOUND: Curve node has no display node")

# Resolve view node IDs for the two target views

# "3D View 1" -> singleton tag "1" for vtkMRMLViewNode
view3DNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")
if view3DNode is None:
    raise RuntimeError("VIEW_1_NOT_FOUND: 3D View 1 (singleton tag '1') not found in scene")

# "Red" slice view
redSliceNode = slicer.app.layoutManager().sliceWidget("Red").mrmlSliceNode()
redSliceNodeId = redSliceNode.GetID()

view3DNodeId = view3DNode.GetID()

# Configure display: restrict to only the specified views
displayNode.SetViewNodeIDs([view3DNodeId, redSliceNodeId])

# Ensure the curve is visible in both view types
# Visibility2D must be on for the Red slice view
displayNode.SetVisibility2D(1)
# Visibility3D must be on for the 3D view
displayNode.SetVisibility3D(1)
# Overall visibility must also be on
displayNode.SetVisibility(1)

# Read back and verify each state
actualViewNodeIDs = displayNode.GetViewNodeIDs()
expectedIDs = [view3DNodeId, redSliceNodeId]
for expected in expectedIDs:
    if expected not in actualViewNodeIDs:
        raise RuntimeError("STATE_NOT_APPLIED: ViewNodeID %s not found in display node's view node list" % expected)

if not displayNode.GetVisibility2D():
    raise RuntimeError("STATE_NOT_APPLIED: Visibility2D")

if not displayNode.GetVisibility3D():
    raise RuntimeError("STATE_NOT_APPLIED: Visibility3D")

if not displayNode.GetVisibility():
    raise RuntimeError("STATE_NOT_APPLIED: Visibility")