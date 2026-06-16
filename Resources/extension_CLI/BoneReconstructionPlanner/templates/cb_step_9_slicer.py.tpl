appLogic = slicer.app.applicationLogic()

# Enable slice intersection visibility
appLogic.SetIntersectingSlicesEnabled(
    slicer.vtkMRMLApplicationLogic.IntersectingSlicesVisibility, True)
if not appLogic.GetIntersectingSlicesEnabled(
        slicer.vtkMRMLApplicationLogic.IntersectingSlicesVisibility):
    raise RuntimeError("STATE_NOT_APPLIED: IntersectingSlicesVisibility")

# Enable slice intersection interaction (translate/rotate handles)
appLogic.SetIntersectingSlicesEnabled(
    slicer.vtkMRMLApplicationLogic.IntersectingSlicesInteractive, True)
if not appLogic.GetIntersectingSlicesEnabled(
        slicer.vtkMRMLApplicationLogic.IntersectingSlicesInteractive):
    raise RuntimeError("STATE_NOT_APPLIED: IntersectingSlicesInteractive")

# Enable translate handles
appLogic.SetIntersectingSlicesEnabled(
    slicer.vtkMRMLApplicationLogic.IntersectingSlicesTranslation, True)
if not appLogic.GetIntersectingSlicesEnabled(
        slicer.vtkMRMLApplicationLogic.IntersectingSlicesTranslation):
    raise RuntimeError("STATE_NOT_APPLIED: IntersectingSlicesTranslation")

# Enable rotate handles
appLogic.SetIntersectingSlicesEnabled(
    slicer.vtkMRMLApplicationLogic.IntersectingSlicesRotation, True)
if not appLogic.GetIntersectingSlicesEnabled(
        slicer.vtkMRMLApplicationLogic.IntersectingSlicesRotation):
    raise RuntimeError("STATE_NOT_APPLIED: IntersectingSlicesRotation")