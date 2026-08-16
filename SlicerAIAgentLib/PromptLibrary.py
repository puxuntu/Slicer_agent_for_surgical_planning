"""Single loader for every prompt text used at runtime.

All prompt text lives in ``Resources/Prompts/*.md`` -- never inline in Python.
That is a hard project rule: a prompt is an experimental variable of this
system, so it must be editable, diffable and citable without touching code.
This module is the only thing that reads that directory.

Files are re-read when their mtime changes, so editing a prompt takes effect on
the next call without restarting Slicer (the same guarantee the system prompt
already had).

Placeholders use ``{{NAME}}`` -- doubled braces so a prompt can contain ordinary
Markdown/JSON braces (``{"type": ...}``) without needing to escape them, unlike
``str.format``.
"""

from __future__ import annotations

import logging
import os
import re
import threading
from typing import Dict, Optional

logger = logging.getLogger(__name__)

#: ``<repo root>/Resources/Prompts``
PROMPTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Resources",
    "Prompts",
)

# Known prompt files, named here so callers refer to a constant rather than a
# string literal scattered across modules.
SYSTEM_PROMPT = "system_prompt.md"
WORKFLOW_ROUTER_PROMPT = "workflow_router_prompt.md"
BASELINE_PURE_LLM_PROMPT = "baseline_pure_llm_prompt.md"
BASELINE_ONLINE_ONLY_PROMPT = "baseline_online_only_prompt.md"
TEMPLATE_REVISION_PROMPT = "template_revision_prompt.md"

_cache: Dict[str, tuple] = {}
_lock = threading.Lock()

_PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def path_for(name: str) -> str:
    """Absolute path of a prompt file (no existence check)."""
    return os.path.join(PROMPTS_DIR, name)


def load(name: str, fallback: str = "") -> str:
    """Return the text of ``Resources/Prompts/<name>``.

    Returns ``fallback`` (and logs) when the file is missing or unreadable, so a
    missing prompt degrades the run instead of crashing it.
    """
    path = path_for(name)
    try:
        stamp = os.path.getmtime(path)
    except OSError:
        logger.warning("Prompt file not found: %s", path)
        return fallback

    with _lock:
        cached = _cache.get(name)
        if cached and cached[0] == stamp:
            return cached[1]

    try:
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()
    except Exception:
        logger.warning("Prompt file unreadable: %s", path, exc_info=True)
        return fallback

    with _lock:
        _cache[name] = (stamp, text)
    return text


def render(name: str, fallback: str = "", **values) -> str:
    """Load ``name`` and substitute ``{{KEY}}`` placeholders from ``values``.

    Keys are matched case-insensitively against the upper-case placeholder name,
    so ``render("x.md", extension_catalog=...)`` fills ``{{EXTENSION_CATALOG}}``.
    An unfilled placeholder collapses to an empty string rather than being left
    as literal ``{{...}}`` text in the prompt.
    """
    text = load(name, fallback)
    if not text:
        return text
    upper = {str(key).upper(): ("" if value is None else str(value)) for key, value in values.items()}
    return _PLACEHOLDER.sub(lambda match: upper.get(match.group(1), ""), text)


def available() -> list:
    """Sorted list of the ``.md`` prompt files present on disk."""
    try:
        return sorted(n for n in os.listdir(PROMPTS_DIR) if n.lower().endswith(".md"))
    except OSError:
        return []


def clear_cache(name: Optional[str] = None) -> None:
    """Drop cached prompt text (all of it, or one file)."""
    with _lock:
        if name is None:
            _cache.clear()
        else:
            _cache.pop(name, None)
