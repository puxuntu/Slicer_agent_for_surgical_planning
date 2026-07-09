# --- ReverseShoulderArthroplasty: Click the "3D Reconstruction" button. ---
import slicer
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'SlicerScrewPlanner':
    try:
        slicer.util.selectModule('SlicerScrewPlanner')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'SlicerScrewPlanner': {_module_enter_error}")
# precondition:end

# Drive the extension's own widget handler on the live module widget:
# it performs the full action (reads selected nodes, creates the
# output nodes downstream steps depend on, toggles dependent UI).
_widget = None
try:
    _widget = slicer.util.getModuleWidget('SlicerScrewPlanner')
except Exception:
    _widget = None
if _widget is None:
    try:
        _widget = slicer.modules.slicerscrewplanner.widgetRepresentation().self()
    except Exception:
        _widget = None
if _widget is None:
    raise RuntimeError("Could not obtain the SlicerScrewPlanner module widget for 'reconstruct3DButton'.")
if not hasattr(_widget, 'onReconstruct3D'):
    raise RuntimeError("SlicerScrewPlanner widget has no handler 'onReconstruct3D' for 'reconstruct3DButton'; regenerate the CLI.")
_widget.onReconstruct3D()
print("[ReverseShoulderArthroplasty] Step 'cb_step_11': clicked 'reconstruct3DButton' via onReconstruct3D().")

