import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

# Reuse or create logic instance
try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

# Get/initialize parameter node (it should already exist from earlier steps)
parameterNode = logic.getParameterNode()

# Ensure required segmentation node references exist
# Search for fibula segmentation node
fibulaNode = parameterNode.GetNodeReference("fibulaSegmentation")
if fibulaNode is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            fibulaNode = n
            break
    if fibulaNode:
        parameterNode.SetNodeReferenceID("fibulaSegmentation", fibulaNode.GetID())

# Search for mandibular segmentation node
mandibleNode = parameterNode.GetNodeReference("mandibularSegmentation")
if mandibleNode is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        name = n.GetName().lower()
        if "mandib" in name or "mandible" in name:
            mandibleNode = n
            break
    if mandibleNode:
        parameterNode.SetNodeReferenceID("mandibularSegmentation", mandibleNode.GetID())

# Set scalar parameter "useNonDecimatedBoneModelsForPreview" with default 'True' if not already set
currentVal = parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview")
if not currentVal:
    parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", "True")

# Call makeModels()
logic.makeModels()

print("[BoneReconstructionPlanner] Step 5 completed: bone models created.")