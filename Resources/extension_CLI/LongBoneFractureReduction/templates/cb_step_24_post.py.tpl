# --- LongBoneFractureReduction: Manually adjust the rotation and displacement of the moving part. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[LongBoneFractureReduction] Step 'cb_step_24' view adjustment completed.")
