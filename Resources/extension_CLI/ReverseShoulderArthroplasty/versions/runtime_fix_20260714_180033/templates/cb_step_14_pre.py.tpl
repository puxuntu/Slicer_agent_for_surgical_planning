# --- ReverseShoulderArthroplasty: Manually click on the glenoid cavity surface to select a point for the "Prosthesis_center_point". (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node, resolve_interaction_node

# Retrieve the markups node created by step 13 (do not create a duplicate)
node = resolve_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_13", _workflow_runtime_repeat_index)

if node is None:
    raise RuntimeError("No vtkMRMLMarkupsFiducialNode found from step 13 placement.")

# Ensure the node has a display node for visibility in 3D view
if node.GetDisplayNode() is None:
    try:
        node.CreateDefaultDisplayNodes()
    except AttributeError:
        # If CreateDefaultDisplayNodes is not available (unlikely), skip
        pass

displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)

slicer.modules.markups.logic().SetActiveListID(node)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToSinglePlaceMode()

_reverseshoulderarthroplasty_cb_step_14_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_14", _reverseshoulderarthroplasty_cb_step_14_id, _workflow_runtime_repeat_index)

print("[ReverseShoulderArthroplasty] Please Click on the glenoid cavity surface in the 3D view to place the point.")
print("When finished, press the 'Done' button in the workflow panel.")
