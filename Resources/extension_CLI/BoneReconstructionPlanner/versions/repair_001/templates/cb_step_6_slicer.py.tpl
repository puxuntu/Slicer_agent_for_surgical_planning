# Change layout to Conventional
layoutManager = slicer.app.layoutManager()
layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView)

# Verify the state change
if layoutManager.layout != slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView:
    raise RuntimeError("STATE_NOT_APPLIED: Conventional layout")