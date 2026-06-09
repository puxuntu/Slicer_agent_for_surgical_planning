# --- BoneReconstructionPlanner: If the fibula is from the right leg, tick the "Right side leg" checkbox. ---
import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

parameterNode = logic.getParameterNode()
# Final state was not explicit; apply source-derived/default truthy state for rightSideLegFibula
parameterNode.SetParameter('rightSideLegFibula', 'True')
try:
    parameterNode.Modified()
except Exception:
    pass
_bonereconstructionplanner_logic = logic
print("[BoneReconstructionPlanner] Step 'cb_step_1' completed.")
