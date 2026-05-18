# --- PelvicFracturePlanning: Segmentation ---
# Auto-generated CLI template for PelvicFracturePlanning.

{vol_lookup}
if inputVolume is None:
    raise RuntimeError("No volume found in the scene. Load the required data first.")
print(f"[PelvicFracturePlanning] Using volume: {{inputVolume.GetName()}}")

try:
    from PelvicFracturePlanning import PelvicFracturePlanningLogic
except ImportError:
    raise RuntimeError(
        "PelvicFracturePlanning extension is not installed. "
        "Please install it via Slicer's Extension Manager first."
    )

class _ProgressStub:
    def setMaximum(self, v): pass
    def setValue(self, v): pass

logic = PelvicFracturePlanningLogic()

showResult = {showResult: True}

# Create output nodes
outputPelvis = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationNode")
outputFrac = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationNode")

print("[PelvicFracturePlanning] Running segmentation...")
logic.process_seg(inputVolume, outputPelvis, outputFrac, _ProgressStub(), showResult)

# Cache for potential re-use
_pelvicfractureplanningLogic = logic

# Cache node IDs for subsequent stages
_pelvicfractureplanning_outputPelvis_id = outputPelvis.GetID()
_pelvicfractureplanning_outputFrac_id = outputFrac.GetID()

outputPelvis.CreateClosedSurfaceRepresentation()
_display = outputPelvis.GetDisplayNode()
if _display:
    _display.SetVisibility(True)

outputFrac.CreateClosedSurfaceRepresentation()
_display = outputFrac.GetDisplayNode()
if _display:
    _display.SetVisibility(True)

print("[PelvicFracturePlanning] Segmentation complete.")