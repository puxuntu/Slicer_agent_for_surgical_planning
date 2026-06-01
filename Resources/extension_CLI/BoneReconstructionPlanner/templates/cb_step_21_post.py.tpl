# --- BoneReconstructionPlanner: 21. Draw a line over the fibula in "3D View 2", starting with the first point distally and the last point proximally. (Process) ---
import slicer

node = slicer.mrmlScene.GetNodeByID(_bonereconstructionplanner_cb_step_21_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_21'")

# Validate user input
numPoints = node.GetNumberOfControlPoints()
if numPoints < 2:
    raise RuntimeError("Need at least 2 control points, got %d. Please add more." % numPoints)

# Store the placed node on the extension parameter node for later steps
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
parameterNode = logic.getParameterNode()
parameterNode.SetNodeReferenceID("fibulaLine", node.GetID())
_bonereconstructionplanner_logic = logic

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[BoneReconstructionPlanner] Step 'cb_step_21' processed with %d control points." % node.GetNumberOfControlPoints())
