# --- PedicleScrewPlanner: cb_step_10 [wizard drive] Click the "Place a control point" button to inactivate the point placement. ---
import slicer
import qt
_wiz_widget = slicer.util.getModuleWidget('PedicleScrewPlanner')
_wiz_hit = False
try:
    _wiz_widget.landmarksStep.startMeasurements.setPlaceModeEnabled(False)
    _wiz_hit = True
except AttributeError:
    _wiz_hit = False
if not _wiz_hit:
    _wiz_root = slicer.util.getModule('PedicleScrewPlanner').widgetRepresentation()
    for _wiz_pw in slicer.util.findChildren(_wiz_root, className='qSlicerMarkupsPlaceWidget'):
        try:
            _wiz_pw.setPlaceModeEnabled(False)
            _wiz_hit = True
            break
        except Exception:
            continue
_wiz_inode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
if _wiz_inode is not None:
    _wiz_inode.SwitchToViewTransformMode()
if _wiz_hit:
    print("[PedicleScrewPlanner] Place mode disabled -- the views take the mouse again.")
else:
    raise RuntimeError("No markups place widget found in the PedicleScrewPlanner wizard.")
