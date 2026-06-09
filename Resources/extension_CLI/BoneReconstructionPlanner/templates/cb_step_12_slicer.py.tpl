# Find mandibular curve node (fuzzy name match)
curveNode = None
for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode"):
    if "mandibular" in node.GetName().lower():
        curveNode = node
        break

if curveNode is None:
    raise RuntimeError("No markups curve node found with 'mandibular' in its name")

# Get the display node
displayNode = curveNode.GetDisplayNode()

# Enable overall visibility and 2D (slice) visibility
displayNode.SetVisibility(True)
displayNode.SetVisibility2D(True)

# Restrict display to Red slice view and View 1 (first 3D view)
displayNode.RemoveAllViewNodeIDs()
displayNode.AddViewNodeID("vtkMRMLSliceNodeRed")
displayNode.AddViewNodeID("vtkMRMLViewNode1")