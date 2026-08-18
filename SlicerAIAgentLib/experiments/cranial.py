"""CranialImplantPlanning: DSC / HD95 / bDSC against the surgeon's ground truth.

Scores every saved run under ``Experiments/CranialImplantPlanning/Overall_Performance/``
by the three metrics of the AutoImplant 2021 challenge (Li et al., *Medical Image
Analysis* 88 (2023) 102865, Section 3.3), writes one workbook beside the runs,
and writes a per-case colour error map into the run's own ``Statistic/scene/`` --
splicing it into that run's ``scene.mrml`` in place, exactly as :mod:`orbital`
does.

The three metrics, in the paper's own terms:

``DSC``
    Standard Dice over the implant volumes.
``HD95``
    95th percentile of the symmetric surface distance, in millimetres.
``bDSC``
    Dice restricted to the implant BORDERS. The paper's Eq. (1) defines the
    border of an implant ``I`` as the voxels of ``I`` whose Euclidean distance to
    the *defective skull* ``S`` is at most ``t``, with ``t = 10``. Both the ground
    truth and the prediction are restricted to the same band, then Dice is taken
    as usual. It exists because "implant borders should be emphasized, since
    borders largely determine the quality of fit, such as the transition between
    the skull and implant", and because it is "less affected by the overall
    implant thickness".

Four facts about this data decided the implementation, and each of them would
have produced a plausible wrong number if assumed instead of checked:

* **The prediction file holds TWO segments.** ``Cranial Implant Result.seg.nrrd``
  is one shared labelmap with ``Skull`` = 1 and ``Implant`` = 2. Reading it as
  "non-zero" would score the ground-truth implant against the whole skull -- 320k
  voxels against 2.1M -- and report a DSC near 0.2 that reads like a pipeline
  failure rather than a coding error. Segments are resolved by NAME, from the
  ``Segment<N>_Name`` / ``Segment<N>_LabelValue`` header fields, because
  ``Implant = 2`` is a convention this data happens to hold and nothing enforces.
* **The defective skull is that same file's ``Skull`` segment**, not
  ``Cranial_Segmentation.seg.nrrd``. The latter is the COMPLETE skull, segmented
  from the CT before the defect was cut: between 87% and 99% of every ground-truth
  implant lies *inside* it. The ``Skull`` segment's intersection with the ground
  truth is exactly 0 voxels in all 100 cases -- it is the skull with the hole,
  which is what Eq. (1) means by ``S``. Using the complete skull would put the
  entire implant inside the border band and turn bDSC into DSC.
* **Ground truth and prediction share a grid**, byte for byte, in every case, so
  every voxelwise measure here is exact -- no resampling, no interpolation of a
  binary mask.
* **Spacing is per case and anisotropic** (in-plane 0.38--0.61 mm across 58
  distinct values, slices always 0.75 mm). Nothing here hard-codes a voxel
  volume, and the surface distances are computed with that spacing.

Shape follows :mod:`orbital`: pure numpy/scipy statistics with no Slicer import at
module level, and a Slicer-only middle where ``slicer``/``vtk`` are imported
lazily inside the functions that need them, so
``scripts/check_cranial_analysis.py`` can exercise the arithmetic outside Slicer
against the real runs. The scene machinery -- meshing, the distance filter, the
write gate and the ``scene.mrml`` splicer -- is IMPORTED from :mod:`orbital`
rather than copied: it is the most dangerous code in the experiments package (it
edits a saved run in place) and a second copy of it would be a second thing to
keep correct.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import orbital
from .run_timing import collect_timing, discover_cases as _discover_cases, timing_sheet

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

EXTENSION_NAME = "CranialImplantPlanning"
EXPERIMENT_DIR = os.path.join("Experiments", EXTENSION_NAME)
RUNS_SUBDIR = "Overall_Performance"
DATASET_SUBDIR = "Dataset"
WORKBOOK_NAME = "CranialImplantPlanning_summary.xlsx"

#: Both files live in the run's own ``Statistic/scene/`` -- unlike the orbital
#: procedure, whose ground truth sits under ``Dataset/<subject>/``. The names
#: contain spaces because that is how the run saved them.
GROUND_TRUTH_FILE = "Ground Truth.seg.nrrd"
RESULT_FILE = "Cranial Implant Result.seg.nrrd"

#: Segment names, resolved to label values per case (see the module docstring).
GROUND_TRUTH_SEGMENT = "Ground Truth"
IMPLANT_SEGMENT = "Implant"
SKULL_SEGMENT = "Skull"

#: AutoImplant 2021 Eq. (1): "t = 10 is a pre-defined distance at which the
#: voxels in an implant I are considered as borders". The paper measures it on
#: the voxel grid, so this is in VOXELS and reproduces the published metric.
BORDER_DISTANCE_VOXELS = 10.0

#: The same band in millimetres, reported beside it. The voxel form is faithful
#: but not comparable across cases here: 10 voxels is 3.8 mm in-plane on the
#: finest case and 7.5 mm through-plane on every case, so the band's physical
#: size moves with the acquisition. Both are reported for the same reason
#: shoulder.py reports two cone denominators -- they answer different questions
#: and picking one silently would answer neither.
BORDER_DISTANCE_MM = 5.0

#: Margin around the implants' bounding box for the cropped metric window. Must
#: be >= BORDER_DISTANCE_VOXELS for the border mask to be exact (see
#: :func:`metric_window`).
METRIC_MARGIN_VOXELS = 16

#: The tolerance the two one-directional surface shares are quoted at. 2 mm is
#: the figure a cranioplasty is judged by clinically, and it is far enough above
#: the voxel size here (0.38-0.75 mm) that it is not measuring the sampling.
SURFACE_TOLERANCE_MM = 2.0

#: Error-map colour scale, fixed so two cases are comparable by eye. Larger than
#: orbital's 3 mm because a cranial implant's HD95 runs to several millimetres:
#: a 3 mm ceiling would saturate most of every map.
COLOR_MAX_MM = 5.0
COLOR_TABLE_NAME = "CIP_ImplantError_0_%dmm" % int(COLOR_MAX_MM)

#: The ONE node this analysis adds to a run's scene. Deliberately one: the run
#: already saved its own "Ground Truth.seg.nrrd" and its scene.mrml references
#: it, so a reference model of the ground truth would be the same surface twice.
ERROR_MAP_NAME = "ErrorMap_Implant_vs_GT"


# ---------------------------------------------------------------------------
# Reading the data (pure)
# ---------------------------------------------------------------------------

def segment_label_values(path: str) -> Dict[str, int]:
    """``{segment name: label value}`` from a .seg.nrrd's custom header fields.

    ``volume_io.read_nrrd`` deliberately drops every ``key:=value`` line, so the
    segment table is not in the header it returns and has to be read here. That
    is what makes it possible to ask for the segment by NAME -- the alternative,
    hard-coding ``Implant == 2``, is a convention this data happens to hold in
    every case and that nothing in the format enforces.
    """
    try:
        with open(path, "rb") as handle:
            blob = handle.read(1 << 17)
    except OSError:
        return {}
    end = blob.find(b"\n\n")
    header = blob[: end if end > 0 else len(blob)].decode("utf-8", "replace")

    names: Dict[str, str] = {}
    labels: Dict[str, int] = {}
    for line in header.splitlines():
        if ":=" not in line:
            continue
        key, _, value = line.partition(":=")
        key = key.strip()
        if key.endswith("_Name"):
            names[key[: -len("_Name")]] = value.strip()
        elif key.endswith("_LabelValue"):
            try:
                labels[key[: -len("_LabelValue")]] = int(value.strip())
            except ValueError:
                continue
    return {names[prefix]: labels[prefix] for prefix in names if prefix in labels}


def spacing_mm(ijk_to_ras: Sequence[Sequence[float]]) -> np.ndarray:
    """mm per voxel along each ARRAY axis, in the (k, j, i) order read_nrrd uses.

    ``read_nrrd`` returns IJK->RAS, whose column *c* is the direction vector of
    axis *c* scaled by its spacing -- so the spacing is that column's norm. Taking
    the inverse matrix instead yields voxels-per-millimetre, which is a plausible
    looking number that scales every distance by ~2.6x on this data and leaves
    DSC (dimensionless) untouched, so only HD95 shows it.
    """
    columns = np.asarray(ijk_to_ras, dtype=float)[:3, :3]
    return np.array([np.linalg.norm(columns[:, 2]),
                     np.linalg.norm(columns[:, 1]),
                     np.linalg.norm(columns[:, 0])])


def voxel_volume_mm3(ijk_to_ras: Sequence[Sequence[float]]) -> float:
    return float(np.prod(spacing_mm(ijk_to_ras)))


def _read_mask(path: str, segment: str,
               fallback_label: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
    """``(boolean mask of one named segment, ijk_to_ras)``."""
    from .volume_io import read_nrrd                            # noqa: PLC0415

    array, ijk_to_ras, _header = read_nrrd(path)
    labels = segment_label_values(path)
    label = labels.get(segment, fallback_label)
    if label is None:
        raise RuntimeError(
            "%s has no segment named %r (it has: %s)"
            % (os.path.basename(path), segment,
               ", ".join(sorted(labels)) or "none"))
    return array == label, ijk_to_ras


# ---------------------------------------------------------------------------
# The metrics (pure)
# ---------------------------------------------------------------------------

def dice(a: np.ndarray, b: np.ndarray) -> Optional[float]:
    total = int(a.sum()) + int(b.sum())
    if total == 0:
        return None
    return 2.0 * float(np.logical_and(a, b).sum()) / total


def jaccard(a: np.ndarray, b: np.ndarray) -> Optional[float]:
    union = int(np.logical_or(a, b).sum())
    if union == 0:
        return None
    return float(np.logical_and(a, b).sum()) / union


def metric_window(mask: np.ndarray, margin: int = METRIC_MARGIN_VOXELS
                  ) -> Tuple[slice, ...]:
    """The sub-box every measurement is computed in. Exact, not an approximation.

    Both implants lie inside ``bbox(gt | pred)``, so the nearest surface voxel of
    one to the other is inside it too -- surface distances are unchanged by the
    crop. The border mask needs only the predicate "distance to the skull <= t":
    any voxel satisfying it has its nearest skull voxel within ``t``, hence inside
    the box once the margin is at least ``t``, so the predicate is reproduced
    exactly even though distances beyond ``t`` may come out larger than the truth.

    It is worth the care: uncropped, the three distance transforms run over the
    whole volume and the batch takes half an hour instead of five minutes.
    """
    index = np.argwhere(mask)
    if index.size == 0:
        return tuple(slice(0, size) for size in mask.shape)
    low = np.maximum(index.min(axis=0) - margin, 0)
    high = np.minimum(index.max(axis=0) + margin + 1, mask.shape)
    return tuple(slice(int(a), int(b)) for a, b in zip(low, high))


def surface_mask(mask: np.ndarray) -> np.ndarray:
    """Voxels of ``mask`` that touch its complement across a face (6-neighbour)."""
    from scipy import ndimage                                   # noqa: PLC0415

    structure = ndimage.generate_binary_structure(3, 1)
    return np.logical_and(
        mask, np.logical_not(ndimage.binary_erosion(mask, structure)))


def surface_distances_mm(a: np.ndarray, b: np.ndarray,
                         spacing: Sequence[float]) -> Tuple[np.ndarray, np.ndarray]:
    """``(distances from b's surface to a's, distances from a's surface to b's)``.

    Voxel surfaces, not meshes -- this is the definition the challenge's own
    evaluation uses, and it keeps HD95 in the same world as DSC and bDSC, which
    are voxel measures by construction. The mesh-based figure is reported
    separately as ``map_hd95_mm`` so the two can be seen to agree.
    """
    from scipy import ndimage                                   # noqa: PLC0415

    a_surface, b_surface = surface_mask(a), surface_mask(b)
    if not a_surface.any() or not b_surface.any():
        return np.array([]), np.array([])
    to_a = ndimage.distance_transform_edt(
        np.logical_not(a_surface), sampling=spacing)[b_surface]
    to_b = ndimage.distance_transform_edt(
        np.logical_not(b_surface), sampling=spacing)[a_surface]
    return to_a, to_b


def border_mask(skull: np.ndarray, threshold: float,
                spacing: Optional[Sequence[float]] = None) -> np.ndarray:
    """AutoImplant Eq. (1): voxels within ``threshold`` of the defective skull.

    ``spacing`` None gives the paper's voxel-unit distance; passing the voxel
    spacing gives the same band in millimetres.
    """
    from scipy import ndimage                                   # noqa: PLC0415

    distance = ndimage.distance_transform_edt(
        np.logical_not(skull), sampling=spacing)
    return distance <= threshold


def case_metrics(ground_truth: np.ndarray, implant: np.ndarray,
                 skull: np.ndarray, ijk_to_ras: Sequence[Sequence[float]]
                 ) -> Dict[str, Any]:
    """Every voxel metric for one case. Pure: numpy + scipy, no Slicer."""
    spacing = spacing_mm(ijk_to_ras)
    voxel_mm3 = float(np.prod(spacing))

    row: Dict[str, Any] = {
        "dsc": _round(dice(ground_truth, implant)),
        "jaccard": _round(jaccard(ground_truth, implant)),
        "gt_voxels": int(ground_truth.sum()),
        "implant_voxels": int(implant.sum()),
        "intersection_voxels": int(np.logical_and(ground_truth, implant).sum()),
        "gt_volume_mm3": _round(float(ground_truth.sum()) * voxel_mm3, 1),
        "implant_volume_mm3": _round(float(implant.sum()) * voxel_mm3, 1),
        "voxel_volume_mm3": _round(voxel_mm3, 6),
        "spacing_mm": " x ".join("%.4f" % value for value in spacing[::-1]),
        "skull_voxels": int(skull.sum()),
        "gt_in_skull_voxels": int(np.logical_and(ground_truth, skull).sum()),
    }
    if row["gt_volume_mm3"] and row["implant_volume_mm3"]:
        row["volume_ratio"] = _round(
            row["implant_volume_mm3"] / row["gt_volume_mm3"])

    window = metric_window(np.logical_or(ground_truth, implant))
    gt_box, implant_box, skull_box = (ground_truth[window], implant[window],
                                      skull[window])

    for suffix, threshold, sampling in (
            ("", BORDER_DISTANCE_VOXELS, None),
            ("_mm", BORDER_DISTANCE_MM, spacing)):
        band = border_mask(skull_box, threshold, sampling)
        gt_border = np.logical_and(gt_box, band)
        implant_border = np.logical_and(implant_box, band)
        row["bdsc" + suffix] = _round(dice(gt_border, implant_border))
        row["border_gt_voxels" + suffix] = int(gt_border.sum())
        row["border_implant_voxels" + suffix] = int(implant_border.sum())

    implant_to_gt, gt_to_implant = surface_distances_mm(gt_box, implant_box, spacing)
    if implant_to_gt.size and gt_to_implant.size:
        both = np.concatenate([implant_to_gt, gt_to_implant])
        row["hd95_mm"] = _round(float(np.percentile(both, 95)), 3)
        row["assd_mm"] = _round(float(both.mean()), 3)
        row["hd_max_mm"] = _round(float(both.max()), 3)
        row["median_surface_mm"] = _round(float(np.median(both)), 3)
        row["mean_implant_to_gt_mm"] = _round(float(implant_to_gt.mean()), 3)
        row["mean_gt_to_implant_mm"] = _round(float(gt_to_implant.mean()), 3)
        # The two ONE-DIRECTIONAL shares, and they are the reason this table has
        # more than three columns. On the worst cases here the prediction sits
        # within a few mm of the truth everywhere it exists (0.0% of it is more
        # than 20 mm out) while half the ground-truth surface has no prediction
        # near it at all: the implant UNDER-COVERS a much larger defect rather
        # than being misplaced. HD95 pools both directions, so it reports that as
        # one large number and cannot say which way it went. These two can, and
        # they are the paper's own "Completeness" and "False Positive Area"
        # criteria measured on the surface.
        row["gt_covered_%dmm_pct" % int(SURFACE_TOLERANCE_MM)] = _round(
            100.0 * float((gt_to_implant <= SURFACE_TOLERANCE_MM).mean()), 2)
        row["implant_on_gt_%dmm_pct" % int(SURFACE_TOLERANCE_MM)] = _round(
            100.0 * float((implant_to_gt <= SURFACE_TOLERANCE_MM).mean()), 2)
    return row


def _round(value: Optional[float], digits: int = 4) -> Optional[float]:
    try:
        if value is None or np.isnan(value):
            return None
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# The colour map (Slicer)
# ---------------------------------------------------------------------------

def _color_table_node(scene_dir: str):
    """Green -> yellow -> orange -> red over 0..COLOR_MAX_MM.

    A near-copy of orbital's, and it cannot simply call it: that one bakes
    orbital's own 3 mm ceiling and table name into the node it builds, and a
    cranial map on a 3 mm scale is red almost everywhere. The colour STOPS and
    the 256-entry interpolation are shared from orbital so the two procedures'
    maps read alike.
    """
    import slicer                                               # noqa: PLC0415

    node = slicer.mrmlScene.AddNewNodeByClass(
        "vtkMRMLColorTableNode", COLOR_TABLE_NAME)
    node.SetTypeToUser()
    node.SetNumberOfColors(orbital.COLOR_TABLE_SIZE)
    stops = list(orbital.COLOR_STOPS)
    for index in range(orbital.COLOR_TABLE_SIZE):
        position = index / float(orbital.COLOR_TABLE_SIZE - 1)
        lower, upper = stops[0], stops[-1]
        for first, second in zip(stops, stops[1:]):
            if first[0] <= position <= second[0]:
                lower, upper = first, second
                break
        span = (upper[0] - lower[0]) or 1.0
        weight = (position - lower[0]) / span
        rgb = [lower[1][c] + weight * (upper[1][c] - lower[1][c]) for c in range(3)]
        node.SetColor(index, "%.2f mm" % (position * COLOR_MAX_MM),
                      rgb[0], rgb[1], rgb[2], 1.0)
    orbital._pin_storage(node, os.path.join(scene_dir, COLOR_TABLE_NAME + ".ctbl"))
    return node


def _surface_from_mask(mask: np.ndarray, ijk_to_ras: Sequence[Sequence[float]],
                       name: str):
    """Mesh ONE boolean mask, through orbital's pipeline, from memory.

    Deliberately not ``orbital._load_segmentation_surface``. That reads the file
    and meshes ``GetNthSegmentID(0)`` -- the FIRST segment -- and segment 0 of
    ``Cranial Implant Result.seg.nrrd`` is ``Skull``, not ``Implant``. Pointing it
    at that file produces a map of the 2.1-million-voxel skull: the wrong surface
    entirely, and by a wide margin the slowest thing in the loop.

    Taking the array instead means the surface is built from exactly the segment
    :func:`_read_mask` resolved by name, the file is not read a second time, and
    the mask is cropped to its own bounding box first -- which is what makes this
    fast, since a cranial implant occupies a small corner of its volume.
    """
    import slicer                                               # noqa: PLC0415
    import vtk                                                  # noqa: PLC0415

    bounds = orbital.crop_bounds(mask.shape, np.nonzero(mask))
    if bounds is None:
        raise RuntimeError("%s is empty" % name)
    (k0, k1), (j0, j1), (i0, i1) = bounds
    cropped = np.ascontiguousarray(mask[k0:k1, j0:j1, i0:i1].astype(np.uint8))
    rows = [[float(value) for value in row] for row in np.asarray(ijk_to_ras)]
    shifted = orbital.cropped_ijk_to_ras(rows, (i0, j0, k0))

    labelmap = None
    segmentation = None
    try:
        labelmap = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLLabelMapVolumeNode", name + "_labelmap")
        slicer.util.updateVolumeFromArray(labelmap, cropped)
        matrix = vtk.vtkMatrix4x4()
        for row in range(4):
            for column in range(4):
                matrix.SetElement(row, column, shifted[row][column])
        labelmap.SetIJKToRASMatrix(matrix)

        segmentation = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLSegmentationNode", name)
        segmentation.CreateDefaultDisplayNodes()
        slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(
            labelmap, segmentation)
        return orbital._segment_surface(segmentation)
    finally:
        # Both are scratch. Nothing this function makes survives it, so the
        # ground truth never appears in the scene the user is looking at.
        for node in (segmentation, labelmap):
            if node is not None:
                orbital._drop_node(node)


def _error_model_node(polydata, name: str, color_node, scene_dir: str):
    """The map, on a MANUAL 0..COLOR_MAX_MM scale.

    Manual and not UseData, for orbital's reason: an auto range rescales per case,
    so a 0.5 mm case and a 5 mm case render with the identical spread of colour
    and the one thing a map is for stops working.
    """
    import slicer                                               # noqa: PLC0415
    import vtk                                                  # noqa: PLC0415

    model = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", name)
    model.SetAndObservePolyData(polydata)
    model.CreateDefaultDisplayNodes()
    display = model.GetDisplayNode()
    display.SetVisibility(True)
    display.SetVisibility2D(True)
    display.SetScalarVisibility(True)
    display.SetActiveScalarName(orbital.DISTANCE_ARRAY)
    display.SetActiveAttributeLocation(vtk.vtkAssignAttribute.POINT_DATA)
    display.SetAndObserveColorNodeID(color_node.GetID())
    display.SetScalarRangeFlag(slicer.vtkMRMLDisplayNode.UseManualScalarRange)
    display.SetScalarRange(0.0, COLOR_MAX_MM)
    orbital._pin_storage(model, os.path.join(scene_dir, name + ".vtp"))
    return model


# ---------------------------------------------------------------------------
# One case
# ---------------------------------------------------------------------------

def ground_truth_path(case: Dict[str, str]) -> str:
    return os.path.join(case.get("scene_dir", ""), GROUND_TRUTH_FILE)


def result_path(case: Dict[str, str]) -> str:
    return os.path.join(case.get("scene_dir", ""), RESULT_FILE)


def case_is_scorable(case: Dict[str, str]) -> bool:
    return os.path.isfile(ground_truth_path(case)) and os.path.isfile(result_path(case))


def analyse_case(case: Dict[str, str], write_scenes: bool = True) -> Dict[str, Any]:
    """Metrics for one run, and (optionally) its colour error map.

    The metrics are read straight from the two labelmaps -- no Slicer needed. The
    map is a second, independent pass through orbital's meshing pipeline, and it
    is deliberately the PREDICTED implant that is coloured (by its distance to the
    ground-truth surface), because the question a reader brings to a cranioplasty
    map is "where is the implant I produced wrong", not "which part of the truth
    did it miss".
    """
    scene_dir = case["scene_dir"]
    label = case.get("subject") or case["run"]
    notes: List[str] = []
    row: Dict[str, Any] = {"case": label, "run": case["run"]}

    gt_file, result_file = ground_truth_path(case), result_path(case)
    for path in (gt_file, result_file):
        if not os.path.isfile(path):
            raise RuntimeError("missing %s" % os.path.basename(path))

    ground_truth, gt_matrix = _read_mask(gt_file, GROUND_TRUTH_SEGMENT, 1)
    implant, matrix = _read_mask(result_file, IMPLANT_SEGMENT)
    skull, _ = _read_mask(result_file, SKULL_SEGMENT)

    if ground_truth.shape != implant.shape:
        raise RuntimeError(
            "the ground truth is %s and the result is %s -- different grids"
            % (ground_truth.shape, implant.shape))
    # A silent frame mismatch is the failure this whole family of metrics is
    # blind to: two masks on differently-placed grids of the same SHAPE would
    # score normally and mean nothing. The grids are identical in this data, so
    # a disagreement is a defect, not a case to resample.
    if not np.allclose(np.asarray(gt_matrix), np.asarray(matrix), atol=1e-6):
        raise RuntimeError(
            "the ground truth and the result are on the same-shaped grid but "
            "not the same one -- their IJK->RAS matrices differ")

    row.update(case_metrics(ground_truth, implant, skull, matrix))

    if not write_scenes:
        return {"rows": [row], "notes": notes, "models": []}

    scene_nodes: List[Any] = []
    error_models: List[str] = []
    try:
        # Built from the arrays already resolved by segment NAME, not by
        # re-reading the files -- see _surface_from_mask for why that matters.
        gt_surface = _surface_from_mask(
            ground_truth, matrix, "GroundTruthSurface_%s" % label)
        implant_surface = _surface_from_mask(
            implant, matrix, "ImplantSurface_%s" % label)

        # The prediction is passed FIRST, so the mesh that comes back carrying
        # the distances is the predicted implant rather than the ground truth.
        mesh, implant_values, gt_values = orbital._surface_distances(
            implant_surface, gt_surface)
        statistics = orbital.distance_statistics(implant_values, gt_values)
        # The map's own hd95, beside the voxel one. They measure the same thing
        # through different objects -- a smoothed triangle mesh against a voxel
        # surface -- so they agree to a fraction of a voxel and a reader can see
        # that rather than take it on trust.
        row["map_hd95_mm"] = statistics.get("hd95_mm")
        row["map_assd_mm"] = statistics.get("assd_mm")

        color_node = _color_table_node(scene_dir)
        scene_nodes.append(color_node)
        # NO ground-truth model. Orbital adds one because its ground truth lives
        # outside the run, under Dataset/<subject>/, so the run's scene has never
        # seen it. Here the run saved "Ground Truth.seg.nrrd" itself and its own
        # scene.mrml already references it -- adding a second copy as a .vtp
        # would put the same surface in the scene twice.
        scene_nodes.append(_error_model_node(
            orbital._named_distance_surface(mesh, implant_values),
            ERROR_MAP_NAME, color_node, scene_dir))
        error_models.append(ERROR_MAP_NAME)

        if orbital._write_error_scene(scene_dir, scene_nodes, notes):
            spliced = orbital._splice_into_scene(
                os.path.join(scene_dir, orbital.SCENE_FILE),
                os.path.join(scene_dir, orbital.ERROR_SCENE_NAME),
                error_models, notes)
            if not spliced:
                notes.append("the error map was NOT added to %s"
                             % orbital.SCENE_FILE)
        else:
            notes.append("%s was left untouched -- the error-map files did not "
                         "all get written" % orbital.SCENE_FILE)
    except Exception as exc:                      # noqa: BLE001 - fail per case
        notes.append("%s: the error map failed (%s)" % (label, exc))
        row["map_error"] = str(exc)
        logger.debug("Cranial error map failed for %s", label, exc_info=True)
    finally:
        for node in reversed(scene_nodes):
            orbital._drop_node(node)

    return {"rows": [row], "notes": notes, "models": error_models}


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------

GT_COVERED_COLUMN = "gt_covered_%dmm_pct" % int(SURFACE_TOLERANCE_MM)
IMPLANT_ON_GT_COLUMN = "implant_on_gt_%dmm_pct" % int(SURFACE_TOLERANCE_MM)

CASE_COLUMNS = [
    "case", "dsc", "bdsc", "hd95_mm", "assd_mm", "bdsc_mm", "jaccard",
    GT_COVERED_COLUMN, IMPLANT_ON_GT_COLUMN,
    "median_surface_mm", "hd_max_mm", "mean_implant_to_gt_mm",
    "mean_gt_to_implant_mm", "map_hd95_mm", "map_assd_mm",
    "gt_volume_mm3", "implant_volume_mm3", "volume_ratio",
    "gt_voxels", "implant_voxels", "intersection_voxels",
    "border_gt_voxels", "border_implant_voxels",
    "border_gt_voxels_mm", "border_implant_voxels_mm",
    "skull_voxels", "gt_in_skull_voxels",
    "voxel_volume_mm3", "spacing_mm", "error", "map_error", "run",
]

SUMMARY_COLUMNS = ["metric", "cases", "mean", "median", "std", "min",
                   "p25", "p75", "max"]

#: What the cohort is summarised over. Mean AND median, because the ground-truth
#: volumes span a factor of 27 across these cases and a single outlier moves the
#: mean of a 100-case cohort visibly.
SUMMARY_METRICS = (
    ("DSC", "dsc"),
    ("bDSC (t = %d voxels)" % int(BORDER_DISTANCE_VOXELS), "bdsc"),
    ("bDSC (t = %.1f mm)" % BORDER_DISTANCE_MM, "bdsc_mm"),
    ("HD95 (mm)", "hd95_mm"),
    ("ASSD (mm)", "assd_mm"),
    ("GT surface covered <=%dmm (%%)" % int(SURFACE_TOLERANCE_MM), GT_COVERED_COLUMN),
    ("Implant surface on GT <=%dmm (%%)" % int(SURFACE_TOLERANCE_MM),
     IMPLANT_ON_GT_COLUMN),
    ("Jaccard", "jaccard"),
    ("Implant / GT volume", "volume_ratio"),
)


def summary_rows(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Distribution of each metric over the cohort. Pure."""
    summary: List[Dict[str, Any]] = []
    for title, key in SUMMARY_METRICS:
        values = np.array([row[key] for row in rows
                           if isinstance(row.get(key), (int, float))], dtype=float)
        if values.size == 0:
            summary.append({"metric": title, "cases": 0})
            continue
        summary.append({
            "metric": title,
            "cases": int(values.size),
            "mean": _round(float(values.mean())),
            "median": _round(float(np.median(values))),
            "std": _round(float(values.std(ddof=1))) if values.size > 1 else None,
            "min": _round(float(values.min())),
            "p25": _round(float(np.percentile(values, 25))),
            "p75": _round(float(np.percentile(values, 75))),
            "max": _round(float(values.max())),
        })
    return summary


DEFINITION_COLUMNS = ["term", "definition"]

METHOD_DEFINITIONS = [
    ("Source", "AutoImplant 2021 challenge, Li et al., Medical Image Analysis 88 "
               "(2023) 102865, Section 3.3 'Evaluation and ranking'. The three "
               "metrics and the border definition are the paper's; the numbers "
               "here are computed by this module from each run's saved files."),
    ("What is compared", "'Ground Truth.seg.nrrd' (segment 'Ground Truth') "
                         "against 'Cranial Implant Result.seg.nrrd' (segment "
                         "'Implant'), both taken from the run's own "
                         "Statistic/scene/ folder."),
    ("Segment selection", "Segments are resolved by NAME from the .seg.nrrd "
                          "header, never by label value. The result file is one "
                          "shared labelmap holding BOTH 'Skull' (1) and "
                          "'Implant' (2); reading it as non-zero would score the "
                          "implant against the whole skull."),
    ("Grid", "The ground truth and the result share an identical grid in every "
             "case, so all voxel measures are exact -- nothing is resampled and "
             "no binary mask is ever interpolated."),
    ("Spacing", "Read per case from the file. In-plane spacing varies between "
                "cases (0.38-0.61 mm here) while slices are 0.75 mm, so voxel "
                "volume varies by a factor of 2.6 and is never assumed."),
    ("Defective skull", "Segment 'Skull' inside the result file -- the skull with "
                        "the defect cut out, whose intersection with the ground "
                        "truth implant is 0 voxels. NOT "
                        "'Cranial_Segmentation.seg.nrrd', which is the complete "
                        "skull segmented before the cut and contains 87-99% of "
                        "the ground-truth implant."),
    ("READ THIS BEFORE QUOTING bDSC", "bDSC is not 'DSC near the edge of the "
                                      "implant'. It is DSC over the part of each "
                                      "implant lying within t of the SKULL, i.e. "
                                      "the transition where the implant seats. It "
                                      "is usually higher than DSC and is reported "
                                      "beside it, never instead of it."),
]

METRIC_DEFINITIONS = [
    ("dsc", "Dice similarity coefficient between the ground-truth implant and "
            "the predicted implant: 2|A n B| / (|A| + |B|). Dimensionless, 1 is "
            "a perfect match."),
    ("bdsc", "Border DSC, AutoImplant Eq. (1) with t = %d VOXELS: both implants "
             "are restricted to voxels whose Euclidean distance to the defective "
             "skull is at most t, then Dice is taken. This is the published "
             "metric." % int(BORDER_DISTANCE_VOXELS)),
    ("bdsc_mm", "The same measure with the band defined in millimetres "
                "(t = %.1f mm). Reported because 10 voxels is a different "
                "physical distance in-plane than through-plane, and different "
                "again between cases." % BORDER_DISTANCE_MM),
    ("hd95_mm", "95th percentile of the symmetric surface distance in "
                "millimetres, over voxel surfaces (a foreground voxel with a "
                "face-neighbour outside the mask). Both directions are pooled "
                "before the percentile is taken."),
    ("READ THIS BEFORE QUOTING HD95", "Quote the MEDIAN over the cohort, not the "
                                      "mean. HD95 pools both directions, so a "
                                      "case where the implant is accurate but "
                                      "covers only half of a large defect scores "
                                      "in the hundreds of millimetres and drags "
                                      "the mean far above the typical case. On "
                                      "this cohort the median is ~2 mm and the "
                                      "mean ~8. The two one-directional columns "
                                      "below say which way any such case went."),
    (GT_COVERED_COLUMN, "Percentage of the GROUND TRUTH's surface with some "
                        "predicted implant within %.0f mm -- COMPLETENESS, the "
                        "paper's 'amount of the defect area covered by the "
                        "implant'. A low value means the implant is too small or "
                        "stops short, whatever DSC says."
                        % SURFACE_TOLERANCE_MM),
    (IMPLANT_ON_GT_COLUMN, "Percentage of the PREDICTED implant's surface within "
                           "%.0f mm of the ground truth -- the complement, close "
                           "to the paper's 'False Positive Area'. A low value "
                           "means the implant extends where no implant belongs. "
                           "Read the two together: on this data they are strongly "
                           "asymmetric, and only the pair distinguishes 'too "
                           "small' from 'in the wrong place'."
                           % SURFACE_TOLERANCE_MM),
    ("assd_mm", "Average symmetric surface distance in millimetres, over the same "
                "pooled distance set."),
    ("hd_max_mm", "The maximum of that set -- the true Hausdorff distance. "
                  "Reported as a diagnostic only: a single stray voxel moves it "
                  "arbitrarily and moves hd95_mm not at all. Quote hd95_mm."),
    ("mean_implant_to_gt_mm", "Mean distance from the predicted implant's surface "
                              "to the ground truth's. Larger than its partner "
                              "means the prediction overshoots."),
    ("mean_gt_to_implant_mm", "Mean distance from the ground truth's surface to "
                              "the prediction's. Larger than its partner means "
                              "the prediction misses part of the truth."),
    ("map_hd95_mm", "hd95 recomputed from the smoothed triangle MESHES built for "
                    "the colour map, rather than from voxel surfaces. It is here "
                    "so the map and the table can be seen to agree; hd95_mm is "
                    "the figure to quote."),
    ("volume_ratio", "Predicted implant volume / ground-truth implant volume. 1.0 "
                     "is equal bulk; it says nothing about placement."),
    ("border_gt_voxels", "Size of the ground truth's border band, in voxels -- how "
                         "much of the implant bDSC actually scored."),
    ("gt_in_skull_voxels", "Ground-truth voxels inside the defective skull. Expected "
                           "to be 0; anything else means the skull segment is not "
                           "the defective one and bDSC is measuring the wrong band."),
    ("spacing_mm", "Voxel size as i x j x k in millimetres, for this case."),
    ("error", "Set when the case could not be scored at all; the row's metrics are "
              "then absent."),
    ("map_error", "Set when the metrics were computed but the colour map failed. "
                  "The metrics in that row are still valid."),
]


def definition_rows(pairs: Sequence[Tuple[str, str]]) -> List[Dict[str, Any]]:
    return [{"term": term, "definition": text} for term, text in pairs]


def discover_cases(experiment_root: str) -> List[Dict[str, str]]:
    return _discover_cases(experiment_root, RUNS_SUBDIR, DATASET_SUBDIR)


def build_report(experiment_root: str, write_scenes: bool = True,
                 progress=None) -> Dict[str, Any]:
    """Score every case. Fail-soft per case: one bad run does not cost the rest."""
    cases = discover_cases(experiment_root)
    rows: List[Dict[str, Any]] = []
    log: List[str] = []

    if write_scenes and cases:
        # saveScene serialises whatever is in the scene, so it must hold nothing
        # but this case's nodes. Cleared ONCE; each case then cleans up after
        # itself through _drop_node.
        import slicer                                           # noqa: PLC0415
        slicer.mrmlScene.Clear(0)

    for index, case in enumerate(cases):
        label = case.get("subject") or case["run"]
        if progress is not None:
            try:
                progress(index, len(cases), label)
            except Exception:
                logger.debug("Cranial progress callback failed", exc_info=True)
        # Logged BEFORE the work: a hard crash takes the report with it, so this
        # line is the only evidence of which case was in flight.
        logger.info("[Cranial] case %d/%d: %s", index + 1, len(cases), label)
        try:
            outcome = analyse_case(case, write_scenes=write_scenes)
        except Exception as exc:                  # noqa: BLE001
            log.append("%s: FAILED -- %s" % (label, exc))
            rows.append({"case": label, "run": case["run"], "error": str(exc)})
            continue
        rows.extend(outcome["rows"])
        log.extend(outcome["notes"])

    scored = [row for row in rows if isinstance(row.get("dsc"), (int, float))]
    summary = summary_rows(scored)
    timing_rows, step_rows = collect_timing(cases, log)

    sheets = [
        ("Implant accuracy", [
            ("One row per case. DSC and bDSC are dimensionless; every distance is "
             "in millimetres.", CASE_COLUMNS, rows),
            ("Across all %d scored cases" % len(scored), SUMMARY_COLUMNS, summary),
            ("DEFINITIONS -- how the measurement is made", DEFINITION_COLUMNS,
             definition_rows(METHOD_DEFINITIONS)),
            ("DEFINITIONS -- the per-case columns", DEFINITION_COLUMNS,
             definition_rows(METRIC_DEFINITIONS)),
        ]),
        timing_sheet(timing_rows, step_rows),
    ]
    return {"sheets": sheets, "log": log, "rows": rows, "summary": summary,
            "timing_rows": timing_rows, "step_rows": step_rows,
            "cases": len(cases), "scored": len(scored)}


def run_analysis(repository_root: str, write_scenes: bool = True,
                 progress=None) -> Dict[str, Any]:
    """Score every case and write the workbook beside the runs."""
    from .workbook import write_workbook                        # noqa: PLC0415

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
