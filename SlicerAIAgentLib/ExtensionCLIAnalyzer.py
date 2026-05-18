"""
ExtensionCLIAnalyzer - 8-stage pipeline for analyzing Slicer extensions
and generating operation CLIs (tool schemas + code templates).

Uses the same LLM provider as the main agent to analyze extension source code,
identify operations, and generate validated code templates that integrate with
the SlicerAIAgent tool system.
"""

import ast
import json
import logging
import os
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
_MAX_SOURCE_FOR_LLM = 30_000

# Maximum revision attempts for failed validation
_MAX_REVISION_ATTEMPTS = 3


def _tokenize_name(name: str) -> set:
    """Split a CamelCase/underscore name into lowercase tokens."""
    import re
    parts = re.split(r'(?<=[a-z])(?=[A-Z])|_|(?<=[A-Z])(?=[A-Z][a-z])', name)
    return {p.lower() for p in parts if p}


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

    8-stage pipeline:
    1. Extension Scanning (AST, no LLM)
    2. Logic Class Analysis (LLM-assisted)
    3. State Dependency Analysis (programmatic + optional LLM)
    4. Node Lifecycle Analysis (LLM-assisted)
    5. Tool Schema Generation (LLM-assisted)
    6. Code Template Generation (LLM-assisted)
    7. Prompt Fragment Generation (LLM-assisted)
    8. Validation (CodeValidator, no LLM)
    """

    def __init__(
        self,
        llm_client,
        output_base_dir: Optional[str] = None,
        code_validator=None,
        on_progress: Optional[Callable[[int, str, str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ):
        """
        Args:
            llm_client: LLMClient instance for making LLM calls.
            output_base_dir: Base directory for saving CLI packages.
                             Defaults to Resources/extension_CLI/.
            code_validator: CodeValidator instance. Created if not provided.
            on_progress: Callback(stage_num, stage_name, detail) for progress updates.
            on_error: Callback(error_message) for error reporting.
        """
        self.llm_client = llm_client
        self.output_base_dir = output_base_dir or self._default_base_dir()
        self.code_validator = code_validator
        self.on_progress = on_progress or (lambda n, s, d: None)
        self.on_error = on_error or (lambda e: None)
        self._analyzer_prompt = self._load_analyzer_prompt()
        self._cancelled = False

    @staticmethod
    def _default_base_dir() -> str:
        module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(module_dir, "Resources", "extension_CLI")

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
        force_overwrite: bool = False,
    ) -> Dict:
        """
        Run the full 8-stage analysis pipeline.

        Args:
            extension_name: Name for the generated CLI directory.
            source_path: Path to the extension's source code root.
            force_overwrite: If True, overwrite existing CLI.

        Returns:
            Dict with 'success', 'cli_dir', 'manifest', 'stages_completed',
            'validation_result', 'error' keys.
        """
        self._cancelled = False
        result = {
            "success": False,
            "cli_dir": None,
            "manifest": None,
            "stages_completed": [],
            "validation_result": None,
            "error": None,
        }

        ext_dir = os.path.join(self.output_base_dir, extension_name)
        if os.path.isdir(ext_dir) and not force_overwrite:
            result["error"] = f"CLI for '{extension_name}' already exists. Use force_overwrite=True."
            return result

        try:
            # Stage 1: Scanning
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

            # Stage 2: Logic Class Analysis (LLM)
            logic_analysis = self._stage2_analyze_logic(scan_result)
            result["stages_completed"].append(2)
            if self._cancelled:
                result["error"] = "Cancelled during Stage 2"
                return result

            # Stage 2.5: AST Signature Verification
            self._verify_signatures_ast(logic_analysis, scan_result)
            result["stages_completed"].append("2.5")
            if self._cancelled:
                result["error"] = "Cancelled during Stage 2.5"
                return result

            # Stage 3: State Dependency Analysis
            stage_map = self._stage3_state_dependencies(logic_analysis)
            result["stages_completed"].append(3)
            if self._cancelled:
                result["error"] = "Cancelled during Stage 3"
                return result

            # Stage 3.5: Cross-Stage Parameter Mapping
            cross_stage_map = self._map_cross_stage_params(stage_map, extension_name)
            result["stages_completed"].append("3.5")
            if self._cancelled:
                result["error"] = "Cancelled during Stage 3.5"
                return result

            # Stage 4: Node Lifecycle Analysis (AST-based)
            node_lifecycle = self._stage4_node_lifecycle(scan_result, logic_analysis)
            result["stages_completed"].append(4)
            if self._cancelled:
                result["error"] = "Cancelled during Stage 4"
                return result

            # Stage 5: Tool Schema Generation (user-facing params only)
            tool_schemas = self._stage5_generate_schemas(
                extension_name, stage_map, logic_analysis,
                node_lifecycle=node_lifecycle,
                cross_stage_map=cross_stage_map,
            )
            result["stages_completed"].append(5)
            if self._cancelled:
                result["error"] = "Cancelled during Stage 5"
                return result

            # Stage 6: Code Template Generation (with cross-stage wiring)
            templates = self._stage6_generate_templates(
                extension_name, stage_map, node_lifecycle, scan_result, logic_analysis,
                cross_stage_map=cross_stage_map,
            )
            result["stages_completed"].append(6)
            if self._cancelled:
                result["error"] = "Cancelled during Stage 6"
                return result

            # Stage 6.5: LLM Review of Templates
            templates = self._stage6b_review_templates(
                templates, logic_analysis, node_lifecycle,
            )
            result["stages_completed"].append("6.5")
            if self._cancelled:
                result["error"] = "Cancelled during Stage 6.5"
                return result

            # Stage 7: Prompt Fragment Generation
            prompt_fragment = self._stage7_generate_prompt(
                extension_name, tool_schemas, stage_map, logic_analysis
            )
            result["stages_completed"].append(7)
            if self._cancelled:
                result["error"] = "Cancelled during Stage 7"
                return result

            # Stage 8: Validation (CodeValidator + semantic) + Save
            manifest, generators = self._build_manifest_and_generators(
                extension_name, scan_result, stage_map
            )
            validation_result = self._stage8_validate(
                templates, generators, logic_analysis=logic_analysis,
            )
            result["stages_completed"].append(8)
            result["validation_result"] = validation_result

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

        return result

    # ================================================================
    # Stage 1: Extension Scanning (AST, no LLM)
    # ================================================================

    def _stage1_scan(self, source_path: str) -> Dict:
        """Scan extension source tree, parse AST, find Logic class."""
        self.on_progress(1, "Scanning extension files", "Walking directory tree...")

        if not os.path.isdir(source_path):
            raise ValueError(f"Source path does not exist: {source_path}")

        # Walk and collect Python files
        py_files = []
        for root, dirs, files in os.walk(source_path):
            # Skip hidden dirs, __pycache__, build dirs
            dirs[:] = [d for d in dirs if not d.startswith((".", "__")) and d != "build"]
            for f in files:
                if f.endswith(".py"):
                    py_files.append(os.path.join(root, f))

        self.on_progress(
            1, "Scanning extension files",
            f"Found {len(py_files)} Python files"
        )

        # Parse each file's AST
        file_inventory = {}
        logic_candidates = []

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
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(node.name)

            file_inventory[fpath] = {
                "classes": classes,
                "functions": functions,
            }

        # Pick best Logic candidate (prefer one with "process" or "run" methods)
        logic_class = None
        if logic_candidates:
            scored = []
            for cand in logic_candidates:
                score = 0
                for m in cand["methods"]:
                    if m.startswith(("process", "run", "compute", "execute")):
                        score += 10
                    if m.startswith("__init__"):
                        score += 1
                scored.append((score, cand))
            scored.sort(key=lambda x: x[0], reverse=True)
            logic_class = scored[0][1]

        # Find the entry point module (the main module file)
        entry_module = None
        if logic_class:
            entry_module = logic_class["file"]

        self.on_progress(
            1, "Scanning extension files",
            f"Logic class: {logic_class['class_name'] if logic_class else 'None'} "
            f"in {os.path.basename(entry_module) if entry_module else 'N/A'}"
        )

        return {
            "source_path": source_path,
            "py_files": py_files,
            "file_inventory": file_inventory,
            "logic_class": logic_class,
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
    # Stage 2: Logic Class Analysis (LLM-assisted)
    # ================================================================

    def _stage2_analyze_logic(self, scan_result: Dict) -> Dict:
        """Use LLM to analyze the Logic class methods in detail."""
        logic_info = scan_result["logic_class"]
        logic_file = logic_info["file"]
        class_name = logic_info["class_name"]

        self.on_progress(
            2, "Analyzing logic class",
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
- Whether it writes state to self.* that future method calls depend on

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
            2, "Analyzing logic class",
            f"Analyzed {len(analysis.get('methods', []))} methods"
        )

        analysis["_logic_source"] = logic_source
        analysis["_logic_file"] = logic_file
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
                2, "Verifying signatures",
                f"Corrected {corrections} method signature(s) via AST"
            )

    # ================================================================
    # Stage 3: State Dependency Analysis (programmatic + optional LLM)
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
    # Stage 4: Node Lifecycle Analysis (LLM-assisted)
    # ================================================================

    def _stage4_node_lifecycle(self, scan_result: Dict, logic_analysis: Dict) -> Dict:
        """Determine node creation mode and param role for each vtkMRML parameter."""
        self.on_progress(4, "Analyzing node lifecycle", "Determining node creation patterns via AST...")

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
                    or p == params[-1]
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
                4, "Analyzing node lifecycle",
                "Asking LLM about node creation patterns..."
            )
            node_lifecycle = self._llm_node_lifecycle(logic_analysis)

        self.on_progress(
            4, "Analyzing node lifecycle",
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
    # Stage 5: Tool Schema Generation (LLM-assisted)
    # ================================================================

    def _stage5_generate_schemas(
        self,
        extension_name: str,
        stage_map: Dict,
        logic_analysis: Dict,
        node_lifecycle: Optional[Dict] = None,
        cross_stage_map: Optional[Dict] = None,
    ) -> List[Dict]:
        """Generate OpenAI function-calling tool schemas."""
        self.on_progress(5, "Generating tool schemas", "Building tool definitions...")

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

{'The extension has multiple stages, so include a "stage" enum parameter.' if has_multiple_stages else 'The extension has a single stage, so no "stage" parameter is needed.'}

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
            5, "Generating tool schemas",
            f"Generated {len(schemas)} tool schema(s): "
            f"{[s.get('function', {}).get('name', '?') for s in schemas]}"
        )

        return schemas

    # ================================================================
    # Stage 6: Code Template Generation (LLM-assisted)
    # ================================================================

    def _stage6_generate_templates(
        self,
        extension_name: str,
        stage_map: Dict,
        node_lifecycle: Dict,
        scan_result: Dict,
        logic_analysis: Dict,
        cross_stage_map: Optional[Dict] = None,
    ) -> Dict[str, str]:
        """Generate Python code templates for each stage."""
        stages = stage_map.get("stages", [])
        templates = {}
        if cross_stage_map is None:
            cross_stage_map = {}

        for i, stage in enumerate(stages):
            stage_name = stage["stage_name"]
            self.on_progress(
                6, "Generating code templates",
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
                6, "Generating code templates",
                "Generating combined 'full' template..."
            )
            full_template = self._generate_full_template(
                extension_name, stages, node_lifecycle, scan_result, logic_analysis,
                cross_stage_map=cross_stage_map,
            )
            templates["full.py.tpl"] = full_template

        self.on_progress(
            6, "Generating code templates",
            f"Generated {len(templates)} templates: {list(templates.keys())}"
        )

        return templates

    def _stage6b_review_templates(
        self,
        templates: Dict[str, str],
        logic_analysis: Dict,
        node_lifecycle: Dict,
    ) -> Dict[str, str]:
        """LLM review of generated templates against actual method source."""
        self.on_progress(
            6, "Reviewing templates",
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

        if corrections_count:
            self.on_progress(
                6, "Reviewing templates",
                f"LLM corrected {corrections_count} template(s)"
            )
        else:
            self.on_progress(
                6, "Reviewing templates",
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
    # Stage 7: Prompt Fragment Generation (LLM-assisted)
    # ================================================================

    def _stage7_generate_prompt(
        self,
        extension_name: str,
        tool_schemas: List[Dict],
        stage_map: Dict,
        logic_analysis: Dict,
    ) -> str:
        """Generate markdown prompt fragment for system prompt injection."""
        self.on_progress(7, "Generating prompt fragment", "Building usage instructions...")

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

        self.on_progress(7, "Generating prompt fragment", "Prompt fragment generated")
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
    # Stage 8: Validation (CodeValidator, no LLM)
    # ================================================================

    def _stage8_validate(
        self,
        templates: Dict[str, str],
        generators: List[Dict],
        logic_analysis: Optional[Dict] = None,
    ) -> Dict:
        """Validate all templates with CodeValidator + semantic checks."""
        self.on_progress(8, "Validating templates", "Running CodeValidator...")

        if not self.code_validator:
            from .CodeValidator import CodeValidator
            self.code_validator = CodeValidator()

        results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "per_template": {},
        }

        for tpl_name, tpl_content in templates.items():
            # Fill with sample values for validation
            sample_code = tpl_content.replace(
                "{vol_lookup}",
                "inputVolume = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode')"
            )
            # Fill any remaining placeholders with defaults
            sample_code = self._fill_remaining_placeholders(sample_code)

            # CodeValidator (security + syntax)
            validation = self.code_validator.validate(sample_code)

            # Semantic validation (undefined vars, arg count)
            if logic_analysis:
                semantic = self._semantic_validate(sample_code, logic_analysis)
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

        self.on_progress(
            8, "Validating templates",
            "PASS" if results["valid"] else f"FAIL: {results['errors']}"
        )

        return results

    def _semantic_validate(self, code: str, logic_analysis: Dict) -> Dict:
        """Check for undefined variables, wrong arg counts, invalid node types."""
        result = {"errors": [], "warnings": []}

        try:
            tree = ast.parse(code)
        except SyntaxError:
            result["errors"].append("Syntax error in generated code")
            return result

        # Collect defined names (assignments, imports, function/class defs, for-loop targets)
        defined = set()
        # Builtins and implicit Slicer names that are always available
        defined.update({
            "slicer", "qt", "vtk", "ctk", "inputVolume", "logic",
            "True", "False", "None", "print", "range", "len", "int",
            "float", "str", "bool", "list", "dict", "set", "tuple",
            "isinstance", "type", "super", "property", "staticmethod",
            "classmethod", "hasattr", "getattr", "callable", "abs",
            "min", "max", "sum", "any", "all", "sorted", "reversed",
            "enumerate", "zip", "map", "filter", "round", "hex", "oct",
            "Exception", "ValueError", "RuntimeError",
            "ImportError", "NameError", "TypeError", "KeyError",
            "AttributeError", "IndexError", "FileNotFoundError",
            "os", "json", "math", "time", "path",
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
        )
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                if func_name in ("CreateNodeByClass", "AddNewNodeByClass"):
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            cls = arg.value
                            if not cls.startswith(valid_prefixes):
                                result["warnings"].append(
                                    f"Unknown MRML node class: '{cls}'"
                                )

        return result

    @staticmethod
    def _fill_remaining_placeholders(code: str) -> str:
        """Fill any remaining {placeholder} or {placeholder: default} patterns with safe defaults."""
        import re
        def _replace(match):
            full = match.group(0)
            name = match.group(1)
            default = match.group(4)  # may be None (group 4 = actual default value, group 3 = ': ' separator)
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
        # Replace single-brace placeholders that aren't double-brace escapes
        # First, temporarily replace {{ }} with a sentinel
        sentinel = "\x00LBRACE\x00"
        code = code.replace("{{", sentinel + "{")
        code = code.replace("}}", "}" + sentinel)
        # Match {name} or {name: default_value} — the default can contain brackets, strings, etc.
        # We use a balanced-brace match for the default portion.
        code = re.sub(r'\{(\w+)((: )(.*?))?\}', _replace, code)
        # Restore literal braces
        code = code.replace(sentinel + "{", "{{")
        code = code.replace("}" + sentinel, "}}")
        return code

    # ================================================================
    # Revision System
    # ================================================================

    def revise(
        self,
        extension_name: str,
        errors: List[str],
        max_attempts: int = _MAX_REVISION_ATTEMPTS,
    ) -> Dict:
        """
        Revise failed templates using LLM feedback.

        Args:
            extension_name: Name of the CLI to revise.
            errors: List of error messages from validation or testing.

        Returns:
            Dict with 'success', 'validation_result', 'attempts' keys.
        """
        from .ExtensionCLILoader import get_cli_base_dir

        cli_dir = os.path.join(get_cli_base_dir(), extension_name)
        if not os.path.isdir(cli_dir):
            return {"success": False, "error": f"No CLI found for {extension_name}"}

        # Load existing CLI data
        manifest_path = os.path.join(cli_dir, "manifest.json")
        generators_path = os.path.join(cli_dir, "code_generators.json")

        with open(manifest_path, "r") as f:
            manifest = json.load(f)
        with open(generators_path, "r") as f:
            generators = json.load(f)

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
                tpl_file = gen.get("template_file", "")
                tpl_path = os.path.join(cli_dir, tpl_file)
                if os.path.isfile(tpl_path):
                    with open(tpl_path, "r") as f:
                        templates[tpl_file] = f.read()

            # Build revision prompt
            templates_text = "\n\n".join(
                f"--- {name} ---\n{content}"
                for name, content in templates.items()
            )

            prompt = textwrap.dedent(f"""\
The following code templates for the "{extension_name}" extension failed validation.
Please fix ALL errors while maintaining the template format (use {{placeholder}} for dynamic values, {{{{ }}}} for literal braces).

ERRORS:
{chr(10).join(f'- {e}' for e in errors)}

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

            # Save fixed templates
            for tpl_name, tpl_content in fixed["templates"].items():
                tpl_path = os.path.join(cli_dir, tpl_name)
                with open(tpl_path, "w", encoding="utf-8") as f:
                    f.write(tpl_content)

            # Re-validate
            if not self.code_validator:
                from .CodeValidator import CodeValidator
                self.code_validator = CodeValidator()

            all_valid = True
            new_errors = []
            for gen in generators:
                tpl_file = gen.get("template_file", "")
                tpl_path = os.path.join(cli_dir, tpl_file)
                if not os.path.isfile(tpl_path):
                    continue
                with open(tpl_path, "r") as f:
                    content = f.read()

                sample = content.replace(
                    "{vol_lookup}",
                    "inputVolume = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode')"
                )
                sample = self._fill_remaining_placeholders(sample)
                validation = self.code_validator.validate(sample)

                if not validation.get("valid", True):
                    all_valid = False
                    new_errors.append(f"{tpl_file}: {validation.get('reason', 'unknown')}")

            if all_valid:
                # Update manifest status
                manifest["status"] = "validated"
                with open(manifest_path, "w") as f:
                    json.dump(manifest, f, indent=2)

                # Append to generation log
                log_path = os.path.join(cli_dir, "generation_log.json")
                log_entries = []
                if os.path.isfile(log_path):
                    with open(log_path, "r") as f:
                        log_entries = json.load(f)
                log_entries.append({
                    "attempt": len(log_entries) + 1,
                    "timestamp": datetime.now().isoformat(),
                    "stage": "revision",
                    "trigger": "validation_failure",
                    "error": "; ".join(errors),
                    "fix": fixed.get("fix_description", ""),
                    "validation_result": {"valid": True},
                })
                with open(log_path, "w") as f:
                    json.dump(log_entries, f, indent=2)

                from .ExtensionCLILoader import invalidate_cache
                invalidate_cache()

                result["success"] = True
                result["validation_result"] = {"valid": True}
                return result

            errors = new_errors

        result["error"] = f"Revision failed after {max_attempts} attempts"
        return result

    # ================================================================
    # Helpers
    # ================================================================

    def _build_manifest_and_generators(
        self,
        extension_name: str,
        scan_result: Dict,
        stage_map: Dict,
    ) -> Tuple[Dict, List[Dict]]:
        """Build manifest.json and code_generators.json contents."""
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
            "status": "validated",
            "tool_count": 1,
            "stages": stage_names,
        }

        return manifest, generators

    def _call_llm(self, user_prompt: str) -> str:
        """Make an isolated LLM call and return the text response."""
        messages = [
            {"role": "system", "content": self._analyzer_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = self.llm_client.chatIsolated(messages)
        return response.get("message", "")

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

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON in the text
            import re
            # Look for JSON array or object
            for pattern in [
                r'\[[\s\S]*\]',
                r'\{[\s\S]*\}',
            ]:
                match = re.search(pattern, text)
                if match:
                    try:
                        return json.loads(match.group())
                    except json.JSONDecodeError:
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
        """Extract the source of a specific method from the logic file."""
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
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == method_name:
                    lines = source.split("\n")
                    start = node.lineno - 1
                    end = node.end_lineno if hasattr(node, 'end_lineno') and node.end_lineno else start + 50
                    return "\n".join(lines[start:end])

        return None
