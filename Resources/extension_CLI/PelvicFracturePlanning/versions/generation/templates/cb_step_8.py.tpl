# --- PelvicFracturePlanning: Choose which fragment needs adjustment in the "Fragment" selection box. ---
import slicer

# precondition:begin
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'PelvicFracturePlanning':
    try:
        slicer.util.selectModule('PelvicFracturePlanning')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'PelvicFracturePlanning': {_module_enter_error}")
# precondition:end

# Retrieve shared logic instance
try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning.PelvicFracturePlanningLogic import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

parameterNode = logic.getParameterNode()

# No retrieval needed; step is a user choice via GUI.
print("[PelvicFracturePlanning] Step 8: Please select the fragment that needs adjustment from the 'Fragment' selection box in the GUI.")

print("[PelvicFracturePlanning] Step 'cb_step_8' completed.")
