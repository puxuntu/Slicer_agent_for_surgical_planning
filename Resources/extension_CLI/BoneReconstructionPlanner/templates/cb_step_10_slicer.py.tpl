# Toggle on enable interaction for slice intersection visibility
#
# This script:
#   1. Gets or creates the crosshair node
#   2. Sets crosshair mode to ShowIntersection (shows intersection lines at crosshair)
#   3. Sets crosshair behavior to enable interaction (jump slices on click/drag)
#   4. Enables intersecting slices visibility on all slice display nodes

# --- Get or create the crosshair node ---
crosshairNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLCrosshairNode")
if crosshairNode is None:
    crosshairNode = slicer.mrmlScene.AddNewNode("vtkMRMLCrosshairNode", "Crosshair")
    # The default crosshair node is a singleton, ensure it is tagged properly
    crosshairNode.SetSingletonTag("default")

# --- Enable slice intersection visibility ---
# ShowIntersection mode displays crosshair with intersection lines
# in all slice views
crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.ShowIntersection)

# --- Enable interaction ---
# OffsetJumpSlice: when the crosshair position is changed (by click/drag),
# the slice views jump to the new position while keeping their relative offset.
# Alternative: use CenteredJumpSlice to center the slices on the crosshair.
crosshairNode.SetCrosshairBehavior(slicer.vtkMRMLCrosshairNode.OffsetJumpSlice)

# --- Also enable intersecting slices visibility on all slice display nodes ---
sliceDisplayNodes = slicer.util.getNodesByClass("vtkMRMLSliceDisplayNode")
for sliceDisplayNode in sliceDisplayNodes:
    sliceDisplayNode.SetIntersectingSlicesVisibility(1)

print("Slice intersection visibility enabled with interaction.")