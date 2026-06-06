from .common import *


class AnalyzerStage4DecompositionMixin:
    def _collect_step_evidence(
        self, step_description: str, method_names: List[str], extension_name: str = ""
    ) -> Dict[str, Any]:
        """Collect deterministic classification evidence for one cookbook step."""
        desc = _text_or_empty(step_description)
        desc_lower = desc.lower()
        evidence = {
            "logic_method_candidates": [],
            "widget_candidates": [],
            "ui_control_candidates": [],
            "slicer_core_candidates": [],
            "interaction_candidates": [],
            "choice_candidates": [],
        }

        matched_method = self._match_description_to_method(desc_lower, method_names)
        if matched_method:
            evidence["logic_method_candidates"].append({
                "method": matched_method,
                "reason": "method name/purpose token overlap",
            })

        for conn in getattr(self, "_widget_connections", []) or []:
            btn_name = _text_or_empty(conn.get("button_widget_name"))
            btn_text = btn_name.lower().replace("_", " ").replace(".", " ")
            btn_words = [w for w in btn_text.split() if len(w) > 3]
            if not btn_words:
                continue
            hits = [w for w in btn_words if w in desc_lower]
            if len(hits) >= 2 or (len(btn_words) == 1 and hits):
                evidence["widget_candidates"].append({
                    "button_widget_name": btn_name,
                    "logic_methods": conn.get("logic_methods", []),
                    "matched_words": hits,
                })

        choice_patterns = {
            "left/right": ("left" in desc_lower and "right" in desc_lower),
            "which side": "which side" in desc_lower,
            "which type": "which type" in desc_lower or "mandibulectomy type" in desc_lower,
            "select scene node": any(
                p in desc_lower for p in (
                    "select the", "choose the", "current scalar volume",
                    "select mandibular segmentation", "select fibula segmentation",
                )
            ),
            "number requested": any(p in desc_lower for p in ("how many", "number of")),
        }
        for name, present in choice_patterns.items():
            if present:
                evidence["choice_candidates"].append(name)

        interaction_patterns = [
            ("markup_placement", "curve", "vtkMRMLMarkupsCurveNode", ("draw", "curve")),
            ("markup_placement", "plane", "vtkMRMLMarkupsPlaneNode", ("plane", "place")),
            ("markup_placement", "line", "vtkMRMLMarkupsLineNode", ("line", "draw")),
            ("view_adjustment", "generic", "vtkMRMLCrosshairNode", ("crosshair", "slice intersection", "drag")),
        ]
        for kind, interaction_type, node_class, words in interaction_patterns:
            if any(w in desc_lower for w in words) and any(
                v in desc_lower for v in ("manual", "manually", "draw", "drag", "click", "place", "position", "adjust")
            ):
                evidence["interaction_candidates"].append({
                    "interaction_kind": kind,
                    "interaction_type": interaction_type,
                    "node_class": node_class,
                    "matched_terms": [w for w in words if w in desc_lower],
                })

        slicer_concepts = [
            ("layout_slice_view", ("layout", "conventional", "slice visibility", "red view", "fov", "spacing")),
            ("markups_display", ("display panel", "advanced panel", "view 1", "markups")),
            ("module_switching", ("switch to", "open module", "open the markups module", "select module", "activate module")),
            ("crosshair", ("crosshair", "slice intersection", "enable interaction")),
            ("subject_hierarchy", ("subject hierarchy", "folder")),
            ("node_display", ("display node", "visibility", "view node")),
        ]
        for category, terms in slicer_concepts:
            matched = [t for t in terms if t in desc_lower]
            if matched:
                evidence["slicer_core_candidates"].append({
                    "category": category,
                    "matched_terms": matched,
                })

        extension_tokens = []
        if extension_name:
            extension_tokens.append(extension_name.lower())
            parts = _re.sub(r'([a-z])([A-Z])', r'\1 \2', extension_name).split()
            acronym = "".join(p[0].lower() for p in parts if p)
            if len(acronym) >= 2:
                extension_tokens.append(acronym)
        for token in extension_tokens:
            if token and token in desc_lower:
                evidence["ui_control_candidates"].append({
                    "control": token,
                    "reason": "extension-specific name/acronym appears in step",
                })

        return evidence

    @staticmethod
    def _evidence_has(evidence: Dict[str, Any], key: str) -> bool:
        value = evidence.get(key, [])
        return isinstance(value, list) and bool(value)

    def _infer_interaction_kind_from_evidence(self, evidence: Dict[str, Any], node_class: str = "") -> str:
        for item in evidence.get("interaction_candidates", []) or []:
            kind = item.get("interaction_kind")
            if kind:
                return kind
        if self._is_markup_node_class(node_class):
            return "markup_placement"
        if node_class:
            return "view_adjustment"
        return "none"

    def _infer_slicer_op_category(self, text: str, evidence: Optional[Dict[str, Any]] = None) -> Optional[str]:
        desc = _text_or_empty(text).lower()
        if evidence:
            cats = evidence.get("slicer_core_candidates", []) or []
            if self._is_ui_location_context_text(desc) and not self._is_explicit_module_switch_text(desc):
                for cat in cats:
                    if isinstance(cat, dict) and cat.get("category") == "markups_display":
                        return "markups_display"
            if cats and isinstance(cats[0], dict) and cats[0].get("category"):
                return cats[0]["category"]
        if any(t in desc for t in ("layout", "red view", "slice visibility", "fov", "spacing")):
            return "layout_slice_view"
        if "crosshair" in desc or "slice intersection" in desc:
            return "crosshair"
        if self._is_explicit_module_switch_text(desc):
            return "module_switching"
        if "display panel" in desc or "advanced panel" in desc or (
            "markups module" in desc and any(t in desc for t in ("display", "view", "advanced", "configure", "set", "show"))
        ):
            return "markups_display"
        if "subject hierarchy" in desc or "folder" in desc:
            return "subject_hierarchy"
        if "display" in desc or "visibility" in desc:
            return "node_display"
        return None

    @staticmethod
    def _is_explicit_module_switch_text(text: str) -> bool:
        """Return true only when switching modules is the requested action."""
        desc = _text_or_empty(text).lower()
        if not desc or "module" not in desc:
            return False
        explicit_patterns = (
            r"\b(switch|change|go|navigate|open|select|activate|enter)\s+(?:to\s+|the\s+)?[a-z0-9 _-]*\bmodule\b",
            r"\bmodule\s+selector\b",
            r"\bselectmodule\b",
        )
        return any(_re.search(pattern, desc) for pattern in explicit_patterns)

    @staticmethod
    def _is_ui_location_context_text(text: str) -> bool:
        """Return true when a module/panel phrase describes UI location context."""
        desc = _text_or_empty(text).lower()
        if not desc:
            return False
        has_location = bool(_re.search(r"\b(in|under|inside|from)\s+(?:the\s+)?[a-z0-9 _'-]*\b(module|panel|tab|section)\b", desc))
        has_setting_action = any(
            term in desc
            for term in (
                "configure", "set ", "show ", "display", "view", "advanced",
                "turn on", "turn off", "enable", "disable", "select "
            )
        )
        return has_location and has_setting_action

    def _stage4_cookbook_decomposition(
        self, cookbook_def, logic_analysis: Dict
    ) -> Dict:
        """
        Use LLM to decompose each cookbook step into sub-operations.

        Each step is classified into one or more of:
        - extension_op: Calls a method on the extension's Logic class.
        - slicer_op: Uses Slicer core API (layout changes, view toggles, etc.).
        - user_interaction: Requires the user to draw/click in the 3D view.
        - user_choice: A chat-based decision point.

        Falls back to keyword heuristics (_cookbook_build_stage_map) on LLM failure.
        """
        self.on_progress(
            4, "Cookbook Stage Map",
            "Decomposing cookbook steps via LLM..."
        )

        # Build cookbook steps text
        steps_text = "\n".join(
            f"Step {s.step_number}: {s.description}"
            for s in cookbook_def.steps
        )

        # Build method catalog from logic analysis
        methods = logic_analysis.get("methods", [])
        method_catalog = []
        for m in methods:
            mname = m.get("name", "")
            params = [
                f"{p.get('name', '')}: {p.get('type', '?')}"
                for p in m.get("parameters", [])
                if p.get("name") != "self"
            ]
            state_reads = m.get("state_reads", [])
            state_writes = m.get("state_writes", [])
            method_catalog.append({
                "name": mname,
                "purpose": m.get("purpose", ""),
                "parameters": params,
                "state_reads": state_reads,
                "state_writes": state_writes,
                "calls_addnode": m.get("calls_addnode", False),
                "adds_output_to_scene": m.get("adds_output_to_scene", False),
            })

        method_names = [m["name"] for m in methods]
        evidence_by_step = {
            s.step_number: self._collect_step_evidence(
                s.description, method_names, cookbook_def.extension_name
            )
            for s in cookbook_def.steps
        }

        # Build cookbook method hints section (AST-verified, not subject to truncation)
        cookbook_method_hints = logic_analysis.get("_cookbook_method_hints", [])
        if cookbook_method_hints:
            _cookbook_hints_section = (
                "\n        ## Cookbook Method Hints (AST-verified)\n"
                "        These methods were identified by matching cookbook step descriptions\n"
                "        against the full AST method list (not subject to truncation).\n"
                "        If a step's description matches one of these, classify as extension_op\n"
                "        with the hinted method:\n"
                f"        {json.dumps(cookbook_method_hints, indent=2)}\n"
            )
        else:
            _cookbook_hints_section = ""

        prompt = textwrap.dedent(f"""\
        You are analyzing a 3D Slicer extension's cookbook workflow and must decompose
        each step into atomic sub-operations.

        ## Cookbook Steps
        {steps_text}

        ## Available Logic Methods
        {json.dumps(method_catalog, indent=2)}
{_cookbook_hints_section}

        ## Deterministic Evidence Candidates
        These candidates were extracted from the extension source, UI/widget
        connections, and known Slicer-core concepts before this LLM call.
        Prefer high-confidence evidence over guessing. If no extension evidence
        or Slicer-core evidence supports an operation, use `unknown_op` instead
        of guessing.
        {json.dumps(evidence_by_step, indent=2)}

        ## Task
        For EACH cookbook step, decompose it into one or more sub-operations.
        Each sub-operation must have one of these types:

        1. **extension_op** — The operation calls a method on THIS extension's own
           Logic class. The code to generate it comes directly from the extension's
           source code — NO knowledge-base search is needed.
           Specify `extension_method_hint` matching one of:
           {json.dumps(method_names[:40])}
           Examples: calling addMandibularCurve(), generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible(),
           or any other method defined in the extension's Logic/Widget class.

        2. **slicer_op** — The operation uses Slicer CORE APIs that are NOT part of
           this extension. Code generation requires searching the Slicer knowledge base
           for the correct API calls (layout changes, view toggles, explicit module switching,
           node selection from Slicer's core modules).
           Specify `slicer_api_keywords` (e.g., ["layout", "red view", "set layout"]).
           Examples: slicer.app.layoutManager().setLayout(),
           slicer.util.getNode(), explicitly switching to a target module,
           toggling slice visibility.
           IMPORTANT: Checkbox ticks, dropdown selections, or button clicks in THIS
           extension's own UI panel are NOT slicer_op — they are either extension_op
           (if a Logic method exists) or user_choice (if the agent cannot determine
           the value, e.g. left vs. right).

        3. **user_interaction** — The user must physically interact with the 3D
           visualization window — drawing curves, positioning planes, placing
           fiducials, dragging objects in the viewport.
           Specify `interaction_type` (one of: "curve", "plane", "line", "fiducial"),
           `node_class` (e.g., "vtkMRMLMarkupsCurveNode"), and
           `placement_instructions` (what to tell the user to do).
           Examples: "Draw a curve along the mandible in the Red slice view",
           "Position the cutting plane by dragging in 3D view".

        4. **user_choice** — The agent CANNOT determine the answer on its own and
           must ask the user via the chat box. This applies whenever a parameter
           value depends on patient-specific or case-specific context that is not
           available in the scene.
           Specify `question` (the question to ask), `choices` (list of
           {{"label": "...", "value": "..."}} objects), `parameter_name`
           (snake_case identifier for the choice), and `default_value` (optional).
           Examples:
           - "Tick Right side leg checkbox" → user_choice (left/right depends on patient)
           - "Select mandibulectomy type" → user_choice (clinical decision)
           - "Choose segmentation" → user_choice if multiple options exist and the
             agent cannot determine the correct one from context.
           Anti-patterns (NOT user_choice):
           - If the agent CAN determine the value programmatically from the scene,
             it is extension_op or slicer_op, not user_choice.
           - A step like "click the Create Models button" is extension_op (there is
             a Logic method) or slicer_op (Slicer core API), NOT user_choice.

        5. **unknown_op** — The operation is required by the cookbook but cannot
           be proven as extension_op or slicer_op from the evidence. Do NOT use
           slicer_op as a catch-all fallback.

        ## Output Format
        Return a JSON object with this structure:
        {{
          "steps": [
            {{
              "step_number": 1,
              "sub_operations": [
                {{
                  "op_type": "extension_op" | "slicer_op" | "user_interaction" | "user_choice" | "unknown_op",
                  "description": "what this sub-operation does",
                  "extension_method_hint": "methodName" or null,
                  "slicer_api_keywords": ["keyword1"] or [],
                  "interaction_type": "curve" | "plane" | "line" | "fiducial" or null,
                  "node_class": "vtkMRML..." or null,
                  "placement_instructions": "..." or null,
                  "min_control_points": 0,
                  "evidence_type": "logic_method" | "widget_connection" | "ui_control" | "parameter_node" | "slicer_core" | "viewport_action" | "user_context" | "unknown",
                  "evidence_id": "method/widget/concept id" or null,
                  "confidence": "high" | "medium" | "low",
                  "interaction_kind": "markup_placement" | "view_adjustment" | "none",
                  "slicer_op_category": "layout_slice_view" | "module_switching" | "markups_display" | "crosshair" | "subject_hierarchy" | "node_display" | "scene_node_lookup" | "cli_module" | "generic_slicer_api" or null,
                  "question": "..." or null,
                  "choices": [{{"label": "...", "value": "..."}}] or [],
                  "parameter_name": "..." or null,
                  "default_value": "..." or null,
                  "is_optional": false
                }}
              ]
            }}
          ]
        }}

        ## Classification Rules (CRITICAL — read carefully)
        - A single cookbook step may have MULTIPLE sub-operations (e.g., setup + user interaction).
        - Every step must have at least one sub-operation.
        - **Ask yourself for each step**: "Can the agent determine ALL parameter values
          programmatically from the scene, or does it need information only the user knows?"
          If it needs user-only information → user_choice.
        - **Ask yourself**: "Does the code for this step come from THIS extension's source,
          or from Slicer's core API?" If from this extension → extension_op. If from
          Slicer core → slicer_op.
        - **Ask yourself**: "Does the user need to physically touch the 3D view?" If yes →
          user_interaction.
        - **Checkbox/toggle steps**: If the checkbox controls patient-specific or
          case-specific behavior (e.g., left/right, type selection) → user_choice.
          If the checkbox triggers a known extension method → extension_op.
          If the checkbox sets an extension parameter node value (no Logic method call,
          just UI state) → extension_op with extension_method_hint set to the parameter name.
          Extension UI checkboxes are NEVER slicer_op.
        - **Dropdown selections**: If selecting from this extension's outputs (e.g.,
          picking a segmentation it created) → extension_op (use the Logic class).
          If selecting from Slicer core nodes or modules → slicer_op.
          If the agent cannot determine WHICH option to select → user_choice.
          IMPORTANT: "Select the [X] volume/segmentation/node" is user_choice when the
          agent cannot programmatically determine WHICH scene node is X. Do NOT guess
          based on node names (e.g., "maybe there's a volume named 'Mandible'").
          If the step says "select the Mandible Volume" and the agent has no reliable
          way to know which volume is the mandible, it must ask the user → user_choice.
        - **Button clicks**: If a step says "Click [X] button" where X is a button in
          THIS extension's UI panel, classify as extension_op even if the exact method
          name is not in the catalog. Extension buttons call extension Logic methods.
          Only classify as slicer_op when the step explicitly references Slicer core
          features (layout changes, module switching, slicer.app, slicer.util).
        - **Module/panel location phrases**: Cookbook steps are user-facing UI records.
          Phrases like "In the Markups module's Display > Advanced panel, configure View..."
          identify where the user found a control. They are NOT a request to switch the
          active module. Do not create a separate `module_switching` sub-operation and do
          not use `slicer.util.selectModule` for such location context. Classify the
          actual setting change (for example Markups display View restrictions) as the
          operation. Use `module_switching` only when the cookbook explicitly asks to make
          the active module change the final state, such as "Switch to Markups module",
          "Open the Markups module", or "Select the Markups module".
        - **Slicer core UI operations** (CRITICAL — these are slicer_op, NOT extension_op):
          The following operations use Slicer's core API, not the extension's Logic class.
          Even if described in the context of using the extension, they are slicer_op:
          • "Slice visibility in 3D view" → slicer_op (use the verified Slicer slice-view API)
          • "Slice intersection visibility" / "Crosshair" → slicer_op (vtkMRMLCrosshairNode)
          • "FOV/Spacing match 2D" → slicer_op (vtkMRMLSliceNode.SetSliceSpacingMode)
          • Explicit "Open [X] module" / "Switch to [X] module" → slicer_op (slicer.util.selectModule)
          • Layout changes (Conventional, Four-Up, etc.) → slicer_op (layoutManager.setLayout)
          • "Display" panel / "View" settings on markup nodes → slicer_op (display node API)
          Extension UI toggles (checkboxes in the extension's own panel) are still
          extension_op, but Slicer core view/display/interaction toggles are slicer_op.
          Key test: "Does this use slicer.app, slicer.util, or a vtkMRML*Node method?"
          If yes → slicer_op. "Does this set an extension parameter node value?" If yes → extension_op.
        - **Evidence requirement**: extension_op must cite extension evidence
          (logic_method/widget_connection/ui_control/parameter_node). slicer_op must
          cite slicer_core evidence and include `slicer_op_category`.
          If evidence is weak or absent, return unknown_op with confidence "low".
        - Mark optional/experimental steps with is_optional: true.
        - Return ONLY the JSON object, no markdown fences or explanation.""")

        try:
            response = self._call_llm(prompt)
            decomposition = self._parse_json_response(response)
            if decomposition is None:
                logger.warning(
                    "Stage 4: LLM response could not be parsed as JSON. "
                    "Response starts with: %s... Falling back to keyword heuristics.",
                    response[:200] if response else "(empty)",
                )
        except Exception as e:
            logger.warning(
                "Stage 4 LLM decomposition failed (%s), falling back to heuristics", e
            )
            decomposition = None

        # Validate LLM output structure
        if (
            not decomposition
            or not isinstance(decomposition.get("steps"), list)
            or len(decomposition["steps"]) != len(cookbook_def.steps)
        ):
            logger.warning(
                "Stage 4 LLM decomposition returned invalid structure "
                "(got %d steps, expected %d), falling back to keyword heuristics",
                len(decomposition.get("steps", [])) if decomposition and isinstance(decomposition, dict) else 0,
                len(cookbook_def.steps),
            )
            return self._cookbook_build_stage_map(cookbook_def, logic_analysis)

        # Convert LLM decomposition into stage_map format
        return self._build_stage_map_from_decomposition(
            decomposition, cookbook_def, logic_analysis
        )

    def _build_stage_map_from_decomposition(
        self, decomposition: Dict, cookbook_def, logic_analysis: Dict
    ) -> Dict:
        """Convert LLM decomposition output into the stage_map dict format."""
        raw_methods = logic_analysis.get("methods", [])
        if isinstance(raw_methods, list):
            all_methods = {}
            for m in raw_methods:
                if isinstance(m, dict) and m.get("name"):
                    all_methods[m["name"]] = m
        else:
            all_methods = raw_methods if isinstance(raw_methods, dict) else {}

        stages = []
        llm_steps = {}
        for raw_step in decomposition.get("steps", []):
            if not isinstance(raw_step, dict):
                continue
            step_number = _int_or_none(raw_step.get("step_number"))
            if step_number is not None:
                llm_steps[step_number] = raw_step

        for cb_step in cookbook_def.steps:
            step_num = cb_step.step_number
            step_id = f"cb_step_{step_num}"
            llm_step = llm_steps.get(step_num, {})
            llm_sub_ops = llm_step.get("sub_operations", [])
            method_names = list(all_methods.keys())
            step_evidence = self._collect_step_evidence(
                cb_step.description, method_names, cookbook_def.extension_name
            )

            # If LLM returned nothing for this step, fall back to heuristic
            if not llm_sub_ops:
                llm_sub_ops = [{
                    "op_type": "extension_op",
                    "description": cb_step.description[:200],
                    "extension_method_hint": None,
                    "slicer_api_keywords": [],
                    "interaction_type": None,
                    "node_class": None,
                    "placement_instructions": None,
                }]

            # Normalize sub-operations: ensure required fields
            sub_ops = []
            for so in llm_sub_ops:
                if not isinstance(so, dict):
                    so = {"description": so}
                op_type = _optional_text(so.get("op_type")) or "extension_op"
                if op_type not in ("extension_op", "slicer_op", "user_interaction", "user_choice", "unknown_op"):
                    op_type = "extension_op"
                description = _text_or_empty(
                    so.get("description", cb_step.description[:200])
                )
                method_hint = _optional_text(so.get("extension_method_hint"))
                node_class = _optional_text(so.get("node_class"))
                evidence_type = _optional_text(so.get("evidence_type")) or "unknown"
                evidence_id = _optional_text(so.get("evidence_id"))
                confidence = (_optional_text(so.get("confidence")) or "medium").lower()
                if confidence not in ("high", "medium", "low"):
                    confidence = "medium"
                interaction_kind = (
                    _optional_text(so.get("interaction_kind"))
                    or self._infer_interaction_kind_from_evidence(step_evidence, node_class or "")
                )
                slicer_op_category = (
                    _optional_text(so.get("slicer_op_category"))
                    or self._infer_slicer_op_category(description, step_evidence)
                )
                normalized = {
                    "op_type": op_type,
                    "description": description,
                    "extension_method_hint": method_hint,
                    "slicer_api_keywords": _text_list(so.get("slicer_api_keywords", [])),
                    "interaction_type": _optional_text(so.get("interaction_type")),
                    "node_class": node_class,
                    "placement_instructions": _optional_text(so.get("placement_instructions")),
                    "min_control_points": so.get("min_control_points", 0),
                    "evidence_type": evidence_type,
                    "evidence_id": evidence_id,
                    "confidence": confidence,
                    "interaction_kind": interaction_kind,
                    "slicer_op_category": slicer_op_category,
                    "is_optional": so.get("is_optional", False),
                }
                # user_choice-specific fields
                if op_type == "user_choice":
                    normalized["question"] = _text_or_empty(so.get("question", cb_step.description))
                    choices = so.get("choices", [])
                    normalized["choices"] = choices if isinstance(choices, list) else []
                    normalized["parameter_name"] = (
                        _optional_text(so.get("parameter_name")) or f"choice_step_{step_num}"
                    )
                    normalized["default_value"] = so.get("default_value")
                sub_ops.append(normalized)

            original_step_text = _text_or_empty(cb_step.description)
            is_location_context = (
                self._is_ui_location_context_text(original_step_text)
                and not self._is_explicit_module_switch_text(original_step_text)
            )
            if is_location_context:
                kept_sub_ops = []
                removed_module_switch = False
                for so in sub_ops:
                    is_module_switch = (
                        so.get("op_type") == "slicer_op"
                        and so.get("slicer_op_category") == "module_switching"
                    )
                    if is_module_switch:
                        removed_module_switch = True
                        continue
                    kept_sub_ops.append(so)
                if removed_module_switch and kept_sub_ops:
                    sub_ops = kept_sub_ops
                    logger.info(
                        "[Stage 4] Removed invented module_switching sub-operation "
                        "from step %d because the cookbook text is UI-location context",
                        step_num,
                    )
                elif removed_module_switch and not kept_sub_ops:
                    sub_ops = [{
                        "op_type": "slicer_op",
                        "description": original_step_text[:300],
                        "extension_method_hint": None,
                        "slicer_api_keywords": ["display", "view"],
                        "interaction_type": None,
                        "node_class": None,
                        "placement_instructions": None,
                        "min_control_points": 0,
                        "evidence_type": "slicer_core",
                        "evidence_id": "markups_display",
                        "confidence": "medium",
                        "interaction_kind": "none",
                        "slicer_op_category": "markups_display",
                        "is_optional": False,
                    }]
                    logger.info(
                        "[Stage 4] Reinterpreted module location context as markups_display "
                        "for step %d",
                        step_num,
                    )

            # Resolve extension_method_hint to actual method names
            for so in sub_ops:
                hint = so.get("extension_method_hint")
                if hint and hint not in all_methods:
                    matched = self._match_method_name(hint, method_names)
                    if matched:
                        so["extension_method_hint"] = matched

            # Deterministic evidence validation. The LLM may propose op_type,
            # but source/UI/Slicer-core evidence decides whether it can stand.
            for so in sub_ops:
                desc_lower = _text_or_empty(so.get("description")).lower()
                if (
                    so["op_type"] not in ("user_choice", "user_interaction")
                    and self._evidence_has(step_evidence, "choice_candidates")
                    and not self._evidence_has(step_evidence, "widget_candidates")
                    and not so.get("extension_method_hint")
                ):
                    so["op_type"] = "user_choice"
                    so["question"] = so.get("question") or so.get("description", cb_step.description)
                    so["choices"] = so.get("choices", [])
                    so["parameter_name"] = so.get("parameter_name") or f"choice_step_{step_num}"
                    so["slicer_api_keywords"] = []
                    so["evidence_type"] = "user_context"
                    so["confidence"] = "high"
                elif (
                    so["op_type"] == "unknown_op"
                    and self._evidence_has(step_evidence, "interaction_candidates")
                ):
                    interaction = step_evidence["interaction_candidates"][0]
                    so["op_type"] = "user_interaction"
                    so["interaction_kind"] = interaction.get("interaction_kind", "markup_placement")
                    so["interaction_type"] = interaction.get("interaction_type")
                    so["node_class"] = interaction.get("node_class")
                    so["placement_instructions"] = so.get("placement_instructions") or so.get("description")
                    so["evidence_type"] = "viewport_action"
                    so["confidence"] = "high"
                elif so["op_type"] == "unknown_op" and self._evidence_has(
                    step_evidence, "logic_method_candidates"
                ):
                    method = step_evidence["logic_method_candidates"][0].get("method")
                    so["op_type"] = "extension_op"
                    so["extension_method_hint"] = method
                    so["evidence_type"] = "logic_method"
                    so["evidence_id"] = method
                    so["confidence"] = "high"
                elif so["op_type"] == "unknown_op" and self._evidence_has(
                    step_evidence, "slicer_core_candidates"
                ):
                    category = self._infer_slicer_op_category(so.get("description", ""), step_evidence)
                    if category:
                        so["op_type"] = "slicer_op"
                        so["slicer_op_category"] = category
                        so["evidence_type"] = "slicer_core"
                        so["evidence_id"] = category
                        so["confidence"] = "medium"

                if so["op_type"] == "extension_op":
                    if so.get("extension_method_hint"):
                        so["evidence_type"] = "logic_method"
                        so["evidence_id"] = so["extension_method_hint"]
                        so["confidence"] = "high"
                    elif self._evidence_has(step_evidence, "widget_candidates"):
                        widget = step_evidence["widget_candidates"][0]
                        logic_methods = widget.get("logic_methods") or []
                        if logic_methods:
                            so["extension_method_hint"] = logic_methods[0]
                        so["evidence_type"] = "widget_connection"
                        so["evidence_id"] = widget.get("button_widget_name")
                        so["confidence"] = "high"
                    elif self._evidence_has(step_evidence, "ui_control_candidates"):
                        so["evidence_type"] = "ui_control"
                        so["evidence_id"] = step_evidence["ui_control_candidates"][0].get("control")
                        so["confidence"] = "medium"
                    else:
                        matched = self._match_description_to_method(desc_lower, method_names)
                        if matched:
                            so["extension_method_hint"] = matched
                            so["evidence_type"] = "logic_method"
                            so["evidence_id"] = matched
                            so["confidence"] = "high"
                        else:
                            so["op_type"] = "unknown_op"
                            so["evidence_type"] = "unknown"
                            so["confidence"] = "low"
                elif so["op_type"] == "slicer_op":
                    category = so.get("slicer_op_category") or self._infer_slicer_op_category(
                        so.get("description", ""), step_evidence
                    )
                    if self._evidence_has(step_evidence, "slicer_core_candidates") and category:
                        so["slicer_op_category"] = category
                        so["evidence_type"] = "slicer_core"
                        so["evidence_id"] = category
                        if so.get("confidence") == "low":
                            so["confidence"] = "medium"
                    else:
                        so["op_type"] = "unknown_op"
                        so["slicer_api_keywords"] = []
                        so["evidence_type"] = "unknown"
                        so["confidence"] = "low"
                elif so["op_type"] == "user_interaction":
                    so["evidence_type"] = "viewport_action"
                    so["interaction_kind"] = (
                        so.get("interaction_kind")
                        or self._infer_interaction_kind_from_evidence(
                            step_evidence, so.get("node_class", "")
                        )
                    )
                    if so["interaction_kind"] == "view_adjustment" and not so.get("node_class"):
                        so["node_class"] = "vtkMRMLCrosshairNode"
                elif so["op_type"] == "user_choice":
                    so["evidence_type"] = "user_context"
                elif so["op_type"] == "unknown_op":
                    so["confidence"] = "low"

            # ── Reclassify extension-specific slicer_ops → extension_op ──
            # slicer_ops that reference the extension's own resources (custom
            # layouts, extension-defined node types, extension module names)
            # cannot be resolved via Slicer KB search. Reclassify them as
            # extension_op so they use the extension source for code generation.
            ext_name = _text_or_empty(cookbook_def.extension_name)
            ext_name_lower = ext_name.lower() if ext_name else ""
            # Common patterns indicating extension-specific knowledge:
            # - The extension's own name in layout/view descriptions
            # - Custom layout IDs registered by the extension
            # - Extension module names not in Slicer core
            _extension_specific_indicators = set()
            if ext_name_lower:
                _extension_specific_indicators.add(ext_name_lower)
                # Also add shortened forms (e.g., "brp" for BoneReconstructionPlanner)
                parts = _re.sub(r'([a-z])([A-Z])', r'\1 \2', ext_name).split()
                if parts:
                    acronym = "".join(p[0].lower() for p in parts if p)
                    if len(acronym) >= 2:
                        _extension_specific_indicators.add(acronym)

            for so in sub_ops:
                if so["op_type"] != "slicer_op":
                    continue
                desc_lower = _text_or_empty(so.get("description")).lower()
                keywords_lower = [
                    _text_or_empty(k).lower()
                    for k in _text_list(so.get("slicer_api_keywords", []))
                ]
                combined_text = desc_lower + " " + " ".join(keywords_lower)

                # Check if the description/keywords reference the extension itself
                is_extension_specific = False
                for indicator in _extension_specific_indicators:
                    if indicator in combined_text:
                        is_extension_specific = True
                        break

                if is_extension_specific:
                    # Try to find a matching extension method
                    matched_method = self._match_description_to_method(desc_lower, method_names)
                    so["op_type"] = "extension_op"
                    so["extension_method_hint"] = matched_method
                    so["slicer_api_keywords"] = []
                    so["evidence_type"] = "ui_control"
                    so["evidence_id"] = ext_name
                    so["confidence"] = "medium"
                    logger.info(
                        "[Stage 4] Reclassified step %d slicer_op → extension_op "
                        "(extension-specific: '%s'): %s",
                        step_num, ext_name, desc_lower[:60],
                    )

            # ── Widget connection verification: slicer_ops matching extension buttons → extension_op ──
            if self._widget_connections:
                for so in sub_ops:
                    if so["op_type"] != "slicer_op":
                        continue
                    desc_lower = _text_or_empty(so.get("description")).lower()
                    for conn in self._widget_connections:
                        btn_name = _text_or_empty(conn.get("button_widget_name")).lower()
                        logic_methods = conn.get("logic_methods", [])
                        # Extract significant words from button name for matching
                        btn_words = [w for w in btn_name.replace("_", " ").replace(".", " ").split() if len(w) > 3]
                        if not btn_words:
                            continue
                        match_count = sum(1 for w in btn_words if w in desc_lower)
                        if match_count >= 2 or (len(btn_words) == 1 and match_count == 1):
                            so["op_type"] = "extension_op"
                            if logic_methods:
                                so["extension_method_hint"] = logic_methods[0]
                            so["slicer_api_keywords"] = []
                            so["evidence_type"] = "widget_connection"
                            so["evidence_id"] = conn.get("button_widget_name", "")
                            so["confidence"] = "high"
                            logger.info(
                                "[Stage 4] Reclassified step %d slicer_op → extension_op "
                                "(widget button '%s' match): %s",
                                step_num, conn.get("button_widget_name", ""), desc_lower[:60],
                            )
                            break

            # ── "Select/choose/set" without method hint → user_choice ──
            for so in sub_ops:
                if so["op_type"] != "slicer_op":
                    continue
                desc = _text_or_empty(so.get("description")).lower()
                has_hint = bool(so.get("extension_method_hint"))
                if not has_hint and any(
                    desc.startswith(w) for w in ("select ", "choose ", "set the ")
                ):
                    so["op_type"] = "user_choice"
                    so["question"] = so.get("description", "")
                    so["slicer_api_keywords"] = []
                    so["parameter_name"] = f"choice_step_{step_num}"
                    so["evidence_type"] = "user_context"
                    so["confidence"] = "high"
                    logger.info(
                        "[Stage 4] Reclassified step %d slicer_op → user_choice "
                        "(selection without method hint): %s",
                        step_num, desc[:60],
                    )

            # ── "Tick/enable/toggle" extension UI controls without method hint → extension_op ──
            # Extension UI checkboxes/toggles set extension parameter node values,
            # not Slicer core API. If there's no Logic method, it's still extension_op
            # because the parameter names are extension-specific.
            for so in sub_ops:
                if so["op_type"] != "slicer_op":
                    continue
                desc = _text_or_empty(so.get("description")).lower()
                has_hint = bool(so.get("extension_method_hint"))
                if not has_hint and any(
                    desc.startswith(w) for w in ("tick ", "toggle ", "enable ", "check ", "uncheck ")
                ):
                    so["op_type"] = "extension_op"
                    so["slicer_api_keywords"] = []
                    so["evidence_type"] = "ui_control"
                    so["evidence_id"] = "extension_ui_toggle"
                    so["confidence"] = "medium"
                    logger.info(
                        "[Stage 4] Reclassified step %d slicer_op → extension_op "
                        "(extension UI control without method hint): %s",
                        step_num, desc[:60],
                    )

            # ── Reclassify extension_op/unknown_op → slicer_op when no method hint and matches Slicer core ──
            # Sub-ops classified as extension_op (or downgraded to unknown_op due to
            # no matching method) that describe Slicer core UI operations should be
            # slicer_op so Stage 5T / Stage 7 can generate proper Slicer API code.
            _SLICER_CORE_PATTERNS = {
                "layout_slice_view": [
                    "layout", "conventional", "four-up", "slice view",
                    "fov", "spacing match", "field of view",
                ],
                "module_switching": [
                    "switch to", "open module", "open the",
                    "select module", "activate module", "go to module",
                ],
                "crosshair": [
                    "crosshair", "slice intersection",
                    "intersection visibility", "enable interaction",
                ],
                "node_display": [
                    "slice visibility", "slice visible",
                    "set slice visible", "toggle slice",
                ],
                "markups_display": [
                    "display view", "view node", "display node",
                    "set view", "view 1", "advanced panel",
                ],
            }
            for so in sub_ops:
                if so["op_type"] not in ("extension_op", "unknown_op"):
                    continue
                if so.get("extension_method_hint"):
                    continue
                desc_lower = _text_or_empty(so.get("description")).lower()
                # Skip if description references the extension name
                is_extension_specific = False
                for indicator in _extension_specific_indicators:
                    if indicator in desc_lower:
                        is_extension_specific = True
                        break
                if is_extension_specific:
                    continue
                category = so.get("slicer_op_category", "")
                patterns = _SLICER_CORE_PATTERNS.get(category, [])
                if not patterns or not any(kw in desc_lower for kw in patterns):
                    # Also check all categories for keyword matches.  The LLM may
                    # provide a broad category such as layout_slice_view for a
                    # more specific Slicer core operation such as slice visibility.
                    for cat, kws in _SLICER_CORE_PATTERNS.items():
                        if any(kw in desc_lower for kw in kws):
                            category = cat
                            patterns = kws
                            break
                if category == "module_switching" and not self._is_explicit_module_switch_text(desc_lower):
                    continue
                if patterns and any(kw in desc_lower for kw in patterns):
                    so["op_type"] = "slicer_op"
                    so["slicer_op_category"] = category
                    so["slicer_api_keywords"] = so.get("slicer_api_keywords") or [category]
                    so["evidence_type"] = "slicer_core"
                    so["evidence_id"] = category
                    so["confidence"] = "high"
                    logger.info(
                        "[Stage 4] Reclassified step %d %s → slicer_op "
                        "(Slicer core UI pattern '%s'): %s",
                        step_num, so.get("op_type", "?"), category, desc_lower[:60],
                    )

            # Build method_details from matched extension_op sub-operations
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

            # Determine overall step op_type
            op_types = {so["op_type"] for so in sub_ops}
            if len(op_types) > 1:
                stage_op_type = "mixed"
            elif op_types:
                stage_op_type = op_types.pop()
            else:
                stage_op_type = "extension_op"

            # Determine stage name
            stage_method_names = [m["name"] for m in stage_methods] if stage_methods else []
            stage_name = self._infer_stage_name(
                stage_method_names, step_num - 1, len(cookbook_def.steps)
            )

            # Determine if the step is optional
            is_optional = any(so.get("is_optional") for so in sub_ops)

            stage = {
                "stage_index": step_num - 1,
                "stage_name": stage_name,
                "methods": stage_method_names,
                "method_details": stage_methods,
                "depends_on": (
                    [f"cb_step_{d}" for d in cb_step.depends_on]
                    if cb_step.depends_on
                    else ([f"cb_step_{step_num - 1}"] if step_num > 1 else [])
                ),
                "input_nodes": [],
                "output_nodes": [],
                "op_type": stage_op_type,
                "cookbook_step": cb_step,
                "sub_operations": sub_ops,
                "is_optional": is_optional,
            }
            stages.append(stage)

        self.on_progress(
            4, "Cookbook Stage Map",
            f"Decomposed {len(stages)} cookbook steps via LLM"
        )

        return {
            "stages": stages,
            "stage_count": len(stages),
            "source": "cookbook_llm_decomposition",
        }

    # ================================================================
