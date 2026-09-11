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

# Initialise the scalar settings the method reads, without overwriting existing values
if not parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview"):
    parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", "True")
if not parameterNode.GetParameter("kindOfMandibleResection"):
    parameterNode.SetParameter("kindOfMandibleResection", "Segmental Mandibulectomy")


def _resolve_reference(role, nodeClass, keyword=""):
    # Strict order: reuse an already-set reference first, only search when empty
    node = parameterNode.GetNodeReference(role)
    if node is not None:
        return node
    candidateNodes = slicer.util.getNodesByClass(nodeClass)
    if keyword:
        matchedNodes = [n for n in candidateNodes if keyword in n.GetName().lower()]
        if matchedNodes:
            candidateNodes = matchedNodes
    if not candidateNodes:
        raise RuntimeError("Required input '" + role + "' (" + nodeClass + ") is not set and no candidate node was found in the scene")
    node = candidateNodes[0]
    parameterNode.SetNodeReferenceID(role, node.GetID())
    return node


_resolve_reference("currentScalarVolume", "vtkMRMLScalarVolumeNode")
_resolve_reference("mandibleModelNode", "vtkMRMLModelNode", "mandible")
_resolve_reference("fibulaModelNode", "vtkMRMLModelNode", "fibula")
_resolve_reference("fibulaLine", "vtkMRMLMarkupsNode", "fibula")

logic.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()

_bonereconstructionplanner_logic = logic

print("Fibula planes generated, fibula bone pieces created and transformed onto the mandible.")
