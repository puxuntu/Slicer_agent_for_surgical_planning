# --- PelvicFracturePlanning: Click the "Apply adjustments" button. ---
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

# Retrieve cross-step cached node IDs
try:
    _fragment_model_id = _pelvicfractureplanning_fragmentmodel_id
    fragmentModel = slicer.mrmlScene.GetNodeByID(_fragment_model_id)
except NameError:
    fragmentModel = None

try:
    _adjust_transform_id = _pelvicfractureplanning_adjusttransform_id
    adjustTransform = slicer.mrmlScene.GetNodeByID(_adjust_transform_id)
except NameError:
    adjustTransform = None

try:
    _adjusted_model_id = _pelvicfractureplanning_adjustedmodel_id
    adjustedModel = slicer.mrmlScene.GetNodeByID(_adjusted_model_id)
except NameError:
    adjustedModel = None

# Validate inputs
if None in (fragmentModel, adjustTransform, adjustedModel):
    raise RuntimeError("Missing required nodes for Apply_transform_to_polydata. Ensure prior steps completed.")

# Call extension function with required arguments
Apply_transform_to_polydata(fragmentModel, adjustTransform, adjustedModel)

print("[PelvicFracturePlanning] Step 'cb_step_10' completed: adjustments applied.")