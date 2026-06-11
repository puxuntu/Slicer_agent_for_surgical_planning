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
    _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

logic = _bonereconstructionplanner_logic
parameterNode = logic.getParameterNode()

# Ensure parameter node references for fibula and mandibular segmentations
role_class = "vtkMRMLSegmentationNode"
for role, keyword in [("fibulaSegmentation", "fibula"), ("mandibularSegmentation", "mandibular")]:
    ref = parameterNode.GetNodeReference(role)
    if ref is None:
        segmentationNodes = slicer.util.getNodesByClass(role_class)
        matched = [node for node in segmentationNodes if keyword.lower() in node.GetName().lower()]
        if len(matched) == 0:
            raise ValueError(f"No segmentation node found for role '{role}' (keyword '{keyword}')")
        ref = matched[0]
        parameterNode.SetNodeReferenceID(role, ref.GetID())
    # Validate node still exists and is of correct class
    if ref is None or not ref.IsA(role_class):
        raise ValueError(f"Invalid or missing segmentation node for role '{role}'")

# Set default for optional parameter if not already set
if not parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview"):
    parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", "True")

# Execute the step
logic.makeModels()

print("[BoneReconstructionPlanner] Step 5 completed: Bone models created.")
