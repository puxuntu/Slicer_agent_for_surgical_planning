# --- ReverseShoulderArthroplasty: Manually adjust the 3D view to get the best angle for placing the fiducial point on the glenoid cavity surface. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[ReverseShoulderArthroplasty] Step 'cb_step_12' view adjustment completed.")
