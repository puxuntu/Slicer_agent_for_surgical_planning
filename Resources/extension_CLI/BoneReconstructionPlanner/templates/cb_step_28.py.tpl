# --- BoneReconstructionPlanner: Enter the desired value in "Between space (mm)". ---
import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

parameterNode = logic.getParameterNode()
additional_between_space_of_fibula_planes = {additional_between_space_of_fibula_planes: 1.5}
parameterNode.SetParameter('additionalBetweenSpaceOfFibulaPlanes', str(additional_between_space_of_fibula_planes))
try:
    parameterNode.Modified()
except Exception:
    pass
_bonereconstructionplanner_logic = logic
print("[BoneReconstructionPlanner] Step 'cb_step_28' completed.")
