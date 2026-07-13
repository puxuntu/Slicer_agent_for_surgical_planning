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
    import_orbital_frac_recon = True
    from OrbitalFractureReconstruction import OrbitalFractureReconstructionLogic
except ImportError:
    raise ImportError("OrbitalFractureReconstruction extension is not installed. Please install it.")

# Reuse existing logic instance or create new one
try:
    logic = _orbitalfracturereconstruction_logic
except NameError:
    logic = OrbitalFractureReconstructionLogic()
    _orbitalfracturereconstruction_logic = logic

# Get the segmentation node
try:
    segmentationNode = slicer.mrmlScene.GetNodeByID(_orbitalfracturereconstruction_segmentationNode_id)
except NameError:
    # Fall back to scene search
    segmentationNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
    if segmentationNode is None:
        raise RuntimeError("No segmentation node found in the scene.")

# Call the method
logic.reconstructFullBone(segmentationNode)

# Cache the output full bone node ID for later steps
if logic.fullBoneNode is not None:
    _orbitalfracturereconstruction_fullBoneNode_id = logic.fullBoneNode.GetID()

print("[OrbitalFractureReconstruction] Full bone reconstructed.")
