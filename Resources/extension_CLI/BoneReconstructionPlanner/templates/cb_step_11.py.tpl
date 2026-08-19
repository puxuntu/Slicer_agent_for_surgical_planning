# --- BoneReconstructionPlanner: Click the "Add mandibular curve" button. (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'BoneReconstructionPlanner':
    try:
        slicer.util.selectModule('BoneReconstructionPlanner')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'BoneReconstructionPlanner': {_module_enter_error}")
# precondition:end

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
_bonereconstructionplanner_logic = logic

# Create the mandibular curve markups node and activate placement mode.
# This reproduces the effect of the extension's "Add mandibular curve" button
# using the same Slicer APIs as the extension logic.
curveNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsCurveNode")
slicer.mrmlScene.AddNode(curveNode)
slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(curveNode)

shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
parentFolderID = shNode.GetItemByName("BoneReconstructionPlanner")
if not parentFolderID:
    parentFolderID = shNode.CreateFolderItem(shNode.GetSceneItemID(), "BoneReconstructionPlanner")
shNode.SetItemParent(shNode.GetItemByDataNode(curveNode), parentFolderID)

curveNode.SetName(slicer.mrmlScene.GetUniqueNameByString("mandibularCurve"))

displayNode = curveNode.GetDisplayNode()
mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
if displayNode is not None and mandibleViewNode is not None:
    displayNode.AddViewNodeID(mandibleViewNode.GetID())

# Setup placement
slicer.modules.markups.logic().SetActiveListID(curveNode)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToSinglePlaceMode()

remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_11", curveNode.GetID(), _workflow_runtime_repeat_index)

print("[BoneReconstructionPlanner] Placement started for step 'cb_step_11'.")