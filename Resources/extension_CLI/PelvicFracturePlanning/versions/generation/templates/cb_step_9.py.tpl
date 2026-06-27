# --- PelvicFracturePlanning: Choose which fragment needs adjustment in the "Fragment" selection box. ---
import slicer
from PelvicFracturePlanning import cal_BBox

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

# Retrieve fragment segmentation node from cross-step cache or scene search
_fragmentNode = None
try:
    _fragmentNodeId = _pelvicfractureplanning_fragmentSegmentationId
    _fragmentNode = slicer.mrmlScene.GetNodeByID(_fragmentNodeId)
except NameError:
    pass
if _fragmentNode is None:
    # Fallback: search for a segmentation node with expected name
    _fragmentNode = slicer.mrmlScene.GetFirstNodeByName('FragmentSegmentation')
if _fragmentNode is None:
    raise RuntimeError("FragmentSegmentation node not found. Ensure previous steps have defined it and cached its ID as _pelvicfractureplanning_fragmentSegmentationId")

cal_BBox(_fragmentNode)
print("[PelvicFracturePlanning] Step 'cb_step_9' completed.")