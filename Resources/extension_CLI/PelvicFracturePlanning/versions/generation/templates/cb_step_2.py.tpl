# --- PelvicFracturePlanning: Click "Run Step 1: Segment Pelvis" button. ---
import slicer
# precondition:begin
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'PelvicFracturePlanning':
    try:
        slicer.util.selectModule('PelvicFracturePlanning')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'PelvicFracturePlanning': {_module_enter_error}")
# precondition:end

# Resolve input volume
{vol_lookup}

# Ensure shared logic instance
try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

# Create output pelvis segmentation node
outputPelvis = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", "PelvisSegmentation")
_pelvicfractureplanning_outputpelvis_id = outputPelvis.GetID()

# Execute pelvis segmentation
logic.segment_pelvis(inputVolume, outputPelvis, None)

print("[PelvicFracturePlanning] Step 'cb_step_2' completed: pelvis segmentation executed.")
