# --- BoneReconstructionPlanner: For the "Current Scalar Volume" option, select the Mandible Volume. ---
import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

try:
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

parameterNode = logic.getParameterNode()
current_scalar_volume_node_name = {current_scalar_volume_node_name: ''}
current_scalar_volume_node = None
if current_scalar_volume_node_name:
    try:
        current_scalar_volume_node = slicer.util.getNode(current_scalar_volume_node_name)
    except Exception:
        pass
if current_scalar_volume_node is None:
    _nodes = slicer.mrmlScene.GetNodesByClass('vtkMRMLScalarVolumeNode')
    _keywords = ['currentscalarvolume', 'mandible']
    for _i in range(_nodes.GetNumberOfItems()):
        _candidate = _nodes.GetItemAsObject(_i)
        _name = (_candidate.GetName() or '').lower()
        if not _keywords or any(_kw in _name for _kw in _keywords):
            current_scalar_volume_node = _candidate
            break
if current_scalar_volume_node is None:
    raise RuntimeError('Could not find node for parameter reference currentScalarVolume')
parameterNode.SetNodeReferenceID('currentScalarVolume', current_scalar_volume_node.GetID())
try:
    parameterNode.Modified()
except Exception:
    pass
_bonereconstructionplanner_logic = logic
print("[BoneReconstructionPlanner] Step 'cb_step_4' completed.")
