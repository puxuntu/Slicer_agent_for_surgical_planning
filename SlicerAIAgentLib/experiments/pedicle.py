"""PedicleScrewPlanner: is each planned screw inside the pedicle, and in what bone.

Every run under ``Experiments/PedicleScrewPlanner/Overall_Performance/`` saved its
plan into ``Statistic/scene/``: one ``w_<N>_D<d>_L.mrk.json`` trajectory per screw
(two control points, entry then tip, with the diameter on the node's
``ScrewDiameter`` attribute), the ``Screw_<site>.vtk`` cylinder built from it, and
the ``Isthmus-<N>.mrk.json`` pedicle-isthmus landmark the surgeon placed. Beside
the runs, ``Dataset/<case>/`` holds the CT the plan was made on and
``segmentation.seg.nrrd``, a per-structure ground truth in which every vertebra
carries its own label.

That segmentation is what makes this analysis possible at all. The metric guide's
§3 is the finding to keep in view: **no HU threshold separates "inside this
vertebra" from "outside it"** on these scans, because trabecular marrow here reads
0-100 HU while paraspinal muscle reads 40-60. Two attempts at a threshold-only
containment test are recorded there, and both failed on real data. So every
positional claim below -- breach, clearance, containment, pedicle width, depth --
is made against the label, and only the density claims (§1.4-1.7) are made against
the CT, where HU is exactly what is being asked about.

Four things this module enforces rather than assumes. Each of them yields a
plausible number rather than an error when it is got wrong, which is why each is
checked in code and reported in the workbook:

* **The plan and the ground truth are in DIFFERENT frames, and the bridge between
  them is a property of the voxel grid, not of a header.** The run's volume was
  loaded centred -- ``space origin: (-125.5,-125.5,-123)``, i.e. minus half the
  extent -- while the dataset volume and its segmentation keep the scanner's own
  origin (``(-156.7,-85.8,676.3)`` for case ``1_304``). Same sizes, same direction
  cosines, different origin: the two are the same image indexed the same way, so a
  point maps across by going THROUGH the voxel index
  (:func:`frame_bridge`). The scene volume is found by matching that grid rather
  than by name, and a run with no matching volume is refused -- ``baselineROI.nrrd``
  sits in the same folder and is a 0.245 mm resample of the same data, so a name
  guess would silently score the plan against an interpolated copy.
* **The vertebra a screw belongs to is decided by the LANDMARK, never by the
  name.** Both sides name their levels (the plan says ``Screw_T11_L``, the ground
  truth says ``T11 vertebra``) and neither name is evidence: the planner's level
  comes from what the user picked in step 2, and the segmentation's from
  TotalSegmentator's own counting, so a miscount at either end -- one the operator
  makes, one the network makes -- puts a screw's numbers against the wrong bone
  while everything still validates. :func:`assign_level` votes the vertebra labels
  in a ball around the surgeon's own isthmus landmark, cross-checks against the
  level's anterior landmark, and reports the agreement (``name_agrees``) as a
  finding rather than using it.
* **A screw is NOT breached where it crosses the entry cortex.** The planner puts
  the entry point ON the bone surface (``Helper.probeVolume``), so the cylinder
  wall within about one radius of the entry plane necessarily straddles it: on the
  saved runs that reads as +0.9 to +2.4 mm of "protrusion" at 0 mm from the entry,
  which would grade four of eight otherwise-contained screws as Gertzbein-Robbins
  B. The first ``radius`` millimetres are therefore excluded from the grade -- that
  is the geometric scale of the effect, since a wall point at axial offset ``d`` can
  only be outside an entry plane inclined at ``theta`` while ``d < r*tan(theta)``.
  ``breach_with_entry_mm`` keeps the unrestricted figure and ``breach_offset_mm``
  says where the worst point was, so nothing is hidden by the exclusion.
* **The entry point is an independent witness that the bridge is right.**
  ``entry_on_surface_mm`` is how far the planned entry lands from the label's
  surface; it is 0.2-1.3 mm on the saved runs, i.e. on the cortex, which is where
  the planner put it. A mistaken bridge -- a missed LPS flip, the wrong volume,
  the wrong case -- moves it by tens of millimetres. It is checked, and a run that
  fails it is reported unscored rather than scored wrongly.

Two measures of the same width are reported, for the reason ``shoulder.py``
reports two cone denominators. ``pedicle_width_mm`` is the minimum caliper of the
label's cross-section perpendicular to the trajectory -- the anatomic pedicle
width, the quantity the 70-80% fill target is quoted against -- and
``channel_width_mm`` is the narrowest chord of that section THROUGH the screw
axis, which is what the screw itself passes through. They agree to about a
millimetre on the saved runs; where they do not, the section has caught something
beside the pedicle and the caliper is the one to distrust.

Not computed, deliberately: **deviation from the anatomic pedicle axis** (guide
§2.11). It needs the pedicle segmented apart from the vertebra, and the only
pedicle-shaped object available here is the channel around the screw -- so the
axis would be derived from the trajectory it is supposed to judge. A circular
number that looks like a measurement is worse than a blank column.

Slicer-free and Qt-free -- numpy, scipy.ndimage and the readers in this package --
so ``scripts/check_pedicle_analysis.py`` runs the whole analysis against the real
saved runs outside Slicer.
"""

from __future__ import annotations

import glob
import logging
import os
import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import geometry_io, segmentation_io, volume_io
from .run_timing import (canonical_step_id, collect_timing,
                         discover_cases as _discover_cases, timing_sheet)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

EXTENSION_NAME = "PedicleScrewPlanner"
EXPERIMENT_DIR = os.path.join("Experiments", EXTENSION_NAME)
RUNS_SUBDIR = "Overall_Performance"
DATASET_SUBDIR = "Dataset"
WORKBOOK_NAME = "PedicleScrewPlanner_summary.xlsx"

#: The ground truth of one case. The CT is found beside it as the only other
#: ``.nrrd``, so a case folder may name its volume anything.
SEGMENTATION_NAME = "segmentation.seg.nrrd"

#: A ground-truth segment that is a vertebra. TotalSegmentator writes
#: ``T11 vertebra`` / ``L1 vertebra``; nothing else in its 100-odd structures
#: matches, so this is what separates the bones a screw can be in from the lungs,
#: ribs and vessels it cannot.
VERTEBRA_NAME = re.compile(r"^\s*([CTLS])\s*(\d+)\s+vertebra\s*$", re.IGNORECASE)

#: ``w_<N>_D<diameter>_L`` -- the planner's trajectory line. The node name spells
#: the diameter ``D:5.0`` and the file name ``D5.0``, since a colon cannot be in a
#: file name; both are accepted and neither is trusted (see ``SCREW_DIAMETER_ATTR``).
LINE_NAME = re.compile(r"^w_(\d+)_D:?([0-9.]+)_L$")
SCREW_MODEL_NAME = re.compile(r"^Screw_(.+)$")
ISTHMUS_FILE = re.compile(r"Isthmus-(\d+)\.mrk\.json$", re.IGNORECASE)

#: The attribute ``Helper.screwDiameter`` reads. Authoritative; the name is only a
#: fallback for a scene saved before the diameter moved off the display node.
SCREW_DIAMETER_ATTR = "ScrewDiameter"


# ---------------------------------------------------------------------------
# Measurement parameters
# ---------------------------------------------------------------------------

#: Radius of the ball voted to decide which vertebra a landmark is in. Large
#: enough that a landmark sitting one voxel outside the label still resolves --
#: on the saved runs one isthmus point does exactly that -- and far smaller than
#: the gap to the next vertebra.
LANDMARK_BALL_MM = 4.0

#: The winning vertebra must hold at least this share of the ball's VERTEBRA
#: votes. Not of the ball: a landmark in a narrow pedicle legitimately has most
#: of its ball outside any bone (0.42 on one saved screw), and refusing that
#: would refuse the correct answer. What must not happen is two vertebrae
#: splitting the vote, which is what this catches.
LANDMARK_MIN_MARGIN = 0.75

#: ...and it must have SOME support, so a landmark that missed the spine entirely
#: cannot be resolved by a single stray voxel.
LANDMARK_MIN_VOXELS = 5

#: How far outside the vertebra the signed-distance field must remain valid. Every
#: distance quoted here is smaller than this, and the crop is taken around the
#: label's own bounding box, so the field is exact within it.
SDF_MARGIN_MM = 25.0

#: Sampling of the screw's lateral surface: a station every 0.25 mm along the axis
#: and 72 rays around it, which is a sample about every 0.2 mm of circumference on
#: a 5 mm screw.
AXIAL_STEP_MM = 0.25
ANGULAR_SAMPLES = 72

#: Radial shells through the screw's volume, for the containment fraction and the
#: path-HU median. Weighted by radius so the samples are area-uniform: an
#: unweighted grid over (radius, angle) over-counts the axis by an order of
#: magnitude and reports the marrow the screw core sits in as if it were the
#: whole implant.
RADIAL_SHELLS = 6

#: The window the extension itself grades, +/-5 mm about the isthmus landmark
#: (three literal ``5``s in ``PlanningMeasurementsStep.okShow``). Reused here so
#: ``breach_isthmus_mm`` and the pedicle width describe the same span of screw the
#: module's own table describes.
ISTHMUS_HALF_WINDOW_MM = 5.0

#: Gertzbein-Robbins, in millimetres of protrusion beyond the pedicle cortex.
#: A <= 0 < B < 2 <= C < 4 <= D < 6 <= E.
GRADE_BOUNDS = ((0.0, "A"), (2.0, "B"), (4.0, "C"), (6.0, "D"))
GRADE_WORST = "E"
#: A and B together are what the literature reports as "clinically acceptable".
ACCEPTABLE_GRADES = ("A", "B")

#: The medial wall is the one that matters: a breach there threatens cord and
#: root, where the same millimetre laterally usually does not. Below this the
#: screw is flagged even when it is contained.
MEDIAL_CLEARANCE_MIN_MM = 1.0

#: Half-angle of the cone of surface directions counted as facing one anatomic
#: way. 60 degrees, so the six directions cover the sphere with overlap and no
#: point is left unclassified.
DIRECTION_CONE_COS = 0.5

#: The directions a CLEARANCE is reported for. Four, not six: a cylinder's
#: outward normals are perpendicular to its axis, and the axis is mostly
#: anterior, so no point of the WALL ever faces anteriorly or posteriorly. The
#: full six still name ``breach_direction``, because the TIP end cap does face
#: anteriorly and a screw out the front of the body protrudes through it.
WALL_DIRECTIONS = ("medial", "lateral", "superior", "inferior")

#: HU bands, from ``PlanningGradeStep.__init__``: ``__cancellousMin = 130`` and
#: ``__corticalMin = __cancellousMax = 250``. Kept identical so a contact area
#: here is the module's own column expressed in mm2 rather than as a percentage.
CANCELLOUS_MIN_HU = 130.0
CORTICAL_MIN_HU = 250.0

#: HU returned where a sample lands outside the CT. Air, so it can only lower a
#: density figure -- never raise one -- and it is the value the extension's own
#: sampler uses.
OUT_OF_VOLUME_HU = -1000.0

#: Erosion applied to the vertebra label before its trabecular HU is taken, so
#: the cortical shell is excluded (guide §2.9).
TRABECULAR_EROSION_MM = 3.0

#: The plane separating the vertebral BODY from the posterior elements, for the
#: trabecular ROI: anterior of the level's isthmus landmarks. An approximation,
#: and named as one in the workbook -- the pedicle isthmus sits at roughly the
#: posterior wall of the body, so this keeps the body and drops the lamina.
BODY_IS_ANTERIOR_OF_ISTHMUS = True

#: Marching step for the axis probes (anterior cortex, depth). Finer than a voxel
#: in every direction, so the crossing is limited by the field and not by the walk.
AXIS_PROBE_STEP_MM = 0.1
AXIS_PROBE_LIMIT_MM = 140.0

#: In-plane search radius for the pedicle cross-section, and its sampling.
SECTION_RADIUS_MM = 14.0
SECTION_STEP_MM = 0.25
SECTION_ALONG_STEP_MM = 0.5
#: Directions over which the caliper width and the through-axis chord are
#: minimised.
SECTION_DIRECTIONS = 180

#: A cross-section wider than this is not a pedicle -- the plane has caught the
#: body or the lamina -- so the width is reported with a note rather than silently
#: divided into a fill ratio.
PEDICLE_WIDTH_MAX_MM = 25.0

#: How far the planned entry may sit from the label's surface before the run is
#: refused. The planner puts it ON the surface, so this is a witness that the
#: frame bridge and the case pairing are both right; 0.2-1.3 mm on the saved runs.
#: Generous, because it also absorbs the difference between the HU surface the
#: planner probed and the label's own boundary.
ENTRY_SURFACE_LIMIT_MM = 6.0

#: How far the ``Screw_<site>`` cylinder's axis may sit from its trajectory line
#: before the two are not the same screw. They are built from the same two points
#: (``p2pCyl(PB, PT, ...)``), so this is 0.000 mm when the pairing is right.
MODEL_AXIS_LIMIT_MM = 1.0

#: The clinical fill target, for the penalty column. 70-80% is the usual range.
FILL_TARGET_PCT = 75.0


# ---------------------------------------------------------------------------
# Timing phases
# ---------------------------------------------------------------------------

#: The wizard's own pages, which is what the cookbook steps follow. t3 is the
#: planning itself -- choosing each site's diameter and dragging its trajectory --
#: and is the phase a reader compares across conditions; charging the grading
#: pages to it would overstate it by the length of a table review.
PHASE_STEPS = {
    "t0": ("cb_step_1", "cb_step_2"),
    "t1": ("cb_step_3", "cb_step_4", "cb_step_5"),
    "t2": ("cb_step_6", "cb_step_7", "cb_step_8", "cb_step_9", "cb_step_10",
           "cb_step_11", "cb_step_12", "cb_step_13", "cb_step_14"),
    "t3": ("cb_step_15", "cb_step_16", "cb_step_17", "cb_step_18", "cb_step_19",
           "cb_step_20"),
    "t4": ("cb_step_21", "cb_step_22", "cb_step_23"),
}
PHASE_ORDER = ("t0", "t1", "t2", "t3", "t4")
PHASE_TITLES = {
    "t0": "t0 load the CT",
    "t1": "t1 region of interest + levels",
    "t2": "t2 place the landmarks",
    "t3": "t3 plan the screws",
    "t4": "t4 grade + finish",
}
_PHASE_OF_STEP = {canonical_step_id(step): phase
                  for phase, steps in PHASE_STEPS.items() for step in steps}


# ---------------------------------------------------------------------------
# Reading one run's plan
# ---------------------------------------------------------------------------

def _storage_files(root: ET.Element, scene_dir: str) -> Dict[str, str]:
    return {node.get("id"): os.path.join(scene_dir, node.get("fileName"))
            for node in root.iter()
            if node.get("id") and node.get("fileName")}


def _node_file(node: ET.Element, storage: Dict[str, str]) -> Optional[str]:
    candidates: List[str] = []
    for entry in (node.get("references") or "").split(";"):
        key, separator, value = entry.partition(":")
        if separator and key.strip() == "storage":
            candidates.extend(value.split())
    candidates.extend((node.get("storageNodeRef") or "").split())
    for candidate in candidates:
        path = storage.get(candidate)
        if path and os.path.isfile(path):
            return path
    return None


def _attribute(node: ET.Element, name: str) -> Optional[str]:
    for entry in (node.get("attributes") or "").split(";"):
        key, separator, value = entry.partition(":")
        if separator and key.strip() == name:
            return value.strip()
    return None


def read_plan(scene_dir: str) -> Dict[str, Any]:
    """``{"lines": {N: {...}}, "models": {site: path}}`` for one saved scene.

    Read from ``scene.mrml`` and not from the file names, for
    ``geometry_io.scene_role_files``' reason: the diameter is a node ATTRIBUTE and
    only the scene records it, while a file name is a display name Slicer will
    uniquify. The name is kept as a fallback so a scene saved before the diameter
    moved off the display node still reads.
    """
    path = os.path.join(scene_dir, "scene.mrml")
    root = ET.parse(path).getroot()
    storage = _storage_files(root, scene_dir)

    lines: Dict[int, Dict[str, Any]] = {}
    models: Dict[str, str] = {}
    for node in root.iter():
        name = node.get("name") or ""
        match = LINE_NAME.match(name)
        if match and node.tag == "MarkupsLine":
            stored = _attribute(node, SCREW_DIAMETER_ATTR)
            file_path = _node_file(node, storage)
            if file_path is None:
                continue
            lines[int(match.group(1))] = {
                "index": int(match.group(1)),
                "node": name,
                "file": file_path,
                "diameter_mm": float(stored) if stored else float(match.group(2)),
                "diameter_from": "attribute" if stored else "node name",
            }
            continue
        match = SCREW_MODEL_NAME.match(name)
        if match and node.tag == "Model":
            file_path = _node_file(node, storage)
            if file_path is not None:
                models[match.group(1)] = file_path
    return {"lines": lines, "models": models}


def read_landmarks(scene_dir: str) -> Dict[str, Any]:
    """``{"isthmus": {N: (point RAS, site label)}, "anterior": [(point, label)]}``.

    ``Isthmus-<N>`` is the pedicle isthmus landmark of screw ``N`` -- the module
    copies it out of ``T`` and labels it with the site, which is the only place
    the plan writes down what it thinks each screw's level is. ``T`` carries three
    points per level, ``(anterior, left isthmus, right isthmus)``, so the level's
    anterior point is the one at the start of the triple its isthmus falls in.
    Both are returned in RAS: the files are written LPS and are mirrored here, in
    the frame the ``.vtk`` models beside them use.
    """
    isthmus: Dict[int, Tuple[np.ndarray, str]] = {}
    for path in sorted(glob.glob(os.path.join(scene_dir, "Isthmus-*.mrk.json"))):
        match = ISTHMUS_FILE.search(os.path.basename(path))
        if not match:
            continue
        points, labels = geometry_io.read_markups_points(path)
        if points.shape[0]:
            isthmus[int(match.group(1))] = (
                geometry_io.lps_to_ras(points)[0], labels[0] if labels else "")

    anterior: List[Tuple[np.ndarray, str]] = []
    raw = os.path.join(scene_dir, "T.mrk.json")
    if os.path.isfile(raw):
        points, labels = geometry_io.read_markups_points(raw)
        points = geometry_io.lps_to_ras(points)
        for index in range(0, points.shape[0] - 2, 3):
            anterior.append((points[index], labels[index] if labels else ""))
    return {"isthmus": isthmus, "anterior": anterior}


def line_endpoints(path: str) -> Tuple[np.ndarray, np.ndarray]:
    """``(entry, tip)`` of a trajectory line, in RAS.

    Control point 0 is the entry and 1 the tip, and that is the extension's own
    order rather than a guess about which end is anterior:
    ``Helper.Screw`` builds the line as ``p2pexLine(PB, PT, ...)`` where ``PB``
    comes from ``probeVolume`` -- the bone surface -- and ``PT`` is the anterior
    landmark end. The screw model is then ``p2pCyl(PB, PT, ...)``, so the two
    agree by construction, which is what ``model_axis_gap_mm`` checks.
    """
    points, _labels = geometry_io.read_markups_points(path)
    if points.shape[0] < 2:
        raise ValueError("%s has %d control point(s), not 2"
                         % (os.path.basename(path), points.shape[0]))
    points = geometry_io.lps_to_ras(points)
    return points[0], points[1]


# ---------------------------------------------------------------------------
# The frame bridge
# ---------------------------------------------------------------------------

def _grid_of(path: str) -> Tuple[List[int], np.ndarray]:
    """``(sizes, ijk_to_ras)`` from a NRRD header alone, without the payload."""
    fields, _meta, ijk_to_ras, sizes, dimension, _offset, _dtype = \
        segmentation_io._read_header(path)                    # noqa: SLF001
    return sizes[:dimension], ijk_to_ras


def scene_volume_matching(scene_dir: str, sizes: Sequence[int],
                          ijk_to_ras: np.ndarray) -> Tuple[Optional[str], List[str]]:
    """The run's own copy of the CT: the ``.nrrd`` on the ground truth's GRID.

    Found by matching rather than by name, and that is not fastidiousness. The
    same folder holds ``baselineROI.nrrd``, a 0.245 mm resample of the same data
    that the extension builds its plan on; picking a volume by name would score
    the plan against an interpolated copy on a different grid, and the bridge
    below -- which is only a translation because the grids are identical -- would
    silently stop being one.
    """
    notes: List[str] = []
    matches: List[str] = []
    for path in sorted(glob.glob(os.path.join(scene_dir, "*.nrrd"))):
        if path.lower().endswith(".seg.nrrd"):
            continue
        try:
            other_sizes, other_matrix = _grid_of(path)
        except Exception as exc:
            notes.append("%s: unreadable header (%s)"
                         % (os.path.basename(path), exc))
            continue
        if list(other_sizes) != list(sizes):
            continue
        if not np.allclose(other_matrix[:3, :3], np.asarray(ijk_to_ras)[:3, :3],
                           atol=1e-6):
            continue
        matches.append(path)
    if not matches:
        return None, notes
    if len(matches) > 1:
        notes.append("%d volumes in the scene share the ground truth's grid (%s); "
                     "using the first"
                     % (len(matches), ", ".join(os.path.basename(p)
                                                for p in matches)))
    return matches[0], notes


def frame_bridge(scene_ijk_to_ras: np.ndarray,
                 truth_ijk_to_ras: np.ndarray) -> np.ndarray:
    """Scene RAS -> ground-truth RAS, THROUGH the voxel index.

    The run loaded its volume centred and the dataset keeps the scanner's origin,
    so the two describe the same image with different world coordinates. Going
    through IJK is what makes that a fact rather than an assumption: voxel
    ``(i,j,k)`` is the same measurement in both files, so the map that takes one
    file's world position of that voxel to the other's is the map between the
    frames. The caller has already required identical ``sizes`` and identical
    direction cosines, which is what makes the result a pure translation.
    """
    return np.asarray(truth_ijk_to_ras, dtype=float) @ np.linalg.inv(
        np.asarray(scene_ijk_to_ras, dtype=float))


def apply_transform(matrix: np.ndarray, points: np.ndarray) -> np.ndarray:
    points = np.atleast_2d(np.asarray(points, dtype=float))
    return (np.column_stack([points, np.ones(points.shape[0])])
            @ np.asarray(matrix, dtype=float).T)[:, :3]


# ---------------------------------------------------------------------------
# The vertebra: mask, signed distance, CT
# ---------------------------------------------------------------------------

def spacing_mm(ijk_to_ras: Sequence[Sequence[float]]) -> np.ndarray:
    """``[si, sj, sk]`` -- the norm of each DIRECTION COLUMN.

    Of the matrix, never of its inverse: the inverse gives voxels per millimetre,
    which scales every distance by the wrong factor and leaves the dimensionless
    ratios untouched, so only the millimetre columns would show it.
    """
    return np.linalg.norm(np.asarray(ijk_to_ras, dtype=float)[:3, :3], axis=0)


def label_bounding_box(volume: np.ndarray, label: int, margin_voxels: int,
                       slab_bytes: int = segmentation_io.SLAB_BYTES
                       ) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """``(low, high)`` in ``[i, j, k]``, scanned in slabs. ``None`` if absent.

    Slabs for :mod:`segmentation_io`'s reason -- the array is a memory map of a
    decompressed segmentation and comparing all of it at once costs a copy of the
    whole volume. ``Segment<N>_Extent`` is deliberately not used: on this data
    every segment records the full volume as its extent, so it would say nothing,
    and where it does say something a stale one truncates silently.
    """
    nk, nj, ni = volume.shape
    step = max(1, int(slab_bytes) // max(1, nj * ni))
    low = np.array([ni, nj, nk], dtype=np.int64)
    high = np.array([-1, -1, -1], dtype=np.int64)
    for start in range(0, nk, step):
        stop = min(nk, start + step)
        mask = np.asarray(volume[start:stop]) == label
        if not mask.any():
            continue
        kk, jj, ii = np.nonzero(mask)
        low = np.minimum(low, [ii.min(), jj.min(), kk.min() + start])
        high = np.maximum(high, [ii.max(), jj.max(), kk.max() + start])
    if high[0] < 0:
        return None
    low = np.maximum(low - margin_voxels, 0)
    high = np.minimum(high + margin_voxels + 1, [ni, nj, nk])
    return low.astype(np.int64), high.astype(np.int64)


class VertebraField(object):
    """One vertebra, cropped: its mask, its signed distance, and the CT over it.

    The signed distance is ``EDT(outside) - EDT(inside)``, sampled trilinearly.
    Both halves are needed and the pair is what puts the zero level set on the
    voxel FACE: between a last-inside voxel at ``-s`` and its outside neighbour at
    ``+s``, a linear interpolation crosses zero at the midpoint, which is the
    boundary the label actually claims. Taking one half alone would put it at a
    voxel centre, half a voxel out -- 0.25-0.5 mm on this data, which is a quarter
    of the width of a Gertzbein-Robbins grade and most of a clearance flag.

    The crop is exact rather than approximate. It is taken around the label's own
    bounding box plus ``SDF_MARGIN_MM``, so every voxel of the label is inside it
    and the nearest label voxel to any point in the box is therefore also inside
    it; and the box border is background, so the nearest background voxel to an
    inside point is too. Uncropped, each transform runs over the whole 64-107
    million voxel volume.
    """

    __slots__ = ("label", "name", "origin", "mask", "sdf", "hu",
                 "ijk_to_ras", "ras_to_ijk", "spacing", "centroid")

    def __init__(self, label: int, name: str, origin: np.ndarray,
                 mask: np.ndarray, sdf: np.ndarray, hu: Optional[np.ndarray],
                 ijk_to_ras: np.ndarray):
        self.label = label
        self.name = name
        self.origin = origin                       # [i0, j0, k0] of the crop
        self.mask = mask
        self.sdf = sdf
        self.hu = hu
        self.ijk_to_ras = np.asarray(ijk_to_ras, dtype=float)
        self.ras_to_ijk = np.linalg.inv(self.ijk_to_ras)
        self.spacing = spacing_mm(self.ijk_to_ras)
        self.centroid = self._centroid()

    # -- coordinates -------------------------------------------------------
    def _local(self, points: np.ndarray) -> np.ndarray:
        """``[k, j, i]`` rows for ``map_coordinates``, in crop-local indices."""
        points = np.atleast_2d(np.asarray(points, dtype=float))
        ijk = (np.column_stack([points, np.ones(points.shape[0])])
               @ self.ras_to_ijk.T)[:, :3]
        return np.vstack([ijk[:, 2] - self.origin[2],
                          ijk[:, 1] - self.origin[1],
                          ijk[:, 0] - self.origin[0]])

    def distance(self, points: np.ndarray) -> np.ndarray:
        """Signed distance in mm to the label's surface. Negative inside.

        Debiased by half a voxel, which is not cosmetic. The transforms measure
        centre-to-centre, so for a boundary at ``X`` the field at a point ``d``
        away reads ``d + h/2``: the zero crossing is still exactly on the voxel
        face (the last inside sample is ``-h`` and the first outside one ``+h``,
        so the interpolation crosses at the midpoint), but every magnitude
        beyond one voxel is a half-voxel too large. Uncorrected that is +0.25 to
        +0.5 mm on this data -- it inflates a breach, and, worse, it inflates a
        CLEARANCE, which is compared against a 1 mm threshold.

        The correction inverts the relation exactly: inside the one-voxel
        transition band the interpolated field has slope 2, so ``d = |raw|/2``;
        beyond it the slope is 1 with the offset, so ``d = |raw| - h/2``. The
        two agree at ``|raw| = h``, so the result is continuous.

        ``h`` is the mean voxel spacing. It is exact for a boundary normal to an
        axis of that spacing and leaves at most half the anisotropy elsewhere --
        0.17 mm on these 0.49 x 0.49 x 1.0 mm volumes, against the 0.25-0.5 mm
        it removes.
        """
        from scipy import ndimage                             # noqa: PLC0415
        raw = ndimage.map_coordinates(self.sdf, self._local(points),
                                      order=1, mode="nearest")
        half = 0.5 * float(np.mean(self.spacing))
        magnitude = np.abs(raw)
        corrected = np.where(magnitude <= 2.0 * half, magnitude / 2.0,
                             magnitude - half)
        return np.sign(raw) * corrected

    def density(self, points: np.ndarray) -> np.ndarray:
        """HU at ``points`` (RAS), nearest neighbour, air outside the crop.

        Nearest neighbour and not trilinear: a CT voxel IS the measurement, and
        interpolating one blurs the cortical peak the density bands are defined
        against -- the 250 HU threshold would then be crossed by a point that no
        voxel reports as cortical.
        """
        from scipy import ndimage                             # noqa: PLC0415
        if self.hu is None:
            return np.full(np.atleast_2d(points).shape[0], np.nan)
        local = np.rint(self._local(points)).astype(np.int64)
        shape = np.asarray(self.hu.shape, dtype=np.int64).reshape(3, 1)
        inside = np.logical_and((local >= 0).all(axis=0),
                                (local < shape).all(axis=0))
        values = np.full(local.shape[1], float(OUT_OF_VOLUME_HU))
        if inside.any():
            chosen = local[:, inside]
            values[inside] = self.hu[chosen[0], chosen[1], chosen[2]]
        return values

    def _centroid(self) -> np.ndarray:
        kk, jj, ii = np.nonzero(self.mask)
        if ii.size == 0:
            return np.zeros(3)
        mean = np.array([ii.mean() + self.origin[0],
                         jj.mean() + self.origin[1],
                         kk.mean() + self.origin[2]])
        return mean @ self.ijk_to_ras[:3, :3].T + self.ijk_to_ras[:3, 3]


def build_field(volume: np.ndarray, label: int, name: str,
                ijk_to_ras: np.ndarray,
                ct: Optional[np.ndarray] = None) -> VertebraField:
    """Crop one vertebra out of the ground truth and build its distance field."""
    from scipy import ndimage                                 # noqa: PLC0415

    spacing = spacing_mm(ijk_to_ras)
    margin = int(np.ceil(SDF_MARGIN_MM / float(spacing.min())))
    box = label_bounding_box(volume, label, margin)
    if box is None:
        raise ValueError("label %d (%s) has no voxels" % (label, name))
    (i0, j0, k0), (i1, j1, k1) = box
    mask = np.asarray(volume[k0:k1, j0:j1, i0:i1]) == label
    # `sampling` is in ARRAY order, which is [k, j, i] -- the reverse of the
    # spacing vector. Passing it the right way round is what makes the distances
    # millimetres; the wrong way round they are still finite and still ordered.
    sampling = spacing[::-1]
    sdf = (ndimage.distance_transform_edt(~mask, sampling=sampling)
           - ndimage.distance_transform_edt(mask, sampling=sampling))
    hu = None
    if ct is not None:
        hu = np.asarray(ct[k0:k1, j0:j1, i0:i1]).astype(np.float32)
    return VertebraField(label, name, np.array([i0, j0, k0]), mask, sdf, hu,
                         ijk_to_ras)


# ---------------------------------------------------------------------------
# Which vertebra is this screw in?
# ---------------------------------------------------------------------------

def vertebra_labels(segmentation: segmentation_io.Segmentation) -> Dict[int, str]:
    """``{label value: name}`` for the segments that are vertebrae."""
    return {segment.label: segment.name for segment in segmentation.segments
            if VERTEBRA_NAME.match(segment.name or "")}


def assign_level(volume: np.ndarray, ijk_to_ras: np.ndarray,
                 labels: Dict[int, str], point: np.ndarray,
                 radius_mm: float = LANDMARK_BALL_MM) -> Dict[str, Any]:
    """Which vertebra a landmark is in, by voting the labels around it.

    The landmark, not the name. Both sides of this comparison label their levels
    and neither label is evidence: the plan's comes from the level the operator
    picked in the wizard's step 2 and the ground truth's from TotalSegmentator's
    own vertebra counting, so an off-by-one at either end -- a miscount by a
    person, a miscount by a network -- would put a screw's breach and fill against
    the vertebra above or below it while every number still looked reasonable.
    The isthmus landmark was placed by hand inside the pedicle being
    instrumented, so where it lands is a fact about this screw.

    A ball rather than the single voxel under the point: on the saved runs one
    isthmus landmark sits one voxel outside the label (a narrow pedicle, a 0.49 mm
    grid), and a point probe reports that screw as belonging to no vertebra at
    all. The margin is measured against the other VERTEBRA votes rather than
    against the ball, because a ball centred in a narrow pedicle is legitimately
    mostly outside bone -- 42% support on that same screw -- while two vertebrae
    splitting the vote is the failure that matters.
    """
    matrix = np.asarray(ijk_to_ras, dtype=float)
    spacing = spacing_mm(matrix)
    index = (np.append(np.asarray(point, dtype=float), 1.0)
             @ np.linalg.inv(matrix).T)[:3]
    reach = np.ceil(float(radius_mm) / spacing).astype(np.int64)
    shape = np.array(volume.shape[::-1], dtype=np.int64)      # [ni, nj, nk]
    low = np.maximum(np.floor(index - reach).astype(np.int64), 0)
    high = np.minimum(np.ceil(index + reach).astype(np.int64) + 1, shape)
    if np.any(high <= low):
        return {"label": None, "name": "", "support": 0.0, "margin": 0.0,
                "voxels": 0, "note": "landmark is outside the ground-truth volume"}

    block = np.asarray(volume[low[2]:high[2], low[1]:high[1], low[0]:high[0]])
    kk, jj, ii = np.mgrid[low[2]:high[2], low[1]:high[1], low[0]:high[0]]
    offset = np.stack([(ii - index[0]) * spacing[0],
                       (jj - index[1]) * spacing[1],
                       (kk - index[2]) * spacing[2]], axis=-1)
    ball = np.linalg.norm(offset, axis=-1) <= float(radius_mm)
    values = block[ball]
    total = int(ball.sum())

    counts = {int(value): int((values == value).sum())
              for value in np.unique(values) if int(value) in labels}
    if not counts:
        return {"label": None, "name": "", "support": 0.0, "margin": 0.0,
                "voxels": 0,
                "note": "no vertebra label within %.1f mm of the landmark"
                        % radius_mm}
    best = max(counts, key=counts.get)
    voted = float(sum(counts.values()))
    result = {
        "label": best,
        "name": labels[best],
        "support": counts[best] / float(max(total, 1)),
        "margin": counts[best] / voted,
        "voxels": counts[best],
        "note": "",
    }
    if counts[best] < LANDMARK_MIN_VOXELS:
        result["note"] = ("only %d voxel(s) of %s within %.1f mm"
                          % (counts[best], labels[best], radius_mm))
    elif result["margin"] < LANDMARK_MIN_MARGIN:
        runners = sorted(counts.items(), key=lambda kv: -kv[1])[1:3]
        result["note"] = ("ambiguous: %s holds %.0f%% of the vertebra votes, "
                          "against %s"
                          % (labels[best], 100.0 * result["margin"],
                             ", ".join("%s %.0f%%" % (labels[label],
                                                      100.0 * count / voted)
                                       for label, count in runners)))
    return result


def nearest_anterior_landmark(anterior: Sequence[Tuple[np.ndarray, str]],
                              isthmus: np.ndarray) -> Optional[np.ndarray]:
    """The level's anterior landmark: the ``T`` triple this isthmus belongs to.

    ``T`` is three points per level in placement order, so the anterior point of
    a level is simply the nearest of them to the isthmus -- the next level's is a
    whole vertebra away.
    """
    if not anterior:
        return None
    distances = [float(np.linalg.norm(point - isthmus)) for point, _ in anterior]
    return anterior[int(np.argmin(distances))][0]


# ---------------------------------------------------------------------------
# One screw
# ---------------------------------------------------------------------------

def axis_basis(direction: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Two unit vectors spanning the plane perpendicular to ``direction``."""
    arbitrary = np.array([1.0, 0.0, 0.0])
    if abs(float(arbitrary @ direction)) > 0.9:
        arbitrary = np.array([0.0, 0.0, 1.0])
    first = np.cross(direction, arbitrary)
    first /= np.linalg.norm(first)
    return first, np.cross(direction, first)


def trajectory_angles(direction: np.ndarray) -> Tuple[float, float]:
    """``(TPA, SPA)`` in degrees for a unit axis in RAS, entry -> tip.

    TPA is the convergence of the axis in the axial plane and SPA its tilt out of
    it. Recomputed from the axis rather than read from the extension's grading
    table, which reports SPA as 0.0 whenever the landmarks were placed on one
    axial slice -- a property of the placement, not of the trajectory.
    """
    direction = np.asarray(direction, dtype=float)
    tpa = float(np.degrees(np.arctan2(abs(direction[0]), abs(direction[1]))))
    spa = float(np.degrees(np.arcsin(np.clip(direction[2], -1.0, 1.0))))
    return tpa, spa


#: Anatomic directions, as unit vectors in RAS given the screw's side. The pair
#: (medial, lateral) is the only one that depends on the side, and getting it
#: backwards inverts exactly the distinction the gate is built on.
def anatomic_directions(is_right_side: bool) -> Dict[str, np.ndarray]:
    medial = np.array([-1.0, 0.0, 0.0]) if is_right_side \
        else np.array([1.0, 0.0, 0.0])
    return {
        "medial": medial,
        "lateral": -medial,
        "anterior": np.array([0.0, 1.0, 0.0]),
        "posterior": np.array([0.0, -1.0, 0.0]),
        "superior": np.array([0.0, 0.0, 1.0]),
        "inferior": np.array([0.0, 0.0, -1.0]),
    }


def grade_for(breach_mm: Optional[float]) -> str:
    """Gertzbein-Robbins letter for a protrusion in millimetres."""
    if breach_mm is None:
        return ""
    for bound, letter in GRADE_BOUNDS:
        if breach_mm <= bound if letter == "A" else breach_mm < bound:
            return letter
    return GRADE_WORST


def _percentile(values: np.ndarray, share: float) -> Optional[float]:
    return float(np.percentile(values, share)) if values.size else None


def _axis_exit_mm(field: VertebraField, origin: np.ndarray, direction: np.ndarray,
                  start_mm: float, limit_mm: float = AXIS_PROBE_LIMIT_MM
                  ) -> Optional[float]:
    """Distance from ``origin`` at which the axis leaves the label, going forward.

    Walked from ``start_mm`` -- the isthmus, which is inside by construction --
    rather than from the entry, so a gap in the label near the posterior cortex
    cannot be mistaken for the anterior wall. Returns None if the axis is still
    inside at ``limit_mm``.
    """
    steps = np.arange(float(start_mm), float(limit_mm) + 1e-9, AXIS_PROBE_STEP_MM)
    if steps.size == 0:
        return None
    values = field.distance(origin[None, :] + steps[:, None] * direction[None, :])
    outside = values >= 0.0
    if not outside.any():
        return None
    return float(steps[int(np.argmax(outside))])


def cross_section_widths(field: VertebraField, entry: np.ndarray,
                         direction: np.ndarray, first: np.ndarray,
                         second: np.ndarray, window: Tuple[float, float]
                         ) -> Dict[str, Any]:
    """Pedicle width across ``window``, two ways, plus where the narrowest is.

    ``caliper`` is the minimum caliper width of the label's cross-section
    perpendicular to the trajectory -- restricted to the piece the screw axis is
    in, so a rib head lying in the same plane is not measured as pedicle. It is
    the anatomic pedicle width, and the quantity the 70-80% fill target refers to.

    ``chord`` is the narrowest line through the AXIS in that same section. It
    cannot be inflated by a lump the section catches elsewhere, and it is what the
    screw itself has to pass through; on the saved runs the two agree to about a
    millimetre. Both are reported because neither alone is safe: the caliper
    over-reads when the plane catches a neighbour, and the chord under-reads when
    the screw sits off-centre.
    """
    from scipy import ndimage                                 # noqa: PLC0415

    grid = np.arange(-SECTION_RADIUS_MM, SECTION_RADIUS_MM + 1e-9, SECTION_STEP_MM)
    gx, gy = np.meshgrid(grid, grid, indexing="ij")
    centre_index = int(len(grid) // 2)
    angles = np.linspace(0.0, np.pi, SECTION_DIRECTIONS, endpoint=False)
    cos_a, sin_a = np.cos(angles), np.sin(angles)
    ray = np.arange(0.0, SECTION_RADIUS_MM + 1e-9, SECTION_STEP_MM)
    ray_angles = np.linspace(0.0, 2.0 * np.pi, SECTION_DIRECTIONS, endpoint=False)

    best_caliper: Optional[Tuple[float, float, float]] = None
    best_chord: Optional[Tuple[float, float]] = None
    used = 0
    total = 0
    for offset in np.arange(window[0], window[1] + 1e-9, SECTION_ALONG_STEP_MM):
        total += 1
        centre = entry + offset * direction
        points = (centre[None, None, :] + gx[..., None] * first
                  + gy[..., None] * second)
        inside = field.distance(points.reshape(-1, 3)).reshape(gx.shape) < 0.0
        pieces, _count = ndimage.label(inside)
        piece = int(pieces[centre_index, centre_index])
        if piece == 0:
            continue                       # the axis is outside the bone here
        used += 1
        component = pieces == piece
        xs, ys = gx[component], gy[component]
        projection = np.outer(cos_a, xs) + np.outer(sin_a, ys)
        # One sample step added back: the extent of a set of SAMPLES is a step
        # short of the extent of the region they cover.
        width = float((projection.max(axis=1)
                       - projection.min(axis=1)).min()) + SECTION_STEP_MM
        area = float(component.sum()) * SECTION_STEP_MM * SECTION_STEP_MM
        if best_caliper is None or width < best_caliper[0]:
            best_caliper = (width, float(offset), area)

        directions = (np.cos(ray_angles)[:, None] * first
                      + np.sin(ray_angles)[:, None] * second)
        along = (centre[None, None, :]
                 + ray[None, :, None] * directions[:, None, :])
        values = field.distance(along.reshape(-1, 3)).reshape(
            SECTION_DIRECTIONS, ray.size)
        outside = values >= 0.0
        reach = np.where(outside.any(axis=1), ray[outside.argmax(axis=1)],
                         ray[-1])
        chord = reach + np.roll(reach, SECTION_DIRECTIONS // 2)
        span = float(chord.min())
        if best_chord is None or span < best_chord[0]:
            best_chord = (span, float(offset))

    return {
        "caliper_mm": best_caliper[0] if best_caliper else None,
        "caliper_at_mm": best_caliper[1] if best_caliper else None,
        "section_area_mm2": best_caliper[2] if best_caliper else None,
        "chord_mm": best_chord[0] if best_chord else None,
        "sections_used": used,
        "sections_total": total,
    }


def screw_metrics(field: VertebraField, entry: np.ndarray, tip: np.ndarray,
                  diameter_mm: float, isthmus: np.ndarray,
                  with_density: bool = True) -> Dict[str, Any]:
    """Every per-screw measure, given the vertebra it is meant to be in."""
    entry = np.asarray(entry, dtype=float)
    tip = np.asarray(tip, dtype=float)
    length = float(np.linalg.norm(tip - entry))
    if length <= 0:
        raise ValueError("the trajectory has zero length")
    direction = (tip - entry) / length
    radius = float(diameter_mm) / 2.0
    first, second = axis_basis(direction)
    isthmus_offset = float((np.asarray(isthmus, dtype=float) - entry) @ direction)

    row: Dict[str, Any] = {
        "diameter_mm": float(diameter_mm),
        "length_mm": length,
        "isthmus_offset_mm": isthmus_offset,
        "entry_on_surface_mm": float(abs(field.distance(entry[None, :])[0])),
        "entry_distance_mm": float(field.distance(entry[None, :])[0]),
    }
    row["tpa_deg"], row["spa_deg"] = trajectory_angles(direction)

    # -- the lateral surface, sampled uniformly in (axial, angle) --------
    stations = np.arange(0.0, length + 1e-9, AXIAL_STEP_MM)
    around = np.linspace(0.0, 2.0 * np.pi, ANGULAR_SAMPLES, endpoint=False)
    radial = (np.cos(around)[:, None] * first + np.sin(around)[:, None] * second)
    wall = (entry[None, None, :] + stations[:, None, None] * direction
            + radius * radial[None, :, :])
    wall_flat = wall.reshape(-1, 3)
    wall_distance = field.distance(wall_flat).reshape(stations.size,
                                                      ANGULAR_SAMPLES)

    # The tip end cap belongs to the breach measure -- a screw out the front of
    # the body protrudes through it -- while the entry cap sits ON the cortex by
    # construction and is not a breach anywhere. Neither belongs to the contact
    # area (guide §1.5: they are cut planes, not bone interface).
    cap_radius = np.linspace(0.0, radius, 4)[1:]
    cap = (tip[None, None, :] + cap_radius[:, None, None] * radial[None, :, :])
    cap_distance = field.distance(cap.reshape(-1, 3))

    # -- the graded span -------------------------------------------------
    # From the start of the pedicle window to the tip. Both ends of that are
    # deliberate.
    #
    # It does not start at the entry, because the screw crosses the posterior
    # cortex there BY DESIGN -- the planner puts the entry point on the bone
    # surface (`Helper.probeVolume`) -- so the cylinder wall around it is
    # necessarily half outside: +0.9 to +2.4 mm at 0 mm on the reference runs.
    # Nor does it stop at the isthmus: a breach through the anterior pedicle or
    # out the front of the body is exactly what a grade is for.
    #
    # The proximal stretch is also where the ground truth is least able to
    # answer the question. A whole-vertebra label has no boundary between the
    # lamina, the facet and the transverse process, and the screw threads
    # between them: on the reference runs two of eight "breaches" sit 16 mm
    # posterior to the isthmus, in that traverse, and both vanish inside the
    # pedicle itself. Gertzbein-Robbins grades the PEDICLE, so the span is the
    # pedicle and everything in front of it.
    #
    # What is excluded is reported (`breach_proximal_mm`) rather than dropped,
    # and `graded_from_mm` says where the span begins -- so a badly placed
    # isthmus landmark, which is the one thing that could move it, is visible.
    window = (max(0.0, isthmus_offset - ISTHMUS_HALF_WINDOW_MM),
              min(length, isthmus_offset + ISTHMUS_HALF_WINDOW_MM))
    graded_from = min(max(float(radius), window[0]), length)
    graded = stations >= graded_from
    if not graded.any():                       # a landmark past the screw's tip
        graded = stations >= float(radius)
        graded_from = float(radius)
    if not graded.any():                       # a screw shorter than its radius
        graded = np.ones(stations.shape, dtype=bool)
        graded_from = 0.0
    in_window = (stations >= window[0]) & (stations <= window[1])
    row["graded_from_mm"] = graded_from

    # -- Gertzbein-Robbins ------------------------------------------------
    per_station = wall_distance.max(axis=1)
    cap_worst = float(cap_distance.max())
    breach = float(max(per_station[graded].max(), cap_worst))
    worst = int(np.argmax(np.where(graded, per_station, -np.inf)))
    # A tie goes to the CAP, and a tie is the normal case rather than a fluke:
    # when a screw is driven out the front of the body its wall and its tip cap
    # protrude by the same amount, because the wall's last station IS the cap's
    # outer ring. "Out the end" is the meaningful description of that.
    through_cap = cap_worst >= per_station[worst]
    row["breach_mm"] = breach
    row["grade"] = grade_for(breach)
    row["breach_offset_mm"] = length if through_cap else float(stations[worst])
    row["breach_with_entry_mm"] = float(max(per_station.max(), cap_worst))
    proximal = ~graded
    row["breach_proximal_mm"] = (float(per_station[proximal].max())
                                 if proximal.any() else None)
    row["breach_isthmus_mm"] = (float(wall_distance[in_window].max())
                                if in_window.any() else None)

    # -- direction of the worst point, and the per-direction clearances ---
    is_right = bool(entry[0] > field.centroid[0])
    row["side"] = "right" if is_right else "left"
    directions = anatomic_directions(is_right)
    # The outward direction AT the worst point, taken from the distance field's
    # own GRADIENT -- the bone's true outward normal there -- rather than from
    # the screw's geometry. The radius through the point is a fair approximation
    # on a flat wall and a poor one at a corner, and it is useless on the tip
    # cap, where it points sideways while the screw is going forwards.
    #
    # Then, for a WALL point, the component along the screw is projected out. A
    # cylinder's SIDE can only leave through a wall -- medial, lateral, superior
    # or inferior -- and the axial part of the normal says how the surface tilts
    # along the screw, not which wall was crossed. Without the projection the
    # anterolateral corner one real screw exits through is named "anterior",
    # which is true of the bone and useless to a surgeon. A TIP CAP breach keeps
    # the axis, because there the screw really is out the front.
    if through_cap:
        worst_point = tip + radius * radial[int(np.argmax(cap_distance.reshape(
            cap_radius.size, ANGULAR_SAMPLES)[-1]))]
        fallback = direction
    else:
        worst_point = wall[worst, int(np.argmax(wall_distance[worst]))]
        fallback = radial[int(np.argmax(wall_distance[worst]))]
    step = float(np.min(field.spacing))
    gradient = np.array([
        float(field.distance(worst_point + step * axis)[0]
              - field.distance(worst_point - step * axis)[0])
        for axis in np.eye(3)])
    norm = float(np.linalg.norm(gradient))
    outward = gradient / norm if norm > 1e-9 else fallback
    if not through_cap:
        outward = outward - float(outward @ direction) * direction
        norm = float(np.linalg.norm(outward))
        outward = outward / norm if norm > 1e-9 else fallback
    row["breach_direction"] = max(
        directions, key=lambda name: float(outward @ directions[name]))

    # Only the four WALL directions get a clearance. A cylinder's outward
    # normals are perpendicular to its axis and the axis is mostly anterior, so
    # no wall point ever faces anteriorly or posteriorly -- those columns would
    # be structurally blank, and anterior containment is what tip_to_cortex_mm
    # measures instead.
    graded_distance = wall_distance[graded]
    for name in WALL_DIRECTIONS:
        facing = (radial @ directions[name]) >= DIRECTION_CONE_COS
        if not facing.any():
            continue
        row["%s_clearance_mm" % name] = -float(graded_distance[:, facing].max())
    row["min_clearance_mm"] = -breach

    # -- containment, over the screw's own volume ------------------------
    shells = (np.arange(RADIAL_SHELLS) + 0.5) / float(RADIAL_SHELLS) * radius
    weights = np.repeat(shells, ANGULAR_SAMPLES)             # area weighting
    body = (entry[None, None, None, :]
            + stations[:, None, None, None] * direction
            + shells[None, :, None, None] * radial[None, None, :, :])
    body_distance = field.distance(body.reshape(-1, 3)).reshape(
        stations.size, RADIAL_SHELLS * ANGULAR_SAMPLES)
    inside = (body_distance < 0.0).astype(float)
    row["containment_pct"] = 100.0 * float((inside * weights).sum()
                                           / (np.ones_like(inside)
                                              * weights).sum())

    # -- depth and the anterior cortex -----------------------------------
    exit_mm = _axis_exit_mm(field, entry, direction,
                            max(isthmus_offset, AXIS_PROBE_STEP_MM))
    if exit_mm is not None:
        row["depth_along_trajectory_mm"] = exit_mm
        row["tip_to_cortex_mm"] = exit_mm - length
        row["length_of_depth_pct"] = 100.0 * length / exit_mm
    else:
        row["depth_along_trajectory_mm"] = None
        row["tip_to_cortex_mm"] = None
        row["length_of_depth_pct"] = None

    # -- pedicle width and fill ------------------------------------------
    section = cross_section_widths(field, entry, direction, first, second, window)
    row["pedicle_width_mm"] = section["caliper_mm"]
    row["pedicle_width_at_mm"] = section["caliper_at_mm"]
    row["pedicle_section_mm2"] = section["section_area_mm2"]
    row["channel_width_mm"] = section["chord_mm"]
    row["pedicle_sections"] = "%d/%d" % (section["sections_used"],
                                         section["sections_total"])
    width = section["caliper_mm"]
    if width and 0 < width <= PEDICLE_WIDTH_MAX_MM:
        row["fill_ratio_pct"] = 100.0 * float(diameter_mm) / width
        row["fill_vs_target_pct"] = row["fill_ratio_pct"] - FILL_TARGET_PCT
    else:
        row["fill_ratio_pct"] = None
        row["fill_vs_target_pct"] = None

    # -- density ----------------------------------------------------------
    if with_density and field.hu is not None:
        surface_hu = field.density(wall_flat)
        area = 2.0 * np.pi * radius * length
        row["surface_mm2"] = area
        row["contact_mm2_ge130"] = area * float(
            (surface_hu >= CANCELLOUS_MIN_HU).mean())
        row["contact_mm2_ge250"] = area * float(
            (surface_hu >= CORTICAL_MIN_HU).mean())
        row["surface_hu_p5"] = _percentile(surface_hu, 5)
        row["surface_hu_p50"] = _percentile(surface_hu, 50)
        row["surface_hu_p95"] = _percentile(surface_hu, 95)

        path_hu = field.density(body.reshape(-1, 3)).reshape(
            stations.size, RADIAL_SHELLS * ANGULAR_SAMPLES)
        spread = np.broadcast_to(weights, path_hu.shape)
        row["path_hu"] = _weighted_median(path_hu.ravel(), spread.ravel())
        thirds = np.array_split(np.arange(stations.size), 3)
        for name, part in zip(("entry", "mid", "tip"), thirds):
            if part.size:
                row["path_hu_%s" % name] = _weighted_median(
                    path_hu[part].ravel(), spread[part].ravel())
    return row


def _weighted_median(values: np.ndarray, weights: np.ndarray) -> Optional[float]:
    """Median of ``values`` weighted by ``weights``.

    The median rather than the mean, for the guide's reason: a few bright
    cortical voxels otherwise dominate a path average. Weighted because the
    samples are on radial shells, and an unweighted median over them would count
    the screw's core as heavily as its wall.
    """
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if values.size == 0 or weights.sum() <= 0:
        return None
    order = np.argsort(values)
    values, weights = values[order], weights[order]
    cumulative = np.cumsum(weights)
    return float(values[int(np.searchsorted(cumulative,
                                            0.5 * cumulative[-1]))])


def trabecular_hu(field: VertebraField, isthmus_points: Sequence[np.ndarray]
                  ) -> Dict[str, Any]:
    """Median HU inside the vertebral body, cortex excluded (guide §2.9).

    The ROI is the label eroded by ``TRABECULAR_EROSION_MM`` and cut back to what
    is anterior of the level's isthmus landmarks. The erosion is what removes the
    cortical shell; the cut is what removes the lamina and the spinous process,
    which are bone but are not what an osteoporosis surrogate is taken in. The
    cut is an approximation -- the isthmus sits at roughly the posterior wall of
    the body -- and is reported as one, which is why the voxel count travels with
    the number.
    """
    from scipy import ndimage                                 # noqa: PLC0415

    if field.hu is None:
        return {"hu": None, "voxels": 0, "note": "no CT"}
    steps = np.maximum(np.round(TRABECULAR_EROSION_MM / field.spacing), 1
                       ).astype(int)
    # Anisotropic voxels: each axis is eroded by the number of voxels that is
    # TRABECULAR_EROSION_MM along THAT axis, rather than by a fixed number of
    # isotropic passes -- these volumes are 0.49 x 0.49 x 1.0 mm, so a uniform
    # kernel would cut twice as deep in plane as through it, and the ROI would
    # keep cortex on the endplates while losing body in the slice.
    eroded = field.mask
    for axis, count in enumerate(steps[::-1]):                # array order k,j,i
        if count <= 0:
            continue
        shape = [1, 1, 1]
        shape[axis] = 2 * int(count) + 1
        eroded = ndimage.binary_erosion(eroded, structure=np.ones(shape, bool))
    if not eroded.any():
        return {"hu": None, "voxels": 0,
                "note": "the label vanishes under a %.0f mm erosion"
                        % TRABECULAR_EROSION_MM}

    if BODY_IS_ANTERIOR_OF_ISTHMUS and len(isthmus_points):
        cut = float(np.mean([float(p[1]) for p in isthmus_points]))
        kk, jj, ii = np.nonzero(eroded)
        index = np.stack([ii + field.origin[0], jj + field.origin[1],
                          kk + field.origin[2]], axis=1).astype(float)
        anterior = (index @ field.ijk_to_ras[:3, :3].T
                    + field.ijk_to_ras[:3, 3])[:, 1] > cut
        if anterior.sum() < 10:
            return {"hu": None, "voxels": int(anterior.sum()),
                    "note": "fewer than 10 body voxels anterior of the isthmus"}
        values = field.hu[kk[anterior], jj[anterior], ii[anterior]]
    else:
        values = field.hu[eroded]
    return {"hu": float(np.median(values)), "voxels": int(values.size),
            "note": ""}


def symmetry_deg(left: np.ndarray, right: np.ndarray) -> float:
    """Angle between the two axes of a level after mirroring one (guide §1.3)."""
    mirrored = np.asarray(right, dtype=float) * np.array([-1.0, 1.0, 1.0])
    return float(np.degrees(np.arccos(
        np.clip(float(np.asarray(left, dtype=float) @ mirrored), -1.0, 1.0))))


# ---------------------------------------------------------------------------
# One case
# ---------------------------------------------------------------------------

def find_case_files(case: Dict[str, str]) -> Dict[str, Any]:
    """The four files a case is scored from, or the reason it cannot be."""
    scene_dir = case["scene_dir"]
    dataset_dir = case.get("dataset_dir") or ""
    found: Dict[str, Any] = {
        "scene_mrml": os.path.join(scene_dir, "scene.mrml"),
        "truth": "", "dataset_ct": "", "scene_ct": "", "problems": []}
    if not os.path.isfile(found["scene_mrml"]):
        found["problems"].append("the run has no scene.mrml")
    if not dataset_dir or not os.path.isdir(dataset_dir):
        found["problems"].append(
            "no dataset folder for subject %r" % (case.get("subject") or ""))
        return found
    truth = os.path.join(dataset_dir, SEGMENTATION_NAME)
    if os.path.isfile(truth):
        found["truth"] = truth
    else:
        found["problems"].append("no %s in %s"
                                 % (SEGMENTATION_NAME, dataset_dir))
    volumes = [p for p in sorted(glob.glob(os.path.join(dataset_dir, "*.nrrd")))
               if not p.lower().endswith(".seg.nrrd")]
    preferred = os.path.join(dataset_dir, "%s.nrrd" % (case.get("subject") or ""))
    if preferred in volumes:
        found["dataset_ct"] = preferred
    elif len(volumes) == 1:
        found["dataset_ct"] = volumes[0]
    elif volumes:
        found["dataset_ct"] = volumes[0]
        found["problems"].append(
            "%d volumes in %s; using %s"
            % (len(volumes), dataset_dir, os.path.basename(volumes[0])))
    return found


def case_is_scorable(case: Dict[str, str]) -> bool:
    found = find_case_files(case)
    return bool(found["truth"]) and os.path.isfile(found["scene_mrml"])


def _round(value: Optional[float], digits: int = 3) -> Optional[float]:
    return None if value is None else round(float(value), digits)


def analyse_case(case: Dict[str, str], with_density: bool = True) -> Dict[str, Any]:
    """Every screw of one run, scored against the case's ground truth."""
    label = case["subject"] or case["run"]
    found = find_case_files(case)
    notes: List[str] = list(found["problems"])
    if not found["truth"]:
        raise ValueError("; ".join(notes) or "no ground-truth segmentation")

    plan = read_plan(case["scene_dir"])
    landmarks = read_landmarks(case["scene_dir"])
    if not plan["lines"]:
        raise ValueError("the saved scene holds no screw trajectories "
                         "(w_<N>_D<d>_L)")

    segmentation = segmentation_io.Segmentation(found["truth"])
    try:
        if segmentation.dimension != 3:
            notes.append("the ground truth has %d layers; only layer 0 is read"
                         % segmentation.layers)
        volume = segmentation.layer_volume(0)
        matrix = segmentation.ijk_to_ras
        labels = vertebra_labels(segmentation)
        if not labels:
            raise ValueError("the ground truth names no vertebra segments "
                             "(expected e.g. 'T11 vertebra')")

        scene_ct, matched_notes = scene_volume_matching(
            case["scene_dir"], segmentation._sizes, matrix)   # noqa: SLF001
        notes.extend(matched_notes)
        if scene_ct is None:
            raise ValueError(
                "no volume in the run's scene shares the ground truth's voxel "
                "grid, so the plan cannot be placed in the ground truth's frame")
        _sizes, scene_matrix = _grid_of(scene_ct)
        bridge = frame_bridge(scene_matrix, matrix)

        # The CT is read once and cropped per vertebra, then released: a case's
        # volume is 258-429 MB decompressed and there is no reason to hold it
        # while the screws are measured.
        ct = None
        if with_density and found["dataset_ct"]:
            try:
                ct, ct_matrix, _fields = volume_io.read_nrrd(found["dataset_ct"])
                if not np.allclose(ct_matrix, matrix, atol=1e-4):
                    notes.append(
                        "%s is not on the ground truth's grid; density columns "
                        "are left blank"
                        % os.path.basename(found["dataset_ct"]))
                    ct = None
            except Exception as exc:
                notes.append("could not read %s (%s); density columns are blank"
                             % (os.path.basename(found["dataset_ct"]), exc))
                ct = None
        elif with_density:
            notes.append("no CT beside the ground truth; density columns are blank")

        screws = _screw_rows(case, label, plan, landmarks, volume, matrix, labels,
                             bridge, ct, notes, with_density)
        del ct
    finally:
        segmentation.close()

    return {
        "rows": screws["rows"],
        "levels": screws["levels"],
        "notes": notes,
        "files": {"truth": found["truth"], "dataset_ct": found["dataset_ct"],
                  "scene_volume": os.path.basename(scene_ct or ""),
                  "bridge_mm": [_round(v, 4) for v in bridge[:3, 3]]},
    }


def _screw_rows(case, label, plan, landmarks, volume, matrix, labels, bridge,
                ct, notes, with_density) -> Dict[str, Any]:
    fields: Dict[int, VertebraField] = {}
    rows: List[Dict[str, Any]] = []
    axes: Dict[Tuple[str, str], np.ndarray] = {}
    per_level: Dict[str, Dict[str, Any]] = {}

    model_axes = {}
    for site, path in plan["models"].items():
        try:
            points = geometry_io.lps_to_ras(geometry_io.read_vtk_points(path))
            model_axes[site] = geometry_io.rod_axis_endpoints(points)
        except Exception as exc:
            notes.append("could not read the %s cylinder (%s)" % (site, exc))

    for index in sorted(plan["lines"]):
        line = plan["lines"][index]
        row: Dict[str, Any] = {
            "case": label, "run": case["run"], "screw": "w_%d" % index,
            "site": "", "diameter_mm": _round(line["diameter_mm"], 2),
            "status": "",
        }
        try:
            entry_scene, tip_scene = line_endpoints(line["file"])
        except Exception as exc:
            row["status"] = "unreadable trajectory: %s" % exc
            rows.append(row)
            continue

        # The site name comes from the cylinder built on this line, matched by
        # GEOMETRY: `p2pCyl(PB, PT, ...)` uses the line's own two points, so the
        # right model's axis coincides with it exactly. Pairing on the creation
        # order in scene.mrml would be right today and silent the day a screw is
        # rebuilt.
        best_site, best_gap = "", None
        for site, (low, high) in model_axes.items():
            gap = min(float(np.linalg.norm(low - entry_scene)
                            + np.linalg.norm(high - tip_scene)),
                      float(np.linalg.norm(high - entry_scene)
                            + np.linalg.norm(low - tip_scene)))
            if best_gap is None or gap < best_gap:
                best_site, best_gap = site, gap
        if best_gap is not None and best_gap <= MODEL_AXIS_LIMIT_MM:
            row["site"] = best_site
            row["model_axis_gap_mm"] = _round(best_gap, 4)
        elif best_gap is not None:
            row["model_axis_gap_mm"] = _round(best_gap, 4)
            notes.append("w_%d has no screw cylinder within %.1f mm (nearest %s, "
                         "%.2f mm); its site name is taken from the landmark"
                         % (index, MODEL_AXIS_LIMIT_MM, best_site, best_gap))

        landmark = landmarks["isthmus"].get(index)
        if landmark is None:
            row["status"] = "no Isthmus-%d landmark, so no vertebra can be " \
                            "identified" % index
            rows.append(row)
            continue
        isthmus_scene, planned_site = landmark
        row["site"] = row["site"] or planned_site
        row["planned_level"] = _level_of(planned_site)

        entry = apply_transform(bridge, entry_scene)[0]
        tip = apply_transform(bridge, tip_scene)[0]
        isthmus = apply_transform(bridge, isthmus_scene)[0]

        vote = assign_level(volume, matrix, labels, isthmus)
        row["level"] = vote["name"]
        row["level_support_pct"] = _round(100.0 * vote["support"], 1)
        row["level_margin_pct"] = _round(100.0 * vote["margin"], 1)
        if vote["note"]:
            notes.append("w_%d: %s" % (index, vote["note"]))
            row["level_note"] = vote["note"]
        if vote["label"] is None:
            row["status"] = vote["note"] or "the isthmus landmark is in no vertebra"
            rows.append(row)
            continue

        anterior = nearest_anterior_landmark(landmarks["anterior"], isthmus_scene)
        if anterior is not None:
            confirm = assign_level(volume, matrix, labels,
                                   apply_transform(bridge, anterior)[0])
            row["level_from_anterior"] = confirm["name"]
            row["level_confirmed"] = (confirm["label"] == vote["label"])
            if confirm["label"] is not None and confirm["label"] != vote["label"]:
                notes.append("w_%d: the isthmus landmark says %s but the level's "
                             "anterior landmark says %s -- scored against the "
                             "isthmus, which is this screw's own"
                             % (index, vote["name"], confirm["name"]))
        row["name_agrees"] = _levels_match(planned_site, vote["name"])

        if vote["label"] not in fields:
            fields[vote["label"]] = build_field(volume, vote["label"],
                                                vote["name"], matrix, ct)
        field = fields[vote["label"]]

        try:
            measured = screw_metrics(field, entry, tip, line["diameter_mm"],
                                     isthmus, with_density=with_density)
        except Exception as exc:
            row["status"] = "could not be measured: %s" % exc
            logger.warning("Pedicle screw w_%d of %s failed", index, label,
                           exc_info=True)
            rows.append(row)
            continue

        for key, value in measured.items():
            row[key] = _round(value) if isinstance(value, float) else value
        row["diameter_mm"] = _round(line["diameter_mm"], 2)
        row["diameter_from"] = line["diameter_from"]

        if measured["entry_on_surface_mm"] > ENTRY_SURFACE_LIMIT_MM:
            # The planner puts the entry ON the bone. If it is not there, either
            # the frame bridge is wrong or this run was driven from a different
            # patient's data -- and both produce numbers that look fine. Refuse
            # them rather than publish them.
            row["status"] = ("the planned entry lands %.1f mm from the vertebra "
                             "surface (limit %.1f), so this screw is not scored"
                             % (measured["entry_on_surface_mm"],
                                ENTRY_SURFACE_LIMIT_MM))
            for key in ("breach_mm", "grade", "containment_pct",
                        "fill_ratio_pct", "min_clearance_mm"):
                row[key] = None
            rows.append(row)
            continue

        row["gate_pass"] = _gate(row)
        rows.append(row)

        if row.get("level"):
            axes[(row["level"], row["side"])] = (tip - entry) / np.linalg.norm(
                tip - entry)
            bucket = per_level.setdefault(row["level"], {"isthmus": [],
                                                         "label": vote["label"]})
            bucket["isthmus"].append(isthmus)

    level_rows = _level_rows(label, case["run"], rows, axes, per_level, fields,
                             notes)
    return {"rows": rows, "levels": level_rows}


def _level_of(site: str) -> str:
    """``T11_L`` -> ``T11``. The plan's own claim about the level, kept as text."""
    return (site or "").rsplit("_", 1)[0]


def _levels_match(site: str, truth_name: str) -> Optional[bool]:
    """Does the plan's level name agree with the ground truth's?

    Reported, never used to decide anything. A disagreement means somebody
    counted vertebrae differently -- the operator in the wizard, or
    TotalSegmentator in the segmentation -- and which of them is right is not
    something this analysis can settle. What it CAN do is score against the
    landmark and say the two names differed.
    """
    planned = _level_of(site)
    match = VERTEBRA_NAME.match(truth_name or "")
    if not planned or not match:
        return None
    return planned.upper() == "%s%s" % (match.group(1).upper(), match.group(2))


def _gate(row: Dict[str, Any]) -> Optional[bool]:
    """The safety gate of guide §4: grade, medial wall, anterior cortex.

    Pass/fail, and deliberately not folded into any score. A screw with excellent
    purchase and a 3 mm medial breach is a failed plan, not a good plan with a
    caveat, so the quality columns beside it are only meaningful once this is
    true.
    """
    grade = row.get("grade")
    if not grade:
        return None
    medial = row.get("medial_clearance_mm")
    tip = row.get("tip_to_cortex_mm")
    if medial is None:
        return None
    return bool(grade in ACCEPTABLE_GRADES
                and medial >= MEDIAL_CLEARANCE_MIN_MM
                and (tip is None or tip > 0.0))


def _level_rows(label, run, rows, axes, per_level, fields, notes
                ) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for level in sorted(per_level):
        bucket = per_level[level]
        members = [r for r in rows if r.get("level") == level
                   and r.get("grade")]
        entry: Dict[str, Any] = {
            "case": label, "run": run, "level": level,
            "screws": len(members),
            "worst_grade": max((r["grade"] for r in members), default=""),
            "worst_breach_mm": _round(max((r["breach_mm"] for r in members
                                           if r.get("breach_mm") is not None),
                                          default=None)),
            "min_clearance_mm": _round(min((r["min_clearance_mm"]
                                            for r in members
                                            if r.get("min_clearance_mm")
                                            is not None), default=None)),
        }
        left, right = axes.get((level, "left")), axes.get((level, "right"))
        entry["symmetry_deg"] = _round(symmetry_deg(left, right)) \
            if left is not None and right is not None else None
        field = fields.get(bucket["label"])
        if field is not None:
            trabecular = trabecular_hu(field, bucket["isthmus"])
            entry["trabecular_hu"] = _round(trabecular["hu"], 1)
            entry["trabecular_voxels"] = trabecular["voxels"]
            if trabecular["note"]:
                notes.append("%s: %s" % (level, trabecular["note"]))
                entry["note"] = trabecular["note"]
        out.append(entry)
    return out


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------

SCREW_COLUMNS = [
    "case", "screw", "site", "level", "name_agrees", "side",
    "diameter_mm", "length_mm",
    "grade", "breach_mm", "breach_direction", "breach_offset_mm",
    "min_clearance_mm", "medial_clearance_mm", "lateral_clearance_mm",
    "superior_clearance_mm", "inferior_clearance_mm",
    "tip_to_cortex_mm", "gate_pass",
    "containment_pct", "pedicle_width_mm", "channel_width_mm",
    "fill_ratio_pct", "fill_vs_target_pct",
    "depth_along_trajectory_mm", "length_of_depth_pct",
    "tpa_deg", "spa_deg",
    "path_hu", "path_hu_entry", "path_hu_mid", "path_hu_tip",
    "contact_mm2_ge130", "contact_mm2_ge250", "surface_mm2",
    "surface_hu_p5", "surface_hu_p50", "surface_hu_p95",
    "breach_isthmus_mm", "breach_proximal_mm", "breach_with_entry_mm",
    "graded_from_mm", "isthmus_offset_mm", "planned_level", "entry_distance_mm",
    "pedicle_width_at_mm", "pedicle_section_mm2",
    "pedicle_sections", "level_support_pct", "level_margin_pct",
    "level_from_anterior", "level_confirmed", "entry_on_surface_mm",
    "model_axis_gap_mm", "diameter_from", "status", "run",
]

LEVEL_COLUMNS = ["case", "level", "screws", "worst_grade", "worst_breach_mm",
                 "min_clearance_mm", "symmetry_deg", "trabecular_hu",
                 "trabecular_voxels", "note", "run"]

CASE_COLUMNS = ["case", "screws", "scored", "levels", "grade_A", "grade_B",
                "grade_C_plus", "acceptable_pct", "gate_passed",
                "worst_breach_mm", "min_clearance_mm", "min_medial_clearance_mm",
                "mean_containment_pct", "mean_fill_pct", "mean_path_hu",
                "levels_named_wrong", "scene_volume", "run"]

SUMMARY_COLUMNS = ["metric", "n", "mean", "sd", "min", "max", "note"]
GRADE_COLUMNS = ["grade", "screws", "share_pct", "meaning"]
DEFINITION_COLUMNS = ["term", "definition"]

PHASE_COLUMNS = (["case", "run", "t_total_s", "inside_steps_s"]
                 + ["%s_s" % phase for phase in PHASE_ORDER]
                 + ["unphased_s", "phase_residual_s"])


METHOD_DEFINITIONS = [
    ("what is measured against what",
     "The plan comes from the run's own Statistic/scene/ (one w_<N>_D<d>_L "
     "trajectory per screw, entry then tip, diameter on the node's "
     "ScrewDiameter attribute). The anatomy comes from "
     "Dataset/<case>/segmentation.seg.nrrd, in which every vertebra carries its "
     "own label. Every POSITIONAL number below is a distance to that label; "
     "every DENSITY number is HU from the case's CT."),
    ("why a segmentation is required at all",
     "Trabecular marrow in these vertebrae reads 0-100 HU while paraspinal "
     "muscle reads 40-60, so no HU threshold separates 'inside the vertebra' "
     "from 'outside it'. Two threshold-only containment tests were tried on this "
     "data and both failed: the minimum distance to dense bone is ~0 mm for "
     "every screw because the entry crosses cortex by design, and marching "
     "forward from the tip until HU < 130 fires immediately because the anterior "
     "body marrow is already below it."),
    ("the two frames, and the bridge between them",
     "The run loaded its CT centred (space origin = minus half the extent) while "
     "the dataset copy and its segmentation keep the scanner's origin. Same "
     "sizes, same direction cosines, different origin: the same image indexed the "
     "same way. Points therefore cross between the frames THROUGH the voxel "
     "index. The run's volume is identified by matching that grid, never by "
     "name -- baselineROI.nrrd sits in the same folder and is a 0.245 mm "
     "resample of the same data."),
    ("entry_on_surface_mm -- the check that the bridge is right",
     "The planner puts the entry point ON the bone surface (Helper.probeVolume), "
     "so how far the entry lands from the label's surface is an independent "
     "witness that the frame bridge, the case pairing and the LPS mirror are all "
     "right. It is 0.2-1.3 mm on the reference runs. A screw above "
     "%.0f mm is reported UNSCORED rather than scored wrongly."
     % ENTRY_SURFACE_LIMIT_MM),
    ("how a screw's vertebra is chosen",
     "By the surgeon's own isthmus landmark, never by name. The vertebra labels "
     "in a %.0f mm ball around Isthmus-<N> are voted; the winner must hold at "
     "least %.0f%% of the vertebra votes. The level's anterior landmark votes "
     "again as a cross-check (level_confirmed). The plan's own level name is "
     "reported beside it (name_agrees) and is never used -- a disagreement means "
     "the operator and TotalSegmentator counted vertebrae differently, which "
     "this analysis reports rather than resolves."
     % (LANDMARK_BALL_MM, 100 * LANDMARK_MIN_MARGIN)),
    ("the signed distance field",
     "EDT(outside) - EDT(inside) over the label, cropped to its bounding box "
     "plus %.0f mm and sampled trilinearly. Both halves are needed: the pair puts "
     "the zero level set on the voxel FACE, where the label's boundary is, while "
     "either half alone puts it at a voxel centre -- half a voxel out, which is a "
     "quarter of a Gertzbein-Robbins grade on this data."
     % SDF_MARGIN_MM),
    ("the graded span, and why it does not start at the entry",
     "Everything from the start of the pedicle window (isthmus - %.0f mm, and "
     "never nearer the entry than one screw radius) to the tip -- reported as "
     "graded_from_mm. It does not start at the entry because the screw crosses "
     "the posterior cortex there BY DESIGN: the planner puts the entry point on "
     "the bone surface, so the cylinder wall around it is necessarily half "
     "outside, +0.9 to +2.4 mm at 0 mm on the reference runs. That stretch is "
     "also where a whole-vertebra label can least answer the question -- it has "
     "no boundary between lamina, facet and transverse process, and the screw "
     "threads between them; two of eight apparent breaches on the reference "
     "runs sat 16 mm posterior to the isthmus, in that traverse, and both "
     "vanished inside the pedicle. Gertzbein-Robbins grades the PEDICLE. Nothing "
     "is hidden: breach_proximal_mm is the worst point in the excluded stretch "
     "and breach_with_entry_mm the unrestricted maximum."
     % ISTHMUS_HALF_WINDOW_MM),
    ("not computed: deviation from the pedicle axis",
     "Guide §2.11 needs the pedicle segmented apart from the vertebra. The only "
     "pedicle-shaped object available here is the channel around the screw, so "
     "the axis would be derived from the trajectory it is meant to judge. A "
     "circular number that looks like a measurement is worse than a blank."),
    ("not computed: facet violation, cortical vs cancellous contact",
     "Guide §2.10 needs the facet joint or the adjacent vertebra's articular "
     "process segmented separately; §2.8 needs the cortical shell segmented "
     "within the label. Neither is in this ground truth. contact_mm2_ge250 is "
     "the HU proxy for §2.8 and is labelled as one."),
]

SCREW_DEFINITIONS = [
    ("grade / breach_mm",
     "Gertzbein-Robbins: the largest distance any part of the screw protrudes "
     "beyond the vertebra's cortex, in mm, and its letter (A <= 0 < B < 2 <= C "
     "< 4 <= D < 6 <= E). Measured over the graded span of the cylinder wall "
     "plus the TIP end cap -- a screw out the front of the body protrudes "
     "through that cap. Report the millimetres as well as the letter: the "
     "letter discards information the number carries."),
    ("graded_from_mm / breach_proximal_mm / breach_with_entry_mm",
     "Where the graded span begins, in mm from the entry, and the worst "
     "protrusion in the stretch before it. The second column is what makes the "
     "first honest -- it is the entry and the posterior-element traverse, "
     "reported rather than dropped. A graded_from_mm far from the usual 12-17 mm "
     "means the isthmus landmark was placed unusually, which is the one thing "
     "that moves this boundary."),
    ("breach_direction",
     "Which wall the worst point is on -- where the screw crosses the cortex, "
     "or, for a contained screw, where it comes closest to it: "
     "medial / lateral / superior / inferior, or anterior for a breach through "
     "the TIP CAP. Severity is strongly direction-dependent -- medial >> "
     "inferior > lateral > superior -- so 1.3 mm medial is worth revising where "
     "the same 1.3 mm laterally usually is not. 'medial' is resolved against "
     "the vertebra's own centroid, so it follows the patient's midline and not "
     "the image's. The direction is the distance field's own gradient there -- "
     "the bone's outward normal -- with the component along the screw projected "
     "out, because a cylinder's side can only leave through a wall and the "
     "axial part of the normal describes how the surface tilts, not which wall "
     "was crossed."),
    ("breach_offset_mm",
     "How far along the screw, from the entry, the worst point is. It is what "
     "separates a wall breach in the pedicle from the entry funnel: a worst point "
     "at 1 mm is the cortex the screw is supposed to cross."),
    ("breach_isthmus_mm",
     "The same measure restricted to the extension's OWN graded window, "
     "+/-%.0f mm about the isthmus landmark. Unambiguously pedicle, and directly "
     "comparable with the module's Screw-Bone Contact table."
     % ISTHMUS_HALF_WINDOW_MM),
    ("diameter_mm / length_mm / diameter_from",
     "The implant, read from the trajectory line: the diameter off the node's "
     "ScrewDiameter attribute (diameter_from says whether it came from there or "
     "from the node name), the length as the distance between its two control "
     "points. Both drive pullout strength -- diameter with the larger effect, "
     "length the more linear one -- and both are only meaningful against the "
     "anatomy, which is what fill_ratio_pct and length_of_depth_pct are for. "
     "Note the planner rounds length DOWN to a multiple of 5 mm, matching real "
     "implant increments and discarding up to 4.99 mm of available depth."),
    ("min_clearance_mm / medial_clearance_mm / lateral_clearance_mm / "
     "superior_clearance_mm / inferior_clearance_mm",
     "The smallest distance from the screw's surface to the cortex, overall and "
     "per anatomic direction (each over the wall points within 60 degrees of that "
     "direction). Positive is margin; negative IS the breach in that direction. "
     "A screw can be Grade A and still have no tolerance for drill wander, which "
     "is what these columns say and the grade does not."),
    ("medial_clearance_mm",
     "Singled out because it is the wall that matters: below %.1f mm the screw is "
     "flagged even when it is contained, since a medial breach threatens cord and "
     "nerve root." % MEDIAL_CLEARANCE_MIN_MM),
    ("containment_pct",
     "The share of the screw's own cylindrical VOLUME inside the vertebra, "
     "sampled on radial shells weighted by radius so the samples are "
     "area-uniform. It complements the grade, which reports only the worst "
     "point. A screw whose last few millimetres are out the front reads high "
     "here and badly there, and both are true."),
    ("pedicle_width_mm / channel_width_mm / fill_ratio_pct",
     "Two measures of the same width, reported together because neither alone is "
     "safe. pedicle_width_mm is the minimum caliper of the label's cross-section "
     "perpendicular to the trajectory (restricted to the piece the axis is in) -- "
     "the anatomic pedicle width, and what the 70-80%% fill target refers to. "
     "channel_width_mm is the narrowest chord of that same section THROUGH the "
     "axis: it cannot be inflated by a lump the plane catches elsewhere, but it "
     "under-reads when the screw sits off-centre. fill_ratio_pct is "
     "diameter / pedicle_width_mm. They agree to about a millimetre on the "
     "reference runs; where they do not, distrust the caliper."),
    ("fill_vs_target_pct",
     "fill_ratio_pct minus %.0f%%. Negative wastes available bone; positive "
     "raises breach and pedicle-fracture risk. Above 100%% the screw is wider "
     "than the pedicle it is in, which is a finding and not a rounding error."
     % FILL_TARGET_PCT),
    ("depth_along_trajectory_mm / tip_to_cortex_mm / length_of_depth_pct",
     "How far the vertebra extends along the trajectory from the entry, how much "
     "of that is left in front of the tip, and the screw's length as a share of "
     "it. ~50-80%% is typical; negative tip_to_cortex_mm is anterior "
     "perforation. The walk starts at the isthmus, which is inside by "
     "construction, so a gap in the label near the entry cannot be mistaken for "
     "the anterior wall."),
    ("tpa_deg / spa_deg",
     "Transverse (axial convergence) and sagittal (cranio-caudal tilt) pedicle "
     "angles, recomputed from the trajectory. The extension's own table reports "
     "SPA as 0.0 whenever the landmarks were placed on one axial slice, which is "
     "a property of the placement rather than of the screw."),
    ("path_hu / path_hu_entry / path_hu_mid / path_hu_tip",
     "Median HU inside the cylindrical volume the screw will occupy -- not merely "
     "on its surface -- whole and in entry/middle/tip thirds. The best density "
     "proxy for grip: a screw threading a marrow gap and one fully embedded can "
     "produce the same SURFACE numbers, and the path median cannot be fooled that "
     "way. It is not a substitute for containment: a screw entirely outside the "
     "pedicle in dense cortex would score well."),
    ("contact_mm2_ge130 / contact_mm2_ge250 / surface_mm2",
     "Absolute area of the screw's lateral wall against bone in each density "
     "band, using the extension's own thresholds (130 cancellous, 250 cortical). "
     "The corrected form of its '%% Screw in ...' columns: a percentage penalises "
     "length, so extending a screw into soft anterior marrow lowers it even "
     "though the screw got stronger. End caps are excluded -- they are cut "
     "planes, not bone interface."),
    ("surface_hu_p5 / surface_hu_p50 / surface_hu_p95",
     "Percentiles of HU at the screw wall, which avoid the categorical jump "
     "between 129 and 131 HU. The low percentile matters most: it describes the "
     "weakest part of the interface."),
    ("gate_pass",
     "Grade A or B AND medial clearance >= %.1f mm AND the tip does not perforate "
     "the anterior cortex. Safety, kept apart from every quality column: a breach "
     "is never averaged into a score."
     % MEDIAL_CLEARANCE_MIN_MM),
    ("entry_distance_mm",
     "The signed distance from the planned entry to the label's surface, of "
     "which entry_on_surface_mm is the magnitude. Negative means the entry is "
     "just inside the cortex, which is where the planner aims it."),
    ("level / planned_level / name_agrees / level_support_pct / "
     "level_margin_pct / level_from_anterior / level_confirmed",
     "level is the vertebra the isthmus landmark is in -- what the screw is "
     "scored against. name_agrees says whether the plan's own site name (e.g. "
     "T11_L) names the same vertebra; 'NO' means the operator and "
     "TotalSegmentator counted differently and the plan's label is misleading, "
     "not that the measurement is. support is the winner's share of the whole "
     "ball (legitimately low in a narrow pedicle) and margin its share of the "
     "vertebra votes (which is the discriminating one)."),
    ("isthmus_offset_mm / pedicle_width_at_mm / pedicle_section_mm2 / "
     "pedicle_sections",
     "Where the surgeon's isthmus landmark sits along the screw, in mm from the "
     "entry (14-22 mm on the reference runs); where in the window the narrowest "
     "section actually was; that section's area; and how many of the sections "
     "across the window could be measured against how many were tried. A "
     "section is skipped when the axis is outside the bone there, so a count "
     "short of the total is itself a finding about the trajectory."),
    ("model_axis_gap_mm",
     "Distance between the trajectory line and the axis of the Screw_<site> "
     "cylinder paired with it. The cylinder is built from the line's own two "
     "points, so this is 0.000 mm when the pairing is right; it is what "
     "identifies each screw's site without trusting the order nodes were saved "
     "in."),
    ("side",
     "The patient's side, derived from the screw's entry relative to that "
     "vertebra's OWN centroid -- never from the site name. The planner's _L/_R "
     "suffix is the order the two isthmus landmarks of a level were placed "
     "(Helper.Pdata3 calls index 1 of each triple 'left' and index 2 'right', "
     "and nothing checks a coordinate), so on both reference runs every screw "
     "named _L is on the patient's RIGHT. Since medial and lateral are defined "
     "against the midline, taking the side from the name would invert exactly "
     "the distinction the safety gate rests on."),
    ("status", "Empty when the screw was scored. Otherwise why it was not."),
]

LEVEL_DEFINITIONS = [
    ("symmetry_deg",
     "Angle between the level's two trajectories after mirroring one across the "
     "sagittal plane. Small is a tidy construct that is easy to connect with a "
     "rod. Large is not wrong in itself -- anatomy is not always symmetric -- but "
     "is worth a look."),
    ("trabecular_hu",
     "Median HU inside the vertebral body with the cortex excluded: the label "
     "eroded by %.0f mm and cut back to what is anterior of the level's isthmus "
     "landmarks. Roughly [literature] >160 normal, 110-160 osteopenic, <110-120 "
     "osteoporotic and associated with screw loosening -- verify the cut-off "
     "against your own scanner. The anterior cut is an approximation (the "
     "isthmus sits at about the posterior wall of the body), which is why the "
     "voxel count travels with the number."
     % TRABECULAR_EROSION_MM),
    ("worst_grade / worst_breach_mm",
     "The level is as accurate as its worse screw, which is what a construct is "
     "judged on."),
]

CASE_DEFINITIONS = [
    ("acceptable_pct",
     "Share of the case's scored screws at Grade A or B -- what the literature "
     "reports as clinically acceptable. Reported beside gate_passed, which is "
     "stricter: it also requires the medial wall and the anterior cortex."),
    ("levels_named_wrong",
     "How many screws the plan named a different vertebra from the one their "
     "landmark is in. Not an error in the measurement; a mislabelled plan."),
    ("scene_volume",
     "Which volume in the run's scene was matched to the ground truth's voxel "
     "grid, and therefore what the frame bridge was built from."),
    ("scored / screws",
     "Scored is how many produced numbers. They differ exactly when a screw has "
     "a status, and a mean quoted against the larger count would overstate the "
     "sweep."),
]

PHASE_DEFINITIONS = [
    ("t0 .. t4",
     "The run's time split by the wizard's own pages: t0 load the CT, t1 the "
     "region of interest and the instrumented levels, t2 place the landmarks, "
     "t3 plan the screws (choose each site's diameter and drag its trajectory), "
     "t4 grade and finish. t3 is the phase to compare across conditions."),
    ("unphased_s",
     "Time in steps this map does not name. Named rather than dropped: a "
     "regenerated CLI package with different step ids would otherwise make the "
     "phases silently shrink while still summing to something plausible."),
    ("phase_residual_s",
     "inside_steps_s minus the phases and unphased_s. Non-zero means the timing "
     "report and the per-step timeline disagree, which is a finding, so it is "
     "never clamped."),
]


def definition_rows(pairs: Sequence[Tuple[str, str]]) -> List[Dict[str, str]]:
    return [{"term": term, "definition": text} for term, text in pairs]


def _stats(values: Sequence[Optional[float]]) -> Dict[str, Any]:
    numbers = [float(v) for v in values if isinstance(v, (int, float))]
    if not numbers:
        return {"n": 0, "mean": None, "sd": None, "min": None, "max": None}
    array = np.asarray(numbers, dtype=float)
    return {"n": len(numbers), "mean": _round(array.mean()),
            "sd": _round(array.std(ddof=1)) if array.size > 1 else 0.0,
            "min": _round(array.min()), "max": _round(array.max())}


def _scored(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [row for row in rows if row.get("grade")]


def case_rows(rows: Sequence[Dict[str, Any]], levels: Sequence[Dict[str, Any]],
              files: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for case in sorted({row["case"] for row in rows}):
        mine = [row for row in rows if row["case"] == case]
        good = _scored(mine)
        grades = [row["grade"] for row in good]
        entry = {
            "case": case,
            "run": mine[0]["run"],
            "screws": len(mine),
            "scored": len(good),
            "levels": len({row.get("level") for row in good if row.get("level")}),
            "grade_A": grades.count("A"),
            "grade_B": grades.count("B"),
            "grade_C_plus": sum(1 for g in grades if g not in ACCEPTABLE_GRADES),
            "acceptable_pct": _round(
                100.0 * sum(1 for g in grades if g in ACCEPTABLE_GRADES)
                / len(grades), 1) if grades else None,
            "gate_passed": sum(1 for row in good if row.get("gate_pass")),
            "worst_breach_mm": _round(max((row["breach_mm"] for row in good
                                           if row.get("breach_mm") is not None),
                                          default=None)),
            "min_clearance_mm": _round(min((row["min_clearance_mm"]
                                            for row in good
                                            if row.get("min_clearance_mm")
                                            is not None), default=None)),
            "min_medial_clearance_mm": _round(
                min((row["medial_clearance_mm"] for row in good
                     if row.get("medial_clearance_mm") is not None),
                    default=None)),
            "mean_containment_pct": _stats([row.get("containment_pct")
                                            for row in good])["mean"],
            "mean_fill_pct": _stats([row.get("fill_ratio_pct")
                                     for row in good])["mean"],
            "mean_path_hu": _stats([row.get("path_hu") for row in good])["mean"],
            "levels_named_wrong": sum(1 for row in mine
                                      if row.get("name_agrees") is False),
            "scene_volume": (files.get(case) or {}).get("scene_volume", ""),
        }
        out.append(entry)
    return out


def summary_rows(rows: Sequence[Dict[str, Any]],
                 levels: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    good = _scored(rows)
    out: List[Dict[str, Any]] = []

    def add(metric: str, values, note: str = ""):
        entry = {"metric": metric, "note": note}
        entry.update(_stats(values))
        out.append(entry)

    add("breach (mm, Gertzbein-Robbins)", [r.get("breach_mm") for r in good],
        "the worst protrusion per screw; 0 or less is fully contained")
    add("min clearance (mm)", [r.get("min_clearance_mm") for r in good],
        "negative IS the breach")
    add("medial clearance (mm)", [r.get("medial_clearance_mm") for r in good],
        "the wall that matters; below %.1f mm is flagged"
        % MEDIAL_CLEARANCE_MIN_MM)
    add("containment (%)", [r.get("containment_pct") for r in good])
    add("pedicle width (mm)", [r.get("pedicle_width_mm") for r in good],
        "minimum caliper of the section perpendicular to the trajectory")
    add("fill ratio (%)", [r.get("fill_ratio_pct") for r in good],
        "diameter / pedicle width; target %.0f%%" % FILL_TARGET_PCT)
    add("length of body depth (%)", [r.get("length_of_depth_pct") for r in good],
        "~50-80% is typical")
    add("tip to anterior cortex (mm)", [r.get("tip_to_cortex_mm") for r in good],
        "negative is anterior perforation")
    add("path HU (median)", [r.get("path_hu") for r in good],
        "inside the screw's own volume, not on its surface")
    add("contact area >=250 HU (mm2)", [r.get("contact_mm2_ge250") for r in good])
    add("TPA (deg)", [r.get("tpa_deg") for r in good])
    add("left/right symmetry (deg)", [lv.get("symmetry_deg") for lv in levels])
    add("trabecular HU (body)", [lv.get("trabecular_hu") for lv in levels],
        "[literature] >160 normal, 110-160 osteopenic, <110-120 osteoporotic")
    add("entry to label surface (mm)", [r.get("entry_on_surface_mm")
                                        for r in rows],
        "the frame-bridge witness; the planner puts the entry ON the cortex")

    grades = [r["grade"] for r in good]
    out.append({"metric": "screws graded A or B", "n": len(grades),
                "mean": _round(100.0 * sum(1 for g in grades
                                           if g in ACCEPTABLE_GRADES)
                               / len(grades), 1) if grades else None,
                "note": "per cent, over every scored screw of every case"})
    passed = [r for r in good if r.get("gate_pass") is not None]
    out.append({"metric": "screws passing the safety gate", "n": len(passed),
                "mean": _round(100.0 * sum(1 for r in passed
                                           if r.get("gate_pass")) / len(passed), 1)
                if passed else None,
                "note": "per cent; grade A/B AND medial clearance AND no "
                        "anterior perforation"})
    mismatched = [r for r in rows if r.get("name_agrees") is False]
    out.append({"metric": "screws whose plan named the wrong level",
                "n": len(mismatched), "mean": None,
                "note": "scored against the landmark either way; "
                        + (", ".join("%s/%s says %s"
                                     % (r["case"], r.get("site"), r.get("level"))
                                     for r in mismatched[:6])
                           if mismatched else "none")})
    return out


GRADE_MEANING = {
    "A": "fully contained -- no part of the screw is outside the cortex",
    "B": "less than 2 mm of protrusion; reported with A as clinically acceptable",
    "C": "2 to 4 mm",
    "D": "4 to 6 mm",
    "E": "6 mm or more",
}


def grade_rows(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    good = _scored(rows)
    total = len(good)
    out = []
    for letter in ("A", "B", "C", "D", "E"):
        count = sum(1 for row in good if row["grade"] == letter)
        out.append({"grade": letter, "screws": count,
                    "share_pct": _round(100.0 * count / total, 1) if total else None,
                    "meaning": GRADE_MEANING[letter]})
    return out


def phase_row(case: Dict[str, str], timing: Dict[str, Any],
              steps: Sequence[Dict[str, Any]], log: List[str]) -> Dict[str, Any]:
    """One run's wall time split by the wizard's pages."""
    label = case["subject"] or case["run"]
    row: Dict[str, Any] = {"case": label, "run": case["run"],
                           "t_total_s": timing.get("total_s"),
                           "inside_steps_s": timing.get("inside_steps_s")}
    totals = {phase: 0.0 for phase in PHASE_ORDER}
    unphased = 0.0
    unknown: List[str] = []
    for step in steps:
        # A '<< step back' row is a replay review, not a step: it carries an
        # empty step_id and its seconds are reported separately as
        # replay_review_s. Summing it into a phase would charge scrubbing the
        # timeline to whichever phase happened to be on screen.
        if step.get("kind") != "step visit" or not step.get("step_id"):
            continue
        seconds = step.get("wall_s")
        if not isinstance(seconds, (int, float)):
            # A branch_op row prints exec as '-'. wall is always a number, so a
            # missing one means the report's own row was unreadable -- skipped,
            # and visible as a non-zero phase_residual_s rather than folded away.
            continue
        phase = _PHASE_OF_STEP.get(canonical_step_id(step.get("step_id") or ""))
        if phase is None:
            unphased += float(seconds)
            unknown.append(str(step.get("step_id")))
        else:
            totals[phase] += float(seconds)
    for phase in PHASE_ORDER:
        row["%s_s" % phase] = _round(totals[phase], 2)
    row["unphased_s"] = _round(unphased, 2)
    inside = timing.get("inside_steps_s")
    row["phase_residual_s"] = _round(
        float(inside) - sum(totals.values()) - unphased, 2) \
        if isinstance(inside, (int, float)) else None
    if unknown:
        log.append("   [!] %s: %d step(s) in no phase (%s) -- the CLI package "
                   "may have been regenerated with different step ids"
                   % (label, len(unknown), ", ".join(sorted(set(unknown))[:6])))
    return row


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------

def discover_cases(experiment_root: str) -> List[Dict[str, str]]:
    """One entry per run folder under ``Overall_Performance``.

    The loop is over the RUNS, not over the data set. ``Dataset/`` holds many
    more cases than have been planned, and a case with no run has no plan to
    score -- listing it would report a procedure that was never performed as a
    failure of the one that was.
    """
    return _discover_cases(experiment_root, RUNS_SUBDIR, DATASET_SUBDIR)


def build_report(experiment_root: str, progress=None,
                 with_density: bool = True) -> Dict[str, Any]:
    """Analyse every run. Fail-soft per case, so one bad scene costs one case."""
    cases = discover_cases(experiment_root)
    rows: List[Dict[str, Any]] = []
    levels: List[Dict[str, Any]] = []
    files: Dict[str, Dict[str, Any]] = {}
    failed: List[str] = []
    log: List[str] = []
    if not cases:
        log.append("No runs found under %s."
                   % os.path.join(experiment_root, RUNS_SUBDIR))
    if not with_density:
        log.append("Density is OFF: the CT is not read, so path HU, contact "
                   "area, surface percentiles and trabecular HU are blank. Every "
                   "positional measure is unaffected -- they are taken against "
                   "the segmentation.")

    for index, case in enumerate(cases):
        label = case["subject"] or case["run"]
        if progress is not None:
            try:
                progress(index, len(cases), label)
            except Exception:
                logger.debug("Progress callback failed", exc_info=True)
        logger.info("[PSP] case %d/%d: %s", index + 1, len(cases), label)
        try:
            result = analyse_case(case, with_density=with_density)
        except Exception as exc:
            log.append("%s: FAILED -- %s" % (label, exc))
            logger.warning("Pedicle analysis failed for %s", label, exc_info=True)
            failed.append(label)
            continue
        rows.extend(result["rows"])
        levels.extend(result["levels"])
        files[label] = result["files"]
        good = _scored(result["rows"])
        log.append("%s: %d screw(s), %d scored -- worst breach %s mm, %d of %d "
                   "at grade A/B [scene volume %s, bridge %s mm]"
                   % (label, len(result["rows"]), len(good),
                      _fmt(max((r["breach_mm"] for r in good
                                if r.get("breach_mm") is not None), default=None)),
                      sum(1 for r in good if r["grade"] in ACCEPTABLE_GRADES),
                      len(good), result["files"]["scene_volume"],
                      result["files"]["bridge_mm"]))
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

    per_case = case_rows(rows, levels, files)
    summary = summary_rows(rows, levels)
    grades = grade_rows(rows)
    timing_title, timing_blocks = timing_sheet(timing_rows, step_rows)

    sheets = [
        ("Screw accuracy", [
            ("One row per planned screw, scored against the vertebra its own "
             "isthmus landmark is in. Safety first (grade, clearances, the "
             "gate), then fit, then the bone it is gripping. Every distance is "
             "to the ground-truth label; every HU is from the case's CT.",
             SCREW_COLUMNS, rows),
            ("Per instrumented level: how the two screws compare with each "
             "other, and the bone they are in.", LEVEL_COLUMNS, levels),
            ("Per run: a construct is as accurate as its worst screw.",
             CASE_COLUMNS, per_case),
            ("Gertzbein-Robbins distribution over every scored screw.",
             GRADE_COLUMNS, grades),
            ("Across every scored screw of every run.", SUMMARY_COLUMNS, summary),
            ("DEFINITIONS -- how the measurement is made",
             DEFINITION_COLUMNS, definition_rows(METHOD_DEFINITIONS)),
            ("DEFINITIONS -- per-screw columns",
             DEFINITION_COLUMNS, definition_rows(SCREW_DEFINITIONS)),
            ("DEFINITIONS -- per-level columns",
             DEFINITION_COLUMNS, definition_rows(LEVEL_DEFINITIONS)),
            ("DEFINITIONS -- per-run columns",
             DEFINITION_COLUMNS, definition_rows(CASE_DEFINITIONS)),
        ]),
        (timing_title, [
            ("The run's time split by the wizard's own pages, summed from the "
             "per-step timeline below.", PHASE_COLUMNS, phase_rows),
            ("DEFINITIONS -- phase columns",
             DEFINITION_COLUMNS, definition_rows(PHASE_DEFINITIONS)),
        ] + list(timing_blocks)),
    ]
    return {"sheets": sheets, "log": log, "rows": rows, "levels": levels,
            "case_rows": per_case, "summary": summary, "grades": grades,
            "phase_rows": phase_rows, "timing_rows": timing_rows,
            "step_rows": step_rows, "cases": len(cases),
            "with_density": bool(with_density),
            "analysed": len({row["case"] for row in rows}),
            "failed_cases": failed}


def _fmt(value: Optional[float]) -> str:
    return "%.2f" % value if isinstance(value, (int, float)) else "--"


def run_analysis(repository_root: str, progress=None,
                 with_density: bool = True) -> Dict[str, Any]:
    """Analyse every run and write the workbook. Returns the report + its path."""
    from .workbook import write_workbook                      # noqa: PLC0415

    experiment_root = os.path.join(repository_root, EXPERIMENT_DIR)
    report = build_report(experiment_root, progress=progress,
                          with_density=with_density)
    output = os.path.join(experiment_root, RUNS_SUBDIR, WORKBOOK_NAME)
    written, notes = write_workbook(output, report["sheets"])
    report["workbook"] = written
    report["log"].extend(notes)
    try:
        report["workbook_relative"] = os.path.relpath(written, repository_root)
    except ValueError:
        report["workbook_relative"] = written
    return report
