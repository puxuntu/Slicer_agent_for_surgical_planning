"""PelvicFracturePlanning: how far the planned reduction is from the surgeon's.

Every run under ``Experiments/PelvicFracturePlanning/Overall_Performance/`` saved
three things into its own ``Statistic/scene/``:

``Fragment Reduction*.seg.nrrd``
    where the pipeline put every bone and fragment.
``Ground truth*.seg.nrrd``
    where the surgeon says they belong.
``Ground truth*.transforms.json``
    **the transform the surgeon applied to get from one to the other**, per
    piece, recorded at the moment the annotation was saved.

The third file is why this module does no registration. The reduction error of a
piece IS that transform, and it is recorded exactly: ``translation_magnitude_mm``
is the displacement, ``rotation_angle_deg`` the rotation, and ``matrix`` the whole
of it. Estimating them back out of the two segmentations -- which is what this
module did first, by ICP -- can only ever approach a number that is already
written down. (It did: on the saved runs the ICP answer and the recorded one
agree to 0.009-0.034 deg. That is a good reason to believe both, and no reason
at all to keep spending a hundred iterations per piece to re-derive one from the
other.)

So the transforms file is the source, and the segmentations are read only for
what it cannot say -- which is still worth reading, for four reasons:

* **Was the record written for THESE files?** A transforms file that is stale
  with respect to the segmentations beside it is the one failure this design has
  that ICP did not: ICP measured whatever was on disk, while a recorded number
  measures whatever was on disk *when it was recorded*. So the matrix is applied
  to the reduction's own surface and the distance to the ground truth's surface
  is measured (``transform_residual_mm``, 0.14-0.24 mm on the saved runs -- the
  two grids' sampling). This check is the whole reason ``verify`` defaults on.
* **How wrong is it at the bone?** ``displacement_mm`` is measured at ONE point,
  the piece's reference centroid, and a rigid body's displacement depends on
  which point you measure -- rotation moves the far end of a bone much further
  than its centre. ``point_error_*`` applies the recorded matrix to every surface
  point of the piece and reports how far each one travels. It is the number a
  surgeon reads, and it is arithmetic, not estimation.
* **What was NOT annotated.** The ground truth names fewer pieces than the
  reduction moves -- the surgeon only corrected some. The rest are listed rather
  than dropped, so it is visible how much of the procedure the table is silent
  about.
* **Are the two pieces the same object?** ``volume_ratio``, which is 1.000 to
  within half a percent when they are.

The record is also checked against ITSELF, which costs nothing and is free of the
segmentations: that ``matrix``'s rotation block is a proper rotation, that its
angle and axis are the ones the matrix actually encodes, and that it carries
``centroid_reduced_mm`` onto ``centroid_annotated_mm``. A hand-edited or
half-written record fails these; a wrong one that passes all three is a different
file's transform, which is what the residual above is for.

Slicer-free and Qt-free -- it is a JSON read and arithmetic over voxel grids --
so ``scripts/check_pelvic_analysis.py`` runs the whole analysis against the real
saved runs outside Slicer.
"""

from __future__ import annotations

import io
import json
import logging
import os
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import segmentation_io
from .run_timing import (canonical_step_id, collect_timing,
                         discover_cases as _discover_cases, timing_sheet)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

EXTENSION_NAME = "PelvicFracturePlanning"
EXPERIMENT_DIR = os.path.join("Experiments", EXTENSION_NAME)
RUNS_SUBDIR = "Overall_Performance"
DATASET_SUBDIR = "Dataset"
WORKBOOK_NAME = "PelvicFracturePlanning_summary.xlsx"

#: All three files live in the run's own ``Statistic/scene/``, named by the MRML
#: node they were saved from. Matched by PREFIX because Slicer's uniquifier
#: appends ``_1`` to the second node of a name -- ``Fragment Reduction_1`` on
#: case 0001, ``Fragment Reduction`` on case 0002 -- and by lower case because
#: the two runs disagree on ``Ground truth`` / ``Ground Truth``.
REDUCTION_PREFIXES = ("fragment reduction",)
TRUTH_PREFIXES = ("ground truth", "groundtruth", "ground_truth", "ground-truth")
SEGMENTATION_SUFFIX = ".seg.nrrd"
TRANSFORM_SUFFIX = ".transforms.json"


# ---------------------------------------------------------------------------
# How much the record has to agree with itself, and with the files beside it
# ---------------------------------------------------------------------------

#: ``matrix @ centroid_reduced`` vs ``centroid_annotated``. The record prints
#: centroids to four decimals, so the two can differ by a rounding step in each
#: of three coordinates and nothing more.
RECORD_TOLERANCE_MM = 5e-3

#: The record's ``rotation_angle_deg`` vs the angle its own ``matrix`` encodes.
RECORD_TOLERANCE_DEG = 1e-2

#: How far ``matrix``'s rotation block may be from orthonormal. It is printed to
#: nine decimals, so this is three orders of magnitude above the rounding and
#: still far below any real defect.
ORTHONORMAL_TOLERANCE = 1e-6

#: RMS distance from the transformed reduction surface to the ground-truth
#: surface, above which the record is not accepted as describing these two files.
#: The floor is the two grids' own sampling, a fraction of a voxel (0.14-0.24 mm
#: on the saved runs), so 1 mm is several times the noise and far below the
#: millimetres a stale record would show.
TRANSFORM_RESIDUAL_LIMIT_MM = 1.0

#: |volume_reduction / volume_truth - 1| above this and the two segments are not
#: treated as the same object. The saved runs sit at 0.0004-0.005: the same
#: object resampled onto two different grids.
VOLUME_TOLERANCE = 0.05

#: A displacement beyond this is not a reduction error -- a pelvis is ~250 mm
#: across, so a piece this far out means the record is not about this bone.
MAX_PLAUSIBLE_DISPLACEMENT_MM = 100.0

#: Points kept per surface. The reduction's surface carries ``point_error``, the
#: ground truth's is the tree the residual is measured against; both are capped
#: so a whole ilium (970k boundary voxels) does not cost a KD-tree of that size
#: for a number that is stable four digits earlier.
SURFACE_MAX_POINTS = 400000

#: Fewer surface points than this and the surface-derived columns are not
#: reported: a handful of voxels says nothing about a distance distribution.
MIN_SURFACE_POINTS = 50

#: The percentile of the symmetric surface distance that is quoted. The MAXIMUM
#: is reported beside it but must not lead: marching a boundary over a voxel grid
#: can always leave one stray voxel, and it moves the maximum by an arbitrary
#: amount and the 95th percentile not at all. Same rule, same reason, as
#: ``cranial.py``.
SURFACE_PERCENTILE = 95.0


# ---------------------------------------------------------------------------
# Timing phases: the extension's own five stages
# ---------------------------------------------------------------------------

#: Cookbook step -> phase. The extension's panel is five numbered buttons, and
#: each one has a tail of optional hand-adjustment steps that belong with it: the
#: surgeon's own correction of a template is part of building that template, not
#: a phase of its own. A step in none of these lands in an ``unassigned`` bucket
#: and is NAMED in the log -- a regenerated workflow that renumbers its steps
#: would otherwise make the phases silently shrink while still summing to
#: something plausible.
PHASE_STEPS = {
    "t0": ("cb_step_1", "cb_step_3"),
    "t1": ("cb_step_2",),
    "t2": ("cb_step_4", "cb_step_5", "cb_step_6", "cb_step_7", "cb_step_8",
           "cb_step_9"),
    "t3": ("cb_step_10", "cb_step_11", "cb_step_12", "cb_step_13"),
    "t4": ("cb_step_14", "cb_step_15", "cb_step_16", "cb_step_17"),
    "t5": ("cb_step_18", "cb_step_19", "cb_step_20", "cb_step_21"),
}
PHASE_ORDER = ("t0", "t1", "t2", "t3", "t4", "t5")
PHASE_TITLES = {
    "t0": "select the CT and frame the view",
    "t1": "Step 1: segment the pelvis",
    "t2": "Step 2: segment the fractures, and separate the fragments",
    "t3": "Step 3: generate the reduction template, and adjust it",
    "t4": "Step 4: register and reduce the fragments, and adjust them",
    "t5": "Step 5: plan the screws, and edit the trajectories",
}

_PHASE_OF_STEP = {canonical_step_id(step): phase
                  for phase, steps in PHASE_STEPS.items() for step in steps}


# ---------------------------------------------------------------------------
# Finding the three files
# ---------------------------------------------------------------------------

def _matching(scene_dir: str, prefixes: Sequence[str], suffix: str) -> List[str]:
    found = []
    for name in sorted(os.listdir(scene_dir)):
        lowered = name.lower()
        if not lowered.endswith(suffix):
            continue
        if any(lowered.startswith(prefix) for prefix in prefixes):
            found.append(os.path.join(scene_dir, name))
    return found


def find_case_files(scene_dir: str) -> Dict[str, Any]:
    """``{reduction, truth, transforms, error}`` for one run's scene folder.

    Ambiguity is an ERROR, not a guess. If a scene held both
    ``Fragment Reduction`` and ``Fragment Reduction_1``, nothing in the file
    names says which one the run ended on -- and scoring the wrong one produces
    a complete, plausible table about a reduction the surgeon never saw.
    """
    result: Dict[str, Any] = {"reduction": "", "truth": "", "transforms": "",
                              "error": ""}
    if not os.path.isdir(scene_dir):
        result["error"] = "no Statistic/scene/ folder"
        return result
    reductions = _matching(scene_dir, REDUCTION_PREFIXES, SEGMENTATION_SUFFIX)
    truths = _matching(scene_dir, TRUTH_PREFIXES, SEGMENTATION_SUFFIX)
    records = _matching(scene_dir, TRUTH_PREFIXES, TRANSFORM_SUFFIX)

    problems = []
    for label, found, pattern in (("Fragment Reduction*", reductions,
                                   SEGMENTATION_SUFFIX),
                                  ("Ground truth*", truths, SEGMENTATION_SUFFIX),
                                  ("Ground truth*", records, TRANSFORM_SUFFIX)):
        if not found:
            problems.append("no '%s%s'" % (label, pattern))
        elif len(found) > 1:
            problems.append("%d files match '%s%s' (%s) -- which one the run "
                            "ended on is not in the names"
                            % (len(found), label, pattern,
                               ", ".join(os.path.basename(p) for p in found)))
    if problems:
        result["error"] = "; ".join(problems)
        return result
    result["reduction"] = reductions[0]
    result["truth"] = truths[0]
    result["transforms"] = records[0]
    return result


def case_is_scorable(case: Dict[str, str]) -> bool:
    return not find_case_files(case.get("scene_dir", ""))["error"]


# ---------------------------------------------------------------------------
# Reading the recorded transform
# ---------------------------------------------------------------------------

def rotation_angle_axis(rotation: np.ndarray) -> Tuple[float, np.ndarray]:
    """``(degrees, unit axis)`` of a rotation matrix."""
    rotation = np.asarray(rotation, dtype=np.float64)
    cosine = float(np.clip((np.trace(rotation) - 1.0) / 2.0, -1.0, 1.0))
    degrees = float(np.degrees(np.arccos(cosine)))
    axis = np.array([rotation[2, 1] - rotation[1, 2],
                     rotation[0, 2] - rotation[2, 0],
                     rotation[1, 0] - rotation[0, 1]], dtype=np.float64)
    norm = float(np.linalg.norm(axis))
    if norm < 1e-12:
        # 0 or 180 degrees: the skew part vanishes and carries no axis. Zero is
        # by far the likelier of the two here and its axis is meaningless
        # anyway; 180 deg would fail every other gate in this module.
        return degrees, np.zeros(3)
    return degrees, axis / norm


def read_transform_record(path: str) -> Dict[str, Any]:
    """The annotation record, as ``{header fields..., pieces: [...]}``.

    Each piece keeps the file's own numbers verbatim plus a parsed 4x4
    ``matrix``. Nothing is recomputed here -- the point of this module is that
    the numbers are read, not derived -- but the record is checked against
    itself in :func:`record_problems`, which is a different thing.
    """
    document = json.load(io.open(path, encoding="utf-8"))
    if not isinstance(document, dict):
        raise RuntimeError("%s is not a JSON object" % os.path.basename(path))
    pieces = document.get("pieces")
    if not isinstance(pieces, list) or not pieces:
        raise RuntimeError("%s names no pieces" % os.path.basename(path))

    parsed: List[Dict[str, Any]] = []
    for entry in pieces:
        if not isinstance(entry, dict) or not entry.get("name"):
            raise RuntimeError("%s has a piece with no name"
                               % os.path.basename(path))
        matrix = np.asarray(entry.get("matrix"), dtype=np.float64)
        if matrix.shape != (4, 4):
            raise RuntimeError("%s: piece %r has no 4x4 matrix"
                               % (os.path.basename(path), entry["name"]))
        piece = dict(entry)
        piece["matrix"] = matrix
        piece["rotation"] = matrix[:3, :3]
        piece["translation"] = matrix[:3, 3]
        parsed.append(piece)

    return {"path": path,
            "segmentation": document.get("segmentation", ""),
            "reduction": document.get("reduction", ""),
            "convention": document.get("convention", ""),
            "pieces": parsed}


def _vector(piece: Dict[str, Any], key: str) -> Optional[np.ndarray]:
    value = piece.get(key)
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        return None
    try:
        return np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError):
        return None


def record_problems(piece: Dict[str, Any]) -> List[str]:
    """Everything wrong with one piece's record, judged against ITSELF.

    Free of the segmentations, so it runs even when they cannot be read -- and
    it is what separates a malformed record from a record that is merely about
    different files, which only the residual can see.
    """
    problems: List[str] = []
    rotation = np.asarray(piece["rotation"], dtype=np.float64)

    residual = rotation.T @ rotation - np.eye(3)
    if float(np.abs(residual).max()) > ORTHONORMAL_TOLERANCE:
        problems.append("the matrix's rotation block is not orthonormal "
                        "(off by %.2e)" % float(np.abs(residual).max()))
    elif float(np.linalg.det(rotation)) < 0.0:
        # A reflection, not a rotation. It would still map points onto points,
        # and rotation_angle_axis would still return an angle.
        problems.append("the matrix's rotation block is a reflection "
                        "(determinant %.4f)" % float(np.linalg.det(rotation)))

    degrees, axis = rotation_angle_axis(rotation)
    stated = piece.get("rotation_angle_deg")
    if isinstance(stated, (int, float)) \
            and abs(float(stated) - degrees) > RECORD_TOLERANCE_DEG:
        problems.append("rotation_angle_deg says %.4f but the matrix encodes "
                        "%.4f" % (float(stated), degrees))
    stated_axis = _vector(piece, "rotation_axis")
    if stated_axis is not None and degrees > RECORD_TOLERANCE_DEG \
            and float(np.linalg.norm(stated_axis)) > 0.0:
        stated_axis = stated_axis / float(np.linalg.norm(stated_axis))
        if float(np.dot(stated_axis, axis)) < 0.999:
            problems.append("rotation_axis is not the axis the matrix encodes")

    reduced = _vector(piece, "centroid_reduced_mm")
    annotated = _vector(piece, "centroid_annotated_mm")
    if reduced is not None and annotated is not None:
        mapped = rotation @ reduced + np.asarray(piece["translation"])
        gap = float(np.linalg.norm(mapped - annotated))
        if gap > RECORD_TOLERANCE_MM:
            problems.append("the matrix does not carry centroid_reduced_mm onto "
                            "centroid_annotated_mm (%.4f mm apart)" % gap)
        stated_translation = _vector(piece, "translation_mm")
        if stated_translation is not None:
            moved = float(np.linalg.norm(
                (annotated - reduced) - stated_translation))
            if moved > RECORD_TOLERANCE_MM:
                problems.append("translation_mm is not the displacement of the "
                                "reference centroid (%.4f mm apart)" % moved)

    displacement = piece.get("translation_magnitude_mm")
    stated_translation = _vector(piece, "translation_mm")
    if isinstance(displacement, (int, float)) and stated_translation is not None:
        if abs(float(np.linalg.norm(stated_translation)) - float(displacement)) \
                > RECORD_TOLERANCE_MM:
            problems.append("translation_magnitude_mm is not the length of "
                            "translation_mm")
    if isinstance(displacement, (int, float)) \
            and float(displacement) > MAX_PLAUSIBLE_DISPLACEMENT_MM:
        problems.append("a %.1f mm displacement is beyond the %.0f mm at which "
                        "this is treated as a reduction error at all -- the "
                        "record is probably not about this bone"
                        % (float(displacement), MAX_PLAUSIBLE_DISPLACEMENT_MM))
    return problems


# ---------------------------------------------------------------------------
# What the record cannot say: the geometry it is applied to
# ---------------------------------------------------------------------------

def point_displacement_stats(points: np.ndarray, rotation: np.ndarray,
                             translation: np.ndarray) -> Dict[str, float]:
    """How far each point travels under the transform, in mm.

    This is the honest size of the error at the bone surface. ``displacement_mm``
    is measured at ONE point -- the record's reference centroid -- and a rigid
    body's displacement depends on which point you pick: a 6 deg rotation moves a
    point 40 mm from the axis by 4 mm however small the translation is.
    """
    points = np.asarray(points, dtype=np.float64)
    moved = points @ np.asarray(rotation, dtype=np.float64).T \
        + np.asarray(translation, dtype=np.float64)
    lengths = np.linalg.norm(moved - points, axis=1)
    return {"mean": float(lengths.mean()),
            "rms": float(np.sqrt(np.mean(lengths ** 2))),
            "max": float(lengths.max())}


def surface_distance_stats(first: np.ndarray, second: np.ndarray) -> Dict[str, float]:
    """Symmetric point-to-point distance between two surface clouds, in mm."""
    from scipy.spatial import cKDTree                          # noqa: PLC0415

    forward, _unused = cKDTree(second).query(np.asarray(first, dtype=np.float64))
    backward, _unused = cKDTree(first).query(np.asarray(second, dtype=np.float64))
    both = np.concatenate([forward, backward])
    return {"mean": float(both.mean()),
            "rms": float(np.sqrt(np.mean(both ** 2))),
            "percentile": float(np.percentile(both, SURFACE_PERCENTILE)),
            "max": float(both.max())}


def transform_residual_mm(source: np.ndarray, target: np.ndarray,
                          rotation: np.ndarray, translation: np.ndarray) -> float:
    """RMS distance from the TRANSFORMED reduction surface to the ground truth's.

    The one thing a recorded number cannot check about itself: whether it was
    recorded for the files sitting beside it. ICP measured whatever was on disk;
    a record measures whatever was on disk when it was written, and the two part
    company the moment a ground truth is re-annotated without the record being
    rewritten.
    """
    from scipy.spatial import cKDTree                          # noqa: PLC0415

    moved = np.asarray(source, dtype=np.float64) \
        @ np.asarray(rotation, dtype=np.float64).T \
        + np.asarray(translation, dtype=np.float64)
    distances, _unused = cKDTree(np.asarray(target, dtype=np.float64)).query(moved)
    return float(np.sqrt(np.mean(distances ** 2)))


# ---------------------------------------------------------------------------
# One case
# ---------------------------------------------------------------------------

def _round(value: Optional[float], digits: int = 4) -> Optional[float]:
    return None if value is None else round(float(value), digits)


def analyse_case(case: Dict[str, str], verify: bool = True) -> Dict[str, Any]:
    """Score every annotated piece of one run.

    ``verify=False`` reads the transforms file alone -- displacement, rotation
    and the record's own consistency, in milliseconds. The default additionally
    reads the two segmentations, which is what supplies the surface error, the
    volumes, the unpaired pieces, and the proof that the record belongs to them.
    """
    label = case["subject"] or case["run"]
    files = find_case_files(case["scene_dir"])
    if files["error"]:
        raise RuntimeError(files["error"])

    record = read_transform_record(files["transforms"])
    rows: List[Dict[str, Any]] = []
    unpaired: List[Dict[str, Any]] = []
    notes: List[str] = []
    notes.extend(_header_notes(record, files))

    # The transform-only columns first, for every piece: they do not depend on
    # anything below, so a segmentation that cannot be read costs the surface
    # error and nothing else.
    for piece in record["pieces"]:
        rows.append(_transform_row(label, case["run"], piece))

    if not verify:
        return {"rows": rows, "unpaired": unpaired, "notes": notes,
                "verified": False,
                "reduction_file": os.path.basename(files["reduction"]),
                "truth_file": os.path.basename(files["truth"]),
                "transform_file": os.path.basename(files["transforms"])}

    # Both are closed in the `finally` whatever happens, including a failure to
    # open the second one: past the header, each owns a temp file holding the
    # decompressed voxels -- up to 912 MB for a whole pelvis -- and Windows will
    # not delete one while its mapping is live.
    planned = truth = None
    try:
        planned = segmentation_io.Segmentation(files["reduction"])
        truth = segmentation_io.Segmentation(files["truth"])
        planned_by_name = planned.by_name()
        truth_by_name = truth.by_name()
        annotated = {segmentation_io.normalise_name(piece["name"])
                     for piece in record["pieces"]}

        for row, piece in zip(rows, record["pieces"]):
            key = segmentation_io.normalise_name(piece["name"])
            try:
                _measure_pair(row, piece, planned, planned_by_name.get(key),
                              truth, truth_by_name.get(key), notes)
            except Exception as exc:                          # one piece, one row
                row["status"] = "failed"
                row["error"] = _joined(row.get("error"), str(exc))
                notes.append("%s: %s" % (piece["name"], exc))

        # A ground-truth segment nobody recorded a transform for. Not fatal --
        # the record is what this module scores -- but a gap worth naming.
        for name in sorted(truth_by_name):
            if name not in annotated:
                notes.append("the ground truth has a segment %r that "
                             "%s records no transform for"
                             % (truth_by_name[name].name,
                                os.path.basename(files["transforms"])))

        # Listed, never dropped. A reader has to be able to see that the
        # reduction moved five things and the annotation speaks about two --
        # otherwise the table looks like the whole procedure was scored.
        for segment in planned.segments:
            if segmentation_io.normalise_name(segment.name) in annotated:
                continue
            measured = segmentation_io.measure_segment(planned, segment,
                                                       with_surface=False)
            unpaired.append({
                "case": label, "run": case["run"], "segment": segment.name,
                "volume_mm3": _round(measured["volume_mm3"], 1),
                "voxels": measured["voxels"],
                "note": "no transform was recorded for it -- the surgeon did "
                        "not move it, so there is nothing to score",
            })
    finally:
        for handle in (planned, truth):
            if handle is not None:
                handle.close()

    return {"rows": rows, "unpaired": unpaired, "notes": notes, "verified": True,
            "reduction_file": os.path.basename(files["reduction"]),
            "truth_file": os.path.basename(files["truth"]),
            "transform_file": os.path.basename(files["transforms"])}


def _joined(*parts) -> str:
    return "; ".join(part for part in parts if part)


def _header_notes(record: Dict[str, Any], files: Dict[str, Any]) -> List[str]:
    """The record names the two files it was written for. Check it means these.

    Cheap, and it catches a transforms file copied from another case before any
    geometry is read -- at which point the residual would say the same thing far
    less legibly.
    """
    notes: List[str] = []
    named = (record.get("segmentation") or "").strip()
    if named and named != os.path.basename(files["truth"]):
        notes.append("%s says it describes %r, but the ground truth beside it is "
                     "%r" % (os.path.basename(files["transforms"]), named,
                             os.path.basename(files["truth"])))
    reduction = (record.get("reduction") or "").strip()
    stem = os.path.basename(files["reduction"])[:-len(SEGMENTATION_SUFFIX)]
    if reduction and reduction != stem:
        notes.append("%s says it was measured against %r, but the reduction "
                     "beside it is %r"
                     % (os.path.basename(files["transforms"]), reduction, stem))
    return notes


def _transform_row(label: str, run: str, piece: Dict[str, Any]) -> Dict[str, Any]:
    """Everything the record itself says about one piece. No geometry read."""
    row: Dict[str, Any] = {"case": label, "run": run, "segment": piece["name"],
                           "status": "scored", "error": ""}

    displacement = piece.get("translation_magnitude_mm")
    row["displacement_mm"] = _round(displacement) \
        if isinstance(displacement, (int, float)) else None
    row["rotation_deg"] = _round(piece.get("rotation_angle_deg")) \
        if isinstance(piece.get("rotation_angle_deg"), (int, float)) else None

    for prefix, key in (("disp_%s_mm", "translation_mm"),
                        ("rot_axis_%s", "rotation_axis"),
                        ("rot_euler_%s_deg", "rotation_euler_deg"),
                        ("reference_%s", "centroid_reduced_mm")):
        vector = _vector(piece, key)
        for axis, value in zip("ras", vector if vector is not None
                               else (None, None, None)):
            row[prefix % axis] = _round(value)

    problems = record_problems(piece)
    row["record_consistent"] = not problems
    if problems:
        row["status"] = "unreliable"
        row["error"] = _joined(*problems)
    return row


def _measure_pair(row: Dict[str, Any], piece: Dict[str, Any],
                  planned: segmentation_io.Segmentation, planned_segment,
                  truth: segmentation_io.Segmentation, truth_segment,
                  notes: List[str]) -> None:
    """Add the columns that need the voxels: volumes, surface error, residual."""
    if planned_segment is None:
        row["status"] = "not in the reduction"
        row["error"] = _joined(row.get("error"),
                               "the reduction has no segment named %r (it has: "
                               "%s)" % (piece["name"], ", ".join(planned.names())))
        notes.append(row["error"])
        return

    planned_measure = segmentation_io.measure_segment(planned, planned_segment)
    row["volume_reduction_mm3"] = _round(planned_measure["volume_mm3"], 1)
    row["reduction_surface_points"] = int(len(planned_measure["surface"]))
    if not planned_measure["voxels"]:
        row["status"] = "empty"
        row["error"] = _joined(row.get("error"),
                               "the reduction's segment holds no voxels")
        return

    source = segmentation_io.subsample(planned_measure["surface"],
                                       SURFACE_MAX_POINTS)
    if len(source) >= MIN_SURFACE_POINTS:
        travel = point_displacement_stats(source, piece["rotation"],
                                          piece["translation"])
        row["point_error_mean_mm"] = _round(travel["mean"], 3)
        row["point_error_rms_mm"] = _round(travel["rms"], 3)
        row["point_error_max_mm"] = _round(travel["max"], 3)

    if truth_segment is None:
        row["error"] = _joined(row.get("error"),
                               "the ground truth has no segment named %r, so "
                               "the record could not be checked against it"
                               % piece["name"])
        notes.append(row["error"])
        return

    truth_measure = segmentation_io.measure_segment(truth, truth_segment)
    row["volume_truth_mm3"] = _round(truth_measure["volume_mm3"], 1)
    row["truth_surface_points"] = int(len(truth_measure["surface"]))
    if not truth_measure["voxels"]:
        row["status"] = "empty"
        row["error"] = _joined(row.get("error"),
                               "the ground truth's segment holds no voxels")
        return

    ratio = planned_measure["volume_mm3"] / truth_measure["volume_mm3"]
    row["volume_ratio"] = _round(ratio)

    target = segmentation_io.subsample(truth_measure["surface"],
                                       SURFACE_MAX_POINTS)
    if len(source) < MIN_SURFACE_POINTS or len(target) < MIN_SURFACE_POINTS:
        row["error"] = _joined(row.get("error"),
                               "%d and %d surface point(s) -- too few to check "
                               "the record against"
                               % (len(source), len(target)))
        return

    residual = transform_residual_mm(source, target, piece["rotation"],
                                     piece["translation"])
    row["transform_residual_mm"] = _round(residual, 3)

    surface = surface_distance_stats(source, target)
    row["surface_mean_mm"] = _round(surface["mean"], 3)
    row["surface_rms_mm"] = _round(surface["rms"], 3)
    row["surface_hd95_mm"] = _round(surface["percentile"], 3)
    row["surface_max_mm"] = _round(surface["max"], 3)

    problems = []
    if residual > TRANSFORM_RESIDUAL_LIMIT_MM:
        problems.append("applying the recorded matrix to the reduction leaves it "
                        "%.2f mm RMS from the ground truth, above the %.1f mm a "
                        "record written for these two files leaves -- it was "
                        "probably recorded before one of them was last saved"
                        % (residual, TRANSFORM_RESIDUAL_LIMIT_MM))
    if abs(ratio - 1.0) > VOLUME_TOLERANCE:
        problems.append("the two volumes differ by %.1f%%, beyond the %.0f%% at "
                        "which they are still the same object resampled"
                        % (100.0 * abs(ratio - 1.0), 100.0 * VOLUME_TOLERANCE))
    row["transform_verified"] = not problems
    if problems:
        row["status"] = "unreliable"
        row["error"] = _joined(row.get("error"), *problems)
        notes.append("%s: %s" % (piece["name"], "; ".join(problems)))


# ---------------------------------------------------------------------------
# Timing, split into the extension's five stages
# ---------------------------------------------------------------------------

def phase_row(case: Dict[str, str], timing: Dict[str, Any],
              steps: List[Dict[str, Any]], log: List[str]) -> Dict[str, Any]:
    """One run's time, split into t0..t5. Mirrors ``shoulder.phase_row``."""
    label = case["subject"] or case["run"]
    row: Dict[str, Any] = {"case": label, "run": case["run"]}

    totals = {phase: {"wall": 0.0, "exec": 0.0, "wait": 0.0, "visits": 0}
              for phase in list(PHASE_ORDER) + ["unassigned"]}
    seen: List[str] = []
    unassigned: List[str] = []
    for step in steps:
        # A '<< step back' row is a replay review, not a step: it carries an
        # empty step_id and its seconds are already reported separately as
        # replay_review_s. Summing it into a phase would charge scrubbing the
        # timeline to whichever phase happened to be on screen.
        if step.get("kind") != "step visit":
            continue
        step_id = canonical_step_id(step.get("step_id", ""))
        if not step_id:
            continue
        seen.append(step_id)
        phase = _PHASE_OF_STEP.get(step_id)
        if phase is None:
            phase = "unassigned"
            if step_id not in unassigned:
                unassigned.append(step_id)
        bucket = totals[phase]
        # branch_op rows print exec as '-', which parses to None. Coerce, never
        # skip: dropping the row would lose its wall time too.
        for key, name in (("wall", "wall_s"), ("exec", "exec_s"), ("wait", "wait_s")):
            value = step.get(name)
            bucket[key] += float(value) if isinstance(value, (int, float)) else 0.0
        bucket["visits"] += 1

    for phase in PHASE_ORDER:
        row["%s_s" % phase] = round(totals[phase]["wall"], 3)
        row["%s_exec_s" % phase] = round(totals[phase]["exec"], 3)
        row["%s_wait_s" % phase] = round(totals[phase]["wait"], 3)

    phase_sum = sum(totals[phase]["wall"] for phase in PHASE_ORDER) \
        + totals["unassigned"]["wall"]
    row["phase_sum_s"] = round(phase_sum, 3)
    for name in ("total_s", "inside_steps_s", "startup_s", "between_steps_s",
                 "replay_review_s", "tail_wait_exit_s"):
        # .get, not [ ]: replay_review_s is absent from the report of a run that
        # was never stepped back, which is the normal case.
        if isinstance(timing.get(name), float):
            row[name if name != "total_s" else "t_total_s"] = timing[name]
    if isinstance(timing.get("inside_steps_s"), float):
        # Not clamped. A non-zero residual is the only evidence a reader has that
        # the phases and the run clock disagree; here it is the report's own
        # two-decimal rounding accumulated over ~15 rows.
        row["phase_residual_s"] = round(timing["inside_steps_s"] - phase_sum, 3)

    row["steps_seen"] = len(seen)
    row["steps_unassigned"] = ", ".join(unassigned)
    if unassigned:
        log.append("   [!] %s: %d step(s) in no timing phase (%s) -- PHASE_STEPS "
                   "is out of date with the workflow, and t0..t5 are short by "
                   "their time" % (label, len(unassigned), ", ".join(unassigned)))
    return row


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------

SEGMENT_COLUMNS = [
    "case", "segment", "status", "displacement_mm", "rotation_deg",
    "point_error_mean_mm", "point_error_rms_mm", "point_error_max_mm",
    "surface_mean_mm", "surface_rms_mm", "surface_hd95_mm", "surface_max_mm",
    "disp_r_mm", "disp_a_mm", "disp_s_mm",
    "rot_axis_r", "rot_axis_a", "rot_axis_s",
    "rot_euler_r_deg", "rot_euler_a_deg", "rot_euler_s_deg",
    "reference_r", "reference_a", "reference_s",
    "volume_reduction_mm3", "volume_truth_mm3", "volume_ratio",
    "transform_residual_mm", "reduction_surface_points", "truth_surface_points",
    "record_consistent", "transform_verified", "error", "run",
]

UNPAIRED_COLUMNS = ["case", "segment", "volume_mm3", "voxels", "note", "run"]

CASE_COLUMNS = ["case", "pieces_annotated", "max_displacement_mm",
                "mean_displacement_mm", "max_rotation_deg", "mean_rotation_deg",
                "max_point_error_mm", "max_surface_hd95_mm",
                "max_transform_residual_mm", "pieces_unannotated",
                "pieces_untrusted", "reduction_file", "truth_file",
                "transform_file", "run"]

SUMMARY_COLUMNS = ["metric", "n", "mean", "sd", "min", "max", "note"]

PHASE_COLUMNS = (["case", "run", "t_total_s", "inside_steps_s"]
                 + ["%s_s" % phase for phase in PHASE_ORDER]
                 + ["phase_sum_s", "phase_residual_s"]
                 + ["%s_exec_s" % phase for phase in PHASE_ORDER]
                 + ["%s_wait_s" % phase for phase in PHASE_ORDER]
                 + ["startup_s", "between_steps_s", "replay_review_s",
                    "tail_wait_exit_s", "steps_seen", "steps_unassigned"])

DEFINITION_COLUMNS = ["term", "definition"]


METHOD_DEFINITIONS = [
    ("where the numbers come from",
     "The run's own 'Ground truth*.transforms.json', written when the "
     "annotation was saved. It records, per piece, the rigid transform from "
     "where the pipeline put that piece to where the surgeon says it belongs -- "
     "which IS the reduction error. displacement_mm and rotation_deg are read "
     "from it; nothing is registered or estimated."),
    ("why nothing is registered",
     "An earlier version of this analysis recovered the same transform by ICP "
     "between the two segmentations. It agreed with the record to 0.009-0.034 "
     "deg, which is a good reason to believe both and no reason to keep "
     "re-deriving a number that is written down. The estimate can only ever "
     "approach the record; it cannot improve on it."),
    ("what the segmentations are still read for",
     "Four things the record cannot say: whether it was written for the files "
     "beside it (transform_residual_mm), how large the error is at the bone "
     "surface rather than at one reference point (point_error_*), whether the "
     "two segments are the same object (volume_ratio), and which pieces the "
     "reduction moved that nobody annotated. Turn verification off for a "
     "transform-only pass, which takes milliseconds and reports none of these."),
    ("how pieces are paired",
     "By NAME, case- and whitespace-insensitively: the record's piece name "
     "against the segment of that name in each segmentation. A ground-truth "
     "segment with no recorded transform, and a reduction segment with no "
     "recorded transform, are both reported rather than dropped."),
    ("when a row is not to be trusted",
     "Two independent verdicts. record_consistent is the record judged against "
     "ITSELF -- the matrix is a proper rotation, its angle and axis are the ones "
     "it encodes, and it carries centroid_reduced_mm onto centroid_annotated_mm. "
     "transform_verified is the record judged against the FILES -- applying the "
     "matrix to the saved reduction lands within %.1f mm RMS of the saved ground "
     "truth, and the two volumes agree. The first catches a malformed record; "
     "only the second catches a record written for an older version of the "
     "annotation, which is this design's one real hazard."
     % TRANSFORM_RESIDUAL_LIMIT_MM),
    ("what is NOT computed",
     "No overlap score (Dice). For a rigid piece, overlap is a function of the "
     "same pose error the record states directly, and it would have to be "
     "measured on a resampled common grid -- a third sampling of data that is "
     "already sampled two different ways."),
]

SEGMENT_DEFINITIONS = [
    ("displacement_mm",
     "The record's translation_magnitude_mm: how far the piece's reference "
     "centroid had to move. disp_r/a/s are its components in RAS (right / "
     "anterior / superior), and reference_r/a/s is the point it is measured at."),
    ("rotation_deg",
     "The record's rotation_angle_deg: the angle of the rigid rotation the "
     "surgeon applied. rot_axis_r/a/s is its axis as a unit vector in RAS, and "
     "rot_euler_r/a/s_deg is the same rotation stated as three angles."),
    ("point_error_*_mm",
     "The recorded matrix applied to every surface point of the piece, and how "
     "far each one travels -- displacement and rotation combined, at the bone. "
     "Always at least the displacement, and usually well above it: a rigid "
     "body's displacement depends on which point you measure, and a 6 deg "
     "rotation moves a point 40 mm from the axis by 4 mm however small the "
     "translation is. This is the number to quote as 'how wrong is it'."),
    ("surface_*_mm",
     "Symmetric distance between the two segmentations' surfaces as they stand, "
     "with no transform applied: the gap a surgeon would see at the fracture "
     "line. Always SMALLER than point_error, because a point that slid ALONG "
     "the surface still has a near neighbour on it. surface_hd95_mm is the "
     "%.0fth percentile, which is what to quote; surface_max_mm is beside it "
     "but must not lead, since one stray boundary voxel moves it and moves the "
     "percentile not at all." % SURFACE_PERCENTILE),
    ("transform_residual_mm",
     "RMS distance from the reduction's surface, AFTER the recorded matrix is "
     "applied to it, to the ground truth's surface. The proof that the record "
     "belongs to these two files. Its floor is the two grids' own sampling, a "
     "fraction of a voxel; anything approaching a millimetre means the record "
     "and the segmentations have drifted apart."),
    ("volume_reduction_mm3 / volume_truth_mm3 / volume_ratio",
     "The two segments' volumes and their ratio. The evidence that they are the "
     "same object: they agree to a fraction of a percent, which is what "
     "resampling one object onto two different grids costs."),
    ("reduction_surface_points / truth_surface_points",
     "Boundary voxels found on each side, before the %d-point cap that the "
     "distance statistics use." % SURFACE_MAX_POINTS),
    ("record_consistent / transform_verified",
     "The two verdicts described above. transform_verified is blank when "
     "verification was not run."),
    ("status",
     "'scored' (both verdicts passed), 'unreliable' (scored, but a verdict "
     "failed -- see 'error'), 'not in the reduction', 'empty', 'failed'."),
]

CASE_DEFINITIONS = [
    ("pieces_annotated", "Pieces the surgeon recorded a transform for."),
    ("max_* / mean_*",
     "Over that run's pieces. The MAX is the one to read: a reduction is as good "
     "as its worst fragment, and averaging over a barely-moved bone and a "
     "displaced fragment hides exactly the fragment."),
    ("pieces_unannotated",
     "Segments the reduction moved that no transform was recorded for. They are "
     "not errors -- the surgeon did not correct them -- but they are how much of "
     "the procedure this table is silent about."),
    ("pieces_untrusted",
     "Pieces that failed either verdict. Anything above 0 means the run's "
     "numbers need reading beside the 'error' column."),
    ("reduction_file / truth_file / transform_file",
     "Which three files the row was built from, by name, so an ambiguous scene "
     "folder is visible rather than resolved silently."),
]

PHASE_DEFINITIONS = [
    ("t0..t5",
     "Wall time in each stage of the extension's own panel: "
     + "; ".join("%s = %s" % (phase, PHASE_TITLES[phase]) for phase in PHASE_ORDER)
     + ". Each numbered stage includes the optional hand-adjustment steps that "
       "follow it, because correcting a template is part of building it."),
    ("*_exec_s / *_wait_s",
     "The phase's time split into SafeExecutor time (the generated code actually "
     "running) and everything else -- which on a choice or interaction step is "
     "the surgeon, and on an automated step is dispatch and panel render."),
    ("phase_sum_s / phase_residual_s",
     "The phases summed, and inside_steps_s minus that. It should be ~0 (the "
     "timing report's own two-decimal rounding); it is printed rather than "
     "hidden, because a real gap means a step landed in no phase and is named in "
     "steps_unassigned."),
    ("t_total_s / startup_s / between_steps_s / replay_review_s / tail_wait_exit_s",
     "The whole run and its four components, straight from Statistic/timing.txt. "
     "See the Timing sheet's own definitions."),
    ("steps_seen / steps_unassigned",
     "Step visits counted, and any step id this module's PHASE_STEPS does not "
     "place. A non-empty steps_unassigned means the workflow was renumbered and "
     "the phases are short by those steps' time."),
]


def definition_rows(pairs: Sequence[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"term": term, "definition": text} for term, text in pairs]


def _stats(values: Sequence[Optional[float]]) -> Dict[str, Any]:
    numbers = [float(v) for v in values if isinstance(v, (int, float))]
    if not numbers:
        return {"n": 0, "mean": None, "sd": None, "min": None, "max": None}
    array = np.asarray(numbers, dtype=np.float64)
    return {"n": len(numbers),
            "mean": round(float(array.mean()), 4),
            # Sample standard deviation, undefined for a single value rather
            # than reported as zero -- a zero there would read as agreement.
            "sd": round(float(array.std(ddof=1)), 4) if len(numbers) > 1 else None,
            "min": round(float(array.min()), 4),
            "max": round(float(array.max()), 4)}


def _scored(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [row for row in rows if row.get("displacement_mm") is not None
            and row.get("rotation_deg") is not None]


def _trusted(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Scored, consistent with itself, and not contradicted by the files.

    ``transform_verified`` is None when verification did not run, which must not
    be read as a failure -- ``is not False`` rather than truthiness.
    """
    return [row for row in _scored(rows)
            if row.get("record_consistent")
            and row.get("transform_verified") is not False]


def case_rows(rows: List[Dict[str, Any]], unpaired: List[Dict[str, Any]],
              files: Dict[str, Dict[str, str]]) -> List[Dict[str, Any]]:
    """One row per run: its worst piece."""
    order: List[str] = []
    for row in rows + unpaired:
        if row["case"] not in order:
            order.append(row["case"])

    out: List[Dict[str, Any]] = []
    for case in order:
        mine = _scored([row for row in rows if row["case"] == case])
        loose = [row for row in unpaired if row["case"] == case]
        run = next((row["run"] for row in rows + unpaired if row["case"] == case), "")
        entry: Dict[str, Any] = {
            "case": case, "run": run,
            "pieces_annotated": len(mine),
            "pieces_unannotated": len(loose),
            "pieces_untrusted": sum(1 for row in rows if row["case"] == case
                                    and (row.get("record_consistent") is False
                                         or row.get("transform_verified") is False)),
        }
        entry.update(files.get(case, {}))
        for key in ("displacement_mm", "rotation_deg"):
            values = [row[key] for row in mine if row.get(key) is not None]
            entry["max_%s" % key] = _round(max(values)) if values else None
            entry["mean_%s" % key] = _round(sum(values) / len(values)) \
                if values else None
        for target, key in (("max_point_error_mm", "point_error_max_mm"),
                            ("max_surface_hd95_mm", "surface_hd95_mm"),
                            ("max_transform_residual_mm", "transform_residual_mm")):
            values = [row[key] for row in mine if row.get(key) is not None]
            entry[target] = _round(max(values)) if values else None
        out.append(entry)
    return out


def summary_rows(rows: List[Dict[str, Any]],
                 unpaired: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Mean / sd / min / max of each measure over every scored piece."""
    mine = _scored(rows)
    trusted = _trusted(rows)
    out: List[Dict[str, Any]] = []

    # The TRUSTED population only. A row that failed a verdict is still printed
    # in the table above -- which verdict failed is the useful part -- but
    # pooling it into a mean would let a stale record move the headline. Same
    # rule, same reason, as shoulder.py's planned / best-effort split.
    for metric, key, note in (
            ("displacement (mm)", "displacement_mm",
             "the recorded translation, at the piece's reference centroid"),
            ("rotation (deg)", "rotation_deg", "the recorded rotation angle"),
            ("point error, mean (mm)", "point_error_mean_mm",
             "how far a surface point travels under the recorded transform, "
             "averaged over the piece"),
            ("point error, max (mm)", "point_error_max_mm",
             "the worst point of the piece -- the headline error"),
            ("surface HD95 (mm)", "surface_hd95_mm",
             "symmetric surface distance, in place"),
            ("transform residual (mm)", "transform_residual_mm",
             "after applying the record -- the evidence it belongs to these files"),
            ("volume ratio", "volume_ratio",
             "reduction / ground truth; 1.000 means the same object resampled")):
        entry = {"metric": metric, "note": note}
        entry.update(_stats([row.get(key) for row in trusted]))
        out.append(entry)

    out.append({"metric": "pieces annotated", "n": len(mine), "mean": None,
                "sd": None, "min": None, "max": None,
                "note": "%d of them passed every verdict; %d did not and are "
                        "excluded from the rows above"
                        % (len(trusted), len(mine) - len(trusted))})
    out.append({"metric": "pieces with no usable record", "n": len(rows) - len(mine),
                "mean": None, "sd": None, "min": None, "max": None,
                "note": "named by the transforms file but carrying no "
                        "displacement or rotation -- see the status column"})
    out.append({"metric": "segments with no recorded transform", "n": len(unpaired),
                "mean": None, "sd": None, "min": None, "max": None,
                "note": "moved by the reduction, not annotated, so not scored"})
    return out


def discover_cases(experiment_root: str) -> List[Dict[str, str]]:
    """One entry per run folder under ``Overall_Performance``."""
    return _discover_cases(experiment_root, RUNS_SUBDIR, DATASET_SUBDIR)


def build_report(experiment_root: str, progress=None,
                 verify: bool = True) -> Dict[str, Any]:
    """Analyse every case. Fail-soft per case, so one bad scene costs one row."""
    cases = discover_cases(experiment_root)
    rows: List[Dict[str, Any]] = []
    unpaired: List[Dict[str, Any]] = []
    files: Dict[str, Dict[str, str]] = {}
    failed: List[str] = []
    log: List[str] = []
    if not cases:
        log.append("No cases found under %s."
                   % os.path.join(experiment_root, RUNS_SUBDIR))
    if not verify:
        # Said in the log, not only in a parameter: without it the sheet's blank
        # residual and volume columns read as measurements that came out empty.
        log.append("Verification is OFF: displacement and rotation are read from "
                   "each run's transforms file, and nothing checks that the file "
                   "was written for the segmentations beside it.")

    for index, case in enumerate(cases):
        label = case["subject"] or case["run"]
        if progress is not None:
            try:
                progress(index, len(cases), label)
            except Exception:
                logger.debug("Progress callback failed", exc_info=True)
        # Before the work, not after: a hard crash takes the report with it, so
        # the last line logged is the only record of which case was in flight.
        logger.info("[PFP] case %d/%d: %s", index + 1, len(cases), label)
        try:
            result = analyse_case(case, verify=verify)
        except Exception as exc:
            log.append("%s: FAILED -- %s" % (label, exc))
            logger.warning("Pelvic analysis failed for %s", label, exc_info=True)
            # Recorded, not merely logged. A case that produces no row at all is
            # invisible in every table, and the panel would quote the DISCOVERED
            # count beside a mean taken over fewer cases than that.
            failed.append(label)
            continue
        rows.extend(result["rows"])
        unpaired.extend(result["unpaired"])
        files[label] = {"reduction_file": result["reduction_file"],
                        "truth_file": result["truth_file"],
                        "transform_file": result["transform_file"]}
        scored = _scored(result["rows"])
        log.append("%s: %d piece(s) annotated, %d segment(s) left unannotated -- "
                   "worst displacement %s mm, worst rotation %s deg"
                   % (label, len(scored), len(result["unpaired"]),
                      _fmt(max((r["displacement_mm"] for r in scored), default=None)),
                      _fmt(max((r["rotation_deg"] for r in scored), default=None))))
        for note in result["notes"]:
            log.append("   [!] %s: %s" % (label, note))

    timing_rows, step_rows = collect_timing(cases, log)
    by_run: Dict[str, List[Dict[str, Any]]] = {}
    for step in step_rows:
        by_run.setdefault(step["run"], []).append(step)
    timing_by_run = {row["run"]: row for row in timing_rows}
    phase_rows = [phase_row(case, timing_by_run.get(case["run"], {}),
                            by_run.get(case["run"], []), log)
                  for case in cases]

    per_case = case_rows(rows, unpaired, files)
    summary = summary_rows(rows, unpaired)
    timing_title, timing_blocks = timing_sheet(timing_rows, step_rows)

    sheets = [
        ("Reduction accuracy", [
            ("How far each piece ended up from where the surgeon put it, READ "
             "from the transform each run recorded when its annotation was "
             "saved. displacement_mm and rotation_deg are that record; "
             "point_error_max_mm is the same transform applied to the piece's "
             "own surface, which is how wrong it is at the bone rather than at "
             "one reference point.",
             SEGMENT_COLUMNS, rows),
            ("Per run: its worst piece, which is what a reduction is as good "
             "as.", CASE_COLUMNS, per_case),
            ("Across every annotated piece. The rows above the counts are taken "
             "over the pieces that passed every verdict.",
             SUMMARY_COLUMNS, summary),
            ("Segments the reduction moved that no transform was recorded for. "
             "Listed, not dropped: they are how much of the procedure the table "
             "above is silent about.",
             UNPAIRED_COLUMNS, unpaired),
            ("DEFINITIONS — how the measurement is made",
             DEFINITION_COLUMNS, definition_rows(METHOD_DEFINITIONS)),
            ("DEFINITIONS — per-piece columns",
             DEFINITION_COLUMNS, definition_rows(SEGMENT_DEFINITIONS)),
            ("DEFINITIONS — per-run columns",
             DEFINITION_COLUMNS, definition_rows(CASE_DEFINITIONS)),
        ]),
        (timing_title, [
            ("The run's time split into the extension's own five stages, summed "
             "from the per-step timeline below. Each numbered stage carries the "
             "optional hand-adjustment steps that follow it.",
             PHASE_COLUMNS, phase_rows),
            ("DEFINITIONS — phase columns",
             DEFINITION_COLUMNS, definition_rows(PHASE_DEFINITIONS)),
        ] + list(timing_blocks)),
    ]
    return {"sheets": sheets, "log": log, "rows": rows, "unpaired": unpaired,
            "case_rows": per_case, "summary": summary, "phase_rows": phase_rows,
            "timing_rows": timing_rows, "step_rows": step_rows,
            "cases": len(cases), "verified": bool(verify),
            # `cases` is what was DISCOVERED and `analysed` is what produced a
            # row. They differ exactly when `failed` is non-empty, and a caller
            # quoting the first beside a mean taken over the second would
            # overstate the sweep.
            "analysed": len({row["case"] for row in rows}),
            "failed_cases": failed}


def _fmt(value: Optional[float]) -> str:
    return "%.2f" % value if isinstance(value, (int, float)) else "--"


def run_analysis(repository_root: str, progress=None,
                 verify: bool = True) -> Dict[str, Any]:
    """Analyse every case and write the workbook. Returns the report + its path."""
    from .workbook import write_workbook                      # noqa: PLC0415

    experiment_root = os.path.join(repository_root, EXPERIMENT_DIR)
    report = build_report(experiment_root, progress=progress, verify=verify)
    output = os.path.join(experiment_root, RUNS_SUBDIR, WORKBOOK_NAME)
    written, notes = write_workbook(output, report["sheets"])
    report["workbook"] = written
    report["log"].extend(notes)
    try:
        report["workbook_relative"] = os.path.relpath(written, repository_root)
    except ValueError:
        report["workbook_relative"] = written
    return report
