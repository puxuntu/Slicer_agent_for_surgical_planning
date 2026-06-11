# --- BoneReconstructionPlanner: Draw a line over the fibula in "3D View 2", starting with the first point distally and the last point proximally. (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

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
    _bonereconstructionplanner_logic = logic

# Start the fibula line placement mode
logic.addFibulaLine()

# Retrieve the newly created line node from the parameter node
parameterNode = logic.getParameterNode()
node = parameterNode.GetNodeReference("fibulaLine")
if node is None:
    raise RuntimeError("addFibulaLine() did not set the fibulaLine reference.")

_bonereconstructionplanner_cb_step_20_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_20", _bonereconstructionplanner_cb_step_20_id, _workflow_runtime_repeat_index)

print('[BoneReconstructionPlanner] Please draw a line over the fibula in "3D View 2", starting with the first point distally and the last point proximally.')
print("When finished, press the 'Done' button in the workflow panel.")
