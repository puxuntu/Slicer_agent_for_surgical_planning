try:
    _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

logic = _bonereconstructionplanner_logic
parameterNode = logic.getParameterNode()
if parameterNode is None:
    # If parameter node doesn't exist, create one using the standard naming convention
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    # Create a parameter node for the module (this mimics typical Slicer module setup)
    pg = slicer.modules.bonereconstructionplanner.widgetRepresentation().self().logic.getParameterNode()
    parameterNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScriptedModuleNode", "BoneReconstructionPlanner")
    # Alternatively, set the default parameter node; but assume it exists from prior steps.
    pass

# Ensure mandible model node references are set
# Find non-decimated mandible model node
mandibleNode = None
mandibleModels = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
for i in range(mandibleModels.GetNumberOfItems()):
    node = mandibleModels.GetItemAsObject(i)
    if "mandible" in node.GetName().lower() and "decimated" not in node.GetName().lower():
        mandibleNode = node
        break
if mandibleNode and parameterNode.GetNodeReference("mandibleModelNode") is None:
    parameterNode.SetNodeReferenceID("mandibleModelNode", mandibleNode.GetID())

# Find decimated mandible model node
decimatedMandibleNode = None
for i in range(mandibleModels.GetNumberOfItems()):
    node = mandibleModels.GetItemAsObject(i)
    if "mandible" in node.GetName().lower() and "decimated" in node.GetName().lower():
        decimatedMandibleNode = node
        break
if decimatedMandibleNode and parameterNode.GetNodeReference("decimatedMandibleModelNode") is None:
    parameterNode.SetNodeReferenceID("decimatedMandibleModelNode", decimatedMandibleNode.GetID())

# Ensure useNonDecimatedBoneModelsForPreview parameter exists (default to False)
if not parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview"):
    parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", "False")

# Run the method
logic.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()

# Store logic for future steps
_bonereconstructionplanner_logic = logic
print("[BoneReconstructionPlanner] Step cb_step_24 completed: fibula planes, bone pieces, and transforms generated.")