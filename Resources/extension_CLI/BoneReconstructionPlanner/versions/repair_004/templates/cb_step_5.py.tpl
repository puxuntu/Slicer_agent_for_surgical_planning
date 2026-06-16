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

# Ensure fibulaSegmentation node reference is set
fibulaSegmentation = parameterNode.GetNodeReference("fibulaSegmentation")
if fibulaSegmentation is None:
    import slicer
    segNodes = slicer.util.getNodesByClass("vtkMRMLSegmentationNode")
    fibulaSegmentation = None
    for node in segNodes:
        if "fibula" in node.GetName().lower():
            fibulaSegmentation = node
            break
    if fibulaSegmentation is None:
        raise RuntimeError("Could not find fibula segmentation node. Please ensure a segmentation node with 'fibula' in its name exists.")
    parameterNode.SetNodeReferenceID("fibulaSegmentation", fibulaSegmentation.GetID())

# Ensure mandibularSegmentation node reference is set
mandibularSegmentation = parameterNode.GetNodeReference("mandibularSegmentation")
if mandibularSegmentation is None:
    mandibularSegmentation = None
    for node in segNodes:
        if "mandib" in node.GetName().lower():
            mandibularSegmentation = node
            break
    if mandibularSegmentation is None:
        raise RuntimeError("Could not find mandibular segmentation node. Please ensure a segmentation node with 'mandible' or 'mandibular' in its name exists.")
    parameterNode.SetNodeReferenceID("mandibularSegmentation", mandibularSegmentation.GetID())

# Set default for useNonDecimatedBoneModelsForPreview if missing
if parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview") == "":
    parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", "True")

# Call the method
logic.makeModels()

# Store logic instance for subsequent steps
_bonereconstructionplanner_logic = logic

print("[BoneReconstructionPlanner] Models created successfully.")
