# Open the Threshold effect in the Segmentation Editor.

# Access the segment editor widget via the loaded module.
segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().editor

# Activate the Threshold effect by its registered name.
segmentEditorWidget.setActiveEffectByName("Threshold")

# Verify the effect was activated.
active = segmentEditorWidget.activeEffect()
if active is None or active.name != "Threshold":
    raise RuntimeError("STATE_NOT_APPLIED: ActiveEffect is not Threshold")