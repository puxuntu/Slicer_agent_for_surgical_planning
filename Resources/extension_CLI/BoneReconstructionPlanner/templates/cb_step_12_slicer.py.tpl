# Configure mandibular curve display to show in View 1 and Red slice view

# Find the mandibular curve markups node by name (fuzzy match)
curveNode = None
for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode"):
    name = node.GetName()
    if "mandibular" in name.lower() or "mandib" in name.lower():
        curveNode = node
        break

if curveNode is None:
    # Fallback: search any markups node with mandibular in name
    for i in range(slicer.mrmlScene.GetNumberOfNodes()):
        node = slicer.mrmlScene.GetNthNode(i)
        if node.IsA("vtkMRMLMarkupsNode") and "mandibular" in node.GetName().lower():
            curveNode = node
            break

if curveNode is None:
    raise ValueError("Mandibular curve node not found in the scene")

# Get the display node (vtkMRMLMarkupsDisplayNode inherits from vtkMRMLDisplayNode)
displayNode = curveNode.GetDisplayNode()
if displayNode is None:
    raise ValueError("Display node not found for the mandibular curve")

# Resolve view node IDs from the layout
layoutManager = slicer.app.layoutManager()

# View 1 (first 3D view)
threeDViewNode = layoutManager.threeDWidget(0).threeDView().mrmlViewNode()
view1ID = threeDViewNode.GetID()

# Red slice view
redSliceNode = layoutManager.sliceWidget("Red").mrmlSliceNode()
redID = redSliceNode.GetID()

# Configure display: overall visibility, 2D/slice visibility, and view filtering
displayNode.SetVisibility(True)
displayNode.SetVisibility2D(True)  # enable display in 2D/slice views
displayNode.RemoveAllViewNodeIDs()
displayNode.AddViewNodeID(view1ID)
displayNode.AddViewNodeID(redID)