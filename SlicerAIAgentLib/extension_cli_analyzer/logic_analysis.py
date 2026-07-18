from .common import *


class AnalyzerLogicAnalysisMixin:
    def _stage3_analyze_logic(self, scan_result: Dict) -> Dict:
        """Analyze the Logic class: AST-derived method universe + LLM annotation.

        The complete method list and its structural facts (signatures,
        state reads/writes, AddNode usage) are enumerated deterministically
        from the AST. The LLM only annotates this fixed universe with
        semantics (purpose, side effects, classification); it cannot omit or
        invent methods, so every downstream consumer — placement-starter
        classification, cross-stage mapping, proven-target lists — sees the
        same complete universe on every run.
        """
        logic_info = scan_result["logic_class"]
        if not logic_info:
            # A ctkWorkflow wizard module has no logic class at all (the analyzer's
            # discover gate only lets such modules through). Its operations are
            # grounded from the scanned wizard facts, so the method universe is
            # legitimately empty -- return a well-formed empty analysis instead of
            # crashing, and let the semantic validator enforce null method hints.
            self.on_progress(
                "analyze", "Analyze Extension Logic",
                "No logic class (wizard-style module) — empty method universe.",
            )
            return {
                "class_name": "",
                "file": "",
                "methods": [],
                "helper_functions": [],
                "module_level_functions": [],
            }
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

        # Deterministic ground truth: every method of the class, with
        # AST-derived signatures and state-access facts.
        method_universe = self._enumerate_logic_method_universe(logic_source, class_name)
        if not method_universe:
            raise RuntimeError(
                f"AST enumeration found no methods in {class_name} ({logic_file})"
            )
        universe_names = [m["name"] for m in method_universe]
        self.on_progress(
            "analyze", "Analyze Extension Logic",
            f"AST enumerated {len(universe_names)} methods; requesting LLM annotation..."
        )

        # Truncate if too large
        if len(logic_source) > _MAX_SOURCE_FOR_LLM:
            logic_source = logic_source[:_MAX_SOURCE_FOR_LLM] + "\n# ... [truncated for LLM analysis] ..."

        method_listing = "\n".join(
            f"- {m['name']}({', '.join(p['name'] for p in m['parameters'])})"
            for m in method_universe
        )

        # Build prompt
        prompt = textwrap.dedent(f"""\
Annotate the methods of the following Slicer extension Logic class.

The COMPLETE method list below was extracted from the source AST and is fixed.
You MUST return exactly one annotation entry for EVERY listed method — do not
skip any method (not even trivial getters/setters or private helpers), and do
not invent methods that are not listed.

METHOD UNIVERSE ({len(universe_names)} methods):
{method_listing}

Return a JSON object with this exact structure:

{{
  "class_name": "{class_name}",
  "source_file": "{os.path.basename(logic_file)}",
  "methods": [
    {{
      "name": "method_name",
      "purpose": "one-line description",
      "parameters": [
        {{"name": "param_name", "type": "vtkMRML... or str or int etc", "description": "what it is"}}
      ],
      "return_value": "description or null",
      "adds_output_to_scene": true/false,
      "side_effects": "one-line description or empty string"
    }}
  ],
  "public_api_methods": ["method1", "method2"],
  "internal_methods": ["_helper1"],
  "pipeline_methods": ["method1", "method2"],
  "state_fields": [
    {{"name": "self.field1", "type": "description"}}
  ]
}}

Annotation guidance:
- "pipeline_methods": the subset of methods that perform meaningful workflow
  operations (process, run, compute, execute), in their natural call order.
- "parameters": annotate types/descriptions only; names and defaults come from
  the AST and any mismatch will be corrected automatically.
- Be precise about whether a method adds its outputs to the MRML scene.""")

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

        universe_name_set = set(universe_names)

        def _validate(candidate, raw):
            if not isinstance(candidate, dict) or not isinstance(candidate.get("methods"), list):
                return None, ["Response must be a JSON object with a 'methods' list"]
            errors = []
            annotated = {}
            for entry in candidate["methods"]:
                if not isinstance(entry, dict) or not entry.get("name"):
                    errors.append("each methods[] entry must be an object with a 'name'")
                    continue
                annotated[entry["name"]] = entry
            invented = sorted(set(annotated) - universe_name_set)
            missing = sorted(universe_name_set - set(annotated))
            if invented:
                errors.append(
                    "methods not in the fixed METHOD UNIVERSE (remove them): "
                    + ", ".join(invented[:20])
                )
            if missing:
                errors.append(
                    "missing annotation entries for these METHOD UNIVERSE methods "
                    "(add them all): " + ", ".join(missing[:40])
                )
            return candidate, errors

        analysis = self._call_llm_structured(
            prompt=prompt,
            validator=_validate,
            call_class="analysis",
            failure_label="Logic class annotation",
        )

        analysis = self._merge_logic_annotations(
            analysis, method_universe, class_name, os.path.basename(logic_file)
        )

        self.on_progress(
            "analyze", "Analyze Extension Logic",
            f"Analyzed {len(analysis.get('methods', []))} methods "
            "(AST universe + LLM annotation)"
        )

        analysis["_logic_source"] = logic_source
        analysis["_logic_file"] = logic_file
        analysis["_cookbook_method_hints"] = []
        return analysis

    @staticmethod
    def _enumerate_logic_method_universe(logic_source: str, class_name: str) -> List[Dict]:
        """Enumerate every method of the class with AST-derived facts.

        Returns one entry per method (in source order):
        name, parameters (name/type/required/default), state_reads,
        state_writes (self.* attribute loads/stores anywhere in the method),
        and calls_addnode.
        """
        try:
            tree = ast.parse(textwrap.dedent(logic_source))
        except SyntaxError:
            return []

        class_def = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                class_def = node
                break
        if class_def is None:
            # Fall back to the first class in the extracted source
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_def = node
                    break
        if class_def is None:
            return []

        universe = []
        for item in class_def.body:
            if not isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            # Parameters with annotations and defaults
            args = item.args
            all_args = args.args[:]
            if all_args and getattr(all_args[0], "arg", None) == "self":
                all_args = all_args[1:]
            defaults = args.defaults[:]
            padded_defaults = [None] * (len(all_args) - len(defaults)) + defaults
            parameters = []
            for arg_obj, default_val in zip(all_args, padded_defaults):
                annotation = ""
                if arg_obj.annotation is not None:
                    try:
                        annotation = ast.unparse(arg_obj.annotation)
                    except Exception:
                        annotation = ""
                entry = {
                    "name": arg_obj.arg,
                    "type": annotation or "Any",
                    "required": default_val is None,
                    "description": "",
                }
                if default_val is not None:
                    try:
                        entry["default"] = _parse_default_value(ast.unparse(default_val))
                    except Exception:
                        entry["default"] = None
                parameters.append(entry)

            # self.* state access
            state_reads, state_writes = set(), set()
            for node in ast.walk(item):
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                        and node.value.id == "self":
                    field = f"self.{node.attr}"
                    if isinstance(node.ctx, (ast.Store, ast.Del)):
                        state_writes.add(field)
                    else:
                        state_reads.add(field)

            # AddNode / AddNewNodeByClass usage
            visitor = _AddNodeVisitor({p["name"] for p in parameters})
            visitor.visit(item)
            calls_addnode = bool(visitor.params_added_to_scene) or visitor.has_addnewnodebyclass

            universe.append({
                "name": item.name,
                "parameters": parameters,
                "state_reads": sorted(state_reads),
                "state_writes": sorted(state_writes),
                "calls_addnode": calls_addnode,
            })
        return universe

    @staticmethod
    def _merge_logic_annotations(
        analysis: Dict, method_universe: List[Dict], class_name: str, source_file: str
    ) -> Dict:
        """Merge LLM annotations onto the AST method universe.

        AST facts (method list, parameter names/defaults, state reads/writes,
        calls_addnode) are ground truth; LLM supplies semantics only. The
        merged 'methods' list always covers the full universe in source order.
        """
        annotated = {
            entry.get("name"): entry
            for entry in analysis.get("methods", [])
            if isinstance(entry, dict) and entry.get("name")
        }

        merged_methods = []
        for fact in method_universe:
            llm = annotated.get(fact["name"], {})
            llm_params = {
                p.get("name"): p
                for p in (llm.get("parameters") or [])
                if isinstance(p, dict) and p.get("name")
            }
            parameters = []
            for param in fact["parameters"]:
                entry = dict(param)
                llm_param = llm_params.get(param["name"], {})
                if llm_param.get("description"):
                    entry["description"] = llm_param["description"]
                # Prefer the LLM's semantic type only when the AST had none
                if (not param.get("type") or param["type"] == "Any") and llm_param.get("type"):
                    entry["type"] = llm_param["type"]
                parameters.append(entry)
            merged_methods.append({
                "name": fact["name"],
                "purpose": llm.get("purpose", ""),
                "parameters": parameters,
                "return_value": llm.get("return_value"),
                "state_reads": fact["state_reads"],
                "state_writes": fact["state_writes"],
                "calls_addnode": fact["calls_addnode"],
                "adds_output_to_scene": bool(
                    fact["calls_addnode"] or llm.get("adds_output_to_scene")
                ),
                "side_effects": llm.get("side_effects", ""),
            })

        # Deterministic state-field inventory from the AST universe; LLM
        # descriptions merged by name when provided.
        llm_field_types = {}
        for field in analysis.get("state_fields", []) or []:
            if isinstance(field, dict) and field.get("name"):
                llm_field_types[field["name"].replace("self.", "")] = field.get("type", "")
        field_writers: Dict[str, List[str]] = {}
        field_readers: Dict[str, List[str]] = {}
        for fact in method_universe:
            for field in fact["state_writes"]:
                field_writers.setdefault(field, []).append(fact["name"])
            for field in fact["state_reads"]:
                field_readers.setdefault(field, []).append(fact["name"])
        state_fields = []
        for field in sorted(set(field_writers) | set(field_readers)):
            state_fields.append({
                "name": field,
                "type": llm_field_types.get(field.replace("self.", ""), ""),
                "set_by": (field_writers.get(field) or [""])[0],
                "read_by": field_readers.get(field, []),
            })

        universe_names = {fact["name"] for fact in method_universe}
        public_default = [n for n in universe_names if not n.startswith("_")]
        internal_default = [n for n in universe_names if n.startswith("_")]

        def _filtered(names, fallback):
            valid = [n for n in (names or []) if n in universe_names]
            return valid or fallback

        return {
            "class_name": analysis.get("class_name") or class_name,
            "source_file": analysis.get("source_file") or source_file,
            "methods": merged_methods,
            "public_api_methods": _filtered(
                analysis.get("public_api_methods"), sorted(public_default)
            ),
            "internal_methods": _filtered(
                analysis.get("internal_methods"), sorted(internal_default)
            ),
            "pipeline_methods": [
                n for n in (analysis.get("pipeline_methods") or []) if n in universe_names
            ],
            "state_fields": state_fields,
        }

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
