# --- CranialImplantPlanning: Manually adjust the boundaries of the ROI to retain the skull portion. (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# Reuse the markup node created by a previous step (do not create a duplicate).
# Prefer a node THIS extension owns. Slicer extensions tag their own nodes
# with MRML attributes in their module's namespace, so an attribute named
# "CranialImplantPlanning.*" identifies the step's real target; picking the most
# recent node of the class alone can land on an unrelated node of the same
# type (a scene may hold several).
nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsROINode")
_candidates = []
for i in range(nodes.GetNumberOfItems()):
    candidate = nodes.GetItemAsObject(i)
    if candidate is not None:
        _candidates.append(candidate)
if not _candidates:
    raise RuntimeError("No vtkMRMLMarkupsROINode found from previous placement step.")
_owned = []
for candidate in _candidates:
    try:
        _names = candidate.GetAttributeNames() or []
    except Exception:
        _names = []
    if any(str(_n).startswith("CranialImplantPlanning.") for _n in _names):
        _owned.append(candidate)
node = (_owned or _candidates)[-1]

displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)
# Enable interaction handles for adjusting the existing markup.
if displayNode is not None:
    roiDisplayNode = slicer.vtkMRMLMarkupsROIDisplayNode.SafeDownCast(displayNode)
    if roiDisplayNode is not None:
        try:
            roiDisplayNode.SetHandlesInteractive(True)
            roiDisplayNode.SetTranslationHandleVisibility(True)
            roiDisplayNode.SetScaleHandleVisibility(True)
            roiDisplayNode.SetRotationHandleVisibility(True)
        except Exception:
            pass
slicer.modules.markups.logic().SetActiveListID(node)
_cranialimplantplanning_cb_step_13_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_13", _cranialimplantplanning_cb_step_13_id, _workflow_runtime_repeat_index)

print("[CranialImplantPlanning] Please Adjust the ROI boundaries on the slice views to retain the skull portion.")
print("When finished, press the 'Done' button in the workflow panel.")