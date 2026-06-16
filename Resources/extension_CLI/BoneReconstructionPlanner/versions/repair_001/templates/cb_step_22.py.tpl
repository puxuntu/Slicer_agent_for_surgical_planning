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

# Resolve required node references
for role, keyword, nodeClass in [("fibulaLine", "FibulaLine", "vtkMRMLMarkupsLineNode"),
                                   ("fibulaModelNode", "FibulaModel", "vtkMRMLModelNode")]:
    node = parameterNode.GetNodeReference(role)
    if node is None:
        nodes = slicer.util.getNodesByClass(nodeClass)
        candidates = [n for n in nodes if keyword.lower() in n.GetName().lower()]
        if not candidates:
            raise RuntimeError(f"Could not find a node of class {nodeClass} with name containing '{keyword}' for role '{role}'")
        node = candidates[0]
        parameterNode.SetNodeReferenceID(role, node.GetID())

logic.centerFibulaLine()

print("[BoneReconstructionPlanner] centerFibulaLine completed.")
