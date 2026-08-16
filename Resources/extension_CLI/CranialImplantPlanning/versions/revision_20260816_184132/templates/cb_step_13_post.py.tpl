# --- CranialImplantPlanning: Manually adjust the boundaries of the ROI to retain the skull portion. (Process) ---
import slicer
from SlicerAIAgentLib.workflow_state import resolve_interaction_node

node = resolve_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_13", "vtkMRMLMarkupsROINode", _workflow_runtime_repeat_index)
if node is None:
    node = slicer.mrmlScene.GetNodeByID(_cranialimplantplanning_cb_step_13_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_13'")

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[CranialImplantPlanning] Step 'cb_step_13' processed with %d control points." % node.GetNumberOfControlPoints())
