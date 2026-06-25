# Change layout to BoneReconstructionPlanner

lm = slicer.app.layoutManager()

# Activate the custom BRP layout using the extension-defined layout ID constant
lm.setLayout(slicer.BRPLayoutId)

# Read-back verification: layout property returns the current layout ID (int)
if lm.layout != slicer.BRPLayoutId:
    raise RuntimeError("STATE_NOT_APPLIED: BoneReconstructionPlanner layout was not set")