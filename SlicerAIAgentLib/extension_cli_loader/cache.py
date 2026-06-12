"""
ExtensionCLILoader - Auto-discovery and dynamic loading of extension CLI tools.

Scans Resources/extension_CLI/*/ for generated extension tool definitions,
loads their schemas, code templates, and prompt fragments at runtime,
and dispatches tool calls from the LLM to the appropriate code generator.
"""

from __future__ import annotations

import json
import logging
import os
import re
import threading
from typing import Any, Callable, Dict, List, Optional

try:
    import slicer
except ImportError:
    slicer = None

logger = logging.getLogger(__name__)

# Module-level cache: {extension_name: {"manifest": ..., "schemas": ..., "generators": ..., ...}}
_cli_cache: Dict[str, Dict] = {}
_cache_valid = False
_cache_lock = threading.Lock()

# Opt-in (default OFF): load CLIs that failed overall validation but have at
# least one individually proven step (manifest["step_validation"]). Unproven
# steps are surfaced as requiring user confirmation at dispatch time.
_allow_partial = os.environ.get("SLICERAIAGENT_CLI_ALLOW_PARTIAL", "") == "1"


def set_allow_partial(enabled: bool) -> None:
    """Enable/disable partial loading of CLIs with per-step validity."""
    global _allow_partial
    if enabled != _allow_partial:
        _allow_partial = bool(enabled)
        invalidate_cache()


def get_allow_partial() -> bool:
    return _allow_partial

__all__ = [name for name in list(globals()) if not name.startswith("__")]


def get_cli_base_dir() -> str:
    """Return the path to Resources/extension_CLI/."""
    module_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    return os.path.join(module_dir, "Resources", "extension_CLI")


def _ensure_cache():
    """Populate the CLI cache by scanning the extension_CLI directory."""
    global _cache_valid, _cli_cache
    if _cache_valid:
        return

    with _cache_lock:
        # Double-check after acquiring the lock
        if _cache_valid:
            return

        base_dir = get_cli_base_dir()
        if not os.path.isdir(base_dir):
            logger.info("No extension_CLI directory found at %s", base_dir)
            _cache_valid = True
            return

        for entry in os.listdir(base_dir):
            ext_dir = os.path.join(base_dir, entry)
            if not os.path.isdir(ext_dir):
                continue

            manifest_path = os.path.join(ext_dir, "manifest.json")
            if not os.path.isfile(manifest_path):
                continue

            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)

                status = manifest.get("status", "unknown")
                partial = False
                if status not in {"validated", "validated_with_warnings"}:
                    if (
                        _allow_partial
                        and status == "validation_failed"
                        and manifest.get("partial_valid_step_count", 0) > 0
                    ):
                        partial = True
                        logger.info(
                            "Loading %s PARTIALLY (%d proven step(s); unproven "
                            "steps will require confirmation)",
                            entry, manifest.get("partial_valid_step_count", 0),
                        )
                    else:
                        logger.info(
                            "Skipping %s (status=%s, not validated)", entry, status
                        )
                        continue
                if manifest.get("manifest_version") not in {2, 3}:
                    logger.info(
                        "Skipping %s (manifest_version=%s, expected 2 or 3; regenerate CLI)",
                        entry,
                        manifest.get("manifest_version", "missing"),
                    )
                    continue

                schemas_path = os.path.join(ext_dir, "tool_schemas.json")
                generators_path = os.path.join(ext_dir, "code_generators.json")
                prompt_path = os.path.join(ext_dir, "prompt_fragment.md")
                metadata_path = os.path.join(ext_dir, "workflow_metadata.json")
                contract_path = os.path.join(ext_dir, "workflow_contract.json")

                schemas = []
                if os.path.isfile(schemas_path):
                    with open(schemas_path, "r", encoding="utf-8") as f:
                        schemas = json.load(f)

                generators = []
                if os.path.isfile(generators_path):
                    with open(generators_path, "r", encoding="utf-8") as f:
                        generators = json.load(f)

                prompt_fragment = ""
                if os.path.isfile(prompt_path):
                    with open(prompt_path, "r", encoding="utf-8") as f:
                        prompt_fragment = f.read()

                workflow_metadata = {}
                if os.path.isfile(metadata_path):
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        workflow_metadata = json.load(f)
                workflow_contract = {}
                if os.path.isfile(contract_path):
                    with open(contract_path, "r", encoding="utf-8") as f:
                        workflow_contract = json.load(f)

                _cli_cache[entry] = {
                    "manifest": manifest,
                    "schemas": schemas,
                    "generators": generators,
                    "prompt_fragment": prompt_fragment,
                    "workflow_metadata": workflow_metadata,
                    "workflow_contract": workflow_contract,
                    "dir": ext_dir,
                    "partial": partial,
                }

                tool_names = [s.get("function", {}).get("name", "?") for s in schemas]
                logger.info(
                    "Loaded extension CLI: %s (tools=%s)", entry, tool_names
                )

            except Exception as e:
                logger.warning("Failed to load extension CLI %s: %s", entry, e)

        _cache_valid = True


def invalidate_cache():
    """Force a cache refresh on the next access."""
    global _cache_valid
    with _cache_lock:
        _cache_valid = False
        _cli_cache.clear()


def get_validated_extensions() -> Dict[str, Dict]:
    """Return the full cache of validated extension CLI data."""
    _ensure_cache()
    return dict(_cli_cache)


def get_dynamic_extension_tools() -> List[Dict]:
    """Return tool schemas from all validated extension CLIs."""
    _ensure_cache()
    tools = []
    for ext_data in _cli_cache.values():
        tools.extend(ext_data["schemas"])
    return tools


def get_extension_prompt_fragments() -> str:
    """Return concatenated prompt fragments from all validated extension CLIs."""
    _ensure_cache()
    fragments = []
    for ext_name, ext_data in _cli_cache.items():
        fragment = ext_data.get("prompt_fragment", "").strip()
        if fragment:
            fragments.append(fragment)
    return "\n\n".join(fragments)
