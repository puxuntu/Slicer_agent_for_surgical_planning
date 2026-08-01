# --- ZygomaticImplantPlanner: Manually adjust the boundary planes. (Process) ---
import slicer
from SlicerAIAgentLib.workflow_state import resolve_interaction_node

node = resolve_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_22", "vtkMRMLMarkupsPlaneNode", _workflow_runtime_repeat_index)
if node is None:
    node = slicer.mrmlScene.GetNodeByID(_zygomaticimplantplanner_cb_step_22_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_22'")

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[ZygomaticImplantPlanner] Step 'cb_step_22' processed with %d control points." % node.GetNumberOfControlPoints())
