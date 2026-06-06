from .common import *


class AnalyzerCrossStageMixin:
    def _stage4_5_cross_stage_mapping(
        self, stage_map: Dict, logic_analysis: Dict, extension_name: str
    ) -> Dict:
        """
        Use LLM to analyze data flow between cookbook steps.

        Produces a cross_stage_map: e.g., "Step 2 writes self.mandibularSegmentation,
        and Step 4 reads it." Falls back to programmatic Jaccard matching on failure.
        """
        self.on_progress(
            "4.5", "Cross-Stage Parameter Mapping",
            "LLM analyzing data flow between steps..."
        )

        stages = stage_map.get("stages", [])
        if len(stages) <= 1:
            self.on_progress(
                "4.5", "Cross-Stage Parameter Mapping",
                "Single stage — no cross-stage mapping needed"
            )
            return {"_extension_name": extension_name}

        # Build step summaries with state info
        step_summaries = []
        for s in stages:
            idx = s.get("stage_index", 0)
            methods = s.get("method_details") or []
            state_reads = []
            state_writes = []
            for m in methods:
                if not isinstance(m, dict):
                    continue
                state_reads.extend(m.get("state_reads") or [])
                state_writes.extend(m.get("state_writes") or [])
            # Also include sub-operation info
            sub_ops = s.get("sub_operations") or []
            sub_ops_desc = [
                f"  - {so['op_type']}: {so.get('description', '')[:100]}"
                for so in sub_ops
                if isinstance(so, dict)
            ]
            step_summaries.append({
                "step_number": idx + 1,
                "step_id": f"cb_step_{idx + 1}",
                "stage_name": s.get("stage_name", ""),
                "methods": s.get("methods", []),
                "state_reads": list(set(state_reads)),
                "state_writes": list(set(state_writes)),
                "sub_operations": sub_ops_desc,
            })

        state_fields = logic_analysis.get("state_fields", [])

        prompt = textwrap.dedent(f"""\
        Analyze the data flow between steps of a Slicer extension cookbook workflow.

        ## State Fields (Logic class self.* fields)
        {json.dumps(state_fields, indent=2)}

        ## Workflow Steps
        {json.dumps(step_summaries, indent=2)}

        ## Task
        For each step that depends on data produced by an earlier step, identify the
        connection. This is critical for code template generation so that later steps
        can find nodes created by earlier steps.

        Connections can be:
        - **state_field**: Step N writes self.fieldX, and Step M reads self.fieldX.
        - **output_node**: Step N creates a vtkMRML node (via parameter or state write),
          and Step M needs that node as input.
        - **scene_state**: Step N changes the scene (selects a node, changes layout),
          and Step M relies on that state.

        Return a JSON object:
        {{
          "connections": [
            {{
              "from_step": 2,
              "to_step": 4,
              "type": "state_field" | "output_node" | "scene_state",
              "field": "self.mandibularSegmentation",
              "description": "Step 2 creates the mandible segmentation node which Step 4 reads"
            }}
          ]
        }}

        Return ONLY the JSON, no markdown fences or explanation.""")

        try:
            response = self._call_llm(prompt)
            result = self._parse_json_response(response)
        except Exception as e:
            logger.warning(
                "Stage 4.5 LLM cross-stage mapping failed (%s), "
                "falling back to programmatic matching", e
            )
            result = None

        # Convert LLM connections into cross_stage_map format
        if result and isinstance(result.get("connections"), list):
            cross_map = {"_extension_name": extension_name}
            for conn in result["connections"]:
                to_step = conn.get("to_step")
                if to_step is None:
                    continue
                to_idx = to_step - 1
                from_idx = conn.get("from_step", 0) - 1
                field = conn.get("field", "")
                desc = conn.get("description", "")
                conn_type = conn.get("type", "state_field")

                stage_map_entry = cross_map.setdefault(to_idx, {})
                # Use the field name as the parameter key
                param_key = field.replace("self.", "") if field else f"step_{from_idx + 1}_output"
                stage_map_entry[param_key] = {
                    "source_stage": from_idx,
                    "source_param": param_key,
                    "type": conn_type,
                    "description": desc,
                }

            self.on_progress(
                "4.5", "Cross-Stage Parameter Mapping",
                f"LLM identified {len(result['connections'])} cross-stage connections"
            )
            return cross_map

        # Fallback to programmatic Jaccard matching
        self.on_progress(
            "4.5", "Cross-Stage Parameter Mapping",
            "Falling back to programmatic name-similarity matching"
        )
        return self._map_cross_stage_params(stage_map, extension_name)

    # ================================================================
    # Node Lifecycle Analysis (folded into Stage 7)
    # ================================================================

    def _compute_node_lifecycle(self, scan_result: Dict, logic_analysis: Dict) -> Dict:
        """Compute node creation mode and param role for each vtkMRML parameter.

        This is an AST-based analysis (no LLM unless AST finds nothing) used
        internally by code template generation (Stage 7).
        """
        return self._stage4_node_lifecycle(scan_result, logic_analysis)

    def _classify_placement_starter_methods(self, logic_analysis: Dict) -> Dict[str, Dict]:
        """Detect extension methods that create a markup and enter placement mode.

        These methods correspond to UI buttons such as "Add cut plane" or
        "Add fibula line".  The generated workflow should call them in the
        pre-interaction template and should not create a second markup node or
        call the same method again in the post-interaction template.
        """
        logic_file = logic_analysis.get("_logic_file", "")
        starters: Dict[str, Dict] = {}

        for method in logic_analysis.get("methods", []):
            method_name = method.get("name", "")
            if not method_name:
                continue
            source = self._extract_method_source(logic_file, method_name) or ""
            if not source:
                continue

            markup_classes = sorted(set(_re.findall(r'"(vtkMRMLMarkups[^"]+Node)"', source)))
            creates_markup = bool(markup_classes) and (
                "CreateNodeByClass" in source or "AddNewNodeByClass" in source
            )
            sets_active_markup = "SetActiveListID" in source
            placement_mode = self._placement_mode_from_source(source)
            enters_place_mode = (
                placement_mode != "none"
                or "SetCurrentInteractionMode" in source
            )
            has_placement_observer = "PointPositionDefinedEvent" in source

            if creates_markup and sets_active_markup and enters_place_mode:
                starters[method_name] = {
                    "node_classes": markup_classes,
                    "starts_markup_placement": True,
                    "placement_mode": placement_mode,
                    "creates_node": creates_markup,
                    "sets_active_list": sets_active_markup,
                    "has_placement_observer": has_placement_observer,
                    "reason": "creates a Markups node, activates it, and enters placement mode",
                }

        if starters:
            logger.info(
                "[Stage 7] Detected placement-starter methods: %s",
                ", ".join(sorted(starters)),
            )
            self.on_progress(
                7, "Analyzing interaction methods",
                f"Detected {len(starters)} placement-starter method(s)"
            )
        return starters

    # ================================================================
    # Internal LLM Review of Templates (part of Stage 7)
    # ================================================================

    def _review_templates(
        self,
        templates: Dict[str, str],
        logic_analysis: Dict,
        node_lifecycle: Dict,
    ) -> Dict[str, str]:
        """Internal LLM review of generated templates. Not a separate pipeline stage."""
        return self._stage7b_review_templates(templates, logic_analysis, node_lifecycle)

    # ================================================================
    # [Kept for fallback] Stage 3: State Dependency Analysis
    # ================================================================
