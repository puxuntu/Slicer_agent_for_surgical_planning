try:
    import BoneReconstructionPlanner
except ImportError:
    raise ImportError("BoneReconstructionPlanner extension is not installed. Please install it from the Slicer Extension Manager.")

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlanner.BoneReconstructionPlannerLogic()
    # Set a default parent folder (scene root) if not already configured
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    logic.parentFolderItemID = shNode.GetSceneItemID()

# Retrieve the markup node placed by the user
node = slicer.mrmlScene.GetNodeByID(_bonereconstructionplanner_cb_step_10_id)
if node is None:
    raise ValueError("Markup node not found. Cannot continue.")

# Validate at least 2 control points
numPoints = node.GetNumberOfControlPoints()
if numPoints < 2:
    raise ValueError(f"At least 2 control points are required, but only {numPoints} were placed.")

# Optional: assign the markup node to logic if needed (not used by addFibulaLine, but for consistency)
# logic.inputMarkupNode = node   # Not required by the method, but we could set it

# Call the method
logic.addFibulaLine()

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

# Store logic instance for subsequent steps
_bonereconstructionplanner_logic = logic

print(f"BoneReconstructionPlanner: Fibula line added from {numPoints} control points.")