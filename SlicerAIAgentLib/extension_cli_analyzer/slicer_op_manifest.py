from .common import *


class AnalyzerSlicerOpManifestMixin:
    def _generate_slicer_op_templates(self, stage_map) -> Dict[str, str]:
        """Generate code templates for all slicer_op sub-operations via KB search.

        Extracts slicer_op sub-operations from the stage_map and uses
        SlicerOpGenerator to search the KB and generate code templates.

        Returns a dict mapping "cb_step_{num}_{idx}" -> template code.
        """
        from ..SlicerOpGenerator import SlicerOpGenerator
        from ..CookbookParser import SubOperation

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
            self.on_progress("ground", "Ground Slicer APIs", "No slicer_op sub-operations found")
            return {}

        self.on_progress(
            "ground", "Ground Slicer APIs",
            f"Generating templates for {len(slicer_ops)} slicer_op operations..."
        )

        # Determine skill_path for KB search
        module_dir = _PROJECT_ROOT
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
                "ground", "Ground Slicer APIs",
                detail,
            )

        # Set up debug file path for live progress tracking
        debug_path = None
        if self._debug_dir:
            debug_path = os.path.join(self._debug_dir, "ground_slicer_api_debug.json")

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
                source="ground_api",
            )
        if isinstance(self._workflow_metadata, dict):
            self._workflow_metadata["ground_api_evidence"] = self._slicer_op_evidence

        self.on_progress(
            "ground", "Ground Slicer APIs",
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
            if not step.get("ui_guidance"):
                step["ui_guidance"] = self._fallback_ui_guidance(
                    step,
                    self._workflow_metadata if isinstance(self._workflow_metadata, dict) else {},
                )
            operation_type = _operation_type_for_step(step)
            step["operation_type"] = operation_type
            operation_model = self._build_step_operation_model(step)
            step["operation_model"] = operation_model
            if isinstance(self._workflow_metadata, dict):
                self._workflow_metadata.setdefault("ui_guidance", {})[
                    step.get("step_id", "")
                ] = step["ui_guidance"]
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
            "manifest_version": 3,
            "pipeline_version": "agentic-cli-v2",
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
                operation_type = _operation_type_for_step(step)
                if operation_type:
                    op_types.add(operation_type)
                for so in step.get("sub_operations", []):
                    if so.get("op_type"):
                        op_types.add(so["op_type"])
            manifest["operation_types"] = sorted(op_types)

        generators = []
        for step in steps:
            step_id = step["step_id"]
            op_type = _operation_type_for_step(step)
            exec_type = _legacy_step_type_for_operation(op_type)

            gen = {
                "tool_name": extension_name,
                "param_signature": {"workflow_step": step_id},
                "description": step.get("description", step_id),
                "requirements": [f"{extension_name} extension must be installed"],
                "operation_type": op_type,
            }
            if step.get("ui_guidance"):
                gen["ui_guidance"] = step["ui_guidance"]
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

            if exec_type == "automated" and step.get("code_template"):
                gen["template_file"] = step["code_template"]
                if step.get("sub_operations"):
                    gen["sub_operations"] = step["sub_operations"]
            elif exec_type == "interactive":
                gen["pre_template_file"] = step.get("pre_template", "")
                gen["post_template_file"] = step.get("post_template", "")
                nc = step.get("node_class")
                gen["interaction_descriptor"] = {
                    "interaction_type": _derive_interaction_type(nc),
                    "interaction_kind": step.get("interaction_kind", ""),
                    "node_class": nc or "",
                    "placement_instructions": step.get("placement_instructions", ""),
                }
                if step.get("ui_guidance"):
                    gen["interaction_descriptor"]["ui_guidance"] = step["ui_guidance"]
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
                if step.get("placement_starter_step_id"):
                    gen["interaction_descriptor"]["placement_starter_step_id"] = step.get(
                        "placement_starter_step_id"
                    )
                if step.get("placement_binding_reason"):
                    gen["interaction_descriptor"]["placement_binding_reason"] = step.get(
                        "placement_binding_reason"
                    )
                if step.get("interaction_binding"):
                    gen["interaction_descriptor"]["binding"] = step["interaction_binding"]
                workflow_metadata = self._workflow_metadata if isinstance(self._workflow_metadata, dict) else {}
                policy = (workflow_metadata.get("interaction_policies", {}) or {}).get(step_id, {})
                if policy:
                    gen["interaction_descriptor"]["placement_policy"] = policy
            elif exec_type == "mixed":
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
                if step.get("ui_guidance"):
                    interaction_desc["ui_guidance"] = step["ui_guidance"]
                workflow_metadata = self._workflow_metadata if isinstance(self._workflow_metadata, dict) else {}
                policy = (workflow_metadata.get("interaction_policies", {}) or {}).get(step_id, {})
                if policy:
                    interaction_desc["placement_policy"] = policy
                gen["interaction_descriptor"] = interaction_desc
                gen["sub_operations"] = step.get("sub_operations", [])
            elif exec_type == "branch":
                gen["condition"] = step.get("condition", "")
                gen["branches"] = step.get("branches", {})
            elif exec_type == "user_choice":
                choice_info = step.get("choice_info", {})
                gen["choice_descriptor"] = {
                    "question": choice_info.get("question", ""),
                    "choices": choice_info.get("choices", []),
                    "parameter_name": choice_info.get("parameter_name", ""),
                    "default_value": choice_info.get("default_value"),
                }
                if step.get("ui_guidance"):
                    gen["choice_descriptor"]["ui_guidance"] = step["ui_guidance"]
                if step.get("choice_binding"):
                    gen["choice_descriptor"]["binding"] = step["choice_binding"]
                if step.get("node_roles"):
                    gen["choice_descriptor"]["node_roles"] = step["node_roles"]
                if step.get("sub_operations"):
                    gen["sub_operations"] = step["sub_operations"]

            if step.get("repeat_group"):
                gen["repeat_group"] = step["repeat_group"]
                if gen.get("choice_descriptor") is not None:
                    gen["choice_descriptor"]["repeat_group"] = step["repeat_group"]
                if gen.get("interaction_descriptor") is not None:
                    gen["interaction_descriptor"]["repeat_group"] = step["repeat_group"]
            if step.get("repeat_block"):
                gen["repeat_block"] = step["repeat_block"]

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
            "phase": self._current_stage_label,
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

        filename = f"{self._current_stage_label}_call_{call_index:03d}.json"
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
