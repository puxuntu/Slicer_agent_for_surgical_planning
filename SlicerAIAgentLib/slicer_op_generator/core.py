from .common import *


class SlicerOpGeneratorCoreMixin:
    def __init__(
        self,
        llm_client,
        skill_executor=None,
        skill_path: Optional[str] = None,
        on_progress=None,
        debug_path: Optional[str] = None,
        extension_name: str = "",
        module_name: str = "",
        extension_source_path: str = "",
    ):
        self.llm_client = llm_client
        self._executor = skill_executor
        self._skill_path = skill_path
        self._executor_initialized = skill_executor is not None
        self._on_progress = on_progress
        self._debug_path = debug_path
        # Extension identity, so grounding can steer searches to the extension's
        # own source for named/custom artifacts instead of fabricating them.
        self._extension_name = extension_name or ""
        self._module_name = module_name or ""
        # Installed source dir of the extension being analyzed; registered as
        # an `ext:<name>/` search root so grounding can find extension-defined
        # artifacts (custom layout IDs, registered constants) instead of
        # emitting MISSING_EVIDENCE or fabricating values.
        self._extension_source_path = extension_source_path or ""
        self.last_run_records = []

    # ------------------------------------------------------------------
    # Lazy SkillToolExecutor initialization
    # ------------------------------------------------------------------

    def _register_extension_root(self):
        """Make the analyzed extension's own source searchable as ext:<name>/."""
        if (
            self._executor is not None
            and self._extension_name
            and self._extension_source_path
            and os.path.isdir(self._extension_source_path)
        ):
            try:
                self._executor.extra_roots[self._extension_name] = self._extension_source_path
            except Exception:
                logger.debug("Extension root registration failed", exc_info=True)

    def _ensure_executor(self):
        if self._executor_initialized:
            self._register_extension_root()
            return
        self._executor_initialized = True
        try:
            from ..UIControlIndex import preanalysis_status
            status = preanalysis_status()
            if not status.get("ok"):
                logger.warning(
                    "Slicer UI pre-analysis missing/empty (%s) — UI-labeled "
                    "grounding is degraded; run scripts/build_rag.py outside "
                    "Slicer to rebuild.", status.get("reason", "unknown"),
                )
        except Exception:
            logger.debug("UI pre-analysis status check failed", exc_info=True)
        if not self._skill_path or not os.path.isdir(self._skill_path):
            logger.warning("No skill_path for SlicerOpGenerator KB search")
            return
        try:
            from ..SkillTools import SkillToolExecutor, get_shared_executor
            shared = get_shared_executor(self._skill_path)
            if shared is not None:
                # Reuse the main agent's executor (avoids a duplicate ONNX
                # session + vector index load).
                self._executor = shared
                logger.info("SlicerOpGenerator: reusing shared SkillToolExecutor.")
            else:
                self._executor = SkillToolExecutor(self._skill_path)
                logger.info("SlicerOpGenerator: SkillToolExecutor loaded.")
            self._register_extension_root()
        except Exception:
            logger.exception("SlicerOpGenerator: failed to load SkillToolExecutor")

    @staticmethod
    def _deterministic_ui_evidence(sub_op) -> Tuple[List[str], List[str]]:
        """Top-matching core-UI control evidence for this sub-op.

        Returns (prompt_lines, matched_object_names); ([], []) when the
        pre-analysis index is unavailable or nothing matches. Pure function —
        safe under the parallel per-op generation threads.
        """
        try:
            from ..UIControlIndex import format_evidence_lines, get_index
            index = get_index()
            if index is None:
                return [], []
            query = " ".join([
                getattr(sub_op, "description", "") or "",
                " ".join(getattr(sub_op, "slicer_api_keywords", []) or []),
            ])
            matches = index.match(query, top_k=5)
            lines = format_evidence_lines(matches, max_total_chars=1200)
            matched = [m["record"].get("object_name", "") for m in matches]
            return lines, matched
        except Exception:
            logger.debug("Deterministic UI evidence lookup failed", exc_info=True)
            return [], []

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
        if (
            "markups module" in text
            and any(t in text for t in ("display", "view", "advanced", "configure", "set", "show"))
            and not any(t in text for t in ("switch to", "open the", "select module", "activate module"))
        ):
            return "markups_display"
        if any(t in text for t in ("switch to", "open module", "open the markups", "select module", "activate module")):
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

    def _build_user_message(
        self, sub_op, category: str, ui_evidence_lines: Optional[List[str]] = None,
    ) -> str:
        """Build the user prompt for a single slicer_op sub-operation."""
        parts = [f"Generate a Python code template for this 3D Slicer operation:\n"]
        parts.append(sub_op.description)
        parts.append(
            "\nEvery executable API call must use a receiver type derivable from retrieved "
            "source or wrapper evidence. Report uncertainty instead of inventing a method. "
            "Do not introduce unrelated UI, icon, toolbar, module-switching, or layout behavior."
            "\nNever fabricate values that an extension DEFINES IN ITS SOURCE — a custom-layout "
            "ID or its XML, an `slicer.<Const>` the extension sets, a registered singleton tag, "
            "or a magic constant must come from the extension's source, not be guessed. If, after "
            "searching the extension source, you cannot find such a value, emit "
            "`raise RuntimeError(\"MISSING_EVIDENCE: <what>\")` instead of a placeholder. This does "
            "NOT apply to ordinary scene nodes referenced by name/role (a curve, segmentation, or "
            "volume the user created) — resolve those at runtime from the scene; never emit "
            "MISSING_EVIDENCE for them."
        )
        ext_name = getattr(self, "_extension_name", "") or ""
        if ext_name:
            module_hint = (
                f" (module `{self._module_name}`)" if getattr(self, "_module_name", "") else ""
            )
            source_root_hint = (
                f"ext:{ext_name}/" if getattr(self, "_extension_source_path", "")
                else f"slicer-extensions/{ext_name}/"
            )
            parts.append(
                f"\nThis operation belongs to the extension `{ext_name}`{module_hint}. If it "
                f"reproduces an artifact the extension REGISTERS IN ITS SOURCE (a custom layout + "
                f"its ID/XML, or an `slicer.<Const>`), search `{source_root_hint}` (the "
                f"extension's own source, registered as a search root for Grep/ReadFile) for "
                f"the real definition or a helper that performs it (for example a `setX`/`addX` "
                f"function) and use that rather than re-registering or guessing one. Ordinary scene "
                f"nodes referenced by name are resolved at runtime, not from source."
            )
        repair_context = getattr(sub_op, "repair_context", None)
        if isinstance(repair_context, dict) and repair_context:
            parts.append("\n\nThis is a targeted repair of a previously generated template.")
            if repair_context.get("validation_issue"):
                parts.append(
                    "\nValidation failure to fix:\n"
                    + str(repair_context["validation_issue"])
                )
            if repair_context.get("semantic_recipe"):
                parts.append(
                    "\nBehavioral repair contract:\n"
                    + json.dumps(repair_context["semantic_recipe"], indent=2)
                )
            if repair_context.get("existing_api_evidence"):
                parts.append(
                    "\nExisting API evidence to verify or replace:\n"
                    + json.dumps(repair_context["existing_api_evidence"], indent=2)
                )
            if repair_context.get("failed_code"):
                parts.append(
                    "\nPreviously failing code:\n```python\n"
                    + str(repair_context["failed_code"])
                    + "\n```"
                )
            parts.append(
                "\nSearch again for source-backed evidence. Do not preserve an API "
                "pattern merely because it appears in the failing code."
            )
        state_intent = infer_final_state_intent(
            " ".join([
                getattr(sub_op, "description", "") or "",
                " ".join(getattr(sub_op, "slicer_api_keywords", []) or []),
            ])
        )

        hints = _CATEGORY_SEARCH_HINTS.get(category, [])
        if hints:
            parts.append(f"\nSuggested API terms to search for: {', '.join(hints[:8])}")

        keywords = getattr(sub_op, "slicer_api_keywords", []) or []
        if keywords:
            parts.append(f"\nAPI keyword hints: {', '.join(keywords[:8])}")

        # Deterministic core-UI evidence: matched offline against the UI
        # pre-analysis index, so the most relevant control records appear in
        # every run regardless of tool-call ordering.
        if ui_evidence_lines is None:
            ui_evidence_lines, _ = self._deterministic_ui_evidence(sub_op)
        if ui_evidence_lines:
            parts.append(
                "\n\nDETERMINISTIC CORE-UI EVIDENCE (from Slicer core UI "
                "pre-analysis; matched offline, no search needed):\n"
                + "\n".join(ui_evidence_lines)
                + "\nThe `api:` names are method names observed near the "
                "control's implementation — treat them as existing core "
                "methods, but confirm the receiver class by reading the cited "
                "doc/implementation file before emitting a state-changing call."
            )

        display_text = " ".join([
            getattr(sub_op, "description", "") or "",
            " ".join(keywords),
            category or "",
        ]).lower()
        targets_slice_view = bool(
            re.search(r"\b(red|green|yellow)\b", display_text)
            or "slice view" in display_text
            or "vtkmrmlslicenode" in display_text
        )
        if (
            category in ("markups_display", "node_display")
            and targets_slice_view
            and state_intent.get("mode") == "set"
            and state_intent.get("state") is True
        ):
            # Only steps that affirmatively SHOW something in a slice view get
            # the 2D-visibility requirement (mirrored by the validator's gate
            # in validation_semantics._validate_display_view_scope_semantics).
            parts.append(
                "\nDisplay-scope requirement: adding `AddViewNodeID(...)` only restricts "
                "which views may show the displayable. Because this operation targets a "
                "slice view, also enable the display node's 2D/slice visibility. For "
                "Markups, include `SetVisibility(True)` and either "
                "`SetVisibility2D(True)`/`Visibility2DOn()` if available or "
                "`SetSliceProjection(True)`/`SliceProjectionOn()` when the object should "
                "be visible in the slice view even when it is not exactly on the current "
                "slice. For Models, include `SetVisibility2D(True)`. For Segmentations, "
                "enable 2D fill or outline visibility. Resolve view nodes from scene or "
                "layout evidence when possible instead of hard-coding IDs. "
                "Do NOT enable interaction handles, interactive modes, or persistent "
                "handle visibility unless the step text explicitly asks for interaction."
            )

        if state_intent.get("mode") == "set":
            parts.append(
                "\nInterpreted state intent: set the requested UI/API state to "
                f"{state_intent.get('state')}. Do not invert the current state."
            )
        elif state_intent.get("mode") == "invert":
            parts.append(
                "\nInterpreted state intent: explicitly invert the current state."
            )

        parts.append(
            "\n\nSearch the knowledge base for relevant examples first, "
            "using slicer-ui-analysis first for UI-labeled controls/actions, "
            "then output ONLY the ```python code block. Generate a final-state "
            "operation, not a toggle, unless the description explicitly requests toggling. "
            "Do not switch the active Slicer module for UI-location context; only use "
            "slicer.util.selectModule when the operation explicitly asks to switch/open/select a module."
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

        ui_evidence_lines, ui_evidence_matched = self._deterministic_ui_evidence(sub_op)
        user_message = self._build_user_message(
            sub_op, category, ui_evidence_lines=ui_evidence_lines,
        )
        messages = [
            {"role": "system", "content": _SLICER_OP_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]

        op_record["prompt_build_s"] = round(_time.monotonic() - t_prompt_start, 3)
        op_record["prompt_user_preview"] = user_message[:1500]
        op_record["prompt_includes_ui_analysis"] = "slicer-ui-analysis" in user_message
        op_record["deterministic_ui_evidence"] = {
            "matched": ui_evidence_matched,
            "injected": bool(ui_evidence_lines),
        }
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
        op_record["evidence_audit"] = _summarize_tool_evidence(tool_calls_history)

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
        op_record["generated_code_preview"] = code[:2000]

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
