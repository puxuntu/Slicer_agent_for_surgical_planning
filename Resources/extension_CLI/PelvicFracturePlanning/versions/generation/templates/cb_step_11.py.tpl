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

# Retrieve logic instance
try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

# Retrieve cross-step cached node IDs (set by previous steps)
_fragmentModelId = None
try:
    _fragmentModelId = _pelvicfractureplanning_fragmentModelId
except NameError:
    pass
_adjustTransformId = None
try:
    _adjustTransformId = _pelvicfractureplanning_adjustTransformId
except NameError:
    pass
_adjustedModelId = None
try:
    _adjustedModelId = _pelvicfractureplanning_adjustedModelId
except NameError:
    pass

# Resolve nodes from IDs or fallback to name search
_fragmentModelNode = slicer.mrmlScene.GetNodeByID(_fragmentModelId) if _fragmentModelId else None
_adjustTransformNode = slicer.mrmlScene.GetNodeByID(_adjustTransformId) if _adjustTransformId else None
_adjustedModelNode = slicer.mrmlScene.GetNodeByID(_adjustedModelId) if _adjustedModelId else None

if _fragmentModelNode is None:
    _fragmentModelNode = slicer.mrmlScene.GetFirstNodeByName('FragmentModel')
if _adjustTransformNode is None:
    _adjustTransformNode = slicer.mrmlScene.GetFirstNodeByName('AdjustTransform')
if _adjustedModelNode is None:
    _adjustedModelNode = slicer.mrmlScene.GetFirstNodeByName('AdjustedModel')

if _fragmentModelNode is None or _adjustTransformNode is None or _adjustedModelNode is None:
    raise RuntimeError("Required nodes (FragmentModel, AdjustTransform, AdjustedModel) not found. Ensure previous steps have cached their IDs.")

Apply_transform_to_polydata(_fragmentModelNode, _adjustTransformNode, _adjustedModelNode)
print("[PelvicFracturePlanning] Step 'cb_step_11' completed.")