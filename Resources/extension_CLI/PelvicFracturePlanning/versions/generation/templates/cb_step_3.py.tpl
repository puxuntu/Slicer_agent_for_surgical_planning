# --- PelvicFracturePlanning: Click "Run Step 2: Segment Fractures" button. ---
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

# Create output fracture segmentation node
outputFrac = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", "FractureSegmentation")
_pelvicfractureplanning_outputfracseg_id = outputFrac.GetID()

# Execute fracture segmentation
logic.segment_fractures(inputVolume, outputFrac, None)

print("[PelvicFracturePlanning] Step 'cb_step_3' completed: fracture segmentation executed.")
