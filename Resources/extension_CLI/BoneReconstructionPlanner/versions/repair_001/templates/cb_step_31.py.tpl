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

# Set scalar parameters with default values only if not already set
parameter_defaults = {
    "additionalBetweenSpaceOfFibulaPlanes": "1.5",
    "fibulaCentroidX": "0.0",
    "fibulaCentroidY": "0.0",
    "fibulaCentroidZ": "0.0",
    "fibulaSegmentsMeasurementMode": "center2center",
    "fixCutGoesThroughTheMandibleTwice": "False",
    "fixCutGoesThroughTheMandibleTwiceCheckBoxChanged": "False",
    "initialSpace": "0.0",
    "kindOfMandibleResection": "Segmental Mandibulectomy",
    "mandibleCentroidX": "0.0",
    "mandibleCentroidY": "0.0",
    "mandibleCentroidZ": "0.0",
    "mandibleSideToRemove": "Removing right side",
    "rightSideLegFibula": "False",
    "useMoreExactVersionOfPositioningAlgorithm": "False",
    "useNonDecimatedBoneModelsForPreview": "True",
}
for param, default in parameter_defaults.items():
    if not parameterNode.GetParameter(param):
        parameterNode.SetParameter(param, default)

# Resolve node references needed by the method (roles listed as required/conditional)
# For required roles, we set them if not already set.
required_roles = ["currentScalarVolume", "fibulaLine", "fibulaModelNode", "mandibleModelNode"]
optional_roles = ["decimatedFibulaModelNode", "decimatedMandibleModelNode", "mandibleCurve", "planeToFixCutGoesThroughTheMandibleTwice"]

def resolve_reference(role, node_class, search_keywords):
    node = parameterNode.GetNodeReference(role)
    if node is not None:
        return node
    # Search by class and keywords
    nodes = slicer.util.getNodesByClass(node_class)
    for n in nodes:
        name = n.GetName().lower()
        if any(kw.lower() in name for kw in search_keywords):
            parameterNode.SetNodeReferenceID(role, n.GetID())
            return n
    return None

# For each required role, attempt to resolve. If not found, raise error.
# Provide reasonable node class and keywords based on role names.
role_resolution = {
    "currentScalarVolume": ("vtkMRMLScalarVolumeNode", ["volume", "scalar"]),
    "fibulaLine": ("vtkMRMLMarkupsLineNode", ["fibula", "line"]),
    "fibulaModelNode": ("vtkMRMLModelNode", ["fibula", "model"]),
    "mandibleModelNode": ("vtkMRMLModelNode", ["mandible", "model"]),
    "decimatedFibulaModelNode": ("vtkMRMLModelNode", ["decimated", "fibula", "model"]),
    "decimatedMandibleModelNode": ("vtkMRMLModelNode", ["decimated", "mandible", "model"]),
    "mandibleCurve": ("vtkMRMLMarkupsCurveNode", ["mandible", "curve"]),
    "planeToFixCutGoesThroughTheMandibleTwice": ("vtkMRMLMarkupsPlaneNode", ["plane", "fix", "cut", "mandible"]),
}

for role in required_roles:
    cls, keywords = role_resolution[role]
    node = resolve_reference(role, cls, keywords)
    if node is None:
        raise RuntimeError(f"Required node reference '{role}' could not be resolved. Please set it before this step.")

# For optional roles, try to resolve but don't fail if missing
for role in optional_roles:
    if role in role_resolution:
        cls, keywords = role_resolution[role]
        resolve_reference(role, cls, keywords)

# Call the method
logic.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()

print("[BoneReconstructionPlanner] Generate fibula planes, fibula bone pieces, and transform to mandible completed.")
