try:
    _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

logic = _bonereconstructionplanner_logic

# Ensure parameter node is accessible
parameterNode = logic.getParameterNode()

# Ensure fibula line (markups curve) reference exists
fibulaLine = parameterNode.GetNodeReference("fibulaLine")
if fibulaLine is None:
    # Search for a markups curve whose name contains "fibula"
    curveNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode")
    for i in range(curveNodes.GetNumberOfItems()):
        n = curveNodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            fibulaLine = n
            break
    if fibulaLine is None:
        raise ValueError("Fibula line (markups curve) not found in the scene.")
    parameterNode.SetNodeReferenceID("fibulaLine", fibulaLine.GetID())

# Ensure fibula model node reference exists
fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
if fibulaModelNode is None:
    modelNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(modelNodes.GetNumberOfItems()):
        n = modelNodes.GetItemAsObject(i)
        if "fibula" in n.GetName().lower():
            fibulaModelNode = n
            break
    if fibulaModelNode is None:
        raise ValueError("Fibula model node not found in the scene.")
    parameterNode.SetNodeReferenceID("fibulaModelNode", fibulaModelNode.GetID())

# Ensure mandible reconstruction folder exists (needed by getMandibleReconstructionFolderItemID())
# If not set, attempt to find or create one
shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
mandibleFolderID = parameterNode.GetParameter("mandibleReconstructionFolderItemID")
if mandibleFolderID == "" or not shNode.HasItem(int(mandibleFolderID)):
    # Try to find an existing folder with "MandibleReconstruction" in name
    folderIDs = []
    for i in range(shNode.GetNumberOfItemChildren(shNode.GetSceneItemID())):
        folderIDs.append(shNode.GetItemChild(shNode.GetSceneItemID(), i))
    foundFolder = None
    for i in range(len(folderIDs)):
        itemID = folderIDs[i]
        itemName = shNode.GetItemName(itemID)
        if itemName and "mandible reconstruction" in itemName.lower():
            foundFolder = itemID
            break
    if foundFolder is None:
        # Create a new folder under the scene
        sceneItemID = shNode.GetSceneItemID()
        foundFolder = shNode.CreateFolderItem(sceneItemID, "MandibleReconstruction")
    parameterNode.SetParameter("mandibleReconstructionFolderItemID", str(foundFolder))

# Call the method
logic.centerFibulaLine()

print("[BoneReconstructionPlanner] Step 23 (centerFibulaLine) completed.")