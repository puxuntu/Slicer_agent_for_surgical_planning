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

parameterNode = logic.getParameterNode()

# Initialize source-derived scalar defaults without overwriting existing values
if not parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview"):
    parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", "True")

# Resolve required segmentation node references (strict order: existing reference first)
for role, keyword in (("fibulaSegmentation", "fibula"), ("mandibularSegmentation", "mandible")):
    if parameterNode.GetNodeReference(role):
        continue
    candidates = slicer.util.getNodesByClass("vtkMRMLSegmentationNode")
    selected = None
    for candidate in candidates:
        if keyword in candidate.GetName().lower():
            selected = candidate
            break
    if selected is None and len(candidates) == 1:
        selected = candidates[0]
    if selected is None:
        raise RuntimeError(f"No segmentation node available for role '{role}'")
    parameterNode.SetNodeReferenceID(role, selected.GetID())

logic.makeModels()

_bonereconstructionplanner_logic = logic

print("Segmentation models (fibula and mandible) were created from the fibula and mandibular segmentation nodes.")
