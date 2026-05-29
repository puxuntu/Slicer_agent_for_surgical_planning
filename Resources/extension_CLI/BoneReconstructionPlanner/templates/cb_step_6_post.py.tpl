try:
    logic = _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    logic = BoneReconstructionPlannerLogic()

# Retrieve the markup node with control points placed by the user
node = slicer.mrmlScene.GetNodeByID(_bonereconstructionplanner_cb_step_6_id)
if node is None:
    raise ValueError("Markup node not found by ID: " + str(_bonereconstructionplanner_cb_step_6_id))

# Validate control points (minimum 0, but we check for positive count)
numPoints = node.GetNumberOfControlPoints()
if numPoints < 0:
    # Should never happen, but guard against potential negative returns
    numPoints = 0

# Set up required state on the logic instance (assumes logic expects inputMarkupNode)
if hasattr(logic, 'inputMarkupNode'):
    logic.inputMarkupNode = node

# Call the method
logic.addMandibularCurve()

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

# Store the logic instance for subsequent steps
_bonereconstructionplanner_logic = logic

# Print completion message with brace escaping for f-string
print(f"BoneReconstructionPlanner: mandibular curve created from {numPoints} control points.")