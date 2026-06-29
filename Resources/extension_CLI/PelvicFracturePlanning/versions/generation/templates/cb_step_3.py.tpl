# --- PelvicFracturePlanning: Click "Run Step 2: Segment Fractures" button. ---
import slicer

# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'PelvicFracturePlanning':
    try:
        slicer.util.selectModule('PelvicFracturePlanning')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'PelvicFracturePlanning': {_module_enter_error}")
# precondition:end

# Reuse cached logic instance
try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

# Retrieve input volume from cross-step cache
{vol_lookup}

# Retrieve pelvis segmentation from cross-step cache
try:
    _pelvis_seg_id = _pelvicfractureplanning_outputpelvisseg_id
    pelvisSeg = slicer.mrmlScene.GetNodeByID(_pelvis_seg_id)
    if pelvisSeg is None:
        raise ValueError("Pelvis segmentation node not found in scene")
except NameError:
    # Fallback: search for a segmentation node named 'Pelvis_seg'
    pelvisSeg = slicer.util.getFirstNodeByClassByName('vtkMRMLSegmentationNode', 'Pelvis_seg')
    if pelvisSeg is None:
        raise RuntimeError("Pelvis segmentation node not available. Ensure step 2 completed.")

# Create output fracture segmentation node if not already present
try:
    _output_frac_id = _pelvicfractureplanning_outputfracseg_id
    outputFrac = slicer.mrmlScene.GetNodeByID(_output_frac_id)
    if outputFrac is None:
        raise ValueError("Output fracture segmentation node ID stale")
except (NameError, ValueError):
    outputFrac = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLSegmentationNode', 'Fractures_seg')
    _pelvicfractureplanning_outputfracseg_id = outputFrac.GetID()

# Run fracture segmentation
logic.segment_fractures(inputVolume, outputFrac, None)

print("[PelvicFracturePlanning] Step 'cb_step_3' completed: fracture segmentation run.")