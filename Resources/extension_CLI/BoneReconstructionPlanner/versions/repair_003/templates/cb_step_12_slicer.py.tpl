"""
Configure mandibular curve display views (3D View 1 and Red).
Restricts visibility of the curve markups node to only these two views.
"""

# Find the mandibular curve node. Try multiple name patterns since the exact
# name assigned by the BoneReconstructionPlanner extension is unknown.
curveNode = None
nameCandidates = ["mandibular", "mandib", "mand"]
for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode"):
    nodeName = node.GetName()
    if nodeName:
        nodeNameLower = nodeName.lower()
        for candidate in nameCandidates:
            if candidate in nodeNameLower:
                curveNode = node
                break
        if curveNode:
            break

if curveNode is None:
    # Fallback: use the first (and ideally only) markups curve node in the scene
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode")
    if nodes.GetNumberOfItems() == 0:
        raise RuntimeError("CURVE_NOT_FOUND: No vtkMRMLMarkupsCurveNode found in the scene")
    curveNode = nodes.GetItemAsObject(0)

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
redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")
if redSliceNode is None:
    raise RuntimeError("RED_SLICE_NOT_FOUND: Red slice node not found in scene")

redSliceNodeId = redSliceNode.GetID()
view3DNodeId = view3DNode.GetID()

# Configure display: restrict to only the specified views.
# According to the vtkMRMLDisplayNode API (used by qMRMLDisplayNodeViewComboBox),
# RemoveAllViewNodeIDs clears all restrictions, then AddViewNodeID adds back.
displayNode.RemoveAllViewNodeIDs()
displayNode.AddViewNodeID(view3DNodeId)
displayNode.AddViewNodeID(redSliceNodeId)

# Enable overall visibility and the display-class-specific visibility states
displayNode.SetVisibility(1)
displayNode.SetVisibility2D(1)
displayNode.SetVisibility3D(1)

# Read back and verify each state
actualViewNodeIDs = displayNode.GetViewNodeIDs()
if view3DNodeId not in actualViewNodeIDs:
    raise RuntimeError("STATE_NOT_APPLIED: ViewNodeID %s not found in display node's view node list" % view3DNodeId)
if redSliceNodeId not in actualViewNodeIDs:
    raise RuntimeError("STATE_NOT_APPLIED: ViewNodeID %s not found in display node's view node list" % redSliceNodeId)

if not displayNode.GetVisibility():
    raise RuntimeError("STATE_NOT_APPLIED: Visibility")
if not displayNode.GetVisibility2D():
    raise RuntimeError("STATE_NOT_APPLIED: Visibility2D")
if not displayNode.GetVisibility3D():
    raise RuntimeError("STATE_NOT_APPLIED: Visibility3D")