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

    def add_step(self, step_id: str, **fields) -> "RunManifest":
        """Upsert one step entry, keyed by (step_id, attempt)."""
        attempt = int(fields.get("attempt", 1) or 1)
        for entry in self.data["steps"]:
            if entry.get("step_id") == step_id and int(entry.get("attempt", 1)) == attempt:
                entry.update({k: v for k, v in fields.items() if v is not None})
                return self.write()
        entry = {"step_id": step_id, "attempt": attempt,
                 "index": len(self.data["steps"]) + 1}
        entry.update({k: v for k, v in fields.items() if v is not None})
        self.data["steps"].append(entry)
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
