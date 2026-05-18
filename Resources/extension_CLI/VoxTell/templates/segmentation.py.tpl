# --- VoxTell: Segmentation ---
# Auto-generated CLI template for VoxTell.

{vol_lookup}
if inputVolume is None:
    raise RuntimeError("No volume found in the scene. Load the required data first.")
print(f"[VoxTell] Using volume: {{inputVolume.GetName()}}")

try:
    from VoxTell import VoxTellLogic
except ImportError:
    raise RuntimeError(
        "VoxTell extension is not installed. "
        "Please install it via Slicer's Extension Manager first."
    )

class _ProgressStub:
    def setMaximum(self, v): pass
    def setValue(self, v): pass

logic = VoxTellLogic()

inputVolumeNode = inputVolume  # alias for volume param
textPrompts = {textPrompts: None}
modelPath = {modelPath: logic.defaultModelPath() if hasattr(logic, 'defaultModelPath') else ''}
useGpu = {useGpu: True}
statusCallback = None

# Create output nodes
outputSegmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")

print("[VoxTell] Running segmentation...")
logic.runSegmentation(inputVolume, textPrompts, modelPath, useGpu, outputSegmentationNode, statusCallback)

# Cache for potential re-use
_voxtellLogic = logic

# Cache node IDs for subsequent stages
_voxtell_outputSegmentationNode_id = outputSegmentationNode.GetID()

outputSegmentationNode.CreateClosedSurfaceRepresentation()
_display = outputSegmentationNode.GetDisplayNode()
if _display:
    _display.SetVisibility(True)

print("[VoxTell] Segmentation complete.")