import slicer

# BoneReconstructionPlanner (extension) defines its custom layout in its own source:
#   slicer.BRPLayoutId = 101
# and provides setBRPLayout(), which activates that registered layout via
#   slicer.app.layoutManager().setLayout(slicer.BRPLayoutId)
try:
    import BoneReconstructionPlanner
    BoneReconstructionPlanner.setBRPLayout()
except ImportError:
    # Fallback: activate the extension's layout using its own defined ID constant.
    slicer.app.layoutManager().setLayout(slicer.BRPLayoutId)

# Read back the active layout arrangement and fail loudly if it did not take effect.
layoutNode = slicer.app.layoutManager().layoutLogic().GetLayoutNode()
if layoutNode.GetViewArrangement() != slicer.BRPLayoutId:
    raise RuntimeError("STATE_NOT_APPLIED: layout")