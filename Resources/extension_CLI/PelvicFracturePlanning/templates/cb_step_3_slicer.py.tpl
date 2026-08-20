# Center the 3D view to inspect the segmented pelvis.
# The pelvis segmentation is an ordinary scene node (output of Step 1 of the
# PelvicFracturePlanning workflow); the 3D view is centered on the displayed
# content (including that segmentation) by resetting the camera focal point.

layoutManager = slicer.app.layoutManager()
threeDWidget = layoutManager.threeDWidget(0)
if threeDWidget is None:
    raise RuntimeError("STATE_NOT_APPLIED: no 3D view widget in the current layout")
threeDView = threeDWidget.threeDView()
threeDView.resetFocalPoint()