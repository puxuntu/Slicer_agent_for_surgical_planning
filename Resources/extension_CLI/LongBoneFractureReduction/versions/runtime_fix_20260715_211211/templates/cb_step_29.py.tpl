# --- LongBoneFractureReduction: Click the "Reduce fracture" button. ---
import slicer
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'LongBoneFractureReduction':
    try:
        slicer.util.selectModule('LongBoneFractureReduction')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'LongBoneFractureReduction': {_module_enter_error}")
# precondition:end

# Drive the extension's own widget handler on the live module widget:
# it performs the full action (reads selected nodes, creates the
# output nodes downstream steps depend on, toggles dependent UI).
_widget = None
try:
    _widget = slicer.util.getModuleWidget('LongBoneFractureReduction')
except Exception:
    _widget = None
if _widget is None:
    try:
        _widget = slicer.modules.longbonefracturereduction.widgetRepresentation().self()
    except Exception:
        _widget = None
if _widget is None:
    raise RuntimeError("Could not obtain the LongBoneFractureReduction module widget for 'btnReduce'.")
if not hasattr(_widget, 'onReduce'):
    raise RuntimeError("LongBoneFractureReduction widget has no handler 'onReduce' for 'btnReduce'; regenerate the CLI.")
_widget.onReduce()
print("[LongBoneFractureReduction] Step 'cb_step_29': clicked 'btnReduce' via onReduce().")

