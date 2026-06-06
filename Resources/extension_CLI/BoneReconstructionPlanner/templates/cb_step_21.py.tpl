try:
    _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

logic = _bonereconstructionplanner_logic
parameterNode = logic.getParameterNode()

# Ensure fibulaLine reference is set
fibulaLine = parameterNode.GetNodeReference("fibulaLine")
if fibulaLine is None:
    # Fuzzy search for a markups line node
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsLineNode")
    fibulaLine = None
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower() and "line" in n.GetName().lower():
            fibulaLine = n
            break
    if fibulaLine is None:
        # Fallback: try exact name
        fibulaLine = slicer.util.getNode("FibulaLine", attributes={"NodeClass": "vtkMRMLMarkupsLineNode"})
    if fibulaLine is not None:
        parameterNode.SetNodeReferenceID("fibulaLine", fibulaLine.GetID())

# Ensure fibulaModelNode reference is set
fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
if fibulaModelNode is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    fibulaModelNode = None
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower() and "model" in n.GetName().lower():
            fibulaModelNode = n
            break
    if fibulaModelNode is None:
        # Fallback: try exact name
        fibulaModelNode = slicer.util.getNode("FibulaModel", attributes={"NodeClass": "vtkMRMLModelNode"})
    if fibulaModelNode is not None:
        parameterNode.SetNodeReferenceID("fibulaModelNode", fibulaModelNode.GetID())

# Call the method
logic.centerFibulaLine()

print("[BoneReconstructionPlanner] cb_step_21: fibula line centered successfully.")
