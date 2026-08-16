"""OrbitalFractureReconstruction: surface error against the surgeon's ground truth.

Two questions per case, both answered against the same ground truth
(``Dataset/<subject>/<subject>_Label.nii.gz``, the correct orbital volume on the
fractured side):

* how far is the pipeline's **reconstruction** from it -- did the procedure work;
* how far is the **fractured** orbit from it -- how much was there to correct.

The second is not padding: a surface error means nothing without the error it
started from. A 0.8 mm reconstruction error is excellent on an orbit that was
4 mm out and unremarkable on one that was 1 mm out, so both are computed the same
way, on the same surfaces, and reported side by side with their ratio.

UNLIKE ``zygomatic.py`` this module needs Slicer. Reading a ``.seg.nrrd`` and a
``.nii.gz``, meshing them identically, and writing a scene a surgeon can open are
all Slicer's own machinery, and reimplementing any of it would be reimplementing
it *differently* -- which for the meshing step would silently bias every number
here. Everything that does NOT need Slicer is kept out of the functions that do
(``slicer``/``vtk`` are imported lazily inside them), so the statistics, the
improvement pairing, case discovery, the MRML splicer and the write-verification
are all checkable by ``scripts/check_orbital_analysis.py``.

WHAT IS AND IS NOT COMPARED
---------------------------
Everything is done on surfaces in RAS world coordinates, so the ground truth
being stored on the full CT grid (512x512x135) and the run's segmentations on the
cropped one (320x160x64) needs no resampling: both resolve to the same anatomy in
world space, and ``_frame_gap_mm`` proves that per case rather than assuming it.

The three surfaces are meshed through ONE pipeline with ONE smoothing factor, for
the same reason: a distance between two surfaces built by different rules
measures the rules.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import xml.etree.ElementTree as ElementTree
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from .run_timing import collect_timing, discover_cases as _discover_cases, timing_sheet

logger = logging.getLogger(__name__)

EXTENSION_NAME = "OrbitalFractureReconstruction"

#: All paths are relative to the repository root so the tree can be moved.
EXPERIMENT_DIR = os.path.join("Experiments", EXTENSION_NAME)
RUNS_SUBDIR = "Overall_Performance"
DATASET_SUBDIR = "Dataset"
WORKBOOK_NAME = "OrbitalFractureReconstruction_summary.xlsx"

#: What the run leaves in ``Statistic/scene/``. Addressed by file name rather
#: than by a node attribute because these names are fixed by the procedure's own
#: templates, and a file that is missing is a case worth naming in the log.
RECONSTRUCTED_FILE = "OFR_Reconstructed_Seg.seg.nrrd"
FRACTURED_FILE = "OFR_Fractured_Seg.seg.nrrd"

#: The surgeon's ground truth, in ``Dataset/<subject>/``.
GROUND_TRUTH_TEMPLATE = "{subject}_Label.nii.gz"

#: (key, file, label) -- the two comparisons, in report order.
COMPARISONS: Sequence[Tuple[str, str, str]] = (
    ("reconstructed", RECONSTRUCTED_FILE, "Reconstructed"),
    ("fractured", FRACTURED_FILE, "Fractured"),
)

#: Applied identically to all three surfaces. Slicer's own default, so the mesh
#: scored here is the mesh the surgeon saw in the 3D view -- and, more
#: importantly, the SAME rule on each, so the distance measures the shapes.
SURFACE_SMOOTHING = 0.5

#: Colour-map range, in mm. Fixed rather than per-case so two cases can be
#: compared by eye; errors above it clamp to the top colour, which is the honest
#: rendering of "off the scale" and is why the workbook carries the real maxima.
COLOR_MAX_MM = 3.0
COLOR_TABLE_NAME = "OFR_SurfaceError_0_%dmm" % int(COLOR_MAX_MM)
#: green -> yellow -> orange -> red, at 0, 1/3, 2/3, 1 of the range.
COLOR_STOPS = ((0.0, (0.10, 0.65, 0.20)), (1 / 3.0, (0.95, 0.95, 0.15)),
               (2 / 3.0, (1.00, 0.55, 0.00)), (1.0, (0.75, 0.05, 0.05)))
COLOR_TABLE_SIZE = 256

#: Point-data array carrying the per-vertex distance, in mm.
DISTANCE_ARRAY = "SurfaceErrorMM"

#: Written into each case's ``Statistic/scene/``.
ERROR_SCENE_NAME = "ErrorMaps.mrml"
SCENE_FILE = "scene.mrml"
SCENE_BACKUP = "scene.mrml.orig"

#: Marker inside every MRML id this module splices into a run's own scene.mrml.
#: It is how a re-run finds and replaces its previous output instead of adding a
#: second copy, so it must never collide with a Slicer-generated id -- those are
#: always ``vtkMRML<Class>Node<digits>``.
ID_MARKER = "OFRErr"

#: How far the two surfaces' centroids may sit apart before the case is reported
#: as a frame mismatch rather than scored. A fractured orbit and its ground truth
#: are the same anatomy, so the real gap is a few mm; a coordinate-system
#: mix-up (LPS read as RAS) mirrors one to the other side of the head, which is
#: tens of mm. Between those two scales there is nothing to confuse.
FRAME_TOLERANCE_MM = 25.0


# ---------------------------------------------------------------------------
# Statistics -- pure numpy, so this part is checkable outside Slicer
# ---------------------------------------------------------------------------

def distance_statistics(gt_to_other: np.ndarray,
                        other_to_gt: np.ndarray) -> Dict[str, Any]:
    """Symmetric surface-distance summary, in mm.

    Both directions are needed and neither is sufficient. A reconstruction that
    covers the ground truth completely but spills far beyond it scores ~0 in the
    ground-truth->other direction and badly in the other; a reconstruction that
    sits entirely inside scores the reverse. Only the symmetric figures (ASSD,
    RMS, the Hausdorff percentiles) are safe to quote on their own, which is why
    they lead and the one-way means follow as diagnostics.

    ``hd95`` rather than the plain maximum is the headline outlier figure: a
    single stray vertex, which marching cubes can always produce at the edge of
    a labelmap, moves the maximum and not the 95th percentile.
    """
    gt_to_other = np.asarray(gt_to_other, dtype=float).ravel()
    other_to_gt = np.asarray(other_to_gt, dtype=float).ravel()
    both = np.concatenate([gt_to_other, other_to_gt]) if (
        gt_to_other.size and other_to_gt.size) else (
        gt_to_other if gt_to_other.size else other_to_gt)
    if both.size == 0:
        return {}
    return {
        # Average symmetric surface distance, in its standard form: the two
        # directions POOLED and averaged, i.e.
        # (sum d(a,B) + sum d(b,A)) / (|A| + |B|). Note what pooling means --
        # each surface contributes in proportion to its vertex count, so the
        # denser one carries more weight. Averaging the two directional means
        # instead would weight the directions equally; that is a different
        # (also defensible) statistic, and not the one reported here.
        "assd_mm": _round(float(both.mean())),
        "rms_mm": _round(float(np.sqrt(np.mean(both ** 2)))),
        "median_mm": _round(float(np.median(both))),
        "hd95_mm": _round(float(np.percentile(both, 95))),
        "hd_max_mm": _round(float(both.max())),
        "mean_gt_to_other_mm": _round(float(gt_to_other.mean())) if gt_to_other.size else None,
        "mean_other_to_gt_mm": _round(float(other_to_gt.mean())) if other_to_gt.size else None,
        # Share of the ground-truth surface within a voxel-ish tolerance: the
        # number a surgeon reads as "how much of the wall is right".
        "within_1mm_pct": _round(_share_below(gt_to_other, 1.0) * 100.0, 2),
        "within_2mm_pct": _round(_share_below(gt_to_other, 2.0) * 100.0, 2),
        "gt_points": int(gt_to_other.size),
        "other_points": int(other_to_gt.size),
    }


# ---------------------------------------------------------------------------
# Cropping the ground truth before it is meshed
#
# The ground truth arrives on the FULL CT grid while the labelled orbit occupies
# a corner of it: across this data set the volume handed to marching cubes is
# 31x to 142x larger than the region that produces any surface at all. That is
# pure waste on every case, and on the one case big enough it is fatal -- 068's
# label is 512x512x419 (110 M voxels, 3x the median), and a batch that had
# processed seventeen cases at 2.3 s each spent 12 s inside it and then died
# with an access violation in vtkCommon, which is what a failed allocation
# looks like once the null it returned is dereferenced.
#
# Cropping is exact, not an approximation: a binary label's surface depends only
# on the labelled voxels and one voxel of background around them, so a margin of
# two changes no vertex. The maths below is pure so it can be checked outside
# Slicer -- getting the origin shift wrong would move the ground truth in world
# space, which does not raise, it just quietly produces wrong distances.
# ---------------------------------------------------------------------------

#: Background voxels kept on every side of the labelled region.
CROP_MARGIN_VOXELS = 2


def crop_bounds(shape_kji: Sequence[int], nonzero_kji: Sequence[Any],
                margin: int = CROP_MARGIN_VOXELS) -> Optional[Tuple[Tuple[int, int], ...]]:
    """Half-open ``((k0,k1),(j0,j1),(i0,i1))`` around the labelled voxels.

    ``None`` when nothing is labelled -- an empty ground truth is a case to
    report, not to crop to a degenerate box.
    """
    bounds = []
    for size, indices in zip(shape_kji, nonzero_kji):
        if len(indices) == 0:
            return None
        low = max(0, int(np.min(indices)) - margin)
        high = min(int(size), int(np.max(indices)) + 1 + margin)
        bounds.append((low, high))
    return tuple(bounds)


def cropped_ijk_to_ras(matrix: Sequence[Sequence[float]],
                       ijk_origin: Sequence[int]) -> List[List[float]]:
    """The IJK->RAS matrix of a crop whose voxel (0,0,0) is ``ijk_origin``.

    Only the translation column moves: it becomes the world position of the
    voxel the cropped array now starts at. The rotation/scale block is untouched,
    so orientation and spacing are preserved exactly and every remaining voxel
    keeps the world position it had.
    """
    out = [list(row) for row in matrix]
    i, j, k = ijk_origin
    for axis in range(3):
        out[axis][3] = (matrix[axis][0] * i + matrix[axis][1] * j
                        + matrix[axis][2] * k + matrix[axis][3])
    return out


def _share_below(values: np.ndarray, threshold: float) -> float:
    values = np.asarray(values, dtype=float).ravel()
    if values.size == 0:
        return float("nan")
    return float((values <= threshold).mean())


def _round(value: Optional[float], digits: int = 4) -> Optional[float]:
    if value is None:
        return None
    try:
        if np.isnan(value):
            return None
    except TypeError:
        return None
    return round(float(value), digits)


def _mean(values: Sequence[Optional[float]]) -> Optional[float]:
    numbers = [v for v in values if isinstance(v, (int, float))]
    return round(sum(numbers) / len(numbers), 4) if numbers else None


# ---------------------------------------------------------------------------
# Surfaces -- Slicer
# ---------------------------------------------------------------------------

class _single_threaded_smp(object):
    """Run a block with VTK's SMP backend limited to one thread.

    ``vtkDistancePolyDataFilter`` evaluates its distances inside
    ``vtkSMPTools::For``, over ONE shared ``vtkImplicitPolyDataDistance``, and
    this Slicer is built with the TBB backend -- so that loop really is
    concurrent. In current VTK that is safe by construction (``SetInput`` builds
    the locator eagerly, the scratch cell is ``vtkSMPThreadLocalObject``, and
    ``FindClosestPoint`` with a caller-supplied cell is documented thread safe),
    but this application ships its own older build of that library, and the
    symptom matches a data race exactly: a non-deterministic access violation
    inside vtkCommon, landing after a different number of cases each run, at a
    call that is merely where the corrupted state was next touched.

    It is also the ONLY concurrent operation in this module, which is what makes
    it worth ruling out rather than reasoning about. One thread costs a few
    seconds per case here and removes the question.

    Fail-open in both directions: a build without the wrapped API just runs as
    it did before, and the default is restored even if the block raises.
    """

    def __enter__(self):
        self._restore = False
        try:
            import vtk                                        # noqa: PLC0415
            vtk.vtkSMPTools.Initialize(1)
            self._restore = True
        except Exception:
            logger.debug("Could not limit VTK's SMP backend", exc_info=True)
        return self

    def __exit__(self, *_exc):
        if not self._restore:
            return False
        try:
            import vtk                                        # noqa: PLC0415
            vtk.vtkSMPTools.Initialize(0)                     # 0 = back to default
        except Exception:
            logger.debug("Could not restore VTK's SMP backend", exc_info=True)
        return False


def _detached_output(filter_) -> "Any":
    """A standalone copy of a filter's output.

    THE rule this module has broken most often, in three different places: a
    filter's output is owned by the filter's executive and holds a reference back
    to the producer, so a pipeline object that escapes the scope its filter lives
    in -- returned to a caller, or wired into a second filter as its input --
    leaves a reference cycle for ``vtkGarbageCollector`` to unpick. Collection is
    DEFERRED, so the fault lands at an arbitrary later moment, inside vtkCommon,
    in an unrelated case, with nothing in the traceback pointing here.

    Copy while the filter is alive, and let the filter and its output die
    together. ``check_orbital_analysis.py`` enforces that every ``GetOutput()``
    goes through this or is read straight into numpy.
    """
    import vtk                                                # noqa: PLC0415
    output = vtk.vtkPolyData()
    output.DeepCopy(filter_.GetOutput())
    return output


def _segment_surface(segmentation_node) -> "Any":
    """The first segment's closed surface, in RAS world coordinates.

    ``GetClosedSurfaceRepresentation`` returns the node's own coordinates; the
    parent transform is applied here even though no run currently sets one on a
    segmentation, because a surface that is silently in the wrong frame produces
    plausible distances rather than an error.
    """
    import vtk                                                # noqa: PLC0415

    segmentation = segmentation_node.GetSegmentation()
    if segmentation.GetNumberOfSegments() < 1:
        raise RuntimeError("segmentation has no segments")
    segmentation.SetConversionParameter("Smoothing factor", str(SURFACE_SMOOTHING))
    if not segmentation_node.CreateClosedSurfaceRepresentation():
        raise RuntimeError("closed-surface conversion failed")
    segment_id = segmentation.GetNthSegmentID(0)
    polydata = vtk.vtkPolyData()
    segmentation_node.GetClosedSurfaceRepresentation(segment_id, polydata)
    # Cells as well as points. vtkDistancePolyDataFilter builds a cell locator
    # over its target, and a surface with vertices but no polygons gives it
    # nothing to locate against -- which is a crash inside VTK, not an error
    # it reports.
    if polydata.GetNumberOfPoints() == 0 or polydata.GetNumberOfCells() == 0:
        raise RuntimeError(
            "closed surface is empty (%d points, %d cells)"
            % (polydata.GetNumberOfPoints(), polydata.GetNumberOfCells()))

    parent = segmentation_node.GetParentTransformNode()
    if parent is not None:
        matrix = vtk.vtkMatrix4x4()
        parent.GetMatrixTransformToWorld(matrix)
        transform = vtk.vtkTransform()
        transform.SetMatrix(matrix)
        filter_ = vtk.vtkTransformPolyDataFilter()
        filter_.SetInputData(polydata)
        filter_.SetTransform(transform)
        filter_.Update()
        # Copied out, not handed out: the filter dies at the end of this
        # function, and its output is owned by its executive and points back at
        # it. See _detached_output.
        polydata = _detached_output(filter_)
    return polydata


def _load_segmentation_surface(path: str, name: str):
    """The surface of a ``.seg.nrrd``, with nothing left in the scene.

    ``GetClosedSurfaceRepresentation`` deep-copies, so the polydata is wholly
    independent of the node and the node can go immediately. Removing it here --
    paired with the load, while the reference is in hand -- is what keeps the
    scene free of anything that would need sweeping up later.
    """
    import slicer                                             # noqa: PLC0415
    if not os.path.isfile(path):
        raise RuntimeError("missing %s" % os.path.basename(path))
    node = slicer.util.loadSegmentation(path)
    try:
        node.SetName(name)
        return _segment_surface(node)
    finally:
        _drop_node(node)


def _load_label_surface(path: str, name: str):
    """The surface of a ``.nii.gz`` label volume, with nothing left in the scene.

    Routed through a segmentation node rather than meshed directly so the ground
    truth goes through the SAME conversion, with the same smoothing, as the two
    surfaces it is compared against.
    """
    import slicer                                             # noqa: PLC0415
    if not os.path.isfile(path):
        raise RuntimeError("missing %s" % os.path.basename(path))
    label_node = slicer.util.loadLabelVolume(path)
    cropped_node = seg_node = None
    try:
        cropped_node, _factor = _cropped_label_volume(label_node, name + "_cropped")
        seg_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode", name)
        seg_node.CreateDefaultDisplayNodes()
        if not slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(
                cropped_node, seg_node):
            raise RuntimeError("could not import the ground-truth label map")
        return _segment_surface(seg_node)
    finally:
        # Every node this made, dropped in reverse order, each by the reference
        # that created it. Nothing survives the call, so nothing has to be found
        # again later.
        for node in (seg_node, cropped_node, label_node):
            _drop_node(node)


def _volume_array_copy(volume_node) -> np.ndarray:
    """An OWNED copy of a volume's voxels.

    ``slicer.util.arrayFromVolume`` returns a numpy VIEW on memory VTK owns, and
    its own documentation warns that it "must not be reallocated" -- yet
    ``updateVolumeFromArray`` calls ``vtkImageData::AllocateScalars``, which
    frees exactly that block. A view held across it is left with a stale
    pointer, and the buffer reference is released against freed memory whenever
    Python next collects it: an access violation inside vtkCommon, at an
    unrelated moment, in an unrelated case.

    Copying at the boundary makes that impossible, which is why nothing in this
    module calls ``arrayFromVolume`` directly -- ``check_orbital_analysis.py``
    enforces that this is the only caller.
    """
    import slicer                                             # noqa: PLC0415
    return np.array(slicer.util.arrayFromVolume(volume_node))


def _cropped_label_volume(label_node, name: str):
    """A NEW label volume holding only the labelled region. ``(node, factor)``.

    A new node rather than an in-place shrink: the loaded node's image data is
    what any view would alias, so not touching it at all is one less way to get
    the lifetime wrong.
    """
    import slicer                                             # noqa: PLC0415
    import vtk                                                # noqa: PLC0415

    array = _volume_array_copy(label_node)                    # k, j, i -- owned
    bounds = crop_bounds(array.shape, np.nonzero(array))
    if bounds is None:
        raise RuntimeError("the ground-truth label is empty")
    (k0, k1), (j0, j1), (i0, i1) = bounds

    matrix = vtk.vtkMatrix4x4()
    label_node.GetIJKToRASMatrix(matrix)
    rows = [[matrix.GetElement(r, c) for c in range(4)] for r in range(4)]
    shifted = cropped_ijk_to_ras(rows, (i0, j0, k0))

    cropped = np.ascontiguousarray(array[k0:k1, j0:j1, i0:i1])
    factor = float(array.size) / max(1, cropped.size)

    node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode", name)
    slicer.util.updateVolumeFromArray(node, cropped)
    new_matrix = vtk.vtkMatrix4x4()
    for r in range(4):
        for c in range(4):
            new_matrix.SetElement(r, c, shifted[r][c])
    node.SetIJKToRASMatrix(new_matrix)
    logger.debug("[Orbital] cropped the ground truth %dx (%d -> %d voxels)",
                 round(factor), array.size, cropped.size)
    return node, factor


def _centroid(polydata) -> np.ndarray:
    from vtk.util import numpy_support                        # noqa: PLC0415
    points = numpy_support.vtk_to_numpy(polydata.GetPoints().GetData())
    return points.mean(axis=0)


def _frame_gap_mm(a, b) -> float:
    return float(np.linalg.norm(_centroid(a) - _centroid(b)))


def _surface_volume_mm3(polydata) -> Optional[float]:
    import vtk                                                # noqa: PLC0415
    try:
        triangles = vtk.vtkTriangleFilter()
        triangles.SetInputData(polydata)
        triangles.Update()
        # Detached before it is handed to the second filter. Wiring
        # properties.SetInputData(triangles.GetOutput()) directly makes each
        # filter reach into the other's lifetime, and both are dropped together
        # at return -- so which one is destroyed first is decided by CPython's
        # collector. This runs on three surfaces of every case, which is why it
        # was the one that eventually landed.
        mesh = _detached_output(triangles)
        properties = vtk.vtkMassProperties()
        properties.SetInputData(mesh)
        properties.Update()
        return _round(properties.GetVolume(), 1)
    except Exception:
        logger.debug("Surface volume failed", exc_info=True)
        return None


def _surface_distances(ground_truth, other):
    """``(gt_mesh, gt_values, other_values)`` -- nothing shared with the filter.

    ``vtkDistancePolyDataFilter`` does both directions in C++; doing it in
    Python over ~10^5 vertices per case would dominate the run.

    Everything returned is a COPY, taken while the filter is still alive. A
    filter's output is owned by its executive and holds a reference back to the
    producer, so handing one out and letting the filter fall out of scope leaves
    a reference cycle for ``vtkGarbageCollector`` to unpick -- deferred, so it
    is collected at some arbitrary later point, in the middle of some other
    case. The same rule as the deep copy above: no VTK object may outlive what
    owns its memory.
    """
    import vtk                                                # noqa: PLC0415
    from vtk.util import numpy_support                        # noqa: PLC0415

    for label, mesh in (("ground truth", ground_truth), ("comparison", other)):
        if mesh is None or mesh.GetNumberOfPoints() == 0 or mesh.GetNumberOfCells() == 0:
            raise RuntimeError("the %s surface has no geometry to measure" % label)

    distance = vtk.vtkDistancePolyDataFilter()
    distance.SetInputData(0, ground_truth)
    distance.SetInputData(1, other)
    # Unsigned: the report and the colour map are both magnitudes. Signed
    # distance would need a watertight, correctly-oriented target to mean
    # anything, and a marching-cubes surface of a cropped label map is not
    # reliably either.
    distance.SignedDistanceOff()
    # See _single_threaded_smp: Update() below is the only concurrent call in
    # this module.
    distance.ComputeSecondDistanceOn()
    # On by default, and pure waste here: the per-triangle array is
    # discarded, and computing it roughly doubles the filter's work on
    # meshes of ~10^5 cells.
    distance.ComputeCellCenterDistanceOff()
    with _single_threaded_smp():
        distance.Update()

    def _values(mesh):
        if mesh is None:
            return np.zeros(0)
        array = mesh.GetPointData().GetArray("Distance")
        if array is None:
            array = mesh.GetPointData().GetScalars()
        if array is None:
            return np.zeros(0)
        # np.abs allocates, so this is a copy and not a view on VTK's buffer.
        return np.abs(numpy_support.vtk_to_numpy(array))

    gt_values = _values(distance.GetOutput())
    other_values = _values(distance.GetSecondDistanceOutput())
    return _detached_output(distance), gt_values, other_values


def _named_distance_surface(mesh, values: np.ndarray):
    """A copy of ``mesh`` carrying ``values`` as the active point scalars."""
    import vtk                                                # noqa: PLC0415
    from vtk.util import numpy_support                        # noqa: PLC0415

    output = vtk.vtkPolyData()
    output.DeepCopy(mesh)
    # deep=1 is NOT optional. numpy_to_vtk defaults to deep=0, which makes the
    # vtkFloatArray a VIEW ON THE NUMPY BUFFER rather than a copy -- and the
    # array handed in here is a temporary with no surviving Python reference, so
    # CPython frees it the moment this call returns and the VTK array is left
    # pointing at freed memory. It is a use-after-free that usually LOOKS fine
    # (the values are still readable until the allocator reuses the block, so
    # the .vtp written seconds later can be perfectly correct) and then takes
    # the process down later, somewhere else entirely: an access violation
    # inside vtkCommon during an unrelated case, several minutes in.
    array = numpy_support.numpy_to_vtk(
        np.ascontiguousarray(values, dtype=np.float32), deep=1)
    array.SetName(DISTANCE_ARRAY)
    output.GetPointData().AddArray(array)
    output.GetPointData().SetActiveScalars(DISTANCE_ARRAY)
    # The filter's own arrays would otherwise ride along and show up as extra,
    # identically-valued choices in the Models module -- and the CELL "Distance"
    # array in particular would render instead of the point one if a viewer
    # picked it, at a different (per-triangle) resolution.
    output.GetPointData().RemoveArray("Distance")
    for name in ("Distance", "Direction"):
        output.GetCellData().RemoveArray(name)
    return output


# ---------------------------------------------------------------------------
# The colour map and the scenes
# ---------------------------------------------------------------------------

def _color_table_node(scene_dir: str):
    """A user colour table green -> yellow -> orange -> red over 0..COLOR_MAX_MM.

    It needs a storage node like the models do: a user-type colour table writes
    ``numcolors`` into the scene XML but not the colours themselves, so without a
    ``.ctbl`` beside the scene the reopened map has a table with 256 undefined
    entries.
    """
    import slicer                                             # noqa: PLC0415

    node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLColorTableNode", COLOR_TABLE_NAME)
    node.SetTypeToUser()
    node.SetNumberOfColors(COLOR_TABLE_SIZE)
    # No SetNamesInitialised: it is deprecated in current Slicer and its only
    # implementation is a vtkErrorMacro, which SafeExecutor's VTK interception
    # would surface as a real error. The per-entry SetColor below names each
    # entry anyway, which is what it used to be needed for.
    stops = list(COLOR_STOPS)
    for index in range(COLOR_TABLE_SIZE):
        position = index / float(COLOR_TABLE_SIZE - 1)
        lower = stops[0]
        upper = stops[-1]
        for first, second in zip(stops, stops[1:]):
            if first[0] <= position <= second[0]:
                lower, upper = first, second
                break
        span = (upper[0] - lower[0]) or 1.0
        weight = (position - lower[0]) / span
        rgb = [lower[1][c] + weight * (upper[1][c] - lower[1][c]) for c in range(3)]
        node.SetColor(index, "%.2f mm" % (position * COLOR_MAX_MM),
                      rgb[0], rgb[1], rgb[2], 1.0)
    _pin_storage(node, os.path.join(scene_dir, COLOR_TABLE_NAME + ".ctbl"))
    return node


def _error_model_node(polydata, name: str, color_node, scene_dir: str,
                      visible: bool):
    """A model node showing ``DISTANCE_ARRAY`` on the fixed 0..COLOR_MAX_MM scale."""
    import slicer                                             # noqa: PLC0415
    import vtk                                                # noqa: PLC0415

    model = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", name)
    model.SetAndObservePolyData(polydata)
    model.CreateDefaultDisplayNodes()
    display = model.GetDisplayNode()
    display.SetVisibility(visible)
    display.SetVisibility2D(True)
    display.SetScalarVisibility(True)
    display.SetActiveScalarName(DISTANCE_ARRAY)
    display.SetActiveAttributeLocation(vtk.vtkAssignAttribute.POINT_DATA)
    display.SetAndObserveColorNodeID(color_node.GetID())
    # Manual, not UseData: an auto range would rescale per case and two cases
    # would no longer be comparable by eye, which is the whole point of a map.
    display.SetScalarRangeFlag(slicer.vtkMRMLDisplayNode.UseManualScalarRange)
    display.SetScalarRange(0.0, COLOR_MAX_MM)
    _pin_storage(model, os.path.join(scene_dir, name + ".vtp"))
    return model


def _plain_model_node(polydata, name: str, scene_dir: str):
    import slicer                                             # noqa: PLC0415
    model = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", name)
    model.SetAndObservePolyData(polydata)
    model.CreateDefaultDisplayNodes()
    display = model.GetDisplayNode()
    display.SetColor(0.85, 0.85, 0.85)
    display.SetOpacity(0.35)
    display.SetVisibility(False)
    _pin_storage(model, os.path.join(scene_dir, name + ".vtp"))
    return model
    return model


def _pin_storage(node, path: str):
    """Give ``node`` a storage node writing exactly ``path``.

    For models this means ``.vtp`` rather than Slicer's default ``.vtk``: the
    legacy writer keeps only the ACTIVE scalar array, and these models carry a
    named array that must survive the round trip for the reopened scene to show
    anything.
    """
    try:
        node.AddDefaultStorageNode()
        storage = node.GetStorageNode()
        if storage is not None:
            extension = os.path.splitext(path)[1].lstrip(".")
            if extension:
                storage.SetDefaultWriteFileExtension(extension)
            storage.SetFileName(path)
        return storage
    except Exception:
        logger.debug("Could not pin the storage node for %s", path, exc_info=True)
        return None


def _write_error_scene(scene_dir: str, nodes: Sequence[Any], notes: List[str]) -> bool:
    """Write the node FILES, then the scene XML. True only if everything landed.

    ``slicer.util.saveScene("....mrml")`` does NOT write node data. Its path for
    a ``.mrml`` suffix is ``qSlicerSceneWriter::writeToMRML``, which is
    ``SetURL`` + ``SetRootDirectory`` + ``vtkMRMLScene::Commit()`` -- and
    ``Commit`` serialises the node *elements* but never asks a storage node to
    write its data. (It is the same fact that makes ``_saveSceneFlat`` in the
    workflow widget write its nodes first and the scene last.) Committing alone
    produces a scene whose storage nodes name files that do not exist, and
    Slicer only reports it when the scene is *opened*:

        vtkMRMLStorableNode::UpdateScene failed: Failed to read node
        ErrorMap_Reconstructed_vs_GT using storage node ...

    So each file is written explicitly and then checked to be ON DISK. The
    caller splices into the run's own scene.mrml only on a True from here: a
    scene must never be edited to point at a file whose write was assumed.
    """
    import slicer                                             # noqa: PLC0415

    ok = True
    # EXACTLY the nodes this case created, handed in by the caller -- never
    # "every node of these classes in the scene". Slicer keeps ~20 built-in
    # colour tables (Labels, Grey, the ColorFiles tables) as SINGLETONS, which
    # survive Clear() and are returned by getNodesByClass("vtkMRMLColorTableNode").
    # Iterating over those was the first version's bug, and it had two effects:
    # most have no storage file name, so this returned False and the splice into
    # the run's scene.mrml was silently skipped; and the ones that do have one
    # point INTO SLICER'S OWN INSTALLATION (share/.../ColorFiles/*.txt), so a
    # save would have overwritten the application's colour tables.
    targets = [node for node in (nodes or []) if node is not None]
    if not targets:
        notes.append("nothing to write into %s" % ERROR_SCENE_NAME)
        return False

    for node in targets:
        storage = node.GetStorageNode()
        path = storage.GetFileName() if storage is not None else ""
        if not path:
            notes.append("%s has no storage file name" % node.GetName())
            ok = False
            continue
        try:
            saved = bool(slicer.util.saveNode(node, path))
        except Exception as exc:
            saved = False
            notes.append("saving %s raised: %s" % (node.GetName(), exc))
        if not saved or not os.path.isfile(path):
            ok = False
            notes.append("%s was NOT written to %s"
                         % (node.GetName(), os.path.basename(path)))

    scene_path = os.path.join(scene_dir, ERROR_SCENE_NAME)
    try:
        if not slicer.util.saveScene(scene_path):
            notes.append("could not write %s" % ERROR_SCENE_NAME)
            ok = False
    except Exception as exc:
        notes.append("writing %s raised: %s" % (ERROR_SCENE_NAME, exc))
        ok = False
    return ok


# ---------------------------------------------------------------------------
# Splicing the error maps into the run's own scene.mrml
# ---------------------------------------------------------------------------

def _renamed_id(old_id: str, suffix: str) -> str:
    """``vtkMRMLModelNode3`` -> ``vtkMRMLModelNodeOFRErr_<suffix>``.

    Slicer-generated ids always end in digits, so stripping the digits and
    appending a marker cannot collide with one -- which matters because the
    target scene.mrml already contains ``vtkMRMLModelNode1..4``.
    """
    return "%s%s_%s" % (re.sub(r"\d+$", "", old_id), ID_MARKER, suffix)


def _splice_into_scene(scene_path: str, error_scene_path: str,
                       node_names: Sequence[str], notes: List[str]) -> bool:
    """Copy the error-map nodes out of ``ErrorMaps.mrml`` into the run's scene.

    XML surgery rather than "load the scene, add nodes, save it": the run's own
    scene carries the 40 MB CT and every node the procedure made, and loading and
    rewriting all of that -- 30 times -- to add two models would be both slow and
    a far larger blast radius than appending four elements.

    Idempotent: a previous run's spliced elements are identified by ID_MARKER and
    removed first, so re-running replaces them instead of stacking copies.
    """
    if not os.path.isfile(scene_path) or not os.path.isfile(error_scene_path):
        return False
    # Written once, and never overwritten afterwards: the point of the backup is
    # to hold the scene as the RUN left it, and a second copy taken after a
    # splice would just preserve the splice.
    backup = os.path.join(os.path.dirname(scene_path), SCENE_BACKUP)
    if not os.path.exists(backup):
        shutil.copy2(scene_path, backup)

    source = ElementTree.parse(error_scene_path).getroot()
    target_tree = ElementTree.parse(scene_path)
    target = target_tree.getroot()

    # Collect the wanted nodes plus everything they reference (display, storage,
    # colour table, and the colour table's own storage node) -- but only those:
    # a display node also references its view, and following that would splice a
    # second View node into a scene that already has one.
    by_id = {el.get("id"): el for el in source if el.get("id")}
    wanted: List[ElementTree.Element] = []
    pending = [el for el in source
               if el.get("name") in set(node_names) and el.get("id")]
    seen = set()
    while pending:
        element = pending.pop(0)
        node_id = element.get("id")
        if node_id in seen:
            continue
        seen.add(node_id)
        wanted.append(element)
        for reference in _referenced_ids(element):
            candidate = by_id.get(reference)
            if candidate is None or reference in seen:
                continue
            if candidate.tag not in _SPLICEABLE_TAGS:
                continue
            pending.append(candidate)
    if not wanted:
        notes.append("no error-map nodes found in %s" % os.path.basename(error_scene_path))
        return False

    # Drop whatever a previous run of this analysis left behind.
    for element in list(target):
        if ID_MARKER in (element.get("id") or ""):
            target.remove(element)

    mapping = {node_id: _renamed_id(node_id, str(index))
               for index, node_id in enumerate(sorted(seen))}
    # Referenced nodes before the nodes that reference them. Slicer resolves
    # references in a second pass so this is not strictly required, but a scene
    # that reads correctly in file order is one less thing to reason about.
    ordered = ([el for el in wanted if el.tag != "Model"]
               + [el for el in wanted if el.tag == "Model"])
    for element in ordered:
        target.append(_rewrite_ids(element, mapping))

    target_tree.write(scene_path, encoding="UTF-8", xml_declaration=True)
    return True


#: Node kinds the splicer may carry across. Anything else a display node happens
#: to point at (a view, the selection singleton) belongs to the scene it came
#: from, and the target scene already has its own.
_SPLICEABLE_TAGS = {
    "Model", "ModelDisplay", "ModelStorage",
    "ColorTable", "ColorTableStorage",
    "ProceduralColor", "ProceduralColorStorage",
}


def _referenced_ids(element: ElementTree.Element) -> List[str]:
    """Every MRML id an element points at, from any attribute."""
    found: List[str] = []
    for value in element.attrib.values():
        found.extend(re.findall(r"vtkMRML[A-Za-z]*Node[A-Za-z0-9_]*", value or ""))
    return found


def _rewrite_ids(element: ElementTree.Element,
                 mapping: Dict[str, str]) -> ElementTree.Element:
    """A copy of ``element`` with every old id replaced by its new one.

    Replacement is on whole ids -- the negative lookahead stops
    ``vtkMRMLModelNode1`` matching inside ``vtkMRMLModelNode10``, which is the
    one way a textual rewrite of this shape goes wrong.
    """
    copied = ElementTree.Element(element.tag, dict(element.attrib))
    copied.text, copied.tail = element.text, element.tail
    for child in element:
        copied.append(_rewrite_ids(child, mapping))
    for key, value in list(copied.attrib.items()):
        new_value = value
        for old_id, new_id in mapping.items():
            new_value = re.sub(re.escape(old_id) + r"(?![0-9])", new_id, new_value)
        if new_value != value:
            copied.set(key, new_value)
    return copied


# ---------------------------------------------------------------------------
# One case, end to end
# ---------------------------------------------------------------------------

def ground_truth_path(case: Dict[str, str]) -> str:
    subject = case.get("subject") or ""
    if not subject or not case.get("dataset_dir"):
        return ""
    return os.path.join(case["dataset_dir"],
                        GROUND_TRUTH_TEMPLATE.format(subject=subject))


def _drop_node(node) -> None:
    """Remove one node the caller still holds a live reference to.

    This is the ONLY way this module removes anything, and the two properties
    that make it safe are both about the reference:

    * The caller holds the Python wrapper, so the C++ node cannot have been
      destroyed -- the pointer is valid even if the node has already left the
      scene. Resolving ids from a snapshot instead is what crashed the batch:
      removing a segmentation cascades to its display and storage nodes, so ids
      collected beforehand can name nodes that no longer exist, and
      ``vtkMRMLScene::RemoveNode`` calls ``n->Register(this)`` on whatever it is
      handed. Its own guard against that ("The caller should make sure the node
      isn't already removed") is inside ``#ifndef NDEBUG`` -- in a release build
      there is no check, just an access violation in vtkCommon.
    * ``IsNodePresent`` is that guard, done properly, on a pointer guaranteed
      live.

    Removal is otherwise cheap and correct: paired with the create that made the
    node, one at a time, never as a bulk sweep.
    """
    if node is None:
        return
    import slicer                                             # noqa: PLC0415
    try:
        if slicer.mrmlScene.IsNodePresent(node):
            slicer.mrmlScene.RemoveNode(node)
    except Exception:
        logger.debug("Could not remove a node", exc_info=True)


def analyse_case(case: Dict[str, str], write_scenes: bool = True) -> Dict[str, Any]:
    """Surface error for both comparisons, and (optionally) the two colour maps.

    The models are built in the main scene, because ``saveScene`` is the only way
    to produce a scene file Slicer is certain to reopen. Every node made here is
    dropped through ``_drop_node`` by the reference that created it -- the
    inputs as soon as their surface is copied out, the models once the scene is
    written -- so the scene is left as it was found without any sweep.
    """
    scene_dir = case["scene_dir"]
    notes: List[str] = []
    label = case["subject"] or case["run"]

    gt_path = ground_truth_path(case)
    if not gt_path or not os.path.isfile(gt_path):
        raise RuntimeError(
            "no ground truth at %s" % (gt_path or "(no Dataset/<subject>/ folder)"))

    rows: List[Dict[str, Any]] = []
    error_models: List[str] = []
    #: The nodes that belong in the saved scene -- kept as an explicit list so
    #: _write_error_scene never has to ask the scene what is in it.
    scene_nodes: List[Any] = []
    try:
        gt_surface = _load_label_surface(gt_path, "GroundTruth_%s" % label)
        gt_volume = _surface_volume_mm3(gt_surface)

        color_node = _color_table_node(scene_dir) if write_scenes else None
        if write_scenes:
            scene_nodes.append(color_node)
            scene_nodes.append(
                _plain_model_node(gt_surface, "GroundTruth_%s" % label, scene_dir))

        for index, (key, filename, title) in enumerate(COMPARISONS):
            row: Dict[str, Any] = {
                "case": label, "run": case["run"], "comparison": key,
                "source_file": filename,
            }
            try:
                surface = _load_segmentation_surface(
                    os.path.join(scene_dir, filename), "%s_%s" % (title, label))
            except Exception as exc:
                notes.append("%s: %s" % (title, exc))
                row["error"] = str(exc)
                rows.append(row)
                continue

            gap = _frame_gap_mm(gt_surface, surface)
            row["centroid_gap_mm"] = _round(gap, 3)
            if gap > FRAME_TOLERANCE_MM:
                message = ("%s is %.1f mm from the ground truth's centroid "
                           "(limit %.0f) -- the two are not in the same frame, "
                           "or not the same orbit" % (title, gap, FRAME_TOLERANCE_MM))
                notes.append(message)
                row["error"] = message
                rows.append(row)
                continue

            gt_mesh, gt_values, other_values = _surface_distances(
                gt_surface, surface)
            row.update(distance_statistics(gt_values, other_values))
            row["volume_mm3"] = _surface_volume_mm3(surface)
            row["gt_volume_mm3"] = gt_volume
            if row["volume_mm3"] and gt_volume:
                row["volume_ratio"] = _round(row["volume_mm3"] / gt_volume)
            rows.append(row)

            if write_scenes:
                name = "ErrorMap_%s_vs_GT" % title
                scene_nodes.append(_error_model_node(
                    _named_distance_surface(gt_mesh, gt_values), name,
                    color_node, scene_dir,
                    # One map visible on opening. Both would overlay the same
                    # surface and the reader would be looking at whichever
                    # happened to render last.
                    visible=(index == 0)))
                error_models.append(name)

        if write_scenes:
            # The splice is conditional on the files being ON DISK, not on the
            # save call returning. Editing the run's own scene.mrml to reference
            # a file that was never written is worse than writing nothing: the
            # run's scene then fails to open, and it fails at the point the
            # surgeon tries to look at it rather than here where it can be said.
            if _write_error_scene(scene_dir, scene_nodes, notes) and error_models:
                spliced = _splice_into_scene(
                    os.path.join(scene_dir, SCENE_FILE),
                    os.path.join(scene_dir, ERROR_SCENE_NAME),
                    error_models, notes)
                if not spliced:
                    notes.append("error maps were NOT added to %s" % SCENE_FILE)
            else:
                notes.append(
                    "%s was left untouched -- the error-map files did not all "
                    "get written" % SCENE_FILE)
    finally:
        # Reverse order, each by the reference that made it: a model's display
        # and storage nodes go with it, and nothing is ever looked up again.
        for node in reversed(scene_nodes):
            _drop_node(node)

    return {"rows": rows, "notes": notes, "models": error_models}


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------

ERROR_COLUMNS = [
    "case", "comparison", "assd_mm", "rms_mm", "median_mm", "hd95_mm", "hd_max_mm",
    "within_1mm_pct", "within_2mm_pct",
    "mean_gt_to_other_mm", "mean_other_to_gt_mm",
    "volume_mm3", "gt_volume_mm3", "volume_ratio",
    "centroid_gap_mm", "gt_points", "other_points", "source_file", "error", "run",
]

IMPROVEMENT_COLUMNS = [
    "case", "fractured_assd_mm", "reconstructed_assd_mm", "assd_improvement_mm",
    "assd_improvement_pct", "fractured_hd95_mm", "reconstructed_hd95_mm",
    "hd95_improvement_mm", "reconstructed_within_1mm_pct", "fractured_within_1mm_pct",
    "improved", "run",
]


def improvement_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Per case: did reconstructing actually move the orbit toward the truth?

    This is the table the claim rests on. A reconstruction error on its own says
    nothing without the error it started from, so every figure here is a pair.
    """
    out: List[Dict[str, Any]] = []
    by_case: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for row in rows:
        by_case.setdefault(row["case"], {})[row["comparison"]] = row
    for case in sorted(by_case):
        pair = by_case[case]
        before, after = pair.get("fractured"), pair.get("reconstructed")
        if not before or not after:
            continue
        if before.get("assd_mm") is None or after.get("assd_mm") is None:
            continue
        delta = before["assd_mm"] - after["assd_mm"]
        entry = {
            "case": case,
            "run": after.get("run", ""),
            "fractured_assd_mm": before["assd_mm"],
            "reconstructed_assd_mm": after["assd_mm"],
            "assd_improvement_mm": _round(delta),
            "assd_improvement_pct": _round(
                100.0 * delta / before["assd_mm"]) if before["assd_mm"] else None,
            "fractured_hd95_mm": before.get("hd95_mm"),
            "reconstructed_hd95_mm": after.get("hd95_mm"),
            "hd95_improvement_mm": _round(
                (before.get("hd95_mm") or 0) - (after.get("hd95_mm") or 0)),
            "reconstructed_within_1mm_pct": after.get("within_1mm_pct"),
            "fractured_within_1mm_pct": before.get("within_1mm_pct"),
            "improved": delta > 0,
        }
        out.append(entry)
    return out


def _aggregate(rows: List[Dict[str, Any]], improvements: List[Dict[str, Any]]
               ) -> List[Dict[str, Any]]:
    summary: List[Dict[str, Any]] = []
    for key, _file, title in COMPARISONS:
        scored = [r for r in rows if r["comparison"] == key and r.get("assd_mm") is not None]
        if not scored:
            continue
        # .get throughout: a row can be scored but incomplete (a metric that
        # could not be derived leaves its own cell blank), and an aggregate that
        # raises on one missing cell would cost the whole report.
        hd95 = [r.get("hd95_mm") for r in scored if isinstance(r.get("hd95_mm"), (int, float))]
        summary.append({
            "comparison": title,
            "cases": len(scored),
            "mean_assd_mm": _mean([r.get("assd_mm") for r in scored]),
            "mean_rms_mm": _mean([r.get("rms_mm") for r in scored]),
            "mean_hd95_mm": _mean(hd95),
            "worst_hd95_mm": round(max(hd95), 4) if hd95 else None,
            "mean_within_1mm_pct": _mean([r.get("within_1mm_pct") for r in scored]),
        })
    if improvements:
        summary.append({
            "comparison": "IMPROVEMENT (fractured - reconstructed)",
            "cases": len(improvements),
            "mean_assd_mm": _mean([r["assd_improvement_mm"] for r in improvements]),
            "mean_rms_mm": None,
            "mean_hd95_mm": _mean([r["hd95_improvement_mm"] for r in improvements]),
            "worst_hd95_mm": None,
            "mean_within_1mm_pct": None,
            "cases_improved": sum(1 for r in improvements if r["improved"]),
        })
    return summary


SUMMARY_COLUMNS = ["comparison", "cases", "mean_assd_mm", "mean_rms_mm",
                   "mean_hd95_mm", "worst_hd95_mm", "mean_within_1mm_pct",
                   "cases_improved"]


# ---------------------------------------------------------------------------
# What every column means, carried in the workbook itself
#
# The numbers travel: a spreadsheet gets copied, mailed and read months later by
# someone without this source. A column called ``hd95_mm`` is not
# self-explanatory, and the difference between the two one-way means is exactly
# the sort of thing a reader will otherwise guess at. So the definitions ship
# with the numbers rather than in a doc beside them.
# ---------------------------------------------------------------------------

DEFINITION_COLUMNS = ["term", "definition"]

#: How the measurement is made at all -- the part that is not a column.
METHOD_DEFINITIONS = [
    ("ground truth",
     "Dataset/<subject>/<subject>_Label.nii.gz -- the surgeon's correct orbital "
     "volume on the fractured side. Every distance in this workbook is measured "
     "against it."),
    ("what is compared",
     "Two surfaces per case, both against the ground truth: 'reconstructed' = "
     "OFR_Reconstructed_Seg, the pipeline's output; 'fractured' = "
     "OFR_Fractured_Seg, the orbit before repair. The second is what makes the "
     "first mean anything -- a given error is good or bad depending on the error "
     "it started from."),
    ("surface generation",
     "All three surfaces are meshed through ONE pipeline at smoothing factor "
     "%.2f. A distance between surfaces built by different rules would measure "
     "the rules." % SURFACE_SMOOTHING),
    ("distance",
     "Unsigned point-to-SURFACE distance in millimetres: each vertex is measured "
     "to the nearest point on the opposing triangles (not to the nearest "
     "vertex). Unsigned, so inside and outside are not distinguished -- see the "
     "two one-way means for that."),
    ("coordinates",
     "RAS world coordinates. The ground truth is stored on the full CT grid and "
     "the run's segmentations on the cropped one; both resolve to the same "
     "anatomy, so no resampling is applied. centroid_gap_mm checks that per case."),
    ("READ THIS BEFORE QUOTING assd_mm",
     "assd_mm averages over the WHOLE orbital surface, and a blowout fracture "
     "affects only part of the wall. The unaffected majority dilutes the "
     "figure, so a real improvement can look small. hd95_mm and "
     "within_1mm_pct are more sensitive to a localised defect."),
]

#: Per-case surface-error columns.
ERROR_DEFINITIONS = [
    ("case", "Subject the run was driven from, taken from the run manifest."),
    ("comparison",
     "'reconstructed' = the pipeline's result; 'fractured' = the orbit before "
     "repair. Both are measured against the same ground truth."),
    ("assd_mm",
     "Average symmetric surface distance (mm). The two directions pooled and "
     "averaged: (sum of ground-truth-to-other + sum of other-to-ground-truth) "
     "divided by the total number of vertices. Each surface therefore "
     "contributes in proportion to its vertex count. The headline figure."),
    ("rms_mm",
     "Root mean square of the same pooled distances (mm). Weights large "
     "deviations more heavily than assd_mm, so rms >> assd means the error is "
     "concentrated rather than spread out."),
    ("median_mm",
     "Median of the pooled distances (mm). Unaffected by a small number of "
     "large deviations; compare with assd_mm to see how skewed the error is."),
    ("hd95_mm",
     "95th percentile of the pooled distances (mm) -- the 95% Hausdorff "
     "distance. Quoted in preference to the maximum because marching cubes can "
     "always produce one stray vertex at the edge of a label map, which moves "
     "the maximum arbitrarily and the percentile not at all."),
    ("hd_max_mm",
     "The largest pooled distance (mm) -- the true symmetric Hausdorff "
     "distance. Reported for completeness; prefer hd95_mm."),
    ("within_1mm_pct",
     "Percentage of GROUND-TRUTH surface vertices whose nearest point on the "
     "compared surface is within 1 mm. One-directional by design: 'how much of "
     "the true wall was reproduced'."),
    ("within_2mm_pct", "As within_1mm_pct, at a 2 mm tolerance."),
    ("mean_gt_to_other_mm",
     "One-way mean (mm), ground truth -> compared surface. Large when the "
     "compared surface is MISSING parts of the truth (under-reconstruction)."),
    ("mean_other_to_gt_mm",
     "One-way mean (mm), compared surface -> ground truth. Large when the "
     "compared surface has EXTRA material outside the truth "
     "(over-reconstruction). Read this pair together: assd_mm alone cannot "
     "tell the two failure modes apart."),
    ("volume_mm3",
     "Volume enclosed by the compared surface (mm3), from vtkMassProperties."),
    ("gt_volume_mm3", "Volume enclosed by the ground-truth surface (mm3)."),
    ("volume_ratio",
     "volume_mm3 / gt_volume_mm3. 1.0 means the same enclosed volume -- which "
     "two differently shaped surfaces can both have, so it is context for the "
     "distances, not a substitute."),
    ("centroid_gap_mm",
     "Distance between the two surfaces' centroids (mm). A coordinate-frame "
     "check, not a quality measure: a few mm is real anatomical difference, "
     "tens of mm means the two are not in the same frame. Above %.0f mm the "
     "case is reported instead of scored." % FRAME_TOLERANCE_MM),
    ("gt_points", "Vertices on the ground-truth surface (the count measured in "
                  "the ground-truth-to-other direction)."),
    ("other_points", "Vertices on the compared surface."),
    ("source_file", "The .seg.nrrd this row's compared surface was read from."),
    ("error", "Why the row could not be scored. Blank when it was."),
    ("run", "Run folder under Overall_Performance, for traceability."),
]

#: The improvement pairing.
IMPROVEMENT_DEFINITIONS = [
    ("fractured_assd_mm", "assd_mm of the orbit BEFORE repair -- the error the "
                          "procedure started from."),
    ("reconstructed_assd_mm", "assd_mm of the pipeline's result."),
    ("assd_improvement_mm",
     "fractured_assd_mm - reconstructed_assd_mm. POSITIVE means the "
     "reconstruction is closer to the ground truth than the untreated fracture "
     "was; negative means it moved away from it."),
    ("assd_improvement_pct",
     "assd_improvement_mm as a percentage of fractured_assd_mm."),
    ("fractured_hd95_mm / reconstructed_hd95_mm",
     "The same pair for hd95_mm."),
    ("hd95_improvement_mm", "fractured_hd95_mm - reconstructed_hd95_mm."),
    ("reconstructed_within_1mm_pct / fractured_within_1mm_pct",
     "The same pair for within_1mm_pct. Here HIGHER is better, so the "
     "reconstruction should exceed the fracture."),
    ("improved", "yes when assd_improvement_mm is greater than 0."),
]

#: The across-all-cases block.
SUMMARY_DEFINITIONS = [
    ("comparison",
     "Which set of rows is aggregated: 'Reconstructed', 'Fractured', or "
     "'IMPROVEMENT (fractured - reconstructed)'."),
    ("cases", "Number of cases contributing a scored value."),
    ("mean_assd_mm / mean_rms_mm / mean_hd95_mm",
     "Mean across CASES, each case weighted equally (unlike assd_mm within a "
     "case, which is weighted by vertex count)."),
    ("worst_hd95_mm", "The largest per-case hd95_mm."),
    ("mean_within_1mm_pct", "Mean of the per-case within_1mm_pct."),
    ("cases_improved",
     "On the IMPROVEMENT row only: how many cases had a positive "
     "assd_improvement_mm."),
]


def definition_rows(pairs: Sequence[Tuple[str, str]]) -> List[Dict[str, Any]]:
    """``[(term, definition)]`` -> workbook rows."""
    return [{"term": term, "definition": text} for term, text in pairs]


def build_report(experiment_root: str, write_scenes: bool = True,
                 progress=None) -> Dict[str, Any]:
    """Analyse every case. Fail-soft per case, so one bad scene costs one row."""
    cases = discover_cases(experiment_root)
    rows: List[Dict[str, Any]] = []
    log: List[str] = []
    if not cases:
        log.append("No cases found under %s."
                   % os.path.join(experiment_root, RUNS_SUBDIR))

    # ONCE, and only when scenes are written: saveScene serialises whatever is
    # in the scene, so it must hold nothing but this case's nodes. Each case
    # then cleans up after itself node by node (_drop_node), so this is the
    # only Clear in the batch.
    if write_scenes and cases:
        try:
            import slicer                                     # noqa: PLC0415
            slicer.mrmlScene.Clear(0)
        except Exception:
            logger.warning("Could not clear the scene before the batch", exc_info=True)

    for index, case in enumerate(cases):
        label = case["subject"] or case["run"]
        if progress is not None:
            try:
                progress(index, len(cases), label)
            except Exception:
                logger.debug("Progress callback failed", exc_info=True)
        # To Slicer's own log, before the work rather than after it. A hard
        # crash takes the report with it, so the last line in the log is the
        # only evidence of which case was in flight when it happened.
        logger.info("[Orbital] case %d/%d: %s", index + 1, len(cases), label)
        try:
            result = analyse_case(case, write_scenes=write_scenes)
        except Exception as exc:
            log.append("%s: FAILED -- %s" % (label, exc))
            logger.warning("Orbital analysis failed for %s", label, exc_info=True)
            continue
        rows.extend(result["rows"])
        scored = [r for r in result["rows"] if r.get("assd_mm") is not None]
        log.append("%s: %d/%d comparison(s) scored%s"
                   % (label, len(scored), len(COMPARISONS),
                      ", %d error map(s) written" % len(result["models"])
                      if result["models"] else ""))
        for note in result["notes"]:
            log.append("   [!] %s: %s" % (label, note))

    improvements = improvement_rows(rows)
    summary = _aggregate(rows, improvements)
    timing_rows, step_rows = collect_timing(cases, log)

    sheets = [
        ("Surface error", [
            ("Symmetric surface distance to the surgeon's ground truth "
             "(Dataset/<subject>/<subject>_Label.nii.gz), in mm. Two rows per "
             "case: the pipeline's reconstruction, and the fractured orbit it "
             "started from. assd = average symmetric surface distance (the "
             "figure to quote); hd95 = 95th-percentile Hausdorff, which ignores "
             "the single stray vertex marching cubes can always produce; "
             "within_1mm_pct = share of the GROUND-TRUTH surface within 1 mm. "
             "All three surfaces are meshed by one pipeline at smoothing %.2f, "
             "so the distance measures the shapes and not the meshing."
             % SURFACE_SMOOTHING,
             ERROR_COLUMNS, rows),
            ("Per-case improvement. A reconstruction error means nothing without "
             "the error it started from, so this pairs them: positive "
             "assd_improvement_mm means the reconstruction is closer to the "
             "ground truth than the fracture was.",
             IMPROVEMENT_COLUMNS, improvements),
            ("Across all cases", SUMMARY_COLUMNS, summary),
            # Last, under the numbers they describe, so the sheet reads
            # top-to-bottom: results first, then what they mean.
            ("DEFINITIONS — how the measurement is made",
             DEFINITION_COLUMNS, definition_rows(METHOD_DEFINITIONS)),
            ("DEFINITIONS — per-case surface error columns",
             DEFINITION_COLUMNS, definition_rows(ERROR_DEFINITIONS)),
            ("DEFINITIONS — improvement columns",
             DEFINITION_COLUMNS, definition_rows(IMPROVEMENT_DEFINITIONS)),
            ("DEFINITIONS — across-all-cases columns",
             DEFINITION_COLUMNS, definition_rows(SUMMARY_DEFINITIONS)),
        ]),
        timing_sheet(timing_rows, step_rows),
    ]
    return {"sheets": sheets, "log": log, "rows": rows,
            "improvements": improvements, "summary": summary,
            "timing_rows": timing_rows, "step_rows": step_rows,
            "cases": len(cases)}


def discover_cases(experiment_root: str) -> List[Dict[str, str]]:
    """One entry per run folder under ``Overall_Performance``."""
    return _discover_cases(experiment_root, RUNS_SUBDIR, DATASET_SUBDIR)


def run_analysis(repository_root: str, write_scenes: bool = True,
                 progress=None) -> Dict[str, Any]:
    """Analyse every case and write the workbook. Returns the report + its path."""
    from .workbook import write_workbook                      # noqa: PLC0415

    experiment_root = os.path.join(repository_root, EXPERIMENT_DIR)
    report = build_report(experiment_root, write_scenes=write_scenes,
                          progress=progress)
    output = os.path.join(experiment_root, RUNS_SUBDIR, WORKBOOK_NAME)
    written, notes = write_workbook(output, report["sheets"])
    report["workbook"] = written
    report["log"].extend(notes)
    try:
        report["workbook_relative"] = os.path.relpath(written, repository_root)
    except ValueError:
        report["workbook_relative"] = written
    return report
