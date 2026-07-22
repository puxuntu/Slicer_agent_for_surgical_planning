# --- OrbitalFractureReconstruction: Manually click and adjust on the Slice views to create the ROI for the "Orbital_Region". (Process) ---
import slicer
from SlicerAIAgentLib.workflow_state import resolve_interaction_node

node = resolve_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_3", "vtkMRMLMarkupsROINode", _workflow_runtime_repeat_index)
if node is None:
    node = slicer.mrmlScene.GetNodeByID(_orbitalfracturereconstruction_cb_step_3_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_3'")

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[OrbitalFractureReconstruction] Step 'cb_step_3' processed with %d control points." % node.GetNumberOfControlPoints())
