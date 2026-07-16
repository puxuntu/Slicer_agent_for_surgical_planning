# Set the reference segment invisible
# (for the LongBoneFractureReduction extension)

# Find the LongBoneFractureReduction parameter node
parameterNode = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScriptedModuleNode')
if parameterNode is None or parameterNode.GetName() != 'LongBoneFractureReduction':
    raise RuntimeError("LongBoneFractureReduction parameter node not found. "
                       "Open the Long Bone Fracture Reduction module first.")

# Access the reference segmentation node via node reference
refSegNode = parameterNode.GetNodeReference('referenceSegmentation')
if refSegNode is None:
    raise RuntimeError("No reference segmentation selected. "
                       "Select a reference segmentation in the module first.")

# Ensure the display node exists (use property syntax for VTK getters)
if refSegNode.DisplayNode is None:
    refSegNode.CreateDefaultDisplayNodes()

displayNode = refSegNode.DisplayNode

# Resolve segment ID from segment name (use property syntax)
seg = refSegNode.Segmentation
segmentId = seg.GetSegmentIdBySegmentName('Reference_Segment')
if segmentId == '':
    raise RuntimeError("Segment 'Reference_Segment' not found in reference segmentation.")

# Set the segment invisible (overall visibility: affects both 3D and 2D views)
displayNode.SetSegmentVisibility(segmentId, False)

# Verify the state was applied
if displayNode.GetSegmentVisibility(segmentId):
    raise RuntimeError("STATE_NOT_APPLIED: SetSegmentVisibility(%s, False) did not take effect." % segmentId)