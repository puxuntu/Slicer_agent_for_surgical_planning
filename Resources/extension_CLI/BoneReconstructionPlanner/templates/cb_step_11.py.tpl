import numpy as np

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

# Ensure parameter node and required references exist
parameterNode = logic.getParameterNode()

# Check for fibulaLine (markups line node)
fibulaLine = parameterNode.GetNodeReference("fibulaLine")
if fibulaLine is None:
    # Search scene for a markups line node containing 'fibula' and 'line'
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsLineNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if n and "fibula" in n.GetName().lower() and "line" in n.GetName().lower():
            fibulaLine = n
            break
    if fibulaLine:
        parameterNode.SetNodeReferenceID("fibulaLine", fibulaLine.GetID())
    else:
        raise RuntimeError("Could not find a fibula line node in the scene.")

# Check for fibulaModelNode (model node)
fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
if fibulaModelNode is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if n and "fibula" in n.GetName().lower() and "model" in n.GetName().lower():
            fibulaModelNode = n
            break
    if fibulaModelNode:
        parameterNode.SetNodeReferenceID("fibulaModelNode", fibulaModelNode.GetID())
    else:
        raise RuntimeError("Could not find a fibula model node in the scene.")

# Call the method
logic.centerFibulaLine()

print("[BoneReconstructionPlanner] Completed step cb_step_11: centered fibula line.")