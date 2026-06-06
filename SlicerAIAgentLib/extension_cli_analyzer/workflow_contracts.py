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
                            "effects": self._infer_callable_effects(node, source_segment),
                        }

        return {
            "logic_methods": logic_methods,
            "module_functions": module_functions,
        }

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

    @staticmethod
    def _infer_operation_intents_from_text(text: str, categories: Optional[List[str]] = None) -> List[str]:
        """Infer generic operation intents from cookbook/user-facing text."""
        text_l = _text_or_empty(text).lower()
        categories = categories or []
        intents = set()
        if "layout" in text_l:
            if any(word in text_l for word in ("change", "switch", "activate", "restore", "set")):
                intents.add("layout_activate")
            if any(word in text_l for word in ("register", "add layout", "create layout")):
                intents.add("layout_register")
        if "slice intersection" in text_l or "slice intersections" in text_l:
            if any(word in text_l for word in ("visibility", "visible", "show", "turn on", "toggle on")):
                intents.add("slice_intersection_visibility")
            if any(word in text_l for word in ("interaction", "translate", "rotate")):
                intents.add("slice_intersection_interaction")
        if any(cat == "markups_display" for cat in categories) or (
            "display" in text_l and "view" in text_l
        ):
            intents.add("view_display_scope")
        if any(cat == "module_switching" for cat in categories):
            intents.add("module_switch")
        return sorted(intents)

    def _infer_step_operation_intents(self, step: Dict) -> List[str]:
        categories = []
        text_parts = [_text_or_empty(step.get("description", ""))]
        for so in step.get("sub_operations", []) or []:
            text_parts.append(_text_or_empty(so.get("description", "")))
            category = so.get("slicer_op_category")
            if category:
                categories.append(category)
            text_parts.extend(_text_list(so.get("slicer_api_keywords", [])))
        if step.get("slicer_op_category"):
            categories.append(step.get("slicer_op_category"))
        return self._infer_operation_intents_from_text(" ".join(text_parts), categories)

    def _match_extension_function(
        self, description: str, function_names: List[str],
        function_inventory: Optional[Dict[str, Dict]] = None,
    ) -> Optional[str]:
        """Match an extension-owned module function to a cookbook description."""
        desc_tokens = set(self._role_keywords(description))
        if not desc_tokens:
            return None
        operation_intents = set(self._infer_operation_intents_from_text(description))
        function_inventory = function_inventory or {}
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
            effects = set((function_inventory.get(name) or {}).get("effects") or [])
            if "layout_activate" in operation_intents:
                if "layout_activate" in effects:
                    score += 3.0
                if "layout_register" in effects and "layout_activate" not in effects:
                    score -= 2.0
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
                only_name = layout_functions[0]
                effects = set((function_inventory.get(only_name) or {}).get("effects") or [])
                if (
                    "layout_activate" in operation_intents
                    and "layout_register" in effects
                    and "layout_activate" not in effects
                ):
                    return None
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
        if step.get("step_type") in ("interactive", "mixed"):
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
            response = self._call_llm(prompt)
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
        step_type = step.get("step_type", "")
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
        if step.get("step_type") == "user_choice":
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
            "module_functions": sorted(callable_inventory.get("module_functions", {}).keys()),
            "module_function_effects": {
                name: info.get("effects", [])
                for name, info in sorted(
                    callable_inventory.get("module_functions", {}).items()
                )
            },
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
                matched = self._match_extension_function(
                    description,
                    module_function_names,
                    callable_inventory.get("module_functions", {}),
                )
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
            if step.get("step_type") != "interactive":
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
        allow_module_switch = any(
            so.get("op_type") == "slicer_op"
            and so.get("slicer_op_category") == "module_switching"
            and self._is_explicit_module_switch_text(
                " ".join([
                    _text_or_empty(step.get("description")),
                    _text_or_empty(so.get("description")),
                    " ".join(_text_list(so.get("slicer_api_keywords", []))),
                ])
            )
            for so in sub_ops
        ) or (
            step.get("op_type") == "slicer_op"
            and self._is_explicit_module_switch_text(_text_or_empty(step.get("description")))
        )
        implementation_uses_slicer_api = bool(
            invokes_slicer_api
            or step_type in ("interactive", "mixed")
            or step.get("interaction_owner")
            or step.get("placement_starter_method")
            or step.get("extension_function_name")
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
