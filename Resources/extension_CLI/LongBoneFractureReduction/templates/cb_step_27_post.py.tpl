# --- LongBoneFractureReduction: Manually adjust the boundaries of the ROI to retain the fractured part of the moving model. (Process) ---
import slicer
from SlicerAIAgentLib.workflow_state import resolve_interaction_node

node = resolve_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_27", "vtkMRMLMarkupsROINode", _workflow_runtime_repeat_index)
if node is None:
    node = slicer.mrmlScene.GetNodeByID(_longbonefracturereduction_cb_step_27_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_27'")

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[LongBoneFractureReduction] Step 'cb_step_27' processed with %d control points." % node.GetNumberOfControlPoints())
