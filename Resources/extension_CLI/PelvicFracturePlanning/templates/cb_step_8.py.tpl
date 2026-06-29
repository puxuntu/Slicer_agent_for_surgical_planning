# --- PelvicFracturePlanning: Choose which fragment needs adjustment in the "Fragment" selection box. ---
import slicer
from PelvicFracturePlanning import display_fracture

# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'PelvicFracturePlanning':
    try:
        slicer.util.selectModule('PelvicFracturePlanning')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'PelvicFracturePlanning': {_module_enter_error}")
# precondition:end

# Retrieve cross-step cached node IDs
try:
    _input_vol_id = _pelvicfractureplanning_inputvolume_id
    inputVolume = slicer.mrmlScene.GetNodeByID(_input_vol_id)
except NameError:
    inputVolume = None  # will be handled by function call

try:
    _pelvis_seg_id = _pelvicfractureplanning_outputpelvisseg_id
    outputPelvisSeg = slicer.mrmlScene.GetNodeByID(_pelvis_seg_id)
except NameError:
    outputPelvisSeg = None

try:
    _frac_seg_id = _pelvicfractureplanning_outputfracseg_id
    outputFracSeg = slicer.mrmlScene.GetNodeByID(_frac_seg_id)
except NameError:
    outputFracSeg = None

try:
    _reduction_id = _pelvicfractureplanning_outputreduction_id
    outputReduction = slicer.mrmlScene.GetNodeByID(_reduction_id)
except NameError:
    outputReduction = None

# Validate inputs
if None in (inputVolume, outputPelvisSeg, outputFracSeg, outputReduction):
    raise RuntimeError("Missing required nodes for display_fracture. Ensure prior steps completed.")

# Call extension function with required arguments
display_fracture(inputVolume, outputPelvisSeg, outputFracSeg, outputReduction)

print("[PelvicFracturePlanning] Step 'cb_step_8' completed: fracture fragment selected.")