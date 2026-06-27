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

# Retrieve required nodes via scene search
_fragmentModel = None
_adjustTransform = None
_adjustedModel = None

# Fallback: scene search if any node is missing
_modelNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
for i in range(_modelNodes.GetNumberOfItems()):
    _node = _modelNodes.GetItemAsObject(i)
    if "fragment" in _node.GetName().lower() and "screw" not in _node.GetName().lower():
        _fragmentModel = _node
        break
if _adjustTransform is None:
    _transNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLTransformNode")
    if _transNodes.GetNumberOfItems() > 0:
        _adjustTransform = _transNodes.GetItemAsObject(0)
if _adjustedModel is None:
    _modelNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLModelNode")
    for i in range(_modelNodes.GetNumberOfItems()):
        _node = _modelNodes.GetItemAsObject(i)
        if "adjusted" in _node.GetName().lower():
            _adjustedModel = _node
            break

if _fragmentModel is None or _adjustTransform is None or _adjustedModel is None:
    raise RuntimeError("Missing required nodes for applying adjustment. Ensure a fragment is selected and transform is set.")

Apply_transform_to_polydata(_fragmentModel, _adjustTransform, _adjustedModel)

print("[PelvicFracturePlanning] Step 'cb_step_11' completed.")
