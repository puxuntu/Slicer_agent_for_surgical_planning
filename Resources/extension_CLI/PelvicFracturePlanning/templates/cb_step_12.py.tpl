# --- PelvicFracturePlanning: Click the "Plan Screws" button. ---
import slicer

# precondition:begin
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'PelvicFracturePlanning':
    try:
        slicer.util.selectModule('PelvicFracturePlanning')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'PelvicFracturePlanning': {_module_enter_error}")
# precondition:end

# Create output screw model node.
_outputScrew = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "ScrewPlan")

# Call logic.plan_screws with positional arguments.
logic.plan_screws(_outputScrew, None)

# Store the output node ID for downstream steps.
try:
    _PelvicFracturePlanning_screw_id = _outputScrew.GetID()
except Exception:
    pass

print("[PelvicFracturePlanning] Step 'cb_step_12' completed.")
