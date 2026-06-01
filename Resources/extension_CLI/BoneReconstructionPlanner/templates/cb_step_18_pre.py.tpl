# --- BoneReconstructionPlanner: 18. Place one mandibular cut plane. (Setup) ---
import slicer

# Reuse the markup node created by addCutPlane() in the previous step (step 17)
nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsPlaneNode")
node = None
for i in range(nodes.GetNumberOfItems() - 1, -1, -1):
    candidate = nodes.GetItemAsObject(i)
    if candidate is not None and candidate.GetName().startswith("mandibularPlane"):
        node = candidate
        break
if node is None:
    # Fallback: get the last created plane
    if nodes.GetNumberOfItems() > 0:
        node = nodes.GetItemAsObject(nodes.GetNumberOfItems() - 1)
if node is None:
    raise RuntimeError("No vtkMRMLMarkupsPlaneNode found from step 17. Ensure step 17 was executed.")

displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)

slicer.modules.markups.logic().SetActiveListID(node)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToPersistentPlaceMode()

# Store the node ID for post-processing
_bonereconstructionplanner_cb_step_18_id = node.GetID()

print("[BoneReconstructionPlanner] Please Place the cutting plane in the 3D view using the extension's Add cut plane workflow.")
print("When finished, press the 'Done' button in the workflow panel.")
