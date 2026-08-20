# --- PelvicFracturePlanning: Click the "Apply template adjustment" button. ---
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
    raise RuntimeError("Could not obtain the PelvicFracturePlanning module widget for 'btnApplyTemplateAdjust'.")
if not hasattr(_widget, 'onApplyTemplateAdjust'):
    raise RuntimeError("PelvicFracturePlanning widget has no handler 'onApplyTemplateAdjust' for 'btnApplyTemplateAdjust'; regenerate the CLI.")
_widget.onApplyTemplateAdjust()
print("[PelvicFracturePlanning] Step 'cb_step_13': clicked 'btnApplyTemplateAdjust' via onApplyTemplateAdjust().")

