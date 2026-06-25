# --- SlicerOrbitSurgerySim: Click "Initial registration" button. ---
import slicer
from PlateRegistration import registerSampleData

# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'PlateRegistration':
    try:
        slicer.util.selectModule('PlateRegistration')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'PlateRegistration': {_module_enter_error}")
# precondition:end

registerSampleData()

print("[SlicerOrbitSurgerySim] Step 'cb_step_5' completed.")
