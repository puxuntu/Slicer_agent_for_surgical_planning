# --- BoneReconstructionPlanner: Draw a line over the fibula in "3D View 2", starting with the first point distally and the last point proximally. (Process) ---
import slicer
from SlicerAIAgentLib.workflow_state import resolve_interaction_node

node = resolve_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_20", "vtkMRMLMarkupsLineNode", _workflow_runtime_repeat_index)
if node is None:
    node = slicer.mrmlScene.GetNodeByID(_bonereconstructionplanner_cb_step_20_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_20'")

# Store the placed node on the extension parameter node for later steps
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'BoneReconstructionPlanner':
    try:
        slicer.util.selectModule('BoneReconstructionPlanner')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'BoneReconstructionPlanner': {_module_enter_error}")
# precondition:end

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

print("[BoneReconstructionPlanner] Step 'cb_step_20' processed with %d control points." % node.GetNumberOfControlPoints())
