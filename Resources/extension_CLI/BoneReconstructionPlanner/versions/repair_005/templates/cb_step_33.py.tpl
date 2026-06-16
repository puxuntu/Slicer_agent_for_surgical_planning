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

# Clear the checkbox (uncheck) and hide the original mandible model,
# which also hides the cutting planes and interaction holders.
_module_widget = slicer.modules.bonereconstructionplanner.widgetRepresentation().self()
_module_widget.ui.showOriginalMandibleCheckBox.checked = False
parameterNode.SetParameter('showOriginalMandible', 'False')
_module_widget.setOriginalMandibleVisility(False)
parameterNode.Modified()

_bonereconstructionplanner_logic = logic
print("[BoneReconstructionPlanner] Step 'cb_step_33' completed.")