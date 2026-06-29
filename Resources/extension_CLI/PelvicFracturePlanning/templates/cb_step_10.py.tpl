# --- PelvicFracturePlanning: Click the "Apply adjustments" button. ---
import slicer
from PelvicFracturePlanning import Apply_transform_to_polydata
from slicer.util import getNodesByClass

# precondition:begin
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'PelvicFracturePlanning':
    try:
        slicer.util.selectModule('PelvicFracturePlanning')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'PelvicFracturePlanning': {_module_enter_error}")
# precondition:end

# Retrieve the fragment model node by searching scene nodes
fragmentModel = None
for node in getNodesByClass('vtkMRMLModelNode'):
    if 'Fragment' in node.GetName():
        fragmentModel = node
        break
if fragmentModel is None:
    raise RuntimeError('Fragment model not found. Ensure prior steps created it.')

# Retrieve the adjust transform node
adjustTransform = None
for node in getNodesByClass('vtkMRMLTransformNode'):
    if 'Adjust' in node.GetName():
        adjustTransform = node
        break
if adjustTransform is None:
    # fallback: use the first transform node
    tNodes = getNodesByClass('vtkMRMLTransformNode')
    if tNodes:
        adjustTransform = tNodes[0]
if adjustTransform is None:
    raise RuntimeError('Adjust transform not found.')

# Create or retrieve the adjusted model node
adjustedModel = None
for node in getNodesByClass('vtkMRMLModelNode'):
    if 'AdjustedModel' in node.GetName():
        adjustedModel = node
        break
if adjustedModel is None:
    adjustedModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode', 'AdjustedModel')

# Apply the transform to the polydata
Apply_transform_to_polydata(fragmentModel, adjustTransform, adjustedModel)

print("[PelvicFracturePlanning] Step 'cb_step_10' completed.")
