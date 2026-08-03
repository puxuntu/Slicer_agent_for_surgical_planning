# --- ZygomaticImplantPlanner: Manually adjust the separation plane. (Process) ---
import slicer
from SlicerAIAgentLib.workflow_state import resolve_interaction_node

node = resolve_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_18", "vtkMRMLMarkupsPlaneNode", _workflow_runtime_repeat_index)
if node is None:
    node = slicer.mrmlScene.GetNodeByID(_zygomaticimplantplanner_cb_step_18_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_18'")

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[ZygomaticImplantPlanner] Step 'cb_step_18' processed with %d control points." % node.GetNumberOfControlPoints())
