import slicer
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
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

parameterNode = logic.getParameterNode()

# Ensure required node references are set
fibulaSegmentation = parameterNode.GetNodeReference("fibulaSegmentation")
if fibulaSegmentation is None:
    # Search for fibula segmentation node
    segNodes = slicer.util.getNodesByClass("vtkMRMLSegmentationNode")
    fibulaSegmentation = None
    for node in segNodes:
        name = node.GetName().lower()
        if "fibula" in name:
            fibulaSegmentation = node
            break
    if fibulaSegmentation is None:
        raise RuntimeError("Fibula segmentation node not found. Ensure step 3/4 completed.")
    parameterNode.SetNodeReferenceID("fibulaSegmentation", fibulaSegmentation.GetID())

mandibularSegmentation = parameterNode.GetNodeReference("mandibularSegmentation")
if mandibularSegmentation is None:
    segNodes = slicer.util.getNodesByClass("vtkMRMLSegmentationNode")
    mandibularSegmentation = None
    for node in segNodes:
        name = node.GetName().lower()
        if "mandibular" in name or "mandible" in name:
            mandibularSegmentation = node
            break
    if mandibularSegmentation is None:
        raise RuntimeError("Mandibular segmentation node not found. Ensure step 3/4 completed.")
    parameterNode.SetNodeReferenceID("mandibularSegmentation", mandibularSegmentation.GetID())

# Set default parameter for useNonDecimatedBoneModelsForPreview if not set
if parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview") == "":
    parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", "True")

# Call the method
logic.makeModels()

print("[BoneReconstructionPlanner] Step 5 complete: Models generated.")
