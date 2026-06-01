try:
    _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

parameterNode = _bonereconstructionplanner_logic.getParameterNode()

# Ensure fibulaLine reference is set
fibulaLine = parameterNode.GetNodeReference("fibulaLine")
if fibulaLine is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            parameterNode.SetNodeReferenceID("fibulaLine", n.GetID())
            break
    else:
        raise ValueError("No fibula line curve found in the scene.")

# Ensure fibulaModelNode reference is set
fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
if fibulaModelNode is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            parameterNode.SetNodeReferenceID("fibulaModelNode", n.GetID())
            break
    else:
        raise ValueError("No fibula model node found in the scene.")

_bonereconstructionplanner_logic.centerFibulaLine()
print("[BoneReconstructionPlanner] Step cb_step_21 completed.")