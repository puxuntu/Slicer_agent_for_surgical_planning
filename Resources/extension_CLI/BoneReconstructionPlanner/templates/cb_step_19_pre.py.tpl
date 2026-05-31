# --- BoneReconstructionPlanner: 19. Click where you want the plane in "3D View 1" to create the first plane. Repeat this process to add as many planes as needed. (Setup) ---
import slicer

# Reuse the markup node created by addCutPlane() in the previous step.
nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsPlaneNode")
node = None
for i in range(nodes.GetNumberOfItems() - 1, -1, -1):
    candidate = nodes.GetItemAsObject(i)
    if candidate is not None:
        node = candidate
        break
if node is None:
    raise RuntimeError("No vtkMRMLMarkupsPlaneNode found from previous placement step.")

displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)
slicer.modules.markups.logic().SetActiveListID(node)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToPersistentPlaceMode()
_bonereconstructionplanner_cb_step_19_id = node.GetID()

print("[BoneReconstructionPlanner] Please Click in 3D View 1 to position the cut plane. Repeat for each plane.")
print("When finished, press the 'Done' button in the workflow panel.")
