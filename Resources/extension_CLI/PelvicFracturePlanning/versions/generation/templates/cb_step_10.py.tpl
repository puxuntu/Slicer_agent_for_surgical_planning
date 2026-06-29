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

try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

# Retrieve nodes for transform application
_fragmentModel = slicer.util.getNode("FragmentModel")
if _fragmentModel is None:
    raise RuntimeError("Fragment model node 'FragmentModel' not found. Ensure fragment adjustment step has been completed.")
_adjustTransform = slicer.util.getNode("AdjustTransform")
if _adjustTransform is None:
    raise RuntimeError("Transform node 'AdjustTransform' not found. Ensure adjustment transform has been created.")
_adjustedModel = slicer.util.getNode("AdjustedModel")
if _adjustedModel is None:
    _adjustedModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "AdjustedModel")

Apply_transform_to_polydata(_fragmentModel, _adjustTransform, _adjustedModel)

print("[PelvicFracturePlanning] Step 'cb_step_10' completed.")
