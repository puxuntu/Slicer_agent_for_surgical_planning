# [runtime-fixed] Auto-revised by runtime self-correction at 20260713_175830.
# Pre-revision templates backed up under versions/runtime_fix_20260713_175830/.
# Fixed runtime error: OrbitalFractureReconstructionLogic.cutWithRoi() missing 2 required positional arguments: 'inputVolume' and 'roiNode'
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

# Resolve the input volume and ROI node from the scene
import slicer
inputVolume = slicer.util.getNode('case1')
roiNode = slicer.util.getNode('Orbital_Region')

# Validate nodes are not None
if inputVolume is None:
    raise RuntimeError("Could not find 'case1' volume node in the scene")
if roiNode is None:
    raise RuntimeError("Could not find 'Orbital_Region' ROI node in the scene")

print(f"[OrbitalFractureReconstruction] Step 5: Cut with ROI using volume='{{inputVolume.GetName()}}' and ROI='{{roiNode.GetName()}}'")

# Call cutWithRoi with the required positional arguments
logic.cutWithRoi(inputVolume, roiNode)
print("[OrbitalFractureReconstruction] Step 5: Cut with ROI completed.")
