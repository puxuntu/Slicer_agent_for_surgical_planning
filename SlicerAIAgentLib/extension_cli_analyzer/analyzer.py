from .common import *
from .llm_calls import AnalyzerLLMCallsMixin
from .repair_memory import AnalyzerRepairMemoryMixin
from .scan import AnalyzerScanMixin
from .logic_analysis import AnalyzerLogicAnalysisMixin
from .stage4_decomposition import AnalyzerStage4DecompositionMixin
from .cross_stage import AnalyzerCrossStageMixin
from .node_lifecycle import AnalyzerNodeLifecycleMixin
from .schemas import AnalyzerSchemasMixin
from .workflow_templates import AnalyzerWorkflowTemplatesMixin
from .template_helpers import AnalyzerTemplateHelpersMixin
from .api_probe import AnalyzerApiProbeMixin
from .template_generation import AnalyzerTemplateGenerationMixin
from .prompt_validation import AnalyzerPromptValidationMixin
from .validation_contracts import AnalyzerValidationContractsMixin
from .validation_semantics import AnalyzerValidationSemanticsMixin
from .live_revision import AnalyzerLiveRevisionMixin
from .cookbook_mapping import AnalyzerCookbookMappingMixin
from .parameter_metadata import AnalyzerParameterMetadataMixin
from .workflow_contracts import AnalyzerWorkflowContractsMixin
from .slicer_op_manifest import AnalyzerSlicerOpManifestMixin
from .phases import AnalyzerPhaseMixin, MANIFEST_VERSION, PIPELINE_VERSION
from .v2_contracts import AnalyzerV2ContractsMixin
from .repair_loop import AnalyzerRepairLoopMixin
from .contract_audit import AnalyzerContractAuditMixin
from .api_proof import AnalyzerApiProofMixin
from ..cli_artifacts import (
    GENERATION_ROUND,
    debug_round_dir,
    next_repair_round_label,
    snapshot_package_version,
)


class ExtensionCLIAnalyzer(
    AnalyzerLLMCallsMixin,
    AnalyzerRepairMemoryMixin,
    AnalyzerScanMixin,
    AnalyzerLogicAnalysisMixin,
    AnalyzerStage4DecompositionMixin,
    AnalyzerCrossStageMixin,
    AnalyzerNodeLifecycleMixin,
    AnalyzerSchemasMixin,
    AnalyzerWorkflowTemplatesMixin,
    AnalyzerTemplateHelpersMixin,
    AnalyzerApiProbeMixin,
    AnalyzerTemplateGenerationMixin,
    AnalyzerPromptValidationMixin,
    AnalyzerValidationContractsMixin,
    AnalyzerValidationSemanticsMixin,
    AnalyzerLiveRevisionMixin,
    AnalyzerCookbookMappingMixin,
    AnalyzerParameterMetadataMixin,
    AnalyzerWorkflowContractsMixin,
    AnalyzerSlicerOpManifestMixin,
    AnalyzerPhaseMixin,
    AnalyzerV2ContractsMixin,
    AnalyzerRepairLoopMixin,
    AnalyzerContractAuditMixin,
    AnalyzerApiProofMixin,
):
    """
    Analyzes a Slicer extension's source code and generates operation CLIs.

    Strict v2 cookbook-driven pipeline:
    discover -> analyze -> contract -> audit_contract -> ground -> generate -> verify_repair -> package.
    """

    def __init__(
        self,
        llm_client,
        output_base_dir: Optional[str] = None,
        code_validator=None,
        on_progress: Optional[Callable[[int, str, str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        method_keyword_map: Optional[Dict[str, str]] = None,
        live_probe_executor: Optional[Callable[[str], Any]] = None,
    ):
        """
        Args:
            llm_client: LLMClient instance for making LLM calls.
            output_base_dir: Base directory for saving CLI packages.
                             Defaults to Resources/extension_CLI/.
            code_validator: CodeValidator instance. Created if not provided.
            on_progress: Callback(stage_num, stage_name, detail) for progress updates.
            on_error: Callback(error_message) for error reporting.
            method_keyword_map: Deprecated compatibility argument. Semantic
                cookbook interpretation is performed by the Stage 4 LLM and
                validated against source-derived candidates.
            live_probe_executor: Optional callable that executes a probe snippet
                on Slicer's main thread and returns the probe result.
        """
        self.llm_client = llm_client
        self.output_base_dir = output_base_dir or self._default_base_dir()
        self.code_validator = code_validator
        # Every progress/error event is timestamped, recorded in memory,
        # mirrored to debug/ui_output.log, and forwarded to the caller —
        # the UI text and the on-disk record can never diverge.
        self._user_on_progress = on_progress or (lambda n, s, d: None)
        self._user_on_error = on_error or (lambda e: None)
        self.on_progress = self._emit_progress
        self.on_error = self._emit_error
        self._progress_events: List[Dict] = []
        self._pipeline_start: Optional[float] = None
        self._phase_start_times: Dict[str, float] = {}
        self._phase_durations: Dict[str, float] = {}
        # Revisions write to their own files so they never clobber the
        # original generation run's log (see live_revision.revise).
        self._progress_log_name = "ui_output.log"
        self._progress_json_name = "progress_events.json"
        self._ui_round_header: List[str] = []
        self._method_keyword_map = {}
        self._live_probe_executor = live_probe_executor
        self._analyzer_prompt = self._load_analyzer_prompt()
        self._cancelled = False
        # Pipeline-scoped state (reset in analyze_and_generate)
        self._debug_dir: Optional[str] = None
        self._llm_call_counter: int = 0
        self._current_stage_label: str = ""
        self._cookbook_def = None                # Parsed CookbookDef when cookbook found
        self._widget_connections: List[Dict] = []
        self._ui_parameter_bindings: Dict[str, Dict] = {}
        self._slicer_op_templates: Dict = {}     # Pre-generated slicer_op templates
        self._slicer_op_evidence: Dict = {}      # API evidence for pre-generated slicer_op templates
        self._placement_starter_methods: Dict = {}
        self._workflow_metadata: Dict = {}
        self._last_logic_analysis: Optional[Dict] = None
        self._last_api_probe_result: Optional[Dict] = None
        self._upstream_feedback: List[Dict] = []
        self._proven_api_chains: Optional[List[str]] = None
        self._ui_evidence_methods: Optional[List[str]] = None
        self._source_path: str = ""

    @staticmethod
    def _default_base_dir() -> str:
        # __file__ may not point to the actual source in some Slicer setups
        # (e.g., when loaded from a staged build directory). Try multiple paths.
        candidates = []
        try:
            candidates.append(_PROJECT_ROOT)
        except Exception:
            pass
        # Fallback: look relative to the SlicerAIAgent module
        try:
            import SlicerAIAgent as _root_mod
            candidates.append(os.path.dirname(os.path.abspath(_root_mod.__file__)))
        except Exception:
            pass
        for module_dir in candidates:
            cli_dir = os.path.join(module_dir, "Resources", "extension_CLI")
            if os.path.isdir(cli_dir):
                return cli_dir
        # Last resort: return the first candidate anyway (will fail later
        # with a clear error if the path doesn't exist)
        if candidates:
            return os.path.join(candidates[0], "Resources", "extension_CLI")
        return ""

    def _load_analyzer_prompt(self) -> str:
        try:
            with open(_ANALYZER_PROMPT_PATH, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            logger.warning("Could not load analyzer prompt, using minimal fallback")
            return "You are a code analysis assistant for Slicer extensions."

    def cancel(self):
        """Cancel the analysis pipeline."""
        self._cancelled = True

    @staticmethod
    def _content_fingerprint(*parts) -> str:
        """Stable content hash over JSON-representable inputs.

        Used by the upstream re-entry loop's monotone-progress rule: a
        re-entry that leaves the contract facts' fingerprint unchanged made
        no progress and terminates the loop.
        """
        import hashlib
        try:
            blob = json.dumps(parts, sort_keys=True, default=str).encode("utf-8")
        except Exception:
            blob = repr(parts).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

    # ================================================================
    # Scoped upstream re-entry helpers
    # ================================================================

    @staticmethod
    def _step_numbers_in_text(text: str) -> set:
        """Step numbers referenced as cb_step_<N> in any identifier/message."""
        return {int(m) for m in _re.findall(r"cb_step_(\d+)", str(text or ""))}

    def _step_numbers_in_errors(self, errors) -> set:
        steps = set()
        for error in errors or []:
            steps |= self._step_numbers_in_text(error)
        return steps

    def _affected_steps_from_requests(self, requests, cross_stage_map) -> set:
        """Steps a re-entry must re-derive: the steps named by the upstream
        requests plus their one-hop data-flow neighbors (a step whose
        contract changes can invalidate what its readers/writers expect)."""
        affected = set()
        for request in requests or []:
            for step_id in request.get("step_ids") or []:
                affected |= self._step_numbers_in_text(step_id)
                if str(step_id).isdigit():
                    affected.add(int(step_id))
            affected |= self._step_numbers_in_text(request.get("template_key", ""))
        if not affected:
            return affected
        for conn in (cross_stage_map or {}).get("connections") or []:
            from_step = conn.get("from_step")
            to_step = conn.get("to_step")
            if from_step in affected or to_step in affected:
                if isinstance(from_step, int):
                    affected.add(from_step)
                if isinstance(to_step, int):
                    affected.add(to_step)
        return affected

    def _attempt_contract_reentry_from_audit(
        self,
        contract_audit: Dict,
        *,
        reentry_count: int,
        prev_contract_fingerprint,
        contract_fingerprint,
        reentry_trace: List[Dict],
        cross_stage_map: Dict,
        stage_map: Dict,
        max_contract_reentries: int,
        max_total_reentries: int,
    ):
        """Convert ContractFidelity audit findings into a scoped contract re-entry.

        Mirrors the verify_repair upstream re-entry: bounded by the same budget and
        a monotone-progress rule. Returns (action, reentry_count, prev_fingerprint)
        where action is 'reenter' (caller `continue`s the loop) or 'stop' (caller
        aborts). The audit finding's own `recommended_route: rebuild_contract` is
        what asks for this — so a recoverable LLM mislabel self-heals instead of
        hard-aborting the whole generation.
        """
        findings = [
            f for f in (contract_audit.get("findings") or [])
            if isinstance(f, dict) and f.get("verdict") == "fail"
        ]
        upstream_requests = [
            {
                "phase": "contract",
                "issue_type": "ContractFidelity",
                "issue_class": f.get("issue_class", "contract"),
                "step_ids": [f.get("step_id")] if f.get("step_id") else [],
                "template_key": "",
                "message": f.get("message", ""),
                "contract_step": {},
                "repair_route": f.get("recommended_route", "rebuild_contract"),
            }
            for f in findings
        ]
        # Include any non-finding audit errors (e.g. workflow-state graph) too.
        known = {r["message"] for r in upstream_requests}
        for err in contract_audit.get("errors") or []:
            if err not in known:
                upstream_requests.append({
                    "phase": "contract",
                    "issue_type": "ContractFidelity",
                    "issue_class": "contract",
                    "step_ids": [],
                    "template_key": "",
                    "message": err,
                    "contract_step": {},
                    "repair_route": "rebuild_contract",
                })
        if not upstream_requests:
            return ("stop", reentry_count, prev_contract_fingerprint)

        # Monotone progress: a re-entry that left the contract facts unchanged
        # would loop forever — stop instead.
        if reentry_count > 0 and contract_fingerprint == prev_contract_fingerprint:
            reentry_trace.append({
                "event": "no_progress",
                "trigger": "audit_contract",
                "detail": (
                    "Audit re-entry produced identical contract facts; stopping "
                    "(monotone-progress rule)."
                ),
            })
            return ("stop", reentry_count, prev_contract_fingerprint)
        if reentry_count >= min(max_contract_reentries, max_total_reentries):
            reentry_trace.append({
                "event": "budget_exhausted",
                "trigger": "audit_contract",
                "detail": f"Re-entry budget exhausted after {reentry_count} re-entries.",
            })
            return ("stop", reentry_count, prev_contract_fingerprint)

        reentry_count += 1
        self._upstream_feedback.extend(upstream_requests)
        affected_steps = self._affected_steps_from_requests(
            upstream_requests, cross_stage_map
        )
        self._reentry_affected_steps = affected_steps or None
        self._reentry_implicated_steps = (
            set(affected_steps)
            | self._step_numbers_in_errors(contract_audit.get("errors") or [])
        )
        self._prev_stage_map = stage_map
        new_prev_fp = self._scoped_contract_fingerprint(
            stage_map, cross_stage_map, self._reentry_affected_steps
        )
        reentry_trace.append({
            "event": "reentry",
            "attempt": reentry_count,
            "phase": "contract",
            "trigger": "audit_contract",
            "affected_steps": sorted(affected_steps),
            "requests": upstream_requests,
        })
        self.on_progress(
            "contract", "Build Workflow Contract",
            f"Audit re-entry {reentry_count}: re-deriving contract with "
            f"{len(upstream_requests)} ContractFidelity finding(s) as feedback, "
            f"scoped to step(s) {sorted(affected_steps) or 'ALL'}...",
        )
        return ("reenter", reentry_count, new_prev_fp)

    @staticmethod
    def _merge_stage_map_scoped(prior: Dict, new: Dict, affected_steps: set):
        """Replace only affected steps' derivations; preserve the rest.

        Returns (merged_stage_map, preserved_count). Stage dicts are aligned
        by stage_index (cookbook step number - 1); the cookbook fixes the
        step count, so indexes are stable across iterations. Steps missing
        from the prior map fall back to the new derivation.
        """
        prior_by_index = {
            stage.get("stage_index"): stage
            for stage in (prior or {}).get("stages", [])
            if isinstance(stage, dict)
        }
        merged = dict(new or {})
        merged_stages = []
        preserved = 0
        for stage in (new or {}).get("stages", []):
            index = stage.get("stage_index") if isinstance(stage, dict) else None
            step_number = index + 1 if isinstance(index, int) else None
            if (
                step_number is not None
                and step_number not in affected_steps
                and index in prior_by_index
            ):
                merged_stages.append(prior_by_index[index])
                preserved += 1
            else:
                merged_stages.append(stage)
        merged["stages"] = merged_stages
        return merged, preserved

    def _scoped_contract_fingerprint(self, stage_map, cross_stage_map, affected_steps) -> str:
        """Monotone-progress fingerprint; restricted to the affected steps on
        a scoped re-entry so noise elsewhere cannot fake progress."""
        if not affected_steps:
            return self._content_fingerprint(
                stage_map, cross_stage_map,
                sorted(getattr(self, "_placement_starter_methods", []) or []),
            )
        scoped = [
            stage for stage in (stage_map or {}).get("stages", [])
            if isinstance(stage, dict)
            and isinstance(stage.get("stage_index"), int)
            and stage["stage_index"] + 1 in affected_steps
        ]
        return self._content_fingerprint(scoped)

    # ================================================================
    # Progress recording (UI output mirrored into the debug folder)
    # ================================================================

    def _emit_progress(self, stage, name, detail) -> None:
        """Record a progress event and forward it to the UI callback."""
        import time as _time
        now = _time.time()
        elapsed = (now - self._pipeline_start) if self._pipeline_start else 0.0
        event = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "elapsed_s": round(elapsed, 1),
            "phase": str(stage),
            "title": str(name),
            "detail": str(detail),
        }
        self._progress_events.append(event)
        self._append_ui_output_line(event)
        try:
            self._user_on_progress(stage, name, detail)
        except Exception:
            logger.debug("UI progress callback failed", exc_info=True)

    def _emit_error(self, error_message) -> None:
        """Record an error event and forward it to the UI callback."""
        self._emit_progress("error", "Error", str(error_message))
        try:
            self._user_on_error(error_message)
        except Exception:
            logger.debug("UI error callback failed", exc_info=True)

    def _begin_ui_output_round(
        self, round_label: str, extension_name: str = "",
        source_path: str = "", source_type: str = "",
    ) -> None:
        """Write a self-describing header to this round's ui_output.log.

        Stored on the instance so _flush_progress_artifacts (which rewrites the
        file from the event list at the end) re-emits it instead of dropping it.
        """
        started = datetime.now().isoformat(timespec="seconds")
        if source_path:
            origin = f"{source_path} ({source_type})" if source_type else str(source_path)
        else:
            origin = "(repair round — no cookbook parse)"
        self._ui_round_header = [
            "=" * 78,
            f"Extension CLI pipeline  |  round: {round_label}",
            f"  extension : {extension_name}",
            f"  source    : {origin}",
            f"  started   : {started}",
            "=" * 78,
        ]
        if not self._debug_dir:
            return
        try:
            os.makedirs(self._debug_dir, exist_ok=True)
            with open(
                os.path.join(self._debug_dir, self._progress_log_name),
                "a", encoding="utf-8",
            ) as f:
                f.write("\n".join(self._ui_round_header) + "\n")
        except Exception:
            logger.debug("ui_output header write failed", exc_info=True)

    def _ui_output_footer(self, result: Dict) -> List[str]:
        """Build the closing summary block for this round's ui_output.log."""
        llm_calls = sum(
            1 for e in self._progress_events if e.get("phase") == "llm_call"
        )
        durations = "  ".join(
            f"{phase}={round(d, 1)}s"
            for phase, d in self._phase_durations.items()
        )
        repaired = result.get("repaired")
        footer = [
            "-" * 78,
            "SUMMARY",
            f"  success         : {bool(result.get('success'))}",
            f"  phases_completed: {', '.join(result.get('phases_completed', []) or []) or '(none)'}",
            f"  llm_calls       : {llm_calls}",
            f"  events          : {len(self._progress_events)}",
        ]
        if isinstance(repaired, list):
            footer.append(f"  templates_changed: {len(repaired)}  {repaired}")
        if durations:
            footer.append(f"  phase_durations : {durations}")
        if result.get("error"):
            footer.append(f"  error           : {str(result.get('error'))[:400]}")
        footer.append("-" * 78)
        return footer

    def _append_ui_output_line(self, event: Dict) -> None:
        """Incrementally mirror one event to debug/ui_output.log.

        Incremental appends keep a partial log even if Slicer dies mid-run;
        _flush_progress_artifacts rewrites the complete file at the end.
        """
        if not self._debug_dir:
            return
        try:
            os.makedirs(self._debug_dir, exist_ok=True)
            with open(
                os.path.join(self._debug_dir, self._progress_log_name),
                "a", encoding="utf-8",
            ) as f:
                f.write(self._format_ui_output_line(event) + "\n")
        except Exception:
            logger.debug("ui_output.log append failed", exc_info=True)

    @staticmethod
    def _format_ui_output_line(event: Dict) -> str:
        return (
            f"[{event['timestamp']} +{event['elapsed_s']:>7.1f}s] "
            f"[{event['phase']}] {event['title']} — {event['detail']}"
        )

    def _flush_progress_artifacts(self, result: Dict) -> None:
        """Write the complete UI output + structured events into debug/."""
        if not self._debug_dir or not self._progress_events:
            return
        try:
            os.makedirs(self._debug_dir, exist_ok=True)
            lines = list(self._ui_round_header)
            lines.extend(
                self._format_ui_output_line(event)
                for event in self._progress_events
            )
            lines.extend(self._ui_output_footer(result))
            with open(
                os.path.join(self._debug_dir, self._progress_log_name),
                "w", encoding="utf-8",
            ) as f:
                f.write("\n".join(lines) + "\n")
            with open(
                os.path.join(self._debug_dir, self._progress_json_name),
                "w", encoding="utf-8",
            ) as f:
                json.dump({
                    "success": bool(result.get("success")),
                    "error": result.get("error"),
                    "phases_completed": result.get("phases_completed", []),
                    "phase_durations_s": {
                        phase: round(duration, 1)
                        for phase, duration in self._phase_durations.items()
                    },
                    "event_count": len(self._progress_events),
                    "events": self._progress_events,
                }, f, indent=2, ensure_ascii=False)
        except Exception:
            logger.debug("Progress artifact flush failed", exc_info=True)

    # ================================================================
    # Main Entry Point
    # ================================================================

    def analyze_and_generate(
        self,
        extension_name: str,
        source_path: str,
        source_type: str = "",
        force_overwrite: bool = False,
    ) -> Dict:
        """
        Run the strict v2 cookbook-driven analysis pipeline.

        Args:
            extension_name: Name for the generated CLI directory.
            source_path: Path to the extension's source code root.
            source_type: How the extension was discovered
                         ("extension_manager", "additional_paths", "loaded_modules").
            force_overwrite: If True, overwrite existing CLI.

        Returns:
            Dict with 'success', 'cli_dir', 'manifest', 'phases_completed',
            'validation_result', 'error' keys.
        """
        import time as _time
        self._cancelled = False
        self._debug_dir = None
        self._llm_call_counter = 0
        self._current_stage_label = ""
        self._progress_events = []
        self._pipeline_start = _time.time()
        self._phase_start_times = {}
        self._phase_durations = {}
        self._progress_log_name = "ui_output.log"
        self._progress_json_name = "progress_events.json"
        self._cookbook_def = None
        self._slicer_op_templates = {}
        self._slicer_op_evidence = {}
        self._placement_starter_methods = {}
        self._widget_connections = []
        self._ui_parameter_bindings = {}
        self._workflow_metadata = {}
        self._last_logic_analysis = None
        self._last_api_probe_result = None
        self._upstream_feedback = []
        self._proven_api_chains = None
        self._ui_evidence_methods = None

        # Validate extension name (prevent path traversal)
        extension_name = _validate_extension_name(extension_name)
        # Extension source becomes a first-class search root for grounding
        # (registered as ext:<name>/ on the tool executor).
        self._source_path = source_path or ""

        result = {
            "success": False,
            "cli_dir": None,
            "manifest": None,
            "phases_completed": [],
            "stages_completed": [],
            "validation_result": None,
            "error": None,
        }

        if not self.output_base_dir:
            self.output_base_dir = self._default_base_dir()
        if not self.output_base_dir:
            result["error"] = (
                "output_base_dir is not set. "
                "Ensure the analyzer is constructed with a valid output directory."
            )
            return result

        ext_dir = os.path.join(self.output_base_dir, extension_name)
        if os.path.isdir(ext_dir) and not force_overwrite:
            result["error"] = f"CLI for '{extension_name}' already exists. Use force_overwrite=True."
            return result

        # Cross-run closed loop: a prior revision that hit an upstream
        # contract/dataflow root cause persisted its diagnosis; seed the
        # contract phase with it so regeneration addresses the failure.
        self._upstream_feedback = self._take_pending_upstream_feedback(extension_name)

        try:
            # First-generation debug artifacts live in their own round folder so a
            # later Repair round never clobbers them (debug/generation/).
            self._debug_dir = debug_round_dir(ext_dir, GENERATION_ROUND)
            self._begin_ui_output_round(GENERATION_ROUND, extension_name, source_path, source_type)

            # ── discover: source scan + cookbook parsing ──
            self._set_phase("discover")
            scan_result = self._stage1_scan(source_path)
            self._record_phase(result, "discover")
            if self._cancelled:
                result["error"] = "Cancelled during discover"
                return result

            if not scan_result.get("logic_class"):
                result["error"] = (
                    f"No ScriptedLoadableModuleLogic subclass found in {source_path}. "
                    "The extension may be C++-only or have no Python logic class."
                )
                return result

            # Extract Widget button→logic-method connections for post-classification verification
            self._widget_connections = []
            widget_info = scan_result.get("widget_class")
            if widget_info:
                widget_source = self._extract_class_source(
                    widget_info.get("file", ""), widget_info.get("class_name", "")
                )
                if widget_source:
                    self._widget_connections = self._extract_widget_connections(widget_source)
            scan_result["ui_widgets"] = self._extract_ui_widget_inventory(
                scan_result.get("ui_files", [])
            )
            entry_source = self._read_entry_source(scan_result)
            self._ui_parameter_bindings = self._extract_ui_parameter_bindings(
                entry_source,
                scan_result.get("ui_files", []),
                self._widget_connections,
            )
            scan_result["ui_parameter_bindings"] = self._ui_parameter_bindings

            # Cookbook detection and parsing are part of discover.
            cookbook_path = self._find_cookbook(extension_name)
            if not cookbook_path:
                result["error"] = (
                    f"No cookbook found for '{extension_name}'. "
                    "A cookbook (.md) in Resources/extensions_cookbook/ is required "
                    "for pipeline generation. "
                    "Expected: Resources/extensions_cookbook/{extension_name}.md "
                    "or Resources/extensions_cookbook/Slicer{extension_name}.md"
                )
                return result

            try:
                from ..CookbookParser import CookbookParser
                parser = CookbookParser()
                self._cookbook_def = parser.parse(cookbook_path)
            except Exception as e:
                result["error"] = f"Cookbook parse error: {e}"
                return result

            if not self._cookbook_def or not self._cookbook_def.steps:
                result["error"] = (
                    f"Cookbook found at {cookbook_path} but failed to parse "
                    "or contains no steps."
                )
                return result

            self.on_progress(
                "discover", "Discover Source And Cookbook",
                f"Parsed cookbook: {cookbook_path} "
                f"({len(self._cookbook_def.steps)} steps)"
            )

            # ── analyze: logic analysis + AST signature verification ──
            self._set_phase("analyze")
            logic_analysis = self._stage3_analyze_logic(scan_result)
            if self._cancelled:
                result["error"] = "Cancelled during analyze"
                return result
            self._verify_signatures_ast(logic_analysis, scan_result)
            self._last_logic_analysis = logic_analysis
            result["logic_analysis"] = logic_analysis
            self._record_phase(result, "analyze")
            if self._cancelled:
                result["error"] = "Cancelled during analyze"
                return result

            # ── closed-loop core: contract → ground → generate → verify_repair ──
            # When verify_repair diagnoses a contract/dataflow root cause it
            # cannot patch at template level, the contract phase is re-run with
            # the structured failure feedback injected (self._upstream_feedback)
            # and only invalidated downstream artifacts are re-derived. Bounded
            # by re-entry caps plus a monotone-progress rule: a re-entry that
            # leaves the contract facts unchanged terminates the loop.
            MAX_CONTRACT_REENTRIES = 2
            MAX_TOTAL_REENTRIES = 3
            reentry_count = 0
            prev_contract_fingerprint = None
            reentry_trace = []
            # Scoped re-entry state: a re-entry re-derives the full contract
            # (the LLM still needs full-workflow context) but only the steps
            # implicated by the upstream feedback — plus their data-flow
            # neighbors — are REPLACED; every other step keeps its previous
            # derivation verbatim. This prevents regression churn on
            # untouched steps and lets ground/generate reuse prior work.
            self._reentry_affected_steps = None
            self._reentry_implicated_steps = set()
            self._prev_stage_map = None
            self._prev_templates = None
            self._slicer_op_template_cache = {}

            while True:
                # ── contract: semantic decomposition + workflow contract ──
                self._set_phase("contract")
                stage_map = self._stage4_cookbook_decomposition(
                    self._cookbook_def, logic_analysis, scan_result
                )
                if self._cancelled:
                    result["error"] = "Cancelled during contract"
                    return result
                if self._reentry_affected_steps and isinstance(self._prev_stage_map, dict):
                    stage_map, preserved_count = self._merge_stage_map_scoped(
                        self._prev_stage_map, stage_map, self._reentry_affected_steps
                    )
                    self.on_progress(
                        "contract", "Build Workflow Contract",
                        f"Scoped re-entry: re-derived step(s) "
                        f"{sorted(self._reentry_affected_steps)}; preserved "
                        f"{preserved_count} unaffected step derivation(s) verbatim",
                    )
                cross_stage_map = self._stage4_5_cross_stage_mapping(
                    stage_map, logic_analysis, extension_name
                )
                self._record_phase(result, "contract")
                if self._cancelled:
                    result["error"] = "Cancelled during contract"
                    return result

                workflow_graph = self._build_workflow_from_cookbook(
                    self._cookbook_def, logic_analysis, stage_map
                )
                # Repair lineage must survive contract re-entries so the
                # escalation ladder never repeats an exhausted strategy.
                prior_repair_history = (
                    self._workflow_metadata.get("repair_strategy_history", [])
                    if isinstance(self._workflow_metadata, dict) else []
                )
                prior_repair_trace = (
                    self._workflow_metadata.get("repair_trace", [])
                    if isinstance(self._workflow_metadata, dict) else []
                )
                self._workflow_metadata = self._build_workflow_metadata(
                    scan_result, logic_analysis, workflow_graph
                )
                if prior_repair_history:
                    self._workflow_metadata["repair_strategy_history"] = prior_repair_history
                if prior_repair_trace:
                    self._workflow_metadata["repair_trace"] = prior_repair_trace
                if reentry_trace:
                    self._workflow_metadata["upstream_reentries"] = list(reentry_trace)
                self._enrich_workflow_with_metadata(workflow_graph, self._workflow_metadata)
                self._placement_starter_methods = self._classify_placement_starter_methods(
                    logic_analysis
                )
                starter_names = sorted(self._placement_starter_methods)
                self.on_progress(
                    "contract", "Build Workflow Contract",
                    f"Placement-starter methods detected: {len(starter_names)}"
                    + (f" ({', '.join(starter_names[:8])}"
                       + (", ..." if len(starter_names) > 8 else "") + ")"
                       if starter_names else ""),
                )
                self._normalize_workflow_contracts(
                    workflow_graph, self._workflow_metadata, scan_result, logic_analysis
                )
                self._synthesize_workflow_ui_guidance(
                    workflow_graph, self._workflow_metadata, scan_result, logic_analysis
                )
                if self._cancelled:
                    result["error"] = "Cancelled during contract"
                    return result

                workflow_contract = self._build_workflow_contract_v2(
                    extension_name, scan_result, cookbook_path, logic_analysis, workflow_graph
                )
                result["workflow_contract"] = workflow_contract
                self._set_phase("audit_contract")
                contract_audit = self._enforce_workflow_contract_audit(
                    workflow_contract,
                    workflow_graph=workflow_graph,
                    logic_analysis=logic_analysis,
                    raise_on_fail=False,
                )
                result["contract_audit"] = contract_audit
                self._record_phase(result, "audit_contract")

                # Fingerprint of the facts a re-entry is supposed to change;
                # used for the monotone-progress termination rule. On a scoped
                # re-entry only the affected steps are fingerprinted — LLM
                # noise on preserved steps (or in the re-derived cross-stage
                # connections) must not defeat the no-progress check.
                contract_fingerprint = self._scoped_contract_fingerprint(
                    stage_map, cross_stage_map, self._reentry_affected_steps
                )

                # A failed contract audit (e.g. an LLM intent mislabel like tagging
                # a "slice visibility in 3D" step as slice-intersection) is
                # RECOVERABLE: re-enter the contract phase with the audit findings
                # as feedback instead of hard-aborting. Bounded by the same budget +
                # monotone-progress rule as verify_repair's upstream re-entry.
                if not contract_audit.get("valid"):
                    action, reentry_count, prev_contract_fingerprint = (
                        self._attempt_contract_reentry_from_audit(
                            contract_audit,
                            reentry_count=reentry_count,
                            prev_contract_fingerprint=prev_contract_fingerprint,
                            contract_fingerprint=contract_fingerprint,
                            reentry_trace=reentry_trace,
                            cross_stage_map=cross_stage_map,
                            stage_map=stage_map,
                            max_contract_reentries=MAX_CONTRACT_REENTRIES,
                            max_total_reentries=MAX_TOTAL_REENTRIES,
                        )
                    )
                    if action == "reenter":
                        continue
                    # Budget/progress exhausted — fail the run through the existing
                    # error handler (same outcome as before, after trying to heal).
                    if reentry_trace and isinstance(self._workflow_metadata, dict):
                        self._workflow_metadata["upstream_reentries"] = reentry_trace
                    raise RuntimeError(
                        "Workflow contract audit failed after re-entry attempts: "
                        + "; ".join(contract_audit.get("errors", []))
                    )

                # ── ground: Slicer API evidence and slicer_op template grounding ──
                self._set_phase("ground")
                self._slicer_op_templates = self._generate_slicer_op_templates(
                    stage_map
                )
                # Recompute the evidence-backed API chain set for this
                # iteration's generation prompts (ground output changed).
                self._proven_api_chains = None
                self._ui_evidence_methods = None
                ground_templates = self._slicer_op_templates or {}
                missing_evidence_steps = sorted(
                    step for step, code in ground_templates.items()
                    if isinstance(code, str) and "MISSING_EVIDENCE" in code
                )
                self.on_progress(
                    "ground", "Ground Slicer APIs",
                    f"Grounded {len(ground_templates)} slicer_op template(s); "
                    f"{len(missing_evidence_steps)} reporting MISSING_EVIDENCE"
                    + (f" ({', '.join(missing_evidence_steps[:6])})"
                       if missing_evidence_steps else ""),
                )
                self._record_phase(result, "ground")

                # ── generate: schemas and templates ──
                self._set_phase("generate")
                tool_schemas = self._stage6_generate_schemas(
                    extension_name, stage_map, logic_analysis,
                    cross_stage_map=cross_stage_map,
                    workflow_graph=workflow_graph,
                )
                self._record_phase(result, "generate")
                if self._cancelled:
                    result["error"] = "Cancelled during generate"
                    return result

                node_lifecycle = self._compute_node_lifecycle(scan_result, logic_analysis)
                templates = self._stage7_generate_templates(
                    extension_name, stage_map, node_lifecycle, scan_result, logic_analysis,
                    cross_stage_map=cross_stage_map,
                    workflow_graph=workflow_graph,
                )
                # Internal LLM review (not a separate numbered stage)
                templates = self._review_templates(templates, logic_analysis, node_lifecycle)  # internal LLM review
                templates = self._sanitize_templates(templates)
                workflow_contract = self._build_workflow_contract_v2(
                    extension_name, scan_result, cookbook_path, logic_analysis, workflow_graph
                )
                result["workflow_contract"] = workflow_contract
                contract_audit = self._enforce_workflow_contract_audit(
                    workflow_contract,
                    workflow_graph=workflow_graph,
                    logic_analysis=logic_analysis,
                )
                result["contract_audit"] = contract_audit
                if self._cancelled:
                    result["error"] = "Cancelled during generate"
                    return result

                # ── verify_repair: static validation, live probes, targeted repair loop ──
                self._set_phase("verify_repair")
                manifest, generators = self._build_manifest_and_generators(
                    extension_name, scan_result, stage_map,
                    workflow_graph=workflow_graph,
                )
                workflow_graph = self._canonicalize_workflow_graph_v2(workflow_graph)
                generators = self._canonicalize_generators_v2(generators)
                templates["workflow.json"] = json.dumps(workflow_graph, indent=2)
                templates["workflow_contract.json"] = self._workflow_contract_to_json(workflow_contract)
                self._sync_template_contracts(
                    templates,
                    generators,
                    workflow_graph=workflow_graph,
                )
                result["workflow_metadata"] = self._workflow_metadata
                templates, validation_result = self._verify_and_repair_templates(
                    extension_name=extension_name,
                    templates=templates,
                    generators=generators,
                    logic_analysis=logic_analysis,
                    workflow_contract=workflow_contract,
                    workflow_graph=workflow_graph,
                )
                probe_result = validation_result.get("api_probe_result") or {}
                self._last_api_probe_result = probe_result
                result["api_probe_result"] = probe_result
                self._record_phase(result, "verify_repair")
                result["workflow_metadata"] = self._workflow_metadata
                result["validation_result"] = validation_result
                if self._cancelled:
                    result["error"] = "Cancelled during verify_repair"
                    return result

                # ── upstream re-entry decision ──
                upstream_requests = validation_result.get("upstream_requests") or []
                if validation_result.get("valid") or not upstream_requests:
                    break
                if reentry_count > 0 and contract_fingerprint == prev_contract_fingerprint:
                    reentry_trace.append({
                        "event": "no_progress",
                        "detail": (
                            "Contract re-entry produced identical contract facts; "
                            "stopping re-entry (monotone-progress rule)."
                        ),
                    })
                    logger.warning("[upstream re-entry] no progress after re-entry; stopping")
                    break
                if reentry_count >= min(MAX_CONTRACT_REENTRIES, MAX_TOTAL_REENTRIES):
                    reentry_trace.append({
                        "event": "budget_exhausted",
                        "detail": f"Re-entry budget exhausted after {reentry_count} re-entries.",
                    })
                    logger.warning("[upstream re-entry] budget exhausted; stopping")
                    break
                reentry_count += 1
                self._upstream_feedback.extend(upstream_requests)
                # Scope the upcoming re-entry: steps named by the upstream
                # requests plus their one-hop data-flow neighbors get
                # re-derived; everything else is preserved from this
                # iteration. Steps named in ANY unresolved validation error
                # also lose ground/generate reuse eligibility.
                affected_steps = self._affected_steps_from_requests(
                    upstream_requests, cross_stage_map
                )
                self._reentry_affected_steps = affected_steps or None
                self._reentry_implicated_steps = (
                    set(affected_steps)
                    | self._step_numbers_in_errors(validation_result.get("errors") or [])
                )
                self._prev_stage_map = stage_map
                self._prev_templates = dict(templates)
                # Compare like with like next iteration: re-scope this
                # iteration's fingerprint to the new affected set.
                prev_contract_fingerprint = self._scoped_contract_fingerprint(
                    stage_map, cross_stage_map, self._reentry_affected_steps
                )
                reentry_trace.append({
                    "event": "reentry",
                    "attempt": reentry_count,
                    "phase": "contract",
                    "affected_steps": sorted(affected_steps),
                    "requests": upstream_requests,
                })
                self.on_progress(
                    "contract", "Build Workflow Contract",
                    f"Upstream re-entry {reentry_count}: re-deriving workflow contract "
                    f"with {len(upstream_requests)} downstream failure(s) as feedback, "
                    f"scoped to step(s) {sorted(affected_steps) or 'ALL'}...",
                )

            if reentry_trace:
                self._workflow_metadata["upstream_reentries"] = reentry_trace
                result["upstream_reentries"] = reentry_trace

            if validation_result.get("valid"):
                self._finalize_package_validation_state(
                    manifest, validation_result,
                    templates=templates, generators=generators,
                )
                self._set_phase("package")
                prompt_fragment = self._stage8_generate_prompt(
                    extension_name, tool_schemas, stage_map, logic_analysis,
                    workflow_graph=workflow_graph,
                )
                self._record_phase(result, "package")
                if self._cancelled:
                    result["error"] = "Cancelled during package"
                    return result
            else:
                self._finalize_package_validation_state(
                    manifest, validation_result,
                    templates=templates, generators=generators,
                )
                prompt_fragment = (
                    f"### {extension_name}\n\n"
                    "Generation failed validation. This CLI package is saved "
                    "only for debugging/revision and is not loaded as a runtime tool.\n"
                )
            manifest["manifest_version"] = MANIFEST_VERSION
            manifest["pipeline_version"] = PIPELINE_VERSION
            manifest["workflow_contract_file"] = "workflow_contract.json"
            templates["workflow_contract.json"] = self._workflow_contract_to_json(workflow_contract)
            templates["workflow_metadata.json"] = json.dumps(self._workflow_metadata or {}, indent=2)

            # Save CLI package
            from ..ExtensionCLILoader import save_cli_package
            cli_dir = save_cli_package(
                extension_name=extension_name,
                manifest=manifest,
                tool_schemas=tool_schemas,
                code_generators=generators,
                templates=templates,
                prompt_fragment=prompt_fragment,
                generation_log_entry={
                    "attempt": 1,
                    "timestamp": datetime.now().isoformat(),
                    "phase": "package",
                    "trigger": "user_request",
                    "phases_completed": result["phases_completed"],
                    "api_probe_result": probe_result,
                    "validation_result": validation_result,
                },
            )
            result["cli_dir"] = cli_dir
            result["manifest"] = manifest

            if validation_result.get("valid"):
                result["success"] = True
            else:
                result["error"] = (
                    f"Validation failed: {validation_result.get('errors', [])}. "
                    "Use revise to fix."
                )

        except Exception as e:
            tb = traceback.format_exc()
            logger.error("ExtensionCLIAnalyzer failed: %s\n%s", e, tb)
            result["error"] = str(e)
            self.on_error(str(e))

        finally:
            # Close the timing of the last phase and emit the run summary so
            # the UI and the persisted log both end with the full picture.
            try:
                self._set_phase("summary")
                import time as _time
                total = _time.time() - (self._pipeline_start or _time.time())
                phase_parts = ", ".join(
                    f"{phase} {duration:.1f}s"
                    for phase, duration in self._phase_durations.items()
                    if phase != "summary"
                )
                status = "SUCCESS" if result.get("success") else (
                    f"FAILED: {str(result.get('error'))[:200]}" if result.get("error")
                    else "validation_failed (saved for revision)"
                )
                self.on_progress(
                    "summary", "Run Summary",
                    f"{status} | total {total:.1f}s | phases: {phase_parts or 'n/a'} "
                    f"| LLM calls: {self._llm_call_counter} "
                    f"| events: {len(self._progress_events)}",
                )
            except Exception:
                logger.debug("Run summary emission failed", exc_info=True)
            self._flush_progress_artifacts(result)
            self._debug_dir = None

        return result



def _patch_mixin_globals():
    from . import llm_calls, repair_memory, scan, logic_analysis, stage4_decomposition, cross_stage, node_lifecycle, schemas, workflow_templates, template_helpers, api_probe, template_generation, prompt_validation, validation_contracts, validation_semantics, live_revision, cookbook_mapping, parameter_metadata, workflow_contracts, slicer_op_manifest, phases, v2_contracts, repair_loop, contract_audit
    for _module in [llm_calls, repair_memory, scan, logic_analysis, stage4_decomposition, cross_stage, node_lifecycle, schemas, workflow_templates, template_helpers, api_probe, template_generation, prompt_validation, validation_contracts, validation_semantics, live_revision, cookbook_mapping, parameter_metadata, workflow_contracts, slicer_op_manifest, phases, v2_contracts, repair_loop, contract_audit]:
        _module.ExtensionCLIAnalyzer = ExtensionCLIAnalyzer


_patch_mixin_globals()
