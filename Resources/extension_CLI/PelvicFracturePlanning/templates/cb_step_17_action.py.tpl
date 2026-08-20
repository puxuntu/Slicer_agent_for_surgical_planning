# --- PelvicFracturePlanning: If further adjustments are required, tick the "Manually adjust a fragment" checkbox. If not, jump to step 22. ---
# [source drive] derived from the scanned signal connection -- do not rewrite.
import slicer
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'PelvicFracturePlanning':
    try:
        slicer.util.selectModule('PelvicFracturePlanning')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'PelvicFracturePlanning': {_module_enter_error}")
# precondition:end

# Drive the extension's own widget handler on the live module widget:
# it performs the full action (reads selected nodes, creates the
# output nodes downstream steps depend on, toggles dependent UI).
_widget = None
try:
    _widget = slicer.util.getModuleWidget('PelvicFracturePlanning')
except Exception:
    _widget = None
if _widget is None:
    try:
        _widget = slicer.modules.pelvicfractureplanning.widgetRepresentation().self()
    except Exception:
        _widget = None
if _widget is None:
    raise RuntimeError("Could not obtain the PelvicFracturePlanning module widget for 'chkManualAdjust'.")
if not hasattr(_widget, 'onManualAdjustToggled'):
    raise RuntimeError("PelvicFracturePlanning widget has no handler 'onManualAdjustToggled' for 'chkManualAdjust'; regenerate the CLI.")
# Resolve the bound control by name across the ways a Slicer
# extension can expose it (.ui object, direct self.<name>
# attribute, or objectName in the widget tree), then set its
# checked state (signals blocked to avoid a double-fire) and
# invoke the handler once. Setting the REAL control state is
# what lets a later programmatic setChecked(opposite) actually
# emit toggled and run the handler (e.g. an 'Update' button that
# unchecks the box to hide 3D interaction handles).
_ctrl = None
_ui = _widget.ui if hasattr(_widget, 'ui') else None
if _ui is not None and hasattr(_ui, 'chkManualAdjust'):
    _ctrl = _ui.chkManualAdjust
if _ctrl is None and hasattr(_widget, 'chkManualAdjust'):
    _ctrl = _widget.chkManualAdjust
if _ctrl is None:
    try:
        _found = slicer.util.findChildren(_widget, name='chkManualAdjust')
        _ctrl = _found[0] if _found else None
    except Exception:
        _ctrl = None
if _ctrl is not None:
    try:
        _ctrl.blockSignals(True)
        _ctrl.checked = True
        _ctrl.blockSignals(False)
    except Exception:
        pass
_widget.onManualAdjustToggled(True)
print("[PelvicFracturePlanning] Step 'cb_step_17': set 'chkManualAdjust' = True via onManualAdjustToggled.")

