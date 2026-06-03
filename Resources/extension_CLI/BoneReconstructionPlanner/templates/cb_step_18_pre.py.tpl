# --- BoneReconstructionPlanner: 18. Place a mandibular cut plane (Setup) ---
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
_bonereconstructionplanner_cb_step_18_id = node.GetID()

print("[BoneReconstructionPlanner] Please Click and drag in the 3D view to position the cutting plane on the mandible")
print("When finished, press the 'Done' button in the workflow panel.")