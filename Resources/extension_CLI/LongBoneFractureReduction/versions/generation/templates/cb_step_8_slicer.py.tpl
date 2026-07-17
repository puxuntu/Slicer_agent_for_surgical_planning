# --- [Segment Editor session] select an option/mode of the active effect ---
# Keep the current effect active (do NOT switch to a default) and set its
# mode by driving the effect's own option widget matching the cookbook label,
# so the effect's handler applies the parameter exactly as a click would.
import slicer
_ses_widget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
_ses_widget.setMRMLScene(slicer.mrmlScene)
_ses_editor_node = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentEditorNode")
if _ses_editor_node is None:
    _ses_editor_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
_ses_widget.setMRMLSegmentEditorNode(_ses_editor_node)
_ses_seg = None
_ses_segs = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
for _ses_i in range(_ses_segs.GetNumberOfItems()):
    _ses_c = _ses_segs.GetItemAsObject(_ses_i)
    if _ses_c is not None and _ses_c.GetAttribute("SlicerAIAgent.SegmentEditorSession") == "1":
        _ses_seg = _ses_c
        break
if _ses_seg is None:
    for _ses_i in range(_ses_segs.GetNumberOfItems() - 1, -1, -1):
        _ses_c = _ses_segs.GetItemAsObject(_ses_i)
        if _ses_c is not None:
            _ses_seg = _ses_c
            break
if _ses_seg is not None:
    _ses_widget.setSegmentationNode(_ses_seg)
_ses_vol = None
_ses_vols = slicer.mrmlScene.GetNodesByClass("vtkMRMLScalarVolumeNode")
for _ses_j in range(_ses_vols.GetNumberOfItems() - 1, -1, -1):
    _ses_vc = _ses_vols.GetItemAsObject(_ses_j)
    if _ses_vc is not None and not _ses_vc.IsA("vtkMRMLLabelMapVolumeNode"):
        _ses_vol = _ses_vc
        break
if _ses_vol is not None:
    _ses_widget.setSourceVolumeNode(_ses_vol)
if _ses_seg is not None and _ses_editor_node is not None:
    _ses_segmentation = _ses_seg.GetSegmentation()
    _ses_target = _ses_seg.GetAttribute("SlicerAIAgent.SegmentEditorTargetSegmentID")
    if not _ses_target or _ses_segmentation.GetSegment(_ses_target) is None:
        _ses_target = _ses_segmentation.GetNthSegmentID(0) if _ses_segmentation.GetNumberOfSegments() > 0 else ""
    if _ses_target:
        _ses_editor_node.SetSelectedSegmentID(_ses_target)
        _ses_widget.setCurrentSegmentID(_ses_target)
        _ses_disp = slicer.vtkMRMLSegmentationDisplayNode.SafeDownCast(_ses_seg.GetDisplayNode())
        if _ses_disp is not None:
            _ses_disp.SetVisibility(True)
            _ses_disp.SetVisibility2DFill(True)
            _ses_disp.SetVisibility2DOutline(True)
            _ses_disp.SetSegmentVisibility(_ses_target, True)
if _ses_widget.activeEffect() is None:
    _ses_widget.setActiveEffectByName("Islands")
_opt_label = "Split islands to segments"
_opt_hit = False
import slicer
for _opt_w in slicer.util.findChildren(_ses_widget):
    try:
        _opt_t = _opt_w.text
    except Exception:
        _opt_t = None
    if isinstance(_opt_t, str) and _opt_t.replace("&", "").strip().lower() == _opt_label.strip().lower():
        try:
            _opt_w.click()
            _opt_hit = True
            break
        except Exception:
            pass
if not _opt_hit:
    for _opt_cb in slicer.util.findChildren(_ses_widget, className="QComboBox"):
        _opt_idx = _opt_cb.findText(_opt_label)
        if _opt_idx >= 0:
            _opt_cb.setCurrentIndex(_opt_idx)
            _opt_hit = True
            break
if _opt_hit:
    print("[SegmentEditor] Option 'Split islands to segments' selected.")
else:
    print("[SegmentEditor] Option 'Split islands to segments' not found (effect options may not be shown).")
# --- [end Segment Editor session] ---
