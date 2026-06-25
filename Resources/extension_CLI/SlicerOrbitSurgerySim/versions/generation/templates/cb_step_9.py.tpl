# --- SlicerOrbitSurgerySim: Click "Mark intersection" button. ---
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
    raise RuntimeError("Could not obtain the PlateRegistration module widget for 'createIntersectButton'.")
if not hasattr(_widget, 'onCreateIntersectButton'):
    raise RuntimeError("PlateRegistration widget has no handler 'onCreateIntersectButton' for 'createIntersectButton'; regenerate the CLI.")
_widget.onCreateIntersectButton()
print("[SlicerOrbitSurgerySim] Step 'cb_step_9': clicked 'createIntersectButton' via onCreateIntersectButton().")

