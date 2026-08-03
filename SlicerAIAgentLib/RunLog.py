"""Run-log naming and artifact writing.

Every turn writes its artifacts under ``logs/<run folder>``. The folder name is
the only thing visible in a file browser, so it carries the four facts a reader
needs before opening anything:

    20260730_143210_pipeline_BoneReconstructionPlanner
    20260730_143512_pureLLM_BoneReconstructionPlanner_cb_step_08_a1
    \_______________/\______/\______________________/\__________/\_/
        when         which        which procedure      which step  attempt
                    condition

The condition token is what separates the system under test (``pipeline`` --
offline CLI generation + online runtime) from the three comparison baselines
(``pureLLM`` / ``onlineOnly`` / ``claudeCode``). Sorting by name gives
chronological order; ``dir *pureLLM*`` gives one condition.

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


def timestamp(epoch: Optional[float] = None) -> str:
    return time.strftime("%Y%m%d_%H%M%S", time.localtime(epoch if epoch else time.time()))


def run_dir_name(
    condition: str,
    extension: str = "",
    step_id: str = "",
    attempt: int = 0,
    turn: int = 0,
    stamp: str = "",
) -> str:
    """Readable, sortable folder name for one run.

    ``pipeline`` + extension           -> 20260730_143210_pipeline_BoneReconstructionPlanner
    ``pipeline`` + no extension        -> 20260730_143210_pipeline_task_turn3
    baseline + extension + step        -> 20260730_143512_pureLLM_BoneReconstructionPlanner_cb_step_08_a1
    """
    parts: List[str] = [stamp or timestamp(), condition_slug(condition)]
    parts.append(slug(extension) if extension else "task")
    if step_id:
        parts.append(pad_step(step_id))
    if condition != CONDITION_PIPELINE and attempt:
        parts.append(f"a{int(attempt)}")
    if not extension and turn:
        parts.append(f"turn{int(turn)}")
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
            "folder": os.path.basename(log_dir),
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
        if action == "start" and entry.get("span_opened_epoch") and entry.get("completed_epoch"):
            try:
                entry["wall_banked"] = round(
                    float(entry.get("wall_banked") or 0.0)
                    + float(entry["completed_epoch"]) - float(entry["span_opened_epoch"]), 3
                )
            except (TypeError, ValueError):
                logger.debug("Bad span for step %s", step_id, exc_info=True)
            entry["span_opened_epoch"] = now
            entry.pop("completed_epoch", None)
        elif not entry.get("span_opened_epoch"):
            entry["span_opened_epoch"] = now
        entry["dispatches"] = int(entry.get("dispatches", 0)) + 1
        if action == "start":
            entry["opens"] = int(entry.get("opens", 0)) + 1
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
        opened = entry.get("span_opened_epoch") or entry.get("opened_epoch")
        if opened:
            try:
                entry["wall_seconds"] = round(
                    float(entry.get("wall_banked") or 0.0)
                    + float(entry["completed_epoch"]) - float(opened), 3
                )
            except (TypeError, ValueError):
                logger.debug("Bad opened_epoch for step %s", step_id, exc_info=True)
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
        return self.write()

    def finish(self, status: str = "completed", **fields) -> "RunManifest":
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

#: Sub-folder of a RUN folder holding what that run leaves for analysis: the
#: human-readable timing report and a flat save of the scene it produced. Inside
#: the run rather than beside it, so a run folder is self-contained -- copying
#: or deleting one takes its statistics with it.
STATISTIC_DIRNAME = "Statistic"

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
    gaps = None
    gaps_note = ""
    if total is not None and startup is not None and tail is not None:
        gaps = total - startup - step_wall - tail
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
    out.append(" Where that time went (these four sum to the total):")
    out.append(f"   startup before step 1 opened : {_fmt_duration(startup)}"
               + (f"   [routing call {float(router.get('seconds') or 0):.2f} s]" if router else ""))
    out.append(f"   inside the steps             : {_fmt_duration(step_wall)}")
    out.append(f"   between steps (auto-advance) : {_fmt_duration(gaps)}")
    if gaps_note:
        out.append(gaps_note)
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
    out.append("")
    out.append(thin)
    out.append(" PER-STEP TIMING")
    out.append(thin)
    out.append(" The three clocks are NOT interchangeable:")
    out.append("   wall  from the step appearing on screen to the workflow moving past it.")
    out.append("         For a step you answer this INCLUDES your own thinking/drawing time.")
    out.append("   exec  wall-clock inside SafeExecutor running that step's generated code,")
    out.append("         summed over every execution (pre+post templates, repair retries,")
    out.append("         loop iterations).")
    out.append("   wait  wall - exec. On a user_choice / user_interaction / branch_op /")
    out.append("         review_op step this is the surgeon; on an automated step it is")
    out.append("         dispatch + panel render.")
    out.append("   runs  how many times the step was opened (>1 means a loop iteration)")
    out.append("         and how many times it executed code.")
    out.append("")
    header = (f" {'#':>3} {'step_id':<14} {'type':<16} {'wall':>9} {'exec':>9} "
              f"{'wait':>9}  {'runs':>7}  status")
    out.append(header)
    out.append(" " + "-" * (len(header) - 1))
    for step in steps:
        wall, execs = _wall(step), _exec(step)
        wait = None if wall is None else max(0.0, wall - (execs or 0.0))
        runs = f"{int(step.get('opens', 0) or 0)}o/{int(step.get('executions', 0) or 0)}x"
        status = str(step.get("status") or "?")
        if not step.get("completed_epoch"):
            # Two different things: a step the run never got past, and a step
            # from a run recorded before the wall clock existed.
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
    out.append(f" {'':>3} {'TOTAL':<14} {'':<16} {_fmt_seconds(step_wall)} "
               f"{_fmt_seconds(step_exec)} {_fmt_seconds(human_wait + machine_overhead)}")
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
