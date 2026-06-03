import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

# Reuse existing logic instance if available, otherwise create new
try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()

# Ensure parameter node exists
parameterNode = logic.getParameterNode()

# Use the logic's built-in default parameter initialization
logic.setDefaultParameters(parameterNode)

# Resolve node references for mandible model nodes
# Look for nodes by class and name substring
mandibleNodeSearch = None
decimatedMandibleNodeSearch = None

modelNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
for i in range(modelNodes.GetNumberOfItems()):
    node = modelNodes.GetItemAsObject(i)
    name = node.GetName().lower()
    if "mandible" in name and "decimated" not in name and "nonDecimated" not in name:
        mandibleNodeSearch = node
    if "mandible" in name and "decimated" in name:
        decimatedMandibleNodeSearch = node

if mandibleNodeSearch and not parameterNode.GetNodeReference("mandibleModelNode"):
    parameterNode.SetNodeReferenceID("mandibleModelNode", mandibleNodeSearch.GetID())

if decimatedMandibleNodeSearch and not parameterNode.GetNodeReference("decimatedMandibleModelNode"):
    parameterNode.SetNodeReferenceID("decimatedMandibleModelNode", decimatedMandibleNodeSearch.GetID())

# Call the method
logic.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()

# Store logic instance for subsequent steps
_bonereconstructionplanner_logic = logic

print("[BoneReconstructionPlanner] Step 22 complete: Fibula planes, bone pieces, and transforms generated.")