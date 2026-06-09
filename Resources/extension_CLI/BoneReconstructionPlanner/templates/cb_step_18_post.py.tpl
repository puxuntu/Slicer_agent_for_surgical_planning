# --- BoneReconstructionPlanner: Place one mandibular cut plane using the extension's Add cut plane workflow. If the user requested N cut planes, repeat the Add cut plane + place plane interaction N times. Do not store these planes as a rotation plane; they are mandibular cut planes managed by the extension. (Process) ---
import slicer
from SlicerAIAgentLib.workflow_state import resolve_interaction_node

node = resolve_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_18", "vtkMRMLMarkupsPlaneNode", _workflow_runtime_repeat_index)
if node is None:
    node = slicer.mrmlScene.GetNodeByID(_bonereconstructionplanner_cb_step_18_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_18'")

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[BoneReconstructionPlanner] Step 'cb_step_18' processed with %d control points." % node.GetNumberOfControlPoints())
