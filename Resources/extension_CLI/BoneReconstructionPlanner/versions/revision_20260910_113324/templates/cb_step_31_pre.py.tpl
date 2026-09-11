# [revised] Rewritten by the runtime revision agent (revision_20260909_215845).
# Pre-revision package backed up under versions/revision_20260909_215845/.
# Requested: do not show the decimatedMandible model in this step
# Change: Hide the decimatedMandible model display while this step is active and restore its previous visibility afterwards.
# --- BoneReconstructionPlanner: Manually adjust the mandibular cut planes in the mandible 3D view by dragging the visible plane interaction handles. (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# The decimatedMandible model sits in front of the cut planes in the mandible 3D view,
# so keep it hidden while this step is active. Only that model is touched: its current
# visibility is saved here and put back by the process template when the user is done.
_cb31_decimatedMandible = None
try:
    _cb31_decimatedMandible = logic.getParameterNode().GetNodeReference("decimatedMandibleModelNode")
except NameError:
    _cb31_decimatedMandible = None
if _cb31_decimatedMandible is None:
    _cb31_decimatedMandible = slicer.mrmlScene.GetFirstNodeByName("decimatedMandible")
_cb31_decimatedMandible_wasVisible = None
if _cb31_decimatedMandible is not None:
    _cb31_decimatedMandibleDisplayNode = _cb31_decimatedMandible.GetDisplayNode()
    if _cb31_decimatedMandibleDisplayNode is not None:
        _cb31_decimatedMandible_wasVisible = bool(_cb31_decimatedMandibleDisplayNode.GetVisibility())
        _cb31_decimatedMandibleDisplayNode.SetVisibility(False)

# Reuse the markup node created by a previous step (do not create a duplicate).
# Prefer a node THIS extension owns. Slicer extensions tag their own nodes
# with MRML attributes in their module's namespace, so an attribute named
# "BoneReconstructionPlanner.*" identifies the step's real target; picking the most
# recent node of the class alone can land on an unrelated node of the same
# type (a scene may hold several).
nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsPlaneNode")
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
    if any(str(_n).startswith("BoneReconstructionPlanner.") for _n in _names):
        _owned.append(candidate)
if _owned:
    node = _owned[-1]
elif _candidates:
    node = _candidates[-1]
else:
    raise RuntimeError("No vtkMRMLMarkupsPlaneNode found from previous placement step.")

# The cut plane nodes and their display nodes are produced by the extension's
# own cut-plane workflow; here only make the selected plane visible and active
# so its existing interaction handles can be dragged in the 3D views.
displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)
slicer.modules.markups.logic().SetActiveListID(node)
_bonereconstructionplanner_cb_step_31_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_31", _bonereconstructionplanner_cb_step_31_id, _workflow_runtime_repeat_index)

print("[BoneReconstructionPlanner] Please Manually adjust the mandibular cut planes in the 3D view by dragging their visible interaction handles.")
print("When finished, press the 'Done' button in the workflow panel.")
