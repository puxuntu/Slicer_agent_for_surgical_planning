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

paramNode = _bonereconstructionplanner_logic.parameterNode

# Set parameters with defaults if not already set (non-empty)
defaults = {
    'additionalBetweenSpaceOfFibulaPlanes': '1.5',
    'fibulaCentroidX': '0.0',
    'fibulaCentroidY': '0.0',
    'fibulaCentroidZ': '0.0',
    'fibulaSegmentsMeasurementMode': 'center2center',
    'fixCutGoesThroughTheMandibleTwice': 'False',
    'fixCutGoesThroughTheMandibleTwiceCheckBoxChanged': 'False',
    'initialSpace': '0.0',
    'kindOfMandibleResection': 'Segmental Mandibulectomy',
    'lockVSP': 'False',
    'makeAllMandiblePlanesRotateTogether': 'True',
    'mandibleCentroidX': '0.0',
    'mandibleCentroidY': '0.0',
    'mandibleCentroidZ': '0.0',
    'mandiblePlanesPositioningForMaximumBoneContact': 'True',
    'mandibleSideToRemove': 'Removing right side',
    'rightSideLegFibula': 'False',
    'useMoreExactVersionOfPositioningAlgorithm': 'False',
    'useNonDecimatedBoneModelsForPreview': 'True',
}
for paramName, defaultVal in defaults.items():
    current = paramNode.GetParameter(paramName)
    if current == '' or current is None:
        paramNode.SetParameter(paramName, defaultVal)

_bonereconstructionplanner_logic.hardVSPUpdate()
print('[BoneReconstructionPlanner] cb_step_30 completed: hardVSPUpdate executed.')
