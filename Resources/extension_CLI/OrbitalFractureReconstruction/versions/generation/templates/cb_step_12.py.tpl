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
    from OrbitalFractureReconstruction import OrbitalFractureReconstructionLogic
except ImportError:
    raise RuntimeError("OrbitalFractureReconstruction extension is not available; please install it before running this step.")

try:
    logic = _orbitalfracturereconstruction_logic
except NameError:
    logic = OrbitalFractureReconstructionLogic()

parameterNode = logic.getParameterNode()
segmentationNode = None
if parameterNode is not None:
    segmentationNode = parameterNode.GetNodeReference("segmentationNode")

if segmentationNode is None:
    segmentationNodes = slicer.util.getNodesByClass("vtkMRMLSegmentationNode")
    if len(segmentationNodes) > 0:
        segmentationNode = segmentationNodes[0]
        if parameterNode is not None:
            parameterNode.SetNodeReferenceID("segmentationNode", segmentationNode.GetID())

if segmentationNode is None:
    raise RuntimeError("No bone segmentation node found for full bone reconstruction.")

logic.reconstructFullBone(segmentationNode)
_orbitalfracturereconstruction_logic = logic
print("Full bone reconstructed.")
