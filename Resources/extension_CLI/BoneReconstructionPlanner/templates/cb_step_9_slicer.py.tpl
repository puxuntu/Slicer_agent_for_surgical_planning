# Configure slice intersection visibility and interaction modes
#
# This template uses slicer.app.applicationLogic().SetIntersectingSlicesEnabled()
# which automatically updates all slice display nodes and forces a visual refresh.

appLogic = slicer.app.applicationLogic()

# --- Visibility ---
# Show or hide slice intersection lines in slice views.
# Set to True to show, False to hide.
appLogic.SetIntersectingSlicesEnabled(
    slicer.vtkMRMLApplicationLogic.IntersectingSlicesVisibility,
    True)

# --- Interaction ---
# Enable or disable the ability to interact with slice intersection handles
# (click-and-drag on intersection lines/handles to reposition slices).
# Set to True to allow interaction, False to disallow.
appLogic.SetIntersectingSlicesEnabled(
    slicer.vtkMRMLApplicationLogic.IntersectingSlicesInteractive,
    True)

# --- Translation Mode ---
# Enable or disable translating (sliding) intersecting slices by
# dragging the intersection handle.
# Set to True to allow translation, False to disallow.
appLogic.SetIntersectingSlicesEnabled(
    slicer.vtkMRMLApplicationLogic.IntersectingSlicesTranslation,
    True)

# --- Rotation Mode ---
# Enable or disable rotating intersecting slices by
# dragging the rotation handle at the end of the intersection line.
# Set to True to allow rotation, False to disallow.
appLogic.SetIntersectingSlicesEnabled(
    slicer.vtkMRMLApplicationLogic.IntersectingSlicesRotation,
    True)