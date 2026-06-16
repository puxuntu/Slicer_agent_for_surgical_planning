"""Reset field of view for the Red slice view."""

import slicer
import vtk

layoutManager = slicer.app.layoutManager()

# Get the "Red" slice widget and its logic
sliceWidget = layoutManager.sliceWidget("Red")
sliceLogic = sliceWidget.sliceLogic()
sliceNode = slicer.util.getNode('vtkMRMLSliceNodeRed')

# Save current field of view for verification
# GetFieldOfView() in VTK Python wrapping returns a tuple (3 doubles), takes zero arguments
oldFov = sliceNode.GetFieldOfView()

# Reset field of view to fit background volume
# (equivalent to clicking the "Fit to window" button in the slice controller)
sliceLogic.StartSliceNodeInteraction(slicer.vtkMRMLSliceNode.FieldOfViewFlag)
sliceLogic.FitSliceToBackground()
sliceNode.UpdateMatrices()
sliceLogic.EndSliceNodeInteraction()

# Verify that field of view was updated
newFov = sliceNode.GetFieldOfView()
if newFov[0] <= 0.0 or newFov[1] <= 0.0:
    raise RuntimeError("STATE_NOT_APPLIED: FieldOfView (non-positive values after reset)")