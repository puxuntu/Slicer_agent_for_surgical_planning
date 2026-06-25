# --- SlicerOrbitSurgerySim: Click "Posterior stop and antero-posterior stops alignment" button. ---
import slicer
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'PlateRegistration':
    try:
        slicer.util.selectModule('PlateRegistration')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'PlateRegistration': {_module_enter_error}")
# precondition:end

# Drive the extension's own widget handler on the live module widget:
# it performs the full action (reads selected nodes, creates the
# output nodes downstream steps depend on, toggles dependent UI).
_widget = None
try:
    _widget = slicer.util.getModuleWidget('PlateRegistration')
except Exception:
    _widget = None
if _widget is None:
    try:
        _widget = slicer.modules.plateregistration.widgetRepresentation().self()
    except Exception:
        _widget = None
if _widget is None:
    raise RuntimeError("Could not obtain the PlateRegistration module widget for 'posteriorStopRegistrationPushButton'.")
if not hasattr(_widget, 'onRotation_p_stop_pushButton'):
    raise RuntimeError("PlateRegistration widget has no handler 'onRotation_p_stop_pushButton' for 'posteriorStopRegistrationPushButton'; regenerate the CLI.")
_widget.onRotation_p_stop_pushButton()
print("[SlicerOrbitSurgerySim] Step 'cb_step_6': clicked 'posteriorStopRegistrationPushButton' via onRotation_p_stop_pushButton().")

