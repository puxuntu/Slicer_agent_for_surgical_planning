import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

# Reuse existing logic instance if available, otherwise create a new one
try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

# Ensure the module's parameter node is set on the logic
# Usually the logic has a method getParameterNode() that returns or creates the parameter node
parameterNode = logic.getParameterNode()

# Set up required node references on the parameter node
# Search for mandible model nodes with fuzzy name matching
mandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
if not mandibleModelNode:
    modelNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(modelNodes.GetNumberOfItems()):
        n = modelNodes.GetItemAsObject(i)
        if "mandible" in n.GetName().lower():
            parameterNode.SetNodeReferenceID("mandibleModelNode", n.GetID())
            mandibleModelNode = n
            break

decimatedMandibleModelNode = parameterNode.GetNodeReference("decimatedMandibleModelNode")
if not decimatedMandibleModelNode:
    modelNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(modelNodes.GetNumberOfItems()):
        n = modelNodes.GetItemAsObject(i)
        if "decimated" in n.GetName().lower() and "mandible" in n.GetName().lower():
            parameterNode.SetNodeReferenceID("decimatedMandibleModelNode", n.GetID())
            decimatedMandibleModelNode = n
            break

# Set default parameter (optional but helps avoid errors)
if not parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview"):
    parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", "False")

# Call the main method
logic.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()

# Store logic instance for subsequent steps
_bonereconstructionplanner_logic = logic

print("[BoneReconstructionPlanner] generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible completed.")