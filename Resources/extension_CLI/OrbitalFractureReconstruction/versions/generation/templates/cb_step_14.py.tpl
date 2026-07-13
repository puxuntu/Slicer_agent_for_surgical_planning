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
    logic = _orbitalfracturereconstruction_logic
except NameError:
    from OrbitalFractureReconstruction import OrbitalFractureReconstructionLogic
    logic = OrbitalFractureReconstructionLogic()
    _orbitalfracturereconstruction_logic = logic

# Ensure side is known from prior step (cutWithRoi sets logic._side)
if logic._side is None:
    raise RuntimeError("Fracture side not determined. Ensure step 13 (cutWithRoi) completed.")

logic.segmentOrbits(logic._side)
print("[OrbitalFractureReconstruction] Step 14: Both orbits segmented (segmentation nodes + 3D shapes).")