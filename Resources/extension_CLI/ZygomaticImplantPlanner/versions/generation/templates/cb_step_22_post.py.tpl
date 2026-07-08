# --- ZygomaticImplantPlanner: Manually adjust the paths. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[ZygomaticImplantPlanner] Step 'cb_step_22' view adjustment completed.")
