#!/usr/bin/env python
"""
Mandible repair: given a resected mandible as STL, generate the missing segment.

Self contained.  This file plus the ``.onnx`` weights are everything needed - it
imports nothing from the project it was developed in.

Usage
-----
    python mandible_repair.py "Resected mandible.stl"
    python mandible_repair.py input.stl -o graft.stl --model mandible_repair.onnx

The only output is one STL of the generated segment, written next to the input
as ``<input>_repaired_segment.stl`` unless ``-o`` says otherwise.  It is in the
same coordinate frame as the input, so loading both into 3D Slicer shows the
graft already seated between the stumps.

Requirements
------------
    pip install numpy scipy scikit-image onnxruntime

(``onnxruntime-gpu`` instead if you want CUDA.  ``vtk`` is used for surface
voxelisation when present, but a built-in fallback covers its absence.)

How it works
------------
1. rasterise the STL into a fine (0.5 mm) world-aligned grid;
2. downsample to the 1 mm grid the network was trained on and window it the way
   training did - a fixed box centred on the bounding box of the defective bone;
3. run the U-Net;
4. map the probability back to the fine grid and clean it against the input bone
   so the graft mates with the stumps instead of overlapping them;
5. mesh, smooth and write the STL.

Coordinate conventions
----------------------
The network works in RAS (x right, y anterior, z superior).  3D Slicer writes
models in RAS, but plenty of tools write LPS, which is the same mandible flipped
front to back.  Feeding a flipped mandible in produces a confident,
plausible-looking graft built for a mandible facing the other way, and nothing
downstream would flag it - so the convention is inferred from the anatomy and
printed.  Override with ``--orientation ras|lps`` if the call is ever wrong.
"""

from __future__ import print_function

import argparse
import os
import struct
import sys
import time

import numpy as np
from scipy import ndimage as nd

# --------------------------------------------------------------------------- #
# Contract with the trained weights.  The spatial shape is read from the model
# where possible; these are the fallbacks and the parts the graph cannot carry.
# --------------------------------------------------------------------------- #
NETWORK_SHAPE = (224, 160, 160)   # voxels, at NETWORK_SPACING
NETWORK_SPACING = 1.0             # mm, isotropic
DEFAULT_MODEL_NAME = "mandible_repair.onnx"

#: A mandibular graft is at most a hemimandible; far past this means the model
#: is not doing what it should, and the run says so rather than failing quietly.
PLAUSIBLE_GRAFT_CM3 = 90.0


# =========================================================================== #
# STL input / output
# =========================================================================== #
def load_stl(path):
    """
    Read a binary or ASCII STL into ``(vertices, faces)``.

    STL stores a triangle soup with no vertex sharing, which is exactly what the
    rasteriser wants, so no welding is done here.
    """
    with open(path, "rb") as handle:
        header = handle.read(84)
        if len(header) < 84:
            raise ValueError("{} is too short to be an STL".format(path))
        triangle_count = struct.unpack("<I", header[80:84])[0]
        rest = handle.read()

    # A binary STL body is exactly 50 bytes per triangle.  Anything else, or a
    # file starting with "solid" that does not match, is ASCII.
    if len(rest) == triangle_count * 50 and triangle_count > 0:
        data = np.frombuffer(rest, dtype=np.uint8).reshape(triangle_count, 50)
        floats = data[:, :48].copy().view("<f4").reshape(triangle_count, 4, 3)
        vertices = floats[:, 1:, :].reshape(-1, 3).astype(np.float64)
    else:
        vertices = _load_ascii_stl(path)

    if len(vertices) == 0:
        raise ValueError("{} contains no triangles".format(path))
    faces = np.arange(len(vertices), dtype=np.int64).reshape(-1, 3)
    return vertices, faces


def _load_ascii_stl(path):
    """Pull the vertex triples out of an ASCII STL."""
    points = []
    with open(path, "r") as handle:
        for line in handle:
            parts = line.split()
            if len(parts) == 4 and parts[0] == "vertex":
                points.append([float(parts[1]), float(parts[2]), float(parts[3])])
    return np.asarray(points, dtype=np.float64).reshape(-1, 3)


def save_stl(vertices, faces, path):
    """Write a binary STL."""
    vertices = np.asarray(vertices, dtype=np.float64)
    triangles = vertices[np.asarray(faces, dtype=np.int64)]        # (F, 3, 3)

    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    lengths = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = normals / np.maximum(lengths, 1e-12)

    count = len(triangles)
    record = np.zeros((count, 50), dtype=np.uint8)
    payload = np.concatenate([normals[:, None, :], triangles], axis=1).astype("<f4")
    record[:, :48] = payload.reshape(count, 12).view(np.uint8).reshape(count, 48)

    with open(path, "wb") as handle:
        handle.write(b"mandible_repair".ljust(80, b"\0"))
        handle.write(struct.pack("<I", count))
        handle.write(record.tobytes())
    return path


def smooth_taubin(vertices, faces, iterations=12, lamb=0.5, mu=-0.53):
    """
    Taubin smoothing: alternating shrink / un-shrink Laplacian passes.

    Plain Laplacian smoothing would pull the surface inwards, and a graft that
    quietly loses half a millimetre all round no longer meets the stumps.
    Taubin's second pass with a negative weight cancels that drift.
    """
    vertices = np.array(vertices, dtype=np.float64, copy=True)
    if iterations <= 0:
        return vertices

    faces = np.asarray(faces, dtype=np.int64)
    # Weld coincident vertices so the triangle soup has real connectivity;
    # without this every vertex is isolated and smoothing does nothing.
    _, unique_index, inverse = np.unique(np.round(vertices, 5), axis=0,
                                         return_index=True, return_inverse=True)
    welded = vertices[unique_index]
    welded_faces = inverse[faces]

    edges = np.concatenate([welded_faces[:, [0, 1]], welded_faces[:, [1, 2]],
                            welded_faces[:, [2, 0]]], axis=0)
    edges = np.concatenate([edges, edges[:, ::-1]], axis=0)
    source, target = edges[:, 0], edges[:, 1]
    degree = np.bincount(source, minlength=len(welded)).astype(np.float64)
    degree[degree == 0] = 1.0

    for step in range(int(iterations) * 2):
        weight = lamb if step % 2 == 0 else mu
        neighbour_sum = np.zeros_like(welded)
        for axis in range(3):
            neighbour_sum[:, axis] = np.bincount(source, weights=welded[target, axis],
                                                 minlength=len(welded))
        welded += weight * (neighbour_sum / degree[:, None] - welded)

    return welded[inverse]


# =========================================================================== #
# Grids, affines and resampling
# =========================================================================== #
def grid_for_bounds(bounds, spacing, margin=10.0):
    """Axis-aligned grid covering ``bounds`` plus a margin; returns (shape, affine)."""
    bounds = np.asarray(bounds, dtype=np.float64)
    spacing = float(spacing)
    lower, upper = bounds[0] - margin, bounds[1] + margin
    shape = np.maximum(np.ceil((upper - lower) / spacing).astype(np.int64) + 1, 2)
    affine = np.eye(4, dtype=np.float64)
    affine[:3, :3] = np.diag([spacing] * 3)
    affine[:3, 3] = lower
    return tuple(int(s) for s in shape), affine


def voxel_to_world(points, affine):
    points = np.atleast_2d(np.asarray(points, dtype=np.float64))
    homogeneous = np.concatenate([points, np.ones((len(points), 1))], axis=1)
    return (homogeneous @ np.asarray(affine, dtype=np.float64).T)[:, :3]


def spacing_from_affine(affine):
    return np.linalg.norm(np.asarray(affine, dtype=np.float64)[:3, :3], axis=0)


def find_boundaries(volume):
    """Bounding box of the foreground as (b0, e0, b1, e1, b2, e2), end exclusive."""
    volume = np.asarray(volume) > 0
    if not volume.any():
        raise ValueError("empty volume")
    box = []
    for axis in range(3):
        other = tuple(a for a in range(3) if a != axis)
        indices = np.where(np.any(volume, axis=other))[0]
        box.extend((int(indices[0]), int(indices[-1]) + 1))
    return tuple(box)


def resample_to_shape(volume, new_shape, order=0):
    """
    Resample onto a new grid size using the pixel-area convention
    ``in = (out + 0.5) * scale - 0.5``.

    Written out rather than using ``scipy.ndimage.zoom`` because zoom's edge
    convention changed between scipy versions, and the exact mapping is what
    keeps the affine bookkeeping - and so the STL alignment - truthful.
    """
    volume = np.asarray(volume)
    new_shape = tuple(int(s) for s in new_shape)
    if volume.shape == new_shape:
        return volume
    scale = np.asarray(volume.shape, dtype=np.float64) / np.asarray(new_shape, dtype=np.float64)
    axes = [(np.arange(new_shape[a], dtype=np.float32) + 0.5) * scale[a] - 0.5 for a in range(3)]
    coordinates = np.meshgrid(*axes, indexing="ij")
    is_bool = volume.dtype == np.bool_
    source = volume.astype(np.float32) if (is_bool or volume.dtype == np.uint8) else volume
    resampled = nd.map_coordinates(source, coordinates, order=order, mode="nearest")
    return resampled > 0.5 if is_bool else resampled


def resample_between_grids(volume, source_affine, target_affine, target_shape, order=0):
    """Resample from one voxel grid onto another, matching world position."""
    volume = np.asarray(volume)
    transform = np.linalg.inv(np.asarray(source_affine, dtype=np.float64)) @ \
        np.asarray(target_affine, dtype=np.float64)
    axes = [np.arange(target_shape[a], dtype=np.float32) for a in range(3)]
    grid = np.meshgrid(*axes, indexing="ij")
    coordinates = [transform[a, 0] * grid[0] + transform[a, 1] * grid[1] +
                   transform[a, 2] * grid[2] + transform[a, 3] for a in range(3)]
    is_bool = volume.dtype == np.bool_
    source = volume.astype(np.float32) if (is_bool or volume.dtype == np.uint8) else volume
    resampled = nd.map_coordinates(source, coordinates, order=order, mode="constant", cval=0.0)
    return resampled > 0.5 if is_bool else resampled


def crop_or_pad(volume, output_shape, centre):
    """Extract a window of ``output_shape`` centred on ``centre``, zero padding outside."""
    volume = np.asarray(volume)
    output_shape = tuple(int(s) for s in output_shape)
    slices_in, slices_out = [], []
    for axis in range(3):
        begin = int(round(centre[axis] - output_shape[axis] / 2.0))
        end = begin + output_shape[axis]
        in_begin, in_end = max(begin, 0), min(end, volume.shape[axis])
        slices_in.append(slice(in_begin, in_end))
        slices_out.append(slice(in_begin - begin, in_end - begin))
    output = np.zeros(output_shape, dtype=volume.dtype)
    output[tuple(slices_out)] = volume[tuple(slices_in)]
    return output


def marching_cubes(volume, level=0.5, step_size=1):
    """Version-tolerant wrapper: scikit-image renamed the Lewiner variant in 0.19."""
    from skimage import measure
    if hasattr(measure, "marching_cubes"):
        result = measure.marching_cubes(volume, level=level, step_size=step_size)
    else:
        result = measure.marching_cubes_lewiner(volume, level=level, step_size=step_size)
    return result[0], result[1]


# =========================================================================== #
# Mesh -> voxels
# =========================================================================== #
def _voxelize_vtk(vertices, faces, shape, affine):
    """Solid voxelisation with VTK's polydata stencil; handles multi-part meshes."""
    import vtk
    from vtk.util import numpy_support

    points = vtk.vtkPoints()
    points.SetData(numpy_support.numpy_to_vtk(np.ascontiguousarray(vertices, dtype=np.float64),
                                              deep=1))
    faces = np.asarray(faces, dtype=np.int64)
    connectivity = np.concatenate(
        [np.full((len(faces), 1), 3, dtype=np.int64), faces], axis=1).ravel()
    cells = vtk.vtkCellArray()
    cells.SetCells(len(faces), numpy_support.numpy_to_vtkIdTypeArray(
        np.ascontiguousarray(connectivity), deep=1))

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetPolys(cells)

    spacing = [float(s) for s in np.diag(affine)[:3]]
    origin = [float(o) for o in affine[:3, 3]]

    image = vtk.vtkImageData()
    image.SetSpacing(*spacing)
    image.SetOrigin(*origin)
    image.SetExtent(0, int(shape[0]) - 1, 0, int(shape[1]) - 1, 0, int(shape[2]) - 1)
    image.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
    image.GetPointData().GetScalars().Fill(1)

    stencil = vtk.vtkPolyDataToImageStencil()
    stencil.SetInputData(polydata)
    stencil.SetOutputOrigin(*origin)
    stencil.SetOutputSpacing(*spacing)
    stencil.SetOutputWholeExtent(image.GetExtent())
    stencil.SetTolerance(0.0)
    stencil.Update()

    painter = vtk.vtkImageStencil()
    painter.SetInputData(image)
    painter.SetStencilConnection(stencil.GetOutputPort())
    painter.ReverseStencilOff()
    painter.SetBackgroundValue(0)
    painter.Update()

    flat = numpy_support.vtk_to_numpy(painter.GetOutput().GetPointData().GetScalars())
    # VTK stores x fastest; this file stores x on axis 0.
    return np.ascontiguousarray(
        flat.reshape(int(shape[2]), int(shape[1]), int(shape[0])).transpose(2, 1, 0)) > 0


def _voxelize_fallback(vertices, faces, shape, affine):
    """
    Solid voxelisation without VTK, by ray parity at voxel centres.

    For every grid line parallel to axis 0 the triangles it passes through are
    collected, their crossings sorted, and the spans between successive pairs
    filled.  That tests the same thing VTK's stencil does - is this voxel centre
    inside the surface - so the two agree to within rounding.

    The obvious alternative, rasterising the shell and flood filling around it,
    is simpler but wrong by half a voxel everywhere: it keeps the whole shell,
    including the half of it that lies outside the surface, which inflates a
    mandible by about 9%.

    Rays are offset by a sub-voxel epsilon so they cannot pass exactly through a
    shared edge or vertex, where a crossing would otherwise be counted twice or
    not at all.
    """
    spacing = float(np.diag(affine)[0])
    origin = np.asarray(affine, dtype=np.float64)[:3, 3]
    triangles = np.asarray(vertices, dtype=np.float64)[np.asarray(faces, dtype=np.int64)]
    _, ny, nz = (int(s) for s in shape)

    epsilon = spacing * 1e-3
    y_origin, z_origin = origin[1] + epsilon, origin[2] + epsilon * 0.5

    x, y, z = triangles[:, :, 0], triangles[:, :, 1], triangles[:, :, 2]
    j_low = np.clip(np.ceil((y.min(axis=1) - y_origin) / spacing), 0, ny - 1).astype(np.int64)
    j_high = np.clip(np.floor((y.max(axis=1) - y_origin) / spacing), 0, ny - 1).astype(np.int64)
    k_low = np.clip(np.ceil((z.min(axis=1) - z_origin) / spacing), 0, nz - 1).astype(np.int64)
    k_high = np.clip(np.floor((z.max(axis=1) - z_origin) / spacing), 0, nz - 1).astype(np.int64)

    # Barycentric coordinates of the ray positions, in the projection onto (y, z).
    determinant = ((z[:, 1] - z[:, 2]) * (y[:, 0] - y[:, 2]) +
                   (y[:, 2] - y[:, 1]) * (z[:, 0] - z[:, 2]))

    rays, crossings = [], []
    for index in range(len(triangles)):
        if j_low[index] > j_high[index] or k_low[index] > k_high[index]:
            continue
        det = determinant[index]
        if det == 0.0:
            continue  # degenerate triangle, contributes no crossing
        js = np.arange(j_low[index], j_high[index] + 1)
        ks = np.arange(k_low[index], k_high[index] + 1)
        gy = (y_origin + js * spacing)[:, None]
        gz = (z_origin + ks * spacing)[None, :]

        y0, y1, y2 = y[index]
        z0, z1, z2 = z[index]
        b0 = ((z1 - z2) * (gy - y2) + (y2 - y1) * (gz - z2)) / det
        b1 = ((z2 - z0) * (gy - y2) + (y0 - y2) * (gz - z2)) / det
        b2 = 1.0 - b0 - b1
        inside = (b0 >= 0.0) & (b1 >= 0.0) & (b2 >= 0.0)
        if not inside.any():
            continue

        hit_x = b0 * x[index, 0] + b1 * x[index, 1] + b2 * x[index, 2]
        gj, gk = np.meshgrid(js, ks, indexing="ij")
        rays.append(gj[inside] * nz + gk[inside])
        crossings.append(hit_x[inside])

    volume = np.zeros(tuple(shape), dtype=bool)
    if not rays:
        return volume

    ray = np.concatenate(rays)
    hit = (np.concatenate(crossings) - origin[0]) / spacing   # fractional index on axis 0
    order = np.lexsort((hit, ray))
    ray, hit = ray[order], hit[order]

    boundaries = np.flatnonzero(np.concatenate([[True], ray[1:] != ray[:-1]]))
    ends = np.concatenate([boundaries[1:], [len(ray)]])
    for begin, end in zip(boundaries, ends):
        if (end - begin) % 2:
            continue  # odd crossing count: the ray grazed the surface, skip it
        j, k = divmod(int(ray[begin]), nz)
        for pair in range(begin, end, 2):
            low = int(np.ceil(hit[pair]))
            high = int(np.floor(hit[pair + 1]))
            if high >= low:
                volume[max(low, 0):high + 1, j, k] = True
    return volume


def voxelize_mesh(vertices, faces, spacing=0.5, margin=12.0, prefer_vtk=True):
    """Rasterise a surface into a binary volume on a world-aligned grid."""
    shape, affine = grid_for_bounds(
        np.array([np.min(vertices, axis=0), np.max(vertices, axis=0)]), spacing, margin)
    if prefer_vtk:
        try:
            return _voxelize_vtk(vertices, faces, shape, affine), affine
        except Exception:  # noqa: BLE001 - fall back rather than fail the run
            pass
    return _voxelize_fallback(vertices, faces, shape, affine), affine


def volume_to_mesh(volume, affine, level=0.5, smoothing=12, step_size=1):
    """Marching cubes on a volume, with vertices returned in world millimetres."""
    volume = np.asarray(volume, dtype=np.float32)
    if not (volume > level).any():
        raise ValueError("nothing to mesh")
    padded = np.pad(volume, 1, mode="constant", constant_values=0.0)
    vertices, faces = marching_cubes(padded, level=level, step_size=step_size)
    vertices = voxel_to_world(vertices - 1.0, affine)
    if smoothing:
        vertices = smooth_taubin(vertices, faces, iterations=smoothing)
    return vertices, faces


def keep_large_components(volume, min_fraction=0.02, min_voxels=200):
    """
    Drop rasterisation speckle while keeping every real fragment.

    This must not reduce to a single component: a resected mandible legitimately
    arrives as two separate stumps.
    """
    volume = np.asarray(volume) > 0
    if not volume.any():
        return volume
    labels, count = nd.label(volume, structure=nd.generate_binary_structure(3, 3))
    if count <= 1:
        return volume
    sizes = np.bincount(labels.ravel())
    sizes[0] = 0
    keep = np.where(sizes >= max(min_fraction * sizes.max(), min_voxels))[0]
    return np.isin(labels, keep)


# =========================================================================== #
# Orientation
# =========================================================================== #
def flip_lps_ras(vertices):
    """Convert between LPS and RAS; the transform is its own inverse."""
    vertices = np.array(vertices, dtype=np.float64, copy=True)
    vertices[:, 0] *= -1.0
    vertices[:, 1] *= -1.0
    return vertices


def posterior_superior_margin(volume):
    """
    Signed score that tells RAS from LPS.

    The condyles and coronoids are the topmost part of a mandible and they sit
    *posterior* to the bulk of the bone, so in RAS the mean y of the top of the
    bone is below the mean y of all of it.  The score is that difference over the
    anterior-posterior extent: positive for RAS, negative when front and back are
    swapped.  It runs +0.13..+0.29 on intact mandibles and +0.00..+0.35 on
    resected ones, so the sign is a reliable discriminator and the magnitude says
    how confident the call is.
    """
    coordinates = np.argwhere(np.asarray(volume) > 0).astype(np.float64)
    if len(coordinates) == 0:
        return 0.0
    superior = coordinates[coordinates[:, 2] >= np.percentile(coordinates[:, 2], 85)]
    extent = coordinates[:, 1].max() - coordinates[:, 1].min()
    return float((coordinates[:, 1].mean() - superior[:, 1].mean()) / max(extent, 1e-6))


def detect_orientation(vertices, faces, spacing=1.5):
    """Return ('ras'|'lps', score); |score| < 0.05 means the call is not trustworthy."""
    volume, _ = voxelize_mesh(vertices, faces, spacing=spacing, margin=8.0)
    score = posterior_superior_margin(keep_large_components(volume))
    return ("ras" if score >= 0 else "lps"), score


# =========================================================================== #
# The network
# =========================================================================== #
class Predictor(object):
    """Runs the reconstruction U-Net through ONNX Runtime."""

    def __init__(self, model_path, device="cpu"):
        import onnxruntime

        available = onnxruntime.get_available_providers()
        providers = (["CUDAExecutionProvider", "CPUExecutionProvider"]
                     if device == "cuda" and "CUDAExecutionProvider" in available
                     else ["CPUExecutionProvider"])
        self.session = onnxruntime.InferenceSession(str(model_path), providers=providers)
        self.input_name = self.session.get_inputs()[0].name

        # The graph carries its spatial shape; the batch axis is dynamic.
        shape = self.session.get_inputs()[0].shape
        spatial = shape[2:] if len(shape) == 5 else []
        self.network_shape = (tuple(int(s) for s in spatial)
                              if len(spatial) == 3 and all(isinstance(s, int) for s in spatial)
                              else NETWORK_SHAPE)
        self.spacing = NETWORK_SPACING

    def __call__(self, window):
        batch = np.ascontiguousarray(window, dtype=np.float32)[None, None]
        return self.session.run(None, {self.input_name: batch})[0][0, 0]


def window_centre(defective):
    """The window is centred on the bounding box of the defective bone."""
    box = find_boundaries(defective)
    return np.array([(box[0] + box[1]) / 2.0, (box[2] + box[3]) / 2.0, (box[4] + box[5]) / 2.0])


def window_affine(affine, centre, shape):
    """Voxel->world affine of the extracted window."""
    begin = np.array([int(round(centre[a] - shape[a] / 2.0)) for a in range(3)], dtype=np.float64)
    transform = np.eye(4, dtype=np.float64)
    transform[:3, 3] = begin
    return np.asarray(affine, dtype=np.float64) @ transform


def prepare_input(fine, fine_affine, network_shape, spacing):
    """
    Fine grid -> the exact window the network was trained on.

    Training framed on the defective mandible's bounding box because that is all
    inference ever has; the window is deliberately wider than a mandible so a
    hemimandibulectomy's graft still fits inside it.
    """
    coarse = resample_to_shape(
        fine,
        np.maximum(np.round(np.asarray(fine.shape) * spacing_from_affine(fine_affine) / spacing),
                   1).astype(np.int64),
        order=0)
    if not coarse.any():
        raise ValueError("the rasterised mandible is empty at {} mm".format(spacing))

    scale = np.asarray(fine.shape, dtype=np.float64) / np.asarray(coarse.shape, dtype=np.float64)
    transform = np.eye(4, dtype=np.float64)
    transform[:3, :3] = np.diag(scale)
    transform[:3, 3] = 0.5 * scale - 0.5
    coarse_affine = np.asarray(fine_affine, dtype=np.float64) @ transform

    centre = window_centre(coarse)
    return crop_or_pad(coarse, network_shape, centre), window_affine(coarse_affine, centre,
                                                                     network_shape)


# =========================================================================== #
# Post-processing
# =========================================================================== #
def clean_prediction(probability, defective, threshold=0.5, min_component_fraction=0.15):
    """
    Turn the raw probability into a graft that actually fits the defect.

    The graft is closed together with the remaining bone, which straightens the
    osteotomy faces so the specimen seats flat; anything overlapping the retained
    mandible is then removed, because a graft may touch the stumps but never
    intersect them; and only the main component survives, since a fibula
    reconstruction is one piece of bone, not a scatter of fragments.
    """
    binary = np.asarray(probability) > threshold
    if not binary.any():
        return binary

    complete = nd.binary_closing(np.logical_or(binary, defective),
                                 structure=nd.generate_binary_structure(3, 1))
    graft = np.logical_and(complete, np.logical_not(defective))

    labels, count = nd.label(graft, structure=nd.generate_binary_structure(3, 3))
    if count > 1:
        sizes = np.bincount(labels.ravel())
        sizes[0] = 0
        keep = np.where(sizes >= min_component_fraction * sizes.max())[0]
        graft = np.isin(labels, keep)
    return graft


def capped_grid(bounds, spacing, margin, max_voxels=12e6, label="output", echo=True):
    """
    Build a fine grid over ``bounds``, coarsening it if it would be too large.

    A safety valve rather than a normal path: a real graft is a few million
    voxels at 0.5 mm, while a mismatched model can predict a region covering the
    whole field of view and exhaust memory before producing anything useful.
    """
    shape, affine = grid_for_bounds(bounds, spacing, margin=margin)
    voxels = float(np.prod(shape))
    if voxels > max_voxels:
        coarser = spacing * (voxels / max_voxels) ** (1.0 / 3.0)
        if echo:
            print("  note: the {} grid would be {:.0f}M voxels at {} mm; using {:.2f} mm".format(
                label, voxels / 1e6, spacing, coarser))
        shape, affine = grid_for_bounds(bounds, coarser, margin=margin)
    return shape, affine


# =========================================================================== #
# End to end
# =========================================================================== #
def repair(input_path, model_path, output_path=None, fine_spacing=0.5, margin=12.0,
           threshold=0.5, smoothing=12, orientation="auto", device="cpu", echo=True):
    """Generate the missing mandible segment; returns the path of the written STL."""
    def report(message):
        if echo:
            print(message)

    start = time.time()
    report("Loading {}".format(input_path))
    vertices, faces = load_stl(input_path)
    report("  {:,} triangles, bounds {} .. {} mm".format(
        len(faces), np.round(vertices.min(axis=0), 1), np.round(vertices.max(axis=0), 1)))

    detected, score = detect_orientation(vertices, faces)
    if orientation == "auto":
        orientation = detected
        report("  orientation: {} (anatomical score {:+.3f})".format(orientation.upper(), score))
        if abs(score) < 0.05:
            report("  WARNING: that call is not confident. Check the result, and re-run with "
                   "--orientation ras|lps if the graft faces the wrong way.")
    elif orientation != detected:
        report("  orientation: {} as requested, but the anatomy looks like {} ({:+.3f})".format(
            orientation.upper(), detected.upper(), score))
    else:
        report("  orientation: {} (anatomical score {:+.3f})".format(orientation.upper(), score))

    flipped = orientation == "lps"
    if flipped:
        vertices = flip_lps_ras(vertices)

    report("Rasterising at {} mm".format(fine_spacing))
    fine, fine_affine = voxelize_mesh(vertices, faces, spacing=fine_spacing, margin=margin)
    fine = keep_large_components(fine)
    pieces = nd.label(fine, structure=nd.generate_binary_structure(3, 3))[1]
    report("  {:.1f} cm3 of bone in {} piece(s)".format(
        fine.sum() * fine_spacing ** 3 / 1000.0, pieces))

    predictor = Predictor(model_path, device=device)
    window, window_matrix = prepare_input(fine, fine_affine, predictor.network_shape,
                                          predictor.spacing)
    report("Running the network on a {} window".format(window.shape))
    inference_start = time.time()
    probability = predictor(window)
    report("  done in {:.1f} s".format(time.time() - inference_start))

    # Move the probability onto a fine grid around the graft, bringing the input
    # bone along, so the result is cleaned at full resolution rather than at 1 mm.
    rough = probability > threshold
    if not rough.any():
        raise RuntimeError("the network predicted an empty graft; check the model and input")
    box = find_boundaries(rough)
    corners = voxel_to_world(np.array([[box[0], box[2], box[4]],
                                       [box[1] - 1, box[3] - 1, box[5] - 1]], dtype=np.float64),
                             window_matrix)
    output_shape, output_affine = capped_grid(
        np.array([corners.min(axis=0), corners.max(axis=0)]), fine_spacing, 8.0,
        label="graft", echo=echo)

    fine_probability = resample_between_grids(probability, window_matrix, output_affine,
                                              output_shape, order=1)
    fine_bone = resample_between_grids(fine, fine_affine, output_affine, output_shape, order=0)
    graft = clean_prediction(fine_probability, fine_bone, threshold=threshold)
    if not graft.any():
        raise RuntimeError("the graft vanished during post-processing; try a lower --threshold")

    output_spacing = float(spacing_from_affine(output_affine)[0])
    volume_cm3 = float(graft.sum()) * output_spacing ** 3 / 1000.0
    report("  graft volume {:.1f} cm3".format(volume_cm3))
    if volume_cm3 > PLAUSIBLE_GRAFT_CM3:
        report("  WARNING: {:.0f} cm3 is larger than any mandibular graft; the model is "
               "probably not matched to this input.".format(volume_cm3))

    report("Meshing")
    # A blur before marching cubes puts the iso-surface between voxels rather
    # than on the staircase, so the graft does not come out visibly voxelised.
    field = nd.gaussian_filter(graft.astype(np.float32), sigma=0.8)
    step = max(int(round((float(graft.sum()) / 1e6) ** (1.0 / 3.0))), 1)
    graft_vertices, graft_faces = volume_to_mesh(field, output_affine, level=0.5,
                                                 smoothing=smoothing, step_size=step)
    if flipped:
        graft_vertices = flip_lps_ras(graft_vertices)

    if output_path is None:
        stem = os.path.splitext(str(input_path))[0]
        output_path = "{}_repaired_segment.stl".format(stem)
    save_stl(graft_vertices, graft_faces, output_path)
    report("  wrote {} ({:,} triangles)".format(output_path, len(graft_faces)))
    report("Finished in {:.1f} s".format(time.time() - start))
    return output_path


def find_default_model(explicit=None):
    """The model given on the command line, or a single .onnx next to this file."""
    if explicit:
        return explicit
    here = os.path.dirname(os.path.abspath(__file__))
    preferred = os.path.join(here, DEFAULT_MODEL_NAME)
    if os.path.exists(preferred):
        return preferred
    candidates = sorted(f for f in os.listdir(here) if f.lower().endswith(".onnx"))
    return os.path.join(here, candidates[0]) if candidates else None


def main(arguments=None):
    parser = argparse.ArgumentParser(
        description="Generate the missing segment of a resected mandible from an STL.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("input", help="STL of the resected mandible")
    parser.add_argument("-o", "--output", default=None,
                        help="output STL (default: <input>_repaired_segment.stl)")
    parser.add_argument("-m", "--model", default=None,
                        help="ONNX weights (default: {} next to this script)".format(
                            DEFAULT_MODEL_NAME))
    parser.add_argument("--orientation", default="auto", choices=["auto", "ras", "lps"],
                        help="coordinate convention of the input; 'auto' infers it from the anatomy")
    parser.add_argument("--fine-spacing", type=float, default=0.5,
                        help="rasterisation spacing in mm; drives output surface quality")
    parser.add_argument("--threshold", type=float, default=0.5, help="probability threshold")
    parser.add_argument("--smoothing", type=int, default=12,
                        help="Taubin smoothing iterations, 0 to disable")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    parser.add_argument("-q", "--quiet", action="store_true")
    options = parser.parse_args(arguments)

    if not os.path.exists(options.input):
        print("Input not found: {}".format(options.input))
        return 1

    model_path = find_default_model(options.model)
    if not model_path or not os.path.exists(model_path):
        print("ONNX model not found. Put {} next to this script, or pass --model.".format(
            DEFAULT_MODEL_NAME))
        return 1

    try:
        repair(options.input, model_path, output_path=options.output,
               fine_spacing=options.fine_spacing, threshold=options.threshold,
               smoothing=options.smoothing, orientation=options.orientation,
               device=options.device, echo=not options.quiet)
    except Exception as error:  # noqa: BLE001 - a CLI should not show a traceback
        print("Failed: {}".format(error))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
