# Center the 3D view(s) on the scene
# (equivalent to the "Center"/"Reset focal view" button of each 3D view controller)
import math
import vtk

# Compute the center of the visible scene content (world/RAS bounds)
sceneBounds = None
for node in slicer.util.getNodesByClass('vtkMRMLDisplayableNode'):
    displayNode = node.GetDisplayNode()
    if displayNode is None or not displayNode.GetVisibility():
        continue
    nodeBounds = [0.0] * 6
    node.GetRASBounds(nodeBounds)
    if sceneBounds is None:
        sceneBounds = [nodeBounds[0], nodeBounds[1], nodeBounds[2], nodeBounds[3], nodeBounds[4], nodeBounds[5]]
    else:
        sceneBounds[0] = min(sceneBounds[0], nodeBounds[0])
        sceneBounds[1] = min(sceneBounds[1], nodeBounds[1])
        sceneBounds[2] = min(sceneBounds[2], nodeBounds[2])
        sceneBounds[3] = max(sceneBounds[3], nodeBounds[3])
        sceneBounds[4] = max(sceneBounds[4], nodeBounds[4])
        sceneBounds[5] = max(sceneBounds[5], nodeBounds[5])

# Reset focal point (center on scene) and camera zoom for all 3D views
slicer.util.resetThreeDViews()

# Read-back: verify each 3D view camera focal point is at the scene center
if sceneBounds is not None:
    minPoint = sceneBounds[0:3]
    maxPoint = sceneBounds[3:6]
    sceneCenter = [(minPoint[i] + maxPoint[i]) / 2.0 for i in range(3)]
    diagonal = math.sqrt(sum((maxPoint[i] - minPoint[i]) ** 2 for i in range(3)))
    tolerance = max(1.0, 0.01 * diagonal)
    layoutManager = slicer.app.layoutManager()
    for viewIndex in range(layoutManager.threeDViewCount):
        cameraNode = layoutManager.threeDWidget(viewIndex).threeDView().cameraNode()
        focalPoint = [0.0, 0.0, 0.0]
        cameraNode.GetFocalPoint(focalPoint)
        distance = math.sqrt(sum((focalPoint[i] - sceneCenter[i]) ** 2 for i in range(3)))
        if distance > tolerance:
            raise RuntimeError("STATE_NOT_APPLIED: 3D view centered on scene")