# --- CranialImplantPlanning: Manually adjust the boundaries of the ROI to retain the skull portion. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[CranialImplantPlanning] Step 'cb_step_10' view adjustment completed.")
