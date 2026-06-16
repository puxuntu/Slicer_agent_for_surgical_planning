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
    slicer.app.layoutManager()  # ensure module is loaded
logic = _bonereconstructionplanner_logic
parameterNode = logic.getParameterNode()

# Set defaults for scalar parameters likely read by this method or its helpers
# Only set if empty (not already configured by prior steps)
params_to_set = {
    'additionalBetweenSpaceOfFibulaPlanes': '1.5',
    'fibulaSegmentsMeasurementMode': 'center2center',
    'fixCutGoesThroughTheMandibleTwice': 'False',
    'fixCutGoesThroughTheMandibleTwiceCheckBoxChanged': 'False',
    'initialSpace': '0.0',
    'kindOfMandibleResection': 'Segmental Mandibulectomy',
    'mandibleSideToRemove': 'Removing right side',
    'rightSideLegFibula': 'False',
    'useMoreExactVersionOfPositioningAlgorithm': 'False',
    'useNonDecimatedBoneModelsForPreview': 'True'
}
for param, default in params_to_set.items():
    current = parameterNode.GetParameter(param)
    if current == '' or current is None:
        parameterNode.SetParameter(param, default)

# The method itself reads node references that should already be set by preceding steps.
# Do not attempt to re-resolve or set them here to avoid overwriting prior configuration.

logic.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()
print("[BoneReconstructionPlanner] Fibula planes, bone pieces, and transformations computed and applied.")
_bonereconstructionplanner_logic = logic