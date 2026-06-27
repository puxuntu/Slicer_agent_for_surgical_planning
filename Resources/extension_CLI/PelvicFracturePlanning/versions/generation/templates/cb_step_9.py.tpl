# --- PelvicFracturePlanning: Choose which fragment needs adjustment in the "Fragment" selection box. ---
import slicer
from PelvicFracturePlanning import cal_BBox

# precondition:begin
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'PelvicFracturePlanning':
    try:
        slicer.util.selectModule('PelvicFracturePlanning')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'PelvicFracturePlanning': {_module_enter_error}")
# precondition:end

# Find the fragment segmentation node
_fragmentNode = None
_segNodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
for i in range(_segNodes.GetNumberOfItems()):
    _node = _segNodes.GetItemAsObject(i)
    if "fragment" in _node.GetName().lower():
        _fragmentNode = _node
        break
if _fragmentNode is None:
    raise RuntimeError("No fragment segmentation node found. Please select a fragment first.")

cal_BBox(_fragmentNode)

print("[PelvicFracturePlanning] Step 'cb_step_9' completed.")
