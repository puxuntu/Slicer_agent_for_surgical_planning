# [runtime-fixed] Auto-revised by runtime self-correction at 20260714_180146.
# Pre-revision templates backed up under versions/runtime_fix_20260714_180146/.
# Fixed runtime error: invalid literal for int() with base 10: 'vtkMRMLMarkupsFiducialNode1'
import slicer

# Find the Prosthesis_center_point markups node by name (already exists in the scene)
node = slicer.util.getNode('Prosthesis_center_point')
if node is None:
    # Fallback: search by ID
    node = slicer.mrmlScene.GetNodeByID('vtkMRMLMarkupsFiducialNode1')

if node is None:
    raise RuntimeError("Node 'Prosthesis_center_point' not found in the scene for step 'cb_step_14'")

# Register the node in the workflow state so subsequent steps can find it
# Function signature: remember_interaction_node(extension, workflow_id, step_id, node_class, repeat_index=0)
# Do NOT pass node_id — the function resolves the node by class name internally
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_14", "vtkMRMLMarkupsFiducialNode")

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[ReverseShoulderArthroplasty] Step 'cb_step_14' processed with %d control points." % node.GetNumberOfControlPoints())
