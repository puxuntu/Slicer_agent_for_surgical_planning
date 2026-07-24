from .common import *


class AnalyzerCookbookMappingMixin:
    def _find_cookbook(self, extension_name: str) -> Optional[str]:
        """Search for a cookbook .md file for the given extension.

        Looks in Resources/extensions_cookbook/ for {name}.md or
        Slicer{name}.md.

        Returns the path if found, else None.
        """
        module_dir = _PROJECT_ROOT
        cookbook_dir = os.path.join(module_dir, "Resources", "extensions_cookbook")
        candidates = [
            os.path.join(cookbook_dir, f"{extension_name}.md"),
            os.path.join(cookbook_dir, f"Slicer{extension_name}.md"),
        ]
        for path in candidates:
            if os.path.isfile(path):
                return path
        return None

    # Deprecated compatibility field. Active semantic mapping is performed by
    # the validated Stage 4 LLM decomposition.
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
        # which prevents a short UI noun such as "plane" from matching an
        # unrelated long compound implementation-method name
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
        logic = scan_result.get("logic_class") or {}
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

        Each cookbook step becomes one atomic workflow operation. The
        user-authored cookbook annotation is the source of truth for
        operation_type. step_type is kept as a temporary compatibility alias.
        """
        steps = []
        for stage in stage_map.get("stages", []):
            cb_step = stage.get("cookbook_step")
            if not cb_step:
                continue

            step_id = f"cb_step_{cb_step.step_number}"
            sub_ops = stage.get("sub_operations", [])
            op_type = (
                stage.get("operation_type")
                or stage.get("op_type")
                or getattr(cb_step, "operation_type", "")
                or "extension_op"
            )
            if op_type not in CANONICAL_OPERATION_TYPES:
                raise RuntimeError(
                    f"{step_id}: unsupported operation type '{op_type}'. "
                    f"Valid values: {', '.join(sorted(CANONICAL_OPERATION_TYPES))}"
                )
            is_optional = stage.get("is_optional", False)

            # Extract interaction info if present
            interaction_info = {}
            for so in sub_ops:
                if so["op_type"] == "user_interaction":
                    node_cls = so.get("node_class")
                    interaction_info = {
                        "interaction_type": _derive_interaction_type(node_cls),
                        "interaction_kind": so.get("interaction_kind") or "none",
                        "node_class": node_cls or "",
                        "creates_node": bool(so.get("creates_node", False)),
                        "requires_place_mode": bool(so.get("requires_place_mode", False)),
                        "setup_dependencies": list(so.get("setup_dependencies") or []),
                        "placement_instructions": so.get("placement_instructions", ""),
                        "min_control_points": so.get("min_control_points", 0),
                    }
                    # A module_tool_interaction carries the module whose active tool
                    # consumes the clicks, so the pre-template can re-bind that tool,
                    # and which tool it is, so it can re-arm one that was released.
                    if so.get("module_context"):
                        interaction_info["module_context"] = so.get("module_context")
                    if so.get("module_tool_context"):
                        interaction_info["module_tool_context"] = so.get("module_tool_context")
                    break

            # Extract user_choice info if present (branch_op carries the same
            # Yes/No choice_info as a user_choice decision). A step may carry
            # SEVERAL choice sub-ops (one cookbook sentence per selector, e.g. four
            # combos on one wizard page): choice_info stays the FIRST for every
            # single-choice consumer, and choice_info_list carries them ALL so the
            # runtime can render one form with every item.
            choice_info = {}
            choice_info_list = []
            # A step may declare that its DEFAULT is whatever the user chose at an
            # earlier step ("The default threshold is the same as in Step 5"), so
            # the second pass through a repeated selector starts from the value
            # already tuned rather than from the widget's own factory default.
            # Backward references only — a later step cannot seed an earlier one.
            default_from_step = ""
            _ref = _re.search(
                r"\b(?:same|default|initial|unchanged)\b[^.]*?\bstep\s+(\d+)\b",
                _text_or_empty(cb_step.description), _re.IGNORECASE,
            )
            if _ref:
                _ref_num = int(_ref.group(1))
                if _ref_num < cb_step.step_number:
                    default_from_step = f"cb_step_{_ref_num}"
            for so in sub_ops:
                if so["op_type"] in ("user_choice", "branch_op"):
                    item = {
                        "question": so.get("question", cb_step.description),
                        "choices": so.get("choices", []),
                        "parameter_name": so.get("parameter_name", f"choice_step_{cb_step.step_number}"),
                        "default_value": so.get("default_value"),
                    }
                    if default_from_step:
                        item["default_from_step"] = default_from_step
                    if so.get("live_items"):
                        item["live_items"] = True
                    if so.get("wizard_combo"):
                        # The source combo this item drives (page class + attr) --
                        # lets the runtime enumerate a dynamic combo's LIVE items
                        # and mirror the pick back onto the extension's own widget.
                        item["wizard_combo"] = so.get("wizard_combo")
                    if not choice_info:
                        choice_info = item
                    choice_info_list.append(item)

            # Extract method name for template generation
            method_name = None
            function_name = None
            for so in sub_ops:
                if so["op_type"] == "extension_op" and so.get("extension_method_hint"):
                    method_name = so["extension_method_hint"]
                    break
                if so["op_type"] == "extension_op" and so.get("extension_function_hint"):
                    function_name = so["extension_function_hint"]

            step = {
                "step_id": step_id,
                "operation_type": op_type,
                "step_type": op_type,
                "op_type": op_type,
                "description": cb_step.description,
                "depends_on": stage.get("depends_on", []),
                "sub_operations": sub_ops,
            }
            semantic_intents = sorted({
                intent
                for so in sub_ops
                for intent in (so.get("operation_intents") or [])
                if intent
            })
            semantic_node_roles = [
                role
                for so in sub_ops
                for role in (so.get("node_roles") or [])
                if isinstance(role, dict)
            ]
            if semantic_intents:
                step["operation_intents"] = semantic_intents
            if semantic_node_roles:
                step["node_roles"] = semantic_node_roles
            if method_name:
                step["method_name"] = method_name
            if function_name:
                step["extension_function_name"] = function_name
            if interaction_info:
                step.update(interaction_info)
            if choice_info:
                step["choice_info"] = choice_info
            if len(choice_info_list) > 1:
                step["choice_info_list"] = choice_info_list
            if is_optional:
                step["is_optional"] = True

            steps.append(step)

        return {
            "steps": steps,
            "step_count": len(steps),
            "source": "cookbook",
            "repeat_blocks": [
                dict(block) for block in stage_map.get("repeat_blocks", []) or []
            ],
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
        time; the runtime agent discovers scene nodes. If cookbook parsing
        produced a finite UI option set, do not infer a scene-node binding
        from incidental domain words.
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
        if normalized <= boolean_options or compact <= boolean_options:
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
