# --- BoneReconstructionPlanner: 12. Click the "Add mandibular curve" button. (Setup) ---
import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()

logic.addMandibularCurve()
_bonereconstructionplanner_logic = logic

print("[BoneReconstructionPlanner] Placement started for step 'cb_step_12'.")
