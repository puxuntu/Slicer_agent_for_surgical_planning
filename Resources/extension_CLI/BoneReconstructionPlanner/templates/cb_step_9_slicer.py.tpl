"""
Enable slice intersection visibility and interaction (Translate and Rotate)
"""

appLogic = slicer.app.applicationLogic()

# Enable slice intersection visibility (show intersection lines in slice views)
appLogic.SetIntersectingSlicesEnabled(
    slicer.vtkMRMLApplicationLogic.IntersectingSlicesVisibility, True)

# Enable slice intersection interaction (show handles)
appLogic.SetIntersectingSlicesEnabled(
    slicer.vtkMRMLApplicationLogic.IntersectingSlicesInteractive, True)

# Enable translation interaction handles
appLogic.SetIntersectingSlicesEnabled(
    slicer.vtkMRMLApplicationLogic.IntersectingSlicesTranslation, True)

# Enable rotation interaction handles
appLogic.SetIntersectingSlicesEnabled(
    slicer.vtkMRMLApplicationLogic.IntersectingSlicesRotation, True)

# Read back and verify all states were applied
if not appLogic.GetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesVisibility):
    raise RuntimeError("STATE_NOT_APPLIED: IntersectingSlicesVisibility")
if not appLogic.GetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesInteractive):
    raise RuntimeError("STATE_NOT_APPLIED: IntersectingSlicesInteractive")
if not appLogic.GetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesTranslation):
    raise RuntimeError("STATE_NOT_APPLIED: IntersectingSlicesTranslation")
if not appLogic.GetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesRotation):
    raise RuntimeError("STATE_NOT_APPLIED: IntersectingSlicesRotation")