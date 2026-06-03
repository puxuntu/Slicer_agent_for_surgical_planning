# Switch to the Markups module
slicer.util.selectModule("Markups")

# Configure Advanced Display settings for the mandibular curve markups node
# to show in View 1 (3D) and Red (slice) views

# Find the markups node by fuzzy name matching
markupsNode = None
for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsNode"):
    if "mandibular" in node.GetName().lower() or "curve" in node.GetName().lower():
        markupsNode = node
        break

if markupsNode is None:
    raise RuntimeError("Mandibular curve markups node not found. "
                       "Please create or rename a markups node containing 'mandibular' or 'curve' in its name.")

# Ensure display nodes exist
if not markupsNode.GetDisplayNode():
    markupsNode.CreateDefaultDisplayNodes()

displayNode = markupsNode.GetDisplayNode()

# Clear any previous view restrictions (default: shown in all views)
displayNode.RemoveAllViewNodeIDs()

# Add view node IDs to restrict display to View 1 and Red slice only
displayNode.AddViewNodeID("vtkMRMLViewNode1")      # View 1 (3D)
displayNode.AddViewNodeID("vtkMRMLSliceNodeRed")   # Red (2D slice)