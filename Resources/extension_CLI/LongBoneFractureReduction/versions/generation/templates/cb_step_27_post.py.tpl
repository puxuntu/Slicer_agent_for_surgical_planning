# --- LongBoneFractureReduction: Manually adjust the moving fragment. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[LongBoneFractureReduction] Step 'cb_step_27' view adjustment completed.")
