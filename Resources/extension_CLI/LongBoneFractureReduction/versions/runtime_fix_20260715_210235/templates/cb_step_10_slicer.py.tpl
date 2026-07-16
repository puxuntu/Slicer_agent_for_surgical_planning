# [runtime-fixed] Auto-revised by runtime self-correction at 20260715_210107.
# Pre-revision templates backed up under versions/runtime_fix_20260715_210107/.
# Fixed runtime error: No reference segmentation selected. Select the reference segmentation in the Long Bone Fracture Reduction module first.
# LongBoneFractureReduction cb_step_10: Set Reference_Segment invisible
# The reference segmentation was created via Segment Editor (not via the
# LongBoneFractureReduction tree selector), so parameterNode.referenceSegmentation
# is None. We find the node from the scene directly.

from LongBoneFractureReduction import LongBoneFractureReductionLogic

logic = LongBoneFractureReductionLogic()
parameterNode = logic.getParameterNode()

# Find the reference segmentation node that was created by the Segment Editor workflow
segNode = slicer.util.getNode("Reference_Segmentation")
if segNode is None:
    raise RuntimeError("Reference_Segmentation node not found in the scene.")

# Assign it to the parameter node so future workflow steps (cb_step_11 onwards)
# can also resolve it via the module's own API
parameterNode.referenceSegmentation = segNode

# Ensure display node exists
if segNode.GetDisplayNode() is None:
    segNode.CreateDefaultDisplayNodes()

displayNode = segNode.GetDisplayNode()

# Find the segment "Reference_Segment" by name
seg = segNode.GetSegmentation()
segmentId = seg.GetSegmentIdBySegmentName("Reference_Segment")
if not segmentId:
    raise RuntimeError("Segment 'Reference_Segment' not found in 'Reference_Segmentation'.")

# Set the segment invisible
displayNode.SetSegmentVisibility(segmentId, False)

# Verify the state was applied
if displayNode.GetSegmentVisibility(segmentId):
    raise RuntimeError("STATE_NOT_APPLIED: SetSegmentVisibility(%s, False) did not take effect." % segmentId)
