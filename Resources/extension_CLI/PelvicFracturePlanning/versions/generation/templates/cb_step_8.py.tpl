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

logic = slicer.util.getModuleLogic('PelvicFracturePlanning')
paramNode = logic.getParameterNode()
inputVolume = paramNode.inputVolume
outputPelvisSeg = paramNode.OutputPelvisSeg
outputFracSeg = paramNode.OutputFracSeg
outputReduction = paramNode.OutputReduction

display_fracture(inputVolume, outputPelvisSeg, outputFracSeg, outputReduction)

print("[PelvicFracturePlanning] Step 'cb_step_8' completed.")