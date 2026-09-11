layoutManager = slicer.app.layoutManager()

# Resolve the Red slice view by identity (its view label), not by position.
redSliceWidget = layoutManager.sliceWidget("Red")
if redSliceWidget is None:
    raise RuntimeError("STATE_NOT_APPLIED: Red slice view widget is not present in the current layout")

# Fit the Red slice view's field of view to its background content
# (equivalent to the slice controller's "Fit to window" / reset field of view).
redSliceWidget.sliceController().fitSliceToBackground()