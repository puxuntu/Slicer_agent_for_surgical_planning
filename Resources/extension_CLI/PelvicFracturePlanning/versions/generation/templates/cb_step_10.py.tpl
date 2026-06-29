# --- PelvicFracturePlanning: Click the "Apply adjustments" button. ---
import slicer
from PelvicFracturePlanning import Apply_transform_to_polydata

# precondition:begin
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'PelvicFracturePlanning':
    try:
        slicer.util.selectModule('PelvicFracturePlanning')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'PelvicFracturePlanning': {_module_enter_error}")
# precondition:end

# Ensure shared logic instance
try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

# Retrieve fragment model and adjustment transform from scene by name
fragmentModel = slicer.mrmlScene.GetFirstNodeByName("FragmentModel")
if fragmentModel is None:
    raise RuntimeError("FragmentModel node not found. Ensure a fragment is selected.")

adjustTransform = slicer.mrmlScene.GetFirstNodeByName("AdjustTransform")
if adjustTransform is None:
    raise RuntimeError("AdjustTransform node not found. Ensure adjustments have been made.")

# Create output adjusted model node
adjustedModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "AdjustedFragment")

# Apply the transform to the fragment polydata
Apply_transform_to_polydata(fragmentModel, adjustTransform, adjustedModel)

print("[PelvicFracturePlanning] Step 'cb_step_10' completed: adjustment applied to fragment.")
