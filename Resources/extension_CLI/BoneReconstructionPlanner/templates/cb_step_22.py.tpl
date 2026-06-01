import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

# Reuse existing logic instance or create a new one
try:
    _bonereconstructionplanner_logic
except NameError:
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

logic = _bonereconstructionplanner_logic

# Get the module's parameter node
parameterNode = logic.getParameterNode()

# Ensure parameter node has references to fibulaLine and fibulaModelNode
fibulaLine = parameterNode.GetNodeReference("fibulaLine")
if fibulaLine is None:
    # Find fibula line curve in scene – typically a vtkMRMLMarkupsCurveNode
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            parameterNode.SetNodeReferenceID("fibulaLine", n.GetID())
            fibulaLine = n
            break
    if fibulaLine is None:
        raise RuntimeError("Could not find a fibula line curve in the scene.")

fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
if fibulaModelNode is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            parameterNode.SetNodeReferenceID("fibulaModelNode", n.GetID())
            fibulaModelNode = n
            break
    if fibulaModelNode is None:
        raise RuntimeError("Could not find a fibula model node in the scene.")

# Call the method (no arguments as it reads from parameter node internally)
logic.centerFibulaLine()

print("[BoneReconstructionPlanner] Step cb_step_22: centerFibulaLine completed.")