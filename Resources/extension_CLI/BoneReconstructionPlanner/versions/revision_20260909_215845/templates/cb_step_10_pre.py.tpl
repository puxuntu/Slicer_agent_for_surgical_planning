# --- BoneReconstructionPlanner: Manually adjust the slice intersection position by translate and rotate of the cross lines in each view. (Setup) ---
import slicer

# This step is a view adjustment, not a Markups placement: give the
# views back to the mouse before the user starts adjusting.
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[BoneReconstructionPlanner] Please Manually adjust the slice intersection position by translate and rotate of the cross lines in each view.")
print("When finished, press the 'Done' button in the workflow panel.")
