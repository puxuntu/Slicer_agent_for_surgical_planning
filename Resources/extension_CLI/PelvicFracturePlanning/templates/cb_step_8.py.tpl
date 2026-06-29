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

# Retrieve the fragment segmentation node from cross-step cached ID
_fragment_seg_node = None
try:
    _fragment_seg_node = slicer.mrmlScene.GetNodeByID(_pelvicfractureplanning_outputfracseg_id)
except NameError:
    pass
if _fragment_seg_node is None:
    raise RuntimeError("Fragment segmentation node not found. Ensure previous segmentation steps have completed.")

cal_BBox(_fragment_seg_node)

print("[PelvicFracturePlanning] Step 'cb_step_8' completed.")