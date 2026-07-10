# --- ReverseShoulderArthroplasty: If further adjustments are required, check the "Adjust Prosthesis (3D transform handles)" box. If not, proceed to Step 20. ---
import slicer
# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'SlicerScrewPlanner':
    try:
        slicer.util.selectModule('SlicerScrewPlanner')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'SlicerScrewPlanner': {_module_enter_error}")
# precondition:end

# Drive the extension's own widget handler on the live module widget
_widget = None
try:
    _widget = slicer.util.getModuleWidget('SlicerScrewPlanner')
except Exception:
    _widget = None
if _widget is None:
    try:
        _widget = slicer.modules.slicerscrewplanner.widgetRepresentation().self()
    except Exception:
        _widget = None
if _widget is None:
    raise RuntimeError("Could not obtain the SlicerScrewPlanner module widget for 'adjustBaseplateCheckBox'.")
if not hasattr(_widget, 'onToggleAdjustBaseplate'):
    raise RuntimeError("SlicerScrewPlanner widget has no handler 'onToggleAdjustBaseplate' for 'adjustBaseplateCheckBox'; regenerate the CLI.")
# Resolve the bound control by name
_ctrl = None
try:
    _ui = _widget.ui
    _ctrl = _ui.adjustBaseplateCheckBox
except AttributeError:
    pass
if _ctrl is None:
    try:
        _ctrl = _widget.adjustBaseplateCheckBox
    except AttributeError:
        pass
if _ctrl is None:
    try:
        _found = slicer.util.findChildren(_widget, name='adjustBaseplateCheckBox')
        _ctrl = _found[0] if _found else None
    except Exception:
        _ctrl = None
if _ctrl is not None:
    try:
        _ctrl.blockSignals(True)
        _ctrl.checked = True
        _ctrl.blockSignals(False)
    except Exception:
        pass
try:
    _widget.onToggleAdjustBaseplate(True)
except TypeError:
    _widget.onToggleAdjustBaseplate()
print("[ReverseShoulderArthroplasty] Step 'cb_step_17': set 'adjustBaseplateCheckBox' = True via onToggleAdjustBaseplate.")
