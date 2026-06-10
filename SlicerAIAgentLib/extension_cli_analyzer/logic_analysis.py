from .common import *


class AnalyzerLogicAnalysisMixin:
    def _stage3_analyze_logic(self, scan_result: Dict) -> Dict:
        """Use LLM to analyze the Logic class methods in detail."""
        logic_info = scan_result["logic_class"]
        logic_file = logic_info["file"]
        class_name = logic_info["class_name"]

        self.on_progress(
            "analyze", "Analyze Extension Logic",
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
            prompt += textwrap.dedent(f"""\

Cookbook workflow (ground truth):
{cookbook_steps_text}

Interpret the cookbook semantics directly. Analyze all methods that may implement
the workflow, without relying on method-name similarity or fixed cookbook phrases.

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
            "analyze", "Analyze Extension Logic",
            f"Analyzed {len(analysis.get('methods', []))} methods"
        )

        analysis["_logic_source"] = logic_source
        analysis["_logic_file"] = logic_file
        analysis["_cookbook_method_hints"] = []
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
                "analyze", "Analyze Extension Logic",
                f"Corrected {corrections} method signature(s) via AST"
            )

    # ================================================================
