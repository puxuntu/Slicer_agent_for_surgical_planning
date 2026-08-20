# [runtime-fixed] Auto-revised by runtime self-correction at 20260820_112958.
# Pre-revision templates backed up under versions/runtime_fix_20260820_112958/.
# Fixed runtime error: STATE_NOT_APPLIED: 3D view centered on scene
import math

# --- Step 1: compute the scene bounding box in RAS over all displayable nodes ---
# with finite, non-degenerate bounds (visible or not, so the whole content is covered).
bounds = None
for node in slicer.util.getNodesByClass("vtkMRMLDisplayableNode"):
    b = [0.0] * 6
    try:
        node.GetRASBounds(b)
    except Exception:
        continue
    if not all(math.isfinite(v) for v in b):
        continue
    if b[0] > b[3] or b[1] > b[4] or b[2] > b[5]:
        continue  # empty / degenerate bounds
    if bounds is None:
        bounds = [b[0], b[1], b[2], b[3], b[4], b[5]]
    else:
        bounds[0] = min(bounds[0], b[0])
        bounds[1] = min(bounds[1], b[1])
        bounds[2] = min(bounds[2], b[2])
        bounds[3] = max(bounds[3], b[3])
        bounds[4] = max(bounds[4], b[4])
        bounds[5] = max(bounds[5], b[5])

if bounds is None:
    raise RuntimeError("STATE_NOT_APPLIED: 3D view centered on scene (no displayable content)")

center = [(bounds[0] + bounds[3]) / 2.0,
          (bounds[1] + bounds[4]) / 2.0,
          (bounds[2] + bounds[5]) / 2.0]
size = [bounds[3] - bounds[0], bounds[4] - bounds[1], bounds[5] - bounds[2]]
diagonal = math.sqrt(size[0] ** 2 + size[1] ** 2 + size[2] ** 2)
radius = max(diagonal / 2.0, 1.0)
margin = 1.15

# --- Step 2: apply explicit camera centering to every 3D-view camera node ---
for cam in slicer.util.getNodesByClass("vtkMRMLCameraNode"):
    position = [0.0] * 3
    focal = [0.0] * 3
    cam.GetPosition(position)
    cam.GetFocalPoint(focal)
    direction = [position[0] - focal[0], position[1] - focal[1], position[2] - focal[2]]
    originalDistance = math.sqrt(direction[0] ** 2 + direction[1] ** 2 + direction[2] ** 2)
    if originalDistance < 1e-6:
        direction = [0.0, 0.0, 1.0]
    else:
        direction = [direction[0] / originalDistance, direction[1] / originalDistance, direction[2] / originalDistance]

    cam.SetFocalPoint(center)

    if cam.GetParallelProjection():
        # Fit the bounding sphere by adjusting the parallel scale; keep the same
        # camera distance (fall back to a sane value if the camera was degenerate).
        cam.SetParallelScale(margin * radius)
        distance = originalDistance if originalDistance >= 1e-6 else margin * radius * 2.0
    else:
        halfAngle = math.radians(cam.GetViewAngle()) / 2.0
        sinHalf = math.sin(halfAngle)
        distance = (margin * radius) / sinHalf if sinHalf > 0.01 else margin * radius * 2.0

    cam.SetPosition(center[0] + direction[0] * distance,
                    center[1] + direction[1] * distance,
                    center[2] + direction[2] * distance)
    cam.ResetClippingRange()

# --- Step 3: deterministic verification (focal points were just set from `center`) ---
for cam in slicer.util.getNodesByClass("vtkMRMLCameraNode"):
    fp = [0.0] * 3
    cam.GetFocalPoint(fp)
    for axis in range(3):
        if abs(fp[axis] - center[axis]) > 1e-3:
            raise RuntimeError("STATE_NOT_APPLIED: 3D view centered on scene")
