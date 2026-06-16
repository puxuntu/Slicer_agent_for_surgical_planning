# Change layout to BoneReconstructionPlanner

# Activate the BoneReconstructionPlanner custom layout
layoutManager = slicer.app.layoutManager()
layoutManager.setLayout(slicer.BRPLayoutId)

# Verify
currentLayout = layoutManager.layout
if currentLayout != slicer.BRPLayoutId:
    raise RuntimeError("STATE_NOT_APPLIED: layout set to BoneReconstructionPlanner")