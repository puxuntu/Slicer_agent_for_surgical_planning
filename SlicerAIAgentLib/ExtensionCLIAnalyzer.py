"""
ExtensionCLIAnalyzer - 9-stage pipeline for analyzing Slicer extensions
and generating operation CLIs (tool schemas + code templates).

The pipeline is cookbook-driven: a markdown cookbook describing the extension's
step-by-step workflow is REQUIRED.  Without it the pipeline aborts.

Uses the same LLM provider as the main agent to analyze extension source code,
identify operations, and generate validated code templates that integrate with
the SlicerAIAgent tool system.
"""

import ast
import json
import logging
import os
import re as _re
import textwrap
import traceback
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Path to the analyzer system prompt
_ANALYZER_PROMPT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "Resources", "Prompts", "extension_cli_analyzer_prompt.md",
)

# Maximum source file size to send to LLM (chars)
_MAX_SOURCE_FOR_LLM = 300_000

# Maximum revision attempts for failed validation
_MAX_REVISION_ATTEMPTS = 3

# Regex to strip JavaScript-style // comments from LLM JSON output.
# Matches // comments that appear after JSON structural chars (, : [ ] { })
# or whitespace — avoids breaking URLs inside string values.
_JS_COMMENT_RE = _re.compile(r'(?<=[,\[\]{}:\s])\s*//[^\n]*')

# Derive interaction_type from node_class.  interaction_type is kept as a
# convenience label for display / logging but is NEVER used as a gate — the
# presence of a `user_interaction` sub-operation in `sub_operations` is the
# authoritative signal that a step requires user interaction.
_NODE_CLASS_TO_INTERACTION_TYPE = {
    "vtkMRMLMarkupsCurveNode": "curve",
    "vtkMRMLMarkupsPlaneNode": "plane",
    "vtkMRMLMarkupsLineNode": "line",
    "vtkMRMLMarkupsFiducialNode": "fiducial",
    "vtkMRMLMarkupsROINode": "roi",
}


def _derive_interaction_type(node_class, fallback="generic"):
    """Derive a human-readable interaction type from a node class string."""
    return _NODE_CLASS_TO_INTERACTION_TYPE.get(node_class or "", fallback)


def _collect_attr_chain(node) -> List[str]:
    """Recursively collect attribute chain from an AST node.

    Turns `slicer.app.layoutManager().setLayout` into
    ["slicer", "app", "layoutManager", "setLayout"].
    """
    import ast as _ast
    parts = []
    current = node
    while True:
        if isinstance(current, _ast.Attribute):
            parts.append(current.attr)
            current = current.value
        elif isinstance(current, _ast.Call):
            current = current.func
        elif isinstance(current, _ast.Name):
            parts.append(current.id)
            break
        elif isinstance(current, _ast.Subscript):
            current = current.value
        else:
            break
    parts.reverse()
    return parts


def _validate_extension_name(name: str) -> str:
    """Validate and sanitize an extension name to prevent path traversal.

    Returns the sanitized name.  Raises ValueError if the name is invalid.
    """
    if not name or not name.strip():
        raise ValueError("Extension name must not be empty.")
    # Reject path separators and traversal patterns
    if any(ch in name for ch in ("/", "\\", "\x00")):
        raise ValueError(
            f"Invalid extension name '{name}': contains path separators."
        )
    if ".." in name:
        raise ValueError(
            f"Invalid extension name '{name}': contains '..' traversal."
        )
    return name.strip()


def _tokenize_name(name: str) -> set:
    """Split a CamelCase/underscore name into lowercase tokens."""
    import re
    name = _text_or_empty(name)
    parts = re.split(r'(?<=[a-z])(?=[A-Z])|_|(?<=[A-Z])(?=[A-Z][a-z])', name)
    return {p.lower() for p in parts if p}


def _text_or_empty(value: Any) -> str:
    """Return a safe text value for fields that may come from LLM JSON."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _optional_text(value: Any) -> Optional[str]:
    """Return a stripped string for meaningful text fields, otherwise None."""
    if value is None or isinstance(value, bool):
        return None
    text = _text_or_empty(value).strip()
    return text or None


def _text_list(value: Any) -> List[str]:
    """Coerce a possibly malformed LLM field into a list of text values."""
    if value is None:
        return []
    if isinstance(value, list):
        return [_text_or_empty(v) for v in value if v is not None]
    return [_text_or_empty(value)]


def _int_or_none(value: Any) -> Optional[int]:
    """Coerce simple integer-like values without treating booleans as numbers."""
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _name_similarity(name_a: str, name_b: str) -> float:
    """Jaccard similarity between tokens of two names."""
    ta = _tokenize_name(name_a)
    tb = _tokenize_name(name_b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _parse_default_value(default_str: str):
    """Parse a default value string from AST into a Python value."""
    if default_str == "True":
        return True
    if default_str == "False":
        return False
    if default_str == "None":
        return None
    try:
        return int(default_str)
    except (ValueError, TypeError):
        pass
    try:
        return float(default_str)
    except (ValueError, TypeError):
        pass
    return default_str


class _AddNodeVisitor(ast.NodeVisitor):
    """AST visitor that detects AddNode/AddNewNodeByClass calls on method parameters."""

    def __init__(self, param_names: set):
        self.param_names = param_names
        self.params_added_to_scene = set()   # params passed to AddNode()
        self.has_addnewnodebyclass = False    # method calls AddNewNodeByClass anywhere
        self._added_node_args = []            # raw args to AddNode calls

    def visit_Call(self, node):
        func_name = self._get_qualified_name(node.func)
        # slicer.mrmlScene.AddNode(param)
        if func_name and func_name.endswith("AddNode"):
            for arg in node.args:
                if isinstance(arg, ast.Name) and arg.id in self.param_names:
                    self.params_added_to_scene.add(arg.id)
                elif isinstance(arg, ast.Name):
                    self._added_node_args.append(arg.id)
            # Don't recurse into the call's args
            return
        # slicer.mrmlScene.AddNewNodeByClass(...)
        if func_name and func_name.endswith("AddNewNodeByClass"):
            self.has_addnewnodebyclass = True
            return
        self.generic_visit(node)

    @staticmethod
    def _get_qualified_name(node):
        parts = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
        return ".".join(reversed(parts)) if parts else None


class ExtensionCLIAnalyzer:
    """
    Analyzes a Slicer extension's source code and generates operation CLIs.

    9-stage cookbook-driven pipeline:
    1. AST Scanning (no LLM)
    2. Cookbook Detection & Parsing (regex-based, no LLM, REQUIRED)
    3. Logic Class Analysis (LLM)
    3.5. AST Signature Verification (no LLM)
    4. Cookbook Stage Map — LLM Decomposition into sub-operations
    4.5. Cross-Stage Parameter Mapping (LLM)
    5C. Workflow Graph Building
    5T. Slicer Op Templates (KB search + LLM)
    6. Tool Schema Generation (LLM)
    7. Code Template Generation (LLM, includes internal LLM review)
    8. Prompt Fragment Generation (LLM)
    9. Validation + Save (CodeValidator, semantic checks, optional revision)
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
            method_keyword_map: Optional per-extension mapping of cookbook
                description keywords to logic method names (e.g.
                {"create bone model": "createBoneModels"}).  Used by the
                heuristic fallback when LLM decomposition fails.  If not
                provided, only fuzzy word-overlap matching is used.
            live_probe_executor: Optional callable that executes a probe snippet
                on Slicer's main thread and returns the probe result.
        """
        self.llm_client = llm_client
        self.output_base_dir = output_base_dir or self._default_base_dir()
        self.code_validator = code_validator
        self.on_progress = on_progress or (lambda n, s, d: None)
        self.on_error = on_error or (lambda e: None)
        self._method_keyword_map = method_keyword_map or {}
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
            candidates.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
        Run the full 9-stage cookbook-driven analysis pipeline.

        Args:
            extension_name: Name for the generated CLI directory.
            source_path: Path to the extension's source code root.
            source_type: How the extension was discovered
                         ("extension_manager", "additional_paths", "loaded_modules").
            force_overwrite: If True, overwrite existing CLI.

        Returns:
            Dict with 'success', 'cli_dir', 'manifest', 'stages_completed',
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
        self._workflow_metadata = {}
        self._last_logic_analysis = None
        self._last_api_probe_result = None

        # Validate extension name (prevent path traversal)
        extension_name = _validate_extension_name(extension_name)

        result = {
            "success": False,
            "cli_dir": None,
            "manifest": None,
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

            # ── Stage 1: AST Scanning (no LLM) ──
            self._current_stage_label = "1"
            scan_result = self._stage1_scan(source_path)
            result["stages_completed"].append(1)
            if self._cancelled:
                result["error"] = "Cancelled during Stage 1"
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

            # ── Stage 2: Cookbook Detection & Parsing (no LLM, REQUIRED) ──
            self._current_stage_label = "2"
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
                from .CookbookParser import CookbookParser
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
                2, "Cookbook detection & parsing",
                f"Parsed cookbook: {cookbook_path} "
                f"({len(self._cookbook_def.steps)} steps)"
            )
            result["stages_completed"].append(2)

            # ── Stage 3: Logic Class Analysis (LLM) ──
            self._current_stage_label = "3"
            logic_analysis = self._stage3_analyze_logic(scan_result)
            self._last_logic_analysis = logic_analysis
            result["logic_analysis"] = logic_analysis
            result["stages_completed"].append(3)
            if self._cancelled:
                result["error"] = "Cancelled during Stage 3"
                return result

            # ── Stage 3.5: AST Signature Verification (no LLM) ──
            self._current_stage_label = "3.5"
            self._verify_signatures_ast(logic_analysis, scan_result)
            result["stages_completed"].append("3.5")
            if self._cancelled:
                result["error"] = "Cancelled during Stage 3.5"
                return result

            # ── Stage 4: Cookbook Stage Map — LLM Decomposition ──
            self._current_stage_label = "4"
            stage_map = self._stage4_cookbook_decomposition(
                self._cookbook_def, logic_analysis
            )
            result["stages_completed"].append(4)
            if self._cancelled:
                result["error"] = "Cancelled during Stage 4"
                return result

            # ── Stage 4.5: Cross-Stage Parameter Mapping (LLM) ──
            self._current_stage_label = "4.5"
            cross_stage_map = self._stage4_5_cross_stage_mapping(
                stage_map, logic_analysis, extension_name
            )
            result["stages_completed"].append("4.5")
            if self._cancelled:
                result["error"] = "Cancelled during Stage 4.5"
                return result

            # ── Stage 5C: Workflow Graph Building ──
            self._current_stage_label = "5C"
            workflow_graph = self._build_workflow_from_cookbook(
                self._cookbook_def, logic_analysis, stage_map
            )
            self._workflow_metadata = self._build_workflow_metadata(
                scan_result, logic_analysis, workflow_graph
            )
            self._enrich_workflow_with_metadata(workflow_graph, self._workflow_metadata)
            result["stages_completed"].append("5C")
            if self._cancelled:
                result["error"] = "Cancelled during Stage 5C"
                return result

            # ── Stage 5T: Slicer Op Template Generation (KB search) ──
            self._current_stage_label = "5T"
            self._slicer_op_templates = self._generate_slicer_op_templates(
                stage_map
            )
            result["stages_completed"].append("5T")

            # ── Stage 6: Tool Schema Generation (LLM) ──
            self._current_stage_label = "6"
            tool_schemas = self._stage6_generate_schemas(
                extension_name, stage_map, logic_analysis,
                cross_stage_map=cross_stage_map,
                workflow_graph=workflow_graph,
            )
            result["stages_completed"].append(6)
            if self._cancelled:
                result["error"] = "Cancelled during Stage 6"
                return result

            # ── Stage 7: Code Template Generation (LLM + internal review) ──
            self._current_stage_label = "7"
            node_lifecycle = self._compute_node_lifecycle(scan_result, logic_analysis)
            self._placement_starter_methods = self._classify_placement_starter_methods(
                logic_analysis
            )
            self._normalize_workflow_contracts(
                workflow_graph, self._workflow_metadata, scan_result, logic_analysis
            )
            templates = self._stage7_generate_templates(
                extension_name, stage_map, node_lifecycle, scan_result, logic_analysis,
                cross_stage_map=cross_stage_map,
                workflow_graph=workflow_graph,
            )
            # Internal LLM review (not a separate numbered stage)
            templates = self._review_templates(templates, logic_analysis, node_lifecycle)  # internal LLM review
            result["stages_completed"].append(7)
            if self._cancelled:
                result["error"] = "Cancelled during Stage 7"
                return result

            # ── Stage 7.5: Live API Probing ──
            self._current_stage_label = "7.5"
            probe_result = self._stage7c_live_api_probe(templates)
            self._last_api_probe_result = probe_result
            result["stages_completed"].append("7.5")
            result["api_probe_result"] = probe_result
            if probe_result.get("revised", 0) > 0:
                templates = self._sanitize_templates(templates)
            if self._cancelled:
                result["error"] = "Cancelled during Stage 7.5"
                return result

            # ── Stage 9: Validation + Save ──
            self._current_stage_label = "9"
            manifest, generators = self._build_manifest_and_generators(
                extension_name, scan_result, stage_map,
                workflow_graph=workflow_graph,
            )
            self._sync_template_contracts(
                templates,
                generators,
                workflow_graph=workflow_graph,
            )
            result["workflow_metadata"] = self._workflow_metadata
            validation_result = self._stage9_validate(
                templates, generators, logic_analysis=logic_analysis,
                api_probe_result=probe_result,
            )
            result["stages_completed"].append(9)
            result["validation_result"] = validation_result

            if validation_result.get("valid"):
                manifest["status"] = "validated"
                manifest["validation_state"] = self._workflow_metadata.get("validation_state", {})
                # ── Stage 8: Prompt Fragment Generation (LLM) ──
                # Generate the runtime prompt only after templates are known to
                # be valid, so prompt instructions match the final package.
                self._current_stage_label = "8"
                prompt_fragment = self._stage8_generate_prompt(
                    extension_name, tool_schemas, stage_map, logic_analysis,
                    workflow_graph=workflow_graph,
                )
                result["stages_completed"].append(8)
                if self._cancelled:
                    result["error"] = "Cancelled during Stage 8"
                    return result
            else:
                manifest["status"] = "validation_failed"
                manifest["validation_state"] = self._workflow_metadata.get("validation_state", {})
                prompt_fragment = (
                    f"### {extension_name}\n\n"
                    "Generation failed validation. This CLI package is saved "
                    "only for debugging/revision and is not loaded as a runtime tool.\n"
                )
            templates["workflow_metadata.json"] = json.dumps(self._workflow_metadata or {}, indent=2)

            # Save CLI package
            from .ExtensionCLILoader import save_cli_package
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
                    "stage": "initial_generation",
                    "trigger": "user_request",
                    "analysis_stages_completed": result["stages_completed"],
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

    # ================================================================
    # Stage 1: Extension Scanning (AST, no LLM)
    # ================================================================

    def _stage1_scan(self, source_path: str) -> Dict:
        """Scan extension source tree, parse AST, find Logic class."""
        self.on_progress(1, "Scanning extension files", "Walking directory tree...")

        if not os.path.isdir(source_path):
            raise ValueError(f"Source path does not exist: {source_path}")

        # Walk and collect Python and .ui files
        py_files = []
        ui_files = []
        for root, dirs, files in os.walk(source_path):
            # Skip hidden dirs, __pycache__, build dirs
            dirs[:] = [d for d in dirs if not d.startswith((".", "__")) and d != "build"]
            for f in files:
                if f.endswith(".py"):
                    py_files.append(os.path.join(root, f))
                elif f.endswith(".ui"):
                    ui_files.append(os.path.join(root, f))

        self.on_progress(
            1, "Scanning extension files",
            f"Found {len(py_files)} Python files"
        )

        # Parse each file's AST
        file_inventory = {}
        logic_candidates = []
        widget_candidates = []

        for fpath in py_files:
            try:
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    source = f.read()
                tree = ast.parse(source)
            except Exception:
                continue

            classes = []
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    bases = [self._ast_name(b) for b in node.bases]
                    methods = [
                        n.name for n in node.body
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                    ]
                    classes.append({
                        "name": node.name,
                        "bases": bases,
                        "methods": methods,
                        "line": node.lineno,
                    })
                    # Detect Logic class
                    is_logic = (
                        "ScriptedLoadableModuleLogic" in bases
                        or node.name.endswith("Logic")
                    )
                    if is_logic:
                        logic_candidates.append({
                            "file": fpath,
                            "class_name": node.name,
                            "methods": methods,
                            "bases": bases,
                            "line": node.lineno,
                        })
                    # Detect Widget class
                    is_widget = (
                        "ScriptedLoadableModuleWidget" in bases
                        or node.name.endswith("Widget")
                    )
                    if is_widget:
                        widget_candidates.append({
                            "file": fpath,
                            "class_name": node.name,
                            "methods": methods,
                            "bases": bases,
                            "line": node.lineno,
                        })
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(node.name)

            file_inventory[fpath] = {
                "classes": classes,
                "functions": functions,
            }

        # Pick best Logic candidate (prefer ScriptedLoadableModuleLogic subclass,
        # then prefer one with "process" or "run" methods)
        logic_class = None
        if logic_candidates:
            scored = []
            for cand in logic_candidates:
                score = 0
                # Strong preference for the Slicer-standard base class
                if "ScriptedLoadableModuleLogic" in cand["bases"]:
                    score += 100
                # Preference for classes with more methods (likely the main logic, not a helper)
                score += min(len(cand["methods"]), 20)
                for m in cand["methods"]:
                    if m.startswith(("process", "run", "compute", "execute")):
                        score += 10
                    if m.startswith("__init__"):
                        score += 1
                scored.append((score, cand))
            scored.sort(key=lambda x: x[0], reverse=True)
            logic_class = scored[0][1]

        # Pick best Widget candidate (prefer ScriptedLoadableModuleWidget subclass)
        widget_class = None
        if widget_candidates:
            scored_w = []
            for cand in widget_candidates:
                score = 0
                if "ScriptedLoadableModuleWidget" in cand["bases"]:
                    score += 100
                score += min(len(cand["methods"]), 20)
                if "setup" in cand["methods"]:
                    score += 50
                scored_w.append((score, cand))
            scored_w.sort(key=lambda x: x[0], reverse=True)
            widget_class = scored_w[0][1]

        # Find the entry point module (the main module file)
        entry_module = None
        if logic_class:
            entry_module = logic_class["file"]

        self.on_progress(
            1, "Scanning extension files",
            f"Logic class: {logic_class['class_name'] if logic_class else 'None'} "
            f"in {os.path.basename(entry_module) if entry_module else 'N/A'}"
            f", Widget class: {widget_class['class_name'] if widget_class else 'None'}"
            f", UI files: {len(ui_files)}"
        )

        return {
            "source_path": source_path,
            "py_files": py_files,
            "ui_files": ui_files,
            "file_inventory": file_inventory,
            "logic_class": logic_class,
            "widget_class": widget_class,
            "entry_module": entry_module,
        }

    @staticmethod
    def _ast_name(node) -> str:
        """Extract a readable name from an AST node."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{ExtensionCLIAnalyzer._ast_name(node.value)}.{node.attr}"
        if isinstance(node, ast.Constant):
            return str(node.value)
        return ""

    # ================================================================
    # .ui File Parsing (Qt Designer XML)
    # ================================================================

    def _parse_ui_file(self, ui_path: str) -> Optional[Dict]:
        """Parse a Qt .ui file and extract sections and buttons."""
        import xml.etree.ElementTree as ET
        try:
            tree = ET.parse(ui_path)
        except ET.ParseError:
            logger.debug("Failed to parse .ui file: %s", ui_path)
            return None

        root = tree.getroot()
        sections = []
        # Find all collapsible sections and their button children
        for widget in root.iter("widget"):
            widget_class = widget.get("class", "")
            if widget_class in ("ctkCollapsibleButton", "ctkCollapsibleGroupBox"):
                section_name = ""
                # Find the text property
                for prop in widget.findall("property"):
                    if prop.get("name") == "text":
                        string_el = prop.find("string")
                        if string_el is not None and string_el.text:
                            section_name = string_el.text.strip()
                if not section_name:
                    section_name = widget_class

                buttons = self._extract_buttons_from_widget(widget)
                if buttons:
                    sections.append({
                        "name": section_name,
                        "buttons": buttons,
                    })

        # If no collapsible sections found, look for top-level buttons
        if not sections:
            all_buttons = []
            for widget in root.iter("widget"):
                wc = widget.get("class", "")
                if wc in ("QPushButton", "ctkCheckablePushButton"):
                    btn = self._parse_button_widget(widget)
                    if btn:
                        all_buttons.append(btn)
            if all_buttons:
                sections.append({"name": "Buttons", "buttons": all_buttons})

        return {"sections": sections} if sections else None

    def _extract_buttons_from_widget(self, parent_widget) -> List[Dict]:
        """Extract buttons from a UI widget element, recursing into all nested layouts/frames."""
        buttons = []
        for child in parent_widget:
            if child.tag == "widget":
                wc = child.get("class", "")
                if wc in ("QPushButton", "ctkCheckablePushButton"):
                    btn = self._parse_button_widget(child)
                    if btn:
                        buttons.append(btn)
                else:
                    # Recurse into any non-button widget (QFrame, QGroupBox, etc.)
                    buttons.extend(self._extract_buttons_from_widget(child))
            elif child.tag == "layout":
                buttons.extend(self._extract_buttons_from_widget(child))
            elif child.tag == "item":
                buttons.extend(self._extract_buttons_from_widget(child))
        return buttons

    @staticmethod
    def _parse_button_widget(widget_el) -> Optional[Dict]:
        """Parse a single button widget element."""
        name = widget_el.get("name", "")
        label = ""
        for prop in widget_el.findall("property"):
            if prop.get("name") == "text":
                string_el = prop.find("string")
                if string_el is not None and string_el.text:
                    label = string_el.text.strip()
        if name:
            return {"widget_name": name, "label": label}
        return None

    def _extract_ui_widget_inventory(self, ui_files: List[str]) -> Dict[str, Dict]:
        """Extract a lightweight widget inventory from Qt Designer .ui files.

        This is intentionally generic: it records widget names, Qt classes, and
        simple string/list properties such as qMRMLNodeComboBox nodeTypes.  Later
        stages can use this as evidence for parameter-node bindings without the
        cookbook author knowing API details.
        """
        import xml.etree.ElementTree as ET

        widgets: Dict[str, Dict] = {}
        for ui_path in ui_files or []:
            try:
                root = ET.parse(ui_path).getroot()
            except Exception:
                continue
            for widget in root.iter("widget"):
                name = widget.get("name", "")
                if not name:
                    continue
                info = {
                    "class": widget.get("class", ""),
                    "properties": {},
                    "ui_file": os.path.basename(ui_path),
                }
                for prop in widget.findall("property"):
                    pname = prop.get("name", "")
                    if not pname:
                        continue
                    value = None
                    string_el = prop.find("string")
                    if string_el is not None:
                        value = string_el.text or ""
                    bool_el = prop.find("bool")
                    if bool_el is not None:
                        value = bool_el.text or ""
                    set_el = prop.find("set")
                    if set_el is not None:
                        value = set_el.text or ""
                    if value is not None:
                        info["properties"][pname] = value
                widgets[name] = info
        return widgets

    # ================================================================
    # Widget Signal Connection Extraction (AST)
    # ================================================================

    def _extract_widget_connections(self, widget_source: str) -> List[Dict]:
        """Extract button→handler→logic_method mappings from Widget class source."""
        try:
            tree = ast.parse(widget_source)
        except SyntaxError:
            return []

        connections = []
        # Find the setup() method
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "setup":
                        connections = self._find_clicked_connections(item, node)

        return connections

    def _find_clicked_connections(self, setup_node, class_node) -> List[Dict]:
        """Find .clicked.connect(self.XXX) patterns in setup() method."""
        connections = []
        # Build handler→logic_method map from all methods in the class
        handler_logic_map = {}
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                logic_calls = self._find_logic_calls_in_method(item)
                if logic_calls:
                    handler_logic_map[item.name] = logic_calls

        for stmt in ast.walk(setup_node):
            if not isinstance(stmt, ast.Call):
                continue
            func = stmt.func
            if not isinstance(func, ast.Attribute):
                continue
            if func.attr != "connect":
                continue

            button_name = ""
            handler_name = ""

            # Pattern 1: something.clicked.connect(self.handlerMethod)
            receiver = func.value
            if isinstance(receiver, ast.Attribute) and receiver.attr == "clicked":
                button_name = self._get_attribute_chain(receiver.value)
                if stmt.args:
                    arg = stmt.args[0]
                    if isinstance(arg, ast.Attribute) and isinstance(arg.value, ast.Name):
                        if arg.value.id == "self":
                            handler_name = arg.attr

            # Pattern 2: something.connect('clicked(bool)', self.handlerMethod)
            #            something.connect("clicked(bool)", self.handlerMethod)
            if not button_name and stmt.args:
                first_arg = stmt.args[0]
                if (isinstance(first_arg, ast.Constant)
                        and isinstance(first_arg.value, str)
                        and "clicked" in first_arg.value):
                    button_name = self._get_attribute_chain(func.value)
                    if len(stmt.args) > 1:
                        second_arg = stmt.args[1]
                        if isinstance(second_arg, ast.Attribute) and isinstance(second_arg.value, ast.Name):
                            if second_arg.value.id == "self":
                                handler_name = second_arg.attr

            if button_name and handler_name:
                logic_methods = handler_logic_map.get(handler_name, [])
                connections.append({
                    "button_widget_name": button_name,
                    "handler_method": handler_name,
                    "logic_methods": logic_methods,
                })

        return connections

    @staticmethod
    def _get_attribute_chain(node) -> str:
        """Build dotted name from chained attribute access (e.g. self.buttonName)."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            base = ExtensionCLIAnalyzer._get_attribute_chain(node.value)
            return f"{base}.{node.attr}" if base else node.attr
        return ""

    def _find_logic_calls_in_method(self, method_node) -> List[str]:
        """Find self.logic.XXX() calls in a method body."""
        calls = []
        for node in ast.walk(method_node):
            if isinstance(node, ast.Call):
                func = node.func
                if (isinstance(func, ast.Attribute)
                        and isinstance(func.value, ast.Attribute)):
                    if (func.value.attr == "logic"
                            and isinstance(func.value.value, ast.Name)
                            and func.value.value.id == "self"):
                        calls.append(func.attr)
        return calls

    # ================================================================
    # Stage 3: Logic Class Analysis (LLM)
    # ================================================================

    def _stage3_analyze_logic(self, scan_result: Dict) -> Dict:
        """Stage 3: Use LLM to analyze the Logic class methods in detail."""
        logic_info = scan_result["logic_class"]
        logic_file = logic_info["file"]
        class_name = logic_info["class_name"]

        self.on_progress(
            3, "Analyzing logic class",
            f"Reading {class_name} from {os.path.basename(logic_file)}..."
        )

        # Extract Logic class source
        logic_source = self._extract_class_source(logic_file, class_name)
        if not logic_source:
            raise RuntimeError(f"Could not extract source for {class_name} from {logic_file}")

        # Truncate if too large
        if len(logic_source) > _MAX_SOURCE_FOR_LLM:
            logic_source = logic_source[:_MAX_SOURCE_FOR_LLM] + "\n# ... [truncated for LLM analysis] ..."

        # Build prompt
        prompt = textwrap.dedent(f"""\
Analyze the following Slicer extension Logic class and return a JSON object with this exact structure:

{{
  "class_name": "{class_name}",
  "source_file": "{os.path.basename(logic_file)}",
  "methods": [
    {{
      "name": "method_name",
      "purpose": "one-line description",
      "parameters": [
        {{"name": "param_name", "type": "vtkMRML... or str or int etc", "required": true, "description": "what it is"}}
      ],
      "return_value": "description or null",
      "state_reads": ["self.field1", "self.field2"],
      "state_writes": ["self.field3"],
      "calls_addnode": true/false,
      "adds_output_to_scene": true/false,
      "side_effects": "description"
    }}
  ],
  "public_api_methods": ["method1", "method2"],
  "internal_methods": ["_helper1"],
  "pipeline_methods": ["method1", "method2"],
  "state_fields": [
    {{"name": "self.field1", "type": "description", "set_by": "method_name", "read_by": ["other_method"]}}
  ]
}}

Focus on public methods that perform meaningful operations (process, run, compute, execute).
Skip trivial getters/setters and Qt signal handlers.
For each method, be precise about:
- Whether it calls slicer.mrmlScene.AddNode() on its output parameters
- Whether it reads state from self.* that must be set by a prior method call
- Whether it writes state to self.* that future method calls depend on""")

        # Inject UI workflow context if available (skipped when cookbook-driven)
        if self._ui_workflow:
            prompt += textwrap.dedent(f"""\
Extracted UI Workflow (from .ui file and Widget class analysis):
```json
{json.dumps(self._ui_workflow, indent=2)}
```
Use this workflow to understand the intended user-facing sequence of operations.
Match method descriptions to their corresponding UI workflow steps.

""")

        # Inject cookbook context if available (cookbook-driven pipeline)
        if self._cookbook_def:
            cookbook_steps_text = "\n".join(
                f"{s.step_number}. {s.description}"
                for s in self._cookbook_def.steps
            )
            # Extract method hints from cookbook descriptions using fuzzy matching
            # against known method names (no extension-specific hardcoding).
            # NOTE: logic_info["methods"] is a list of *strings* from Stage 1 AST
            # scanning, not a list of dicts.
            ext_method_hints = []
            raw_methods = logic_info.get("methods", [])
            method_names_for_hint = [
                m if isinstance(m, str) else m.get("name", "")
                for m in raw_methods
            ]
            for s in self._cookbook_def.steps:
                hint = self._match_description_to_method(
                    s.description.lower(), method_names_for_hint
                )
                if hint and hint not in ext_method_hints:
                    ext_method_hints.append(hint)
            prompt += textwrap.dedent(f"""\

Cookbook workflow (ground truth — only methods referenced here should be analyzed):
{cookbook_steps_text}

Extension method hints from cookbook: {', '.join(ext_method_hints) if ext_method_hints else 'none identified'}
Focus your analysis on methods that match the cookbook workflow. Other methods can be listed briefly.

""")

        prompt += textwrap.dedent(f"""\
Logic class source:
```python
{logic_source}
```

Return ONLY the JSON object, no markdown fences or explanation.""")

        response = self._call_llm(prompt)
        analysis = self._parse_json_response(response)

        if not analysis or "methods" not in analysis:
            raise RuntimeError(
                f"LLM analysis returned invalid structure. Response: {response[:500]}"
            )

        self.on_progress(
            3, "Analyzing logic class",
            f"Analyzed {len(analysis.get('methods', []))} methods"
        )

        analysis["_logic_source"] = logic_source
        analysis["_logic_file"] = logic_file
        analysis["_cookbook_method_hints"] = ext_method_hints if self._cookbook_def else []
        return analysis

    def _verify_signatures_ast(self, logic_analysis: Dict, scan_result: Dict) -> None:
        """Cross-check LLM-extracted method signatures against actual AST."""
        logic_file = logic_analysis.get("_logic_file", "")
        methods = logic_analysis.get("methods", [])
        corrections = 0

        for method in methods:
            mname = method.get("name", "")
            method_source = self._extract_method_source(logic_file, mname)
            if not method_source:
                continue
            method_source = textwrap.dedent(method_source)

            try:
                tree = ast.parse(method_source)
            except SyntaxError:
                continue

            # Find the FunctionDef
            func_def = None
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == mname:
                        func_def = node
                        break
            if not func_def:
                continue

            # Extract actual params from AST
            ast_params = []
            args = func_def.args
            all_args = args.args[:]
            # Skip 'self' if present
            if all_args and getattr(all_args[0], 'arg', None) == 'self':
                all_args = all_args[1:]

            defaults = args.defaults[:]
            # Pad defaults with None for params without defaults
            padded_defaults = [None] * (len(all_args) - len(defaults)) + defaults

            for arg_obj, default_val in zip(all_args, padded_defaults):
                annotation = ""
                if arg_obj.annotation:
                    if isinstance(arg_obj.annotation, ast.Name):
                        annotation = arg_obj.annotation.id
                    elif isinstance(arg_obj.annotation, ast.Attribute):
                        annotation = self._ast_name(arg_obj.annotation) or ""
                    elif isinstance(arg_obj.annotation, ast.Subscript):
                        annotation = self._ast_name(arg_obj.annotation.value) or ""
                default_str = None
                if default_val is not None:
                    try:
                        default_str = ast.unparse(default_val)
                    except Exception:
                        default_str = "..."
                ast_params.append({
                    "name": arg_obj.arg,
                    "type": annotation,
                    "default": default_str,
                })

            # Compare with LLM params
            llm_params = method.get("parameters", [])
            llm_param_names = [p.get("name", "") for p in llm_params]
            ast_param_names = [p["name"] for p in ast_params]

            if llm_param_names != ast_param_names:
                logger.info(
                    "Signature mismatch for %s: LLM=%s AST=%s — correcting",
                    mname, llm_param_names, ast_param_names,
                )
                # Rebuild parameters from AST, preserving LLM descriptions where names match
                llm_desc_map = {p.get("name", ""): p for p in llm_params}
                new_params = []
                for ap in ast_params:
                    if ap["name"] in llm_desc_map:
                        # Keep LLM description, update name/type
                        entry = dict(llm_desc_map[ap["name"]])
                        entry["name"] = ap["name"]
                        if ap["type"]:
                            entry["type"] = ap["type"]
                        if ap["default"] is not None:
                            entry["required"] = False
                            entry["default"] = _parse_default_value(ap["default"])
                        new_params.append(entry)
                    else:
                        # New param from AST not in LLM output
                        entry = {
                            "name": ap["name"],
                            "type": ap["type"] or "Any",
                            "required": ap["default"] is None,
                            "description": "",
                        }
                        if ap["default"] is not None:
                            entry["default"] = _parse_default_value(ap["default"])
                        new_params.append(entry)

                method["parameters"] = new_params
                corrections += 1

        if corrections:
            self.on_progress(
                "3.5", "Verifying signatures",
                f"Corrected {corrections} method signature(s) via AST"
            )

    # ================================================================
    # Stage 4: Cookbook Stage Map — LLM Decomposition
    # ================================================================

    def _collect_step_evidence(
        self, step_description: str, method_names: List[str], extension_name: str = ""
    ) -> Dict[str, Any]:
        """Collect deterministic classification evidence for one cookbook step."""
        desc = _text_or_empty(step_description)
        desc_lower = desc.lower()
        evidence = {
            "logic_method_candidates": [],
            "widget_candidates": [],
            "ui_control_candidates": [],
            "slicer_core_candidates": [],
            "interaction_candidates": [],
            "choice_candidates": [],
        }

        matched_method = self._match_description_to_method(desc_lower, method_names)
        if matched_method:
            evidence["logic_method_candidates"].append({
                "method": matched_method,
                "reason": "method name/purpose token overlap",
            })

        for conn in getattr(self, "_widget_connections", []) or []:
            btn_name = _text_or_empty(conn.get("button_widget_name"))
            btn_text = btn_name.lower().replace("_", " ").replace(".", " ")
            btn_words = [w for w in btn_text.split() if len(w) > 3]
            if not btn_words:
                continue
            hits = [w for w in btn_words if w in desc_lower]
            if len(hits) >= 2 or (len(btn_words) == 1 and hits):
                evidence["widget_candidates"].append({
                    "button_widget_name": btn_name,
                    "logic_methods": conn.get("logic_methods", []),
                    "matched_words": hits,
                })

        choice_patterns = {
            "left/right": ("left" in desc_lower and "right" in desc_lower),
            "which side": "which side" in desc_lower,
            "which type": "which type" in desc_lower or "mandibulectomy type" in desc_lower,
            "select scene node": any(
                p in desc_lower for p in (
                    "select the", "choose the", "current scalar volume",
                    "select mandibular segmentation", "select fibula segmentation",
                )
            ),
            "number requested": any(p in desc_lower for p in ("how many", "number of")),
        }
        for name, present in choice_patterns.items():
            if present:
                evidence["choice_candidates"].append(name)

        interaction_patterns = [
            ("markup_placement", "curve", "vtkMRMLMarkupsCurveNode", ("draw", "curve")),
            ("markup_placement", "plane", "vtkMRMLMarkupsPlaneNode", ("plane", "place")),
            ("markup_placement", "line", "vtkMRMLMarkupsLineNode", ("line", "draw")),
            ("view_adjustment", "generic", "vtkMRMLCrosshairNode", ("crosshair", "slice intersection", "drag")),
        ]
        for kind, interaction_type, node_class, words in interaction_patterns:
            if any(w in desc_lower for w in words) and any(
                v in desc_lower for v in ("manual", "manually", "draw", "drag", "click", "place", "position", "adjust")
            ):
                evidence["interaction_candidates"].append({
                    "interaction_kind": kind,
                    "interaction_type": interaction_type,
                    "node_class": node_class,
                    "matched_terms": [w for w in words if w in desc_lower],
                })

        slicer_concepts = [
            ("layout_slice_view", ("layout", "conventional", "slice visibility", "red view", "fov", "spacing")),
            ("module_switching", ("open the markups module", "markups module", "module")),
            ("markups_display", ("display panel", "advanced panel", "view 1", "markups")),
            ("crosshair", ("crosshair", "slice intersection", "enable interaction")),
            ("subject_hierarchy", ("subject hierarchy", "folder")),
            ("node_display", ("display node", "visibility", "view node")),
        ]
        for category, terms in slicer_concepts:
            matched = [t for t in terms if t in desc_lower]
            if matched:
                evidence["slicer_core_candidates"].append({
                    "category": category,
                    "matched_terms": matched,
                })

        extension_tokens = []
        if extension_name:
            extension_tokens.append(extension_name.lower())
            parts = _re.sub(r'([a-z])([A-Z])', r'\1 \2', extension_name).split()
            acronym = "".join(p[0].lower() for p in parts if p)
            if len(acronym) >= 2:
                extension_tokens.append(acronym)
        for token in extension_tokens:
            if token and token in desc_lower:
                evidence["ui_control_candidates"].append({
                    "control": token,
                    "reason": "extension-specific name/acronym appears in step",
                })

        return evidence

    @staticmethod
    def _evidence_has(evidence: Dict[str, Any], key: str) -> bool:
        value = evidence.get(key, [])
        return isinstance(value, list) and bool(value)

    def _infer_interaction_kind_from_evidence(self, evidence: Dict[str, Any], node_class: str = "") -> str:
        for item in evidence.get("interaction_candidates", []) or []:
            kind = item.get("interaction_kind")
            if kind:
                return kind
        if self._is_markup_node_class(node_class):
            return "markup_placement"
        if node_class:
            return "view_adjustment"
        return "none"

    def _infer_slicer_op_category(self, text: str, evidence: Optional[Dict[str, Any]] = None) -> Optional[str]:
        desc = _text_or_empty(text).lower()
        if evidence:
            cats = evidence.get("slicer_core_candidates", []) or []
            if cats and isinstance(cats[0], dict) and cats[0].get("category"):
                return cats[0]["category"]
        if any(t in desc for t in ("layout", "red view", "slice visibility", "fov", "spacing")):
            return "layout_slice_view"
        if "crosshair" in desc or "slice intersection" in desc:
            return "crosshair"
        if "markups module" in desc or "open the markups" in desc:
            return "module_switching"
        if "display panel" in desc or "advanced panel" in desc:
            return "markups_display"
        if "subject hierarchy" in desc or "folder" in desc:
            return "subject_hierarchy"
        if "display" in desc or "visibility" in desc:
            return "node_display"
        return None

    def _stage4_cookbook_decomposition(
        self, cookbook_def, logic_analysis: Dict
    ) -> Dict:
        """
        Use LLM to decompose each cookbook step into sub-operations.

        Each step is classified into one or more of:
        - extension_op: Calls a method on the extension's Logic class.
        - slicer_op: Uses Slicer core API (layout changes, view toggles, etc.).
        - user_interaction: Requires the user to draw/click in the 3D view.
        - user_choice: A chat-based decision point.

        Falls back to keyword heuristics (_cookbook_build_stage_map) on LLM failure.
        """
        self.on_progress(
            4, "Cookbook Stage Map",
            "Decomposing cookbook steps via LLM..."
        )

        # Build cookbook steps text
        steps_text = "\n".join(
            f"Step {s.step_number}: {s.description}"
            for s in cookbook_def.steps
        )

        # Build method catalog from logic analysis
        methods = logic_analysis.get("methods", [])
        method_catalog = []
        for m in methods:
            mname = m.get("name", "")
            params = [
                f"{p.get('name', '')}: {p.get('type', '?')}"
                for p in m.get("parameters", [])
                if p.get("name") != "self"
            ]
            state_reads = m.get("state_reads", [])
            state_writes = m.get("state_writes", [])
            method_catalog.append({
                "name": mname,
                "purpose": m.get("purpose", ""),
                "parameters": params,
                "state_reads": state_reads,
                "state_writes": state_writes,
                "calls_addnode": m.get("calls_addnode", False),
                "adds_output_to_scene": m.get("adds_output_to_scene", False),
            })

        method_names = [m["name"] for m in methods]
        evidence_by_step = {
            s.step_number: self._collect_step_evidence(
                s.description, method_names, cookbook_def.extension_name
            )
            for s in cookbook_def.steps
        }

        # Build cookbook method hints section (AST-verified, not subject to truncation)
        cookbook_method_hints = logic_analysis.get("_cookbook_method_hints", [])
        if cookbook_method_hints:
            _cookbook_hints_section = (
                "\n        ## Cookbook Method Hints (AST-verified)\n"
                "        These methods were identified by matching cookbook step descriptions\n"
                "        against the full AST method list (not subject to truncation).\n"
                "        If a step's description matches one of these, classify as extension_op\n"
                "        with the hinted method:\n"
                f"        {json.dumps(cookbook_method_hints, indent=2)}\n"
            )
        else:
            _cookbook_hints_section = ""

        prompt = textwrap.dedent(f"""\
        You are analyzing a 3D Slicer extension's cookbook workflow and must decompose
        each step into atomic sub-operations.

        ## Cookbook Steps
        {steps_text}

        ## Available Logic Methods
        {json.dumps(method_catalog, indent=2)}
{_cookbook_hints_section}

        ## Deterministic Evidence Candidates
        These candidates were extracted from the extension source, UI/widget
        connections, and known Slicer-core concepts before this LLM call.
        Prefer high-confidence evidence over guessing. If no extension evidence
        or Slicer-core evidence supports an operation, use `unknown_op` instead
        of guessing.
        {json.dumps(evidence_by_step, indent=2)}

        ## Task
        For EACH cookbook step, decompose it into one or more sub-operations.
        Each sub-operation must have one of these types:

        1. **extension_op** — The operation calls a method on THIS extension's own
           Logic class. The code to generate it comes directly from the extension's
           source code — NO knowledge-base search is needed.
           Specify `extension_method_hint` matching one of:
           {json.dumps(method_names[:40])}
           Examples: calling addMandibularCurve(), generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible(),
           or any other method defined in the extension's Logic/Widget class.

        2. **slicer_op** — The operation uses Slicer CORE APIs that are NOT part of
           this extension. Code generation requires searching the Slicer knowledge base
           for the correct API calls (layout changes, view toggles, module switching,
           node selection from Slicer's core modules).
           Specify `slicer_api_keywords` (e.g., ["layout", "red view", "set layout"]).
           Examples: slicer.app.layoutManager().setLayout(),
           slicer.util.getNode(), switching to Markups module, toggling slice visibility.
           IMPORTANT: Checkbox ticks, dropdown selections, or button clicks in THIS
           extension's own UI panel are NOT slicer_op — they are either extension_op
           (if a Logic method exists) or user_choice (if the agent cannot determine
           the value, e.g. left vs. right).

        3. **user_interaction** — The user must physically interact with the 3D
           visualization window — drawing curves, positioning planes, placing
           fiducials, dragging objects in the viewport.
           Specify `interaction_type` (one of: "curve", "plane", "line", "fiducial"),
           `node_class` (e.g., "vtkMRMLMarkupsCurveNode"), and
           `placement_instructions` (what to tell the user to do).
           Examples: "Draw a curve along the mandible in the Red slice view",
           "Position the cutting plane by dragging in 3D view".

        4. **user_choice** — The agent CANNOT determine the answer on its own and
           must ask the user via the chat box. This applies whenever a parameter
           value depends on patient-specific or case-specific context that is not
           available in the scene.
           Specify `question` (the question to ask), `choices` (list of
           {{"label": "...", "value": "..."}} objects), `parameter_name`
           (snake_case identifier for the choice), and `default_value` (optional).
           Examples:
           - "Tick Right side leg checkbox" → user_choice (left/right depends on patient)
           - "Select mandibulectomy type" → user_choice (clinical decision)
           - "Choose segmentation" → user_choice if multiple options exist and the
             agent cannot determine the correct one from context.
           Anti-patterns (NOT user_choice):
           - If the agent CAN determine the value programmatically from the scene,
             it is extension_op or slicer_op, not user_choice.
           - A step like "click the Create Models button" is extension_op (there is
             a Logic method) or slicer_op (Slicer core API), NOT user_choice.

        5. **unknown_op** — The operation is required by the cookbook but cannot
           be proven as extension_op or slicer_op from the evidence. Do NOT use
           slicer_op as a catch-all fallback.

        ## Output Format
        Return a JSON object with this structure:
        {{
          "steps": [
            {{
              "step_number": 1,
              "sub_operations": [
                {{
                  "op_type": "extension_op" | "slicer_op" | "user_interaction" | "user_choice" | "unknown_op",
                  "description": "what this sub-operation does",
                  "extension_method_hint": "methodName" or null,
                  "slicer_api_keywords": ["keyword1"] or [],
                  "interaction_type": "curve" | "plane" | "line" | "fiducial" or null,
                  "node_class": "vtkMRML..." or null,
                  "placement_instructions": "..." or null,
                  "min_control_points": 0,
                  "evidence_type": "logic_method" | "widget_connection" | "ui_control" | "parameter_node" | "slicer_core" | "viewport_action" | "user_context" | "unknown",
                  "evidence_id": "method/widget/concept id" or null,
                  "confidence": "high" | "medium" | "low",
                  "interaction_kind": "markup_placement" | "view_adjustment" | "none",
                  "slicer_op_category": "layout_slice_view" | "module_switching" | "markups_display" | "crosshair" | "subject_hierarchy" | "node_display" | "scene_node_lookup" | "cli_module" | "generic_slicer_api" or null,
                  "question": "..." or null,
                  "choices": [{{"label": "...", "value": "..."}}] or [],
                  "parameter_name": "..." or null,
                  "default_value": "..." or null,
                  "is_optional": false
                }}
              ]
            }}
          ]
        }}

        ## Classification Rules (CRITICAL — read carefully)
        - A single cookbook step may have MULTIPLE sub-operations (e.g., setup + user interaction).
        - Every step must have at least one sub-operation.
        - **Ask yourself for each step**: "Can the agent determine ALL parameter values
          programmatically from the scene, or does it need information only the user knows?"
          If it needs user-only information → user_choice.
        - **Ask yourself**: "Does the code for this step come from THIS extension's source,
          or from Slicer's core API?" If from this extension → extension_op. If from
          Slicer core → slicer_op.
        - **Ask yourself**: "Does the user need to physically touch the 3D view?" If yes →
          user_interaction.
        - **Checkbox/toggle steps**: If the checkbox controls patient-specific or
          case-specific behavior (e.g., left/right, type selection) → user_choice.
          If the checkbox triggers a known extension method → extension_op.
          If the checkbox sets an extension parameter node value (no Logic method call,
          just UI state) → extension_op with extension_method_hint set to the parameter name.
          Extension UI checkboxes are NEVER slicer_op.
        - **Dropdown selections**: If selecting from this extension's outputs (e.g.,
          picking a segmentation it created) → extension_op (use the Logic class).
          If selecting from Slicer core nodes or modules → slicer_op.
          If the agent cannot determine WHICH option to select → user_choice.
          IMPORTANT: "Select the [X] volume/segmentation/node" is user_choice when the
          agent cannot programmatically determine WHICH scene node is X. Do NOT guess
          based on node names (e.g., "maybe there's a volume named 'Mandible'").
          If the step says "select the Mandible Volume" and the agent has no reliable
          way to know which volume is the mandible, it must ask the user → user_choice.
        - **Button clicks**: If a step says "Click [X] button" where X is a button in
          THIS extension's UI panel, classify as extension_op even if the exact method
          name is not in the catalog. Extension buttons call extension Logic methods.
          Only classify as slicer_op when the step explicitly references Slicer core
          features (layout changes, module switching, slicer.app, slicer.util).
        - **Slicer core UI operations** (CRITICAL — these are slicer_op, NOT extension_op):
          The following operations use Slicer's core API, not the extension's Logic class.
          Even if described in the context of using the extension, they are slicer_op:
          • "Slice visibility in 3D view" → slicer_op (use the verified Slicer slice-view API)
          • "Slice intersection visibility" / "Crosshair" → slicer_op (vtkMRMLCrosshairNode)
          • "FOV/Spacing match 2D" → slicer_op (vtkMRMLSliceNode.SetSliceSpacingMode)
          • "Open [X] module" / "Switch to [X] module" → slicer_op (slicer.util.selectModule)
          • Layout changes (Conventional, Four-Up, etc.) → slicer_op (layoutManager.setLayout)
          • "Display" panel / "View" settings on markup nodes → slicer_op (display node API)
          Extension UI toggles (checkboxes in the extension's own panel) are still
          extension_op, but Slicer core view/display/interaction toggles are slicer_op.
          Key test: "Does this use slicer.app, slicer.util, or a vtkMRML*Node method?"
          If yes → slicer_op. "Does this set an extension parameter node value?" If yes → extension_op.
        - **Evidence requirement**: extension_op must cite extension evidence
          (logic_method/widget_connection/ui_control/parameter_node). slicer_op must
          cite slicer_core evidence and include `slicer_op_category`.
          If evidence is weak or absent, return unknown_op with confidence "low".
        - Mark optional/experimental steps with is_optional: true.
        - Return ONLY the JSON object, no markdown fences or explanation.""")

        try:
            response = self._call_llm(prompt)
            decomposition = self._parse_json_response(response)
            if decomposition is None:
                logger.warning(
                    "Stage 4: LLM response could not be parsed as JSON. "
                    "Response starts with: %s... Falling back to keyword heuristics.",
                    response[:200] if response else "(empty)",
                )
        except Exception as e:
            logger.warning(
                "Stage 4 LLM decomposition failed (%s), falling back to heuristics", e
            )
            decomposition = None

        # Validate LLM output structure
        if (
            not decomposition
            or not isinstance(decomposition.get("steps"), list)
            or len(decomposition["steps"]) != len(cookbook_def.steps)
        ):
            logger.warning(
                "Stage 4 LLM decomposition returned invalid structure "
                "(got %d steps, expected %d), falling back to keyword heuristics",
                len(decomposition.get("steps", [])) if decomposition and isinstance(decomposition, dict) else 0,
                len(cookbook_def.steps),
            )
            return self._cookbook_build_stage_map(cookbook_def, logic_analysis)

        # Convert LLM decomposition into stage_map format
        return self._build_stage_map_from_decomposition(
            decomposition, cookbook_def, logic_analysis
        )

    def _build_stage_map_from_decomposition(
        self, decomposition: Dict, cookbook_def, logic_analysis: Dict
    ) -> Dict:
        """Convert LLM decomposition output into the stage_map dict format."""
        raw_methods = logic_analysis.get("methods", [])
        if isinstance(raw_methods, list):
            all_methods = {}
            for m in raw_methods:
                if isinstance(m, dict) and m.get("name"):
                    all_methods[m["name"]] = m
        else:
            all_methods = raw_methods if isinstance(raw_methods, dict) else {}

        stages = []
        llm_steps = {}
        for raw_step in decomposition.get("steps", []):
            if not isinstance(raw_step, dict):
                continue
            step_number = _int_or_none(raw_step.get("step_number"))
            if step_number is not None:
                llm_steps[step_number] = raw_step

        for cb_step in cookbook_def.steps:
            step_num = cb_step.step_number
            step_id = f"cb_step_{step_num}"
            llm_step = llm_steps.get(step_num, {})
            llm_sub_ops = llm_step.get("sub_operations", [])
            method_names = list(all_methods.keys())
            step_evidence = self._collect_step_evidence(
                cb_step.description, method_names, cookbook_def.extension_name
            )

            # If LLM returned nothing for this step, fall back to heuristic
            if not llm_sub_ops:
                llm_sub_ops = [{
                    "op_type": "extension_op",
                    "description": cb_step.description[:200],
                    "extension_method_hint": None,
                    "slicer_api_keywords": [],
                    "interaction_type": None,
                    "node_class": None,
                    "placement_instructions": None,
                }]

            # Normalize sub-operations: ensure required fields
            sub_ops = []
            for so in llm_sub_ops:
                if not isinstance(so, dict):
                    so = {"description": so}
                op_type = _optional_text(so.get("op_type")) or "extension_op"
                if op_type not in ("extension_op", "slicer_op", "user_interaction", "user_choice", "unknown_op"):
                    op_type = "extension_op"
                description = _text_or_empty(
                    so.get("description", cb_step.description[:200])
                )
                method_hint = _optional_text(so.get("extension_method_hint"))
                node_class = _optional_text(so.get("node_class"))
                evidence_type = _optional_text(so.get("evidence_type")) or "unknown"
                evidence_id = _optional_text(so.get("evidence_id"))
                confidence = (_optional_text(so.get("confidence")) or "medium").lower()
                if confidence not in ("high", "medium", "low"):
                    confidence = "medium"
                interaction_kind = (
                    _optional_text(so.get("interaction_kind"))
                    or self._infer_interaction_kind_from_evidence(step_evidence, node_class or "")
                )
                slicer_op_category = (
                    _optional_text(so.get("slicer_op_category"))
                    or self._infer_slicer_op_category(description, step_evidence)
                )
                normalized = {
                    "op_type": op_type,
                    "description": description,
                    "extension_method_hint": method_hint,
                    "slicer_api_keywords": _text_list(so.get("slicer_api_keywords", [])),
                    "interaction_type": _optional_text(so.get("interaction_type")),
                    "node_class": node_class,
                    "placement_instructions": _optional_text(so.get("placement_instructions")),
                    "min_control_points": so.get("min_control_points", 0),
                    "evidence_type": evidence_type,
                    "evidence_id": evidence_id,
                    "confidence": confidence,
                    "interaction_kind": interaction_kind,
                    "slicer_op_category": slicer_op_category,
                    "is_optional": so.get("is_optional", False),
                }
                # user_choice-specific fields
                if op_type == "user_choice":
                    normalized["question"] = _text_or_empty(so.get("question", cb_step.description))
                    choices = so.get("choices", [])
                    normalized["choices"] = choices if isinstance(choices, list) else []
                    normalized["parameter_name"] = (
                        _optional_text(so.get("parameter_name")) or f"choice_step_{step_num}"
                    )
                    normalized["default_value"] = so.get("default_value")
                sub_ops.append(normalized)

            # Resolve extension_method_hint to actual method names
            for so in sub_ops:
                hint = so.get("extension_method_hint")
                if hint and hint not in all_methods:
                    matched = self._match_method_name(hint, method_names)
                    if matched:
                        so["extension_method_hint"] = matched

            # Deterministic evidence validation. The LLM may propose op_type,
            # but source/UI/Slicer-core evidence decides whether it can stand.
            for so in sub_ops:
                desc_lower = _text_or_empty(so.get("description")).lower()
                if (
                    so["op_type"] not in ("user_choice", "user_interaction")
                    and self._evidence_has(step_evidence, "choice_candidates")
                    and not self._evidence_has(step_evidence, "widget_candidates")
                    and not so.get("extension_method_hint")
                ):
                    so["op_type"] = "user_choice"
                    so["question"] = so.get("question") or so.get("description", cb_step.description)
                    so["choices"] = so.get("choices", [])
                    so["parameter_name"] = so.get("parameter_name") or f"choice_step_{step_num}"
                    so["slicer_api_keywords"] = []
                    so["evidence_type"] = "user_context"
                    so["confidence"] = "high"
                elif (
                    so["op_type"] == "unknown_op"
                    and self._evidence_has(step_evidence, "interaction_candidates")
                ):
                    interaction = step_evidence["interaction_candidates"][0]
                    so["op_type"] = "user_interaction"
                    so["interaction_kind"] = interaction.get("interaction_kind", "markup_placement")
                    so["interaction_type"] = interaction.get("interaction_type")
                    so["node_class"] = interaction.get("node_class")
                    so["placement_instructions"] = so.get("placement_instructions") or so.get("description")
                    so["evidence_type"] = "viewport_action"
                    so["confidence"] = "high"
                elif so["op_type"] == "unknown_op" and self._evidence_has(
                    step_evidence, "logic_method_candidates"
                ):
                    method = step_evidence["logic_method_candidates"][0].get("method")
                    so["op_type"] = "extension_op"
                    so["extension_method_hint"] = method
                    so["evidence_type"] = "logic_method"
                    so["evidence_id"] = method
                    so["confidence"] = "high"
                elif so["op_type"] == "unknown_op" and self._evidence_has(
                    step_evidence, "slicer_core_candidates"
                ):
                    category = self._infer_slicer_op_category(so.get("description", ""), step_evidence)
                    if category:
                        so["op_type"] = "slicer_op"
                        so["slicer_op_category"] = category
                        so["evidence_type"] = "slicer_core"
                        so["evidence_id"] = category
                        so["confidence"] = "medium"

                if so["op_type"] == "extension_op":
                    if so.get("extension_method_hint"):
                        so["evidence_type"] = "logic_method"
                        so["evidence_id"] = so["extension_method_hint"]
                        so["confidence"] = "high"
                    elif self._evidence_has(step_evidence, "widget_candidates"):
                        widget = step_evidence["widget_candidates"][0]
                        logic_methods = widget.get("logic_methods") or []
                        if logic_methods:
                            so["extension_method_hint"] = logic_methods[0]
                        so["evidence_type"] = "widget_connection"
                        so["evidence_id"] = widget.get("button_widget_name")
                        so["confidence"] = "high"
                    elif self._evidence_has(step_evidence, "ui_control_candidates"):
                        so["evidence_type"] = "ui_control"
                        so["evidence_id"] = step_evidence["ui_control_candidates"][0].get("control")
                        so["confidence"] = "medium"
                    else:
                        matched = self._match_description_to_method(desc_lower, method_names)
                        if matched:
                            so["extension_method_hint"] = matched
                            so["evidence_type"] = "logic_method"
                            so["evidence_id"] = matched
                            so["confidence"] = "high"
                        else:
                            so["op_type"] = "unknown_op"
                            so["evidence_type"] = "unknown"
                            so["confidence"] = "low"
                elif so["op_type"] == "slicer_op":
                    category = so.get("slicer_op_category") or self._infer_slicer_op_category(
                        so.get("description", ""), step_evidence
                    )
                    if self._evidence_has(step_evidence, "slicer_core_candidates") and category:
                        so["slicer_op_category"] = category
                        so["evidence_type"] = "slicer_core"
                        so["evidence_id"] = category
                        if so.get("confidence") == "low":
                            so["confidence"] = "medium"
                    else:
                        so["op_type"] = "unknown_op"
                        so["slicer_api_keywords"] = []
                        so["evidence_type"] = "unknown"
                        so["confidence"] = "low"
                elif so["op_type"] == "user_interaction":
                    so["evidence_type"] = "viewport_action"
                    so["interaction_kind"] = (
                        so.get("interaction_kind")
                        or self._infer_interaction_kind_from_evidence(
                            step_evidence, so.get("node_class", "")
                        )
                    )
                    if so["interaction_kind"] == "view_adjustment" and not so.get("node_class"):
                        so["node_class"] = "vtkMRMLCrosshairNode"
                elif so["op_type"] == "user_choice":
                    so["evidence_type"] = "user_context"
                elif so["op_type"] == "unknown_op":
                    so["confidence"] = "low"

            # ── Reclassify extension-specific slicer_ops → extension_op ──
            # slicer_ops that reference the extension's own resources (custom
            # layouts, extension-defined node types, extension module names)
            # cannot be resolved via Slicer KB search. Reclassify them as
            # extension_op so they use the extension source for code generation.
            ext_name = _text_or_empty(cookbook_def.extension_name)
            ext_name_lower = ext_name.lower() if ext_name else ""
            # Common patterns indicating extension-specific knowledge:
            # - The extension's own name in layout/view descriptions
            # - Custom layout IDs registered by the extension
            # - Extension module names not in Slicer core
            _extension_specific_indicators = set()
            if ext_name_lower:
                _extension_specific_indicators.add(ext_name_lower)
                # Also add shortened forms (e.g., "brp" for BoneReconstructionPlanner)
                parts = _re.sub(r'([a-z])([A-Z])', r'\1 \2', ext_name).split()
                if parts:
                    acronym = "".join(p[0].lower() for p in parts if p)
                    if len(acronym) >= 2:
                        _extension_specific_indicators.add(acronym)

            for so in sub_ops:
                if so["op_type"] != "slicer_op":
                    continue
                desc_lower = _text_or_empty(so.get("description")).lower()
                keywords_lower = [
                    _text_or_empty(k).lower()
                    for k in _text_list(so.get("slicer_api_keywords", []))
                ]
                combined_text = desc_lower + " " + " ".join(keywords_lower)

                # Check if the description/keywords reference the extension itself
                is_extension_specific = False
                for indicator in _extension_specific_indicators:
                    if indicator in combined_text:
                        is_extension_specific = True
                        break

                if is_extension_specific:
                    # Try to find a matching extension method
                    matched_method = self._match_description_to_method(desc_lower, method_names)
                    so["op_type"] = "extension_op"
                    so["extension_method_hint"] = matched_method
                    so["slicer_api_keywords"] = []
                    so["evidence_type"] = "ui_control"
                    so["evidence_id"] = ext_name
                    so["confidence"] = "medium"
                    logger.info(
                        "[Stage 4] Reclassified step %d slicer_op → extension_op "
                        "(extension-specific: '%s'): %s",
                        step_num, ext_name, desc_lower[:60],
                    )

            # ── Widget connection verification: slicer_ops matching extension buttons → extension_op ──
            if self._widget_connections:
                for so in sub_ops:
                    if so["op_type"] != "slicer_op":
                        continue
                    desc_lower = _text_or_empty(so.get("description")).lower()
                    for conn in self._widget_connections:
                        btn_name = _text_or_empty(conn.get("button_widget_name")).lower()
                        logic_methods = conn.get("logic_methods", [])
                        # Extract significant words from button name for matching
                        btn_words = [w for w in btn_name.replace("_", " ").replace(".", " ").split() if len(w) > 3]
                        if not btn_words:
                            continue
                        match_count = sum(1 for w in btn_words if w in desc_lower)
                        if match_count >= 2 or (len(btn_words) == 1 and match_count == 1):
                            so["op_type"] = "extension_op"
                            if logic_methods:
                                so["extension_method_hint"] = logic_methods[0]
                            so["slicer_api_keywords"] = []
                            so["evidence_type"] = "widget_connection"
                            so["evidence_id"] = conn.get("button_widget_name", "")
                            so["confidence"] = "high"
                            logger.info(
                                "[Stage 4] Reclassified step %d slicer_op → extension_op "
                                "(widget button '%s' match): %s",
                                step_num, conn.get("button_widget_name", ""), desc_lower[:60],
                            )
                            break

            # ── "Select/choose/set" without method hint → user_choice ──
            for so in sub_ops:
                if so["op_type"] != "slicer_op":
                    continue
                desc = _text_or_empty(so.get("description")).lower()
                has_hint = bool(so.get("extension_method_hint"))
                if not has_hint and any(
                    desc.startswith(w) for w in ("select ", "choose ", "set the ")
                ):
                    so["op_type"] = "user_choice"
                    so["question"] = so.get("description", "")
                    so["slicer_api_keywords"] = []
                    so["parameter_name"] = f"choice_step_{step_num}"
                    so["evidence_type"] = "user_context"
                    so["confidence"] = "high"
                    logger.info(
                        "[Stage 4] Reclassified step %d slicer_op → user_choice "
                        "(selection without method hint): %s",
                        step_num, desc[:60],
                    )

            # ── "Tick/enable/toggle" extension UI controls without method hint → extension_op ──
            # Extension UI checkboxes/toggles set extension parameter node values,
            # not Slicer core API. If there's no Logic method, it's still extension_op
            # because the parameter names are extension-specific.
            for so in sub_ops:
                if so["op_type"] != "slicer_op":
                    continue
                desc = _text_or_empty(so.get("description")).lower()
                has_hint = bool(so.get("extension_method_hint"))
                if not has_hint and any(
                    desc.startswith(w) for w in ("tick ", "toggle ", "enable ", "check ", "uncheck ")
                ):
                    so["op_type"] = "extension_op"
                    so["slicer_api_keywords"] = []
                    so["evidence_type"] = "ui_control"
                    so["evidence_id"] = "extension_ui_toggle"
                    so["confidence"] = "medium"
                    logger.info(
                        "[Stage 4] Reclassified step %d slicer_op → extension_op "
                        "(extension UI control without method hint): %s",
                        step_num, desc[:60],
                    )

            # ── Reclassify extension_op/unknown_op → slicer_op when no method hint and matches Slicer core ──
            # Sub-ops classified as extension_op (or downgraded to unknown_op due to
            # no matching method) that describe Slicer core UI operations should be
            # slicer_op so Stage 5T / Stage 7 can generate proper Slicer API code.
            _SLICER_CORE_PATTERNS = {
                "layout_slice_view": [
                    "layout", "conventional", "four-up", "slice view",
                    "fov", "spacing match", "field of view",
                ],
                "module_switching": [
                    "module", "switch to", "open module",
                    "select module", "markups module",
                ],
                "crosshair": [
                    "crosshair", "slice intersection",
                    "intersection visibility", "enable interaction",
                ],
                "node_display": [
                    "slice visibility", "slice visible",
                    "set slice visible", "toggle slice",
                ],
                "markups_display": [
                    "display view", "view node", "display node",
                    "set view", "view 1", "advanced panel",
                ],
            }
            for so in sub_ops:
                if so["op_type"] not in ("extension_op", "unknown_op"):
                    continue
                if so.get("extension_method_hint"):
                    continue
                desc_lower = _text_or_empty(so.get("description")).lower()
                # Skip if description references the extension name
                is_extension_specific = False
                for indicator in _extension_specific_indicators:
                    if indicator in desc_lower:
                        is_extension_specific = True
                        break
                if is_extension_specific:
                    continue
                category = so.get("slicer_op_category", "")
                patterns = _SLICER_CORE_PATTERNS.get(category, [])
                if not patterns or not any(kw in desc_lower for kw in patterns):
                    # Also check all categories for keyword matches.  The LLM may
                    # provide a broad category such as layout_slice_view for a
                    # more specific Slicer core operation such as slice visibility.
                    for cat, kws in _SLICER_CORE_PATTERNS.items():
                        if any(kw in desc_lower for kw in kws):
                            category = cat
                            patterns = kws
                            break
                if patterns and any(kw in desc_lower for kw in patterns):
                    so["op_type"] = "slicer_op"
                    so["slicer_op_category"] = category
                    so["slicer_api_keywords"] = so.get("slicer_api_keywords") or [category]
                    so["evidence_type"] = "slicer_core"
                    so["evidence_id"] = category
                    so["confidence"] = "high"
                    logger.info(
                        "[Stage 4] Reclassified step %d %s → slicer_op "
                        "(Slicer core UI pattern '%s'): %s",
                        step_num, so.get("op_type", "?"), category, desc_lower[:60],
                    )

            # Build method_details from matched extension_op sub-operations
            stage_methods = []
            for so in sub_ops:
                if so["op_type"] == "extension_op" and so.get("extension_method_hint"):
                    matched = so["extension_method_hint"]
                    m_info = all_methods.get(matched, {})
                    stage_methods.append({
                        "name": matched,
                        "purpose": so["description"],
                        "parameters": m_info.get("parameters", []),
                        "return_value": m_info.get("return_value"),
                        "state_reads": m_info.get("state_reads", []),
                        "state_writes": m_info.get("state_writes", []),
                        "calls_addnode": m_info.get("calls_addnode", False),
                        "adds_output_to_scene": m_info.get("adds_output_to_scene", False),
                        "side_effects": m_info.get("side_effects", []),
                    })

            # Determine overall step op_type
            op_types = {so["op_type"] for so in sub_ops}
            if len(op_types) > 1:
                stage_op_type = "mixed"
            elif op_types:
                stage_op_type = op_types.pop()
            else:
                stage_op_type = "extension_op"

            # Determine stage name
            stage_method_names = [m["name"] for m in stage_methods] if stage_methods else []
            stage_name = self._infer_stage_name(
                stage_method_names, step_num - 1, len(cookbook_def.steps)
            )

            # Determine if the step is optional
            is_optional = any(so.get("is_optional") for so in sub_ops)

            stage = {
                "stage_index": step_num - 1,
                "stage_name": stage_name,
                "methods": stage_method_names,
                "method_details": stage_methods,
                "depends_on": (
                    [f"cb_step_{d}" for d in cb_step.depends_on]
                    if cb_step.depends_on
                    else ([f"cb_step_{step_num - 1}"] if step_num > 1 else [])
                ),
                "input_nodes": [],
                "output_nodes": [],
                "op_type": stage_op_type,
                "cookbook_step": cb_step,
                "sub_operations": sub_ops,
                "is_optional": is_optional,
            }
            stages.append(stage)

        self.on_progress(
            4, "Cookbook Stage Map",
            f"Decomposed {len(stages)} cookbook steps via LLM"
        )

        return {
            "stages": stages,
            "stage_count": len(stages),
            "source": "cookbook_llm_decomposition",
        }

    # ================================================================
    # Stage 4.5: Cross-Stage Parameter Mapping (LLM)
    # ================================================================

    def _stage4_5_cross_stage_mapping(
        self, stage_map: Dict, logic_analysis: Dict, extension_name: str
    ) -> Dict:
        """
        Use LLM to analyze data flow between cookbook steps.

        Produces a cross_stage_map: e.g., "Step 2 writes self.mandibularSegmentation,
        and Step 4 reads it." Falls back to programmatic Jaccard matching on failure.
        """
        self.on_progress(
            "4.5", "Cross-Stage Parameter Mapping",
            "LLM analyzing data flow between steps..."
        )

        stages = stage_map.get("stages", [])
        if len(stages) <= 1:
            self.on_progress(
                "4.5", "Cross-Stage Parameter Mapping",
                "Single stage — no cross-stage mapping needed"
            )
            return {"_extension_name": extension_name}

        # Build step summaries with state info
        step_summaries = []
        for s in stages:
            idx = s.get("stage_index", 0)
            methods = s.get("method_details") or []
            state_reads = []
            state_writes = []
            for m in methods:
                if not isinstance(m, dict):
                    continue
                state_reads.extend(m.get("state_reads") or [])
                state_writes.extend(m.get("state_writes") or [])
            # Also include sub-operation info
            sub_ops = s.get("sub_operations") or []
            sub_ops_desc = [
                f"  - {so['op_type']}: {so.get('description', '')[:100]}"
                for so in sub_ops
                if isinstance(so, dict)
            ]
            step_summaries.append({
                "step_number": idx + 1,
                "step_id": f"cb_step_{idx + 1}",
                "stage_name": s.get("stage_name", ""),
                "methods": s.get("methods", []),
                "state_reads": list(set(state_reads)),
                "state_writes": list(set(state_writes)),
                "sub_operations": sub_ops_desc,
            })

        state_fields = logic_analysis.get("state_fields", [])

        prompt = textwrap.dedent(f"""\
        Analyze the data flow between steps of a Slicer extension cookbook workflow.

        ## State Fields (Logic class self.* fields)
        {json.dumps(state_fields, indent=2)}

        ## Workflow Steps
        {json.dumps(step_summaries, indent=2)}

        ## Task
        For each step that depends on data produced by an earlier step, identify the
        connection. This is critical for code template generation so that later steps
        can find nodes created by earlier steps.

        Connections can be:
        - **state_field**: Step N writes self.fieldX, and Step M reads self.fieldX.
        - **output_node**: Step N creates a vtkMRML node (via parameter or state write),
          and Step M needs that node as input.
        - **scene_state**: Step N changes the scene (selects a node, changes layout),
          and Step M relies on that state.

        Return a JSON object:
        {{
          "connections": [
            {{
              "from_step": 2,
              "to_step": 4,
              "type": "state_field" | "output_node" | "scene_state",
              "field": "self.mandibularSegmentation",
              "description": "Step 2 creates the mandible segmentation node which Step 4 reads"
            }}
          ]
        }}

        Return ONLY the JSON, no markdown fences or explanation.""")

        try:
            response = self._call_llm(prompt)
            result = self._parse_json_response(response)
        except Exception as e:
            logger.warning(
                "Stage 4.5 LLM cross-stage mapping failed (%s), "
                "falling back to programmatic matching", e
            )
            result = None

        # Convert LLM connections into cross_stage_map format
        if result and isinstance(result.get("connections"), list):
            cross_map = {"_extension_name": extension_name}
            for conn in result["connections"]:
                to_step = conn.get("to_step")
                if to_step is None:
                    continue
                to_idx = to_step - 1
                from_idx = conn.get("from_step", 0) - 1
                field = conn.get("field", "")
                desc = conn.get("description", "")
                conn_type = conn.get("type", "state_field")

                stage_map_entry = cross_map.setdefault(to_idx, {})
                # Use the field name as the parameter key
                param_key = field.replace("self.", "") if field else f"step_{from_idx + 1}_output"
                stage_map_entry[param_key] = {
                    "source_stage": from_idx,
                    "source_param": param_key,
                    "type": conn_type,
                    "description": desc,
                }

            self.on_progress(
                "4.5", "Cross-Stage Parameter Mapping",
                f"LLM identified {len(result['connections'])} cross-stage connections"
            )
            return cross_map

        # Fallback to programmatic Jaccard matching
        self.on_progress(
            "4.5", "Cross-Stage Parameter Mapping",
            "Falling back to programmatic name-similarity matching"
        )
        return self._map_cross_stage_params(stage_map, extension_name)

    # ================================================================
    # Node Lifecycle Analysis (folded into Stage 7)
    # ================================================================

    def _compute_node_lifecycle(self, scan_result: Dict, logic_analysis: Dict) -> Dict:
        """Compute node creation mode and param role for each vtkMRML parameter.

        This is an AST-based analysis (no LLM unless AST finds nothing) used
        internally by code template generation (Stage 7).
        """
        return self._stage4_node_lifecycle(scan_result, logic_analysis)

    def _classify_placement_starter_methods(self, logic_analysis: Dict) -> Dict[str, Dict]:
        """Detect extension methods that create a markup and enter placement mode.

        These methods correspond to UI buttons such as "Add cut plane" or
        "Add fibula line".  The generated workflow should call them in the
        pre-interaction template and should not create a second markup node or
        call the same method again in the post-interaction template.
        """
        logic_file = logic_analysis.get("_logic_file", "")
        starters: Dict[str, Dict] = {}

        for method in logic_analysis.get("methods", []):
            method_name = method.get("name", "")
            if not method_name:
                continue
            source = self._extract_method_source(logic_file, method_name) or ""
            if not source:
                continue

            markup_classes = sorted(set(_re.findall(r'"(vtkMRMLMarkups[^"]+Node)"', source)))
            creates_markup = bool(markup_classes) and (
                "CreateNodeByClass" in source or "AddNewNodeByClass" in source
            )
            sets_active_markup = "SetActiveListID" in source
            enters_place_mode = (
                "SwitchToSinglePlaceMode" in source
                or "SwitchToPersistentPlaceMode" in source
                or "SetCurrentInteractionMode" in source
            )
            has_placement_observer = "PointPositionDefinedEvent" in source

            if creates_markup and sets_active_markup and enters_place_mode:
                starters[method_name] = {
                    "node_classes": markup_classes,
                    "has_placement_observer": has_placement_observer,
                    "reason": "creates a Markups node, activates it, and enters placement mode",
                }

        if starters:
            logger.info(
                "[Stage 7] Detected placement-starter methods: %s",
                ", ".join(sorted(starters)),
            )
            self.on_progress(
                7, "Analyzing interaction methods",
                f"Detected {len(starters)} placement-starter method(s)"
            )
        return starters

    # ================================================================
    # Internal LLM Review of Templates (part of Stage 7)
    # ================================================================

    def _review_templates(
        self,
        templates: Dict[str, str],
        logic_analysis: Dict,
        node_lifecycle: Dict,
    ) -> Dict[str, str]:
        """Internal LLM review of generated templates. Not a separate pipeline stage."""
        return self._stage7b_review_templates(templates, logic_analysis, node_lifecycle)

    # ================================================================
    # [Kept for fallback] Stage 3: State Dependency Analysis
    # ================================================================

    @staticmethod
    def _is_auxiliary_method(method: Dict) -> bool:
        """Check if a method is auxiliary (setup/install/cache/download) rather than a primary operation."""
        name = method.get("name", "").lower()
        purpose = method.get("purpose", "").lower()
        # Auxiliary keyword patterns
        aux_patterns = [
            "install", "setup", "setuppython", "clearcache", "clear_cache",
            "download", "check", "isinstalled", "ismodel", "torchversion",
            "incompatible", "installed", "disallowed",
        ]
        for pat in aux_patterns:
            if pat in name or pat in purpose:
                return True
        # Methods with no vtkMRML parameters and no state writes are likely auxiliary
        has_vtkmrml_param = any(
            "vtkMRML" in p.get("type", "")
            for p in method.get("parameters", [])
            if p.get("name") != "self"
        )
        has_state_write = bool(method.get("state_writes", []))
        if not has_vtkmrml_param and not has_state_write:
            return True
        return False

    def _stage3_state_dependencies(self, logic_analysis: Dict) -> Dict:
        """Build stage map from state dependencies."""
        self.on_progress(3, "Analyzing state dependencies", "Building dependency graph...")

        methods = logic_analysis.get("methods", [])
        pipeline_methods = logic_analysis.get("pipeline_methods", [])
        state_fields = logic_analysis.get("state_fields", [])

        # Classify methods as primary or auxiliary
        primary_methods = []
        auxiliary_methods = []
        for m in methods:
            if self._is_auxiliary_method(m):
                auxiliary_methods.append(m["name"])
            else:
                primary_methods.append(m)

        # Only include primary methods in the dependency graph
        dep_graph = {}
        for method in primary_methods:
            name = method["name"]
            writes = set(method.get("state_writes", []))
            dep_graph[name] = {"writes": writes, "reads": set(method.get("state_reads", []))}

        # Compute dependencies among primary methods
        method_deps = {}
        for name, info in dep_graph.items():
            deps = set()
            for other_name, other_info in dep_graph.items():
                if other_name == name:
                    continue
                if info["reads"] & other_info["writes"]:
                    deps.add(other_name)
            method_deps[name] = deps

        # Identify stages (topological grouping) from primary methods only
        stages = []
        assigned = set()
        remaining = set(dep_graph.keys())

        while remaining:
            current_stage = []
            for name in sorted(remaining):
                if method_deps.get(name, set()).issubset(assigned):
                    current_stage.append(name)

            if not current_stage:
                current_stage = sorted(remaining)

            stages.append(current_stage)
            assigned.update(current_stage)
            remaining -= set(current_stage)

        # Build stage map — each stage gets its primary methods + any auxiliary methods
        # that should run as setup (folded into the first stage that has primary methods)
        stage_map = []
        for i, stage_methods in enumerate(stages):
            method_infos = []
            for mname in stage_methods:
                for m in primary_methods:
                    if m["name"] == mname:
                        method_infos.append(m)
                        break

            stage_name = self._infer_stage_name(stage_methods, i, len(stages))

            input_nodes = []
            output_nodes = []
            for mi in method_infos:
                for p in mi.get("parameters", []):
                    ptype = p.get("type", "")
                    if "vtkMRML" in ptype and p.get("required", True):
                        if "output" in p.get("name", "").lower() or "output" in p.get("description", "").lower():
                            output_nodes.append(p)
                        else:
                            input_nodes.append(p)

            stage_map.append({
                "stage_index": i,
                "stage_name": stage_name,
                "methods": stage_methods,
                "method_details": method_infos,
                "depends_on": [stages[j] for j in range(i) if j < len(stages)],
                "input_nodes": input_nodes,
                "output_nodes": output_nodes,
            })

        self.on_progress(
            3, "Analyzing state dependencies",
            f"Found {len(stage_map)} stages: {[s['stage_name'] for s in stage_map]}"
        )

        return {"stages": stage_map, "dep_graph": dep_graph, "method_deps": method_deps}

    @staticmethod
    def _infer_stage_name(methods: List[str], index: int, total: int) -> str:
        """Infer a semantic name for a stage from its method names."""
        names_lower = " ".join(m.lower() for m in methods)
        if "seg" in names_lower:
            return "segmentation"
        if "plan" in names_lower or "reduc" in names_lower or "screw" in names_lower:
            return "planning"
        if "regist" in names_lower or "align" in names_lower:
            return "registration"
        if "detect" in names_lower or "find" in names_lower:
            return "detection"
        if "mesh" in names_lower or "model" in names_lower or "generat" in names_lower:
            return "generation"
        if "visual" in names_lower or "render" in names_lower or "display" in names_lower:
            return "visualization"
        if total == 1:
            return "full"
        return f"stage_{index + 1}"

    @staticmethod
    def _map_cross_stage_params(stage_map: Dict, extension_name: str = "") -> Dict:
        """
        Map parameters in later stages to output parameters from earlier stages.

        Returns:
            {stage_index: {param_name: {"source_stage": int, "source_param": str}},
             "_extension_name": str}
        """
        stages = stage_map.get("stages", [])
        cross_map = {}
        if extension_name:
            cross_map["_extension_name"] = extension_name

        for i, stage in enumerate(stages):
            if i == 0:
                continue

            # Collect all output params from prior stages
            prior_outputs = []
            for j in range(i):
                for mi in stages[j].get("method_details", []):
                    for p in mi.get("parameters", []):
                        pname = p.get("name", "")
                        ptype = p.get("type", "")
                        if "vtkMRML" in ptype and (
                            "output" in pname.lower()
                            or "result" in pname.lower()
                            or "out" in pname.lower()
                        ):
                            prior_outputs.append((j, pname, ptype))

            # Match this stage's vtkMRML params against prior outputs
            stage_map_entry = {}
            for mi in stage.get("method_details", []):
                for p in mi.get("parameters", []):
                    pname = p.get("name", "")
                    ptype = p.get("type", "")
                    if "vtkMRML" not in ptype:
                        continue

                    # Try to match against prior outputs by type + name similarity
                    best_match = None
                    best_score = 0.0
                    for (src_stage, src_name, src_type) in prior_outputs:
                        if src_type != ptype:
                            continue
                        score = _name_similarity(pname, src_name)
                        if score > best_score:
                            best_score = score
                            best_match = (src_stage, src_name)

                    if best_match and best_score > 0.4:
                        stage_map_entry[pname] = {
                            "source_stage": best_match[0],
                            "source_param": best_match[1],
                        }

            if stage_map_entry:
                cross_map[i] = stage_map_entry

        return cross_map

    # ================================================================
    # Node Lifecycle Analysis (used internally by Stage 7)
    # ================================================================

    def _stage4_node_lifecycle(self, scan_result: Dict, logic_analysis: Dict) -> Dict:
        """Determine node creation mode and param role for each vtkMRML parameter."""
        self.on_progress(7, "Analyzing node lifecycle", "Determining node creation patterns via AST...")

        node_lifecycle = {}
        methods = logic_analysis.get("methods", [])
        logic_file = logic_analysis.get("_logic_file", "")

        for method in methods:
            mname = method["name"]
            params = method.get("parameters", [])

            # Build set of all param names for this method
            all_param_names = {p.get("name", "") for p in params}

            # Extract and parse method source
            method_source = self._extract_method_source(logic_file, mname)
            if not method_source:
                method_source = ""
            else:
                method_source = textwrap.dedent(method_source)

            # Run AST visitor
            visitor = _AddNodeVisitor(all_param_names)
            try:
                tree = ast.parse(method_source)
                visitor.visit(tree)
            except SyntaxError:
                logger.warning("Could not parse method %s for lifecycle analysis", mname)

            for p in params:
                ptype = p.get("type", "")
                pname = p.get("name", "")
                if "vtkMRML" not in ptype:
                    continue

                is_output = (
                    "output" in pname.lower()
                    or "result" in pname.lower()
                    or "out" in pname.lower()
                )
                if not is_output:
                    continue

                key = f"{mname}:{pname}"

                # Determine create_mode using AST results
                if pname in visitor.params_added_to_scene:
                    # Method calls AddNode(param) — caller should pre-create without adding
                    create_mode = "CreateNodeByClass"
                    reason = f"AST: method passes '{pname}' to AddNode() — pre-create without adding to scene"
                elif visitor.has_addnewnodebyclass:
                    # Method uses AddNewNodeByClass for other nodes, but not this param
                    # Be safe: use AddNewNodeByClass so the node is in the scene
                    create_mode = "AddNewNodeByClass"
                    reason = "AST: method uses AddNewNodeByClass for internal nodes — create and add to scene"
                else:
                    # No AddNode call targets this param — caller must create AND add
                    create_mode = "AddNewNodeByClass"
                    reason = "AST: no AddNode() call targets this param — caller creates and adds to scene"

                node_lifecycle[key] = {
                    "create_mode": create_mode,
                    "reason": reason,
                    "node_class": ptype,
                    "param_role": "output",
                }

        # If no output nodes found from parameters, ask LLM
        if not node_lifecycle:
            self.on_progress(
                7, "Analyzing node lifecycle",
                "Asking LLM about node creation patterns..."
            )
            node_lifecycle = self._llm_node_lifecycle(logic_analysis)

        self.on_progress(
            7, "Analyzing node lifecycle",
            f"Analyzed {len(node_lifecycle)} output nodes via AST"
        )

        return node_lifecycle

    def _llm_node_lifecycle(self, logic_analysis: Dict) -> Dict:
        """Use LLM to determine node lifecycle for ambiguous cases."""
        methods = logic_analysis.get("methods", [])
        method_summaries = []
        for m in methods:
            params_str = ", ".join(
                f"{p['name']}: {p['type']}"
                for p in m.get("parameters", [])
            )
            method_summaries.append(
                f"  {m['name']}({params_str})\n"
                f"    adds_output_to_scene: {m.get('adds_output_to_scene', 'unknown')}\n"
                f"    calls_addnode: {m.get('calls_addnode', 'unknown')}"
            )

        prompt = textwrap.dedent(f"""\
For each method below, determine whether its output node parameters should be created
with CreateNodeByClass (creates WITHOUT adding to scene) or AddNewNodeByClass (creates AND adds).

Rules:
- If the method calls slicer.mrmlScene.AddNode() on the parameter → use CreateNodeByClass (template should NOT add to scene)
- If the method does NOT add to scene itself → use AddNewNodeByClass (template must add)
- When unsure, default to CreateNodeByClass (safer — avoids "Node already added" errors)

Methods:
{chr(10).join(method_summaries)}

Return JSON:
{{
  "nodes": [
    {{"method": "method_name", "param": "param_name", "node_class": "vtkMRML...Node", "create_mode": "CreateNodeByClass" or "AddNewNodeByClass", "reason": "why"}}
  ]
}}""")

        response = self._call_llm(prompt)
        parsed = self._parse_json_response(response)
        if not parsed:
            return {}

        result = {}
        for node in parsed.get("nodes", []):
            key = f"{node['method']}:{node['param']}"
            result[key] = {
                "create_mode": node.get("create_mode", "CreateNodeByClass"),
                "reason": node.get("reason", ""),
                "node_class": node.get("node_class", ""),
            }
        return result

    # ================================================================
    # [Kept for fallback] Interactive Pattern Detection
    # ================================================================

    # MRML markup node class prefixes for AST scanning
    _MARKUP_NODE_CLASSES = {
        "vtkMRMLMarkupsCurveNode": "curve",
        "vtkMRMLMarkupsPlaneNode": "plane",
        "vtkMRMLMarkupsLineNode": "line",
        "vtkMRMLMarkupsFiducialNode": "fiducial",
        "vtkMRMLMarkupsROINode": "roi",
    }

    _INTERACTION_PATTERNS = [
        "StartPlaceMode", "SetPlaceModeEnabled", "SwitchToSinglePlaceMode",
        "SwitchToPersistentPlaceMode", "PlaceModeEnabled",
        "AddObserver", "PointModifiedEvent", "PointAddedEvent",
        "PointPositionDefinedEvent", "InteractionEvent",
        "DynamicModeler", "vtkSlicerDynamicModelerModuleLogic",
        "HandlesInteractive", "RotationHandleVisibility",
        "TranslationHandleVisibility", "ScaleHandleVisibility",
        "QTimer", "singleShot",
    ]

    def _stage4b_detect_interactive_patterns(
        self, scan_result: Dict, logic_analysis: Dict
    ) -> Dict:
        """
        Detect interactive markup placement patterns in the extension source.

        Scans both the Logic class and the Widget class (if found in the same file)
        for markup node creation, placement mode entry, observer setup, and
        debounce timer patterns.

        Returns:
            Dict with:
            - has_interactive: bool
            - patterns: list of detected interactive pattern descriptors
            - widget_source: str (Widget class source, if found)
        """
        self.on_progress("4.5", "Interactive Pattern Detection", "Scanning for markup nodes...")

        result = {"has_interactive": False, "patterns": [], "widget_source": ""}

        # Read the full extension source to scan for Widget class
        entry_module = scan_result.get("entry_module")
        if not entry_module or not os.path.isfile(entry_module):
            return result

        with open(entry_module, "r", encoding="utf-8", errors="ignore") as f:
            full_source = f.read()

        try:
            full_tree = ast.parse(full_source)
        except SyntaxError:
            return result

        # --- AST-based detection ---
        detected_markup_refs = set()
        detected_interaction_calls = set()
        detected_observer_patterns = set()
        detected_timer_patterns = set()

        for node in ast.walk(full_tree):
            # Detect string literals referencing markup node classes
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                for cls_name, interaction_type in self._MARKUP_NODE_CLASSES.items():
                    if cls_name in val:
                        detected_markup_refs.add((cls_name, interaction_type))
                if "Markups" in val and "Node" in val and val not in self._MARKUP_NODE_CLASSES:
                    detected_markup_refs.add((val, "unknown"))

            # Detect AddNewNodeByClass calls with markup node types
            if isinstance(node, ast.Call):
                func_str = self._get_call_name(node)
                if func_str and "AddNewNodeByClass" in func_str:
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            for cls_name, interaction_type in self._MARKUP_NODE_CLASSES.items():
                                if cls_name in arg.value:
                                    detected_markup_refs.add((cls_name, interaction_type))

                # Detect placement mode calls
                if func_str:
                    for pattern in ["StartPlaceMode", "SetPlaceModeEnabled",
                                    "SwitchToSinglePlaceMode", "SwitchToPersistentPlaceMode"]:
                        if pattern in func_str:
                            detected_interaction_calls.add(pattern)

        # String-based detection for patterns harder to catch with AST
        for pattern in self._INTERACTION_PATTERNS:
            if pattern in full_source:
                if "Observer" in pattern or "Event" in pattern:
                    detected_observer_patterns.add(pattern)
                elif "Timer" in pattern or "singleShot" in pattern:
                    detected_timer_patterns.add(pattern)

        has_interactive = bool(detected_markup_refs)
        result["has_interactive"] = has_interactive

        if not has_interactive:
            self.on_progress("4.5", "Interactive Pattern Detection", "No interactive patterns found")
            return result

        # --- LLM-assisted classification ---
        result["patterns"] = [
            {"class": cls, "interaction_type": itype}
            for cls, itype in detected_markup_refs
        ]
        result["interaction_calls"] = list(detected_interaction_calls)
        result["observer_patterns"] = list(detected_observer_patterns)
        result["timer_patterns"] = list(detected_timer_patterns)

        # Extract Widget class source for LLM context
        widget_source = self._extract_widget_source(full_tree, full_source)
        result["widget_source"] = widget_source[:_MAX_SOURCE_FOR_LLM]

        # Ask LLM to classify interactive patterns into phases
        logic_class_name = scan_result.get("logic_class", {}).get("class_name", "Logic")
        method_names = [
            m.get("name", "") for m in logic_analysis.get("methods", [])
            if not self._is_auxiliary_method(m)
        ]

        classification_prompt = textwrap.dedent(f"""\
        Analyze the following Slicer extension for interactive 3D user interaction patterns.

        Extension Logic class: {logic_class_name}
        Logic methods: {json.dumps(method_names[:30])}

        Detected markup node types: {json.dumps(list(detected_markup_refs))}
        Detected interaction calls: {json.dumps(list(detected_interaction_calls))}
        Detected observer patterns: {json.dumps(list(detected_observer_patterns))}
        Detected timer patterns: {json.dumps(list(detected_timer_patterns))}

        Widget class source (excerpt):
        ```python
        {widget_source}
        ```

        Classify each detected interactive pattern into a structured phase.
        For each phase, determine:
        1. phase_name: a short snake_case identifier
        2. interaction_type: "curve", "plane", "line", "fiducial", or "unknown"
        3. description: what the user does in this phase
        4. node_class: the vtkMRML node class used
        5. placement_instructions: what to tell the user to do
        6. min_control_points: minimum control points needed (0 if unknown)
        7. has_reactive_chain: true if observer triggers recomputation
        8. reactive_description: what recomputation happens (if has_reactive_chain)
        9. is_optional: true if this is an optional/experimental phase
        10. depends_on: list of phase_names this phase depends on

        Respond with ONLY a JSON array of phase objects, no markdown fences.
        """)

        self.on_progress("4.5", "Interactive Pattern Detection", "LLM classifying patterns...")
        try:
            llm_response = self._call_llm(classification_prompt)
            phases = self._parse_json_response(llm_response)
            if isinstance(phases, list):
                result["phases"] = phases
                self.on_progress(
                    "4.5", "Interactive Pattern Detection",
                    f"Classified {len(phases)} interactive phases"
                )
        except Exception as e:
            logger.warning(f"Stage 4.5 LLM classification failed: {e}")
            result["phases"] = []

        return result

    def _extract_widget_source(self, tree, full_source: str) -> str:
        """Extract the Widget class source from the full module AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    base_name = ""
                    if isinstance(base, ast.Name):
                        base_name = base.id
                    elif isinstance(base, ast.Attribute):
                        base_name = base.attr
                    if "Widget" in base_name:
                        try:
                            lines = full_source.split("\n")
                            start = node.lineno - 1
                            end = node.end_lineno if hasattr(node, "end_lineno") else len(lines)
                            return "\n".join(lines[start:end])
                        except Exception:
                            return ""
        return ""

    @staticmethod
    def _get_call_name(node) -> str:
        """Get the dotted name of a Call node's function."""
        parts = []
        current = node.func
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))

    # ================================================================
    # Stage 4.7: Workflow Graph Construction
    # ================================================================

    def _stage4c_build_workflow_graph(
        self,
        interactive_patterns: Dict,
        logic_analysis: Dict,
        stage_map: Dict,
        extension_name: str,
    ) -> Dict:
        """
        Construct a workflow graph from detected interactive patterns.

        When self._ui_workflow is available (from Stage 1.5), uses it as the
        primary step source, enriching interactive steps with detected pattern
        metadata (node_class, reactive_chains) from Stage 4.5.

        Otherwise falls back to merging stage_map + interactive patterns.
        """
        self.on_progress("4.7", "Workflow Graph Construction", "Building workflow graph...")

        phases = interactive_patterns.get("phases", [])

        # Build a lookup of interactive pattern metadata by logic method name
        pattern_by_method = {}
        for p in phases:
            # phase_name may match a logic method; also check interaction_type
            pattern_by_method[p.get("phase_name", "").lower()] = p

        # ---- UI Workflow path (preferred when available) ----
        if self._ui_workflow:
            steps = self._build_steps_from_ui_workflow(
                self._ui_workflow, pattern_by_method, phases
            )
            if steps:
                return self._finalize_workflow_graph(steps, "4.7")

        # ---- Fallback: original merge logic ----
        if not phases:
            self.on_progress("4.7", "Workflow Graph Construction", "No phases to build")
            return None

        steps = []
        automated_stages = stage_map.get("stages", [])

        # First, add any automated stages that aren't covered by interactive phases
        phase_names = [p.get("phase_name") for p in phases]

        added_automated = set()
        for stage_idx, stage_info in enumerate(automated_stages):
            stage_methods = stage_info.get("methods", [])
            # Check if this stage's purpose overlaps with any interactive phase
            stage_name = stage_info.get("semantic_name", stage_info.get("stage_name", f"stage_{stage_idx}"))
            is_covered = any(
                p.get("phase_name") == stage_name
                for p in phases
            )
            if not is_covered and stage_idx not in added_automated:
                step = {
                    "step_id": stage_name,
                    "phase": stage_name,
                    "step_type": "automated",
                    "description": f"Automated step: {stage_name}",
                    "method_name": stage_methods[0] if stage_methods else None,
                    "depends_on": [],
                    "produces_nodes": [],
                }
                # Add dependency on previous step
                if steps:
                    step["depends_on"] = [steps[-1]["step_id"]]
                steps.append(step)
                added_automated.add(stage_idx)

        # Add interactive phases
        for phase in phases:
            phase_name = phase.get("phase_name", "unknown")
            interaction_type = phase.get("interaction_type", "unknown")
            node_class_map = {
                "curve": "vtkMRMLMarkupsCurveNode",
                "plane": "vtkMRMLMarkupsPlaneNode",
                "line": "vtkMRMLMarkupsLineNode",
                "fiducial": "vtkMRMLMarkupsFiducialNode",
            }
            node_class = phase.get("node_class") or node_class_map.get(interaction_type, "")

            step = {
                "step_id": phase_name,
                "phase": phase_name,
                "step_type": "interactive",
                "description": phase.get("description", ""),
                "interaction_type": interaction_type,
                "node_class": node_class,
                "placement_instructions": phase.get("placement_instructions", ""),
                "min_control_points": phase.get("min_control_points", 0),
                "validation_rules": [f"minimum {phase.get('min_control_points', 0)} control points"],
                "is_optional": phase.get("is_optional", False),
                "produces_nodes": [],
            }

            # Reactive chains
            if phase.get("has_reactive_chain"):
                step["reactive_chains"] = [{
                    "trigger_event": "PointModifiedEvent",
                    "recompute_description": phase.get("reactive_description", ""),
                    "debounce_ms": 300,
                }]
            else:
                step["reactive_chains"] = []

            # Dependencies
            deps = phase.get("depends_on", [])
            if isinstance(deps, list):
                step["depends_on"] = deps
            elif isinstance(deps, str):
                step["depends_on"] = [deps]
            else:
                # Auto-link to previous step
                if steps:
                    step["depends_on"] = [steps[-1]["step_id"]]

            steps.append(step)

        return self._finalize_workflow_graph(steps, "4.7")

    def _build_steps_from_ui_workflow(
        self,
        ui_workflow: Dict,
        pattern_by_method: Dict,
        phases: list,
    ) -> list:
        """Build workflow steps from the Stage 1.5 UI workflow, enriched with
        detected interactive pattern metadata from Stage 4.5."""
        node_class_map = {
            "curve": "vtkMRMLMarkupsCurveNode",
            "plane": "vtkMRMLMarkupsPlaneNode",
            "line": "vtkMRMLMarkupsLineNode",
            "fiducial": "vtkMRMLMarkupsFiducialNode",
        }

        steps = []
        step_id_set = set()

        for section in ui_workflow.get("ui_sections", []):
            is_section_optional = section.get("is_optional", False)
            for ui_step in section.get("steps", []):
                step_id = ui_step.get("step_id", "")
                logic_method = ui_step.get("logic_method", "")
                step_type = ui_step.get("step_type", "automated")
                is_optional = ui_step.get("is_optional", is_section_optional)

                # Cross-reference with Stage 4.5 detected patterns
                matched_pattern = self._match_pattern(
                    logic_method, step_id, pattern_by_method, phases
                )

                if step_type == "interactive":
                    interaction_type = ui_step.get("interaction_type") or (
                        matched_pattern.get("interaction_type", "") if matched_pattern else ""
                    )
                    node_class = (
                        ui_step.get("node_class")
                        or (matched_pattern.get("node_class", "") if matched_pattern else "")
                        or node_class_map.get(interaction_type, "")
                    )
                    min_cp = (
                        ui_step.get("min_control_points")
                        or (matched_pattern.get("min_control_points", 0) if matched_pattern else 0)
                        or 0
                    )
                    step = {
                        "step_id": step_id,
                        "phase": step_id,
                        "step_type": "interactive",
                        "description": ui_step.get("description", ""),
                        "method_name": logic_method,
                        "interaction_type": interaction_type,
                        "node_class": node_class,
                        "placement_instructions": ui_step.get("placement_instructions", "")
                            or (matched_pattern.get("placement_instructions", "") if matched_pattern else ""),
                        "min_control_points": min_cp,
                        "validation_rules": [f"minimum {min_cp} control points"],
                        "is_optional": is_optional,
                        "produces_nodes": [],
                    }
                    # Reactive chains from matched pattern
                    if matched_pattern and matched_pattern.get("has_reactive_chain"):
                        step["reactive_chains"] = [{
                            "trigger_event": "PointModifiedEvent",
                            "recompute_description": matched_pattern.get("reactive_description", ""),
                            "debounce_ms": 300,
                        }]
                    else:
                        step["reactive_chains"] = []
                else:
                    # Automated step
                    step = {
                        "step_id": step_id,
                        "phase": step_id,
                        "step_type": "automated",
                        "description": ui_step.get("description", f"Automated: {step_id}"),
                        "method_name": logic_method,
                        "depends_on": [],
                        "produces_nodes": [],
                    }
                    if is_optional:
                        step["is_optional"] = True

                # Dependencies from UI workflow
                deps = ui_step.get("depends_on", [])
                if isinstance(deps, list) and deps:
                    step["depends_on"] = deps
                elif not deps and steps:
                    step["depends_on"] = [steps[-1]["step_id"]]

                step_id_set.add(step_id)
                steps.append(step)

        return steps

    @staticmethod
    def _match_pattern(
        logic_method: str, step_id: str, pattern_by_method: Dict, phases: list
    ) -> Optional[Dict]:
        """Find the best matching Stage 4.5 pattern for a UI workflow step."""
        if not logic_method and not step_id:
            return None
        # Try exact match on logic method name
        if logic_method:
            for p in phases:
                pn = p.get("phase_name", "")
                if pn.lower() == logic_method.lower():
                    return p
        # Try step_id match
        if step_id:
            for p in phases:
                pn = p.get("phase_name", "")
                if pn.lower() == step_id.lower():
                    return p
        # Try token overlap
        lm_tokens = set(logic_method.lower().split("_")) if logic_method else set()
        si_tokens = set(step_id.lower().split("_")) if step_id else set()
        search_tokens = lm_tokens | si_tokens
        if search_tokens:
            for p in phases:
                pn_tokens = set(p.get("phase_name", "").lower().split("_"))
                if search_tokens & pn_tokens:
                    return p
        return None

    def _finalize_workflow_graph(self, steps: list, stage_label: str) -> Dict:
        """Apply optional→branch transformation and build the workflow_graph dict."""
        # Mark optional phases as branch steps
        for i, step in enumerate(steps):
            if step.get("is_optional"):
                step["step_type"] = "branch"
                step["condition"] = step.get("description", "Optional step")
                next_steps = [
                    s["step_id"] for s in steps[i+1:]
                    if not s.get("is_optional")
                ]
                step["branches"] = {
                    "yes": step["step_id"],
                    "no": next_steps[0] if next_steps else "",
                }

        workflow_graph = {
            "steps": steps,
            "phases": [
                {
                    "name": s["step_id"],
                    "optional": s.get("is_optional", False),
                }
                for s in steps
            ],
        }

        self.on_progress(
            stage_label, "Workflow Graph Construction",
            f"Built graph with {len(steps)} steps"
        )
        return workflow_graph

    # ================================================================
    # Stage 4.9: Workflow Validation (LLM-assisted)
    # ================================================================

    def _stage4d_validate_workflow(
        self, workflow_graph: Dict, logic_analysis: Dict
    ) -> Dict:
        """LLM reviews the workflow graph for completeness and correctness."""
        self.on_progress("4.9", "Workflow Validation", "LLM reviewing workflow...")

        steps_summary = [
            {
                "step_id": s["step_id"],
                "step_type": s["step_type"],
                "description": s.get("description", ""),
                "interaction_type": s.get("interaction_type"),
                "depends_on": s.get("depends_on", []),
            }
            for s in workflow_graph.get("steps", [])
        ]

        method_names = [
            m.get("name", "") for m in logic_analysis.get("methods", [])
        ]

        validation_prompt = textwrap.dedent(f"""\
        Review this workflow graph for a Slicer extension CLI tool.
        Check for:
        1. Every interactive step has a clear user action described
        2. Every automated step has a callable method that exists
        3. Dependencies form a connected DAG (no orphans, no cycles)
        4. Step order is sensible (data loading before processing, etc.)

        IMPORTANT: Do NOT remove automated steps. Automated steps (like "create models",
        "center line", "update plan") are valid workflow steps that the user triggers
        by clicking a button. Only suggest removing steps that are clearly not part of
        the user workflow (e.g., internal timer callbacks, error handlers, email/feedback).

        Workflow steps: {json.dumps(steps_summary, indent=2)}
        Available logic methods: {json.dumps(method_names[:30])}

        If the graph is valid, respond with: {{"valid": true}}
        If there are issues, respond with: {{"valid": false, "fixes": [list of fixes to apply]}}
        Each fix should be: {{"step_id": "...", "field": "...", "new_value": ...}}
        To remove a step entirely, use: {{"step_id": "...", "field": "step_type", "new_value": "removed"}}
        """)

        try:
            llm_response = self._call_llm(validation_prompt)
            review = self._parse_json_response(llm_response)
            if isinstance(review, dict) and not review.get("valid", True):
                # Apply fixes
                steps_to_remove = set()
                for fix in review.get("fixes", []):
                    step_id = fix.get("step_id")
                    field = fix.get("field")
                    new_value = fix.get("new_value")
                    if field == "step_type" and new_value == "removed":
                        steps_to_remove.add(step_id)
                        continue
                    for step in workflow_graph.get("steps", []):
                        if step.get("step_id") == step_id:
                            step[field] = new_value
                # Remove marked steps
                if steps_to_remove:
                    # Build dependency map for rewiring
                    dep_map = {}
                    for s in workflow_graph.get("steps", []):
                        dep_map[s.get("step_id", "")] = s.get("depends_on", [])

                    # Rewire: if step A depends on removed step B,
                    # replace B with B's own dependencies
                    for s in workflow_graph.get("steps", []):
                        new_deps = []
                        for dep in s.get("depends_on", []):
                            if dep in steps_to_remove:
                                # Replace with the removed step's dependencies
                                replaced = dep_map.get(dep, [])
                                for r in replaced:
                                    if r not in steps_to_remove and r not in new_deps:
                                        new_deps.append(r)
                            else:
                                new_deps.append(dep)
                        s["depends_on"] = new_deps

                    workflow_graph["steps"] = [
                        s for s in workflow_graph.get("steps", [])
                        if s.get("step_id") not in steps_to_remove
                    ]
                    workflow_graph["phases"] = [
                        p for p in workflow_graph.get("phases", [])
                        if p.get("name") not in steps_to_remove
                    ]
                fix_count = len(review.get("fixes", []))
                remove_count = len(steps_to_remove)
                self.on_progress(
                    "4.9", "Workflow Validation",
                    f"Applied {fix_count - remove_count} fixes, removed {remove_count} steps"
                )
            else:
                self.on_progress("4.9", "Workflow Validation", "Workflow validated")
        except Exception as e:
            logger.warning(f"Stage 4.9 LLM validation failed: {e}")
            self.on_progress("4.9", "Workflow Validation", "Validation skipped (LLM error)")

        return workflow_graph

    # ================================================================
    # Stage 6: Tool Schema Generation (LLM)
    # ================================================================

    def _generate_workflow_schemas(
        self, extension_name: str, workflow_graph: Dict, logic_analysis: Dict,
    ) -> List[Dict]:
        """Generate tool schema for an interactive workflow extension."""
        steps = workflow_graph.get("steps", [])
        # Filter out removed/invalid steps
        valid_types = {"automated", "interactive", "branch", "mixed", "user_choice"}
        steps = [s for s in steps if s.get("step_type") in valid_types]
        step_ids = [s["step_id"] for s in steps]
        automated_steps = [s for s in steps if s["step_type"] == "automated"]
        interactive_steps = [s for s in steps if s["step_type"] == "interactive"]
        branch_steps = [s for s in steps if s["step_type"] == "branch"]

        # Build enum of step IDs for the schema
        step_enum = step_ids

        # Build descriptions for each step
        step_descriptions = []
        for s in steps:
            desc = f"'{s['step_id']}': {s['description']}"
            if s["step_type"] == "interactive":
                desc += f" (interactive: {s.get('interaction_type', 'unknown')})"
            elif s["step_type"] == "branch":
                desc += " (optional — ask user first)"
            step_descriptions.append(desc)

        schema = {
            "type": "function",
            "function": {
                "name": extension_name,
                "description": (
                    f"Guided interactive workflow for {extension_name}. "
                    f"Execute steps in order. Interactive steps require user 3D interaction. "
                    f"Steps: {'; '.join(step_descriptions[:10])}"
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "workflow_step": {
                            "type": "string",
                            "enum": step_enum,
                            "description": "Which workflow step to execute",
                        },
                        "user_action": {
                            "type": "string",
                            "enum": ["start", "proceed", "skip", "cancel", "choice_made"],
                            "description": (
                                "Action: 'start' to begin a step, 'proceed' after user "
                                "completes interaction, 'skip' for optional steps, "
                                "'cancel' to abort workflow, 'choice_made' for user_choice steps"
                            ),
                        },
                    },
                    "required": ["workflow_step", "user_action"],
                },
            },
        }

        self.on_progress(
            6, "Generating tool schemas",
            f"Generated interactive workflow schema with {len(steps)} steps"
        )
        return [schema]

    def _stage6_generate_schemas(
        self,
        extension_name: str,
        stage_map: Dict,
        logic_analysis: Dict,
        node_lifecycle: Optional[Dict] = None,
        cross_stage_map: Optional[Dict] = None,
        workflow_graph: Optional[Dict] = None,
    ) -> List[Dict]:
        """Generate OpenAI function-calling tool schemas."""
        self.on_progress(6, "Generating tool schemas", "Building tool definitions...")

        # Interactive workflow schema generation
        if workflow_graph:
            return self._generate_workflow_schemas(extension_name, workflow_graph, logic_analysis)

        stages = stage_map.get("stages", [])
        if not stages:
            raise RuntimeError("No stages identified — cannot generate tool schemas")

        # Determine which params are internal (output nodes, cross-stage inputs)
        internal_params = set()
        if node_lifecycle:
            for key, info in node_lifecycle.items():
                if info.get("param_role") == "output":
                    internal_params.add(key.split(":", 1)[1])
        if cross_stage_map:
            for k, stage_map_entry in cross_stage_map.items():
                if isinstance(k, str) and k.startswith("_"):
                    continue
                internal_params.update(stage_map_entry.keys())

        # Build context for LLM — only include user-facing params
        stages_desc = []
        for s in stages:
            methods_desc = []
            for m in s.get("method_details", []):
                params_desc = []
                for p in m.get("parameters", []):
                    pname = p.get("name", "")
                    ptype = p.get("type", "")
                    # Skip params the template handles internally
                    if pname in internal_params:
                        params_desc.append(
                            f"    {pname}: {ptype} (INTERNAL — template creates this)"
                        )
                    elif "vtkMRML" in ptype:
                        # Input node from user (e.g., inputVolume)
                        params_desc.append(
                            f"    {pname}: {ptype} ({'required' if p.get('required') else 'optional'}) — {p.get('description', '')}"
                        )
                    elif "progress" in pname.lower() or pname == "qd":
                        params_desc.append(
                            f"    {pname}: {ptype} (INTERNAL — auto-filled by template)"
                        )
                    else:
                        params_desc.append(
                            f"    {pname}: {ptype} ({'required' if p.get('required') else 'optional'}) — {p.get('description', '')}"
                        )
                methods_desc.append(
                    f"  Method: {m['name']}\n"
                    f"  Purpose: {m.get('purpose', '')}\n"
                    f"  Parameters:\n" + "\n".join(params_desc)
                )
            stages_desc.append(
                f"Stage: {s['stage_name']}\n"
                f"Methods:\n" + "\n".join(methods_desc)
            )

        # Determine if we need a stage parameter (multiple stages) or single tool
        has_multiple_stages = len(stages) > 1

        # Reference schema format — minimal, only user-facing params
        example_schema = textwrap.dedent("""\
{
  "type": "function",
  "function": {
    "name": "PelvicFracturePlanning",
    "description": "...",
    "parameters": {
      "type": "object",
      "properties": {
        "stage": {"type": "string", "enum": ["segmentation", "planning", "full"], "description": "..."},
        "volume_node_name": {"type": "string", "description": "..."}
      },
      "required": ["stage"]
    }
  }
}""")

        prompt = textwrap.dedent(f"""\
Generate an OpenAI function-calling tool schema for a Slicer extension named "{extension_name}".

Extension stages:
{chr(10).join(stages_desc)}

{'The extension has multiple stages, so include a "stage" enum parameter.' if has_multiple_stages else 'The extension has a single stage, so no "stage" parameter is needed.'}""")

        if self._ui_workflow:
            prompt += textwrap.dedent(f"""\
Extracted UI Workflow (reflects the intended user-facing operation sequence):
```json
{json.dumps(self._ui_workflow, indent=2)}
```
Use this workflow to design tool schemas that match the actual user-facing steps.

""")

        prompt += textwrap.dedent("""\

IMPORTANT RULES:
- Do NOT include parameters marked as "INTERNAL" — the code template handles these automatically.
- Do NOT include any vtkMRML node parameters — the template creates/resolves them internally.
- Only include parameters that the LLM caller needs to provide: the "stage" enum, "volume_node_name", and any user-configurable options (thresholds, text prompts, flags, etc.).
- Boolean parameters with defaults should be optional with the default value.
- Filesystem paths (model_path, download_dir, output_path, etc.) MUST be optional — the template auto-discovers them. Do NOT mark them as required.
- The "required" list should be MINIMAL — only include what the LLM can reasonably fill from the user's request (e.g., text prompts). Never require paths, callbacks, or internal config.
- For text-prompted segmentation tools, include "text_prompts" (or similar) as required since the LLM derives it from the user's request (e.g., "segment the spine" → ["spine"]).

Also add an optional "volume_node_name" string parameter if the extension operates on a CT/volume input.

Reference schema format:
{example_schema}

Return a JSON array containing exactly one tool schema object.
The tool name should be based on the extension name (CamelCase, no spaces).
The description should explain what the tool does and when to use it.

Return ONLY the JSON array, no markdown fences.""")

        response = self._call_llm(prompt)
        schemas = self._parse_json_response(response)

        if isinstance(schemas, dict):
            schemas = [schemas]
        if not isinstance(schemas, list) or not schemas:
            raise RuntimeError(f"Invalid tool schema response: {str(response)[:300]}")

        # Validate schema structure
        for schema in schemas:
            if "function" not in schema:
                schema["function"] = schema
            if "type" not in schema:
                schema["type"] = "function"

        # Post-process: strip any remaining vtkMRML output params from schema
        # and demote filesystem path params from required
        _path_param_patterns = ("path", "dir", "directory", "folder")
        for schema in schemas:
            func = schema.get("function", {})
            params_obj = func.get("parameters", {})
            props = params_obj.get("properties", {})
            required = params_obj.get("required", [])

            to_remove = []
            for pname, pdef in props.items():
                ptype = pdef.get("type", "")
                desc = pdef.get("description", "")
                # Remove vtkMRML node params and progress/booleans the template handles
                if "vtkMRML" in str(ptype) or "vtkMRML" in desc:
                    to_remove.append(pname)
                elif pname in internal_params:
                    to_remove.append(pname)
                # Demote filesystem path params from required → optional
                elif pname.lower() != "volume_node_name":
                    plower = pname.lower()
                    if any(pat in plower for pat in _path_param_patterns):
                        if pname in required:
                            required.remove(pname)

            for pname in to_remove:
                del props[pname]
                if pname in required:
                    required.remove(pname)

            if required:
                params_obj["required"] = required
            elif "required" in params_obj and not required:
                del params_obj["required"]

        self.on_progress(
            6, "Generating tool schemas",
            f"Generated {len(schemas)} tool schema(s): "
            f"{[s.get('function', {}).get('name', '?') for s in schemas]}"
        )

        return schemas

    # ================================================================
    # Stage 7: Code Template Generation (LLM + internal review)
    # ================================================================

    def _generate_workflow_templates(
        self,
        extension_name: str,
        workflow_graph: Dict,
        scan_result: Dict,
        logic_analysis: Dict,
    ) -> Dict[str, str]:
        """
        Generate split templates for interactive workflow steps.

        For interactive steps: generates pre-interaction (node creation, placement mode)
        and post-interaction (validation, processing) templates.
        For automated steps: generates a single code template.
        Also generates the workflow.json file.
        """
        steps = workflow_graph.get("steps", [])
        templates = {}
        logic_class_name = scan_result.get("logic_class", {}).get("class_name", "")
        entry_module = scan_result.get("entry_module", "")
        module_name = os.path.splitext(os.path.basename(entry_module))[0] if entry_module else extension_name

        def _matching_slicer_template_items(step_id: str) -> List[Tuple[str, str]]:
            matches = []
            prefix = f"{step_id}_"
            for tpl_key, tpl_code in self._slicer_op_templates.items():
                if tpl_key == step_id or tpl_key.startswith(prefix):
                    matches.append((tpl_key, tpl_code))
            matches.sort(key=lambda item: item[0])
            return matches

        def _matching_slicer_templates(step_id: str) -> List[str]:
            return [code for _, code in _matching_slicer_template_items(step_id)]

        def _attach_slicer_evidence(step: Dict, template_file: str, source_keys: List[str]):
            evidence_items = [
                self._slicer_op_evidence.get(key, {})
                for key in source_keys
                if self._slicer_op_evidence.get(key)
            ]
            if not evidence_items:
                return
            merged = self._merge_api_evidence(evidence_items)
            step["api_evidence"] = merged
            if isinstance(self._workflow_metadata, dict):
                self._workflow_metadata.setdefault("api_evidence", {})[template_file] = merged

        placement_starter_by_step = {}
        for step in steps:
            method = step.get("method_name")
            if method in self._placement_starter_methods:
                placement_starter_by_step[step.get("step_id", "")] = method
                continue
            for so in step.get("sub_operations", []):
                hint = so.get("extension_method_hint")
                if hint in self._placement_starter_methods:
                    placement_starter_by_step[step.get("step_id", "")] = hint
                    break

        for step_index, step in enumerate(steps):
            step_id = step["step_id"]
            step_type = step["step_type"]
            op_type = step.get("op_type", "")

            if op_type == "unknown_op" or any(
                so.get("op_type") == "unknown_op" for so in step.get("sub_operations", [])
            ):
                key = f"templates/{step_id}.py.tpl"
                step["step_type"] = "automated"
                step["code_template"] = key
                templates[key] = self._generate_unknown_op_template(step)

            elif step_type == "automated" and op_type == "slicer_op":
                # Slicer_op templates are pre-generated in Stage 5T
                key = f"templates/{step_id}_slicer.py.tpl"
                step["code_template"] = key
                pregen_items = _matching_slicer_template_items(step_id)
                if pregen_items:
                    templates[key] = "\n\n".join(code for _, code in pregen_items)
                    _attach_slicer_evidence(step, key, [item_key for item_key, _ in pregen_items])
                else:
                    # Fallback: generate via LLM with generic slicer prompt
                    templates[key] = self._generate_slicer_fallback_template(step)

            elif step_type == "automated" and op_type == "mixed":
                # Automated step with mixed sub-operations: compose ALL sub-ops
                # (extension_op + slicer_op) into a single template.
                sub_ops = step.get("sub_operations", [])
                auto_parts = []
                # Consume Stage 5T templates once for the whole step.
                consumed_5t = False
                for so in sub_ops:
                    if so["op_type"] == "extension_op" and so.get("extension_method_hint"):
                        ext_step = dict(step)
                        ext_step["method_name"] = so["extension_method_hint"]
                        ext_step["description"] = so["description"]
                        if so["extension_method_hint"] in self._placement_starter_methods:
                            ext_tpl = self._generate_placement_starter_pre_template(
                                extension_name, ext_step, logic_class_name, module_name,
                            )
                        else:
                            ext_tpl = self._generate_automated_workflow_template(
                                extension_name, ext_step, logic_class_name, module_name,
                                logic_analysis,
                            )
                        auto_parts.append(f"# Extension op: {so['description']}\n{ext_tpl}")
                    elif so["op_type"] == "slicer_op":
                        if not consumed_5t:
                            pregen_items = _matching_slicer_template_items(step_id)
                            if pregen_items:
                                auto_parts.append(
                                    "# Slicer ops (Stage 5T)\n"
                                    + "\n\n".join(code for _, code in pregen_items)
                                )
                                _attach_slicer_evidence(
                                    step,
                                    f"templates/{step_id}.py.tpl",
                                    [item_key for item_key, _ in pregen_items],
                                )
                            else:
                                so_keywords = so.get("slicer_api_keywords", [])
                                so_desc = so.get("description", "")
                                llm_code = self._generate_slicer_api_template_llm(
                                    step_id, so_desc, so_keywords,
                                )
                                if llm_code:
                                    auto_parts.append(f"# Slicer op: {so_desc}\n{llm_code}")
                                else:
                                    auto_parts.append(f"# Slicer op: {so_desc}\n# TODO: generate slicer code\npass")
                            consumed_5t = True
                    elif so["op_type"] in ("extension_op", "unknown_op") and not so.get("extension_method_hint"):
                        if so.get("extension_function_hint"):
                            ext_step = dict(step)
                            ext_step["extension_function_name"] = so["extension_function_hint"]
                            ext_step["description"] = so.get("description", step.get("description", ""))
                            auto_parts.append(
                                f"# Extension function op: {so['description']}\n"
                                + self._generate_extension_function_template(
                                    extension_name, ext_step, module_name,
                                )
                            )
                            continue
                        # No method hint — generate targeted code for this sub-op only.
                        so_desc = so.get("description", "")
                        so_keywords = so.get("slicer_api_keywords", [])
                        category = so.get("slicer_op_category")
                        if category or so_keywords:
                            llm_code = self._generate_slicer_api_template_llm(
                                step_id, so_desc, so_keywords,
                            )
                            if llm_code:
                                auto_parts.append(f"# Auto op: {so_desc}\n{llm_code}")
                            else:
                                auto_parts.append(
                                    f"# Auto op: {so_desc}\n"
                                    f"# TODO: implement this operation\npass"
                                )
                key = f"templates/{step_id}.py.tpl"
                templates[key] = "\n\n".join(auto_parts) if auto_parts else "# No sub-operations\npass"
                step["code_template"] = key

            elif step_type == "automated":
                # Single code template for automated steps
                if step.get("extension_function_name"):
                    tpl = self._generate_extension_function_template(
                        extension_name, step, module_name,
                    )
                elif step.get("method_name") in self._placement_starter_methods:
                    step["interaction_owner"] = "extension_method"
                    step["placement_starter_method"] = step.get("method_name")
                    step["created_node_source"] = "extension_method"
                    tpl = self._generate_placement_starter_pre_template(
                        extension_name, step, logic_class_name, module_name,
                    )
                else:
                    tpl = self._generate_automated_workflow_template(
                        extension_name, step, logic_class_name, module_name, logic_analysis,
                    )
                templates[f"templates/{step_id}.py.tpl"] = tpl
                step["code_template"] = f"templates/{step_id}.py.tpl"

            elif step_type == "interactive":
                node_class = step.get("node_class", "")
                is_non_markup_interaction = bool(node_class) and not self._is_markup_node_class(node_class)
                prev_starter_method = None
                if step_index > 0:
                    prev_step_id = steps[step_index - 1].get("step_id", "")
                    prev_starter_method = placement_starter_by_step.get(prev_step_id)
                if prev_starter_method and self._is_markup_node_class(node_class):
                    step["interaction_owner"] = "previous_extension_method"
                    step["placement_starter_method"] = prev_starter_method
                    step["created_node_source"] = "previous_extension_method"

                # Pre-interaction template
                if prev_starter_method and self._is_markup_node_class(node_class):
                    pre_tpl = self._generate_existing_placement_pre_template(
                        extension_name, step, prev_starter_method,
                    )
                elif is_non_markup_interaction:
                    pre_tpl = self._generate_view_adjustment_pre_template(
                        extension_name, step,
                    )
                else:
                    if self._is_markup_node_class(node_class):
                        step["interaction_owner"] = "runtime_template"
                        step["created_node_source"] = "template"
                    pre_tpl = self._generate_pre_interaction_template(
                        extension_name, step, logic_class_name, module_name,
                    )
                templates[f"templates/{step_id}_pre.py.tpl"] = pre_tpl
                step["pre_template"] = f"templates/{step_id}_pre.py.tpl"

                # Post-interaction template
                if is_non_markup_interaction:
                    post_tpl = self._generate_view_adjustment_post_template(
                        extension_name, step,
                    )
                else:
                    post_tpl = self._generate_post_interaction_template(
                        extension_name, step, logic_class_name, module_name, logic_analysis,
                    )
                templates[f"templates/{step_id}_post.py.tpl"] = post_tpl
                step["post_template"] = f"templates/{step_id}_post.py.tpl"

            elif step_type == "mixed":
                # Mixed step: pre_template contains all automated sub-ops,
                # then user interaction follows.
                sub_ops = step.get("sub_operations", [])
                auto_parts = []
                placement_starter_method = None
                slicer_templates_appended = False
                pre_key = f"templates/{step_id}_pre.py.tpl"
                for so in sub_ops:
                    if so["op_type"] == "extension_op" and so.get("extension_method_hint"):
                        # Generate extension_op code
                        ext_step = dict(step)
                        ext_step["method_name"] = so["extension_method_hint"]
                        ext_step["description"] = so["description"]
                        if so["extension_method_hint"] in self._placement_starter_methods:
                            placement_starter_method = so["extension_method_hint"]
                            step["interaction_owner"] = "extension_method"
                            step["placement_starter_method"] = placement_starter_method
                            step["created_node_source"] = "extension_method"
                            ext_tpl = self._generate_placement_starter_pre_template(
                                extension_name, ext_step, logic_class_name, module_name,
                            )
                        else:
                            ext_tpl = self._generate_automated_workflow_template(
                                extension_name, ext_step, logic_class_name, module_name,
                                logic_analysis,
                            )
                        auto_parts.append(f"# Extension op: {so['description']}\n{ext_tpl}")
                    elif so["op_type"] == "extension_op" and so.get("extension_function_hint"):
                        ext_step = dict(step)
                        ext_step["extension_function_name"] = so["extension_function_hint"]
                        ext_step["description"] = so.get("description", step.get("description", ""))
                        auto_parts.append(
                            f"# Extension function op: {so['description']}\n"
                            + self._generate_extension_function_template(
                                extension_name, ext_step, module_name,
                            )
                        )
                    elif so["op_type"] == "slicer_op":
                        # Use pre-generated slicer_op template
                        if slicer_templates_appended:
                            continue
                        pregen_parts = _matching_slicer_templates(step_id)
                        if pregen_parts:
                            auto_parts.append(
                                f"# Slicer op: {so['description']}\n"
                                + "\n\n".join(pregen_parts)
                            )
                            _attach_slicer_evidence(
                                step,
                                pre_key,
                                [item_key for item_key, _ in _matching_slicer_template_items(step_id)],
                            )
                            slicer_templates_appended = True
                        else:
                            # No pre-generated template — try LLM with keywords
                            so_keywords = so.get("slicer_api_keywords", [])
                            so_desc = so.get("description", "")
                            llm_code = self._generate_slicer_api_template_llm(
                                step_id, so_desc, so_keywords,
                            )
                            if llm_code:
                                auto_parts.append(f"# Slicer op: {so_desc}\n{llm_code}")
                            else:
                                auto_parts.append(f"# Slicer op: {so_desc}\n# TODO: generate slicer code\npass")

                step["pre_template"] = pre_key

                # Append node creation + ID storage for the interaction sub-op
                # so the post-template can retrieve the node.
                interaction_sub_ops = [
                    so for so in sub_ops if so.get("op_type") == "user_interaction"
                ]
                if interaction_sub_ops:
                    iso = interaction_sub_ops[0]
                    node_class = iso.get("node_class") or step.get("node_class", "")
                    if (
                        node_class
                        and self._is_markup_node_class(node_class)
                        and not placement_starter_method
                    ):
                        step["interaction_owner"] = "runtime_template"
                        step["created_node_source"] = "template"
                        node_name = step_id.replace("_", " ").title()
                        node_var = f"_{extension_name.lower()}_{step_id}_id"
                        instructions = iso.get(
                            "placement_instructions",
                            step.get("description", ""),
                        )
                        interaction_block = (
                            f"\n\n# --- Setup interaction node ---\n"
                            f"import slicer\n"
                            f"node = slicer.mrmlScene.AddNewNodeByClass"
                            f"(\"{node_class}\", \"{node_name}\")\n"
                            f"displayNode = node.GetDisplayNode()\n"
                            f"if displayNode is not None:\n"
                            f"    displayNode.SetVisibility(True)\n"
                            f"slicer.modules.markups.logic().SetActiveListID(node)\n"
                            f"interactionNode = slicer.mrmlScene.GetNodeByID"
                            f"(\"vtkMRMLInteractionNodeSingleton\")\n"
                            f"interactionNode.SwitchToPersistentPlaceMode()\n"
                            f"{node_var} = node.GetID()\n"
                            f"print(\"[{extension_name}] Please {instructions}\")\n"
                        )
                        auto_parts.append(interaction_block)
                    elif node_class and not self._is_markup_node_class(node_class):
                        step["interaction_kind"] = "view_adjustment"
                        instructions = iso.get(
                            "placement_instructions",
                            step.get("description", ""),
                        )
                        auto_parts.append(
                            "\n\n# --- View adjustment interaction ---\n"
                            f"print(\"[{extension_name}] Please {instructions}\")\n"
                            "print(\"When finished, press the 'Done' button in the workflow panel.\")\n"
                        )

                templates[pre_key] = (
                    "\n\n".join(auto_parts) if auto_parts
                    else "# No automated sub-operations\npass"
                )

                # Post-interaction template for the user_interaction part
                post_key = f"templates/{step_id}_post.py.tpl"
                step["post_template"] = post_key
                if placement_starter_method:
                    templates[post_key] = self._generate_placement_starter_post_template(
                        extension_name, step, placement_starter_method,
                    )
                elif interaction_sub_ops and not self._is_markup_node_class(
                    interaction_sub_ops[0].get("node_class") or step.get("node_class", "")
                ):
                    templates[post_key] = self._generate_view_adjustment_post_template(
                        extension_name, step,
                    )
                else:
                    templates[post_key] = self._generate_post_interaction_template(
                        extension_name, step, logic_class_name, module_name, logic_analysis,
                    )

            elif step_type == "branch":
                # Branch steps don't need templates — handled by the orchestrator
                pass

            elif step_type == "user_choice":
                # user_choice steps don't need code templates — handled by the
                # orchestrator which presents the question and collects the answer.
                pass

        # Post-generation consistency check: verify pre/post templates agree
        # on node ID variables (_ext_step_id).
        consistency_fixes = 0
        for step in steps:
            if step.get("step_type") not in ("interactive", "mixed"):
                continue
            s_id = step["step_id"]
            node_var = f"_{extension_name.lower()}_{s_id}_id"

            # Check post-template references the var
            post_key = step.get("post_template", "")
            if not post_key or post_key not in templates:
                continue
            if node_var not in templates[post_key]:
                continue

            # Verify pre-template defines it
            pre_key = step.get("pre_template", "")
            if not pre_key or pre_key not in templates:
                continue
            if node_var in templates[pre_key]:
                continue

            # Missing — inject node ID storage at end of pre-template.
            # Only inject when node_class is set (a markup node was created).
            # For steps with empty node_class (e.g. slice crosshair adjustment),
            # no node exists to store — skip injection.
            node_class = step.get("node_class", "")
            if not node_class:
                continue
            injection = (
                f"\n# [Auto-injected] Store node ID for post-step\n"
                f"try:\n"
                f"    {node_var} = node.GetID()\n"
                f"except NameError:\n"
                f"    {node_var} = ''\n"
            )
            templates[pre_key] = templates[pre_key].rstrip() + "\n" + injection
            consistency_fixes += 1
            logger.info(
                "[Stage 7] Injected missing node ID '%s' into %s",
                node_var, pre_key,
            )

        if consistency_fixes:
            logger.info(
                "[Stage 7] Fixed %d pre/post node ID consistency issues",
                consistency_fixes,
            )

        # Store workflow graph as JSON template (only valid steps)
        valid_types = {"automated", "interactive", "branch", "mixed", "user_choice"}
        clean_graph = {k: v for k, v in workflow_graph.items() if k != "steps"}
        clean_graph["steps"] = [s for s in steps if s.get("step_type") in valid_types]
        templates["workflow.json"] = json.dumps(clean_graph, indent=2)
        templates["workflow_metadata.json"] = json.dumps(self._workflow_metadata or {}, indent=2)

        self.on_progress(
            7, "Generating code templates",
            f"Generated {len(templates)} workflow templates"
        )
        return templates

    def _generate_extension_function_template(
        self, extension_name: str, step: Dict, module_name: str,
    ) -> str:
        """Generate deterministic code for an extension-owned module function."""
        function_name = step.get("extension_function_name", "")
        step_id = step.get("step_id", "")
        description = step.get("description", step_id)
        if not function_name:
            return self._generate_unknown_op_template(step)
        lines = [
            f"# --- {extension_name}: {description} ---",
            f"from {module_name} import {function_name}",
            "",
            f"{function_name}()",
            "",
            f"print(\"[{extension_name}] Step '{step_id}' completed.\")",
        ]
        return "\n".join(lines) + "\n"

    def _generate_automated_workflow_template(
        self, extension_name, step, logic_class_name, module_name, logic_analysis,
    ) -> str:
        """Generate a code template for an automated workflow step.

        Uses LLM to generate proper state setup. Falls back to a static template
        on LLM failure.
        """
        method_name = step.get("method_name", "")
        step_id = step.get("step_id", "")
        description = step.get("description", step_id)

        # Try LLM-assisted generation
        tpl = self._generate_automated_template_llm(
            extension_name, step, logic_class_name, module_name, logic_analysis,
        )
        if tpl:
            return tpl

        # Fallback: static template
        if method_name:
            method_call_lines = [
                "# Execute the automated step",
                f"if hasattr(logic, '{method_name}'):",
                f"    result = logic.{method_name}()",
                "else:",
                "    result = None",
            ]
        else:
            # No extension method — try to generate code from sub-operations via LLM
            sub_ops = step.get("sub_operations", [])
            sub_op_parts = []
            for so in sub_ops:
                so_desc = so.get("description", "")
                so_keywords = so.get("slicer_api_keywords", [])
                so_method = so.get("extension_method_hint")
                if so.get("op_type") == "slicer_op" and so_keywords:
                    code = self._generate_slicer_api_template_llm(
                        step_id, so_desc, so_keywords,
                    )
                    if code:
                        sub_op_parts.append(f"# {so_desc}\n{code}")
                elif so.get("op_type") == "extension_op" and so_method:
                    sub_op_parts.append(
                        f"# {so_desc}\n"
                        f"if hasattr(logic, '{so_method}'):\n"
                        f"    logic.{so_method}()"
                    )
            if sub_op_parts:
                method_call_lines = ["\n\n".join(sub_op_parts)]
            else:
                method_call_lines = [
                    "# No specific method mapped to this step",
                    "# TODO: Determine the correct extension method to call",
                    "pass",
                ]

        lines = [
            f"# --- {extension_name}: {description} ---",
        ]
        # Only include extension import boilerplate if we actually call an extension method
        if method_name or any(
            so.get("op_type") == "extension_op" and so.get("extension_method_hint")
            for so in step.get("sub_operations", [])
        ):
            lines.extend([
                "try:",
                f"    from {module_name} import {logic_class_name}",
                "except ImportError:",
                f"    raise RuntimeError(\"{extension_name} extension is not installed.\")",
                "",
                "try:",
                f"    logic = _{extension_name.lower()}_logic",
                "except NameError:",
                f"    logic = {logic_class_name}()",
                "",
            ])
        lines.extend(method_call_lines)
        lines.append("")
        # Only store logic instance if we actually created one
        if method_name or any(
            so.get("op_type") == "extension_op" and so.get("extension_method_hint")
            for so in step.get("sub_operations", [])
        ):
            lines.append(f"_{extension_name.lower()}_logic = logic")
        lines.append(f"print(\"[{extension_name}] Step '{step_id}' completed.\")")

        return "\n".join(lines) + "\n"

    def _generate_automated_template_llm(
        self, extension_name, step, logic_class_name, module_name, logic_analysis,
    ) -> Optional[str]:
        """Use LLM to generate an automated workflow template with proper state setup."""
        method_name = step.get("method_name", "")
        if not method_name:
            return None

        # Gather method info
        method_info = None
        for m in logic_analysis.get("methods", []):
            if m.get("name") == method_name:
                method_info = m
                break

        # Get method source
        logic_file = logic_analysis.get("_logic_file", "")
        method_source = self._extract_method_source(logic_file, method_name) or ""

        if not method_source and not method_info:
            return None

        # Truncate source if needed (no limit — full method source for template generation)
        # if len(method_source) > 5000:
        #     method_source = method_source[:5000] + "\n# ... [truncated]"

        # Build method signature info
        params_desc = ""
        if method_info:
            params = method_info.get("parameters", [])
            if params:
                params_desc = "Parameters:\n" + "\n".join(
                    f"  - {p.get('name')}: {p.get('type', '?')} ({'required' if p.get('required') else 'optional'}) — {p.get('description', '')}"
                    for p in params
                )
            state_reads = method_info.get("state_reads", [])
            state_writes = method_info.get("state_writes", [])
            if state_reads:
                params_desc += f"\nState reads: {', '.join(state_reads)}"
            if state_writes:
                params_desc += f"\nState writes: {', '.join(state_writes)}"

        # UI workflow context
        ui_context = ""
        if self._ui_workflow:
            for sec in self._ui_workflow.get("ui_sections", []):
                for s in sec.get("steps", []):
                    if s.get("step_id") == step.get("step_id") or s.get("logic_method") == method_name:
                        ui_context = f"Button label: '{s.get('button_label', '')}'\nDescription: {s.get('description', '')}"
                        break

        prompt = textwrap.dedent(f"""\
            Generate a Python code snippet for a 3D Slicer extension workflow step.

            Extension: {extension_name}
            Logic class: `{logic_class_name}` (import from `{module_name}`)
            Step: {step.get('step_id', '')}
            Method to call: `{method_name}()`
            {ui_context}

            {params_desc}

            Method source code:
            ```python
            {method_source}
            ```

            The code must:
            1. Import the logic class from `{module_name}`
            2. Reuse the existing logic instance `_{extension_name.lower()}_logic` if it exists, otherwise create a new `{logic_class_name}()`
            3. Set up any required state on the logic instance BEFORE calling the method (e.g., if the method reads `self.mandibleSegmentationNode`, find the node in the scene and assign it)
            4. To find scene nodes, use robust fuzzy matching — NEVER rely on exact node names. Use this pattern:
               ```python
               nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLSegmentationNode")
               for i in range(nodes.GetNumberOfItems()):
                   n = nodes.GetItemAsObject(i)
                   if "fibula" in n.GetName().lower():
                       fibulaNode = n
                       break
               ```
               Or for parameter node references: first check `parameterNode.GetNodeReference("refName")`, and if None, search the scene by class + name substring, then set via `parameterNode.SetNodeReferenceID("refName", node.GetID())`.
            5. Call the method with correct arguments
            6. Store the logic instance as `_{extension_name.lower()}_logic` for subsequent steps
            7. Print a completion message

            IMPORTANT restrictions:
            - Do NOT use `dir()`, `eval()`, `exec()`, `globals()`, or `locals()` — these are blocked in the execution sandbox.
            - Use `try/except NameError` to check if a variable exists, NOT `if 'var' in dir()`.
            - Do NOT use curly brace template placeholders. Write actual Python values (strings, numbers, etc.). If you need a node name, hardcode a reasonable default like `slicer.util.getNode('FibulaModel')`.
            - Escape all braces in f-strings and .format() calls by doubling them: use doubled-braces for literal braces in output strings.
            - Return ONLY raw Python code. Do NOT wrap it in markdown fences (```python ... ```).""")

        try:
            for _attempt in range(2):
                response = self._call_llm(prompt)
                response = self._strip_markdown_fences(response) if response else None
                if not response:
                    break
                # Validate syntax immediately — retry once on failure
                import ast as _ast
                try:
                    _ast.parse(response)
                    return response
                except (SyntaxError, IndentationError) as e:
                    if _attempt == 0:
                        logger.info(
                            "LLM automated template for step %s had syntax error: %s. Retrying...",
                            step.get("step_id", "?"), e,
                        )
                        # Add error context for retry
                        prompt += (
                            f"\n\nYour previous output had a syntax error: {e}\n"
                            "Output ONLY the corrected Python code, no explanation."
                        )
                    else:
                        logger.warning(
                            "LLM automated template for step %s still has syntax error after retry: %s",
                            step.get("step_id", "?"), e,
                        )
                        return response  # Return as-is, stage 9 / revision will catch it
        except Exception:
            logger.debug("LLM automated template generation failed", exc_info=True)
        return None

    def _generate_slicer_api_template_llm(
        self, step_id: str, description: str, slicer_api_keywords: List[str],
    ) -> Optional[str]:
        """Generate pure Slicer API code via LLM for steps with no extension method.

        Called when a step has slicer_op sub-operations but no method_name on the
        extension Logic class.  Uses the LLM with the step description and API
        keyword hints to produce Slicer core API code (no extension imports).
        """
        keywords_str = ", ".join(slicer_api_keywords) if slicer_api_keywords else "none"
        prompt = textwrap.dedent(f"""\
            Generate a Python code snippet for a 3D Slicer operation.

            Step ID: {step_id}
            Description: {description}
            API keyword hints: [{keywords_str}]

            The code must:
            1. Use Slicer's built-in Python API only (slicer.mrmlScene,
               slicer.app.layoutManager(), slicer.modules, etc.)
            2. Be a complete, self-contained snippet that performs the described operation
            3. Use robust patterns (check for None, handle missing nodes gracefully)
            4. Print a short completion message

            IMPORTANT restrictions:
            - Do NOT use `dir()`, `eval()`, `exec()`, `globals()`, or `locals()`
            - Do NOT import the extension module — use only Slicer core APIs
            - Do NOT use curly brace template placeholders — write actual Python values
            - Escape all braces in f-strings by doubling them
            - Return ONLY raw Python code, no markdown fences""")

        try:
            for _attempt in range(2):
                response = self._call_llm(prompt)
                response = self._strip_markdown_fences(response) if response else None
                if not response or "slicer" not in response.lower():
                    break
                import ast as _ast
                try:
                    _ast.parse(response)
                    return response
                except (SyntaxError, IndentationError) as e:
                    if _attempt == 0:
                        prompt += (
                            f"\n\nPrevious output had syntax error: {e}\n"
                            "Output ONLY the corrected Python code, no explanation."
                        )
                    else:
                        return response
        except Exception:
            logger.debug("Slicer API LLM template generation failed", exc_info=True)
        return None

    def _generate_placement_starter_pre_template(
        self, extension_name, step, logic_class_name, module_name,
    ) -> str:
        """Generate deterministic setup code for extension-driven placement.

        The extension method itself creates the markup node and enters
        placement mode, so this template only calls that method.
        """
        method_name = step.get("method_name", "")
        step_id = step.get("step_id", "")
        description = step.get("description", step_id)

        lines = [
            f"# --- {extension_name}: {description} (Setup) ---",
            "import slicer",
            f"from {module_name} import {logic_class_name}",
            "",
            "try:",
            f"    logic = _{extension_name.lower()}_logic",
            "except NameError:",
            f"    logic = {logic_class_name}()",
            "",
            f"logic.{method_name}()",
            f"_{extension_name.lower()}_logic = logic",
            "",
            f"print(\"[{extension_name}] Placement started for step '{step_id}'.\")",
        ]
        return "\n".join(lines) + "\n"

    def _generate_placement_starter_post_template(
        self, extension_name, step, method_name,
    ) -> str:
        """Generate post-interaction code for extension-driven placement.

        Placement-starter extension methods usually attach their own observers
        and process control points as the user places them.  The post step only
        exits placement mode and reports completion.
        """
        step_id = step.get("step_id", "")
        lines = [
            f"# --- {extension_name}: {step.get('description', step_id)} (Done) ---",
            "import slicer",
            "",
            "interactionNode = slicer.mrmlScene.GetNodeByID(\"vtkMRMLInteractionNodeSingleton\")",
            "if interactionNode is not None:",
            "    interactionNode.SwitchToViewTransformMode()",
            "",
            f"print(\"[{extension_name}] Step '{step_id}' interaction completed after {method_name}().\")",
        ]
        return "\n".join(lines) + "\n"

    @staticmethod
    def _is_markup_node_class(node_class: str) -> bool:
        """Return True for MRML Markups nodes that support placement/control points."""
        return _text_or_empty(node_class).startswith("vtkMRMLMarkups")

    def _generate_existing_placement_pre_template(
        self, extension_name, step, starter_method,
    ) -> str:
        """Reuse the markup node created by the previous placement-starter step."""
        step_id = step.get("step_id", "")
        node_class = step.get("node_class", "vtkMRMLMarkupsFiducialNode")
        instructions = step.get("placement_instructions", step.get("description", ""))
        node_var = f"_{extension_name.lower()}_{step_id}_id"

        lines = [
            f"# --- {extension_name}: {step.get('description', step_id)} (Setup) ---",
            "import slicer",
            "",
            f"# Reuse the markup node created by {starter_method}() in the previous step.",
            f"nodes = slicer.mrmlScene.GetNodesByClass(\"{node_class}\")",
            "node = None",
            "for i in range(nodes.GetNumberOfItems() - 1, -1, -1):",
            "    candidate = nodes.GetItemAsObject(i)",
            "    if candidate is not None:",
            "        node = candidate",
            "        break",
            "if node is None:",
            f"    raise RuntimeError(\"No {node_class} found from previous placement step.\")",
            "",
            "displayNode = node.GetDisplayNode()",
            "if displayNode is not None:",
            "    displayNode.SetVisibility(True)",
            "slicer.modules.markups.logic().SetActiveListID(node)",
            "interactionNode = slicer.mrmlScene.GetNodeByID(\"vtkMRMLInteractionNodeSingleton\")",
            "if interactionNode is not None:",
            "    interactionNode.SwitchToPersistentPlaceMode()",
            f"{node_var} = node.GetID()",
            "",
            f"print(\"[{extension_name}] Please {instructions}\")",
            "print(\"When finished, press the 'Done' button in the workflow panel.\")",
        ]
        return "\n".join(lines) + "\n"

    def _generate_view_adjustment_pre_template(self, extension_name, step) -> str:
        """Generate setup for interactions that do not create markups nodes."""
        step_id = step.get("step_id", "")
        instructions = step.get("placement_instructions", step.get("description", ""))
        lines = [
            f"# --- {extension_name}: {step.get('description', step_id)} (Setup) ---",
            "import slicer",
            "",
            "# This step is a view adjustment, not a Markups placement.",
            f"print(\"[{extension_name}] Please {instructions}\")",
            "print(\"When finished, press the 'Done' button in the workflow panel.\")",
        ]
        return "\n".join(lines) + "\n"

    def _generate_view_adjustment_post_template(self, extension_name, step) -> str:
        """Generate completion code for non-markup interactions."""
        step_id = step.get("step_id", "")
        lines = [
            f"# --- {extension_name}: {step.get('description', step_id)} (Done) ---",
            "import slicer",
            "",
            "interactionNode = slicer.mrmlScene.GetNodeByID(\"vtkMRMLInteractionNodeSingleton\")",
            "if interactionNode is not None:",
            "    interactionNode.SwitchToViewTransformMode()",
            "",
            f"print(\"[{extension_name}] Step '{step_id}' view adjustment completed.\")",
        ]
        return "\n".join(lines) + "\n"

    def _generate_pre_interaction_template(
        self, extension_name, step, logic_class_name, module_name,
    ) -> str:
        """Generate the pre-interaction template for an interactive step."""
        interaction_type = step.get("interaction_type", "unknown")
        node_class = step.get("node_class", "vtkMRMLMarkupsFiducialNode")
        instructions = step.get("placement_instructions", step.get("description", ""))
        node_name = step["step_id"].replace("_", " ").title()
        min_points = step.get("min_control_points", 0)

        lines = [
            f"# --- {extension_name}: {step.get('description', step['step_id'])} (Setup) ---",
            "import slicer",
            "",
            "# Create the markup node for user interaction",
            f"node = slicer.mrmlScene.AddNewNodeByClass(\"{node_class}\", \"{node_name}\")",
            "displayNode = node.GetDisplayNode()",
            "if displayNode is not None:",
            "    displayNode.SetVisibility(True)",
            "",
            f"print(\"[{extension_name}] Please {instructions}\")",
            "print(\"When finished, press the 'Done' button in the workflow panel.\")",
            "",
            "# Enter placement mode",
            "slicer.modules.markups.logic().SetActiveListID(node)",
            "interactionNode = slicer.mrmlScene.GetNodeByID(\"vtkMRMLInteractionNodeSingleton\")",
            "interactionNode.SwitchToPersistentPlaceMode()",
            "",
            f"_{extension_name.lower()}_{step['step_id']}_id = node.GetID()",
        ]

        return "\n".join(lines) + "\n"

    def _generate_post_interaction_template(
        self, extension_name, step, logic_class_name, module_name, logic_analysis,
    ) -> str:
        """Generate the post-interaction template for an interactive step."""
        # Try LLM-assisted generation first
        llm_template = self._generate_post_interaction_template_llm(
            extension_name, step, logic_class_name, module_name, logic_analysis,
        )
        if llm_template:
            return llm_template

        # Fallback: static template
        min_points = step.get("min_control_points", 0)
        node_var = f"_{extension_name.lower()}_{step['step_id']}_id"

        lines = [
            f"# --- {extension_name}: {step.get('description', step['step_id'])} (Process) ---",
            "import slicer",
            "",
            f"node = slicer.mrmlScene.GetNodeByID({node_var})",
            "if node is None:",
            f"    raise RuntimeError(\"Node not found for step '{step['step_id']}'\")",
            "",
        ]

        if min_points > 0:
            lines += [
                "# Validate user input",
                "numPoints = node.GetNumberOfControlPoints()",
                f"if numPoints < {min_points}:",
                f"    raise RuntimeError(\"Need at least {min_points} control points, got %d. Please add more.\" % numPoints)",
                "",
            ]

        if step.get("reactive_chains"):
            for chain in step["reactive_chains"]:
                lines.append(f"# Reactive chain: {chain.get('recompute_description', '')}")

        parameter_role = (
            step.get("parameter_role")
            or (step.get("interaction_binding") or {}).get("parameter_name", "")
        )
        if parameter_role:
            lines += [
                "# Store the placed node on the extension parameter node for later steps",
                f"from {module_name} import {logic_class_name}",
                "try:",
                f"    logic = _{extension_name.lower()}_logic",
                "except NameError:",
                f"    logic = {logic_class_name}()",
                "parameterNode = logic.getParameterNode()",
                f"parameterNode.SetNodeReferenceID(\"{parameter_role}\", node.GetID())",
                f"_{extension_name.lower()}_logic = logic",
                "",
            ]

        lines += [
            "# Exit placement mode",
            "interactionNode = slicer.mrmlScene.GetNodeByID(\"vtkMRMLInteractionNodeSingleton\")",
            "interactionNode.SwitchToViewTransformMode()",
            "",
            f"print(\"[{extension_name}] Step '{step['step_id']}' processed with %d control points.\" % node.GetNumberOfControlPoints())",
        ]

        return "\n".join(lines) + "\n"

    def _generate_post_interaction_template_llm(
        self, extension_name, step, logic_class_name, module_name, logic_analysis,
    ) -> Optional[str]:
        """Use LLM to generate a post-interaction template that calls the logic method."""
        method_name = step.get("method_name", "")
        if not method_name:
            return None

        # Gather method info
        method_info = None
        for m in logic_analysis.get("methods", []):
            if m.get("name") == method_name:
                method_info = m
                break

        # Get method source
        logic_file = logic_analysis.get("_logic_file", "")
        method_source = self._extract_method_source(logic_file, method_name) or ""

        if not method_source and not method_info:
            return None

        # Method source sent in full (no truncation)
        # if len(method_source) > 5000:
        #     method_source = method_source[:5000] + "\n# ... [truncated]"

        # Build parameter / state info
        params_desc = ""
        if method_info:
            params = method_info.get("parameters", [])
            if params:
                params_desc = "Parameters:\n" + "\n".join(
                    f"  - {p.get('name')}: {p.get('type', '?')} ({'required' if p.get('required') else 'optional'}) — {p.get('description', '')}"
                    for p in params
                )
            state_reads = method_info.get("state_reads", [])
            state_writes = method_info.get("state_writes", [])
            if state_reads:
                params_desc += f"\nState reads: {', '.join(state_reads)}"
            if state_writes:
                params_desc += f"\nState writes: {', '.join(state_writes)}"

        node_class = step.get("node_class", "vtkMRMLMarkupsFiducialNode")
        node_var = f"_{extension_name.lower()}_{step['step_id']}_id"
        min_points = step.get("min_control_points", 0)

        # UI workflow context
        ui_context = ""
        if self._ui_workflow:
            for sec in self._ui_workflow.get("ui_sections", []):
                for s in sec.get("steps", []):
                    if s.get("step_id") == step.get("step_id") or s.get("logic_method") == method_name:
                        ui_context = f"Button label: '{s.get('button_label', '')}'\nDescription: {s.get('description', '')}"
                        break

        prompt = textwrap.dedent(f"""\
            Generate a Python code snippet for a 3D Slicer extension workflow step.
            This is the POST-INTERACTION part — the user has finished placing control points on a {node_class}.

            Extension: {extension_name}
            Logic class: `{logic_class_name}` (import from `{module_name}`)
            Step: {step.get('step_id', '')}
            Method to call: `{method_name}()`
            {ui_context}

            {params_desc}

            Method source code:
            ```python
            {method_source}
            ```

            Context: The user just placed control points on a markup node. The node ID is stored in variable `{node_var}`.
            Parameter-node role for this interaction, if any: `{step.get('parameter_role') or (step.get('interaction_binding') or {}).get('parameter_name', '')}`.

            The code must:
            1. Import the logic class from `{module_name}`
            2. Retrieve the markup node by its ID: `node = slicer.mrmlScene.GetNodeByID({node_var})`
            3. Validate the user placed enough control points ({min_points} minimum)
            4. Reuse the existing logic instance `_{extension_name.lower()}_logic` if it exists in `dir()`, otherwise create a new `{logic_class_name}()`
            5. Set up any required state on the logic instance BEFORE calling the method (e.g., if the method reads `self.inputMarkupNode`, assign the retrieved node to it)
            6. Call the method `{method_name}()` with correct arguments — pass the markup node if the method expects it
            7. Exit placement mode: `interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")` then `interactionNode.SwitchToViewTransformMode()`
            8. Store the logic instance as `_{extension_name.lower()}_logic` for subsequent steps
            9. Print a completion message with the number of control points
            10. If a non-empty parameter-node role is listed above, call `logic.getParameterNode().SetNodeReferenceID(role, node.GetID())` before later steps need that node.

            IMPORTANT restrictions:
            - Do NOT use `dir()`, `eval()`, `exec()`, `globals()`, or `locals()` — these are blocked in the execution sandbox.
            - Use `try/except NameError` to check if a variable exists, NOT `if 'var' in dir()`.
            - Do NOT use curly brace template placeholders. Write actual Python values (strings, numbers, etc.). If you need a node name, use a hardcoded lookup like `slicer.util.getNode('NodeName')`.
            - Escape all braces in f-strings and .format() calls by doubling them: use doubled-braces for literal braces in output strings.
            - Return ONLY raw Python code. Do NOT wrap it in markdown fences (```python ... ```).""")

        try:
            for _attempt in range(2):
                response = self._call_llm(prompt)
                response = self._strip_markdown_fences(response) if response else None
                if not response or "import" not in response:
                    break
                # Validate syntax immediately — retry once on failure
                import ast as _ast
                try:
                    _ast.parse(response)
                    return response
                except (SyntaxError, IndentationError) as e:
                    if _attempt == 0:
                        logger.info(
                            "LLM post-interaction template for step %s had syntax error: %s. Retrying...",
                            step.get("step_id", "?"), e,
                        )
                        prompt += (
                            f"\n\nYour previous output had a syntax error: {e}\n"
                            "Output ONLY the corrected Python code, no explanation."
                        )
                    else:
                        logger.warning(
                            "LLM post-interaction template for step %s still has syntax error after retry: %s",
                            step.get("step_id", "?"), e,
                        )
                        return response
        except Exception:
            logger.debug("LLM post-interaction template generation failed", exc_info=True)
        return None

    @staticmethod
    def _sanitize_templates(templates: Dict[str, str]) -> Dict[str, str]:
        """Post-generation sanitization of code templates.

        Fixes common LLM output issues that would cause Stage 9 validation
        failures:
        1. Null bytes in generated code
        2. Blocked module imports (sys, os, subprocess, etc.)
        3. Trailing whitespace / mixed line endings
        4. Unexpected indentation (LLM returns indented blocks)
        5. Empty method calls like ``logic.()`` from null method hints

        This runs BEFORE Stage 9 validation and BEFORE the internal LLM
        review, so it catches the most basic issues cheaply without needing
        an LLM revision pass.
        """
        import ast as _ast
        import textwrap as _textwrap

        # Blocked imports — mirror CodeValidator's list
        _BLOCKED_MODULES = {
            "os", "sys", "subprocess", "socket", "shutil",
            "pathlib", "signal", "ctypes", "multiprocessing",
        }
        _BLOCKED_IMPORT_RE = _re.compile(
            r'^(\s*)import\s+(' + "|".join(_BLOCKED_MODULES) + r')\b.*$',
            _re.MULTILINE,
        )
        _BLOCKED_FROM_IMPORT_RE = _re.compile(
            r'^(\s*)from\s+(' + "|".join(_BLOCKED_MODULES) + r')\s+import\b.*$',
            _re.MULTILINE,
        )
        # Empty method call pattern: logic.() or result = logic.()
        _EMPTY_METHOD_CALL_RE = _re.compile(
            r'(\w+)\.\(\)',
        )

        sanitized = {}
        fixes_applied = 0
        for key, code in templates.items():
            if not isinstance(code, str) or not code.strip():
                sanitized[key] = code
                continue

            # Skip non-code entries (workflow.json, etc.)
            if not key.endswith(".py.tpl"):
                sanitized[key] = code
                continue

            original = code

            # 1. Strip null bytes
            code = code.replace("\x00", "")

            # 2. Normalize line endings
            code = code.replace("\r\n", "\n").replace("\r", "\n")

            # 3. Remove blocked module imports
            code = _BLOCKED_FROM_IMPORT_RE.sub(
                lambda m: f"{m.group(1)}# [removed blocked import: {m.group(0).strip()}]",
                code,
            )
            code = _BLOCKED_IMPORT_RE.sub(
                lambda m: f"{m.group(1)}# [removed blocked import: {m.group(0).strip()}]",
                code,
            )

            # 4. Fix indentation: try ast.parse, on failure try dedent
            try:
                _ast.parse(code)
            except (SyntaxError, IndentationError) as e:
                if "indent" in str(e).lower() or "unexpected" in str(e).lower():
                    dedented = _textwrap.dedent(code)
                    try:
                        _ast.parse(dedented)
                        code = dedented
                        logger.info(
                            "[Stage 7] Fixed indentation in '%s' via dedent",
                            key,
                        )
                    except (SyntaxError, IndentationError):
                        # dedent didn't help — leave for revision
                        pass

            # 5. Fix empty method calls: logic.() → # logic.<no method available>()
            if _EMPTY_METHOD_CALL_RE.search(code):
                def _fix_empty_call(m):
                    var = m.group(1)
                    # Only fix if it looks like a method call on a logic/object var
                    if var in ("logic", "_logic", "result"):
                        return f"# {var}.<method>()  # method name not available"
                    return m.group(0)
                code = _EMPTY_METHOD_CALL_RE.sub(_fix_empty_call, code)

            # 6. Detect stub templates (only pass + comments/print)
            _stripped = [
                l.strip() for l in code.split('\n')
                if l.strip() and not l.strip().startswith('#')
            ]
            _non_trivial = [
                l for l in _stripped
                if l != 'pass' and not l.startswith('print(')
            ]
            if not _non_trivial:
                fixes_applied += 1
                logger.warning(
                    "[Stage 7] Template '%s' appears to be a stub "
                    "(only pass/comments). Consider regenerating.",
                    key,
                )

            if code != original:
                fixes_applied += 1
                logger.info(
                    "[Stage 7] Sanitized template '%s'",
                    key,
                )

            sanitized[key] = code

        if fixes_applied:
            logger.info(
                "[Stage 7] Sanitization fixed %d/%d templates",
                fixes_applied, len(templates),
            )

        return sanitized

    # ================================================================
    # Stage 7.5: Live API Probing
    # ================================================================

    @staticmethod
    def _build_var_to_expr_map(code: str) -> Dict[str, str]:
        """Map local variables to the expressions that create them.

        This preserves calls, unlike the old chain extractor.  For example:
            lm = slicer.app.layoutManager()
            lm.setLayout(...)
        is probed as `hasattr(slicer.app.layoutManager(), "setLayout")`.
        """
        import ast as _ast
        var_map: Dict[str, str] = {}
        try:
            tree = _ast.parse(code)
        except (SyntaxError, IndentationError):
            return var_map

        for node in tree.body:
            if not isinstance(node, _ast.Assign):
                continue
            if len(node.targets) != 1 or not isinstance(node.targets[0], _ast.Name):
                continue
            try:
                expr = _ast.unparse(node.value)
            except Exception:
                continue
            var_map[node.targets[0].id] = expr
        return var_map

    @staticmethod
    def _expand_probe_expr(expr: str, var_map: Dict[str, str]) -> str:
        """Inline simple variable assignments inside a receiver expression."""
        import ast as _ast

        class _ReplaceNames(_ast.NodeTransformer):
            def __init__(self):
                self.changed = False

            def visit_Name(self, node):
                if isinstance(node.ctx, _ast.Load) and node.id in var_map:
                    replacement = var_map[node.id]
                    try:
                        repl_node = _ast.parse(f"({replacement})", mode="eval").body
                    except SyntaxError:
                        return node
                    self.changed = True
                    return _ast.copy_location(repl_node, node)
                return node

        expanded = expr
        for _ in range(5):
            try:
                tree = _ast.parse(expanded, mode="eval")
            except SyntaxError:
                return expanded
            replacer = _ReplaceNames()
            tree = replacer.visit(tree)
            _ast.fix_missing_locations(tree)
            if not replacer.changed:
                return expanded
            try:
                new_expanded = _ast.unparse(tree.body)
            except Exception:
                return expanded
            if new_expanded == expanded:
                return expanded
            expanded = new_expanded
        return expanded

    @staticmethod
    def _expr_starts_with_api_root(expr: str) -> bool:
        return bool(_re.match(r'^\s*\(*\s*(slicer|vtk|qt|ctk)\b', expr))

    @staticmethod
    def _make_probe_receiver_safe(expr: str) -> str:
        """Avoid scene mutations while probing receiver objects."""
        import ast as _ast

        class _SafeReceiverCalls(_ast.NodeTransformer):
            def visit_Call(self, node):
                node = self.generic_visit(node)
                if (
                    isinstance(node.func, _ast.Attribute)
                    and node.func.attr == "AddNewNodeByClass"
                    and len(node.args) >= 1
                ):
                    node.func.attr = "CreateNodeByClass"
                    node.args = node.args[:1]
                    node.keywords = []
                return node

        try:
            tree = _ast.parse(expr, mode="eval")
            tree = _SafeReceiverCalls().visit(tree)
            _ast.fix_missing_locations(tree)
            return _ast.unparse(tree.body)
        except Exception:
            return expr

    @staticmethod
    def _extract_api_probe_specs(code: str) -> List[Dict[str, Any]]:
        """Extract receiver-level API probes from template code.

        Pass 1: Extract method call chains (e.g., obj.method()).
        Pass 2: Extract bare attribute accesses (e.g., slicer.vtkMRMLSliceNode.EnumValue).
        """
        import ast as _ast
        try:
            tree = _ast.parse(code)
        except (SyntaxError, IndentationError):
            return []

        var_map = ExtensionCLIAnalyzer._build_var_to_expr_map(code)
        specs: List[Dict[str, Any]] = []
        seen = set()

        # Pass 1: method calls (existing logic)
        for node in _ast.walk(tree):
            if not isinstance(node, _ast.Call) or not isinstance(node.func, _ast.Attribute):
                continue
            attr = node.func.attr
            try:
                receiver_expr = _ast.unparse(node.func.value)
            except Exception:
                continue
            receiver_expr = ExtensionCLIAnalyzer._expand_probe_expr(receiver_expr, var_map)
            receiver_expr = ExtensionCLIAnalyzer._make_probe_receiver_safe(receiver_expr)
            if ".GetDisplayNode()" in receiver_expr:
                continue
            if not ExtensionCLIAnalyzer._expr_starts_with_api_root(receiver_expr):
                continue
            try:
                recv_tree = _ast.parse(receiver_expr, mode="eval")
            except SyntaxError:
                continue
            unresolved = {
                n.id for n in _ast.walk(recv_tree)
                if isinstance(n, _ast.Name) and n.id not in {"slicer", "vtk", "qt", "ctk"}
            }
            if unresolved:
                continue

            chain = f"{receiver_expr}.{attr}"
            key = (receiver_expr, attr)
            if key in seen:
                continue
            seen.add(key)
            specs.append({
                "chain": chain,
                "receiver_expr": receiver_expr,
                "attr": attr,
                "lineno": getattr(node, "lineno", 0),
                "is_attribute": False,
            })

        # Pass 2: bare attribute accesses (e.g., slicer.vtkMRMLSliceNode.SpacingModeMatch2D)
        # These are ast.Attribute nodes that are NOT the func of a Call.
        call_func_ids = set()
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Call) and isinstance(node.func, _ast.Attribute):
                call_func_ids.add(id(node.func))

        for node in _ast.walk(tree):
            if not isinstance(node, _ast.Attribute):
                continue
            if id(node) in call_func_ids:
                continue
            attr = node.attr
            try:
                receiver_expr = _ast.unparse(node.value)
            except Exception:
                continue
            receiver_expr = ExtensionCLIAnalyzer._expand_probe_expr(receiver_expr, var_map)
            if not ExtensionCLIAnalyzer._expr_starts_with_api_root(receiver_expr):
                continue
            # Skip expressions with unresolved locals
            try:
                recv_tree = _ast.parse(receiver_expr, mode="eval")
            except SyntaxError:
                continue
            unresolved = {
                n.id for n in _ast.walk(recv_tree)
                if isinstance(n, _ast.Name) and n.id not in {"slicer", "vtk", "qt", "ctk"}
            }
            if unresolved:
                continue

            chain = f"{receiver_expr}.{attr}"
            key = (receiver_expr, attr)
            if key in seen:
                continue
            seen.add(key)
            specs.append({
                "chain": chain,
                "receiver_expr": receiver_expr,
                "attr": attr,
                "lineno": getattr(node, "lineno", 0),
                "is_attribute": True,
            })

        return specs

    @staticmethod
    def _extract_api_chains(code: str) -> List[str]:
        """Return display names for API calls extracted from template code."""
        return [p["chain"] for p in ExtensionCLIAnalyzer._extract_api_probe_specs(code)]

    def _get_template_purpose(self, tpl_key: str) -> str:
        """Look up a human-readable description for a template from the cookbook."""
        import re as _re
        m = _re.search(r"cb_step_(\d+)", tpl_key)
        if not m:
            return ""
        step_num = int(m.group(1))
        if not self._cookbook_def:
            return ""
        for step in self._cookbook_def.steps:
            if step.step_number == step_num:
                return step.description
        return ""

    @staticmethod
    def _generate_probes(api_specs: List[Dict[str, Any]]) -> List[Dict]:
        """Generate micro-probes that evaluate actual receiver objects.

        For method calls: check hasattr and return available methods.
        For attribute accesses (enums, constants): try to resolve and return
        all public attributes on failure.
        """
        probes = []
        seen = set()
        for spec in api_specs:
            receiver_expr = spec.get("receiver_expr", "")
            attr = spec.get("attr", "")
            is_attr = spec.get("is_attribute", False)
            if not receiver_expr or not attr:
                continue
            key = f"{receiver_expr}.{attr}"
            if key in seen:
                continue
            seen.add(key)

            if is_attr:
                # Attribute access probe: resolve the attribute and catch errors
                probe_code = (
                    f"try:\n"
                    f"    _obj = {receiver_expr}\n"
                    f"    _val = getattr(_obj, '{attr}')\n"
                    f"    __result = {{'exists': True, 'type': type(_val).__name__, 'value_repr': repr(_val)[:80]}}\n"
                    f"except AttributeError as _e:\n"
                    f"    _all = [m for m in dir(_obj) if not m.startswith('_')][:40]\n"
                    f"    __result = {{'exists': False, 'error': str(_e), 'type': type(_obj).__name__, 'available_methods': _all, 'all_attrs': _all}}\n"
                    f"except Exception as _e:\n"
                    f"    __result = {{'error': f'{{type(_e).__name__}}: {{_e}}'}}"
                )
            else:
                # Method call probe: check hasattr and return available methods
                probe_code = (
                    f"try:\n"
                    f"    _obj = {receiver_expr}\n"
                    f"    _exists = _obj is not None and hasattr(_obj, '{attr}')\n"
                    f"    _available = []\n"
                    f"    if not _exists and _obj is not None:\n"
                    f"        _available = [m for m in dir(_obj) if not m.startswith('_')][:40]\n"
                    f"    _all_attrs = [m for m in dir(_obj) if not m.startswith('_')][:80] if _obj else []\n"
                    f"    __result = {{'exists': _exists, 'is_none': _obj is None, 'type': type(_obj).__name__, 'available_methods': _available, 'all_attrs': _all_attrs}}\n"
                    f"except Exception as _e:\n"
                    f"    __result = {{'error': f'{{type(_e).__name__}}: {{_e}}'}}"
                )
            probes.append({
                "chain": key,
                "receiver_expr": receiver_expr,
                "attr": attr,
                "probe_code": probe_code,
                "lineno": spec.get("lineno", 0),
            })

        return probes

    @staticmethod
    def _execute_probe(probe_code: str) -> Any:
        """Execute a probe snippet in Slicer's Python environment.

        Runs in the caller's thread.  Probes may instantiate temporary MRML
        nodes when evaluating receivers such as AddNewNodeByClass(...), so this
        method removes any newly added nodes before returning.
        """
        import slicer as _slicer_mod
        exec_globals = {
            "__builtins__": __builtins__,
            "slicer": _slicer_mod,
            "vtk": globals().get("vtk"),
            "qt": globals().get("qt"),
            "ctk": globals().get("ctk"),
        }

        def _scene_node_ids():
            ids = set()
            try:
                nodes = _slicer_mod.mrmlScene.GetNodes()
                for i in range(nodes.GetNumberOfItems()):
                    node = nodes.GetItemAsObject(i)
                    if node:
                        ids.add(node.GetID())
            except Exception:
                pass
            return ids

        before_ids = _scene_node_ids()
        try:
            exec(probe_code, exec_globals)
            return exec_globals.get("__result", "NO_RESULT")
        except Exception as e:
            return f"EXCEPTION: {e}"
        finally:
            try:
                after_ids = _scene_node_ids()
                for node_id in after_ids - before_ids:
                    node = _slicer_mod.mrmlScene.GetNodeByID(node_id)
                    if node:
                        _slicer_mod.mrmlScene.RemoveNode(node)
            except Exception:
                pass

    def _execute_live_probe(self, probe_code: str) -> Any:
        """Execute a live probe, using the UI-provided main-thread bridge if available."""
        if self._live_probe_executor:
            return self._live_probe_executor(probe_code)
        return self._execute_probe(probe_code)

    def _stage7c_live_api_probe(
        self, templates: Dict[str, str],
    ) -> Dict[str, Any]:
        """Probe generated templates against the live Slicer API.

        For each .py.tpl template, extracts `slicer.*` API calls and
        verifies that the attribute chain exists.  Returns a report of
        failures with available-alternative context for LLM revision.

        Returns:
            {"probed": int, "failures": [...], "revised": int}
        """
        try:
            import slicer as _slicer_mod  # noqa: F401
        except ImportError:
            logger.info(
                "[Stage 7.5] Slicer not available — skipping live API probe"
            )
            return {"probed": 0, "failures": [], "revised": 0}

        self.on_progress(
            "7.5", "Live API Probing",
            "Verifying template API calls against running Slicer..."
        )

        all_specs_by_template = {}
        syntax_skipped = []
        for key, code in templates.items():
            if not key.endswith(".py.tpl") or not code or not code.strip():
                continue
            sample_code = code.replace(
                "{vol_lookup}",
                "inputVolume = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode')"
            )
            sample_code = self._fill_remaining_placeholders(sample_code)
            try:
                ast.parse(sample_code)
            except SyntaxError as exc:
                syntax_skipped.append({"template": key, "error": str(exc)})
                continue
            specs = self._extract_api_probe_specs(sample_code)
            if specs:
                all_specs_by_template[key] = specs

        if not all_specs_by_template:
            return {
                "probed": 0,
                "failures": [],
                "revised": 0,
                "syntax_skipped": syntax_skipped,
            }

        # Collect all unique receiver probes
        all_specs = []
        seen_specs = set()
        for specs in all_specs_by_template.values():
            for spec in specs:
                key = (spec.get("receiver_expr", ""), spec.get("attr", ""))
                if key not in seen_specs:
                    seen_specs.add(key)
                    all_specs.append(spec)

        probes = self._generate_probes(all_specs)
        logger.info(
            "[Stage 7.5] Generated %d probes for %d API calls across %d templates",
            len(probes), len(all_specs), len(all_specs_by_template),
        )

        # Execute probes
        probe_results = {}
        for probe in probes:
            chain_key = probe["chain"]
            result = self._execute_live_probe(probe["probe_code"])
            probe_results[chain_key] = result

        # Analyze results — collect failures
        failures = []
        for chain_key, probe_result in probe_results.items():
            if isinstance(probe_result, dict):
                if probe_result.get("error"):
                    failures.append({
                        "chain": chain_key,
                        "error": probe_result["error"],
                    })
                elif not probe_result.get("exists"):
                    failures.append({
                        "chain": chain_key,
                        "receiver_type": probe_result.get("type"),
                        "receiver_is_none": probe_result.get("is_none"),
                        "available_methods": probe_result.get("available_methods", []),
                    })
            elif isinstance(probe_result, str) and probe_result.startswith("EXCEPTION:"):
                failures.append({
                    "chain": chain_key,
                    "error": probe_result,
                })

        if not failures:
            logger.info("[Stage 7.5] All %d API probes passed", len(probes))
            self.on_progress(
                "7.5", "Live API Probing",
                f"All {len(probes)} API probes passed"
            )
            return {
                "probed": len(probes),
                "failures": [],
                "revised": 0,
                "syntax_skipped": syntax_skipped,
            }

        # Log failures
        logger.warning(
            "[Stage 7.5] %d/%d API probes failed",
            len(failures), len(all_specs),
        )
        for f in failures:
            logger.warning("[Stage 7.5] FAILED: %s", f["chain"])

        # Map failures back to affected templates
        affected_templates = {}
        for tpl_key, specs in all_specs_by_template.items():
            for spec in specs:
                chain = spec.get("chain", "")
                for f in failures:
                    if chain == f["chain"] or chain.startswith(f["chain"] + "."):
                        affected_templates.setdefault(tpl_key, []).append(f)
                        break

        # Revise affected templates via LLM
        revised_count = 0
        unresolved_failures = []
        for tpl_key, tpl_failures in affected_templates.items():
            if tpl_key not in templates:
                continue
            original_code = templates[tpl_key]
            # Look up template purpose from stage_map for better LLM context
            purpose = self._get_template_purpose(tpl_key)
            revised = self._revise_template_for_api(
                tpl_key, original_code, tpl_failures,
                template_purpose=purpose,
            )
            if revised and revised != original_code:
                templates[tpl_key] = revised
                revised_count += 1
                logger.info(
                    "[Stage 7.5] Revised template '%s' for API failures",
                    tpl_key,
                )
            else:
                for failure in tpl_failures:
                    failure_with_template = dict(failure)
                    failure_with_template["template"] = tpl_key
                    unresolved_failures.append(failure_with_template)

        self.on_progress(
            "7.5", "Live API Probing",
            f"Found {len(failures)} API issues, revised {revised_count} templates"
        )
        return {
            "probed": len(probes),
            "failures": failures,
            "revised": revised_count,
            "unresolved_failures": unresolved_failures,
            "syntax_skipped": syntax_skipped,
        }

    def _revise_template_for_api(
        self, template_key: str, code: str, failures: List[Dict],
        template_purpose: str = "",
    ) -> Optional[str]:
        """Ask the LLM to revise a template to fix API failures."""
        failure_descriptions = []
        for f in failures:
            chain = f.get("chain", "")
            failed_attr = chain.rsplit(".", 1)[-1] if "." in chain else chain
            desc = f"API call `{chain}` does NOT EXIST."
            if f.get("receiver_type"):
                desc += f" Receiver type: {f['receiver_type']}."
            if f.get("receiver_is_none"):
                desc += " Receiver evaluated to None."
            # Include all attributes (not just callables) for better LLM context
            all_attrs = f.get("all_attrs") or f.get("available_methods", [])
            if all_attrs and isinstance(all_attrs, list):
                desc += f"\n  All public attributes on the receiver: {all_attrs}"
                # Add close matches: attributes whose names contain parts of the failed attr
                close = [
                    a for a in all_attrs
                    if any(part in a.lower() for part in failed_attr.lower().split("_") if len(part) > 2)
                ]
                if close:
                    desc += f"\n  Close matches for '{failed_attr}': {close}"
            elif "error" in f:
                desc += f" Error: {f['error']}"
            failure_descriptions.append(desc)

        purpose_section = ""
        if template_purpose:
            purpose_section = f"\nTemplate purpose: {template_purpose}\n"

        prompt = textwrap.dedent(f"""\
            The following Python template for 3D Slicer has API errors detected
            by live probing against the running Slicer instance.

            Template file: {template_key}
            {purpose_section}
            API failures:
            {chr(10).join(f'- {fd}' for fd in failure_descriptions)}

            Current template code:
            ```python
            {code}
            ```

            Fix the template so it uses the correct Slicer API.
            Only fix the broken API calls. Do not change the logic or structure.

            When fixing attribute access errors (e.g., incorrect enum values),
            select from the "Close matches" list above. These are attributes on
            the actual receiver object whose names are similar to the failed attribute.

            IMPORTANT restrictions:
            - Do NOT use `os`, `sys`, `subprocess`, `socket`, `shutil`, `pathlib`.
            - Do NOT use `eval()`, `exec()`, `open()`, `getattr()` on user input.
            - Do NOT use `dir()`, `globals()`, `locals()`.
            - Use `try/except NameError` to check variable existence.
            - Return ONLY raw Python code. Do NOT wrap in markdown fences.
        """)

        try:
            for _attempt in range(2):
                response = self._call_llm(prompt)
                response = self._strip_markdown_fences(response) if response else None
                if not response:
                    break
                import ast as _ast
                try:
                    _ast.parse(response)
                    return response
                except (SyntaxError, IndentationError) as e:
                    if _attempt == 0:
                        prompt += (
                            f"\n\nYour previous output had a syntax error: {e}\n"
                            "Output ONLY the corrected Python code, no explanation."
                        )
                    else:
                        return response
        except Exception:
            logger.debug(
                "[Stage 7.5] LLM revision failed for %s", template_key,
                exc_info=True,
            )
        return None

    def _stage7_generate_templates(
        self,
        extension_name: str,
        stage_map: Dict,
        node_lifecycle: Dict,
        scan_result: Dict,
        logic_analysis: Dict,
        cross_stage_map: Optional[Dict] = None,
        workflow_graph: Optional[Dict] = None,
    ) -> Dict[str, str]:
        """Generate Python code templates for each stage."""
        # Interactive workflow template generation
        if workflow_graph:
            templates = self._generate_workflow_templates(
                extension_name, workflow_graph, scan_result, logic_analysis,
            )
            return self._sanitize_templates(templates)

        stages = stage_map.get("stages", [])
        templates = {}
        if cross_stage_map is None:
            cross_stage_map = {}

        for i, stage in enumerate(stages):
            stage_name = stage["stage_name"]
            self.on_progress(
                7, "Generating code templates",
                f"Generating template for stage '{stage_name}' ({i+1}/{len(stages)})..."
            )

            template = self._generate_single_template(
                extension_name, stage, node_lifecycle, scan_result, logic_analysis,
                stage_index=i, cross_stage_map=cross_stage_map,
            )
            templates[f"{stage_name}.py.tpl"] = template

        # Also generate "full" template if multiple stages
        if len(stages) > 1:
            self.on_progress(
                7, "Generating code templates",
                "Generating combined 'full' template..."
            )
            full_template = self._generate_full_template(
                extension_name, stages, node_lifecycle, scan_result, logic_analysis,
                cross_stage_map=cross_stage_map,
            )
            templates["full.py.tpl"] = full_template

        self.on_progress(
            7, "Generating code templates",
            f"Generated {len(templates)} templates: {list(templates.keys())}"
        )

        return self._sanitize_templates(templates)

    def _stage7b_review_templates(
        self,
        templates: Dict[str, str],
        logic_analysis: Dict,
        node_lifecycle: Dict,
    ) -> Dict[str, str]:
        """LLM review of generated templates against actual method source."""
        self.on_progress(
            7, "Reviewing templates",
            "Sending templates to LLM for correctness review..."
        )

        logic_file = logic_analysis.get("_logic_file", "")
        class_name = logic_analysis.get("class_name", "")
        methods = logic_analysis.get("methods", [])
        reviewed = dict(templates)
        corrections_count = 0

        for tpl_name, tpl_code in templates.items():
            # Extract stage name from template filename
            stage_name = tpl_name.replace(".py.tpl", "")

            # Collect relevant method sources for this stage
            method_sources = []
            for m in methods:
                mname = m["name"]
                # Include method if its name appears in the template
                if f"logic.{mname}(" in tpl_code:
                    src = self._extract_method_source(logic_file, mname)
                    if src:
                        params_str = ", ".join(
                            f"{p['name']}: {p['type']}"
                            for p in m.get("parameters", [])
                        )
                        method_sources.append(
                            f"ACTUAL SIGNATURE: {mname}({params_str})\n"
                            f"Source:\n```python\n{src}\n```"
                        )

            if not method_sources:
                continue

            prompt = textwrap.dedent(f"""\
You are reviewing a generated code template for calling methods of a Slicer extension.

TEMPLATE NAME: {tpl_name}
TEMPLATE CODE:
```python
{tpl_code}
```

ACTUAL METHOD SIGNATURES AND SOURCES:
{chr(10).join(method_sources)}

NODE LIFECYCLE (how the template should create nodes):
{json.dumps(node_lifecycle, indent=2)}

CRITICAL CONSTRAINTS — do NOT violate these:
- Lines containing "slicer.mrmlScene.GetNodeByID(...)" are CROSS-STAGE wiring
  that resolves parameters from earlier pipeline stages by immutable node ID.
  Do NOT replace them with CreateNodeByClass/AddNewNodeByClass/slicer.util.getNode.
  They MUST stay as-is.
- Lines containing "_id = " followed by ".GetID()" are node ID caching for cross-stage
  lookups. Do NOT remove or modify them.
- Lines containing "# from prior stage" are variable aliasing in the full pipeline.
  Do NOT replace them.
- Lines containing "CreateNodeByClass" or "AddNewNodeByClass" are intentional node lifecycle
  choices based on AST analysis. Do NOT change the create mode (CreateNodeByClass vs AddNewNodeByClass)
  unless the method clearly does the opposite of what the lifecycle says.
- Lines containing template placeholders like {{param_name}} or {{param_name: default}}
  are dynamic fill points for the runtime template engine. Do NOT replace them with
  hardcoded values (e.g., do NOT change "textPrompts = {{text_prompts}}" to
  "textPrompts = []").
- Double-brace expressions like {{{{expr}}}} inside f-strings are intentional
  literal braces. Do NOT simplify {{{{expr}}}} to
  {{expr}} — that would create an invalid template placeholder.

Verify the template for these issues ONLY:
1. Are all logic.methodName() calls using the CORRECT parameter NAMES and COUNT?
2. Are all variables DEFINED before they are used (no NameError at runtime)?
3. Are boolean parameters set to valid literal values (True/False), not bare variable names?
4. Is the try/except for cached logic correct? (logic should be assigned in the except block, not after it)

Do NOT change: node creation mode, cross-stage wiring, or display setup code.

Return JSON:
{{
  "issues": [
    {{"line": 0, "problem": "description", "fix": "description of fix"}}
  ],
  "corrected_template": "the corrected full template string, or null if no changes needed"
}}

If the template is correct with no issues, return:
{{"issues": [], "corrected_template": null}}""")

            response = self._call_llm(prompt)
            review = self._parse_json_response(response)

            if not review:
                logger.warning("LLM review returned unparseable response for %s", tpl_name)
                continue

            issues = review.get("issues", [])
            corrected = review.get("corrected_template")

            if issues:
                issue_desc = "; ".join(
                    f"L{i.get('line', '?')}: {i.get('problem', '')}" for i in issues
                )
                logger.info("LLM review found %d issue(s) in %s: %s",
                            len(issues), tpl_name, issue_desc)

            if corrected and isinstance(corrected, str) and corrected.strip():
                # Validate the corrected template: fill placeholders then parse
                sample = corrected.replace(
                    "{vol_lookup}",
                    "inputVolume = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode')"
                )
                sample = self._fill_remaining_placeholders(sample)
                try:
                    ast.parse(sample)
                    # Also verify the placeholder is preserved in the raw template
                    if "{vol_lookup}" not in corrected:
                        logger.warning(
                            "LLM correction for %s removed {vol_lookup} placeholder, keeping original",
                            tpl_name,
                        )
                        continue
                    reviewed[tpl_name] = corrected
                    corrections_count += 1
                    logger.info("Applied LLM correction to %s", tpl_name)
                except SyntaxError as e:
                    logger.warning(
                        "LLM correction for %s has syntax error, keeping original: %s",
                        tpl_name, e,
                    )

        syntax_issues = self._syntax_check_templates(reviewed)
        if isinstance(self._workflow_metadata, dict):
            self._workflow_metadata.setdefault("validation_state", {})[
                "stage7_syntax_valid"
            ] = not bool(syntax_issues)
            if syntax_issues:
                self._workflow_metadata["stage7_syntax_issues"] = syntax_issues

        if syntax_issues:
            self.on_progress(
                7, "Reviewing templates",
                f"Found {len(syntax_issues)} syntax issue(s); validation/revision must fix them"
            )
        elif corrections_count:
            self.on_progress(
                7, "Reviewing templates",
                f"LLM corrected {corrections_count} template(s)"
            )
        else:
            self.on_progress(
                7, "Reviewing templates",
                "All templates passed LLM review"
            )

        return reviewed

    def _generate_single_template(
        self,
        extension_name: str,
        stage: Dict,
        node_lifecycle: Dict,
        scan_result: Dict,
        logic_analysis: Dict,
        stage_index: int = 0,
        cross_stage_map: Optional[Dict] = None,
    ) -> str:
        """Generate a code template for a single stage."""
        stage_name = stage["stage_name"]
        method_details = stage.get("method_details", [])
        module_name = os.path.splitext(os.path.basename(scan_result["entry_module"]))[0]
        class_name = logic_analysis["class_name"]
        if cross_stage_map is None:
            cross_stage_map = {}

        stage_cross = cross_stage_map.get(stage_index, {})
        ext_slug = cross_stage_map.get("_extension_name", extension_name).lower()

        # Build node creation / retrieval code
        node_creations = []
        output_param_names = set()
        for m in method_details:
            for p in m.get("parameters", []):
                ptype = p.get("type", "")
                pname = p.get("name", "")
                if "vtkMRML" not in ptype:
                    continue

                # Cross-stage inputs take priority — matched to prior stage outputs
                if pname in stage_cross:
                    src_param = stage_cross[pname]["source_param"]
                    # Use node ID lookup instead of name (methods may rename nodes)
                    node_creations.append(
                        f"{pname} = slicer.mrmlScene.GetNodeByID(_{ext_slug}_{src_param}_id)"
                    )
                    continue

                is_output = (
                    "output" in pname.lower()
                    or "result" in pname.lower()
                    or "out" in pname.lower()
                )
                if not is_output:
                    continue

                output_param_names.add(pname)
                key = f"{m['name']}:{pname}"
                lifecycle = node_lifecycle.get(key, {})
                mode = lifecycle.get("create_mode", "CreateNodeByClass")

                if mode == "CreateNodeByClass":
                    node_creations.append(
                        f"{pname} = slicer.mrmlScene.CreateNodeByClass(\"{ptype}\")"
                    )
                else:
                    node_creations.append(
                        f"{pname} = slicer.mrmlScene.AddNewNodeByClass(\"{ptype}\")"
                    )

        # Build param defaults for all non-vtkMRML, non-progress, non-self params
        param_defaults = []
        # Track which param names are already handled (vtkMRML nodes, inputVolume)
        handled_params = {"self"}
        for m in method_details:
            for p in m.get("parameters", []):
                pname = p.get("name", "")
                ptype = p.get("type", "")
                if "vtkMRML" in ptype:
                    handled_params.add(pname)
                if "progress" in pname.lower() or pname == "qd":
                    handled_params.add(pname)

        # Detect volume param and map to inputVolume
        volume_param_name = None
        for m in method_details:
            for p in m.get("parameters", []):
                pt = p.get("type", "")
                pn = p.get("name", "")
                if pn == "self":
                    continue
                if "vtkMRMLScalarVolumeNode" in pt or "vtkMRMLVolumeNode" in pt:
                    volume_param_name = pn
                    handled_params.add(pn)
                    if pn != "inputVolume":
                        param_defaults.append(f"{pn} = inputVolume  # alias for volume param")
                    break
            if volume_param_name:
                break

        for m in method_details:
            for p in m.get("parameters", []):
                ptype = p.get("type", "")
                pname = p.get("name", "")
                default = p.get("default")
                if pname in handled_params:
                    continue

                # Bool params — optional with detected or True default
                if ptype == "bool":
                    if default is not None:
                        param_defaults.append(f"{pname} = {{{pname}: {default}}}")
                    else:
                        param_defaults.append(f"{pname} = {{{pname}: True}}")
                # Callback / callable params — never fillable from arguments
                elif "callback" in pname.lower() or "callable" in ptype.lower():
                    param_defaults.append(f"{pname} = None")
                # Params with known defaults (from AST analysis)
                elif default is not None:
                    param_defaults.append(f"{pname} = {{{pname}: {default}}}")
                # String params without default → auto-discovery for paths, required otherwise
                elif ptype in ("str", "string"):
                    plower = pname.lower()
                    if "modelpath" in plower or "model_path" in plower:
                        # Auto-discover model path via logic
                        param_defaults.append(
                            f"{pname} = {{{pname}: logic.defaultModelPath() "
                            f"if hasattr(logic, 'defaultModelPath') else ''}}"
                        )
                    elif "path" in plower or "dir" in plower:
                        # Other path params — optional with empty default
                        param_defaults.append(f"{pname} = {{{pname}: ''}}")
                    else:
                        # General string params — required placeholder (LLM must provide)
                        param_defaults.append(f"{pname} = {{{pname}}}")
                # List/array params — required placeholder (LLM must provide the list)
                elif ptype in ("list", "array", "list[str]"):
                    param_defaults.append(f"{pname} = {{{pname}}}")
                # Numeric params — optional with 0 default
                elif ptype in ("int", "float"):
                    param_defaults.append(f"{pname} = {{{pname}: 0}}")
                # Everything else — optional with None default
                else:
                    param_defaults.append(f"{pname} = {{{pname}: None}}")

                handled_params.add(pname)

        # Build method call code
        method_calls = []
        for m in method_details:
            params = m.get("parameters", [])
            param_names = []
            for p in params:
                pn = p["name"]
                if pn == "self":
                    continue
                if "progress" in pn.lower() or pn == "qd":
                    param_names.append("_ProgressStub()")
                elif pn == volume_param_name and volume_param_name != "inputVolume":
                    param_names.append("inputVolume")
                else:
                    param_names.append(pn)
            method_calls.append(
                f"logic.{m['name']}({', '.join(param_names)})"
            )

        # Determine if this stage depends on prior state
        depends_on_prior = bool(stage.get("depends_on"))
        has_state_reads = any(
            m.get("state_reads") for m in method_details
        )

        # Build the template
        lines = [
            f"# --- {extension_name}: {stage_name.replace('_', ' ').title()} ---",
            f"# Auto-generated CLI template for {extension_name}.",
            "",
            "{vol_lookup}",
            "if inputVolume is None:",
            "    raise RuntimeError(\"No volume found in the scene. Load the required data first.\")",
            f'print(f"[{extension_name}] Using volume: {{{{inputVolume.GetName()}}}}")',
            "",
        ]

        # Import
        lines.extend([
            "try:",
            f"    from {module_name} import {class_name}",
            "except ImportError:",
            "    raise RuntimeError(",
            f"        \"{extension_name} extension is not installed. \"",
            "        \"Please install it via Slicer's Extension Manager first.\"",
            "    )",
            "",
        ])

        # State dependency check (only if there's a real prior stage)
        if stage_index > 0 and (depends_on_prior or has_state_reads):
            lines.extend([
                "# Retrieve cached state from prior stage",
                "try:",
                f"    logic = _{extension_name.lower()}Logic",
                "    print(\"Reusing cached logic instance from prior stage.\")",
                "except NameError:",
                f"    logic = {class_name}()",
                "",
            ])

        # Progress stub
        lines.extend([
            "class _ProgressStub:",
            "    def setMaximum(self, v): pass",
            "    def setValue(self, v): pass",
            "",
        ])

        # Logic instantiation (only if not already instantiated in try/except)
        if not (stage_index > 0 and (depends_on_prior or has_state_reads)):
            lines.extend([
                f"logic = {class_name}()",
                "",
            ])

        # Param defaults (boolean etc.)
        if param_defaults:
            for pd in param_defaults:
                lines.append(pd)
            lines.append("")

        # Node creation
        if node_creations:
            lines.append("# Create output nodes")
            for nc in node_creations:
                lines.append(nc)
            lines.append("")

        # Method calls
        lines.append(f"print(\"[{extension_name}] Running {stage_name}...\")")
        for mc in method_calls:
            lines.append(mc)
        lines.append("")

        # Cache state
        state_writes = []
        for m in method_details:
            state_writes.extend(m.get("state_writes", []))
        if state_writes:
            lines.extend([
                "# Cache for potential re-use",
                f"_{extension_name.lower()}Logic = logic",
                "",
            ])

        # Cache node IDs for cross-stage lookups (IDs are immutable, names are not)
        if output_param_names:
            lines.append("# Cache node IDs for subsequent stages")
            for pname in output_param_names:
                lines.append(f"_{ext_slug}_{pname}_id = {pname}.GetID()")
            lines.append("")

        # Display results for output segmentation nodes
        for pname in output_param_names:
            # Find the param type
            for m in method_details:
                for p in m.get("parameters", []):
                    if p["name"] == pname:
                        ptype = p.get("type", "")
                        if "vtkMRMLSegmentationNode" in ptype:
                            lines.extend([
                                f"{pname}.CreateClosedSurfaceRepresentation()",
                                f"_display = {pname}.GetDisplayNode()",
                                "if _display:",
                                "    _display.SetVisibility(True)",
                                "",
                            ])
                        elif "vtkMRMLModelNode" in ptype:
                            lines.extend([
                                f"_display = {pname}.GetDisplayNode()",
                                "if _display is None:",
                                f"    _display = {pname}.CreateDefaultDisplayNode()",
                                "_display.SetVisibility(True)",
                                "",
                            ])

        lines.extend([
            f"print(\"[{extension_name}] {stage_name.replace('_', ' ').title()} complete.\")",
        ])

        return "\n".join(lines)

    def _generate_full_template(
        self,
        extension_name: str,
        stages: List[Dict],
        node_lifecycle: Dict,
        scan_result: Dict,
        logic_analysis: Dict,
        cross_stage_map: Optional[Dict] = None,
    ) -> str:
        """Generate a combined template that runs all stages sequentially."""
        module_name = os.path.splitext(os.path.basename(scan_result["entry_module"]))[0]
        class_name = logic_analysis["class_name"]
        if cross_stage_map is None:
            cross_stage_map = {}

        # Track all created variables across stages for cross-stage wiring
        created_vars = {}  # var_name -> node_class

        lines = [
            f"# --- Full Pipeline: {extension_name} ---",
            f"# Auto-generated CLI template — runs all stages sequentially.",
            "",
            "{vol_lookup}",
            "if inputVolume is None:",
            "    raise RuntimeError(\"No volume found in the scene. Load the required data first.\")",
            f'print(f"[{extension_name}] Using volume: {{{{inputVolume.GetName()}}}}")',
            "",
            "try:",
            f"    from {module_name} import {class_name}",
            "except ImportError:",
            "    raise RuntimeError(",
            f"        \"{extension_name} extension is not installed. \"",
            "        \"Please install it via Slicer's Extension Manager first.\"",
            "    )",
            "",
            "class _ProgressStub:",
            "    def setMaximum(self, v): pass",
            "    def setValue(self, v): pass",
            "",
            f"logic = {class_name}()",
            "",
        ]

        # Collect param defaults across all methods (deduplicated)
        seen_default_names = set()
        all_defaults = []

        # Detect volume param name across all methods
        volume_param_name = None
        for stage in stages:
            for m in stage.get("method_details", []):
                for p in m.get("parameters", []):
                    pt = p.get("type", "")
                    pn = p.get("name", "")
                    if pn == "self":
                        continue
                    if "vtkMRMLScalarVolumeNode" in pt or "vtkMRMLVolumeNode" in pt:
                        if volume_param_name is None:
                            volume_param_name = pn
                        break

        # Track handled params
        handled_defaults = {"self", "inputvolume"}
        for stage in stages:
            for m in stage.get("method_details", []):
                for p in m.get("parameters", []):
                    pname = p.get("name", "")
                    ptype = p.get("type", "")
                    if "vtkMRML" in ptype:
                        handled_defaults.add(pname)
                    if "progress" in pname.lower() or pname == "qd":
                        handled_defaults.add(pname)

        # Volume param alias
        if volume_param_name and volume_param_name != "inputVolume":
            all_defaults.append(f"{volume_param_name} = inputVolume  # alias for volume param")
            handled_defaults.add(volume_param_name)

        for stage in stages:
            for m in stage.get("method_details", []):
                for p in m.get("parameters", []):
                    ptype = p.get("type", "")
                    pname = p.get("name", "")
                    default = p.get("default")
                    if pname in handled_defaults or pname in seen_default_names:
                        continue
                    seen_default_names.add(pname)

                    if ptype == "bool":
                        if default is not None:
                            all_defaults.append(f"{pname} = {default}")
                        else:
                            all_defaults.append(f"{pname} = True")
                    elif "callback" in pname.lower() or "callable" in ptype.lower():
                        all_defaults.append(f"{pname} = None")
                    elif default is not None:
                        all_defaults.append(f"{pname} = {default}")
                    elif ptype in ("str", "string"):
                        plower = pname.lower()
                        if "modelpath" in plower or "model_path" in plower:
                            all_defaults.append(
                                f"{pname} = logic.defaultModelPath() "
                                f'if hasattr(logic, "defaultModelPath") else ""'
                            )
                        else:
                            all_defaults.append(f'{pname} = ""')
                    elif ptype in ("list", "array", "list[str]"):
                        all_defaults.append(f"{pname} = []")
                    elif ptype in ("int", "float"):
                        all_defaults.append(f"{pname} = 0")
                    else:
                        all_defaults.append(f"{pname} = None")
        if all_defaults:
            for d in all_defaults:
                lines.append(d)
            lines.append("")

        # Generate each stage
        for i, stage in enumerate(stages):
            stage_name = stage["stage_name"]
            method_details = stage.get("method_details", [])
            stage_cross = cross_stage_map.get(i, {})

            lines.append(f"# === STAGE {i+1}: {stage_name.replace('_', ' ').title()} ===")

            # Node creations for this stage
            for m in method_details:
                for p in m.get("parameters", []):
                    ptype = p.get("type", "")
                    pname = p.get("name", "")
                    if "vtkMRML" not in ptype:
                        continue
                    # Cross-stage: check if this param matches a prior stage output
                    if pname in stage_cross:
                        src_param = stage_cross[pname]["source_param"]
                        lines.append(f"{pname} = {src_param}  # from prior stage")
                        continue
                    is_output = (
                        "output" in pname.lower()
                        or "result" in pname.lower()
                        or "out" in pname.lower()
                    )
                    if not is_output:
                        continue

                    key = f"{m['name']}:{pname}"
                    lc = node_lifecycle.get(key, {})
                    mode = lc.get("create_mode", "CreateNodeByClass")
                    if mode == "CreateNodeByClass":
                        lines.append(
                            f'{pname} = slicer.mrmlScene.CreateNodeByClass("{ptype}")'
                        )
                    else:
                        lines.append(
                            f'{pname} = slicer.mrmlScene.AddNewNodeByClass("{ptype}")'
                        )
                    created_vars[pname] = ptype

            # Method calls
            for m in method_details:
                params = m.get("parameters", [])
                param_names = []
                for p in params:
                    pn = p["name"]
                    if pn == "self":
                        continue
                    if "progress" in pn.lower() or pn == "qd":
                        param_names.append("_ProgressStub()")
                    elif pn == volume_param_name and volume_param_name != "inputVolume":
                        param_names.append("inputVolume")
                    else:
                        param_names.append(pn)
                lines.append(f"logic.{m['name']}({', '.join(param_names)})")

            lines.append(f"print(f'  Stage {i+1} complete.')")
            lines.append("")

        # Cache
        lines.extend([
            f"_{extension_name.lower()}Logic = logic",
            "",
            f"print(\"[{extension_name}] === Pipeline Complete ===\")",
        ])

        return "\n".join(lines)

    # ================================================================
    # Stage 8: Prompt Fragment Generation (LLM)
    # ================================================================

    def _generate_workflow_prompt_fragment(
        self, extension_name: str, tool_schemas: List[Dict], workflow_graph: Dict,
    ) -> str:
        """Generate prompt fragment for an interactive workflow tool."""
        steps = workflow_graph.get("steps", [])
        tool_name = tool_schemas[0]["function"]["name"] if tool_schemas else extension_name

        # Determine the actual first step ID
        first_step_id = steps[0]["step_id"] if steps else ""

        lines = [
            f"### Interactive Workflow: {extension_name}",
            "",
            f"**Tool name:** `{tool_name}`",
            f"**Type:** Guided interactive workflow",
            "",
            "This tool orchestrates a multi-step workflow where some steps require the user to",
            "perform 3D interactions (drawing curves, positioning planes, placing fiducials).",
            "Execute steps sequentially, ONE STEP PER TURN. After each interactive step, relay instructions to the user",
            "and wait for them to complete the interaction before proceeding.",
            "",
            "**Workflow Steps:**",
        ]

        for i, step in enumerate(steps):
            step_type = step["step_type"]
            op_type = step.get("op_type", "")
            desc = step.get("description", step["step_id"])
            # Cookbook-aware markers
            if step_type == "automated":
                if op_type == "slicer_op":
                    marker = "[automated: slicer_op]"
                elif op_type == "extension_op":
                    marker = "[automated: extension_op]"
                else:
                    marker = "[automated]"
            elif step_type == "interactive":
                marker = "[interactive]"
            elif step_type == "mixed":
                marker = "[mixed: automated + interaction]"
            else:
                marker = "[optional]"
            # Truncate long descriptions for readability
            short_desc = desc.split("\n")[0][:150] if len(desc) > 150 else desc.split("\n")[0]
            lines.append(f"{i+1}. `{step['step_id']}` {marker} — {short_desc}")
            if step_type == "interactive":
                lines.append(f"   - Interaction: {step.get('interaction_type', 'unknown')}")
                if step.get("placement_instructions"):
                    lines.append(f"   - Tell user: {step['placement_instructions'][:200]}")
            elif step_type == "mixed":
                sub_ops = step.get("sub_operations", [])
                for so in sub_ops:
                    so_type = so.get("op_type", "")
                    so_desc = so.get("description", "")[:100]
                    if so_type == "user_interaction":
                        lines.append(f"   - User interaction: {so.get('interaction_type', 'unknown')}")
                        if so.get("placement_instructions"):
                            lines.append(f"   - Tell user: {so['placement_instructions'][:200]}")

        lines.extend([
            "",
            "**Protocol:**",
            f"1. Call `{tool_name}` with `workflow_step='{first_step_id}'` and `user_action='start'` to begin",
            "2. For **automated** steps (extension_op and slicer_op): output the returned `code` verbatim in a ```python block. Then call the next step.",
            "3. For **interactive** steps: output the returned `pre_code` verbatim in a ```python block. Relay instructions to the user. Wait for them to click 'Done'.",
            "4. For **mixed** steps: output the returned `pre_code` verbatim. Then relay interaction instructions. Wait for 'Done'. Then output post_code.",
            "5. For **optional** steps: ask user if they want to proceed. If yes, call with `user_action='start'`. If no, call with `user_action='skip'`.",
            "6. After each step completes, call the tool with the NEXT step's `step_id` and `user_action='start'`.",
            "7. Continue until all steps are done.",
            "",
            "**CRITICAL RULES:**",
            "- Execute ONE step per turn. Do NOT call multiple steps in a single turn.",
            "- Do NOT skip automated steps. Their code MUST be output and executed.",
            "- Always start from step 1 (`" + first_step_id + "`) and proceed in order.",
        ])

        fragment = "\n".join(lines)
        self.on_progress(8, "Generating prompt fragment", "Generated workflow prompt")
        return fragment

    def _stage8_generate_prompt(
        self,
        extension_name: str,
        tool_schemas: List[Dict],
        stage_map: Dict,
        logic_analysis: Dict,
        workflow_graph: Optional[Dict] = None,
    ) -> str:
        """Generate markdown prompt fragment for system prompt injection."""
        self.on_progress(8, "Generating prompt fragment", "Building usage instructions...")

        # Interactive workflow prompt fragment
        if workflow_graph:
            return self._generate_workflow_prompt_fragment(
                extension_name, tool_schemas, workflow_graph,
            )

        stages = stage_map.get("stages", [])
        tool_name = tool_schemas[0]["function"]["name"] if tool_schemas else extension_name

        # Use LLM to generate a user-facing capability summary
        capability = self._llm_capability_summary(extension_name, logic_analysis, stages)

        # Build stage descriptions — one concise line per stage
        # Pick the most "primary" method's purpose for each stage
        stage_lines = []
        for s in stages:
            sname = s["stage_name"]
            stage_desc = self._stage_description(s)
            stage_lines.append(
                f'  - `stage="{sname}"` — {stage_desc}'
            )

        # Build full stage description
        if len(stages) > 1:
            full_line = (
                f'  - `stage="full"` — Run the complete pipeline: '
                + " + ".join(s["stage_name"] for s in stages)
            )
        else:
            full_line = ""

        # Prerequisites
        prereqs = [
            f"{extension_name} Slicer extension must be installed",
            "Required data (e.g., CT volume) must be loaded in the scene",
        ]

        # Check for GPU requirements
        logic_source = logic_analysis.get("_logic_source", "")
        if "torch" in logic_source or "cuda" in logic_source or "gpu" in logic_source.lower():
            prereqs.append("CUDA GPU recommended (CPU fallback may be very slow)")

        # Check for model files
        if "model" in logic_source.lower() and ("load" in logic_source.lower() or "path" in logic_source.lower()):
            prereqs.append("Pre-trained model files must be present in the extension's Resources directory")

        fragment = textwrap.dedent(f"""\
### {extension_name} Extension

- **{extension_name}**: If the user asks to {capability}, call `{tool_name}` with the appropriate `stage` parameter rather than writing custom code.
{chr(10).join(stage_lines)}
{full_line}
  - Prerequisites: {"; ".join(prereqs)}
  **CRITICAL**: After receiving the `{tool_name}` result, your very next response must be exactly one ```agent_plan JSON block followed by one ```python code block containing the tool's `code` string verbatim. Do NOT modify the generated code. Do NOT write analysis or planning text before the code blocks.
""")

        self.on_progress(8, "Generating prompt fragment", "Prompt fragment generated")
        return fragment.strip()

    def _llm_capability_summary(self, extension_name: str, logic_analysis: Dict, stages: List[Dict]) -> str:
        """Use LLM to generate a concise user-facing capability description."""
        methods = logic_analysis.get("methods", [])
        class_name = logic_analysis.get("class_name", "")

        # Collect method names and their docstrings/purposes
        method_info = []
        for m in methods:
            name = m.get("name", "")
            purpose = m.get("purpose", "")
            params = [p.get("name", "") for p in m.get("parameters", []) if p.get("name") != "self"]
            method_info.append(f"- {name}({', '.join(params)}): {purpose}")

        stage_info = []
        for s in stages:
            sname = s.get("stage_name", "")
            sdesc = s.get("description", "")
            method_names = [m.get("name", "") for m in s.get("method_details", [])]
            stage_info.append(f"- Stage '{sname}': {sdesc} (methods: {', '.join(method_names)})")

        prompt = textwrap.dedent(f"""\
You are writing a trigger phrase for a Slicer extension tool.

Extension name: {extension_name}
Logic class: {class_name}

Methods in {class_name}:
{chr(10).join(method_info)}

Pipeline stages:
{chr(10).join(stage_info)}

Task: Write ONE concise sentence (under 20 words) describing what this extension does FROM THE USER'S PERSPECTIVE.
Focus on the END RESULT the user wants (e.g., "segment anatomical structures from CT volumes using text prompts").
Do NOT mention internal steps like installing packages, downloading models, or caching.
Do NOT mention the extension name.

The sentence will be used in this context: "If the user asks to [YOUR SENTENCE], call the tool."

Examples of good outputs:
- "segment bones, organs, or other structures from a CT or MRI volume using text prompts"
- "segment pelvic fractures and plan surgical screw placement"
- "register two volumes using rigid or affine transformation"
- "measure distances and angles between markup points"

Return ONLY the sentence, nothing else.""")

        response = self._call_llm(prompt)
        if response:
            summary = response.strip().strip('"').strip("'")
            # Truncate if too long
            if len(summary) > 150:
                summary = summary[:147] + "..."
            return summary

        # Fallback
        return f"use {extension_name} on a loaded volume"

    @staticmethod
    def _stage_description(stage: Dict) -> str:
        """Generate a concise user-facing description for a single pipeline stage."""
        method_details = stage.get("method_details", [])
        # Find the "primary" method: the one that produces output nodes or
        # has the most relevant name (run, process, segment, etc.)
        primary = None
        for m in method_details:
            name_lower = m.get("name", "").lower()
            if any(kw in name_lower for kw in ("run", "process", "segment", "execute", "perform")):
                primary = m
                break
        if primary is None and method_details:
            primary = method_details[0]

        if primary:
            purpose = primary.get("purpose", "")
            if purpose:
                return purpose

        # Fallback to stage name
        return stage.get("stage_name", "unknown").replace("_", " ")

    # ================================================================
    # Stage 9: Validation + Save
    # ================================================================

    def _stage9_validate(
        self,
        templates: Dict[str, str],
        generators: List[Dict],
        logic_analysis: Optional[Dict] = None,
        api_probe_result: Optional[Dict] = None,
    ) -> Dict:
        """Validate all templates with CodeValidator + semantic checks."""
        self.on_progress(9, "Validating templates", "Running CodeValidator...")

        if not self.code_validator:
            from .CodeValidator import CodeValidator
            self.code_validator = CodeValidator()

        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "per_template": {},
        }

        template_context = self._build_template_validation_context(generators)

        for tpl_name, tpl_content in templates.items():
            # Skip non-Python files (e.g., workflow.json)
            if not tpl_name.endswith((".py.tpl", ".py")):
                continue

            # Fill with sample values for validation
            sample_code = tpl_content.replace(
                "{vol_lookup}",
                "inputVolume = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode')"
            )
            # Fill any remaining placeholders with defaults
            sample_code = self._fill_remaining_placeholders(sample_code)

            # CodeValidator (security + syntax)
            validation = self.code_validator.validate(sample_code)
            if validation.get("destructive_ops"):
                gen = template_context.get(tpl_name, {}).get("generator", {})
                destructive_contract = self._destructive_ops_contract(
                    sample_code,
                    tpl_content,
                    gen,
                    validation.get("destructive_ops", []) or [],
                )
                if destructive_contract.get("allowed"):
                    validation["requires_confirmation"] = bool(
                        destructive_contract.get("scope") != "display_view_scope_reset"
                    )
                    gen["allow_destructive_ops"] = True
                    gen["destructive_ops_contract"] = destructive_contract
                else:
                    validation["valid"] = False
                    reason = (
                        "Template contains destructive operations without an explicit "
                        f"allow_destructive_ops contract: {validation.get('destructive_ops')}"
                    )
                    validation["reason"] = (
                        f"{validation.get('reason')}; {reason}"
                        if validation.get("reason") else reason
                    )

            if "SLICER_OP_GENERATION_FAILED" in sample_code:
                validation["valid"] = False
                reason = "Slicer-op template generation failed due to insufficient retrieval evidence"
                validation["reason"] = (
                    f"{validation.get('reason')}; {reason}"
                    if validation.get("reason") else reason
                )
            if "UNKNOWN_OP_GENERATION_FAILED" in sample_code:
                validation["valid"] = False
                reason = "Operation type could not be proven from extension or Slicer-core evidence"
                validation["reason"] = (
                    f"{validation.get('reason')}; {reason}"
                    if validation.get("reason") else reason
                )

            # Semantic validation (undefined vars, arg count)
            if logic_analysis:
                semantic = self._semantic_validate(sample_code, logic_analysis, api_probe_result=api_probe_result)
                if semantic.get("errors"):
                    validation["valid"] = False
                    existing_reason = validation.get("reason") or ""
                    new_reasons = "; ".join(semantic["errors"])
                    validation["reason"] = (
                        f"{existing_reason}; {new_reasons}" if existing_reason
                        else new_reasons
                    )
                if semantic.get("warnings"):
                    validation.setdefault("warnings", []).extend(semantic["warnings"])

            contract = self._validate_template_contract(
                tpl_name, sample_code, template_context.get(tpl_name), templates,
                raw_code=tpl_content,
            )
            if isinstance(self._workflow_metadata, dict):
                chains = self._extract_api_chains(sample_code)
                if chains:
                    self._workflow_metadata.setdefault("api_evidence", {})[tpl_name] = {
                        "api_chains": chains,
                        "probe_status": (
                            "not_run" if api_probe_result is None
                            else "passed" if not api_probe_result.get("unresolved_failures") else "failed"
                        ),
                    }
            if contract.get("errors"):
                validation["valid"] = False
                existing_reason = validation.get("reason") or ""
                new_reasons = "; ".join(contract["errors"])
                validation["reason"] = (
                    f"{existing_reason}; {new_reasons}" if existing_reason
                    else new_reasons
                )
            if contract.get("warnings"):
                validation.setdefault("warnings", []).extend(contract["warnings"])

            results["per_template"][tpl_name] = validation

            if not validation.get("valid", True):
                results["valid"] = False
                results["errors"].append(
                    f"{tpl_name}: {validation.get('reason', 'unknown error')}"
                )
            if validation.get("warnings"):
                results["warnings"].extend(
                    f"{tpl_name}: {w}" for w in validation.get("warnings", [])
                )

        generator_contract = self._validate_generator_contracts(generators)
        if generator_contract.get("errors"):
            results["valid"] = False
            results["errors"].extend(generator_contract["errors"])
        if generator_contract.get("warnings"):
            results["warnings"].extend(generator_contract["warnings"])

        if api_probe_result:
            unresolved = api_probe_result.get("unresolved_failures")
            if unresolved is None and api_probe_result.get("failures") and not api_probe_result.get("revised"):
                unresolved = api_probe_result.get("failures", [])
            unresolved = unresolved or []
            if unresolved:
                results["valid"] = False
                for failure in unresolved:
                    template = failure.get("template", "unknown template")
                    chain = failure.get("chain", "unknown API")
                    error = failure.get("error") or (
                        "API call does not exist"
                        if not failure.get("receiver_is_none")
                        else "API receiver resolved to None"
                    )
                    results["errors"].append(
                        f"{template}: Unresolved live API probe failure for '{chain}': {error}"
                    )

        if isinstance(self._workflow_metadata, dict):
            static_valid = all(
                item.get("valid", True)
                for item in results.get("per_template", {}).values()
            )
            probe_failures = bool(
                api_probe_result
                and (
                    api_probe_result.get("unresolved_failures")
                    or (
                        api_probe_result.get("failures")
                        and not api_probe_result.get("revised")
                    )
                )
            )
            self._workflow_metadata["validation_state"] = {
                "static_valid": static_valid,
                "api_probe_valid": None if api_probe_result is None else not probe_failures,
                "contract_valid": not bool(
                    generator_contract.get("errors")
                    or any(
                        "Required operation" in e
                        or "operation_model" in e
                        or "extension_op without" in e
                        or "Interaction is owned" in e
                        for e in results.get("errors", [])
                    )
                ),
                "overall_valid": bool(results.get("valid")),
            }

        self.on_progress(
            9, "Validating templates",
            "PASS" if results["valid"] else f"FAIL: {results['errors']}"
        )

        return results

    def _validate_generator_contracts(self, generators: List[Dict]) -> Dict:
        """Validate workflow generator metadata that is not tied to a template."""
        result = {"errors": [], "warnings": []}
        by_step = {
            (gen.get("param_signature", {}) or {}).get("workflow_step", ""): gen
            for gen in generators or []
        }
        for gen in generators or []:
            step_id = gen.get("param_signature", {}).get("workflow_step", "")
            step_type = gen.get("step_type", "")
            operation_model = gen.get("operation_model") or {}
            if step_type and operation_model and operation_model.get("step_type") != step_type:
                result["errors"].append(
                    f"{step_id}: operation_model step_type does not match generator step_type"
                )

            if step_type == "user_choice":
                choice_desc = gen.get("choice_descriptor", {}) or {}
                parameter_name = choice_desc.get("parameter_name", "")
                binding = (
                    choice_desc.get("binding")
                    or self._workflow_metadata.get("choice_bindings", {}).get(step_id, {})
                )
                is_closed_form = self._choice_is_closed_form(choice_desc)
                is_count_like = self._choice_is_count_like(
                    choice_desc,
                    {"description": gen.get("description", "")},
                )
                if parameter_name and not binding and not is_closed_form and not is_count_like:
                    result["warnings"].append(
                        f"{step_id}: user choice '{parameter_name}' has no source-derived parameter binding"
                    )
            if step_type in ("interactive", "mixed"):
                interaction_desc = gen.get("interaction_descriptor", {}) or {}
                node_class = interaction_desc.get("node_class", "")
                if node_class and self._is_markup_node_class(node_class):
                    owner = interaction_desc.get("interaction_owner", "")
                    starter = interaction_desc.get("placement_starter_method", "")
                    if owner == "extension_method" and not starter:
                        result["errors"].append(
                            f"{step_id}: interaction owned by extension method but no placement_starter_method is recorded"
                        )
            repeat_group = (
                gen.get("repeat_group")
                or (gen.get("choice_descriptor") or {}).get("repeat_group")
                or (gen.get("interaction_descriptor") or {}).get("repeat_group")
            )
            if repeat_group and repeat_group.get("interaction_step") == step_id:
                start_gen = by_step.get(repeat_group.get("start_step", ""))
                start_starter = self._generator_placement_starter(start_gen)
                interaction_starter = self._generator_placement_starter(gen)
                interaction_owner = (
                    (gen.get("interaction_descriptor") or {}).get("interaction_owner", "")
                )
                if (
                    interaction_owner != "previous_extension_method"
                    and start_starter
                    and interaction_starter
                    and start_starter == interaction_starter
                ):
                    result["errors"].append(
                        f"{step_id}: repeat interaction and start step both call placement starter '{interaction_starter}'"
                    )
        return result

    @staticmethod
    def _generator_placement_starter(gen: Optional[Dict]) -> str:
        """Return the extension placement starter method recorded on a generator."""
        if not gen:
            return ""
        desc = gen.get("interaction_descriptor") or {}
        if desc.get("placement_starter_method"):
            return desc.get("placement_starter_method", "")
        for so in gen.get("sub_operations", []) or []:
            if so.get("op_type") == "extension_op" and so.get("extension_method_hint"):
                return so.get("extension_method_hint", "")
        return ""

    @staticmethod
    def _build_template_validation_context(generators: List[Dict]) -> Dict[str, Dict]:
        """Map each template file to its workflow generator and role."""
        context = {}
        for gen in generators or []:
            for role, key in (
                ("template", "template_file"),
                ("pre", "pre_template_file"),
                ("post", "post_template_file"),
            ):
                tpl_name = gen.get(key)
                if tpl_name:
                    context[tpl_name] = {"generator": gen, "role": role}
        return context

    def _sync_template_contracts(
        self,
        templates: Dict[str, str],
        generators: List[Dict],
        workflow_graph: Optional[Dict] = None,
    ) -> Dict[str, Dict]:
        """Synchronize deterministic template evidence back into contracts.

        Template revision can repair code, but validation consumes generator and
        workflow metadata.  This pass keeps those representations aligned
        without extension-specific rules.
        """
        context = self._build_template_validation_context(generators)
        workflow_steps = {
            step.get("step_id", ""): step
            for step in (workflow_graph or {}).get("steps", [])
            if isinstance(step, dict)
        }
        sync_report = {
            "extension_functions": [],
            "destructive_contracts": [],
        }

        for tpl_name, raw_code in templates.items():
            if not tpl_name.endswith((".py.tpl", ".py")):
                continue
            ctx = context.get(tpl_name)
            if not ctx:
                continue
            gen = ctx.get("generator", {})
            step_id = (gen.get("param_signature") or {}).get("workflow_step", "")
            workflow_step = workflow_steps.get(step_id)
            sample_code = self._fill_remaining_placeholders(
                raw_code.replace(
                    "{vol_lookup}",
                    "inputVolume = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode')",
                )
            )

            function_name = self._detect_extension_function_call(sample_code)
            if function_name:
                self._record_extension_function_contract(
                    gen, workflow_step, function_name
                )
                sync_report["extension_functions"].append({
                    "template": tpl_name,
                    "function": function_name,
                })

            destructive_ops = self._template_destructive_ops(sample_code)
            if destructive_ops:
                contract = self._destructive_ops_contract(
                    sample_code, raw_code, gen, destructive_ops
                )
                if contract.get("allowed"):
                    gen["allow_destructive_ops"] = True
                    gen["destructive_ops_contract"] = contract
                    if workflow_step is not None:
                        workflow_step["allow_destructive_ops"] = True
                        workflow_step["destructive_ops_contract"] = contract
                    sync_report["destructive_contracts"].append({
                        "template": tpl_name,
                        "ops": destructive_ops,
                        "scope": contract.get("scope", ""),
                    })

            if gen.get("op_type") == "slicer_op" or any(
                so.get("op_type") == "slicer_op"
                for so in (gen.get("sub_operations", []) or [])
            ):
                existing_evidence = gen.get("api_evidence") or {}
                current_evidence = self._build_template_api_evidence(
                    sample_code,
                    gen,
                    source="template_contract_sync",
                )
                if existing_evidence.get("accepted_footprints"):
                    existing_evidence = self._merge_api_evidence([
                        existing_evidence,
                        current_evidence,
                    ])
                else:
                    existing_evidence = current_evidence
                gen["api_evidence"] = existing_evidence
                if workflow_step is not None:
                    workflow_step["api_evidence"] = existing_evidence
                if isinstance(self._workflow_metadata, dict):
                    self._workflow_metadata.setdefault("api_evidence", {})[tpl_name] = existing_evidence

            self._refresh_generator_operation_model(gen, workflow_step)

        if isinstance(self._workflow_metadata, dict):
            self._workflow_metadata["template_contract_sync"] = sync_report
            self._workflow_metadata["operation_model"] = {
                (gen.get("param_signature") or {}).get("workflow_step", ""): gen.get("operation_model", {})
                for gen in generators or []
                if (gen.get("param_signature") or {}).get("workflow_step")
            }
        return sync_report

    @staticmethod
    def _merge_api_evidence(evidence_items: List[Dict]) -> Dict:
        """Merge API evidence records from multiple generated sub-templates."""
        merged = {
            "source": "stage5T",
            "accepted_footprints": [],
            "api_chains": [],
            "operation_descriptions": [],
            "slicer_op_categories": [],
            "slicer_api_keywords": [],
        }
        for evidence in evidence_items:
            if not isinstance(evidence, dict):
                continue
            for key in (
                "accepted_footprints", "api_chains", "operation_descriptions",
                "slicer_op_categories", "slicer_api_keywords",
            ):
                values = evidence.get(key) or []
                if isinstance(values, str):
                    values = [values]
                for value in values:
                    if value and value not in merged[key]:
                        merged[key].append(value)
        return merged

    def _build_template_api_evidence(
        self,
        code: str,
        op_context: Optional[Any] = None,
        source: str = "template",
    ) -> Dict:
        """Build per-template API evidence from generated code and op metadata."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            tree = None

        footprints = []
        local_chains = []
        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    attr = node.func.attr
                    if attr not in footprints:
                        footprints.append(attr)
                    try:
                        chain = ast.unparse(node.func)
                    except Exception:
                        chain = attr
                    if chain and chain not in local_chains:
                        local_chains.append(chain)
                elif isinstance(node, ast.Attribute):
                    attr = node.attr
                    if attr and attr not in footprints:
                        footprints.append(attr)
                elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                    value = node.value
                    if value.startswith("vtkMRML") and value not in footprints:
                        footprints.append(value)

        api_chains = self._extract_api_chains(code)
        for chain in local_chains:
            if chain not in api_chains:
                api_chains.append(chain)

        def _ctx_get(name: str, default=None):
            if isinstance(op_context, dict):
                return op_context.get(name, default)
            return getattr(op_context, name, default)

        sub_ops = _ctx_get("sub_operations", []) or []
        descriptions = []
        categories = []
        keywords = []
        if sub_ops:
            for so in sub_ops:
                if not isinstance(so, dict):
                    continue
                desc = so.get("description")
                category = so.get("slicer_op_category")
                if desc and desc not in descriptions:
                    descriptions.append(desc)
                if category and category not in categories:
                    categories.append(category)
                for keyword in so.get("slicer_api_keywords", []) or []:
                    if keyword and keyword not in keywords:
                        keywords.append(keyword)
        else:
            desc = _ctx_get("description", "")
            category = _ctx_get("slicer_op_category", "")
            if desc:
                descriptions.append(desc)
            if category:
                categories.append(category)
            for keyword in (_ctx_get("slicer_api_keywords", []) or []):
                if keyword and keyword not in keywords:
                    keywords.append(keyword)

        return {
            "source": source,
            "accepted_footprints": sorted(set(footprints)),
            "api_chains": sorted(set(api_chains)),
            "operation_descriptions": descriptions,
            "slicer_op_categories": categories,
            "slicer_api_keywords": keywords,
        }

    def _record_extension_function_contract(
        self,
        gen: Dict,
        workflow_step: Optional[Dict],
        function_name: str,
    ) -> None:
        """Record a top-level extension function in generator/workflow contracts."""
        gen["extension_function_name"] = function_name
        if workflow_step is not None:
            workflow_step["extension_function_name"] = function_name

        for target in (gen, workflow_step):
            if not isinstance(target, dict):
                continue
            for so in target.get("sub_operations", []) or []:
                if (
                    so.get("op_type") == "extension_op"
                    and not so.get("extension_method_hint")
                ):
                    so["extension_function_hint"] = function_name
                    so["evidence_type"] = "module_function"
                    so["evidence_id"] = function_name
                    so["confidence"] = "high"

    def _refresh_generator_operation_model(
        self,
        gen: Dict,
        workflow_step: Optional[Dict],
    ) -> None:
        """Recompute operation models after contract synchronization."""
        source = workflow_step if workflow_step is not None else gen
        operation_model = self._build_step_operation_model(source)
        gen["operation_model"] = operation_model
        if workflow_step is not None:
            workflow_step["operation_model"] = operation_model
        step_id = (gen.get("param_signature") or {}).get("workflow_step", "")
        if step_id and isinstance(self._workflow_metadata, dict):
            self._workflow_metadata.setdefault("operation_model", {})[step_id] = operation_model

    def _detect_extension_function_call(self, code: str) -> str:
        """Return an imported extension module function that is called in code."""
        inventory = (
            self._workflow_metadata.get("extension_callable_inventory", {})
            if isinstance(self._workflow_metadata, dict) else {}
        )
        function_names = set(inventory.get("module_functions", []) or [])
        if not function_names:
            return ""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return ""

        imported = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_name = alias.name
                    local_name = alias.asname or alias.name
                    if imported_name in function_names:
                        imported[local_name] = imported_name
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    local_name = alias.asname or alias.name
                    if local_name in function_names:
                        imported[local_name] = local_name

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id in imported:
                    return imported[func.id]
                if isinstance(func, ast.Attribute) and func.attr in function_names:
                    return func.attr
        return ""

    def _template_destructive_ops(self, code: str) -> List[str]:
        """Extract destructive operations using CodeValidator when available."""
        if not self.code_validator:
            from .CodeValidator import CodeValidator
            self.code_validator = CodeValidator()
        try:
            validation = self.code_validator.validate(code)
            return validation.get("destructive_ops", []) or []
        except Exception:
            return []

    def _syntax_check_templates(self, templates: Dict[str, str]) -> List[Dict[str, str]]:
        """Return syntax issues for Python templates after placeholder filling."""
        issues = []
        for tpl_name, tpl_content in templates.items():
            if not tpl_name.endswith((".py.tpl", ".py")):
                continue
            sample_code = self._fill_remaining_placeholders(
                tpl_content.replace(
                    "{vol_lookup}",
                    "inputVolume = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode')",
                )
            )
            try:
                ast.parse(sample_code)
            except SyntaxError as exc:
                issues.append({
                    "template": tpl_name,
                    "error": str(exc),
                })
        return issues

    @staticmethod
    def _template_has_destructive_allow_comment(raw_code: str) -> bool:
        """Return True when a template declares an explicit destructive contract."""
        for line in raw_code.splitlines()[:10]:
            stripped = line.strip().lower()
            if not stripped.startswith("#"):
                continue
            if "allow_destructive_ops" in stripped and "true" in stripped:
                return True
        return False

    @staticmethod
    def _is_display_view_scope_reset(code: str, destructive_ops: List[str], gen: Dict) -> bool:
        """Return True for display-node view-list resets followed by scoped adds."""
        if not destructive_ops:
            return False
        if any("RemoveAllViewNodeIDs" not in op for op in destructive_ops):
            return False
        if "AddViewNodeID" not in code:
            return False
        categories = {
            so.get("slicer_op_category", "")
            for so in (gen.get("sub_operations", []) or [])
            if isinstance(so, dict)
        }
        if categories and not (categories & {"markups_display", "node_display", "layout_slice_view"}):
            return False
        return True

    def _destructive_ops_contract(
        self,
        code: str,
        raw_code: str,
        gen: Dict,
        destructive_ops: List[str],
    ) -> Dict:
        """Build a typed destructive-operation policy decision."""
        explicit = bool(
            gen.get("allow_destructive_ops")
            or self._template_has_destructive_allow_comment(raw_code)
        )
        display_scope_reset = self._is_display_view_scope_reset(code, destructive_ops, gen)
        allowed = explicit or display_scope_reset
        scope = "display_view_scope_reset" if display_scope_reset else "destructive_operation"
        return {
            "allowed": allowed,
            "explicit": explicit,
            "scope": scope,
            "operations": destructive_ops,
            "reason": (
                "Display node view restrictions are cleared before assigning explicit view IDs."
                if display_scope_reset
                else "Template declares allow_destructive_ops."
                if explicit
                else "No destructive operation contract was found."
            ),
        }

    @staticmethod
    def _template_has_meaningful_code(code: str) -> bool:
        """Return False for required templates that only pass/print/comment."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return True
        for stmt in tree.body:
            if isinstance(stmt, (ast.Import, ast.ImportFrom, ast.Pass)):
                continue
            if (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Name)
                and stmt.value.func.id == "print"
            ):
                continue
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                continue
            return True
        return False

    @staticmethod
    def _template_assigns_name(code: str, name: str) -> bool:
        """Return True if code assigns a variable name directly."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False
        for node in ast.walk(tree):
            targets = []
            if isinstance(node, ast.Assign):
                targets = list(node.targets)
            elif isinstance(node, ast.AnnAssign):
                targets = [node.target]
            elif isinstance(node, ast.AugAssign):
                targets = [node.target]
            for target in targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return True
        return False

    @staticmethod
    def _template_matches_api_evidence(code: str, evidence: Dict) -> bool:
        """Return True if code contains any accepted API evidence footprint."""
        if not isinstance(evidence, dict):
            return False
        code_lower = code.lower()
        footprints = evidence.get("accepted_footprints") or []
        chains = evidence.get("api_chains") or []
        for item in list(footprints) + list(chains):
            if not item:
                continue
            if str(item).lower() in code_lower:
                return True
        return False

    def _validate_template_contract(
        self,
        tpl_name: str,
        code: str,
        context: Optional[Dict],
        templates: Dict[str, str],
        raw_code: Optional[str] = None,
    ) -> Dict:
        """Validate workflow-level contracts that CodeValidator cannot know."""
        result = {"errors": [], "warnings": []}
        if not context:
            return result

        gen = context.get("generator", {})
        role = context.get("role")
        raw_code = raw_code if raw_code is not None else code
        sub_ops = gen.get("sub_operations", []) or []
        api_chains = self._extract_api_chains(code)
        code_has_slicer_api = bool(api_chains)
        for so in sub_ops:
            if so.get("op_type") == "unknown_op":
                result["errors"].append("Required operation has unknown_op classification")
            if so.get("op_type") == "slicer_op" and so.get("confidence") == "low":
                result["errors"].append("Required slicer_op has low classification confidence")
            if (
                so.get("op_type") == "extension_op"
                and not so.get("extension_method_hint")
                and not so.get("extension_function_hint")
                and code_has_slicer_api
            ):
                result["errors"].append(
                    "extension_op without an extension method contains Slicer API calls; "
                    "classify it as slicer_op or bind it to an extension parameter role"
                )

        operation_model = gen.get("operation_model") or {}
        if code_has_slicer_api and not (
            operation_model.get("invokes_slicer_api")
            or operation_model.get("implementation_uses_slicer_api")
        ):
            has_extension_callable = bool(
                gen.get("method_name")
                or gen.get("extension_function_name")
                or any(so.get("extension_method_hint") for so in sub_ops)
                or any(so.get("extension_function_hint") for so in sub_ops)
            )
            if not has_extension_callable:
                result["errors"].append(
                    "Template uses Slicer API calls but operation_model.invokes_slicer_api is false"
                )

        # ── Sub-operation coverage check ──
        # Verify every non-optional, code-generating sub-operation has a code
        # footprint in the template.  user_interaction and user_choice don't
        # generate code in the same template, so skip them.
        if sub_ops and self._template_has_meaningful_code(code):
            for so in sub_ops:
                if so.get("is_optional"):
                    continue
                so_type = so.get("op_type", "")
                # Skip sub-ops that don't contribute code to this template
                if so_type in ("user_interaction", "user_choice"):
                    continue
                so_desc = (so.get("description") or "").lower()
                so_keywords = [k.lower() for k in (so.get("slicer_api_keywords") or [])]
                so_method = so.get("extension_method_hint") or ""
                # Check if the template references this sub-operation
                found = False
                # Check for extension method call
                if so_method and so_method in code:
                    found = True
                so_function = so.get("extension_function_hint") or ""
                if not found and so_function and so_function in code:
                    found = True
                # Check for comment header referencing the description
                if not found:
                    # Extract significant words from description (>4 chars)
                    desc_words = [w for w in so_desc.split() if len(w) > 4]
                    if desc_words:
                        match_count = sum(1 for w in desc_words if w in code.lower())
                        if match_count >= min(2, len(desc_words)):
                            found = True
                # Check for slicer API keywords
                if not found and so_keywords:
                    for kw in so_keywords:
                        if kw and kw in code.lower():
                            found = True
                            break
                # Prefer per-template API evidence discovered during Stage 5T
                # or contract synchronization over broad category fallbacks.
                if not found and so_type == "slicer_op":
                    evidence = gen.get("api_evidence") or {}
                    if self._template_matches_api_evidence(code, evidence):
                        found = True
                # Check for slicer_op_category-specific API patterns
                if not found and so_type == "slicer_op":
                    category = so.get("slicer_op_category", "")
                    _CATEGORY_API_HINTS = {
                        "layout_slice_view": ["setLayout", "SliceVisible", "SetSliceResolutionMode", "SliceResolutionMatch", "SetViewArrangement", "AddLayoutDescription", "GetLayoutByName", "layoutManager"],
                        "module_switching": ["selectModule", "moduleManager"],
                        "markups_display": ["GetDisplayNode", "SetViewNodeID", "AddViewNodeID"],
                        "crosshair": [
                            "Crosshair", "SetCrosshairMode", "ShowIntersection",
                            "SetCrosshairBehavior", "OffsetJumpSlice", "NoCrosshair",
                            "vtkMRMLSliceDisplayNode", "SliceDisplayNode",
                            "SetIntersectingSlicesVisibility",
                            "GetIntersectingSlicesVisibility",
                            "IntersectingSlicesVisibility",
                        ],
                        "node_display": ["SetSliceVisible", "SetVisibility", "GetDisplayNode"],
                    }
                    hints = _CATEGORY_API_HINTS.get(category, [])
                    code_lower = code.lower()
                    for hint in hints:
                        if hint.lower() in code_lower:
                            found = True
                            break
                if not found:
                    result["errors"].append(
                        f"Sub-operation '{so_desc[:60]}' ({so_type}) has no code in template"
                    )
        node_class = (
            gen.get("interaction_descriptor", {}).get("node_class", "")
            if isinstance(gen.get("interaction_descriptor"), dict)
            else ""
        )
        is_markup = self._is_markup_node_class(node_class)

        if "TODO" in code:
            result["errors"].append("Required template contains TODO")
        unresolved_placeholders = [
            p["name"] for p in self._find_template_placeholders(raw_code)
            if p["name"] != "vol_lookup" and not p["has_default"]
        ]
        if unresolved_placeholders:
            result["errors"].append(
                "Required template contains unresolved placeholders: "
                + ", ".join(unresolved_placeholders)
            )
        allow_instruction_only = role == "pre" and node_class and not is_markup
        if not allow_instruction_only and not self._template_has_meaningful_code(code):
            result["errors"].append("Required template is a stub (only pass/comments/prints)")

        if gen.get("step_type") == "user_choice":
            choice_desc = gen.get("choice_descriptor", {}) or {}
            parameter_name = choice_desc.get("parameter_name", "")
            binding = choice_desc.get("binding")
            metadata_binding = self._workflow_metadata.get("choice_bindings", {}).get(
                gen.get("param_signature", {}).get("workflow_step", ""),
                {},
            )
            choices = choice_desc.get("choices", [])
            is_closed_form = self._choice_is_closed_form(choice_desc)
            is_count_like = self._choice_is_count_like(
                choice_desc,
                {"description": gen.get("description", "")},
            )
            if parameter_name and not binding and not metadata_binding and not is_closed_form and not is_count_like:
                result["warnings"].append(
                    f"User choice '{parameter_name}' has no source-derived parameter binding"
                )

        if "GetNumberOfControlPoints(" in code and node_class and not is_markup:
            result["errors"].append(
                f"Template uses Markups control-point API on non-Markups node class '{node_class}'"
            )
        if "SetActiveListID(" in code and node_class and not is_markup:
            result["errors"].append(
                f"Template enters Markups placement mode for non-Markups node class '{node_class}'"
            )

        if role == "post":
            pre_name = gen.get("pre_template_file")
            pre_code = templates.get(pre_name, "") if pre_name else ""
            for var_name in sorted(set(_re.findall(r"\b(_[A-Za-z0-9]+_cb_step_\d+_id)\b", code))):
                if not pre_code:
                    result["errors"].append(
                        f"Post-template references '{var_name}' but has no pre-template"
                    )
                elif not self._template_assigns_name(pre_code, var_name):
                    result["errors"].append(
                        f"Post-template references '{var_name}' but pre-template does not assign it"
                    )

        interaction_desc = gen.get("interaction_descriptor", {}) or {}
        owner = interaction_desc.get("interaction_owner", "")
        if role == "pre" and owner in ("extension_method", "previous_extension_method"):
            if self._template_creates_markup_node(code):
                result["errors"].append(
                    "Interaction is owned by an extension placement method but pre-template creates a new Markups node"
                )

        return result

    @staticmethod
    def _template_creates_markup_node(code: str) -> bool:
        """Return True when code creates a vtkMRMLMarkups* node directly."""
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func_name = ""
            if isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            if func_name not in ("CreateNodeByClass", "AddNewNodeByClass"):
                continue
            if not node.args:
                continue
            arg0 = node.args[0]
            if isinstance(arg0, ast.Constant) and isinstance(arg0.value, str):
                if arg0.value.startswith("vtkMRMLMarkups"):
                    return True
        return False

    @staticmethod
    def _find_template_placeholders(template_str: str) -> List[Dict[str, Any]]:
        """Find single-brace template placeholders outside Python strings."""
        string_ranges = []
        for m in _re.finditer(
            r'(?:[fFrRbBuU]{0,2})("""|\'\'\'|"|\')(.*?)\1',
            template_str,
            _re.DOTALL,
        ):
            string_ranges.append((m.start(), m.end()))

        def _in_string(pos: int) -> bool:
            return any(start <= pos < end for start, end in string_ranges)

        placeholders = []
        i = 0
        while i < len(template_str):
            if template_str.startswith("{{", i):
                i += 2
                continue
            if template_str[i] != "{" or _in_string(i):
                i += 1
                continue
            depth = 0
            j = i
            found = False
            while j < len(template_str):
                if template_str[j] == "{":
                    depth += 1
                elif template_str[j] == "}":
                    depth -= 1
                    if depth == 0:
                        found = True
                        break
                j += 1
            if found:
                inner = template_str[i + 1:j]
                has_default = ":" in inner
                name = inner.split(":", 1)[0].strip()
                if name.isidentifier():
                    placeholders.append({"name": name, "has_default": has_default})
                i = j + 1
            else:
                i += 1
        deduped = {}
        for placeholder in placeholders:
            name = placeholder["name"]
            deduped[name] = {
                "name": name,
                "has_default": deduped.get(name, {}).get("has_default", False)
                or placeholder["has_default"],
            }
        return [deduped[name] for name in sorted(deduped)]

    def _semantic_validate(self, code: str, logic_analysis: Dict,
                           api_probe_result: Optional[Dict] = None) -> Dict:
        """Check for undefined variables, wrong arg counts, invalid node types,
        and cross-reference API chains against live probe failures."""
        result = {"errors": [], "warnings": []}

        try:
            tree = ast.parse(code)
        except SyntaxError:
            result["errors"].append("Syntax error in generated code")
            return result

        # Collect defined names (assignments, imports, function/class defs, for-loop targets)
        defined = set()
        # All Python builtins (functions, constants, exceptions, types)
        import builtins as _builtins
        defined.update(name for name in dir(_builtins) if not name.startswith("_"))
        # Slicer-runtime names that are always available but not in builtins
        defined.update({
            "slicer", "qt", "vtk", "ctk", "inputVolume", "logic",
            "json", "math", "time", "path",
            "_ProgressStub",
        })

        # Collect names from assignments and imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        defined.add(target.id)
                    elif isinstance(target, (ast.Tuple, ast.List)):
                        for elt in target.elts:
                            if isinstance(elt, ast.Name):
                                defined.add(elt.id)
            elif isinstance(node, ast.AugAssign):
                if isinstance(node.target, ast.Name):
                    defined.add(node.target.id)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defined.add(node.name)
                for arg in node.args.args:
                    defined.add(arg.arg)
            elif isinstance(node, ast.ClassDef):
                defined.add(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    defined.add(alias.asname or alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    defined.add(alias.asname or alias.name)
            elif isinstance(node, ast.For):
                if isinstance(node.target, ast.Name):
                    defined.add(node.target.id)
            elif isinstance(node, ast.comprehension):
                if isinstance(node.target, ast.Name):
                    defined.add(node.target.id)
                elif isinstance(node.target, (ast.Tuple, ast.List)):
                    for elt in node.target.elts:
                        if isinstance(elt, ast.Name):
                            defined.add(elt.id)
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                for item in node.items:
                    if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                        defined.add(item.optional_vars.id)
            elif isinstance(node, ast.Try):
                for handler in node.handlers:
                    if handler.name:
                        defined.add(handler.name)

        # Find undefined variables (names used but never defined)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id not in defined and not node.id.startswith("_"):
                    # Skip common patterns
                    if node.id in ("self", "cls"):
                        continue
                    result["errors"].append(f"Undefined variable: '{node.id}'")

        # Check method call arg counts
        method_signatures = {}
        for m in logic_analysis.get("methods", []):
            param_count = len(m.get("parameters", []))
            # Subtract 'self' if present
            params = m.get("parameters", [])
            if params and params[0].get("name") == "self":
                param_count -= 1
            method_signatures[m["name"]] = param_count

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if (isinstance(node.func, ast.Attribute)
                        and isinstance(node.func.value, ast.Name)
                        and node.func.value.id == "logic"
                        and node.func.attr in method_signatures):
                    expected = method_signatures[node.func.attr]
                    actual = len(node.args)
                    if actual != expected:
                        result["errors"].append(
                            f"logic.{node.func.attr}() called with {actual} args, "
                            f"expected {expected}"
                        )

        # Check node class strings are valid MRML types
        valid_prefixes = (
            "vtkMRMLScalar", "vtkMRMLSegmentation", "vtkMRMLModel",
            "vtkMRMLMarkup", "vtkMRMLTransform", "vtkMRMLVolume",
            "vtkMRMLLabelMap", "vtkMRMLTable", "vtkMRMLChart",
            "vtkMRMLView", "vtkMRMLLayout", "vtkMRMLCamera",
            "vtkMRMLClip", "vtkMRMLColor", "vtkMRMLDisplay",
            "vtkMRMLStorage", "vtkMRMLSubjectHierarchy",
            "vtkMRMLCrosshair",
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                if func_name in ("CreateNodeByClass", "AddNewNodeByClass"):
                    for arg in node.args[:1]:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            cls = arg.value
                            if not cls.startswith(valid_prefixes):
                                result["warnings"].append(
                                    f"Unknown MRML node class: '{cls}'"
                                )

        # Cross-check API chains against live probe failures
        if api_probe_result and api_probe_result.get("failures"):
            failed_chains = {f.get("chain", "") for f in api_probe_result["failures"]}
            template_chains = ExtensionCLIAnalyzer._extract_api_chains(code)
            for chain in template_chains:
                for failed in failed_chains:
                    if chain == failed or chain.startswith(failed + "."):
                        result["warnings"].append(
                            f"API chain '{chain}' was flagged by live probe as potentially invalid"
                        )
                        break

        return result

    @staticmethod
    def _fill_remaining_placeholders(code: str) -> str:
        """Fill any remaining {placeholder} or {placeholder: default} patterns with safe defaults."""
        import re
        def _replace(match):
            full = match.group(0)
            name = match.group(1)
            default = match.group(3)  # group 3 = default value (after optional ': ')
            # If the placeholder has an inline default (e.g. {text_prompts: ["seg"]}), use it
            if default is not None:
                return default
            # Common placeholders
            if "name" in name.lower():
                return '"SampleNode"'
            if "radius" in name.lower() or "size" in name.lower():
                return "1.5"
            if "path" in name.lower():
                return '"/tmp/sample"'
            return '""'
        # Replace single-brace placeholders that aren't double-brace escapes.
        # Strategy: use a UUID-based sentinel that cannot collide with regex output.
        # The sentinel must NOT contain { or } so the regex never partially consumes it.
        import uuid
        _L = f"__DBLBRACE_L_{uuid.uuid4().hex}__"
        _R = f"__DBLBRACE_R_{uuid.uuid4().hex}__"
        code = code.replace("{{", _L)
        code = code.replace("}}", _R)
        # Match {name} or {name:default} or {name: default}
        # The colon-space is optional: both {name:val} and {name: val} are accepted.
        code = re.sub(r'\{(\w+)(: *(.*?))?\}', _replace, code)
        # Restore literal braces
        code = code.replace(_L, "{{")
        code = code.replace(_R, "}}")
        return code

    # ================================================================
    # Live Execution Validation (runs on Qt main thread)
    # ================================================================

    @staticmethod
    def live_validate_templates(
        cli_dir: str,
        executor,
        on_progress=None,
    ) -> Dict[str, Dict]:
        """Validate generated templates by executing them in Slicer's Python console.

        Runs each .py.tpl template with safe default placeholder values via
        SafeExecutor.execute(always_rollback=True). The MRML scene is always
        rolled back after each execution regardless of success or failure.

        This method MUST be called on the Qt main thread (where SafeExecutor
        has access to slicer.mrmlScene).

        Args:
            cli_dir: Path to the extension CLI directory (containing templates/).
            executor: A SafeExecutor instance.
            on_progress: Optional callback(idx, total, key, result) called
                after each template is tested.

        Returns:
            Dict mapping template key → {
                "live_valid": bool,
                "error": str or None,
                "output": str,
                "execution_time": float,
            }
        """
        import glob as _glob

        templates_dir = os.path.join(cli_dir, "templates")
        if not os.path.isdir(templates_dir):
            return {}

        # Collect all .py.tpl files
        tpl_files = sorted(_glob.glob(os.path.join(templates_dir, "*.py.tpl")))
        if not tpl_files:
            return {}

        # ── Capture full scene state before validation ──
        # SafeExecutor's always_rollback handles MRML node add/remove,
        # but does NOT restore layout, module, or interaction state.
        # We capture these separately and restore after all templates run.
        _pre_layout = None
        _pre_module = None
        _pre_interaction_node_mode = None
        try:
            lm = slicer.app.layoutManager()
            if lm:
                _pre_layout = lm.layout
        except Exception:
            pass
        try:
            _pre_module = slicer.util.getSelectedModule()
        except Exception:
            pass
        try:
            interactionNode = slicer.mrmlScene.GetNodeByID(
                "vtkMRMLInteractionNodeSingleton"
            )
            if interactionNode:
                _pre_interaction_node_mode = interactionNode.GetCurrentInteractionMode()
        except Exception:
            pass

        results = {}
        total = len(tpl_files)

        for idx, tpl_path in enumerate(tpl_files):
            tpl_key = os.path.relpath(tpl_path, cli_dir)  # e.g. "templates/cb_step_4_pre.py.tpl"
            tpl_name = os.path.basename(tpl_path)

            try:
                with open(tpl_path, "r", encoding="utf-8") as f:
                    raw_code = f.read()
            except Exception as e:
                results[tpl_key] = {
                    "live_valid": False,
                    "error": f"Failed to read template: {e}",
                    "output": "",
                    "execution_time": 0,
                }
                if on_progress:
                    on_progress(idx, total, tpl_key, results[tpl_key])
                continue

            if not raw_code.strip():
                results[tpl_key] = {
                    "live_valid": True,
                    "error": None,
                    "output": "(empty template)",
                    "execution_time": 0,
                }
                if on_progress:
                    on_progress(idx, total, tpl_key, results[tpl_key])
                continue

            # Fill placeholders with safe defaults
            filled_code = ExtensionCLIAnalyzer._fill_remaining_placeholders(raw_code)

            # Wrap in try/except to catch runtime errors cleanly
            wrapped_code = textwrap.dedent(f"""\
                _tpl_validation_error = None
                try:
                    exec({repr(filled_code)})
                except SystemExit:
                    pass  # SystemExit is ok (e.g. sys.exit in tested code)
                except Exception as _e:
                    _tpl_validation_error = f"{{type(_e).__name__}}: {{_e}}"
                """).strip()

            exec_result = executor.execute(wrapped_code, always_rollback=True)

            # Check for execution errors
            error = exec_result.get("error")
            output = exec_result.get("output", "")
            traceback_str = exec_result.get("traceback", "")

            # Also check the captured validation error from the wrapper
            # (runtime errors like AttributeError, ImportError are caught by our wrapper)
            if not error and "_tpl_validation_error" in output:
                # Parse the validation error from stdout
                import re
                m = re.search(r"_tpl_validation_error\s*=\s*(.+)", output)
                if m:
                    val_err = m.group(1).strip().strip('"').strip("'")
                    if val_err and val_err != "None":
                        error = val_err

            # If executor itself reported an error (syntax error, etc.), use that
            if exec_result.get("error") and not error:
                error = exec_result["error"]

            # Also check traceback for useful error info
            if not error and traceback_str:
                # Extract the last line of traceback which has the error type
                tb_lines = traceback_str.strip().split("\n")
                for line in reversed(tb_lines):
                    line = line.strip()
                    if line and not line.startswith("File ") and not line.startswith("Traceback"):
                        error = line
                        break

            results[tpl_key] = {
                "live_valid": error is None,
                "error": error,
                "output": output[:500] if output else "",
                "execution_time": exec_result.get("execution_time", 0),
            }

            if on_progress:
                on_progress(idx, total, tpl_key, results[tpl_key])

        # ── Restore scene state after all templates validated ──
        try:
            if _pre_layout is not None:
                lm = slicer.app.layoutManager()
                if lm and lm.layout != _pre_layout:
                    lm.setLayout(_pre_layout)
        except Exception:
            pass
        try:
            if _pre_module is not None:
                slicer.util.selectModule(_pre_module)
        except Exception:
            pass
        try:
            if _pre_interaction_node_mode is not None:
                interactionNode = slicer.mrmlScene.GetNodeByID(
                    "vtkMRMLInteractionNodeSingleton"
                )
                if interactionNode:
                    interactionNode.SetCurrentInteractionMode(
                        _pre_interaction_node_mode
                    )
        except Exception:
            pass

        return results

    # ================================================================
    # Revision System
    # ================================================================

    _MAX_SOURCE_CONTEXT_CHARS = 400_000

    def _build_revision_source_context(
        self,
        source_path: Optional[str],
        manifest: Dict,
        generators: List[Dict],
    ) -> str:
        """Build source code context for the revision prompt.

        Extracts the logic class method sources and UI file content from
        the extension's source directory.  Method sources are extracted via
        AST so only the relevant class body is included (not the full file).

        Returns a formatted string for the revision prompt, or empty string
        if source_path is not available.
        """
        if not source_path or not os.path.isdir(source_path):
            return ""

        logic_class_name = manifest.get("logic_class_name", "")
        module_name = manifest.get("extension_module_name", "")

        # Find .py and .ui files in the extension source tree
        py_files = []
        ui_files = []
        for root, dirs, files in os.walk(source_path):
            dirs[:] = [d for d in dirs if not d.startswith((".", "__")) and d != "build"]
            for f in files:
                if f.endswith(".py"):
                    py_files.append(os.path.join(root, f))
                elif f.endswith(".ui"):
                    ui_files.append(os.path.join(root, f))

        # Extract logic class method sources
        parts = []
        for py_file in py_files:
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    source = f.read()
                tree = ast.parse(source)
            except Exception:
                continue

            lines = source.split("\n")
            for node in ast.iter_child_nodes(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                # Match the logic class
                if node.name != logic_class_name and not (
                    logic_class_name and node.name.endswith("Logic")
                ):
                    continue

                method_sources = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        start = item.lineno - 1
                        end = (
                            item.end_lineno
                            if hasattr(item, "end_lineno") and item.end_lineno
                            else start + 60
                        )
                        method_src = "\n".join(lines[start:end])
                        method_sources.append(
                            f"  def {item.name}(...):\n"
                            + "\n".join("    " + l for l in method_src.split("\n")[1:])
                        )

                if method_sources:
                    parts.append(
                        f"--- {os.path.basename(py_file)}: class {node.name} ---\n"
                        + "\n\n".join(method_sources)
                    )
                break

        # Include UI file (has parameter node property names, widget names)
        for ui_file in ui_files:
            try:
                with open(ui_file, "r", encoding="utf-8", errors="ignore") as f:
                    ui_content = f.read()
                # Trim UI to just property names and node references (remove layout boilerplate)
                if len(ui_content) > 5000:
                    # Extract lines with objectName, property, node references
                    import re
                    key_lines = []
                    for line in ui_content.split("\n"):
                        stripped = line.strip()
                        if any(kw in stripped for kw in (
                            "objectName", "property", "nodeReference",
                            "MRMLNode", "parameterName", "SetNodeReferenceID",
                            "<property", "<string>", "ctkMRMLNodeComboBox",
                        )):
                            key_lines.append(stripped)
                    if key_lines:
                        ui_content = (
                            "<!-- UI key properties (truncated) -->\n"
                            + "\n".join(key_lines[:200])
                        )
                    else:
                        ui_content = "<!-- UI file present but no key properties found -->"
                parts.append(f"--- {os.path.basename(ui_file)} (UI) ---\n{ui_content}")
            except Exception:
                pass

        combined = "\n\n".join(parts)

        # Truncate if too large
        if len(combined) > self._MAX_SOURCE_CONTEXT_CHARS:
            combined = combined[:self._MAX_SOURCE_CONTEXT_CHARS] + "\n# ... [truncated]"

        return combined

    def _build_revision_prompt_fragment(
        self,
        extension_name: str,
        tool_schemas: List[Dict],
        generators: List[Dict],
    ) -> str:
        """Build a deterministic prompt fragment after successful revision."""
        tool_names = []
        for schema in tool_schemas or []:
            fn = schema.get("function", {}) if isinstance(schema, dict) else {}
            if fn.get("name"):
                tool_names.append(fn["name"])
        if not tool_names:
            tool_names = [extension_name]

        step_lines = []
        for gen in generators or []:
            step = gen.get("param_signature", {}).get("workflow_step", "")
            desc = gen.get("description", "")
            step_type = gen.get("step_type", "automated")
            if step:
                step_lines.append(f"- `{step}` [{step_type}]: {desc}")

        return (
            f"### {extension_name}\n\n"
            f"Generated CLI package status: validated.\n\n"
            f"Available tool: `{tool_names[0]}`.\n\n"
            "Execute cookbook workflow steps in order. For automated steps, run "
            "the returned code. For interactive or mixed steps, run the pre-code, "
            "wait for the user to finish the requested interaction, then run the "
            "post-code.\n\n"
            "Workflow steps:\n"
            + "\n".join(step_lines)
            + "\n"
        )

    def revise(
        self,
        extension_name: str,
        errors: List[str],
        max_attempts: int = _MAX_REVISION_ATTEMPTS,
        source_path: Optional[str] = None,
        logic_analysis: Optional[Dict] = None,
        api_probe_result: Optional[Dict] = None,
    ) -> Dict:
        """
        Revise failed templates using LLM feedback.

        Args:
            extension_name: Name of the CLI to revise.
            errors: List of error messages from validation or testing.
            source_path: Path to the extension's source directory. If provided,
                the logic class source code and UI file are included in the
                revision prompt so the LLM can verify API calls against actual
                method signatures.
            logic_analysis: Optional in-memory logic analysis from the failed
                generation run. When present, semantic validation remains active
                during revision.
            api_probe_result: Optional live API probe result from the failed
                generation run. When present, unresolved live API failures remain
                blocking during revision.

        Returns:
            Dict with 'success', 'validation_result', 'attempts' keys.
        """
        extension_name = _validate_extension_name(extension_name)
        from .ExtensionCLILoader import get_cli_base_dir

        cli_dir = os.path.join(get_cli_base_dir(), extension_name)
        if not os.path.isdir(cli_dir):
            return {"success": False, "error": f"No CLI found for {extension_name}"}

        # Load existing CLI data
        manifest_path = os.path.join(cli_dir, "manifest.json")
        generators_path = os.path.join(cli_dir, "code_generators.json")
        tool_schemas_path = os.path.join(cli_dir, "tool_schemas.json")
        workflow_metadata_path = os.path.join(cli_dir, "workflow_metadata.json")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        with open(generators_path, "r", encoding="utf-8") as f:
            generators = json.load(f)

        workflow_metadata = {}
        if os.path.isfile(workflow_metadata_path):
            try:
                with open(workflow_metadata_path, "r", encoding="utf-8") as f:
                    workflow_metadata = json.load(f)
            except Exception:
                workflow_metadata = {}
        self._workflow_metadata = workflow_metadata

        # Load workflow.json to provide semantic context for revision
        workflow_path = os.path.join(cli_dir, manifest.get("workflow_graph_file", "workflow.json"))
        workflow_steps = {}
        workflow_data = None
        if os.path.isfile(workflow_path):
            try:
                with open(workflow_path, "r", encoding="utf-8") as f:
                    workflow_data = json.load(f)
                for ws in workflow_data.get("steps", []):
                    workflow_steps[ws.get("step_id", "")] = ws
            except Exception:
                pass

        tool_schemas = []
        if os.path.isfile(tool_schemas_path):
            with open(tool_schemas_path, "r", encoding="utf-8") as f:
                tool_schemas = json.load(f)

        # Collect source code context (logic class methods + UI file)
        source_context = self._build_revision_source_context(
            source_path, manifest, generators
        )

        # Repair deterministic workflow contracts before template-only LLM
        # revision.  This lets revision fix stale graph/generator metadata from
        # older failed packages without extension-specific rules.
        if source_path and workflow_data and logic_analysis:
            try:
                scan_result = self._stage1_scan(source_path)
                self._placement_starter_methods = self._classify_placement_starter_methods(
                    logic_analysis
                )
                self._normalize_workflow_contracts(
                    workflow_data, self._workflow_metadata, scan_result, logic_analysis
                )
                _, generators = self._build_workflow_manifest_and_generators(
                    extension_name, scan_result, workflow_data
                )
                with open(workflow_path, "w", encoding="utf-8") as f:
                    json.dump(workflow_data, f, indent=2)
                with open(generators_path, "w", encoding="utf-8") as f:
                    json.dump(generators, f, indent=2)
                with open(workflow_metadata_path, "w", encoding="utf-8") as f:
                    json.dump(self._workflow_metadata, f, indent=2)
                workflow_steps = {
                    ws.get("step_id", ""): ws
                    for ws in workflow_data.get("steps", [])
                }
            except Exception:
                logger.debug("Revision workflow normalization failed", exc_info=True)

        result = {
            "success": False,
            "validation_result": None,
            "attempts": 0,
            "error": None,
        }

        for attempt in range(max_attempts):
            result["attempts"] = attempt + 1
            self.on_progress(
                0, "Revising templates",
                f"Revision attempt {attempt + 1}/{max_attempts}..."
            )

            # Read all templates
            templates = {}
            for gen in generators:
                # Collect all template file references from this generator
                tpl_files = []
                if gen.get("template_file"):
                    tpl_files.append(gen["template_file"])
                if gen.get("pre_template_file"):
                    tpl_files.append(gen["pre_template_file"])
                if gen.get("post_template_file"):
                    tpl_files.append(gen["post_template_file"])
                for tpl_file in tpl_files:
                    tpl_path = os.path.join(cli_dir, tpl_file)
                    if os.path.isfile(tpl_path):
                        with open(tpl_path, "r") as f:
                            templates[tpl_file] = f.read()

            # Build revision prompt
            templates_text = "\n\n".join(
                f"--- {name} ---\n{content}"
                for name, content in templates.items()
            )

            source_section = ""
            if source_context:
                source_section = f"\nEXTENSION SOURCE CODE (use to verify correct API calls):\n{source_context}\n"

            # Build semantic context from workflow.json so the LLM knows what
            # each template is SUPPOSED to do (not just what the stub looks like).
            semantic_section = ""
            if workflow_steps:
                semantic_lines = []
                for tpl_file, tpl_code in templates.items():
                    # Find matching workflow step(s) by template file reference
                    step_id = None
                    # Extract step ID from template filename (e.g., cb_step_5 from templates/cb_step_5.py.tpl)
                    import re as _re_for_tpl
                    m = _re_for_tpl.search(r"(cb_step_\d+)", tpl_file)
                    if m:
                        step_id = m.group(1)
                    ws = workflow_steps.get(step_id) if step_id else None
                    if ws:
                        desc = ws.get("description", "")
                        sub_ops = ws.get("sub_operations", [])
                        sub_ops_text = "\n".join(
                            f"    - [{so.get('op_type')}] {so.get('description')}"
                            for so in sub_ops
                        )
                        semantic_lines.append(
                            f"Template '{tpl_file}' (step {step_id}):\n"
                            f"  Cookbook description: {desc}\n"
                            f"  Required sub-operations:\n{sub_ops_text}"
                        )
                if semantic_lines:
                    semantic_section = (
                        "\nSEMANTIC CONTEXT (what each template should implement):\n"
                        + "\n".join(semantic_lines) + "\n"
                    )

            prompt = textwrap.dedent(f"""\
The following code templates for the "{extension_name}" extension failed validation.
Please fix ALL errors while maintaining the template format (use {{placeholder}} for dynamic values, {{{{ }}}} for literal braces).

ERRORS:
{chr(10).join(f'- {e}' for e in errors)}
{source_section}
{semantic_section}
CONSTRAINTS (CodeValidator):
- BLOCKED: os, subprocess, sys, socket, urllib, http, pickle, ctypes, mmap
- BLOCKED: eval, exec, compile, __import__, open, file, input, getattr, setattr, delattr
- BLOCKED: globals, locals, vars, dir
- ALLOWED: slicer, vtk, qt, ctk, numpy, SimpleITK, math, json, re, copy

TEMPLATES TO FIX:
{templates_text}

Return a JSON object with this structure:
{{
  "templates": {{
    "template_file_name.py.tpl": "fixed template content",
    ...
  }},
  "fix_description": "what was changed and why"
}}

Return ONLY the JSON, no markdown fences.""")

            response = self._call_llm(prompt)
            fixed = self._parse_json_response(response)

            if not fixed or "templates" not in fixed:
                self.on_error(f"Revision attempt {attempt + 1}: LLM returned invalid response")
                continue

            # Save fixed templates — ensure .py.tpl files go into templates/ subdir
            for tpl_name, tpl_content in fixed["templates"].items():
                if tpl_name.endswith(".py.tpl") and not tpl_name.startswith("templates/"):
                    tpl_name = f"templates/{tpl_name}"
                tpl_path = os.path.join(cli_dir, tpl_name)
                os.makedirs(os.path.dirname(tpl_path), exist_ok=True)
                with open(tpl_path, "w", encoding="utf-8") as f:
                    f.write(tpl_content)
                templates[tpl_name] = tpl_content

            # Re-validate
            if not self.code_validator:
                from .CodeValidator import CodeValidator
                self.code_validator = CodeValidator()

            self._sync_template_contracts(
                templates,
                generators,
                workflow_graph=workflow_data,
            )
            with open(generators_path, "w", encoding="utf-8") as f:
                json.dump(generators, f, indent=2)
            if workflow_data is not None:
                with open(workflow_path, "w", encoding="utf-8") as f:
                    json.dump(workflow_data, f, indent=2)
            with open(workflow_metadata_path, "w", encoding="utf-8") as f:
                json.dump(self._workflow_metadata, f, indent=2)

            fresh_probe_result = self._stage7c_live_api_probe(templates)
            for tpl_name, tpl_content in templates.items():
                tpl_path = os.path.join(cli_dir, tpl_name)
                if tpl_name.endswith(".py.tpl") and os.path.isfile(tpl_path):
                    with open(tpl_path, "w", encoding="utf-8") as f:
                        f.write(tpl_content)

            self._sync_template_contracts(
                templates,
                generators,
                workflow_graph=workflow_data,
            )
            with open(generators_path, "w", encoding="utf-8") as f:
                json.dump(generators, f, indent=2)
            if workflow_data is not None:
                with open(workflow_path, "w", encoding="utf-8") as f:
                    json.dump(workflow_data, f, indent=2)
            with open(workflow_metadata_path, "w", encoding="utf-8") as f:
                json.dump(self._workflow_metadata, f, indent=2)

            validation_result = self._stage9_validate(
                templates, generators,
                logic_analysis=logic_analysis,
                api_probe_result=fresh_probe_result,
            )

            if validation_result.get("valid"):
                # Update manifest status
                manifest["status"] = "validated"
                manifest["validation_state"] = self._workflow_metadata.get("validation_state", {})
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, indent=2)
                if os.path.isfile(workflow_metadata_path):
                    with open(workflow_metadata_path, "w", encoding="utf-8") as f:
                        json.dump(self._workflow_metadata, f, indent=2)

                prompt_fragment = self._build_revision_prompt_fragment(
                    extension_name, tool_schemas, generators
                )
                with open(
                    os.path.join(cli_dir, "prompt_fragment.md"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(prompt_fragment)

                # Append to generation log
                log_path = os.path.join(cli_dir, "generation_log.json")
                log_entries = []
                if os.path.isfile(log_path):
                    with open(log_path, "r", encoding="utf-8") as f:
                        log_entries = json.load(f)
                log_entries.append({
                    "attempt": len(log_entries) + 1,
                    "timestamp": datetime.now().isoformat(),
                    "stage": "revision",
                    "trigger": "validation_failure",
                    "error": "; ".join(errors),
                    "fix": fixed.get("fix_description", ""),
                    "api_probe_result": fresh_probe_result,
                    "validation_result": validation_result,
                })
                with open(log_path, "w", encoding="utf-8") as f:
                    json.dump(log_entries, f, indent=2)

                from .ExtensionCLILoader import invalidate_cache
                invalidate_cache()

                result["success"] = True
                result["validation_result"] = validation_result
                return result

            manifest["status"] = "validation_failed"
            manifest["validation_state"] = self._workflow_metadata.get("validation_state", {})
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
            if os.path.isfile(workflow_metadata_path):
                with open(workflow_metadata_path, "w", encoding="utf-8") as f:
                    json.dump(self._workflow_metadata, f, indent=2)
            log_path = os.path.join(cli_dir, "generation_log.json")
            log_entries = []
            if os.path.isfile(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8") as f:
                        log_entries = json.load(f)
                except Exception:
                    log_entries = []
            log_entries.append({
                "attempt": len(log_entries) + 1,
                "timestamp": datetime.now().isoformat(),
                "stage": "revision",
                "trigger": "validation_failure",
                "status": "validation_failed",
                "error": "; ".join(errors),
                "fix": fixed.get("fix_description", ""),
                "api_probe_result": fresh_probe_result,
                "validation_result": validation_result,
            })
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(log_entries, f, indent=2)
            errors = validation_result.get("errors", [])

        manifest["status"] = "validation_failed"
        manifest["validation_state"] = self._workflow_metadata.get("validation_state", {})
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        with open(
            os.path.join(cli_dir, "prompt_fragment.md"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(
                f"### {extension_name}\n\n"
                "Revision failed validation. This CLI package is saved only "
                "for debugging and is not loaded as a runtime tool.\n"
            )

        result["error"] = f"Revision failed after {max_attempts} attempts"
        return result

    # ================================================================
    # Cookbook-Driven Pipeline Helpers
    # ================================================================

    def _find_cookbook(self, extension_name: str) -> Optional[str]:
        """Search for a cookbook .md file for the given extension.

        Looks in Resources/extensions_cookbook/ for {name}.md or
        Slicer{name}.md.

        Returns the path if found, else None.
        """
        module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cookbook_dir = os.path.join(module_dir, "Resources", "extensions_cookbook")
        candidates = [
            os.path.join(cookbook_dir, f"{extension_name}.md"),
            os.path.join(cookbook_dir, f"Slicer{extension_name}.md"),
        ]
        for path in candidates:
            if os.path.isfile(path):
                return path
        return None

    # Optional per-extension keyword map: cookbook description → method hint.
    # Populated by callers via the method_keyword_map constructor parameter.
    _method_keyword_map: Dict[str, str] = {}

    def _match_description_to_method(self, desc_lower: str, method_names: List[str]) -> Optional[str]:
        """Match a cookbook step description to a logic method name.

        Uses the per-extension keyword map (if any) first, then falls back
        to fuzzy word-overlap matching against known method names.

        The scoring normalizes by method name length (sqrt of word count)
        to prevent very long method names from winning simply because
        they contain more words.
        """
        desc_lower = _text_or_empty(desc_lower).lower()
        # Keyword map lookup (per-extension, not hardcoded)
        for keyword, method_hint in self._method_keyword_map.items():
            if keyword in desc_lower:
                matched = self._match_method_name(method_hint, method_names)
                if matched:
                    return matched

        # Fuzzy: extract significant words and try to match
        words = [w for w in desc_lower.split() if len(w) > 3]
        if not words:
            return None
        best_name = None
        best_score = 0.0
        for name in method_names:
            name_lower = name.lower()
            # Raw word overlap count
            raw_hits = sum(1 for w in words if w in name_lower)
            if raw_hits == 0:
                continue
            # Normalize by sqrt of method's word count to penalize very long
            # method names that match many words by sheer length.
            name_word_count = max(len(name.split('_')), 1)
            score = raw_hits / (name_word_count ** 0.5)
            if score > best_score:
                best_score = score
                best_name = name
        # Threshold: require at least 2 raw word hits AND a good normalized score
        if best_score >= 1.5 and best_name is not None:
            # Double-check: verify at least 2 words actually overlap
            raw_check = sum(1 for w in words if w in best_name.lower())
            if raw_check >= 2:
                return best_name
        return None

    def _match_method_name(self, hint: str, available: List[str]) -> Optional[str]:
        """Match a hinted method name to an actual method name (fuzzy).

        Uses exact match, case-insensitive match, then substring containment
        with a length-ratio guard to prevent short hints from matching
        very long method names (e.g., a 4-char hint should not match a
        60-char method via substring containment).
        """
        hint = _optional_text(hint)
        if not hint:
            return None
        if hint in available:
            return hint
        hint_lower = hint.lower()
        # Try case-insensitive exact match
        for name in available:
            if name.lower() == hint_lower:
                return name
        # Try substring containment with length-ratio guard
        # Reject matches where one side is >3x longer than the other,
        # which prevents e.g. "plane" matching
        # "generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible"
        max_ratio = 3.0
        for name in available:
            name_lower = name.lower()
            if hint_lower in name_lower:
                ratio = len(name_lower) / max(len(hint_lower), 1)
                if ratio <= max_ratio:
                    return name
            elif name_lower in hint_lower:
                ratio = len(hint_lower) / max(len(name_lower), 1)
                if ratio <= max_ratio:
                    return name
        return None

    def _build_ui_summary(self, scan_result: Dict) -> str:
        """Build a text summary of UI elements from scan_result."""
        parts = []
        logic = scan_result.get("logic_class", {})
        methods = logic.get("methods", [])
        if methods:
            if isinstance(methods, list):
                # Methods may be strings or dicts
                for m in methods[:30]:
                    if isinstance(m, str):
                        parts.append(f"  method: {m}")
                    elif isinstance(m, dict):
                        parts.append(f"  method: {m.get('name', '?')}")
            elif isinstance(methods, dict):
                for name in list(methods.keys())[:30]:
                    parts.append(f"  method: {name}")
        return "\n".join(parts) if parts else "(no UI info)"

    def _cookbook_build_stage_map(self, cookbook_def, logic_analysis: Dict) -> Dict:
        """Build a stage_map from cookbook steps using keyword heuristics.

        Classifies each cookbook step's operations into sub_operations of type
        extension_op / slicer_op / user_interaction / user_choice using keyword
        heuristics and method name matching against the logic analysis.

        Classification criteria:
        - extension_op: Calls this extension's own Logic methods (code from local source).
        - slicer_op: Uses Slicer core API not in this extension (needs KB search).
        - user_interaction: User physically acts in 3D view (draw, position, drag).
        - user_choice: Agent cannot determine value, must ask user via chat.
        """
        stages = []
        raw_methods = logic_analysis.get("methods", [])
        # Convert list of method dicts to name-keyed dict
        if isinstance(raw_methods, list):
            all_methods = {}
            for m in raw_methods:
                if isinstance(m, dict) and m.get("name"):
                    all_methods[m["name"]] = m
        elif isinstance(raw_methods, dict):
            all_methods = raw_methods
        else:
            all_methods = {}
        method_names = list(all_methods.keys())

        # Keyword heuristics for classification
        #
        # user_choice keywords: steps where the agent cannot determine the
        # answer on its own and must ask the user (patient-specific, case-specific
        # choices, left/right, type selection, checkbox for unknown value).
        _USER_CHOICE_KEYWORDS = {
            "left or right", "left/right", "right side", "left side",
            "choose", "select the", "which side", "which type",
            "segmental", "hemimandibulectomy", "hemimandible",
            "tick the", "check the", "checkbox for",
        }
        # slicer_op keywords: Slicer core API operations NOT in this extension.
        # These need knowledge-base search to generate correct API calls.
        _SLICER_OP_KEYWORDS = {
            "layout", "conventional", "slice visibility", "slice intersection",
            "toggle on", "toggle off", "enable interaction", "open the",
            "module", "markups module", "display panel", "view node",
            "view 1", "red view", "3d view", "set layout",
        }
        # user_interaction keywords: user physically interacts with 3D view.
        _USER_INTERACTION_KEYWORDS = {
            "draw", "click and draw", "click where", "place", "move the",
            "manually adjust", "drag", "position", "create a curve",
            "drawing", "placing", "click in", "click on",
        }

        for step in cookbook_def.steps:
            step_id = f"cb_step_{step.step_number}"
            desc_lower = step.description.lower()

            # Classify sub-operations for this step
            sub_ops = []

            # 0. Check for user_choice FIRST — if the step describes a decision
            #    the agent cannot make on its own (e.g., left/right, type choice),
            #    classify as user_choice before attempting method/keyword matching.
            #    This prevents misclassifying "Tick Right side leg checkbox" as slicer_op.
            user_choice_kw = None
            for kw in _USER_CHOICE_KEYWORDS:
                if kw in desc_lower:
                    user_choice_kw = kw
                    break
            if user_choice_kw:
                # Derive choices and question from the step description
                choices = []
                question = step.description[:200]
                parameter_name = f"choice_step_{step.step_number}"
                if "left" in desc_lower and "right" in desc_lower:
                    choices = [
                        {"label": "Left", "value": "left"},
                        {"label": "Right", "value": "right"},
                    ]
                    parameter_name = "side"
                    question = "Which side? (Left or Right)"
                elif "segmental" in desc_lower and "hemimandibulectomy" in desc_lower:
                    choices = [
                        {"label": "Segmental", "value": "segmental"},
                        {"label": "Hemimandibulectomy", "value": "hemimandibulectomy"},
                    ]
                    parameter_name = "mandibulectomy_type"
                    question = "Which mandibulectomy type?"
                sub_ops.append({
                    "op_type": "user_choice",
                    "description": step.description[:200],
                    "extension_method_hint": None,
                    "slicer_api_keywords": [],
                    "interaction_type": None,
                    "node_class": None,
                    "placement_instructions": None,
                    "question": question,
                    "choices": choices,
                    "parameter_name": parameter_name,
                    "default_value": None,
                    "is_optional": False,
                })

            # 1. Try to match extension methods by keyword extraction from description
            matched_method = self._match_description_to_method(desc_lower, method_names)
            if matched_method:
                m_info = all_methods.get(matched_method, {})
                sub_ops.append({
                    "op_type": "extension_op",
                    "description": step.description[:200],
                    "extension_method_hint": matched_method,
                    "slicer_api_keywords": [],
                    "interaction_type": None,
                    "node_class": None,
                    "placement_instructions": None,
                })

            # 2. Check for slicer_op keywords (layout, view, module changes)
            #    Only Slicer core API operations that need KB search.
            slicer_parts = []
            for kw in _SLICER_OP_KEYWORDS:
                if kw in desc_lower:
                    slicer_parts.append(kw)
            if slicer_parts:
                sub_ops.append({
                    "op_type": "slicer_op",
                    "description": f"Slicer core operations: {', '.join(slicer_parts[:3])}",
                    "extension_method_hint": None,
                    "slicer_api_keywords": slicer_parts[:5],
                    "interaction_type": None,
                    "node_class": None,
                    "placement_instructions": None,
                })

            # 3. Check for user_interaction keywords (drawing, clicking in view)
            interaction_type = None
            for kw in _USER_INTERACTION_KEYWORDS:
                if kw in desc_lower:
                    if "curve" in desc_lower or "draw" in desc_lower:
                        interaction_type = "curve"
                    elif "plane" in desc_lower:
                        interaction_type = "plane"
                    elif "line" in desc_lower:
                        interaction_type = "line"
                    elif "fiducial" in desc_lower or "point" in desc_lower:
                        interaction_type = "fiducial"
                    else:
                        interaction_type = "fiducial"
                    break

            if interaction_type:
                node_class = {
                    "curve": "vtkMRMLMarkupsCurveNode",
                    "plane": "vtkMRMLMarkupsPlaneNode",
                    "line": "vtkMRMLMarkupsLineNode",
                    "fiducial": "vtkMRMLMarkupsFiducialNode",
                }.get(interaction_type)
                sub_ops.append({
                    "op_type": "user_interaction",
                    "description": step.description[:200],
                    "extension_method_hint": None,
                    "slicer_api_keywords": [],
                    "interaction_type": interaction_type,
                    "node_class": node_class,
                    "placement_instructions": step.description[:300],
                })

            # Default: if nothing matched, treat as extension_op
            if not sub_ops:
                sub_ops.append({
                    "op_type": "extension_op",
                    "description": step.description[:200],
                    "extension_method_hint": matched_method,
                    "slicer_api_keywords": [],
                    "interaction_type": None,
                    "node_class": None,
                    "placement_instructions": None,
                })

            # Determine overall step op_type
            op_types = {so["op_type"] for so in sub_ops}
            if len(op_types) > 1:
                stage_op_type = "mixed"
            elif op_types:
                stage_op_type = op_types.pop()
            else:
                stage_op_type = "extension_op"

            # Build stage_methods from matched extension_op sub-operations
            stage_methods = []
            for so in sub_ops:
                if so["op_type"] == "extension_op" and so.get("extension_method_hint"):
                    matched = so["extension_method_hint"]
                    m_info = all_methods.get(matched, {})
                    stage_methods.append({
                        "name": matched,
                        "purpose": so["description"],
                        "parameters": m_info.get("parameters", []),
                        "return_value": m_info.get("return_value"),
                        "state_reads": m_info.get("state_reads", []),
                        "state_writes": m_info.get("state_writes", []),
                        "calls_addnode": m_info.get("calls_addnode", False),
                        "adds_output_to_scene": m_info.get("adds_output_to_scene", False),
                        "side_effects": m_info.get("side_effects", []),
                    })

            # Determine stage name
            stage_method_names = [m["name"] for m in stage_methods] if stage_methods else []
            stage_name = self._infer_stage_name(
                stage_method_names, step.step_number - 1, len(cookbook_def.steps)
            )

            stage = {
                "stage_index": step.step_number - 1,
                "stage_name": stage_name,
                "methods": stage_methods,
                "method_details": stage_methods,
                "depends_on": [
                    f"cb_step_{d}" for d in step.depends_on
                ] if step.depends_on else (
                    [f"cb_step_{step.step_number - 1}"] if step.step_number > 1 else []
                ),
                "input_nodes": [],
                "output_nodes": [],
                "op_type": stage_op_type,
                "cookbook_step": step,
                "sub_operations": sub_ops,
            }
            stages.append(stage)

        return {
            "stages": stages,
            "stage_count": len(stages),
            "source": "cookbook",
        }

    def _build_workflow_from_cookbook(
        self, cookbook_def, logic_analysis: Dict, stage_map: Dict,
    ) -> Dict:
        """Build a workflow.json-compatible dict from cookbook steps.

        Each cookbook step becomes a workflow step with the appropriate
        step_type, op_type, and sub_operations.  Supports all five
        step types: automated, interactive, mixed, branch, user_choice.

        When the stage_map was produced by LLM decomposition (source ==
        "cookbook_llm_decomposition"), the op_type is reused directly
        instead of being re-derived from sub_operations, avoiding
        classification mismatches between the two code paths.
        """
        # Determine if we can trust the decomposition's classification
        from_llm_decomposition = (
            stage_map.get("source") == "cookbook_llm_decomposition"
        )

        steps = []
        for stage in stage_map.get("stages", []):
            cb_step = stage.get("cookbook_step")
            if not cb_step:
                continue

            step_id = f"cb_step_{cb_step.step_number}"
            sub_ops = stage.get("sub_operations", [])
            op_type = stage.get("op_type", "extension_op")
            is_optional = stage.get("is_optional", False)

            # Determine step_type — reuse decomposition's classification when
            # available, otherwise derive from sub_operations.
            if from_llm_decomposition:
                # Trust the LLM decomposition's op_type mapping
                _OP_TYPE_TO_STEP_TYPE = {
                    "extension_op": "automated",
                    "slicer_op": "automated",
                    "user_interaction": "interactive",
                    "user_choice": "user_choice",
                    "unknown_op": "automated",
                    "mixed": "mixed",
                }
                step_type = _OP_TYPE_TO_STEP_TYPE.get(op_type, "automated")
                # Validate "mixed" actually contains interaction/choice sub-ops.
                # A step with only extension_op + slicer_op is not truly mixed.
                if step_type == "mixed":
                    has_user_part = any(
                        so.get("op_type") in ("user_interaction", "user_choice")
                        for so in sub_ops
                    )
                    if not has_user_part:
                        logger.info(
                            "Downgrading step %s from 'mixed' to 'automated' "
                            "(no user_interaction/user_choice sub-ops)",
                            step_id,
                        )
                        step_type = "automated"
                # Apply optional→branch override
                if is_optional and step_type == "automated":
                    step_type = "branch"
            else:
                # Heuristic fallback: derive from sub_operations
                has_interaction = any(so["op_type"] == "user_interaction" for so in sub_ops)
                has_auto = any(so["op_type"] in ("extension_op", "slicer_op", "unknown_op") for so in sub_ops)
                has_choice = any(so["op_type"] == "user_choice" for so in sub_ops)

                if has_choice and not has_interaction:
                    step_type = "user_choice"
                elif is_optional and not has_interaction and not has_choice:
                    step_type = "branch"
                elif has_interaction and has_auto:
                    step_type = "mixed"
                elif has_interaction:
                    step_type = "interactive"
                else:
                    step_type = "automated"

            # Extract interaction info if present
            interaction_info = {}
            for so in sub_ops:
                if so["op_type"] == "user_interaction":
                    node_cls = so.get("node_class")
                    interaction_info = {
                        "interaction_type": _derive_interaction_type(node_cls),
                        "interaction_kind": so.get("interaction_kind") or self._infer_interaction_kind_from_evidence({}, node_cls or ""),
                        "node_class": node_cls or "",
                        "placement_instructions": so.get("placement_instructions", ""),
                        "min_control_points": so.get("min_control_points", 0),
                    }
                    break

            # Extract user_choice info if present
            choice_info = {}
            for so in sub_ops:
                if so["op_type"] == "user_choice":
                    choice_info = {
                        "question": so.get("question", cb_step.description),
                        "choices": so.get("choices", []),
                        "parameter_name": so.get("parameter_name", f"choice_step_{cb_step.step_number}"),
                        "default_value": so.get("default_value"),
                    }
                    break

            # Extract method name for template generation
            method_name = None
            for so in sub_ops:
                if so["op_type"] == "extension_op" and so.get("extension_method_hint"):
                    method_name = so["extension_method_hint"]
                    break

            step = {
                "step_id": step_id,
                "step_type": step_type,
                "op_type": op_type,
                "description": cb_step.description,
                "depends_on": stage.get("depends_on", []),
                "sub_operations": sub_ops,
            }
            if method_name:
                step["method_name"] = method_name
            if interaction_info:
                step.update(interaction_info)
            if choice_info:
                step["choice_info"] = choice_info
            if is_optional:
                step["is_optional"] = True
                if step_type == "branch":
                    step["condition"] = cb_step.description
                    # Find the next non-optional step for the "no" branch
                    stage_idx = stage.get("stage_index", 0)
                    next_steps = [
                        f"cb_step_{s.get('stage_index', 0) + 1}"
                        for s in stage_map.get("stages", [])
                        if s.get("stage_index", 0) > stage_idx
                        and not s.get("is_optional", False)
                    ]
                    step["branches"] = {
                        "yes": step_id,
                        "no": next_steps[0] if next_steps else "",
                    }

            steps.append(step)

        return {
            "steps": steps,
            "step_count": len(steps),
            "source": "cookbook",
        }

    @staticmethod
    def _role_keywords(text: str) -> List[str]:
        """Tokenize camelCase/snake/text identifiers into semantic keywords."""
        text = _text_or_empty(text)
        text = _re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", text)
        text = _re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
        words = _re.findall(r"[A-Za-z][A-Za-z0-9]+", text.lower())
        stop = {
            "the", "and", "for", "with", "node", "select", "choose", "current",
            "which", "what", "option", "step", "user", "choice", "number",
            "many", "want", "manually", "create", "add", "set",
        }
        tokens = [w for w in words if w not in stop and len(w) > 2]
        variants = [w[:6] for w in tokens if len(w) >= 6]
        return list(dict.fromkeys(tokens + variants))

    @staticmethod
    def _guess_node_class_for_role(role: str) -> str:
        """Infer a likely MRML node class from a parameter-node role name."""
        r = _text_or_empty(role).lower()
        if any(
            token in r for token in (
                "number", "count", "checked", "enabled", "visible",
                "show", "use", "lock", "mode", "space", "distance",
                "radius", "height", "width", "length", "tolerance",
            )
        ):
            return ""
        if "segmentation" in r:
            return "vtkMRMLSegmentationNode"
        if "scalarvolume" in r or "volume" in r:
            return "vtkMRMLScalarVolumeNode"
        if "curve" in r:
            return "vtkMRMLMarkupsCurveNode"
        if "line" in r:
            return "vtkMRMLMarkupsLineNode"
        if "plane" in r:
            return "vtkMRMLMarkupsPlaneNode"
        if "fiducial" in r or "point" in r:
            return "vtkMRMLMarkupsFiducialNode"
        if "model" in r:
            return "vtkMRMLModelNode"
        if "transform" in r:
            return "vtkMRMLTransformNode"
        return ""

    @staticmethod
    def _choice_is_count_like(choice: Dict, step: Dict) -> bool:
        """Return True for numeric/count questions, not scene-node selectors."""
        text = " ".join([
            _text_or_empty(choice.get("parameter_name", "")),
            _text_or_empty(choice.get("question", "")),
            _text_or_empty(step.get("description", "")),
        ]).lower()
        return any(
            token in text for token in (
                "how many", "number of", "count", "num", "amount",
            )
        )

    @staticmethod
    def _choice_is_closed_form(choice: Dict) -> bool:
        """Return True for finite non-node choices such as yes/no or left/right.

        Node-selector questions usually have no static choices at generation
        time; the runtime agent discovers scene nodes.  If cookbook parsing
        produced a finite clinical/UI option set, do not infer a scene-node
        binding from overlapping words such as "fibula".
        """
        choices = choice.get("choices") or []
        if not choices:
            return False
        labels = {str(c.get("label", "")).strip().lower() for c in choices}
        values = {str(c.get("value", "")).strip().lower() for c in choices}
        labels_and_values = labels | values
        normalized = {
            _re.sub(r"[^a-z0-9]+", " ", item).strip()
            for item in labels_and_values
            if item
        }
        compact = {item.replace(" ", "") for item in normalized}
        boolean_options = {"yes", "no", "true", "false"}
        side_options = {
            "left", "right", "left leg", "right leg",
            "left side", "right side", "left fibula", "right fibula",
        }
        compact_side_options = {item.replace(" ", "") for item in side_options}
        if normalized <= boolean_options or compact <= boolean_options:
            return True
        if normalized <= side_options or compact <= compact_side_options:
            return True
        choice_text = " ".join([
            _text_or_empty(choice.get("parameter_name", "")),
            _text_or_empty(choice.get("question", "")),
            " ".join(labels_and_values),
        ]).lower()
        node_selector_terms = (
            " node", "segmentation", "volume", "model",
            "markup", "markups", "transform",
        )
        return len(choices) <= 4 and not any(term in choice_text for term in node_selector_terms)

    def _extract_parameter_roles_from_source(self, source: str) -> Dict[str, Dict]:
        """Extract parameter-node role reads/writes from extension Python source."""
        roles: Dict[str, Dict] = {}
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return roles

        def _record(role: str, access: str, method: str = ""):
            if not role:
                return
            entry = roles.setdefault(role, {
                "role": role,
                "accesses": [],
                "methods": [],
                "keywords": self._role_keywords(role),
                "node_class": self._guess_node_class_for_role(role),
            })
            if access not in entry["accesses"]:
                entry["accesses"].append(access)
            if method and method not in entry["methods"]:
                entry["methods"].append(method)

        parent_stack = []
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                setattr(child, "_parent", node)

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func_name = self._get_call_name(node)
            if not func_name:
                continue
            if not any(
                suffix in func_name for suffix in (
                    "GetNodeReference", "SetNodeReferenceID",
                    "GetParameter", "SetParameter",
                )
            ):
                continue
            if not node.args:
                continue
            arg0 = node.args[0]
            if not isinstance(arg0, ast.Constant) or not isinstance(arg0.value, str):
                continue
            method = ""
            parent = getattr(node, "_parent", None)
            while parent is not None:
                if isinstance(parent, ast.FunctionDef):
                    method = parent.name
                    break
                parent = getattr(parent, "_parent", None)
            if "NodeReference" in func_name:
                access = "node_reference_write" if "Set" in func_name else "node_reference_read"
            else:
                access = "parameter_write" if "Set" in func_name else "parameter_read"
            _record(arg0.value, access, method)
        return roles

    def _build_workflow_metadata(
        self, scan_result: Dict, logic_analysis: Dict, workflow_graph: Dict,
    ) -> Dict:
        """Build generic workflow metadata used by templates and runtime dispatch."""
        source = ""
        entry_module = scan_result.get("entry_module", "")
        if entry_module and os.path.isfile(entry_module):
            try:
                with open(entry_module, "r", encoding="utf-8", errors="ignore") as f:
                    source = f.read()
            except Exception:
                source = ""

        bindings = self._extract_parameter_roles_from_source(source)
        metadata = {
            "extension_module_name": os.path.splitext(os.path.basename(entry_module))[0],
            "logic_class_name": scan_result.get("logic_class", {}).get("class_name", ""),
            "metadata_version": 3,
            "parameter_bindings": bindings,
            "choice_bindings": {},
            "interaction_bindings": {},
            "operation_model": {},
            "node_roles": {},
            "repeat_groups": {},
            "validation_state": {
                "static_valid": None,
                "api_probe_valid": None,
                "contract_valid": None,
            },
            "api_evidence": {},
        }

        for step in workflow_graph.get("steps", []):
            step_id = step.get("step_id", "")
            operation_model = self._build_step_operation_model(step)
            metadata["operation_model"][step_id] = operation_model
            step["operation_model"] = operation_model

            choice = step.get("choice_info") or {}
            pname = choice.get("parameter_name")
            can_bind_choice_to_node = not (
                self._choice_is_closed_form(choice)
                or self._choice_is_count_like(choice, step)
            )
            if pname and pname in bindings:
                metadata["choice_bindings"][step_id] = {
                    "parameter_name": pname,
                    "choice_parameter_name": pname,
                    **bindings[pname],
                }
            elif pname and self._choice_is_closed_form(choice):
                choice_text = " ".join([
                    pname,
                    choice.get("question", ""),
                    step.get("description", ""),
                    " ".join(str(c.get("label", "")) for c in choice.get("choices", []) if isinstance(c, dict)),
                ])
                choice_keywords = set(self._role_keywords(choice_text))
                best_role = None
                best_score = 0
                for role, info in bindings.items():
                    if info.get("node_class"):
                        continue
                    role_keywords = set(info.get("keywords", []))
                    score = len(choice_keywords & role_keywords)
                    if score > best_score:
                        best_role = role
                        best_score = score
                if best_role and best_score >= 1:
                    metadata["choice_bindings"][step_id] = {
                        "parameter_name": best_role,
                        "choice_parameter_name": pname,
                        **bindings[best_role],
                    }
            elif pname and can_bind_choice_to_node:
                choice_text = " ".join([
                    pname,
                    choice.get("question", ""),
                    step.get("description", ""),
                ])
                choice_node_class = self._guess_node_class_for_role(choice_text)
                choice_keywords = set(self._role_keywords(choice_text))
                best_role = None
                best_score = 0
                class_candidates = []
                for role, info in bindings.items():
                    if not info.get("node_class"):
                        continue
                    if choice_node_class and info.get("node_class") != choice_node_class:
                        continue
                    class_candidates.append(role)
                    role_keywords = set(info.get("keywords", []))
                    score = len(choice_keywords & role_keywords)
                    if score > best_score:
                        best_role = role
                        best_score = score
                if best_role or (choice_node_class and len(class_candidates) == 1):
                    matched_role = best_role or class_candidates[0]
                    metadata["choice_bindings"][step_id] = {
                        "parameter_name": matched_role,
                        "choice_parameter_name": pname,
                        **bindings[matched_role],
                    }

            node_class = step.get("node_class", "")
            if node_class:
                desc_keywords = set(self._role_keywords(step.get("description", "")))
                best_role = None
                best_score = 0
                for role, info in bindings.items():
                    if info.get("node_class") != node_class:
                        continue
                    role_keywords = set(info.get("keywords", []))
                    score = len(desc_keywords & role_keywords)
                    if score > best_score:
                        best_role = role
                        best_score = score
                if best_role:
                    metadata["interaction_bindings"][step_id] = {
                        "parameter_name": best_role,
                        **bindings[best_role],
                    }
                    step["parameter_role"] = best_role
                    if "do not store" in step.get("description", "").lower():
                        metadata["interaction_bindings"].pop(step_id, None)
                        step.pop("parameter_role", None)

            node_roles = self._infer_step_node_roles(step, metadata)
            if node_roles:
                metadata["node_roles"][step_id] = node_roles
                step["node_roles"] = node_roles

        # Generic repeat detection for "how many" + placement starter + placement interaction.
        steps = workflow_graph.get("steps", [])
        for i, step in enumerate(steps[:-2]):
            choice = step.get("choice_info") or {}
            pname = choice.get("parameter_name", "")
            text = f"{step.get('description', '')} {choice.get('question', '')}".lower()
            if not (
                step.get("step_type") == "user_choice"
                and ("number" in pname.lower() or "count" in pname.lower() or "how many" in text)
            ):
                continue
            auto_step = steps[i + 1]
            interaction_step = steps[i + 2]
            repeat_text = " ".join([
                interaction_step.get("description", ""),
                interaction_step.get("placement_instructions", "") or "",
                " ".join(
                    _text_or_empty(so.get("description", ""))
                    for so in interaction_step.get("sub_operations", [])
                ),
                " ".join(
                    _text_or_empty(so.get("placement_instructions", ""))
                    for so in interaction_step.get("sub_operations", [])
                ),
            ]).lower()
            interaction_has_user_action = (
                interaction_step.get("step_type") == "interactive"
                or (
                    interaction_step.get("step_type") == "mixed"
                    and any(
                        so.get("op_type") == "user_interaction"
                        for so in interaction_step.get("sub_operations", [])
                    )
                )
            )
            interaction_node_classes = [
                interaction_step.get("node_class", ""),
                *[
                    so.get("node_class", "")
                    for so in interaction_step.get("sub_operations", [])
                ],
            ]
            interaction_is_markup_placement = any(
                self._is_markup_node_class(node_class)
                for node_class in interaction_node_classes
            )
            if (
                auto_step.get("step_type") == "automated"
                and interaction_has_user_action
                and interaction_is_markup_placement
                and (
                    any(
                        w in repeat_text
                        for w in (
                            "repeat", "each", "as many", "needed",
                            "per plane", "n times", "requested",
                        )
                    )
                    or self._choice_is_count_like(choice, step)
                )
            ):
                group_id = f"repeat_{step['step_id']}_{auto_step['step_id']}_{interaction_step['step_id']}"
                group = {
                    "group_id": group_id,
                    "count_parameter": pname,
                    "count_step": step["step_id"],
                    "start_step": auto_step["step_id"],
                    "interaction_step": interaction_step["step_id"],
                }
                metadata["repeat_groups"][group_id] = group
                for s in (step, auto_step, interaction_step):
                    s["repeat_group"] = group

        return metadata

    def _build_extension_callable_inventory(
        self, scan_result: Dict, logic_analysis: Dict,
    ) -> Dict[str, Dict]:
        """Collect extension-owned callable targets beyond Logic methods.

        Logic methods remain the preferred target.  Top-level module functions
        are kept as a secondary extension-owned target for workflows such as
        custom layout helpers registered by a scripted module.
        """
        logic_methods = {}
        for method in logic_analysis.get("methods", []) or []:
            if isinstance(method, dict) and method.get("name"):
                logic_methods[method["name"]] = method

        module_functions = {}
        entry_module = scan_result.get("entry_module", "")
        if entry_module and os.path.isfile(entry_module):
            try:
                with open(entry_module, "r", encoding="utf-8", errors="ignore") as f:
                    source = f.read()
                tree = ast.parse(source)
            except Exception:
                tree = None
            if tree is not None:
                for node in tree.body:
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        module_functions[node.name] = {
                            "name": node.name,
                            "line": node.lineno,
                            "source_file": entry_module,
                        }

        return {
            "logic_methods": logic_methods,
            "module_functions": module_functions,
        }

    def _match_extension_function(
        self, description: str, function_names: List[str],
    ) -> Optional[str]:
        """Match an extension-owned module function to a cookbook description."""
        desc_tokens = set(self._role_keywords(description))
        if not desc_tokens:
            return None
        best_name = None
        best_score = 0.0
        for name in function_names:
            name_tokens = set(self._role_keywords(name))
            if not name_tokens:
                continue
            overlap = desc_tokens & name_tokens
            if not overlap:
                continue
            # Prefer concise function names with a direct semantic overlap.
            score = len(overlap) / (len(name_tokens) ** 0.5)
            if "layout" in overlap:
                score += 1.0
            if score > best_score:
                best_score = score
                best_name = name
        if best_name and best_score >= 1.0:
            return best_name

        desc_lower = _text_or_empty(description).lower()
        if "layout" in desc_lower and any(
            word in desc_lower for word in ("custom", "restore", "registered", "view")
        ):
            layout_functions = [
                name for name in function_names
                if "layout" in set(self._role_keywords(name))
            ]
            if len(layout_functions) == 1:
                return layout_functions[0]
        return None

    def _step_placement_starter(self, step: Dict) -> str:
        """Return the placement-starter method a workflow step calls, if any."""
        method = step.get("method_name")
        if method in self._placement_starter_methods:
            return method
        for so in step.get("sub_operations", []) or []:
            hint = so.get("extension_method_hint")
            if hint in self._placement_starter_methods:
                return hint
        return ""

    def _normalize_workflow_contracts(
        self,
        workflow_graph: Dict,
        metadata: Dict,
        scan_result: Dict,
        logic_analysis: Dict,
    ) -> None:
        """Normalize workflow graph/contracts before templates are generated.

        This pass is intentionally deterministic.  It repairs generic workflow
        structure that template revision cannot safely fix, such as duplicate
        repeat placement starters and extension-owned module-level call targets.
        """
        if not workflow_graph:
            return

        metadata = metadata if isinstance(metadata, dict) else {}
        callable_inventory = self._build_extension_callable_inventory(
            scan_result, logic_analysis
        )
        metadata["extension_callable_inventory"] = {
            "logic_methods": sorted(callable_inventory.get("logic_methods", {}).keys()),
            "module_functions": sorted(callable_inventory.get("module_functions", {}).keys()),
        }

        module_function_names = list(callable_inventory.get("module_functions", {}).keys())
        steps = workflow_graph.get("steps", []) or []
        by_step = {step.get("step_id", ""): step for step in steps}

        # Resolve extension-owned module-level functions for extension_op steps
        # that do not map to a Logic method.
        for step in steps:
            if step.get("step_type") not in ("automated", "mixed"):
                continue
            for so in step.get("sub_operations", []) or []:
                if so.get("op_type") != "extension_op":
                    continue
                if so.get("extension_method_hint") or so.get("extension_function_hint"):
                    continue
                description = " ".join([
                    _text_or_empty(step.get("description", "")),
                    _text_or_empty(so.get("description", "")),
                ])
                matched = self._match_extension_function(description, module_function_names)
                if matched:
                    so["extension_function_hint"] = matched
                    so["evidence_type"] = "module_function"
                    so["evidence_id"] = matched
                    so["confidence"] = "high"
                    step["extension_function_name"] = matched

        # Canonicalize count-driven placement repeats.  The starter call belongs
        # to the repeat start step; the following interaction step reuses that
        # node and must not call the same starter again.
        for group in (metadata.get("repeat_groups") or {}).values():
            start_step = by_step.get(group.get("start_step", ""))
            interaction_step = by_step.get(group.get("interaction_step", ""))
            if not start_step or not interaction_step:
                continue
            start_starter = self._step_placement_starter(start_step)
            interaction_starter = self._step_placement_starter(interaction_step)
            if not start_starter or start_starter != interaction_starter:
                continue

            interaction_sub_ops = interaction_step.get("sub_operations", []) or []
            kept_sub_ops = []
            removed_starter = False
            for so in interaction_sub_ops:
                if (
                    so.get("op_type") == "extension_op"
                    and so.get("extension_method_hint") == start_starter
                ):
                    removed_starter = True
                    continue
                kept_sub_ops.append(so)
            if not removed_starter:
                continue

            interaction_step["sub_operations"] = kept_sub_ops
            interaction_step.pop("method_name", None)
            interaction_step["interaction_owner"] = "previous_extension_method"
            interaction_step["placement_starter_method"] = start_starter
            interaction_step["created_node_source"] = "previous_extension_method"

            has_user_interaction = any(
                so.get("op_type") == "user_interaction" for so in kept_sub_ops
            )
            has_code_op = any(
                so.get("op_type") in ("extension_op", "slicer_op", "unknown_op")
                for so in kept_sub_ops
            )
            if has_user_interaction and not has_code_op:
                interaction_step["step_type"] = "interactive"
                interaction_step["op_type"] = "user_interaction"
            elif has_user_interaction:
                interaction_step["step_type"] = "mixed"
                interaction_step["op_type"] = "mixed"

            start_step["interaction_owner"] = "extension_method"
            start_step["placement_starter_method"] = start_starter
            start_step["created_node_source"] = "extension_method"
            metadata.setdefault("interaction_policies", {})[interaction_step["step_id"]] = {
                "interaction_owner": interaction_step["interaction_owner"],
                "placement_starter_method": start_starter,
                "created_node_source": interaction_step["created_node_source"],
            }
            metadata.setdefault("interaction_policies", {})[start_step["step_id"]] = {
                "interaction_owner": start_step["interaction_owner"],
                "placement_starter_method": start_starter,
                "created_node_source": start_step["created_node_source"],
            }

        # Recompute operation and node-role metadata after normalization.
        metadata["operation_model"] = {}
        metadata["node_roles"] = {}
        for step in steps:
            step_id = step.get("step_id", "")
            operation_model = self._build_step_operation_model(step)
            metadata["operation_model"][step_id] = operation_model
            step["operation_model"] = operation_model
            node_roles = self._infer_step_node_roles(step, metadata)
            if node_roles:
                metadata["node_roles"][step_id] = node_roles
                step["node_roles"] = node_roles

    def _build_step_operation_model(self, step: Dict) -> Dict:
        """Describe a workflow step using generic operation semantics."""
        step_type = step.get("step_type", "")
        sub_ops = step.get("sub_operations", []) or []
        op_types = [so.get("op_type", "") for so in sub_ops if so.get("op_type")]
        if step.get("op_type"):
            op_types.append(step.get("op_type"))
        op_types = sorted(set(op_types))

        interaction_kinds = []
        for so in sub_ops:
            if so.get("op_type") == "user_interaction":
                kind = so.get("interaction_kind") or so.get("interaction_type") or "interaction"
                interaction_kinds.append(kind)
        if step_type == "interactive":
            interaction_kinds.append(
                step.get("interaction_kind")
                or step.get("interaction_type")
                or "interaction"
            )

        produces_interaction_state = (
            step_type in ("interactive", "mixed")
            or any(so.get("op_type") == "user_interaction" for so in sub_ops)
        )
        invokes_extension_method = bool(step.get("method_name")) or any(
            so.get("extension_method_hint") for so in sub_ops
        )
        invokes_extension_function = bool(step.get("extension_function_name")) or any(
            so.get("extension_function_hint") for so in sub_ops
        )
        invokes_slicer_api = (
            step.get("op_type") == "slicer_op"
            or any(so.get("op_type") == "slicer_op" for so in sub_ops)
        )
        implementation_uses_slicer_api = bool(
            invokes_slicer_api
            or step_type in ("interactive", "mixed")
            or step.get("interaction_owner")
            or step.get("placement_starter_method")
            or step.get("extension_function_name")
        )
        return {
            "step_type": step_type,
            "op_types": op_types,
            "invokes_extension_method": invokes_extension_method,
            "invokes_extension_function": invokes_extension_function,
            "invokes_slicer_api": invokes_slicer_api,
            "implementation_uses_slicer_api": implementation_uses_slicer_api,
            "produces_interaction_state": produces_interaction_state,
            "interaction_kinds": sorted(set(interaction_kinds)),
        }

    def _infer_step_node_roles(self, step: Dict, metadata: Dict) -> List[Dict]:
        """Infer generic node roles produced or consumed by a workflow step."""
        roles = []
        step_id = step.get("step_id", "")

        def _add(role_kind: str, node_class: str, parameter_name: str = "") -> None:
            if not node_class and not parameter_name:
                return
            roles.append({
                "role_kind": role_kind,
                "step_id": step_id,
                "node_class": node_class or "",
                "parameter_name": parameter_name or "",
            })

        binding = metadata.get("interaction_bindings", {}).get(step_id, {})
        node_class = step.get("node_class", "")
        if node_class:
            _add("interaction_output", node_class, binding.get("parameter_name", ""))

        for so in step.get("sub_operations", []) or []:
            if so.get("op_type") == "user_interaction":
                _add(
                    "interaction_output",
                    so.get("node_class", ""),
                    binding.get("parameter_name", ""),
                )

        choice_binding = metadata.get("choice_bindings", {}).get(step_id, {})
        if choice_binding:
            _add(
                "choice_input",
                choice_binding.get("node_class", ""),
                choice_binding.get("parameter_name", ""),
            )
        return roles

    @staticmethod
    def _enrich_workflow_with_metadata(workflow_graph: Dict, metadata: Dict) -> None:
        """Attach generated metadata directly to workflow steps."""
        for step in workflow_graph.get("steps", []):
            sid = step.get("step_id", "")
            if sid in metadata.get("operation_model", {}):
                step["operation_model"] = metadata["operation_model"][sid]
            if sid in metadata.get("node_roles", {}):
                step["node_roles"] = metadata["node_roles"][sid]
            if sid in metadata.get("choice_bindings", {}):
                step["choice_binding"] = metadata["choice_bindings"][sid]
            if sid in metadata.get("interaction_bindings", {}):
                step["interaction_binding"] = metadata["interaction_bindings"][sid]

    def _generate_slicer_op_templates(self, stage_map) -> Dict[str, str]:
        """Generate code templates for all slicer_op sub-operations via KB search.

        Extracts slicer_op sub-operations from the stage_map and uses
        SlicerOpGenerator to search the KB and generate code templates.

        Returns a dict mapping "cb_step_{num}_{idx}" -> template code.
        """
        from .SlicerOpGenerator import SlicerOpGenerator
        from .CookbookParser import SubOperation

        # Collect all slicer_op sub-operations from stage_map
        slicer_ops = []
        for stage in stage_map.get("stages", []):
            step_num = stage.get("stage_index", 0) + 1
            for so in stage.get("sub_operations", []):
                if so.get("op_type") == "slicer_op":
                    sub_op = SubOperation(
                        op_type="slicer_op",
                        description=so.get("description", ""),
                        extension_method_hint=so.get("extension_method_hint"),
                        slicer_api_keywords=so.get("slicer_api_keywords", []),
                        interaction_type=so.get("interaction_type"),
                        node_class=so.get("node_class"),
                        placement_instructions=so.get("placement_instructions"),
                        evidence_type=so.get("evidence_type"),
                        evidence_id=so.get("evidence_id"),
                        confidence=so.get("confidence"),
                        interaction_kind=so.get("interaction_kind"),
                        slicer_op_category=so.get("slicer_op_category"),
                    )
                    slicer_ops.append((step_num, sub_op))

        if not slicer_ops:
            self.on_progress("5T", "Slicer op generation", "No slicer_op sub-operations found")
            return {}

        self.on_progress(
            "5T", "Slicer op generation",
            f"Generating templates for {len(slicer_ops)} slicer_op operations..."
        )

        # Determine skill_path for KB search
        module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        skill_path = os.path.join(module_dir, "Resources", "Skills", "slicer-skill-full")

        def _on_op_progress(finished, total, desc):
            if desc.startswith("done "):
                detail = f"[{finished}/{total}] done {desc[5:]}"
            elif desc.startswith("started "):
                detail = f"[{finished}/{total}] running {desc[8:]}"
            elif "timed out" in desc.lower() or "failed" in desc.lower():
                detail = f"[{finished}/{total}] {desc}"
            else:
                detail = f"[{finished}/{total}] {desc}"
            self.on_progress(
                "5T", "Slicer op generation",
                detail,
            )

        # Set up debug file path for live progress tracking
        debug_path = None
        if self._debug_dir:
            debug_path = os.path.join(self._debug_dir, "stage_5T_debug.json")

        generator = SlicerOpGenerator(
            llm_client=self.llm_client,
            skill_path=skill_path,
            on_progress=_on_op_progress,
            debug_path=debug_path,
        )

        templates = generator.generate(slicer_ops)
        self._slicer_op_evidence = {}
        for idx, (step_num, sub_op) in enumerate(slicer_ops):
            key = f"cb_step_{step_num}_{idx}"
            code = templates.get(key, "")
            if not code:
                continue
            self._slicer_op_evidence[key] = self._build_template_api_evidence(
                code,
                sub_op,
                source="stage5T",
            )
        if isinstance(self._workflow_metadata, dict):
            self._workflow_metadata["stage5T_api_evidence"] = self._slicer_op_evidence

        self.on_progress(
            "5T", "Slicer op generation",
            f"Generated {len(templates)} slicer_op templates"
        )

        # Log template keys for debug
        for key, code in templates.items():
            code_preview = code.split("\n")[0][:80] if code else "(empty)"
            logger.info("[5T] Template '%s': %s", key, code_preview)

        return templates

    def _generate_slicer_fallback_template(self, step: Dict) -> str:
        """Fallback template for slicer_op steps when no pre-generated template exists."""
        sub_ops = step.get("sub_operations", [])
        slicer_descs = [so["description"] for so in sub_ops if so["op_type"] == "slicer_op"]
        desc = "; ".join(slicer_descs) if slicer_descs else step.get("description", "")
        return (
            "# [SLICER_OP_GENERATION_FAILED] No generated slicer_op template was available.\n"
            f"# Operation: {desc}\n"
            "raise RuntimeError(\"Slicer-op template generation failed: no generated template was available\")\n"
        )

    def _generate_unknown_op_template(self, step: Dict) -> str:
        """Blocking template for required operations without enough evidence."""
        desc = _text_or_empty(step.get("description", step.get("step_id", "")))
        return (
            "# [UNKNOWN_OP_GENERATION_FAILED] Operation type could not be proven from extension or Slicer-core evidence.\n"
            f"# Operation: {desc}\n"
            "raise RuntimeError(\"Operation generation failed: insufficient classification evidence\")\n"
        )

    def _build_workflow_manifest_and_generators(
        self,
        extension_name: str,
        scan_result: Dict,
        workflow_graph: Dict,
    ) -> Tuple[Dict, List[Dict]]:
        """Build manifest and generators for an interactive workflow."""
        steps = workflow_graph.get("steps", [])
        for step in steps:
            operation_model = self._build_step_operation_model(step)
            step["operation_model"] = operation_model
            if isinstance(self._workflow_metadata, dict):
                self._workflow_metadata.setdefault("operation_model", {})[
                    step.get("step_id", "")
                ] = operation_model
                if step.get("interaction_owner") or step.get("placement_starter_method"):
                    self._workflow_metadata.setdefault("interaction_policies", {})[
                        step.get("step_id", "")
                    ] = {
                        "interaction_owner": step.get("interaction_owner", ""),
                        "placement_starter_method": step.get("placement_starter_method", ""),
                        "created_node_source": step.get("created_node_source", ""),
                    }
        stage_names = [s["step_id"] for s in steps]

        manifest = {
            "extension_name": extension_name,
            "extension_module_name": os.path.splitext(os.path.basename(scan_result.get("entry_module", "")))[0],
            "logic_class_name": scan_result.get("logic_class", {}).get("class_name", ""),
            "version": "1.0.0",
            "status": "draft",
            "workflow_type": "interactive",
            "workflow_graph_file": "workflow.json",
            "workflow_metadata_file": "workflow_metadata.json",
            "stages": stage_names,
        }
        # Add cookbook metadata when cookbook-driven
        if self._cookbook_def:
            manifest["cookbook_driven"] = True
            manifest["cookbook_file"] = os.path.basename(self._cookbook_def.source_file)
            op_types = set()
            for step in steps:
                if step.get("op_type"):
                    op_types.add(step["op_type"])
                for so in step.get("sub_operations", []):
                    if so.get("op_type"):
                        op_types.add(so["op_type"])
            manifest["operation_types"] = sorted(op_types)

        generators = []
        for step in steps:
            step_id = step["step_id"]
            step_type = step["step_type"]
            op_type = step.get("op_type", "")

            gen = {
                "tool_name": extension_name,
                "param_signature": {"workflow_step": step_id},
                "description": step.get("description", step_id),
                "requirements": [f"{extension_name} extension must be installed"],
                "step_type": step_type,
            }
            if op_type:
                gen["op_type"] = op_type
            if step.get("method_name"):
                gen["method_name"] = step["method_name"]
            if step.get("extension_function_name"):
                gen["extension_function_name"] = step["extension_function_name"]
            if step.get("allow_destructive_ops"):
                gen["allow_destructive_ops"] = bool(step.get("allow_destructive_ops"))
            if step.get("destructive_ops_contract"):
                gen["destructive_ops_contract"] = step["destructive_ops_contract"]
            if step.get("api_evidence"):
                gen["api_evidence"] = step["api_evidence"]
            if step.get("operation_model"):
                gen["operation_model"] = step["operation_model"]
            if step.get("node_roles"):
                gen["node_roles"] = step["node_roles"]

            if step_type == "automated" and step.get("code_template"):
                gen["template_file"] = step["code_template"]
                if step.get("sub_operations"):
                    gen["sub_operations"] = step["sub_operations"]
            elif step_type == "interactive":
                gen["pre_template_file"] = step.get("pre_template", "")
                gen["post_template_file"] = step.get("post_template", "")
                nc = step.get("node_class")
                gen["interaction_descriptor"] = {
                    "interaction_type": _derive_interaction_type(nc),
                    "interaction_kind": step.get("interaction_kind", ""),
                    "node_class": nc or "",
                    "placement_instructions": step.get("placement_instructions", ""),
                }
                if step.get("interaction_owner"):
                    gen["interaction_descriptor"]["interaction_owner"] = step.get("interaction_owner")
                if step.get("placement_starter_method"):
                    gen["interaction_descriptor"]["placement_starter_method"] = step.get(
                        "placement_starter_method"
                    )
                if step.get("created_node_source"):
                    gen["interaction_descriptor"]["created_node_source"] = step.get(
                        "created_node_source"
                    )
                if step.get("interaction_binding"):
                    gen["interaction_descriptor"]["binding"] = step["interaction_binding"]
            elif step_type == "mixed":
                gen["pre_template_file"] = step.get("pre_template", "")
                gen["post_template_file"] = step.get("post_template", "")
                # Collect interaction info from sub_operations
                interaction_desc = {}
                for so in step.get("sub_operations", []):
                    if so.get("op_type") == "user_interaction":
                        nc = so.get("node_class")
                        interaction_desc = {
                            "interaction_type": _derive_interaction_type(nc),
                            "interaction_kind": so.get("interaction_kind", ""),
                            "node_class": nc or "",
                            "placement_instructions": so.get("placement_instructions", ""),
                        }
                        break
                if step.get("interaction_binding"):
                    interaction_desc["binding"] = step["interaction_binding"]
                if step.get("interaction_owner"):
                    interaction_desc["interaction_owner"] = step.get("interaction_owner")
                if step.get("placement_starter_method"):
                    interaction_desc["placement_starter_method"] = step.get(
                        "placement_starter_method"
                    )
                if step.get("node_roles"):
                    interaction_desc["node_roles"] = step["node_roles"]
                if step.get("created_node_source"):
                    interaction_desc["created_node_source"] = step.get("created_node_source")
                gen["interaction_descriptor"] = interaction_desc
                gen["sub_operations"] = step.get("sub_operations", [])
            elif step_type == "branch":
                gen["condition"] = step.get("condition", "")
                gen["branches"] = step.get("branches", {})
            elif step_type == "user_choice":
                choice_info = step.get("choice_info", {})
                gen["choice_descriptor"] = {
                    "question": choice_info.get("question", ""),
                    "choices": choice_info.get("choices", []),
                    "parameter_name": choice_info.get("parameter_name", ""),
                    "default_value": choice_info.get("default_value"),
                }
                if step.get("choice_binding"):
                    gen["choice_descriptor"]["binding"] = step["choice_binding"]
                if step.get("node_roles"):
                    gen["choice_descriptor"]["node_roles"] = step["node_roles"]

            if step.get("repeat_group"):
                gen["repeat_group"] = step["repeat_group"]
                if gen.get("choice_descriptor") is not None:
                    gen["choice_descriptor"]["repeat_group"] = step["repeat_group"]
                if gen.get("interaction_descriptor") is not None:
                    gen["interaction_descriptor"]["repeat_group"] = step["repeat_group"]

            generators.append(gen)

        return manifest, generators

    # ================================================================
    # Helpers
    # ================================================================

    def _build_manifest_and_generators(
        self,
        extension_name: str,
        scan_result: Dict,
        stage_map: Dict,
        workflow_graph: Optional[Dict] = None,
    ) -> Tuple[Dict, List[Dict]]:
        """Build manifest.json and code_generators.json contents."""
        # Interactive workflow manifest
        if workflow_graph:
            return self._build_workflow_manifest_and_generators(
                extension_name, scan_result, workflow_graph,
            )

        stages = stage_map.get("stages", [])
        has_multiple = len(stages) > 1

        # Build stage enum values
        stage_names = [s["stage_name"] for s in stages]
        if has_multiple:
            stage_names.append("full")

        # Build generators list
        generators = []
        for s in stages:
            sname = s["stage_name"]
            methods = s.get("method_details", [])
            descriptions = [m.get("purpose", "") for m in methods]
            requirements = [
                f"{extension_name} Slicer extension must be installed",
            ]
            # Check for GPU requirement
            for m in methods:
                for p in m.get("parameters", []):
                    if "progress" in p.get("name", "").lower():
                        break

            generators.append({
                "tool_name": extension_name,
                "param_signature": {"stage": sname} if has_multiple else {},
                "template_file": f"templates/{sname}.py.tpl",
                "description": "; ".join(descriptions) if descriptions else sname,
                "requirements": requirements,
            })

        if has_multiple:
            generators.append({
                "tool_name": extension_name,
                "param_signature": {"stage": "full"},
                "template_file": "templates/full.py.tpl",
                "description": f"Complete {extension_name} pipeline: " + " + ".join(
                    s["stage_name"] for s in stages
                ),
                "requirements": [
                    f"{extension_name} Slicer extension must be installed",
                ],
            })

        manifest = {
            "extension_name": extension_name,
            "extension_module_name": os.path.splitext(
                os.path.basename(scan_result.get("entry_module", ""))
            )[0],
            "logic_class_name": scan_result.get("logic_class", {}).get("class_name", ""),
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "source_type": "analyzed_extension",
            "source_path": scan_result.get("source_path", ""),
            "status": "draft",
            "tool_count": 1,
            "stages": stage_names,
        }

        return manifest, generators

    def _call_llm(self, user_prompt: str) -> str:
        """Make an isolated LLM call and return the text response.

        If self._debug_dir is set, also saves the full input/output/thinking
        to a JSON file in the debug directory.

        Retries once on empty responses.
        """
        messages = [
            {"role": "system", "content": self._analyzer_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = self.llm_client.chatIsolated(messages)
        message_text = response.get("message", "")

        # Retry once on empty responses
        if not message_text or not message_text.strip():
            logger.info("Empty LLM response, retrying once...")
            response = self.llm_client.chatIsolated(messages)
            message_text = response.get("message", "")

        # Debug saving
        if self._debug_dir:
            try:
                self._save_debug_call(messages, response)
            except Exception:
                logger.debug("Failed to save debug call", exc_info=True)

        return message_text

    @staticmethod
    def _strip_markdown_fences(text: str) -> str:
        """Remove surrounding ```python ... ``` or ``` ... ``` fences from LLM output."""
        text = text.strip()
        if text.startswith("```"):
            # Remove opening fence
            first_newline = text.index("\n") if "\n" in text else len(text)
            text = text[first_newline + 1:]
            # Remove closing fence
            if text.rstrip().endswith("```"):
                text = text.rstrip()[:-3].rstrip()
        return text

    def _save_debug_call(self, messages: list, response: dict) -> None:
        """Save a single LLM call's debug info to a JSON file."""
        if not os.path.isdir(self._debug_dir):
            os.makedirs(self._debug_dir, exist_ok=True)

        call_index = self._llm_call_counter
        self._llm_call_counter += 1

        debug_entry = {
            "call_index": call_index,
            "timestamp": datetime.now().isoformat(),
            "stage": self._current_stage_label,
            "input": {
                "system_prompt": messages[0].get("content", "") if len(messages) > 0 else "",
                "user_prompt": messages[1].get("content", "") if len(messages) > 1 else "",
            },
            "output": {
                "message": response.get("message", ""),
                "reasoning_content": response.get("reasoning_content", ""),
            },
            "usage": response.get("usage", {}),
        }

        filename = f"stage_{self._current_stage_label}_call_{call_index:03d}.json"
        filepath = os.path.join(self._debug_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(debug_entry, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _parse_json_response(text: str) -> Any:
        """Extract and parse JSON from an LLM response."""
        if not text:
            return None

        # Strip markdown code fences if present
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first and last fence lines
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        # Strip JavaScript-style // comments that LLMs frequently emit.
        # Only strip when // appears after a JSON structural character
        # (comma, colon, bracket, brace) or whitespace — this avoids
        # breaking URL strings like "https://...".
        text = _JS_COMMENT_RE.sub("", text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Use json.JSONDecoder.raw_decode for balanced extraction
            # instead of greedy regex that matches too broadly.
            return ExtensionCLIAnalyzer._extract_json_balanced(text)

    @staticmethod
    def _extract_json_balanced(text: str) -> Any:
        """Extract the first valid JSON object or array using balanced-brace matching.

        Uses json.JSONDecoder.raw_decode() which stops at the end of the first
        valid JSON value, avoiding the greedy-regex problem of matching from
        the first ``{`` to the *last* ``}`` in the response.
        """
        decoder = json.JSONDecoder()
        # Search for the first '{' or '[' in the text
        for i, ch in enumerate(text):
            if ch in ('{', '['):
                try:
                    obj, _ = decoder.raw_decode(text, i)
                    return obj
                except json.JSONDecodeError:
                    # This opening brace wasn't the start of valid JSON;
                    # continue scanning for the next one.
                    continue
        logger.warning("Could not parse JSON from LLM response: %s", text[:300])
        return None

    def _extract_class_source(self, file_path: str, class_name: str) -> Optional[str]:
        """Extract the full source of a class from a Python file."""
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source = f.read()
        except Exception:
            return None

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return None

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                lines = source.split("\n")
                start = node.lineno - 1
                # Find end: last line of the class body
                end = node.end_lineno if hasattr(node, 'end_lineno') and node.end_lineno else len(lines)
                return "\n".join(lines[start:end])

        return None

    def _extract_method_source(self, file_path: str, method_name: str) -> Optional[str]:
        """Extract the source of a specific method, scoped to the Logic class body.

        Walks only the top-level class definitions to find the Logic class,
        then searches its methods — avoids matching identically-named methods
        in other classes (e.g. ``setup()`` in Widget vs Logic).
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                source = f.read()
        except Exception:
            return None

        try:
            tree = ast.parse(source)
        except SyntaxError:
            return None

        lines = source.split("\n")

        # First try: search only inside Logic-like class bodies
        for node in ast.iter_child_nodes(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            # Only search classes that look like the Logic class
            bases = [self._ast_name(b) for b in node.bases]
            is_logic = (
                "ScriptedLoadableModuleLogic" in bases
                or node.name.endswith("Logic")
            )
            if not is_logic:
                continue
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if item.name == method_name:
                        start = item.lineno - 1
                        end = (
                            item.end_lineno
                            if hasattr(item, "end_lineno") and item.end_lineno
                            else start + 50
                        )
                        return "\n".join(lines[start:end])

        # Fallback: search all top-level nodes (covers helper functions
        # defined outside any class).
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == method_name:
                    start = node.lineno - 1
                    end = (
                        node.end_lineno
                        if hasattr(node, "end_lineno") and node.end_lineno
                        else start + 50
                    )
                    return "\n".join(lines[start:end])

        return None

    # ================================================================
    # Stage 1.5: UI Workflow Extraction
    # ================================================================

    def _stage1_5_extract_workflow(self, scan_result: Dict) -> Optional[Dict]:
        """Extract the user-facing workflow from UI (.ui file) + Widget class.

        Returns a structured workflow dict, or None if insufficient UI data.
        """
        widget_class = scan_result.get("widget_class")
        ui_files = scan_result.get("ui_files", [])

        # Parse .ui file(s)
        ui_sections = None
        for ui_path in ui_files:
            parsed = self._parse_ui_file(ui_path)
            if parsed and parsed.get("sections"):
                ui_sections = parsed
                break

        # Extract Widget signal connections
        widget_connections = []
        widget_source = None
        if widget_class:
            widget_source = self._extract_class_source(
                widget_class["file"], widget_class["class_name"]
            )
            if widget_source:
                widget_connections = self._extract_widget_connections(widget_source)

        # If no UI data at all, skip this stage
        if not ui_sections and not widget_connections:
            self.on_progress(1.5, "UI workflow extraction", "No UI/Widget data — skipping")
            return None

        # Build the LLM prompt for workflow synthesis
        prompt_parts = [
            "## Task: Synthesize Extension Workflow from UI Analysis\n",
            "You are analyzing a 3D Slicer extension's user-facing workflow.",
            "Based on the UI layout and Widget signal connections below,",
            "produce a structured JSON workflow that reflects the actual user-facing workflow.\n",
        ]

        # UI sections and buttons
        if ui_sections:
            prompt_parts.append("### UI Layout (from .ui file)\n")
            prompt_parts.append("```json")
            prompt_parts.append(json.dumps(ui_sections, indent=2))
            prompt_parts.append("```\n")

        # Widget signal connections
        if widget_connections:
            prompt_parts.append("### Widget Signal Connections (from AST)\n")
            prompt_parts.append("Each entry maps a UI button to its handler method and the logic methods it calls.\n")
            prompt_parts.append("Some buttons may not appear in the UI Layout above (created programmatically).\n")
            prompt_parts.append("You MUST include steps for these buttons too — match them by their handler/logic method names.\n")
            prompt_parts.append("```json")
            prompt_parts.append(json.dumps(widget_connections, indent=2))
            prompt_parts.append("```\n")

        # Logic class methods (for context)
        logic_class = scan_result.get("logic_class")
        if logic_class:
            prompt_parts.append("### Logic Class Methods\n")
            prompt_parts.append(f"Class: `{logic_class['class_name']}`\n")
            prompt_parts.append("Methods: " + ", ".join(f"`{m}`" for m in logic_class.get("methods", [])))
            prompt_parts.append("\n")

        # Output schema instructions
        prompt_parts.append("### Required Output\n")
        prompt_parts.append(textwrap.dedent("""\
            Return a single JSON object with this structure:
            ```json
            {
              "ui_sections": [
                {
                  "section_name": "Section Name from UI",
                  "is_optional": false,
                  "steps": [
                    {
                      "step_id": "snake_case_id",
                      "button_label": "Button text from UI",
                      "logic_method": "methodName",
                      "description": "What this step does",
                      "step_type": "automated" or "interactive",
                      "interaction_type": "fiducial|curve|line|plane|null",
                      "depends_on": ["previous_step_id"],
                      "is_optional": false
                    }
                  ]
                }
              ]
            }
            ```

            Rules:
            1. Use the UI section order as the workflow sequence.
            2. Match button widget names to logic methods using the signal connections.
            3. Include ALL buttons from the signal connections, even those not in the UI Layout — they are created programmatically.
            4. `step_type` is "interactive" if the button triggers user 3D interaction (placing markups, drawing curves), "automated" for buttons that just trigger computation.
            6. `interaction_type` should be one of: fiducial, curve, line, plane, or null for automated steps.
            7. `depends_on` should list step_ids of prerequisite steps (sequential by default).
            8. Mark optional/experimental sections with `is_optional: true`.
            9. Use descriptive snake_case step_ids that reflect the button's purpose.
            10. Return ONLY the JSON object, no other text.
        """))

        full_prompt = "\n".join(prompt_parts)
        response_text = self._call_llm(full_prompt)

        if not response_text:
            self.on_progress(1.5, "UI workflow extraction", "LLM returned empty response")
            return None

        workflow = self._parse_json_response(response_text)
        if not workflow or "ui_sections" not in workflow:
            self.on_progress(1.5, "UI workflow extraction", "Failed to parse workflow JSON from LLM")
            return None

        return workflow
