# [runtime-fixed] Auto-revised by runtime self-correction at 20260715_210305.
# Pre-revision templates backed up under versions/runtime_fix_20260715_210305/.
# Fixed runtime error: STATE_NOT_APPLIED: No ROI node found from previous step.
import slicer

# Resolve the Moving fracture ROI node directly from the scene
# (workflow state did not store it, so we look up by name)
node = slicer.util.getNode("Moving fracture ROI")
if node is None:
    raise RuntimeError("Could not find 'Moving fracture ROI' node in the scene.")

# Ensure display node exists for visibility
displayNode = node.GetDisplayNode()
if displayNode is None:
    node.CreateDefaultDisplayNodes()
    displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)

# Enable interactive handles for manual adjustment
if node is not None:
    try:
        node.SetHandlesInteractive(True)
        node.SetTranslationHandleVisibility(True)
        node.SetScaleHandleVisibility(True)
        node.SetRotationHandleVisibility(True)
    except Exception:
        pass

slicer.modules.markups.logic().SetActiveListID(node)
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_27", node.GetID(), _workflow_runtime_repeat_index)

print("[LongBoneFractureReduction] Please Manually adjust the ROI boundaries for the moving model.")
print("When finished, press the 'Done' button in the workflow panel.")
