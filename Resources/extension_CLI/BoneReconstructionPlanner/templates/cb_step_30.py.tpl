try:
    _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

logic = _bonereconstructionplanner_logic
parameterNode = logic.getParameterNode()

# Initialize parameter defaults (never overwrite non-empty values)
param_defaults = {
    "additionalBetweenSpaceOfFibulaPlanes": "1.5",
    "fibulaCentroidX": "0.0",
    "fibulaCentroidY": "0.0",
    "fibulaCentroidZ": "0.0",
    "fibulaSegmentsMeasurementMode": "center2center",
    "fixCutGoesThroughTheMandibleTwice": "False",
    "fixCutGoesThroughTheMandibleTwiceCheckBoxChanged": "False",
    "initialSpace": "0.0",
    "kindOfMandibleResection": "Segmental Mandibulectomy",
    "lockVSP": "False",
    "makeAllMandiblePlanesRotateTogether": "True",
    "mandibleCentroidX": "0.0",
    "mandibleCentroidY": "0.0",
    "mandibleCentroidZ": "0.0",
    "mandiblePlanesPositioningForMaximumBoneContact": "True",
    "mandibleSideToRemove": "Removing right side",
    "rightSideLegFibula": "False",
    "useMoreExactVersionOfPositioningAlgorithm": "False",
    "useNonDecimatedBoneModelsForPreview": "True"
}
for param, default_val in param_defaults.items():
    current = parameterNode.GetParameter(param)
    if not current:
        parameterNode.SetParameter(param, default_val)

# Set up node references if missing
# mandiblePlaneOfRotation - look for a plane markups node with name containing "plane of rotation"
if parameterNode.GetNodeReference("mandiblePlaneOfRotation") is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsPlaneNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "plane of rotation" in n.GetName().lower():
            parameterNode.SetNodeReferenceID("mandiblePlaneOfRotation", n.GetID())
            break

# fibulaLine - look for a line markups node with name containing "fibula line"
if parameterNode.GetNodeReference("fibulaLine") is None:
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsLineNode")
    for i in range(nodes.GetNumberOfItems()):
        n = nodes.GetItemAsObject(i)
        if "fibula line" in n.GetName().lower():
            parameterNode.SetNodeReferenceID("fibulaLine", n.GetID())
            break

# Ensure required self attributes exist
try:
    logic.mandiblePlaneObserversAndNodeIDList
except AttributeError:
    logic.mandiblePlaneObserversAndNodeIDList = []

try:
    logic.mandibleToFibulaRegistrationTransformMatricesList
except AttributeError:
    logic.mandibleToFibulaRegistrationTransformMatricesList = []

# Call the method
logic.onGenerateFibulaPlanesTimerTimeout()

print("[BoneReconstructionPlanner] Step cb_step_30 completed successfully.")