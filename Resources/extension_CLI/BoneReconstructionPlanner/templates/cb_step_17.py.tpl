# --- BoneReconstructionPlanner: 17. Click "Add cut plane" button. (Setup) ---
import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()

logic.addCutPlane()
_bonereconstructionplanner_logic = logic

print("[BoneReconstructionPlanner] Placement started for step 'cb_step_17'.")
