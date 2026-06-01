# --- BoneReconstructionPlanner: 20. Draw a line over the fibula in "3D View 2", starting with the first point distally and the last point proximally. (Setup) ---
import slicer

# Reuse the markup node created by addFibulaLine() in the previous step.
nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsLineNode")
node = None
for i in range(nodes.GetNumberOfItems() - 1, -1, -1):
    candidate = nodes.GetItemAsObject(i)
    if candidate is not None:
        node = candidate
        break
if node is None:
    raise RuntimeError("No vtkMRMLMarkupsLineNode found from previous placement step.")

displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)
slicer.modules.markups.logic().SetActiveListID(node)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToPersistentPlaceMode()
_bonereconstructionplanner_cb_step_20_id = node.GetID()

print("[BoneReconstructionPlanner] Please Click first point at distal end of fibula, last point at proximal end of fibula in 3D View 2")
print("When finished, press the 'Done' button in the workflow panel.")
