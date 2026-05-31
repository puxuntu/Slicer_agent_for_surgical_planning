import slicer

crosshairNode = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLCrosshairNode')
if crosshairNode is None:
    crosshairNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLCrosshairNode', 'Crosshair')
crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.ShowIntersection)
print("[Slicer] Crosshair slice intersection visibility enabled.")
