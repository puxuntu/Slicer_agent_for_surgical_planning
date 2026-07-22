# --- PedicleScrewPlanner: cb_step_2 [wizard drive] Click the "Next" button in the "1. Load Image Volume" page. ---
import slicer
import qt
_wiz_widget = slicer.util.getModuleWidget('PedicleScrewPlanner')
_wiz_flow = _wiz_widget.workflow
_wiz_flow.goForward()
slicer.app.processEvents()
print("[PedicleScrewPlanner] Wizard page navigation: goForward.")