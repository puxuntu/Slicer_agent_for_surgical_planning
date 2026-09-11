# --- PedicleScrewPlanner: cb_step_23 [wizard drive] Click the "Next" button in the "Grading Step" page. ---
import slicer
import qt
_wiz_widget = slicer.util.getModuleWidget('PedicleScrewPlanner')
_wiz_flow = _wiz_widget.workflow
_wiz_flow.goForward()
slicer.app.processEvents(qt.QEventLoop.ExcludeUserInputEvents)
print("[PedicleScrewPlanner] Wizard page navigation: goForward.")