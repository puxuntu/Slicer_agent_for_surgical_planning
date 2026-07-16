from .common import *


def _resolve_qt_control_lines(widget_expr, control_name, out_var="_ctrl", indent=""):
    """Emit Python source lines that resolve a Qt control by name and leave it
    in ``out_var`` (or None).

    Slicer extensions expose their controls in different ways: loaded from a Qt
    Designer ``.ui`` file (``self.ui.<name>``), assigned as direct widget
    attributes (``self.<name>``), or reachable only by objectName in the widget
    tree. The old generator hardcoded ``_widget.ui.<name>`` which silently
    fails (AttributeError swallowed) for extensions that use direct attributes,
    leaving the control state unset — so a later ``setChecked(opposite)`` in an
    "Update"/"Fix" handler emits no ``toggled`` signal and dependent UI (e.g.
    3D interaction handles) never updates. This resolver is general: it tries
    all three exposure styles and hardcodes nothing beyond the passed-in name.
    """
    q = repr(control_name)
    i = indent
    return [
        f"{i}{out_var} = None",
        f"{i}_ui = getattr({widget_expr}, 'ui', None)",
        f"{i}if _ui is not None:",
        f"{i}    {out_var} = getattr(_ui, {q}, None)",
        f"{i}if {out_var} is None:",
        f"{i}    {out_var} = getattr({widget_expr}, {q}, None)",
        f"{i}if {out_var} is None:",
        f"{i}    try:",
        f"{i}        _found = slicer.util.findChildren({widget_expr}, name={q})",
        f"{i}        {out_var} = _found[0] if _found else None",
        f"{i}    except Exception:",
        f"{i}        {out_var} = None",
    ]


class AnalyzerWorkflowTemplatesMixin:
    def _generate_workflow_templates(
        self,
        extension_name: str,
        workflow_graph: Dict,
        scan_result: Dict,
        logic_analysis: Dict,
    ) -> Dict[str, str]:
        """
        Generate split templates for interactive workflow steps.

        For interactive steps: generates pre-interaction (node creation, placement mode)
        and post-interaction (validation, processing) templates.
        For automated steps: generates a single code template.
        Also generates the workflow.json file.
        """
        steps = workflow_graph.get("steps", [])
        templates = {}
        logic_class_name = scan_result.get("logic_class", {}).get("class_name", "")
        entry_module = scan_result.get("entry_module", "")
        module_name = os.path.splitext(os.path.basename(entry_module))[0] if entry_module else extension_name

        def _matching_slicer_template_items(step_id: str) -> List[Tuple[str, str]]:
            matches = []
            prefix = f"{step_id}_"
            for tpl_key, tpl_code in self._slicer_op_templates.items():
                if tpl_key == step_id or tpl_key.startswith(prefix):
                    matches.append((tpl_key, tpl_code))
            matches.sort(key=lambda item: item[0])
            return matches

        def _matching_slicer_templates(step_id: str) -> List[str]:
            return [code for _, code in _matching_slicer_template_items(step_id)]

        def _attach_slicer_evidence(step: Dict, template_file: str, source_keys: List[str]):
            evidence_items = [
                self._slicer_op_evidence.get(key, {})
                for key in source_keys
                if self._slicer_op_evidence.get(key)
            ]
            if not evidence_items:
                return
            merged = self._merge_api_evidence(evidence_items)
            step["api_evidence"] = merged
            if isinstance(self._workflow_metadata, dict):
                self._workflow_metadata.setdefault("api_evidence", {})[template_file] = merged

        for step_index, step in enumerate(steps):
            step_id = step["step_id"]
            op_type = _operation_type_for_step(step)
            step["operation_type"] = op_type
            step["op_type"] = op_type
            step.setdefault("step_type", op_type)
            step_type = _legacy_step_type_for_operation(op_type)

            if self._parameter_update_ops_for_step(step):
                key = f"templates/{step_id}.py.tpl"
                step["code_template"] = key
                templates[key] = self._generate_parameter_update_template(
                    extension_name, step, logic_class_name, module_name,
                )

            elif step_type == "automated" and op_type == "slicer_op":
                # Slicer_op templates are pre-generated in the ground phase.
                key = f"templates/{step_id}_slicer.py.tpl"
                step["code_template"] = key
                pregen_items = _matching_slicer_template_items(step_id)
                if pregen_items:
                    templates[key] = "\n\n".join(code for _, code in pregen_items)
                    _attach_slicer_evidence(step, key, [item_key for item_key, _ in pregen_items])
                else:
                    # Fallback: generate via LLM with generic slicer prompt
                    templates[key] = self._generate_slicer_fallback_template(step)

            elif step_type == "automated" and op_type == "mixed":
                # Automated step with mixed sub-operations: compose ALL sub-ops
                # (extension_op + slicer_op) into a single template.
                sub_ops = step.get("sub_operations", [])
                auto_parts = []
                # Consume ground-phase templates once for the whole step.
                consumed_5t = False
                for so in sub_ops:
                    if so.get("operation_intent") == "extension_parameter_update":
                        ext_step = dict(step)
                        ext_step["sub_operations"] = [so]
                        auto_parts.append(
                            f"# Extension parameter update: {so.get('description', '')}\n"
                            + self._generate_parameter_update_template(
                                extension_name, ext_step, logic_class_name, module_name,
                            )
                        )
                    elif so["op_type"] == "extension_op" and so.get("extension_method_hint"):
                        ext_step = dict(step)
                        ext_step["method_name"] = so["extension_method_hint"]
                        ext_step["description"] = so["description"]
                        if so["extension_method_hint"] in self._placement_starter_methods:
                            ext_tpl = self._generate_placement_starter_pre_template(
                                extension_name, ext_step, logic_class_name, module_name,
                            )
                        else:
                            ext_tpl = self._generate_automated_workflow_template(
                                extension_name, ext_step, logic_class_name, module_name,
                                logic_analysis,
                            )
                        auto_parts.append(f"# Extension op: {so['description']}\n{ext_tpl}")
                    elif so["op_type"] == "slicer_op":
                        if not consumed_5t:
                            pregen_items = _matching_slicer_template_items(step_id)
                            if pregen_items:
                                auto_parts.append(
                                    "# Slicer ops (ground phase)\n"
                                    + "\n\n".join(code for _, code in pregen_items)
                                )
                                _attach_slicer_evidence(
                                    step,
                                    f"templates/{step_id}.py.tpl",
                                    [item_key for item_key, _ in pregen_items],
                                )
                            else:
                                so_keywords = so.get("slicer_api_keywords", [])
                                so_desc = so.get("description", "")
                                llm_code = self._generate_slicer_api_template_llm(
                                    step_id, so_desc, so_keywords,
                                )
                                if llm_code:
                                    auto_parts.append(f"# Slicer op: {so_desc}\n{llm_code}")
                                else:
                                    auto_parts.append(f"# Slicer op: {so_desc}\n# TODO: generate slicer code\npass")
                            consumed_5t = True
                    elif so["op_type"] in ("extension_op", "unknown_op") and not so.get("extension_method_hint"):
                        if so.get("extension_function_hint"):
                            ext_step = dict(step)
                            ext_step["extension_function_name"] = so["extension_function_hint"]
                            ext_step["description"] = so.get("description", step.get("description", ""))
                            auto_parts.append(
                                f"# Extension function op: {so['description']}\n"
                                + self._generate_extension_function_template(
                                    extension_name, ext_step, module_name,
                                )
                            )
                            continue
                        # No method hint — generate targeted code for this sub-op only.
                        so_desc = so.get("description", "")
                        so_keywords = so.get("slicer_api_keywords", [])
                        category = so.get("slicer_op_category")
                        if category or so_keywords:
                            llm_code = self._generate_slicer_api_template_llm(
                                step_id, so_desc, so_keywords,
                            )
                            if llm_code:
                                auto_parts.append(f"# Auto op: {so_desc}\n{llm_code}")
                            else:
                                auto_parts.append(
                                    f"# Auto op: {so_desc}\n"
                                    f"# TODO: implement this operation\npass"
                                )
                key = f"templates/{step_id}.py.tpl"
                templates[key] = "\n\n".join(auto_parts) if auto_parts else "# No sub-operations\npass"
                step["code_template"] = key

            elif step_type == "automated":
                # Single code template for automated steps.
                # A button-click step (cookbook "Click the X button") whose widget
                # drives a connected handler IS that handler -- prefer it over a
                # module-function / logic-method match the LLM may have proposed
                # (e.g. "Apply adjustments" -> _widget.onApplyAdjust(), not the
                # unrelated module helper Apply_transform_to_polydata). Returns None
                # when no captured button-handler connection exists -> falls through.
                tpl = self._maybe_generate_button_handler_template(
                    extension_name, step, logic_class_name, module_name,
                )
                if tpl is not None:
                    pass
                elif step.get("extension_function_name"):
                    tpl = self._generate_extension_function_template(
                        extension_name, step, module_name,
                    )
                elif step.get("method_name") in self._placement_starter_methods:
                    step["interaction_owner"] = "extension_method"
                    step["placement_starter_method"] = step.get("method_name")
                    step["created_node_source"] = "extension_method"
                    tpl = self._generate_placement_starter_pre_template(
                        extension_name, step, logic_class_name, module_name,
                    )
                else:
                    # Scoped re-entry reuse: this is the one branch whose
                    # template is a single LLM generation, so an unchanged,
                    # unimplicated step can keep its prior template verbatim.
                    tpl = self._prev_template_for_reuse(
                        f"templates/{step_id}.py.tpl", step
                    )
                    if tpl is None:
                        tpl = self._generate_automated_workflow_template(
                            extension_name, step, logic_class_name, module_name, logic_analysis,
                        )
                templates[f"templates/{step_id}.py.tpl"] = tpl
                step["code_template"] = f"templates/{step_id}.py.tpl"

            elif step_type == "interactive":
                node_class = step.get("node_class", "")
                # Revision A: dispatch on interaction_kind (semantic intent)
                # rather than node_class (data shape). Previously the guard
                # `bool(node_class) and not _is_markup_node_class(node_class)`
                # required a non-empty node_class to reach the view-adjustment
                # branch, so view_adjustment steps with empty node_class fell
                # into _generate_pre_interaction_template which always creates
                # a Markups node and enters placement mode — hijacking the
                # mouse for any drag-existing-handle or viewport-adjustment
                # interaction.
                interaction_kind = (step.get("interaction_kind") or "").strip()
                # Infer interaction_kind conservatively from node_class when
                # Stage 4 didn't set it (preserves legacy behavior for steps
                # classified before Revision B's descriptor enrichment).
                if not interaction_kind:
                    if self._is_markup_node_class(node_class):
                        interaction_kind = "markup_placement"
                    elif node_class:
                        interaction_kind = "view_adjustment"
                    step["interaction_kind"] = interaction_kind

                starter_binding = self._find_recent_placement_starter_for_interaction(
                    steps, step_index
                )
                prev_starter_method = (
                    step.get("placement_starter_method")
                    or starter_binding.get("method")
                )
                if prev_starter_method and interaction_kind == "markup_placement":
                    step["interaction_owner"] = "previous_extension_method"
                    step["placement_starter_method"] = prev_starter_method
                    step["created_node_source"] = "previous_extension_method"
                    if starter_binding:
                        step["placement_starter_step_id"] = starter_binding.get("step_id", "")
                        step["placement_binding_reason"] = starter_binding.get("reason", "")

                is_view_adjustment = interaction_kind == "view_adjustment"
                # An in-tool interaction: the user drives an already-active module
                # tool/effect (e.g. a Segment Editor island click) that consumes the
                # view clicks itself — node-less, no place mode, like view_adjustment
                # but with a tool re-bind and interaction-affirming instruction text.
                is_module_tool = interaction_kind == "module_tool_interaction"

                # A draw/place step whose Stage-4 contract says it does NOT
                # create its own node (creates_node is False) is operating on a
                # markup a co-located earlier step already created — it must
                # REUSE that node, not add a duplicate. Generic: keys only on the
                # semantic descriptor (creates_node) + the node being a Markups
                # class, never on step identity. The reused node keeps its
                # concrete subclass (e.g. a closed curve stays closed, since
                # GetNodesByClass matches by IsA), so the drawn markup matches
                # whatever the create step made — fixing both the wrong-class and
                # the duplicate-node failure modes at once.
                reuse_existing_markup = (
                    interaction_kind == "markup_placement"
                    and not prev_starter_method
                    and step.get("creates_node") is False
                    and self._is_markup_node_class(node_class)
                )
                if reuse_existing_markup:
                    step["interaction_owner"] = "runtime_template"
                    step["created_node_source"] = "previous_step"

                # Pre-interaction template
                if interaction_kind == "markup_placement" and prev_starter_method:
                    pre_tpl = self._generate_existing_placement_pre_template(
                        extension_name, step, prev_starter_method,
                    )
                elif reuse_existing_markup:
                    pre_tpl = self._generate_existing_placement_pre_template(
                        extension_name, step, "",
                    )
                elif is_module_tool:
                    pre_tpl = self._generate_module_tool_interaction_pre_template(
                        extension_name, step,
                    )
                elif is_view_adjustment:
                    pre_tpl = self._generate_view_adjustment_pre_template(
                        extension_name, step,
                    )
                else:
                    # markup_placement without prev_starter_method, or
                    # unknown/missing interaction_kind falling back to the
                    # legacy markups-creation default.
                    if interaction_kind == "markup_placement" or not interaction_kind:
                        if self._is_markup_node_class(node_class) or not node_class:
                            step.setdefault("interaction_owner", "runtime_template")
                            step.setdefault("created_node_source", "template")
                    pre_tpl = self._generate_pre_interaction_template(
                        extension_name, step, logic_class_name, module_name,
                    )
                templates[f"templates/{step_id}_pre.py.tpl"] = pre_tpl
                step["pre_template"] = f"templates/{step_id}_pre.py.tpl"

                # Post-interaction template — mirror the same dispatch.
                if is_module_tool:
                    post_tpl = self._generate_module_tool_interaction_post_template(
                        extension_name, step,
                    )
                elif is_view_adjustment:
                    post_tpl = self._generate_view_adjustment_post_template(
                        extension_name, step,
                    )
                else:
                    post_tpl = self._generate_post_interaction_template(
                        extension_name, step, logic_class_name, module_name, logic_analysis,
                    )
                templates[f"templates/{step_id}_post.py.tpl"] = post_tpl
                step["post_template"] = f"templates/{step_id}_post.py.tpl"

            elif step_type == "mixed":
                # Mixed step: pre_template contains all automated sub-ops,
                # then user interaction follows.
                sub_ops = step.get("sub_operations", [])
                auto_parts = []
                placement_starter_method = None
                slicer_templates_appended = False
                pre_key = f"templates/{step_id}_pre.py.tpl"
                for so in sub_ops:
                    if so.get("operation_intent") == "extension_parameter_update":
                        ext_step = dict(step)
                        ext_step["sub_operations"] = [so]
                        auto_parts.append(
                            f"# Extension parameter update: {so.get('description', '')}\n"
                            + self._generate_parameter_update_template(
                                extension_name, ext_step, logic_class_name, module_name,
                            )
                        )
                    elif so["op_type"] == "extension_op" and so.get("extension_method_hint"):
                        # Generate extension_op code
                        ext_step = dict(step)
                        ext_step["method_name"] = so["extension_method_hint"]
                        ext_step["description"] = so["description"]
                        if so["extension_method_hint"] in self._placement_starter_methods:
                            placement_starter_method = so["extension_method_hint"]
                            step["interaction_owner"] = "extension_method"
                            step["placement_starter_method"] = placement_starter_method
                            step["created_node_source"] = "extension_method"
                            ext_tpl = self._generate_placement_starter_pre_template(
                                extension_name, ext_step, logic_class_name, module_name,
                            )
                        else:
                            ext_tpl = self._generate_automated_workflow_template(
                                extension_name, ext_step, logic_class_name, module_name,
                                logic_analysis,
                            )
                        auto_parts.append(f"# Extension op: {so['description']}\n{ext_tpl}")
                    elif so["op_type"] == "extension_op" and so.get("extension_function_hint"):
                        ext_step = dict(step)
                        ext_step["extension_function_name"] = so["extension_function_hint"]
                        ext_step["description"] = so.get("description", step.get("description", ""))
                        auto_parts.append(
                            f"# Extension function op: {so['description']}\n"
                            + self._generate_extension_function_template(
                                extension_name, ext_step, module_name,
                            )
                        )
                    elif so["op_type"] == "slicer_op":
                        # Use pre-generated slicer_op template
                        if slicer_templates_appended:
                            continue
                        pregen_parts = _matching_slicer_templates(step_id)
                        if pregen_parts:
                            auto_parts.append(
                                f"# Slicer op: {so['description']}\n"
                                + "\n\n".join(pregen_parts)
                            )
                            _attach_slicer_evidence(
                                step,
                                pre_key,
                                [item_key for item_key, _ in _matching_slicer_template_items(step_id)],
                            )
                            slicer_templates_appended = True
                        else:
                            # No pre-generated template — try LLM with keywords
                            so_keywords = so.get("slicer_api_keywords", [])
                            so_desc = so.get("description", "")
                            llm_code = self._generate_slicer_api_template_llm(
                                step_id, so_desc, so_keywords,
                            )
                            if llm_code:
                                auto_parts.append(f"# Slicer op: {so_desc}\n{llm_code}")
                            else:
                                auto_parts.append(f"# Slicer op: {so_desc}\n# TODO: generate slicer code\npass")

                step["pre_template"] = pre_key

                # Append node creation + ID storage for the interaction sub-op
                # so the post-template can retrieve the node.
                interaction_sub_ops = [
                    so for so in sub_ops if so.get("op_type") == "user_interaction"
                ]
                if interaction_sub_ops:
                    iso = interaction_sub_ops[0]
                    node_class = iso.get("node_class") or step.get("node_class", "")
                    # Revision A (mixed-step mirror): dispatch on interaction_kind
                    # rather than requiring a non-empty node_class. Same fix as
                    # the interactive branch above.
                    interaction_kind = (iso.get("interaction_kind") or step.get("interaction_kind") or "").strip()
                    if not interaction_kind:
                        if self._is_markup_node_class(node_class):
                            interaction_kind = "markup_placement"
                        elif node_class:
                            interaction_kind = "view_adjustment"
                        step["interaction_kind"] = interaction_kind

                    is_view_adjustment = interaction_kind == "view_adjustment"
                    is_markup_placement = interaction_kind == "markup_placement"
                    is_module_tool = interaction_kind == "module_tool_interaction"

                    if (
                        is_markup_placement
                        and node_class
                        and self._is_markup_node_class(node_class)
                        and not placement_starter_method
                    ):
                        step["interaction_owner"] = "runtime_template"
                        step["created_node_source"] = "template"
                        node_name = step_id.replace("_", " ").title()
                        node_var = f"_{extension_name.lower()}_{step_id}_id"
                        instructions = self._interaction_instructions_for_template(step)
                        policy = self._placement_mode_policy(step)
                        block_lines = [
                            "",
                            "",
                            "# --- Setup interaction node ---",
                            "import slicer",
                            "from SlicerAIAgentLib.workflow_state import remember_interaction_node",
                            f"node = slicer.mrmlScene.AddNewNodeByClass(\"{node_class}\", \"{node_name}\")",
                            "displayNode = node.GetDisplayNode()",
                            "if displayNode is not None:",
                            "    displayNode.SetVisibility(True)",
                        ]
                        if policy.get("should_set_active_list"):
                            block_lines.append("slicer.modules.markups.logic().SetActiveListID(node)")
                        if policy.get("should_enter_placement_mode"):
                            block_lines.extend([
                                "interactionNode = slicer.mrmlScene.GetNodeByID(\"vtkMRMLInteractionNodeSingleton\")",
                                "if interactionNode is not None:",
                                *self._placement_mode_code(policy),
                            ])
                        block_lines.extend([
                            f"{node_var} = node.GetID()",
                            (
                                "remember_interaction_node("
                                f"_workflow_runtime_extension, _workflow_runtime_id, \"{step_id}\", "
                                f"{node_var}, _workflow_runtime_repeat_index)"
                            ),
                            f"print(\"[{extension_name}] Please {instructions}\")",
                        ])
                        interaction_block = "\n".join(block_lines)
                        auto_parts.append(interaction_block)
                    elif is_module_tool:
                        step["interaction_kind"] = "module_tool_interaction"
                        # Ensure the module_context propagates to the interaction
                        # descriptor so the pre-template can re-bind the active tool.
                        if not step.get("module_context"):
                            step["module_context"] = iso.get("module_context", "")
                        auto_parts.append(
                            "\n\n# --- In-tool interaction (active module tool consumes the clicks) ---\n"
                            + self._generate_module_tool_interaction_pre_template(
                                extension_name, step,
                            )
                        )
                    elif is_view_adjustment:
                        step["interaction_kind"] = "view_adjustment"
                        instructions = iso.get(
                            "placement_instructions",
                            step.get("description", ""),
                        )
                        instructions = self._sanitize_interaction_instruction(
                            instructions,
                            fallback=step.get("description", ""),
                        )
                        auto_parts.append(
                            "\n\n# --- View adjustment interaction ---\n"
                            f"print(\"[{extension_name}] Please {instructions}\")\n"
                            "print(\"When finished, press the 'Done' button in the workflow panel.\")\n"
                        )

                templates[pre_key] = (
                    "\n\n".join(auto_parts) if auto_parts
                    else "# No automated sub-operations\npass"
                )

                # Post-interaction template for the user_interaction part
                post_key = f"templates/{step_id}_post.py.tpl"
                step["post_template"] = post_key
                mixed_interaction_kind = (
                    (interaction_sub_ops[0].get("interaction_kind") if interaction_sub_ops else "")
                    or step.get("interaction_kind", "")
                )
                if placement_starter_method:
                    templates[post_key] = self._generate_placement_starter_post_template(
                        extension_name, step, placement_starter_method,
                    )
                elif mixed_interaction_kind == "module_tool_interaction":
                    templates[post_key] = self._generate_module_tool_interaction_post_template(
                        extension_name, step,
                    )
                elif interaction_sub_ops and not self._is_markup_node_class(
                    interaction_sub_ops[0].get("node_class") or step.get("node_class", "")
                ):
                    templates[post_key] = self._generate_view_adjustment_post_template(
                        extension_name, step,
                    )
                else:
                    templates[post_key] = self._generate_post_interaction_template(
                        extension_name, step, logic_class_name, module_name, logic_analysis,
                    )

            elif step_type == "branch":
                # Branch steps don't need templates — handled by the orchestrator
                pass

            elif op_type == "branch_op":
                # A branch_op presents the decision like a user_choice (no
                # decision template), but ALSO performs an extension action on
                # ACCEPT (e.g. tick a checkbox that enables an optional mode).
                # Generate that action as a per-step template; the runtime
                # injects it only when the user accepts. If no widget/handler is
                # captured, degrade to a plain pre-guard branch (no action).
                action_tpl = self._maybe_generate_button_handler_template(
                    extension_name, step, logic_class_name, module_name,
                )
                if action_tpl:
                    action_key = f"templates/{step_id}_action.py.tpl"
                    templates[action_key] = action_tpl
                    step["branch_action_template"] = action_key

            elif step_type == "user_choice":
                # user_choice steps don't need code templates — handled by the
                # orchestrator which presents the question and collects the answer.
                pass

        # Post-generation consistency check: verify pre/post templates agree
        # on node ID variables (_ext_step_id).
        consistency_fixes = 0
        for step in steps:
            exec_type = _legacy_step_type_for_operation(_operation_type_for_step(step))
            if exec_type != "interactive":
                continue
            s_id = step["step_id"]
            node_var = f"_{extension_name.lower()}_{s_id}_id"

            # Check post-template references the var
            post_key = step.get("post_template", "")
            if not post_key or post_key not in templates:
                continue
            if node_var not in templates[post_key]:
                continue

            # Verify pre-template defines it
            pre_key = step.get("pre_template", "")
            if not pre_key or pre_key not in templates:
                continue
            if node_var in templates[pre_key]:
                continue

            # Missing — inject node ID storage at end of pre-template.
            # Only inject when node_class is set (a markup node was created).
            # For steps with empty node_class (e.g. slice crosshair adjustment),
            # no node exists to store — skip injection.
            node_class = step.get("node_class", "")
            if not node_class:
                continue
            injection = (
                f"\n# [Auto-injected] Store node ID for post-step\n"
                f"try:\n"
                f"    {node_var} = node.GetID()\n"
                f"except NameError:\n"
                f"    {node_var} = ''\n"
            )
            templates[pre_key] = templates[pre_key].rstrip() + "\n" + injection
            consistency_fixes += 1
            logger.info(
                "[generate] Injected missing node ID '%s' into %s",
                node_var, pre_key,
            )

        if consistency_fixes:
            logger.info(
                "[generate] Fixed %d pre/post node ID consistency issues",
                consistency_fixes,
            )

        # Core-module session threading: cookbook steps "In the 'X' module, ..."
        # form coherent multi-step sessions (e.g. Segment Editor: create -> add ->
        # activate -> apply). Each slicer_op is grounded in ISOLATION, losing the
        # module's shared, stateful workflow (which segmentation, which SELECTED
        # segment, one editor node), which yields duplicate / mis-targeted objects
        # (e.g. Threshold "Apply" writing into a materialized 'Segment_1' instead of
        # the segment "Add segment" created). Each registered per-module session
        # driver wraps the module's step templates with deterministic, CodeValidator-
        # safe preamble/postamble that threads that state via MRML node attributes.
        # Subsumes the former Segment-Editor crash-preventer (binding still happens).
        session_fixes = self._apply_module_session_drivers(templates, steps)
        if session_fixes:
            logger.info(
                "[generate] Applied core-module session drivers to %d template(s)",
                session_fixes,
            )

        # Store workflow graph as JSON template (only valid steps)
        valid_types = CANONICAL_OPERATION_TYPES
        clean_graph = {k: v for k, v in workflow_graph.items() if k != "steps"}
        clean_graph["steps"] = [
            s for s in steps
            if _operation_type_for_step(s) in valid_types
        ]
        templates["workflow.json"] = json.dumps(clean_graph, indent=2)
        templates["workflow_metadata.json"] = json.dumps(self._workflow_metadata or {}, indent=2)

        self._phase_progress(
            "generate",
            f"Generated {len(templates)} workflow templates",
            "Generate Schemas And Templates",
        )
        return templates

    @staticmethod
    def _parameter_update_ops_for_step(step: Dict) -> List[Dict]:
        operations = list(step.get("sub_operations") or [])
        operations.extend(step.get("atomic_operations") or [])
        return [
            so for so in operations
            if so.get("operation_intent") in (
                "extension_parameter_update",
                "extension_node_reference_update",
            )
            and so.get("parameter_name")
        ]

    @staticmethod
    def _parameter_placeholder_name(role: str) -> str:
        text = _re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", role or "")
        text = _re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
        return text or "parameter_value"

    @staticmethod
    def _placeholder_default_literal(value: Any, value_property: str) -> str:
        if value is None:
            return "0.0" if value_property == "value" else "''"
        if isinstance(value, bool):
            return "True" if value else "False"
        if isinstance(value, (int, float)):
            return repr(value)
        return repr(str(value))

    @staticmethod
    def _node_class_for_reference_role(role: str, binding: Dict[str, Any]) -> str:
        text = " ".join([
            role or "",
            (binding or {}).get("widget_name", ""),
            (binding or {}).get("ui_text", ""),
        ]).lower()
        if "segmentation" in text:
            return "vtkMRMLSegmentationNode"
        if "volume" in text:
            return "vtkMRMLScalarVolumeNode"
        if "curve" in text:
            return "vtkMRMLMarkupsCurveNode"
        if "line" in text:
            return "vtkMRMLMarkupsLineNode"
        if "plane" in text:
            return "vtkMRMLMarkupsPlaneNode"
        if "model" in text:
            return "vtkMRMLModelNode"
        return "vtkMRMLNode"

    @staticmethod
    def _node_reference_keywords(role: str, step: Dict) -> List[str]:
        text = " ".join([
            role or "",
            _text_or_empty(step.get("description", "")),
            " ".join(
                _text_or_empty(so.get("description", ""))
                for so in (step.get("sub_operations") or [])
            ),
        ]).lower()
        tokens = []
        for token in _re.findall(r"[a-z0-9]+", text):
            if len(token) < 4:
                continue
            if token in {
                "select", "choose", "current", "scalar", "volume",
                "segmentation", "node", "option", "section",
            }:
                continue
            if token not in tokens:
                tokens.append(token)
        return tokens[:5]

    def _generate_parameter_update_template(
        self,
        extension_name: str,
        step: Dict,
        logic_class_name: str,
        module_name: str,
    ) -> str:
        """Generate deterministic code for extension parameter-node UI updates."""
        step_id = step.get("step_id", "")
        ops = self._parameter_update_ops_for_step(step)
        if not ops:
            return self._generate_unknown_op_template(step)

        logic_var = f"_{extension_name.lower()}_logic"
        lines = [
            *self._template_header_lines(extension_name, step, ""),
            "import slicer",
            f"from {module_name} import {logic_class_name}",
            "",
            *self._emit_module_enter_precondition(module_name),
            "try:",
            f"    logic = {logic_var}",
            "except NameError:",
            f"    logic = {logic_class_name}()",
            f"    {logic_var} = logic",
            "",
            "parameterNode = logic.getParameterNode()",
        ]

        applier_lines: List[str] = []
        for so in ops:
            role = so.get("parameter_name", "")
            mode = so.get("target_value_mode", "")
            target = so.get("target_value")
            binding = so.get("ui_parameter_binding") or {}
            role_info = binding.get("role") or {}
            value_property = so.get("value_property") or role_info.get("value_property", "")
            if so.get("operation_intent") == "extension_node_reference_update":
                placeholder = self._parameter_placeholder_name(role)
                node_class = self._node_class_for_reference_role(role, binding)
                keywords = self._node_reference_keywords(role, step)
                # A @parameterNodeWrapper has no SetNodeReferenceID; its node
                # references are typed properties. Assign the property directly
                # when the role names a wrapper field, else use the classic API.
                wrapper_fields = set((self._parameter_node_wrapper or {}).get("fields") or {})
                if role in wrapper_fields:
                    assign_line = f"parameterNode.{role} = {placeholder}_node"
                else:
                    assign_line = (
                        f"parameterNode.SetNodeReferenceID({role!r}, {placeholder}_node.GetID())"
                    )
                lines.extend([
                    f"{placeholder}_node_name = {{{placeholder}_node_name: ''}}",
                    f"{placeholder}_node = None",
                    f"if {placeholder}_node_name:",
                    "    try:",
                    f"        {placeholder}_node = slicer.util.getNode({placeholder}_node_name)",
                    "    except Exception:",
                    "        pass",
                    f"if {placeholder}_node is None:",
                    f"    _nodes = slicer.mrmlScene.GetNodesByClass({node_class!r})",
                    f"    _keywords = {keywords!r}",
                    "    for _i in range(_nodes.GetNumberOfItems()):",
                    "        _candidate = _nodes.GetItemAsObject(_i)",
                    "        _name = (_candidate.GetName() or '').lower()",
                    "        if not _keywords or any(_kw in _name for _kw in _keywords):",
                    f"            {placeholder}_node = _candidate",
                    "            break",
                    f"if {placeholder}_node is None:",
                    f"    raise RuntimeError('Could not find node for parameter reference {role}')",
                    assign_line,
                ])
            elif target is True:
                lines.extend(self._widget_sync_lines(so, module_name, True))
                lines.append(f"parameterNode.SetParameter({role!r}, 'True')")
                applier_lines.extend(self._applier_call_lines(role, "True", module_name))
            elif target is False:
                lines.extend(self._widget_sync_lines(so, module_name, False))
                lines.append(f"parameterNode.SetParameter({role!r}, 'False')")
                applier_lines.extend(self._applier_call_lines(role, "False", module_name))
            elif mode == "invert":
                lines.extend([
                    f"_current_{role} = parameterNode.GetParameter({role!r}) == 'True'",
                    f"parameterNode.SetParameter({role!r}, 'False' if _current_{role} else 'True')",
                ])
                applier_lines.extend(self._applier_call_lines(
                    role, f"not _current_{role}", module_name
                ))
            elif value_property in ("value", "currentText", "currentIndex"):
                placeholder = self._parameter_placeholder_name(role)
                default = (binding.get("properties") or {}).get(value_property)
                default_literal = self._placeholder_default_literal(default, value_property)
                lines.append(f"{placeholder} = {{{placeholder}: {default_literal}}}")
                lines.append(f"parameterNode.SetParameter({role!r}, str({placeholder}))")
                applier_lines.extend(self._applier_call_lines(role, placeholder, module_name))
            else:
                default = (
                    role_info.get("true_value")
                )
                if default is None:
                    default = "True"
                if isinstance(default, bool):
                    default_text = "True" if default else "False"
                else:
                    default_text = str(default)
                if default_text in ("True", "False"):
                    lines.extend(self._widget_sync_lines(
                        so, module_name, default_text == "True"
                    ))
                lines.append(
                    f"# Final state was not explicit; apply source-derived/default truthy state for {role}"
                )
                lines.append(f"parameterNode.SetParameter({role!r}, {default_text!r})")
                applier_lines.extend(self._applier_call_lines(
                    role,
                    "True" if default_text == "True" else repr(default_text),
                    module_name,
                ))

        # Order matters: Modified() fires the extension's GUI observer first
        # (it recomputes any multi-parameter gates from the now-set values);
        # the evidence-backed applier calls run LAST so the explicit final
        # state always has the last word over observer recomputation.
        lines.extend([
            "try:",
            "    parameterNode.Modified()",
            "except Exception:",
            "    pass",
        ])
        lines.extend(applier_lines)
        lines.extend([
            f"{logic_var} = logic",
            f"print(\"[{extension_name}] Step '{step_id}' completed.\")",
        ])
        return "\n".join(lines) + "\n"

    @staticmethod
    def _widget_sync_lines(so: Dict, module_name: str, target: bool) -> List[str]:
        """Sync the bound UI control's checked state for boolean updates.

        Extensions often write GUI control state back into parameters on
        every sync (the ratchet: an unchecked button re-writes 'False' over a
        programmatic 'True'). Mirroring the user's actual click — setting the
        bound control's checked state — keeps GUI and parameter consistent so
        later GUI-driven syncs cannot revert the value. Evidence-backed: the
        widget name comes from the source-derived UI parameter binding.
        """
        binding = so.get("ui_parameter_binding") or {}
        widget_name = binding.get("widget_name", "")
        role_info = binding.get("role") or {}
        value_property = so.get("value_property") or role_info.get("value_property", "")
        has_checked_evidence = (
            value_property == "checked"
            or "checked" in (binding.get("properties") or {})
        )
        if not widget_name or not module_name or not has_checked_evidence:
            return []
        return [
            "# Sync the bound UI control (mirrors the user's click) so",
            "# GUI-driven parameter syncs cannot ratchet the value back.",
            "# Resolve the control across .ui / direct-attribute / widget-tree",
            "# exposure styles so this works for any extension, not only ones",
            "# that load a Qt Designer .ui file.",
            "try:",
            f"    _module_widget = slicer.modules.{module_name.lower()}.widgetRepresentation().self()",
            *_resolve_qt_control_lines("_module_widget", widget_name, "_sync_ctrl", indent="    "),
            "    if _sync_ctrl is not None:",
            f"        _sync_ctrl.checked = {target}",
            "except Exception:",
            "    pass",
        ]

    def _prev_template_for_reuse(self, key: str, step: Dict) -> Optional[str]:
        """Prior iteration's template, when scoped-re-entry reuse is sound.

        Eligible only when (a) this iteration IS a scoped upstream re-entry,
        (b) the prior iteration produced this exact template key, and (c) the
        step was neither re-derived (affected) nor named in any unresolved
        validation error (implicated). Unaffected steps' contract dicts are
        preserved verbatim by the scoped merge, so their prior templates were
        generated from identical facts — regenerating them only spends time
        and risks regression churn.
        """
        affected = getattr(self, "_reentry_affected_steps", None)
        if not affected:
            return None
        prev = getattr(self, "_prev_templates", None) or {}
        if key not in prev:
            return None
        step_numbers = {
            int(m) for m in _re.findall(r"cb_step_(\d+)", str(step.get("step_id", "")))
        }
        if not step_numbers:
            return None
        blocked = set(affected) | set(
            getattr(self, "_reentry_implicated_steps", set()) or set()
        )
        if step_numbers & blocked:
            return None
        return prev.get(key)

    def _applier_call_lines(
        self, role: str, state_expression: str, module_name: str = "",
    ) -> List[str]:
        """Emit the evidence-backed applier call for a parameter role, if any.

        A bare SetParameter only records state — the user-visible effect comes
        from the extension's own applier method (the method that reads and
        applies the parameter). Emitted only when the shared selection rule
        yields one dominant high-confidence applier; ambiguous evidence emits
        nothing (no guessing). Appliers may live on the logic class or on the
        module widget class (GUI observers commonly delegate to widget
        methods); the receiver recorded in the evidence decides the call form.
        """
        applier = self._select_unambiguous_applier(role)
        if applier is None:
            return []
        argument = state_expression if applier.get("parameter_count", 0) >= 1 else ""
        lines = [
            "# Apply the parameter via the extension's own applier method —",
            "# a bare SetParameter only records state; GUI observers may",
            "# recompute it differently.",
        ]
        if applier.get("receiver") == "module_widget" and module_name:
            lines.extend([
                f"_module_widget = slicer.modules.{module_name.lower()}.widgetRepresentation().self()",
                f"_module_widget.{applier['method']}({argument})",
            ])
        else:
            lines.append(f"logic.{applier['method']}({argument})")
        return lines

    def _generate_extension_function_template(
        self, extension_name: str, step: Dict, module_name: str,
    ) -> str:
        """Generate deterministic code for an extension-owned module function."""
        function_name = step.get("extension_function_name", "")
        step_id = step.get("step_id", "")
        if not function_name:
            return self._generate_unknown_op_template(step)
        lines = [
            *self._template_header_lines(extension_name, step, ""),
            "import slicer",
            f"from {module_name} import {function_name}",
            "",
            *self._emit_module_enter_precondition(module_name),
            f"{function_name}()",
            "",
            f"print(\"[{extension_name}] Step '{step_id}' completed.\")",
        ]
        return "\n".join(lines) + "\n"

    def _maybe_generate_button_handler_template(
        self, extension_name, step, logic_class_name, module_name,
    ) -> Optional[str]:
        """Drive the widget's connected handler for a button-click or checkbox step.

        A cookbook "Click the X button" / "Tick the Y checkbox" step's real unit
        of work is the widget handler (e.g. ``onInitialRegistrationPushButton`` /
        ``onInteractionTransform``): it reads the selected nodes, CREATES the
        output nodes downstream steps consume, and toggles dependent UI. A
        low-level logic call does neither, and an LLM left to guess invents wrong
        APIs (e.g. a destructive ``writeParameterDict`` with the wrong arity).
        When the step's widget maps to a clicked OR toggled handler in the scanned
        widget connections, emit a deterministic template that drives it on the
        live module widget. Returns None when there is no such connection (the
        caller falls back to its normal generation).
        """
        # Resolve the widget's connected handler FIRST, then decide (below) whether
        # to drive it. A step's widget_name (e.g. "loadButton") is matched against
        # the class-wide scanned widget connections to its clicked/toggled handler
        # (e.g. onLoadSkull).
        connections = getattr(self, "_widget_connections", None) or []
        if not connections:
            return None
        # widget_name -> target_value (target_value matters only for a toggle).
        widget_targets = {}
        for so in step.get("sub_operations", []) or []:
            if isinstance(so, dict) and so.get("widget_name"):
                widget_targets.setdefault(so["widget_name"], so.get("target_value"))
        if step.get("widget_name"):
            widget_targets.setdefault(step["widget_name"], step.get("target_value"))
        if not widget_targets:
            return None

        _TOGGLE = ("toggled", "stateChanged", "checkBoxToggled")
        handler = widget = None
        is_toggle = False
        shares_state = False
        for conn in connections:
            sig = str(conn.get("signal", ""))
            wn = conn.get("button_widget_name")
            if wn not in widget_targets or not conn.get("handler_method"):
                continue
            if "clicked" in sig:
                handler, widget, is_toggle = conn["handler_method"], wn, False
                shares_state = bool(conn.get("shares_widget_state"))
                break
            if any(s in sig for s in _TOGGLE):
                handler, widget, is_toggle = conn["handler_method"], wn, True
                shares_state = bool(conn.get("shares_widget_state"))
                break
        if not handler:
            return None
        # Paradigm gate (applied AFTER the connection is resolved). Drive the
        # handler when it SHARES `self.<attr>` widget state with another handler
        # (a handler-state chain, e.g. onLoadSkull sets self.resultSeg that a later
        # onAddRoi/onCutDefect reads — see scan._handler_state_chain): that widget
        # state cannot be reproduced by a low-level logic reimplementation, which
        # leaves it None (the later handler crashes) and reads uncached globals.
        # Otherwise fall back to the proven logic-method path for a CLASSIC
        # extension with a resolvable logic method — the original caution: driving
        # a bare handler bypasses the cross-stage param-node reference plumbing the
        # logic-method template binds (e.g. BRP centerFibulaLine reads a fibulaLine
        # reference via the param node, NOT shared self-state), giving None at
        # runtime. Wrapper extensions and UI-only toggles keep driving the handler.
        if not shares_state:
            is_wrapper = bool(getattr(self, "_parameter_node_wrapper", None))
            has_logic_method = bool(step.get("method_name")) or any(
                isinstance(so, dict)
                and (so.get("extension_method_hint") or so.get("extension_function_hint"))
                for so in step.get("sub_operations", []) or []
            )
            if not is_wrapper and has_logic_method:
                return None
        step_id = step.get("step_id", "")
        mod_attr = module_name.lower()
        lines = list(self._template_header_lines(extension_name, step, "")) + [
            "import slicer",
            *self._emit_module_enter_precondition(module_name),
            "# Drive the extension's own widget handler on the live module widget:",
            "# it performs the full action (reads selected nodes, creates the",
            "# output nodes downstream steps depend on, toggles dependent UI).",
            "_widget = None",
            "try:",
            f"    _widget = slicer.util.getModuleWidget({module_name!r})",
            "except Exception:",
            "    _widget = None",
            "if _widget is None:",
            "    try:",
            f"        _widget = slicer.modules.{mod_attr}.widgetRepresentation().self()",
            "    except Exception:",
            "        _widget = None",
            "if _widget is None:",
            f"    raise RuntimeError(\"Could not obtain the {module_name} module widget for '{widget}'.\")",
            f"if not hasattr(_widget, {handler!r}):",
            f"    raise RuntimeError(\"{module_name} widget has no handler '{handler}' for '{widget}'; regenerate the CLI.\")",
        ]
        if is_toggle and widget.isidentifier():
            _tv = widget_targets.get(widget)
            if _tv is None:
                # No explicit target_value captured: infer tick/untick polarity from
                # the step text so "Untick the X checkbox" emits checked=False instead
                # of defaulting to True (re-tick). Generic; reuses _infer_final_state_intent.
                _intent = _infer_final_state_intent(step.get("description", "") or "")
                if _intent.get("state") is not None:
                    _tv = _intent["state"]
            checked = "False" if _tv is False else "True"
            lines += [
                "# Resolve the bound control by name across the ways a Slicer",
                "# extension can expose it (.ui object, direct self.<name>",
                "# attribute, or objectName in the widget tree), then set its",
                "# checked state (signals blocked to avoid a double-fire) and",
                "# invoke the handler once. Setting the REAL control state is",
                "# what lets a later programmatic setChecked(opposite) actually",
                "# emit toggled and run the handler (e.g. an 'Update' button that",
                "# unchecks the box to hide 3D interaction handles).",
                *_resolve_qt_control_lines("_widget", widget, "_ctrl"),
                "if _ctrl is not None:",
                "    try:",
                "        _ctrl.blockSignals(True)",
                f"        _ctrl.checked = {checked}",
                "        _ctrl.blockSignals(False)",
                "    except Exception:",
                "        pass",
                "try:",
                f"    _widget.{handler}({checked})",
                "except TypeError:",
                f"    _widget.{handler}()",
                f"print(\"[{extension_name}] Step '{step_id}': set '{widget}' = {checked} via {handler}.\")",
                "",
            ]
        else:
            lines += [
                f"_widget.{handler}()",
                f"print(\"[{extension_name}] Step '{step_id}': clicked '{widget}' via {handler}().\")",
                "",
            ]
        return "\n".join(lines) + "\n"

    def _generate_automated_workflow_template(
        self, extension_name, step, logic_class_name, module_name, logic_analysis,
    ) -> str:
        """Generate a code template for an automated workflow step.

        Uses LLM to generate proper state setup. Falls back to a static template
        on LLM failure.
        """
        method_name = step.get("method_name", "")
        step_id = step.get("step_id", "")
        description = step.get("description", step_id)

        # A 'Click the X button' step's real action is the widget handler, which
        # also creates the output nodes later steps need — prefer driving it.
        handler_tpl = self._maybe_generate_button_handler_template(
            extension_name, step, logic_class_name, module_name,
        )
        if handler_tpl:
            return handler_tpl

        # Try LLM-assisted generation
        tpl = self._generate_automated_template_llm(
            extension_name, step, logic_class_name, module_name, logic_analysis,
        )
        if tpl:
            return tpl

        # Fallback: static template
        if method_name:
            method_call_lines = [
                "# Execute the automated step",
                f"if hasattr(logic, '{method_name}'):",
                f"    result = logic.{method_name}()",
                "else:",
                "    result = None",
            ]
        else:
            # No extension method — try to generate code from sub-operations via LLM
            sub_ops = step.get("sub_operations", [])
            sub_op_parts = []
            for so in sub_ops:
                so_desc = so.get("description", "")
                so_keywords = so.get("slicer_api_keywords", [])
                so_method = so.get("extension_method_hint")
                if so.get("op_type") == "slicer_op" and so_keywords:
                    code = self._generate_slicer_api_template_llm(
                        step_id, so_desc, so_keywords,
                    )
                    if code:
                        sub_op_parts.append(f"# {so_desc}\n{code}")
                elif so.get("op_type") == "extension_op" and so_method:
                    sub_op_parts.append(
                        f"# {so_desc}\n"
                        f"if hasattr(logic, '{so_method}'):\n"
                        f"    logic.{so_method}()"
                    )
            if sub_op_parts:
                method_call_lines = ["\n\n".join(sub_op_parts)]
            else:
                method_call_lines = [
                    "# No specific method mapped to this step",
                    "# TODO: Determine the correct extension method to call",
                    "pass",
                ]

        lines = self._template_header_lines(extension_name, step, "")
        # Only include extension import boilerplate if we actually call an extension method
        if method_name or any(
            so.get("op_type") == "extension_op" and so.get("extension_method_hint")
            for so in step.get("sub_operations", [])
        ):
            lines.extend([
                "try:",
                f"    from {module_name} import {logic_class_name}",
                "except ImportError:",
                f"    raise RuntimeError(\"{extension_name} extension is not installed.\")",
                "",
                *self._emit_module_enter_precondition(module_name),
                "try:",
                f"    logic = _{extension_name.lower()}_logic",
                "except NameError:",
                f"    logic = {logic_class_name}()",
                "",
            ])
        lines.extend(method_call_lines)
        lines.append("")
        # Only store logic instance if we actually created one
        if method_name or any(
            so.get("op_type") == "extension_op" and so.get("extension_method_hint")
            for so in step.get("sub_operations", [])
        ):
            lines.append(f"_{extension_name.lower()}_logic = logic")
        lines.append(f"print(\"[{extension_name}] Step '{step_id}' completed.\")")

        return "\n".join(lines) + "\n"

    def _generate_automated_template_llm(
        self, extension_name, step, logic_class_name, module_name, logic_analysis,
    ) -> Optional[str]:
        """Use LLM to generate an automated workflow template with proper state setup."""
        method_name = step.get("method_name", "")
        if not method_name:
            return None

        # Gather method info
        method_info = None
        for m in logic_analysis.get("methods", []):
            if m.get("name") == method_name:
                method_info = m
                break

        # Get method source
        logic_file = logic_analysis.get("_logic_file", "")
        method_source = self._extract_method_source(logic_file, method_name) or ""

        if not method_source and not method_info:
            return None

        # Truncate source if needed (no limit — full method source for template generation)
        # if len(method_source) > 5000:
        #     method_source = method_source[:5000] + "\n# ... [truncated]"

        # Build method signature info
        params_desc = ""
        if method_info:
            params = method_info.get("parameters", [])
            if params:
                params_desc = "Parameters:\n" + "\n".join(
                    f"  - {p.get('name')}: {p.get('type', '?')} ({'required' if p.get('required') else 'optional'}) — {p.get('description', '')}"
                    for p in params
                )
            state_reads = method_info.get("state_reads", [])
            state_writes = method_info.get("state_writes", [])
            if state_reads:
                params_desc += f"\nState reads: {', '.join(state_reads)}"
            if state_writes:
                params_desc += f"\nState writes: {', '.join(state_writes)}"

        ui_context = ""

        parameter_context = ""
        if isinstance(self._workflow_metadata, dict):
            defaults = self._workflow_metadata.get("parameter_defaults", {}) or {}
            deps = self._workflow_metadata.get("parameter_method_dependencies", {}).get(method_name, {})
            appliers_by_role = self._workflow_metadata.get("parameter_appliers", {}) or {}
            roles = deps.get("parameter_roles", []) or []
            if roles:
                rows = []
                for role in roles:
                    default = defaults.get(role)
                    if default:
                        rows.append(
                            f"  - {role}: default {default.get('value')!r} "
                            f"({default.get('source')}, {default.get('confidence')} confidence)"
                        )
                    else:
                        rows.append(f"  - {role}: no inferred default")
                parameter_context = "Parameter-node dependencies:\n" + "\n".join(rows)
            requirements = deps.get("node_requirements", {}) or {}
            if requirements:
                requirement_rows = [
                    f"  - {role}: {(req or {}).get('requirement', 'optional_unknown')}"
                    for role, req in sorted(requirements.items())
                ]
                parameter_context += (
                    f"\nCaller-settable node-reference roles for {method_name} "
                    "(EXHAUSTIVE — do not set any role not listed; roles marked "
                    "produced_by_method are created by the method itself and must "
                    "NOT be set by the caller):\n" + "\n".join(requirement_rows)
                )
            applier_rows = [
                f"  - {role}: logic.{entries[0]['method']}(<final state>)"
                for role, entries in sorted(appliers_by_role.items())
                if entries and entries[0].get("confidence") == "high"
            ]
            if applier_rows:
                parameter_context += (
                    "\nEvidence-backed applier methods (a bare SetParameter only "
                    "records state — call the applier with the explicit final "
                    "state to make the effect happen):\n" + "\n".join(applier_rows)
                )

        proven_block = self._proven_api_chain_block()
        prompt = textwrap.dedent(f"""\
            Generate a Python code snippet for a 3D Slicer extension workflow step.

            Extension: {extension_name}
            Logic class: `{logic_class_name}` (import from `{module_name}`)
            Step: {step.get('step_id', '')}
            Method to call: `{method_name}()`
            {ui_context}

            {params_desc}
            {parameter_context}

            Method source code:
            ```python
            {method_source}
            ```
            {proven_block}

            The code must:
            1. Import the logic class from `{module_name}`
            2. Do not emit module lifecycle setup; the generator adds the shared lifecycle precondition deterministically.
            3. Reuse the existing logic instance `_{extension_name.lower()}_logic` if it exists, otherwise create a new `{logic_class_name}()`
            4. Set up any required state on the logic instance BEFORE calling the method. Derive required roles, node classes, and lookup terms only from the provided parameter metadata and method source.
               If the method or its helper methods read scalar values from `parameterNode.GetParameter(...)`, initialize missing values using the provided source-derived defaults with `parameterNode.SetParameter(...)` before calling the method. Never overwrite a non-empty parameter value.
            5. For parameter node references, resolution order is STRICT:
               (a) `parameterNode.GetNodeReference(role)` FIRST — earlier workflow steps
               usually set it already; if it returns a node, use it directly and do NOT
               re-resolve by name or keyword. (b) Only when the reference is empty,
               search by the source-derived node class and role keywords, then store the
               selected node reference. Do not invent fixed node names or anatomy/domain terms.
            6. Call the method with correct arguments
            7. Store the logic instance as `_{extension_name.lower()}_logic` for subsequent steps
            8. Print a completion message
            9. Use API receivers whose types are derivable from the supplied source and
               parameter metadata. If a receiver type is uncertain, do not invent a method;
               fail with a clear missing-evidence message.

            IMPORTANT restrictions:
            - Do NOT use `dir()`, `eval()`, `exec()`, `globals()`, or `locals()` — these are blocked in the execution sandbox.
            - Use `try/except NameError` to check if a variable exists, NOT `if 'var' in dir()`.
            - Do NOT use curly brace template placeholders. Write actual source-derived Python values. Do not invent or hardcode node names.
            - Escape all braces in f-strings and .format() calls by doubling them: use doubled-braces for literal braces in output strings.
            - Do not introduce unrelated UI, icon, toolbar, module-switching, or layout behavior.
            - Use ONLY the parameter/reference role names listed in the supplied parameter metadata. NEVER invent a role name (for example from a helper-method name); a role that is not listed does not exist.
            - Do NOT pre-set state the called method or its helper methods create or derive internally (roles marked produced_by_method, folder/hierarchy bookkeeping, output references). Set only the inputs the method reads.
            - Never call a method on the direct result of an API that can return None (GetNodeReference, GetItemDataNode, GetDisplayNode, ...) without first checking the result for None.
            - Return ONLY raw Python code. Do NOT wrap it in markdown fences (```python ... ```).""")

        try:
            for _attempt in range(2):
                response = self._call_llm(prompt, call_class="generation", attempt=_attempt)
                response = self._strip_markdown_fences(response) if response else None
                if not response:
                    break
                # Validate syntax immediately — retry once on failure
                import ast as _ast
                try:
                    _ast.parse(response)
                    return self._inject_module_enter_precondition(response, module_name)
                except (SyntaxError, IndentationError) as e:
                    if _attempt == 0:
                        logger.info(
                            "LLM automated template for step %s had syntax error: %s. Retrying...",
                            step.get("step_id", "?"), e,
                        )
                        # Add error context for retry
                        prompt += (
                            f"\n\nYour previous output had a syntax error: {e}\n"
                            "Output ONLY the corrected Python code, no explanation."
                        )
                    else:
                        logger.warning(
                            "LLM automated template for step %s still has syntax error after retry: %s",
                            step.get("step_id", "?"), e,
                        )
                        return self._inject_module_enter_precondition(
                            response, module_name
                        )  # Return as-is; validation will catch remaining issues.
        except Exception:
            logger.debug("LLM automated template generation failed", exc_info=True)
        return None

    def _generate_slicer_api_template_llm(
        self, step_id: str, description: str, slicer_api_keywords: List[str],
    ) -> Optional[str]:
        """Generate pure Slicer API code via LLM for steps with no extension method.

        Called when a step has slicer_op sub-operations but no method_name on the
        extension Logic class.  Uses the LLM with the step description and API
        keyword hints to produce Slicer core API code (no extension imports).
        """
        keywords_str = ", ".join(slicer_api_keywords) if slicer_api_keywords else "none"
        proven_block = self._proven_api_chain_block()
        prompt = textwrap.dedent(f"""\
            Generate a Python code snippet for a 3D Slicer operation.

            Step ID: {step_id}
            Description: {description}
            API keyword hints: [{keywords_str}]
            {proven_block}

            The code must:
            1. Use Slicer's built-in Python API only (slicer.mrmlScene,
               slicer.app.layoutManager(), slicer.modules, etc.)
            2. Be a complete, self-contained snippet that performs the described operation
            3. Use robust patterns (check for None, handle missing nodes gracefully)
            4. Print a short completion message
            5. Use only API calls whose receiver type and method are supported by supplied evidence.

            IMPORTANT restrictions:
            - Do NOT use `dir()`, `eval()`, `exec()`, `globals()`, or `locals()`
            - Do NOT import the extension module — use only Slicer core APIs
            - Do NOT use curly brace template placeholders — write actual Python values
            - Escape all braces in f-strings by doubling them
            - Do not introduce unrelated UI, icon, toolbar, module-switching, or layout behavior
            - Return ONLY raw Python code, no markdown fences""")

        try:
            for _attempt in range(2):
                response = self._call_llm(prompt, call_class="generation", attempt=_attempt)
                response = self._strip_markdown_fences(response) if response else None
                if not response or "slicer" not in response.lower():
                    break
                import ast as _ast
                try:
                    _ast.parse(response)
                    return response
                except (SyntaxError, IndentationError) as e:
                    if _attempt == 0:
                        prompt += (
                            f"\n\nPrevious output had syntax error: {e}\n"
                            "Output ONLY the corrected Python code, no explanation."
                        )
                    else:
                        return response
        except Exception:
            logger.debug("Slicer API LLM template generation failed", exc_info=True)
        return None

    def _apply_module_session_drivers(self, templates, steps=None):
        """Apply the per-module session drivers to every generated ``*.py.tpl``
        template (``module_sessions.all_drivers``). Each driver OVERRIDES its
        module's known standard ops with deterministic, idempotent code (e.g. the
        Segment Editor's create-segmentation / add-segment) and WRAPS the rest
        (binding + shared-state preamble). Idempotent (marker-guarded), so it is
        safe — and intended — to call in EVERY generation path (fresh generation,
        live revision, repair re-grounding) so the fix survives corrections/
        revisions. ``steps`` (the workflow steps) supplies each template's
        description for object-name extraction when the grounded code lacks it.
        Returns the number of templates changed."""
        from .module_sessions import all_drivers, extract_module
        drivers = all_drivers()
        desc_by_key = {}
        # Thread the active tool/effect across the ORDERED steps so an option /
        # apply / interaction step operates on the effect a PRIOR step activated
        # (e.g. Islands) instead of a defaulted Threshold. Keyed on the module +
        # the driver's own effect-activation detection — generic, no step identity.
        effect_by_key = {}
        active_effect = None
        for step in (steps or []):
            if not isinstance(step, dict):
                continue
            desc = step.get("description", "") or ""
            module = extract_module(desc)
            matched_driver = None
            for driver in drivers:
                if driver.claims(module):
                    matched_driver = driver
                    break
            if module and matched_driver is None:
                # Entered a different named module — the prior active tool no
                # longer governs interaction; drop it so it can't leak forward.
                active_effect = None
            elif matched_driver is not None:
                activated = matched_driver.effect_activated_by(step)
                if activated:
                    active_effect = activated
            key = step.get("code_template")
            if key:
                desc_by_key[key] = desc
                effect_by_key[key] = active_effect
        changed = 0
        for tpl_key in list(templates.keys()):
            if not isinstance(tpl_key, str) or not tpl_key.endswith(".py.tpl"):
                continue
            orig = templates[tpl_key]
            if not isinstance(orig, str):
                continue
            code = orig
            desc = desc_by_key.get(tpl_key, "")
            # A session driver only rewrites steps that belong to ITS module, taken
            # from the cookbook's "In the 'X' module, ..." context. Without this
            # gate the driver's DESCRIPTION-based signals leak onto unrelated steps:
            # e.g. the Segment Editor driver treats any step whose text contains
            # "apply" as a Threshold-effect apply, so an extension_op button step
            # like "Apply separation" gets its (correct) handler-drive template
            # overwritten with Segment Editor effect code. Generic: keyed purely on
            # the module label, never on the extension or a specific step; a step
            # with no module context (extension_op / interaction) matches no driver.
            module = extract_module(desc)
            step_active_effect = effect_by_key.get(tpl_key)
            for driver in drivers:
                if driver.claims(module):
                    code = driver.wrap(code, desc, active_effect=step_active_effect)
            if code != orig:
                templates[tpl_key] = code
                changed += 1
        return changed

    def _ensure_segment_editor_bindings(self, code: str) -> str:
        """Apply the Segment Editor session driver to a single re-grounded template
        (used by the repair loop's re-grounding). Delegates to the generic
        module-session framework (``module_sessions.SegmentEditorSessionDriver``)
        so a re-grounded Segment Editor template gets the same coherent binding +
        target-segment selection as the main generation pass. Idempotent."""
        from .module_sessions import SegmentEditorSessionDriver
        return SegmentEditorSessionDriver().wrap(code)

    def _generate_placement_starter_pre_template(
        self, extension_name, step, logic_class_name, module_name,
    ) -> str:
        """Generate deterministic setup code for extension-driven placement.

        The extension method itself creates the markup node and enters
        placement mode, so this template only calls that method.
        """
        method_name = step.get("method_name", "")
        step_id = step.get("step_id", "")
        repeat_group = step.get("repeat_group") or {}
        interaction_step_id = repeat_group.get("interaction_step") or step_id
        starter_info = self._placement_starter_info(method_name)
        node_classes = starter_info.get("node_classes") or []
        node_class = node_classes[0] if node_classes else step.get("node_class", "vtkMRMLMarkupsFiducialNode")

        lines = [
            *self._template_header_lines(extension_name, step, "Setup"),
            "import slicer",
            "from SlicerAIAgentLib.workflow_state import remember_interaction_node",
            f"from {module_name} import {logic_class_name}",
            "",
            *self._emit_module_enter_precondition(module_name),
            "try:",
            f"    logic = _{extension_name.lower()}_logic",
            "except NameError:",
            f"    logic = {logic_class_name}()",
            "",
            f"_workflow_before_ids = set()",
            f"_workflow_nodes = slicer.mrmlScene.GetNodesByClass(\"{node_class}\")",
            "_workflow_before_count = _workflow_nodes.GetNumberOfItems()",
            "for _workflow_i in range(_workflow_before_count):",
            "    _workflow_n = _workflow_nodes.GetItemAsObject(_workflow_i)",
            "    if _workflow_n is not None:",
            "        _workflow_before_ids.add(_workflow_n.GetID())",
            "",
            f"logic.{method_name}()",
            "",
            "_workflow_created_node = None",
            f"_workflow_nodes = slicer.mrmlScene.GetNodesByClass(\"{node_class}\")",
            "for _workflow_i in range(_workflow_nodes.GetNumberOfItems() - 1, -1, -1):",
            "    _workflow_n = _workflow_nodes.GetItemAsObject(_workflow_i)",
            "    if _workflow_n is not None and _workflow_n.GetID() not in _workflow_before_ids:",
            "        _workflow_created_node = _workflow_n",
            "        break",
            "if _workflow_created_node is not None:",
            f"    remember_interaction_node(_workflow_runtime_extension, _workflow_runtime_id, \"{interaction_step_id}\", _workflow_created_node.GetID(), _workflow_runtime_repeat_index)",
            f"_{extension_name.lower()}_logic = logic",
            "",
            f"print(\"[{extension_name}] Placement started for step '{step_id}'.\")",
        ]
        return "\n".join(lines) + "\n"

    def _generate_placement_starter_post_template(
        self, extension_name, step, method_name,
    ) -> str:
        """Generate post-interaction code for extension-driven placement.

        Placement-starter extension methods usually attach their own observers
        and process control points as the user places them.  The post step only
        exits placement mode and reports completion.
        """
        step_id = step.get("step_id", "")
        lines = [
            *self._template_header_lines(extension_name, step, "Done"),
            "import slicer",
            "",
            "interactionNode = slicer.mrmlScene.GetNodeByID(\"vtkMRMLInteractionNodeSingleton\")",
            "if interactionNode is not None:",
            "    interactionNode.SwitchToViewTransformMode()",
            "",
            f"print(\"[{extension_name}] Step '{step_id}' interaction completed after {method_name}().\")",
        ]
        return "\n".join(lines) + "\n"
