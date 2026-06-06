try:
    _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

logic = _bonereconstructionplanner_logic
parameterNode = logic.getParameterNode()

# Ensure fibula segmentation node reference exists; if not, search scene
fibulaSegNode = parameterNode.GetNodeReference("fibulaSegmentation")
if fibulaSegNode is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            fibulaSegNode = n
            break
    if fibulaSegNode is None:
        raise ValueError("Could not find a segmentation node containing 'fibula' in its name.")
    parameterNode.SetNodeReferenceID("fibulaSegmentation", fibulaSegNode.GetID())

# Ensure mandibular segmentation node reference exists
mandSegNode = parameterNode.GetNodeReference("mandibularSegmentation")
if mandSegNode is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "mandibular" in n.GetName().lower() or "mandible" in n.GetName().lower():
            mandSegNode = n
            break
    if mandSegNode is None:
        raise ValueError("Could not find a segmentation node containing 'mandibular' or 'mandible' in its name.")
    parameterNode.SetNodeReferenceID("mandibularSegmentation", mandSegNode.GetID())

# Set default for useNonDecimatedBoneModelsForPreview if not already set
currentVal = parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview")
if not currentVal:  # empty string means not set
    parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", "True")

# Call the method
logic.makeModels()

print("Step 5 (makeModels) completed successfully.")