# --- BoneReconstructionPlanner: If the fibula is from the right leg, tick the "Right side leg" checkbox. ---
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
# Resolve the control across .ui / direct-attribute / widget-tree
# exposure styles so this works for any extension, not only ones
# that load a Qt Designer .ui file.
try:
    _module_widget = slicer.modules.bonereconstructionplanner.widgetRepresentation().self()
    _sync_ctrl = None
    _ui = _module_widget.ui if hasattr(_module_widget, 'ui') else None
    if _ui is not None and hasattr(_ui, 'rightSideLegFibulaCheckBox'):
        _sync_ctrl = _ui.rightSideLegFibulaCheckBox
    if _sync_ctrl is None and hasattr(_module_widget, 'rightSideLegFibulaCheckBox'):
        _sync_ctrl = _module_widget.rightSideLegFibulaCheckBox
    if _sync_ctrl is None:
        try:
            _found = slicer.util.findChildren(_module_widget, name='rightSideLegFibulaCheckBox')
            _sync_ctrl = _found[0] if _found else None
        except Exception:
            _sync_ctrl = None
    if _sync_ctrl is not None:
        _sync_ctrl.checked = True
except Exception:
    pass
# Final state was not explicit; apply source-derived/default truthy state for rightSideLegFibula
parameterNode.SetParameter('rightSideLegFibula', 'True')
try:
    parameterNode.Modified()
except Exception:
    pass
_bonereconstructionplanner_logic = logic
print("[BoneReconstructionPlanner] Step 'cb_step_1' completed.")
