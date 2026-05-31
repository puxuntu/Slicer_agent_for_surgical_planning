crosshairNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLCrosshairNode")
if crosshairNode is None:
    crosshairNode = slicer.mrmlScene.AddNewNode("vtkMRMLCrosshairNode", "Crosshair")
    crosshairNode.SetSingletonTag("default")

crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.ShowIntersection)
print("Crosshair slice intersection visibility enabled.")
