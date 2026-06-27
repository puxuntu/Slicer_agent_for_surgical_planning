# --- PelvicFracturePlanning: Click the "Plan Screws" button. ---
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

# Retrieve logic instance
try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

# Create output screw model node
_screwNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode')
_screwNode.SetName('PelvicScrews')

# Call the proven method logic.plan_screws
logic.plan_screws(OutputScrew=_screwNode, progressDiag=None)
print("[PelvicFracturePlanning] Step 'cb_step_12': planned screw trajectories.")
