#!/usr/bin/env python3
"""Build a comparison table from ``logs/``, across all four conditions.

    python scripts/collect_runs.py                 # summary + logs/runs_index.csv
    python scripts/collect_runs.py --step cb_step_9
    python scripts/collect_runs.py --logs D:/archive/run3 --out table.csv

One row per (run, step). The system under test (``pipeline``) and the three
baselines (``pure_llm`` / ``online_only`` / ``claude_code``) come out in the same
shape, so a step can be compared across conditions in one read.

This is DERIVED from the run folders every time it is asked for, not written
alongside them at runtime. A second live writer of the same facts can drift from
the first; a derivation cannot. (It replaces ``logs/baseline_runs.jsonl``, which
duplicated the per-run record byte for byte and covered only the baselines --
a "whole session in one file" that silently omitted the system under test.)

Standard library only: it has to run in whatever Python is at hand, including
Slicer's.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys

MANIFEST = "run_manifest.json"

COLUMNS = [
    "condition", "extension", "subject", "step_id", "attempt", "status",
    "operation_type", "exec_seconds", "code_chars",
    "gen_seconds", "prompt_chars", "tokens", "cost",
    "tool_rounds", "tool_calls",
    # What the PERSON did, from PlanningRecorder. Present for both arms of the
    # user study and empty for a run recorded before it existed -- appended
    # rather than interleaved, so a reader scanning the older columns finds
    # them where they have always been.
    "wall_seconds", "active_seconds", "compute_seconds", "idle_seconds",
    "away_seconds", "clicks", "clicks_3d", "clicks_2d", "clicks_panel",
    "clicks_other",
    "started", "error", "folder",
]

#: Report order: the system under test first, then the baselines in their
#: numbered order, then the user study's unaided comparison arm, so a printed
#: table reads the way the comparison is stated.
CONDITION_ORDER = ["pipeline", "pure_llm", "online_only", "claude_code", "manual"]

#: The four operating buckets, summed into one ``active`` column. Mirrors
#: ``PlanningRecorder.TARGET_KINDS``; a literal rather than an import because
#: this script has to run against a copied ``logs/`` with no library beside it.
_ACTIVE_STATES = ("view_3d", "view_2d", "panel", "other")


def _interaction_columns(totals, counts):
    """The eight interaction cells from one ``totals``/``counts`` pair."""
    totals = totals or {}
    counts = counts or {}
    if not totals and not counts:
        return {}
    active = sum(float(totals.get(state) or 0.0) for state in _ACTIVE_STATES)
    return {
        "active_seconds": round(active, 2),
        "compute_seconds": round(float(totals.get("compute") or 0.0), 2),
        "idle_seconds": round(float(totals.get("idle") or 0.0), 2),
        "away_seconds": round(float(totals.get("away") or 0.0), 2),
        "clicks": int(counts.get("clicks_total") or 0),
        "clicks_3d": int(counts.get("clicks_view_3d") or 0),
        "clicks_2d": int(counts.get("clicks_view_2d") or 0),
        "clicks_panel": int(counts.get("clicks_panel") or 0),
        # The fourth target: anywhere else in Slicer. Without it the three
        # named columns look like they should sum to `clicks` and do not.
        "clicks_other": int(counts.get("clicks_other") or 0),
    }


def _read_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception:
        return None


def _runtime_dir(run_dir):
    """Where a run's execution artifacts live.

    A run folder holds exactly two subfolders -- ``runtime/`` (manifest, router
    call, one folder per step) and ``Statistic/`` (the report + saved scene).
    Runs written before that split put the same files at the run root, so fall
    back to it: this script is a DERIVATION over whatever is on disk, and it
    should not silently drop older runs from the comparison.
    """
    nested = os.path.join(run_dir, "runtime")
    if os.path.isfile(os.path.join(nested, MANIFEST)):
        return nested
    return run_dir


def _step_execution(runtime_dir, step_folder):
    """Per-step execution.json, when the step has its own folder (pipeline)."""
    if not step_folder:
        return {}
    return _read_json(os.path.join(runtime_dir, step_folder, "execution.json")) or {}


def collect(logs_dir):
    """Yield one row per (run, step), oldest run first."""
    if not os.path.isdir(logs_dir):
        return
    for name in sorted(os.listdir(logs_dir)):
        run_dir = _runtime_dir(os.path.join(logs_dir, name))
        manifest = _read_json(os.path.join(run_dir, MANIFEST))
        if not isinstance(manifest, dict):
            continue  # not a run folder (or an interrupted one with no manifest)

        totals = manifest.get("totals") or {}
        interaction = manifest.get("interaction") or {}
        by_label = interaction.get("by_label") or {}
        condition = manifest.get("condition", "")
        base = {
            "condition": condition,
            "extension": manifest.get("extension") or "",
            # The input data set, so rows can be grouped per patient as well as
            # per procedure -- the four conditions on one subject are the unit
            # of comparison.
            "subject": manifest.get("subject") or "",
            "started": manifest.get("started") or "",
            "folder": name,
        }
        steps = manifest.get("steps") or []
        if not steps:
            # A run that produced no step (router declined, or cancelled early).
            row = dict.fromkeys(COLUMNS, "")
            row.update(base)
            row.update({
                "status": manifest.get("status", ""),
                "gen_seconds": totals.get("generation_seconds", ""),
                "prompt_chars": totals.get("prompt_chars", ""),
                "tokens": totals.get("tokens", ""),
                "cost": totals.get("cost", ""),
                "wall_seconds": interaction.get("wall_seconds", ""),
            })
            # An unaided comparison-arm run is one row by construction -- it has
            # no steps -- so the session's own interaction figures are the row's.
            row.update(_interaction_columns(interaction.get("totals"),
                                            interaction.get("counts")))
            yield row
            continue

        # Run-level totals belong to the RUN. A baseline run is one step, so
        # they describe that step; a pipeline run has many, so attaching them to
        # every row would multiply the run's cost by its step count.
        one_step = len(steps) == 1
        for step in steps:
            execution = _step_execution(run_dir, step.get("folder"))
            row = dict.fromkeys(COLUMNS, "")
            row.update(base)
            row.update({
                "step_id": step.get("step_id", ""),
                "attempt": step.get("attempt", 1),
                "status": step.get("status", ""),
                "operation_type": step.get("operation_type", ""),
                "exec_seconds": step.get("seconds", execution.get("seconds", "")),
                "code_chars": step.get("code_chars", ""),
                "wall_seconds": step.get("wall_seconds", ""),
                "error": (step.get("error") or "").replace("\n", " ")[:200],
            })
            # Keyed on the step id, matching `steps[]` -- so a step re-visited
            # by a loop iteration or a replay re-run carries its ACCUMULATED
            # interaction, the same way its wall clock is accumulated.
            entry = by_label.get(str(step.get("step_id") or "")) or {}
            row.update(_interaction_columns(entry.get("totals"),
                                            entry.get("counts")))
            if one_step:
                row.update({
                    "gen_seconds": totals.get("generation_seconds", ""),
                    "prompt_chars": totals.get("prompt_chars", ""),
                    "tokens": totals.get("tokens", ""),
                    "cost": totals.get("cost", ""),
                    "tool_rounds": totals.get("tool_rounds", ""),
                    "tool_calls": totals.get("tool_calls", ""),
                })
            yield row


def _fmt(value, width, places=None):
    """Column cell. Floats are ROUNDED, never truncated — a truncated 13.2884…
    reads as a precision claim the number does not make."""
    if value is None:
        text = ""
    elif places is not None and isinstance(value, (int, float)) and not isinstance(value, bool):
        text = f"{value:.{places}f}"
    else:
        text = str(value)
    if len(text) > width:
        text = text[: width - 1] + "…"
    return text.ljust(width)


def print_summary(rows, step_filter=""):
    if not rows:
        print("No runs found.")
        return

    if step_filter:
        rows = [r for r in rows if r["step_id"] == step_filter]
        if not rows:
            print(f"No runs for step {step_filter!r}.")
            return
        print(f"\n=== {step_filter} across conditions ===")
        rows.sort(key=lambda r: (
            CONDITION_ORDER.index(r["condition"])
            if r["condition"] in CONDITION_ORDER else 99,
            r["attempt"] or 0,
        ))
        # (header, width, decimal places or None)
        head = [("condition", 13, None), ("att", 4, None), ("status", 8, None),
                ("exec s", 8, 2), ("gen s", 8, 1), ("prompt ch", 10, None),
                ("tokens", 9, None), ("cost $", 9, 4)]
        print("  " + "".join(_fmt(h, w) for h, w, _ in head))
        print("  " + "-" * sum(w for _, w, _ in head))
        for r in rows:
            values = (r["condition"], r["attempt"], r["status"], r["exec_seconds"],
                      r["gen_seconds"], r["prompt_chars"], r["tokens"], r["cost"])
            print("  " + "".join(_fmt(v, w, p) for v, (_, w, p) in zip(values, head)))
        print("\n  Folders:")
        for r in rows:
            print(f"    {r['condition']:<13} {r['folder']}")
        return

    print("\n=== runs by condition ===")
    head = [("condition", 13, None), ("runs", 6, None), ("steps", 7, None),
            ("ok", 5, None), ("failed", 8, None), ("tokens", 12, None),
            ("cost $", 9, 4)]
    print("  " + "".join(_fmt(h, w) for h, w, _ in head))
    print("  " + "-" * sum(w for _, w, _ in head))
    for condition in CONDITION_ORDER + sorted(
            {r["condition"] for r in rows} - set(CONDITION_ORDER)):
        subset = [r for r in rows if r["condition"] == condition]
        if not subset:
            continue
        tokens = sum(int(r["tokens"]) for r in subset
                     if str(r["tokens"]).strip().isdigit())
        cost = sum(float(r["cost"]) for r in subset if str(r["cost"]).strip())
        values = (condition, len({r["folder"] for r in subset}), len(subset),
                  sum(1 for r in subset if r["status"] == "ok"),
                  sum(1 for r in subset if r["status"] == "failed"),
                  tokens or "", cost or "")
        print("  " + "".join(_fmt(v, w, p) for v, (_, w, p) in zip(values, head)))

    compared = sorted({r["step_id"] for r in rows if r["step_id"]
                       and r["condition"] != "pipeline"})
    if compared:
        print("\n  Steps with a baseline run: " + ", ".join(compared))
        print("  Compare one with:  --step <step_id>")


def main(argv=None):
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--logs", default=os.path.join(here, "logs"),
                        help="logs directory (default: <repo>/logs)")
    parser.add_argument("--out", default="",
                        help="CSV output path (default: <logs>/runs_index.csv)")
    parser.add_argument("--step", default="",
                        help="print one step across every condition")
    parser.add_argument("--jsonl", action="store_true",
                        help="also write runs_index.jsonl beside the CSV")
    args = parser.parse_args(argv)

    rows = list(collect(args.logs))
    out = args.out or os.path.join(args.logs, "runs_index.csv")
    try:
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        with open(out, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        if args.jsonl:
            with open(os.path.splitext(out)[0] + ".jsonl", "w", encoding="utf-8") as handle:
                for row in rows:
                    handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception as exc:
        print(f"Could not write {out}: {exc}", file=sys.stderr)
        return 1

    print_summary(rows, args.step)
    print(f"\n{len(rows)} row(s) -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
