# Get the crosshair node and set it to ShowIntersection mode
crosshairNode = slicer.util.getNode("Crosshair")
crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.ShowIntersection)

# Get all slice display nodes and enable slice intersection visibility, interaction, translate, and rotate
sliceDisplayNodes = slicer.util.getNodesByClass("vtkMRMLSliceDisplayNode")
for sliceDisplayNode in sliceDisplayNodes:
    sliceDisplayNode.SetIntersectingSlicesVisibility(True)
    sliceDisplayNode.SetIntersectingSlicesInteractive(True)
    sliceDisplayNode.SetIntersectingSlicesTranslationEnabled(True)
    sliceDisplayNode.SetIntersectingSlicesRotationEnabled(True)

# Set interaction mode to Translate and Rotate (ViewTransform mode)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()