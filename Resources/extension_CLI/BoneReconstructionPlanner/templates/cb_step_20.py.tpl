# --- BoneReconstructionPlanner: 20. Click "Add fibula line" button. (Setup) ---
import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()

logic.addFibulaLine()
_bonereconstructionplanner_logic = logic

print("[BoneReconstructionPlanner] Placement started for step 'cb_step_20'.")
