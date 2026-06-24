from .common import *

_PRECONDITION_BEGIN = "# precondition:begin"
_PRECONDITION_END = "# precondition:end"


class AnalyzerValidationSemanticsMixin:
    @staticmethod
    def _is_extension_module_import(module_name: str) -> bool:
        """Return whether an import name represents extension code."""
        top = _text_or_empty(module_name).split(".")[0]
        if not top:
            return False
        non_extension_imports = {
            "slicer", "SlicerAIAgentLib", "vtk", "qt", "ctk", "logging",
            "os", "sys", "json", "re", "abc", "typing", "functools",
            "collections", "itertools", "math", "time", "copy",
            "pathlib", "io", "traceback", "warnings", "numpy",
        }
        if top in non_extension_imports:
            return False
        return not top.startswith(("vtkMRML", "vtkSlicer", "qSlicer", "qMRML"))

    @staticmethod
    def _template_calls_select_module(code: str) -> bool:
        return bool(_re.search(r"\bslicer\s*\.\s*util\s*\.\s*selectModule\s*\(", code))

    @staticmethod
    def _template_enters_markup_placement_mode(code: str) -> bool:
        return bool(_re.search(
            r"\b(SwitchToSinglePlaceMode|SwitchToPersistentPlaceMode|StartPlaceMode|SetPlaceModeEnabled)\s*\(",
            code or "",
        ))

    @staticmethod
    def _template_print_text_has_repeat_instruction(code: str) -> bool:
        printed = []
        for match in _re.finditer(r"\bprint\s*\(\s*([rubfRUBF]*)(['\"])(.*?)\2\s*\)", code or "", _re.DOTALL):
            printed.append(match.group(3))
        text = "\n".join(printed).lower()
        return bool(_re.search(
            r"\b(repeat|for each|each requested|requested .* times|continue placing)\b",
            text,
        ))

    @staticmethod
    def _validate_callable_reference_misuse(code: str) -> Dict[str, List[str]]:
        """Catch known Slicer functions accidentally used as attributes."""
        result = {"errors": [], "warnings": []}
        patterns = [
            (
                r"\bslicer\s*\.\s*util\s*\.\s*selectedModule\b(?!\s*\()",
                "slicer.util.selectedModule",
                "slicer.util.selectedModule()",
            ),
        ]
        for pattern, bad, good in patterns:
            if _re.search(pattern, code or ""):
                result["errors"].append(
                    f"CallableReferenceMisuse: used {bad} without calling it; "
                    f"use {good} when reading the active module name"
                )
        return result

    @staticmethod
    def _validate_user_instruction_text(code: str) -> Dict[str, List[str]]:
        """Reject invalid user-facing instructions such as 'Please None'."""
        result = {"errors": [], "warnings": []}
        invalid = []
        for match in _re.finditer(r"\bprint\s*\(\s*([rubfRUBF]*)(['\"])(.*?)\2\s*\)", code or "", _re.DOTALL):
            text = (match.group(3) or "").strip()
            lowered = text.lower()
            if _re.search(r"\bplease\s+(none|null|undefined|n/a|na)\b", lowered):
                invalid.append(text)
            elif lowered in {"please", "please.", "please:", "please -"}:
                invalid.append(text)
        for text in invalid:
            result["errors"].append(
                f"BadInstructionText: invalid user-facing instruction {text!r}; "
                "use the cookbook step description or a concrete interaction instruction"
            )
        return result

    @staticmethod
    def _expr_text(node) -> str:
        """Best-effort source text of an expression node (receiver chains)."""
        try:
            return ast.unparse(node)
        except Exception:
            parts = []
            cur = node
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Call) and isinstance(cur.func, (ast.Attribute, ast.Name)):
                return AnalyzerValidationSemanticsMixin._expr_text(cur.func) + "()"
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))

    def _collect_parameter_writes(self, code: str) -> List[Tuple[str, str, int]]:
        """Literal (kind, role, lineno) writes on the extension parameter node.

        Only LITERAL string roles on parameter-node receivers are collected —
        dynamic role names (variables, f-strings) are intentionally skipped to
        avoid false positives.
        """
        writes: List[Tuple[str, str, int]] = []
        try:
            tree = ast.parse(code or "")
        except SyntaxError:
            return writes
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            attr = node.func.attr
            if attr not in ("SetParameter", "SetNodeReferenceID"):
                continue
            receiver = self._expr_text(node.func.value)
            if "parameterNode" not in receiver and "getParameterNode" not in receiver:
                continue
            if not node.args:
                continue
            role_arg = node.args[0]
            role = None
            if isinstance(role_arg, ast.Constant) and isinstance(role_arg.value, str):
                role = role_arg.value
            elif hasattr(ast, "Str") and isinstance(role_arg, ast.Str):  # py<3.8
                role = role_arg.s
            if role:
                writes.append((attr, role, getattr(node, "lineno", 0)))
        return writes

    def _validate_parameter_role_contract(self, code: str) -> Dict[str, List[str]]:
        """Reject writes to parameter/reference roles that don't exist or that
        the called method produces internally.

        Generic cause→effect fidelity: only roles present in the
        source-derived metadata exist, and roles a called method derives
        itself (requirement 'produced_by_method') must never be pre-set by
        the caller — fabricated bookkeeping (e.g. seeding a folder reference
        from the scene root) is how templates crash at runtime.
        """
        result = {"errors": [], "warnings": []}
        metadata = self._workflow_metadata if isinstance(self._workflow_metadata, dict) else {}
        bindings = metadata.get("parameter_bindings") or {}
        if not bindings:
            return result  # no source metadata available — cannot judge
        writes = self._collect_parameter_writes(code)
        if not writes:
            return result
        dependencies = metadata.get("parameter_method_dependencies") or {}
        produced_roles: Dict[str, str] = {}
        for method in self._extension_methods_called_by_template(code):
            requirements = (dependencies.get(method) or {}).get("node_requirements") or {}
            for role, requirement in requirements.items():
                if (requirement or {}).get("requirement") == "produced_by_method":
                    produced_roles[role] = method
        for kind, role, lineno in writes:
            if role not in bindings:
                result["errors"].append(
                    f"InventedParameterRole: template writes parameter/reference role "
                    f"'{role}' (line {lineno}) that is not in source-derived metadata; "
                    "remove the block — never invent role names"
                )
            elif role in produced_roles:
                result["errors"].append(
                    f"InventedParameterRole: role '{role}' is produced internally by "
                    f"logic.{produced_roles[role]}(); remove the caller-side write "
                    f"(line {lineno})"
                )
        return result

    def _validate_parameter_effect_application(self, code: str) -> Dict[str, List[str]]:
        """Require evidence-backed effect application after parameter writes.

        A bare SetParameter only records state; when the metadata knows a
        high-confidence applier method (a logic method that reads the
        parameter and is name-similar to it), the template must call it with
        the explicit final state. Satisfied automatically when any called
        method reads the role (init-then-call and record-for-later patterns).
        """
        result = {"errors": [], "warnings": []}
        metadata = self._workflow_metadata if isinstance(self._workflow_metadata, dict) else {}
        appliers_by_role = metadata.get("parameter_appliers") or {}
        if not appliers_by_role:
            return result
        effects = metadata.get("method_parameter_effects") or {}
        writes = [
            entry for entry in self._collect_parameter_writes(code)
            if entry[0] == "SetParameter"
        ]
        if not writes:
            return result
        called_methods = set(self._extension_methods_called_by_template(code))
        for _, role, lineno in writes:
            if any(
                role in set((effects.get(method) or {}).get("reads") or [])
                for method in called_methods
            ):
                continue  # cause→effect satisfied by a called reader/applier
            # Shared selection rule with the template emitter: BLOCK only on
            # the one applier the emitter itself would emit. Demanding any
            # other candidate creates an unfixable deadlock (the emitter
            # refuses ambiguous evidence by design).
            selected = self._select_unambiguous_applier(role)
            if selected is not None:
                if selected.get("method") in called_methods:
                    continue  # cause→effect satisfied by the selected applier
                result["errors"].append(
                    f"ParameterEffectNotApplied: template sets parameter '{role}' "
                    f"(line {lineno}) but never calls an evidence-backed applier; call "
                    f"logic.{selected['method']}(<explicit final state>) after SetParameter "
                    "— parameter writes alone only record state and GUI observers may "
                    "recompute it differently"
                )
                continue
            high = [
                a for a in appliers_by_role.get(role, [])
                if a.get("confidence") == "high"
            ]
            if high:
                names = ", ".join(sorted(a.get("method", "") for a in high)[:4])
                result["warnings"].append(
                    f"Parameter '{role}' (line {lineno}) has ambiguous applier "
                    f"evidence ({names}); no applier emitted or required — verify "
                    "the parameter's effect is applied at runtime"
                )
        return result

    _INTERACTION_ENABLE_RE = _re.compile(
        r"\b(\w*Interactive\w*|\w*InteractionHandle\w*|\w*HandleVisibility\w*|\w*InteractiveHandles\w*)\s*\("
    )
    # Morpheme stems covering interaction vocabulary (interact/interactive,
    # handle/handles, rotate/rotation, translate/translation, ...).
    _INTERACTION_TEXT_TOKENS = (
        "interact", "handle", "drag", "rotat", "translat", "manipulat",
        "adjust", "edit", "move",
    )

    def _validate_interaction_scope(self, code: str, gen: Dict) -> Dict:
        """Minimality backstop: interaction affordances need textual backing.

        A template may enable interaction/handle modes only when the step's
        own description/intents mention interaction. Doubly narrow trigger
        (interaction-shaped API enabled AND no interaction vocabulary in the
        step text) to avoid false positives.
        """
        result = {"errors": [], "warnings": []}
        code = code or ""
        offending = []
        for match in self._INTERACTION_ENABLE_RE.finditer(code):
            name = match.group(1)
            if name.endswith("On"):
                offending.append(name)
                continue
            rest = code[match.end():match.end() + 40]
            if _re.match(r"\s*(True|[1-9])\b", rest):
                offending.append(name)
        if not offending:
            return result
        text = self._display_scope_text(gen)
        if any(token in text for token in self._INTERACTION_TEXT_TOKENS):
            return result
        result["errors"].append(
            "InteractionScopeExceeded: template enables interaction/handle modes ("
            + ", ".join(sorted(set(offending))[:5])
            + ") but the step description does not request interaction; "
            "implement only the requested state change"
        )
        return result

    # ── paired-step mechanism consistency ──
    # Two steps that describe opposite states of the SAME control ("toggle on
    # X" / "toggle off X") must change state through the SAME underlying API.
    # When they diverge, at least one of them silently targets a similarly
    # worded but different feature — a wrong-target bug that executes without
    # error and so never reaches the repair loop on its own.

    _PAIR_POSITIVE_TOKENS = {
        "on", "enable", "enabled", "show", "shown", "visible", "true", "start",
    }
    _PAIR_NEGATIVE_TOKENS = {
        "off", "disable", "disabled", "hide", "hidden", "invisible", "false", "stop",
    }
    _PAIR_GENERIC_TOKENS = {
        "toggle", "turn", "switch", "set", "make", "the", "and", "for",
        "step", "with", "from", "into",
    }
    # Generic state-carrier mechanisms present in most templates; they are
    # never the distinguishing state-changing API of a step.
    _PAIR_GENERIC_API_CORES = {"parameter", "attribute", "name", "modified"}

    @classmethod
    def _pair_subject_and_polarity(cls, text: str):
        """(subject_tokens, polarity) for a step description; polarity is
        +1/-1 or 0 when absent/ambiguous."""
        tokens = {
            t for t in _re.findall(r"[a-z0-9]+", _text_or_empty(text).lower())
            if len(t) >= 2
        }
        positive = bool(tokens & cls._PAIR_POSITIVE_TOKENS)
        negative = bool(tokens & cls._PAIR_NEGATIVE_TOKENS)
        polarity = 0
        if positive != negative:
            polarity = 1 if positive else -1
        subject = tokens - cls._PAIR_POSITIVE_TOKENS - cls._PAIR_NEGATIVE_TOKENS
        subject -= cls._PAIR_GENERIC_TOKENS
        return subject, polarity

    @classmethod
    def _pair_state_api_cores(cls, code: str) -> Dict[str, str]:
        """Map normalized state-API core -> representative spelling.

        Cores come from Set*/set* calls, trailing-On/Off calls, and boolean
        property assignments — the shapes a state change takes in Slicer.
        """
        cores: Dict[str, str] = {}
        code = code or ""
        for match in _re.finditer(r"\.\s*([Ss]et[A-Za-z0-9_]+)\s*\(", code):
            name = match.group(1)
            cores.setdefault(name[3:].lower(), name)
        for match in _re.finditer(r"\.\s*([A-Za-z0-9_]+?)(?:On|Off)\s*\(\s*\)", code):
            name = match.group(1)
            cores.setdefault(name.lower(), name)
        for match in _re.finditer(
            r"\.\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:True|False|0|1)\b", code
        ):
            name = match.group(1)
            cores.setdefault(name.lower(), name)
        return {
            core: spelling for core, spelling in cores.items()
            if core not in cls._PAIR_GENERIC_API_CORES
        }

    def _validate_paired_step_mechanisms(
        self, templates: Dict[str, str], generators: List[Dict],
    ) -> Dict[str, List[str]]:
        """Blocking check: opposite-polarity step pairs over the same subject
        must share at least one primary state-changing API core."""
        result = {"errors": [], "warnings": []}
        candidates = []
        for gen in generators or []:
            tpl_name = gen.get("template_file")
            if not tpl_name or tpl_name not in templates:
                continue
            subject, polarity = self._pair_subject_and_polarity(gen.get("description"))
            if polarity == 0 or not subject:
                continue
            cores = self._pair_state_api_cores(templates.get(tpl_name, ""))
            candidates.append({
                "gen": gen,
                "template": tpl_name,
                "subject": subject,
                "polarity": polarity,
                "cores": cores,
            })

        for i, a in enumerate(candidates):
            for b in candidates[i + 1:]:
                if a["polarity"] == b["polarity"]:
                    continue
                union = a["subject"] | b["subject"]
                if not union:
                    continue
                jaccard = len(a["subject"] & b["subject"]) / len(union)
                if jaccard < 0.7:
                    continue
                # Cannot judge a side with no detectable state API.
                if not a["cores"] or not b["cores"]:
                    continue
                if set(a["cores"]) & set(b["cores"]):
                    continue
                apis_a = ", ".join(sorted(a["cores"].values())[:4])
                apis_b = ", ".join(sorted(b["cores"].values())[:4])
                for side, other in ((a, b), (b, a)):
                    result["errors"].append(
                        f"{side['template']}: PairedStepMechanismMismatch: this step and "
                        f"'{other['template']}' describe opposite states of the same "
                        f"control but use different state-changing APIs "
                        f"({apis_a} vs {apis_b}); re-ground both steps against the "
                        f"single evidenced mechanism for that control"
                    )
        return result

    def _operation_intents_for_generator(self, gen: Dict) -> List[str]:
        operation_model = gen.get("operation_model") or {}
        intents = list(operation_model.get("operation_intents") or [])
        if intents:
            return sorted(set(intents))
        return self._infer_step_operation_intents(gen)

    @staticmethod
    def _display_scope_categories(gen: Dict) -> List[str]:
        categories = []
        for so in gen.get("sub_operations", []) or []:
            if so.get("op_type") == "slicer_op" and so.get("slicer_op_category"):
                categories.append(_text_or_empty(so.get("slicer_op_category")))
        if gen.get("slicer_op_category"):
            categories.append(_text_or_empty(gen.get("slicer_op_category")))
        return sorted(set(c for c in categories if c))

    @staticmethod
    def _display_scope_text(gen: Dict) -> str:
        parts = [_text_or_empty(gen.get("description"))]
        for so in gen.get("sub_operations", []) or []:
            parts.append(_text_or_empty(so.get("description")))
            parts.extend(_text_list(so.get("slicer_api_keywords", [])))
            parts.append(_text_or_empty(so.get("node_class")))
            parts.append(_text_or_empty(so.get("slicer_op_category")))
        operation_model = gen.get("operation_model") or {}
        parts.extend(_text_list(operation_model.get("operation_intents", [])))
        return " ".join(parts).lower()

    @staticmethod
    def _display_scope_node_class(gen: Dict) -> str:
        for so in gen.get("sub_operations", []) or []:
            node_class = _text_or_empty(so.get("node_class"))
            if node_class:
                return node_class
        descriptor = gen.get("interaction_descriptor") or {}
        if isinstance(descriptor, dict):
            node_class = _text_or_empty(descriptor.get("node_class"))
            if node_class:
                return node_class
        return ""

    @staticmethod
    def _display_scope_targets_slice_view(code: str, gen: Dict) -> bool:
        text = AnalyzerValidationSemanticsMixin._display_scope_text(gen)
        code_text = (code or "").lower()
        return bool(
            _re.search(r"\b(red|green|yellow)\b", text)
            or "slice view" in text
            or "vtkmrmlslicenode" in text
            or _re.search(r"vtkmrmlslicenode(red|green|yellow)?", code_text)
            or _re.search(r"GetSingletonNode\s*\(\s*['\"](Red|Green|Yellow)['\"]", code or "")
        )

    @staticmethod
    def _code_enables_markups_slice_visibility(code: str) -> bool:
        return bool(
            _re.search(r"\b(SetVisibility2D|Visibility2DOn)\s*\(", code or "")
            or _re.search(r"\b(SetSliceProjection|SliceProjectionOn)\s*\(", code or "")
        )

    @staticmethod
    def _code_enables_model_slice_visibility(code: str) -> bool:
        return bool(_re.search(r"\b(SetVisibility2D|Visibility2DOn)\s*\(", code or ""))

    @staticmethod
    def _code_enables_segmentation_slice_visibility(code: str) -> bool:
        return bool(
            _re.search(
                r"\b(SetVisibility2D|Visibility2DOn|SetVisibility2DFill|"
                r"SetVisibility2DOutline|SetSegmentVisibility2D)",
                code or "",
            )
        )

    def _validate_display_view_scope_semantics(self, code: str, gen: Dict, intents: set) -> Dict:
        """Validate that display view filters also enable slice/2D visibility."""
        result = {"errors": [], "warnings": []}
        categories = set(self._display_scope_categories(gen))
        if not (
            "view_display_scope" in intents
            or categories & {"markups_display", "node_display"}
        ):
            return result
        if not self._display_scope_targets_slice_view(code, gen):
            return result
        # Only steps that affirmatively SHOW something in a slice view must
        # enable 2D visibility. Hide/invert/ambiguous intents are exempt —
        # this gate mirrors the generator-side display-scope prompt gate
        # (slicer_op_generator/core.py); both must stay in sync.
        state_intent = _infer_final_state_intent(self._display_scope_text(gen))
        if not (state_intent.get("mode") == "set" and state_intent.get("state") is True):
            return result

        text = self._display_scope_text(gen)
        node_class = self._display_scope_node_class(gen)
        node_class_l = node_class.lower()
        code_l = (code or "").lower()
        is_markups = (
            "markups_display" in categories
            or "vtkmrmlmarkups" in node_class_l
            or "markups" in text
            or "markups" in code_l
        )
        is_segmentation = "segmentation" in node_class_l or "segmentation" in text
        is_model = (
            "vtkmrmlmodel" in node_class_l
            or "model" in text
            or "modeldisplaynode" in code_l
        )

        if is_markups:
            if not self._code_enables_markups_slice_visibility(code):
                result["errors"].append(
                    "Markups display step targets a slice view but only restricts view IDs; "
                    "expected SetVisibility2D/Visibility2DOn or SetSliceProjection/"
                    "SliceProjectionOn so the markup is actually visible in slice views"
                )
        elif is_segmentation:
            if not self._code_enables_segmentation_slice_visibility(code):
                result["errors"].append(
                    "Segmentation display step targets a slice view but does not enable "
                    "2D fill/outline visibility"
                )
        elif is_model:
            if not self._code_enables_model_slice_visibility(code):
                result["errors"].append(
                    "Model display step targets a slice view but does not enable "
                    "2D visibility"
                )
        else:
            if "AddViewNodeID" in code or "SetViewNodeIDs" in code:
                result["warnings"].append(
                    "Display step targets a slice view; verify the display node class also "
                    "enables the required 2D/slice visibility API"
                )
        return result

    def _extension_function_effects(self, function_name: str) -> List[str]:
        if not function_name or not isinstance(self._workflow_metadata, dict):
            return []
        inventory = self._workflow_metadata.get("extension_callable_inventory", {}) or {}
        effects_by_name = inventory.get("module_function_effects", {}) or {}
        return list(effects_by_name.get(function_name, []) or [])

    @staticmethod
    def _function_name_suggests_layout_activation(function_name: str) -> bool:
        name_l = _text_or_empty(function_name).lower()
        return (
            "layout" in name_l
            and name_l.startswith(("set", "switch", "activate", "restore", "show"))
        )

    # A step that names a SPECIFIC 3D view ("3D View 1") must resolve the
    # view node by identity (name/singleton tag/view label from layout
    # evidence). Positional accessors like threeDWidget(0) depend on the
    # active layout and widget creation order — the canonical wrong-view bug.
    _NAMED_3D_VIEW_TEXT_RE = _re.compile(r"\b3-?d\s*view\s*\d+\b|\bview\s*\d+\b")
    _POSITIONAL_3D_ACCESS_RE = _re.compile(r"\bthreeDWidget\s*\(\s*\d+\s*\)")

    def _validate_named_view_resolution(self, code: str, gen: Dict) -> Dict:
        result = {"errors": [], "warnings": []}
        text = self._display_scope_text(gen)
        if not self._NAMED_3D_VIEW_TEXT_RE.search(text):
            return result
        match = self._POSITIONAL_3D_ACCESS_RE.search(code or "")
        if not match:
            return result
        result["errors"].append(
            "PositionalViewResolution: the step names a specific 3D view but "
            f"the template resolves a view positionally ({match.group(0)}), "
            "which depends on the active layout and widget creation order; "
            "resolve the named view NODE by its name, singleton tag, or view "
            "label from layout evidence (e.g. GetSingletonNode / "
            "GetFirstNodeByName) instead"
        )
        return result

    def _validate_slicer_operation_semantics(self, code: str, gen: Dict) -> Dict:
        """Validate generic Slicer UI-operation effects beyond API existence."""
        result = {"errors": [], "warnings": []}
        interaction_scope = self._validate_interaction_scope(code, gen)
        result["errors"].extend(interaction_scope["errors"])
        result["warnings"].extend(interaction_scope["warnings"])
        named_view = self._validate_named_view_resolution(code, gen)
        result["errors"].extend(named_view["errors"])
        result["warnings"].extend(named_view["warnings"])
        intents = set(self._operation_intents_for_generator(gen))
        if not intents:
            return result

        if "layout_activate" in intents:
            called_function = self._detect_extension_function_call(code)
            called_effects = set(self._extension_function_effects(called_function))
            code_activates_layout = bool(
                _re.search(r"\.\s*setLayout\s*\(", code)
                or _re.search(r"\blayoutManager\s*\([^)]*\)\s*\.\s*setLayout\s*\(", code)
                or "layout_activate" in called_effects
                or (
                    called_function
                    and not called_effects
                    and self._function_name_suggests_layout_activation(called_function)
                )
            )
            code_only_registers_layout = bool(
                "AddLayoutDescription" in code
                or "layout_register" in called_effects
                or (
                    called_function
                    and "layout" in called_function.lower()
                    and called_function.lower().startswith("add")
                    and "layout_activate" not in called_effects
                )
            )
            if not code_activates_layout:
                result["errors"].append(
                    "Layout activation step does not produce an evidence-backed active-layout change"
                )
            elif (
                code_only_registers_layout
                and "layout_activate" not in called_effects
                and not _re.search(r"\.\s*setLayout\s*\(", code)
            ):
                result["errors"].append(
                    "Layout activation step only registers a layout and does not activate it"
                )

        if "slice_intersection_visibility" in intents:
            called_function = self._detect_extension_function_call(code)
            called_effects = set(self._extension_function_effects(called_function))
            uses_app_logic = "SetIntersectingSlicesEnabled" in code
            uses_display_setter = "SetIntersectingSlicesVisibility" in code
            refreshes_slice_nodes = bool("Modified(" in code and "vtkMRMLSliceNode" in code)
            has_global_effect = uses_app_logic or "slice_intersection_global" in called_effects
            has_display_effect = (
                uses_display_setter
                or "slice_intersection_display_node" in called_effects
            )
            has_refresh_effect = refreshes_slice_nodes or "slice_view_refresh" in called_effects
            uses_crosshair_only = bool(
                ("vtkMRMLCrosshairNode" in code or "SetCrosshairMode" in code)
                and not has_global_effect
                and not has_display_effect
            )
            if uses_crosshair_only:
                result["errors"].append(
                    "Slice intersection visibility step changes only crosshair state, "
                    "which does not satisfy the requested slice-intersection behavior"
                )
            elif not has_global_effect and not (has_display_effect and has_refresh_effect):
                result["errors"].append(
                    "Slice intersection visibility step does not provide evidence-backed "
                    "intersection visibility behavior with any required view refresh"
                )

        display_scope_contract = self._validate_display_view_scope_semantics(code, gen, intents)
        result["errors"].extend(display_scope_contract["errors"])
        result["warnings"].extend(display_scope_contract["warnings"])

        return result

    def _module_switch_allowed_by_contract(self, gen: Dict, code: str = "") -> bool:
        operation_model = gen.get("operation_model") or {}
        if operation_model.get("allow_module_switch"):
            return True
        intents = set(_text_list(gen.get("operation_intents", [])))
        for so in gen.get("sub_operations", []) or []:
            intents.update(_text_list(so.get("operation_intents", [])))
            if so.get("operation_intent"):
                intents.add(so["operation_intent"])
        if "module_switch" in intents:
            return True
        # Precondition exception: a template that imports an extension module
        # is making a logic-method call, and any slicer.util.selectModule() in
        # it is for widget-lifecycle setup (so module.enter() has run), not
        # UI navigation. The original rule targets UI-navigation cookbooks
        # ("go to module X") which don't import the extension's code.
        if code and self._template_imports_extension_module(code):
            return True
        return False

    @staticmethod
    def _template_imports_extension_module(code: str) -> bool:
        """Return True if the template imports a non-standard (extension) module.

        Used to distinguish widget-lifecycle selectModule (allowed) from
        UI-navigation selectModule (blocked). Standard imports (slicer, vtk,
        qt, SlicerAIAgentLib, python stdlib) don't count — only imports of
        third-party / extension modules.
        """
        if not code:
            return False
        for m in _re.finditer(r'^\s*from\s+([\w.]+)\s+import\s+', code, _re.MULTILINE):
            top = m.group(1).split(".")[0]
            if AnalyzerValidationSemanticsMixin._is_extension_module_import(top):
                return True
        for m in _re.finditer(r'^\s*import\s+([\w.]+)', code, _re.MULTILINE):
            top = m.group(1).split(".")[0]
            if AnalyzerValidationSemanticsMixin._is_extension_module_import(top):
                return True
        return False

    @staticmethod
    def _strip_precondition_regions(code: str) -> str:
        """Remove emitted precondition blocks from code for operation-level checks.

        Preconditions (widget-lifecycle setup wrapped in `# precondition:begin` /
        `# precondition:end` marker comments) are not part of the template's
        Slicer API surface. Operation-level checks (e.g. code_has_slicer_api)
        should evaluate only the operation itself, not the emitted setup.
        """
        if not code or _PRECONDITION_BEGIN not in code:
            return code
        out = []
        in_prec = False
        for line in code.split("\n"):
            stripped = line.strip()
            if stripped == _PRECONDITION_BEGIN:
                in_prec = True
                continue
            if stripped == _PRECONDITION_END:
                in_prec = False
                continue
            if not in_prec:
                out.append(line)
        return "\n".join(out)

    @staticmethod
    def _extension_methods_called_by_template(code: str) -> List[str]:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return []
        methods = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                # "logic" is the extension logic instance; "_module_widget"
                # is the module widget instance (widget-receiver appliers).
                and func.value.id in ("logic", "_module_widget")
            ):
                methods.append(func.attr)
        return sorted(set(methods))

    @staticmethod
    def _template_sets_parameter(code: str, role: str) -> bool:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return False
        literal_sequences: Dict[str, set] = {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                continue
            if not isinstance(node.value, (ast.List, ast.Tuple)):
                continue
            values = set()
            for elt in node.value.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    values.add(elt.value)
            if values:
                literal_sequences[node.targets[0].id] = values

        loop_targets: Dict[str, set] = {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.For) or not isinstance(node.target, ast.Name):
                continue
            values = set()
            if isinstance(node.iter, ast.Name):
                values.update(literal_sequences.get(node.iter.id, set()))
            elif isinstance(node.iter, (ast.List, ast.Tuple)):
                for elt in node.iter.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        values.add(elt.value)
            if values:
                loop_targets[node.target.id] = values

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func_name = ExtensionCLIAnalyzer._get_call_name(node)
            if not func_name.endswith("SetParameter") or not node.args:
                continue
            arg0 = node.args[0]
            if isinstance(arg0, ast.Constant) and arg0.value == role:
                return True
            if isinstance(arg0, ast.Name) and role in loop_targets.get(arg0.id, set()):
                return True
        return False

    def _scalar_role_has_prior_producer(self, role: str, step_id: str = "") -> bool:
        if not isinstance(self._workflow_metadata, dict):
            return False
        audit = self._workflow_metadata.get("contract_audit") or {}
        state_graph = (
            audit.get("workflow_state_graph")
            if isinstance(audit, dict)
            else {}
        ) or self._workflow_metadata.get("workflow_state_graph") or {}
        producers = (
            state_graph.get("parameter_producers")
            or state_graph.get("producers")
            or {}
        )
        role_producers = producers.get(role, []) if isinstance(producers, dict) else []
        if not role_producers:
            return False
        if not step_id:
            return True
        step_order = {}
        steps = (
            self._workflow_metadata.get("workflow_steps")
            or self._workflow_metadata.get("steps")
            or []
        )
        for index, step in enumerate(steps if isinstance(steps, list) else []):
            if isinstance(step, dict) and step.get("step_id"):
                step_order[step["step_id"]] = index
        if not step_order and isinstance(state_graph.get("step_order"), dict):
            step_order = state_graph.get("step_order") or {}
        current_order = step_order.get(step_id)
        if current_order is None:
            return bool(role_producers)
        for producer in role_producers:
            producer_step = (
                producer.get("step_id", "")
                if isinstance(producer, dict)
                else str(producer)
            )
            producer_order = step_order.get(producer_step)
            if producer_order is not None and producer_order < current_order:
                return True
        return False

    def _validate_scalar_parameter_contract(
        self,
        code: str,
        step_id: str = "",
    ) -> Dict[str, List[str]]:
        """Ensure automated extension method calls have scalar parameter defaults."""
        result = {"errors": [], "warnings": []}
        if not isinstance(self._workflow_metadata, dict):
            return result
        methods = self._extension_methods_called_by_template(code)
        if not methods:
            return result

        bindings = self._workflow_metadata.get("parameter_bindings", {}) or {}
        defaults = self._workflow_metadata.get("parameter_defaults", {}) or {}
        dependencies = self._workflow_metadata.get("parameter_method_dependencies", {}) or {}
        method_effects = self._workflow_metadata.get("method_parameter_effects", {}) or {}
        choice_bound_roles = {
            binding.get("parameter_name")
            for binding in (self._workflow_metadata.get("choice_bindings", {}) or {}).values()
            if isinstance(binding, dict)
        }

        for method in methods:
            dep = dependencies.get(method, {}) or {}
            for role in dep.get("parameter_roles", []) or []:
                effects = method_effects.get(method, {}) or {}
                if role in (effects.get("writes", []) or []):
                    continue
                info = bindings.get(role, {}) or {}
                if info.get("node_class"):
                    continue
                value_types = set(info.get("value_types") or [])
                if not (value_types & {"float", "int", "bool"}):
                    continue
                if role in choice_bound_roles or self._template_sets_parameter(code, role):
                    continue
                if self._scalar_role_has_prior_producer(role, step_id=step_id):
                    continue
                if role in defaults:
                    default_info = defaults.get(role, {}) or {}
                    if default_info.get("confidence") == "low":
                        result["errors"].append(
                            f"Parameter '{role}' for logic.{method}() uses low-confidence "
                            f"{default_info.get('source', 'default')} default {default_info.get('value')!r}; "
                            "bind the parameter to a user/cookbook value, derive a source-backed default, "
                            "or raise a clear required-input error instead of silently using a fallback"
                        )
                    continue
                result["errors"].append(
                    f"logic.{method}() depends on scalar parameter '{role}' "
                    f"({', '.join(sorted(value_types))}) but no user binding, template assignment, "
                    "or source-derived default is available"
                )
        return result

    def _validate_node_class_contract(self, code: str) -> Dict[str, List[str]]:
        """Detect fallback code that resolves a parameter role with the wrong MRML class."""
        result = {"errors": []}
        if not isinstance(self._workflow_metadata, dict):
            return result
        bindings = self._workflow_metadata.get("parameter_bindings", {}) or {}
        for role, info in bindings.items():
            expected = info.get("node_class", "")
            if not expected or "vtkMRMLMarkups" not in expected or role not in code:
                continue
            classes = set(_re.findall(r"['\"](vtkMRMLMarkups[A-Za-z0-9_]+Node)['\"]", code))
            mismatches = sorted(cls for cls in classes if cls != expected)
            if mismatches and expected not in classes:
                result["errors"].append(
                    f"Template references parameter role '{role}' with node class "
                    f"{', '.join(mismatches)} but metadata expects {expected}"
                )
        return result

    def _validate_node_requirement_contract(self, code: str) -> Dict[str, List[str]]:
        """Validate generated pre-call node-reference requirement metadata."""
        result = {"errors": [], "warnings": []}
        if not isinstance(self._workflow_metadata, dict):
            return result
        dependencies = self._workflow_metadata.get("parameter_method_dependencies", {}) or {}
        defaults = self._workflow_metadata.get("parameter_defaults", {}) or {}
        valid_kinds = {"required", "conditional", "produced_by_method", "optional_unknown"}
        for method in self._extension_methods_called_by_template(code):
            requirements = (dependencies.get(method, {}) or {}).get("node_requirements", {}) or {}
            for role, requirement in requirements.items():
                kind = requirement.get("requirement", "optional_unknown")
                conditions = requirement.get("conditions") or []
                if kind not in valid_kinds:
                    result["errors"].append(
                        f"Node reference '{role}' for logic.{method}() has invalid requirement kind '{kind}'"
                    )
                    continue
                if kind == "conditional" and not conditions:
                    result["warnings"].append(
                        f"Node reference '{role}' for logic.{method}() is conditional but has no "
                        "runtime-evaluable condition; missing-reference validation will be skipped"
                    )
                for condition in conditions:
                    parameter = condition.get("parameter", "")
                    if not parameter:
                        result["warnings"].append(
                            f"Node reference '{role}' for logic.{method}() has a condition without a parameter"
                        )
                    elif parameter not in defaults:
                        result["warnings"].append(
                            f"Conditional node reference '{role}' for logic.{method}() depends on "
                            f"parameter '{parameter}' without a source-derived default"
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
    def _template_creates_any_node(code: str) -> bool:
        """Return True when code creates any MRML node via CreateNodeByClass/AddNewNodeByClass."""
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
            if func_name in ("CreateNodeByClass", "AddNewNodeByClass"):
                return True
        return False

    @staticmethod
    def _template_enters_place_mode(code: str) -> bool:
        """Return True when code calls SwitchToPersistentPlaceMode / StartPlaceMode / SetCurrentInteractionMode."""
        return any(
            call in code
            for call in (
                "SwitchToPersistentPlaceMode",
                "StartPlaceMode",
                "SetCurrentInteractionMode",
            )
        )

    @staticmethod
    def _template_references_markups_class(code: str) -> bool:
        """Return True when code references any vtkMRMLMarkups*Node class string."""
        return bool(_re.search(r"['\"]vtkMRMLMarkups[A-Za-z0-9_]*Node['\"]", code))

    def _validate_interaction_kind_contract(self, code: str, gen: Dict) -> Dict[str, List[str]]:
        """Revision D: catch the original bug class (view_adjustment descriptor
        but template creates a Markups node and enters placement mode) at
        generation time, not at every runtime step.

        Rules (errors block manifest validation):
          - interaction_kind == "view_adjustment" AND template creates any
            MRML node → misrouted dispatch.
          - interaction_kind == "view_adjustment" AND template references a
            vtkMRMLMarkups*Node string → misrouted dispatch.
          - creates_node == False (explicit) AND template creates any node
            → descriptor/template mismatch.
          - requires_place_mode == False (explicit) AND template enters
            placement mode → descriptor/template mismatch.
        """
        result: Dict[str, List[str]] = {"errors": [], "warnings": []}
        if not isinstance(gen, dict):
            return result
        sub_ops = gen.get("sub_operations") or []
        # Find the user_interaction sub-op driving this template, if any.
        interaction_so = None
        for so in sub_ops:
            if so.get("op_type") == "user_interaction":
                interaction_so = so
                break
        # If no explicit user_interaction sub-op, fall back to top-level
        # generator fields (some generators carry interaction metadata there).
        interaction_kind = (
            (interaction_so or {}).get("interaction_kind")
            or gen.get("interaction_kind")
            or ""
        )
        creates_node = (
            (interaction_so or {}).get("creates_node")
            if interaction_so is not None
            else gen.get("creates_node")
        )
        requires_place_mode = (
            (interaction_so or {}).get("requires_place_mode")
            if interaction_so is not None
            else gen.get("requires_place_mode")
        )
        if not interaction_kind and creates_node is None and requires_place_mode is None:
            return result  # not an interaction template

        tpl_label = gen.get("template_file") or gen.get("pre_template_file") or gen.get("post_template_file") or "<unknown>"
        creates_any = self._template_creates_any_node(code)
        enters_place = self._template_enters_place_mode(code)
        refs_markups = self._template_references_markups_class(code)

        if interaction_kind == "view_adjustment":
            if creates_any:
                result["errors"].append(
                    f"view_adjustment template '{tpl_label}' creates an MRML node; "
                    "dispatch misrouted a viewport/handle-drag interaction into node creation"
                )
            if refs_markups:
                result["errors"].append(
                    f"view_adjustment template '{tpl_label}' references a vtkMRMLMarkups*Node; "
                    "dispatch misrouted a viewport/handle-drag interaction into Markups placement"
                )
            if enters_place:
                result["errors"].append(
                    f"view_adjustment template '{tpl_label}' enters placement mode; "
                    "this hijacks the mouse for viewport/handle-drag interactions"
                )
        # creates_node/requires_place_mode checks fire only when the descriptor
        # explicitly said False — missing values (None) are advisory, not contracts.
        if creates_node is False and creates_any:
            result["errors"].append(
                f"Template '{tpl_label}' creates a node but the step descriptor "
                "declared creates_node=false"
            )
        if requires_place_mode is False and enters_place:
            result["errors"].append(
                f"Template '{tpl_label}' enters placement mode but the step descriptor "
                "declared requires_place_mode=false"
            )
        return result

    def _validate_module_enter_precondition(self, code: str, gen: Dict) -> Dict[str, List[str]]:
        """Catch templates that call extension logic methods without ensuring
        the module is active. Extension methods assume module.enter() has run
        (parameter node init, observers, UI bindings); without
        slicer.util.selectModule(), the widget lifecycle never fires and the
        method silently misbehaves (missing UI, missing observers, etc.).

        Detection: the template imports an extension module (anything outside
        the standard Slicer/python import set) AND does not contain a
        slicer.util.selectModule() call. The check is intentionally general —
        it does not encode any specific module name.
        """
        result: Dict[str, List[str]] = {"errors": [], "warnings": []}
        if not isinstance(gen, dict) or not isinstance(code, str) or not code:
            return result

        extension_modules = set()
        imports_logic_class = False
        logic_class_name = ""
        if isinstance(self._workflow_metadata, dict):
            logic_class_name = _text_or_empty(self._workflow_metadata.get("logic_class_name", ""))
        try:
            tree = ast.parse(code)
        except SyntaxError:
            tree = None
        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    top = (node.module or "").split(".")[0]
                    if self._is_extension_module_import(top):
                        extension_modules.add(top)
                        for alias in node.names:
                            imported_name = alias.name
                            if (
                                imported_name == logic_class_name
                                or imported_name.endswith("Logic")
                            ):
                                imports_logic_class = True
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        top = alias.name.split(".")[0]
                        if self._is_extension_module_import(top):
                            extension_modules.add(top)
        else:
            for m in _re.finditer(r'^\s*from\s+([\w.]+)\s+import\s+', code, _re.MULTILINE):
                top = m.group(1).split(".")[0]
                if self._is_extension_module_import(top):
                    extension_modules.add(top)
            for m in _re.finditer(r'^\s*import\s+([\w.]+)', code, _re.MULTILINE):
                top = m.group(1).split(".")[0]
                if self._is_extension_module_import(top):
                    extension_modules.add(top)

        if not extension_modules:
            return result  # no extension import — not a logic-calling template
        if not imports_logic_class and not self._extension_methods_called_by_template(code):
            return result

        if "slicer.util.selectModule(" in code:
            return result  # precondition present

        tpl_label = (
            gen.get("template_file")
            or gen.get("pre_template_file")
            or gen.get("post_template_file")
            or "<unknown>"
        )
        imported = ", ".join(sorted(extension_modules))
        result["errors"].append(
            f"Template '{tpl_label}' imports extension module(s) {imported} "
            "but does not call slicer.util.selectModule() to ensure the module is active; "
            "extension logic methods require module.enter() to have run (parameter node init, "
            "observers, UI bindings)"
        )
        return result

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
                elif isinstance(node.target, (ast.Tuple, ast.List)):
                    for elt in node.target.elts:
                        if isinstance(elt, ast.Name):
                            defined.add(elt.id)
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

        # Generated templates execute at MODULE level in __main__ (not inside a
        # class), so a module-level `self`/`cls` is always a bug — usually code
        # copied verbatim from the extension's widget/logic source. Collect the
        # `self`/`cls` Load references that sit outside any def/lambda so we can
        # flag them; references nested inside a function definition stay valid.
        module_self_cls = set()

        def _scan_self_cls(node, in_func):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                    _scan_self_cls(child, True)
                    continue
                if (
                    isinstance(child, ast.Name)
                    and isinstance(child.ctx, ast.Load)
                    and child.id in ("self", "cls")
                    and not in_func
                ):
                    module_self_cls.add(id(child))
                _scan_self_cls(child, in_func)

        _scan_self_cls(tree, False)

        # Find undefined variables (names used but never defined)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id in ("self", "cls"):
                    if id(node) in module_self_cls:
                        result["errors"].append(
                            f"Undefined variable: '{node.id}' — generated templates run at "
                            "module level; access the parameter node via 'paramNode' / "
                            "'logic.getParameterNode()', not 'self'/'cls'"
                        )
                    continue
                if node.id not in defined and not node.id.startswith("_"):
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
            "vtkMRMLCrosshair", "vtkMRMLScriptedModule",
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
        """Fill remaining template placeholders outside Python strings."""
        string_ranges = []
        for match in _re.finditer(
            r'(?:[fFrRbBuU]{0,2})("""|\'\'\'|"|\')(.*?)\1',
            code,
            _re.DOTALL,
        ):
            string_ranges.append((match.start(), match.end()))

        def _string_end_at(pos: int) -> Optional[int]:
            for start, end in string_ranges:
                if start <= pos < end:
                    return end
            return None

        def _sample_value(name: str) -> str:
            lower = name.lower()
            if "name" in lower:
                return '"SampleNode"'
            if "radius" in lower or "size" in lower or "distance" in lower:
                return "1.5"
            if "path" in lower:
                return '"/tmp/sample"'
            # Boolean-like placeholders — emit True so the assembled code parses
            # even when the template expects a bool/checked value.
            if any(k in lower for k in (
                "checked", "enabled", "visible", "active", "flag",
                "show_", "_show", "use_", "_use", "is_", "_is",
            )):
                return "True"
            # Integer counts/indices
            if any(k in lower for k in ("count", "number", "index", "num_")):
                return "1"
            # Choice/selection values
            if any(k in lower for k in ("choice", "selection", "option", "value", "selected")):
                return '"sample"'
            # MRML node IDs
            if lower.endswith("_id") or lower.endswith("id") and "node" in lower:
                return '"vtkMRMLSampleNode1"'
            return '""'

        result = []
        i = 0
        n = len(code)
        while i < n:
            string_end = _string_end_at(i)
            if string_end is not None:
                result.append(code[i:string_end])
                i = string_end
                continue

            if code.startswith("{{", i) or code.startswith("}}", i):
                result.append(code[i:i + 2])
                i += 2
                continue

            if code[i] != "{":
                result.append(code[i])
                i += 1
                continue

            depth = 0
            j = i
            found = False
            while j < n:
                if code[j] == "{":
                    depth += 1
                elif code[j] == "}":
                    depth -= 1
                    if depth == 0:
                        found = True
                        break
                j += 1

            if not found:
                result.append(code[i])
                i += 1
                continue

            inner = code[i + 1:j]
            colon_pos = inner.find(":")
            if colon_pos >= 0 and inner[:colon_pos].strip().isidentifier():
                name = inner[:colon_pos].strip()
                default = inner[colon_pos + 1:]
                if default.startswith(" "):
                    default = default[1:]
                result.append(default)
            elif inner.strip().isidentifier():
                result.append(_sample_value(inner.strip()))
            else:
                result.append(code[i:j + 1])
            i = j + 1

        return "".join(result)

    # ================================================================
