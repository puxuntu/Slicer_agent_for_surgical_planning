# --- BoneReconstructionPlanner: Clear the "Show original mandible model" checkbox. ---
import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

parameterNode = logic.getParameterNode()
parameterNode.SetParameter('showOriginalMandible', 'False')
try:
    parameterNode.Modified()
except Exception:
    pass
_bonereconstructionplanner_logic = logic
print("[BoneReconstructionPlanner] Step 'cb_step_32' completed.")
