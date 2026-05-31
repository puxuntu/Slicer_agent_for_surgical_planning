try:
    _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

logic = _bonereconstructionplanner_logic

# Ensure parameter node and its references are set up
parameterNode = logic.getParameterNode()
if not parameterNode:
    # Create a new parameter node if none exists
    import json
    node = slicer.mrmlScene.CreateNodeByClass("vtkMRMLScriptedModuleNode")
    node.SetModuleName("BoneReconstructionPlanner")
    parameterNode = slicer.mrmlScene.AddNode(node)
    logic.setParameterNode(parameterNode)

# Set mandible model node references if missing
mandibleModel = parameterNode.GetNodeReference("mandibleModelNode")
if not mandibleModel:
    modelNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(modelNodes.GetNumberOfItems()):
        node = modelNodes.GetItemAsObject(i)
        if "mandible" in node.GetName().lower():
            mandibleModel = node
            break
    if mandibleModel:
        parameterNode.SetNodeReferenceID("mandibleModelNode", mandibleModel.GetID())

decimatedMandibleModel = parameterNode.GetNodeReference("decimatedMandibleModelNode")
if not decimatedMandibleModel:
    modelNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(modelNodes.GetNumberOfItems()):
        node = modelNodes.GetItemAsObject(i)
        if "decimated" in node.GetName().lower() and "mandible" in node.GetName().lower():
            decimatedMandibleModel = node
            break
    if not decimatedMandibleModel:
        # fallback: use the same mandible model
        decimatedMandibleModel = mandibleModel
    if decimatedMandibleModel:
        parameterNode.SetNodeReferenceID("decimatedMandibleModelNode", decimatedMandibleModel.GetID())

# Ensure mandible planes folder exists (look for it by name in subject hierarchy)
shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
planesFolder = shNode.GetItemByName("Mandible planes")
if planesFolder == 0:
    # Create a new folder under the scene
    sceneFolder = shNode.GetSceneItemID()
    planesFolder = shNode.CreateFolderItem(sceneFolder, "Mandible planes")
    # Logic method getMandiblePlanesFolderItemID should find this folder

# Ensure required list attribute exists on the logic instance
if not hasattr(logic, "mandibleToFibulaRegistrationTransformMatricesList"):
    logic.mandibleToFibulaRegistrationTransformMatricesList = []

# Call the main method
logic.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()

print("[BoneReconstructionPlanner] Step 23 complete: Generated fibula planes, bone pieces, and transformed them to mandible.")