# --- ZygomaticImplantPlanner: Manually adjust the symmetry plane. (Setup) ---
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

node = logic.findRole(logic.R_PLANE)
if node is None:
    raise RuntimeError('No symmetry plane node found from the previous step.')

displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)

# Enable interactive handles on the symmetry plane using the extension's own mechanism.
logic.setSymmetryPlaneInteraction(True)

slicer.modules.markups.logic().SetActiveListID(node)
_zygomaticimplantplanner_cb_step_11_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, 'cb_step_11', _zygomaticimplantplanner_cb_step_11_id, _workflow_runtime_repeat_index)

print('[ZygomaticImplantPlanner] Please Manually adjust the symmetry plane.')
print('When finished, press the \'Done\' button in the workflow panel.')
