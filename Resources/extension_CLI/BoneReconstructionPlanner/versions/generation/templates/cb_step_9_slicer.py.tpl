# Show slice intersections in the views and enable interactive translation/rotation.
# This mirrors the "Slice intersections" toolbar/context-menu toggle and the
# Interaction > Translate / Rotate options, which are implemented through
# vtkMRMLApplicationLogic::SetIntersectingSlicesEnabled(operation, enabled).
# (Base/QTGUI/qSlicerViewersToolBar.cxx, qSlicerSubjectHierarchyViewContextMenuPlugin.cxx)

appLogic = slicer.app.applicationLogic()
if not appLogic:
    raise RuntimeError("STATE_NOT_APPLIED: applicationLogic unavailable")

appLogicClass = slicer.vtkMRMLApplicationLogic
operations = {
    "IntersectingSlicesVisibility": appLogicClass.IntersectingSlicesVisibility,
    "IntersectingSlicesInteractive": appLogicClass.IntersectingSlicesInteractive,
    "IntersectingSlicesTranslation": appLogicClass.IntersectingSlicesTranslation,
    "IntersectingSlicesRotation": appLogicClass.IntersectingSlicesRotation,
}

# Show slice intersections and enable interaction with translation + rotation.
for name, operation in operations.items():
    appLogic.SetIntersectingSlicesEnabled(operation, True)

# Verify the state took effect.
for name, operation in operations.items():
    if not appLogic.GetIntersectingSlicesEnabled(operation):
        raise RuntimeError("STATE_NOT_APPLIED: %s" % name)