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
    import_orbital_frac_recon = True
    from OrbitalFractureReconstruction import OrbitalFractureReconstructionLogic
except ImportError:
    raise ImportError("OrbitalFractureReconstruction extension is not installed. Please install it.")

# Reuse existing logic instance or create new one
try:
    logic = _orbitalfracturereconstruction_logic
except NameError:
    logic = OrbitalFractureReconstructionLogic()
    _orbitalfracturereconstruction_logic = logic

# The reconstructFullBone method reads the segmentation node from internal state
logic.reconstructFullBone()

# Cache the output full bone node ID for later steps
if logic.fullBoneNode is not None:
    _orbitalfracturereconstruction_fullBoneNode_id = logic.fullBoneNode.GetID()

print("[OrbitalFractureReconstruction] Full bone reconstructed.")
