import slicer
# precondition:begin
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

# Set defaults for scalar parameters relevant to this step (only from contract)
scalar_defaults = {
    'kindOfMandibleResection': 'Segmental Mandibulectomy',
    'useNonDecimatedBoneModelsForPreview': 'True'
}
for param, default in scalar_defaults.items():
    current = parameterNode.GetParameter(param)
    if not current:
        parameterNode.SetParameter(param, default)

# Call the reconstruction regeneration method
logic.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()

print("[BoneReconstructionPlanner] Generated fibula planes, fibula bone pieces, and transformed them to mandible.")
