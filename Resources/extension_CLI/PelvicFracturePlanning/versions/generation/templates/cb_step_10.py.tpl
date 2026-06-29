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

# Get or create the shared logic instance
try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

# Retrieve required node IDs from cross-step cache
try:
    _fragmentModelID = _pelvicfractureplanning_FragmentModel_id
except NameError:
    raise RuntimeError("Missing cached FragmentModel node ID from previous step.")
try:
    _adjustTransformID = _pelvicfractureplanning_AdjustTransform_id
except NameError:
    raise RuntimeError("Missing cached AdjustTransform node ID from previous step.")
try:
    _adjustedModelID = _pelvicfractureplanning_AdjustedModel_id
except NameError:
    raise RuntimeError("Missing cached AdjustedModel node ID from previous step.")

FragmentModel = slicer.mrmlScene.GetNodeByID(_fragmentModelID)
AdjustTransform = slicer.mrmlScene.GetNodeByID(_adjustTransformID)
AdjustedModel = slicer.mrmlScene.GetNodeByID(_adjustedModelID)

if any(node is None for node in [FragmentModel, AdjustTransform, AdjustedModel]):
    raise RuntimeError("One or more required nodes could not be resolved from cached IDs.")

Apply_transform_to_polydata(FragmentModel, AdjustTransform, AdjustedModel)

print("[PelvicFracturePlanning] Step 'cb_step_10' completed.")