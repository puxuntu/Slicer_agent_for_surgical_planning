# --- BoneReconstructionPlanner: 12. Tick the following options: "Automatic mandibular planes positioning for maximum bones contact area" and "Make all mandible planes rotate together." ---
try:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
except ImportError:
    raise RuntimeError("BoneReconstructionPlanner extension is not installed.")

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()

# Execute the automated step
if hasattr(logic, 'automaticMandibularPlanesPositioningForMaximumBonesContactArea'):
    result = logic.automaticMandibularPlanesPositioningForMaximumBonesContactArea()
else:
    result = None

_bonereconstructionplanner_logic = logic
print("[BoneReconstructionPlanner] Step 'cb_step_12' completed.")
