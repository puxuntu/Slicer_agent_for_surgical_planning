import slicer
import BoneReconstructionPlanner

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
    logic = BoneReconstructionPlanner.BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

parameterNode = logic.getParameterNode()

# Resolve required node reference: fibulaLine (markups line of the fibula)
fibulaLine = parameterNode.GetNodeReference("fibulaLine")
if not fibulaLine:
    fibulaLineCandidates = slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")
    for candidate in fibulaLineCandidates:
        if "fibula" in candidate.GetName().lower():
            fibulaLine = candidate
            break
    if not fibulaLine:
        raise RuntimeError("Required node reference 'fibulaLine' is not set and no matching vtkMRMLMarkupsLineNode was found in the scene.")
    parameterNode.SetNodeReferenceID("fibulaLine", fibulaLine.GetID())

# Resolve required node reference: fibulaModelNode (model of the fibula)
fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
if not fibulaModelNode:
    fibulaModelCandidates = slicer.util.getNodesByClass("vtkMRMLModelNode")
    for candidate in fibulaModelCandidates:
        if "fibula" in candidate.GetName().lower():
            fibulaModelNode = candidate
            break
    if not fibulaModelNode:
        raise RuntimeError("Required node reference 'fibulaModelNode' is not set and no matching vtkMRMLModelNode was found in the scene.")
    parameterNode.SetNodeReferenceID("fibulaModelNode", fibulaModelNode.GetID())

logic.centerFibulaLine()

_bonereconstructionplanner_logic = logic
print("Centered the fibula line by iteratively intersecting the fibula model with planes at the line endpoints.")
