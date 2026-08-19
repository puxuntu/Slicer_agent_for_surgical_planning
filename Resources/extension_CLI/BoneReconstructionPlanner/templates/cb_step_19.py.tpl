# --- BoneReconstructionPlanner: Click "Add fibula line" button. (Setup) ---
import slicer
import numpy as np
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

parameterNode = logic.getParameterNode()

# Create the fibula line markups node and activate placement mode.
# This reproduces the effect of the extension's "Add fibula line" button
# using the same Slicer APIs as the extension logic.
lineNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsLineNode")
slicer.mrmlScene.AddNode(lineNode)
slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(lineNode)

shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
parentFolderID = shNode.GetItemByName("BoneReconstructionPlanner")
if not parentFolderID:
    parentFolderID = shNode.CreateFolderItem(shNode.GetSceneItemID(), "BoneReconstructionPlanner")
shNode.SetItemParent(shNode.GetItemByDataNode(lineNode), parentFolderID)

lineNode.SetName(slicer.mrmlScene.GetUniqueNameByString("fibulaLine"))

displayNode = lineNode.GetDisplayNode()
if displayNode is not None:
    fibulaViewNode = slicer.mrmlScene.GetSingletonNode(slicer.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
    if fibulaViewNode is not None:
        displayNode.AddViewNodeID(fibulaViewNode.GetID())

    # The extension also shows the line in Red when the fibula volume is the primary one.
    fibulaCentroidX = parameterNode.GetParameter("fibulaCentroidX")
    if fibulaCentroidX != "":
        scalarVolume = parameterNode.GetNodeReference("currentScalarVolume")
        redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")
        if scalarVolume is not None and redSliceNode is not None:
            fibulaCentroid = np.array([
                float(fibulaCentroidX),
                float(parameterNode.GetParameter("fibulaCentroidY")),
                float(parameterNode.GetParameter("fibulaCentroidZ"))
            ])
            mandibleCentroid = np.array([
                float(parameterNode.GetParameter("mandibleCentroidX")),
                float(parameterNode.GetParameter("mandibleCentroidY")),
                float(parameterNode.GetParameter("mandibleCentroidZ"))
            ])
            bounds = [0, 0, 0, 0, 0, 0]
            scalarVolume.GetBounds(bounds)
            bounds = np.array(bounds)
            centerOfScalarVolume = np.array([
                (bounds[0] + bounds[1]) / 2,
                (bounds[2] + bounds[3]) / 2,
                (bounds[4] + bounds[5]) / 2
            ])
            if np.linalg.norm(fibulaCentroid - centerOfScalarVolume) < np.linalg.norm(mandibleCentroid - centerOfScalarVolume):
                displayNode.AddViewNodeID(redSliceNode.GetID())

# Setup placement
slicer.modules.markups.logic().SetActiveListID(lineNode)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToSinglePlaceMode()

remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_19", lineNode.GetID(), _workflow_runtime_repeat_index)

print("[BoneReconstructionPlanner] Placement started for step 'cb_step_19'.")