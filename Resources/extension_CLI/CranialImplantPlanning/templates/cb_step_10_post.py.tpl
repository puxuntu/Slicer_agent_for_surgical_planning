# --- CranialImplantPlanning: Manually adjust the boundary of the ROI to keep the skull part. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[CranialImplantPlanning] Step 'cb_step_10' view adjustment completed.")
