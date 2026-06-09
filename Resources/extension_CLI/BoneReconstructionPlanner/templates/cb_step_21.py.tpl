import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

# Reuse existing logic instance or create new
try:
    _bonereconstructionplanner_logic
except NameError:
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

logic = _bonereconstructionplanner_logic

# Get parameter node (create if needed)
parameterNode = logic.getParameterNode()
if not parameterNode:
    parameterNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScriptedModuleNode")
    logic.setDefaultParameters(parameterNode)  # correct method name

# Find fibulaLine (markup line) and fibulaModelNode if not already referenced
if not parameterNode.GetNodeReference("fibulaLine"):
    # Search for a markup line node with "fibula" in name
    markupNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsLineNode")
    for i in range(markupNodes.GetNumberOfItems()):
        node = markupNodes.GetItemAsObject(i)
        if node and "fibula" in node.GetName().lower():
            parameterNode.SetNodeReferenceID("fibulaLine", node.GetID())
            break
    else:
        # Fallback: try exact name
        try:
            node = slicer.util.getNode("FibulaLine")
            parameterNode.SetNodeReferenceID("fibulaLine", node.GetID())
        except slicer.util.MRMLNodeNotFoundException:
            print("Could not find fibulaLine node. Please ensure a markup line exists with 'fibula' in the name.")

if not parameterNode.GetNodeReference("fibulaModelNode"):
    # Search for a model node with "fibula" in name
    modelNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(modelNodes.GetNumberOfItems()):
        node = modelNodes.GetItemAsObject(i)
        if node and "fibula" in node.GetName().lower():
            parameterNode.SetNodeReferenceID("fibulaModelNode", node.GetID())
            break
    else:
        # Fallback: try exact name
        try:
            node = slicer.util.getNode("FibulaModel")
            parameterNode.SetNodeReferenceID("fibulaModelNode", node.GetID())
        except slicer.util.MRMLNodeNotFoundException:
            print("Could not find fibulaModelNode. Please ensure a model node exists with 'fibula' in the name.")

# Call the method
logic.centerFibulaLine()

print("BoneReconstructionPlanner: centerFibulaLine completed successfully.")