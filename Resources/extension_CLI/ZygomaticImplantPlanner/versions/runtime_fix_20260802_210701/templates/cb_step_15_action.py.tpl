# --- ZygomaticImplantPlanner: If the mandible is still attached to the maxilla, tick the "The mandible is still attached to the maxilla" checkbox. If not, jump to step 20. ---
# [source drive] derived from the scanned signal connection -- do not rewrite.
import slicer
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'ZygomaticImplantPlanner':
    try:
        slicer.util.selectModule('ZygomaticImplantPlanner')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'ZygomaticImplantPlanner': {_module_enter_error}")
# precondition:end

# Drive the extension's own widget handler on the live module widget:
# it performs the full action (reads selected nodes, creates the
# output nodes downstream steps depend on, toggles dependent UI).
_widget = None
try:
    _widget = slicer.util.getModuleWidget('ZygomaticImplantPlanner')
except Exception:
    _widget = None
if _widget is None:
    try:
        _widget = slicer.modules.zygomaticimplantplanner.widgetRepresentation().self()
    except Exception:
        _widget = None
if _widget is None:
    raise RuntimeError("Could not obtain the ZygomaticImplantPlanner module widget for 'mandibleConnectedCheckBox'.")
if not hasattr(_widget, '_onMandibleConnectedToggled'):
    raise RuntimeError("ZygomaticImplantPlanner widget has no handler '_onMandibleConnectedToggled' for 'mandibleConnectedCheckBox'; regenerate the CLI.")
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
if _ui is not None and hasattr(_ui, 'mandibleConnectedCheckBox'):
    _ctrl = _ui.mandibleConnectedCheckBox
if _ctrl is None and hasattr(_widget, 'mandibleConnectedCheckBox'):
    _ctrl = _widget.mandibleConnectedCheckBox
if _ctrl is None:
    try:
        _found = slicer.util.findChildren(_widget, name='mandibleConnectedCheckBox')
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
# The handler requires the control's checked state as its single argument.
# Invoke it exactly once with the state this step requires.
_widget._onMandibleConnectedToggled(True)
print("[ZygomaticImplantPlanner] Step 'cb_step_15': set 'mandibleConnectedCheckBox' = True via _onMandibleConnectedToggled.")
