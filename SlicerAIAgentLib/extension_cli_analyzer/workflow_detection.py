from .common import *


class AnalyzerWorkflowDetectionMixin:
    def _stage3_state_dependencies(self, logic_analysis: Dict) -> Dict:
        """Build stage map from state dependencies."""
        self.on_progress(3, "Analyzing state dependencies", "Building dependency graph...")

        methods = logic_analysis.get("methods", [])
        pipeline_methods = logic_analysis.get("pipeline_methods", [])
        state_fields = logic_analysis.get("state_fields", [])

        # Classify methods as primary or auxiliary
        primary_methods = []
        auxiliary_methods = []
        for m in methods:
            if self._is_auxiliary_method(m):
                auxiliary_methods.append(m["name"])
            else:
                primary_methods.append(m)

        # Only include primary methods in the dependency graph
        dep_graph = {}
        for method in primary_methods:
            name = method["name"]
            writes = set(method.get("state_writes", []))
            dep_graph[name] = {"writes": writes, "reads": set(method.get("state_reads", []))}

        # Compute dependencies among primary methods
        method_deps = {}
        for name, info in dep_graph.items():
            deps = set()
            for other_name, other_info in dep_graph.items():
                if other_name == name:
                    continue
                if info["reads"] & other_info["writes"]:
                    deps.add(other_name)
            method_deps[name] = deps

        # Identify stages (topological grouping) from primary methods only
        stages = []
        assigned = set()
        remaining = set(dep_graph.keys())

        while remaining:
            current_stage = []
            for name in sorted(remaining):
                if method_deps.get(name, set()).issubset(assigned):
                    current_stage.append(name)

            if not current_stage:
                current_stage = sorted(remaining)

            stages.append(current_stage)
            assigned.update(current_stage)
            remaining -= set(current_stage)

        # Build stage map — each stage gets its primary methods + any auxiliary methods
        # that should run as setup (folded into the first stage that has primary methods)
        stage_map = []
        for i, stage_methods in enumerate(stages):
            method_infos = []
            for mname in stage_methods:
                for m in primary_methods:
                    if m["name"] == mname:
                        method_infos.append(m)
                        break

            stage_name = self._infer_stage_name(stage_methods, i, len(stages))

            input_nodes = []
            output_nodes = []
            for mi in method_infos:
                for p in mi.get("parameters", []):
                    ptype = p.get("type", "")
                    if "vtkMRML" in ptype and p.get("required", True):
                        if "output" in p.get("name", "").lower() or "output" in p.get("description", "").lower():
                            output_nodes.append(p)
                        else:
                            input_nodes.append(p)

            stage_map.append({
                "stage_index": i,
                "stage_name": stage_name,
                "methods": stage_methods,
                "method_details": method_infos,
                "depends_on": [stages[j] for j in range(i) if j < len(stages)],
                "input_nodes": input_nodes,
                "output_nodes": output_nodes,
            })

        self.on_progress(
            3, "Analyzing state dependencies",
            f"Found {len(stage_map)} stages: {[s['stage_name'] for s in stage_map]}"
        )

        return {"stages": stage_map, "dep_graph": dep_graph, "method_deps": method_deps}

    @staticmethod
    def _infer_stage_name(methods: List[str], index: int, total: int) -> str:
        """Infer a semantic name for a stage from its method names."""
        names_lower = " ".join(m.lower() for m in methods)
        if "seg" in names_lower:
            return "segmentation"
        if "plan" in names_lower or "reduc" in names_lower or "screw" in names_lower:
            return "planning"
        if "regist" in names_lower or "align" in names_lower:
            return "registration"
        if "detect" in names_lower or "find" in names_lower:
            return "detection"
        if "mesh" in names_lower or "model" in names_lower or "generat" in names_lower:
            return "generation"
        if "visual" in names_lower or "render" in names_lower or "display" in names_lower:
            return "visualization"
        if total == 1:
            return "full"
        return f"stage_{index + 1}"

    @staticmethod
    def _map_cross_stage_params(stage_map: Dict, extension_name: str = "") -> Dict:
        """
        Map parameters in later stages to output parameters from earlier stages.

        Returns:
            {stage_index: {param_name: {"source_stage": int, "source_param": str}},
             "_extension_name": str}
        """
        stages = stage_map.get("stages", [])
        cross_map = {}
        if extension_name:
            cross_map["_extension_name"] = extension_name

        for i, stage in enumerate(stages):
            if i == 0:
                continue

            # Collect all output params from prior stages
            prior_outputs = []
            for j in range(i):
                for mi in stages[j].get("method_details", []):
                    for p in mi.get("parameters", []):
                        pname = p.get("name", "")
                        ptype = p.get("type", "")
                        if "vtkMRML" in ptype and (
                            "output" in pname.lower()
                            or "result" in pname.lower()
                            or "out" in pname.lower()
                        ):
                            prior_outputs.append((j, pname, ptype))

            # Match this stage's vtkMRML params against prior outputs
            stage_map_entry = {}
            for mi in stage.get("method_details", []):
                for p in mi.get("parameters", []):
                    pname = p.get("name", "")
                    ptype = p.get("type", "")
                    if "vtkMRML" not in ptype:
                        continue

                    # Try to match against prior outputs by type + name similarity
                    best_match = None
                    best_score = 0.0
                    for (src_stage, src_name, src_type) in prior_outputs:
                        if src_type != ptype:
                            continue
                        score = _name_similarity(pname, src_name)
                        if score > best_score:
                            best_score = score
                            best_match = (src_stage, src_name)

                    if best_match and best_score > 0.4:
                        stage_map_entry[pname] = {
                            "source_stage": best_match[0],
                            "source_param": best_match[1],
                        }

            if stage_map_entry:
                cross_map[i] = stage_map_entry

        return cross_map

    # ================================================================
    # Node Lifecycle Analysis (used internally by Stage 7)
    # ================================================================

    def _stage4_node_lifecycle(self, scan_result: Dict, logic_analysis: Dict) -> Dict:
        """Determine node creation mode and param role for each vtkMRML parameter."""
        self.on_progress(7, "Analyzing node lifecycle", "Determining node creation patterns via AST...")

        node_lifecycle = {}
        methods = logic_analysis.get("methods", [])
        logic_file = logic_analysis.get("_logic_file", "")

        for method in methods:
            mname = method["name"]
            params = method.get("parameters", [])

            # Build set of all param names for this method
            all_param_names = {p.get("name", "") for p in params}

            # Extract and parse method source
            method_source = self._extract_method_source(logic_file, mname)
            if not method_source:
                method_source = ""
            else:
                method_source = textwrap.dedent(method_source)

            # Run AST visitor
            visitor = _AddNodeVisitor(all_param_names)
            try:
                tree = ast.parse(method_source)
                visitor.visit(tree)
            except SyntaxError:
                logger.warning("Could not parse method %s for lifecycle analysis", mname)

            for p in params:
                ptype = p.get("type", "")
                pname = p.get("name", "")
                if "vtkMRML" not in ptype:
                    continue

                is_output = (
                    "output" in pname.lower()
                    or "result" in pname.lower()
                    or "out" in pname.lower()
                )
                if not is_output:
                    continue

                key = f"{mname}:{pname}"

                # Determine create_mode using AST results
                if pname in visitor.params_added_to_scene:
                    # Method calls AddNode(param) — caller should pre-create without adding
                    create_mode = "CreateNodeByClass"
                    reason = f"AST: method passes '{pname}' to AddNode() — pre-create without adding to scene"
                elif visitor.has_addnewnodebyclass:
                    # Method uses AddNewNodeByClass for other nodes, but not this param
                    # Be safe: use AddNewNodeByClass so the node is in the scene
                    create_mode = "AddNewNodeByClass"
                    reason = "AST: method uses AddNewNodeByClass for internal nodes — create and add to scene"
                else:
                    # No AddNode call targets this param — caller must create AND add
                    create_mode = "AddNewNodeByClass"
                    reason = "AST: no AddNode() call targets this param — caller creates and adds to scene"

                node_lifecycle[key] = {
                    "create_mode": create_mode,
                    "reason": reason,
                    "node_class": ptype,
                    "param_role": "output",
                }

        # If no output nodes found from parameters, ask LLM
        if not node_lifecycle:
            self.on_progress(
                7, "Analyzing node lifecycle",
                "Asking LLM about node creation patterns..."
            )
            node_lifecycle = self._llm_node_lifecycle(logic_analysis)

        self.on_progress(
            7, "Analyzing node lifecycle",
            f"Analyzed {len(node_lifecycle)} output nodes via AST"
        )

        return node_lifecycle

    def _llm_node_lifecycle(self, logic_analysis: Dict) -> Dict:
        """Use LLM to determine node lifecycle for ambiguous cases."""
        methods = logic_analysis.get("methods", [])
        method_summaries = []
        for m in methods:
            params_str = ", ".join(
                f"{p['name']}: {p['type']}"
                for p in m.get("parameters", [])
            )
            method_summaries.append(
                f"  {m['name']}({params_str})\n"
                f"    adds_output_to_scene: {m.get('adds_output_to_scene', 'unknown')}\n"
                f"    calls_addnode: {m.get('calls_addnode', 'unknown')}"
            )

        prompt = textwrap.dedent(f"""\
For each method below, determine whether its output node parameters should be created
with CreateNodeByClass (creates WITHOUT adding to scene) or AddNewNodeByClass (creates AND adds).

Rules:
- If the method calls slicer.mrmlScene.AddNode() on the parameter → use CreateNodeByClass (template should NOT add to scene)
- If the method does NOT add to scene itself → use AddNewNodeByClass (template must add)
- When unsure, default to CreateNodeByClass (safer — avoids "Node already added" errors)

Methods:
{chr(10).join(method_summaries)}

Return JSON:
{{
  "nodes": [
    {{"method": "method_name", "param": "param_name", "node_class": "vtkMRML...Node", "create_mode": "CreateNodeByClass" or "AddNewNodeByClass", "reason": "why"}}
  ]
}}""")

        response = self._call_llm(prompt)
        parsed = self._parse_json_response(response)
        if not parsed:
            return {}

        result = {}
        for node in parsed.get("nodes", []):
            key = f"{node['method']}:{node['param']}"
            result[key] = {
                "create_mode": node.get("create_mode", "CreateNodeByClass"),
                "reason": node.get("reason", ""),
                "node_class": node.get("node_class", ""),
            }
        return result

    # ================================================================
    # [Kept for fallback] Interactive Pattern Detection
    # ================================================================

    # MRML markup node class prefixes for AST scanning
    _MARKUP_NODE_CLASSES = {
        "vtkMRMLMarkupsCurveNode": "curve",
        "vtkMRMLMarkupsPlaneNode": "plane",
        "vtkMRMLMarkupsLineNode": "line",
        "vtkMRMLMarkupsFiducialNode": "fiducial",
        "vtkMRMLMarkupsROINode": "roi",
    }

    _INTERACTION_PATTERNS = [
        "StartPlaceMode", "SetPlaceModeEnabled", "SwitchToSinglePlaceMode",
        "SwitchToPersistentPlaceMode", "PlaceModeEnabled",
        "AddObserver", "PointModifiedEvent", "PointAddedEvent",
        "PointPositionDefinedEvent", "InteractionEvent",
        "DynamicModeler", "vtkSlicerDynamicModelerModuleLogic",
        "HandlesInteractive", "RotationHandleVisibility",
        "TranslationHandleVisibility", "ScaleHandleVisibility",
        "QTimer", "singleShot",
    ]

    def _stage4b_detect_interactive_patterns(
        self, scan_result: Dict, logic_analysis: Dict
    ) -> Dict:
        """
        Detect interactive markup placement patterns in the extension source.

        Scans both the Logic class and the Widget class (if found in the same file)
        for markup node creation, placement mode entry, observer setup, and
        debounce timer patterns.

        Returns:
            Dict with:
            - has_interactive: bool
            - patterns: list of detected interactive pattern descriptors
            - widget_source: str (Widget class source, if found)
        """
        self.on_progress("4.5", "Interactive Pattern Detection", "Scanning for markup nodes...")

        result = {"has_interactive": False, "patterns": [], "widget_source": ""}

        # Read the full extension source to scan for Widget class
        entry_module = scan_result.get("entry_module")
        if not entry_module or not os.path.isfile(entry_module):
            return result

        with open(entry_module, "r", encoding="utf-8", errors="ignore") as f:
            full_source = f.read()

        try:
            full_tree = ast.parse(full_source)
        except SyntaxError:
            return result

        # --- AST-based detection ---
        detected_markup_refs = set()
        detected_interaction_calls = set()
        detected_observer_patterns = set()
        detected_timer_patterns = set()

        for node in ast.walk(full_tree):
            # Detect string literals referencing markup node classes
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                for cls_name, interaction_type in self._MARKUP_NODE_CLASSES.items():
                    if cls_name in val:
                        detected_markup_refs.add((cls_name, interaction_type))
                if "Markups" in val and "Node" in val and val not in self._MARKUP_NODE_CLASSES:
                    detected_markup_refs.add((val, "unknown"))

            # Detect AddNewNodeByClass calls with markup node types
            if isinstance(node, ast.Call):
                func_str = self._get_call_name(node)
                if func_str and "AddNewNodeByClass" in func_str:
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            for cls_name, interaction_type in self._MARKUP_NODE_CLASSES.items():
                                if cls_name in arg.value:
                                    detected_markup_refs.add((cls_name, interaction_type))

                # Detect placement mode calls
                if func_str:
                    for pattern in ["StartPlaceMode", "SetPlaceModeEnabled",
                                    "SwitchToSinglePlaceMode", "SwitchToPersistentPlaceMode"]:
                        if pattern in func_str:
                            detected_interaction_calls.add(pattern)

        # String-based detection for patterns harder to catch with AST
        for pattern in self._INTERACTION_PATTERNS:
            if pattern in full_source:
                if "Observer" in pattern or "Event" in pattern:
                    detected_observer_patterns.add(pattern)
                elif "Timer" in pattern or "singleShot" in pattern:
                    detected_timer_patterns.add(pattern)

        has_interactive = bool(detected_markup_refs)
        result["has_interactive"] = has_interactive

        if not has_interactive:
            self.on_progress("4.5", "Interactive Pattern Detection", "No interactive patterns found")
            return result

        # --- LLM-assisted classification ---
        result["patterns"] = [
            {"class": cls, "interaction_type": itype}
            for cls, itype in detected_markup_refs
        ]
        result["interaction_calls"] = list(detected_interaction_calls)
        result["observer_patterns"] = list(detected_observer_patterns)
        result["timer_patterns"] = list(detected_timer_patterns)

        # Extract Widget class source for LLM context
        widget_source = self._extract_widget_source(full_tree, full_source)
        result["widget_source"] = widget_source[:_MAX_SOURCE_FOR_LLM]

        # Ask LLM to classify interactive patterns into phases
        logic_class_name = scan_result.get("logic_class", {}).get("class_name", "Logic")
        method_names = [
            m.get("name", "") for m in logic_analysis.get("methods", [])
            if not self._is_auxiliary_method(m)
        ]

        classification_prompt = textwrap.dedent(f"""\
        Analyze the following Slicer extension for interactive 3D user interaction patterns.

        Extension Logic class: {logic_class_name}
        Logic methods: {json.dumps(method_names[:30])}

        Detected markup node types: {json.dumps(list(detected_markup_refs))}
        Detected interaction calls: {json.dumps(list(detected_interaction_calls))}
        Detected observer patterns: {json.dumps(list(detected_observer_patterns))}
        Detected timer patterns: {json.dumps(list(detected_timer_patterns))}

        Widget class source (excerpt):
        ```python
        {widget_source}
        ```

        Classify each detected interactive pattern into a structured phase.
        For each phase, determine:
        1. phase_name: a short snake_case identifier
        2. interaction_type: "curve", "plane", "line", "fiducial", or "unknown"
        3. description: what the user does in this phase
        4. node_class: the vtkMRML node class used
        5. placement_instructions: what to tell the user to do
        6. min_control_points: minimum control points needed (0 if unknown)
        7. has_reactive_chain: true if observer triggers recomputation
        8. reactive_description: what recomputation happens (if has_reactive_chain)
        9. is_optional: true if this is an optional/experimental phase
        10. depends_on: list of phase_names this phase depends on

        Respond with ONLY a JSON array of phase objects, no markdown fences.
        """)

        self.on_progress("4.5", "Interactive Pattern Detection", "LLM classifying patterns...")
        try:
            llm_response = self._call_llm(classification_prompt)
            phases = self._parse_json_response(llm_response)
            if isinstance(phases, list):
                result["phases"] = phases
                self.on_progress(
                    "4.5", "Interactive Pattern Detection",
                    f"Classified {len(phases)} interactive phases"
                )
        except Exception as e:
            logger.warning(f"Stage 4.5 LLM classification failed: {e}")
            result["phases"] = []

        return result

    def _extract_widget_source(self, tree, full_source: str) -> str:
        """Extract the Widget class source from the full module AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    base_name = ""
                    if isinstance(base, ast.Name):
                        base_name = base.id
                    elif isinstance(base, ast.Attribute):
                        base_name = base.attr
                    if "Widget" in base_name:
                        try:
                            lines = full_source.split("\n")
                            start = node.lineno - 1
                            end = node.end_lineno if hasattr(node, "end_lineno") else len(lines)
                            return "\n".join(lines[start:end])
                        except Exception:
                            return ""
        return ""

    @staticmethod
    def _get_call_name(node) -> str:
        """Get the dotted name of a Call node's function."""
        parts = []
        current = node.func
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return ".".join(reversed(parts))

    # ================================================================
    # Stage 4.7: Workflow Graph Construction
    # ================================================================

    def _stage4c_build_workflow_graph(
        self,
        interactive_patterns: Dict,
        logic_analysis: Dict,
        stage_map: Dict,
        extension_name: str,
    ) -> Dict:
        """
        Construct a workflow graph from detected interactive patterns.

        When self._ui_workflow is available (from Stage 1.5), uses it as the
        primary step source, enriching interactive steps with detected pattern
        metadata (node_class, reactive_chains) from Stage 4.5.

        Otherwise falls back to merging stage_map + interactive patterns.
        """
        self.on_progress("4.7", "Workflow Graph Construction", "Building workflow graph...")

        phases = interactive_patterns.get("phases", [])

        # Build a lookup of interactive pattern metadata by logic method name
        pattern_by_method = {}
        for p in phases:
            # phase_name may match a logic method; also check interaction_type
            pattern_by_method[p.get("phase_name", "").lower()] = p

        # ---- UI Workflow path (preferred when available) ----
        if self._ui_workflow:
            steps = self._build_steps_from_ui_workflow(
                self._ui_workflow, pattern_by_method, phases
            )
            if steps:
                return self._finalize_workflow_graph(steps, "4.7")

        # ---- Fallback: original merge logic ----
        if not phases:
            self.on_progress("4.7", "Workflow Graph Construction", "No phases to build")
            return None

        steps = []
        automated_stages = stage_map.get("stages", [])

        # First, add any automated stages that aren't covered by interactive phases
        phase_names = [p.get("phase_name") for p in phases]

        added_automated = set()
        for stage_idx, stage_info in enumerate(automated_stages):
            stage_methods = stage_info.get("methods", [])
            # Check if this stage's purpose overlaps with any interactive phase
            stage_name = stage_info.get("semantic_name", stage_info.get("stage_name", f"stage_{stage_idx}"))
            is_covered = any(
                p.get("phase_name") == stage_name
                for p in phases
            )
            if not is_covered and stage_idx not in added_automated:
                step = {
                    "step_id": stage_name,
                    "phase": stage_name,
                    "step_type": "automated",
                    "description": f"Automated step: {stage_name}",
                    "method_name": stage_methods[0] if stage_methods else None,
                    "depends_on": [],
                    "produces_nodes": [],
                }
                # Add dependency on previous step
                if steps:
                    step["depends_on"] = [steps[-1]["step_id"]]
                steps.append(step)
                added_automated.add(stage_idx)

        # Add interactive phases
        for phase in phases:
            phase_name = phase.get("phase_name", "unknown")
            interaction_type = phase.get("interaction_type", "unknown")
            node_class_map = {
                "curve": "vtkMRMLMarkupsCurveNode",
                "plane": "vtkMRMLMarkupsPlaneNode",
                "line": "vtkMRMLMarkupsLineNode",
                "fiducial": "vtkMRMLMarkupsFiducialNode",
            }
            node_class = phase.get("node_class") or node_class_map.get(interaction_type, "")

            step = {
                "step_id": phase_name,
                "phase": phase_name,
                "step_type": "interactive",
                "description": phase.get("description", ""),
                "interaction_type": interaction_type,
                "node_class": node_class,
                "placement_instructions": phase.get("placement_instructions", ""),
                "min_control_points": phase.get("min_control_points", 0),
                "validation_rules": [f"minimum {phase.get('min_control_points', 0)} control points"],
                "is_optional": phase.get("is_optional", False),
                "produces_nodes": [],
            }

            # Reactive chains
            if phase.get("has_reactive_chain"):
                step["reactive_chains"] = [{
                    "trigger_event": "PointModifiedEvent",
                    "recompute_description": phase.get("reactive_description", ""),
                    "debounce_ms": 300,
                }]
            else:
                step["reactive_chains"] = []

            # Dependencies
            deps = phase.get("depends_on", [])
            if isinstance(deps, list):
                step["depends_on"] = deps
            elif isinstance(deps, str):
                step["depends_on"] = [deps]
            else:
                # Auto-link to previous step
                if steps:
                    step["depends_on"] = [steps[-1]["step_id"]]

            steps.append(step)

        return self._finalize_workflow_graph(steps, "4.7")

    def _build_steps_from_ui_workflow(
        self,
        ui_workflow: Dict,
        pattern_by_method: Dict,
        phases: list,
    ) -> list:
        """Build workflow steps from the Stage 1.5 UI workflow, enriched with
        detected interactive pattern metadata from Stage 4.5."""
        node_class_map = {
            "curve": "vtkMRMLMarkupsCurveNode",
            "plane": "vtkMRMLMarkupsPlaneNode",
            "line": "vtkMRMLMarkupsLineNode",
            "fiducial": "vtkMRMLMarkupsFiducialNode",
        }

        steps = []
        step_id_set = set()

        for section in ui_workflow.get("ui_sections", []):
            is_section_optional = section.get("is_optional", False)
            for ui_step in section.get("steps", []):
                step_id = ui_step.get("step_id", "")
                logic_method = ui_step.get("logic_method", "")
                step_type = ui_step.get("step_type", "automated")
                is_optional = ui_step.get("is_optional", is_section_optional)

                # Cross-reference with Stage 4.5 detected patterns
                matched_pattern = self._match_pattern(
                    logic_method, step_id, pattern_by_method, phases
                )

                if step_type == "interactive":
                    interaction_type = ui_step.get("interaction_type") or (
                        matched_pattern.get("interaction_type", "") if matched_pattern else ""
                    )
                    node_class = (
                        ui_step.get("node_class")
                        or (matched_pattern.get("node_class", "") if matched_pattern else "")
                        or node_class_map.get(interaction_type, "")
                    )
                    min_cp = (
                        ui_step.get("min_control_points")
                        or (matched_pattern.get("min_control_points", 0) if matched_pattern else 0)
                        or 0
                    )
                    step = {
                        "step_id": step_id,
                        "phase": step_id,
                        "step_type": "interactive",
                        "description": ui_step.get("description", ""),
                        "method_name": logic_method,
                        "interaction_type": interaction_type,
                        "node_class": node_class,
                        "placement_instructions": ui_step.get("placement_instructions", "")
                            or (matched_pattern.get("placement_instructions", "") if matched_pattern else ""),
                        "min_control_points": min_cp,
                        "validation_rules": [f"minimum {min_cp} control points"],
                        "is_optional": is_optional,
                        "produces_nodes": [],
                    }
                    # Reactive chains from matched pattern
                    if matched_pattern and matched_pattern.get("has_reactive_chain"):
                        step["reactive_chains"] = [{
                            "trigger_event": "PointModifiedEvent",
                            "recompute_description": matched_pattern.get("reactive_description", ""),
                            "debounce_ms": 300,
                        }]
                    else:
                        step["reactive_chains"] = []
                else:
                    # Automated step
                    step = {
                        "step_id": step_id,
                        "phase": step_id,
                        "step_type": "automated",
                        "description": ui_step.get("description", f"Automated: {step_id}"),
                        "method_name": logic_method,
                        "depends_on": [],
                        "produces_nodes": [],
                    }
                    if is_optional:
                        step["is_optional"] = True

                # Dependencies from UI workflow
                deps = ui_step.get("depends_on", [])
                if isinstance(deps, list) and deps:
                    step["depends_on"] = deps
                elif not deps and steps:
                    step["depends_on"] = [steps[-1]["step_id"]]

                step_id_set.add(step_id)
                steps.append(step)

        return steps

    @staticmethod
    def _match_pattern(
        logic_method: str, step_id: str, pattern_by_method: Dict, phases: list
    ) -> Optional[Dict]:
        """Find the best matching Stage 4.5 pattern for a UI workflow step."""
        if not logic_method and not step_id:
            return None
        # Try exact match on logic method name
        if logic_method:
            for p in phases:
                pn = p.get("phase_name", "")
                if pn.lower() == logic_method.lower():
                    return p
        # Try step_id match
        if step_id:
            for p in phases:
                pn = p.get("phase_name", "")
                if pn.lower() == step_id.lower():
                    return p
        # Try token overlap
        lm_tokens = set(logic_method.lower().split("_")) if logic_method else set()
        si_tokens = set(step_id.lower().split("_")) if step_id else set()
        search_tokens = lm_tokens | si_tokens
        if search_tokens:
            for p in phases:
                pn_tokens = set(p.get("phase_name", "").lower().split("_"))
                if search_tokens & pn_tokens:
                    return p
        return None

    def _finalize_workflow_graph(self, steps: list, stage_label: str) -> Dict:
        """Apply optional→branch transformation and build the workflow_graph dict."""
        # Mark optional phases as branch steps
        for i, step in enumerate(steps):
            if step.get("is_optional"):
                step["step_type"] = "branch"
                step["condition"] = step.get("description", "Optional step")
                next_steps = [
                    s["step_id"] for s in steps[i+1:]
                    if not s.get("is_optional")
                ]
                step["branches"] = {
                    "yes": step["step_id"],
                    "no": next_steps[0] if next_steps else "",
                }

        workflow_graph = {
            "steps": steps,
            "phases": [
                {
                    "name": s["step_id"],
                    "optional": s.get("is_optional", False),
                }
                for s in steps
            ],
        }

        self.on_progress(
            stage_label, "Workflow Graph Construction",
            f"Built graph with {len(steps)} steps"
        )
        return workflow_graph

    # ================================================================
    # Stage 4.9: Workflow Validation (LLM-assisted)
    # ================================================================

    def _stage4d_validate_workflow(
        self, workflow_graph: Dict, logic_analysis: Dict
    ) -> Dict:
        """LLM reviews the workflow graph for completeness and correctness."""
        self.on_progress("4.9", "Workflow Validation", "LLM reviewing workflow...")

        steps_summary = [
            {
                "step_id": s["step_id"],
                "step_type": s["step_type"],
                "description": s.get("description", ""),
                "interaction_type": s.get("interaction_type"),
                "depends_on": s.get("depends_on", []),
            }
            for s in workflow_graph.get("steps", [])
        ]

        method_names = [
            m.get("name", "") for m in logic_analysis.get("methods", [])
        ]

        validation_prompt = textwrap.dedent(f"""\
        Review this workflow graph for a Slicer extension CLI tool.
        Check for:
        1. Every interactive step has a clear user action described
        2. Every automated step has a callable method that exists
        3. Dependencies form a connected DAG (no orphans, no cycles)
        4. Step order is sensible (data loading before processing, etc.)

        IMPORTANT: Do NOT remove automated steps. Automated steps (like "create models",
        "center line", "update plan") are valid workflow steps that the user triggers
        by clicking a button. Only suggest removing steps that are clearly not part of
        the user workflow (e.g., internal timer callbacks, error handlers, email/feedback).

        Workflow steps: {json.dumps(steps_summary, indent=2)}
        Available logic methods: {json.dumps(method_names[:30])}

        If the graph is valid, respond with: {{"valid": true}}
        If there are issues, respond with: {{"valid": false, "fixes": [list of fixes to apply]}}
        Each fix should be: {{"step_id": "...", "field": "...", "new_value": ...}}
        To remove a step entirely, use: {{"step_id": "...", "field": "step_type", "new_value": "removed"}}
        """)

        try:
            llm_response = self._call_llm(validation_prompt)
            review = self._parse_json_response(llm_response)
            if isinstance(review, dict) and not review.get("valid", True):
                # Apply fixes
                steps_to_remove = set()
                for fix in review.get("fixes", []):
                    step_id = fix.get("step_id")
                    field = fix.get("field")
                    new_value = fix.get("new_value")
                    if field == "step_type" and new_value == "removed":
                        steps_to_remove.add(step_id)
                        continue
                    for step in workflow_graph.get("steps", []):
                        if step.get("step_id") == step_id:
                            step[field] = new_value
                # Remove marked steps
                if steps_to_remove:
                    # Build dependency map for rewiring
                    dep_map = {}
                    for s in workflow_graph.get("steps", []):
                        dep_map[s.get("step_id", "")] = s.get("depends_on", [])

                    # Rewire: if step A depends on removed step B,
                    # replace B with B's own dependencies
                    for s in workflow_graph.get("steps", []):
                        new_deps = []
                        for dep in s.get("depends_on", []):
                            if dep in steps_to_remove:
                                # Replace with the removed step's dependencies
                                replaced = dep_map.get(dep, [])
                                for r in replaced:
                                    if r not in steps_to_remove and r not in new_deps:
                                        new_deps.append(r)
                            else:
                                new_deps.append(dep)
                        s["depends_on"] = new_deps

                    workflow_graph["steps"] = [
                        s for s in workflow_graph.get("steps", [])
                        if s.get("step_id") not in steps_to_remove
                    ]
                    workflow_graph["phases"] = [
                        p for p in workflow_graph.get("phases", [])
                        if p.get("name") not in steps_to_remove
                    ]
                fix_count = len(review.get("fixes", []))
                remove_count = len(steps_to_remove)
                self.on_progress(
                    "4.9", "Workflow Validation",
                    f"Applied {fix_count - remove_count} fixes, removed {remove_count} steps"
                )
            else:
                self.on_progress("4.9", "Workflow Validation", "Workflow validated")
        except Exception as e:
            logger.warning(f"Stage 4.9 LLM validation failed: {e}")
            self.on_progress("4.9", "Workflow Validation", "Validation skipped (LLM error)")

        return workflow_graph

    # ================================================================
    # Stage 6: Tool Schema Generation (LLM)
    # ================================================================
