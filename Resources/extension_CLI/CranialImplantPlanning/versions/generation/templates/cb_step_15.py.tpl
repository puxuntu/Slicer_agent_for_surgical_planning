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
    from SlicerE3Implant import SlicerE3ImplantLogic as SlicerE3ImplantLogic
    logic = SlicerE3ImplantLogic()
    _cranialimplantplanning_logic = logic

# Retrieve skull array from labelmap node produced by step 8
try:
    _cranial_labelmap_node = slicer.mrmlScene.GetNodeByID(_cranialimplantplanning_labelmapNode_id)
    if _cranial_labelmap_node is None:
        raise RuntimeError("Labelmap node not found from step 8.")
except NameError:
    raise RuntimeError("Missing labelmap node ID from step 8. Ensure step 8 completed successfully.")
skullArr = slicer.util.arrayFromVolume(_cranial_labelmap_node)

# Retrieve curve node from prior step (expected to be cached by interaction step)
try:
    curveNode = slicer.mrmlScene.GetNodeByID(_cranialimplantplanning_curveNode_id)
except NameError:
    raise RuntimeError("Missing curve node ID from prior step. Ensure prior interaction step completed.")

# Retrieve reference volume via vol_lookup
{vol_lookup}
referenceVolume = inputVolume

_cranialimplantplanning_near_erased_mask = logic.eraseNearSideDefect(skullArr, curveNode, referenceVolume)

try:
    _cranialimplantplanning_near_erased_mask
except NameError:
    pass
_cranialimplantplanning_near_erased_mask = _cranialimplantplanning_near_erased_mask

print("Step 15: Near-side defect erased from skull mask.")