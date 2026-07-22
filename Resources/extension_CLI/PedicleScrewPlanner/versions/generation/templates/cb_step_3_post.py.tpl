# --- PedicleScrewPlanner: Manually adjust the boundaries of the ROI. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[PedicleScrewPlanner] Step 'cb_step_3' view adjustment completed.")
