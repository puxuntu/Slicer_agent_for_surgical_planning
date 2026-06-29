# --- PelvicFracturePlanning: Click the "Run Step 5: Plan Screws" button. ---
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

# Get the logic (cached across steps)
try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

# Create output screw model node
screwModelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', 'ScrewPlan')

# Call the logic method to plan screw trajectories (pass progressDiag as positional None)
logic.plan_screws(screwModelNode, None)

# Cache the screw node ID for downstream steps
_pelvicfrac_screw_id = screwModelNode.GetID()

print("[PelvicFracturePlanning] Step 'cb_step_11' completed.")
