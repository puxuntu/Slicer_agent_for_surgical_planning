from .common import *
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


class ExtensionCLIAnalyzer(
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
):
    """
    Analyzes a Slicer extension's source code and generates operation CLIs.

    Strict v2 cookbook-driven pipeline:
    discover -> analyze -> contract -> ground -> generate -> verify_repair -> package.
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
        self.on_progress = on_progress or (lambda n, s, d: None)
        self.on_error = on_error or (lambda e: None)
        self._method_keyword_map = {}
        self._live_probe_executor = live_probe_executor
        self._analyzer_prompt = self._load_analyzer_prompt()
        self._cancelled = False
        # Pipeline-scoped state (reset in analyze_and_generate)
        self._ui_workflow: Optional[Dict] = None  # only used by legacy fallback methods
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
        self._cancelled = False
        self._debug_dir = None
        self._llm_call_counter = 0
        self._current_stage_label = ""
        self._cookbook_def = None
        self._slicer_op_templates = {}
        self._slicer_op_evidence = {}
        self._placement_starter_methods = {}
        self._widget_connections = []
        self._ui_parameter_bindings = {}
        self._workflow_metadata = {}
        self._last_logic_analysis = None
        self._last_api_probe_result = None

        # Validate extension name (prevent path traversal)
        extension_name = _validate_extension_name(extension_name)

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

        try:
            # Set up debug directory (lazily created on first LLM call)
            self._debug_dir = os.path.join(ext_dir, "debug")

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
            self._last_logic_analysis = logic_analysis
            result["logic_analysis"] = logic_analysis
            self._record_phase(result, "analyze")
            if self._cancelled:
                result["error"] = "Cancelled during analyze"
                return result

            self._verify_signatures_ast(logic_analysis, scan_result)
            if self._cancelled:
                result["error"] = "Cancelled during analyze"
                return result

            # ── contract: semantic decomposition + workflow contract ──
            self._set_phase("contract")
            stage_map = self._stage4_cookbook_decomposition(
                self._cookbook_def, logic_analysis, scan_result
            )
            self._record_phase(result, "contract")
            if self._cancelled:
                result["error"] = "Cancelled during contract"
                return result

            cross_stage_map = self._stage4_5_cross_stage_mapping(
                stage_map, logic_analysis, extension_name
            )
            if self._cancelled:
                result["error"] = "Cancelled during contract"
                return result

            workflow_graph = self._build_workflow_from_cookbook(
                self._cookbook_def, logic_analysis, stage_map
            )
            self._workflow_metadata = self._build_workflow_metadata(
                scan_result, logic_analysis, workflow_graph
            )
            self._enrich_workflow_with_metadata(workflow_graph, self._workflow_metadata)
            self._placement_starter_methods = self._classify_placement_starter_methods(
                logic_analysis
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

            # ── ground: Slicer API evidence and slicer_op template grounding ──
            self._set_phase("ground")
            self._slicer_op_templates = self._generate_slicer_op_templates(
                stage_map
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

            if validation_result.get("valid"):
                manifest["status"] = "validated"
                manifest["validation_state"] = self._workflow_metadata.get("validation_state", {})
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
                manifest["status"] = "validation_failed"
                manifest["validation_state"] = self._workflow_metadata.get("validation_state", {})
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
            self._debug_dir = None

        return result



def _patch_mixin_globals():
    from . import scan, logic_analysis, stage4_decomposition, cross_stage, node_lifecycle, schemas, workflow_templates, template_helpers, api_probe, template_generation, prompt_validation, validation_contracts, validation_semantics, live_revision, cookbook_mapping, parameter_metadata, workflow_contracts, slicer_op_manifest, phases, v2_contracts, repair_loop
    for _module in [scan, logic_analysis, stage4_decomposition, cross_stage, node_lifecycle, schemas, workflow_templates, template_helpers, api_probe, template_generation, prompt_validation, validation_contracts, validation_semantics, live_revision, cookbook_mapping, parameter_metadata, workflow_contracts, slicer_op_manifest, phases, v2_contracts, repair_loop]:
        _module.ExtensionCLIAnalyzer = ExtensionCLIAnalyzer


_patch_mixin_globals()
