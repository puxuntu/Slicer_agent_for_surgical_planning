import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

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
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

parameterNode = logic.getParameterNode()

# Set scalar parameters from defaults if not already set
parametersToSet = [
    ("additionalBetweenSpaceOfFibulaPlanes", "1.5"),
    ("fibulaCentroidX", "0.0"),
    ("fibulaCentroidY", "0.0"),
    ("fibulaCentroidZ", "0.0"),
    ("fibulaSegmentsMeasurementMode", "center2center"),
    ("fixCutGoesThroughTheMandibleTwice", "False"),
    ("fixCutGoesThroughTheMandibleTwiceCheckBoxChanged", "False"),
    ("initialSpace", "0.0"),
    ("kindOfMandibleResection", "Segmental Mandibulectomy"),
    ("mandibleCentroidX", "0.0"),
    ("mandibleCentroidY", "0.0"),
    ("mandibleCentroidZ", "0.0"),
    ("mandibleSideToRemove", "Removing right side"),
    ("rightSideLegFibula", "False"),
    ("useMoreExactVersionOfPositioningAlgorithm", "False"),
    ("useNonDecimatedBoneModelsForPreview", "True"),
]

for paramName, defaultValue in parametersToSet:
    currentValue = parameterNode.GetParameter(paramName)
    if currentValue is None or currentValue == "":
        parameterNode.SetParameter(paramName, defaultValue)

# Node references are expected to be set by previous steps.
# The method reads 'mandibleModelNode' and 'decimatedMandibleModelNode' from the parameter node.
# We do not attempt to set them here; if missing, the method will raise an appropriate error.

logic.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()
print("[BoneReconstructionPlanner] Step 24: generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible completed.")
