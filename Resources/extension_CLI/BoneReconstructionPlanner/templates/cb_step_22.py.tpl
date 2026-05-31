try:
    logic = _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

# Ensure parameter node exists and has required references
parameterNode = logic.getParameterNode()

# Check and set fibulaLine reference (markups fiducial)
fibulaLine = parameterNode.GetNodeReference("fibulaLine")
if fibulaLine is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsFiducialNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            fibulaLine = n
            break
    if fibulaLine is not None:
        parameterNode.SetNodeReferenceID("fibulaLine", fibulaLine.GetID())

# Check and set fibulaModelNode reference (model node)
fibulaModel = parameterNode.GetNodeReference("fibulaModelNode")
if fibulaModel is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            fibulaModel = n
            break
    if fibulaModel is not None:
        parameterNode.SetNodeReferenceID("fibulaModelNode", fibulaModel.GetID())

# Call the method
logic.centerFibulaLine()

# Store logic for subsequent steps
_bonereconstructionplanner_logic = logic

print("[BoneReconstructionPlanner] cb_step_22 completed: fibula line centered.")