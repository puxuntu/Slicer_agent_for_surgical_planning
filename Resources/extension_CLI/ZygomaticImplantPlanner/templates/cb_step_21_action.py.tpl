# --- ZygomaticImplantPlanner: If further adjustments are required, tick the "Manually adjust the boundary planes" checkbox. If not, jump to step 24. ---
# [source drive] derived from the scanned .ui binding -- do not rewrite.
import slicer
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'ZygomaticImplantPlanner':
    try:
        slicer.util.selectModule('ZygomaticImplantPlanner')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'ZygomaticImplantPlanner': {_module_enter_error}")
# precondition:end

# 'refineZygomaCheckBox' is bound to the extension's parameter field 'refineZygoma' by its
# .ui SlicerParameterName property; connectGui() keeps control and field in
# sync. Setting the field is what ticking the box does, so the extension's
# own parameter-node observer performs the real work and the control updates.
_widget = None
try:
    _widget = slicer.util.getModuleWidget('ZygomaticImplantPlanner')
except Exception:
    _widget = None
if _widget is None:
    try:
        _widget = slicer.modules.zygomaticimplantplanner.widgetRepresentation().self()
    except Exception:
        _widget = None
if _widget is None:
    raise RuntimeError("Could not obtain the ZygomaticImplantPlanner module widget for 'refineZygomaCheckBox'.")
_pnode = _widget._parameterNode if hasattr(_widget, '_parameterNode') else None
if _pnode is None and hasattr(_widget, 'logic'):
    _logic = _widget.logic
    if _logic is not None and hasattr(_logic, 'getParameterNode'):
        try:
            _pnode = _logic.getParameterNode()
        except Exception:
            _pnode = None
if _pnode is None:
    raise RuntimeError("Could not reach the ZygomaticImplantPlanner parameter node to set 'refineZygoma'.")
if not hasattr(_pnode, 'refineZygoma'):
    raise RuntimeError("ZygomaticImplantPlanner parameter node has no field 'refineZygoma'; regenerate the CLI.")
_pnode.refineZygoma = True
print("[ZygomaticImplantPlanner] Step 'cb_step_21': set 'refineZygomaCheckBox' (parameter 'refineZygoma') = True.")

