"""Readers for the geometry a saved run leaves behind: legacy VTK, STL, markups.

VTK is used when it is importable (inside Slicer it always is) and a pure-Python
reader backs it up, so the whole analysis runs -- and can be checked -- outside
Slicer against the same files on disk.

Coordinate systems are the trap here, and the resolution is measured rather
than assumed. Everything a flat scene save produces -- the ``.vtk`` models, the
``.mrk.json`` paths -- and the manually planned ``.stl`` rods turn out to agree
with each other on disk, so this module reads every file in its OWN frame and
converts nothing. What it does NOT do is take that on trust: mirroring the paths
onto the wrong side of the head produces plausible-looking numbers rather than
an error, so ``resolve_frame`` proves the agreement against the bone geometry
and raises when it cannot.

Note the plan table (``ZygomaticPlanTable.tsv``) is the exception: its
Entry R/A/S columns ARE in RAS, so they are used only for cross-checking the
stored BIC/side/length by path name, never as geometry.
"""

from __future__ import annotations

import io
import json
import logging
import os
import re
import struct
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


def lps_to_ras(points: np.ndarray) -> np.ndarray:
    """Mirror the first two axes. Its own inverse."""
    points = np.asarray(points, dtype=np.float64)
    if points.size == 0:
        return points
    out = points.copy()
    out[..., 0] *= -1.0
    out[..., 1] *= -1.0
    return out


# ---------------------------------------------------------------------------
# Legacy VTK PolyData
# ---------------------------------------------------------------------------

_VTK_DTYPES = {
    "float": ">f4", "double": ">f8",
    "int": ">i4", "unsigned_int": ">u4",
    "short": ">i2", "unsigned_short": ">u2",
    "char": ">i1", "unsigned_char": ">u1",
    "long": ">i8", "unsigned_long": ">u8",
}


def _read_vtk_points_python(path: str) -> np.ndarray:
    """POINTS of a legacy .vtk PolyData, without VTK.

    Legacy binary VTK is BIG-endian regardless of the writing machine, which is
    the one detail that silently produces garbage coordinates if assumed
    otherwise.
    """
    with open(path, "rb") as handle:
        blob = handle.read()
    match = re.search(rb"^POINTS\s+(\d+)\s+(\w+)\s*\n", blob, re.MULTILINE)
    if not match:
        return np.zeros((0, 3))
    count = int(match.group(1))
    kind = match.group(2).decode("ascii", "replace")
    start = match.end()
    binary = re.search(rb"^BINARY\s*$", blob[:match.start()], re.MULTILINE) is not None
    if binary:
        dtype = _VTK_DTYPES.get(kind, ">f4")
        width = np.dtype(dtype).itemsize
        need = count * 3 * width
        if len(blob) - start < need:
            raise ValueError(f"{path}: truncated POINTS block")
        values = np.frombuffer(blob[start:start + need], dtype=dtype)
        return values.reshape(count, 3).astype(np.float64)
    text = blob[start:].decode("ascii", "replace")
    numbers: List[float] = []
    for token in text.split():
        try:
            numbers.append(float(token))
        except ValueError:
            break                       # first non-number ends the POINTS block
        if len(numbers) >= count * 3:
            break
    return np.asarray(numbers[:count * 3], dtype=np.float64).reshape(-1, 3)


def read_vtk_points(path: str) -> np.ndarray:
    """POINTS of a .vtk PolyData, in RAS (Slicer stores model geometry in RAS)."""
    try:
        import vtk                                          # noqa: PLC0415
        from vtk.util.numpy_support import vtk_to_numpy     # noqa: PLC0415
        reader = vtk.vtkPolyDataReader()
        reader.SetFileName(path)
        reader.Update()
        data = reader.GetOutput()
        if data is not None and data.GetPoints() is not None:
            return np.asarray(
                vtk_to_numpy(data.GetPoints().GetData()), dtype=np.float64)
        return np.zeros((0, 3))
    except ImportError:
        return _read_vtk_points_python(path)


# ---------------------------------------------------------------------------
# STL
# ---------------------------------------------------------------------------

def read_stl_points(path: str) -> np.ndarray:
    """Triangle vertices of a binary or ASCII STL, in FILE coordinates.

    No conversion here: an STL carries no coordinate-system record, so the
    caller decides (see ``detect_stl_convention``).
    """
    with open(path, "rb") as handle:
        header = handle.read(84)
        if len(header) < 84:
            return np.zeros((0, 3))
        count = struct.unpack("<I", header[80:84])[0]
        body = handle.read()
    if count > 0 and len(body) >= count * 50:
        # 50 bytes/triangle: 12 normal + 36 vertices + 2 attribute bytes.
        raw = np.frombuffer(body[:count * 50], dtype=np.uint8).reshape(count, 50)
        verts = raw[:, 12:48].copy().view("<f4").reshape(count * 3, 3)
        return np.asarray(verts, dtype=np.float64)
    points: List[List[float]] = []
    for line in io.open(path, encoding="utf-8", errors="ignore"):
        parts = line.split()
        if len(parts) == 4 and parts[0] == "vertex":
            points.append([float(x) for x in parts[1:]])
    return np.asarray(points, dtype=np.float64) if points else np.zeros((0, 3))


def rod_axis_endpoints(points: np.ndarray, cap_fraction: float = 0.05
                       ) -> Tuple[np.ndarray, np.ndarray]:
    """The two AXIS endpoints of a rod-shaped mesh (an implant cylinder).

    The extreme vertex is on the end-cap RIM, not on the axis -- for a 2 mm
    implant that is a ~2 mm error at each end, which tilts the path and shifts
    the entry point off the bone surface. So each end is the CENTROID of the
    vertices within ``cap_fraction`` of the length from that extreme: the mean
    of a cap's rim is the axis point.
    """
    points = np.asarray(points, dtype=np.float64)
    if points.shape[0] < 2:
        raise ValueError("need at least two points to find an axis")
    centre = points.mean(axis=0)
    centred = points - centre
    # SVD, not eigen-decomposition: same principal axis, better conditioned on
    # the near-degenerate covariance of a long thin rod.
    axis = np.linalg.svd(centred, full_matrices=False)[2][0]
    projection = centred @ axis
    span = float(projection.max() - projection.min())
    if span <= 0:
        raise ValueError("degenerate mesh: no extent along its principal axis")
    band = max(span * float(cap_fraction), 1e-6)
    low = points[projection <= projection.min() + band].mean(axis=0)
    high = points[projection >= projection.max() - band].mean(axis=0)
    return low, high


# ---------------------------------------------------------------------------
# Markups JSON
# ---------------------------------------------------------------------------

def read_markups_points(path: str) -> Tuple[np.ndarray, List[str]]:
    """Control points of a .mrk.json in the FILE's own frame, with their labels.

    Deliberately unconverted: the models saved beside it are in the same frame
    (proven by ``resolve_frame``), and converting one side of a comparison is
    how a mirrored path gets a plausible score instead of an error.
    """
    data = json.load(io.open(path, encoding="utf-8"))
    markups = (data.get("markups") or [{}])[0]
    control = markups.get("controlPoints") or []
    if not control:
        return np.zeros((0, 3)), []
    points = np.asarray([cp["position"] for cp in control], dtype=np.float64)
    labels = [str(cp.get("label", "")) for cp in control]
    return points, labels


def resolve_frame(probe_points: np.ndarray, reference_points: np.ndarray,
                  tolerance_mm: float = 5.0) -> Tuple[np.ndarray, str]:
    """Put ``probe_points`` in the same frame as ``reference_points``.

    Returns ``(converted, how)`` where ``how`` is ``"as-written"`` or
    ``"mirrored"``. The test is physical, not a header: an implant entry point
    lies ON the bone, so the frame in which the probe points sit within
    ``tolerance_mm`` of the reference cloud is the right one.

    Raises when NEITHER frame fits. That is the point of the function -- an
    LPS/RAS mix-up mirrors the paths onto the other side of the head, where they
    still intersect bone and still produce a BIC number, just a meaningless one.
    A loud failure is the only safe outcome.
    """
    reference = np.asarray(reference_points, dtype=np.float64)
    probe = np.asarray(probe_points, dtype=np.float64).reshape(-1, 3)
    if reference.size == 0 or probe.size == 0:
        return probe, "as-written"
    best = None
    for label, converted in (("as-written", probe), ("mirrored", lps_to_ras(probe))):
        worst = max(float(np.linalg.norm(reference - point, axis=1).min())
                    for point in converted)
        if best is None or worst < best[0]:
            best = (worst, label, converted)
    worst, label, converted = best
    if worst > float(tolerance_mm):
        raise ValueError(
            f"cannot place points in the reference frame: closest fit leaves a "
            f"point {worst:.1f} mm from the bone (limit {tolerance_mm} mm). "
            f"Refusing to score a possibly mirrored path.")
    return converted, label


# ---------------------------------------------------------------------------
# scene.mrml -> role -> file
# ---------------------------------------------------------------------------

def scene_role_files(scene_dir: str, role_attribute: str,
                     scene_file: str = "scene.mrml") -> Dict[str, List[str]]:
    """Map ``<role> -> [<file path>, ...]`` for one flat-saved scene.

    A LIST per role, because roles repeat: a four-implant plan has four nodes
    tagged ``implantPath``, and a dict of one would silently keep whichever came
    last. Order follows the scene file, which is creation order.

    Read from ``scene.mrml`` rather than guessed from file names: the node's
    role is an ATTRIBUTE the extension sets, while the file name is the node's
    display name, which Slicer will silently uniquify (``MaxillaRegion_1``) and
    a user can rename. Only the attribute is authoritative.
    """
    import xml.etree.ElementTree as ET      # noqa: PLC0415

    path = os.path.join(scene_dir, scene_file)
    roles: Dict[str, List[str]] = {}
    try:
        root = ET.parse(path).getroot()
    except Exception:
        logger.warning("Could not parse %s", path, exc_info=True)
        return roles

    # Storage nodes hold the file names; models/markups reference them by id.
    storage_files: Dict[str, str] = {}
    for node in root.iter():
        node_id = node.get("id")
        file_name = node.get("fileName")
        if node_id and file_name:
            storage_files[node_id] = file_name

    for node in root.iter():
        attributes = node.get("attributes") or ""
        role = ""
        for entry in attributes.split(";"):
            key, sep, value = entry.partition(":")
            if sep and key.strip() == role_attribute:
                role = value.strip()
                break
        if not role:
            continue
        # `references="display:vtkMRMLModelDisplayNode1;storage:vtkMRMLModelStorageNode1;"`
        # -- the storage node id is what carries the file name. `storageNodeRef`
        # is the older spelling and is accepted too.
        candidates: List[str] = []
        for entry in (node.get("references") or "").split(";"):
            key, sep, value = entry.partition(":")
            if sep and key.strip() == "storage":
                candidates.extend(value.split())
        candidates.extend((node.get("storageNodeRef") or "").split())
        for candidate in candidates:
            file_name = storage_files.get(candidate)
            if file_name:
                roles.setdefault(role, []).append(os.path.join(scene_dir, file_name))
                break
    return roles


def role_file(roles: Dict[str, List[str]], *names: str) -> Optional[str]:
    """First existing file for the first role that has one. "" -> None."""
    for name in names:
        for path in roles.get(name) or []:
            if os.path.isfile(path):
                return path
    return None
