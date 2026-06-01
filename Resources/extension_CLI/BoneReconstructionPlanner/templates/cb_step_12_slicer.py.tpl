# --- BoneReconstructionPlanner: 12. Configure display for mandibular curve to show in both View 1 and Red view. ---
import slicer

# Get the parameter node and the mandible curve
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

parameterNode = logic.getParameterNode()
curveNode = parameterNode.GetNodeReference("mandibleCurve")
if curveNode is None:
    # Fallback: find the most recent curve
    nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsCurveNode")
    for i in range(nodes.GetNumberOfItems() - 1, -1, -1):
        n = nodes.GetItemAsObject(i)
        if "mandibular" in n.GetName().lower():
            curveNode = n
            break
    if curveNode is None:
        raise RuntimeError("Mandibular curve node not found. Run step 13 first.")

displayNode = curveNode.GetDisplayNode()
if displayNode is None:
    raise RuntimeError("Curve display node not available.")

# Add view node IDs: Mandible view (View 1) and Red slice view
# View 1 ID is typically obtained from the singleton tag (MANDIBLE_VIEW_SINGLETON_TAG)
mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
if mandibleViewNode:
    displayNode.AddViewNodeID(mandibleViewNode.GetID())

# Red slice node (2D slice view) - note: markups can be shown in slice views
redSliceNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceNodeRed")
if redSliceNode:
    displayNode.AddViewNodeID(redSliceNode.GetID())

# Switch to Markups module (optional, for user context)
slicer.util.selectModule('Markups')

# Ensure visibility is on
displayNode.SetVisibility(True)

print("[BoneReconstructionPlanner] Step cb_step_12 completed: curve display configured for View 1 and Red view.")
