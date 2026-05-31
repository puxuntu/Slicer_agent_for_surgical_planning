import slicer

# Change the layout to the custom "BoneReconstructionPlanner" layout
layoutManager = slicer.app.layoutManager()
# Use the layout name as registered by the module
layoutManager.setLayoutByName("BoneReconstructionPlanner")

print("[BoneReconstructionPlanner] Layout changed back to BoneReconstructionPlanner.")