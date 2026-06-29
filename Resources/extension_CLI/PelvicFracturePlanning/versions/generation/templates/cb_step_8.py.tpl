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

# Ensure shared logic instance
try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

# Retrieve the fracture segmentation node (output of step 3) from cached ID or scene
fragmentSegNode = None
try:
    fragmentSegNode = slicer.mrmlScene.GetNodeByID(_pelvicfractureplanning_outputfracseg_id)
except Exception:
    pass
if fragmentSegNode is None:
    # Fallback: use first vtkMRMLSegmentationNode with "Fracture" in name
    for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode"):
        if "Fracture" in node.GetName():
            fragmentSegNode = node
            break
if fragmentSegNode is None:
    raise RuntimeError("Could not find fracture segmentation node for cal_BBox.")

# Compute bounding box for the fragment segmentation
cal_BBox(fragmentSegNode)

print("[PelvicFracturePlanning] Step 'cb_step_8' completed: fragment bounding box computed.")
