import importlib
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

# Reuse existing logic instance if available, otherwise create new
try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

# Ensure required state: parent folder item ID
# If not set, create a dedicated folder under scene root for this extension
try:
    parentFolderID = logic.getParentFolderItemID()
except AttributeError:
    parentFolderID = None
if parentFolderID is None:
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    # Check if folder already exists
    folderName = "BoneReconstructionPlanner"
    existingFolderID = shNode.GetItemByName(folderName)
    if existingFolderID == 0:
        parentFolderID = shNode.CreateFolderItem(shNode.GetSceneItemID(), folderName)
    else:
        parentFolderID = existingFolderID
    # Attempt to store it on the logic instance (if it accepts setter)
    if hasattr(logic, 'setParentFolderItemID'):
        logic.setParentFolderItemID(parentFolderID)
    # If no setter, we'll rely on the method getParentFolderItemID returning this value
    # For that, we may need to set a member variable directly. Since we can't use setattr that directly,
    # we assume the logic has a way to store it, e.g., via parameter node.
    # As a fallback, store it in the parameter node so the logic can read it.
    paramNode = logic.getParameterNode()
    if paramNode:
        paramNode.SetNodeReferenceID("parentFolderItemID", str(parentFolderID))

# Ensure fibula and mandible segmentation nodes are set in parameter node
paramNode = logic.getParameterNode()
if paramNode:
    fibulaSeg = paramNode.GetNodeReference("fibulaSegmentation")
    if fibulaSeg is None:
        # Search scene for segmentation node with 'fibula' in name
        nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
        for i in range(nodes.GetNumberOfItems()):
            n = nodes.GetItemAsObject(i)
            if "fibula" in n.GetName().lower():
                fibulaSeg = n
                paramNode.SetNodeReferenceID("fibulaSegmentation", fibulaSeg.GetID())
                break
    mandibleSeg = paramNode.GetNodeReference("mandibularSegmentation")
    if mandibleSeg is None:
        nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
        for i in range(nodes.GetNumberOfItems()):
            n = nodes.GetItemAsObject(i)
            if "mandible" in n.GetName().lower():
                mandibleSeg = n
                paramNode.SetNodeReferenceID("mandibularSegmentation", mandibleSeg.GetID())
                break
    # If still missing, raise error
    if fibulaSeg is None:
        raise RuntimeError("Fibula segmentation node not found in scene. Run previous steps to create it.")
    if mandibleSeg is None:
        raise RuntimeError("Mandible segmentation node not found in scene. Run previous steps to create it.")

# Optionally set default useNonDecimatedBoneModelsForPreview if not set
if paramNode and not paramNode.GetParameter("useNonDecimatedBoneModelsForPreview"):
    paramNode.SetParameter("useNonDecimatedBoneModelsForPreview", "False")

# Call the method
logic.makeModels()

print("[BoneReconstructionPlanner] Step 5 (cb_step_5) completed: Models created from segmentations.")