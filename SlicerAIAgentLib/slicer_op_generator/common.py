"""
SlicerOpGenerator - Generate code templates for Slicer core API operations
(Type 2 / slicer_op sub-operations) by delegating to the main agent's
tool-calling loop.

Uses LLMClient.chatWithToolsIsolated() so the LLM adaptively searches the
knowledge base (VectorSearch, Grep, ReadFile) and generates
code in a single integrated loop — the same pipeline the main agent uses
for interactive queries.
"""

import ast
import json
import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt for slicer_op template generation via tool-calling loop
# ---------------------------------------------------------------------------

_SLICER_OP_SYSTEM_PROMPT = """\
You are a 3D Slicer Python code-template generator. Given a description of a
Slicer operation, search the knowledge base for API examples if needed, then
generate a standalone Python code template.

## Search Strategy

All search paths are relative to the skill root. Do NOT prepend absolute paths.

Search roots:
- `slicer-source/` — Slicer source code and script repository
- `slicer-ui-analysis/` — generated Slicer core UI label/action to implementation/API evidence
- `slicer-extensions/` — Extension repositories
- `slicer-dependencies/` — VTK, ITK, CTK, etc.

You have three search tools: VectorSearch, Grep, ReadFile.

### When to search vs. skip
- If you already know a simple, verified Slicer API (for example layoutManager().setLayout), \
you may generate code directly. For view-controller, display-node, markups, or MRML-node APIs, \
confirm the exact receiver and method with VectorSearch, Grep, or ReadFile before writing code.
- If the operation is described as a UI control, toolbar action, menu action, checkbox, or panel setting, \
search `slicer-ui-analysis/` for the user-facing label/action first. Use UI evidence to identify the \
receiver/slot/control intent, then verify the executable API against implementation or MRML/API evidence.
- If unsure about an API signature, do **one** VectorSearch or Grep to confirm, \
then generate code immediately.
- You have up to 15 tool rounds total. Prefer fewer rounds — generate code as soon \
as you have enough evidence.

### Extension-specific artifacts
This applies ONLY to artifacts the extension DEFINES IN ITS OWN SOURCE whose exact
value you must reproduce: a custom layout registered by the extension (its layout
ID and XML), an `slicer.<Const>` the extension sets, a custom singleton tag, or a
magic constant. Their concrete values live in the extension's OWN source, not in
Slicer core. Search `slicer-extensions/<ExtensionName>/` (and any `ext:` root
provided) for the real definition or accessor (for example a `setX`/`addX` helper
or an `slicer.<Const>`) and use that. Do NOT guess an ID, invent XML, or copy a
placeholder value.

This does NOT apply to ordinary MRML scene nodes the user/workflow creates and that
are referenced by NAME or role (for example a "mandibular curve", a segmentation,
or a volume). Those are resolved at RUNTIME from the scene by name/role lookup
(parameter-node references, `GetFirstNodeByName`, fuzzy name match) — generate that
lookup directly; do NOT treat them as missing source artifacts.

### Efficient search order
If you need to search, prefer these sources in order:
1. `slicer-ui-analysis/` — UI labels/actions mapped to nearby implementation/API evidence
2. `slicer-source/Docs/developer_guide/script_repository/` — official cookbook examples
3. `slicer-source/Base/Python/slicer/util.py` — core Python API
4. `slicer-source/Modules/CLI/` — ready-made CLI operations
5. `slicer-source/Modules/Scripted/<relevant-module>/` — Python modules
6. `slicer-source/Modules/Loadable/<relevant-module>/` — C++ modules with Python wrappers
7. `slicer-source/Libs/MRML/Core/` — MRML node definitions

**Grep** returns an aggregated summary (per-file hit counts + representative matches), \
not line-by-line results. Use the `files` list to find relevant files, then ReadFile for context.
**ReadFile** returns smart-sliced content for large files. Provide a `query` parameter to extract \
matching sections.

### Stop condition
Once you have seen the target function's parameter list and at least one usage example, \
**stop calling tools immediately** and output the code. Search for "sufficiency", not "completeness".

## Output Requirements

- Output ONLY a single ```python code block. No explanation, no agent_plan.
- Code runs inside Slicer's Python environment (`slicer` and `vtk` are available).
- Use `slicer.mrmlScene`, `slicer.app.layoutManager()`, etc. directly.
- For finding nodes by name, use fuzzy matching (iterate nodes, check keyword in name).
- Use `{placeholder}` syntax for runtime values, e.g. `{node_name: TargetNode}`.
- Do NOT use f-strings (single braces are template placeholders). Use %-formatting.
  If you need literal braces, double them: `{{expr}}`.
- Generate final-state code. If the requested operation says enable/on/show/visible,
  call an API that sets the state to true/visible; if it says disable/off/hide,
  set the state to false/hidden. Do not use toggle APIs unless the request
  explicitly asks to invert the current state.
- For slice-intersection operations, implement the requested intersection
  visibility and interaction state. Do not substitute crosshair visibility.
  Search source/docs for the appropriate state APIs and any required refresh.
- For custom layout operations, distinguish registering a layout from activating
  it. A "change/switch/restore layout" operation must actually activate the
  requested layout; registration alone is not sufficient.
- NEVER fabricate extension-specific data artifacts. Do not invent or guess a
  custom-layout ID, layout XML, node name, singleton tag, or magic constant that
  belongs to an extension. Every such literal must come from retrieved source
  evidence (the extension's own source). If, after searching the extension source,
  you cannot find the real value or a helper that performs the operation, do NOT
  emit a placeholder, a guessed number, or made-up XML — instead emit exactly:
  `raise RuntimeError("MISSING_EVIDENCE: <what is missing>")`
  as the entire operation body, so the failure is explicit rather than silently
  wrong.
- For display/view-scope operations, adding view IDs is only a view filter.
  If the target includes a slice view, also enable the target display class's
  supported slice/2D visibility state. Search evidence for the discovered
  display-node class rather than assuming one shared API.
  Resolve view node IDs from scene/layout evidence when possible; avoid
  hard-coded view-node IDs unless the ID or singleton tag is verified.
- Do NOT call `slicer.util.selectModule(...)` for module/panel location context
  such as "In the Markups module Display > Advanced panel, configure View...".
  Those phrases describe where a user found a control; implement the requested
  state directly. Use `selectModule` only when the operation explicitly asks to
  switch/open/select/activate a module as the final state.
- Keep code short and focused on the single operation.
- Do NOT import os, subprocess, sys, socket, or use eval/exec/open.
- Do NOT use destructive operations.
"""

# ---------------------------------------------------------------------------
# Tool filtering
# ---------------------------------------------------------------------------

_ALLOWED_TOOLS = frozenset({"Grep", "ReadFile", "VectorSearch"})

_NO_EVIDENCE_TEXT = "(No relevant snippets found in knowledge base)"
_GENERATION_FAILED_SENTINEL = "SLICER_OP_GENERATION_FAILED"
_MAX_TOOL_ROUNDS = 15
_PER_OP_TIMEOUT_S = 600  # Max seconds per slicer_op (tool loop can be slow)
_UI_ANALYSIS_PREFIX = "slicer-ui-analysis/"


def infer_final_state_intent(text: str) -> Dict[str, Any]:
    """Infer whether a UI-style operation asks for a final state or inversion."""
    raw = text or ""
    normalized = re.sub(r"[^a-z0-9]+", " ", raw.lower()).strip()
    padded = f" {normalized} "

    invert_patterns = (
        " invert current state ",
        " invert the current state ",
        " toggle current state ",
        " toggle the current state ",
        " flip current state ",
        " flip the current state ",
        " switch to opposite ",
        " switch to the opposite ",
    )
    true_patterns = (
        " toggle on ",
        " turn on ",
        " switch on ",
        " set on ",
        " enable ",
        " enabled ",
        " show ",
        " visible ",
        " visibility on ",
        " select ",
        " selected ",
        " checked ",
        " activate ",
        " activated ",
    )
    false_patterns = (
        " toggle off ",
        " turn off ",
        " switch off ",
        " set off ",
        " disable ",
        " disabled ",
        " hide ",
        " hidden ",
        " invisible ",
        " visibility off ",
        " unselect ",
        " deselect ",
        " unchecked ",
        " uncheck ",
        " deactivate ",
        " deactivated ",
    )

    if any(pattern in padded for pattern in invert_patterns):
        return {
            "mode": "invert",
            "state": None,
            "confidence": "high",
            "source": "explicit_invert_language",
        }
    true_hit = next((pattern.strip() for pattern in true_patterns if pattern in padded), "")
    false_hit = next((pattern.strip() for pattern in false_patterns if pattern in padded), "")
    if true_hit and not false_hit:
        return {
            "mode": "set",
            "state": True,
            "confidence": "high",
            "source": true_hit,
        }
    if false_hit and not true_hit:
        return {
            "mode": "set",
            "state": False,
            "confidence": "high",
            "source": false_hit,
        }
    if true_hit and false_hit:
        return {
            "mode": "ambiguous",
            "state": None,
            "confidence": "low",
            "source": f"{true_hit}; {false_hit}",
        }
    return {
        "mode": "unspecified",
        "state": None,
        "confidence": "none",
        "source": "",
    }


def _get_allowed_tool_defs() -> List[Dict]:
    """Return tool definitions filtered to only KB search tools."""
    from ..SkillTools import get_skill_tools
    return [
        t for t in get_skill_tools()
        if t.get("function", {}).get("name") in _ALLOWED_TOOLS
    ]


# ---------------------------------------------------------------------------
# Category inference helpers (used to build user prompt hints)
# ---------------------------------------------------------------------------

_CATEGORY_SEARCH_HINTS = {
    "layout_slice_view": [
        "slicer-ui-analysis", "qMRMLSliceControllerWidget", "actionShow_in_3D",
        "layoutManager", "vtkMRMLLayoutNode", "sliceWidget",
        "mrmlSliceNode", "sliceController", "setSliceVisible", "SetSliceResolutionMode",
        "SliceResolutionMatch2DView", "SliceResolutionMatchVolumes",
        "SetViewArrangement", "SlicerLayoutConventionalView", "setLayout active layout",
        "layoutManager setLayout", "AddLayoutDescription registers layout only", "GetLayoutByName",
    ],
    "module_switching": [
        "slicer.util.selectModule", "moduleSelector", "markups module",
        "selectModule",
    ],
    "markups_display": [
        "slicer-ui-analysis", "qSlicerMarkupsModule.ui", "qMRMLDisplayNodeViewComboBox",
        "vtkMRMLMarkupsDisplayNode", "AddViewNodeID", "SetActiveListID",
        "Markups display advanced view", "SetVisibility2D", "SetSliceProjection",
        "SliceProjection",
    ],
    "crosshair": [
        "slicer-ui-analysis", "sliceIntersectionsVisibilityCheckBox",
        "SetIntersectingSlicesEnabled", "vtkMRMLApplicationLogic",
        "IntersectingSlicesVisibility", "IntersectingSlicesInteractive",
        "IntersectingSlicesTranslation", "IntersectingSlicesRotation",
        "qSlicerViewersToolBar", "vtkMRMLSliceDisplayNode",
        "vtkMRMLSliceNode Modified", "slice intersection",
    ],
    "subject_hierarchy": [
        "GetSubjectHierarchyNode", "CreateFolderItem", "SetItemParent",
    ],
    "node_display": [
        "GetDisplayNode", "SetVisibility", "AddViewNodeID", "SetVisibility2D",
        "SetVisibility2DFill", "SetVisibility2DOutline",
    ],
    "scene_node_lookup": [
        "slicer.util.getNode", "GetFirstNodeByClass", "GetNodesByClass",
    ],
    "cli_module": [
        "slicer.cli.run", "Modules/CLI",
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _truncate_result(result, max_chars: int = 2000) -> str:
    """Truncate a tool result dict to a compact preview string for debug output."""
    if not isinstance(result, dict):
        s = str(result)
        return s[:max_chars] + "..." if len(s) > max_chars else s
    if "error" in result:
        return f"ERROR: {str(result['error'])[:max_chars]}"

    if result.get("tool") == "VectorSearch":
        results = result.get("results") or []
        formatted = result.get("formatted_context") or ""
        if formatted:
            preview = formatted[:max_chars]
            suffix = "..." if len(formatted) > max_chars else ""
            return f"VectorSearch: {len(results)} result(s)\n{preview}{suffix}"
        return f"VectorSearch: {len(results)} result(s)"

    if result.get("tool") == "Grep":
        total_hits = result.get("total_hits", 0)
        total_files = result.get("total_files", 0)
        files = result.get("files") or []
        file_preview = ", ".join(
            f"{item.get('file')} ({item.get('hits', 0)})"
            for item in files[:5]
        )
        return f"Grep: {total_hits} hit(s) in {total_files} file(s): {file_preview}"

    content = result.get("content", "")
    if isinstance(content, str):
        return content[:max_chars] + "..." if len(content) > max_chars else content
    return str(result)[:max_chars]


def _dedupe_keep_order(values: List[str], limit: Optional[int] = None) -> List[str]:
    """Return non-empty strings in first-seen order."""
    seen = set()
    out = []
    for value in values:
        if not value:
            continue
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
        if limit is not None and len(out) >= limit:
            break
    return out


def _is_ui_analysis_path(path: Any) -> bool:
    if not isinstance(path, str):
        return False
    normalized = path.replace("\\", "/").lower()
    return (
        normalized == "slicer-ui-analysis"
        or normalized.startswith(_UI_ANALYSIS_PREFIX)
        or "/slicer_ui_preanalysis/" in normalized
    )


def _collect_tool_result_files(result: Any) -> Tuple[List[str], List[str]]:
    """Collect UI-analysis and non-UI file paths mentioned in a tool result."""
    ui_files: List[str] = []
    other_files: List[str] = []

    def _add(path: Any, source_type: str = "") -> None:
        if not isinstance(path, str) or not path:
            return
        if _is_ui_analysis_path(path) or source_type == "ui_analysis":
            ui_files.append(path)
        else:
            other_files.append(path)

    if not isinstance(result, dict):
        return [], []

    if result.get("source_type") == "ui_analysis":
        _add(result.get("path") or result.get("file"), "ui_analysis")
    else:
        _add(result.get("path") or result.get("file"), result.get("source_type", ""))

    for item in result.get("results") or []:
        if isinstance(item, dict):
            _add(item.get("file_path") or item.get("file"), item.get("source_type", ""))

    for item in result.get("files") or []:
        if isinstance(item, dict):
            _add(item.get("file"), item.get("source_type", ""))

    for item in result.get("representative_matches") or []:
        if isinstance(item, dict):
            _add(item.get("file"), item.get("source_type", ""))

    formatted = result.get("formatted_context")
    if isinstance(formatted, str):
        for match in re.finditer(r"slicer-ui-analysis/[^\s`'\"),]+", formatted):
            ui_files.append(match.group(0))

    return _dedupe_keep_order(ui_files, 20), _dedupe_keep_order(other_files, 20)


def _extract_ui_lines(text: str, limit: int = 20) -> List[str]:
    """Extract audit-relevant lines from UI-analysis markdown/tool output."""
    if not isinstance(text, str) or not text:
        return []
    interesting = []
    prefixes = (
        "## widget:",
        "## action:",
        "- Confidence:",
        "- Search text:",
        "- Text:",
        "- Tooltip:",
        "- Implementation candidates:",
        "- Matched implementation lines:",
        "- Connected slots/functions:",
        "- API footprints:",
        "- Key UI properties:",
    )
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith(prefixes):
            interesting.append(line)
        elif (
            line.startswith("- `")
            and any(marker in line for marker in (".cxx:", ".cpp:", ".h:", ".py:"))
        ):
            interesting.append(line)
    return _dedupe_keep_order(interesting, limit)


def _extract_backticked_values(lines: List[str], label: str, limit: int = 30) -> List[str]:
    values: List[str] = []
    for line in lines:
        if label not in line:
            continue
        values.extend(re.findall(r"`([^`]+)`", line))
    return _dedupe_keep_order(values, limit)


def _summarize_tool_evidence(tool_calls_history: List[Dict]) -> Dict[str, Any]:
    """Summarize whether/how the ground phase used generated Slicer UI pre-analysis."""
    ui_query_paths: List[str] = []
    ui_result_files: List[str] = []
    non_ui_result_files: List[str] = []
    vector_queries: List[str] = []
    grep_patterns: List[str] = []
    read_paths: List[str] = []
    ui_lines: List[str] = []
    source_type_counts: Dict[str, int] = {}

    for call in tool_calls_history or []:
        if not isinstance(call, dict):
            continue
        tool = call.get("tool", "")
        args = call.get("args") or {}
        result = call.get("result") or {}

        if tool == "VectorSearch":
            vector_queries.append(str(args.get("query", "")))
        elif tool == "Grep":
            grep_patterns.append(str(args.get("pattern", "")))
        elif tool == "ReadFile":
            read_paths.append(str(args.get("path", "")))

        path_arg = args.get("path")
        if _is_ui_analysis_path(path_arg):
            ui_query_paths.append(path_arg)

        for item in result.get("results") or []:
            if isinstance(item, dict):
                st = item.get("source_type", "")
                if st:
                    source_type_counts[st] = source_type_counts.get(st, 0) + 1
        for item in result.get("files") or []:
            if isinstance(item, dict):
                st = item.get("source_type", "")
                if st:
                    source_type_counts[st] = source_type_counts.get(st, 0) + 1
        result_source_type = result.get("source_type")
        if result_source_type:
            source_type_counts[result_source_type] = source_type_counts.get(result_source_type, 0) + 1

        ui_files, other_files = _collect_tool_result_files(result)
        ui_result_files.extend(ui_files)
        non_ui_result_files.extend(other_files)

        formatted = result.get("formatted_context")
        if isinstance(formatted, str) and "slicer-ui-analysis/" in formatted:
            ui_lines.extend(_extract_ui_lines(formatted))

        content = result.get("content")
        if result.get("source_type") == "ui_analysis" and isinstance(content, str):
            ui_lines.extend(_extract_ui_lines(content))

        for item in result.get("representative_matches") or []:
            if not isinstance(item, dict):
                continue
            if _is_ui_analysis_path(item.get("file")):
                ui_lines.extend(_extract_ui_lines(item.get("context", "")))
                content_line = item.get("content")
                if isinstance(content_line, str):
                    ui_lines.extend(_extract_ui_lines(content_line))

    ui_lines = _dedupe_keep_order(ui_lines, 25)
    ui_result_files = _dedupe_keep_order(ui_result_files, 20)
    non_ui_result_files = _dedupe_keep_order(non_ui_result_files, 20)

    return {
        "ui_analysis": {
            "used": bool(ui_query_paths or ui_result_files or source_type_counts.get("ui_analysis")),
            "query_paths": _dedupe_keep_order(ui_query_paths, 10),
            "result_files": ui_result_files,
            "matched_lines_preview": ui_lines,
            "connected_slots": _extract_backticked_values(ui_lines, "Connected slots/functions"),
            "api_footprints": _extract_backticked_values(ui_lines, "API footprints"),
            "implementation_candidates": _extract_backticked_values(ui_lines, "Implementation candidates"),
        },
        "source_verification": {
            "non_ui_result_files": non_ui_result_files,
            "source_type_counts": source_type_counts,
        },
        "searches": {
            "vector_queries": _dedupe_keep_order(vector_queries, 10),
            "grep_patterns": _dedupe_keep_order(grep_patterns, 10),
            "read_paths": _dedupe_keep_order(read_paths, 10),
        },
    }


# ---------------------------------------------------------------------------
# SlicerOpGenerator
# ---------------------------------------------------------------------------


__all__ = [name for name in list(globals()) if not name.startswith('__')]
