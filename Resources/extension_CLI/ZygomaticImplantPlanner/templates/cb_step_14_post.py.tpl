# --- ZygomaticImplantPlanner: Manually adjust the separation plane. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[ZygomaticImplantPlanner] Step 'cb_step_14' view adjustment completed.")
