# --- OrbitalFractureReconstruction: Manually click and adjust on the Slice views to create the ROI for the "Orbital_Region". (Setup) ---
import slicer
from SlicerAIAgentLib.workflow_state import remember_interaction_node

# Get or create the ROI node for placement
node = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLMarkupsROINode")
if node is None:
    # Create a new ROI node for the user to place
    node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsROINode", "Orbital_Region")

# Ensure the node is visible and interactive
displayNode = node.GetDisplayNode()
if displayNode is None:
    node.CreateDefaultDisplayNodes()
    displayNode = node.GetDisplayNode()
if displayNode is not None:
    displayNode.SetVisibility(True)

slicer.modules.markups.logic().SetActiveListID(node)
interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if interactionNode is not None:
    interactionNode.SwitchToSinglePlaceMode()

_orbitalfracturereconstruction_cb_step_3_id = node.GetID()
remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, "cb_step_3", _orbitalfracturereconstruction_cb_step_3_id, _workflow_runtime_repeat_index)

print("[OrbitalFractureReconstruction] Please Click and adjust on the slice views to create the ROI for Orbital_Region")
print("When finished, press the 'Done' button in the workflow panel.")