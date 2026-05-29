try:
    _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

logic = _bonereconstructionplanner_logic
parameterNode = logic.getParameterNode()

# Ensure fibula segmentation node is set
fibulaSegNode = parameterNode.GetNodeReference("fibulaSegmentation")
if fibulaSegNode is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            fibulaSegNode = n
            break
    if fibulaSegNode is not None:
        parameterNode.SetNodeReferenceID("fibulaSegmentation", fibulaSegNode.GetID())

# Ensure mandibular segmentation node is set
mandibularSegNode = parameterNode.GetNodeReference("mandibularSegmentation")
if mandibularSegNode is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "mandibular" in n.GetName().lower():
            mandibularSegNode = n
            break
    if mandibularSegNode is not None:
        parameterNode.SetNodeReferenceID("mandibularSegmentation", mandibularSegNode.GetID())

# Optionally set default for useNonDecimatedBoneModelsForPreview if needed
# parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", "False")

logic.makeModels()
print("[BoneReconstructionPlanner] Step 4 (makeModels) completed.")