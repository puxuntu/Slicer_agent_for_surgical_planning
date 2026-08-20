# --- PelvicFracturePlanning: Manually click to add a cut point and adjust the position and rotation of the cutting plane. (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# Reuse the markup node created by onManualSplit() in the previous step.
# Prefer a node THIS extension owns. Slicer extensions tag their own nodes
# with MRML attributes in their module's namespace, so an attribute named
# "PelvicFracturePlanning.*" identifies the step's real target; picking the most
# recent node of the class alone can land on an unrelated node of the same
# type (a scene may hold several).
nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsFiducialNode")
_candidates = []
for i in range(nodes.GetNumberOfItems()):
    candidate = nodes.GetItemAsObject(i)
    if candidate is not None:
        _candidates.append(candidate)
_owned = []
for candidate in _candidates:
    try:
        _names = candidate.GetAttributeNames() or []
    except Exception:
        _names = []
    if any(str(_n).startswith("PelvicFracturePlanning.") for _n in _names):
        _owned.append(candidate)
node = (_owned or _candidates)[-1] if (_owned or _candidates) else None
if node is None:
    raise RuntimeError("No vtkMRMLMarkupsFiducialNode found from previous placement step.")

# The placement node is created and made interactive by the extension's
# onManualSplit() method, so no display-node setup is required here.
_pelvicfractureplanning_cb_step_8_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_8", _pelvicfractureplanning_cb_step_8_id, _workflow_runtime_repeat_index)

print("[PelvicFracturePlanning] Please Click in the view to add a cut point, then adjust the cutting plane's position and rotation.")
print("When finished, press the 'Done' button in the workflow panel.")
