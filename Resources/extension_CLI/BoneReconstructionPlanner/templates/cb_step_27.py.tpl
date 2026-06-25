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

# Set scalar defaults if missing (parameters read by the method)
if not parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview"):
    parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", "True")
if not parameterNode.GetParameter("kindOfMandibleResection"):
    parameterNode.SetParameter("kindOfMandibleResection", "Segmental Mandibulectomy")

# Ensure required node references are set using cached IDs from prior steps
# mandibleModelNode
if parameterNode.GetNodeReference("mandibleModelNode") is None:
    try:
        node_id = _bonereconstructionplanner_mandibleModelNode_id
        node = slicer.mrmlScene.GetNodeByID(node_id)
        if node:
            parameterNode.SetNodeReferenceID("mandibleModelNode", node.GetID())
    except NameError:
        pass

# fibulaModelNode
if parameterNode.GetNodeReference("fibulaModelNode") is None:
    try:
        node_id = _bonereconstructionplanner_fibulaModelNode_id
        node = slicer.mrmlScene.GetNodeByID(node_id)
        if node:
            parameterNode.SetNodeReferenceID("fibulaModelNode", node.GetID())
    except NameError:
        pass

# fibulaLine
if parameterNode.GetNodeReference("fibulaLine") is None:
    try:
        node_id = _bonereconstructionplanner_fibulaLine_id
        node = slicer.mrmlScene.GetNodeByID(node_id)
        if node:
            parameterNode.SetNodeReferenceID("fibulaLine", node.GetID())
    except NameError:
        pass

# currentScalarVolume (required)
if parameterNode.GetNodeReference("currentScalarVolume") is None:
    try:
        node_id = _bonereconstructionplanner_currentScalarVolume_id
        node = slicer.mrmlScene.GetNodeByID(node_id)
        if node:
            parameterNode.SetNodeReferenceID("currentScalarVolume", node.GetID())
    except NameError:
        pass

# decimatedMandibleModelNode (optional; method may use it)
if parameterNode.GetNodeReference("decimatedMandibleModelNode") is None:
    try:
        node_id = _bonereconstructionplanner_decimatedMandibleModelNode_id
        node = slicer.mrmlScene.GetNodeByID(node_id)
        if node:
            parameterNode.SetNodeReferenceID("decimatedMandibleModelNode", node.GetID())
    except NameError:
        pass

# Execute the method
logic.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()

print("[BoneReconstructionPlanner] generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible completed.")
