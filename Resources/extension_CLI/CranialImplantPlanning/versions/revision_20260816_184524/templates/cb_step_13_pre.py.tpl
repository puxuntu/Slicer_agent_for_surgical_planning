# [runtime-fixed] Auto-revised by runtime self-correction at 20260816_184254.
# Pre-revision templates backed up under versions/runtime_fix_20260816_184254/.
# Fixed runtime error: No vtkMRMLMarkupsROINode found from previous placement step.
# [Workflow runtime] Hidden generated-CLI workflow context
_workflow_runtime_extension = 'CranialImplantPlanning'
_workflow_runtime_id = 'CranialImplantPlanning_1786919982267'
_workflow_runtime_step = 'cb_step_13'
_workflow_runtime_repeat_index = 0
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# --- Repair: CranialImplantPlanning cb_step_13 (adjust ROI) ---
# The previous placement step left no ROI node in the scene, so instead of
# failing, reuse an existing ROI if one exists, otherwise recreate it fitted
# to the skull bounds (same behavior as the extension's "Add ROI" button).

def _roi_candidate_names(node):
    try:
        return node.GetAttributeNames() or []
    except Exception:
        return []

roiNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsROINode")
roiCandidates = []
for i in range(roiNodes.GetNumberOfItems()):
    item = roiNodes.GetItemAsObject(i)
    if item is not None:
        roiCandidates.append(item)

if roiCandidates:
    # Prefer a node owned by this extension (attribute in its namespace), else the most recent ROI.
    owned = [c for c in roiCandidates if any(str(n).startswith("CranialImplantPlanning.") for n in _roi_candidate_names(c))]
    roiNode = (owned or roiCandidates)[-1]
else:
    # No ROI exists yet -> create one, fitted to the skull segmentation bounds.
    roiNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode", "CropROI")
    roiNode.CreateDefaultDisplayNodes()

    bounds = [0.0] * 6
    segNode = slicer.mrmlScene.GetFirstNodeByName("Cranial_Segmentation")
    if segNode is None:
        segNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
        if segNodes.GetNumberOfItems() > 0:
            segNode = segNodes.GetItemAsObject(0)
    if segNode is not None:
        segNode.GetRASBounds(bounds)
    else:
        modelNode = slicer.mrmlScene.GetFirstNodeByName("Skull (drawing target)")
        if modelNode is not None:
            modelNode.GetRASBounds(bounds)

    roiNode.SetCenter((bounds[0] + bounds[1]) / 2.0, (bounds[2] + bounds[3]) / 2.0, (bounds[4] + bounds[5]) / 2.0)
    roiNode.SetSize(max(bounds[1] - bounds[0], 1.0), max(bounds[3] - bounds[2], 1.0), max(bounds[5] - bounds[4], 1.0))

# Show only the ROI boundary: enable scale handles for resizing, keep the
# displacement (translation) and rotation handlers hidden.
displayNode = roiNode.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)
    roiDisplayNode = slicer.vtkMRMLMarkupsROIDisplayNode.SafeDownCast(displayNode)
    if roiDisplayNode is not None:
        try:
            roiDisplayNode.SetHandlesInteractive(True)
            roiDisplayNode.SetTranslationHandleVisibility(False)
            roiDisplayNode.SetScaleHandleVisibility(True)
            roiDisplayNode.SetRotationHandleVisibility(False)
        except Exception:
            pass

slicer.modules.markups.logic().SetActiveListID(roiNode)
_cranialimplantplanning_cb_step_13_id = roiNode.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_13", _cranialimplantplanning_cb_step_13_id, _workflow_runtime_repeat_index)

print("[CranialImplantPlanning] Please adjust the ROI boundaries on the slice views to retain the skull portion.")
print("When finished, press the 'Done' button in the workflow panel.")
