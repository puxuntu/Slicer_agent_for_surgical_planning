"""LongBoneFractureReduction: how far the planned reduction is from the truth.

Every run under ``Experiments/LongBoneFractureReduction/Overall_Performance/``
saved the moving fragment's mesh in its **un-reduced** pose plus the transform
node the pipeline computed for it, so one number is common to every case: the
rigid **pose** ``P`` that carries the moving fragment from where it was
segmented to where the pipeline put it. The ground truth pose ``G`` for the same
fragment arrives two different ways, and the whole of this module is about
reducing both of them to the same object -- the residual

    E = G . P^-1

the transform still needed, in world RAS, to carry the pipeline's answer onto
the truth. Every metric below is a reading of that one matrix.

**Cases the surgeon annotated** (``Dataset_From_6Hospital``) carry
``Statistic/scene/Moving_Segment_groundtruth.json``, written when the annotation
was saved. It states ``ground_truth_ras`` -- ``G`` itself -- beside the pose the
pipeline had reached (``pose_before_annotation_ras``, which is ``P``) and the
adjustment between them. Nothing is estimated: ``rotation_deg`` reproduces the
file's own ``adjustment_rotation_deg`` to 1e-6 deg on all seven.

**Cases from a fracture simulation** (``Dataset_From_TotalSegmentor``) have no
annotation. What they have is the simulation's own record,
``Dataset/Dataset_From_TotalSegmentor/<subject>/<subject>_fracture.json``, which
states the rigid ``displacement_matrix_ras`` ``D`` it applied to ONE of the two
fragments when it broke the intact bone. Reducing that fragment means undoing
``D``; reducing the OTHER one means applying ``D`` to it instead, since the
reference it must meet is the displaced one. So the ground truth is ``D^-1`` or
``D`` and **which one is a property of the run, not of the data set** -- the
surgeon segments whichever fragment they choose to move, and across the 57
simulated runs here it is the displaced fragment 25 times and the fixed one 32.
Guessing costs nothing visible: the wrong matrix produces a complete table of
plausible millimetres about a bone that was never reconstructed.

So the choice is DECIDED and then CHECKED, by two independent facts:

* **Decided** by centroid. The simulation records ``moved_fragment_centroid_ras``
  and the voxel count of each fragment, and the run saved the fractured labelmap
  the two were cut from -- so the fixed fragment's centroid follows from the
  union's. Assigning the run's two meshes to those two centroids is a 2x2
  assignment; on the saved runs the winning assignment beats the other by at
  least 131 mm while itself costing at most 16 mm.
* **Checked** by abutment. A correct ``G`` carries the moving fragment's
  fracture surface onto the reference fragment's, because that is what a
  reduction IS. ``truth_fit_mm`` is the median distance between them afterwards:
  0.3-1.7 mm across the simulated runs with the right matrix and 14.7-60.7 mm
  with the wrong one. The same column is measured on the annotated runs
  (0.9-2.6 mm), so one witness covers both populations.

Three more things are proved rather than assumed, each because getting it wrong
yields a plausible number instead of an error:

* **The pose is read out of the run's own transform files**, ``Reduction
  Transform.h5`` composed with ``Reduction Base.h5`` -- and the chain is taken
  from ``scene.mrml``, not from those names, so a run whose hierarchy differs is
  refused rather than silently composed the wrong way round. The ITK reader is
  witnessed by the annotated cases: the pose it recovers equals the
  ``pose_before_annotation_ras`` the annotation recorded, to 6e-14, on all seven.
  Those seven are what license the same reader on the other 57.
* **The frame is measured.** Slicer wrote these ``.vtk`` models in LPS, so the
  meshes need mirroring in x and y before they can meet an ``*_ras`` matrix --
  and an unmirrored mesh is not an error, it is the same bone on the other side
  of the origin, which still produces distances. Both frames are tried and the
  one its own witness accepts is kept (:func:`resolve_points_frame`).
* **No shaft axis is inferred.** The clinical split of a residual into
  angulation / malrotation / shortening needs the bone's own axis, and the
  obvious estimate -- the fragment's principal axis -- disagrees with the axis
  the simulation recorded by a median of 6.5 deg and up to 12.4 deg over the 57
  runs where both exist, which is larger than most of the residual rotations it
  would be decomposing. So the decomposition is reported ONLY where the axis is
  a recorded fact (the simulated cases), and ``pca_axis_vs_recorded_deg`` carries
  the measurement that justifies the refusal into the workbook itself.

Slicer-free and Qt-free -- it is JSON, a legacy-VTK read, a small HDF5 read and
arithmetic -- so ``scripts/check_longbone_analysis.py`` runs the whole analysis
against the real saved runs outside Slicer.
"""

from __future__ import annotations

import io
import json
import logging
import os
import re
import struct
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import volume_io
from .geometry_io import lps_to_ras, read_vtk_points
from .run_timing import (canonical_step_id, collect_timing,
                         discover_cases as _discover_cases, timing_sheet)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

EXTENSION_NAME = "LongBoneFractureReduction"
EXPERIMENT_DIR = os.path.join("Experiments", EXTENSION_NAME)
RUNS_SUBDIR = "Overall_Performance"
DATASET_SUBDIR = "Dataset"
WORKBOOK_NAME = "LongBoneFractureReduction_summary.xlsx"

#: The data sets sit one level below ``Dataset/``, one folder per collection, and
#: a subject belongs to exactly one of them. Searched in order; the collection a
#: subject is found in becomes its ``dataset`` column, which is what separates
#: the annotated population from the simulated one in every summary.
DATASET_COLLECTIONS = ("Dataset_From_6Hospital", "Dataset_From_TotalSegmentor")

#: Node names inside a run's ``Statistic/scene/``. The two fragments and the two
#: fracture surfaces are saved from nodes of these names, so the files are
#: ``<name>.vtk`` -- except the fracture surfaces, which the extension suffixes
#: with the iteration that produced them (``Moving fracture surface_2.vtk``).
MOVING_MODEL = "Moving_Segment"
REFERENCE_MODEL = "Reference_Segment"
MOVING_SURFACE_PREFIX = "moving fracture surface"
REFERENCE_SURFACE_PREFIX = "reference fracture surface"

#: The annotation a surgeon left on a 6-Hospital case, beside the shape it
#: describes.
ANNOTATION_NAME = "Moving_Segment_groundtruth.json"
ANNOTATION_SHAPE = "Moving_Segment_groundtruth.vtk"

#: The simulation's record, under the subject's own dataset folder.
SIMULATION_SUFFIX = "_fracture.json"


# ---------------------------------------------------------------------------
# How much has to agree with what, before a row is trusted
# ---------------------------------------------------------------------------

#: Median distance between the two fracture surfaces once the ground truth pose
#: is applied to the moving one. This is the verdict on ``G`` -- see the module
#: docstring: the saved runs sit at 0.3-2.6 mm with the right ground truth and
#: never below 14.7 mm with the wrong one, so anywhere in between separates
#: them. 5 mm is three times under the smallest failure and twice over the
#: largest success.
TRUTH_FIT_LIMIT_MM = 5.0

#: Distance below which two candidate mesh frames are not distinguishable, used
#: by :func:`resolve_points_frame`. A mirrored bone is hundreds of millimetres
#: from the un-mirrored one -- these frames are never close -- so this only has
#: to be larger than the real distances (a few mm) and smaller than a mirror.
FRAME_TOLERANCE_MM = 40.0

#: How far the recorded ground-truth matrix may be from orthonormal, and how far
#: its stated angle/shift may be from the ones it encodes. The annotation prints
#: full double precision, so these are pure sanity gates on a hand-edited file.
ORTHONORMAL_TOLERANCE = 1e-6
RECORD_TOLERANCE_DEG = 1e-3

#: ``adjustment_shift_mm`` in the annotation is the displacement at the moving
#: fragment's centroid, and this module recomputes it from the mesh's own point
#: average rather than from whatever centre the annotator used. The two agree to
#: 0.008 mm on the saved runs; a millimetre apart would mean they are not about
#: the same shape.
RECORD_SHIFT_TOLERANCE_MM = 0.5

#: The pose recovered from the ``.h5`` files, against the pose the annotation
#: recorded. 6e-14 on the saved runs -- this is a reader check, not a
#: measurement, so the tolerance is numerical.
POSE_RESIDUAL_LIMIT_MM = 1e-6

#: Points kept for the KD-tree the symmetric surface distance is measured with.
#: The point-wise error below uses every point (it needs no tree); this cap is
#: only so a 206k-point femur does not build a tree of that size for a number
#: that is stable four digits earlier.
SURFACE_MAX_POINTS = 120000

#: Fewer points than this on either side and the surface columns are not
#: reported at all.
MIN_SURFACE_POINTS = 50

#: The percentile of the symmetric surface distance that is quoted. Same rule,
#: same reason, as ``cranial.py`` and ``pelvic.py``: the maximum is reported
#: beside it but must not lead, since one stray mesh vertex moves it and moves
#: the percentile not at all.
SURFACE_PERCENTILE = 95.0


# ---------------------------------------------------------------------------
# Timing phases: the extension's own panel, in order
# ---------------------------------------------------------------------------

#: Cookbook step -> phase. A step in none of these lands in an ``unassigned``
#: bucket and is NAMED in the log, because a regenerated workflow that renumbers
#: its steps would otherwise make the phases silently shrink while still summing
#: to something plausible.
#:
#: t5 and t6 are deliberately not one phase. Step 30 is the surgeon dragging the
#: moving fragment into a rough alignment and step 31 is the extension's own
#: registration; charging the first to "reduction" would report hand time as
#: compute time, which is the single comparison this table exists to support.
PHASE_STEPS = {
    "t0": ("cb_step_1", "cb_step_2", "cb_step_3", "cb_step_4", "cb_step_5",
           "cb_step_6"),
    "t1": ("cb_step_7", "cb_step_8", "cb_step_9", "cb_step_10", "cb_step_11",
           "cb_step_12", "cb_step_13", "cb_step_14"),
    "t2": ("cb_step_15", "cb_step_16", "cb_step_17", "cb_step_18",
           "cb_step_19", "cb_step_20", "cb_step_21", "cb_step_22"),
    "t3": ("cb_step_23", "cb_step_24", "cb_step_25", "cb_step_26",
           "cb_step_27"),
    "t4": ("cb_step_28", "cb_step_29"),
    "t5": ("cb_step_30",),
    "t6": ("cb_step_31",),
}
PHASE_ORDER = ("t0", "t1", "t2", "t3", "t4", "t5", "t6")
PHASE_TITLES = {
    "t0": "select the CT, and crop it to an ROI if needed",
    "t1": "segment the reference (fixed) fragment",
    "t2": "segment the moving fragment",
    "t3": "reconstruct both fragments in 3D",
    "t4": "detect the fracture surfaces and initialise the registration",
    "t5": "hand pre-alignment of the moving fragment",
    "t6": "run the reduction",
}

_PHASE_OF_STEP = {canonical_step_id(step): phase
                  for phase, steps in PHASE_STEPS.items() for step in steps}


# ---------------------------------------------------------------------------
# The transform files: ITK affine over HDF5, without h5py
# ---------------------------------------------------------------------------

#: The only transform class these runs write. Named explicitly so a file holding
#: anything else -- a b-spline, a 2-D transform -- is refused rather than having
#: twelve doubles pulled out of it.
ITK_TRANSFORM_TYPE = b"AffineTransform_double_3_3"

#: RAS <-> LPS. Its own inverse, as a 4x4 so it can be composed.
_FLIP = np.diag([-1.0, -1.0, 1.0, 1.0])


def read_itk_affine(path: str) -> np.ndarray:
    """The 4x4 **to-parent, RAS** matrix stored in a Slicer ``.h5`` transform.

    Slicer writes linear transforms through ITK, which means: an HDF5 container,
    the *from*-parent direction, and LPS. So the file's twelve
    ``TransformParameters`` (a 3x3 followed by a translation) and three
    ``TransformFixedParameters`` (the centre of rotation) become

        to-parent, RAS  =  F . (from-parent, LPS)^-1 . F

    and the centre is folded in as ``A(x - c) + t + c``, which is ITK's own
    definition and not a convention this module may choose.

    ``h5py`` is not in Slicer's Python and this is one 8 KB file per run, so the
    parameter block is located by its PROPERTIES rather than by parsing HDF5:
    twelve finite doubles whose first nine are a proper rotation. That is a
    strong enough signature that exactly one window in the file matches, and
    **exactly one** is required -- two candidates mean the file is not what this
    reader thinks it is, and picking either would be a guess. The fixed
    parameters are the three doubles immediately before it, which is how ITK
    lays the two datasets out.

    The reader is not taken on trust: on the seven annotated runs the pose it
    recovers equals the pose those runs recorded independently, to 6e-14
    (``pose_h5_residual_mm``), and that is what licenses it on the rest.
    """
    with open(path, "rb") as handle:
        blob = handle.read()
    if ITK_TRANSFORM_TYPE not in blob:
        raise ValueError("%s does not hold an %s"
                         % (os.path.basename(path),
                            ITK_TRANSFORM_TYPE.decode("ascii")))
    matches: List[int] = []
    for offset in range(24, len(blob) - 96 + 1, 8):
        values = struct.unpack_from("<12d", blob, offset)
        if not all(value == value and abs(value) < 1e8 for value in values):
            continue
        rotation = np.array(values[:9], dtype=np.float64).reshape(3, 3)
        if np.abs(rotation @ rotation.T - np.eye(3)).max() > ORTHONORMAL_TOLERANCE:
            continue
        if abs(float(np.linalg.det(rotation)) - 1.0) > ORTHONORMAL_TOLERANCE:
            continue
        matches.append(offset)
    if len(matches) != 1:
        raise ValueError("%s: %d candidate parameter blocks, expected exactly 1"
                         % (os.path.basename(path), len(matches)))
    offset = matches[0]
    values = struct.unpack_from("<12d", blob, offset)
    centre = np.array(struct.unpack_from("<3d", blob, offset - 24),
                      dtype=np.float64)
    rotation = np.array(values[:9], dtype=np.float64).reshape(3, 3)
    translation = np.array(values[9:12], dtype=np.float64)

    from_parent = np.eye(4)
    from_parent[:3, :3] = rotation
    from_parent[:3, 3] = translation + centre - rotation @ centre
    return _FLIP @ np.linalg.inv(from_parent) @ _FLIP


# ---------------------------------------------------------------------------
# The pose: which transforms, in which order, according to the scene itself
# ---------------------------------------------------------------------------

_NODE_RE = re.compile(r"<(\w+)\b([^>]*)>")


def _attribute(text: str, name: str) -> str:
    found = re.search(r'\b%s="([^"]*)"' % name, text)
    return found.group(1) if found else ""


def _unquote(name: str) -> str:
    """``Reduction%20Transform.h5`` -> ``Reduction Transform.h5``."""
    return re.sub(r"%([0-9A-Fa-f]{2})",
                  lambda m: chr(int(m.group(1), 16)), name)


def _scene_nodes(scene_file: str) -> List[Tuple[str, str]]:
    with io.open(scene_file, encoding="utf-8", errors="replace") as handle:
        blob = handle.read()
    return [(match.group(1), match.group(2))
            for match in _NODE_RE.finditer(blob)]


def transform_chain(scene_file: str, model_name: str = MOVING_MODEL
                    ) -> List[str]:
    """The transform files above ``model_name``, nearest parent FIRST.

    Read out of ``scene.mrml`` rather than assumed from the file names, because
    the composition order is the one thing here that cannot be checked
    afterwards: ``Reduction Transform`` composed with ``Reduction Base`` the
    wrong way round is still a rigid pose, still lands the fragment somewhere
    plausible, and still produces a full table of millimetres. On every run
    saved so far ``Reduction Base`` is the identity, which is exactly why the
    order has to come from the scene -- an identity hides the mistake until the
    day a run has a real one.

    Raises when the chain cannot be resolved: a non-linear transform in it, a
    transform with no saved file, or a cycle.
    """
    nodes = _scene_nodes(scene_file)
    by_id: Dict[str, Tuple[str, str]] = {}
    for tag, attributes in nodes:
        node_id = _attribute(attributes, "id")
        if node_id:
            by_id[node_id] = (tag, attributes)

    model = None
    for tag, attributes in nodes:
        if tag == "Model" and _attribute(attributes, "name") == model_name:
            model = attributes
            break
    if model is None:
        raise ValueError("scene.mrml names no model %r" % model_name)

    def parent_of(attributes: str) -> str:
        references = _attribute(attributes, "references")
        found = re.search(r"(?:^|;)transform:([^;]+)", references)
        return found.group(1) if found else ""

    def storage_file(attributes: str) -> str:
        references = _attribute(attributes, "references")
        found = re.search(r"(?:^|;)storage:([^;]+)", references)
        if not found or found.group(1) not in by_id:
            return ""
        return _unquote(_attribute(by_id[found.group(1)][1], "fileName"))

    chain: List[str] = []
    seen: List[str] = []
    current = parent_of(model)
    while current:
        if current in seen:
            raise ValueError("scene.mrml: the transform chain above %r loops"
                             % model_name)
        seen.append(current)
        if current not in by_id:
            raise ValueError("scene.mrml: %r is under transform %s, which the "
                             "scene does not declare" % (model_name, current))
        tag, attributes = by_id[current]
        if tag != "LinearTransform":
            raise ValueError("scene.mrml: %r is under a %s, which is not a "
                             "rigid pose this module can read"
                             % (model_name, tag))
        name = storage_file(attributes)
        if not name:
            raise ValueError("scene.mrml: transform %r above %r was not saved "
                             "to a file"
                             % (_attribute(attributes, "name"), model_name))
        chain.append(name)
        current = parent_of(attributes)
    if not chain:
        raise ValueError("scene.mrml: %r is under no transform -- this run "
                         "recorded no reduction to score" % model_name)
    return chain


def pose_from_scene(scene_dir: str, model_name: str = MOVING_MODEL
                    ) -> Tuple[np.ndarray, List[str]]:
    """``(4x4 to-world RAS, [file names, nearest parent first])``.

    A node's world pose is its parents applied outermost first, so the chain --
    which runs from the node upwards -- is composed in reverse.
    """
    chain = transform_chain(os.path.join(scene_dir, "scene.mrml"), model_name)
    pose = np.eye(4)
    for name in reversed(chain):
        path = os.path.join(scene_dir, name)
        if not os.path.isfile(path):
            raise ValueError("the scene names transform file %r, which is not "
                             "in Statistic/scene/" % name)
        pose = pose @ read_itk_affine(path)
    return pose, chain


# ---------------------------------------------------------------------------
# Rigid-transform arithmetic
# ---------------------------------------------------------------------------

def apply_transform(matrix: np.ndarray, points: np.ndarray) -> np.ndarray:
    """``matrix`` applied to an ``(N, 3)`` cloud (or a single point)."""
    matrix = np.asarray(matrix, dtype=np.float64)
    points = np.asarray(points, dtype=np.float64)
    flat = points.reshape(-1, 3)
    moved = flat @ matrix[:3, :3].T + matrix[:3, 3]
    return moved.reshape(points.shape)


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
        # 0 or 180 deg: the skew part vanishes and carries no axis. Zero is by
        # far the likelier here -- a 180 deg residual would fail every other
        # gate -- and its axis is meaningless anyway.
        return degrees, np.zeros(3)
    return degrees, axis / norm


def rotation_vector_deg(rotation: np.ndarray) -> np.ndarray:
    """The rotation as ``angle * axis``, in degrees."""
    degrees, axis = rotation_angle_axis(rotation)
    return degrees * axis


def is_rigid(matrix: np.ndarray) -> bool:
    rotation = np.asarray(matrix, dtype=np.float64)[:3, :3]
    return bool(
        np.abs(rotation @ rotation.T - np.eye(3)).max() <= ORTHONORMAL_TOLERANCE
        and abs(float(np.linalg.det(rotation)) - 1.0) <= ORTHONORMAL_TOLERANCE)


# ---------------------------------------------------------------------------
# Which frame the saved meshes are in
# ---------------------------------------------------------------------------

#: The two frames a Slicer-written model file can be in, and the only two this
#: module will consider. ``as-written`` is the file's own numbers; ``LPS->RAS``
#: mirrors x and y. Named rather than boolean because the choice is recorded in
#: every row (``mesh_frame``) and has to be readable there.
FRAME_AS_WRITTEN = "as-written"
FRAME_MIRRORED = "LPS->RAS"


def in_frame(points: np.ndarray, frame: str) -> np.ndarray:
    """``points`` converted into RAS according to a resolved frame label."""
    return lps_to_ras(points) if frame == FRAME_MIRRORED else np.asarray(
        points, dtype=np.float64)


def resolve_points_frame(points: np.ndarray, distance_to_witness
                         ) -> Tuple[np.ndarray, str, float]:
    """``(points in RAS, frame label, the witness distance)``.

    Slicer wrote these models in LPS, so they need mirroring in x and y before
    they can meet an ``*_ras`` matrix. That is a fact about a writer, not a law,
    and getting it wrong is not an error: the mirrored bone is the same bone on
    the far side of the origin, and every distance in this module would still be
    computed, just about nothing. So both frames are offered to a witness that
    knows where the bone actually is, and the closer one wins -- provided it is
    close at all. Neither fitting is a refusal, never a default.

    ``distance_to_witness(points, frame)`` returns how far a candidate cloud is
    from where the record says it should be, in mm. It is given the frame label
    as well as the points, so a witness that has to convert a second file (the
    annotation's saved shape, the other fragment) converts it the same way rather
    than inferring which candidate it was handed.
    """
    points = np.asarray(points, dtype=np.float64)
    scored: List[Tuple[float, str, np.ndarray]] = []
    for label in (FRAME_AS_WRITTEN, FRAME_MIRRORED):
        candidate = in_frame(points, label)
        try:
            scored.append((float(distance_to_witness(candidate, label)), label,
                           candidate))
        except Exception:
            logger.debug("Frame witness failed for %s", label, exc_info=True)
    if not scored:
        raise ValueError("no frame could be tested against the witness")
    scored.sort(key=lambda entry: entry[0])
    distance, label, candidate = scored[0]
    if distance > FRAME_TOLERANCE_MM:
        raise ValueError(
            "cannot place the saved meshes in RAS: the better of the two frames "
            "still leaves them %.1f mm from where the record says the bone is "
            "(limit %.0f mm). Refusing to score a possibly mirrored fragment."
            % (distance, FRAME_TOLERANCE_MM))
    return candidate, label, distance


# ---------------------------------------------------------------------------
# Reading the two kinds of ground truth
# ---------------------------------------------------------------------------

def read_annotation(path: str) -> Dict[str, Any]:
    """The surgeon's ``Moving_Segment_groundtruth.json``, parsed.

    Nothing is recomputed here. The file states ``G`` (``ground_truth_ras``), the
    pipeline's pose ``P`` (``pose_before_annotation_ras``) and the adjustment
    between them; this module re-derives the adjustment from ``G`` and its own
    ``P`` and then CHECKS it against the recorded one, which is a different thing
    from trusting it.
    """
    document = json.load(io.open(path, encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("%s is not a JSON object" % os.path.basename(path))
    parsed: Dict[str, Any] = {"path": path,
                              "fragment": document.get("fragment", ""),
                              "shape": document.get("shape", ""),
                              "annotated": document.get("annotated", "")}
    for key in ("ground_truth_ras", "pose_before_annotation_ras",
                "manual_adjustment_ras"):
        matrix = np.asarray(document.get(key), dtype=np.float64)
        if matrix.shape != (4, 4):
            raise ValueError("%s: %s is not a 4x4 matrix"
                             % (os.path.basename(path), key))
        parsed[key] = matrix
    for key in ("adjustment_rotation_deg", "adjustment_shift_mm"):
        value = document.get(key)
        parsed[key] = float(value) if isinstance(value, (int, float)) else None
    return parsed


def read_simulation(path: str) -> Dict[str, Any]:
    """The fracture simulator's record for one subject, parsed."""
    document = json.load(io.open(path, encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("%s is not a JSON object" % os.path.basename(path))
    displacement = np.asarray(document.get("displacement_matrix_ras"),
                              dtype=np.float64)
    if displacement.shape != (4, 4):
        raise ValueError("%s states no 4x4 displacement_matrix_ras"
                         % os.path.basename(path))
    if not is_rigid(displacement):
        raise ValueError("%s: displacement_matrix_ras is not a rigid transform"
                         % os.path.basename(path))
    # The record states the inverse too. Read it rather than inverting, and then
    # CHECK the two against each other: a hand-edited record whose two matrices
    # have drifted apart would otherwise be silently half-used, since this module
    # picks one or the other depending on which fragment the run moved.
    reduction = document.get("reduction_matrix_ras")
    reduction = (np.asarray(reduction, dtype=np.float64)
                 if isinstance(reduction, list) else np.linalg.inv(displacement))
    if reduction.shape != (4, 4) or np.abs(
            reduction @ displacement - np.eye(4)).max() > 1e-6:
        raise ValueError("%s: reduction_matrix_ras is not the inverse of "
                         "displacement_matrix_ras" % os.path.basename(path))
    centroid = np.asarray(document.get("moved_fragment_centroid_ras"),
                          dtype=np.float64)
    if centroid.shape != (3,):
        raise ValueError("%s states no moved_fragment_centroid_ras"
                         % os.path.basename(path))
    axis = document.get("shaft_axis_ras")
    axis = np.asarray(axis, dtype=np.float64) if isinstance(axis, list) else None
    if axis is not None and (axis.shape != (3,)
                             or not float(np.linalg.norm(axis))):
        axis = None
    site = document.get("fracture_site_ras")
    site = np.asarray(site, dtype=np.float64) if isinstance(site, list) else None
    if site is not None and site.shape != (3,):
        site = None
    displaced = document.get("displacement") or {}

    def number(container, key):
        value = container.get(key)
        return float(value) if isinstance(value, (int, float)) else None

    return {"path": path,
            "pattern": document.get("pattern", ""),
            "displacement_matrix_ras": displacement,
            "reduction_matrix_ras": reduction,
            "moved_fragment_centroid_ras": centroid,
            "shaft_axis_ras": (axis / float(np.linalg.norm(axis))
                               if axis is not None else None),
            "fracture_site_ras": site,
            "n_fixed_voxels": number(document, "n_fixed_voxels") or 0.0,
            "n_moved_voxels": number(document, "n_moved_voxels") or 0.0,
            "simulated_rotation_deg": number(displaced, "total_rotation_deg"),
            "simulated_translation_mm": number(displaced, "translation_mm")}


def fragment_centroids(labelmap_path: str, record: Dict[str, Any]
                       ) -> Tuple[np.ndarray, np.ndarray, float]:
    """``(moved centroid, fixed centroid, voxel-count mismatch)`` in RAS.

    The run saved the fractured labelmap the two fragments were cut from, but it
    is BINARY -- the pipeline thresholded it, so the two fragments are one blob
    in it and it cannot say on its own which is which. What it can say is where
    the union's centre of mass is, and the simulation states the moved fragment's
    centre and both voxel counts, so the fixed fragment's centre follows:

        c_fixed = (c_union . N - c_moved . n_moved) / n_fixed

    The mismatch returned beside them is ``|N - (n_fixed + n_moved)|``: the union
    must be exactly the two fragments, and it is (0 voxels out on every saved
    run). A non-zero mismatch means the labelmap in the run is not the one the
    record describes, and the derived centroid is then arithmetic about a
    different volume.
    """
    array, ijk_to_ras, _header = volume_io.read_nrrd(labelmap_path)
    filled = np.nonzero(array > 0)
    if not len(filled[0]):
        raise ValueError("%s is empty" % os.path.basename(labelmap_path))
    k_index, j_index, i_index = filled
    ijk = np.stack([i_index, j_index, k_index], axis=1).astype(np.float64)
    union = (ijk @ ijk_to_ras[:3, :3].T + ijk_to_ras[:3, 3]).mean(axis=0)

    moved_count = record["n_moved_voxels"]
    fixed_count = record["n_fixed_voxels"]
    if moved_count <= 0 or fixed_count <= 0:
        raise ValueError("%s states no fragment voxel counts"
                         % os.path.basename(record["path"]))
    total = moved_count + fixed_count
    moved = record["moved_fragment_centroid_ras"]
    fixed = (union * total - moved * moved_count) / fixed_count
    return moved, fixed, abs(float(len(k_index)) - total)


def decide_fragment_role(moving_centroid: np.ndarray,
                         reference_centroid: np.ndarray,
                         moved_centroid: np.ndarray,
                         fixed_centroid: np.ndarray) -> Tuple[str, float, float]:
    """``(role, margin_mm, cost_mm)`` -- which simulated fragment the run moved.

    A 2x2 assignment between the run's two meshes and the simulation's two
    fragments, scored by centroid distance and averaged over the two pairs so
    both numbers are in millimetres of one fragment.

    ``margin`` is how much better the winning assignment is than the other. It is
    reported rather than gated on here, because the verdict that actually decides
    the row is the abutment check downstream; on the saved runs the margin is
    never below 131 mm while the winning cost never exceeds 17 mm, which is the
    evidence that a surface centroid and a volume centroid being different points
    does not endanger the choice.
    """
    moving_centroid = np.asarray(moving_centroid, dtype=np.float64)
    reference_centroid = np.asarray(reference_centroid, dtype=np.float64)
    as_moved = (np.linalg.norm(moving_centroid - moved_centroid)
                + np.linalg.norm(reference_centroid - fixed_centroid)) / 2.0
    as_fixed = (np.linalg.norm(moving_centroid - fixed_centroid)
                + np.linalg.norm(reference_centroid - moved_centroid)) / 2.0
    role = "moved" if as_moved <= as_fixed else "fixed"
    return role, float(abs(as_moved - as_fixed)), float(min(as_moved, as_fixed))


def ground_truth_for_role(record: Dict[str, Any], role: str) -> np.ndarray:
    """The pose that reduces the run's moving fragment, given which one it is.

    The simulation displaced one fragment by ``D`` and left the other where the
    intact bone had it. Reducing the displaced one undoes ``D``; reducing the
    fixed one must instead carry it onto the displaced one, which is ``D`` itself
    -- a reduction is relative, and the reference is whatever the run did not
    move.
    """
    if role == "moved":
        return record["reduction_matrix_ras"]
    if role == "fixed":
        return record["displacement_matrix_ras"]
    raise ValueError("unknown fragment role %r" % role)


# ---------------------------------------------------------------------------
# What the residual transform says
# ---------------------------------------------------------------------------

def point_displacement_stats(points: np.ndarray, matrix: np.ndarray
                             ) -> Dict[str, float]:
    """How far each point travels under ``matrix``, in mm.

    The honest size of the error at the bone. ``translation_mm`` is measured at
    ONE point -- the fragment's centroid -- and a rigid body's displacement
    depends on which point you pick: a 3 deg residual rotation moves the far end
    of a 200 mm femur by 5 mm however small the translation is.
    """
    points = np.asarray(points, dtype=np.float64)
    lengths = np.linalg.norm(apply_transform(matrix, points) - points, axis=1)
    return {"mean": float(lengths.mean()),
            "rms": float(np.sqrt(np.mean(lengths ** 2))),
            "percentile": float(np.percentile(lengths, SURFACE_PERCENTILE)),
            "max": float(lengths.max())}


def _capped(points: np.ndarray, limit: int = SURFACE_MAX_POINTS) -> np.ndarray:
    points = np.asarray(points, dtype=np.float64)
    if len(points) <= limit:
        return points
    # A stride, not a random sample: the analysis has to give the same answer
    # twice, and nothing here seeds a generator.
    return points[::int(np.ceil(len(points) / float(limit)))]


def _kdtree():
    try:
        from scipy.spatial import cKDTree                     # noqa: PLC0415
        return cKDTree
    except ImportError:
        logger.info("scipy is unavailable; the distance columns are left blank")
        return None


def surface_distance_stats(first: np.ndarray, second: np.ndarray
                           ) -> Optional[Dict[str, float]]:
    """Symmetric point-to-point distance between two surface clouds, in mm."""
    first, second = _capped(first), _capped(second)
    tree = _kdtree()
    if tree is None or len(first) < MIN_SURFACE_POINTS \
            or len(second) < MIN_SURFACE_POINTS:
        return None
    forward, _unused = tree(second).query(first)
    backward, _unused = tree(first).query(second)
    both = np.concatenate([forward, backward])
    return {"mean": float(both.mean()),
            "rms": float(np.sqrt(np.mean(both ** 2))),
            "percentile": float(np.percentile(both, SURFACE_PERCENTILE)),
            "max": float(both.max())}


def median_distance(source: np.ndarray, target: np.ndarray) -> Optional[float]:
    """Median distance from each point of ``source`` to the nearest in ``target``.

    One-directional and a median, deliberately: this is used on the fracture
    surfaces, which the extension detects independently on each fragment and
    which therefore need not cover the same patch of bone. A mean or a maximum
    would be dominated by whichever rim one side found and the other did not, and
    the question being asked -- do these two surfaces sit on top of each other --
    is answered by the middle of the distribution.
    """
    source, target = _capped(source), _capped(target)
    tree = _kdtree()
    if tree is None or len(source) < MIN_SURFACE_POINTS \
            or len(target) < MIN_SURFACE_POINTS:
        return None
    distances, _unused = tree(target).query(source)
    return float(np.median(distances))


def principal_axis(points: np.ndarray, samples: int = 30000) -> np.ndarray:
    """The cloud's first principal direction, as a unit vector.

    Reported as a diagnostic, never used to decompose a residual -- see the
    module docstring: on the 57 runs where a recorded shaft axis exists this
    disagrees with it by a median of 6.5 deg and up to 12.4 deg, because a
    femoral head or a pair of condyles pulls the principal axis off the shaft.
    """
    points = np.asarray(points, dtype=np.float64)
    centred = _capped(points - points.mean(axis=0), samples)
    _u, _s, right = np.linalg.svd(centred, full_matrices=False)
    axis = right[0]
    return axis / float(np.linalg.norm(axis))


def angle_between(first: np.ndarray, second: np.ndarray) -> float:
    """Unsigned angle in degrees between two directions, treating them as axes."""
    first = np.asarray(first, dtype=np.float64)
    second = np.asarray(second, dtype=np.float64)
    cosine = abs(float(np.dot(first, second)))
    cosine /= float(np.linalg.norm(first) * np.linalg.norm(second))
    return float(np.degrees(np.arccos(min(1.0, cosine))))


def axis_decomposition(residual: np.ndarray, points: np.ndarray,
                       axis: np.ndarray, site: Optional[np.ndarray]
                       ) -> Dict[str, float]:
    """The residual split along and about the bone's own axis.

    The clinical reading of a long-bone reduction error: how much of the leftover
    rotation is *malrotation* (about the shaft) versus *angulation* (tipping it),
    and how much of the leftover translation is *shortening* (along the shaft)
    versus *offset* (across it).

    The rotation split is of the rotation VECTOR, so the two components recombine
    in quadrature to the total; rotation vectors do not add, which makes this
    exact only to second order -- negligible at the 0.2-13 deg residuals seen
    here and not at 90.

    ``axial_error_mm`` is SIGNED, against an axis pointed from the fracture site
    towards the fragment's far end: positive means the fragment has to move
    further from the fracture to be correct, i.e. the pipeline left it
    overlapping the reference; negative means it left it distracted. Without a
    fracture site the axis has no canonical direction and the magnitude is
    reported instead.
    """
    axis = np.asarray(axis, dtype=np.float64)
    axis = axis / float(np.linalg.norm(axis))
    points = np.asarray(points, dtype=np.float64)
    centroid = points.mean(axis=0)
    if site is not None:
        if float(np.dot(centroid - np.asarray(site, dtype=np.float64),
                        axis)) < 0:
            axis = -axis

    shift = apply_transform(residual, centroid[None])[0] - centroid
    along = float(np.dot(shift, axis))
    rotation = rotation_vector_deg(residual[:3, :3])
    torsion = float(np.dot(rotation, axis))
    return {"axial_rotation_deg": abs(torsion),
            "angulation_deg": float(np.linalg.norm(rotation - torsion * axis)),
            "axial_error_mm": along if site is not None else abs(along),
            "transverse_error_mm": float(np.linalg.norm(shift - along * axis))}


# ---------------------------------------------------------------------------
# Finding a case's files
# ---------------------------------------------------------------------------

def _matching(scene_dir: str, prefix: str, suffix: str) -> List[str]:
    return sorted(os.path.join(scene_dir, name)
                  for name in os.listdir(scene_dir)
                  if name.lower().startswith(prefix)
                  and name.lower().endswith(suffix))


def dataset_folder(experiment_root: str, subject: str) -> Tuple[str, str]:
    """``(folder, collection)`` for a subject, or ``("", "")``."""
    if not subject:
        return "", ""
    for collection in DATASET_COLLECTIONS:
        folder = os.path.join(experiment_root, DATASET_SUBDIR, collection,
                              subject)
        if os.path.isdir(folder):
            return folder, collection
    return "", ""


def find_case_files(case: Dict[str, str], experiment_root: str) -> Dict[str, Any]:
    """Everything one run needs, or an ``error`` naming what is missing.

    Ambiguity is an ERROR, not a guess. Two ``Moving fracture surface*.vtk`` in
    one scene folder means two detection runs were saved, and nothing in the
    names says which one the reduction used -- scoring the wrong one produces a
    complete, plausible verdict about a fracture surface the registration never
    saw.
    """
    scene_dir = case["scene_dir"]
    result: Dict[str, Any] = {
        "scene_dir": scene_dir, "moving": "", "reference": "",
        "moving_surface": "", "reference_surface": "", "annotation": "",
        "annotation_shape": "", "simulation": "", "labelmap": "",
        "dataset": "", "error": ""}
    if not os.path.isdir(scene_dir):
        result["error"] = "no Statistic/scene/ folder"
        return result

    problems: List[str] = []
    for key, name in (("moving", MOVING_MODEL), ("reference", REFERENCE_MODEL)):
        path = os.path.join(scene_dir, name + ".vtk")
        if os.path.isfile(path):
            result[key] = path
        else:
            problems.append("no %s.vtk" % name)
    for key, prefix in (("moving_surface", MOVING_SURFACE_PREFIX),
                        ("reference_surface", REFERENCE_SURFACE_PREFIX)):
        found = _matching(scene_dir, prefix, ".vtk")
        if len(found) == 1:
            result[key] = found[0]
        elif not found:
            problems.append("no '%s*.vtk'" % prefix)
        else:
            problems.append("%d files match '%s*.vtk' (%s) -- which one the "
                            "reduction used is not in the names"
                            % (len(found), prefix,
                               ", ".join(os.path.basename(p) for p in found)))

    subject = case.get("subject") or ""
    folder, collection = dataset_folder(experiment_root, subject)
    result["dataset"] = collection
    annotation = os.path.join(scene_dir, ANNOTATION_NAME)
    if os.path.isfile(annotation):
        result["annotation"] = annotation
        shape = os.path.join(scene_dir, ANNOTATION_SHAPE)
        result["annotation_shape"] = shape if os.path.isfile(shape) else ""
        if not result["annotation_shape"]:
            problems.append("%s is missing beside %s, so the recorded ground "
                            "truth cannot be attached to the shape it describes"
                            % (ANNOTATION_SHAPE, ANNOTATION_NAME))
    else:
        simulation = os.path.join(folder, subject + SIMULATION_SUFFIX)
        if folder and os.path.isfile(simulation):
            result["simulation"] = simulation
        else:
            problems.append(
                "no %s beside the run and no %s%s under Dataset/ -- neither "
                "kind of ground truth is available for %r"
                % (ANNOTATION_NAME, subject or "<subject>", SIMULATION_SUFFIX,
                   subject))
        # The input labelmap, which is every .nrrd in the folder that is not a
        # segmentation. It is what the fixed fragment's centroid is derived from.
        volumes = [path for path in _matching(scene_dir, "", ".nrrd")
                   if not path.lower().endswith(".seg.nrrd")]
        if len(volumes) == 1:
            result["labelmap"] = volumes[0]
        elif not volumes:
            problems.append("no input .nrrd in the scene folder, so the fixed "
                            "fragment's centroid cannot be derived")
        else:
            problems.append("%d input .nrrd files in the scene folder (%s) -- "
                            "which one the run was driven from is not in the "
                            "names"
                            % (len(volumes),
                               ", ".join(os.path.basename(p) for p in volumes)))

    result["error"] = "; ".join(problems)
    return result


def case_is_scorable(case: Dict[str, str], experiment_root: str) -> bool:
    return not find_case_files(case, experiment_root)["error"]


# ---------------------------------------------------------------------------
# One case
# ---------------------------------------------------------------------------

def _round(value: Optional[float], digits: int = 4) -> Optional[float]:
    return round(float(value), digits) if isinstance(value, (int, float)) else None


def _bone_and_side(subject: str) -> Tuple[str, str]:
    """``('femur', 'left')`` from ``s0287_femur_left``; blanks when unnamed.

    The 6-hospital subjects are numbered (``5``, ``10_204``) and say nothing
    about anatomy, so both come back empty rather than guessed -- these two
    columns are for grouping, and a wrong group is worse than no group.
    """
    lowered = (subject or "").lower()
    bone = next((name for name in ("femur", "humerus", "tibia", "radius",
                                   "ulna", "fibula") if name in lowered), "")
    side = next((name for name in ("left", "right") if name in lowered), "")
    return bone, side


def analyse_case(case: Dict[str, str], experiment_root: str) -> Dict[str, Any]:
    """One run -> one row, plus the notes worth surfacing beside it."""
    label = case.get("subject") or case["run"]
    files = find_case_files(case, experiment_root)
    bone, side = _bone_and_side(case.get("subject", ""))
    row: Dict[str, Any] = {
        "case": label, "run": case["run"], "dataset": files["dataset"],
        "bone": bone, "side": side, "status": "failed", "error": files["error"],
        "truth_source": ("annotation" if files["annotation"]
                         else ("simulation" if files["simulation"] else ""))}
    if files["error"]:
        return {"row": row, "notes": [files["error"]]}

    pose, chain = pose_from_scene(files["scene_dir"])
    row["pose_chain"] = " o ".join(chain)
    if not is_rigid(pose):
        raise ValueError("the pose composed from %s is not a rigid transform"
                         % row["pose_chain"])

    moving_raw = read_vtk_points(files["moving"])
    reference_raw = read_vtk_points(files["reference"])
    if len(moving_raw) < MIN_SURFACE_POINTS:
        raise ValueError("%s.vtk holds %d points"
                         % (MOVING_MODEL, len(moving_raw)))

    truth = (_annotated_truth(files, moving_raw, pose) if files["annotation"]
             else _simulated_truth(files, moving_raw, reference_raw))
    notes: List[str] = list(truth["notes"])
    row.update(truth["columns"])
    row["mesh_frame"] = truth["frame"]
    moving = truth["points"]

    # The residual. Everything below it is a reading of this one matrix.
    residual = truth["matrix"] @ np.linalg.inv(pose)
    row["moving_points"] = int(len(moving))
    _fill_error_columns(row, residual, truth["matrix"], moving, pose)
    _fill_witness_columns(row, files, truth, pose, notes)
    if truth.get("record") is not None:
        _fill_axis_columns(row, truth, residual, moving)

    if row.get("truth_verified") is False or row.get("record_consistent") is False:
        row["status"] = "unreliable"
        if not row["error"]:
            row["error"] = "a verdict failed -- see the notes in the log"
    else:
        row["status"] = "scored"
    return {"row": row, "notes": notes}


def _annotated_truth(files: Dict[str, Any], moving_raw: np.ndarray,
                     pose: np.ndarray) -> Dict[str, Any]:
    """``G`` for a surgeon-annotated case, and the frame the meshes live in.

    The frame witness is the annotation's own saved shape: ``G`` carries the
    moving fragment onto ``Moving_Segment_groundtruth.vtk`` by construction, so
    the frame in which it does is the frame the files are in. That same distance
    is also the check that the record describes THESE files, so it is kept as
    ``truth_shape_residual_mm`` rather than thrown away once the frame is fixed.
    """
    record = read_annotation(files["annotation"])
    matrix = record["ground_truth_ras"]
    shape_raw = read_vtk_points(files["annotation_shape"])
    if len(shape_raw) != len(moving_raw):
        raise ValueError(
            "%s holds %d points and %s holds %d: the annotation's shape is not "
            "this fragment's mesh, so the ground truth cannot be attached to it"
            % (ANNOTATION_SHAPE, len(shape_raw),
               os.path.basename(files["moving"]), len(moving_raw)))

    def witness(points, frame):
        # Same mesh, same vertex order, so the two clouds are compared point for
        # point rather than by a tree -- and the annotation's shape is converted
        # the same way the fragment was, since both came out of the same writer.
        return float(np.abs(apply_transform(matrix, points)
                            - in_frame(shape_raw, frame)).max())

    points, frame, residual = resolve_points_frame(moving_raw, witness)
    problems = _annotation_problems(record, pose)
    columns = {
        "truth_source": "annotation",
        "annotated": record.get("annotated", ""),
        "recorded_rotation_deg": _round(record.get("adjustment_rotation_deg")),
        "recorded_shift_mm": _round(record.get("adjustment_shift_mm")),
        "pose_h5_residual_mm": _round(
            float(np.abs(pose - record["pose_before_annotation_ras"]).max()), 12),
        "truth_shape_residual_mm": _round(residual, 6),
        "record_consistent": not problems,
    }
    return {"matrix": matrix, "points": points, "frame": frame,
            "notes": problems, "columns": columns, "record": None}


def _annotation_problems(record: Dict[str, Any], pose: np.ndarray) -> List[str]:
    """The annotation judged against ITSELF, and against the run's own pose."""
    problems: List[str] = []
    matrix = record["ground_truth_ras"]
    if not is_rigid(matrix):
        problems.append("ground_truth_ras is not a rigid transform")
    recorded_pose = record["pose_before_annotation_ras"]
    adjustment = record["manual_adjustment_ras"]
    if np.abs(adjustment @ recorded_pose - matrix).max() > 1e-6:
        problems.append("manual_adjustment_ras does not carry "
                        "pose_before_annotation_ras onto ground_truth_ras")
    gap = float(np.abs(pose - recorded_pose).max())
    if gap > POSE_RESIDUAL_LIMIT_MM:
        problems.append(
            "the pose composed from the run's .h5 transforms differs from the "
            "recorded pose_before_annotation_ras by %.3g -- the annotation was "
            "written for a different reduction than the one saved here" % gap)
    stated = record.get("adjustment_rotation_deg")
    if stated is not None:
        degrees, _axis = rotation_angle_axis(adjustment[:3, :3])
        if abs(degrees - stated) > RECORD_TOLERANCE_DEG:
            problems.append("adjustment_rotation_deg says %.4f, the matrix "
                            "encodes %.4f" % (stated, degrees))
    return problems


def _simulated_truth(files: Dict[str, Any], moving_raw: np.ndarray,
                     reference_raw: np.ndarray) -> Dict[str, Any]:
    """``G`` for a simulated case: decide which fragment the run moved.

    The frame is settled BEFORE the role, and by a fact that does not depend on
    it: whichever fragment the run segmented, one of the two meshes IS the
    simulation's displaced fragment, so in the right frame one of them is within
    a fragment's width of ``moved_fragment_centroid_ras`` and in the mirrored one
    neither is within hundreds of millimetres.
    """
    record = read_simulation(files["simulation"])
    target = record["moved_fragment_centroid_ras"]
    notes: List[str] = []

    def witness(points, frame):
        partner = in_frame(reference_raw, frame)
        return min(float(np.linalg.norm(points.mean(axis=0) - target)),
                   float(np.linalg.norm(partner.mean(axis=0) - target)))

    points, frame, _distance = resolve_points_frame(moving_raw, witness)
    reference = in_frame(reference_raw, frame)

    moved, fixed, mismatch = fragment_centroids(files["labelmap"], record)
    if mismatch:
        notes.append("the saved labelmap holds %.0f voxels more or fewer than "
                     "the two fragments the record counts, so the fixed "
                     "fragment's centroid is derived from a different volume "
                     "than the record describes" % mismatch)
    role, margin, cost = decide_fragment_role(points.mean(axis=0),
                                              reference.mean(axis=0),
                                              moved, fixed)
    columns = {
        "truth_source": "simulation",
        "fracture_pattern": record["pattern"],
        "fragment_role": role,
        "role_margin_mm": _round(margin, 2),
        "role_cost_mm": _round(cost, 2),
        "simulated_rotation_deg": _round(record["simulated_rotation_deg"]),
        "simulated_translation_mm": _round(record["simulated_translation_mm"]),
    }
    return {"matrix": ground_truth_for_role(record, role), "points": points,
            "frame": frame, "notes": notes, "columns": columns,
            "record": record, "role": role}


def _fill_error_columns(row: Dict[str, Any], residual: np.ndarray,
                        truth: np.ndarray, moving: np.ndarray,
                        pose: np.ndarray) -> None:
    """The residual, read every way this module reports it."""
    planned = apply_transform(pose, moving)
    centroid = planned.mean(axis=0)
    shift = apply_transform(residual, centroid[None])[0] - centroid
    degrees, axis = rotation_angle_axis(residual[:3, :3])

    row["rotation_deg"] = _round(degrees)
    row["translation_mm"] = _round(float(np.linalg.norm(shift)))
    for name, value in zip(("shift_r_mm", "shift_a_mm", "shift_s_mm"), shift):
        row[name] = _round(float(value))
    for name, value in zip(("rot_axis_r", "rot_axis_a", "rot_axis_s"), axis):
        row[name] = _round(float(value))

    stats = point_displacement_stats(planned, residual)
    row["point_error_mean_mm"] = _round(stats["mean"])
    row["point_error_rms_mm"] = _round(stats["rms"])
    row["point_error_p95_mm"] = _round(stats["percentile"])
    row["point_error_max_mm"] = _round(stats["max"])

    surface = surface_distance_stats(planned, apply_transform(truth, moving))
    if surface:
        row["surface_mean_mm"] = _round(surface["mean"])
        row["surface_rms_mm"] = _round(surface["rms"])
        row["surface_hd95_mm"] = _round(surface["percentile"])
        row["surface_max_mm"] = _round(surface["max"])

    # How large the problem was, measured exactly the same way as the residual so
    # the two are comparable and their ratio means something. The un-reduced
    # fragment is the mesh as saved, so the transform from it to the truth IS the
    # ground-truth pose.
    initial_degrees, _unused = rotation_angle_axis(truth[:3, :3])
    initial_centroid = moving.mean(axis=0)
    row["initial_rotation_deg"] = _round(initial_degrees)
    row["initial_shift_mm"] = _round(float(np.linalg.norm(
        apply_transform(truth, initial_centroid[None])[0] - initial_centroid)))
    initial = point_displacement_stats(moving, truth)
    row["initial_point_error_mean_mm"] = _round(initial["mean"])
    if initial["mean"] > 1e-9:
        row["residual_fraction"] = _round(stats["mean"] / initial["mean"])


def _fill_witness_columns(row: Dict[str, Any], files: Dict[str, Any],
                          truth: Dict[str, Any], pose: np.ndarray,
                          notes: List[str]) -> None:
    """The abutment verdict: does this ground truth actually close the fracture?

    A reduction IS the two fracture surfaces meeting, so a ``G`` that leaves them
    apart is not this fragment's ground truth. It is the only check that covers
    both populations, and on the simulated ones it is what stands behind the
    choice of which fragment the run moved -- the wrong matrix leaves the
    surfaces 14.7-60.7 mm apart where the right one leaves them under 2.

    ``pipeline_fit_mm`` is recorded beside it for reading and NOT as an accuracy
    score: a fragment can mate its fracture surface perfectly and still be
    rotated about it, which is exactly the error this module exists to measure.
    """
    frame = truth["frame"]
    moving_surface = in_frame(read_vtk_points(files["moving_surface"]), frame)
    reference_surface = in_frame(read_vtk_points(files["reference_surface"]),
                                 frame)

    row["truth_fit_mm"] = _round(median_distance(
        apply_transform(truth["matrix"], moving_surface), reference_surface))
    row["pipeline_fit_mm"] = _round(median_distance(
        apply_transform(pose, moving_surface), reference_surface))

    fit = row["truth_fit_mm"]
    if fit is None:
        row["truth_verified"] = None
        notes.append("the fracture surfaces could not be compared, so the "
                     "ground truth stands unchecked")
        return
    row["truth_verified"] = bool(fit <= TRUTH_FIT_LIMIT_MM)
    if not row["truth_verified"]:
        notes.append(
            "the ground truth does not close the fracture: after applying it "
            "the moving fragment's fracture surface still sits %.1f mm from the "
            "reference's (limit %.1f). This row is about the wrong reduction."
            % (fit, TRUTH_FIT_LIMIT_MM))


def _fill_axis_columns(row: Dict[str, Any], truth: Dict[str, Any],
                       residual: np.ndarray, moving: np.ndarray) -> None:
    """The clinical split, and the measurement that says why it is only here.

    The axis is the simulation's own ``shaft_axis_ras``, stated in the INTACT
    bone's frame. The run's ground-truth frame is that frame only when the run
    moved the displaced fragment; when it moved the fixed one, the reduced
    configuration is the displaced fragment's, so the axis and the fracture site
    are carried there by the displacement itself.
    """
    record = truth["record"]
    axis = record["shaft_axis_ras"]
    if axis is None:
        return
    anatomy = (np.eye(4) if truth.get("role") == "moved"
               else record["displacement_matrix_ras"])
    axis_in_truth = anatomy[:3, :3] @ axis
    site = record["fracture_site_ras"]
    site_in_truth = (apply_transform(anatomy, site[None])[0]
                     if site is not None else None)

    reduced = apply_transform(truth["matrix"], moving)
    for key, value in axis_decomposition(residual, reduced, axis_in_truth,
                                         site_in_truth).items():
        row[key] = _round(value)
    row["pca_axis_vs_recorded_deg"] = _round(
        angle_between(principal_axis(reduced), axis_in_truth), 2)


# ---------------------------------------------------------------------------
# Timing, split into the extension's own stages
# ---------------------------------------------------------------------------

def phase_row(case: Dict[str, str], timing: Dict[str, Any],
              steps: List[Dict[str, Any]], log: List[str]) -> Dict[str, Any]:
    """One run's time, split into t0..t6. Mirrors ``pelvic.phase_row``."""
    label = case.get("subject") or case["run"]
    row: Dict[str, Any] = {"case": label, "run": case["run"]}

    totals = {phase: {"wall": 0.0, "exec": 0.0, "wait": 0.0}
              for phase in list(PHASE_ORDER) + ["unassigned"]}
    seen: List[str] = []
    unassigned: List[str] = []
    for step in steps:
        # A '<< step back' row is a replay review, not a step: its seconds are
        # reported separately as replay_review_s, and summing it into a phase
        # would charge scrubbing the timeline to whichever phase was on screen.
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
        for key, name in (("wall", "wall_s"), ("exec", "exec_s"),
                          ("wait", "wait_s")):
            value = step.get(name)
            totals[phase][key] += (float(value)
                                   if isinstance(value, (int, float)) else 0.0)

    for phase in PHASE_ORDER:
        row["%s_s" % phase] = round(totals[phase]["wall"], 3)
        row["%s_exec_s" % phase] = round(totals[phase]["exec"], 3)
        row["%s_wait_s" % phase] = round(totals[phase]["wait"], 3)

    phase_sum = sum(totals[phase]["wall"] for phase in PHASE_ORDER) \
        + totals["unassigned"]["wall"]
    row["phase_sum_s"] = round(phase_sum, 3)
    for name in ("total_s", "inside_steps_s", "startup_s", "between_steps_s",
                 "replay_review_s", "tail_wait_exit_s"):
        if isinstance(timing.get(name), float):
            row[name if name != "total_s" else "t_total_s"] = timing[name]
    if isinstance(timing.get("inside_steps_s"), float):
        # Not clamped: a non-zero residual is the only evidence a reader has
        # that the phases and the run clock disagree.
        row["phase_residual_s"] = round(timing["inside_steps_s"] - phase_sum, 3)

    row["steps_seen"] = len(seen)
    row["steps_unassigned"] = ", ".join(unassigned)
    if unassigned:
        log.append("   [!] %s: %d step(s) in no timing phase (%s) -- PHASE_STEPS "
                   "is out of date with the workflow, and t0..t6 are short by "
                   "their time" % (label, len(unassigned), ", ".join(unassigned)))
    return row


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------

CASE_COLUMNS = [
    "case", "dataset", "bone", "side", "truth_source", "status",
    "rotation_deg", "translation_mm",
    "point_error_mean_mm", "point_error_rms_mm", "point_error_p95_mm",
    "point_error_max_mm",
    "surface_mean_mm", "surface_rms_mm", "surface_hd95_mm", "surface_max_mm",
    "axial_rotation_deg", "angulation_deg", "axial_error_mm",
    "transverse_error_mm",
    "initial_rotation_deg", "initial_shift_mm", "initial_point_error_mean_mm",
    "residual_fraction",
    "shift_r_mm", "shift_a_mm", "shift_s_mm",
    "rot_axis_r", "rot_axis_a", "rot_axis_s",
    "truth_fit_mm", "pipeline_fit_mm", "truth_verified",
    "fragment_role", "role_margin_mm", "role_cost_mm", "fracture_pattern",
    "simulated_rotation_deg", "simulated_translation_mm",
    "pca_axis_vs_recorded_deg",
    "recorded_rotation_deg", "recorded_shift_mm", "pose_h5_residual_mm",
    "truth_shape_residual_mm", "record_consistent", "annotated",
    "mesh_frame", "pose_chain", "moving_points", "error", "run",
]

SUMMARY_COLUMNS = ["population", "metric", "n", "mean", "sd", "median", "min",
                   "max", "note"]

PHASE_COLUMNS = (["case", "run", "t_total_s", "inside_steps_s"]
                 + ["%s_s" % phase for phase in PHASE_ORDER]
                 + ["phase_sum_s", "phase_residual_s"]
                 + ["%s_exec_s" % phase for phase in PHASE_ORDER]
                 + ["%s_wait_s" % phase for phase in PHASE_ORDER]
                 + ["startup_s", "between_steps_s", "replay_review_s",
                    "tail_wait_exit_s", "steps_seen", "steps_unassigned"])

DEFINITION_COLUMNS = ["term", "definition"]

#: The metrics the summary block reports, per population.
SUMMARY_METRICS = [
    ("rotation_deg", "residual rotation (deg)"),
    ("translation_mm", "residual translation at the centroid (mm)"),
    ("point_error_mean_mm", "point error, mean over the surface (mm)"),
    ("point_error_p95_mm", "point error, 95th percentile (mm)"),
    ("point_error_max_mm", "point error, worst point (mm)"),
    ("surface_hd95_mm", "surface distance, 95th percentile (mm)"),
    ("axial_rotation_deg", "malrotation about the shaft (deg)"),
    ("angulation_deg", "angulation across the shaft (deg)"),
    ("axial_error_mm", "shortening (+) / distraction (-) along the shaft (mm)"),
    ("transverse_error_mm", "offset across the shaft (mm)"),
    ("initial_point_error_mean_mm", "displacement to be corrected, mean (mm)"),
    ("residual_fraction", "what fraction of it was left (0 = perfect)"),
    ("truth_fit_mm", "fracture gap under the ground truth (mm)"),
]


METHOD_DEFINITIONS = [
    ("what is measured",
     "E = G . P^-1, the rigid transform still needed to carry the pipeline's "
     "reduced fragment onto the ground truth, in world RAS. P is the pose the "
     "run computed (read from its own Reduction Transform.h5 / Reduction "
     "Base.h5, composed in the order scene.mrml declares); G is the ground "
     "truth pose for the same fragment. Every millimetre and degree in the "
     "table is a reading of that one matrix."),
    ("where G comes from -- annotated cases",
     "The run's own Moving_Segment_groundtruth.json, written when the surgeon "
     "saved the annotation: ground_truth_ras IS G. Nothing is registered or "
     "estimated. rotation_deg reproduces the file's own "
     "adjustment_rotation_deg to 1e-6 deg, and recorded_rotation_deg / "
     "recorded_shift_mm are carried in the table so that can be seen rather "
     "than believed."),
    ("where G comes from -- simulated cases",
     "The fracture simulator's <subject>_fracture.json, which states the rigid "
     "displacement_matrix_ras D it applied to ONE of the two fragments. If the "
     "run moved that fragment, reducing it means undoing D, so G = D^-1; if the "
     "run moved the OTHER fragment, its reference is the displaced one, so "
     "G = D. Which of the two is a property of the run -- the surgeon segments "
     "whichever fragment they choose to move -- and it is 'moved' in 25 of "
     "these 57 runs and 'fixed' in 32."),
    ("how that choice is made, and how it is checked",
     "Made by centroid: the record states the displaced fragment's centre and "
     "both voxel counts, and the run saved the labelmap they were cut from, so "
     "the fixed fragment's centre follows from the union's. Assigning the run's "
     "two meshes to those two centres is a 2x2 assignment (fragment_role, with "
     "role_margin_mm and role_cost_mm beside it). Checked by abutment: a "
     "correct G closes the fracture, so truth_fit_mm -- the median distance "
     "between the two fracture surfaces afterwards -- is 0.3-1.7 mm with the "
     "right matrix and 14.7-60.7 mm with the wrong one."),
    ("why the h5 reader may be trusted",
     "On the seven annotated runs the pose composed from the .h5 files equals "
     "the pose_before_annotation_ras those runs recorded independently, to "
     "6e-14 (pose_h5_residual_mm). Those seven are what license the same reader "
     "on the other 57, where nothing else states the pose."),
    ("why no shaft axis is estimated",
     "The clinical split needs the bone's own axis. The obvious estimate -- the "
     "fragment's principal axis -- disagrees with the axis the simulation "
     "recorded by a median of 6.5 deg and up to 12.4 deg "
     "(pca_axis_vs_recorded_deg), which is larger than most of the residual "
     "rotations it would be decomposing. So the four decomposition columns are "
     "reported only where the axis is a recorded fact, and are blank on the "
     "annotated cases. A blank there is a refusal, not a zero."),
    ("what is NOT computed",
     "No overlap score (Dice) and no registration of any kind. Both fragments "
     "are rigid and their pose error is stated exactly by E; an overlap would "
     "be a lossy function of the same thing, measured on a third resampling of "
     "data that is already sampled two different ways."),
]

CASE_DEFINITIONS = [
    ("rotation_deg / translation_mm",
     "The residual E as an angle and as a displacement. translation_mm is "
     "measured AT THE FRAGMENT'S CENTROID, because a rigid body's displacement "
     "depends on which point you pick; shift_r/a/s_mm are its components in RAS "
     "and rot_axis_r/a/s the rotation's axis as a unit vector."),
    ("point_error_*_mm",
     "E applied to every point of the moving fragment's own surface, and how "
     "far each one travels: rotation and translation combined, at the bone. "
     "This is the number to quote as 'how wrong is the reduction'. It is always "
     "at least translation_mm and usually well above it."),
    ("surface_*_mm",
     "Symmetric distance between the pipeline's reduced fragment and the ground "
     "truth's, surface to surface. Always SMALLER than point_error, because a "
     "point that slid ALONG the bone still has a near neighbour on it -- which "
     "on a long bone is exactly the shortening component. surface_hd95_mm is "
     "the %.0fth percentile, which is what to quote; surface_max_mm is beside "
     "it but must not lead." % SURFACE_PERCENTILE),
    ("axial_rotation_deg / angulation_deg",
     "The residual rotation split about and across the bone's own axis: "
     "malrotation versus angulation. Of the rotation VECTOR, so the two "
     "recombine in quadrature to rotation_deg. Simulated cases only."),
    ("axial_error_mm / transverse_error_mm",
     "The residual translation split along and across the same axis: "
     "shortening/distraction versus offset. axial_error_mm is SIGNED against an "
     "axis pointed from the fracture site outwards -- positive means the "
     "fragment must move further from the fracture to be correct, i.e. the "
     "pipeline left it overlapping the reference. Simulated cases only."),
    ("initial_* / residual_fraction",
     "How large the displacement was before the reduction, measured exactly the "
     "way the residual is (the un-reduced mesh carried onto the truth), so the "
     "two are comparable. residual_fraction is "
     "point_error_mean / initial_point_error_mean: 0 is a perfect reduction and "
     "1 is having done nothing. A 1 mm residual is excellent on a fragment that "
     "was 40 mm out and unremarkable on one that was 3 mm out, which is why "
     "these columns sit beside the error and not in a footnote."),
    ("truth_fit_mm / pipeline_fit_mm / truth_verified",
     "The median distance from the moving fragment's fracture surface to the "
     "reference's, after the ground truth pose and after the pipeline's. The "
     "first is the VERDICT on the ground truth -- a reduction closes the "
     "fracture, so a G that does not is the wrong G (truth_verified is it "
     "against %.0f mm). The second is beside it for reading, NOT as an accuracy "
     "score: a fragment can mate its fracture surface perfectly and still be "
     "rotated about it." % TRUTH_FIT_LIMIT_MM),
    ("fragment_role / role_margin_mm / role_cost_mm",
     "Which of the simulation's two fragments this run moved, how much better "
     "that assignment scored than the other one, and what the winning "
     "assignment itself cost. The margin is never below 131 mm on the saved "
     "runs while the cost never exceeds 17 mm, which is why a surface centroid "
     "and a volume centroid being different points does not endanger it."),
    ("recorded_* / pose_h5_residual_mm / truth_shape_residual_mm / "
     "record_consistent",
     "Annotated cases only: what the annotation itself stated, how far the pose "
     "recovered from the run's transform files is from the pose it recorded "
     "(a reader check -- 6e-14), and how far the ground truth pose applied to "
     "the mesh lands from the shape the annotation saved beside it (a check "
     "that the record describes THESE files). record_consistent is those "
     "checks plus the record's agreement with itself."),
    ("mesh_frame / pose_chain / moving_points",
     "Which frame the saved .vtk models turned out to be in (Slicer writes them "
     "in LPS, so 'LPS->RAS' is expected -- it is measured per case rather than "
     "assumed), which transform files were composed to make P and in what "
     "order, and how many surface points the point statistics are over."),
    ("status",
     "'scored' (every verdict passed), 'unreliable' (a verdict failed -- read "
     "the error column and treat the millimetres as unproven), 'failed' (no row "
     "could be built at all)."),
]

PHASE_DEFINITIONS = [
    ("t0..t6",
     "Wall time in each stage of the extension's own panel: "
     + "; ".join("%s = %s" % (phase, PHASE_TITLES[phase])
                 for phase in PHASE_ORDER)
     + ". t5 and t6 are deliberately separate: t5 is the surgeon dragging the "
       "fragment into a rough alignment by hand and t6 is the extension's own "
       "registration, and merging them would report hand time as compute time."),
    ("*_exec_s / *_wait_s",
     "The phase's time split into SafeExecutor time (the generated code actually "
     "running) and everything else -- which on a choice or interaction step is "
     "the surgeon, and on an automated step is dispatch and panel render."),
    ("phase_sum_s / phase_residual_s",
     "The phases summed, and inside_steps_s minus that. It should be ~0 (the "
     "timing report's own rounding); it is printed rather than hidden, because "
     "a real gap means a step landed in no phase and is named in "
     "steps_unassigned."),
    ("t_total_s / startup_s / between_steps_s / replay_review_s / "
     "tail_wait_exit_s",
     "The whole run and its components, straight from Statistic/timing.txt. See "
     "the Timing sheet's own definitions."),
]


def definition_rows(pairs: Sequence[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"term": term, "definition": text} for term, text in pairs]


def _stats(values: Sequence[Optional[float]]) -> Dict[str, Any]:
    numbers = [float(v) for v in values if isinstance(v, (int, float))]
    if not numbers:
        return {"n": 0, "mean": None, "sd": None, "median": None,
                "min": None, "max": None}
    array = np.asarray(numbers, dtype=np.float64)
    return {"n": len(numbers),
            "mean": round(float(array.mean()), 4),
            # Sample standard deviation, undefined for a single value rather
            # than reported as zero -- a zero there would read as agreement.
            "sd": round(float(array.std(ddof=1)), 4) if len(numbers) > 1 else None,
            "median": round(float(np.median(array)), 4),
            "min": round(float(array.min()), 4),
            "max": round(float(array.max()), 4)}


def _trusted(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Scored, and not contradicted by the fracture surfaces.

    ``record_consistent`` is None on a simulated case, which must not read as a
    failure -- ``is not False`` rather than truthiness.
    """
    return [row for row in rows
            if row.get("status") == "scored"
            and row.get("truth_verified") is not False
            and row.get("record_consistent") is not False]


def summary_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Per population, then over everything. Never pooled silently.

    The two populations are not the same experiment: one has a surgeon's
    annotation as its truth and the other a simulator's own record, and only the
    second can state a shaft axis. A single pooled mean would answer neither
    question and would drift with the proportion of each in the folder, so the
    pooled block comes LAST and only for the metrics both populations carry.
    """
    trusted = _trusted(rows)
    populations: List[Tuple[str, List[Dict[str, Any]]]] = []
    for name, source in (("annotated (6 hospitals)", "annotation"),
                         ("simulated (TotalSegmentor)", "simulation")):
        subset = [row for row in trusted if row.get("truth_source") == source]
        if subset:
            populations.append((name, subset))

    def carried(subset: List[Dict[str, Any]], key: str) -> bool:
        return any(isinstance(row.get(key), (int, float)) for row in subset)

    shared = [(key, title) for key, title in SUMMARY_METRICS
              if all(carried(subset, key) for _name, subset in populations)]
    if len(populations) > 1:
        # Pooled LAST, and only over the metrics EVERY population carries. The
        # four decomposition columns exist on the simulated cases alone, so a
        # pooled row for one of them would be the simulated row printed twice
        # under a name that says it covers everything.
        populations.append(("all cases", trusted))

    out: List[Dict[str, Any]] = []
    for index, (name, subset) in enumerate(populations):
        pooled = len(populations) > 1 and index == len(populations) - 1
        for key, title in (shared if pooled else SUMMARY_METRICS):
            values = [row.get(key) for row in subset]
            if not any(isinstance(value, (int, float)) for value in values):
                continue
            entry = {"population": name, "metric": title}
            entry.update(_stats(values))
            if key == "axial_error_mm":
                entry["note"] = ("signed: positive is overlap, negative is "
                                 "distraction, so the mean can cancel -- read "
                                 "it beside min/max")
            out.append(entry)
        entry = {"population": name, "metric": "cases", "n": len(subset),
                 "note": "cases counted in the rows above"}
        if pooled and len(shared) != len(SUMMARY_METRICS):
            entry["note"] += ("; %d metric(s) omitted here because only one "
                              "population carries them -- read those in that "
                              "population's own block"
                              % (len(SUMMARY_METRICS) - len(shared)))
        out.append(entry)

    untrusted = [row for row in rows if row not in trusted]
    if untrusted:
        out.append({"population": "excluded", "metric": "cases not counted",
                    "n": len(untrusted),
                    "note": "a verdict failed or no row could be built: "
                            + ", ".join(sorted({row["case"]
                                                for row in untrusted})[:8])})
    return out


def discover_cases(experiment_root: str) -> List[Dict[str, str]]:
    """One entry per run folder under ``Overall_Performance``."""
    return _discover_cases(experiment_root, RUNS_SUBDIR, DATASET_SUBDIR)


def build_report(experiment_root: str, progress=None) -> Dict[str, Any]:
    """Analyse every case. Fail-soft per case, so one bad scene costs one row."""
    cases = discover_cases(experiment_root)
    rows: List[Dict[str, Any]] = []
    failed: List[str] = []
    log: List[str] = []
    if not cases:
        log.append("No cases found under %s."
                   % os.path.join(experiment_root, RUNS_SUBDIR))

    for index, case in enumerate(cases):
        label = case.get("subject") or case["run"]
        if progress is not None:
            try:
                progress(index, len(cases), label)
            except Exception:
                logger.debug("Progress callback failed", exc_info=True)
        # Before the work, not after: a hard crash takes the report with it, so
        # the last line logged is the only record of which case was in flight.
        logger.info("[LBFR] case %d/%d: %s", index + 1, len(cases), label)
        try:
            result = analyse_case(case, experiment_root)
        except Exception as exc:
            log.append("%s: FAILED -- %s" % (label, exc))
            logger.warning("Long-bone analysis failed for %s", label,
                           exc_info=True)
            # Recorded, not merely logged. A case that produces no row is
            # invisible in every table, and a caller quoting the DISCOVERED
            # count beside a mean taken over fewer would overstate the sweep.
            failed.append(label)
            continue
        rows.append(result["row"])
        row = result["row"]
        log.append("%s [%s]: rotation %s deg, translation %s mm, point error "
                   "mean %s mm (was %s mm before the reduction)"
                   % (label, row.get("truth_source") or "?",
                      _fmt(row.get("rotation_deg")),
                      _fmt(row.get("translation_mm")),
                      _fmt(row.get("point_error_mean_mm")),
                      _fmt(row.get("initial_point_error_mean_mm"))))
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

    summary = summary_rows(rows)
    timing_title, timing_blocks = timing_sheet(timing_rows, step_rows)

    sheets = [
        ("Reduction accuracy", [
            ("One row per run: how far the planned reduction ended up from the "
             "ground truth, read from the single rigid residual E = G . P^-1. "
             "point_error_mean_mm is the number to quote; read it beside "
             "initial_point_error_mean_mm, which is how far out the fragment "
             "was to begin with.",
             CASE_COLUMNS, rows),
            ("Per population, over the cases that passed every verdict. The two "
             "populations are reported separately because their ground truth "
             "comes from different places and only the simulated one can state "
             "a shaft axis; the pooled block is last and covers only what both "
             "carry.",
             SUMMARY_COLUMNS, summary),
            ("DEFINITIONS — how the measurement is made",
             DEFINITION_COLUMNS, definition_rows(METHOD_DEFINITIONS)),
            ("DEFINITIONS — per-case columns",
             DEFINITION_COLUMNS, definition_rows(CASE_DEFINITIONS)),
        ]),
        (timing_title, [
            ("The run's time split into the extension's own stages, summed from "
             "the per-step timeline below.",
             PHASE_COLUMNS, phase_rows),
            ("DEFINITIONS — phase columns",
             DEFINITION_COLUMNS, definition_rows(PHASE_DEFINITIONS)),
        ] + list(timing_blocks)),
    ]
    return {"sheets": sheets, "log": log, "rows": rows, "summary": summary,
            "phase_rows": phase_rows, "timing_rows": timing_rows,
            "step_rows": step_rows, "cases": len(cases),
            "analysed": len(rows), "failed_cases": failed}


def _fmt(value: Optional[float]) -> str:
    return "%.2f" % value if isinstance(value, (int, float)) else "--"


def run_analysis(repository_root: str, progress=None) -> Dict[str, Any]:
    """Analyse every case and write the workbook. Returns the report + its path."""
    from .workbook import write_workbook                      # noqa: PLC0415

    experiment_root = os.path.join(repository_root, EXPERIMENT_DIR)
    report = build_report(experiment_root, progress=progress)
    output = os.path.join(experiment_root, RUNS_SUBDIR, WORKBOOK_NAME)
    written, notes = write_workbook(output, report["sheets"])
    report["workbook"] = written
    report["log"].extend(notes)
    try:
        report["workbook_relative"] = os.path.relpath(written, repository_root)
    except ValueError:
        report["workbook_relative"] = written
    return report
