"""ZygomaticImplantPlanner: relative BIC and run timing across every case.

Two tables, one workbook:

**BIC** — for each case, the four agentic paths against the four manually
planned ones. The absolute BIC of a path is the number of bone points inside the
thread-layer cylindrical shell along it, so it scales with the patient's bone
morphology, point-cloud density and imaging resolution. To remove that, each
manual path is normalised to 1 and its agentic counterpart reported relative to
it:

    relative BIC_i = rho_i(ours) / rho_i(manual)

Above 1 means our path achieves more bone-implant contact than the surgeon's.
Because the Quad Approach partitions each zygoma's candidate endpoints between
its two ipsilateral paths, one path can fall slightly below 1 while the pair
does not, so the per-SIDE sum is reported too: two manual paths contribute a
normalised 2, and a side total above 2 means our framework wins on that side's
overall bone engagement.

**Timing** — the run's own `Statistic/timing.txt`, parsed back into columns.

The manual plan is read from ``Experiments/<Extension>/Dataset/<subject>/``,
where ``<subject>`` is the folder the run's data was loaded from (the run
manifest records it). Every ``*.stl`` in that folder is taken to be one implant
rod; **their names carry no meaning to this analysis** and may be anything --
anything else in the folder (the volume, ``F.mrk.json``) is ignored.

Two decisions worth knowing, because getting either wrong yields plausible
numbers rather than an error:

- **Paths are paired by ENTRY POINT, never by file name.** The manual STLs are
  numbered independently of the plan -- on the current data set `1.stl` is the
  counterpart of `Implant_3` and `4.stl` of `Implant_1`, in both cases -- so
  pairing by index would compare each path with someone else's. Both plans put
  their implants on the same entry points by construction, and they do: the
  observed gap is under 0.001 mm on 7 of 8 paths and 0.28 mm on the eighth.
  A candidate further away than ``MAX_ENTRY_MATCH_MM`` is therefore not the
  same implant, and is reported unpaired rather than scored.
- **The agentic BIC is RECOMPUTED here, not read from the plan table.** The
  comparison is only meaningful if both sides are measured by the same
  instrument on the same bone cloud, and the stored number is not that
  instrument: ``generateOptimalPaths`` scores the candidate vector and only THEN
  pulls the tip back by ``safetyMargin`` (3 mm), so the path drawn in the scene
  is 3 mm shorter than the segment its score was taken over. Its inline counter
  also differs from ``bicScore`` at the ends -- it clips the projection instead
  of excluding out-of-segment points, so bone within one shell-radius of the
  entry counts even when it lies behind it.

  Both are reported. ``bic_ours`` / ``bic_manual`` use ``bic_score`` over the
  **drawn** segment -- what the implant physically occupies -- applied
  identically to both sides, and that pair is what ``relative_bic`` divides.
  ``bic_ours_as_planned`` reproduces the planner's own score and
  ``reconstruction_ok`` records whether it equals the stored value: that is the
  evidence that the bone cloud, the coordinate frame and the path geometry were
  all reconstructed correctly. On the current data set it matches 8 of 8 paths.

Note ``bic_ours`` and ``bic_manual`` are counts over each path's OWN drawn
length, and the two lengths differ (the planner picks the implant length): on
case 002 our ``Implant_1`` is 4.4 mm shorter than the rod it is compared with.
That is a real property of the plan, not an artefact, but it is why
``length_ours_mm`` / ``length_manual_mm`` sit beside the scores in the sheet --
a relative BIC should be read together with them.
"""

from __future__ import annotations

import io
import logging
import os
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np

from . import geometry_io as gio

logger = logging.getLogger(__name__)

EXTENSION_NAME = "ZygomaticImplantPlanner"

#: All paths below are relative to the repository root so the tree can be moved
#: or shared without editing code.
EXPERIMENT_DIR = os.path.join("Experiments", EXTENSION_NAME)
RUNS_SUBDIR = "Overall_Performance"
DATASET_SUBDIR = "Dataset"
WORKBOOK_NAME = "ZygomaticImplantPlanner_summary.xlsx"

#: The attribute the extension tags its own nodes with.
ROLE_ATTRIBUTE = "ZygomaticImplantPlanner.role"

#: Defaults of ZygomaticImplantPlannerLogic.computePaths. The BIC shell and the
#: bone cloud MUST match what produced the plan, or the recomputed agentic score
#: will not reproduce the stored one and the manual score is not comparable.
BIC_RADIUS_MM = 2.0
BIC_MARGIN_MM = 0.2
SAMPLE_RATE = 10
#: Pull-back applied to the tip AFTER scoring, so the drawn path is this much
#: shorter than the segment the stored BIC was taken over. Needed only to
#: reproduce that stored value as a cross-check.
SAFETY_MARGIN_MM = 3.0

#: How far an entry point may sit from the bone cloud before the frames are
#: considered irreconcilable (see geometry_io.resolve_frame). Entries lie ON the
#: bone; the observed spread on real cases is under 1.5 mm.
FRAME_TOLERANCE_MM = 5.0

#: How far a manual rod's end may sit from the agentic entry and still be the
#: same implant. The two plans share their entry points by construction, so the
#: real gap is a rounding error (under 0.3 mm on every path of the current data
#: set); this only has to be small enough that an STL which is NOT an implant --
#: anything else that lands in a case folder, now that the rods are named by
#: bare number and nothing distinguishes them -- is left unpaired instead of
#: being silently scored as somebody's implant.
MAX_ENTRY_MATCH_MM = 5.0


# ---------------------------------------------------------------------------
# The measurement
# ---------------------------------------------------------------------------

def bic_score(entry: Sequence[float], tip: Sequence[float], bone_points: np.ndarray,
              radius: float = BIC_RADIUS_MM, margin: float = BIC_MARGIN_MM) -> int:
    """Bone points inside the cylindrical shell along the segment [entry, tip].

    A line-for-line port of ``ZygomaticImplantPlanner.bicScore``. Deliberately a
    copy rather than an import: the analysis has to run against saved scenes
    without the extension loaded, and a drifting reimplementation would be worse
    than an explicit one -- which is why the recomputed agentic score is checked
    against the stored one on every case.
    """
    entry = np.asarray(entry, dtype=np.float64)
    tip = np.asarray(tip, dtype=np.float64)
    bone_points = np.asarray(bone_points, dtype=np.float64)
    vector = tip - entry
    length = float(np.linalg.norm(vector))
    if length < 1e-9 or bone_points.shape[0] == 0:
        return 0
    unit = vector / length
    diff = bone_points - entry
    projection = diff @ unit
    within = (projection >= 0.0) & (projection <= length)
    dist_sq = np.einsum("ij,ij->i", diff, diff) - np.square(projection)
    lo_sq = max(0.0, radius - margin) ** 2
    hi_sq = (radius + margin) ** 2
    return int(((dist_sq < hi_sq) & (dist_sq > lo_sq) & within).sum())


def planner_bic_score(entry: Sequence[float], tip: Sequence[float],
                      bone_points: np.ndarray, radius: float = BIC_RADIUS_MM,
                      margin: float = BIC_MARGIN_MM,
                      safety_margin: float = SAFETY_MARGIN_MM) -> int:
    """Reproduce the number the PLANNER stored, quirks and all.

    Exists purely to validate the reconstruction and is never used for the
    comparison. Two differences from ``bic_score``, both inherited from
    ``generateOptimalPaths``:

    1. It scores ``[entry, tip + safety_margin]`` -- the candidate vector as it
       stood when scored, before the tip was pulled back.
    2. It CLIPS the projection to ``[0, length]`` instead of excluding points
       outside it, so a bone point behind the entry is measured to the ENTRY and
       counts whenever it falls in the shell. ``bic_score`` excludes it.

    Neither is what an implant physically contacts, which is why the comparison
    uses ``bic_score``; but matching this exactly is what proves the bone cloud,
    the coordinate frame and the path geometry were reconstructed correctly.
    """
    entry = np.asarray(entry, dtype=np.float64)
    tip = np.asarray(tip, dtype=np.float64)
    bone_points = np.asarray(bone_points, dtype=np.float64)
    vector = tip - entry
    norm = float(np.linalg.norm(vector))
    if norm < 1e-9 or bone_points.shape[0] == 0:
        return 0
    vector = (tip + (vector / norm) * float(safety_margin)) - entry
    length = float(np.linalg.norm(vector)) + 1e-4
    unit = vector / length
    diff = bone_points - entry
    norm_sq = np.einsum("ij,ij->i", diff, diff)
    projection = np.clip(diff @ unit, 0.0, None)
    projection[projection > length] = 0.0
    dist_sq = norm_sq - np.square(projection)
    return int((((dist_sq < (radius + margin) ** 2)
                 & (dist_sq > (radius - margin) ** 2))).sum())


def bone_cloud(roles: Dict[str, List[str]], sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """The cloud the extension scores BIC against.

    Mirrors ``_bonePointsForBic``: the separation target subsampled by
    ``2 * sample_rate``, plus both zygoma clouds at full density. The separation
    target is the maxilla region when the maxilla/mandible split was run and the
    step-2 cropped region otherwise -- the same fallback ``separationTarget()``
    makes, and it changes the point count, so it cannot be guessed.
    """
    stride = max(1, 2 * int(sample_rate))
    parts: List[np.ndarray] = []
    target = gio.role_file(roles, "maxillaRegion", "croppedRegion")
    if target:
        parts.append(gio.read_vtk_points(target)[::stride])
    for role in ("zygomaCloudRight", "zygomaCloudLeft"):
        path = gio.role_file(roles, role)
        if path:
            parts.append(gio.read_vtk_points(path))
    parts = [p for p in parts if p.shape[0] > 0]
    if not parts:
        raise ValueError("no bone geometry in this scene (maxilla/cropped region "
                         "and both zygoma clouds are all missing)")
    return np.concatenate(parts, axis=0)


# ---------------------------------------------------------------------------
# Reading one case
# ---------------------------------------------------------------------------

def read_plan_table(path: str) -> List[Dict[str, Any]]:
    """The extension's own summary table: Path, Side, Length, BIC, Entry R/A/S."""
    rows: List[Dict[str, Any]] = []
    if not path or not os.path.isfile(path):
        return rows
    lines = [l for l in io.open(path, encoding="utf-8").read().splitlines() if l.strip()]
    if len(lines) < 2:
        return rows
    header = lines[0].split("\t")
    for line in lines[1:]:
        cells = line.split("\t")
        row = dict(zip(header, cells))
        for key in ("Length", "BIC", "EntryR", "EntryA", "EntryS"):
            try:
                row[key] = float(row.get(key, ""))
            except (TypeError, ValueError):
                row[key] = None
        rows.append(row)
    return rows


def agentic_paths(scene_dir: str) -> List[Dict[str, Any]]:
    """The planned paths: name, entry and tip in the scene's own frame."""
    roles = gio.scene_role_files(scene_dir, ROLE_ATTRIBUTE)
    paths: List[Dict[str, Any]] = []
    for path_file in sorted(roles.get("implantPath") or []):
        if not os.path.isfile(path_file):
            continue
        points, labels = gio.read_markups_points(path_file)
        if points.shape[0] < 2:
            continue
        name = os.path.basename(path_file).split(".")[0]      # ImplantPath_1
        paths.append({
            "name": name,
            "implant": name.replace("ImplantPath", "Implant"),
            "entry": points[0],
            "tip": points[1],
            "entry_label": labels[0] if labels else "",
        })
    return paths


def manual_paths(dataset_dir: str, notes: Optional[List[str]] = None
                 ) -> List[Dict[str, Any]]:
    """The surgeon's paths, from the STL rods: both axis endpoints per file.

    Every ``*.stl`` in the case folder is a candidate, whatever it is called --
    the file name is carried through to the sheet for traceability and is used
    for nothing else. ``name`` keeps the extension so a folder of bare numbers
    (``1.stl``) still reads as a file rather than as an index.

    Which end is the entry is NOT decided here -- it follows from the pairing,
    since the entry is the end that coincides with the agentic entry.

    One unreadable or non-rod file must not cost the case its other three paths,
    so each is read independently and a failure is appended to ``notes``.
    """
    paths: List[Dict[str, Any]] = []
    if not os.path.isdir(dataset_dir):
        return paths
    for name in sorted(f for f in os.listdir(dataset_dir) if f.lower().endswith(".stl")):
        try:
            points = gio.read_stl_points(os.path.join(dataset_dir, name))
            if points.shape[0] < 2:
                raise ValueError("fewer than two vertices")
            low, high = gio.rod_axis_endpoints(points)
        except Exception as exc:
            logger.warning("Unusable STL %s in %s", name, dataset_dir, exc_info=True)
            if notes is not None:
                notes.append("%s could not be read as an implant rod (%s)"
                             % (name, exc))
            continue
        paths.append({"name": name, "ends": (low, high)})
    return paths


def pair_by_entry(agentic: List[Dict[str, Any]], manual: List[Dict[str, Any]],
                  max_entry_mm: float = MAX_ENTRY_MATCH_MM
                  ) -> List[Tuple[Dict[str, Any], Optional[Dict[str, Any]], float]]:
    """Pair each agentic path with the manual one sharing its entry point.

    The two plans place implants at the SAME entry points by construction, so
    the entry is the identity of a path and the file numbering is not: on the
    current data set ``1.stl`` belongs with ``Implant_3``. Cost is the distance
    from the agentic entry to the nearer end of the manual rod, and the
    assignment is solved globally (Hungarian when SciPy is present, greedy
    otherwise) so one ambiguous pair cannot cascade.

    A match further than ``max_entry_mm`` is REJECTED rather than scored. The
    assignment is total -- it hands every agentic path a partner whether or not
    a real one exists -- so without the ceiling, a case folder holding three
    rods and one unrelated STL would compare an implant against the unrelated
    one and report a number for it.

    Returns ``(agentic, manual_or_None, distance_mm)`` and sets ``entry``/``tip``
    on the matched manual path, oriented to agree with its partner. The distance
    is returned even when the match is rejected, so the sheet shows why.
    """
    if not agentic or not manual:
        return [(a, None, float("nan")) for a in agentic]

    cost = np.zeros((len(agentic), len(manual)))
    which_end = np.zeros((len(agentic), len(manual)), dtype=int)
    for i, a in enumerate(agentic):
        for j, m in enumerate(manual):
            distances = [float(np.linalg.norm(a["entry"] - end)) for end in m["ends"]]
            which_end[i, j] = int(np.argmin(distances))
            cost[i, j] = min(distances)

    try:
        from scipy.optimize import linear_sum_assignment    # noqa: PLC0415
        rows, cols = linear_sum_assignment(cost)
        assignment = dict(zip(rows.tolist(), cols.tolist()))
    except Exception:
        assignment, taken = {}, set()
        for i, j in sorted(((i, j) for i in range(len(agentic)) for j in range(len(manual))),
                           key=lambda ij: cost[ij]):
            if i not in assignment and j not in taken:
                assignment[i], _ = j, taken.add(j)

    paired = []
    for i, a in enumerate(agentic):
        j = assignment.get(i)
        if j is None:
            paired.append((a, None, float("nan")))
            continue
        if float(cost[i, j]) > float(max_entry_mm):
            paired.append((a, None, float(cost[i, j])))
            continue
        m = dict(manual[j])
        end = which_end[i, j]
        m["entry"] = m["ends"][end]
        m["tip"] = m["ends"][1 - end]
        paired.append((a, m, float(cost[i, j])))
    return paired


# ---------------------------------------------------------------------------
# timing.txt + case discovery
#
# Both live in run_timing.py: neither is procedure-specific -- what a run folder
# looks like and what its timing report says are properties of RunLog, and
# OrbitalFractureReconstruction needs exactly the same columns. Re-exported here
# so this module's callers (and its own build_report below) are unchanged.
# ---------------------------------------------------------------------------

from .run_timing import (                                     # noqa: E402
    STEP_TIMING_COLUMNS,
    TIMING_COLUMNS,
    collect_timing,
    parse_timing,
    parse_timing_steps,
    subject_from_run as _subject_from_run,
    timing_sheet,
)


def discover_cases(experiment_root: str) -> List[Dict[str, str]]:
    """One entry per run folder under ``Overall_Performance``, oldest name first."""
    from .run_timing import discover_cases as _discover        # noqa: PLC0415
    return _discover(experiment_root, RUNS_SUBDIR, DATASET_SUBDIR)



# ---------------------------------------------------------------------------
# One case, end to end
# ---------------------------------------------------------------------------

def analyse_case(case: Dict[str, str], sample_rate: int = SAMPLE_RATE,
                 radius: float = BIC_RADIUS_MM, margin: float = BIC_MARGIN_MM
                 ) -> Dict[str, Any]:
    """Per-path BIC rows plus the per-side aggregate for one case."""
    scene_dir = case["scene_dir"]
    roles = gio.scene_role_files(scene_dir, ROLE_ATTRIBUTE)
    bone = bone_cloud(roles, sample_rate)
    table = {row.get("Path"): row for row in
             read_plan_table(gio.role_file(roles, "planTable") or "")}

    agentic = agentic_paths(scene_dir)
    if not agentic:
        raise ValueError("no implant paths in the saved scene")
    # Prove the paths and the bone are in the same frame before scoring anything.
    entries = np.asarray([p["entry"] for p in agentic])
    _unused, frame = gio.resolve_frame(entries, bone, FRAME_TOLERANCE_MM)

    notes: List[str] = []
    manual = manual_paths(case.get("dataset_dir", ""), notes)
    manual_frame = "n/a"
    if manual:
        ends = np.asarray([e for m in manual for e in m["ends"]])
        converted, manual_frame = gio.resolve_frame(ends, bone, FRAME_TOLERANCE_MM)
        if manual_frame == "mirrored":
            for index, m in enumerate(manual):
                m["ends"] = (converted[2 * index], converted[2 * index + 1])

    rows: List[Dict[str, Any]] = []
    for a, m, distance in pair_by_entry(agentic, manual):
        stored = table.get(a["implant"], {})
        ours = bic_score(a["entry"], a["tip"], bone, radius, margin)
        theirs = bic_score(m["entry"], m["tip"], bone, radius, margin) if m else None
        as_planned = planner_bic_score(a["entry"], a["tip"], bone, radius, margin)
        rows.append({
            "case": case["subject"] or case["run"],
            "run": case["run"],
            "path": a["implant"],
            "side": str(stored.get("Side") or ""),
            "manual_file": (m or {}).get("name", ""),
            "entry_match_mm": round(distance, 3) if distance == distance else None,
            "bic_ours": ours,
            "bic_manual": theirs,
            "relative_bic": (round(ours / theirs, 4) if theirs else None),
            "length_ours_mm": round(float(np.linalg.norm(a["tip"] - a["entry"])), 3),
            "length_manual_mm": (round(float(np.linalg.norm(m["tip"] - m["entry"])), 3)
                                 if m else None),
            "bic_ours_stored": stored.get("BIC"),
            "bic_ours_as_planned": as_planned,
            "reconstruction_ok": (
                None if stored.get("BIC") is None else int(stored["BIC"]) == as_planned),
        })
    return {
        "rows": rows,
        "bone_points": int(bone.shape[0]),
        "frame_paths": frame,
        "frame_manual": manual_frame,
        "n_manual": len(manual),
        "notes": notes,
        # Told apart in the log: an unpaired path means either that the case
        # folder is missing/empty or that the nearest rod was too far away to be
        # the same implant, and the two ask for different things of the reader.
        "rejected": [(r["path"], r["entry_match_mm"]) for r in rows
                     if r["bic_manual"] is None and r["entry_match_mm"] is not None],
    }


def side_totals(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Per-side aggregate: the sum of that side's relative BICs.

    Two manual paths contribute a normalised 2, so a sum above 2 means the
    framework wins on that side's overall bone engagement -- the check that the
    Quad Approach's endpoint partitioning has not traded away fixation quality
    even where a single path dips below 1.
    """
    totals: List[Dict[str, Any]] = []
    by_case: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for row in rows:
        if row.get("relative_bic") is None:
            continue
        by_case.setdefault((row["case"], row.get("side") or "?"), []).append(row)
    for (case, side), group in sorted(by_case.items()):
        relative = [r["relative_bic"] for r in group]
        totals.append({
            "case": case,
            "side": side,
            "paths": len(group),
            "sum_relative_bic": round(sum(relative), 4),
            "baseline": len(group),          # each manual path normalises to 1
            "beats_manual": sum(relative) > len(group),
            "sum_bic_ours": sum(r["bic_ours"] for r in group),
            "sum_bic_manual": sum(r["bic_manual"] for r in group),
        })
    return totals


# ---------------------------------------------------------------------------
# The report
# ---------------------------------------------------------------------------

#: Per-path BIC columns, in the order they appear in the sheet.
BIC_COLUMNS = [
    "case", "path", "side", "manual_file", "entry_match_mm",
    "bic_ours", "bic_manual", "relative_bic",
    "length_ours_mm", "length_manual_mm",
    "bic_ours_stored", "bic_ours_as_planned", "reconstruction_ok", "run",
]

SIDE_COLUMNS = [
    "case", "side", "paths", "sum_relative_bic", "baseline", "beats_manual",
    "sum_bic_ours", "sum_bic_manual",
]

# TIMING_COLUMNS / STEP_TIMING_COLUMNS are imported from run_timing above.


def _mean(values: List[float]) -> Optional[float]:
    values = [v for v in values if isinstance(v, (int, float))]
    return round(sum(values) / len(values), 4) if values else None


def build_report(experiment_root: str, sample_rate: int = SAMPLE_RATE
                 ) -> Dict[str, Any]:
    """Analyse every case and return the sheets plus a human-readable log.

    Fail-soft per case: one unreadable scene must not cost the other cases their
    numbers, so its error is recorded as a row in the log and the rest continue.
    """
    cases = discover_cases(experiment_root)
    bic_rows: List[Dict[str, Any]] = []
    log: List[str] = []
    if not cases:
        log.append("No cases found under %s." % os.path.join(experiment_root, RUNS_SUBDIR))

    for case in cases:
        label = case["subject"] or case["run"]
        try:
            result = analyse_case(case, sample_rate=sample_rate)
        except Exception as exc:
            log.append("%s: BIC FAILED -- %s" % (label, exc))
            logger.warning("BIC analysis failed for %s", label, exc_info=True)
        else:
            bic_rows.extend(result["rows"])
            checked = [r for r in result["rows"] if r["reconstruction_ok"] is not None]
            agreed = sum(1 for r in checked if r["reconstruction_ok"])
            paired = sum(1 for r in result["rows"] if r["bic_manual"] is not None)
            log.append(
                "%s: %d path(s), %d paired with a manual STL (%d rod(s) read from "
                "%s), bone cloud %d pts, planner score reproduced %d/%d"
                % (label, len(result["rows"]), paired, result["n_manual"],
                   os.path.basename(case.get("dataset_dir") or "") or "(none)",
                   result["bone_points"], agreed, len(checked)))
            for note in result["notes"]:
                log.append("   [!] %s: %s" % (label, note))
            if checked and agreed < len(checked):
                log.append("   [!] %s: the recomputed planner score does not match the "
                           "stored one -- the bone cloud may not be the one the plan "
                           "was made against; treat this case's BIC with care."
                           % label)
            # Two different problems, so two different messages: no rod to pair
            # with at all, versus a rod that was there but is not the same
            # implant. The second is the one that would otherwise be scored.
            if not result["n_manual"]:
                log.append("   [!] %s: no .stl found in %s -- every path is unpaired. "
                           "The folder must be named after the run's subject."
                           % (label, case.get("dataset_dir") or "(no dataset folder)"))
            elif result["rejected"]:
                log.append("   [!] %s: %s left unpaired -- the nearest manual rod end "
                           "is over %.1f mm from the entry point, so it is not the "
                           "same implant."
                           % (label,
                              ", ".join("%s (%.2f mm)" % (name, distance)
                                        for name, distance in result["rejected"]),
                              MAX_ENTRY_MATCH_MM))
            elif paired < len(result["rows"]):
                log.append("   [!] %s: %d path(s) had no manual counterpart in %s"
                           % (label, len(result["rows"]) - paired,
                              case.get("dataset_dir") or "(no dataset folder)"))

    timing_rows, step_rows = collect_timing(cases, log)

    totals = side_totals(bic_rows)

    per_case: List[Dict[str, Any]] = []
    for case_name in sorted({r["case"] for r in bic_rows}):
        rows = [r for r in bic_rows if r["case"] == case_name
                and r["relative_bic"] is not None]
        if not rows:
            continue
        per_case.append({
            "case": case_name,
            "paths": len(rows),
            "mean_relative_bic": _mean([r["relative_bic"] for r in rows]),
            "min_relative_bic": round(min(r["relative_bic"] for r in rows), 4),
            "max_relative_bic": round(max(r["relative_bic"] for r in rows), 4),
            "paths_above_1": sum(1 for r in rows if r["relative_bic"] > 1.0),
        })
    if per_case:
        per_case.append({
            "case": "ALL CASES",
            "paths": sum(c["paths"] for c in per_case),
            "mean_relative_bic": _mean([r["relative_bic"] for r in bic_rows
                                        if r["relative_bic"] is not None]),
            "min_relative_bic": min(c["min_relative_bic"] for c in per_case),
            "max_relative_bic": max(c["max_relative_bic"] for c in per_case),
            "paths_above_1": sum(c["paths_above_1"] for c in per_case),
        })

    sheets = [
        ("BIC", [
            ("Per-path relative BIC  (relative = ours / manual, on the SAME entry "
             "point; > 1 means more bone-implant contact than the surgeon's path. "
             "manual_file names the STL the path was paired with and "
             "entry_match_mm how far its end sat from the entry -- both are "
             "traceability, not inputs. Read relative_bic together with the two "
             "length columns: each score counts contact over its own path's "
             "length, and the planner chooses that length.)",
             BIC_COLUMNS, bic_rows),
            ("Per-side totals  (each side's two manual paths sum to the baseline, "
             "so a sum above it means the Quad Approach partitioning did not cost "
             "overall fixation on that side)",
             SIDE_COLUMNS, totals),
            ("Per-case summary",
             ["case", "paths", "mean_relative_bic", "min_relative_bic",
              "max_relative_bic", "paths_above_1"], per_case),
        ]),
        timing_sheet(timing_rows, step_rows),
    ]
    return {"sheets": sheets, "log": log, "bic_rows": bic_rows,
            "side_totals": totals, "per_case": per_case, "timing_rows": timing_rows,
            "step_rows": step_rows, "cases": len(cases)}


def run_analysis(repository_root: str, sample_rate: int = SAMPLE_RATE
                 ) -> Dict[str, Any]:
    """Analyse every case and write the workbook. Returns the report + its path.

    ``repository_root`` is the extension checkout; everything below it is
    addressed relatively, so the tree can be moved or handed to someone else
    without editing code.
    """
    from .workbook import write_workbook                     # noqa: PLC0415

    experiment_root = os.path.join(repository_root, EXPERIMENT_DIR)
    report = build_report(experiment_root, sample_rate=sample_rate)
    output = os.path.join(experiment_root, RUNS_SUBDIR, WORKBOOK_NAME)
    written, notes = write_workbook(output, report["sheets"])
    report["workbook"] = written
    report["log"].extend(notes)
    # Relative, because that is how the path was given and how it stays valid
    # if the tree moves.
    try:
        report["workbook_relative"] = os.path.relpath(written, repository_root)
    except ValueError:
        report["workbook_relative"] = written
    return report
