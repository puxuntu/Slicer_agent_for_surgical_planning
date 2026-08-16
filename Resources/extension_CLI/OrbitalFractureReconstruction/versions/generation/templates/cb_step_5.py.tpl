import slicer
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'OrbitalFractureReconstruction':
    try:
        slicer.util.selectModule('OrbitalFractureReconstruction')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'OrbitalFractureReconstruction': {_module_enter_error}")
# precondition:end

try:
    from OrbitalFractureReconstruction import OrbitalFractureReconstructionLogic
except ImportError:
    raise RuntimeError("OrbitalFractureReconstruction extension is not installed. Install it from the Extension Manager.")

try:
    logic = _orbitalfracturereconstruction_logic
except NameError:
    logic = OrbitalFractureReconstructionLogic()
    _orbitalfracturereconstruction_logic = logic

{vol_lookup}
try:
    roiNode = slicer.mrmlScene.GetNodeByID(_orbitalfracturereconstruction_cb_step_3_id)
except NameError:
    raise RuntimeError("ROI node was not created by the previous placement step.")
resample = {resample: False}

if inputVolume is None:
    raise RuntimeError("Required input CT volume not found for cutWithRoi.")
if roiNode is None:
    raise RuntimeError("Required ROI node not found for cutWithRoi.")

logic.cutWithRoi(inputVolume, roiNode, resample)

print("[OrbitalFractureReconstruction] Cut with ROI completed.")