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

# Read the fractured side from the module widget's sideComboBox
moduleWidget = slicer.util.getModuleWidget('OrbitalFractureReconstruction')
if moduleWidget is None:
    raise RuntimeError("OrbitalFractureReconstruction module widget not found. Ensure the module was entered.")

# sideComboBox index 0 = "Red box" (patient-right) -> side "right"
# sideComboBox index 1 = "Blue box" (patient-left) -> side "left"
logic._side = "right" if moduleWidget.sideComboBox.currentIndex == 0 else "left"
print(f"[OrbitalFractureReconstruction] Fractured side determined from widget: {logic._side}")

# The segmentOrbits method reads logic._side internally
logic.segmentOrbits()
print("[OrbitalFractureReconstruction] Step 14: Both orbits segmented.")
