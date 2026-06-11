# --- BoneReconstructionPlanner: Place one mandibular cut plane using the extension's Add cut plane workflow. If the user requested N cut planes, repeat the Add cut plane + place plane interaction N times. Do not store these planes as a rotation plane; they are mandibular cut planes managed by the extension. (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

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
_bonereconstructionplanner_cb_step_18_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_18", _bonereconstructionplanner_cb_step_18_id, _workflow_runtime_repeat_index)

print("[BoneReconstructionPlanner] Please Place this plane, then click Done.")
print("When finished, press the 'Done' button in the workflow panel.")
