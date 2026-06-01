try:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
except ImportError:
    raise ImportError("BoneReconstructionPlanner extension is not installed. Please install it from the Slicer Extension Manager.")

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

parameterNode = logic.getParameterNode()

# Ensure fibula segmentation reference exists
fibulaSegmentation = parameterNode.GetNodeReference("fibulaSegmentation")
if fibulaSegmentation is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            fibulaSegmentation = n
            parameterNode.SetNodeReferenceID("fibulaSegmentation", n.GetID())
            break
    if fibulaSegmentation is None:
        raise ValueError("Fibula segmentation node not found in the scene. Please run previous steps first.")

# Ensure mandibular segmentation reference exists
mandibularSegmentation = parameterNode.GetNodeReference("mandibularSegmentation")
if mandibularSegmentation is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "mandibular" in n.GetName().lower():
            mandibularSegmentation = n
            parameterNode.SetNodeReferenceID("mandibularSegmentation", n.GetID())
            break
    if mandibularSegmentation is None:
        raise ValueError("Mandibular segmentation node not found in the scene. Please run previous steps first.")

# Optionally ensure useNonDecimatedBoneModelsForPreview is set (default will be False if not set)
# We do not override it unless explicitly required by user preference.

logic.makeModels()

print("[BoneReconstructionPlanner] Step 5 (makeModels) completed. Models and decimated models created.")