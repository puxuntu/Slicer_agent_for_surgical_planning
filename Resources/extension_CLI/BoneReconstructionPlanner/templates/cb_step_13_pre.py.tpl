# --- BoneReconstructionPlanner: Manually click and draw on the "Red" view to create a curve along the mandible. (Setup) ---
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

# Start the mandibular curve placement mode
logic.addMandibularCurve()

# Retrieve the newly created curve node from the parameter node
parameterNode = logic.getParameterNode()
node = parameterNode.GetNodeReference("mandibleCurve")
if node is None:
    raise RuntimeError("addMandibularCurve() did not set the mandibleCurve reference.")

_bonereconstructionplanner_cb_step_13_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_13", _bonereconstructionplanner_cb_step_13_id, _workflow_runtime_repeat_index)

print('[BoneReconstructionPlanner] Please manually click and draw on the "Red" view to create a curve along the mandible.')
print("When finished, press the 'Done' button in the workflow panel.")
