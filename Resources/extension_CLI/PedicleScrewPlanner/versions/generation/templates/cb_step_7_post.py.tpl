# --- PedicleScrewPlanner: Manually adjust the rotation angle of the red slice. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[PedicleScrewPlanner] Step 'cb_step_7' view adjustment completed.")
