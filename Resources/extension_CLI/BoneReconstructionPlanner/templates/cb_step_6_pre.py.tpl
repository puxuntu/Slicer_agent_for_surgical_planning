# Extension op: Click 'Add mandibular curve' button to create a curve markup node.
# Try to reuse existing logic instance, or create new one
try:
    logic = _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

# Call the method
logic.addMandibularCurve()

print("BoneReconstructionPlanner: Mandibular curve added successfully.")

# Slicer op: Open the Markups module.
slicer.util.selectModule("Markups")

# Slicer op: In the Markups module, expand the Display and Advanced panels, and set View to View 1 with Red selected.
slicer.util.selectModule("Markups")