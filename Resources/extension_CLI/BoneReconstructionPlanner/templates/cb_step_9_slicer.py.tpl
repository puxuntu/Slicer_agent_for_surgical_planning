# --- BoneReconstructionPlanner: 9. Toggle on slice intersection visibility (crosshair) in toolbar. ---
import slicer

# Get the crosshair singleton node (should exist by default)
crosshairNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLCrosshairNode")
if not crosshairNode:
    # Create one if none exists (required for the operation)
    crosshairNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLCrosshairNode", "Crosshair")
    crosshairNode.SetSingletonTag("default")

# Set crosshair mode to ShowIntersection (turns on slice intersection visibility)
crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.ShowIntersection)

print("[BoneReconstructionPlanner] Step cb_step_9 completed: slice intersection visibility toggled ON.")
