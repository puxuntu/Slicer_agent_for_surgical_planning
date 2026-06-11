import slicer

# Obtain or create the BoneReconstructionPlanner logic instance
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'BoneReconstructionPlanner':
    try:
        slicer.util.selectModule('BoneReconstructionPlanner')
    except Exception as _module_enter_error:
        print("Warning: could not activate module 'BoneReconstructionPlanner': {}".format(_module_enter_error))
# precondition:end

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

# Ensure the parameter node exists (created by the module's widget)
parameterNode = logic.getParameterNode()
if not parameterNode:
    raise RuntimeError("No parameter node found for BoneReconstructionPlanner. Ensure the module UI has been initialized.")

# Set the parameters required by the contract for step cb_step_30
# These placeholders will be filled by the workflow runtime.
kindOfMandibleResection = {kindOfMandibleResection: "Segmental Mandibulectomy"}
useNonDecimatedBoneModelsForPreview = {useNonDecimatedBoneModelsForPreview: "True"}
parameterNode.SetParameter("kindOfMandibleResection", kindOfMandibleResection)
parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", useNonDecimatedBoneModelsForPreview)

# Set node references if provided (placeholders for mandibleModelNode and decimatedMandibleModelNode)
mandibleModelNodeRef = {mandibleModelNodeRef: ""}
if mandibleModelNodeRef:
    parameterNode.SetNodeReferenceID("mandibleModelNode", mandibleModelNodeRef)
decimatedMandibleModelNodeRef = {decimatedMandibleModelNodeRef: ""}
if decimatedMandibleModelNodeRef:
    parameterNode.SetNodeReferenceID("decimatedMandibleModelNode", decimatedMandibleModelNodeRef)

print("[BoneReconstructionPlanner] Executing generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible")
logic.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()
print("[BoneReconstructionPlanner] Step cb_step_30 completed: fibula planes, bone pieces, and transforms generated.")