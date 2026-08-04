"""Run-log naming and artifact writing.

Every turn writes its artifacts under ``logs/<run folder>``. The folder name is
the only thing visible in a file browser, so it carries the five facts a reader
needs before opening anything:

    ZygomaticImplantPlanner_baoyawen_pipeline_20260803_154954
    ZygomaticImplantPlanner_baoyawen_pureLLM_cb_step_08_a1_20260803_155230
    \_____________________/\_______/\______/\__________/\_/\_____________/
         which procedure    which    which   which step  |      when
                           subject  condition          attempt

The condition token is what separates the system under test (``pipeline`` --
offline CLI generation + online runtime) from the three comparison baselines
(``pureLLM`` / ``onlineOnly`` / ``claudeCode``). The subject is the input data
set, taken from the folder the scene's data was loaded out of, so the four
conditions run on one patient sort together. ``dir Zygomatic*`` gives one
procedure, ``dir *pureLLM*`` one condition; the stamp is last, so sorting on it
(or on ``started`` in the manifest) recovers chronological order.

Inside a run, a guided workflow gets **one subfolder per step**. That is not
cosmetic: a 33-step workflow used to write every step's plan, role trace and
timing report to the same three filenames, so only the last step's survived.

Everything here is Qt-free and fail-soft: a logging failure must never abort the
run being logged.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Conditions
# ---------------------------------------------------------------------------

CONDITION_PIPELINE = "pipeline"
CONDITION_PURE_LLM = "pure_llm"
CONDITION_ONLINE_ONLY = "online_only"
CONDITION_CLAUDE_CODE = "claude_code"

#: Short token used in the folder name. camelCase so it stays readable inside a
#: long underscore-joined name without being mistaken for a separate field.
CONDITION_SLUGS = {
    CONDITION_PIPELINE: "pipeline",
    CONDITION_PURE_LLM: "pureLLM",
    CONDITION_ONLINE_ONLY: "onlineOnly",
    CONDITION_CLAUDE_CODE: "claudeCode",
}

#: Written into every manifest so a folder explains itself without the reader
#: having to know the project's vocabulary.
CONDITION_LABELS = {
    CONDITION_PIPELINE: (
        "System under test: offline CLI generation + online guided runtime"
    ),
    CONDITION_PURE_LLM: (
        "Baseline 1: pure LLM, no retrieval, no tools, no generated CLI"
    ),
    CONDITION_ONLINE_ONLY: (
        "Baseline 2: online agent with search tools, generated CLI ablated"
    ),
    CONDITION_CLAUDE_CODE: (
        "Baseline 3: external Claude Code + Slicer skill over MCP"
    ),
}

MANIFEST_NAME = "run_manifest.json"

#: Sub-folder of a RUN folder holding what that run leaves for analysis: the
#: human-readable timing report and a flat save of the scene it produced. Inside
#: the run rather than beside it, so a run folder is self-contained -- copying
#: or deleting one takes its statistics with it.
STATISTIC_DIRNAME = "Statistic"

#: The OTHER of a run folder's two subfolders: everything written while the run
#: executes -- the manifest, the routing call, one folder per step, the role
#: trace. A run folder therefore has exactly two children, and which one a
#: reader wants is answerable from the name: ``Statistic/`` is the report and
#: the scene it produced, ``runtime/`` is the evidence behind them.
RUNTIME_DIRNAME = "runtime"

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")
_TRAILING_NUMBER = re.compile(r"^(.*?)(\d+)$")


def condition_slug(condition: str) -> str:
    return CONDITION_SLUGS.get(condition, slug(condition) or "unknown")


def condition_label(condition: str) -> str:
    return CONDITION_LABELS.get(condition, str(condition))


def slug(text: Any, max_len: int = 48) -> str:
    """Filesystem-safe token: no separators, no spaces, bounded length."""
    cleaned = _UNSAFE.sub("-", str(text or "")).strip("-._")
    return cleaned[:max_len]


def pad_step(step_id: Any) -> str:
    """``cb_step_8`` -> ``cb_step_08`` so step folders sort in run order.

    Lexicographic sort is what a file browser gives you, and unpadded ids put
    step 10 before step 2. The TRUE, unpadded ``step_id`` is always recorded in
    ``step.json`` and in the manifest, so nothing downstream has to guess.
    """
    text = slug(step_id)
    match = _TRAILING_NUMBER.match(text)
    if not match:
        return text
    prefix, number = match.group(1), match.group(2)
    return f"{prefix}{int(number):02d}" if len(number) < 2 else text


def _run_folder_name(log_dir: str) -> str:
    """Name of the RUN folder, given the directory artifacts are written to.

    That directory is ``<run>/runtime`` under the two-subfolder layout and
    ``<run>`` under the old one, so the name is one level up in the first case
    and the basename in the second.
    """
    cleaned = str(log_dir or "").rstrip("/\\")
    if os.path.basename(cleaned) == RUNTIME_DIRNAME:
        cleaned = os.path.dirname(cleaned)
    return os.path.basename(cleaned)


def timestamp(epoch: Optional[float] = None) -> str:
    return time.strftime("%Y%m%d_%H%M%S", time.localtime(epoch if epoch else time.time()))


def run_dir_name(
    condition: str,
    extension: str = "",
    subject: str = "",
    step_id: str = "",
    attempt: int = 0,
    turn: int = 0,
    stamp: str = "",
) -> str:
    """Readable folder name for one run: procedure, subject, condition, when.

    ``pipeline`` + extension + subject -> ZygomaticImplantPlanner_baoyawen_pipeline_20260803_154954
    ``pipeline`` + extension           -> BoneReconstructionPlanner_pipeline_20260730_143210
    ``pipeline`` + no extension        -> task_pipeline_turn3_20260730_143210
    baseline + extension + step        -> BoneReconstructionPlanner_baoyawen_pureLLM_cb_step_08_a1_20260730_143512

    PROCEDURE FIRST, timestamp LAST. Analysis is done per procedure and per
    subject -- every run of one patient through one procedure, across the four
    conditions -- and a leading timestamp scatters exactly that grouping through
    the directory listing. The trade is that a name sort is no longer
    chronological; the stamp is still the last field, so ``sort`` on it (or on
    ``started`` in the manifest) recovers that. ``dir *pureLLM*`` still gives one
    condition and ``dir Zygomatic*`` now gives one procedure.

    ``subject`` is the input data set the run was driven from, normally derived
    from the folder the scene's data was loaded out of (see
    ``WidgetExecutionFlowMixin._sceneSubjectName``). Omitted entirely when it
    cannot be determined -- a made-up placeholder in a folder name is worse than
    a missing field, since it would silently merge two patients' runs.
    """
    parts: List[str] = [slug(extension) if extension else "task"]
    if subject:
        parts.append(slug(subject))
    parts.append(condition_slug(condition))
    if step_id:
        parts.append(pad_step(step_id))
    if condition != CONDITION_PIPELINE and attempt:
        parts.append(f"a{int(attempt)}")
    if not extension and turn:
        parts.append(f"turn{int(turn)}")
    parts.append(stamp or timestamp())
    return "_".join(part for part in parts if part)


# ---------------------------------------------------------------------------
# Fail-soft writers
# ---------------------------------------------------------------------------

def ensure_dir(path: str) -> str:
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        logger.debug("Could not create log directory %s", path, exc_info=True)
    return path


def write_text(path: str, text: str) -> str:
    """Write ``text``; return the path, or "" when it could not be written."""
    try:
        ensure_dir(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text if text is not None else "")
        return path
    except Exception:
        logger.debug("Could not write %s", path, exc_info=True)
        return ""


def append_text(path: str, text: str) -> str:
    try:
        ensure_dir(os.path.dirname(path))
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(text if text is not None else "")
        return path
    except Exception:
        logger.debug("Could not append %s", path, exc_info=True)
        return ""


def write_json(path: str, payload: Any) -> str:
    try:
        ensure_dir(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, default=str)
        return path
    except Exception:
        logger.debug("Could not write %s", path, exc_info=True)
        return ""


def write_execution(step_dir: str, execution: Optional[Dict[str, Any]],
                    extra: Optional[Dict[str, Any]] = None) -> None:
    """Persist an execution result: structured JSON plus raw stdout/stderr.

    The pipeline never wrote this at all -- success, output, errors and the
    scene delta only ever reached the role trace, which the next step then
    overwrote. That made the system under test the least-instrumented of the
    four conditions, which is backwards for the comparison.
    """
    if not execution and not extra:
        return
    execution = execution or {}
    payload = {
        "success": execution.get("success"),
        "timed_out": execution.get("timed_out"),
        "seconds": execution.get("execution_time"),
        "error": execution.get("error") or "",
        "output_chars": len(execution.get("output") or ""),
    }
    payload.update(extra or {})
    write_json(os.path.join(step_dir, "execution.json"), payload)

    output = execution.get("output") or ""
    error = execution.get("error") or ""
    if output or error:
        body = ""
        if output:
            body += "===== stdout =====\n" + output + "\n"
        if error:
            body += "===== stderr / error =====\n" + error + "\n"
        write_text(os.path.join(step_dir, "output.txt"), body)


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

class RunManifest:
    """``run_manifest.json``: what this folder is, without opening anything else.

    Rewritten on every mutation rather than at the end, because a Slicer session
    that hangs or is killed mid-workflow is a normal outcome during evaluation
    and the partial run is still data.
    """

    SCHEMA = "slicer_ai_agent.run_manifest/2"

    def __init__(self, log_dir: str, condition: str, **fields):
        self.log_dir = log_dir
        self.data: Dict[str, Any] = {
            "schema": self.SCHEMA,
            "condition": condition,
            "condition_label": condition_label(condition),
            # The RUN folder, not the directory the manifest sits in. Since the
            # manifest moved into `<run>/runtime/`, a plain basename here reports
            # every run as "runtime" -- which is what the timing report prints
            # and what scripts/collect_runs.py keys its rows on.
            "folder": _run_folder_name(log_dir),
            "started": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "started_epoch": round(time.time(), 3),
            "status": "running",
            "steps": [],
        }
        self.data.update({k: v for k, v in fields.items() if v is not None})
        self.write()

    def update(self, **fields) -> "RunManifest":
        self.data.update(fields)
        return self.write()

    def set_totals(self, **totals) -> "RunManifest":
        current = dict(self.data.get("totals") or {})
        current.update(totals)
        self.data["totals"] = current
        return self.write()

    def find_step(self, step_id: str, attempt: int = 1) -> Optional[Dict[str, Any]]:
        """The live step entry, or None. Mutating it requires a write() after."""
        for entry in self.data["steps"]:
            if entry.get("step_id") == step_id and int(entry.get("attempt", 1)) == attempt:
                return entry
        return None

    def add_step(self, step_id: str, **fields) -> "RunManifest":
        """Upsert one step entry, keyed by (step_id, attempt)."""
        attempt = int(fields.get("attempt", 1) or 1)
        entry = self.find_step(step_id, attempt)
        if entry is not None:
            entry.update({k: v for k, v in fields.items() if v is not None})
            return self.write()
        entry = {"step_id": step_id, "attempt": attempt,
                 "index": len(self.data["steps"]) + 1}
        entry.update({k: v for k, v in fields.items() if v is not None})
        self.data["steps"].append(entry)
        return self.write()

    # ------------------------------------------------------------------
    # Per-step wall clock
    #
    # ``seconds`` (written by the execution recorder) is the time SafeExecutor
    # spent running that step's code -- machine time. It is NOT how long the
    # step took: a ``user_choice`` step whose code runs in 8 ms can sit on
    # screen for a minute while the surgeon picks a node, and a
    # ``user_interaction`` step is almost entirely hand time. Measuring a guided
    # run therefore needs a second clock, taken at the two moments the step is
    # actually visible to the user: when it OPENS and when the workflow moves
    # past it.
    # ------------------------------------------------------------------
    def open_step(self, step_id: str, action: str = "", **fields) -> "RunManifest":
        """Upsert a step and stamp when it opened -- ONCE, however often it is
        dispatched.

        A step is dispatched more than once by design (``start`` shows the
        picker or arms the interaction, ``choice_made`` / ``proceed`` completes
        it) and a loop body is dispatched once per iteration. Re-stamping on
        each would move the step's start to the moment the user answered it,
        erasing exactly the interval this exists to measure. ``opens`` and
        ``dispatches`` are counted instead, so a step that ran three times in a
        loop stays legible as one entry.
        """
        attempt = int(fields.get("attempt", 1) or 1)
        self.add_step(step_id, action=action or None, **fields)
        entry = self.find_step(step_id, attempt)
        if entry is None:
            return self.write()
        now = round(time.time(), 3)
        if not entry.get("opened_epoch"):
            entry["opened_epoch"] = now  # first open; never moves
        # A step can be VISITED more than once: a repeat block re-arms its body
        # and re-dispatches every member with action="start" (6 of the 9
        # generated workflows have multi-step loop bodies), and the replay
        # stepper and the baseline harness both re-run a step the same way.
        # Measuring last-completion minus first-open would then make each body
        # step's span cover the WHOLE loop, including its siblings' time: the
        # per-step spans overlap, their sum exceeds the run it is being reported
        # against, and a neighbouring interaction's hand time is printed as an
        # automated step's overhead. So a re-visit banks the span that just
        # closed and starts a new one, and wall_seconds is their sum.
        #
        # Keyed on action="start" specifically: the completion dispatches within
        # one visit (choice_made / proceed / skip) must NOT close the span, or a
        # choice step's think time and an interaction step's placement time --
        # the whole point of this clock -- would be dropped.
        if action == "start" and entry.get("span_opened_epoch"):
            # Close the previous visit at its completion if it had one, and at
            # NOW if it did not. A visit with no completion was ABANDONED -- a
            # step-back re-ran the workflow from an earlier step, or a stale
            # auto-advance opened this step and the rewind moved past it. Before
            # this branch handled that case, the old span stayed open and the
            # next visit's finish_step measured from it, charging this step
            # everything in between (observed: a branch_op reporting 60.6 s for
            # a 5.3 s visit, which pushed the run's per-step total 64 s past the
            # run itself). A step cannot be in two visits at once.
            closed_at = entry.get("completed_epoch") or now
            try:
                entry["wall_banked"] = round(
                    float(entry.get("wall_banked") or 0.0)
                    + float(closed_at) - float(entry["span_opened_epoch"]), 3
                )
            except (TypeError, ValueError):
                logger.debug("Bad span for step %s", step_id, exc_info=True)
            entry["span_opened_epoch"] = now
            entry.pop("completed_epoch", None)
            self._timeline_close("step", step_id, status="abandoned")
        elif not entry.get("span_opened_epoch"):
            entry["span_opened_epoch"] = now
        entry["dispatches"] = int(entry.get("dispatches", 0)) + 1
        if action == "start":
            entry["opens"] = int(entry.get("opens", 0)) + 1
            # A new visit starts clean. `add_step` MERGES fields, so an error
            # from a previous attempt survives into a re-run that then succeeds
            # -- and the report prints it under the successful row, which reads
            # as a step that failed and was recorded ok.
            if not fields.get("error"):
                entry.pop("error", None)
            # One timeline row per visit, so a re-run after a rewind is its own
            # row rather than being folded into the first visit's total.
            self._timeline_open(
                "step", step_id=step_id,
                operation_type=fields.get("operation_type") or entry.get("operation_type"),
                description=entry.get("description"),
            )
        return self.write()

    def finish_step(self, step_id: str, exec_seconds: Optional[float] = None,
                    **fields) -> "RunManifest":
        """Stamp when a step completed and accumulate its execution time.

        ``completed_epoch`` closes the CURRENT visit (an interactive step
        completes on its post-template); ``wall_seconds`` is that visit plus
        every visit banked by ``open_step``. ``exec_seconds_total`` ACCUMULATES
        rather than overwrites, because a step can run code more than once --
        pre + post templates, self-correction retries, loop iterations -- and
        the last run's duration is not the step's cost. ``seconds`` keeps its
        old meaning (the last execution) so ``scripts/collect_runs.py`` is
        unaffected.
        """
        attempt = int(fields.get("attempt", 1) or 1)
        self.add_step(step_id, **fields)
        entry = self.find_step(step_id, attempt)
        if entry is None:
            return self.write()
        entry["completed_epoch"] = round(time.time(), 3)
        if exec_seconds is not None:
            try:
                entry["exec_seconds_total"] = round(
                    float(entry.get("exec_seconds_total") or 0.0) + float(exec_seconds), 6
                )
                entry["executions"] = int(entry.get("executions", 0)) + 1
            except (TypeError, ValueError):
                logger.debug("Bad exec_seconds for step %s", step_id, exc_info=True)
        opened = entry.get("span_opened_epoch")
        if not opened and not entry.get("wall_banked"):
            # No banked visits either: fall back to the first open, as before.
            opened = entry.get("opened_epoch")
        try:
            banked = float(entry.get("wall_banked") or 0.0)
            if opened:
                # A step suspended for replay has no open span; completing while
                # suspended must not re-measure from its FIRST open, which would
                # silently pull the whole review back into this step.
                entry["wall_seconds"] = round(
                    banked + float(entry["completed_epoch"]) - float(opened), 3)
            elif banked:
                entry["wall_seconds"] = round(banked, 3)
        except (TypeError, ValueError):
            logger.debug("Bad opened_epoch for step %s", step_id, exc_info=True)
        row = self._timeline_find_open("step", step_id)
        if row is not None:
            if exec_seconds is not None:
                try:
                    row["exec_seconds"] = round(
                        float(row.get("exec_seconds") or 0.0) + float(exec_seconds), 6)
                except (TypeError, ValueError):
                    pass
            row["status"] = entry.get("status") or "ok"
            row["error"] = str(entry.get("error") or "")
            self._timeline_close("step", step_id)
        return self.write()

    # ------------------------------------------------------------------
    # Timeline: one row per ACTIVITY, in the order they happened
    #
    # ``steps`` aggregates a step's visits into one entry (wall = their sum,
    # runs = 2o/2x), which answers "what did this step cost in total" but cannot
    # answer "what happened, in order" -- a step re-run after a rewind is
    # indistinguishable from a loop iteration, and the review between them is
    # invisible. The timeline records each VISIT and each REPLAY span as its own
    # row, so the whole run reads top to bottom in one table. Kept ALONGSIDE
    # ``steps`` rather than replacing it: scripts/collect_runs.py reads that.
    # ------------------------------------------------------------------
    def _timeline(self) -> List[Dict[str, Any]]:
        return self.data.setdefault("timeline", [])

    def _timeline_open(self, kind: str, **fields) -> Dict[str, Any]:
        entry = {"kind": kind, "opened_epoch": round(time.time(), 3)}
        entry.update({k: v for k, v in fields.items() if v is not None})
        self._timeline().append(entry)
        return entry

    def _timeline_find_open(self, kind: str, step_id: str = "") -> Optional[Dict[str, Any]]:
        for entry in reversed(self._timeline()):
            if entry.get("kind") != kind or entry.get("completed_epoch"):
                continue
            if step_id and entry.get("step_id") != step_id:
                continue
            return entry
        return None

    def _timeline_close(self, kind: str, step_id: str = "", **fields) -> Optional[Dict[str, Any]]:
        entry = self._timeline_find_open(kind, step_id)
        if entry is None:
            return None
        # `boundary_epoch` closes the row THERE rather than now, and never
        # before it opened -- a visit that existed only inside a replay preview
        # then measures zero instead of overlapping the review row.
        boundary = fields.pop("boundary_epoch", None)
        closed = round(time.time(), 3)
        if boundary is not None:
            closed = max(float(entry.get("opened_epoch") or boundary), float(boundary))
        entry["completed_epoch"] = closed
        entry.update({k: v for k, v in fields.items() if v is not None})
        return entry

    # ------------------------------------------------------------------
    # Replay scrubbing: its own bucket, taken OUT of the step it interrupts
    # ------------------------------------------------------------------
    def suspend_step_span(self, step_id: str, attempt: int = 1) -> "RunManifest":
        """Close a step's open visit WITHOUT completing it.

        Pressing Back leaves the live step on screen but stops it being what the
        surgeon is doing. Without this, the whole review lands in that step's
        ``wall`` and -- since ``exec`` does not move -- is reported as think time
        on a step nobody was thinking about. Banking the span here and reopening
        it in ``resume_step_span`` moves that interval into the replay bucket,
        which is what lets the four-way split still sum to the run.
        """
        entry = self.find_step(step_id, attempt)
        if entry is None or not entry.get("span_opened_epoch"):
            return self
        try:
            entry["wall_banked"] = round(
                float(entry.get("wall_banked") or 0.0)
                + round(time.time(), 3) - float(entry["span_opened_epoch"]), 3
            )
        except (TypeError, ValueError):
            logger.debug("Bad span while suspending %s", step_id, exc_info=True)
        entry.pop("span_opened_epoch", None)
        # The timeline row closes with it. A suspended visit that stayed open
        # would print as "-" and its seconds would be missing from the table
        # even though they are inside the run -- the wall column has to sum to
        # the total, so every interval that was banked must appear as a row.
        self._timeline_close("step", step_id, status="stepped back")
        return self.write()

    def resume_step_span(self, step_id: str, attempt: int = 1) -> "RunManifest":
        """Reopen the visit closed by ``suspend_step_span`` as a NEW row.

        Only Forward-back-to-live gets here. "Run from here" abandons the
        suspended step and re-dispatches an earlier one, which ``open_step``
        records as its own visit -- resuming here as well would leave a second,
        empty row for a step the run never returned to.
        """
        entry = self.find_step(step_id, attempt)
        if entry is None or entry.get("span_opened_epoch"):
            return self
        entry["span_opened_epoch"] = round(time.time(), 3)
        self._timeline_open(
            "step", step_id=step_id,
            operation_type=entry.get("operation_type"),
            description=entry.get("description"),
            resumed=True,
        )
        return self.write()

    def replay_enter(self, from_step: str = "") -> "RunManifest":
        """Start counting review time (the first Back of a scrubbing session)."""
        replay = self.data.setdefault("replay", {"seconds": 0.0, "events": []})
        if not replay.get("entered_epoch"):
            replay["entered_epoch"] = round(time.time(), 3)
            # Its own timeline row, opened where the scrubbing began and closed
            # when the user leaves the preview -- so the table shows the review
            # between the step it interrupted and the step it resumed at.
            self._timeline_open("replay", step_id=from_step or "")
        return self.write()

    def replay_exit(self, resumed_at: str = "", ended_by: str = "") -> "RunManifest":
        """Stop counting review time and bank it (Forward to live, or a re-run)."""
        replay = self.data.get("replay") or {}
        entered = replay.get("entered_epoch")
        if not entered:
            return self
        try:
            replay["seconds"] = round(
                float(replay.get("seconds") or 0.0)
                + round(time.time(), 3) - float(entered), 3
            )
        except (TypeError, ValueError):
            logger.debug("Bad replay span", exc_info=True)
        entered = float(entered)
        replay.pop("entered_epoch", None)
        if ended_by == "rerun":
            # Leaving the preview by re-running rewinds the workflow, so no step
            # visit survives it. Bounded at the moment review began: anything
            # after that is review time, already banked above.
            self.abandon_open_spans(entered)
        events = replay.get("events") or []
        backs = sum(1 for e in events if e.get("action") == "back")
        fwds = sum(1 for e in events if e.get("action") == "forward")
        self._timeline_close("replay", navigations=len(events), backs=backs,
                             forwards=fwds, resumed_at=resumed_at or "",
                             ended_by=ended_by or "")
        return self.write()

    @staticmethod
    def _span_is_live(entry: Dict[str, Any]) -> bool:
        """Is this step's visit still running?

        `finish_step` deliberately LEAVES `span_opened_epoch` in place so a
        re-visit can bank it, so its presence alone is not "running". The span
        is live only when no completion has landed since it opened. Shared by
        every caller that ends spans in bulk -- getting it wrong there rewrites
        completed steps' walls to span the whole run, which is a plausible
        number rather than an error.
        """
        opened = entry.get("span_opened_epoch")
        if not opened:
            return False
        completed = entry.get("completed_epoch")
        try:
            return not (completed and float(completed) >= float(opened))
        except (TypeError, ValueError):
            return False

    def abandon_open_spans(self, boundary_epoch: Optional[float] = None) -> "RunManifest":
        """End every step visit still in flight, banking time only up to
        ``boundary_epoch``.

        A rewind ends whatever was on screen: the run resumes from an earlier
        step, so no later visit continues. Two things make the boundary matter
        rather than just using "now":

        - A step opened by a stale auto-advance DURING the preview (the timer
          was queued before Back was pressed) has its whole span inside the
          replay window. Banking to now would count that window twice -- once as
          review, once as that step's wall -- and the report's split would stop
          summing to the run.
        - The interval between the Back click and the rewind is review time,
          which ``suspend_step_span`` has already moved into the replay bucket
          for the step that WAS on screen.

        So the bank is clamped at zero: a visit that only existed inside the
        preview contributes nothing, which is the truth about it.
        """
        boundary = float(boundary_epoch) if boundary_epoch else round(time.time(), 3)
        for entry in self.data.get("steps") or []:
            if not self._span_is_live(entry):
                continue
            opened = entry["span_opened_epoch"]
            try:
                banked = max(0.0, boundary - float(opened))
                entry["wall_banked"] = round(
                    float(entry.get("wall_banked") or 0.0) + banked, 3)
            except (TypeError, ValueError):
                logger.debug("Bad span while abandoning %s", entry.get("step_id"),
                             exc_info=True)
                continue
            entry.pop("span_opened_epoch", None)
            entry.pop("completed_epoch", None)
            self._timeline_close("step", str(entry.get("step_id") or ""),
                                 status="abandoned", boundary_epoch=boundary)
        return self.write()

    def note_replay(self, action: str, index: Optional[int] = None,
                    step_id: str = "") -> "RunManifest":
        """Record one navigation so the trace shows WHAT was reviewed, not only
        that time passed."""
        replay = self.data.setdefault("replay", {"seconds": 0.0, "events": []})
        replay.setdefault("events", []).append({
            "action": action,
            "index": index,
            "step_id": step_id,
            "epoch": round(time.time(), 3),
        })
        return self.write()

    def reopen_step(self, step_id: str, attempt: int = 1) -> "RunManifest":
        """Undo a completion stamp for a step that turned out to be WAITING.

        An interactive step runs its PRE template on ``start``, and the
        execution recorder stamps every execution as a completion -- it runs
        before the runtime has decided whether the step is finished or is about
        to wait for the user. For an interactive step it is about to wait, so
        the stamp is retracted here and the real one lands when the POST
        template runs after Done. Without this, a run exited mid-interaction
        would record the step as completed in the fraction of a second its
        setup code took.
        """
        entry = self.find_step(step_id, attempt)
        if entry is None:
            return self
        entry.pop("completed_epoch", None)
        entry.pop("wall_seconds", None)
        entry["status"] = "running"
        for row in reversed(self._timeline()):
            if row.get("kind") == "step" and row.get("step_id") == step_id:
                row.pop("completed_epoch", None)
                break
        return self.write()

    def _seal_open_spans(self) -> None:
        """Close whatever was still running when the run ended.

        Exit can land mid-step, or while the user is still scrubbing the replay
        timeline. An interval left open renders as "-" in the report, so its
        seconds vanish from the table while still being inside the run -- the
        wall column stops summing to the total, and (for a step) the time gets
        counted a second time in the after-the-last-step tail, which measures
        from the last COMPLETED step. Sealing here records what actually
        happened: the span ended because the run did.
        """
        now = round(time.time(), 3)
        replay = self.data.get("replay") or {}
        if replay.get("entered_epoch"):
            try:
                replay["seconds"] = round(
                    float(replay.get("seconds") or 0.0)
                    + now - float(replay["entered_epoch"]), 3)
            except (TypeError, ValueError):
                logger.debug("Bad replay span at seal", exc_info=True)
            replay.pop("entered_epoch", None)
            self._timeline_close("replay", ended_by="exit")
        for entry in self.data.get("steps") or []:
            if not self._span_is_live(entry):
                continue
            opened = entry["span_opened_epoch"]
            try:
                entry["wall_seconds"] = round(
                    float(entry.get("wall_banked") or 0.0) + now - float(opened), 3)
            except (TypeError, ValueError):
                logger.debug("Bad span at seal for %s", entry.get("step_id"), exc_info=True)
                continue
            entry.pop("span_opened_epoch", None)
            entry["completed_epoch"] = now
            entry["ended_at_exit"] = True
            self._timeline_close("step", str(entry.get("step_id") or ""),
                                 status="open at exit")

    def finish(self, status: str = "completed", **fields) -> "RunManifest":
        self._seal_open_spans()
        self.data["status"] = status
        self.data["finished"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        started = self.data.get("started_epoch")
        if started:
            self.data["seconds"] = round(time.time() - float(started), 3)
        self.data.update(fields)
        return self.write()

    def write(self) -> "RunManifest":
        steps = self.data.get("steps") or []
        self.data["step_count"] = len(steps)
        self.data["steps_ok"] = sum(1 for s in steps if s.get("status") == "ok")
        self.data["steps_failed"] = sum(1 for s in steps if s.get("status") == "failed")
        write_json(os.path.join(self.log_dir, MANIFEST_NAME), self.data)
        return self


# ---------------------------------------------------------------------------
# Statistics: the human-readable timing report written when a run is closed
# ---------------------------------------------------------------------------

#: Step types where the wall clock is dominated by a person, so `wall - exec`
#: is the surgeon's time and not the runtime's overhead. Kept as an explicit
#: set (not "everything that is not automated") so an operation type added
#: later is reported as overhead until someone decides it waits for a human.
HUMAN_IN_LOOP_TYPES = frozenset({
    "user_choice", "user_interaction", "branch_op", "review_op",
})


def _fmt_seconds(value: Optional[float], width: int = 9) -> str:
    if value is None:
        return "-".rjust(width)
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "-".rjust(width)
    if value >= 60:
        return f"{int(value // 60)}m{value % 60:04.1f}s".rjust(width)
    return f"{value:.2f}s".rjust(width)


def _fmt_clock(epoch: Optional[float]) -> str:
    if not epoch:
        return "unknown"
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(epoch)))
    except (TypeError, ValueError):
        return "unknown"


def _fmt_duration(seconds: Optional[float]) -> str:
    if seconds is None:
        return "unknown"
    seconds = float(seconds)
    if seconds < 60:
        return f"{seconds:.1f} s"
    minutes, rest = divmod(seconds, 60)
    if minutes < 60:
        return f"{seconds:.1f} s  ({int(minutes)} min {rest:04.1f} s)"
    hours, minutes = divmod(int(minutes), 60)
    return f"{seconds:.1f} s  ({hours} h {minutes} min {rest:04.1f} s)"


def build_run_statistics(manifest: Dict[str, Any], exit_epoch: float,
                         scene_dir: str = "", scene_note: str = "") -> str:
    """Render one guided run's timing as a human-readable report.

    Pure function of the manifest, so the same text can be re-derived later
    from ``run_manifest.json`` alone -- nothing here is computed from state that
    only existed while Slicer was running.
    """
    steps = list(manifest.get("steps") or [])
    send_epoch = manifest.get("send_clicked_epoch") or manifest.get("started_epoch")
    router = manifest.get("router") or {}

    opened = [float(s["opened_epoch"]) for s in steps if s.get("opened_epoch")]
    completed = [float(s["completed_epoch"]) for s in steps if s.get("completed_epoch")]
    first_open = min(opened) if opened else None
    last_complete = max(completed) if completed else None

    total = (exit_epoch - float(send_epoch)) if send_epoch else None
    startup = (first_open - float(send_epoch)) if (send_epoch and first_open) else None
    tail = (exit_epoch - last_complete) if last_complete else None

    def _wall(step):
        value = step.get("wall_seconds")
        return float(value) if value is not None else None

    def _exec(step):
        value = step.get("exec_seconds_total")
        if value is None:
            value = step.get("seconds")
        return float(value) if value is not None else None

    step_wall = sum(w for w in (_wall(s) for s in steps) if w is not None)
    step_exec = sum(e for e in (_exec(s) for s in steps) if e is not None)
    human_wait = 0.0
    machine_overhead = 0.0
    for step in steps:
        wall, execs = _wall(step), _exec(step) or 0.0
        if wall is None:
            continue
        wait = max(0.0, wall - execs)
        if str(step.get("operation_type") or "") in HUMAN_IN_LOOP_TYPES:
            human_wait += wait
        else:
            machine_overhead += wait
    # Time spent scrubbing the replay timeline. Its own term because
    # suspend_step_span takes it OUT of the step that was on screen -- so it is
    # neither step time nor a gap, and the identity below only closes if it is
    # subtracted explicitly.
    replay_info = manifest.get("replay") or {}
    replay = float(replay_info.get("seconds") or 0.0)
    replay_events = list(replay_info.get("events") or [])
    gaps = None
    gaps_note = ""
    if total is not None and startup is not None and tail is not None:
        gaps = total - startup - step_wall - tail - replay
        if gaps < 0:
            # Never clamped to zero. These four figures are printed under a
            # header saying they sum to the total, so a negative residual is the
            # only evidence a reader has that the per-step clocks and the run
            # clock disagree; hiding it would make the report quietly contradict
            # itself instead of saying so.
            gaps_note = ("   [!] clocks inconsistent: the per-step walls exceed "
                         f"the run by {-gaps:.1f} s")

    out: List[str] = []
    rule = "=" * 78
    thin = "-" * 78
    out.append(rule)
    out.append(" SlicerAIAgent - guided workflow run timing")
    out.append(rule)
    out.append(f" Run folder    : {manifest.get('folder', '')}")
    out.append(f" Procedure     : {manifest.get('extension') or '(none)'}")
    subject = manifest.get("subject") or ""
    if subject:
        source = manifest.get("subject_source") or ""
        out.append(f" Subject       : {subject}" + (f"   ({source})" if source else ""))
    out.append(f" Condition     : {manifest.get('condition', '')}")
    out.append(f" Final status  : {manifest.get('status', '')}")
    prompt = " ".join(str(manifest.get("prompt") or "").split())
    out.append(f" Request       : {prompt[:200] or '(not recorded)'}")
    model = manifest.get("model") or {}
    if model:
        out.append(f" Model         : {model.get('model', '?')} ({model.get('provider', '?')})")
    out.append("")
    out.append(f" Send clicked  : {_fmt_clock(send_epoch)}")
    out.append(f" Exit clicked  : {_fmt_clock(exit_epoch)}")
    out.append(f" TOTAL RUN TIME: {_fmt_duration(total)}")
    out.append("")
    parts = "five" if replay else "four"
    out.append(f" Where that time went (these {parts} sum to the total):")
    out.append(f"   startup before step 1 opened : {_fmt_duration(startup)}"
               + (f"   [routing call {float(router.get('seconds') or 0):.2f} s]" if router else ""))
    out.append(f"   inside the steps             : {_fmt_duration(step_wall)}")
    out.append(f"   between steps (auto-advance) : {_fmt_duration(gaps)}")
    if gaps_note:
        out.append(gaps_note)
    if replay:
        back = sum(1 for e in replay_events if e.get("action") == "back")
        fwd = sum(1 for e in replay_events if e.get("action") == "forward")
        rerun = sum(1 for e in replay_events if e.get("action") == "rerun")
        out.append(f"   reviewing the replay timeline: {_fmt_duration(replay)}"
                   f"   ({back} back, {fwd} forward, {rerun} re-run"
                   + ")")
    out.append(f"   after the last step, waiting for Exit : {_fmt_duration(tail)}")
    out.append("")
    out.append(" Of the time inside the steps:")
    out.append(f"   executing generated code     : {_fmt_duration(step_exec)}")
    out.append(f"   waiting for the user         : {_fmt_duration(human_wait)}"
               "   (choices, 3D interaction, review)")
    out.append(f"   runtime overhead             : {_fmt_duration(machine_overhead)}"
               "   (dispatch + panel render on automated steps)")
    out.append("")
    totals = manifest.get("totals") or {}
    out.append(f" Steps recorded: {len(steps)}   ok: {manifest.get('steps_ok', 0)}"
               f"   failed: {manifest.get('steps_failed', 0)}"
               f"   still open at exit: {sum(1 for s in steps if s.get('status') == 'running')}")
    if totals:
        out.append(f" Model cost    : {totals.get('tokens', 0)} tokens, "
                   f"${float(totals.get('cost', 0) or 0):.4f}")
        # Attribute it. A clean guided run calls the model exactly once -- to
        # route -- and the dispatched steps call none, so showing the split makes
        # that claim checkable rather than asserted, and tells a reader whether
        # any self-correction fired.
        _router = manifest.get("router") or {}
        _r_tokens = int(_router.get("tokens") or 0)
        if _r_tokens:
            _other = int(totals.get("tokens", 0) or 0) - _r_tokens
            out.append(f"                 routing call {_r_tokens} tokens, "
                       f"${float(_router.get('cost', 0) or 0):.4f}"
                       + (f"; self-correction {_other} tokens" if _other > 0 else
                          "; the dispatched steps called no model"))
    out.append("")
    timeline = list(manifest.get("timeline") or [])

    out.append(thin)
    out.append(" TIMELINE" if timeline else " PER-STEP TIMING")
    out.append(thin)
    if timeline:
        out.append(" Everything that happened, in the order it happened -- one row per")
        out.append(" step VISIT plus one row per replay review, so the whole run is a")
        out.append(" single table whose wall column sums to the TOTAL line at its foot.")
        out.append("")
    out.append(" The three clocks are NOT interchangeable:")
    out.append("   wall  from the step appearing on screen to the workflow moving past it.")
    out.append("         For a step you answer this INCLUDES your own thinking/drawing time.")
    out.append("   exec  wall-clock inside SafeExecutor running that step's generated code,")
    out.append("         summed over every execution (pre+post templates, repair retries,")
    out.append("         loop iterations).")
    out.append("   wait  wall - exec. On a user_choice / user_interaction / branch_op /")
    out.append("         review_op step this is the surgeon; on an automated step it is")
    out.append("         dispatch + panel render.")
    if timeline:
        out.append("   runs  'visit' -- each row is one visit. A step re-run after a")
        out.append("         step-back gets its own row rather than being summed into")
        out.append("         the first one, so a loop body shows each iteration.")
        out.append("")
        out.append(" A '<< step back' row is a review of the replay timeline: from pressing")
        out.append(" Back to the run resuming (a re-run from a step, or Forward back to live).")
        out.append(" That time is NOT charged to the step that was on screen -- the step's")
        out.append(" clock is suspended while you scrub -- so the rows never overlap.")
    else:
        out.append("   runs  how many times the step was opened (>1 means a loop iteration)")
        out.append("         and how many times it executed code.")
    out.append("")
    header = (f" {'#':>3} {'step_id':<14} {'type':<16} {'wall':>9} {'exec':>9} "
              f"{'wait':>9}  {'runs':>7}  status")
    out.append(header)
    out.append(" " + "-" * (len(header) - 1))

    if timeline:
        # Chronological: one row per VISIT and one per replay span, in the order
        # they happened. A step re-run after a rewind is a separate row from its
        # first visit, and the review that separates them sits between the two --
        # so "stepped back at 20, resumed at 10" reads directly off the table
        # instead of having to be inferred from a 2o/2x in an aggregate row.
        index = 0
        for entry in timeline:
            opened = entry.get("opened_epoch")
            closed = entry.get("completed_epoch")
            wall = (float(closed) - float(opened)) if (opened and closed) else None
            index += 1
            if entry.get("kind") == "replay":
                # No exec: nothing runs while scrubbing, so the whole span is
                # wait -- which is what keeps the wall and wait columns' totals
                # equal to the split's replay term.
                navs = int(entry.get("navigations") or 0)
                resumed = str(entry.get("resumed_at") or "")
                where = str(entry.get("step_id") or "?")
                # How it ended is the useful half: "re-ran from" means the run
                # was rewound and that step executed again (so the rows below
                # repeat), "returned to" means nothing was re-executed.
                verb = ("re-ran from" if entry.get("ended_by") == "rerun"
                        else "returned to")
                out.append(
                    f" {index:>3} {'<< step back':<14} {'(replay review)':<16} "
                    f"{_fmt_seconds(wall)} {_fmt_seconds(None)} {_fmt_seconds(wall)}  "
                    f"{str(navs) + ' nav':>7}  "
                    + (f"left {where}" if where != "?" else "scrubbed")
                    + (f", {verb} {resumed}" if resumed else "")
                    + ("" if closed else "   (still previewing at exit)")
                )
                continue
            execs = entry.get("exec_seconds")
            execs = float(execs) if execs is not None else None
            wait = None if wall is None else max(0.0, wall - (execs or 0.0))
            status = str(entry.get("status") or "")
            if not closed:
                status = (status or "running") + " (open at exit)"
            out.append(
                f" {index:>3} {str(entry.get('step_id', ''))[:14]:<14} "
                f"{str(entry.get('operation_type') or '?')[:16]:<16} "
                f"{_fmt_seconds(wall)} {_fmt_seconds(execs)} {_fmt_seconds(wait)}  "
                f"{'visit':>7}  {status}"
            )
            error = " ".join(str(entry.get("error") or "").split())
            if error:
                out.append(f"      error: {error[:160]}")
    else:
        # Runs recorded before the timeline existed: the aggregate view.
        for step in steps:
            wall, execs = _wall(step), _exec(step)
            wait = None if wall is None else max(0.0, wall - (execs or 0.0))
            runs = f"{int(step.get('opens', 0) or 0)}o/{int(step.get('executions', 0) or 0)}x"
            status = str(step.get("status") or "?")
            if not step.get("completed_epoch"):
                status += " (open at exit)" if status == "running" else " (no clock)"
            out.append(
                f" {int(step.get('index', 0)):>3} {str(step.get('step_id', ''))[:14]:<14} "
                f"{str(step.get('operation_type') or '?')[:16]:<16} "
                f"{_fmt_seconds(wall)} {_fmt_seconds(execs)} {_fmt_seconds(wait)}  "
                f"{runs:>7}  {status}"
            )
            error = str(step.get("error") or "").strip()
            if error:
                out.append(f"      error: {' '.join(error.split())[:160]}")
    out.append(" " + "-" * (len(header) - 1))
    out.append(f" {'':>3} {'TOTAL':<14} {'':<16} "
               f"{_fmt_seconds(step_wall + replay)} "
               f"{_fmt_seconds(step_exec)} "
               f"{_fmt_seconds(human_wait + machine_overhead + replay)}")
    out.append("")

    by_type: Dict[str, List[float]] = {}
    for step in steps:
        wall = _wall(step)
        if wall is None:
            continue
        key = str(step.get("operation_type") or "?")
        bucket = by_type.setdefault(key, [0.0, 0.0, 0.0])
        bucket[0] += 1
        bucket[1] += wall
        bucket[2] += _exec(step) or 0.0
    if by_type:
        out.append(thin)
        out.append(" BY OPERATION TYPE")
        out.append(thin)
        out.append(f" {'type':<18} {'steps':>6} {'wall':>10} {'exec':>10} {'wait':>10}")
        for key in sorted(by_type, key=lambda k: -by_type[k][1]):
            count, wall, execs = by_type[key]
            out.append(f" {key:<18} {int(count):>6} {_fmt_seconds(wall, 10)} "
                       f"{_fmt_seconds(execs, 10)} {_fmt_seconds(wall - execs, 10)}")
        out.append("")

    out.append(thin)
    out.append(" SCENE SNAPSHOT")
    out.append(thin)
    if scene_dir:
        out.append(f" Saved to: {scene_dir}")
    if scene_note:
        out.append(f" {scene_note}")
    if not scene_dir and not scene_note:
        out.append(" (not saved)")
    out.append("")
    out.append(rule)
    return "\n".join(out) + "\n"
