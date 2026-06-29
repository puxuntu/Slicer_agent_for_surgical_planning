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

try:
    logic = _pelvicfractureplanning_logic
except NameError:
    logic = slicer.util.getModuleLogic('PelvicFracturePlanning')
    _pelvicfractureplanning_logic = logic

paramNode = logic.getParameterNode()

# Retrieve the fragment model, adjustment transform, and adjusted model from the parameter node
# These were set by previous steps (e.g., step 9) as node references.
fragmentModel = paramNode.GetNodeReference("FragmentModel")
adjustTransform = paramNode.GetNodeReference("AdjustTransform")
adjustedModel = paramNode.GetNodeReference("AdjustedModel")

# Validate that all required nodes exist
if fragmentModel is None:
    raise RuntimeError("FragmentModel node reference not found in parameter node. Ensure step 9 completed successfully.")
if adjustTransform is None:
    raise RuntimeError("AdjustTransform node reference not found in parameter node. Ensure step 9 completed successfully.")
if adjustedModel is None:
    raise RuntimeError("AdjustedModel node reference not found in parameter node. Ensure step 9 completed successfully.")

# Apply the manual adjustment to the fragment
Apply_transform_to_polydata(fragmentModel, adjustTransform, adjustedModel)

print("[PelvicFracturePlanning] Step 'cb_step_10' completed.")
