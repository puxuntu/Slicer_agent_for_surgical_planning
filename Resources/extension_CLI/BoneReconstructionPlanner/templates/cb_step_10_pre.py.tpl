# Extension op: Click 'Add fibula line' button to create a line markup node.
import numpy as np
try:
    _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()
parameterNode = _bonereconstructionplanner_logic.getParameterNode()
_bonereconstructionplanner_logic.addFibulaLine()
print("[BoneReconstructionPlanner] Step cb_step_10 completed: added fibula line.")