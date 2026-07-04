# --- CranialImplantPlanning: Click the "Cut Defect" button. ---
import slicer
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'SlicerE3Implant':
    try:
        slicer.util.selectModule('SlicerE3Implant')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'SlicerE3Implant': {_module_enter_error}")
# precondition:end

# Drive the extension's own widget handler on the live module widget:
# it performs the full action (reads selected nodes, creates the
# output nodes downstream steps depend on, toggles dependent UI).
_widget = None
try:
    _widget = slicer.util.getModuleWidget('SlicerE3Implant')
except Exception:
    _widget = None
if _widget is None:
    try:
        _widget = slicer.modules.slicere3implant.widgetRepresentation().self()
    except Exception:
        _widget = None
if _widget is None:
    raise RuntimeError("Could not obtain the SlicerE3Implant module widget for 'cutButton'.")
if not hasattr(_widget, 'onCutDefect'):
    raise RuntimeError("SlicerE3Implant widget has no handler 'onCutDefect' for 'cutButton'; regenerate the CLI.")
_widget.onCutDefect()
print("[CranialImplantPlanning] Step 'cb_step_16': clicked 'cutButton' via onCutDefect().")

