# --- BoneReconstructionPlanner: In the BoneReconstructionPlanner module, in the "Mandible planes" row, toggle on the eye-icon tool button to show the mandibular cut planes. ---
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
# Resolve the control across .ui / widget-tree exposure styles so
# this works for any extension, not only ones that load a Qt Designer
# .ui file. The tool button lives in the Qt Designer .ui (accessed via
# the widget's `ui` attribute) or in the widget tree.
try:
    _module_widget = slicer.modules.bonereconstructionplanner.widgetRepresentation().self()
    _sync_ctrl = None
    _ui = _module_widget.ui if hasattr(_module_widget, 'ui') else None
    if _ui is not None and hasattr(_ui, 'showMandiblePlanesToolButton'):
        _sync_ctrl = _ui.showMandiblePlanesToolButton
    if _sync_ctrl is None:
        try:
            _found = slicer.util.findChildren(_module_widget, name='showMandiblePlanesToolButton')
            _sync_ctrl = _found[0] if _found else None
        except Exception:
            _sync_ctrl = None
    if _sync_ctrl is not None:
        _sync_ctrl.checked = True
except Exception:
    pass
parameterNode.SetParameter('showMandiblePlanes', 'True')
try:
    parameterNode.Modified()
except Exception:
    pass
# Apply the parameter via the extension's own applier method —
# a bare SetParameter only records state; GUI observers may
# recompute it differently.
_module_widget = slicer.modules.bonereconstructionplanner.widgetRepresentation().self()
_module_widget.setMandiblePlanesVisibility(True)
_bonereconstructionplanner_logic = logic
print("[BoneReconstructionPlanner] Step 'cb_step_29' completed.")