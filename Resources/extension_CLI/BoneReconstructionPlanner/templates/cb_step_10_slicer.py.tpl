crosshairNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLCrosshairNode")
if crosshairNode is None:
    crosshairNode = slicer.mrmlScene.AddNewNode("vtkMRMLCrosshairNode", "Crosshair")
    crosshairNode.SetSingletonTag("default")

crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.ShowIntersection)
crosshairNode.SetCrosshairBehavior(slicer.vtkMRMLCrosshairNode.OffsetJumpSlice)
print("Crosshair interaction enabled.")
