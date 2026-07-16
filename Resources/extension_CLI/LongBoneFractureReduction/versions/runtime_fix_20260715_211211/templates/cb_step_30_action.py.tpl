# --- LongBoneFractureReduction: If further adjustments are required, check the "Manually adjust the moving fragment" box. If not, stop here. ---
import slicer

# precondition:begin
# Ensure the extension module is active so module.enter() has run.
_active_module_name = slicer.util.selectedModule()
if _active_module_name != 'LongBoneFractureReduction':
    try:
        slicer.util.selectModule('LongBoneFractureReduction')
    except Exception as _module_enter_error:
        print(f"Warning: could not activate module 'LongBoneFractureReduction': {_module_enter_error}")
# precondition:end

# Drive the extension's own widget handler on the live module widget:
_widget = None
try:
    _widget = slicer.util.getModuleWidget('LongBoneFractureReduction')
except Exception:
    _widget = None
if _widget is None:
    try:
        _widget = slicer.modules.longbonefracturereduction.widgetRepresentation().self()
    except Exception:
        _widget = None
if _widget is None:
    raise RuntimeError("Could not obtain the LongBoneFractureReduction module widget for 'chkManualAdjust'.")

# Check if the handler exists
if not hasattr(_widget, 'onManualAdjustToggled'):
    raise RuntimeError("LongBoneFractureReduction widget has no handler 'onManualAdjustToggled' for 'chkManualAdjust'; regenerate the CLI.")

# Safely access the checkbox control
_ctrl = None
try:
    _ui = _widget.ui
except AttributeError:
    _ui = None
if _ui is not None:
    try:
        _ctrl = _ui.chkManualAdjust
    except AttributeError:
        _ctrl = None
if _ctrl is None:
    try:
        _ctrl = _widget.chkManualAdjust
    except AttributeError:
        _ctrl = None
if _ctrl is None:
    try:
        _found = slicer.util.findChildren(_widget, name='chkManualAdjust')
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
    _widget.onManualAdjustToggled(True)
except TypeError:
    _widget.onManualAdjustToggled()

print("[LongBoneFractureReduction] Step 'cb_step_30': set 'chkManualAdjust' = True via onManualAdjustToggled.")