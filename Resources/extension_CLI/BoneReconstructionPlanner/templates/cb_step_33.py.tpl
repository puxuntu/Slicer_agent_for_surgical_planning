# --- BoneReconstructionPlanner: Clear the "Show original mandible model" checkbox. ---
import slicer
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

parameterNode = logic.getParameterNode()
# Sync the bound UI control (mirrors the user's click) so
# GUI-driven parameter syncs cannot ratchet the value back.
try:
    _module_widget = slicer.modules.bonereconstructionplanner.widgetRepresentation().self()
    _module_widget.ui.showOriginalMandibleCheckBox.checked = False
except Exception:
    pass
parameterNode.SetParameter('showOriginalMandible', 'False')
try:
    parameterNode.Modified()
except Exception:
    pass
# Apply the parameter via the extension's own applier method —
# a bare SetParameter only records state; GUI observers may
# recompute it differently.
_module_widget = slicer.modules.bonereconstructionplanner.widgetRepresentation().self()
_module_widget.setOriginalMandibleVisility(False)
_bonereconstructionplanner_logic = logic
print("[BoneReconstructionPlanner] Step 'cb_step_33' completed.")
