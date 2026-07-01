import slicer
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'SlicerE3Implant':
    try:
        slicer.util.selectModule('SlicerE3Implant')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'SlicerE3Implant': {_module_enter_error}")
# precondition:end

try:
    logic = _cranialimplantplanning_logic
except NameError:
    from SlicerE3Implant import SlicerE3ImplantLogic
    logic = SlicerE3ImplantLogic()
    _cranialimplantplanning_logic = logic

# Retrieve defect_binary from step 15
try:
    defect_binary = _cranialimplantplanning_near_erased_mask
except NameError:
    raise RuntimeError("Missing defect_binary from step 15. Ensure step 15 completed successfully.")

implant = logic.reconstruct(defect_binary)

# Store the result for subsequent steps
try:
    _cranial_implant
    _cranial_implant = implant
except NameError:
    _cranial_implant = implant

print("[CranialImplantPlanning] Implant reconstruction completed.")