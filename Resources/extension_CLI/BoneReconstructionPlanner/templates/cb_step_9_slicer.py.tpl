# Enable slice intersection visibility and interaction modes
appLogic = slicer.app.applicationLogic()

# Enable visibility of slice intersections
appLogic.SetIntersectingSlicesEnabled(
    appLogic.IntersectingSlicesVisibility, True)

# Enable interaction with slice intersections (show handles)
appLogic.SetIntersectingSlicesEnabled(
    appLogic.IntersectingSlicesInteractive, True)

# Enable translation handles for slice intersections
appLogic.SetIntersectingSlicesEnabled(
    appLogic.IntersectingSlicesTranslation, True)

# Enable rotation handles for slice intersections
appLogic.SetIntersectingSlicesEnabled(
    appLogic.IntersectingSlicesRotation, True)

# Force visual update of all slice nodes (workaround for https://github.com/Slicer/Slicer/issues/6338)
sliceNodes = slicer.util.getNodesByClass('vtkMRMLSliceNode')
for sliceNode in sliceNodes:
    sliceNode.Modified()