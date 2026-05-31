"""
SlicerOpGenerator - Generate code templates for Slicer core API operations
(Type 2 / slicer_op sub-operations) by searching the knowledge base.

Mirrors the main agent's two-phase retrieval architecture:
  Phase 1 (pre-retrieval): query decomposition → multi-query vector search →
         source-type re-ranking → full-file promotion → symbol search.
  Phase 2 (iterative deepening): up to _MAX_ROUNDS of adaptive
         grep / readfile / symbol search with convergence detection.

Uses SkillToolExecutor (shared with the main agent) for all search operations.
"""

import logging
import os
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Code generation prompts
# ---------------------------------------------------------------------------

_CODEGEN_SYSTEM_PROMPT = """\
You are a 3D Slicer Python code generator.  Given a description of a Slicer
operation and relevant code snippets from the Slicer knowledge base, generate
a standalone Python code template that implements the operation.

Requirements:
- The code must run inside Slicer's Python environment (has `slicer` and `vtk`).
- Use `slicer.mrmlScene`, `slicer.app.layoutManager()`, etc. directly.
- If the operation involves finding a specific node by name, use fuzzy name
  matching (iterate nodes, check if a keyword appears in the name).
- Use `{placeholder}` syntax for values that depend on runtime context,
  e.g. `{volume_name: Mandible}` or `{layout_name: Conventional}`.
- Do NOT use f-strings. Single braces `{...}` are interpreted as template
  placeholders by the runtime template engine. Use %-formatting instead:
  `print("Found %d nodes" % count)` not `print(f"Found {count} nodes")`.
  If you must use literal braces, double them: `{{expr}}`.
- Keep the code short and focused on the single operation described.
- Do NOT import os, subprocess, sys, socket, or use eval/exec/open.
- Do NOT use destructive operations.
- Output ONLY the Python code, no markdown fences, no explanation.
"""

_RETRIEVAL_POLICY = """\
Retrieval policy:
- Review pre-retrieved snippets before searching broader sources.
- Prefer script repository examples and API docs, then exact API definitions.
- Use targeted source areas before broad search:
  1. slicer-source/Base/Python/slicer/util.py
  2. slicer-source/Modules/CLI/
  3. slicer-source/Modules/Scripted/<relevant-module>/
  4. slicer-source/Modules/Loadable/<relevant-module>/
  5. slicer-source/Base/Python/slicer/
  6. slicer-source/Libs/MRML/Core/
- Stop when evidence is sufficient; do not search for completeness.
"""

_CODEGEN_USER_TEMPLATE = """\
{retrieval_policy}

## Operation to implement

{description}

## Relevant Slicer code snippets from knowledge base

{snippets}

Generate the Python code template:"""


# ---------------------------------------------------------------------------
# Query decomposition prompt
# ---------------------------------------------------------------------------

_DECOMPOSE_SYSTEM_PROMPT = """\
You are a search query optimizer for a 3D Slicer code knowledge base.
Given a description of a Slicer operation, produce 2-4 short, diverse search
queries that would find relevant code examples.

Rules:
- Each query should target a different aspect (e.g. one for the main API call,
  one for parameter setup, one for node creation/display).
- Use concrete Slicer API names if mentioned in the description.
- Keep each query under 10 words.
- Return ONLY a JSON array of strings, no other text."""

_DECOMPOSE_THRESHOLD_WORDS = 8  # skip decomposition for short descriptions


# ---------------------------------------------------------------------------
# Search configuration
# ---------------------------------------------------------------------------

_MAX_ROUNDS = 10
_MAX_SNIPPET_CHARS = 25000
_CONVERGENCE_THRESHOLD_CHARS = 300
_PER_OP_TIMEOUT_S = 120  # Max seconds per slicer_op before giving up
_MIN_EVIDENCE_CHARS = 300
_NO_EVIDENCE_TEXT = "(No relevant snippets found in knowledge base)"
_GENERATION_FAILED_SENTINEL = "SLICER_OP_GENERATION_FAILED"

# Source-type weights (mirrors VectorRetriever._SOURCE_TYPE_WEIGHT)
_SOURCE_TYPE_WEIGHTS = {
    "doc_example": 1.3,
    "python_api": 1.2,
    "effect_implementation": 1.1,
    "scripted_module": 1.1,
    "test_example": 1.05,
    "source": 1.0,
}

# Full-file promotion threshold (mirrors main agent's _buildRetrievalContext)
_FULL_FILE_CHUNK_THRESHOLD = 3

# How many top files from vector/grep to queue for reading
_MAX_READFILE_PER_ROUND = 6
_MAX_GREP_FILES_TO_QUEUE = 8

_CATEGORY_SEARCH_HINTS = {
    "layout_slice_view": [
        "layoutManager", "vtkMRMLLayoutNode", "sliceWidget",
        "mrmlSliceNode", "SetSliceVisible", "SpacingModeMatch2D",
    ],
    "module_switching": [
        "slicer.util.selectModule", "moduleSelector", "markups module",
    ],
    "markups_display": [
        "vtkMRMLMarkupsDisplayNode", "AddViewNodeID", "SetActiveListID",
        "Markups display advanced view",
    ],
    "crosshair": [
        "vtkMRMLCrosshairNode", "SetCrosshairMode", "ShowIntersection",
        "slice intersection",
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

_CATEGORY_TARGET_PATHS = {
    "layout_slice_view": [
        "slicer-source/Base/Python/slicer/",
        "slicer-source/Libs/MRML/Core/",
    ],
    "module_switching": [
        "slicer-source/Base/Python/slicer/util.py",
        "slicer-source/Base/Python/slicer/",
    ],
    "markups_display": [
        "slicer-source/Modules/Loadable/Markups/",
        "slicer-source/Docs/developer_guide/script_repository/",
        "slicer-source/Libs/MRML/Core/",
    ],
    "crosshair": [
        "slicer-source/Libs/MRML/Core/",
        "slicer-source/Modules/Loadable/",
    ],
    "subject_hierarchy": [
        "slicer-source/Libs/MRML/Core/",
        "slicer-source/Base/Python/slicer/",
    ],
    "node_display": [
        "slicer-source/Libs/MRML/Core/",
        "slicer-source/Modules/Loadable/",
    ],
    "cli_module": [
        "slicer-source/Modules/CLI/",
    ],
}


# ---------------------------------------------------------------------------
# _SearchContext — accumulates evidence across rounds
# ---------------------------------------------------------------------------

class _SearchContext:
    """Accumulates evidence across multiple search rounds for one sub-operation."""

    def __init__(self, description: str, keywords: List[str]):
        self.description = description
        self.keywords = list(keywords)
        self.sub_queries: List[str] = []  # decomposed queries
        self.round_logs: List[str] = []
        self._snippet_parts: List[str] = []
        self._files_read: Set[str] = set()
        self._grep_file_hits: List[str] = []
        self._prev_length: int = 0
        # Vector search result tracking for full-file promotion
        self._chunk_file_counts: Counter = Counter()
        self._full_file_paths: Set[str] = set()
        # Symbol names discovered (for SearchSymbol rounds)
        self._symbol_names: Set[str] = set()

    def add_snippet(self, source: str, content: str):
        self._snippet_parts.append(content)
        self.round_logs.append(source)

    def mark_file_read(self, path: str):
        self._files_read.add(path)

    def already_read(self, path: str) -> bool:
        return path in self._files_read

    def get_accumulated(self) -> str:
        if not self._snippet_parts:
            return _NO_EVIDENCE_TEXT
        combined = "\n\n".join(self._snippet_parts)
        if len(combined) > _MAX_SNIPPET_CHARS:
            combined = combined[:_MAX_SNIPPET_CHARS] + "\n\n# ... [truncated for length]"
        return combined

    def current_length(self) -> int:
        return sum(len(p) for p in self._snippet_parts)

    def is_converged(self) -> bool:
        current = self.current_length()
        delta = current - self._prev_length
        converged = delta < _CONVERGENCE_THRESHOLD_CHARS
        self._prev_length = current
        return converged

    def add_keywords(self, new_kws: List[str]) -> None:
        for kw in new_kws:
            if kw and kw not in self.keywords:
                self.keywords.append(kw)


# ---------------------------------------------------------------------------
# Helper: extract API terms from snippets for query expansion
# ---------------------------------------------------------------------------

_SKIP_TERMS = {
    "GetNumberOfItems", "GetItemAsObject", "GetNumberOfValues",
    "GetDisplayNode", "GetName", "SetName", "GetValue", "SetValue",
    "NewInstance", "SafeDownCast", "GetClassName", "IsA",
    "GetModifiedEvent", "InvokeEvent", "AddObserver",
    "PrintSelf", "GetDebug", "SetDebug",
}


def _extract_api_terms_from_snippets(snippets: str, max_terms: int = 6) -> List[str]:
    """Extract plausible Slicer API search terms from accumulated snippets.

    Looks for camelCase/PascalCase identifiers that look like Slicer API calls
    and returns the most distinctive ones as potential grep keywords.
    """
    # CamelCase with at least 2 humps
    candidates = set(re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b', snippets))
    candidates -= _SKIP_TERMS
    # Shorter names tend to be more specific API calls
    return sorted(candidates, key=len)[:max_terms]


def _extract_symbol_names(snippets: str, max_names: int = 8) -> List[str]:
    """Extract plausible function/method/class names for AST symbol search."""
    # snake_case function names
    snake = re.findall(r'\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\s*\(', snippets)
    # CamelCase method names after a dot
    camel = re.findall(r'\.([a-z][a-zA-Z0-9]*)\s*\(', snippets)
    # PascalCase class names after 'class' or 'new'
    pascal = re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z]+)+)\b', snippets)
    all_names = set(snake + camel + pascal) - _SKIP_TERMS
    # Deduplicate and limit
    return list(all_names)[:max_names]


# ---------------------------------------------------------------------------
# SlicerOpGenerator
# ---------------------------------------------------------------------------

class SlicerOpGenerator:
    """Search the Slicer KB (mirroring the main agent's retrieval pipeline)
    and generate code templates for slicer_op steps.

    Two-phase architecture:
      Phase 1  (pre-retrieval): query decomposition → multi-query dense
               retrieval → source-type re-ranking → full-file promotion →
               symbol search.
      Phase 2  (iterative deepening): up to _MAX_ROUNDS of adaptive
               grep / readfile / symbol search with query expansion and
               convergence detection.
    """

    def __init__(
        self,
        llm_client,
        skill_executor=None,
        skill_path: Optional[str] = None,
        on_progress=None,
        debug_path: Optional[str] = None,
    ):
        """
        Args:
            llm_client: LLMClient with chatIsolated() for code generation.
            skill_executor: Optional pre-built SkillToolExecutor. If None, one
                will be created lazily from skill_path.
            skill_path: Path to the Slicer knowledge base directory
                (Resources/Skills/slicer-skill-full/).
            on_progress: Optional callback(finished, total, description) called
                after each sub-op completes.
            debug_path: Optional path to write a stage_5T_debug.json file
                with per-operation progress. The file is updated live during
                generation so you can inspect it while the pipeline runs.
        """
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

    @staticmethod
    def _deterministic_template(sub_op, category: str) -> Optional[str]:
        """Return deterministic code for common high-confidence Slicer ops."""
        desc = getattr(sub_op, "description", "")
        text = (desc + " " + " ".join(getattr(sub_op, "slicer_api_keywords", []) or [])).lower()
        if category == "module_switching" and "markup" in text:
            return (
                "import slicer\n\n"
                "slicer.util.selectModule('Markups')\n"
                "print(\"[Slicer] Markups module opened.\")\n"
            )
        if category == "layout_slice_view":
            lines = [
                "import slicer",
                "",
                "layoutManager = slicer.app.layoutManager()",
            ]
            if "conventional" in text:
                lines.append("layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView)")
            if "red" in text or "slice" in text:
                lines.extend([
                    "redWidget = layoutManager.sliceWidget('Red')",
                    "if redWidget is None:",
                    "    raise RuntimeError(\"Red slice widget is not available\")",
                    "redSliceNode = redWidget.mrmlSliceNode()",
                ])
                if "toggle off" in text or "visibility off" in text:
                    lines.append("redSliceNode.SetSliceVisible(False)")
                elif "slice visibility" in text or "3d" in text:
                    lines.append("redSliceNode.SetSliceVisible(True)")
                if "spacing" in text or "fov" in text or "match 2d" in text:
                    lines.append("redSliceNode.SetSliceSpacingMode(slicer.vtkMRMLSliceNode.SpacingModeMatch2D)")
            lines.append("")
            lines.append("print(\"[Slicer] Layout/slice view operation completed.\")")
            return "\n".join(lines) + "\n"
        if category == "crosshair":
            return (
                "import slicer\n\n"
                "crosshairNode = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLCrosshairNode')\n"
                "if crosshairNode is None:\n"
                "    crosshairNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLCrosshairNode', 'Crosshair')\n"
                "crosshairNode.SetCrosshairMode(slicer.vtkMRMLCrosshairNode.ShowIntersection)\n"
                "print(\"[Slicer] Crosshair slice intersection visibility enabled.\")\n"
            )
        return None

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
        self._time_mod = _time  # store for use in _iterative_search

        self._ensure_executor()

        results: Dict[str, str] = {}
        total = len(sub_ops)
        started = [0]   # mutable counter for start tracking
        finished = [0]  # mutable counter for completion tracking
        lock = _threading.Lock()
        errors: list = []

        # Thread-safe debug log — each entry tracks one operation's lifecycle
        debug_log: list = []

        def _write_debug():
            """Write the debug JSON file (call under lock or at end)."""
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
                pass  # debug writing must never break generation

        if not sub_ops:
            return results

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
                "search_time_s": None,
                "codegen_time_s": None,
                "total_time_s": None,
                "snippet_chars": 0,
                "code_chars": 0,
                "search_rounds": 0,
                "error": None,
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

            try:
                deterministic = self._deterministic_template(sub_op, category)
                if deterministic:
                    op_record["status"] = "deterministic"
                    op_record["search_time_s"] = 0.0
                    op_record["snippet_chars"] = 0
                    op_record["codegen_time_s"] = 0.0
                    op_record["total_time_s"] = round(_time.monotonic() - t0, 2)
                    op_record["code_chars"] = len(deterministic)
                    logger.info(
                        "[5T] step %d deterministic template (%s): %s",
                        step_num, category, desc_short,
                    )
                    return key, deterministic

                t1 = _time.monotonic()
                snippets = self._iterative_search(sub_op)
                t2 = _time.monotonic()
                search_time = t2 - t1

                op_record["status"] = "search_done"
                op_record["search_time_s"] = round(search_time, 2)
                op_record["snippet_chars"] = len(snippets)
                _write_debug()

                logger.info(
                    "[5T] step %d search done: %.1fs, snippets=%d chars  %s",
                    step_num, search_time, len(snippets), desc_short,
                )
                if self._is_low_evidence(snippets):
                    code = self._generation_failed_template(
                        sub_op,
                        "Knowledge-base search did not find enough reliable Slicer API evidence.",
                    )
                    op_record["status"] = "low_evidence"
                    op_record["error"] = "Low evidence for slicer_op generation"
                    with lock:
                        errors.append(
                            f"Step {step_num} ({desc_short}): low evidence for slicer_op generation"
                        )
                    logger.warning(
                        "[5T] step %d low evidence; emitted blocking template: %s",
                        step_num, desc_short,
                    )
                else:
                    code = self._generate_code(sub_op, snippets)
                t3 = _time.monotonic()
                codegen_time = t3 - t2

                if op_record.get("status") != "low_evidence":
                    op_record["status"] = "done"
                op_record["codegen_time_s"] = round(codegen_time, 2)
                op_record["total_time_s"] = round(t3 - t0, 2)
                op_record["code_chars"] = len(code)

                logger.info(
                    "[5T] step %d codegen done: %.1fs, code=%d chars, total=%.1fs  %s",
                    step_num, codegen_time, len(code), t3 - t0, desc_short,
                )
                return key, code
            except Exception as exc:
                err_msg = f"Step {step_num} FAILED: {type(exc).__name__}: {exc}"
                op_record["status"] = "failed"
                op_record["error"] = err_msg
                logger.exception("[5T] %s", err_msg)
                with lock:
                    errors.append(err_msg)
                return key, f"# Failed to generate slicer_op: {sub_op.description}\n# Error: {exc}\npass"
            finally:
                with lock:
                    finished[0] += 1
                    fin = finished[0]
                _write_debug()
                if self._on_progress:
                    self._on_progress(fin, total, desc_short)

        logger.info("[5T] Starting generation of %d slicer_op templates (max 4 threads)", total)
        _write_debug()

        _pool_timeout = _PER_OP_TIMEOUT_S * max(1, len(sub_ops))
        pool = ThreadPoolExecutor(max_workers=min(4, len(sub_ops)))
        futures = {pool.submit(_gen_one, item, idx): idx for idx, item in enumerate(sub_ops)}
        try:
            for future in as_completed(futures, timeout=_pool_timeout):
                idx = futures[future]
                try:
                    key, code = future.result(timeout=_PER_OP_TIMEOUT_S)
                    results[key] = code
                except Exception as exc:
                    step_num = sub_ops[idx][0]
                    desc = sub_ops[idx][1].description[:60]
                    err_type = type(exc).__name__
                    err_msg = f"Step {step_num} ({desc}): {err_type}: {exc}"
                    logger.warning("[5T] %s", err_msg)
                    with lock:
                        errors.append(err_msg)
                    key = f"cb_step_{step_num}_{idx}"
                    results[key] = f"# Timed out or failed: {desc}\n# {err_type}: {exc}\npass"

                    # Update debug record
                    with lock:
                        for rec in debug_log:
                            if rec.get("key") == key:
                                rec["status"] = "timeout" if "Timeout" in err_type else "failed"
                                rec["error"] = err_msg
                                break
                    _write_debug()
        except TimeoutError:
            # Pool timeout — cancel remaining futures and generate fallback code
            pending = [f for f in futures if not f.done()]
            logger.warning(
                "[5T] Pool timeout after %.0fs — %d operations still pending",
                _pool_timeout, len(pending),
            )
            for f in pending:
                f.cancel()
            # Generate fallback entries for any missing keys
            for idx, item in enumerate(sub_ops):
                step_num, sub_op = item
                key = f"cb_step_{step_num}_{idx}"
                if key not in results:
                    desc = sub_op.description[:60]
                    results[key] = f"# Timed out: {desc}\npass"
                    errors.append(f"Step {step_num} ({desc}): timed out")
                    with lock:
                        for rec in debug_log:
                            if rec.get("key") == key:
                                rec["status"] = "timeout"
                                rec["error"] = "Pool timeout"
                                break
            _write_debug()
        finally:
            # Shutdown pool without waiting for stuck threads (cancel=True)
            pool.shutdown(wait=False, cancel_futures=True)

        logger.info(
            "[5T] Generation complete: %d/%d succeeded, %d errors",
            len(results) - len(errors), total, len(errors),
        )
        if errors:
            logger.warning("[5T] Errors:\n  %s", "\n  ".join(errors))

        # Final debug write with summary
        _write_debug()

        return results

    # ==================================================================
    # Phase 1: Pre-retrieval (mirrors _buildRetrievalContext)
    # ==================================================================

    def _phase1_preretrieval(self, ctx: _SearchContext) -> None:
        """Run the pre-retrieval phase before iterative deepening.

        Steps:
        1. Decompose the operation description into sub-queries.
        2. Multi-query vector search with source-type re-ranking.
        3. Full-file promotion for .md files with many chunk hits.
        4. AST symbol search for concrete API names mentioned in the description.
        """
        import time as _time

        # Step 1: Query decomposition
        t0 = _time.monotonic()
        self._decompose_queries(ctx)
        t1 = _time.monotonic()
        n_queries = len(ctx.sub_queries)
        logger.info("[5T] Phase1.1 decompose: %.1fs (%d queries)", t1 - t0, n_queries)

        self._phase1_targeted_grep(ctx)
        t1b = _time.monotonic()
        logger.info("[5T] Phase1.1b targeted grep: %.1fs", t1b - t1)

        # Step 2: Multi-query vector search
        queries = ctx.sub_queries if ctx.sub_queries else [ctx.description]
        all_vector_results = []
        seen_chunk_ids: Set[str] = set()

        for query in queries:
            result = self._executor._vector_search(query, top_k=10)
            for item in result.get("results", []):
                cid = item.get("chunk_id", "")
                if cid and cid not in seen_chunk_ids:
                    seen_chunk_ids.add(cid)
                    all_vector_results.append(item)
        t2 = _time.monotonic()
        logger.info("[5T] Phase1.2 vector: %.1fs (%d chunks)", t2 - t1b, len(all_vector_results))

        # Re-rank by source-type weighted score
        all_vector_results = self._rerank_by_source_type(all_vector_results)

        # Deduplicate by file path and format
        formatted_parts = []
        seen_files: Set[str] = set()
        for item in all_vector_results[:20]:
            fpath = item.get("file_path", "")
            start = item.get("start_line", "")
            end = item.get("end_line", "")
            stype = item.get("source_type", "source")
            score = item.get("final_score", item.get("vector_score", 0))
            content = item.get("content", "")

            # Track per-file chunk counts for full-file promotion
            if fpath:
                ctx._chunk_file_counts[fpath] += 1

            if fpath in seen_files:
                continue
            seen_files.add(fpath)

            if content:
                formatted_parts.append(
                    f"### {fpath}:{start}-{end} [{stype}] (score={score:.3f})\n"
                    f"```\n{content}\n```"
                )

            if fpath:
                ctx.mark_file_read(fpath)

        if formatted_parts:
            ctx.add_snippet(
                "## Pre-retrieval vector search (multi-query, source-ranked)",
                "\n\n".join(formatted_parts),
            )

        # Step 3: Full-file promotion for .md files
        t3 = _time.monotonic()
        self._promote_full_files(ctx)
        t4 = _time.monotonic()
        logger.info("[5T] Phase1.3 full-file: %.1fs", t4 - t3)

        # Step 4: AST symbol search for concrete names in the description
        self._phase1_symbol_search(ctx)
        t5 = _time.monotonic()
        logger.info("[5T] Phase1.4 symbol: %.1fs", t5 - t4)

    def _decompose_queries(self, ctx: _SearchContext) -> None:
        """Decompose the operation description into diverse sub-queries.

        Mirrors LLMClient.decomposeQuery().  Uses a word-count heuristic to
        skip the LLM call for short descriptions.
        """
        desc = ctx.description.strip()
        keywords = ctx.keywords

        # Heuristic: short descriptions don't need decomposition
        word_count = len(desc.split())
        if word_count < _DECOMPOSE_THRESHOLD_WORDS and len(keywords) <= 2:
            ctx.sub_queries = [desc] + [k for k in keywords if k != desc]
            return

        # Try LLM decomposition
        kw_text = f" Keywords: {', '.join(keywords)}" if keywords else ""
        prompt = (
            f"{_DECOMPOSE_SYSTEM_PROMPT}\n\n"
            f"Operation: {desc}{kw_text}"
        )
        messages = [
            {"role": "system", "content": _DECOMPOSE_SYSTEM_PROMPT},
            {"role": "user", "content": f"Operation: {desc}{kw_text}"},
        ]

        try:
            response = self.llm_client.chatIsolated(messages)
            text = response.get("message", "").strip()
            # Parse JSON array
            import json
            if text.startswith("["):
                sub_queries = json.loads(text)
            else:
                # Try to find array in text
                match = re.search(r'\[[\s\S]*\]', text)
                sub_queries = json.loads(match.group()) if match else None

            if isinstance(sub_queries, list) and sub_queries:
                ctx.sub_queries = [str(q).strip() for q in sub_queries if str(q).strip()]
                return
        except Exception:
            logger.debug("Query decomposition failed, using raw description")

        # Fallback: description + each keyword as separate queries
        ctx.sub_queries = [desc] + [k for k in keywords if k and k != desc]

    def _phase1_targeted_grep(self, ctx: _SearchContext) -> None:
        """Search category-specific source areas before broad vector/grep."""
        category = getattr(ctx, "category", None)
        if not category:
            return
        paths = _CATEGORY_TARGET_PATHS.get(category, [])
        if not paths or not ctx.keywords:
            return
        terms = ctx.keywords[:6]
        pattern = "|".join(re.escape(t) for t in terms if t)
        if not pattern:
            return
        parts = []
        for path in paths[:3]:
            result = self._executor._grep(pattern, path)
            if "error" in result:
                continue
            for m in result.get("representative_matches", [])[:4]:
                file_path = m.get("file", "")
                line = m.get("line", "")
                content = m.get("context", m.get("content", ""))
                parts.append(f"### {file_path}:{line}\n```\n{content}\n```")
            for f in result.get("files", [])[:3]:
                file_path = f.get("file")
                if file_path and file_path not in ctx._files_read and file_path not in ctx._grep_file_hits:
                    ctx._grep_file_hits.append(file_path)
        if parts:
            ctx.add_snippet(
                f"## Targeted grep ({category})",
                "\n\n".join(parts[:10]),
            )

    def _rerank_by_source_type(self, results: List[Dict]) -> List[Dict]:
        """Re-rank vector search results by source-type weight.

        Mirrors VectorRetriever.search() which multiplies vector_score by
        _SOURCE_TYPE_WEIGHTS to produce final_score.
        """
        for item in results:
            stype = item.get("source_type", "source")
            weight = _SOURCE_TYPE_WEIGHTS.get(stype, 1.0)
            vscore = item.get("vector_score", 0)
            item["final_score"] = vscore * weight
        results.sort(key=lambda x: x.get("final_score", 0), reverse=True)
        return results

    def _promote_full_files(self, ctx: _SearchContext) -> None:
        """Promote .md files with many chunk hits to whole-file reads.

        Mirrors the main agent's _buildRetrievalContext logic: if an .md file
        appears in ≥3 chunk results, read the entire file and replace chunk-
        level snippets with the full content.
        """
        for fpath, count in ctx._chunk_file_counts.items():
            if count < _FULL_FILE_CHUNK_THRESHOLD:
                continue
            if not fpath.endswith(".md"):
                continue
            if fpath in ctx._full_file_paths or fpath in ctx._files_read:
                continue

            result = self._executor._readfile(fpath, ctx.description)
            content = result.get("content")
            if content:
                ctx.add_snippet(
                    f"## Full file: {fpath} (promoted — {count} chunk hits)",
                    content,
                )
                ctx._full_file_paths.add(fpath)
                ctx.mark_file_read(fpath)

    def _phase1_symbol_search(self, ctx: _SearchContext) -> None:
        """Use AST symbol search to find concrete API definitions.

        Extracts potential API names from the description and keywords,
        then uses SearchSymbol to find their definitions via tree-sitter.
        """
        # Extract candidate symbol names from the description
        # PascalCase names (e.g. SetLayout, GetNodeByID)
        pascal = re.findall(r'\b([A-Z][a-z]+(?:[A-Z][a-z0-9]+)+)\b', ctx.description)
        # snake_case names from keywords
        snake = [k for k in ctx.keywords if "_" in k and k.islower()]
        candidates = list(dict.fromkeys(pascal + snake))[:6]

        if not candidates:
            return

        all_symbols = []
        for name in candidates:
            if name in ctx._symbol_names:
                continue
            ctx._symbol_names.add(name)
            result = self._executor._search_symbol(
                pattern=name,
                path=self._executor.skill_path,
                symbol_type="all",
            )
            symbols = result.get("symbols", [])
            if symbols:
                all_symbols.extend(symbols[:5])

        if not all_symbols:
            return

        parts = []
        for sym in all_symbols[:15]:
            name = sym.get("name", "")
            fpath = sym.get("file", "")
            line = sym.get("line", "")
            stype = sym.get("type", "")
            sig = sym.get("signature", "")[:120]
            src_type = sym.get("source_type", "source")
            if fpath:
                ctx.mark_file_read(fpath)
            parts.append(
                f"### {fpath}:{line} [{stype}:{src_type}] {name}\n{sig}"
            )

        if parts:
            ctx.add_snippet(
                "## Symbol search results (AST, tree-sitter)",
                "\n".join(parts),
            )

    # ==================================================================
    # Phase 2: Iterative deepening
    # ==================================================================

    def _iterative_search(self, sub_op) -> str:
        """Two-phase search: pre-retrieval + iterative deepening.

        Phase 1 runs once (query decomposition, multi-query vector search,
        source-type re-ranking, full-file promotion, symbol search).

        Phase 2 runs up to _MAX_ROUNDS of adaptive deepening with query
        expansion and convergence detection.
        """
        import time as _time

        category = self._infer_category(sub_op)
        seed_keywords = list(sub_op.slicer_api_keywords or [])
        seed_keywords.extend(_CATEGORY_SEARCH_HINTS.get(category, []))
        ctx = _SearchContext(sub_op.description, seed_keywords)
        ctx.category = category

        if not self._executor:
            logger.warning("[5T] No executor available — skipping search for '%s'",
                           sub_op.description[:60])
            return ctx.get_accumulated()

        desc_short = sub_op.description.split("\n")[0][:50]

        # ── Phase 1: Pre-retrieval ──
        t0 = _time.monotonic()
        logger.info("[5T] '%s' Phase 1 starting...", desc_short)
        self._phase1_preretrieval(ctx)
        t1 = _time.monotonic()
        logger.info(
            "[5T] '%s' Phase 1 done: %.1fs, snippets=%d chars, files=%d",
            desc_short, t1 - t0, ctx.current_length(), len(ctx._files_read),
        )

        # Early exit: if Phase 1 found almost nothing, skip Phase 2 entirely.
        # No point running 10 rounds of deepening on empty results.
        if ctx.current_length() < 100 and not ctx._files_read:
            logger.info(
                "[5T] '%s' Phase 1 found nothing useful — skipping Phase 2 deepening",
                desc_short,
            )
            return ctx.get_accumulated()

        # ── Phase 2: Iterative deepening ──
        final_round = 0
        for round_num in range(1, _MAX_ROUNDS + 1):
            final_round = round_num
            prev_hit_count = len(ctx._files_read)
            tr = _time.monotonic()

            logger.info("[5T] '%s' Phase 2 round %d starting...", desc_short, round_num)

            # Adaptive strategy selection based on what we already know
            self._do_adaptive_round(ctx, round_num)

            round_elapsed = _time.monotonic() - tr
            logger.info(
                "[5T] '%s' Phase 2 round %d done: %.1fs, snippets=%d chars, files=%d",
                desc_short, round_num, round_elapsed,
                ctx.current_length(), len(ctx._files_read),
            )

            # Convergence: growth stalled
            if round_num >= 2 and ctx.is_converged():
                logger.info(
                    "[5T] '%s' converged after round %d "
                    "(growth < %d chars)", desc_short, round_num,
                    _CONVERGENCE_THRESHOLD_CHARS,
                )
                break

            # Exhaustion: no new files discovered and no queued reads
            new_hits = len(ctx._files_read) - prev_hit_count
            if round_num >= 2 and new_hits == 0 and not ctx._grep_file_hits:
                logger.info(
                    "[5T] '%s' exhausted after round %d "
                    "(no new files found)", round_num,
                )
                break

            # Query expansion: extract API terms from accumulated snippets
            accumulated = ctx.get_accumulated()
            new_terms = _extract_api_terms_from_snippets(accumulated)
            if new_terms:
                ctx.add_keywords(new_terms)
                logger.debug(
                    "SlicerOpGenerator: query expansion added: %s", new_terms,
                )

            # Symbol expansion: discover new symbol names
            new_syms = _extract_symbol_names(accumulated)
            for sym in new_syms:
                if sym not in ctx._symbol_names:
                    ctx._symbol_names.add(sym)

        ctx.round_logs.append(f"Phase 2: {min(final_round, _MAX_ROUNDS)} rounds")
        return ctx.get_accumulated()

    def _do_adaptive_round(self, ctx: _SearchContext, round_num: int):
        """Run one round of adaptive deepening.

        Chooses strategies based on what has been discovered so far:
        - If we have grep file hits queued → read them (highest priority)
        - If we have new keywords/symbols → grep + symbol search
        - If neither → try vector search with expanded query
        """
        has_queued_reads = bool(ctx._grep_file_hits)
        has_keywords = bool(ctx.keywords)

        # Always try to drain queued grep hits first
        if has_queued_reads:
            self._do_readfile(ctx, round_num)

        # Grep for latest keywords (discovers new files to read)
        if has_keywords:
            self._do_grep(ctx, round_num)

        # Symbol search: try newly discovered symbol names we haven't
        # searched yet (only in odd rounds to balance cost)
        if round_num % 2 == 1:
            self._do_symbol_search(ctx, round_num)

        # Vector search with expanded query (every 3rd round for diversity)
        if round_num % 3 == 0:
            self._do_vector_search(ctx, round_num)

    # ------------------------------------------------------------------
    # Individual search strategies (Phase 2)
    # ------------------------------------------------------------------

    def _do_vector_search(self, ctx: _SearchContext, round_num: int):
        """Dense vector search with expanded query."""
        # Build query from description + accumulated keywords
        query = ctx.description
        if ctx.keywords:
            query += " " + " ".join(ctx.keywords[-6:])

        result = self._executor._vector_search(query, top_k=8)
        formatted = result.get("formatted_context")
        if formatted:
            ctx.add_snippet(f"## Vector search (round {round_num})", formatted)

        for item in result.get("results", []):
            fpath = item.get("file_path", "")
            if fpath:
                ctx.mark_file_read(fpath)

    def _do_grep(self, ctx: _SearchContext, round_num: int):
        """Grep for specific API terms."""
        if not ctx.keywords:
            return

        terms = ctx.keywords[-6:]
        pattern = "|".join(terms)

        result = self._executor._grep(pattern, self._executor.skill_path)
        if "error" in result:
            return

        rep_matches = result.get("representative_matches", [])
        if rep_matches:
            parts = []
            for m in rep_matches[:6]:
                file_path = m.get("file", "")
                line = m.get("line", "")
                content = m.get("context", m.get("content", ""))
                parts.append(f"### {file_path}:{line}\n```\n{content}\n```")
            if parts:
                ctx.add_snippet(
                    f"## Grep results (round {round_num}): {', '.join(terms[:3])}",
                    "\n\n".join(parts),
                )

        # Queue new file hits for reading
        new_hits = [
            f["file"] for f in result.get("files", [])[:_MAX_GREP_FILES_TO_QUEUE]
            if f.get("file") not in ctx._files_read
        ]
        ctx._grep_file_hits.extend(
            h for h in new_hits if h not in ctx._grep_file_hits
        )

    def _do_readfile(self, ctx: _SearchContext, round_num: int):
        """Read full function/class bodies from queued grep hits."""
        files_to_read = ctx._grep_file_hits
        ctx._grep_file_hits = []

        if not files_to_read:
            return

        parts = []
        for rel_path in files_to_read[:_MAX_READFILE_PER_ROUND]:
            if ctx.already_read(rel_path):
                continue
            ctx.mark_file_read(rel_path)

            # Use the most specific keyword available for smart slicing
            query = ctx.description
            if ctx.keywords:
                query = ctx.keywords[0]

            result = self._executor._readfile(rel_path, query)
            content = result.get("content")
            if content:
                strategy = result.get("strategy", "unknown")
                parts.append(
                    f"### {rel_path} (strategy: {strategy})\n```python\n{content}\n```"
                )

        if parts:
            ctx.add_snippet(
                f"## Full code from KB files (round {round_num})",
                "\n\n".join(parts),
            )

    def _do_symbol_search(self, ctx: _SearchContext, round_num: int):
        """AST symbol search for newly discovered symbol names."""
        # Find symbols we haven't searched yet
        new_symbols = ctx._symbol_names - ctx._symbol_names  # all already tracked
        # Actually, we track what we've searched in _searched_symbols
        if not hasattr(ctx, '_searched_symbols'):
            ctx._searched_symbols: Set[str] = set()

        unsearched = ctx._symbol_names - ctx._searched_symbols
        if not unsearched:
            return

        # Search up to 4 new symbols per round
        batch = list(unsearched)[:4]
        for name in batch:
            ctx._searched_symbols.add(name)
            result = self._executor._search_symbol(
                pattern=name,
                path=self._executor.skill_path,
                symbol_type="all",
            )
            symbols = result.get("symbols", [])
            if not symbols:
                continue

            parts = []
            for sym in symbols[:5]:
                fname = sym.get("file", "")
                line = sym.get("line", "")
                stype = sym.get("type", "")
                sig = sym.get("signature", "")[:120]
                src_type = sym.get("source_type", "source")
                if fname:
                    ctx.mark_file_read(fname)
                parts.append(f"### {fname}:{line} [{stype}:{src_type}] {name}\n{sig}")

            if parts:
                ctx.add_snippet(
                    f"## Symbol search (round {round_num}): {name}",
                    "\n".join(parts),
                )

    # ------------------------------------------------------------------
    # Code generation (LLM)
    # ------------------------------------------------------------------

    @staticmethod
    def _is_low_evidence(snippets: str) -> bool:
        """Return True when retrieval did not provide enough grounding."""
        if not snippets or snippets.strip() == _NO_EVIDENCE_TEXT:
            return True
        useful = snippets.replace(_NO_EVIDENCE_TEXT, "").strip()
        return len(useful) < _MIN_EVIDENCE_CHARS

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

    def _generate_code(self, sub_op, kb_snippets: str) -> str:
        """Use LLM to generate a Python code template from accumulated KB snippets.

        Includes a single retry if the first attempt produces code with
        syntax errors, and null-byte / blocked-import stripping.
        """
        import ast as _ast
        desc_short = sub_op.description.split("\n")[0][:50]
        logger.info(
            "[5T] Codegen starting for '%s' (%d chars snippets)",
            desc_short, len(kb_snippets),
        )

        user_content = (
            _CODEGEN_USER_TEMPLATE
            .replace("{retrieval_policy}", _RETRIEVAL_POLICY)
            .replace("{description}", sub_op.description)
            .replace("{snippets}", kb_snippets)
        )
        messages = [
            {"role": "system", "content": _CODEGEN_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]

        for attempt in range(2):  # up to 2 attempts
            try:
                response = self.llm_client.chatIsolated(messages)
            except Exception as exc:
                logger.exception("[5T] Codegen LLM call FAILED for '%s'", desc_short)
                raise

            code = response.get("message", "")

            if not code:
                logger.warning("[5T] Codegen returned empty for '%s'", desc_short)
                return f"# Empty response for: {sub_op.description}\npass"

            code = self._strip_fences(code)

            # Basic sanitization
            code = code.replace("\x00", "")
            code = code.replace("\r\n", "\n").replace("\r", "\n")

            # Validate syntax
            try:
                _ast.parse(code)
                logger.info(
                    "[5T] Codegen done for '%s': %d chars (attempt %d)",
                    desc_short, len(code), attempt + 1,
                )
                return code
            except (SyntaxError, IndentationError) as e:
                if attempt == 0:
                    logger.warning(
                        "[5T] Codegen for '%s' had syntax error on attempt 1: %s. Retrying...",
                        desc_short, e,
                    )
                    # Add error context to second attempt
                    messages = [
                        {"role": "system", "content": _CODEGEN_SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                        {"role": "assistant", "content": code},
                        {"role": "user", "content": (
                            "The code above has a syntax error. Fix it and output ONLY "
                            "the corrected Python code, no explanation."
                        )},
                    ]
                    continue
                else:
                    logger.warning(
                        "[5T] Codegen for '%s' still has syntax error after retry: %s. "
                        "Returning as-is.",
                        desc_short, e,
                    )
                    return code

        return code  # unreachable but satisfies linter

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
