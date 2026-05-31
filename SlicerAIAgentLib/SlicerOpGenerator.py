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
import logging
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Callable, Dict, List, Optional, Tuple

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
- `slicer-extensions/` — Extension repositories
- `slicer-dependencies/` — VTK, ITK, CTK, etc.

You have three search tools: VectorSearch, Grep, ReadFile.

### When to search vs. skip
- If you already know the Slicer API from training (e.g. setLayout, SetSliceVisible, \
SetSliceResolutionMode), skip search entirely and generate code directly.
- If unsure about an API signature, do **one** VectorSearch or Grep to confirm, \
then generate code immediately.
- You have up to 15 tool rounds total. Prefer fewer rounds — generate code as soon \
as you have enough evidence.

### Efficient search order
If you need to search, prefer these sources in order:
1. `slicer-source/Docs/developer_guide/script_repository/` — official cookbook examples
2. `slicer-source/Base/Python/slicer/util.py` — core Python API
3. `slicer-source/Modules/CLI/` — ready-made CLI operations
4. `slicer-source/Modules/Scripted/<relevant-module>/` — Python modules
5. `slicer-source/Modules/Loadable/<relevant-module>/` — C++ modules with Python wrappers
6. `slicer-source/Libs/MRML/Core/` — MRML node definitions

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
- Use `{placeholder}` syntax for runtime values, e.g. `{volume_name: Mandible}`.
- Do NOT use f-strings (single braces are template placeholders). Use %-formatting.
  If you need literal braces, double them: `{{expr}}`.
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


def _get_allowed_tool_defs() -> List[Dict]:
    """Return tool definitions filtered to only KB search tools."""
    from .SkillTools import get_skill_tools
    return [
        t for t in get_skill_tools()
        if t.get("function", {}).get("name") in _ALLOWED_TOOLS
    ]


# ---------------------------------------------------------------------------
# Category inference helpers (used to build user prompt hints)
# ---------------------------------------------------------------------------

_CATEGORY_SEARCH_HINTS = {
    "layout_slice_view": [
        "layoutManager", "vtkMRMLLayoutNode", "sliceWidget",
        "mrmlSliceNode", "SetSliceVisible", "SetSliceResolutionMode",
        "SliceResolutionMatch2DView", "SliceResolutionMatchVolumes",
        "SetViewArrangement", "SlicerLayoutConventionalView", "SetLayout",
        "AddLayoutDescription", "GetLayoutByName",
    ],
    "module_switching": [
        "slicer.util.selectModule", "moduleSelector", "markups module",
        "selectModule",
    ],
    "markups_display": [
        "vtkMRMLMarkupsDisplayNode", "AddViewNodeID", "SetActiveListID",
        "Markups display advanced view",
    ],
    "crosshair": [
        "vtkMRMLCrosshairNode", "SetCrosshairMode", "ShowIntersection",
        "NoCrosshair", "CrosshairBehavior", "OffsetJumpSlice",
        "CenteredJumpSlice", "SetCrosshairBehavior", "slice intersection",
    ],
    "subject_hierarchy": [
        "GetSubjectHierarchyNode", "CreateFolderItem", "SetItemParent",
    ],
    "node_display": [
        "GetDisplayNode", "SetVisibility", "AddViewNodeID",
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
    # For search results, show summary counts instead of full content
    if "error" in result:
        return f"ERROR: {str(result['error'])[:max_chars]}"
    content = result.get("content", "")
    if isinstance(content, str):
        return content[:max_chars] + "..." if len(content) > max_chars else content
    return str(result)[:max_chars]


# ---------------------------------------------------------------------------
# SlicerOpGenerator
# ---------------------------------------------------------------------------

class SlicerOpGenerator:
    """Generate code templates for slicer_op steps using the main agent's
    tool-calling loop (chatWithToolsIsolated).

    The LLM adaptively searches the KB and generates code in one integrated
    pass — the same pipeline the main agent uses for interactive queries.
    """

    def __init__(
        self,
        llm_client,
        skill_executor=None,
        skill_path: Optional[str] = None,
        on_progress=None,
        debug_path: Optional[str] = None,
    ):
        self.llm_client = llm_client
        self._executor = skill_executor
        self._skill_path = skill_path
        self._executor_initialized = skill_executor is not None
        self._on_progress = on_progress
        self._debug_path = debug_path

    # ------------------------------------------------------------------
    # Lazy SkillToolExecutor initialization
    # ------------------------------------------------------------------

    def _ensure_executor(self):
        if self._executor_initialized:
            return
        self._executor_initialized = True
        if not self._skill_path or not os.path.isdir(self._skill_path):
            logger.warning("No skill_path for SlicerOpGenerator KB search")
            return
        try:
            from .SkillTools import SkillToolExecutor
            self._executor = SkillToolExecutor(self._skill_path)
            logger.info("SlicerOpGenerator: SkillToolExecutor loaded.")
        except Exception:
            logger.exception("SlicerOpGenerator: failed to load SkillToolExecutor")

    @staticmethod
    def _infer_category(sub_op) -> str:
        category = getattr(sub_op, "slicer_op_category", None)
        if category:
            return category
        text = (
            getattr(sub_op, "description", "") + " "
            + " ".join(getattr(sub_op, "slicer_api_keywords", []) or [])
        ).lower()
        if any(t in text for t in ("layout", "slice visibility", "red view", "fov", "spacing")):
            return "layout_slice_view"
        if "crosshair" in text or "slice intersection" in text:
            return "crosshair"
        if "markups module" in text or "open the markups" in text:
            return "module_switching"
        if "display panel" in text or "advanced panel" in text:
            return "markups_display"
        if "subject hierarchy" in text or "folder" in text:
            return "subject_hierarchy"
        if "display" in text or "visibility" in text:
            return "node_display"
        return "generic_slicer_api"

    # ------------------------------------------------------------------
    # Tool executor adapter
    # ------------------------------------------------------------------

    def _make_tool_executor(self) -> Callable[[str, Dict], Dict]:
        """Create a tool executor that only allows KB search tools."""
        def executor(tool_name: str, arguments: Dict) -> Dict:
            if tool_name not in _ALLOWED_TOOLS:
                return {"error": f"Tool '{tool_name}' is not available during template generation"}
            return self._executor.execute(tool_name, arguments)
        return executor

    # ------------------------------------------------------------------
    # Prompt construction
    # ------------------------------------------------------------------

    @staticmethod
    def _build_user_message(sub_op, category: str) -> str:
        """Build the user prompt for a single slicer_op sub-operation."""
        parts = [f"Generate a Python code template for this 3D Slicer operation:\n"]
        parts.append(sub_op.description)

        hints = _CATEGORY_SEARCH_HINTS.get(category, [])
        if hints:
            parts.append(f"\nSuggested API terms to search for: {', '.join(hints[:8])}")

        keywords = getattr(sub_op, "slicer_api_keywords", []) or []
        if keywords:
            parts.append(f"\nAPI keyword hints: {', '.join(keywords[:8])}")

        parts.append(
            "\n\nSearch the knowledge base for relevant examples first, "
            "then output ONLY the ```python code block."
        )
        return "".join(parts)

    # ------------------------------------------------------------------
    # Code generation via tool-calling loop
    # ------------------------------------------------------------------

    def _generate_one(self, sub_op, category: str, op_record: dict,
                      lock, _write_debug, emit_progress=None) -> Tuple[str, str]:
        """Generate a code template for one sub-op via the tool-calling loop.

        Returns (code, status) where status is "done" or "fallback".
        Writes intermediate debug state to op_record for live diagnostics.
        """
        import time as _time

        desc_short = sub_op.description.split("\n")[0][:50]

        # Step 1: Build prompt
        op_record["status"] = "building_prompt"
        _write_debug()
        t_prompt_start = _time.monotonic()

        messages = [
            {"role": "system", "content": _SLICER_OP_SYSTEM_PROMPT},
            {"role": "user", "content": self._build_user_message(sub_op, category)},
        ]

        op_record["prompt_build_s"] = round(_time.monotonic() - t_prompt_start, 3)
        logger.info("[5T] '%s' prompt built", desc_short)

        # Step 2: Prepare tools and executor
        op_record["status"] = "preparing_tools"
        _write_debug()

        tools = _get_allowed_tool_defs()
        executor = self._make_tool_executor()

        executor_ready = self._executor is not None
        op_record["executor_ready"] = executor_ready
        op_record["tool_count"] = len(tools)
        logger.info(
            "[5T] '%s' tools prepared: executor=%s, %d tools",
            desc_short, executor_ready, len(tools),
        )

        if not executor_ready:
            op_record["status"] = "no_executor"
            _write_debug()
            logger.warning("[5T] '%s' no executor — generating from LLM knowledge only", desc_short)

        # Step 3: Call tool-calling loop
        op_record["status"] = "tool_loop_running"
        _write_debug()
        t_loop_start = _time.monotonic()
        logger.info("[5T] '%s' chatWithToolsIsolated starting...", desc_short)

        def _on_tool_progress(progress: Dict):
            progress_text = (progress.get("reasoning_content") or "").strip()
            if not progress_text:
                return
            progress_text = progress_text.replace("\n", " | ")
            round_num = progress.get("round")
            phase = progress.get("phase", "tool")
            event = {
                "round": round_num,
                "phase": phase,
                "message": progress_text[:500],
            }
            with lock:
                op_record.setdefault("progress_events", []).append(event)
                op_record["progress_events"] = op_record["progress_events"][-12:]
                op_record["last_progress"] = event
            _write_debug()
            if emit_progress:
                detail = progress_text
                if round_num:
                    detail = f"round {round_num} {phase}: {progress_text}"
                emit_progress(detail)

        try:
            response = self.llm_client.chatWithToolsIsolated(
                messages=messages,
                tools=tools,
                tool_executor=executor,
                max_tool_rounds=_MAX_TOOL_ROUNDS,
                on_progress=_on_tool_progress,
            )
        except Exception as exc:
            t_loop_end = _time.monotonic()
            op_record["status"] = "tool_loop_exception"
            op_record["tool_loop_s"] = round(t_loop_end - t_loop_start, 2)
            op_record["error"] = f"chatWithToolsIsolated raised {type(exc).__name__}: {exc}"
            _write_debug()
            logger.exception("[5T] '%s' chatWithToolsIsolated FAILED after %.1fs",
                             desc_short, t_loop_end - t_loop_start)
            raise

        t_loop_end = _time.monotonic()
        tool_loop_s = t_loop_end - t_loop_start

        # Extract detailed debug info from response
        timing_report = response.get("timing_report", {})
        tool_calls_history = response.get("tool_calls_history", [])

        # Summary fields
        op_record["status"] = "tool_loop_done"
        op_record["tool_loop_s"] = round(tool_loop_s, 2)
        op_record["tool_rounds"] = timing_report.get("tool_rounds", 0)
        op_record["api_calls"] = timing_report.get("api_calls", 0)
        op_record["total_tokens"] = timing_report.get("total_tokens", 0)
        op_record["total_api_time_s"] = round(timing_report.get("total_api_time", 0), 3)
        op_record["total_tool_time_s"] = round(timing_report.get("total_tool_time", 0), 3)
        op_record["tool_names_called"] = list(dict.fromkeys(
            tc.get("tool", "") for tc in tool_calls_history
        ))

        # Per-round timing breakdown
        rounds_data = timing_report.get("rounds", [])
        op_record["rounds"] = [
            {
                "round": r.get("round"),
                "phase": r.get("phase"),
                "api_time_s": r.get("api_time"),
                "tool_time_s": r.get("tool_time"),
                "round_time_s": r.get("round_time"),
                "tools": r.get("tools", []),
                "tokens": r.get("tokens", 0),
            }
            for r in rounds_data
        ]

        # Full tool call history (truncate large results)
        _MAX_RESULT_CHARS = 2000
        op_record["tool_calls_history"] = [
            {
                "tool": tc.get("tool", ""),
                "args": tc.get("args", {}),
                "result_preview": _truncate_result(tc.get("result"), _MAX_RESULT_CHARS),
            }
            for tc in tool_calls_history
        ]

        # LLM reasoning content (truncated)
        reasoning = response.get("reasoning_content", "")
        if reasoning:
            op_record["reasoning_chars"] = len(reasoning)
            op_record["reasoning_preview"] = reasoning[:3000]
        else:
            op_record["reasoning_chars"] = 0

        _write_debug()

        logger.info(
            "[5T] '%s' tool loop done: %.1fs, %d rounds, %d API calls, %d tokens, "
            "api=%.1fs tool=%.1fs, tools=%s",
            desc_short, tool_loop_s,
            len(rounds_data),
            timing_report.get("api_calls", 0),
            timing_report.get("total_tokens", 0),
            timing_report.get("total_api_time", 0),
            timing_report.get("total_tool_time", 0),
            op_record["tool_names_called"],
        )

        # Step 4: Extract code
        op_record["status"] = "extracting_code"
        _write_debug()

        code = response.get("code")

        if not code:
            content = response.get("message", "")
            op_record["raw_response_chars"] = len(content)
            code = self._strip_fences(content)

        if not code:
            op_record["status"] = "no_code"
            op_record["error"] = "LLM did not produce code"
            _write_debug()
            logger.warning("[5T] '%s' no code produced", desc_short)
            return self._generation_failed_template(
                sub_op, "LLM did not produce code after tool rounds"
            ), "fallback"

        # Step 5: Sanitize and validate
        op_record["status"] = "validating"
        _write_debug()

        code = code.replace("\x00", "").replace("\r\n", "\n").replace("\r", "\n")

        try:
            ast.parse(code)
        except (SyntaxError, IndentationError) as e:
            op_record["status"] = "fixing_syntax"
            op_record["syntax_error"] = str(e)
            _write_debug()
            logger.warning("[5T] '%s' syntax error, retrying: %s", desc_short, e)
            code = self._fix_syntax(code, sub_op)

        return code, "done"

    def _fix_syntax(self, code: str, sub_op) -> str:
        """Try to fix syntax errors via a single LLM call."""
        messages = [
            {
                "role": "system",
                "content": (
                    "Fix Python syntax errors. The code uses {placeholder} template "
                    "syntax — do NOT convert these to f-strings. Output ONLY the "
                    "corrected code, no explanation, no markdown fences."
                ),
            },
            {
                "role": "user",
                "content": f"Fix the syntax error in this code:\n\n{code}",
            },
        ]
        try:
            response = self.llm_client.chatIsolated(messages)
            fixed = response.get("message", "")
            fixed = self._strip_fences(fixed)
            ast.parse(fixed)
            return fixed
        except Exception:
            return code

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self, sub_ops: List[tuple]) -> Dict[str, str]:
        """Generate code templates for all slicer_op sub-operations.

        Args:
            sub_ops: List of (step_number, SubOperation) tuples.

        Returns:
            Dict mapping "cb_step_{num}_{idx}" -> template code string.
        """
        import time as _time
        import threading as _threading
        import json as _json

        self._ensure_executor()

        results: Dict[str, str] = {}
        total = len(sub_ops)
        started = [0]
        finished = [0]
        lock = _threading.Lock()
        errors: list = []
        debug_log: list = []
        timed_out_keys = set()

        def _write_debug():
            if not self._debug_path:
                return
            try:
                with open(self._debug_path, "w", encoding="utf-8") as f:
                    _json.dump({
                        "stage": "5T",
                        "total_operations": total,
                        "started": started[0],
                        "finished": finished[0],
                        "errors_count": len(errors),
                        "operations": debug_log,
                    }, f, indent=2)
            except Exception:
                pass

        if not sub_ops:
            return results

        def _emit_progress(finished_count: int, total_count: int, detail: str):
            if not self._on_progress:
                return
            try:
                self._on_progress(finished_count, total_count, detail)
            except Exception:
                logger.debug("[5T] progress callback failed", exc_info=True)

        def _gen_one(item: tuple, idx: int) -> Tuple[str, str]:
            step_num, sub_op = item
            key = f"cb_step_{step_num}_{idx}"
            desc_short = sub_op.description.split("\n")[0][:60]
            category = self._infer_category(sub_op)
            t0 = _time.monotonic()

            op_record = {
                "step": step_num,
                "key": key,
                "description": sub_op.description[:200],
                "keywords": sub_op.slicer_api_keywords[:10],
                "category": category,
                "status": "started",
                "total_time_s": None,
                "code_chars": 0,
                "tool_rounds": None,
                "api_calls": None,
                "error": None,
                "progress_events": [],
            }

            with lock:
                started[0] += 1
                started_idx = started[0]
                debug_log.append(op_record)
            logger.info(
                "[5T] step %d STARTED [%d/%d]: %s",
                step_num, started_idx, total, desc_short,
            )
            _write_debug()
            _emit_progress(finished[0], total, f"started {desc_short}")

            def _emit_op_progress(detail: str):
                with lock:
                    if key in timed_out_keys:
                        return
                _emit_progress(finished[0], total, f"{desc_short}: {detail}")

            try:
                code, status = self._generate_one(
                    sub_op, category, op_record, lock, _write_debug,
                    emit_progress=_emit_op_progress,
                )
                t1 = _time.monotonic()

                with lock:
                    timed_out = key in timed_out_keys
                if timed_out:
                    return key, code

                op_record["status"] = status
                op_record["total_time_s"] = round(t1 - t0, 2)
                op_record["code_chars"] = len(code)

                logger.info(
                    "[5T] step %d done: %.1fs, code=%d chars, status=%s  %s",
                    step_num, t1 - t0, len(code), status, desc_short,
                )

                if status == "fallback":
                    with lock:
                        errors.append(
                            f"Step {step_num} ({desc_short}): used fallback template"
                        )

                return key, code
            except Exception as exc:
                err_msg = f"Step {step_num} FAILED: {type(exc).__name__}: {exc}"
                with lock:
                    timed_out = key in timed_out_keys
                if timed_out:
                    return key, (
                        f"# Timed out or failed after timeout: {sub_op.description}\n"
                        f"# Error: {exc}\npass"
                    )
                op_record["status"] = "failed"
                op_record["error"] = err_msg
                logger.exception("[5T] %s", err_msg)
                with lock:
                    errors.append(err_msg)
                return key, f"# Failed to generate slicer_op: {sub_op.description}\n# Error: {exc}\npass"
            finally:
                with lock:
                    timed_out = key in timed_out_keys
                    if timed_out:
                        fin = finished[0]
                    else:
                        finished[0] += 1
                        fin = finished[0]
                _write_debug()
                if not timed_out:
                    _emit_progress(fin, total, f"done {desc_short}")

        logger.info("[5T] Starting generation of %d slicer_op templates (sequential)", total)
        _write_debug()
        _emit_progress(0, total, f"starting {total} slicer_op templates")

        for idx, item in enumerate(sub_ops):
            step_num, sub_op = item
            desc = sub_op.description[:60]
            key = f"cb_step_{step_num}_{idx}"
            pool = ThreadPoolExecutor(max_workers=1)
            future = pool.submit(_gen_one, item, idx)
            try:
                result_key, code = future.result(timeout=_PER_OP_TIMEOUT_S)
                results[result_key] = code
            except FuturesTimeoutError:
                err_msg = (
                    f"Step {step_num} ({desc}): timed out after "
                    f"{_PER_OP_TIMEOUT_S}s"
                )
                logger.warning("[5T] %s", err_msg)
                future.cancel()
                with lock:
                    timed_out_keys.add(key)
                    errors.append(err_msg)
                    for rec in debug_log:
                        if rec.get("key") == key:
                            rec["status"] = "timeout"
                            rec["error"] = err_msg
                            break
                results[key] = f"# Timed out: {desc}\npass"
                _write_debug()
                _emit_progress(finished[0], total, err_msg)
            except Exception as exc:
                err_type = type(exc).__name__
                err_msg = f"Step {step_num} ({desc}): {err_type}: {exc}"
                logger.warning("[5T] %s", err_msg)
                with lock:
                    errors.append(err_msg)
                    for rec in debug_log:
                        if rec.get("key") == key:
                            rec["status"] = "failed"
                            rec["error"] = err_msg
                            break
                results[key] = f"# Timed out or failed: {desc}\n# {err_type}: {exc}\npass"
                _write_debug()
                _emit_progress(finished[0], total, err_msg)
            finally:
                pool.shutdown(wait=False, cancel_futures=True)

        logger.info(
            "[5T] Generation complete: %d/%d succeeded, %d errors",
            len(results) - len(errors), total, len(errors),
        )
        if errors:
            logger.warning("[5T] Errors:\n  %s", "\n  ".join(errors))

        _write_debug()
        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _generation_failed_template(sub_op, reason: str) -> str:
        desc = getattr(sub_op, "description", "")
        safe_reason = reason.replace('"', "'")
        return (
            f"# [{_GENERATION_FAILED_SENTINEL}] {safe_reason}\n"
            f"# Operation: {desc}\n"
            "raise RuntimeError("
            f"\"Slicer-op template generation failed: {safe_reason}\""
            ")\n"
        )

    @staticmethod
    def _strip_fences(text: str) -> str:
        """Remove surrounding ```python ... ``` fences."""
        text = text.strip()
        if text.startswith("```"):
            nl = text.find("\n")
            if nl >= 0:
                text = text[nl + 1:]
            if text.rstrip().endswith("```"):
                text = text.rstrip()[:-3].rstrip()
        return text
