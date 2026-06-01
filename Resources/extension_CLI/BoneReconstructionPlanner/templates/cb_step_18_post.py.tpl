# --- BoneReconstructionPlanner: 18. Place one mandibular cut plane. (Process) ---
import slicer

node = slicer.mrmlScene.GetNodeByID(_bonereconstructionplanner_cb_step_18_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_18'. Ensure pre-step was executed.")

# Validate user input: at least one control point
numPoints = node.GetNumberOfControlPoints()
if numPoints < 1:
    raise RuntimeError("Need at least 1 control point, got {0}. Please add more.".format(numPoints))

# Store the placed node reference on the extension parameter node
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

parameterNode = logic.getParameterNode()
# The extension manages planes internally via observers; we just store for tracking
parameterNode.SetNodeReferenceID("mandiblePlaneOfRotation", node.GetID())

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[BoneReconstructionPlanner] Step 'cb_step_18' processed with {0} control points.".format(numPoints))
