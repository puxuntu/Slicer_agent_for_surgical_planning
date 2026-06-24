from .common import *


class AnalyzerCrossStageMixin:
    def _stage4_5_cross_stage_mapping(
        self, stage_map: Dict, logic_analysis: Dict, extension_name: str
    ) -> Dict:
        """
        Use LLM to analyze data flow between cookbook steps.

        Produces a cross_stage_map describing which step writes state or nodes
        consumed by later steps. Invalid semantic output stops generation.
        """
        self.on_progress(
            "contract", "Build Workflow Contract",
            "LLM analyzing data flow between steps..."
        )

        stages = stage_map.get("stages", [])
        if len(stages) <= 1:
            self.on_progress(
                "contract", "Build Workflow Contract",
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
            # Node DATAFLOW endpoints, so the LLM can connect a user-choice node
            # pick to the later logic-method parameter that consumes it (even when
            # the two have different names):
            #   node_outputs  — nodes this step PRODUCES (a user_choice node pick,
            #                   stored under its choice parameter name).
            #   node_inputs   — logic-method parameter names this step CONSUMES.
            node_outputs = []
            for so in sub_ops:
                if not isinstance(so, dict):
                    continue
                if str(so.get("value_kind") or "") == "node" and so.get("parameter_name"):
                    node_outputs.append({
                        "param": so.get("parameter_name"),
                        "node_class": so.get("node_class") or "",
                    })
            node_inputs = []
            for m in methods:
                if not isinstance(m, dict):
                    continue
                for p in m.get("parameters") or []:
                    pname = p.get("name") if isinstance(p, dict) else p
                    if pname and pname != "self":
                        node_inputs.append(pname)
            step_summaries.append({
                "step_number": idx + 1,
                "step_id": f"cb_step_{idx + 1}",
                "stage_name": s.get("stage_name", ""),
                "methods": s.get("methods", []),
                "state_reads": list(set(state_reads)),
                "state_writes": list(set(state_writes)),
                "sub_operations": sub_ops_desc,
                "node_outputs": node_outputs,
                "node_inputs": sorted(set(node_inputs)),
            })

        state_fields = logic_analysis.get("state_fields", [])

        # Closed-loop re-entry: downstream failures diagnosed as dataflow gaps
        # are surfaced so the re-derived mapping covers the missed connections.
        feedback_block = ""
        if getattr(self, "_upstream_feedback", None):
            feedback_block = (
                "\n## Upstream Failure Feedback\n"
                "A previous generation failed downstream validation with these "
                "issues diagnosed as missing or incorrect cross-step dataflow. "
                "Make sure the connections you return account for every input "
                "named below (its producing step must be connected):\n"
                + json.dumps(self._upstream_feedback, indent=2) + "\n"
            )

        prompt = textwrap.dedent(f"""\
        Analyze the data flow between steps of a Slicer extension cookbook workflow.

        ## State Fields (Logic class self.* fields)
        {json.dumps(state_fields, indent=2)}

        ## Workflow Steps
        {json.dumps(step_summaries, indent=2)}
        {feedback_block}
        ## Task
        For each step that depends on data produced by an earlier step, identify the
        connection. This is critical for code template generation so that later steps
        can find nodes created by earlier steps.

        Connections can be:
        - **state_field**: Step N writes self.fieldX, and Step M reads self.fieldX.
        - **output_node**: Step N produces a vtkMRML node, and Step M needs that node
          as input. This INCLUDES a user_choice step where the user picks a node (its
          `node_outputs`) that a later step's logic method consumes (its `node_inputs`).
          For output_node connections you MUST set:
            "from_param": the producer's output name (a `node_outputs[].param` of from_step,
                          or the self.field it creates),
            "to_param":   the consumer's input name (a `node_inputs[]` parameter of to_step).
          These may differ (e.g. from_param "orbitLandmarksNode" -> to_param "source_lm_node").
          Only connect node classes that are compatible.
        - **scene_state**: Step N changes the scene (selects a node, changes layout),
          and Step M relies on that state.

        Return a JSON object:
        {{
          "connections": [
            {{
              "from_step": 2,
              "to_step": 4,
              "type": "state_field" | "output_node" | "scene_state",
              "field": "self.outputNode",
              "from_param": "orbitLandmarksNode",
              "to_param": "source_lm_node",
              "description": "Step 2's chosen node feeds Step 4's method parameter"
            }}
          ]
        }}

        Return ONLY the JSON, no markdown fences or explanation.""")

        valid_step_numbers = {item["step_number"] for item in step_summaries}
        state_field_names = {
            _text_or_empty(item.get("name") if isinstance(item, dict) else item).replace("self.", "")
            for item in state_fields
        }
        node_inputs_by_step = {
            s["step_number"]: set(s.get("node_inputs", []))
            for s in step_summaries
        }

        def _validate(candidate, raw):
            if not (isinstance(candidate, dict) and isinstance(candidate.get("connections"), list)):
                return candidate, ["expected a JSON object containing a connections list"]
            validation_errors = []
            for index, conn in enumerate(candidate["connections"]):
                label = f"connections[{index}]"
                if not isinstance(conn, dict):
                    validation_errors.append(f"{label} must be an object")
                    continue
                from_step = _int_or_none(conn.get("from_step"))
                to_step = _int_or_none(conn.get("to_step"))
                if from_step not in valid_step_numbers or to_step not in valid_step_numbers:
                    validation_errors.append(f"{label} references an unknown step")
                elif from_step >= to_step:
                    validation_errors.append(f"{label} must connect an earlier step to a later step")
                if conn.get("type") not in ("state_field", "output_node", "scene_state"):
                    validation_errors.append(f"{label} has an invalid type")
                field = _text_or_empty(conn.get("field")).replace("self.", "")
                if conn.get("type") == "state_field" and field not in state_field_names:
                    validation_errors.append(f"{label} references an unknown state field")
                # Lenient grounding for node dataflow: when an output_node names a
                # consumer parameter, it must be one of that step's known method
                # node inputs (only enforced when we have the method signatures).
                if conn.get("type") == "output_node":
                    to_param = _text_or_empty(conn.get("to_param"))
                    known_inputs = node_inputs_by_step.get(to_step, set())
                    if to_param and known_inputs and to_param not in known_inputs:
                        validation_errors.append(
                            f"{label} to_param {to_param!r} is not a node input parameter "
                            f"of step {to_step} (expected one of {sorted(known_inputs)})"
                        )
            return candidate, validation_errors

        result = self._call_llm_structured(
            prompt=prompt,
            validator=_validate,
            call_class="contract",
            failure_label="Contract-phase LLM cross-stage mapping",
        )

        # ── deterministic verification + closure against AST ground truth ──
        # state_field connections are fully checkable: the writer/reader pair
        # must exist in the AST-derived state access sets (logic analysis uses
        # the AST method universe). Unverifiable claims are dropped; missing
        # connections (an AST read of a field some earlier step writes) are
        # added deterministically. This bounds connection-count variance by
        # construction — the LLM's remaining latitude is output_node and
        # scene_state semantics.
        def _norm_field(name: str) -> str:
            name = _text_or_empty(name)
            if not name:
                return ""
            return name if name.startswith("self.") else f"self.{name}"

        reads_by_step = {
            s["step_number"]: {_norm_field(f) for f in s.get("state_reads", [])}
            for s in step_summaries
        }
        writes_by_step = {
            s["step_number"]: {_norm_field(f) for f in s.get("state_writes", [])}
            for s in step_summaries
        }

        verified_connections = []
        dropped_connections = []
        for conn in (result.get("connections") if isinstance(result, dict) else None) or []:
            if conn.get("type") != "state_field":
                verified_connections.append(conn)
                continue
            from_step = _int_or_none(conn.get("from_step"))
            to_step = _int_or_none(conn.get("to_step"))
            field = _norm_field(conn.get("field"))
            if (
                field
                and field in writes_by_step.get(from_step, set())
                and field in reads_by_step.get(to_step, set())
            ):
                verified_connections.append(conn)
            else:
                dropped_connections.append(conn)

        existing = {
            (
                _int_or_none(conn.get("from_step")),
                _int_or_none(conn.get("to_step")),
                _norm_field(conn.get("field")),
            )
            for conn in verified_connections
            if conn.get("type") == "state_field"
        }
        closure_added = []
        for to_step in sorted(reads_by_step):
            for field in sorted(reads_by_step[to_step]):
                writers = [
                    s for s in writes_by_step
                    if s < to_step and field in writes_by_step[s]
                ]
                if not writers:
                    continue
                from_step = max(writers)  # nearest earlier writer
                if (from_step, to_step, field) in existing:
                    continue
                connection = {
                    "from_step": from_step,
                    "to_step": to_step,
                    "type": "state_field",
                    "field": field,
                    "description": (
                        f"Deterministic closure: AST shows step {from_step} writes "
                        f"{field} and step {to_step} reads it"
                    ),
                    "provenance": "ast_closure",
                }
                verified_connections.append(connection)
                closure_added.append(connection)
                existing.add((from_step, to_step, field))

        if dropped_connections or closure_added:
            logger.info(
                "[cross-stage] AST verification dropped %d unverifiable state_field "
                "connection(s) and added %d by deterministic closure",
                len(dropped_connections), len(closure_added),
            )
            self.on_progress(
                "contract", "Build Workflow Contract",
                f"AST verification: -{len(dropped_connections)} unverifiable, "
                f"+{len(closure_added)} closure connection(s)",
            )
        if isinstance(result, dict):
            result["connections"] = verified_connections
            if dropped_connections:
                result["dropped_connections"] = dropped_connections

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
                field_key = field.replace("self.", "") if field else ""
                # The CONSUMER key (what the downstream step reads under) and the
                # PRODUCER source (what the upstream step stored under) may differ
                # — e.g. a user_choice node 'orbitLandmarksNode' feeding a logic
                # method parameter 'source_lm_node'. to_param/from_param carry the
                # two names; fall back to the shared field for state_field edges.
                to_param = _text_or_empty(conn.get("to_param"))
                from_param = _text_or_empty(conn.get("from_param"))
                param_key = to_param or field_key or f"step_{from_idx + 1}_output"
                source_param = from_param or field_key or param_key

                stage_map_entry = cross_map.setdefault(to_idx, {})
                stage_map_entry[param_key] = {
                    "source_stage": from_idx,
                    "source_param": source_param,
                    "type": conn_type,
                    "description": desc,
                }

            self.on_progress(
                "contract", "Build Workflow Contract",
                f"LLM identified {len(result['connections'])} cross-stage connections"
            )
            return cross_map

        raise RuntimeError("Contract-phase LLM cross-stage mapping returned invalid structure")

    # ================================================================
    # Node Lifecycle Analysis (folded into generate)
    # ================================================================

    def _compute_node_lifecycle(self, scan_result: Dict, logic_analysis: Dict) -> Dict:
        """Compute node creation mode and param role for each vtkMRML parameter.

        This is an AST-based analysis (no LLM unless AST finds nothing) used
        internally by code template generation (generate).
        """
        return self._stage4_node_lifecycle(scan_result, logic_analysis)

    def _classify_placement_starter_methods(self, logic_analysis: Dict) -> Dict[str, Dict]:
        """Detect extension methods that create a markup and enter placement mode.

        These methods correspond to UI actions that create interaction nodes
        and enter placement mode. The generated workflow should call them in the
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
                "[generate] Detected placement-starter methods: %s",
                ", ".join(sorted(starters)),
            )
            self.on_progress(
                "generate", "Generate Schemas And Templates",
                f"Detected {len(starters)} placement-starter method(s)"
            )
        return starters

    # ================================================================
    # Internal LLM Review of Templates (part of generate)
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
