# --- ZygomaticImplantPlanner: Click the "4. Identify zygomatic bones" button. ---
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
    raise RuntimeError("Could not obtain the ZygomaticImplantPlanner module widget for 'step4Button'.")
if not hasattr(_widget, 'onStep4'):
    raise RuntimeError("ZygomaticImplantPlanner widget has no handler 'onStep4' for 'step4Button'; regenerate the CLI.")
_widget.onStep4()
print("[ZygomaticImplantPlanner] Step 'cb_step_16': clicked 'step4Button' via onStep4().")

