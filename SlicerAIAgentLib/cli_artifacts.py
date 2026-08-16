"""Shared on-disk layout for generated Extension CLI artifacts.

Centralizes where generation/repair debug output and versioned package snapshots
live, so the generation pipeline, the repair pipeline, and the main agent all
agree on the structure:

    Resources/extension_CLI/<Ext>/
      manifest.json, workflow*.json, templates/, ...   <- ACTIVE package (latest)
      versions/
        generation/         <- snapshot of the first-generation package
        repair_001/ ...     <- snapshot after each repair round
        runtime_fix_<ts>/   <- snapshot before a runtime self-correction rewrote
                               a step template (pre-revision backup)
      debug/
        generation/        <- first-generation LLM calls + ui_output.log
        repair_001/ ...    <- each repair round, isolated (never clobbered)

Pure path/IO helpers only — no Slicer or heavy dependencies — so any layer can
import this without pulling in the analyzer.
"""

from __future__ import annotations

import os
import re
import shutil
from typing import Optional

GENERATION_ROUND = "generation"
_REPAIR_RE = re.compile(r"^repair_(\d+)$")


# ── round-scoped debug folders ───────────────────────────────────────────────

def debug_round_dir(ext_dir: str, round_label: str) -> str:
    """Return (creating it) the debug folder for one generation/repair round."""
    path = os.path.join(ext_dir, "debug", round_label)
    os.makedirs(path, exist_ok=True)
    return path


def next_repair_round_label(ext_dir: str) -> str:
    """Return ``repair_NNN`` for the next repair round under ``<ext_dir>/debug``."""
    highest = 0
    debug_root = os.path.join(ext_dir, "debug")
    if os.path.isdir(debug_root):
        for name in os.listdir(debug_root):
            match = _REPAIR_RE.match(name)
            if match:
                highest = max(highest, int(match.group(1)))
    return f"repair_{highest + 1:03d}"


# ── package version snapshots ────────────────────────────────────────────────

# The files that make up the active package (copied into versions/<round>/).
_PACKAGE_FILES = (
    "manifest.json",
    "tool_schemas.json",
    "code_generators.json",
    "prompt_fragment.md",
    "workflow.json",
    "workflow_metadata.json",
    "workflow_contract.json",
    # Hand-editable: the Step-instructions editor writes the surgeon-facing
    # clinical text here. Snapshotted with the rest so a versions/<round>/ is a
    # complete package rather than one missing the only file a human authored.
    "step_instructions.json",
)


def snapshot_package_version(ext_dir: str, round_label: str) -> Optional[str]:
    """Copy the active package into ``<ext_dir>/versions/<round_label>/``.

    Captures the package JSON/markdown files plus ``templates/`` so the first
    generation and each repair round can be compared. The active package always
    stays at the root (what the agent loads), so this is a pure archive.
    Fail-soft: returns the snapshot dir, or ``None`` on any error.
    """
    try:
        dest = os.path.join(ext_dir, "versions", round_label)
        os.makedirs(dest, exist_ok=True)
        for name in _PACKAGE_FILES:
            src = os.path.join(ext_dir, name)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(dest, name))
        templates_src = os.path.join(ext_dir, "templates")
        if os.path.isdir(templates_src):
            templates_dest = os.path.join(dest, "templates")
            if os.path.isdir(templates_dest):
                shutil.rmtree(templates_dest, ignore_errors=True)
            shutil.copytree(templates_src, templates_dest)
        return dest
    except Exception:
        return None


# ── active-package backup (regeneration "swap on success" safety) ────────────

_ACTIVE_BACKUP_DIR = ".active_backup"

#: Everything at the package root EXCEPT these is the active package. Defining
#: it by exclusion rather than by an allow-list is what makes backup / clear /
#: restore agree by construction: a file added to the package later is covered
#: by all three without anyone remembering to list it. The named entries are
#: history, not package -- they survive a regeneration on purpose.
_PRESERVED_ENTRIES = ("versions", "debug", "runtime_errors", _ACTIVE_BACKUP_DIR)


def _active_package_entries(ext_dir: str):
    """Names at the package root that make up the ACTIVE package."""
    try:
        return sorted(name for name in os.listdir(ext_dir)
                      if name not in _PRESERVED_ENTRIES)
    except Exception:
        return []


def _remove_active_package(ext_dir: str) -> int:
    """Delete the active package, leaving history untouched. Returns the count."""
    removed = 0
    for name in _active_package_entries(ext_dir):
        target = os.path.join(ext_dir, name)
        try:
            if os.path.isdir(target):
                shutil.rmtree(target, ignore_errors=True)
            else:
                os.remove(target)
            removed += 1
        except Exception:
            pass
    return removed


def clear_active_package(ext_dir: str) -> int:
    """Remove the active package so a regeneration starts from a clean slate.

    Overwriting in place cannot do this: a file the OLD package had and the new
    run does not produce -- a template for a step that no longer exists, a
    stale workflow_contract.json -- survives and becomes part of the "new"
    package, so what ships is a mixture of two generations.

    Only ever called AFTER :func:`backup_active_package` has taken a complete
    copy; on a failed run :func:`restore_active_package` puts all of it back.
    """
    return _remove_active_package(ext_dir)


def backup_active_package(ext_dir: str) -> Optional[str]:
    """Snapshot the current active package so a failed regeneration can restore it.

    Copies the package JSON/markdown files plus ``templates/`` into
    ``<ext_dir>/.active_backup/``. This gives regeneration "swap on success"
    semantics: if the run errors out, :func:`restore_active_package` puts the
    previously-active package back so a known-good CLI is never lost. Returns the
    backup dir, or ``None`` when there is no active package to protect.
    Fail-soft.
    """
    if not os.path.isfile(os.path.join(ext_dir, "manifest.json")):
        return None
    backup = os.path.join(ext_dir, _ACTIVE_BACKUP_DIR)
    try:
        if os.path.isdir(backup):
            shutil.rmtree(backup, ignore_errors=True)
        os.makedirs(backup, exist_ok=True)
        for name in _active_package_entries(ext_dir):
            src = os.path.join(ext_dir, name)
            dst = os.path.join(backup, name)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        return backup
    except Exception:
        shutil.rmtree(backup, ignore_errors=True)
        return None


def restore_active_package(ext_dir: str) -> bool:
    """Restore the active package from ``<ext_dir>/.active_backup/``.

    Replaces whatever a failed regeneration left at the package root with the
    snapshot taken by :func:`backup_active_package`, then removes the backup.
    Returns True if a backup existed and was restored. Fail-soft.
    """
    backup = os.path.join(ext_dir, _ACTIVE_BACKUP_DIR)
    if not os.path.isdir(backup):
        return False
    try:
        _remove_active_package(ext_dir)
        for name in os.listdir(backup):
            src = os.path.join(backup, name)
            dst = os.path.join(ext_dir, name)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        shutil.rmtree(backup, ignore_errors=True)
        return True
    except Exception:
        return False


def discard_active_backup(ext_dir: str) -> None:
    """Drop the regeneration backup after a successful run. Fail-soft."""
    backup = os.path.join(ext_dir, _ACTIVE_BACKUP_DIR)
    try:
        if os.path.isdir(backup):
            shutil.rmtree(backup, ignore_errors=True)
    except Exception:
        pass


