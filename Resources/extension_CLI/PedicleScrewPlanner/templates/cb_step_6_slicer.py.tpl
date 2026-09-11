# Enable slice intersection visibility and interaction with Translate and Rotate
# for every slice display node in the scene (backing properties of the "Slice
# intersections" / "Interaction" / Translate / Rotate options).
# Source evidence: vtkMRMLSliceDisplayNode.h (Set/GetIntersectingSlicesVisibility,
# Set/GetIntersectingSlicesInteractive, Set/GetIntersectingSlicesTranslationEnabled,
# Set/GetIntersectingSlicesRotationEnabled) and slicer.util.getNodesByClass.

sliceDisplayNodes = slicer.util.getNodesByClass("vtkMRMLSliceDisplayNode")
if not sliceDisplayNodes:
    raise RuntimeError("STATE_NOT_APPLIED: no vtkMRMLSliceDisplayNode found in scene")

for sliceDisplayNode in sliceDisplayNodes:
    # Show intersection lines of the other slice planes in each slice viewer.
    sliceDisplayNode.SetIntersectingSlicesVisibility(True)
    if not sliceDisplayNode.GetIntersectingSlicesVisibility():
        raise RuntimeError("STATE_NOT_APPLIED: IntersectingSlicesVisibility")

    # Show handles for slice intersection interaction.
    sliceDisplayNode.SetIntersectingSlicesInteractive(True)
    if not sliceDisplayNode.GetIntersectingSlicesInteractive():
        raise RuntimeError("STATE_NOT_APPLIED: IntersectingSlicesInteractive")

    # Enable the Translate interaction handle.
    sliceDisplayNode.SetIntersectingSlicesTranslationEnabled(True)
    if not sliceDisplayNode.GetIntersectingSlicesTranslationEnabled():
        raise RuntimeError("STATE_NOT_APPLIED: IntersectingSlicesTranslationEnabled")

    # Enable the Rotate interaction handle.
    sliceDisplayNode.SetIntersectingSlicesRotationEnabled(True)
    if not sliceDisplayNode.GetIntersectingSlicesRotationEnabled():
        raise RuntimeError("STATE_NOT_APPLIED: IntersectingSlicesRotationEnabled")

# Workaround to force visual update (see https://github.com/Slicer/Slicer/issues/6338)
sliceNodes = slicer.util.getNodesByClass("vtkMRMLSliceNode")
for sliceNode in sliceNodes:
    sliceNode.Modified()