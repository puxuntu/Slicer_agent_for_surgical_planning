# --- BoneReconstructionPlanner: Click the Add cut plane button. (Setup) ---
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
        print('[BoneReconstructionPlanner] Warning: could not activate module BoneReconstructionPlanner: ' + repr(_module_enter_error))
# precondition:end

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
_bonereconstructionplanner_logic = logic

parameterNode = logic.getParameterNode()

# Advance the color index used to pick mandibular plane colors (same as extension logic).
colorIndexStr = parameterNode.GetParameter('colorIndex')
if colorIndexStr != '':
    colorIndex = int(colorIndexStr) + 1
    parameterNode.SetParameter('colorIndex', str(colorIndex))
else:
    colorIndex = 0
    parameterNode.SetParameter('colorIndex', str(colorIndex))

# Create the mandibular cut plane markups node and activate placement mode.
# This reproduces the effect of the extension Add cut plane button
# using the same Slicer APIs as the extension logic.
planeNode = slicer.mrmlScene.CreateNodeByClass('vtkMRMLMarkupsPlaneNode')
slicer.mrmlScene.AddNode(planeNode)
slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(planeNode)

shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
mandibularPlanesFolderID = shNode.GetItemByName('Mandibular planes')
if not mandibularPlanesFolderID:
    parentFolderID = shNode.GetItemByName('BoneReconstructionPlanner')
    if not parentFolderID:
        parentFolderID = shNode.CreateFolderItem(shNode.GetSceneItemID(), 'BoneReconstructionPlanner')
    mandibularPlanesFolderID = shNode.CreateFolderItem(parentFolderID, 'Mandibular planes')
shNode.SetItemParent(shNode.GetItemByDataNode(planeNode), mandibularPlanesFolderID)

planeNode.SetName(slicer.mrmlScene.GetUniqueNameByString('mandibularPlane'))
planeNode.SetAttribute('isMandibularPlane', 'True')
planeNode.SetSize(50.0, 50.0)
planeNode.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneType3Points)

# Pick the same medium-chart color used by the extension logic.
colorTableNode = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
if colorTableNode is not None:
    colorTable = colorTableNode.GetLookupTable()
    colorWithAlpha = colorTable.GetTableValue(colorIndex % 8)
    color = [colorWithAlpha[0], colorWithAlpha[1], colorWithAlpha[2]]
else:
    color = None

displayNode = slicer.vtkMRMLMarkupsDisplayNode.SafeDownCast(planeNode.GetDisplayNode())
if displayNode is not None:
    displayNode.SetGlyphScale(2.5)
    if color is not None:
        displayNode.SetSelectedColor(color)
    mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, 'vtkMRMLViewNode')
    if mandibleViewNode is not None:
        displayNode.AddViewNodeID(mandibleViewNode.GetID())

# Setup placement
slicer.modules.markups.logic().SetActiveListID(planeNode)
interactionNode = slicer.mrmlScene.GetNodeByID('vtkMRMLInteractionNodeSingleton')
if interactionNode is not None:
    interactionNode.SwitchToSinglePlaceMode()

remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, 'cb_step_18', planeNode.GetID(), _workflow_runtime_repeat_index)

print('[BoneReconstructionPlanner] Placement started for step cb_step_17.')