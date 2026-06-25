"""
Reset field of view in Red slice view.
Equivalent to clicking the "Fit to window" button in the Red slice view controller.
"""
import slicer
from slicer import vtkMRMLSliceNode as SliceNode

# Get the Red slice widget and its logic
layoutManager = slicer.app.layoutManager()
sliceWidget = layoutManager.sliceWidget("Red")
sliceLogic = sliceWidget.sliceLogic()
sliceNode = sliceWidget.mrmlSliceNode()

# Capture field of view before reset (for read-back verification)
fovBefore = sliceNode.GetFieldOfView()

# Execute the reset field of view sequence
# This matches the implementation in qMRMLSliceControllerWidget::fitSliceToBackground()
sliceLogic.StartSliceNodeInteraction(SliceNode.ResetFieldOfViewFlag)
sliceLogic.FitSliceToBackground()
sliceNode.UpdateMatrices()
sliceLogic.EndSliceNodeInteraction()

# Verify the field of view was actually changed by the reset
fovAfter = sliceNode.GetFieldOfView()
if (fovBefore[0] == fovAfter[0] and fovBefore[1] == fovAfter[1] and fovBefore[2] == fovAfter[2]):
    raise RuntimeError("STATE_NOT_APPLIED: ResetFieldOfView - FieldOfView did not change after FitSliceToBackground")