import slicer

# Resolve the "mandible" curve by fuzzy name match (runtime scene lookup).
mandibleNode = None
for node in slicer.util.getNodesByClass("vtkMRMLMarkupsNode"):
    if "{curve_name_keyword: mandible}" in node.GetName().lower():
        mandibleNode = node
        break
if mandibleNode is None:
    raise RuntimeError("MISSING_NODE: mandible curve not found in scene")

displayNode = mandibleNode.GetDisplayNode()
if displayNode is None:
    raise RuntimeError("MISSING_NODE: display node for mandible curve not found")

# Resolve the target view nodes by identity, not by layout position.
# 3D View 1        -> vtkMRMLViewNode  singleton tag "1"
# Red slice view   -> vtkMRMLSliceNode singleton tag "Red"
threeDViewNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")
redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")
if threeDViewNode is None or redSliceNode is None:
    raise RuntimeError("MISSING_NODE: target view node (3D View 1 / Red) not found")

viewNodeIDs = [threeDViewNode.GetID(), redSliceNode.GetID()]

# Restrict the curve's display to exactly these views (view filter).
displayNode.SetViewNodeIDs(viewNodeIDs)

# A slice view is included in the target, so make sure the markups display
# is enabled for 2D (slice) views as well as 3D.
displayNode.SetVisibility2D(True)

# Read back and verify the state took effect.
applied = list(displayNode.GetViewNodeIDs())
if set(applied) != set(viewNodeIDs):
    raise RuntimeError("STATE_NOT_APPLIED: ViewNodeIDs = %s" % applied)
if not displayNode.GetVisibility2D():
    raise RuntimeError("STATE_NOT_APPLIED: Visibility2D")