# --- ZygomaticImplantPlanner: Manually adjust the paths. (Process) ---
import slicer
from SlicerAIAgentLib.workflow_state import resolve_interaction_node

node = resolve_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_26", "vtkMRMLMarkupsLineNode", _workflow_runtime_repeat_index)
if node is None:
    node = slicer.mrmlScene.GetNodeByID(_zygomaticimplantplanner_cb_step_26_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_26'")

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[ZygomaticImplantPlanner] Step 'cb_step_26' processed with %d control points." % node.GetNumberOfControlPoints())
