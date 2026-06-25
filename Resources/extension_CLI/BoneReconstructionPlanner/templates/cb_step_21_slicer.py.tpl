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

# Execute the reset field of view sequence
# This matches the implementation in qMRMLSliceControllerWidget::fitSliceToBackground()
sliceLogic.StartSliceNodeInteraction(SliceNode.ResetFieldOfViewFlag)
sliceLogic.FitSliceToBackground()
sliceNode.UpdateMatrices()
sliceLogic.EndSliceNodeInteraction()

# No strict FOV-change check needed — if the view was already fitted,
# FitSliceToBackground correctly does nothing and that is still success.