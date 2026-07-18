from .common import *
from .phases import PIPELINE_VERSION


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

        # Integrity guard: grounding quality depends on the core-UI
        # pre-analysis artifacts; degrade loudly rather than silently.
        try:
            from ..UIControlIndex import preanalysis_status
            status = preanalysis_status()
            if not status.get("ok"):
                self.on_progress(
                    "ground", "Ground Slicer APIs",
                    "WARNING: Slicer UI pre-analysis missing/empty "
                    f"({status.get('reason', 'unknown')}) — UI-labeled grounding is "
                    "degraded; run scripts/build_rag.py outside Slicer to rebuild.",
                )
        except Exception:
            logger.debug("UI pre-analysis status check failed", exc_info=True)

        # Scoped re-entry reuse: grounding is the most expensive phase, and
        # after a scoped contract merge most sub-ops are byte-identical to
        # the previous iteration. Reuse the cached grounded code when the
        # sub-op's evidence-relevant inputs are unchanged and its step is not
        # implicated in the failures driving this iteration. Failed
        # groundings (MISSING_EVIDENCE) are never reused.
        cache = getattr(self, "_slicer_op_template_cache", None)
        if cache is None:
            cache = {}
            self._slicer_op_template_cache = cache
        implicated_steps = getattr(self, "_reentry_implicated_steps", set()) or set()

        def _sub_op_fingerprint(step_num, sub_op) -> str:
            return self._content_fingerprint(step_num, [
                getattr(sub_op, field, None) for field in (
                    "description", "extension_method_hint", "slicer_api_keywords",
                    "interaction_type", "node_class", "placement_instructions",
                    "interaction_kind", "slicer_op_category",
                )
            ])

        reused: Dict[str, str] = {}
        to_ground = []
        to_ground_meta = []  # (final_key, fingerprint) aligned with to_ground
        for idx, (step_num, sub_op) in enumerate(slicer_ops):
            final_key = f"cb_step_{step_num}_{idx}"
            fingerprint = _sub_op_fingerprint(step_num, sub_op)
            cached_code = cache.get(fingerprint)
            if (
                cached_code
                and step_num not in implicated_steps
                and "MISSING_EVIDENCE" not in cached_code
            ):
                reused[final_key] = cached_code
            else:
                to_ground.append((step_num, sub_op))
                to_ground_meta.append((final_key, fingerprint))

        if reused:
            self.on_progress(
                "ground", "Ground Slicer APIs",
                f"Reusing {len(reused)} previously grounded template(s) "
                f"(unchanged inputs); re-grounding {len(to_ground)}",
            )
        self.on_progress(
            "ground", "Ground Slicer APIs",
            f"Generating templates for {len(to_ground)} slicer_op operations..."
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

        _ext_name = (
            self._cookbook_def.extension_name
            if getattr(self, "_cookbook_def", None) else ""
        )
        generator = SlicerOpGenerator(
            llm_client=self.llm_client,
            skill_path=skill_path,
            on_progress=_on_op_progress,
            debug_path=debug_path,
            extension_name=_ext_name,
            extension_source_path=getattr(self, "_source_path", ""),
        )

        templates = dict(reused)
        if to_ground:
            # generator.generate keys results by position within the list it
            # was given; remap subset positions back to the full-enumeration
            # keys and refresh the reuse cache with the new groundings.
            generated = generator.generate(to_ground)
            for subset_idx, (final_key, fingerprint) in enumerate(to_ground_meta):
                step_num = to_ground[subset_idx][0]
                code = generated.get(f"cb_step_{step_num}_{subset_idx}", "")
                if code:
                    templates[final_key] = code
                    cache[fingerprint] = code
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
            "pipeline_version": PIPELINE_VERSION,
            "extension_name": extension_name,
            "extension_module_name": os.path.splitext(os.path.basename(scan_result.get("entry_module") or ""))[0],
            # logic_class is None (not merely absent) for a wizard-style module.
            "logic_class_name": (scan_result.get("logic_class") or {}).get("class_name", ""),
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
            # logic_class is None (not merely absent) for a wizard-style module.
            "logic_class_name": (scan_result.get("logic_class") or {}).get("class_name", ""),
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "source_type": "analyzed_extension",
            "source_path": scan_result.get("source_path", ""),
            # Every directory this module's source spans: the module folder plus
            # any sibling packages its files import (a wizard-step package in a
            # multi-module repo). The agent's ext:/installed-source search reads
            # these so runtime lookups see the SAME files the scan analyzed.
            "source_roots": ([scan_result.get("source_path", "")]
                             + list(scan_result.get("sibling_packages") or [])),
            "status": "draft",
            "tool_count": 1,
            "stages": stage_names,
        }

        return manifest, generators

    def _call_llm(
        self,
        user_prompt: str,
        call_class: Optional[str] = None,
        attempt: int = 0,
        validation_errors: Optional[list] = None,
    ) -> str:
        """Make an isolated LLM call and return the text response.

        If self._debug_dir is set, also saves the full input/output/thinking
        to a JSON file in the debug directory.

        Retries once on empty responses.

        Args:
            call_class: Pipeline call class ("analysis", "contract", "critic",
                "grounding", "generation", "repair") used to select sampling
                options (temperature). None keeps provider defaults.
            attempt: Re-ask attempt index, recorded in debug artifacts.
            validation_errors: Errors that triggered this re-ask, recorded in
                debug artifacts.
        """
        messages = [
            {"role": "system", "content": self._analyzer_prompt},
            {"role": "user", "content": user_prompt},
        ]
        options = self._llm_sampling_options(call_class)
        response = self.llm_client.chatIsolated(messages, options=options)
        message_text = response.get("message", "")

        # Retry once on empty responses
        if not message_text or not message_text.strip():
            logger.info("Empty LLM response, retrying once...")
            response = self.llm_client.chatIsolated(messages, options=options)
            message_text = response.get("message", "")

        # Debug saving
        if self._debug_dir:
            try:
                self._save_debug_call(
                    messages,
                    response,
                    extra={
                        "call_class": call_class,
                        "attempt": attempt,
                        "validation_errors": list(validation_errors or []),
                        "sampling_options": options or {},
                    },
                )
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

    def _save_debug_call(self, messages: list, response: dict, extra: Optional[dict] = None) -> None:
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
        if extra:
            debug_entry.update(extra)

        filename = f"{self._current_stage_label}_call_{call_index:03d}.json"
        filepath = os.path.join(self._debug_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(debug_entry, f, indent=2, ensure_ascii=False)

        # Surface each LLM call in the readable ui_output.log so the round's log
        # shows the call sequence (and rough cost), not just phase transitions.
        try:
            usage = response.get("usage", {}) or {}
            out_len = len(str(response.get("message", "") or ""))
            tok = usage.get("total_tokens")
            detail = (
                f"call {call_index:03d} -> {filename} (out {out_len} chars"
                + (f", {tok} tok" if tok else "")
                + ")"
            )
            self._emit_progress("llm_call", self._current_stage_label or "llm", detail)
        except Exception:
            logger.debug("llm_call progress emit failed", exc_info=True)

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
