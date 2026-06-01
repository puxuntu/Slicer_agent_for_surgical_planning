try:
    _bonereconstructionplanner_logic
except NameError:
    from BoneReconstructionPlanner import BoneReconstructionPlannerLogic
    _bonereconstructionplanner_logic = BoneReconstructionPlannerLogic()

# Find a suitable scalar volume node
volumeNode = None
volumes = slicer.mrmlScene.GetNodesByClass("vtkMRMLScalarVolumeNode")
for i in range(volumes.GetNumberOfItems()):
    n = volumes.GetItemAsObject(i)
    if n.GetName().lower().startswith("ct") or "input" in n.GetName().lower():
        volumeNode = n
        break
if volumeNode is None and volumes.GetNumberOfItems() > 0:
    volumeNode = volumes.GetItemAsObject(0)

if volumeNode is None:
    print("No scalar volume node found in scene. Cannot set background volume.")
else:
    _bonereconstructionplanner_logic.setBackgroundVolumeFromID(volumeNode.GetID())
    print(f"[BoneReconstructionPlanner] Background volume set to: {volumeNode.GetName()}")