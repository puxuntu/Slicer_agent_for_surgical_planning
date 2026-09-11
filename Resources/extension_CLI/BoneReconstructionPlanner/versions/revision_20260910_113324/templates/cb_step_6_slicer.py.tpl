# Switch to the built-in Conventional (four-up) layout
layoutManager = slicer.app.layoutManager()
layoutNode = layoutManager.layoutLogic().GetLayoutNode()

conventional_layout = slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView
layoutManager.setLayout(conventional_layout)

# Read back the applied layout
if layoutNode.GetViewArrangement() != conventional_layout:
    raise RuntimeError("STATE_NOT_APPLIED: vtkMRMLLayoutNode.ViewArrangement")