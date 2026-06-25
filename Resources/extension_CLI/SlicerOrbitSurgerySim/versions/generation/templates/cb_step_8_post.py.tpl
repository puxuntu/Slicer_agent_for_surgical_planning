# --- SlicerOrbitSurgerySim: Manually adjust the position and rotation of the plate. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[SlicerOrbitSurgerySim] Step 'cb_step_8' view adjustment completed.")
