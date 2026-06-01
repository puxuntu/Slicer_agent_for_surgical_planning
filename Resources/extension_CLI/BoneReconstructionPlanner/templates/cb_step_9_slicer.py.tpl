"""
Toggle slice intersection visibility (crosshair)
"""

# Get the crosshair singleton node
crosshairNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLCrosshairNode")
if crosshairNode is None:
    crosshairNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLCrosshairNode")
    crosshairNode.SetSingletonTag("default")
    slicer.mrmlScene.AddNode(crosshairNode)

# Toggle between ShowIntersection and NoCrosshair
if crosshairNode.GetCrosshairMode() == slicer.vtkMRMLCrosshairNode.ShowIntersection:
    crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.NoCrosshair)
else:
    crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.ShowIntersection)

# Also toggle slice intersection lines (lines from other slice orientations)
sliceDisplayNodes = slicer.util.getNodesByClass("vtkMRMLSliceDisplayNode")
for sliceDisplayNode in sliceDisplayNodes:
    currentVisibility = sliceDisplayNode.GetIntersectingSlicesVisibility()
    sliceDisplayNode.SetIntersectingSlicesVisibility(1 - currentVisibility)

# Force visual update
sliceNodes = slicer.util.getNodesByClass("vtkMRMLSliceNode")
for sliceNode in sliceNodes:
    sliceNode.Modified()