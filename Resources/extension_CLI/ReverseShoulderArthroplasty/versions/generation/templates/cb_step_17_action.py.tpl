# --- ReverseShoulderArthroplasty: If further adjustments are required, check the "Adjust Prosthesis (3D transform handles)" box. If not, proceed to Step 20. ---
import slicer

# precondition:begin
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'SlicerScrewPlanner3':
    try:
        slicer.util.selectModule('SlicerScrewPlanner3')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'SlicerScrewPlanner3': {_module_enter_error}")
# precondition:end

# Drive the extension's own widget handler on the live module widget
_widget = None
try:
    _widget = slicer.util.getModuleWidget('SlicerScrewPlanner3')
except Exception:
    _widget = None
if _widget is None:
    try:
        _widget = slicer.modules.slicerscrewplanner3.widgetRepresentation().self()
    except Exception:
        _widget = None
if _widget is None:
    raise RuntimeError("Could not obtain the SlicerScrewPlanner3 module widget for 'adjustBaseplateCheckBox'.")

# Resolve the checkbox control (avoid getattr, use direct attribute access)
_ctrl = None
_ui = None
try:
    _ui = _widget.ui
except AttributeError:
    _ui = None
if _ui is not None:
    try:
        _ctrl = _ui.adjustBaseplateCheckBox
    except AttributeError:
        _ctrl = None
if _ctrl is None:
    try:
        _ctrl = _widget.adjustBaseplateCheckBox
    except AttributeError:
        _ctrl = None
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

# Invoke the handler
try:
    _widget.onToggleAdjustBaseplate(True)
except TypeError:
    _widget.onToggleAdjustBaseplate()
except AttributeError:
    raise RuntimeError("SlicerScrewPlanner3 widget has no handler 'onToggleAdjustBaseplate'.")

print("[ReverseShoulderArthroplasty] Step 'cb_step_17': set 'adjustBaseplateCheckBox' = True via onToggleAdjustBaseplate.")
