# Click the "Center view" button of the 3D view to center the view
# (resets the camera focal point around the visible scene content,
# including the reference reconstruction).
layoutManager = slicer.app.layoutManager()
threeDWidget = layoutManager.threeDWidget(0)
threeDView = threeDWidget.threeDView()
if threeDView is None:
    raise RuntimeError("STATE_NOT_APPLIED: 3D view")
threeDView.resetFocalPoint()