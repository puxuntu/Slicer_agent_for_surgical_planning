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

# Retrieve required nodes from pipeline state
try:
    roiNode = slicer.mrmlScene.GetNodeByID(_cranialimplantplanning_roiNode_id)
except NameError:
    raise RuntimeError("ROI node ID not found in pipeline state (_cranialimplantplanning_roiNode_id)")

try:
    referenceVolume = slicer.mrmlScene.GetNodeByID(_cranialimplantplanning_referenceVolume_id)
except NameError:
    raise RuntimeError("Reference volume ID not found in pipeline state (_cranialimplantplanning_referenceVolume_id)")

# Execute method
roiInsideMask = logic.roiInsideMask(roiNode, referenceVolume)

# Store result for subsequent steps
_cranialimplantplanning_roi_inside_mask = roiInsideMask

print("[CranialImplantPlanning] ROI inside mask computed successfully.")
