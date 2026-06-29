# --- PelvicFracturePlanning: Untick the "Edit Screw trajectories" checkbox. ---
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

# Obtain the module widget and untick the checkbox via its handler
_widget = slicer.util.getModuleWidget('PelvicFracturePlanning')
if _widget is None:
    raise RuntimeError("Could not obtain PelvicFracturePlanning widget.")

# Directly invoke the handler to disable screw editing (assumes handler exists)
if hasattr(_widget, 'onEditScrewsToggled'):
    _widget.onEditScrewsToggled(False)
else:
    # Fallback: set the checkbox state via UI if accessible
    if hasattr(_widget, 'ui') and hasattr(_widget.ui, 'chkEditScrews'):
        _widget.ui.chkEditScrews.checked = False
        _widget.onEditScrewsToggled(False)

print("[PelvicFracturePlanning] Step 'cb_step_15': Unticked 'Edit Screw trajectories'.")