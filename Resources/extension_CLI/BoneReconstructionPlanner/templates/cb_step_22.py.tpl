import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

# Reuse existing logic instance or create new one
try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

# Ensure parameterNode exists
parameterNode = logic.getParameterNode()

# Set missing parameter values from defaults (never overwrite non-empty)
defaults = {
    "additionalBetweenSpaceOfFibulaPlanes": "1.5",
    "fibulaCentroidX": "0.0",
    "fibulaCentroidY": "0.0",
    "fibulaCentroidZ": "0.0",
    "fibulaSegmentsMeasurementMode": "center2center",
    "fixCutGoesThroughTheMandibleTwice": "False",
    "fixCutGoesThroughTheMandibleTwiceCheckBoxChanged": "False",
    "initialSpace": "0.0",
    "kindOfMandibleResection": "Segmental Mandibulectomy",
    "mandibleCentroidX": "0.0",
    "mandibleCentroidY": "0.0",
    "mandibleCentroidZ": "0.0",
    "mandibleSideToRemove": "Removing right side",
    "rightSideLegFibula": "False",
    "useMoreExactVersionOfPositioningAlgorithm": "False",
    "useNonDecimatedBoneModelsForPreview": "True",
}
for param, default in defaults.items():
    current = parameterNode.GetParameter(param)
    if not current:
        parameterNode.SetParameter(param, default)

# Find mandible model nodes and set references if missing
mandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
if not mandibleModelNode:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "mandible" in n.GetName().lower():
            mandibleModelNode = n
            break
    if mandibleModelNode:
        parameterNode.SetNodeReferenceID("mandibleModelNode", mandibleModelNode.GetID())

decimatedMandibleModelNode = parameterNode.GetNodeReference("decimatedMandibleModelNode")
if not decimatedMandibleModelNode:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "mandible" in n.GetName().lower() and "decimated" in n.GetName().lower():
            decimatedMandibleModelNode = n
            break
    if not decimatedMandibleModelNode and mandibleModelNode:
        # If no explicit decimated node, fall back to using the same model
        decimatedMandibleModelNode = mandibleModelNode
    if decimatedMandibleModelNode:
        parameterNode.SetNodeReferenceID("decimatedMandibleModelNode", decimatedMandibleModelNode.GetID())

# Call the method
logic.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()

print("[BoneReconstructionPlanner] Step 22 completed: Generated fibula planes, bone pieces, and transformed to mandible.")