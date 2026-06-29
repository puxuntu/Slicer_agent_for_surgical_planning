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

try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

# Retrieve fragment segmentation node from scene (assumes previous step created it)
_fragmentNodes = slicer.util.getNodesByClass("vtkMRMLSegmentationNode")
_fragmentNode = None
for _node in _fragmentNodes:
    if _node.GetSegmentation().GetNumberOfSegments() > 0:
        _segmentName = _node.GetSegmentation().GetNthSegment(0).GetName().lower()
        if 'fracture' in _segmentName or 'fragment' in _segmentName:
            _fragmentNode = _node
            break
if _fragmentNode is None:
    for _node in _fragmentNodes:
        if 'pelvis' not in _node.GetName().lower():
            _fragmentNode = _node
            break
if _fragmentNode is None:
    raise RuntimeError("No fragment segmentation node found. Ensure fracture segmentation has been completed.")

cal_BBox(_fragmentNode)

print("[PelvicFracturePlanning] Step 'cb_step_8' completed.")