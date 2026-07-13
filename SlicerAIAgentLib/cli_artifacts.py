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
_BACKUP_EXTRAS = ("prompt_fragment.md", "generation_log.json")


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
        for name in _PACKAGE_FILES + _BACKUP_EXTRAS:
            src = os.path.join(ext_dir, name)
            if os.path.isfile(src):
                shutil.copy2(src, os.path.join(backup, name))
        templates_src = os.path.join(ext_dir, "templates")
        if os.path.isdir(templates_src):
            shutil.copytree(templates_src, os.path.join(backup, "templates"))
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
        for name in _PACKAGE_FILES + _BACKUP_EXTRAS:
            stale = os.path.join(ext_dir, name)
            if os.path.isfile(stale):
                os.remove(stale)
        active_templates = os.path.join(ext_dir, "templates")
        if os.path.isdir(active_templates):
            shutil.rmtree(active_templates, ignore_errors=True)
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


