# --- SlicerOrbitSurgerySim: Click "Posterior stop and antero-posterior stops alignment" button. ---
import slicer
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'PlateRegistration':
    try:
        slicer.util.selectModule('PlateRegistration')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'PlateRegistration': {_module_enter_error}")
# precondition:end

# Obtain the PlateRegistration module widget and its parameterNode
_widget = None
try:
    _widget = slicer.util.getModuleWidget('PlateRegistration')
except Exception:
    _widget = None
if _widget is None:
    try:
        _widget = slicer.modules.plateregistration.widgetRepresentation().self()
    except Exception:
        _widget = None
if _widget is None:
    raise RuntimeError("Could not obtain the PlateRegistration module widget for 'posteriorStopRegistrationPushButton'.")

_paramNode = _widget._parameterNode
if _paramNode is None:
    raise RuntimeError("PlateRegistration widget has no _parameterNode.")

# Ensure the required node references are set (should have been created in steps 1-4)
# Use cached node IDs if available from prior steps, else fall back to scene node names
if _paramNode.originalPlateLm is None or _paramNode.orbitLm is None or _paramNode.originalPlateModel is None or _paramNode.fractureOrbitModel is None:
    # Attempt to retrieve nodes by known names (as used in the test scene)
    try:
        node_orbit_model = slicer.util.getNode('skull_sample_left_fracture')
        node_plate_model = slicer.util.getNode('synth_plate_large_left')
        node_orbit_lm = slicer.util.getNode('left_orbit_lm')
        node_plate_lm = slicer.util.getNode('synth_plate_large_left_lm')
        _paramNode.originalPlateLm = node_plate_lm
        _paramNode.orbitLm = node_orbit_lm
        _paramNode.originalPlateModel = node_plate_model
        _paramNode.fractureOrbitModel = node_orbit_model
    except Exception as _node_lookup_error:
        print(f"Warning: could not set parameterNode references by name: {_node_lookup_error}")

# Check if registeredPlateLm was created by step 5 (initial registration)
if _paramNode.registeredPlateLm is None:
    print("[Step 6] registeredPlateLm is None. Running initial registration to create it...")
    _widget.onInitialRegistrationPushButton()
    print("[Step 6] Initial registration done.")

# Validate that the posterior stop handler exists
if not hasattr(_widget, 'onRotation_p_stop_pushButton'):
    raise RuntimeError("PlateRegistration widget has no handler 'onRotation_p_stop_pushButton' for 'posteriorStopRegistrationPushButton'; regenerate the CLI.")

# Click the posterior stop alignment button
_widget.onRotation_p_stop_pushButton()
print("[SlicerOrbitSurgerySim] Step 'cb_step_6': clicked 'posteriorStopRegistrationPushButton' via onRotation_p_stop_pushButton().")