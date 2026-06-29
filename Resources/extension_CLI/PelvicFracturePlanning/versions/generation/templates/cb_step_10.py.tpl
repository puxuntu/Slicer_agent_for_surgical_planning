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

# Retrieve shared logic instance
try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning.PelvicFracturePlanningLogic import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

# Retrieve nodes from cross-step cached node IDs
fragmentModel = None
adjustTransform = None
adjustedModel = None

try:
    fragmentModelID = _pelvicfractureplanning_fragmentModel_id
    if fragmentModelID:
        fragmentModel = slicer.mrmlScene.GetNodeByID(fragmentModelID)
except NameError:
    pass

try:
    adjustTransformID = _pelvicfractureplanning_adjustTransform_id
    if adjustTransformID:
        adjustTransform = slicer.mrmlScene.GetNodeByID(adjustTransformID)
except NameError:
    pass

try:
    adjustedModelID = _pelvicfractureplanning_adjustedModel_id
    if adjustedModelID:
        adjustedModel = slicer.mrmlScene.GetNodeByID(adjustedModelID)
except NameError:
    pass

# Fallback: search by class if not yet wired
if fragmentModel is None:
    fragmentModel = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLModelNode')
    if fragmentModel is not None:
        print("[PelvicFracturePlanning] Warning: FragmentModel not found via cached ID; using first model node.")
if adjustTransform is None:
    adjustTransform = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLTransformNode')
    if adjustTransform is not None:
        print("[PelvicFracturePlanning] Warning: AdjustTransform not found via cached ID; using first transform node.")
if adjustedModel is None:
    adjustedModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', 'AdjustedFragment')
    print("[PelvicFracturePlanning] Warning: AdjustedModel not found via cached ID; created new node.")

# Apply the transform
if fragmentModel is not None and adjustTransform is not None and adjustedModel is not None:
    Apply_transform_to_polydata(fragmentModel, adjustTransform, adjustedModel)
    # Cache output node ID for downstream steps
    _pelvicfractureplanning_adjustedModel_id = adjustedModel.GetID()
    print("[PelvicFracturePlanning] Apply adjustments executed.")
else:
    print("[PelvicFracturePlanning] Error: Could not find all required nodes (FragmentModel, AdjustTransform, AdjustedModel).")
    print("[PelvicFracturePlanning] Please ensure a fragment is selected and an adjustment transform exists.")

print("[PelvicFracturePlanning] Step 'cb_step_10' completed.")