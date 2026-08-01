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
    import ZygomaticImplantPlanner
except ImportError:
    raise RuntimeError("The ZygomaticImplantPlanner extension is not installed. Install it from the Slicer Extension Manager.")

try:
    logic = _zygomaticimplantplanner_logic
except NameError:
    logic = ZygomaticImplantPlanner.ZygomaticImplantPlannerLogic()
    _zygomaticimplantplanner_logic = logic

left_planes = list(logic.findAllRole(logic.R_BOUND_L) or [])
right_planes = list(logic.findAllRole(logic.R_BOUND_R) or [])
boundary_planes = left_planes + right_planes
if not boundary_planes:
    raise RuntimeError('No boundary plane nodes found from the previous step.')

# Show all handles and visibility on both boundary planes so the user can adjust them.
for plane in boundary_planes:
    displayNode = plane.GetDisplayNode()
    if displayNode is not None:
        displayNode.SetVisibility(True)
    logic._freePlaneHandles(plane)

node = boundary_planes[0]
slicer.modules.markups.logic().SetActiveListID(node)
_zygomaticimplantplanner_cb_step_22_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, 'cb_step_22', _zygomaticimplantplanner_cb_step_22_id, _workflow_runtime_repeat_index)

print('[ZygomaticImplantPlanner] Please Manually adjust the boundary planes.')
print('When finished, press the \'Done\' button in the workflow panel.')
