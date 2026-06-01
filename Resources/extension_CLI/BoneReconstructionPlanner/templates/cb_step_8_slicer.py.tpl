# Set Red slice view resolution mode to "Match 2D view" (FOV, Spacing match 2D)

# Get the Red slice node
sliceNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
if sliceNode is None:
    raise RuntimeError("Red slice node not found")

# Set resolution mode to match 2D view (Field of View and Spacing derived from 2D view dimensions)
# Available modes:
#   SliceResolutionMatch2DView             - FOV and Spacing match 2D view
#   SliceResolutionMatchVolumes            - FOV and Spacing match volumes
#   SliceFOVMatch2DViewSpacingMatchVolumes - FOV match 2D view, spacing match volumes
#   SliceFOVMatchVolumesSpacingMatch2DView - FOV match volumes, spacing match 2D view
#   SliceResolutionCustom                  - Custom resolution
sliceNode.SetSliceResolutionMode(slicer.vtkMRMLSliceNode.SliceResolutionMatch2DView)