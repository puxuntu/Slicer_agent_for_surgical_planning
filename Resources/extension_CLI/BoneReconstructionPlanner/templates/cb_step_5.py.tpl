from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()

parameterNode = logic.getParameterNode()

# Ensure required parameter is set with default if not already
if parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview") == "":
    parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", "True")

# Ensure fibula segmentation node reference exists
if parameterNode.GetNodeReference("fibulaSegmentation") is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    fibulaSegmentation = None
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            fibulaSegmentation = n
            break
    if fibulaSegmentation:
        parameterNode.SetNodeReferenceID("fibulaSegmentation", fibulaSegmentation.GetID())
    else:
        raise RuntimeError("No fibula segmentation found in the scene. Run previous step first.")

# Ensure mandibular segmentation node reference exists
if parameterNode.GetNodeReference("mandibularSegmentation") is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    mandibularSegmentation = None
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "mandibular" in n.GetName().lower() or "mandible" in n.GetName().lower():
            mandibularSegmentation = n
            break
    if mandibularSegmentation:
        parameterNode.SetNodeReferenceID("mandibularSegmentation", mandibularSegmentation.GetID())
    else:
        raise RuntimeError("No mandibular segmentation found in the scene. Run previous step first.")

logic.makeModels()

_bonereconstructionplanner_logic = logic
print("[BoneReconstructionPlanner] Step 5 - Models created.")