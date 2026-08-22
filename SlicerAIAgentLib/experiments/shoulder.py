"""ReverseShoulderArthroplasty: the screw/peg angles, the bone-density ratio, and
where the run's time went.

Scores every run under ``Experiments/ReverseShoulderArthroplasty/Overall_Performance/``
against the four measures of Li et al., *Automatic surgical planning based on bone
density assessment and path integral in cone space for reverse shoulder
arthroplasty* (IJCARS 2022, 17:1017-1027), Table 1:

    theta1  angle between long screw 1 and the middle peg
    theta2  angle between long screw 2 and the middle peg
    theta3  angle between the two long screws
    delta   the chosen path's bone-density integral divided by the LARGEST
            integral anywhere in the cone, ignoring the screw-exposure
            constraint. 1.0 means the containment constraint cost nothing.

and t1 / t2 / t3 / t -- 3D reconstruction, reference-point picking, automatic
planning, and the whole procedure.

WHY EVERY NUMBER IS RECOMPUTED FROM THE SAVED SCENE
---------------------------------------------------
The extension stores none of this. ``RSA_PlanResults.tsv`` carries endpoints,
lengths and a status string but no score; ``quality_index`` is identically 1.000
by construction (``path_optimizer.py`` assigns ``stability_score`` and ``max_hu``
the same value); and the density integral of the paths that were *rejected* --
which is what delta divides by -- is never computed at all, because the optimizer
``continue``s past a candidate before scoring it. So delta exists only if it is
rebuilt here.

That makes reproducing the extension's own arithmetic exactly the whole game, and
the evidence that it was reproduced is that the recomputed integral of a chosen
path equals the ``Stability score`` the run printed at the time: 5098 for
10250_L screw 1, 4855 for 10250_R screw 1, bit for bit. ``score_reproduced`` is
that comparison, per case, on every run that still has the log line.

Slicer-free and Qt-free -- unlike ``orbital.py``, which needs Slicer to mesh.
Everything here is arithmetic over point sets and one CT array, so
``scripts/check_rsa_analysis.py`` runs the ENTIRE analysis, delta included,
against the real saved runs outside Slicer. Given that the highest-consequence
failure mode below produces a *perfect-looking* delta rather than an error, that
check is not a convenience.
"""

from __future__ import annotations

import io
import logging
import os
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import geometry_io as gio
from .run_timing import (canonical_step_id, collect_timing,
                         discover_cases as _discover_cases, timing_sheet)
from .volume_io import read_nrrd, sample_nearest

logger = logging.getLogger(__name__)

EXTENSION_NAME = "ReverseShoulderArthroplasty"

#: Relative to the repository root, so the tree can be moved without editing code.
EXPERIMENT_DIR = os.path.join("Experiments", EXTENSION_NAME)
RUNS_SUBDIR = "Overall_Performance"
DATASET_SUBDIR = "Dataset"
WORKBOOK_NAME = "ReverseShoulderArthroplasty_summary.xlsx"

#: Node names, fixed by the extension's own ``visualize*`` methods. Addressed by
#: name rather than through ``geometry_io.scene_role_files``: this extension sets
#: no MRML role attributes at all, so there is nothing for that helper to key on.
SCREW_PATH_FILES = ("Path_Screw1.vtk", "Path_Screw2.vtk")
MIDDLE_PATH_FILE = "MiddleScrew_Path.vtk"
CONE_FILES = ("Cone_Region_Screw1.vtk", "Cone_Region_Screw2.vtk")
PLAN_TABLE_FILE = "RSA_PlanResults.tsv"

#: The surgeon's own two long screws, planned by hand on the same prosthesis, to
#: compare against. Their geometry is taken from the TABLE and not from the mesh:
#: ``Manual_Screw_Model_*.vtk`` is a screw cylinder that overhangs its entry point
#: by 3 mm, so its extreme vertex is not the entry, whereas the table's
#: Start*/End* columns are the trajectory itself and are already in RAS. The mesh
#: is read anyway, as a witness -- see ``manual_paths``.
MANUAL_PLAN_TABLE_FILE = "RSA_ManualPlanResults.tsv"
MANUAL_SCREW_FILES = ("Manual_Screw_Model_1.vtk", "Manual_Screw_Model_2.vtk")
MANUAL_TABLE_LABELS = ("Manual screw 1", "Manual screw 2")

#: The two plans are compared per baseplate hole, and they are paired by that
#: hole rather than by the digit in the file name. On every screw of every saved
#: case the two entry points are identical to 0.000000 mm -- the manual plan
#: reuses the pipeline's baseplate pose and only re-aims the screws -- so a gap
#: anywhere near this ceiling means the two plans are not on the same prosthesis
#: and their deltas are not comparable.
ENTRY_PAIR_TOLERANCE_MM = 0.5
#: How far the manual screw MESH's own axis may sit from the direction its table
#: row declares before the mesh stops corroborating the table.
MANUAL_MESH_TOLERANCE_DEG = 1.0

# ---------------------------------------------------------------------------
# The planner's own constants. Every one is a FALLBACK: each is measured from
# the saved scene where the scene can answer, because all three are spin boxes
# the surgeon can change (SlicerScrewPlanner3.py:493, :488) and a run made with
# a different value would otherwise be scored against a cone it never searched.
# ---------------------------------------------------------------------------

#: SlicerScrewPlanner3.py:110. Measured per case from the drawn tube instead.
SCREW_LENGTH_MM = 38.97
#: SlicerScrewPlanner3.py:2491, hard-coded there.
MIDDLE_LENGTH_MM = 14.72
#: SlicerScrewPlanner3.py:109 -- the HALF angle. The paper's alpha = 45 deg is
#: the FULL apex angle, and this extension ships half of the paper's cone.
#: Writing 45 here would double the search space and depress every delta.
#: Measured per case as atan(cone radius / cone height) from the saved cone.
CONE_HALF_ANGLE_DEG = 22.5

#: The CALL SITE's resolutions (SlicerScrewPlanner3.py:2345-2346), not
#: PathGenerator's ``(150, 30, 30)`` default and not the ``resolution=(72, 8, 40)``
#: passed one line later -- only element [2] of THAT tuple is ever read
#: (path_optimizer.py:689, :1086). Using 72x8 here would undercount the maximum.
CONE_NUM_ANGLE = 144
CONE_NUM_RADIUS = 16
#: Stations along the centreline: ``num_segments = resolution[2]``.
INTEGRATION_STATIONS = 40
#: Nominal ``threshold`` of ``generate_optimal_path``. It gates nothing that
#: reaches delta -- it only tallies ``safe_count``, which is reproduced here
#: purely because the run logged it and it is therefore a second cross-check.
SAFE_POINT_THRESHOLD = 127

#: The denominator is a maximum over a GRID, so a reader is entitled to ask
#: whether delta is an artefact of the grid. The sweep is repeated once at this
#: multiple in both directions and the difference reported.
DENOMINATOR_REFINE = 2

#: path_optimizer.py:560 returns this for a point outside the image, and
#: path_optimizer.py:1120 adds it to the sum unconditionally. It is neither
#: clamped nor skipped: normalized it is about -98, and it is SUBTRACTED.
OUT_OF_BOUNDS_HU = -2000.0
GRAYSCALE_LEVELS = 255.0

#: A drawn tube whose measured length differs from the extension's constant by
#: more than this means the prosthesis constants changed; the run is still scored
#: (on its own measured length) but the case is flagged.
LENGTH_TOLERANCE_MM = 0.05
#: ``RSA_PlanResults.tsv`` prints six significant figures, so agreement to a few
#: microns is the most the cross-check can demand.
TSV_TOLERANCE_MM = 5e-3
#: Of ``INTEGRATION_STATIONS``. A chosen path is inside the CT along its whole
#: length; anything less means the geometry and the volume are not in one frame,
#: and the integral must not be reported. See "the mirror" below.
MIN_SAMPLES_IN_BOUNDS = INTEGRATION_STATIONS - 1
#: How far the cone model's own axis may sit from the middle peg's direction.
#: They are the same vector by construction (``cone_normal = -planeNormal``,
#: SlicerScrewPlanner3.py:2312, and the peg is drawn along it, :2503), so the
#: only spread is the float32 the models are written in -- measured at 0.000 to
#: 0.054 deg over the saved cases. The ceiling is set well above that but two
#: orders of magnitude below the failure it exists to catch: fitting the axis
#: from the half-disc's centroid instead of the peg gives 7.7 deg.
AXIS_AGREEMENT_DEG = 0.25

#: Cookbook step -> phase of the paper's timing breakdown. A step in none of
#: these lands in an ``unassigned`` bucket and is named in the log: a regenerated
#: workflow that renumbers its steps would otherwise make the phases silently
#: shrink while still summing to something plausible.
#:
#: The two judgement calls, both one edit away:
#:  * cb_step_16..19 place and orient the baseplate. This version of the
#:    extension has no p2/p3/p4 -- ``onPositionBaseplate`` reads control point 0
#:    only, and SlicerScrewPlanner3.py:2218 says the hole-to-hole line "replaces
#:    the removed 4th direction point" -- so the baseplate pose IS the rest of
#:    the paper's reference frame, and it belongs with the picking phase.
#:  * t3 is cb_step_20 ALONE. That one step runs the entire cone search, twice
#:    (once per screw). Steps 21-23 hand-edit the result afterwards, so counting
#:    them as "automatic planning" would report the surgeon's dragging as
#:    algorithm time -- 8.3 s of it on 10250_L.
PHASE_STEPS = {
    "t0": ("cb_step_1",),
    "t1": ("cb_step_2", "cb_step_3", "cb_step_4", "cb_step_5", "cb_step_6",
           "cb_step_7", "cb_step_8", "cb_step_9", "cb_step_10", "cb_step_11"),
    "t2": ("cb_step_12", "cb_step_13", "cb_step_14", "cb_step_15",
           "cb_step_16", "cb_step_17", "cb_step_18", "cb_step_19"),
    "t3": ("cb_step_20",),
    "t_refine": ("cb_step_21", "cb_step_22", "cb_step_23"),
}
PHASE_ORDER = ("t0", "t1", "t2", "t3", "t_refine")


# ---------------------------------------------------------------------------
# Reading the plan geometry
# ---------------------------------------------------------------------------

def read_path_points(path: str) -> np.ndarray:
    """The points of one saved ``.vtk`` model, in RAS.

    ``geometry_io.read_vtk_points`` returns the file's OWN coordinates, and
    Slicer writes model files in LPS (``3D Slicer output. SPACE=LPS`` on line 2
    of every one of these). Its docstring says RAS; the code converts nothing.
    So the flip happens here, once, at the read -- nothing downstream ever sees
    LPS.

    This is the single most consequential line in the module, and it fails
    silently in a way that looks like success. ``lps_to_ras`` is ``diag(-1,-1,1)``,
    an orthogonal map, so every dot product -- and therefore all three angles --
    is EXACTLY invariant under it: theta1/2/3 come out right whether or not the
    flip happened. Only delta notices, and on a real case the mirrored path
    leaves the CT array entirely, every sample returns the out-of-bounds
    sentinel, and numerator and denominator are then the same large negative
    number: delta = 1.000, which reads as a flawless plan. Hence the three
    guards below (``tsv_max_gap_mm``, ``samples_in_bounds``, and the
    delta > 1 flag), none of which is redundant.
    """
    return gio.lps_to_ras(gio.read_vtk_points(path))


def tube_axis(points: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
    """``(entry, tip, radius)`` of a ``vtkTubeFilter`` surface.

    These are tube SURFACES, not polylines -- there is no ``LINES`` section to
    read. The point order is ring-major: every side around the start, then every
    side around the end, so each half's centroid is an axis point.

    Split in HALF, never at an assumed ring size: ``Path_Screw*`` has 16 points
    as 2x8 but ``MiddleScrew_Path`` has 24 as 2x**12**. Reading the peg as three
    rings of eight yields a 7.4 mm "length" instead of 14.72 and a direction that
    is wrong -- which would corrupt theta1, theta2 AND the cone axis (hence both
    denominators) at once, without raising.
    """
    points = np.asarray(points, dtype=np.float64)
    if points.shape[0] < 4 or points.shape[0] % 2:
        raise ValueError("a tube needs an even number of points, got %d"
                         % points.shape[0])
    half = points.shape[0] // 2
    entry = points[:half].mean(axis=0)
    tip = points[half:].mean(axis=0)
    # Positive proof that the halves ARE the two rings: every point of a ring is
    # one tube radius from its own centroid. A mis-split mixes the ends and the
    # spread explodes, so this catches a future change of tube resolution rather
    # than trusting the count.
    radii = np.concatenate([np.linalg.norm(points[:half] - entry, axis=1),
                            np.linalg.norm(points[half:] - tip, axis=1)])
    if radii.std() > 0.05 * max(radii.mean(), 1e-6):
        raise ValueError("point halves are not the two ends of a tube "
                         "(ring radii %.3f +/- %.3f mm)" % (radii.mean(), radii.std()))
    return entry, tip, float(radii.mean())


def path_axis(scene_dir: str, file_name: str) -> Dict[str, Any]:
    """``entry`` / ``tip`` / ``direction`` / ``length`` of one drawn path, in RAS."""
    points = read_path_points(os.path.join(scene_dir, file_name))
    entry, tip, radius = tube_axis(points)
    length = float(np.linalg.norm(tip - entry))
    if length <= 1e-6:
        raise ValueError("%s: degenerate path of zero length" % file_name)
    return {"entry": entry, "tip": tip, "direction": (tip - entry) / length,
            "length": length, "tube_radius": radius}


def read_plan_table(path: str) -> List[Dict[str, Any]]:
    """``RSA_PlanResults.tsv`` as rows, keyed by its ``Path`` column.

    Used ONLY to prove the coordinate frame and to carry the ``Status`` string
    through -- never as geometry. Its ``Start*``/``End*`` columns are already in
    RAS (the headers say so: ``StartR``, ``StartA``, ``StartS``), which is exactly
    what makes it an independent witness for the flip applied in
    ``read_path_points``.
    """
    rows: List[Dict[str, Any]] = []
    if not os.path.isfile(path):
        return rows
    lines = [line for line in io.open(path, encoding="utf-8-sig",
                                      errors="replace").read().splitlines() if line.strip()]
    if not lines:
        return rows
    header = lines[0].split("\t")
    for line in lines[1:]:
        cells = line.split("\t")
        row: Dict[str, Any] = {}
        for name, value in zip(header, cells):
            value = value.strip()
            try:
                row[name] = float(value)
            except ValueError:
                row[name] = value
        rows.append(row)
    return rows


def plan_table_endpoints(rows: List[Dict[str, Any]], label: str
                         ) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """``(start, end)`` in RAS for the row whose ``Path`` cell is ``label``."""
    for row in rows:
        if str(row.get("Path", "")).strip().lower() != label.lower():
            continue
        try:
            return (np.array([row["StartR"], row["StartA"], row["StartS"]], dtype=float),
                    np.array([row["EndR"], row["EndA"], row["EndS"]], dtype=float))
        except (KeyError, TypeError, ValueError):
            return None
    return None


def manual_paths(scene_dir: str, notes: List[str]) -> List[Optional[Dict[str, Any]]]:
    """The surgeon's two hand-planned screws, in RAS, one entry per hole.

    Geometry comes from ``RSA_ManualPlanResults.tsv``, not from the meshes: a
    ``Manual_Screw_Model_*.vtk`` is the screw CYLINDER, which overhangs its entry
    point by about 3 mm at the head and is 3.1 mm in radius, so neither its
    extreme vertex nor its cap centroid is the trajectory's start. The table's
    ``Start*``/``End*`` columns ARE the trajectory, and are written in RAS by the
    same writer that produced the pipeline's own table -- which this module has
    already proved agrees with the drawn geometry to under a micron.

    The mesh is still read, as an independent witness that the table describes
    the screw that was actually drawn: ``mesh_agreement_deg`` is the angle
    between the mesh's principal axis and the table's direction. It corroborates
    rather than corrects -- a disagreement is reported and the table is still
    used, because the table is the more precise of the two.
    """
    table = read_plan_table(os.path.join(scene_dir, MANUAL_PLAN_TABLE_FILE))
    paths: List[Optional[Dict[str, Any]]] = []
    for index, label in enumerate(MANUAL_TABLE_LABELS):
        pair = plan_table_endpoints(table, label)
        if pair is None:
            paths.append(None)
            continue
        entry, tip = pair
        length = float(np.linalg.norm(tip - entry))
        if length <= 1e-6:
            notes.append("%s in %s has zero length" % (label, MANUAL_PLAN_TABLE_FILE))
            paths.append(None)
            continue
        path: Dict[str, Any] = {
            "entry": entry, "tip": tip, "direction": (tip - entry) / length,
            "length": length,
            "status": next((str(row.get("Status", "")) for row in table
                            if str(row.get("Path", "")).strip().lower() == label.lower()),
                           ""),
        }
        mesh_file = os.path.join(scene_dir, MANUAL_SCREW_FILES[index])
        if os.path.isfile(mesh_file):
            try:
                points = read_path_points(mesh_file)
                low, high = gio.rod_axis_endpoints(points)
                mesh_direction = high - low
                mesh_direction = mesh_direction / np.linalg.norm(mesh_direction)
                # The mesh axis has no inherent sense, so take the acute angle:
                # it is the LINE that has to agree, not an arrow.
                agreement = _angle_deg(mesh_direction, path["direction"])
                path["mesh_agreement_deg"] = round(min(agreement, 180.0 - agreement), 3)
                if path["mesh_agreement_deg"] > MANUAL_MESH_TOLERANCE_DEG:
                    notes.append("%s: the drawn mesh points %.2f deg away from the "
                                 "trajectory its table row declares -- the table "
                                 "was used, but the two disagree"
                                 % (label, path["mesh_agreement_deg"]))
            except Exception as exc:
                notes.append("%s: could not read %s as a witness (%s)"
                             % (label, MANUAL_SCREW_FILES[index], exc))
        paths.append(path)
    return paths


# ---------------------------------------------------------------------------
# The CT
# ---------------------------------------------------------------------------

def ct_volume_path(case: Dict[str, str]) -> str:
    """The CT the run was driven from, inside the saved scene folder.

    Resolved from the volume the surgeon actually chose at step 1, because
    ``SlicerScrewPlanner3.getBoneVolume()`` falls through a name heuristic to
    "the first volume with image data" -- so with two volumes in a scene the file
    name alone cannot say which one was scored. When the recorded choice is
    missing we fall back to the subject name and then to elimination, and raise
    rather than guess if more than one candidate survives.
    """
    scene_dir = case["scene_dir"]
    for name in (_recorded_choice(case, "ct_volume"), case.get("subject")):
        if name:
            candidate = os.path.join(scene_dir, "%s.nrrd" % name)
            if os.path.isfile(candidate):
                return candidate
    volumes = sorted(name for name in os.listdir(scene_dir)
                     if name.endswith(".nrrd") and not name.endswith(".seg.nrrd"))
    if len(volumes) == 1:
        return os.path.join(scene_dir, volumes[0])
    if not volumes:
        raise ValueError("no CT volume in %s" % scene_dir)
    raise ValueError("cannot tell which of %d volumes in %s the run used: %s"
                     % (len(volumes), scene_dir, ", ".join(volumes)))


def _recorded_choice(case: Dict[str, str], parameter_name: str) -> Optional[Any]:
    """The value the surgeon gave for one named parameter, from the step logs."""
    import json                                                # noqa: PLC0415

    runtime = os.path.join(case["run_dir"], "runtime")
    if not os.path.isdir(runtime):
        return None
    for name in sorted(os.listdir(runtime)):
        step_file = os.path.join(runtime, name, "step.json")
        if not os.path.isfile(step_file):
            continue
        try:
            step = json.load(io.open(step_file, encoding="utf-8"))
        except Exception:
            logger.debug("Unreadable %s", step_file, exc_info=True)
            continue
        if step.get("parameter_name") == parameter_name:
            return step.get("choice_value")
    return None


# ---------------------------------------------------------------------------
# The bone-density path integral
# ---------------------------------------------------------------------------

def path_integrals(apex: np.ndarray, directions: np.ndarray, length: float,
                   array: np.ndarray, ras_to_ijk: np.ndarray,
                   scalar_min: float, scalar_max: float,
                   stations: int = INTEGRATION_STATIONS
                   ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """``(integral, safe_points, samples_in_bounds)``, one per direction.

    An exact reproduction of ``PathOptimizer._check_path_with_volume``
    (path_optimizer.py:1086-1125). Four details of it decide the number and none
    of them announces itself if it is wrong:

    * ``j`` runs 1..stations, so the first sample sits at ``length/40`` and the
      last EXACTLY at the tip. The cone candidate itself lies further out, at
      ``length/cos(theta)``; the march deliberately stops short of it.
    * The value is nearest-neighbour, never interpolated (``volume_io``).
    * Normalisation is ``round((hu - min) * 255 / (max - min))`` over the WHOLE
      volume's scalar range. That has a non-zero offset, so it is not
      ratio-invariant: taking the range from a cropped array, or summing raw HU,
      rescales every delta in the workbook without changing anything visible.
    * It is a SUM over the stations, not a mean.

    Density comes from the CT and only the CT. The bone segmentation and the
    solid-bone field gate containment, which is precisely the constraint delta
    exists to measure the cost of, and so must not enter either side of it.
    """
    directions = np.asarray(directions, dtype=np.float64).reshape(-1, 3)
    steps = length * np.arange(1, stations + 1, dtype=np.float64) / stations
    points = (np.asarray(apex, dtype=np.float64)[None, None, :]
              + directions[:, None, :] * steps[None, :, None])

    values, inside = sample_nearest(array, ras_to_ijk, points.reshape(-1, 3),
                                    OUT_OF_BOUNDS_HU)
    span = float(scalar_max) - float(scalar_min)
    if span <= 0:
        span = 1.0
    normalised = np.rint((values - float(scalar_min)) * GRAYSCALE_LEVELS / span)
    normalised = normalised.reshape(directions.shape[0], stations)

    return (normalised.sum(axis=1).astype(np.int64),
            (normalised >= SAFE_POINT_THRESHOLD).sum(axis=1).astype(np.int64),
            inside.reshape(directions.shape[0], stations).sum(axis=1).astype(np.int64))


def _unit_directions(apex: np.ndarray, targets: np.ndarray) -> np.ndarray:
    vectors = np.asarray(targets, dtype=np.float64).reshape(-1, 3) - np.asarray(apex, float)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    keep = norms[:, 0] > 1e-9
    return vectors[keep] / norms[keep]


def searched_cone_directions(cone_points: np.ndarray, apex: np.ndarray) -> np.ndarray:
    """The candidate set the planner actually enumerated, read from its own model.

    ``Cone_Region_Screw{i}`` is saved with the apex at index 0 and every
    candidate after it, which IS the optimizer's loop (``for i in range(1,
    num_points)``, path_optimizer.py:710). Delaunay meshing permutes the order,
    but a maximum over a set does not care.
    """
    return _unit_directions(apex, np.asarray(cone_points)[1:])


def full_cone_directions(apex: np.ndarray, axis: np.ndarray, length: float,
                         half_angle_deg: float, num_angle: int, num_radius: int
                         ) -> np.ndarray:
    """Every direction in the WHOLE cone, rebuilt in the generator's own basis.

    The planner searches only half of it: ``path_generator.py:135-141`` drops
    every azimuth whose radial vector points toward the other screw's hole, so
    the two screws cannot converge. That halving is an anti-crossing rule, not
    the exposure constraint delta ablates, which is why the paper's "entire
    conical space" is this set and the planner's half-cone is reported beside it
    rather than instead of it.

    The basis (``ref``, ``cross``, and stepping by Rodrigues) is copied from
    ``PathGenerator.generate_cone_points`` so the rebuilt grid lands on the same
    azimuths the planner used, making the half-cone a strict subset.
    """
    axis = np.asarray(axis, dtype=np.float64)
    axis = axis / np.linalg.norm(axis)
    base = np.asarray(apex, dtype=np.float64) + axis * length
    radius = length * np.tan(np.radians(half_angle_deg))

    reference = np.array([0.0, 0.0, 1.0]) if abs(axis[2]) < 0.9 else np.array([0.0, 1.0, 0.0])
    spoke = np.cross(axis, reference)
    spoke = spoke / np.linalg.norm(spoke)

    targets = [base]                                   # the centre path
    rates = np.arange(1, num_radius + 1, dtype=np.float64) / num_radius
    step = 2.0 * np.pi / num_angle
    for _index in range(num_angle):
        targets.append(base + spoke[None, :] * (radius * rates)[:, None])
        cosine, sine = np.cos(step), np.sin(step)
        spoke = (spoke * cosine + np.cross(axis, spoke) * sine
                 + axis * float(np.dot(axis, spoke)) * (1.0 - cosine))
    return _unit_directions(apex, np.vstack([np.atleast_2d(t) for t in targets]))


# ---------------------------------------------------------------------------
# What the run itself logged
# ---------------------------------------------------------------------------

_SCREW_HEADER = re.compile(r"---\s*Planning Screw\s*(\d+)\s*---")
_STABILITY = re.compile(r"Stability score \(total normalized HU\):\s*(-?\d+)")
_SAFE_POINTS = re.compile(r"Number of safe points along path:\s*(\d+)")


def logged_scores(run_dir: str) -> Dict[int, Dict[str, int]]:
    """``{screw index: {"score":, "safe_points":}}`` from the planning step's stdout.

    A cross-check only, never a source: ``output.txt`` is truncated around 10 KB
    and on both reference runs that cuts off partway through screw 2, so the
    second screw usually has no logged score at all. A missing entry is normal
    and is reported as such rather than as a mismatch.
    """
    found: Dict[int, Dict[str, int]] = {}
    runtime = os.path.join(run_dir, "runtime")
    if not os.path.isdir(runtime):
        return found
    for name in sorted(os.listdir(runtime)):
        output = os.path.join(runtime, name, "output.txt")
        if not os.path.isfile(output):
            continue
        text = io.open(output, encoding="utf-8", errors="replace").read()
        if "Planning Screw" not in text:
            continue
        current = None
        for line in text.splitlines():
            header = _SCREW_HEADER.search(line)
            if header:
                current = int(header.group(1))
                continue
            if current is None:
                continue
            score = _STABILITY.search(line)
            if score:
                found.setdefault(current, {})["score"] = int(score.group(1))
            safe = _SAFE_POINTS.search(line)
            if safe:
                found.setdefault(current, {})["safe_points"] = int(safe.group(1))
    return found


# ---------------------------------------------------------------------------
# One case
# ---------------------------------------------------------------------------

def _angle_deg(a: np.ndarray, b: np.ndarray) -> float:
    """Angle between two unit vectors, in degrees.

    The clip is load-bearing rather than decorative: a dot product of
    1.0000000000000002 makes ``arccos`` return NaN, which then propagates
    through every mean in the summary as a blank cell nobody can explain.
    """
    return float(np.degrees(np.arccos(np.clip(float(np.dot(a, b)), -1.0, 1.0))))


def _apply_cone_bound(angle_row: Dict[str, Any], half_angle_deg: float) -> None:
    """Answer the paper's acceptance test: is each screw inside the cone?

    theta1 and theta2 are measured from the cone axis, so the half-angle is
    their hard bound -- a value sitting exactly on it is a rim candidate, which
    is a result and not an error.
    """
    angle_row["cone_half_angle_deg"] = round(float(half_angle_deg), 3)
    for key, theta in (("theta1_within_cone", angle_row.get("theta1_deg")),
                       ("theta2_within_cone", angle_row.get("theta2_deg"))):
        if theta is not None:
            angle_row[key] = theta <= angle_row["cone_half_angle_deg"] + 1e-3


#: The two plans compared at every hole. "pipeline" is the cone search this
#: system drove; "manual" is the surgeon's own hand plan on the same prosthesis.
PLANS = ("pipeline", "manual")


def analyse_case(case: Dict[str, str]) -> Dict[str, Any]:
    """``{"angle_rows", "metric_rows", "comparison_rows", "notes"}`` for one run."""
    scene_dir = case["scene_dir"]
    label = case["subject"] or case["run"]
    notes: List[str] = []

    peg = path_axis(scene_dir, MIDDLE_PATH_FILE)
    screws: List[Optional[Dict[str, Any]]] = []
    for file_name in SCREW_PATH_FILES:
        try:
            screws.append(path_axis(scene_dir, file_name))
        except Exception as exc:
            notes.append("%s: %s" % (file_name, exc))
            screws.append(None)
    manual = manual_paths(scene_dir, notes)

    for name, measured, expected in (("peg", peg["length"], MIDDLE_LENGTH_MM),
                                     ("screw 1", screws[0] and screws[0]["length"],
                                      SCREW_LENGTH_MM),
                                     ("screw 2", screws[1] and screws[1]["length"],
                                      SCREW_LENGTH_MM),
                                     ("manual screw 1", manual[0] and manual[0]["length"],
                                      SCREW_LENGTH_MM),
                                     ("manual screw 2", manual[1] and manual[1]["length"],
                                      SCREW_LENGTH_MM)):
        if measured is not None and abs(measured - expected) > LENGTH_TOLERANCE_MM:
            notes.append("%s is %.3f mm, not the expected %.2f mm -- the "
                         "prosthesis constants differ from the analysed ones; "
                         "scored on the measured length"
                         % (name, measured, expected))

    # Paired by ENTRY POINT, never by the digit in the file name. Both plans use
    # the same baseplate, so the pairing is exact where it holds at all -- and
    # where it does not, the two screws are not in the same hole and comparing
    # their deltas would be comparing two different pieces of bone.
    for index in range(len(manual)):
        if manual[index] is None or screws[index] is None:
            continue
        gap = float(np.linalg.norm(manual[index]["entry"] - screws[index]["entry"]))
        manual[index]["entry_gap_mm"] = round(gap, 6)
        if gap > ENTRY_PAIR_TOLERANCE_MM:
            notes.append("manual screw %d enters %.2f mm from the planned screw %d "
                         "-- the two plans are not on the same baseplate hole, so "
                         "they are not compared" % (index + 1, gap, index + 1))
            manual[index] = None

    # The cone axis is the middle peg's direction. Not fitted from the cone
    # model: its base is a 180-degree HALF disc, so the axis foot lies on the
    # boundary and the point centroid is 5.5 mm off it -- fitting the axis as
    # "apex towards the mean of the base" gives a 7.7 degree error and a
    # half-angle of 23.5 instead of 22.5. The peg is exact; the cone is used
    # below only to CHECK it.
    axis = peg["direction"]

    # One angle row per PLAN, so the paper's Table 1 can be read for the
    # algorithm and for the surgeon side by side. The peg columns repeat on both
    # rows because the peg is shared: both plans are measured against the same
    # prosthesis axis, which is the only reason their angles are comparable.
    by_plan = {"pipeline": screws, "manual": manual}
    angle_rows: List[Dict[str, Any]] = []
    for plan in PLANS:
        pair = by_plan[plan]
        row: Dict[str, Any] = {
            "case": label, "plan": plan, "run": case["run"],
            "peg_len_mm": round(peg["length"], 3),
            "screw1_len_mm": round(pair[0]["length"], 3) if pair[0] else None,
            "screw2_len_mm": round(pair[1]["length"], 3) if pair[1] else None,
            "error": "",
        }
        if pair[0]:
            row["theta1_deg"] = round(_angle_deg(pair[0]["direction"], axis), 3)
            if pair[0].get("mesh_agreement_deg") is not None:
                row["mesh_agreement_deg"] = pair[0]["mesh_agreement_deg"]
        if pair[1]:
            row["theta2_deg"] = round(_angle_deg(pair[1]["direction"], axis), 3)
            if pair[1].get("mesh_agreement_deg") is not None:
                row["mesh_agreement_deg"] = max(
                    row.get("mesh_agreement_deg") or 0.0, pair[1]["mesh_agreement_deg"])
        if pair[0] and pair[1]:
            row["theta3_deg"] = round(
                _angle_deg(pair[0]["direction"], pair[1]["direction"]), 3)
        angle_rows.append(row)
    angle_row = angle_rows[0]                      # the pipeline row

    # --- frame proof 1: the plan table, which is written in RAS ---------------
    plan_rows = read_plan_table(os.path.join(scene_dir, PLAN_TABLE_FILE))
    gaps: List[float] = []
    status_by_screw: Dict[int, str] = {}
    for index, (screw, table_label) in enumerate(
            zip(screws, ("Screw 1", "Screw 2"))):
        for row in plan_rows:
            if str(row.get("Path", "")).strip().lower() == table_label.lower():
                status_by_screw[index] = str(row.get("Status", ""))
        if screw is None:
            continue
        pair = plan_table_endpoints(plan_rows, table_label)
        if pair is None:
            continue
        gaps.append(float(np.abs(pair[0] - screw["entry"]).max()))
        gaps.append(float(np.abs(pair[1] - screw["tip"]).max()))
    peg_pair = plan_table_endpoints(plan_rows, "Middle screw")
    if peg_pair is not None:
        gaps.append(float(np.abs(peg_pair[0] - peg["entry"]).max()))
        gaps.append(float(np.abs(peg_pair[1] - peg["tip"]).max()))

    # A property of the case, not of one plan, so it goes on both rows -- and it
    # underwrites the manual plan too, whose geometry comes from a sibling table
    # written by the same writer in the same frame.
    for row in angle_rows:
        if gaps:
            row["tsv_max_gap_mm"] = round(max(gaps), 6)
            row["frame_proof"] = ("plan table (RAS)" if max(gaps) <= TSV_TOLERANCE_MM
                                  else "PLAN TABLE DISAGREES")
        else:
            row["frame_proof"] = "in-bounds only"
    if gaps and max(gaps) > TSV_TOLERANCE_MM:
        notes.append("the drawn paths and %s disagree by up to %.3f mm -- the "
                     "geometry may be in the wrong coordinate frame"
                     % (PLAN_TABLE_FILE, max(gaps)))

    # --- the CT ---------------------------------------------------------------
    # Guarded separately from the work below, because everything above this line
    # -- the three angles, the lengths, the plan-table frame proof -- is geometry
    # only and is already computed. Losing the CT costs delta; it must not also
    # cost this case its row in the paper's angle table. (The `try` below is a
    # memory block, not error handling: its `finally` frees 140 MB of CT.)
    metric_rows: List[Dict[str, Any]] = []
    comparison_rows: List[Dict[str, Any]] = []
    try:
        array, ijk_to_ras, _header = read_nrrd(ct_volume_path(case))
    except Exception as exc:
        for row in angle_rows:
            row["error"] = str(exc)
        notes.append("no CT could be read, so no density was scored: %s" % exc)
        # The paper's acceptance test is geometry and needs no CT, so it is
        # still answered -- against the shipped half-angle, since the per-case
        # one is recovered alongside the density scoring that just failed.
        for row in angle_rows:
            _apply_cone_bound(row, CONE_HALF_ANGLE_DEG)
        return {"angle_rows": angle_rows, "metric_rows": metric_rows,
                "comparison_rows": comparison_rows, "notes": notes}

    try:
        ras_to_ijk = np.linalg.inv(ijk_to_ras)
        scalar_min, scalar_max = float(array.min()), float(array.max())

        peg_integral, _safe, peg_inside = path_integrals(
            peg["entry"], peg["direction"][None, :], peg["length"],
            array, ras_to_ijk, scalar_min, scalar_max)
        for row in angle_rows:
            row["peg_integral"] = int(peg_integral[0])
        if int(peg_inside[0]) < MIN_SAMPLES_IN_BOUNDS:
            for row in angle_rows:
                row["peg_integral"] = None
            notes.append("the middle peg leaves the CT array -- the geometry and "
                         "the volume are not in the same frame")

        logged = logged_scores(case["run_dir"])
        hand_adjusted = bool(_recorded_choice(case, "adjust_screw"))
        for row in angle_rows:
            row["hand_adjusted"] = hand_adjusted

        agreements: List[float] = []
        half_angles: List[float] = []
        for index in range(len(SCREW_PATH_FILES)):
            status = status_by_screw.get(index, "")
            # "BEST EFFORT - leaves the bone, ..." is how the planner records
            # that nothing in the cone was fully contained, so it returned the
            # DEEPEST-reaching candidate, tie-broken by protrusion and only then
            # by density. That row's delta answers a different question and the
            # summary must be able to count them separately.
            selection = ("best effort" if status.upper().startswith("BEST EFFORT")
                         else ("planned" if status else ""))

            anchor = screws[index] or manual[index]
            if anchor is None:
                for plan in PLANS:
                    metric_rows.append({
                        "case": label, "run": case["run"], "screw": index + 1,
                        "plan": plan,
                        "error": "no trajectory for this screw in the saved scene"})
                continue

            # ONE cone per hole, shared by both plans -- see _cone_denominators.
            cone = _cone_denominators(index, anchor["entry"], axis, anchor["length"],
                                      scene_dir, array, ras_to_ijk,
                                      scalar_min, scalar_max, notes)
            if cone.get("axis_agreement_deg") is not None:
                agreements.append(cone["axis_agreement_deg"])
            if cone.get("cone_half_angle_deg") is not None:
                half_angles.append(cone["cone_half_angle_deg"])

            scored: Dict[str, Dict[str, Any]] = {}
            for plan in PLANS:
                row = _score_trajectory(index, plan, by_plan[plan][index], cone,
                                        array, ras_to_ijk, scalar_min, scalar_max,
                                        notes)
                row["case"], row["run"] = label, case["run"]
                if plan == "pipeline":
                    row["status"], row["selection"] = status, selection
                    row["hand_adjusted"] = hand_adjusted
                    _attach_logged(row, logged.get(index + 1) or {}, index, notes)
                else:
                    source = by_plan[plan][index] or {}
                    row["status"] = source.get("status", "")
                    row["selection"] = "manual"
                    if source.get("entry_gap_mm") is not None:
                        row["entry_gap_mm"] = source["entry_gap_mm"]
                    if source.get("mesh_agreement_deg") is not None:
                        row["mesh_agreement_deg"] = source["mesh_agreement_deg"]
                metric_rows.append(row)
                scored[plan] = row

            comparison = _compare_plans(index, label, case["run"], scored,
                                        by_plan, axis)
            if comparison is not None:
                comparison_rows.append(comparison)

        # --- the cone's own axis, as an independent check on the peg's --------
        if agreements:
            for row in angle_rows:
                row["cone_axis_agreement_deg"] = round(max(agreements), 4)
            if max(agreements) > AXIS_AGREEMENT_DEG:
                notes.append("the saved cone's axis and the middle peg differ by "
                             "%.3f deg -- the cone may not be the one that was "
                             "searched" % max(agreements))
        for row in angle_rows:
            _apply_cone_bound(row,
                              max(half_angles) if half_angles else CONE_HALF_ANGLE_DEG)
    finally:
        # 140 MB per CT at int16 and one per case; a 60-case sweep would
        # otherwise hold every one of them until the report is written.
        del array

    return {"angle_rows": angle_rows, "metric_rows": metric_rows,
            "comparison_rows": comparison_rows, "notes": notes}


def _attach_logged(row: Dict[str, Any], logged: Dict[str, int], index: int,
                   notes: List[str]) -> None:
    """Compare the recomputed figures against what the run printed at the time."""
    if "score" in logged:
        row["score_logged"] = logged["score"]
        row["score_reproduced"] = logged["score"] == row.get("integral_chosen")
        if not row["score_reproduced"]:
            notes.append("screw %d: the recomputed integral %s does not match the "
                         "%d this run logged -- the sampler no longer reproduces "
                         "the planner" % (index + 1, row.get("integral_chosen"),
                                          logged["score"]))
    if "safe_points" in logged:
        # The second witness, and it is not redundant: the integral is a sum, so
        # two different sample sets can reach it by cancellation, whereas the
        # threshold tally is a count over the same samples. Agreeing on both is
        # much stronger evidence that the sampler sits on the same voxels.
        row["safe_points_logged"] = logged["safe_points"]
        row["safe_points_reproduced"] = logged["safe_points"] == row.get("safe_points")
        if not row["safe_points_reproduced"]:
            notes.append("screw %d: %s centreline samples reach the threshold, but "
                         "this run logged %d -- the sampler is not on the same "
                         "voxels" % (index + 1, row.get("safe_points"),
                                     logged["safe_points"]))


def _compare_plans(index: int, label: str, run: str,
                   scored: Dict[str, Dict[str, Any]],
                   by_plan: Dict[str, List[Optional[Dict[str, Any]]]],
                   axis: np.ndarray) -> Optional[Dict[str, Any]]:
    """One row pairing the two plans at one baseplate hole.

    Both trajectories were scored against the SAME cone, so their deltas are on
    one scale and the difference between them is the whole point of the table:
    it is how much of the density available at this hole the search captured that
    the hand plan did not, in the units the paper already defines.
    """
    pipeline, manual = scored.get("pipeline") or {}, scored.get("manual") or {}
    if pipeline.get("delta") is None or manual.get("delta") is None:
        return None
    row: Dict[str, Any] = {
        "case": label, "run": run, "screw": index + 1,
        "selection": pipeline.get("selection", ""),
        "integral_pipeline": pipeline.get("integral_chosen"),
        "integral_manual": manual.get("integral_chosen"),
        "integral_max_cone": pipeline.get("integral_max_cone"),
        "delta_pipeline": pipeline.get("delta"),
        "delta_manual": manual.get("delta"),
        "delta_gain": round(pipeline["delta"] - manual["delta"], 4),
        "pipeline_denser": pipeline["delta"] > manual["delta"],
        "entry_gap_mm": manual.get("entry_gap_mm"),
    }
    if manual.get("integral_chosen"):
        row["integral_ratio"] = round(
            float(pipeline["integral_chosen"]) / float(manual["integral_chosen"]), 4)
    a, b = by_plan["pipeline"][index], by_plan["manual"][index]
    if a and b:
        # Each plan's angulation from the prosthesis axis -- theta1 for screw 1
        # and theta2 for screw 2, restated here so one row carries the whole
        # comparison at this hole.
        row["theta_pipeline_deg"] = round(_angle_deg(a["direction"], axis), 3)
        row["theta_manual_deg"] = round(_angle_deg(b["direction"], axis), 3)
        # How far apart the two plans aim. It carries no quality judgement on its
        # own -- two trajectories can differ by 15 degrees and score alike -- but
        # a large angle beside a small delta_gain is the interesting case: the
        # surgeon chose a very different corridor of equally good bone.
        row["plans_apart_deg"] = round(_angle_deg(a["direction"], b["direction"]), 3)
        row["tip_gap_mm"] = round(float(np.linalg.norm(a["tip"] - b["tip"])), 3)
    return row


def _cone_denominators(index: int, apex: np.ndarray, axis: np.ndarray, length: float,
                       scene_dir: str, array: np.ndarray, ras_to_ijk: np.ndarray,
                       scalar_min: float, scalar_max: float, notes: List[str]
                       ) -> Dict[str, Any]:
    """The cone at one baseplate hole, and the best density integral inside it.

    Computed ONCE per hole and shared by both plans, which is not just an
    optimisation -- it is what makes the comparison mean anything. The surgeon's
    hand plan reuses the pipeline's baseplate pose, so both trajectories leave
    the SAME point along the SAME cone axis (measured at 0.000000 mm apart on
    every screw of every saved case). Dividing them by one denominator therefore
    asks a single well-posed question: of the density available at this hole, how
    much did each plan capture?
    """
    cone: Dict[str, Any] = {"searched": None, "axis_agreement_deg": None}

    # --- denominator A: the half-cone the planner enumerated ------------------
    cone_path = os.path.join(scene_dir, CONE_FILES[index])
    if os.path.isfile(cone_path):
        cone_points = read_path_points(cone_path)
        cone_apex = cone_points[0]
        if float(np.linalg.norm(cone_apex - apex)) > 1e-3:
            notes.append("screw %d: %s starts %.3f mm from the screw's own entry "
                         "point -- the cone was not paired with this screw"
                         % (index + 1, CONE_FILES[index],
                            float(np.linalg.norm(cone_apex - apex))))
        else:
            rest = cone_points[1:]
            # Recovered rather than assumed: the half-angle is a spin box, so a
            # run made at a different setting must be scored against the cone it
            # actually had. Height and radius both come straight out of the
            # saved model, and the axis used is the peg's (see analyse_case).
            height = float(np.dot(rest.mean(axis=0) - cone_apex, axis))
            radius = float(np.linalg.norm(rest - (cone_apex + axis * height),
                                          axis=1).max())
            cone["cone_height_mm"] = round(height, 3)
            cone["cone_radius_mm"] = round(radius, 3)
            cone["cone_half_angle_deg"] = round(
                float(np.degrees(np.arctan2(radius, height))), 3)
            # The base disc is planar, so its own normal is an independent
            # reading of the axis the planner used.
            centred = rest - rest.mean(axis=0)
            normal = np.linalg.svd(centred, full_matrices=False)[2][2]
            if float(np.dot(normal, axis)) < 0:
                normal = -normal
            cone["axis_agreement_deg"] = _angle_deg(normal, axis)

            searched = searched_cone_directions(cone_points, apex)
            totals, _s, _i = path_integrals(apex, searched, length, array,
                                            ras_to_ijk, scalar_min, scalar_max)
            cone["searched"] = searched
            cone["candidates_searched"] = int(searched.shape[0])
            cone["integral_max_searched"] = int(totals.max())
    else:
        notes.append("screw %d: no %s, so the planner's own search space could "
                     "not be scored" % (index + 1, CONE_FILES[index]))

    # --- denominator B: the entire cone, which is what the paper divides by ---
    half_angle = cone.get("cone_half_angle_deg") or CONE_HALF_ANGLE_DEG
    for suffix, refine in (("", 1), ("_2x", DENOMINATOR_REFINE)):
        directions = full_cone_directions(apex, axis, length, half_angle,
                                          CONE_NUM_ANGLE * refine,
                                          CONE_NUM_RADIUS * refine)
        totals, _s, _i = path_integrals(apex, directions, length, array,
                                        ras_to_ijk, scalar_min, scalar_max)
        cone["integral_max_cone" + suffix] = int(totals.max())
        if not suffix:
            cone["candidates_cone"] = int(directions.shape[0])

    coarse, fine = cone.get("integral_max_cone"), cone.get("integral_max_cone_2x")
    if coarse and fine:
        # The denominator is a maximum over a grid. This column is what tells a
        # reader delta is a property of the anatomy and not of the sampling.
        cone["denominator_sensitivity_pct"] = round(100.0 * (fine - coarse) / coarse, 3)
    return cone


#: Keys of the cone that are copied onto every trajectory row scored against it.
_CONE_ROW_KEYS = ("integral_max_searched", "integral_max_cone", "integral_max_cone_2x",
                  "candidates_searched", "candidates_cone",
                  "denominator_sensitivity_pct",
                  "cone_half_angle_deg", "cone_height_mm", "cone_radius_mm")


def _score_trajectory(index: int, plan: str, screw: Optional[Dict[str, Any]],
                      cone: Dict[str, Any], array: np.ndarray,
                      ras_to_ijk: np.ndarray, scalar_min: float, scalar_max: float,
                      notes: List[str]) -> Dict[str, Any]:
    """One trajectory's density row: its integral, and its delta in ``cone``."""
    row: Dict[str, Any] = {"screw": index + 1, "plan": plan, "error": ""}
    if screw is None:
        row["error"] = "no %s trajectory in the saved scene" % plan
        return row

    apex, direction, length = screw["entry"], screw["direction"], screw["length"]
    row.update({
        "entry_r": round(float(apex[0]), 3), "entry_a": round(float(apex[1]), 3),
        "entry_s": round(float(apex[2]), 3),
        "dir_r": round(float(direction[0]), 4), "dir_a": round(float(direction[1]), 4),
        "dir_s": round(float(direction[2]), 4),
        "length_mm": round(length, 3),
    })

    chosen, safe, inside = path_integrals(apex, direction[None, :], length,
                                          array, ras_to_ijk, scalar_min, scalar_max)
    row["integral_chosen"] = int(chosen[0])
    row["safe_points"] = int(safe[0])
    row["samples_in_bounds"] = int(inside[0])

    if int(inside[0]) < MIN_SAMPLES_IN_BOUNDS:
        # Refuse to divide. A path that leaves the array scores the sentinel at
        # every station, and the SAME sentinel dominates the denominator, so the
        # ratio comes out at ~1.000 -- a perfect score for a plan that is not
        # even in the patient.
        row["error"] = ("only %d of %d samples are inside the CT -- the path and "
                        "the volume are not in one frame; no ratio computed"
                        % (int(inside[0]), INTEGRATION_STATIONS))
        notes.append("screw %d (%s): %s" % (index + 1, plan, row["error"]))
        return row

    for key in _CONE_ROW_KEYS:
        if cone.get(key) is not None:
            row[key] = cone[key]
    for column, source in (("delta", "integral_max_cone"),
                           ("delta_2x", "integral_max_cone_2x"),
                           ("delta_searched", "integral_max_searched")):
        best = cone.get(source)
        if best:
            row[column] = round(float(chosen[0]) / float(best), 4)

    searched = cone.get("searched")
    if searched is not None:
        # Zero means this trajectory IS one the planner enumerated. For the
        # pipeline row that identifies it as the search's argmax; for the manual
        # row it is merely informative -- a surgeon aiming by hand has no reason
        # to land on the grid, and does not on any saved case.
        row["on_search_grid_deg"] = round(
            _angle_deg(direction, searched[int(np.argmax(searched @ direction))]), 3)

    if row.get("delta") is not None and row["delta"] > 1.0:
        notes.append("screw %d (%s): delta is %.3f, above 1 -- the trajectory beats "
                     "every candidate in its own cone, which is only reachable by "
                     "hand-adjustment or a wrong denominator"
                     % (index + 1, plan, row["delta"]))
    return row


# ---------------------------------------------------------------------------
# Timing, split into the paper's phases
# ---------------------------------------------------------------------------

_PHASE_OF_STEP = {canonical_step_id(step): phase
                  for phase, steps in PHASE_STEPS.items() for step in steps}


def phase_row(case: Dict[str, str], timing: Dict[str, Any],
              steps: List[Dict[str, Any]], log: List[str]) -> Dict[str, Any]:
    """One run's time, split into t0 / t1 / t2 / t3 / t_refine."""
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
    for phase in ("t1", "t2", "t3"):
        row["%s_exec_s" % phase] = round(totals[phase]["exec"], 3)
        row["%s_wait_s" % phase] = round(totals[phase]["wait"], 3)
    row["t3_visits"] = totals["t3"]["visits"]

    phase_sum = sum(totals[phase]["wall"] for phase in PHASE_ORDER) \
        + totals["unassigned"]["wall"]
    row["phase_sum_s"] = round(phase_sum, 3)
    for name in ("total_s", "inside_steps_s", "startup_s", "between_steps_s",
                 "replay_review_s", "tail_wait_exit_s"):
        # .get, not [ ]: replay_review_s is absent from the report of a run
        # that was never stepped back, which is the normal case.
        if isinstance(timing.get(name), float):
            row[name if name != "total_s" else "t_total_s"] = timing[name]
    if isinstance(timing.get("inside_steps_s"), float):
        # Not clamped. A non-zero residual is the only evidence a reader has
        # that the phases and the run clock disagree; here it is the report's
        # own two-decimal rounding accumulated over ~20 rows.
        row["phase_residual_s"] = round(timing["inside_steps_s"] - phase_sum, 3)

    row["steps_seen"] = len(seen)
    row["steps_unassigned"] = ", ".join(unassigned)
    if unassigned:
        log.append("   [!] %s: %d step(s) in no timing phase (%s) -- PHASE_STEPS "
                   "is out of date with the workflow, and t1/t2/t3 are short by "
                   "their time" % (label, len(unassigned), ", ".join(unassigned)))
    return row


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------

ANGLE_COLUMNS = ["case", "plan", "theta1_deg", "theta2_deg", "theta3_deg",
                 "cone_half_angle_deg", "theta1_within_cone", "theta2_within_cone",
                 "screw1_len_mm", "screw2_len_mm", "peg_len_mm", "peg_integral",
                 "cone_axis_agreement_deg", "mesh_agreement_deg",
                 "frame_proof", "tsv_max_gap_mm",
                 "hand_adjusted", "error", "run"]

METRIC_COLUMNS = ["case", "screw", "plan", "status", "selection",
                  "integral_chosen", "integral_max_cone", "delta",
                  "integral_max_searched", "delta_searched",
                  "integral_max_cone_2x", "delta_2x", "denominator_sensitivity_pct",
                  "candidates_cone", "candidates_searched", "on_search_grid_deg",
                  "safe_points", "samples_in_bounds",
                  "score_logged", "score_reproduced",
                  "safe_points_logged", "safe_points_reproduced",
                  "cone_half_angle_deg", "cone_height_mm", "cone_radius_mm",
                  "entry_r", "entry_a", "entry_s", "dir_r", "dir_a", "dir_s",
                  "length_mm", "entry_gap_mm", "mesh_agreement_deg",
                  "hand_adjusted", "error", "run"]

COMPARISON_COLUMNS = ["case", "screw", "selection",
                      "delta_pipeline", "delta_manual", "delta_gain",
                      "pipeline_denser",
                      "integral_pipeline", "integral_manual", "integral_ratio",
                      "integral_max_cone",
                      "theta_pipeline_deg", "theta_manual_deg",
                      "plans_apart_deg", "tip_gap_mm", "entry_gap_mm", "run"]

SUMMARY_COLUMNS = ["metric", "n", "mean", "sd", "min", "max", "note"]

PHASE_COLUMNS = ["case", "run", "t_total_s", "t1_s", "t2_s", "t3_s",
                 "t0_s", "t_refine_s", "phase_sum_s", "inside_steps_s",
                 "phase_residual_s",
                 "t1_exec_s", "t2_exec_s", "t3_exec_s",
                 "t1_wait_s", "t2_wait_s", "t3_wait_s",
                 "startup_s", "between_steps_s", "replay_review_s",
                 "tail_wait_exit_s", "t3_visits", "steps_seen", "steps_unassigned"]

DEFINITION_COLUMNS = ["term", "definition"]


def _stats(values: Sequence[Optional[float]]) -> Dict[str, Any]:
    numbers = [float(v) for v in values if isinstance(v, (int, float))]
    if not numbers:
        return {"n": 0, "mean": None, "sd": None, "min": None, "max": None}
    array = np.asarray(numbers, dtype=np.float64)
    return {"n": len(numbers),
            "mean": round(float(array.mean()), 4),
            # Sample standard deviation, undefined for a single case rather
            # than reported as zero -- a zero there would read as agreement.
            "sd": round(float(array.std(ddof=1)), 4) if len(numbers) > 1 else None,
            "min": round(float(array.min()), 4),
            "max": round(float(array.max()), 4)}


def summary_rows(angle_rows: List[Dict[str, Any]],
                 metric_rows: List[Dict[str, Any]],
                 comparison_rows: Optional[List[Dict[str, Any]]] = None
                 ) -> List[Dict[str, Any]]:
    """Mean / sd / min / max of each measure, across every case."""
    comparison_rows = comparison_rows or []
    scored = [row for row in metric_rows if row.get("delta") is not None
              and row.get("plan") == "pipeline"]
    # The two populations are NOT pooled. A "best effort" screw was chosen by
    # how deep it stays buried -- tie-broken by protrusion, and only then by
    # density -- so its delta scores a trajectory that was never optimised for
    # density at all. Averaging the two gives a number that answers neither
    # question and whose meaning drifts with the proportion of best-effort
    # screws in the cohort. Reporting the COUNT of them separately, which is
    # what the block below does, is not the same as reporting the DELTA
    # separately, which is what the paper's Table 1 needs.
    planned = [r for r in scored if r.get("selection") != "best effort"]
    effort = [r for r in scored if r.get("selection") == "best effort"]

    manual = [row for row in metric_rows if row.get("delta") is not None
              and row.get("plan") == "manual"]

    rows: List[Dict[str, Any]] = []
    measures: List[Tuple[str, List[Any], str]] = []
    for plan in PLANS:
        angles = [r for r in angle_rows if r.get("plan") == plan]
        measures.extend([
            ("theta1 (deg) — %s" % plan, [r.get("theta1_deg") for r in angles],
             "screw 1 against the middle peg"),
            ("theta2 (deg) — %s" % plan, [r.get("theta2_deg") for r in angles],
             "screw 2 against the middle peg"),
            ("theta3 (deg) — %s" % plan, [r.get("theta3_deg") for r in angles],
             "the two long screws against each other"),
        ])
    measures.extend([
        ("delta — pipeline (planned)", [r.get("delta") for r in planned],
         "the paper's delta, over the screws the planner actually optimised for "
         "density. Divides by the maximum over the FULL cone."),
        ("delta_searched — pipeline (planned)",
         [r.get("delta_searched") for r in planned],
         "the same, dividing instead by the half-cone the planner enumerated"),
        ("integral — pipeline (planned)",
         [r.get("integral_chosen") for r in planned],
         "the chosen path's own density integral"),
    ])
    if effort:
        measures.extend([
            ("delta — pipeline (BEST EFFORT)", [r.get("delta") for r in effort],
             "kept apart: these trajectories were chosen by DEPTH, not by "
             "density, so this is not the paper's delta and must not be pooled "
             "with the row above"),
            ("delta_searched — pipeline (BEST EFFORT)",
             [r.get("delta_searched") for r in effort],
             "the same, over the half-cone"),
        ])
    if manual:
        measures.extend([
            ("delta — manual", [r.get("delta") for r in manual],
             "the surgeon's hand-planned screws, scored in the SAME cone by the "
             "same integral. Every screw is included: a hand plan has no "
             "best-effort branch to separate."),
            ("integral — manual", [r.get("integral_chosen") for r in manual],
             "the hand-planned path's own density integral"),
        ])
    if comparison_rows:
        measures.extend([
            ("delta_gain (pipeline - manual)",
             [r.get("delta_gain") for r in comparison_rows],
             "paired per baseplate hole, so both sides share one denominator. "
             "Positive means the search found denser bone than the hand plan."),
            ("plans_apart (deg)",
             [r.get("plans_apart_deg") for r in comparison_rows],
             "how far the two plans aim from each other. Carries no quality "
             "judgement alone -- a large angle beside a small delta_gain means "
             "the surgeon chose a different corridor of equally good bone."),
        ])
    for metric, values, note in measures:
        row = {"metric": metric, "note": note}
        row.update(_stats(values))
        rows.append(row)

    # The rows below are COUNTS, not distributions, so they leave
    # mean/sd/min/max empty rather than filling those columns with a fraction
    # and a tally that happen to be numbers. `n` is the denominator and the note
    # carries the statement.
    if comparison_rows:
        won = sum(1 for r in comparison_rows if r.get("pipeline_denser"))
        rows.append({"metric": "screws where the pipeline beat the hand plan",
                     "n": len(comparison_rows),
                     "note": "%d of %d paired screw(s). Both sides were scored on "
                             "the same CT, along the same %d stations, and divided "
                             "by the same cone maximum, so the pairing is exact "
                             "rather than statistical."
                             % (won, len(comparison_rows), INTEGRATION_STATIONS)})
    for plan in PLANS:
        within = [r for r in angle_rows if r.get("plan") == plan
                  and r.get("theta1_within_cone") is not None
                  and r.get("theta2_within_cone") is not None]
        if not within:
            continue
        good = sum(1 for r in within
                   if r["theta1_within_cone"] and r["theta2_within_cone"])
        rows.append({"metric": "cases with theta1 AND theta2 inside the cone — %s"
                               % plan,
                     "n": len(within),
                     "note": "%d of %d case(s). This is the paper's acceptance "
                             "test, taken against the cone half-angle this "
                             "extension actually used, not against the paper's "
                             "alpha. The hand plan is under no obligation to "
                             "respect it -- the surgeon was not searching a cone."
                             % (good, len(within))})
    pipeline_rows = [r for r in metric_rows if r.get("plan") == "pipeline"]
    best_effort = [r for r in pipeline_rows if r.get("selection") == "best effort"]
    if best_effort:
        rows.append({"metric": "screws chosen as BEST EFFORT", "n": len(pipeline_rows),
                     "note": "%d of %d screw(s) had no fully contained trajectory, "
                             "so the planner returned the deepest-reaching "
                             "candidate instead. Those were picked by depth "
                             "rather than by density, so their delta measures a "
                             "different objective and should be reported apart "
                             "from the rest." % (len(best_effort), len(pipeline_rows))})
    return rows


COMPARISON_DEFINITIONS = [
    ("what this block compares",
     "The pipeline's cone search against the surgeon's own hand plan, one row "
     "per baseplate hole. Both trajectories start at the SAME point -- the hand "
     "plan reuses the pipeline's baseplate pose, measured at 0.000000 mm apart "
     "on every screw of every saved case -- so they search the same cone in the "
     "same bone, and the comparison is a paired one rather than a statistical "
     "one."),
    ("delta_pipeline / delta_manual / delta_gain",
     "Each plan's density integral divided by the SAME cone maximum, and the "
     "difference. One denominator is what makes the two deltas subtractable: it "
     "asks how much of the density available at this hole each plan captured. "
     "Positive delta_gain means the search found denser bone."),
    ("integral_pipeline / integral_manual / integral_ratio",
     "The two raw integrals and their ratio, for a reader who would rather not "
     "go through the cone maximum at all."),
    ("pipeline_denser",
     "Whether delta_pipeline exceeded delta_manual on this screw."),
    ("theta_pipeline_deg / theta_manual_deg",
     "Each plan's angulation from the prosthesis axis at this hole -- theta1 for "
     "screw 1, theta2 for screw 2 -- restated so one row carries the whole "
     "comparison."),
    ("plans_apart_deg / tip_gap_mm",
     "How far the two trajectories aim from each other, and how far apart their "
     "tips end up. Neither is a quality measure on its own: two screws can "
     "differ by 15 degrees and score alike. A large angle beside a small "
     "delta_gain is the interesting case -- the surgeon chose a different "
     "corridor through equally good bone."),
    ("entry_gap_mm",
     "Distance between the two plans' entry points, which must be ~0 for the "
     "pairing to be meaningful. Above %.1f mm the screws are not in the same "
     "hole and the pair is dropped rather than compared."
     % ENTRY_PAIR_TOLERANCE_MM),
    ("selection",
     "Carried over from the pipeline side. On a 'best effort' row the pipeline "
     "trajectory was chosen by DEPTH rather than density, so losing to the hand "
     "plan there is expected and is not evidence about the search."),
]


METHOD_DEFINITIONS = [
    ("what is measured",
     "The four quantities of Li et al., IJCARS 2022 17:1017-1027, Table 1: the "
     "three angles among the two long screws and the middle peg, and delta, the "
     "ratio of the chosen path's bone-density integral to the largest integral "
     "available anywhere in the cone when the screw-exposure constraint is "
     "ignored. Closer to 1 means containment cost less density."),
    ("everything is recomputed",
     "The extension stores none of this. RSA_PlanResults.tsv carries endpoints "
     "and a status but no score, quality_index is identically 1.000 by "
     "construction, and the integral of a REJECTED path -- which is what delta "
     "divides by -- is never computed by the planner at all, because it skips a "
     "candidate before scoring it. So the density integral is rebuilt here from "
     "the saved CT and the saved geometry."),
    ("the evidence that it is the same arithmetic",
     "score_logged is the 'Stability score' the run printed at planning time, "
     "and score_reproduced says whether the recomputed integral equals it. On "
     "the reference cases it matches bit for bit. The planner's stdout is "
     "truncated near 10 KB, so screw 2 usually has no logged score; a blank "
     "there is a missing witness, not a disagreement."),
    ("the integral",
     "The SUM of %d integer 0-255 samples taken along the screw centreline at "
     "j*length/%d for j = 1..%d -- nearest-neighbour, never interpolated, "
     "normalised as round((HU - min) * 255 / (max - min)) over the whole "
     "volume's scalar range. A sample outside the CT contributes the planner's "
     "own out-of-bounds sentinel (about -98 after normalisation) rather than "
     "zero. Every one of those choices is the extension's; changing any of them "
     "changes delta without changing anything visible."
     % (INTEGRATION_STATIONS, INTEGRATION_STATIONS, INTEGRATION_STATIONS)),
    ("the cone, and why there are two denominators",
     "The cone has its apex at the screw's entry point on the baseplate, its "
     "axis along the middle peg, height = the screw length and half-angle taken "
     "from the saved cone model. The planner searches only HALF of it: it drops "
     "every azimuth pointing toward the other screw's hole, so the two screws "
     "cannot converge. That is an anti-crossing rule, not the exposure "
     "constraint delta ablates, so delta divides by the FULL cone (the paper's "
     "'entire conical space') and delta_searched divides by the half the "
     "planner actually enumerated, read out of its own saved Cone_Region model."),
    ("the cone half-angle is not the paper's alpha",
     "This extension ships a %.1f deg HALF-angle, i.e. a %.0f deg full apex "
     "angle. The paper's alpha = 45 deg is the half-angle, so its cone is twice "
     "as wide and its theta1/theta2 range up to 45 deg where these are bounded "
     "by %.1f. Compare the angles to cone_half_angle_deg in this table, not to "
     "the paper's 45." % (CONE_HALF_ANGLE_DEG, 2 * CONE_HALF_ANGLE_DEG,
                          CONE_HALF_ANGLE_DEG)),
    ("coordinates",
     "Slicer writes model files in LPS; the plan table is in RAS. Everything "
     "here is converted to RAS at the read. The check matters because the "
     "angles cannot detect a failure to convert -- the mirror is orthogonal, so "
     "all three come out identical either way -- while delta would come out at "
     "about 1.000 for a plan that is not in the patient. tsv_max_gap_mm and "
     "samples_in_bounds are the two guards."),
]

ANGLE_DEFINITIONS = [
    ("theta1_deg / theta2_deg",
     "Angle between long screw 1 (respectively 2) and the middle peg. The peg's "
     "direction is also the axis of both cones, so these are the screws' "
     "angulations from that axis and cannot exceed the cone half-angle."),
    ("theta3_deg", "Angle between the two long screws."),
    ("theta1_within_cone / theta2_within_cone",
     "Whether the angle is inside the cone half-angle -- the paper's acceptance "
     "test. A value exactly at the bound is a rim candidate and is a result, "
     "not an error."),
    ("screw1_len_mm / screw2_len_mm / peg_len_mm",
     "Measured from the drawn tubes, not assumed. The prosthesis fixes them at "
     "%.2f mm and %.2f mm; a run whose constants differ is scored on its own "
     "measured lengths and flagged in the log."
     % (SCREW_LENGTH_MM, MIDDLE_LENGTH_MM)),
    ("peg_integral",
     "The middle peg's own density integral. It has no delta: its direction is "
     "fixed by the prosthesis, so there is no cone to search and nothing to "
     "divide by."),
    ("cone_axis_agreement_deg",
     "Angle between the middle peg's direction and the plane normal of the "
     "saved cone's base -- two independent readings of the axis the planner "
     "used. Expected 0."),
    ("frame_proof / tsv_max_gap_mm",
     "How the coordinate frame was established, and the largest disagreement "
     "between the drawn geometry and RSA_PlanResults.tsv, which is written "
     "independently and in RAS. Microns are the table's own six-figure "
     "rounding."),
    ("hand_adjusted",
     "Whether the run answered yes to 'adjust screw' after planning. If it did, "
     "the paths were dragged by hand and rewritten WITHOUT re-running the "
     "search, so delta then scores a trajectory the algorithm never chose."),
]

METRIC_DEFINITIONS = [
    ("screw / status / selection",
     "Which long screw, and the Status cell RSA_PlanResults.tsv recorded for "
     "it. 'best effort' means no trajectory in the cone kept the whole screw "
     "inside the bone, so the planner returned the DEEPEST-reaching one, broken "
     "by protrusion and only then by density. Its delta therefore measures a "
     "different objective and must not be averaged in silently."),
    ("integral_chosen", "The density integral of the path that was planned."),
    ("integral_max_cone / delta",
     "The largest integral anywhere in the FULL cone, and the ratio to it. This "
     "is the paper's delta."),
    ("integral_max_searched / delta_searched",
     "The same, over the half-cone the planner actually enumerated (read out of "
     "the saved Cone_Region model, so it is the exact candidate set). "
     "delta_searched >= delta always, and the gap is the cost of the "
     "anti-crossing filter rather than of containment."),
    ("integral_max_cone_2x / delta_2x / denominator_sensitivity_pct",
     "The full-cone sweep repeated at %dx the angular and radial resolution, "
     "and the percentage by which the maximum moved. The denominator is a "
     "maximum over a grid, and this column is what shows delta is a property of "
     "the anatomy rather than of the sampling." % DENOMINATOR_REFINE),
    ("candidates_cone / candidates_searched",
     "How many directions each denominator was taken over. candidates_searched "
     "is the planner's own count; a value other than half the full cone plus "
     "one means its refinement pass fired."),
    ("chosen_on_grid_deg",
     "The angle between the drawn path and the nearest candidate the planner "
     "searched. Zero means the drawn path IS the search's argmax. Anything else "
     "means it was moved by hand afterwards."),
    ("safe_points",
     "How many of the %d centreline samples reach the planner's nominal 0-255 "
     "threshold of %d. A display statistic in the extension -- it gates nothing "
     "-- reproduced here only because the run logged it, which makes it a "
     "second witness that the sampler is the same."
     % (INTEGRATION_STATIONS, SAFE_POINT_THRESHOLD)),
    ("samples_in_bounds",
     "How many of the %d samples fell inside the CT array. Fewer than %d and no "
     "ratio is reported at all: a path that has left the volume scores the "
     "sentinel at every station, and so does its denominator, so the ratio "
     "would come out near 1.000 for a plan that is not in the patient."
     % (INTEGRATION_STATIONS, MIN_SAMPLES_IN_BOUNDS)),
    ("score_logged / score_reproduced",
     "The Stability score this run printed while planning, and whether the "
     "recomputed integral equals it. Blank means the planner's stdout was "
     "truncated before that screw."),
    ("safe_points_logged / safe_points_reproduced",
     "The same comparison for the threshold tally. Not redundant with the one "
     "above: the integral is a SUM, which two different sample sets can reach "
     "by cancellation, while this is a COUNT over the same samples. Agreeing on "
     "both is what shows the sampler sits on the same voxels."),
    ("cone_half_angle_deg / cone_height_mm / cone_radius_mm",
     "Recovered from the saved cone model rather than assumed, because the "
     "half-angle is a spin box: a run made at a different setting must be "
     "scored against the cone it actually had."),
    ("entry_* / dir_*",
     "The screw's entry point and unit direction in RAS, so a reader can "
     "re-derive any of the above."),
]

PHASE_DEFINITIONS = [
    ("t1_s / t2_s / t3_s",
     "The paper's three phases, summed from the per-step timeline. "
     "t1 = reconstructing the 3D bone model (cb_step_2..11: segment, threshold, "
     "keep the largest island, build the surface). "
     "t2 = establishing the reference frame (cb_step_12..19: place the "
     "prosthesis centre point, then position and orient the baseplate -- this "
     "version of the extension picks ONE point, and the baseplate pose "
     "replaces the paper's remaining reference points). "
     "t3 = the automatic planning (cb_step_20 alone: that one step runs the "
     "whole cone search, once per screw)."),
    ("t0_s / t_refine_s",
     "Selecting the already-loaded CT, and the optional post-plan hand "
     "adjustment (cb_step_21..23). Both count toward the total and toward "
     "none of t1/t2/t3 -- charging the surgeon's dragging to 'automatic "
     "planning' would overstate t3 by several seconds."),
    ("t_total_s",
     "The whole run, Send click to Exit click. It includes the Exit dialog and "
     "the scene save (tail_wait_exit_s), which should be subtracted before this "
     "is quoted as procedure time, and it excludes loading the CT, which "
     "happens before the Send click and is outside every clock recorded here."),
    ("*_exec_s / *_wait_s",
     "Within a phase: time inside SafeExecutor running generated code, and "
     "wall minus exec. On the human-answered steps wait is the surgeon; on the "
     "automated ones it is dispatch and panel render."),
    ("phase_sum_s / phase_residual_s",
     "The phases summed, and inside_steps_s minus that sum. It should be within "
     "a few hundredths -- the timing report rounds each row to two decimals. It "
     "is printed rather than clamped."),
    ("t3_visits",
     "How many times the planning step ran. More than one means the run looped "
     "back through prosthesis adjustment and re-planned, so t3 is the total "
     "across those visits."),
    ("steps_seen / steps_unassigned",
     "How many step visits were summed, and any step belonging to no phase. "
     "steps_unassigned must be empty; anything in it means the workflow was "
     "renumbered and t1/t2/t3 are short by that step's time."),
]


def definition_rows(pairs: Sequence[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"term": term, "definition": text} for term, text in pairs]


def discover_cases(experiment_root: str) -> List[Dict[str, str]]:
    """One entry per run folder under ``Overall_Performance``."""
    return _discover_cases(experiment_root, RUNS_SUBDIR, DATASET_SUBDIR)


def build_report(experiment_root: str, progress=None) -> Dict[str, Any]:
    """Analyse every case. Fail-soft per case, so one bad scene costs one row."""
    cases = discover_cases(experiment_root)
    angle_rows: List[Dict[str, Any]] = []
    metric_rows: List[Dict[str, Any]] = []
    comparison_rows: List[Dict[str, Any]] = []
    failed: List[str] = []
    log: List[str] = []
    if not cases:
        log.append("No cases found under %s."
                   % os.path.join(experiment_root, RUNS_SUBDIR))

    for index, case in enumerate(cases):
        label = case["subject"] or case["run"]
        if progress is not None:
            try:
                progress(index, len(cases), label)
            except Exception:
                logger.debug("Progress callback failed", exc_info=True)
        # Before the work, not after: a hard crash takes the report with it, so
        # the last line logged is the only record of which case was in flight.
        logger.info("[RSA] case %d/%d: %s", index + 1, len(cases), label)
        try:
            result = analyse_case(case)
        except Exception as exc:
            log.append("%s: FAILED -- %s" % (label, exc))
            logger.warning("RSA analysis failed for %s", label, exc_info=True)
            # Recorded, not merely logged. A case that produces no row at all is
            # invisible in every table -- the panel's status line would report
            # the DISCOVERED count beside a mean taken over fewer cases than
            # that, which reads as a complete sweep.
            failed.append(label)
            continue
        angle_rows.extend(result["angle_rows"])
        metric_rows.extend(result["metric_rows"])
        comparison_rows.extend(result["comparison_rows"])
        pipeline_angles = next((r for r in result["angle_rows"]
                                if r.get("plan") == "pipeline"), {})
        scored = [row for row in result["metric_rows"] if row.get("delta") is not None]
        won = sum(1 for r in result["comparison_rows"] if r.get("pipeline_denser"))
        log.append("%s: theta 1/2/3 = %s / %s / %s deg, %d trajector(ies) scored, "
                   "pipeline denser on %d of %d paired screw(s)"
                   % (label,
                      _fmt(pipeline_angles.get("theta1_deg")),
                      _fmt(pipeline_angles.get("theta2_deg")),
                      _fmt(pipeline_angles.get("theta3_deg")),
                      len(scored), won, len(result["comparison_rows"])))
        for note in result["notes"]:
            log.append("   [!] %s: %s" % (label, note))

    timing_rows, step_rows = collect_timing(cases, log)
    by_case = {}
    for step in step_rows:
        by_case.setdefault(step["run"], []).append(step)
    timing_by_run = {row["run"]: row for row in timing_rows}
    phase_rows = [phase_row(case, timing_by_run.get(case["run"], {}),
                            by_case.get(case["run"], []), log)
                  for case in cases]

    summary = summary_rows(angle_rows, metric_rows, comparison_rows)
    timing_title, timing_blocks = timing_sheet(timing_rows, step_rows)

    sheets = [
        ("Metrics", [
            # The comparison leads the sheet: it is the question the workbook
            # exists to answer, and everything under it is the working.
            ("PIPELINE vs the surgeon's HAND PLAN, one row per baseplate hole. "
             "Both trajectories leave the same entry point along the same cone "
             "axis, and both are scored by the same integral on the same CT and "
             "divided by the same cone maximum -- so delta_gain is a paired "
             "difference, not a comparison of two separately-normalised numbers. "
             "Positive delta_gain means the cone search found denser bone than "
             "the hand plan did.",
             COMPARISON_COLUMNS, comparison_rows),
            ("Angles among the two long screws and the middle peg, per case and "
             "per plan, in degrees. The peg's direction is also the axis of both "
             "search cones, so theta1 and theta2 are the screws' angulations "
             "from that axis and — for the pipeline — are bounded by the cone "
             "half-angle, which this extension sets to %.1f deg, half of the "
             "paper's alpha. The hand plan is under no such bound."
             % CONE_HALF_ANGLE_DEG,
             ANGLE_COLUMNS, angle_rows),
            ("Bone-density path integral and its cone-space maximum, one row "
             "per long screw per plan. delta divides by the maximum over the "
             "FULL cone, which is the paper's 'entire conical space'; "
             "delta_searched divides by the half-cone the planner actually "
             "enumerated. A 'best effort' row had no fully contained trajectory "
             "and was chosen by depth rather than density, so its delta answers "
             "a different question.",
             METRIC_COLUMNS, metric_rows),
            ("Across all cases", SUMMARY_COLUMNS, summary),
            # Last, under the numbers they describe, so the sheet reads results
            # first and then what they mean.
            ("DEFINITIONS — how the measurement is made",
             DEFINITION_COLUMNS, definition_rows(METHOD_DEFINITIONS)),
            ("DEFINITIONS — pipeline vs manual columns",
             DEFINITION_COLUMNS, definition_rows(COMPARISON_DEFINITIONS)),
            ("DEFINITIONS — angle columns",
             DEFINITION_COLUMNS, definition_rows(ANGLE_DEFINITIONS)),
            ("DEFINITIONS — density columns",
             DEFINITION_COLUMNS, definition_rows(METRIC_DEFINITIONS)),
        ]),
        (timing_title, [
            ("The paper's phases, summed from the per-step timeline below. "
             "t1 = 3D bone reconstruction, t2 = the reference point and the "
             "baseplate pose, t3 = the automatic cone search. t0 (selecting the "
             "CT) and t_refine (post-plan hand adjustment) count toward the "
             "total and toward none of the three.",
             PHASE_COLUMNS, phase_rows),
            ("DEFINITIONS — phase columns",
             DEFINITION_COLUMNS, definition_rows(PHASE_DEFINITIONS)),
        ] + list(timing_blocks)),
    ]
    return {"sheets": sheets, "log": log, "angle_rows": angle_rows,
            "metric_rows": metric_rows, "comparison_rows": comparison_rows,
            "summary": summary,
            "phase_rows": phase_rows, "timing_rows": timing_rows,
            "step_rows": step_rows, "cases": len(cases),
            # `cases` is what was DISCOVERED and `analysed` is what produced a
            # row. They differ exactly when `failed` is non-empty, and a caller
            # quoting the first beside a mean taken over the second would
            # overstate the sweep.
            # Distinct CASES, not rows: angle_rows now carries one row per plan.
            "analysed": len({row["case"] for row in angle_rows}),
            "failed_cases": failed}


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
