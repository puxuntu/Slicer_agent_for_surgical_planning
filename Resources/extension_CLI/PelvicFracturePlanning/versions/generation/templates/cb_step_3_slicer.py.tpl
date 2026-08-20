# Center the 3D view on the scene (reset focal point around the scene content)
layoutManager = slicer.app.layoutManager()
threeDWidget = layoutManager.threeDWidget(0)
threeDView = threeDWidget.threeDView()
if threeDView is None:
    raise RuntimeError("STATE_NOT_APPLIED: threeDView")
threeDView.resetFocalPoint()