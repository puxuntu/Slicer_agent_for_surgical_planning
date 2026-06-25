# Configure mandibular curve display to show in 3D View 1 (mandible view) and Red slice view

# (1) Find the mandibular curve node by name pattern matching
curveNode = None
nodeIter = iter([slicer.mrmlScene.GetNthNodeByClass(i, "vtkMRMLMarkupsCurveNode")
                 for i in range(slicer.mrmlScene.GetNumberOfNodesByClass("vtkMRMLMarkupsCurveNode"))])
for node in nodeIter:
    name = node.GetName() or ""
    if "mandibular" in name.lower() or "mandiblecurve" in name.lower():
        curveNode = node
        break
if not curveNode:
    raise RuntimeError("Could not find mandibular curve node in the scene")

# (2) Get the display node
displayNode = curveNode.GetDisplayNode()
if not displayNode:
    raise RuntimeError("Display node is None for mandibular curve node")

# (3) Resolve "3D View 1" (the mandible view via its singleton tag "1") and "Red" slice node
mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
if not mandibleViewNode:
    raise RuntimeError("Could not find 3D View 1 (mandible view) node using MANDIBLE_VIEW_SINGLETON_TAG")
redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")
if not redSliceNode:
    raise RuntimeError("Could not find Red slice node")

# (4) Build list of view IDs — show only in these two views
viewNodeIDs = [mandibleViewNode.GetID(), redSliceNode.GetID()]

# (5) Apply view restriction (replaces existing view node ID list)
displayNode.SetViewNodeIDs(viewNodeIDs)

# (6) Enable overall visibility (3D and 2D/slice)
displayNode.SetVisibility(1)
displayNode.SetVisibility2D(1)

# (7) Read-back verification
actualViewIDs = displayNode.GetViewNodeIDs()
for vid in viewNodeIDs:
    if vid not in actualViewIDs:
        raise RuntimeError("STATE_NOT_APPLIED: view node ID %s not in display node's view list" % vid)
if not displayNode.GetVisibility():
    raise RuntimeError("STATE_NOT_APPLIED: Visibility is False after SetVisibility(1)")
if not displayNode.GetVisibility2D():
    raise RuntimeError("STATE_NOT_APPLIED: Visibility2D is False after SetVisibility2D(1)")