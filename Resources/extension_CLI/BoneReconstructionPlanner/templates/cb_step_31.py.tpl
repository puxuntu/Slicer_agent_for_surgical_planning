# --- BoneReconstructionPlanner: When the reconstruction is satisfactory, in the BoneReconstructionPlanner module's "Mandible planes" row, toggle off the eye-icon tool button to hide the mandibular cut planes. ---
import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

parameterNode = logic.getParameterNode()
parameterNode.SetParameter('showMandiblePlanes', 'False')
try:
    parameterNode.Modified()
except Exception:
    pass
_bonereconstructionplanner_logic = logic
print("[BoneReconstructionPlanner] Step 'cb_step_31' completed.")
