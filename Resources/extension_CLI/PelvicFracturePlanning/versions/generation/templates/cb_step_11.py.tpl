# --- PelvicFracturePlanning: Click the "Run Step 5: Plan Screws" button. ---
import slicer

# precondition:begin
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'PelvicFracturePlanning':
    try:
        slicer.util.selectModule('PelvicFracturePlanning')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'PelvicFracturePlanning': {_module_enter_error}")
# precondition:end

try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

# Create output model node for screws
_outputScrew = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "plan_screws_output")
_outputScrew_id = _outputScrew.GetID()

# Call the proven method with the model node and no progress dialog (headless)
logic.plan_screws(OutputScrew=_outputScrew, progressDiag=None)

print("[PelvicFracturePlanning] Step 'cb_step_11' completed. Screws planned into model node: " + _outputScrew.GetName())
