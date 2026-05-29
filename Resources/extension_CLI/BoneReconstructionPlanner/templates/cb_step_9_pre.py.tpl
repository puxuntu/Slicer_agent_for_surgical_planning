# Extension op: Click 'Add cut plane' button to create a new plane markup node.
import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

# Reuse existing logic instance if available, otherwise create a new one
try:
    _bonereconstructionplanner_logic  # type: ignore
except NameError:
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

# The method reads self.PLANE_SIDE_SIZE and self.PLANE_GLYPH_SCALE from the logic instance.
# These are expected to be already initialized (e.g., in __init__ or prior steps).
# No additional state setup is required for this step beyond having the logic instance.

# Execute the step
_bonereconstructionplanner_logic.addCutPlane()

print("[BoneReconstructionPlanner] cb_step_9: addCutPlane() completed successfully.")