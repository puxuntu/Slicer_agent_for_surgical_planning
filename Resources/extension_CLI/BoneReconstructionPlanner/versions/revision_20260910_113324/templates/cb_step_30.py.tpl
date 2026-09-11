# --- BoneReconstructionPlanner: In the same "Mandible planes" row, toggle on the axes-icon tool button to show the plane interaction handles. ---
import slicer
from BoneReconstructionPlanner import BoneReconstructionPlannerLogic

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
    logic = _bonereconstructionplanner_logic
except NameError:
    logic = BoneReconstructionPlannerLogic()
    _bonereconstructionplanner_logic = logic

parameterNode = logic.getParameterNode()

# Sync the bound UI control (mirrors the user's click) so GUI-driven
# parameter syncs cannot ratchet the value back. The module widget does
# not expose the tool button as a direct attribute, so resolve it by its
# object name through the widget tree.
try:
    _module_widget = slicer.modules.bonereconstructionplanner.widgetRepresentation().self()
    _found = slicer.util.findChildren(_module_widget, name='showMandiblePlanesInteractionHandlesToolButton')
    if _found:
        _found[0].checked = True
except Exception:
    pass

parameterNode.SetParameter('showMandiblePlanesInteractionHandles', 'True')
try:
    parameterNode.Modified()
except Exception:
    pass

# Apply the parameter via the extension's own applier method —
# a bare SetParameter only records state; GUI observers may
# recompute it differently.
_module_widget = slicer.modules.bonereconstructionplanner.widgetRepresentation().self()
_module_widget.setMandiblePlanesInteractionHandlesVisibility(True)
_bonereconstructionplanner_logic = logic
print("[BoneReconstructionPlanner] Step 'cb_step_30' completed.")