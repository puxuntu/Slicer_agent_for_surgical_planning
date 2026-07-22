# [runtime-fixed] Auto-revised by runtime self-correction at 20260720_111246.
# Pre-revision templates backed up under versions/runtime_fix_20260720_111246/.
# Fixed runtime error: could not find nodes in the scene by name or id 'case1'
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
    logic = _orbitalfracturereconstruction_logic
except NameError:
    from OrbitalFractureReconstruction import OrbitalFractureReconstructionLogic
    logic = OrbitalFractureReconstructionLogic()
    _orbitalfracturereconstruction_logic = logic

# Resolve the input volume and ROI node from the scene using their actual scene names
import slicer
inputVolume = slicer.util.getNode('OrbitalFracture082')
roiNode = slicer.util.getNode('Orbital_Region')

# Validate nodes are not None
if inputVolume is None:
    raise RuntimeError("Could not find 'OrbitalFracture082' volume node in the scene")
if roiNode is None:
    raise RuntimeError("Could not find 'Orbital_Region' ROI node in the scene")

print(f"[OrbitalFractureReconstruction] Step 5: Cut with ROI using volume='{{inputVolume.GetName()}}' and ROI='{{roiNode.GetName()}}'")

# Call cutWithRoi with the required positional arguments
logic.cutWithRoi(inputVolume, roiNode)
print("[OrbitalFractureReconstruction] Step 5: Cut with ROI completed.")
