# --- PelvicFracturePlanning: Manually adjust the position and rotation of the selected fragment. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[PelvicFracturePlanning] Step 'cb_step_10' view adjustment completed.")
