# --- PedicleScrewPlanner: Manually adjust the start and end position of puncture site in 2D views. (Setup) ---
import slicer

# This step is a view adjustment, not a Markups placement: give the
# views back to the mouse before the user starts adjusting.
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToViewTransformMode()

print("[PedicleScrewPlanner] Please Manually adjust the start and end position of the puncture site in the 2D views.")
print("When finished, press the 'Done' button in the workflow panel.")
