# --- BoneReconstructionPlanner: 15. Change the layout from "Conventional" back to the custom layout "BoneReconstructionPlanner" (restore the extension's dedicated layout). ---
try:
    from BoneReconstructionPlanner import setBRPLayout
    setBRPLayout()
except ImportError:
    # Fallback: try to set layout by name using module's own logic
    # The extension registers a custom layout; attempt to activate it via the module selector
    slicer.util.selectModule("BoneReconstructionPlanner")
    # The above may not restore the layout directly; if still fails, raise error
    raise RuntimeError("Could not restore custom layout. The setBRPLayout function is missing.")

print("[BoneReconstructionPlanner] Step 'cb_step_15' completed.")