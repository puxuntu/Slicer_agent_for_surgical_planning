# --- ReverseShoulderArthroplasty: Click the "Prosthesis implantation" button. ---
import slicer
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'SlicerScrewPlanner3':
    try:
        slicer.util.selectModule('SlicerScrewPlanner3')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'SlicerScrewPlanner3': {_module_enter_error}")
# precondition:end

# Drive the extension's own widget handler on the live module widget:
# it performs the full action (reads selected nodes, creates the
# output nodes downstream steps depend on, toggles dependent UI).
_widget = None
try:
    _widget = slicer.util.getModuleWidget('SlicerScrewPlanner3')
except Exception:
    _widget = None
if _widget is None:
    try:
        _widget = slicer.modules.slicerscrewplanner3.widgetRepresentation().self()
    except Exception:
        _widget = None
if _widget is None:
    raise RuntimeError("Could not obtain the SlicerScrewPlanner3 module widget for 'positionBaseplateButton'.")
if not hasattr(_widget, 'onPositionBaseplate'):
    raise RuntimeError("SlicerScrewPlanner3 widget has no handler 'onPositionBaseplate' for 'positionBaseplateButton'; regenerate the CLI.")
_widget.onPositionBaseplate()
print("[ReverseShoulderArthroplasty] Step 'cb_step_16': clicked 'positionBaseplateButton' via onPositionBaseplate().")

