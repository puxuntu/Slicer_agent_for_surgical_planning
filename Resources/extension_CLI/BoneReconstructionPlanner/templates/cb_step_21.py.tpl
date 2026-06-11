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

logic = _bonereconstructionplanner_logic
parameterNode = logic.getParameterNode()

# Ensure fibulaLine reference
if not parameterNode.GetNodeReference("fibulaLine"):
    fibulaLineNodes = slicer.util.getNodesByClass("vtkMRMLMarkupsLineNode")
    if fibulaLineNodes:
        # Select first node with name containing "fibula" (case-insensitive)
        fibulaLine = None
        for node in fibulaLineNodes:
            if "fibula" in node.GetName().lower():
                fibulaLine = node
                break
        if fibulaLine is None:
            fibulaLine = fibulaLineNodes[0]
        parameterNode.SetNodeReferenceID("fibulaLine", fibulaLine.GetID())
    else:
        raise ValueError("No vtkMRMLMarkupsLineNode found in scene for fibulaLine. Please create or load one with 'fibula' in its name.")

# Ensure fibulaModelNode reference
if not parameterNode.GetNodeReference("fibulaModelNode"):
    modelNodes = slicer.util.getNodesByClass("vtkMRMLModelNode")
    fibulaModel = None
    for node in modelNodes:
        if "fibula" in node.GetName().lower():
            fibulaModel = node
            break
    if fibulaModel is None and modelNodes:
        fibulaModel = modelNodes[0]
    if fibulaModel:
        parameterNode.SetNodeReferenceID("fibulaModelNode", fibulaModel.GetID())
    else:
        raise ValueError("No vtkMRMLModelNode found in scene for fibulaModelNode. Please create or load one with 'fibula' in its name.")

logic.centerFibulaLine()
print("[BoneReconstructionPlanner] Completed cb_step_21: centerFibulaLine")
