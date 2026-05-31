import slicer

# Get the mandibular curve node that was created in step 12.
# The curve node name starts with "mandibularCurve" and may have a unique suffix.
curveNode = None
curveNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode")
for i in range(curveNodes.GetNumberOfItems()):
    node = curveNodes.GetItemAsObject(i)
    if "mandibularCurve" in node.GetName():
        curveNode = node
        break

if curveNode is None:
    raise RuntimeError("mandibularCurve node not found. Did step 12 run?")

displayNode = curveNode.GetDisplayNode()
if displayNode is None:
    raise RuntimeError("Curve display node not found.")

# Add the Red slice view to the curve's visible views.
redSliceNode = slicer.app.layoutManager().sliceWidget('Red').mrmlSliceNode()
if redSliceNode is None:
    raise RuntimeError("Red slice node not found.")
displayNode.AddViewNodeID(redSliceNode.GetID())

print("[Slicer] Configured display settings for mandibular curve: added Red slice view visibility.")