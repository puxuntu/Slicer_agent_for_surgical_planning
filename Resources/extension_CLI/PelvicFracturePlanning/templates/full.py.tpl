# --- Full Pipeline: PelvicFracturePlanning ---
# Auto-generated CLI template — runs all stages sequentially.

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

showResult = True

# === STAGE 1: Segmentation ===
outputPelvis = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationNode")
outputFrac = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationNode")
logic.process_seg(inputVolume, outputPelvis, outputFrac, _ProgressStub(), showResult)
print(f'  Stage 1 complete.')

# === STAGE 2: Planning ===
OutputPelvisSeg = outputPelvis  # from prior stage
OutputFracSeg = outputFrac  # from prior stage
OutputReduction = slicer.mrmlScene.CreateNodeByClass("vtkMRMLSegmentationNode")
OutputScrew = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
logic.process_plan(inputVolume, OutputPelvisSeg, OutputFracSeg, OutputReduction, OutputScrew, _ProgressStub(), showResult)
print(f'  Stage 2 complete.')

_pelvicfractureplanningLogic = logic

print("[PelvicFracturePlanning] === Pipeline Complete ===")