"""
Configure Markups Display settings: Show in both View 1 and Red view.

This script restricts display of a markups node so it is only visible
in the 3D view (View 1) and the Red slice view. All other views (e.g.,
Green, Yellow) will not show the markups.
"""

# -----------------------------------------------------------------------------
# 1. Find the markups node by name (fuzzy match)
# -----------------------------------------------------------------------------
markupsNode = None
markupsName = "{markups_name: F}"  # Replace with your markups node name
for node in slicer.mrmlScene.GetNodesByClass("vtkMRMLMarkupsNode"):
    if markupsName.lower() in node.GetName().lower():
        markupsNode = node
        break

if markupsNode is None:
    raise ValueError("Markups node not found: " + markupsName)

# -----------------------------------------------------------------------------
# 2. Get the display node
# -----------------------------------------------------------------------------
displayNode = markupsNode.GetDisplayNode()
if displayNode is None:
    raise ValueError("Markups node has no display node: " + markupsName)

# -----------------------------------------------------------------------------
# 3. Collect the view node IDs for the target views
# -----------------------------------------------------------------------------
layoutManager = slicer.app.layoutManager()

viewNodeIDs = []

# View 1 (3D view)
threeDWidget = layoutManager.threeDWidget(0)
if threeDWidget:
    viewNodeIDs.append(threeDWidget.mrmlViewNode().GetID())

# Red slice view
sliceWidget = layoutManager.sliceWidget("Red")
if sliceWidget:
    viewNodeIDs.append(sliceWidget.mrmlSliceNode().GetID())

if not viewNodeIDs:
    raise RuntimeError("Could not find target views (View 1 or Red slice view).")

# -----------------------------------------------------------------------------
# 4. Restrict the markups display to only the selected views
# -----------------------------------------------------------------------------
# SetViewNodeIDs replaces the entire view list, hiding the markup from all
# other views. To add views incrementally, use AddViewNodeID() instead.
displayNode.SetViewNodeIDs(viewNodeIDs)

print("Markups '%s' is now displayed only in: %s" % (
    markupsNode.GetName(),
    ", ".join(viewNodeIDs)
))