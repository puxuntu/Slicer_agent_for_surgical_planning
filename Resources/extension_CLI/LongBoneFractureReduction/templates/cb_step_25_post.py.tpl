# [runtime-fixed] Auto-revised by runtime self-correction at 20260715_211211.
# Pre-revision templates backed up under versions/runtime_fix_20260715_211211/.
# Fixed runtime error: Node not found for step 'cb_step_25'
import slicer

# Find the reference fracture ROI node
node = resolve_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_25", "vtkMRMLMarkupsROINode", _workflow_runtime_repeat_index)
if node is None:
    # Try by name from the scene
    node = slicer.util.getNode("Reference fracture ROI")
if node is None:
    # Try first ROI in scene
    roiNodes = slicer.util.getNodesByClass("vtkMRMLMarkupsROINode")
    if roiNodes:
        node = list(roiNodes.values())[0]
if node is None:
    raise RuntimeError("Could not find a MarkupsROINode for step 'cb_step_25'. Please ensure an ROI was created (step 24).")
else:
    # Remember this node for later steps
    remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_25", node.GetID(), _workflow_runtime_repeat_index)

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[LongBoneFractureReduction] Step 'cb_step_25' processed with ROI node: %s (%d control points)" % (node.GetName(), node.GetNumberOfControlPoints()))
