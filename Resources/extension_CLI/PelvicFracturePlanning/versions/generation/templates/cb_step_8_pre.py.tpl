# --- PelvicFracturePlanning: Manually click to add a cut point and adjust the position and rotation of the cutting plane. (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# The interaction node is created by the extension's onManualSplit() in the
# previous step. Reuse the most recent vtkMRMLMarkupsFiducialNode.
nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsFiducialNode")
_candidates = []
for i in range(nodes.GetNumberOfItems()):
    candidate = nodes.GetItemAsObject(i)
    if candidate is not None:
        _candidates.append(candidate)
if not _candidates:
    raise RuntimeError("No vtkMRMLMarkupsFiducialNode found from previous placement step.")
node = _candidates[-1]

_pelvicfractureplanning_cb_step_8_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_8", _pelvicfractureplanning_cb_step_8_id, _workflow_runtime_repeat_index)

print("[PelvicFracturePlanning] Please Place a cut point and adjust the position and rotation of the manual cutting plane.")
print("When finished, press the 'Done' button in the workflow panel.")
