try:
    _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

logic = _bonereconstructionplanner_logic

# Ensure parameter node exists
parameterNode = logic.getParameterNode()
if parameterNode is None:
    # Module may not be initialized; try to create parameter node
    import slicer
    node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScriptedModuleNode", "BoneReconstructionPlanner")
    logic.getParameterNode = lambda: node
    parameterNode = node

# Check and set mandible model node references
mandible_nodes = slicer.util.getNodesByClass("vtkMRMLModelNode")
decimated_id = parameterNode.GetNodeReferenceID("decimatedMandibleModelNode")
nondecimated_id = parameterNode.GetNodeReferenceID("nonDecimatedMandibleModelNode")

if not decimated_id:
    for node in mandible_nodes:
        if "mandible" in node.GetName().lower() and "decim" in node.GetName().lower():
            parameterNode.SetNodeReferenceID("decimatedMandibleModelNode", node.GetID())
            break

if not nondecimated_id:
    for node in mandible_nodes:
        if "mandible" in node.GetName().lower() and "decim" not in node.GetName().lower():
            parameterNode.SetNodeReferenceID("nonDecimatedMandibleModelNode", node.GetID())
            break

# Also ensure the parameter node's "mandibleModelNode" reference is set (may be used by method logic)
mandible_node = parameterNode.GetNodeReference("mandibleModelNode")
if not mandible_node:
    # Fallback: use either decimated or non-decimated
    if decimated_id:
        parameterNode.SetNodeReferenceID("mandibleModelNode", decimated_id)
    elif nondecimated_id:
        parameterNode.SetNodeReferenceID("mandibleModelNode", nondecimated_id)
    else:
        # last resort: find any mandible model
        for node in mandible_nodes:
            if "mandible" in node.GetName().lower():
                parameterNode.SetNodeReferenceID("mandibleModelNode", node.GetID())
                break

# Call the method
logic.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()

print("BoneReconstructionPlanner: Step 13 completed - fibula planes, bone pieces, and transformation to mandible generated.")