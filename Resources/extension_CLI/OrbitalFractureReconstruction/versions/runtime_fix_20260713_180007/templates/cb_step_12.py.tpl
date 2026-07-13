# [runtime-fixed] Auto-revised by runtime self-correction at 20260713_175909.
# Pre-revision templates backed up under versions/runtime_fix_20260713_175909/.
# Fixed runtime error: OrbitalFractureReconstructionLogic.reconstructFullBone() missing 1 required positional argument: 'segmentationNode'
import slicer
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'OrbitalFractureReconstruction':
    try:
        slicer.util.selectModule('OrbitalFractureReconstruction')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'OrbitalFractureReconstruction': {{_module_enter_error}}")
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

# Look up the bone segmentation node that was selected in step cb_step_11
boneSegNode = slicer.util.getNode("Bone_Segmentation")
if boneSegNode is None:
    raise RuntimeError("Could not find Bone_Segmentation node in the scene")

# Call reconstructFullBone with the required segmentationNode argument
logic.reconstructFullBone(boneSegNode)

# Cache the output full bone node ID for later steps
if logic.fullBoneNode is not None:
    _orbitalfracturereconstruction_fullBoneNode_id = logic.fullBoneNode.GetID()

print("[OrbitalFractureReconstruction] Full bone reconstructed successfully.")
