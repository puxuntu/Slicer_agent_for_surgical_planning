"""
Enable slice intersection visibility and interaction with Translate and Rotate.

This script iterates over all vtkMRMLSliceDisplayNode instances in the scene
and sets intersection visibility, interactive mode, translation, and rotation
enabled to True.
"""

# Get all slice display nodes
sliceDisplayNodes = slicer.util.getNodesByClass("vtkMRMLSliceDisplayNode")

for sliceDisplayNode in sliceDisplayNodes:
    # Enable visibility of slice intersection lines
    sliceDisplayNode.SetIntersectingSlicesVisibility(True)
    # Enable interaction with slice intersections
    sliceDisplayNode.SetIntersectingSlicesInteractive(True)
    # Enable translation handles on slice intersections
    sliceDisplayNode.SetIntersectingSlicesTranslationEnabled(True)
    # Enable rotation handles on slice intersections
    sliceDisplayNode.SetIntersectingSlicesRotationEnabled(True)

# Trigger visual update on all slice nodes
sliceNodes = slicer.util.getNodesByClass('vtkMRMLSliceNode')
for sliceNode in sliceNodes:
    sliceNode.Modified()