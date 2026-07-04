# --- CranialImplantPlanning: Manually adjust the 3D view to get the best angle for placing the cutting curve. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[CranialImplantPlanning] Step 'cb_step_12' view adjustment completed.")
