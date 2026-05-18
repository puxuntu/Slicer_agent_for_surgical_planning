# --- PelvicFracturePlanning: Planning ---
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

# Retrieve cached state from prior stage
try:
    logic = _pelvicfractureplanningLogic
    print("Reusing cached logic instance from prior stage.")
except NameError:
    logic = PelvicFracturePlanningLogic()

class _ProgressStub:
    def setMaximum(self, v): pass
    def setValue(self, v): pass

showResult = {showResult: True}

# Create output nodes
OutputPelvisSeg = slicer.mrmlScene.GetNodeByID(_pelvicfractureplanning_outputPelvis_id)
OutputFracSeg = slicer.mrmlScene.GetNodeByID(_pelvicfractureplanning_outputFrac_id)
OutputReduction = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationNode")
OutputScrew = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")

print("[PelvicFracturePlanning] Running planning...")
logic.process_plan(inputVolume, OutputPelvisSeg, OutputFracSeg, OutputReduction, OutputScrew, _ProgressStub(), showResult)

# Cache for potential re-use
_pelvicfractureplanningLogic = logic

# Cache node IDs for subsequent stages
_pelvicfractureplanning_OutputReduction_id = OutputReduction.GetID()
_pelvicfractureplanning_OutputScrew_id = OutputScrew.GetID()

OutputReduction.CreateClosedSurfaceRepresentation()
_display = OutputReduction.GetDisplayNode()
if _display:
    _display.SetVisibility(True)

_display = OutputScrew.GetDisplayNode()
if _display is None:
    _display = OutputScrew.CreateDefaultDisplayNode()
_display.SetVisibility(True)

print("[PelvicFracturePlanning] Planning complete.")