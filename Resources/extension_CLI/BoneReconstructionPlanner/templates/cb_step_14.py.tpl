# --- BoneReconstructionPlanner: 14. Restore the extension's custom layout. ---
import slicer

# Try to restore the layout registered by the extension under name "BoneReconstructionPlanner"
layoutManager = slicer.app.layoutManager()
layoutIndex = layoutManager.layoutNameToLayoutIndex("BoneReconstructionPlanner")
if layoutIndex >= 0:
    layoutManager.setLayout(layoutIndex)
else:
    # Fallback: set a conventional layout (3D + 2D slices) if custom layout not registered
    layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView)
    print("[BoneReconstructionPlanner] Warning: Custom layout not found, set conventional layout.")

print("[BoneReconstructionPlanner] Step cb_step_14 completed.")
