# Find the mandibular curve markups node by fuzzy name matching
curveNode = None
for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode"):
    if "mandibular" in node.GetName().lower():
        curveNode = node
        break

if curveNode is None:
    raise ValueError("Mandibular curve node not found in the scene")

# Get the display node
displayNode = curveNode.GetDisplayNode()
if displayNode is None:
    raise ValueError("Display node not found for the mandibular curve")

# Resolve view node IDs for 'View 1' (3D view) and 'Red' (slice view)
viewNodeIDs = []

# View 1 is typically the first 3D view (singletag 1)
threeDWidget = slicer.app.layoutManager().threeDWidget(0)
if threeDWidget:
    viewNodeIDs.append(threeDWidget.mrmlViewNode().GetID())

# Red slice view
sliceWidget = slicer.app.layoutManager().sliceWidget("Red")
if sliceWidget:
    viewNodeIDs.append(sliceWidget.mrmlSliceNode().GetID())

# Set the view restriction: show only in the specified views
displayNode.SetViewNodeIDs(viewNodeIDs)

# Enable overall visibility
displayNode.SetVisibility(True)

# Enable 2D/slice visibility so the curve appears in the Red slice view
displayNode.SetVisibility2D(True)