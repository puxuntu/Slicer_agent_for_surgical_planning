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
    raise RuntimeError("OrbitalFractureReconstruction extension is not installed. Install it from the Extension Manager and restart Slicer.")

try:
    logic = _orbitalfracturereconstruction_logic
except NameError:
    logic = OrbitalFractureReconstructionLogic()
    _orbitalfracturereconstruction_logic = logic

# The ROI cut step must have already populated the half-volume arrays and the
# cut volume node on the shared logic instance.
logic.segmentOrbits({side})

_orbitalfracturereconstruction_logic = logic

print("[OrbitalFractureReconstruction] Healthy and fractured orbit segmentations created.")
