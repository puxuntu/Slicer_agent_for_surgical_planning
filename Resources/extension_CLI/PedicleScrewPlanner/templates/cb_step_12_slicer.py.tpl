# Disable the "Set interaction" option for slice intersections.
# This is the "Interaction" action in the Viewers toolbar / slice controller,
# backed by vtkMRMLApplicationLogic::IntersectingSlicesInteractive
# (which also keeps slice thick-slab interactive in sync, per the C++ implementation).
appLogic = slicer.app.applicationLogic()
appLogic.SetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesInteractive, False)
if appLogic.GetIntersectingSlicesEnabled(slicer.vtkMRMLApplicationLogic.IntersectingSlicesInteractive):
    raise RuntimeError("STATE_NOT_APPLIED: IntersectingSlicesInteractive")