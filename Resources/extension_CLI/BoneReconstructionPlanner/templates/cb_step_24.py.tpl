import logging
try:
    _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

parameterNode = _bonereconstructionplanner_logic.getParameterNode()

# Set default parameter values without overwriting existing non-empty values
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
for param, default in defaults.items():
    if not parameterNode.GetParameter(param):
        parameterNode.SetParameter(param, default)

# Ensure expected internal state exists (e.g., observer list)
if not hasattr(_bonereconstructionplanner_logic, "mandiblePlaneObserversAndNodeIDList"):
    _bonereconstructionplanner_logic.mandiblePlaneObserversAndNodeIDList = []

# Resolve node references if not already set
if parameterNode.GetNodeReference("mandiblePlaneOfRotation") is None:
    planeNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsPlaneNode")
    for i in range(planeNodes.GetNumberOfItems()):
        node = planeNodes.GetItemAsObject(i)
        if "mandibleplaneofrotation" in node.GetName().lower():
            parameterNode.SetNodeReferenceID("mandiblePlaneOfRotation", node.GetID())
            break
    else:
        logging.warning("mandiblePlaneOfRotation not found in scene")

if parameterNode.GetNodeReference("fibulaLine") is None:
    lineNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsLineNode")
    for i in range(lineNodes.GetNumberOfItems()):
        node = lineNodes.GetItemAsObject(i)
        if "fibulaline" in node.GetName().lower():
            parameterNode.SetNodeReferenceID("fibulaLine", node.GetID())
            break
    else:
        logging.warning("fibulaLine not found in scene")

# Call the method
_bonereconstructionplanner_logic.onGenerateFibulaPlanesTimerTimeout()

print("[BoneReconstructionPlanner] Step cb_step_24 completed.")