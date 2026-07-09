# --- ReverseShoulderArthroplasty: Manually adjust the endpoints of the planning paths. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[ReverseShoulderArthroplasty] Step 'cb_step_21' view adjustment completed.")
