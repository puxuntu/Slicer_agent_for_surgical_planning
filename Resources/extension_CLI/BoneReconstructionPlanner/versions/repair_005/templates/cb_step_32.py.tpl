# --- BoneReconstructionPlanner: When the reconstruction is satisfactory, in the BoneReconstructionPlanner module's "Mandible planes" row, toggle off the eye-icon tool button to hide the mandibular cut planes. ---
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
# Toggle off the eye icon to hide mandibular cut planes
_module_widget = slicer.modules.bonereconstructionplanner.widgetRepresentation().self()
_module_widget.ui.showMandiblePlanesToolButton.checked = False
parameterNode.SetParameter('showMandiblePlanes', 'False')
try:
    parameterNode.Modified()
except Exception:
    pass
# Apply the parameter via the extension's own applier method
_module_widget.setMandiblePlanesVisibility(False)
_bonereconstructionplanner_logic = logic
print("[BoneReconstructionPlanner] Step 'cb_step_32' completed.")
