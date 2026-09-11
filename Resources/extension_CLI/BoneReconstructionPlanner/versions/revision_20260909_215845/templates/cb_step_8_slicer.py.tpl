# Enable the Red slice view's automatic slice spacing mode so the slice
# resolution (spacing) matches the 2D viewport resolution.
# Backing API: vtkMRMLSliceNode SliceSpacingMode (Automatic vs Prescribed).
#   AutomaticSliceSpacingMode = 0, PrescribedSliceSpacingMode = 1

lm = slicer.app.layoutManager()
sliceWidget = lm.sliceWidget("Red")
if sliceWidget is None:
    raise RuntimeError("RedSliceViewNotFound")

sliceNode = sliceWidget.mrmlSliceNode()
if sliceNode is None:
    raise RuntimeError("RedSliceNodeNotFound")

# "Spacing match 2D" == automatic slice spacing mode
sliceNode.SetSliceSpacingModeToAutomatic()

# Read back
if sliceNode.GetSliceSpacingMode() != sliceNode.AutomaticSliceSpacingMode:
    raise RuntimeError("STATE_NOT_APPLIED: SliceSpacingMode (automatic)")