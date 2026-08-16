"""Read a run's ``Statistic/timing.txt`` back into columns, and find the cases.

Shared by every procedure's analysis, because none of it is procedure-specific:
what a run folder looks like, and what its timing report says, are properties of
``RunLog``. It was written for ZygomaticImplantPlanner and lifted here unchanged
when OrbitalFractureReconstruction needed the same columns -- a second copy would
have been a second thing to update whenever the report's wording changes, and the
failure mode of a stale copy is a silently blank column rather than an error.

Parsed from the *rendered report* rather than from ``run_manifest.json``: the
report is what a run leaves in ``Statistic/`` and what a reader compares against,
so a case whose manifest has been lost still yields a row. The cost is a
dependency on that report's wording, which is why every field below is an
explicit regex -- a report that changes its phrasing leaves a blank cell instead
of a wrong number.

Qt-free and Slicer-free, so it is checkable outside Slicer.
"""

from __future__ import annotations

import io
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# The summary block
# ---------------------------------------------------------------------------

#: (column, regex) over the report's summary block. Kept as an explicit list so
#: a reader can see exactly which lines are lifted.
_TIMING_FIELDS: List[Tuple[str, str]] = [
    # Numbers are matched with an optional leading minus: the between-steps
    # residual goes NEGATIVE exactly when the per-step clocks disagree with the
    # run clock, which is the one value a reader must not see as a blank cell.
    ("procedure", r"^\s*Procedure\s*:\s*(.+?)\s*$"),
    ("subject", r"^\s*Subject\s*:\s*(\S+)"),
    ("condition", r"^\s*Condition\s*:\s*(.+?)\s*$"),
    ("status", r"^\s*Final status\s*:\s*(.+?)\s*$"),
    ("model", r"^\s*Model\s*:\s*(.+?)\s*$"),
    ("send_clicked", r"^\s*Send clicked\s*:\s*(.+?)\s*$"),
    ("exit_clicked", r"^\s*Exit clicked\s*:\s*(.+?)\s*$"),
    ("total_s", r"^\s*TOTAL RUN TIME\s*:\s*(-?[\d.]+) s"),
    ("startup_s", r"^\s*startup before step 1 opened\s*:\s*(-?[\d.]+) s"),
    ("routing_call_s", r"routing call (-?[\d.]+) s"),
    ("inside_steps_s", r"^\s*inside the steps\s*:\s*(-?[\d.]+) s"),
    ("between_steps_s", r"^\s*between steps \(auto-advance\)\s*:\s*(-?[\d.]+) s"),
    ("replay_review_s", r"^\s*reviewing the replay timeline\s*:\s*(-?[\d.]+) s"),
    ("tail_wait_exit_s", r"^\s*after the last step, waiting for Exit\s*:\s*(-?[\d.]+) s"),
    ("executing_code_s", r"^\s*executing generated code\s*:\s*(-?[\d.]+) s"),
    ("waiting_for_user_s", r"^\s*waiting for the user\s*:\s*(-?[\d.]+) s"),
    ("runtime_overhead_s", r"^\s*runtime overhead\s*:\s*(-?[\d.]+) s"),
    ("steps_recorded", r"Steps recorded:\s*(\d+)"),
    ("steps_ok", r"\bok:\s*(\d+)"),
    ("steps_failed", r"failed:\s*(\d+)"),
    ("tokens", r"Model cost\s*:\s*(\d+) tokens"),
    ("cost_usd", r"Model cost\s*:.*\$([\d.]+)"),
]

_NUMERIC_TIMING = {name for name, _ in _TIMING_FIELDS
                   if name.endswith("_s") or name in
                   ("steps_recorded", "steps_ok", "steps_failed", "tokens", "cost_usd")}


def parse_timing(path: str) -> Dict[str, Any]:
    """Pull the summary block of a timing report back into columns."""
    result: Dict[str, Any] = {}
    if not path or not os.path.isfile(path):
        return result
    text = io.open(path, encoding="utf-8", errors="replace").read()
    for name, pattern in _TIMING_FIELDS:
        match = re.search(pattern, text, re.MULTILINE)
        if not match:
            continue
        value = match.group(1).strip()
        if name in _NUMERIC_TIMING:
            try:
                value = float(value)
            except ValueError:
                continue
        result[name] = value
    # Sums to the total, so a reader can see the split is complete.
    parts = [result.get(k) for k in ("startup_s", "inside_steps_s", "between_steps_s",
                                     "replay_review_s", "tail_wait_exit_s")]
    known = [p for p in parts if isinstance(p, float)]
    if known and isinstance(result.get("total_s"), float):
        result["split_residual_s"] = round(result["total_s"] - sum(known), 3)
    return result


# ---------------------------------------------------------------------------
# The TIMELINE table
# ---------------------------------------------------------------------------

#: Column slices of the TIMELINE table rendered by ``RunLog.build_run_statistics``.
#: Fixed-width rather than split-on-whitespace because two fields contain single
#: spaces of their own -- the ``<< step back`` label and the ``(replay review)``
#: type -- which any whitespace split would tear in half.
_TIMELINE_SLICES = {
    "order": (0, 4), "step_id": (5, 19), "type": (20, 36),
    "wall_s": (37, 46), "exec_s": (47, 56), "wait_s": (57, 66),
    "runs": (68, 75), "status": (77, None),
}

_DURATION = re.compile(r"^(?:(\d+)m)?([\d.]+)s$")


def duration_seconds(text: str) -> Optional[float]:
    """``47.05s`` / ``1m02.6s`` / ``-`` -> seconds or None."""
    text = (text or "").strip()
    match = _DURATION.match(text)
    if not match:
        return None
    minutes, seconds = match.group(1), match.group(2)
    try:
        return round((int(minutes) * 60 if minutes else 0) + float(seconds), 3)
    except ValueError:
        return None


def parse_timing_steps(path: str) -> List[Dict[str, Any]]:
    """One row per line of the report's TIMELINE table.

    Rows come through in the order they happened, so a step re-run after a
    step-back appears twice with the ``<< step back`` review between them --
    which is the whole point of listing them per step rather than in aggregate.
    """
    rows: List[Dict[str, Any]] = []
    if not path or not os.path.isfile(path):
        return rows
    lines = io.open(path, encoding="utf-8", errors="replace").read().splitlines()
    started = False
    for line in lines:
        if line.lstrip().startswith("# step_id"):
            started = True
            continue
        if not started:
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("---"):
            # The rule under the header, then the rule that closes the table.
            if rows:
                break
            continue
        if stripped.startswith("error:"):
            # Continuation of the row above, not a row of its own.
            if rows:
                rows[-1]["error"] = stripped[len("error:"):].strip()
            continue
        if stripped.startswith("TOTAL"):
            break
        cells = {name: line[start:stop].strip()
                 for name, (start, stop) in _TIMELINE_SLICES.items()}
        try:
            order = int(cells["order"])
        except (TypeError, ValueError):
            continue                      # not a table row
        step_id = cells["step_id"]
        replay = step_id.startswith("<<")
        rows.append({
            "order": order,
            "kind": "replay review" if replay else "step visit",
            "step_id": "" if replay else step_id,
            "type": cells["type"].strip("()"),
            "wall_s": duration_seconds(cells["wall_s"]),
            "exec_s": duration_seconds(cells["exec_s"]),
            "wait_s": duration_seconds(cells["wait_s"]),
            "runs": cells["runs"],
            "status": cells["status"],
            "error": "",
        })
    return rows


# ---------------------------------------------------------------------------
# Case discovery
# ---------------------------------------------------------------------------

def subject_from_run(run_dir: str) -> str:
    """The data set a run was driven from: the manifest's record, else the name."""
    for candidate in (os.path.join(run_dir, "runtime", "run_manifest.json"),
                      os.path.join(run_dir, "run_manifest.json")):
        if os.path.isfile(candidate):
            try:
                subject = json.load(io.open(candidate, encoding="utf-8")).get("subject")
                if subject:
                    return str(subject)
            except Exception:
                logger.debug("Unreadable manifest %s", candidate, exc_info=True)
    # <procedure>_<subject>_<condition>_<stamp>
    parts = os.path.basename(run_dir).split("_")
    return parts[1] if len(parts) >= 4 else ""


def discover_cases(experiment_root: str, runs_subdir: str,
                   dataset_subdir: str) -> List[Dict[str, str]]:
    """One entry per run folder under ``runs_subdir``, oldest name first.

    A run qualifies on having a ``Statistic/scene/`` folder -- i.e. on having
    been exited with "save". A run without one produced no geometry to score and
    is skipped silently rather than reported as a failure.
    """
    runs_dir = os.path.join(experiment_root, runs_subdir)
    dataset_dir = os.path.join(experiment_root, dataset_subdir)
    cases: List[Dict[str, str]] = []
    if not os.path.isdir(runs_dir):
        return cases
    for name in sorted(os.listdir(runs_dir)):
        run_dir = os.path.join(runs_dir, name)
        scene_dir = os.path.join(run_dir, "Statistic", "scene")
        if not os.path.isdir(scene_dir):
            continue
        subject = subject_from_run(run_dir)
        cases.append({
            "run": name,
            "subject": subject,
            "run_dir": run_dir,
            "scene_dir": scene_dir,
            "timing": os.path.join(run_dir, "Statistic", "timing.txt"),
            "dataset_dir": os.path.join(dataset_dir, subject) if subject else "",
        })
    return cases


# ---------------------------------------------------------------------------
# The Timing sheet, rendered identically for every procedure
# ---------------------------------------------------------------------------

TIMING_COLUMNS = [
    "case", "run", "procedure", "condition", "status", "model",
    "send_clicked", "exit_clicked", "total_s",
    "startup_s", "routing_call_s", "inside_steps_s", "between_steps_s",
    "replay_review_s", "tail_wait_exit_s", "split_residual_s",
    "executing_code_s", "waiting_for_user_s", "runtime_overhead_s",
    "steps_recorded", "steps_ok", "steps_failed", "tokens", "cost_usd",
]

STEP_TIMING_COLUMNS = [
    "case", "order", "kind", "step_id", "type",
    "wall_s", "exec_s", "wait_s", "runs", "status", "error", "run",
]


def collect_timing(cases: List[Dict[str, str]], log: List[str]
                   ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """``(summary rows, per-step rows)`` for every case, tagged with its label."""
    timing_rows: List[Dict[str, Any]] = []
    step_rows: List[Dict[str, Any]] = []
    for case in cases:
        label = case["subject"] or case["run"]
        timing = parse_timing(case["timing"])
        if timing:
            timing["case"], timing["run"] = label, case["run"]
            timing_rows.append(timing)
        else:
            log.append("%s: no timing.txt in Statistic/" % label)
        steps = parse_timing_steps(case["timing"])
        for step in steps:
            step["case"], step["run"] = label, case["run"]
        step_rows.extend(steps)
        if timing and not steps:
            log.append("   [!] %s: the timing report has a summary but no "
                       "per-step timeline (written before the timeline existed?)"
                       % label)
    return timing_rows, step_rows


#: (term, definition) for the Timing sheet. Two clocks are measured and it
#: matters which is which, so both are spelled out where the numbers are.
TIMING_DEFINITIONS = [
    ("the two clocks",
     "Every step has a WALL time and an EXEC time. wall is screen to screen -- "
     "how long the step was in front of the user, including their own thinking "
     "and hand movements. exec is the time inside SafeExecutor actually running "
     "generated code. wait = wall - exec is therefore the human (or the "
     "runtime's own overhead), and it is usually the larger of the two."),
    ("case / run", "The subject, and the run folder the numbers came from."),
    ("procedure / condition / status / model",
     "Which workflow, which experimental condition, how the run ended "
     "(completed / cancelled / running), and the model behind the routing call."),
    ("send_clicked / exit_clicked",
     "When the user pressed Send, and when they pressed Exit."),
    ("total_s",
     "The whole run, Send click to Exit click. Anchored to the CLICK, not to "
     "the moment the router answered, so the seconds the user spent waiting for "
     "the routing call are inside it."),
    ("startup_s", "From the Send click until step 1 appeared."),
    ("routing_call_s",
     "The single model call that chose which procedure the request meant. The "
     "only model call a clean guided run makes."),
    ("inside_steps_s", "Summed wall time of the steps themselves."),
    ("between_steps_s", "Gaps between steps -- the runtime's auto-advance."),
    ("replay_review_s",
     "Time spent scrubbing the replay timeline. Taken OUT of the step that was "
     "on screen, so it is not mistaken for thinking time on that step."),
    ("tail_wait_exit_s", "After the last step finished, waiting for Exit."),
    ("split_residual_s",
     "total_s minus the five components above. Should be ~0; anything else "
     "means the per-step clocks and the run clock disagree, and it is printed "
     "rather than hidden so a reader can see that."),
    ("executing_code_s", "Total time inside SafeExecutor across the run."),
    ("waiting_for_user_s",
     "wall - exec summed over the steps a human answers (choices, "
     "interactions, reviews, branches)."),
    ("runtime_overhead_s",
     "wall - exec summed over the automated steps -- what the runtime spent "
     "around the code rather than in it."),
    ("steps_recorded / steps_ok / steps_failed", "Step counts for the run."),
    ("tokens / cost_usd", "Model usage for the run (the routing call, plus any "
                          "self-correction)."),
]

STEP_TIMING_DEFINITIONS = [
    ("order", "Position in the run's timeline, in the order things happened."),
    ("kind",
     "'step visit' or 'replay review'. A step re-run after a step-back appears "
     "twice, with the '<< step back' review row between them."),
    ("step_id / type",
     "The cookbook step, and its operation type (user_choice, extension_op, "
     "slicer_op, user_interaction, branch_op, review_op)."),
    ("wall_s", "Screen to screen for THIS visit, including the user's own time."),
    ("exec_s",
     "SafeExecutor time for this visit, accumulated across the pre and post "
     "templates, any self-correction retries, and any loop iterations -- so it "
     "is the total for the visit, not the last execution's duration."),
    ("wait_s", "wall_s - exec_s."),
    ("runs", "How many executions the visit involved."),
    ("status / error", "How the step ended, and the message if it failed."),
]


def timing_sheet(timing_rows: List[Dict[str, Any]],
                 step_rows: List[Dict[str, Any]]):
    """The ``Timing`` sheet, so every procedure's workbook reads the same."""
    from_pairs = [{"term": term, "definition": text}
                  for term, text in TIMING_DEFINITIONS]
    step_pairs = [{"term": term, "definition": text}
                  for term, text in STEP_TIMING_DEFINITIONS]
    return ("Timing", [
        ("Per-run summary, parsed from Statistic/timing.txt. The five *_s "
         "columns after total_s sum to it; split_residual_s is what is left "
         "over and should be ~0.",
         TIMING_COLUMNS, timing_rows),
        ("Per-step detail, in the order things happened. A step re-run after "
         "a step-back appears twice, with the '<< step back' review between "
         "them. wall = screen to screen (includes the surgeon's own time), "
         "exec = inside SafeExecutor, wait = wall - exec.",
         STEP_TIMING_COLUMNS, step_rows),
        ("DEFINITIONS — per-run timing columns",
         ["term", "definition"], from_pairs),
        ("DEFINITIONS — per-step timing columns",
         ["term", "definition"], step_pairs),
    ])
