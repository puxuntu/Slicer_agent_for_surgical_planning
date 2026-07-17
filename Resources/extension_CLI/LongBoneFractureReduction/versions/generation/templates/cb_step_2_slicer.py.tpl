# --- [Segment Editor session] create or reuse the segmentation ---
# Deterministic + idempotent: reuse an existing segmentation of this name
# (a re-run / correction never duplicates it), else create it, and mark it the
# session segmentation for the add / apply steps.
import slicer
_ses_seg = None
_ses_segs = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
for _ses_i in range(_ses_segs.GetNumberOfItems()):
    _ses_c = _ses_segs.GetItemAsObject(_ses_i)
    if _ses_c is not None and _ses_c.GetName() == "bone_segmentation":
        _ses_seg = _ses_c
        break
if _ses_seg is None:
    _ses_seg = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", "bone_segmentation")
_ses_seg.CreateDefaultDisplayNodes()
_ses_all = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
for _ses_k in range(_ses_all.GetNumberOfItems()):
    _ses_o = _ses_all.GetItemAsObject(_ses_k)
    if _ses_o is not None:
        _ses_o.SetAttribute("SlicerAIAgent.SegmentEditorSession", "0")
_ses_seg.SetAttribute("SlicerAIAgent.SegmentEditorSession", "1")
segmentationNode = _ses_seg
if _ses_seg.GetName() != "bone_segmentation":
    raise RuntimeError("STATE_NOT_APPLIED: segmentation name")
print("[SegmentEditor] Segmentation 'bone_segmentation' ready.")
# --- [end Segment Editor session] ---
