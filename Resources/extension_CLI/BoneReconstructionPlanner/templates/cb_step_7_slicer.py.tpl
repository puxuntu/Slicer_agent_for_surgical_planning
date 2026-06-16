# Toggle on slice visibility in 3D for red slice

# Get the Red slice node by its known node ID
redSliceNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
if redSliceNode is None:
    raise RuntimeError("Red slice node not found (vtkMRMLSliceNodeRed)")

# Set slice visible in 3D views
redSliceNode.SetSliceVisible(True)

# Read back the state to confirm it was applied
if not redSliceNode.GetSliceVisible():
    raise RuntimeError("STATE_NOT_APPLIED: SliceVisible")