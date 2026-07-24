# --- LongBoneFractureReduction: In the 2D view, click to select the moving part. (Done) ---
import slicer

print("[LongBoneFractureReduction] Step 'cb_step_17' in-tool interaction completed.")

# --- [Segment Editor session end] release the active effect ---
# The session never entered the module, so SegmentEditor.exit() never runs;
# an effect left active keeps its cursor on every slice view. Release it.
import slicer
_ses_end = slicer.modules.segmenteditor.widgetRepresentation().self().editor
if _ses_end.activeEffect() is not None:
    _ses_end.setActiveEffect(None)
print("[SegmentEditor] Session finished; active effect released.")
# --- [end Segment Editor session] ---
