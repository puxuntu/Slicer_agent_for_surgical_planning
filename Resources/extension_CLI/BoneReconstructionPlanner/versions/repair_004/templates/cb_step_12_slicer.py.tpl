"""
Configure mandibular curve display views (3D View 1 and Red).

Find the markups curve node (assumes exactly one exists after step 11),
get its display node, and configure it to be visible ONLY in 3D View 1
(the 3D view with singleton tag '1') and the Red slice view.
"""

# ---------------------------------------------------------------------------
# Step 1: Find the mandibular curve node (first markups curve node in scene)
# ---------------------------------------------------------------------------
curveNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLMarkupsCurveNode")
if curveNode is None:
    raise RuntimeError("No markups curve node found in the scene. Ensure step 11 was executed.")

# ---------------------------------------------------------------------------
# Step 2: Resolve view node IDs
# ---------------------------------------------------------------------------
# 3D View 1 -> vtkMRMLViewNode with singleton tag '1'
view3DNode = slicer.mrmlScene.GetSingletonNode('1', 'vtkMRMLViewNode')
if view3DNode is None:
    raise RuntimeError("3D View 1 (vtkMRMLViewNode singleton tag '1') not found.")

# Red slice view -> vtkMRMLSliceNode accessed via scene singleton
redSliceNode = slicer.mrmlScene.GetSingletonNode('Red', 'vtkMRMLSliceNode')
if redSliceNode is None:
    raise RuntimeError("Red slice view not found.")

view3DId = view3DNode.GetID()
redSliceId = redSliceNode.GetID()

# ---------------------------------------------------------------------------
# Step 3: Get the display node and restrict it to the two target views
# ---------------------------------------------------------------------------
displayNode = curveNode.GetDisplayNode()
if displayNode is None:
    raise RuntimeError("Display node not found for the curve node.")

# Remove any existing view restrictions, then add only the desired views.
displayNode.RemoveAllViewNodeIDs()
displayNode.AddViewNodeID(view3DId)
displayNode.AddViewNodeID(redSliceId)

# ---------------------------------------------------------------------------
# Step 4: Enable visibility in 3D and 2D (slice) views
# ---------------------------------------------------------------------------
displayNode.SetVisibility(True)
displayNode.SetVisibility3D(True)
displayNode.SetVisibility2D(True)

# ---------------------------------------------------------------------------
# Step 5: Read-back verification
# ---------------------------------------------------------------------------
if not displayNode.GetVisibility3D():
    raise RuntimeError("Visibility3D not applied on curve display node")
if not displayNode.GetVisibility2D():
    raise RuntimeError("Visibility2D not applied on curve display node")
if not displayNode.GetVisibility():
    raise RuntimeError("Overall visibility not applied on curve display node")

viewIDs = displayNode.GetViewNodeIDs()
if view3DId not in viewIDs:
    raise RuntimeError("3D View 1 ID not found in display node view node IDs")
if redSliceId not in viewIDs:
    raise RuntimeError("Red slice view ID not found in display node view node IDs")

print("Mandibular curve display configured for 3D View 1 and Red slice.")