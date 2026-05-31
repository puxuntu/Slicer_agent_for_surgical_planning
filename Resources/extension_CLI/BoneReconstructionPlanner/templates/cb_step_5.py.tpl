try:
    import BoneReconstructionPlanner
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
except ImportError:
    raise ImportError(
        "The BoneReconstructionPlanner extension is not installed. "
        "Please install it using the Slicer Extension Manager."
    )

# Reuse or create logic instance
try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

# Get parameter node
parameterNode = logic.getParameterNode()

# Ensure fibula segmentation reference exists
fibulaSeg = parameterNode.GetNodeReference("fibulaSegmentation")
if fibulaSeg is None:
    segNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    for i in range(segNodes.GetNumberOfItems()):
        n = segNodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            fibulaSeg = n
            break
    if fibulaSeg is None:
        raise RuntimeError("Fibula segmentation node not found in the scene.")
    parameterNode.SetNodeReferenceID("fibulaSegmentation", fibulaSeg.GetID())

# Ensure mandibular segmentation reference exists
mandibularSeg = parameterNode.GetNodeReference("mandibularSegmentation")
if mandibularSeg is None:
    segNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    for i in range(segNodes.GetNumberOfItems()):
        n = segNodes.GetItemAsObject(i)
        if "mandib" in n.GetName().lower():  # covers mandible, mandibular
            mandibularSeg = n
            break
    if mandibularSeg is None:
        raise RuntimeError("Mandibular segmentation node not found in the scene.")
    parameterNode.SetNodeReferenceID("mandibularSegmentation", mandibularSeg.GetID())

# Set preview option if not already set (default to False)
if not parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview"):
    parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", "False")

# Run the model generation
logic.makeModels()

print("Step 5 completed: bone models created.")