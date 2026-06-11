import slicer
import traceback

# Reuse existing logic instance if available
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'BoneReconstructionPlanner':
    try:
        slicer.util.selectModule('BoneReconstructionPlanner')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'BoneReconstructionPlanner': {_module_enter_error}")
# precondition:end

try:
    _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

logic = _bonereconstructionplanner_logic

# Get the parameter node for this module
parameterNode = logic.getParameterNode()

# Ensure default parameter 'useNonDecimatedBoneModelsForPreview' is set
if not parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview"):
    parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview", "True")

# Ensure segmentation node references exist for fibula and mandible
for role, search_name in [("fibulaSegmentation", "fibula"), ("mandibularSegmentation", "mandible")]:
    node = parameterNode.GetNodeReference(role)
    if node is None:
        # Search by name using the role keyword as fallback
        node = slicer.mrmlScene.GetFirstNodeByName(role)
        if node is None:
            # Try broader search: look for vtkMRMLSegmentationNode with name containing search_name
            nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
            for i in range(nodes.GetNumberOfItems()):
                n = nodes.GetItemAsObject(i)
                if search_name.lower() in n.GetName().lower():
                    node = n
                    break
        if node is None:
            raise RuntimeError(f"Could not find segmentation node for role '{role}'. Ensure fibula and mandible segmentations are created before Step 5.")
        parameterNode.SetNodeReferenceID(role, node.GetID())

# Execute the makeModels step
try:
    logic.makeModels()
except Exception as e:
    print(f"[BoneReconstructionPlanner] Error in makeModels: {e}")
    traceback.print_exc()
    raise

# Store logic instance for subsequent steps
_bonereconstructionplanner_logic = logic

print("[BoneReconstructionPlanner] Step 5 complete: bone models created and oriented in segmentation views.")
