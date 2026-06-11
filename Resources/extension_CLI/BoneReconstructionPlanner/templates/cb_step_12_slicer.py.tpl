# Configure mandibular curve display in View 1 and Red

# Find the mandibular curve markups node by fuzzy name matching
curveNode = None
for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode"):
    if "mandibular" in node.GetName().lower():
        curveNode = node
        break
if curveNode is None:
    # Also check closed curve nodes
    for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsClosedCurveNode"):
        if "mandibular" in node.GetName().lower():
            curveNode = node
            break

if curveNode is None:
    raise ValueError("Mandibular curve node not found in the scene")

# Get the display node
displayNode = curveNode.GetDisplayNode()
if displayNode is None:
    curveNode.CreateDefaultDisplayNodes()
    displayNode = curveNode.GetDisplayNode()

# Resolve view node IDs from layout
layoutManager = slicer.app.layoutManager()

# View 1 (first 3D view, singleton tag "1")
threeDViewNode = layoutManager.threeDWidget(0).mrmlViewNode()
# Red slice view
redSliceNode = layoutManager.sliceWidget("Red").mrmlSliceNode()

# Restrict display to only View 1 and Red
viewNodeIDs = [threeDViewNode.GetID(), redSliceNode.GetID()]
displayNode.SetViewNodeIDs(viewNodeIDs)

# Enable overall visibility and 2D/slice visibility (Red is a slice view)
displayNode.SetVisibility(True)
displayNode.SetVisibility2D(True)