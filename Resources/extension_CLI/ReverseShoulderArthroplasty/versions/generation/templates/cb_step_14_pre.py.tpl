# --- ReverseShoulderArthroplasty: Manually click on the glenoid cavity surface to select a point for the "Prosthesis_center_point". (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import resolve_interaction_node, remember_interaction_node

# First, attempt to retrieve the markup node from workflow state (should be from step 13)
node = resolve_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_13", "vtkMRMLMarkupsFiducialNode", _workflow_runtime_repeat_index)
if node is None:
    # Fallback: try to find the most recently created fiducial node
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsFiducialNode")
    for i in range(nodes.GetNumberOfItems() - 1, -1, -1):
        candidate = nodes.GetItemAsObject(i)
        if candidate is not None:
            node = candidate
            break
if node is None:
    raise RuntimeError("No vtkMRMLMarkupsFiducialNode found for placement step.")

# Ensure node is visible
displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)

# Set as active list for placement
slicer.modules.markups.logic().SetActiveListID(node)

# Switch to single place mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToSinglePlaceMode()

# Remember node for post step
_reverseshoulderarthroplasty_cb_step_14_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_14", _reverseshoulderarthroplasty_cb_step_14_id, _workflow_runtime_repeat_index)

print('[ReverseShoulderArthroplasty] Please manually click on the glenoid cavity surface to select a point for the "Prosthesis_center_point".')
print("When finished, press the 'Done' button in the workflow panel.")
