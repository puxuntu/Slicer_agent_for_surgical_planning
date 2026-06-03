import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

# Reuse existing logic instance if available, otherwise create new
try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

# Get the parameter node associated with the logic
parameterNode = logic.getParameterNode()

# Ensure required referenced nodes exist in the scene
# Find "fibulaLine" - a markups line node
fibulaLine = parameterNode.GetNodeReference("fibulaLine")
if fibulaLine is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsLineNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            fibulaLine = n
            parameterNode.SetNodeReferenceID("fibulaLine", n.GetID())
            break

# Find "fibulaModelNode" - a model node
fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
if fibulaModelNode is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            fibulaModelNode = n
            parameterNode.SetNodeReferenceID("fibulaModelNode", n.GetID())
            break

# Ensure that the required nodes are found
if fibulaLine is None:
    raise ValueError("Could not find a fibula line (vtkMRMLMarkupsLineNode) in the scene.")
if fibulaModelNode is None:
    raise ValueError("Could not find a fibula model (vtkMRMLModelNode) in the scene.")

# Call the method
logic.centerFibulaLine()

print("[BoneReconstructionPlanner] centerFibulaLine completed successfully.")