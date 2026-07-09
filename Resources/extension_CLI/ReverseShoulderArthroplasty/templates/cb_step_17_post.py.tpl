# --- ReverseShoulderArthroplasty: Manually adjust the 3D transform handles. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[ReverseShoulderArthroplasty] Step 'cb_step_17' view adjustment completed.")
