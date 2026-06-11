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

paramNode = _bonereconstructionplanner_logic.getParameterNode()

# Ensure fibulaLine (vtkMRMLMarkupsLineNode) reference exists
fibulaLineRef = paramNode.GetNodeReference("fibulaLine")
if fibulaLineRef is None:
    fibulaLineNodes = slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")
    fibulaLineNode = None
    for node in fibulaLineNodes:
        name = node.GetName().lower()
        if "fibula" in name and "line" in name:
            fibulaLineNode = node
            break
    if fibulaLineNode is None:
        raise RuntimeError("No fibula line node found in the scene. Run previous steps first.")
    paramNode.SetNodeReferenceID("fibulaLine", fibulaLineNode.GetID())

# Ensure fibulaModelNode (vtkMRMLModelNode) reference exists
fibulaModelRef = paramNode.GetNodeReference("fibulaModelNode")
if fibulaModelRef is None:
    modelNodes = slicer.util.getNodesByClass("vtkMRMLModelNode")
    fibulaModelNode = None
    for node in modelNodes:
        name = node.GetName().lower()
        if "fibula" in name and "model" in name:
            fibulaModelNode = node
            break
    if fibulaModelNode is None:
        raise RuntimeError("No fibula model node found in the scene. Run previous steps first.")
    paramNode.SetNodeReferenceID("fibulaModelNode", fibulaModelNode.GetID())

# The method also relies on getMandibleReconstructionFolderItemID() from parameterNode.
# We assume it has been set in earlier steps. If not, the method may fail; we let it propagate.

_bonereconstructionplanner_logic.centerFibulaLine()
print("centerFibulaLine completed successfully.")
