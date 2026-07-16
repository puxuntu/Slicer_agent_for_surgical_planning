# [runtime-fixed] Auto-revised by runtime self-correction at 20260715_210235.
# Pre-revision templates backed up under versions/runtime_fix_20260715_210235/.
# Fixed runtime error: STATE_NOT_APPLIED: No ROI node found from previous step.
# --- LongBoneFractureReduction: Fix for cb_step_25 — Find reference ROI from scene and store in workflow state ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# Step cb_step_24 ("Add / reset reference ROI") completed successfully.
# The reference ROI should exist in the scene. Find it.
roiNodes = slicer.util.getNodesByClass('vtkMRMLMarkupsROINode')
if len(roiNodes) == 0:
    raise RuntimeError("No ROI node found in scene after 'Add / reset reference ROI' step. Please run cb_step_24 first.")

# Find ROI whose name contains "reference" (case-insensitive)
referenceROI = None
for roi in roiNodes:
    name = roi.GetName().lower()
    if 'reference' in name or 'fracture' in name:
        referenceROI = roi
        break

if referenceROI is None:
    # Fallback: use the first/only ROI node
    referenceROI = roiNodes[0]

print(f"Found reference ROI node: {{referenceROI.GetName()}} (ID: {{referenceROI.GetID()}})")

# Ensure display node exists and is visible
displayNode = referenceROI.GetDisplayNode()
if displayNode is None:
    referenceROI.CreateDefaultDisplayNodes()
    displayNode = referenceROI.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)

# Make it the active markups list for user interaction
slicer.modules.markups.logic().SetActiveListID(referenceROI)

# Store in workflow state so subsequent workflow steps can find it
remember_interaction_node("LongBoneFractureReduction", "LongBoneFractureReduction_1784163548576", "cb_step_25", referenceROI.GetID(), 0)

print("[LongBoneFractureReduction] Reference ROI is ready for manual adjustment.")
print("Please manually adjust the ROI boundaries for the reference model in the 3D/slice views.")
print("When finished, type 'done' to proceed.")
