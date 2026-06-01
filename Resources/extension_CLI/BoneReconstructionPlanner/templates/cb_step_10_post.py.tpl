# --- BoneReconstructionPlanner: 10. Manually adjust the slice intersection position. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[BoneReconstructionPlanner] Step 'cb_step_10' view adjustment completed.")
