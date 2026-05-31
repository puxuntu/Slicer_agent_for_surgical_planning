import slicer

layoutManager = slicer.app.layoutManager()
layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView)

print("[Slicer] Layout/slice view operation completed.")
