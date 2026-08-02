# --- ZygomaticImplantPlanner: Manually adjust the separation plane. (Setup) ---
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

node = logic.findRole(logic.R_MMPLANE)
if node is None:
    raise RuntimeError("No maxilla/mandible separation plane node found from previous step. Run the maxilla/mandible separation step first.")

displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)

logic._freePlaneHandles(node)
slicer.modules.markups.logic().SetActiveListID(node)
_zygomaticimplantplanner_cb_step_18_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_18", _zygomaticimplantplanner_cb_step_18_id, _workflow_runtime_repeat_index)

print("[ZygomaticImplantPlanner] Please manually adjust the maxilla/mandible separation plane using its interactive handles.")
print("When finished, press the 'Done' button in the workflow panel.")
