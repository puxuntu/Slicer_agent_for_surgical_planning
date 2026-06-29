import slicer
from PelvicFracturePlanning import Apply_transform_to_polydata

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

# Retrieve nodes from cross-step cached IDs (set by interaction step 9)
try:
    fragmentModel = slicer.mrmlScene.GetNodeByID(_pelvicfractureplanning_fragmentModel_id)
    adjustTransform = slicer.mrmlScene.GetNodeByID(_pelvicfractureplanning_adjustTransform_id)
    adjustedModel = slicer.mrmlScene.GetNodeByID(_pelvicfractureplanning_adjustedModel_id)
except NameError as e:
    raise RuntimeError(f"Missing cached node ID from an earlier step: {e}")

if fragmentModel is None or adjustTransform is None or adjustedModel is None:
    raise RuntimeError("One or more required nodes could not be resolved from cached IDs.")

# Apply the transform to the polydata
Apply_transform_to_polydata(fragmentModel, adjustTransform, adjustedModel)

print("[PelvicFracturePlanning] Step 'cb_step_10' completed.")
