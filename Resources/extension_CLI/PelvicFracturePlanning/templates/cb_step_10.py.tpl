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

# Retrieve cross-step shared state
try:
    logic = _PelvicFracturePlanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _PelvicFracturePlanning_logic = logic

parameterNode = logic.getParameterNode()

# Get the three required node arguments for Apply_transform_to_polydata
# Fallback: search scene for model node with name containing 'Fragment'
fragmentNodes = slicer.util.getNodesByClass('vtkMRMLModelNode')
fragmentModel = None
for node in fragmentNodes:
    if 'Fragment' in node.GetName():
        fragmentModel = node
        break
if fragmentModel is None:
    raise RuntimeError("FragmentModel could not be found. Please ensure a fragment model is available.")

# Fallback: search for transform node with name containing 'Adjust'
transformNodes = slicer.util.getNodesByClass('vtkMRMLTransformNode')
adjustTransform = None
for node in transformNodes:
    if 'Adjust' in node.GetName():
        adjustTransform = node
        break
if adjustTransform is None:
    raise RuntimeError("AdjustTransform could not be found. Please ensure an adjustment transform exists.")

# Fallback: search for model node with name containing 'Adjusted'
adjustedNodes = slicer.util.getNodesByClass('vtkMRMLModelNode')
adjustedModel = None
for node in adjustedNodes:
    if 'Adjusted' in node.GetName():
        adjustedModel = node
        break
if adjustedModel is None:
    # Create a new model node for the adjusted result
    adjustedModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', 'Adjusted_Fragment')

# Apply the transform to the fragment polydata
Apply_transform_to_polydata(fragmentModel, adjustTransform, adjustedModel)

print("[PelvicFracturePlanning] Adjustments applied. Result stored in '" + adjustedModel.GetName() + "'.")
print("[PelvicFracturePlanning] Step 'cb_step_10' completed.")