# --- PelvicFracturePlanning: Manually adjust the position and rotation of the selected template. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[PelvicFracturePlanning] Step 'cb_step_12' view adjustment completed.")
