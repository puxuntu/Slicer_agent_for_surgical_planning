import slicer
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
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

parameterNode = logic.getParameterNode()

# Ensure required node references are set
fibulaSegmentation = parameterNode.GetNodeReference('fibulaSegmentation')
if fibulaSegmentation is None:
    segNodes = slicer.util.getNodesByClass('vtkMRMLSegmentationNode')
    fibulaSegmentation = None
    for node in segNodes:
        name = node.GetName().lower()
        if 'fibula' in name:
            fibulaSegmentation = node
            break
    if fibulaSegmentation is None:
        raise RuntimeError('Fibula segmentation node not found. Ensure step 3/4 completed.')
    parameterNode.SetNodeReferenceID('fibulaSegmentation', fibulaSegmentation.GetID())

mandibularSegmentation = parameterNode.GetNodeReference('mandibularSegmentation')
if mandibularSegmentation is None:
    segNodes = slicer.util.getNodesByClass('vtkMRMLSegmentationNode')
    mandibularSegmentation = None
    for node in segNodes:
        name = node.GetName().lower()
        if 'mandibular' in name or 'mandible' in name:
            mandibularSegmentation = node
            break
    if mandibularSegmentation is None:
        raise RuntimeError('Mandibular segmentation node not found. Ensure step 3/4 completed.')
    parameterNode.SetNodeReferenceID('mandibularSegmentation', mandibularSegmentation.GetID())

# Set default parameter for useNonDecimatedBoneModelsForPreview if not set
if parameterNode.GetParameter('useNonDecimatedBoneModelsForPreview') == '':
    parameterNode.SetParameter('useNonDecimatedBoneModelsForPreview', 'True')
useNonDecimatedBoneModelsForPreviewChecked = parameterNode.GetParameter('useNonDecimatedBoneModelsForPreview') == 'True'

# Create bone models from the segmentations.
# logic.makeModels is not in the proven target list for this receiver; replicate
# its implementation using proven Slicer APIs.
wasModified = parameterNode.StartModify()

shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
sceneItemID = shNode.GetSceneItemID()
parentFolderItemID = shNode.GetItemByName('BoneReconstructionPlanner')
if not parentFolderItemID:
    parentFolderItemID = shNode.CreateFolderItem(sceneItemID, 'BoneReconstructionPlanner')
segmentationModelsFolder = shNode.GetItemByName('Segmentation Models')
if segmentationModelsFolder:
    shNode.RemoveItem(segmentationModelsFolder)
segmentationModelsFolder = shNode.CreateFolderItem(parentFolderItemID, 'Segmentation Models')

fibulaModelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', 'fibula')
mandibleModelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', 'mandible')
decimatedFibulaModelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', 'decimatedFibula')
decimatedMandibleModelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', 'decimatedMandible')

segmentations = [fibulaSegmentation, mandibularSegmentation]
models = [fibulaModelNode, mandibleModelNode]
decimatedModels = [decimatedFibulaModelNode, decimatedMandibleModelNode]

for i in range(2):
    models[i].CreateDefaultDisplayNodes()
    decimatedModels[i].CreateDefaultDisplayNodes()

    seg = segmentations[i]
    seg.GetSegmentation().CreateRepresentation(slicer.vtkSegmentationConverter.GetSegmentationClosedSurfaceRepresentationName())
    segmentID = seg.GetSegmentation().GetNthSegmentID(0)
    segment = seg.GetSegmentation().GetSegment(segmentID)
    segDisplayNode = seg.GetDisplayNode()
    segDisplayNode.SetSegmentVisibility3D(segmentID, False)

    segmentationLogic = slicer.modules.segmentations.logic()
    segmentationLogic.ExportSegmentToRepresentationNode(segment, models[i])

    modelDisplayNode = models[i].GetDisplayNode()
    decimatedModelDisplayNode = decimatedModels[i].GetDisplayNode()
    decimatedModelDisplayNode.SetColor(models[i].GetDisplayNode().GetColor())

    if useNonDecimatedBoneModelsForPreviewChecked:
        modelDisplayNode.SetVisibility(True)
        decimatedModelDisplayNode.SetVisibility(False)
    else:
        modelDisplayNode.SetVisibility(False)
        decimatedModelDisplayNode.SetVisibility(True)

    param = {
        'inputModel': models[i],
        'outputModel': decimatedModels[i],
        'reductionFactor': 0.95,
        'method': 'FastQuadric'
    }
    slicer.cli.runSync(slicer.modules.decimation, parameters=param)

    modelNodeItemID = shNode.GetItemByDataNode(models[i])
    shNode.SetItemParent(modelNodeItemID, segmentationModelsFolder)
    decimatedModelNodeItemID = shNode.GetItemByDataNode(decimatedModels[i])
    shNode.SetItemParent(decimatedModelNodeItemID, segmentationModelsFolder)

    if i == 0:
        singletonTag = slicer.FIBULA_VIEW_SINGLETON_TAG
        viewUpDirection = [0.0, 1.0, 0.0]
        cameraDirection = [1.0, 0.0, 0.0]
    else:
        singletonTag = slicer.MANDIBLE_VIEW_SINGLETON_TAG
        viewUpDirection = [0.0, 0.0, 1.0]
        cameraDirection = [0.0, -1.0, 0.0]
    viewNode = slicer.mrmlScene.GetSingletonNode(singletonTag, 'vtkMRMLViewNode')
    cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(viewNode)

    modelDisplayNode.AddViewNodeID(viewNode.GetID())
    decimatedModelDisplayNode.AddViewNodeID(viewNode.GetID())

    bounds = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    models[i].GetBounds(bounds)
    centroid = [(bounds[0] + bounds[1]) / 2.0, (bounds[2] + bounds[3]) / 2.0, (bounds[4] + bounds[5]) / 2.0]

    cameraNode.SetPosition([centroid[0] - cameraDirection[0] * 300,
                            centroid[1] - cameraDirection[1] * 300,
                            centroid[2] - cameraDirection[2] * 300])
    cameraNode.SetFocalPoint(centroid)
    cameraNode.SetViewUp(viewUpDirection)
    cameraNode.ResetClippingRange()

    if i == 0:
        parameterNode.SetParameter('fibulaCentroidX', str(centroid[0]))
        parameterNode.SetParameter('fibulaCentroidY', str(centroid[1]))
        parameterNode.SetParameter('fibulaCentroidZ', str(centroid[2]))
    else:
        parameterNode.SetParameter('mandibleCentroidX', str(centroid[0]))
        parameterNode.SetParameter('mandibleCentroidY', str(centroid[1]))
        parameterNode.SetParameter('mandibleCentroidZ', str(centroid[2]))

fibulaModelNode.SetName('fibula')
mandibleModelNode.SetName('mandible')

parameterNode.SetNodeReferenceID('fibulaModelNode', fibulaModelNode.GetID())
parameterNode.SetNodeReferenceID('mandibleModelNode', mandibleModelNode.GetID())
parameterNode.SetNodeReferenceID('decimatedFibulaModelNode', decimatedFibulaModelNode.GetID())
parameterNode.SetNodeReferenceID('decimatedMandibleModelNode', decimatedMandibleModelNode.GetID())

parameterNode.EndModify(wasModified)

print('[BoneReconstructionPlanner] Step 5 complete: Models generated.')