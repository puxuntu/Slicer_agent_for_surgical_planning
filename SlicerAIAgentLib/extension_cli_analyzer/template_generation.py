from .common import *


class AnalyzerTemplateGenerationMixin:
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
                "generate", "Generate Schemas And Templates",
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
                "generate", "Generate Schemas And Templates",
                "Generating combined 'full' template..."
            )
            full_template = self._generate_full_template(
                extension_name, stages, node_lifecycle, scan_result, logic_analysis,
                cross_stage_map=cross_stage_map,
            )
            templates["full.py.tpl"] = full_template

        self.on_progress(
            "generate", "Generate Schemas And Templates",
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
            "generate", "Generate Schemas And Templates",
            "Sending templates to LLM for correctness review..."
        )

        logic_file = logic_analysis.get("_logic_file", "")
        class_name = logic_analysis.get("class_name", "")
        methods = logic_analysis.get("methods", [])
        reviewed = dict(templates)
        corrections_count = 0

        # Scoped re-entry: a template byte-identical to the prior iteration's
        # already passed this review once — re-reviewing identical content
        # only spends LLM calls and risks churn.
        unchanged_templates = set()
        if getattr(self, "_reentry_affected_steps", None):
            prior = getattr(self, "_prev_templates", None) or {}
            unchanged_templates = {
                tpl_name for tpl_name, tpl_code in templates.items()
                if prior.get(tpl_name) == tpl_code
            }
            if unchanged_templates:
                self.on_progress(
                    "generate", "Generate Schemas And Templates",
                    f"Review scope: skipping {len(unchanged_templates)} template(s) "
                    "unchanged since the previously reviewed iteration",
                )

        for tpl_name, tpl_code in templates.items():
            if tpl_name in unchanged_templates:
                continue
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
5. For every executable API call, is the receiver type derivable from supplied
   source or node-lifecycle evidence? Distinguish a known-invalid call from missing proof.
6. Does the template change ONLY the state the step requires? Flag any
   state-changing call whose user-visible effect exceeds the step description
   (for example enabling interaction handles, interactive modes, or persistent
   handle visibility when only visibility was asked), and remove it in the
   corrected template.

Do NOT change: node creation mode, cross-stage wiring, or display setup code.
Do NOT introduce unrelated UI, icon, toolbar, module-switching, or layout behavior.

Return JSON:
{{
  "issues": [
    {{"line": 0, "call": "receiver.method", "diagnosis": "invalid_code|missing_proof", "problem": "description", "fix": "description of fix"}}
  ],
  "corrected_template": "the corrected full template string, or null if no changes needed"
}}

If the template is correct with no issues, return:
{{"issues": [], "corrected_template": null}}""")

            response = self._call_llm(prompt, call_class="critic")
            review = self._parse_json_response(response)

            if not review:
                logger.warning("LLM review returned unparseable response for %s", tpl_name)
                continue
            # The critic prompt asks for an object {"issues": [...],
            # "corrected_template": ...}, but the LLM occasionally returns a bare
            # JSON array (e.g. just the issues list). A list is truthy, so without
            # this guard the next line does list.get(...) -> "'list' object has no
            # attribute 'get'" and the whole generate phase aborts. Treat any
            # non-object review as "no usable correction" and skip this template.
            if not isinstance(review, dict):
                logger.warning(
                    "LLM review for %s returned a %s, not an object; skipping review",
                    tpl_name, type(review).__name__,
                )
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
                corrected_templates = self._sanitize_templates({tpl_name: corrected})
                corrected = corrected_templates.get(tpl_name, corrected)
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

        reviewed = self._sanitize_templates(reviewed)
        syntax_issues = self._syntax_check_templates(reviewed)
        if isinstance(self._workflow_metadata, dict):
            self._workflow_metadata.setdefault("validation_state", {})[
                "generate_syntax_valid"
            ] = not bool(syntax_issues)
            if syntax_issues:
                self._workflow_metadata["generate_syntax_issues"] = syntax_issues

        if syntax_issues:
            self.on_progress(
                "generate", "Generate Schemas And Templates",
                f"Found {len(syntax_issues)} syntax issue(s); validation/revision must fix them"
            )
        elif corrections_count:
            self.on_progress(
                "generate", "Generate Schemas And Templates",
                f"LLM corrected {corrections_count} template(s)"
            )
        else:
            self.on_progress(
                "generate", "Generate Schemas And Templates",
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
