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

# Get the logic (cached across steps)
try:
    logic = _pelvicfractureplanning_logic
except NameError:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
    logic = PelvicFracturePlanningLogic()
    _pelvicfractureplanning_logic = logic

# Retrieve nodes from cross-step cached IDs (set by earlier steps)
try:
    inputVolume = slicer.mrmlScene.GetNodeByID(_pelvicfractureplanning_inputVolume_id)
    outputPelvisSeg = slicer.mrmlScene.GetNodeByID(_pelvicfractureplanning_outputPelvisSeg_id)
    outputFracSeg = slicer.mrmlScene.GetNodeByID(_pelvicfractureplanning_outputFracSeg_id)
    outputReduction = slicer.mrmlScene.GetNodeByID(_pelvicfractureplanning_outputReduction_id)
except NameError as e:
    raise RuntimeError(f"Missing cached node ID from an earlier step: {e}")

if inputVolume is None or outputPelvisSeg is None or outputFracSeg is None:
    raise RuntimeError("One or more required nodes could not be resolved from cached IDs.")

# Call the extension function to display the fracture fragment
display_fracture(inputVolume, outputPelvisSeg, outputFracSeg, outputReduction)

print("[PelvicFracturePlanning] Step 'cb_step_8' completed.")
