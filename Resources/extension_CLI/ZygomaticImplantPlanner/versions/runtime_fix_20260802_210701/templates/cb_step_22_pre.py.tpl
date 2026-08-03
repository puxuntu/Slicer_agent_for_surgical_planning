# --- ZygomaticImplantPlanner: Manually adjust the boundary planes. (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'ZygomaticImplantPlanner':
    try:
        slicer.util.selectModule('ZygomaticImplantPlanner')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'ZygomaticImplantPlanner': {_module_enter_error}")
# precondition:end

try:
    logic = _zygomaticimplantplanner_logic
except NameError:
    try:
        from ZygomaticImplantPlanner import ZygomaticImplantPlannerLogic
        logic = ZygomaticImplantPlannerLogic()
        _zygomaticimplantplanner_logic = logic
    except Exception:
        raise RuntimeError("ZygomaticImplantPlanner extension is not installed. Install it from the Extension Manager.")

_boundary_nodes = logic.findAllRole(logic.R_BOUND_L) or []
_boundary_nodes += logic.findAllRole(logic.R_BOUND_R) or []
_boundary_nodes = [n for n in _boundary_nodes if n is not None]
if not _boundary_nodes:
    raise RuntimeError("No boundary plane nodes found from previous step. Run the zygomatic computation step first.")

for planeNode in _boundary_nodes:
    displayNode = planeNode.GetDisplayNode()
    if displayNode is not None:
        displayNode.SetVisibility(True)
    logic._freePlaneHandles(planeNode)

node = _boundary_nodes[0]
slicer.modules.markups.logic().SetActiveListID(node)
_zygomaticimplantplanner_cb_step_22_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_22", _zygomaticimplantplanner_cb_step_22_id, _workflow_runtime_repeat_index)

print("[ZygomaticImplantPlanner] Please manually adjust the left and right boundary planes using their interactive handles.")
print("When finished, press the 'Done' button in the workflow panel.")
