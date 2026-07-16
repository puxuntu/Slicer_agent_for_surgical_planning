# --- LongBoneFractureReduction: Manually adjust the boundaries of the ROI to retain the fractured part of the reference model. (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import resolve_interaction_node, remember_interaction_node

# Retrieve the ROI node created in the previous step (cb_step_24)
node = resolve_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_25", _workflow_runtime_repeat_index)
if node is None:
    raise RuntimeError("STATE_NOT_APPLIED: No ROI node found from previous step.")

# Ensure display node exists for visibility
displayNode = node.GetDisplayNode()
if displayNode is None:
    node.CreateDefaultDisplayNodes()
    displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)

slicer.modules.markups.logic().SetActiveListID(node)
_longbonefracturereduction_cb_step_25_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_25", _longbonefracturereduction_cb_step_25_id, _workflow_runtime_repeat_index)

print("[LongBoneFractureReduction] Please Manually adjust the ROI boundaries for the reference model.")
print("When finished, press the 'Done' button in the workflow panel.")