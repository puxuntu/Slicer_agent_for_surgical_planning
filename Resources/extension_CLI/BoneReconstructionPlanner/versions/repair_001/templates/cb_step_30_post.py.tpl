# --- BoneReconstructionPlanner: Manually adjust the mandibular cut planes in the mandible 3D view by dragging the visible plane interaction handles. (Done) ---
import slicer

interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[BoneReconstructionPlanner] Step 'cb_step_30' view adjustment completed.")
