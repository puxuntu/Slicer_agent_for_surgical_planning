# Configure markups display to show in both View 1 and Red views
# Get the mandibular curve node (placed in step 12)
markupsNode = None
for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode"):
    if "mandibularCurve" in node.GetName():
        markupsNode = node
        break

if markupsNode is None:
    # Fallback: use the most recent markups curve
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode")
    if nodes.GetNumberOfItems() > 0:
        markupsNode = nodes.GetItemAsObject(nodes.GetNumberOfItems()-1)
    else:
        raise RuntimeError("No markups curve node found. Ensure step 12 completed.")

# Get display node (create default if it doesn't exist)
displayNode = markupsNode.GetDisplayNode()
if displayNode is None:
    markupsNode.CreateDefaultDisplayNodes()
    displayNode = markupsNode.GetDisplayNode()

# Collect view node IDs for the target views
viewNodeIDs = []

# Add 3D view "View 1" (first 3D widget, typically named "1")
for i in range(slicer.app.layoutManager().threeDViewCount):
    viewNode = slicer.app.layoutManager().threeDWidget(i).mrmlViewNode()
    if "View" in viewNode.GetLayoutName() or viewNode.GetLayoutName() == "1":
        viewNodeIDs.append(viewNode.GetID())
        break

# Add "Red" slice view
sliceWidget = slicer.app.layoutManager().sliceWidget("Red")
viewNodeIDs.append(sliceWidget.mrmlSliceNode().GetID())

# Restrict the markups display to only the specified views
displayNode.SetViewNodeIDs(viewNodeIDs)

print("Markups display configured for View 1 and Red views")