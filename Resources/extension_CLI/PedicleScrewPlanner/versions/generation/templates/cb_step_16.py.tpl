# --- PedicleScrewPlanner: cb_step_16 [wizard drive] Click the "Grade Screws" button. ---
import slicer
import qt
_wiz_widget = slicer.util.getModuleWidget('PedicleScrewPlanner')
_wiz_hit = False
try:
    _wiz_widget.gradeStep.gradeScrews()
    _wiz_hit = True
except AttributeError:
    _wiz_hit = False
if not _wiz_hit:
    # Fallback: click by visible text anywhere in the module widget.
    _wiz_root = slicer.util.getModule('PedicleScrewPlanner').widgetRepresentation()
    _wiz_label = 'Grade Screws'.replace('&', '').strip().lower()
    for _wiz_cls in ('QPushButton', 'QToolButton'):
        for _wiz_btn in slicer.util.findChildren(_wiz_root, className=_wiz_cls):
            try:
                _wiz_text = _wiz_btn.text
            except Exception:
                continue
            if isinstance(_wiz_text, str) and _wiz_text.replace('&', '').strip().lower() == _wiz_label:
                _wiz_btn.click()
                _wiz_hit = True
                break
        if _wiz_hit:
            break
slicer.app.processEvents()
if _wiz_hit:
    print("[PedicleScrewPlanner] Triggered the 'Grade Screws' action.")
else:
    raise RuntimeError("Could not trigger the 'Grade Screws' button in the PedicleScrewPlanner wizard.")