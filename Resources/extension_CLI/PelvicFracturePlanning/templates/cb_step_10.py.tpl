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

# Retrieve nodes from cross-step cached IDs
_fragment_model = None
_adjust_transform = None
_adjusted_model = None
try:
    _fragment_model = slicer.mrmlScene.GetNodeByID(_pelvicfractureplanning_fragmentmodel_id)
except NameError:
    pass
try:
    _adjust_transform = slicer.mrmlScene.GetNodeByID(_pelvicfractureplanning_adjusttransform_id)
except NameError:
    pass
try:
    _adjusted_model = slicer.mrmlScene.GetNodeByID(_pelvicfractureplanning_adjustedmodel_id)
except NameError:
    pass

if _fragment_model is None:
    raise RuntimeError("Fragment model node not found. Ensure prior adjustment step has run.")
if _adjust_transform is None:
    raise RuntimeError("Adjustment transform not found. Ensure transform has been created.")
if _adjusted_model is None:
    raise RuntimeError("Adjusted model node not found. Ensure output model has been prepared.")

Apply_transform_to_polydata(_fragment_model, _adjust_transform, _adjusted_model)

print("[PelvicFracturePlanning] Step 'cb_step_10' completed.")