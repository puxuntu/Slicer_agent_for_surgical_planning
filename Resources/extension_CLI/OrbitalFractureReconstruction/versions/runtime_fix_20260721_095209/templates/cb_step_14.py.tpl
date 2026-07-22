# [runtime-fixed] Auto-revised by runtime self-correction at 20260713_180007.
# Pre-revision templates backed up under versions/runtime_fix_20260713_180007/.
# Fixed runtime error: OrbitalFractureReconstructionLogic.segmentOrbits() missing 1 required positional argument: 'side'
import slicer

try:
    logic = _orbitalfracturereconstruction_logic
except NameError:
    from OrbitalFractureReconstruction import OrbitalFractureReconstructionLogic
    logic = OrbitalFractureReconstructionLogic()
    _orbitalfracturereconstruction_logic = logic

# Read the fractured side from the module widget's sideComboBox
# Index 0 = "Red box" (patient-right) -> side "right"
# Index 1 = "Blue box" (patient-left) -> side "left"
moduleWidget = slicer.util.getModuleWidget('OrbitalFractureReconstruction')
if moduleWidget is None:
    raise RuntimeError("OrbitalFractureReconstruction module widget not found. Ensure the module was entered.")

fractured_side = "right" if moduleWidget.sideComboBox.currentIndex == 0 else "left"
print(f"[OrbitalFractureReconstruction] Fractured side determined from widget: {{fractured_side}}")

# Call segmentOrbits with the required side argument
logic.segmentOrbits(fractured_side)
print("[OrbitalFractureReconstruction] Step 14: Both orbits segmented.")
