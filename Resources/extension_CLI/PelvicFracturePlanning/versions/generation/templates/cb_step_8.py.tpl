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

# Get or create the shared logic instance
try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

# Retrieve required node IDs from cross-step cache
try:
    _inputVolume_id = _pelvicfractureplanning_inputVolume_id
except NameError:
    raise RuntimeError("Missing cached inputVolume node ID from previous step.")
try:
    _outputPelvisSeg_id = _pelvicfractureplanning_outputPelvisSeg_id
except NameError:
    raise RuntimeError("Missing cached outputPelvisSeg node ID from previous step.")
try:
    _outputFracSeg_id = _pelvicfractureplanning_outputFracSeg_id
except NameError:
    raise RuntimeError("Missing cached outputFracSeg node ID from previous step.")
try:
    _outputReduction_id = _pelvicfractureplanning_outputReduction_id
except NameError:
    raise RuntimeError("Missing cached outputReduction node ID from previous step.")

inputVolume = slicer.mrmlScene.GetNodeByID(_inputVolume_id)
outputPelvisSeg = slicer.mrmlScene.GetNodeByID(_outputPelvisSeg_id)
outputFracSeg = slicer.mrmlScene.GetNodeByID(_outputFracSeg_id)
outputReduction = slicer.mrmlScene.GetNodeByID(_outputReduction_id)

if any(node is None for node in [inputVolume, outputPelvisSeg, outputFracSeg, outputReduction]):
    raise RuntimeError("One or more required nodes could not be resolved from cached IDs.")

display_fracture(inputVolume, outputPelvisSeg, outputFracSeg, outputReduction)

print("[PelvicFracturePlanning] Step 'cb_step_8' completed.")