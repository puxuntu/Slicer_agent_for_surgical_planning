"""The user study's quantitative evaluation: one workbook per Results folder.

``Experiments/3_User_Study/Results/`` holds one folder per (arm, procedure,
participant), named ``【Agent】Pedicle Screw Planning【P1】`` /
``【Extension】Pedicle Screw Planning【P1】`` and so on, each holding that
participant's runs of that procedure in that arm. This module scores every run
in one such folder with the procedure's EXISTING analysis -- the same
``build_report`` the per-extension Experiments panels call -- and writes the
result to ``Quanti_Quali_Eva/<the folder's own name>.xlsx``. The mapping is one
folder in, one workbook out, so the number of workbooks follows the number of
folders and a new participant needs no code.

Nothing about the metrics lives here. What this module owns is only what is
different about the user study:

* **Where the runs and the data are.** The per-extension panels find both under
  one experiment root with fixed sub-folder names; here the runs are in
  ``Results/<folder>/`` and the data in ``Dataset/<procedure>/``, so the run set
  is built with ``run_timing.discover_runs`` and handed to ``build_report`` as
  ``cases=``. Every analysis consumes only those records.
* **Which analysis a folder gets.** Decided by the extension name every run
  folder starts with (``PedicleScrewPlanner_<subject>_<condition>_<stamp>``),
  never by the folder's display name, which is the study's prose.
* **Two sheets the procedure analyses do not have.** *Run set* says which folder,
  participant, arm, runs and data the workbook was computed from -- sixteen files
  that look alike must each say what they are. *Interaction* tabulates what the
  PlanningRecorder measured (wall clock, the seven activity states, the clicks
  by location) for every run. Both arms record exactly the same quantities, which
  is what makes the two arms comparable; the procedure's Timing sheet is built
  for the guided arm's step structure and is mostly empty for the other.

Two deliberate defaults, so the evaluation reads the Results tree and writes only
the workbook: the orbital analysis runs with ``write_scenes=False`` (it still
measures everything; it just does not add colour maps to each run's scene or
close the open scene), and the mandible analysis keeps its own cache of each
run's predicted ground truth (``Statistic/analysis/``), which is how it makes a
second sweep cheap and its reference inspectable.

Qt-free, so ``scripts/check_user_study_eval.py`` runs it outside Slicer.
"""

from __future__ import annotations

import importlib
import io
import json
import logging
import os
import re
import statistics
import time
from typing import Any, Callable, Dict, List, Optional, Sequence

from . import run_timing

logger = logging.getLogger(__name__)

#: The study's folder, as an untouched checkout spells it. Resolved, never
#: joined: see resolve_study_dir.
STUDY_DIR = os.path.join("Experiments", "3_User_Study")
RESULTS_SUBDIR = "Results"
DATASET_SUBDIR = "Dataset"
OUTPUT_SUBDIR = "Quanti_Quali_Eva"

#: ``【Agent】Pedicle Screw Planning【P1】`` -> arm, procedure, participant.
FOLDER_PATTERN = re.compile(
    u"^【(?P<arm>[^】]+)】\\s*(?P<procedure>.+?)\\s*"
    u"【(?P<participant>[^】]+)】$")

#: ``<Extension>_<subject>_<condition>_<YYYYmmdd_HHMMSS>``; the subject may
#: itself contain underscores (``45_154277``).
RUN_PATTERN = re.compile(
    r"^(?P<extension>[A-Za-z0-9]+)_(?P<subject>.+)_(?P<condition>manual|pipeline)"
    r"_(?P<stamp>\d{8}_\d{6})$")

#: The arm a folder is labelled with -> the condition its runs must carry. A
#: run whose condition disagrees is reported, because a run copied into the
#: wrong arm would otherwise be scored as the other arm without a sound.
ARM_CONDITIONS = {"agent": "pipeline", "extension": "manual"}

#: extension name (what every run folder starts with) -> how to analyse it.
#:   module   the experiments module whose build_report scores it
#:   first    what build_report's first argument is: "runs" (the folder the
#:            runs are in -- only named in its log) or "repository" (the
#:            checkout -- mandible locates its shape-completion model with it)
#:   options  keyword arguments, the per-extension panels' defaults except
#:            orbital's write_scenes (see the module docstring)
#:   scene    True when the analysis builds temporary nodes in the MRML scene,
#:            so it must not run while a guided workflow owns that scene
#: A procedure absent from this table is listed in the panel and not scored.
ANALYSES: Dict[str, Dict[str, Any]] = {
    "PedicleScrewPlanner": {"module": "pedicle", "first": "runs",
                            "options": {"with_density": True}, "scene": False},
    "BoneReconstructionPlanner": {"module": "mandible", "first": "repository",
                                  "options": {"recompute": False}, "scene": False},
    "OrbitalFractureReconstruction": {"module": "orbital", "first": "runs",
                                      "options": {"write_scenes": False},
                                      "scene": True},
    "ZygomaticImplantPlanner": {"module": "zygomatic", "first": "runs",
                                "options": {}, "scene": False},
}


# ---------------------------------------------------------------------------
# Locating the study and its folders
# ---------------------------------------------------------------------------

def resolve_study_dir(repository_root: str) -> str:
    """The user study's folder, wherever its tier sits.

    The tier name (``3_User_Study``) belongs to the study and the first tier has
    already been renamed once, so a miss on the declared spelling falls back to
    the first ``Experiments/<tier>/`` whose ``Results/`` holds at least one
    ``【arm】procedure【participant】`` folder -- the one thing that identifies
    this study's data. One level only, as in ``run_timing.resolve_experiment_dir``.
    """
    declared = os.path.join(repository_root, STUDY_DIR)
    if os.path.isdir(os.path.join(declared, RESULTS_SUBDIR)):
        return declared
    base = os.path.join(repository_root, "Experiments")
    try:
        tiers = sorted(os.listdir(base))
    except OSError:
        return declared
    for tier in tiers:
        results = os.path.join(base, tier, RESULTS_SUBDIR)
        try:
            if any(FOLDER_PATTERN.match(name) for name in os.listdir(results)):
                return os.path.join(base, tier)
        except OSError:
            continue
    return declared


def parse_folder(name: str) -> Optional[Dict[str, str]]:
    """``{"arm", "procedure", "participant"}`` for a Results folder, else None."""
    match = FOLDER_PATTERN.match(name or "")
    if not match:
        return None
    return {"arm": match.group("arm").strip(),
            "procedure": match.group("procedure").strip(),
            "participant": match.group("participant").strip()}


def participant_key(participant: str):
    """P2 before P10: by the number in the id, then by the id itself."""
    digits = re.findall(r"\d+", participant or "")
    return (int(digits[0]) if digits else 1 << 30, participant or "")


def discover_groups(study_dir: str) -> List[Dict[str, Any]]:
    """One record per ``Results/【arm】procedure【participant】`` folder.

    Sorted by procedure, then participant, then arm, which is the order the
    panel's selectors offer them. A folder that does not follow the naming is
    ignored rather than guessed at.
    """
    results = os.path.join(study_dir, RESULTS_SUBDIR)
    groups: List[Dict[str, Any]] = []
    try:
        names = sorted(os.listdir(results))
    except OSError:
        return groups
    for name in names:
        path = os.path.join(results, name)
        parsed = parse_folder(name)
        if not parsed or not os.path.isdir(path):
            continue
        runs, extensions, problems = [], {}, []
        expected = ARM_CONDITIONS.get(parsed["arm"].lower())
        for run in sorted(os.listdir(path)):
            match = RUN_PATTERN.match(run)
            if not match or not os.path.isdir(os.path.join(path, run)):
                continue
            runs.append(run)
            extensions[match.group("extension")] = extensions.get(
                match.group("extension"), 0) + 1
            if expected and match.group("condition") != expected:
                problems.append("%s is a %s run in the %s folder"
                                % (run, match.group("condition"), parsed["arm"]))
        saved = [r for r in runs
                 if os.path.isdir(os.path.join(path, r, "Statistic", "scene"))]
        unsaved = [r for r in runs if r not in saved]
        if unsaved:
            problems.append("%d run(s) have no saved scene and are skipped: %s"
                            % (len(unsaved), ", ".join(unsaved)))
        extension = max(extensions, key=extensions.get) if extensions else ""
        if len(extensions) > 1:
            problems.append("runs of %d procedures in one folder (%s); scoring %s"
                            % (len(extensions), ", ".join(sorted(extensions)), extension))
        dataset = os.path.join(study_dir, DATASET_SUBDIR, parsed["procedure"])
        groups.append(dict(parsed, **{
            "folder": name,
            "runs_dir": path,
            "extension": extension,
            "analysis": ANALYSES.get(extension),
            "runs": runs,
            "saved_runs": saved,
            "dataset_dir": dataset if os.path.isdir(dataset) else "",
            "output": os.path.join(study_dir, OUTPUT_SUBDIR, name + ".xlsx"),
            "problems": problems,
        }))
    arm_order = {"agent": 0, "extension": 1}
    groups.sort(key=lambda g: (g["procedure"].lower(), participant_key(g["participant"]),
                               arm_order.get(g["arm"].lower(), 9), g["arm"]))
    return groups


def group_cases(group: Dict[str, Any]) -> List[Dict[str, str]]:
    """The folder's scorable runs, in the ORDER THEY WERE PERFORMED.

    Performed order, not name order, because in a user study the sequence is
    data: the first case of each arm is where the learning happens.
    """
    cases = run_timing.discover_runs(group["runs_dir"], group.get("dataset_dir") or "")
    for case in cases:
        if not group.get("dataset_dir"):
            # discover_runs would join the subject onto "" and produce a
            # RELATIVE path that resolves against whatever the working folder
            # happens to be. No data folder is said plainly instead.
            case["dataset_dir"] = ""
        match = RUN_PATTERN.match(case["run"])
        case["stamp"] = match.group("stamp") if match else ""
    cases.sort(key=lambda c: (c["stamp"], c["run"]))
    for index, case in enumerate(cases, start=1):
        case["order"] = index
    return cases


# ---------------------------------------------------------------------------
# The two study sheets
# ---------------------------------------------------------------------------

#: The seven disjoint activity states the PlanningRecorder measures, and the
#: four that make up the person's hands-on time.
STATES = (("view_3d", "view_3d_s"), ("view_2d", "view_2d_s"), ("panel", "panel_s"),
          ("other", "other_s"), ("compute", "compute_s"), ("idle", "idle_s"),
          ("away", "away_s"))
HANDS_ON = ("view_3d", "view_2d", "panel", "other")
COUNTS = ("clicks_total", "clicks_view_3d", "clicks_view_2d", "clicks_panel",
          "clicks_other", "double_clicks", "drags", "drag_pixels", "wheel_notches",
          "keys")

INTERACTION_COLUMNS = (["order", "case", "wall_s", "elapsed_s", "paused_s", "pauses"]
                       + [column for _, column in STATES[:4]] + ["hands_on_s"]
                       + [column for _, column in STATES[4:]]
                       + list(COUNTS) + ["run"])

INTERACTION_DEFINITIONS = [
    ("source", "runtime/interaction.json of each run (else the copy in "
               "run_manifest.json): the PlanningRecorder's own measurement, "
               "tabulated here and not recomputed. The guided and the unaided arm "
               "record exactly the same quantities."),
    ("order", "The case's position in the order this participant performed this "
              "arm (by the run folder's time stamp)."),
    ("wall_s", "Recorded time, pauses excluded. The seven state columns sum to it."),
    ("elapsed_s / paused_s / pauses", "The raw clock, the time removed as pauses, "
                                      "and how many pauses there were."),
    ("view_3d_s / view_2d_s / panel_s / other_s",
     "Time inside a burst of input in a 3D view, a slice view, the procedure's own "
     "panel, or anywhere else in Slicer."),
    ("hands_on_s", "The sum of those four: the person operating Slicer."),
    ("compute_s", "The main thread blocked -- an algorithm running."),
    ("idle_s", "No input and nothing running: reading, deciding, waiting."),
    ("away_s", "Slicer was not the active window."),
    ("clicks_*", "Mouse presses while Slicer was active, in total and by where they "
                 "landed; the four located columns sum to clicks_total."),
    ("drags / drag_pixels / wheel_notches / keys",
     "Press-move-release gestures and their pointer travel, scroll-wheel notches, "
     "and key presses."),
    ("summary rows", "mean / SD / median / min / max over this folder's runs."),
]


def _interaction_of(run_dir: str) -> Dict[str, Any]:
    """The recorder's record: its own file first (the oldest runs have only that),
    else the copy in the manifest."""
    path = os.path.join(run_dir, "runtime", "interaction.json")
    if os.path.isfile(path):
        try:
            return json.load(io.open(path, encoding="utf-8")) or {}
        except Exception:                                    # noqa: BLE001
            logger.debug("Unreadable %s", path, exc_info=True)
    manifest = os.path.join(run_dir, "runtime", "run_manifest.json")
    if os.path.isfile(manifest):
        try:
            return json.load(io.open(manifest, encoding="utf-8")).get("interaction") or {}
        except Exception:                                    # noqa: BLE001
            logger.debug("Unreadable %s", manifest, exc_info=True)
    return {}


def _number(value: Any) -> Optional[float]:
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


def interaction_rows(cases: Sequence[Dict[str, str]], log: List[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for case in cases:
        label = case["subject"] or case["run"]
        data = _interaction_of(case["run_dir"])
        if not data.get("wall_seconds"):
            log.append("   [!] %s: no interaction record (the recorder was not "
                       "running, or the run was not closed with Exit)" % label)
            continue
        totals = data.get("totals") or {}
        counts = data.get("counts") or {}
        row: Dict[str, Any] = {
            "order": case.get("order"), "case": label, "run": case["run"],
            "wall_s": _round(_number(data.get("wall_seconds"))),
            "elapsed_s": _round(_number(data.get("elapsed_seconds"))),
            "paused_s": _round(_number(data.get("paused_seconds"))),
            "pauses": data.get("pause_count"),
        }
        for state, column in STATES:
            row[column] = _round(_number(totals.get(state)) or 0.0)
        row["hands_on_s"] = _round(sum(_number(totals.get(s)) or 0.0 for s in HANDS_ON))
        for key in COUNTS:
            value = _number(counts.get(key))
            row[key] = None if value is None else (round(value, 1) if key == "drag_pixels"
                                                   else int(value))
        rows.append(row)
    return rows


def _round(value: Optional[float], digits: int = 2) -> Optional[float]:
    return None if value is None else round(value, digits)


def summary_rows(rows: Sequence[Dict[str, Any]], columns: Sequence[str]
                 ) -> List[Dict[str, Any]]:
    """mean / SD / median / min / max of every numeric column, one row each."""
    if not rows:
        return []
    numeric = [c for c in columns if c not in ("order", "case", "run")]
    out = []
    for name, reduce in (("mean", statistics.mean), ("SD", statistics.stdev),
                         ("median", statistics.median), ("min", min), ("max", max)):
        row: Dict[str, Any] = {"case": name}
        for column in numeric:
            values = [r[column] for r in rows if isinstance(r.get(column), (int, float))
                      and not isinstance(r.get(column), bool)]
            if len(values) < (2 if name == "SD" else 1):
                continue
            row[column] = round(float(reduce(values)), 2)
        out.append(row)
    return out


def run_set_sheet(group: Dict[str, Any], cases: Sequence[Dict[str, str]],
                  study_dir: str):
    """What this workbook was computed from -- sixteen files that look alike
    must each say which one they are."""
    analysis = group.get("analysis") or {}

    def rel(path: str) -> str:
        if not path:
            return "(none)"
        try:
            return os.path.relpath(path, study_dir)
        except ValueError:
            return path

    facts = [
        ("participant", group["participant"]),
        ("arm", group["arm"]),
        ("procedure", group["procedure"]),
        ("extension", group["extension"] or "(not recognised)"),
        ("results folder", rel(group["runs_dir"])),
        ("dataset folder", rel(group.get("dataset_dir") or "")),
        ("analysis", "experiments/%s.py  build_report(%s)"
         % (analysis.get("module", "?"),
            ", ".join("%s=%r" % kv for kv in sorted((analysis.get("options") or {}).items()))
            or "defaults")),
        ("runs in the folder", len(group["runs"])),
        ("runs scored", len(cases)),
        ("generated", time.strftime("%Y-%m-%d %H:%M:%S")),
    ]
    facts.extend(("note", problem) for problem in group.get("problems") or [])
    case_rows = [{"order": c.get("order"), "case": c["subject"] or c["run"],
                  "run": c["run"], "performed": _stamp_text(c.get("stamp", "")),
                  "dataset": ("yes" if c.get("dataset_dir") and os.path.isdir(c["dataset_dir"])
                              else "MISSING")}
                 for c in cases]
    return ("Run set", [
        ("Which runs this workbook scores. One workbook per Results folder: one "
         "participant, one arm, one procedure.",
         ["item", "value"], [{"item": k, "value": v} for k, v in facts]),
        ("The runs, in the order the participant performed them. Every sheet "
         "lists its cases in this order.",
         ["order", "case", "run", "performed", "dataset"], case_rows),
    ])


def _stamp_text(stamp: str) -> str:
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(stamp, "%Y%m%d_%H%M%S"))
    except (TypeError, ValueError):
        return stamp


def interaction_sheet(cases: Sequence[Dict[str, str]], log: List[str]):
    rows = interaction_rows(cases, log)
    return ("Interaction", [
        ("Time and input per run, as the PlanningRecorder measured them -- the "
         "measurement both arms share, so this sheet is directly comparable "
         "between the agentic and the extension workbook of a participant.",
         INTERACTION_COLUMNS, rows),
        ("Across this folder's runs.", INTERACTION_COLUMNS,
         summary_rows(rows, INTERACTION_COLUMNS)),
        ("DEFINITIONS", ["term", "definition"],
         [{"term": t, "definition": d} for t, d in INTERACTION_DEFINITIONS]),
    ])


# ---------------------------------------------------------------------------
# Running one folder, or all of them
# ---------------------------------------------------------------------------

def analysis_module(extension: str):
    spec = ANALYSES.get(extension)
    if not spec:
        raise ValueError("no analysis is registered for %s" % (extension or "this folder"))
    return importlib.import_module("." + spec["module"], __package__), spec


def run_group(repository_root: str, group: Dict[str, Any],
              progress: Optional[Callable[[int, int, str], None]] = None
              ) -> Dict[str, Any]:
    """Score one Results folder and write its workbook. Returns the report.

    The procedure's own ``build_report`` does the measuring; this adds the two
    study sheets around its sheets and writes them to ``group["output"]``.
    """
    from .workbook import write_workbook                      # noqa: PLC0415

    module, spec = analysis_module(group.get("extension", ""))
    study_dir = os.path.dirname(os.path.dirname(group["runs_dir"]))
    cases = group_cases(group)
    first = repository_root if spec["first"] == "repository" else group["runs_dir"]
    report = module.build_report(first, progress=progress, cases=cases,
                                 **dict(spec.get("options") or {}))
    log = report.setdefault("log", [])
    if not group.get("dataset_dir"):
        log.insert(0, "[!] no Dataset/%s/ folder -- analyses that need a ground "
                      "truth from it cannot score these runs" % group["procedure"])
    for problem in group.get("problems") or []:
        log.insert(0, "[!] %s" % problem)
    sheets = ([run_set_sheet(group, cases, study_dir)] + list(report["sheets"])
              + [interaction_sheet(cases, log)])
    written, notes = write_workbook(group["output"], sheets)
    report["workbook"] = written
    log.extend(notes)
    try:
        report["workbook_relative"] = os.path.relpath(written, repository_root)
    except ValueError:
        report["workbook_relative"] = written
    report["scored_runs"] = len(cases)
    return report


def failures_in(report: Dict[str, Any]) -> List[str]:
    """Runs a procedure analysis could not score, whatever its report calls them."""
    failed = list(report.get("failed_cases") or [])
    for line in report.get("log") or []:
        match = re.match(r"^(\S.*?): (?:BIC )?FAILED -- ", str(line))
        if match and match.group(1) not in failed:
            failed.append(match.group(1))
    return failed
