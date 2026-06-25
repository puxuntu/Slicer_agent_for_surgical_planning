"""
Change layout to Conventional.
"""
layoutManager = slicer.app.layoutManager()
layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView)

# Read back to verify the layout was applied
layoutNode = layoutManager.layoutLogic().GetLayoutNode()
applied = layoutNode.GetViewArrangement()
if applied != slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView:
    raise RuntimeError(
        "STATE_NOT_APPLIED: Layout did not switch to Conventional "
        "(expected %d, got %d)" % (slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView, applied)
    )