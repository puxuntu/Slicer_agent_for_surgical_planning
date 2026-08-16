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
    raise RuntimeError("OrbitalFractureReconstruction extension is not installed. Please install it from the Extension Manager.")

# Reuse the shared logic instance if it already exists from an earlier workflow step.
try:
    logic = _orbitalfracturereconstruction_logic
except NameError:
    logic = OrbitalFractureReconstructionLogic()
    _orbitalfracturereconstruction_logic = logic

# This step consumes state produced by earlier workflow steps and retained on the
# shared logic instance: normal/fracture labelmaps, IJK-to-RAS transforms, fracture
# image data, side, cut volume node, model paths, and device. No parameter-node setup
# is required for reconstructFractured() itself.
logic.reconstructFractured()

print("Fractured wall reconstructed (segmentation node + 3D shape).")
