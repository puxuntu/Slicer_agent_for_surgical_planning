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

# Retrieve the three required node arguments for Apply_transform_to_polydata
try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

# Fragment model node (the fragment to adjust)
# Search by name pattern as a fallback
fragmentModel = slicer.mrmlScene.GetFirstNodeByName("FragmentModel")
if fragmentModel is None:
    # Fallback: find a model node that is a fragment (not the pelvis or screw)
    allModels = slicer.util.getNodesByClass("vtkMRMLModelNode")
    for model in allModels:
        name = model.GetName().lower()
        if "fragment" in name or "fracture" in name:
            fragmentModel = model
            break
    if fragmentModel is None:
        raise RuntimeError("Could not find the fragment model node. Please ensure a fracture fragment model exists in the scene.")

# Transform node (the adjustment transform)
transformNode = slicer.mrmlScene.GetFirstNodeByName("AdjustTransform")
if transformNode is None:
    # Fallback: find a linear transform node
    allTransforms = slicer.util.getNodesByClass("vtkMRMLTransformNode")
    if len(allTransforms) > 0:
        transformNode = allTransforms[0]
    else:
        raise RuntimeError("Could not find the adjustment transform node. Please apply a transform to the fragment before this step.")

# Output model node for the adjusted fragment (create if not exists)
adjustedModel = slicer.mrmlScene.GetFirstNodeByName("AdjustedFragment")
if adjustedModel is None:
    adjustedModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "AdjustedFragment")

# Apply the transform to the fragment polydata
Apply_transform_to_polydata(fragmentModel, transformNode, adjustedModel)

print("[PelvicFracturePlanning] Step 'cb_step_10' completed. Adjustment applied.")
