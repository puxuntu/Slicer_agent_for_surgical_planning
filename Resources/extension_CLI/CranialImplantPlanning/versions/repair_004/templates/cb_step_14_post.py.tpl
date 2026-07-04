# --- CranialImplantPlanning: Manually draw the curve on the skull model to enclose the fractured skull portion. (Process) ---
import slicer
from SlicerAIAgentLib.workflow_state import resolve_interaction_node

node = resolve_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_14", "vtkMRMLMarkupsClosedCurveNode", _workflow_runtime_repeat_index)
if node is None:
    node = slicer.mrmlScene.GetNodeByID(_cranialimplantplanning_cb_step_14_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_14'")

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[CranialImplantPlanning] Step 'cb_step_14' processed with %d control points." % node.GetNumberOfControlPoints())
