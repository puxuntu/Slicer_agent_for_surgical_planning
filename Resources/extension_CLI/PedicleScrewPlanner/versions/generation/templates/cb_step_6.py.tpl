# --- PedicleScrewPlanner: cb_step_6 [wizard drive] Click the "Place a control point" button. ---
import slicer
import qt
_wiz_widget = slicer.util.getModuleWidget('PedicleScrewPlanner')
_wiz_hit = False
try:
    _wiz_root = slicer.util.getModule('PedicleScrewPlanner').widgetRepresentation()
    _wiz_pw = slicer.util.findChildren(_wiz_root, className='qSlicerMarkupsPlaceWidget')[0]
    _wiz_pw.setPlaceModeEnabled(True)
    _wiz_hit = True
except (IndexError, Exception):
    _wiz_hit = False
if not _wiz_hit:
    _wiz_root = slicer.util.getModule('PedicleScrewPlanner').widgetRepresentation()
    for _wiz_pw in slicer.util.findChildren(_wiz_root, className='qSlicerMarkupsPlaceWidget'):
        try:
            _wiz_pw.setPlaceModeEnabled(True)
            _wiz_hit = True
            break
        except Exception:
            continue
if _wiz_hit:
    print("[PedicleScrewPlanner] Place mode enabled -- click in the views to add points.")
else:
    raise RuntimeError("No markups place widget found in the PedicleScrewPlanner wizard.")