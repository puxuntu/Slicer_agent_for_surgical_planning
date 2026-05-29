# --- BoneReconstructionPlanner: 8. Change the layout from "Conventional" back to the custom layout "BoneReconstructionPlanner". For the R (red) view, toggle off the slice visibility in the 3D view. (Process) ---
import slicer

node = slicer.mrmlScene.GetNodeByID(_bonereconstructionplanner_cb_step_8_id)
if node is None:
    raise RuntimeError("Node not found for step 'cb_step_8'")

# Exit placement mode
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
interactionNode.SwitchToViewTransformMode()

print("[BoneReconstructionPlanner] Step 'cb_step_8' processed with %d control points." % node.GetNumberOfControlPoints())
