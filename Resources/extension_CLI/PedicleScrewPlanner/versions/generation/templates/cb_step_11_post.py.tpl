# --- PedicleScrewPlanner: Manually adjust the start and end position of puncture site in 2D views. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[PedicleScrewPlanner] Step 'cb_step_11' view adjustment completed.")
