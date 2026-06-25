# --- SlicerOrbitSurgerySim: Tick the "Enable 3D interaction transform handle" checkbox. ---
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
    raise RuntimeError("Could not obtain the PlateRegistration module widget for 'interactionTransformCheckbox'.")
if not hasattr(_widget, 'onInteractionTransform'):
    raise RuntimeError("PlateRegistration widget has no handler 'onInteractionTransform' for 'interactionTransformCheckbox'; regenerate the CLI.")
# Set the control's checked state (signals blocked to avoid a
# double-fire), then invoke the handler once. The handler may read
# the widget state (no arg) or accept the new bool — try the bool.
_ctrl = None
try:
    _ctrl = _widget.ui.interactionTransformCheckbox
except Exception:
    _ctrl = None
if _ctrl is not None:
    try:
        _ctrl.blockSignals(True)
        _ctrl.checked = True
        _ctrl.blockSignals(False)
    except Exception:
        pass
try:
    _widget.onInteractionTransform(True)
except TypeError:
    _widget.onInteractionTransform()
print("[SlicerOrbitSurgerySim] Step 'cb_step_7': set 'interactionTransformCheckbox' = True via onInteractionTransform.")

