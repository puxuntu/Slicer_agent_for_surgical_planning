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

# Get or create the shared logic instance (allow cross-step reuse)
try:
    logic = _PelvicFracturePlanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _PelvicFracturePlanning_logic = logic

# Retrieve arguments from the parameter node (set by prior steps)
parameterNode = logic.getParameterNode()
fragmentModel = parameterNode.GetNodeReference('FragmentModel')
adjustTransform = parameterNode.GetNodeReference('AdjustTransform')
adjustedModel = parameterNode.GetNodeReference('AdjustedModel')

# Fallback: if any reference is None, search the scene for plausible nodes
if fragmentModel is None:
    fragmentModels = slicer.util.getNodesByClass('vtkMRMLModelNode')
    for node in fragmentModels:
        if 'Fragment' in node.GetName():
            fragmentModel = node
            break
    if fragmentModel is None:
        raise RuntimeError('Could not find fragment model node for adjustment.')

if adjustTransform is None:
    transforms = slicer.util.getNodesByClass('vtkMRMLTransformNode')
    if transforms:
        adjustTransform = transforms[0]
    else:
        raise RuntimeError('Could not find transform node for adjustment.')

if adjustedModel is None:
    # AdjustedModel may be created by the function; we can pass a new model node or None
    adjustedModel = None  # Let the function create it

# Call the extension function
Apply_transform_to_polydata(fragmentModel, adjustTransform, adjustedModel)

print("[PelvicFracturePlanning] Step 'cb_step_10' completed.")
