# --- PelvicFracturePlanning: Manually click to add a cut point and adjust the position and rotation of the cutting plane. (Process) ---
import slicer
from SlicerAIAgentLib.workflow_state import resolve_interaction_node

node = resolve_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_7", "vtkMRMLMarkupsPlaneNode", _workflow_runtime_repeat_index)
if node is None:
    node = slicer.mrmlScene.GetNodeByID(_pelvicfractureplanning_cb_step_7_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_7'")

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[PelvicFracturePlanning] Step 'cb_step_7' processed with %d control points." % node.GetNumberOfControlPoints())
