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

# Resolve required reference: fibulaLine
fibulaLine = parameterNode.GetNodeReference("fibulaLine")
if fibulaLine is None:
    lineNodes = slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")
    if lineNodes:
        fibulaLine = lineNodes[0]
        parameterNode.SetNodeReferenceID("fibulaLine", fibulaLine.GetID())
    else:
        raise RuntimeError("Required reference 'fibulaLine' not found.")

# Resolve required reference: fibulaModelNode
fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
if fibulaModelNode is None:
    modelNodes = slicer.util.getNodesByClass("vtkMRMLModelNode")
    if modelNodes:
        fibulaModelNode = modelNodes[0]
        parameterNode.SetNodeReferenceID("fibulaModelNode", fibulaModelNode.GetID())
    else:
        raise RuntimeError("Required reference 'fibulaModelNode' not found.")

logic.centerFibulaLine()
print("[BoneReconstructionPlanner] Fibula line centered.")
