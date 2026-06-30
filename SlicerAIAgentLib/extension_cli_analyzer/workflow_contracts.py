from .common import *


class AnalyzerWorkflowContractsMixin:
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
                        source_segment = ast.get_source_segment(source, node) or ""
                        module_functions[node.name] = {
                            "name": node.name,
                            "line": node.lineno,
                            "source_file": entry_module,
                            "param_count": len([
                                arg for arg in node.args.args
                                if arg.arg not in ("self", "cls")
                            ]),
                            "effects": self._infer_callable_effects(node, source_segment),
                        }

        return {
            "logic_methods": logic_methods,
            "module_functions": module_functions,
            "logic_attributes": self._collect_logic_instance_attributes(
                scan_result, logic_analysis
            ),
        }

    @staticmethod
    def _collect_attr_target(target, names: set) -> None:
        """Add ``self.<name>`` assignment targets (incl. tuple unpacking) to names."""
        elements = target.elts if isinstance(target, (ast.Tuple, ast.List)) else [target]
        for elem in elements:
            if (
                isinstance(elem, ast.Attribute)
                and isinstance(elem.value, ast.Name)
                and elem.value.id == "self"
            ):
                names.add(elem.attr)

    def _collect_logic_instance_attributes(
        self, scan_result: Dict, logic_analysis: Dict,
    ) -> List[str]:
        """Collect member names defined on the Logic class via a static AST scan.

        Used to prove (or disprove) attribute accesses like ``logic.parameterNode``
        on the extension Logic receiver.  Proving NON-existence demands a
        deterministic scan, so we read the actual class source rather than rely on
        the LLM-derived ``state_fields``.  Collected members:
          - instance attributes assigned as ``self.<name> = ...`` in any method
          - class-level assignments
          - ``@property`` names and all method names
        The LLM ``state_fields`` names are unioned in as a low-risk supplement.
        """
        names: set = set()

        logic_info = scan_result.get("logic_class") or {}
        logic_file = logic_info.get("file", "") or logic_analysis.get("_logic_file", "")
        class_name = logic_info.get("class_name", "") or logic_analysis.get("class_name", "")
        source = ""
        if logic_file and class_name:
            try:
                source = self._extract_class_source(logic_file, class_name) or ""
            except Exception:
                source = ""
        if source:
            try:
                tree = ast.parse(source)
            except Exception:
                tree = None
            if tree is not None:
                class_def = next(
                    (n for n in ast.walk(tree)
                     if isinstance(n, ast.ClassDef) and n.name == class_name),
                    None,
                ) or next(
                    (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)),
                    None,
                )
                if class_def is not None:
                    # Instance attributes set as self.<name> = ... anywhere in the class.
                    for node in ast.walk(class_def):
                        if isinstance(node, ast.Assign):
                            for target in node.targets:
                                self._collect_attr_target(target, names)
                        elif isinstance(node, ast.AnnAssign):
                            self._collect_attr_target(node.target, names)
                    # Class-level assignments + method/property names.
                    for node in class_def.body:
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            names.add(node.name)
                        elif isinstance(node, ast.Assign):
                            for target in node.targets:
                                if isinstance(target, ast.Name):
                                    names.add(target.id)
                        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                            names.add(node.target.id)

        # Supplement with LLM-derived state fields (never the sole source).
        for field in logic_analysis.get("state_fields", []) or []:
            raw = field.get("name", "") if isinstance(field, dict) else field
            raw = _text_or_empty(raw)
            if raw.startswith("self."):
                raw = raw[len("self."):]
            raw = raw.split(".")[0].split("[")[0].strip()
            if raw.isidentifier():
                names.add(raw)

        return sorted(n for n in names if n and not n.startswith("__"))

    @staticmethod
    def _infer_callable_effects(node: Optional[ast.AST], source: str = "") -> List[str]:
        """Infer coarse side effects of an extension-owned callable."""
        effects = set()
        source_text = _text_or_empty(source)
        if node is not None:
            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    func = child.func
                    attr = func.attr if isinstance(func, ast.Attribute) else ""
                    name = func.id if isinstance(func, ast.Name) else ""
                    callee = attr or name
                    if callee == "AddLayoutDescription":
                        effects.add("layout_register")
                    elif callee == "setLayout":
                        effects.add("layout_activate")
                    elif callee == "SetIntersectingSlicesEnabled":
                        effects.add("slice_intersection_global")
                    elif callee == "SetIntersectingSlicesVisibility":
                        effects.add("slice_intersection_display_node")
                    elif callee == "Modified":
                        effects.add("slice_view_refresh")
        # Lightweight fallback for source snippets that AST traversal could not
        # classify because wrappers/aliases obscure the direct receiver.
        if "AddLayoutDescription" in source_text:
            effects.add("layout_register")
        if ".setLayout(" in source_text or "setLayout(" in source_text:
            effects.add("layout_activate")
        if "SetIntersectingSlicesEnabled" in source_text:
            effects.add("slice_intersection_global")
        if "SetIntersectingSlicesVisibility" in source_text:
            effects.add("slice_intersection_display_node")
        if ".Modified(" in source_text or "Modified(" in source_text:
            effects.add("slice_view_refresh")
        return sorted(effects)

    def _infer_step_operation_intents(self, step: Dict) -> List[str]:
        intents = set(_text_list(step.get("operation_intents", [])))
        for so in step.get("sub_operations", []) or []:
            intents.update(_text_list(so.get("operation_intents", [])))
            if so.get("operation_intent"):
                intents.add(_text_or_empty(so.get("operation_intent")))
        if step.get("operation_intent"):
            intents.add(_text_or_empty(step.get("operation_intent")))
        return sorted(i for i in intents if i)

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

    def _step_interaction_node_class(self, step: Dict) -> str:
        """Return the node class requested by a user interaction step."""
        if step.get("node_class"):
            return step.get("node_class", "")
        for so in step.get("sub_operations", []) or []:
            if so.get("op_type") == "user_interaction" and so.get("node_class"):
                return so.get("node_class", "")
        return ""

    def _step_has_user_interaction_for_node_class(self, step: Dict, node_class: str) -> bool:
        """Return True if a step already contains an interaction for node_class."""
        if not node_class:
            return False
        if _legacy_step_type_for_operation(_operation_type_for_step(step)) in ("interactive", "mixed"):
            if self._step_interaction_node_class(step) == node_class:
                return True
            for so in step.get("sub_operations", []) or []:
                if (
                    so.get("op_type") == "user_interaction"
                    and so.get("node_class") == node_class
                ):
                    return True
        return False

    def _placement_starter_supports_node_class(self, method_name: str, node_class: str) -> bool:
        """Return True when a placement-starter method can create node_class."""
        if not method_name or not node_class:
            return False
        info = self._placement_starter_methods.get(method_name) or {}
        node_classes = info.get("node_classes") or []
        if not node_classes:
            return True
        return node_class in node_classes

    def _find_recent_placement_starter_for_interaction(
        self,
        steps: List[Dict],
        step_index: int,
        max_lookback: int = 5,
    ) -> Dict[str, Any]:
        """Find a recent extension placement starter for an interaction step.

        Cookbook steps are user-facing, so display/layout/module configuration
        may sit between "click Add markup" and "draw/place it".  This helper
        keeps that continuity without relying on extension-specific wording.
        """
        if step_index <= 0 or step_index >= len(steps):
            return {}
        interaction_step = steps[step_index]
        node_class = self._step_interaction_node_class(interaction_step)
        if not self._is_markup_node_class(node_class):
            return {}

        start_index = max(0, step_index - max_lookback)
        for previous_index in range(step_index - 1, start_index - 1, -1):
            previous_step = steps[previous_index]
            if self._step_has_user_interaction_for_node_class(previous_step, node_class):
                return {}
            starter = self._step_placement_starter(previous_step)
            if not starter:
                continue
            if not self._placement_starter_supports_node_class(starter, node_class):
                continue
            return {
                "method": starter,
                "step_id": previous_step.get("step_id", ""),
                "node_class": node_class,
                "lookback_steps": step_index - previous_index,
                "reason": "recent_same_node_class_placement_starter",
            }
        return {}

    def _synthesize_workflow_ui_guidance(
        self,
        workflow_graph: Dict,
        metadata: Dict,
        scan_result: Dict,
        logic_analysis: Dict,
    ) -> None:
        """Attach user-facing workflow guidance to each generated workflow step."""
        if not workflow_graph:
            return
        metadata = metadata if isinstance(metadata, dict) else {}
        steps = workflow_graph.get("steps", []) or []
        if not steps:
            return

        fallback_by_step = {
            step.get("step_id", ""): self._fallback_ui_guidance(step, metadata)
            for step in steps
            if step.get("step_id")
        }
        llm_guidance = self._llm_ui_guidance(
            steps,
            metadata,
            scan_result,
            logic_analysis,
            fallback_by_step,
        )

        metadata.setdefault("ui_guidance", {})
        for step in steps:
            step_id = step.get("step_id", "")
            if not step_id:
                continue
            guidance = self._validate_ui_guidance(
                llm_guidance.get(step_id) if isinstance(llm_guidance, dict) else None,
                fallback_by_step.get(step_id, {}),
            )
            step["ui_guidance"] = guidance
            metadata["ui_guidance"][step_id] = guidance

    def _llm_ui_guidance(
        self,
        steps: List[Dict],
        metadata: Dict,
        scan_result: Dict,
        logic_analysis: Dict,
        fallback_by_step: Dict[str, Dict],
    ) -> Dict[str, Dict]:
        """Ask the LLM for compact UI guidance; return {} on any uncertainty."""
        if not self.llm_client:
            return {}
        contexts = [
            self._build_guidance_context(step, metadata, fallback_by_step.get(step.get("step_id", ""), {}))
            for step in steps
        ]
        extension_name = (
            scan_result.get("module_name")
            or scan_result.get("extension_name")
            or scan_result.get("logic_class", {}).get("class_name", "")
            or logic_analysis.get("class_name", "")
            or "the extension"
        )
        prompt = textwrap.dedent(f"""\
            You are creating user-facing workflow guidance for a 3D Slicer extension.

            Extension: {extension_name}

            Rewrite cookbook-like steps into concise UI labels and instructions.
            Focus on what the user should do now, not implementation details.
            For repeated placement steps, describe exactly one item per Done click.
            Do not tell the user to type done. The UI has a Done button.

            Return ONLY JSON:
            {{
              "steps": [
                {{
                  "step_id": "cb_step_1",
                  "ui_guidance": {{
                    "title": "short action label",
                    "instruction": "one concise instruction or empty string",
                    "done_label": "Done",
                    "choice_label": "",
                    "input_label": "",
                    "object_label": "plane",
                    "repeat": {{"summary": "", "current": null, "total_source": ""}}
                  }}
                }}
              ]
            }}

            Workflow contexts:
            {json.dumps(contexts, indent=2)}
            """)
        try:
            response = self._call_llm(prompt, call_class="contract")
            parsed = self._parse_json_response(response)
        except Exception:
            logger.debug("UI guidance synthesis failed", exc_info=True)
            return {}
        if not isinstance(parsed, dict):
            return {}
        result = {}
        for item in parsed.get("steps", []) or []:
            if not isinstance(item, dict):
                continue
            step_id = item.get("step_id", "")
            guidance = item.get("ui_guidance", {})
            if step_id and isinstance(guidance, dict):
                result[step_id] = guidance
        return result

    def _build_guidance_context(self, step: Dict, metadata: Dict, fallback: Dict) -> Dict:
        """Return compact, sanitized context for UI guidance synthesis."""
        step_id = step.get("step_id", "")
        return {
            "step_id": step_id,
            "step_type": step.get("step_type", ""),
            "operation_type": _operation_type_for_step(step),
            "op_type": step.get("op_type", ""),
            "description": _text_or_empty(step.get("description", ""))[:500],
            "interaction_type": step.get("interaction_type", ""),
            "interaction_kind": step.get("interaction_kind", ""),
            "node_class": self._step_interaction_node_class(step),
            "choice_info": step.get("choice_info", {}),
            "repeat_group": step.get("repeat_group", {}),
            "interaction_owner": step.get("interaction_owner", ""),
            "placement_starter_method": step.get("placement_starter_method", ""),
            "operation_model": step.get("operation_model") or metadata.get("operation_model", {}).get(step_id, {}),
            "node_roles": step.get("node_roles") or metadata.get("node_roles", {}).get(step_id, []),
            "fallback_ui_guidance": fallback,
        }

    def _validate_ui_guidance(self, candidate: Optional[Dict], fallback: Dict) -> Dict:
        """Return candidate guidance if it is usable, otherwise deterministic fallback."""
        fallback = dict(fallback or {})
        if not isinstance(candidate, dict):
            return fallback
        guidance = dict(fallback)
        for key in ("title", "instruction", "done_label", "choice_label", "input_label", "object_label"):
            value = _text_or_empty(candidate.get(key, "")).strip()
            if value:
                guidance[key] = value[:240] if key == "instruction" else value[:80]
        repeat = candidate.get("repeat")
        if isinstance(repeat, dict):
            clean_repeat = dict(guidance.get("repeat") or {})
            summary = _text_or_empty(repeat.get("summary", "")).strip()
            if summary:
                clean_repeat["summary"] = summary[:80]
            total_source = _text_or_empty(repeat.get("total_source", "")).strip()
            if total_source:
                clean_repeat["total_source"] = total_source[:80]
            guidance["repeat"] = clean_repeat
        return guidance

    def _fallback_ui_guidance(self, step: Dict, metadata: Dict) -> Dict:
        """Build deterministic user-facing guidance from generic workflow semantics."""
        operation_type = _operation_type_for_step(step)
        step_type = _legacy_step_type_for_operation(operation_type)
        description = _text_or_empty(step.get("description", "")).strip()
        object_label = self._guidance_object_label(step)
        repeat_group = step.get("repeat_group") or {}
        is_repeat_interaction = self._is_repeat_interaction_step(step)

        guidance = {
            "title": self._clean_guidance_title(description) or "Workflow step",
            "instruction": "",
            "done_label": "Done",
            "choice_label": "",
            "input_label": "",
            "object_label": object_label,
            "repeat": {},
        }

        if step_type in ("interactive", "mixed"):
            action = "Place" if object_label not in ("interaction", "view") else "Complete"
            if is_repeat_interaction:
                guidance["title"] = f"{action} {object_label}"
                guidance["instruction"] = (
                    f"Place this {object_label}, then click Done."
                    if action == "Place"
                    else "Complete this interaction, then click Done."
                )
                guidance["done_label"] = f"{object_label.title()} placed" if action == "Place" else "Done"
            else:
                guidance["title"] = self._interaction_guidance_title(step, object_label)
                guidance["instruction"] = self._interaction_guidance_instruction(step, object_label)
                guidance["done_label"] = "Done"
        elif step_type == "user_choice":
            choice_info = step.get("choice_info", {}) or {}
            question = _text_or_empty(choice_info.get("question") or description)
            label = self._choice_guidance_label(step, object_label)
            guidance["title"] = question or f"Choose {label}"
            guidance["choice_label"] = label
            guidance["input_label"] = label
            guidance["instruction"] = (
                f"Enter {label.lower()}."
                if not choice_info.get("choices")
                else "Choose one option."
            )
        elif step_type == "branch":
            guidance["title"] = self._clean_guidance_title(description) or "Optional step"
            guidance["instruction"] = "Choose whether to run this optional step."
        else:
            guidance["title"] = self._automated_guidance_title(step)
            guidance["instruction"] = ""

        if repeat_group:
            guidance["repeat"] = {
                "summary": f"{object_label.title()} {{current}} of {{total}}",
                "current": None,
                "total_source": repeat_group.get("count_step", ""),
                "group_id": repeat_group.get("group_id", ""),
            }
        return guidance

    @staticmethod
    def _clean_guidance_title(text: str) -> str:
        """Convert a cookbook sentence into a compact label."""
        text = _re.sub(r"\s+", " ", _text_or_empty(text)).strip(" .")
        text = _re.sub(r"^(click|press|select|choose)\s+", lambda m: m.group(1).title() + " ", text, flags=_re.I)
        if len(text) > 80:
            text = text[:77].rstrip() + "..."
        return text

    def _guidance_object_label(self, step: Dict) -> str:
        """Return the object the user is manipulating or choosing."""
        text = " ".join([
            _text_or_empty(step.get("description", "")),
            _text_or_empty((step.get("choice_info") or {}).get("question", "")),
            " ".join(_text_or_empty(so.get("description", "")) for so in step.get("sub_operations", []) or []),
        ]).lower()
        if "cut" in text and "plane" in text:
            return "cutting plane"
        object_name = self._interaction_object_name(step)
        if object_name and object_name != "placement":
            return object_name
        if "plane" in text:
            return "plane"
        if "curve" in text:
            return "curve"
        if "side" in text:
            return "side"
        if "number" in text or "how many" in text or "count" in text:
            return "value"
        if _operation_type_for_step(step) == "user_choice":
            return "choice"
        if "view" in text or "slice" in text:
            return "view"
        return "interaction"

    def _interaction_guidance_title(self, step: Dict, object_label: str) -> str:
        if object_label in ("view", "interaction"):
            return self._clean_guidance_title(step.get("description", "")) or "Adjust view"
        verb = "Draw" if object_label == "curve" else "Place"
        return f"{verb} {object_label}"

    def _interaction_guidance_instruction(self, step: Dict, object_label: str) -> str:
        if object_label == "curve":
            return "Draw the curve, then click Done."
        if object_label in ("plane", "cutting plane", "line", "point", "fiducial"):
            return f"Place this {object_label}, then click Done."
        current = self._interaction_instructions_for_template(step)
        return _text_or_empty(current).strip() or "Complete the interaction, then click Done."

    def _choice_guidance_label(self, step: Dict, object_label: str) -> str:
        choice_info = step.get("choice_info", {}) or {}
        text = " ".join([
            _text_or_empty(choice_info.get("parameter_name", "")),
            _text_or_empty(choice_info.get("question", "")),
            _text_or_empty(step.get("description", "")),
        ]).lower()
        if any(token in text for token in ("how many", "number", "count", "num")):
            if object_label == "cutting plane":
                return "Number of cutting planes"
            if object_label and object_label not in ("choice", "value", "interaction"):
                return f"Number of {object_label}s"
            return "Number"
        if object_label == "side":
            return "Side"
        if object_label and object_label not in ("choice", "interaction"):
            return object_label.title()
        return "Choice"

    def _automated_guidance_title(self, step: Dict) -> str:
        intents = set((step.get("operation_model") or {}).get("operation_intents") or [])
        if "layout_activate" in intents:
            return "Update layout"
        if "slice_intersection_visibility" in intents:
            return "Update slice visibility"
        return self._clean_guidance_title(step.get("description", "")) or "Run step"

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
            "logic_attributes": list(callable_inventory.get("logic_attributes", []) or []),
            "module_functions": sorted(callable_inventory.get("module_functions", {}).keys()),
            "module_function_effects": {
                name: info.get("effects", [])
                for name, info in sorted(
                    callable_inventory.get("module_functions", {}).items()
                )
            },
            "module_function_param_counts": {
                name: info.get("param_count", 0)
                for name, info in sorted(
                    callable_inventory.get("module_functions", {}).items()
                )
            },
        }

        steps = workflow_graph.get("steps", []) or []
        by_step = {step.get("step_id", ""): step for step in steps}
        self._validate_repeat_block_graph(workflow_graph, by_step)

        self._promote_closed_form_parameter_choices(steps)
        module_function_names = sorted(callable_inventory.get("module_functions", {}).keys())
        for step in steps:
            for so in step.get("sub_operations", []) or []:
                if so.get("op_type") != "extension_op":
                    continue
                if so.get("extension_method_hint") or so.get("extension_function_hint"):
                    continue
                text = " ".join([
                    _text_or_empty(so.get("description")),
                    _text_or_empty(step.get("description")),
                ])
                text_keywords = set(self._role_keywords(text))
                candidates = []
                for function_name in module_function_names:
                    score = len(text_keywords & set(self._role_keywords(function_name)))
                    if score:
                        candidates.append((score, function_name))
                if candidates:
                    candidates.sort(reverse=True)
                    if len(candidates) == 1 or candidates[0][0] > candidates[1][0]:
                        so["extension_function_hint"] = candidates[0][1]

        # Canonicalize count-driven placement repeats.  The starter call belongs
        # to the repeat start step; the following interaction step reuses that
        # node and must not call the same starter again.
        for group in (metadata.get("repeat_groups") or {}).values():
            start_step = by_step.get(group.get("start_step", ""))
            interaction_step = by_step.get(group.get("interaction_step", ""))
            if not start_step or not interaction_step:
                continue
            self._normalize_repeat_interaction_instructions(interaction_step)
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
            if has_user_interaction:
                interaction_step["operation_type"] = "user_interaction"
                interaction_step["op_type"] = "user_interaction"
                interaction_step["step_type"] = "user_interaction"

            start_step["interaction_owner"] = "extension_method"
            start_step["placement_starter_method"] = start_starter
            start_step["created_node_source"] = "extension_method"
            starter_info = self._placement_starter_info(start_starter)
            interaction_policy = self._placement_mode_policy(interaction_step, starter_info)
            metadata.setdefault("interaction_policies", {})[interaction_step["step_id"]] = {
                "interaction_owner": interaction_step["interaction_owner"],
                "placement_starter_method": start_starter,
                "created_node_source": interaction_step["created_node_source"],
                "placement_mode": starter_info.get("placement_mode", ""),
                "generated_placement_policy": interaction_policy,
            }
            metadata.setdefault("interaction_policies", {})[start_step["step_id"]] = {
                "interaction_owner": start_step["interaction_owner"],
                "placement_starter_method": start_starter,
                "created_node_source": start_step["created_node_source"],
                "placement_mode": starter_info.get("placement_mode", ""),
            }

        # Bind user interactions to recent extension placement starters even
        # when Slicer-core display/layout configuration steps intervene.
        for step_index, step in enumerate(steps):
            if _legacy_step_type_for_operation(_operation_type_for_step(step)) != "interactive":
                continue
            if step.get("placement_starter_method"):
                continue
            binding = self._find_recent_placement_starter_for_interaction(
                steps, step_index
            )
            if not binding:
                continue
            starter = binding.get("method", "")
            if not starter:
                continue
            step["interaction_owner"] = "previous_extension_method"
            step["placement_starter_method"] = starter
            step["created_node_source"] = "previous_extension_method"
            step["placement_starter_step_id"] = binding.get("step_id", "")
            step["placement_binding_reason"] = binding.get("reason", "")
            starter_info = self._placement_starter_info(starter)
            interaction_policy = self._placement_mode_policy(step, starter_info)
            metadata.setdefault("interaction_policies", {})[step["step_id"]] = {
                "interaction_owner": step["interaction_owner"],
                "placement_starter_method": starter,
                "created_node_source": step["created_node_source"],
                "placement_starter_step_id": binding.get("step_id", ""),
                "placement_binding_reason": binding.get("reason", ""),
                "node_class": binding.get("node_class", ""),
                "lookback_steps": binding.get("lookback_steps"),
                "placement_mode": starter_info.get("placement_mode", ""),
                "generated_placement_policy": interaction_policy,
            }
            starter_step = by_step.get(binding.get("step_id", ""))
            if starter_step:
                starter_step["interaction_owner"] = "extension_method"
                starter_step["placement_starter_method"] = starter
                starter_step["created_node_source"] = "extension_method"

        for step in steps:
            if step.get("extension_function_name"):
                continue
            function_hints = [
                so.get("extension_function_hint")
                for so in step.get("sub_operations", []) or []
                if so.get("op_type") == "extension_op" and so.get("extension_function_hint")
            ]
            function_hints = sorted(set(hint for hint in function_hints if hint))
            if len(function_hints) == 1 and not step.get("method_name"):
                step["extension_function_name"] = function_hints[0]

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

    @staticmethod
    def _validate_repeat_block_graph(
        workflow_graph: Dict,
        by_step: Dict[str, Dict],
    ) -> None:
        """Validate generic repeat control without changing atomic step types."""
        ordered_ids = [
            step.get("step_id", "")
            for step in workflow_graph.get("steps", []) or []
            if step.get("step_id")
        ]
        used_ranges = []  # (lo, hi) ordered-index spans of prior repeat bodies
        repeat_ids = set()
        for block in workflow_graph.get("repeat_blocks", []) or []:
            repeat_id = block.get("repeat_id", "")
            body_steps = block.get("body_steps", []) or []
            controller = block.get("controller", {}) or {}
            kind = controller.get("kind", "")
            if not repeat_id or repeat_id in repeat_ids:
                raise RuntimeError("Repeat blocks require unique non-empty repeat_id values")
            repeat_ids.add(repeat_id)
            if not body_steps or any(step_id not in by_step for step_id in body_steps):
                raise RuntimeError(f"{repeat_id}: repeat body references missing workflow steps")
            indexes = [ordered_ids.index(step_id) for step_id in body_steps]
            if indexes != list(range(min(indexes), max(indexes) + 1)):
                raise RuntimeError(f"{repeat_id}: repeat body must be contiguous and ordered")
            lo, hi = min(indexes), max(indexes)
            for blo, bhi in used_ranges:
                # Allow disjoint OR fully-contained (nested) bodies -- a loop inside
                # a one-time conditional is legitimate control flow. Reject only a
                # crossing/partial overlap.
                disjoint = hi < blo or lo > bhi
                contained = (lo >= blo and hi <= bhi) or (blo >= lo and bhi <= hi)
                if not (disjoint or contained):
                    raise RuntimeError(
                        f"{repeat_id}: crossing/partial overlap of repeat bodies is not supported"
                    )
            used_ranges.append((lo, hi))
            if block.get("entry_step") != body_steps[0]:
                raise RuntimeError(f"{repeat_id}: entry_step must be the first body step")
            if block.get("terminal_step") != body_steps[-1]:
                raise RuntimeError(f"{repeat_id}: terminal_step must be the last body step")
            exit_step = block.get("exit_step", "")
            if exit_step and exit_step not in by_step:
                raise RuntimeError(f"{repeat_id}: exit_step references a missing workflow step")
            if kind not in {"count", "until_choice", "while_choice"}:
                raise RuntimeError(f"{repeat_id}: unsupported repeat controller '{kind}'")
            if int(block.get("max_iterations", 0) or 0) <= 0:
                raise RuntimeError(f"{repeat_id}: max_iterations must be greater than zero")
            if kind == "count":
                source_step = controller.get("source_step", "")
                if source_step not in by_step:
                    raise RuntimeError(f"{repeat_id}: count controller source step is missing")
                if _operation_type_for_step(by_step[source_step]) != "user_choice":
                    raise RuntimeError(f"{repeat_id}: count controller source must be user_choice")
                if source_step in body_steps:
                    raise RuntimeError(f"{repeat_id}: count controller source cannot be in its body")
                if ordered_ids.index(source_step) >= ordered_ids.index(body_steps[0]):
                    raise RuntimeError(f"{repeat_id}: count controller source must precede its body")
            else:  # until_choice / while_choice — a pre-guarded conditional section
                if not _text_or_empty(controller.get("prompt", "")):
                    raise RuntimeError(f"{repeat_id}: choice controller requires a prompt")
                source_step = controller.get("source_step", "")
                if not source_step or source_step not in by_step:
                    raise RuntimeError(f"{repeat_id}: until/while controller requires a source step")
                if _operation_type_for_step(by_step[source_step]) not in ("user_choice", "branch_op"):
                    raise RuntimeError(f"{repeat_id}: until/while controller source must be user_choice or branch_op")
                # Decision-at-end LOOP-BACK: the decision IS the terminal step and
                # accept jumps backward to entry (a per-item loop). Its source is in
                # the body (the last step), so skip the pre-guard "source precedes
                # body" checks; the forward/stop exit is still validated below.
                is_loop_back = source_step == block.get("terminal_step") or bool(controller.get("loop_back"))
                if is_loop_back:
                    if source_step != block.get("terminal_step"):
                        raise RuntimeError(f"{repeat_id}: loop_back controller source must be the terminal step")
                else:
                    if source_step in body_steps:
                        raise RuntimeError(f"{repeat_id}: until/while controller source cannot be in its body")
                    if ordered_ids.index(source_step) >= ordered_ids.index(body_steps[0]):
                        raise RuntimeError(f"{repeat_id}: until/while controller source must precede its body")
                # A jump/exit target (when set) must come after the body (forward),
                # never inside it (an "" exit_step means stop -> end of workflow).
                if exit_step:
                    if exit_step in body_steps:
                        raise RuntimeError(f"{repeat_id}: exit_step cannot be inside the repeat body")
                    if ordered_ids.index(exit_step) <= ordered_ids.index(body_steps[-1]):
                        raise RuntimeError(f"{repeat_id}: exit_step must come after the repeat body")

    @staticmethod
    def _choice_is_closed_form_parameter_choice(choice_info: Dict) -> bool:
        choices = choice_info.get("choices") or []
        if not choices:
            return False
        values = {
            str(choice.get("value", "")).strip().lower()
            for choice in choices
        }
        labels = {
            str(choice.get("label", "")).strip().lower()
            for choice in choices
        }
        closed_values = {
            "true", "false", "yes", "no",
            "left", "right", "left leg", "right leg",
            "left side", "right side",
        }
        return bool(values or labels) and (values | labels) <= closed_values

    def _promote_closed_form_parameter_choices(self, steps: List[Dict]) -> None:
        """Closed-form parameter questions must ask first, then apply choice."""
        for step in steps or []:
            choice_info = step.get("choice_info") or {}
            if not self._choice_is_closed_form_parameter_choice(choice_info):
                continue
            parameter_name = choice_info.get("parameter_name", "")
            if not parameter_name:
                continue
            sub_ops = step.get("sub_operations", []) or []
            matching_ops = [
                so for so in sub_ops
                if (
                    so.get("operation_intent") == "extension_parameter_update"
                    and so.get("parameter_name") == parameter_name
                )
            ]
            if not matching_ops:
                continue
            step["step_type"] = "user_choice"
            step["operation_type"] = "user_choice"
            step["op_type"] = "user_choice"
            for so in matching_ops:
                so["op_type"] = "user_choice"
                so["evidence_type"] = "user_context"
                so["question"] = choice_info.get("question") or so.get("question") or step.get("description")
                so["choices"] = choice_info.get("choices", [])
                so["default_value"] = choice_info.get("default_value")

    def _build_step_operation_model(self, step: Dict) -> Dict:
        """Describe a workflow step using generic operation semantics."""
        step_type = _operation_type_for_step(step)
        sub_ops = step.get("sub_operations", []) or []
        op_types = [so.get("op_type", "") for so in sub_ops if so.get("op_type")]
        if step_type:
            op_types.append(step_type)
        op_types = sorted(set(op_types))

        interaction_kinds = []
        for so in sub_ops:
            if so.get("op_type") == "user_interaction":
                kind = so.get("interaction_kind") or so.get("interaction_type") or "interaction"
                interaction_kinds.append(kind)
        if step_type in ("user_interaction", "interactive"):
            interaction_kinds.append(
                step.get("interaction_kind")
                or step.get("interaction_type")
                or "interaction"
            )

        produces_interaction_state = (
            step_type in ("user_interaction", "interactive", "mixed")
            or any(so.get("op_type") == "user_interaction" for so in sub_ops)
        )
        invokes_extension_method = bool(step.get("method_name")) or any(
            so.get("extension_method_hint") for so in sub_ops
        )
        invokes_extension_function = bool(step.get("extension_function_name")) or any(
            so.get("extension_function_hint") for so in sub_ops
        )
        invokes_slicer_api = (
            step_type == "slicer_op"
            or any(so.get("op_type") == "slicer_op" for so in sub_ops)
            or any(
                so.get("operation_intent") == "extension_node_reference_update"
                for so in sub_ops
            )
        )
        semantic_intents = set(self._infer_step_operation_intents(step))
        allow_module_switch = (
            "module_switch" in semantic_intents
            or any(
                so.get("op_type") == "slicer_op"
                and so.get("slicer_op_category") == "module_switching"
                for so in sub_ops
            )
        )
        implementation_uses_slicer_api = bool(
            invokes_slicer_api
            or step_type in ("user_interaction", "interactive", "mixed")
            or step.get("interaction_owner")
            or step.get("placement_starter_method")
            or step.get("extension_function_name")
            or any(
                so.get("operation_intent") == "extension_node_reference_update"
                for so in sub_ops
            )
        )
        operation_intents = self._infer_step_operation_intents(step)
        return {
            "step_type": step_type,
            "op_types": op_types,
            "operation_intents": operation_intents,
            "invokes_extension_method": invokes_extension_method,
            "invokes_extension_function": invokes_extension_function,
            "invokes_slicer_api": invokes_slicer_api,
            "implementation_uses_slicer_api": implementation_uses_slicer_api,
            "allow_module_switch": allow_module_switch,
            "produces_interaction_state": produces_interaction_state,
            "interaction_kinds": sorted(set(interaction_kinds)),
        }

    def _infer_step_node_roles(self, step: Dict, metadata: Dict) -> List[Dict]:
        """Infer generic node roles produced or consumed by a workflow step."""
        semantic_roles = [
            role for role in (step.get("node_roles") or [])
            if isinstance(role, dict)
        ]
        for so in step.get("sub_operations", []) or []:
            semantic_roles.extend(
                role for role in (so.get("node_roles") or [])
                if isinstance(role, dict)
            )
        if semantic_roles:
            unique = []
            seen = set()
            for role in semantic_roles:
                key = (
                    role.get("role_kind", ""),
                    role.get("step_id", ""),
                    role.get("node_class", ""),
                    role.get("parameter_name", ""),
                )
                if key not in seen:
                    seen.add(key)
                    unique.append(role)
            return unique
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
            if sid in metadata.get("ui_guidance", {}):
                step["ui_guidance"] = metadata["ui_guidance"][sid]
