try:
    logic = _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    logic = BoneReconstructionPlannerLogic()

node = slicer.mrmlScene.GetNodeByID(_bonereconstructionplanner_cb_step_9_id)
if node is None:
    raise ValueError("Markup node not found")
nPoints = node.GetNumberOfControlPoints()
if nPoints < 1:
    raise ValueError("At least one control point required")

# Ensure required state attributes exist
if not hasattr(logic, 'PLANE_SIDE_SIZE'):
    logic.PLANE_SIDE_SIZE = 30.0
if not hasattr(logic, 'PLANE_GLYPH_SCALE'):
    logic.PLANE_GLYPH_SCALE = 3.0

logic.addCutPlane()

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

_bonereconstructionplanner_logic = logic

print(f"[BoneReconstructionPlanner] Step 9 completed. Control points placed: {nPoints}")