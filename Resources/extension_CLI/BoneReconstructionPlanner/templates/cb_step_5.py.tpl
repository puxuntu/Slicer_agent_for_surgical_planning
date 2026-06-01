try:
    _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic as _BoneReconstructionPlannerLogic
    _bonereconstructionplanner_logic = _BoneReconstructionPlannerLogic()

logic = _bonereconstructionplanner_logic
parameterNode = logic.getParameterNode()

# Ensure fibula segmentation is set
fibulaSegmentation = parameterNode.GetNodeReference("fibulaSegmentation")
if not fibulaSegmentation:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            fibulaSegmentation = n
            break
    if fibulaSegmentation:
        parameterNode.SetNodeReferenceID("fibulaSegmentation", fibulaSegmentation.GetID())

# Ensure mandibular segmentation is set
mandibularSegmentation = parameterNode.GetNodeReference("mandibularSegmentation")
if not mandibularSegmentation:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "mandib" in n.GetName().lower():
            mandibularSegmentation = n
            break
    if mandibularSegmentation:
        parameterNode.SetNodeReferenceID("mandibularSegmentation", mandibularSegmentation.GetID())

# Optional: set useNonDecimatedBoneModelsForPreview (defaults to False if not set)
if not parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview"):
    parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", "False")

logic.makeModels()

print("[BoneReconstructionPlanner] Step 5 complete: models created from segmentations.")