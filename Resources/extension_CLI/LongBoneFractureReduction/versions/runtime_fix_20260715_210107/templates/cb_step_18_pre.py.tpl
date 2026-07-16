# --- LongBoneFractureReduction: In the 2D view, click to select the moving part. (Setup) ---
import slicer

# In-tool interaction: the active module tool/effect consumes the view
# clicks itself; do NOT create a Markups node or enter placement mode.

# --- [Segment Editor session] prepare the active effect for in-view interaction ---
# The prior steps activated the effect and set its mode; re-bind the
# session segmentation + target so the effect's own slice-view clicks work.
import slicer
_ses_widget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
_ses_widget.setMRMLScene(slicer.mrmlScene)
_ses_editor_node = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentEditorNode")
if _ses_editor_node is not None:
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
if _ses_vol is not None:
    try:
        slicer.util.setSliceViewerLayers(background=_ses_vol, fit=True)
    except Exception:
        pass
# --- [end Segment Editor session] ---

print("[LongBoneFractureReduction] Please Click in the 2D view to select the moving part island.")
print("When finished, press the 'Done' button in the workflow panel.")
