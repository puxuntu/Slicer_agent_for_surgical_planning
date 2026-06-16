from .common import *


class WidgetWorkflowMixin:
    def _setupWorkflowUI(self):
        """Set up UI components for guided interactive workflows."""
        from SlicerAIAgentLib.WorkflowOrchestrator import WorkflowOrchestrator
        from SlicerAIAgentLib.InteractionManager import InteractionManager
        from SlicerAIAgentLib.WorkflowRuntime import WorkflowRuntime

        self._interactionManager = InteractionManager()
        self._workflowOrchestrator = WorkflowOrchestrator(
            interaction_manager=self._interactionManager,
        )
        self._workflowRuntime = WorkflowRuntime()

        self._setupWorkflowUserPanel()

    def _setupWorkflowUserPanel(self):
        """Create or connect the user-facing workflow panel controls."""
        if not getattr(self, "_workflowUserFrame", None):
            self._workflowUserFrame = qt.QFrame()
            self._workflowUserFrame.setObjectName("workflowUserFrame")
            self._workflowUserFrame.setStyleSheet(
                "QFrame#workflowUserFrame { background-color: #f7fbff; "
                "border: 1px solid #b8d7f2; border-radius: 4px; }"
            )
            layout = qt.QVBoxLayout(self._workflowUserFrame)
            layout.setContentsMargins(10, 8, 10, 8)

            header = qt.QHBoxLayout()
            self._workflowTitleLabel = qt.QLabel("Workflow")
            self._workflowTitleLabel.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f3b57;")
            self._workflowStatusLabel = qt.QLabel("Idle")
            self._workflowStatusLabel.setStyleSheet("font-weight: bold; color: #3b6f9e;")
            header.addWidget(self._workflowTitleLabel, 1)
            header.addWidget(self._workflowStatusLabel)
            layout.addLayout(header)

            self._workflowProgressBar = qt.QProgressBar()
            self._workflowProgressBar.setMinimum(0)
            self._workflowProgressBar.setMaximum(1)
            self._workflowProgressBar.setValue(0)
            layout.addWidget(self._workflowProgressBar)

            self._workflowStepLabel = qt.QLabel("Step 0 of 0")
            self._workflowActionLabel = qt.QLabel("")
            self._workflowActionLabel.setWordWrap(True)
            self._workflowActionLabel.setStyleSheet("font-weight: bold; color: #222;")
            self._workflowInstructionLabel = qt.QLabel("")
            self._workflowInstructionLabel.setWordWrap(True)
            layout.addWidget(self._workflowStepLabel)
            layout.addWidget(self._workflowActionLabel)
            layout.addWidget(self._workflowInstructionLabel)

            self._workflowChoiceContainer = qt.QWidget()
            self._workflowChoiceLayout = qt.QHBoxLayout(self._workflowChoiceContainer)
            self._workflowChoiceLayout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self._workflowChoiceContainer)

            controls = qt.QHBoxLayout()
            self._workflowDoneButton = qt.QPushButton("Done")
            self._workflowSkipButton = qt.QPushButton("Skip")
            self._workflowCancelButton = qt.QPushButton("Cancel")
            controls.addWidget(self._workflowDoneButton)
            controls.addWidget(self._workflowSkipButton)
            controls.addWidget(self._workflowCancelButton)
            controls.addStretch(1)
            layout.addLayout(controls)
            self.layout.addWidget(self._workflowUserFrame)

        self._workflowBannerLabel = self._workflowTitleLabel
        self._workflowInstructionsLabel = self._workflowInstructionLabel
        self._workflowChoiceButtons = []
        self._workflowChoiceInput = None
        self._workflowChoiceSubmitButton = None

        if getattr(self, "_workflowDoneButton", None):
            self._workflowDoneButton.clicked.connect(self._onWorkflowDoneClicked)
        if getattr(self, "_workflowSkipButton", None):
            self._workflowSkipButton.clicked.connect(self._onWorkflowSkipClicked)
        if getattr(self, "_workflowCancelButton", None):
            self._workflowCancelButton.clicked.connect(self._onWorkflowCancelClicked)

        # Build the replay stepper unconditionally: the workflow frame can be
        # loaded from the .ui file (widget_core.py) instead of built here, in
        # which case the programmatic block above is skipped. This wraps the
        # progress bar with the Back / Forward / Run-from-here buttons.
        self._setupReplayControls()

        self._positionWorkflowUserPanel()
        self._clearWorkflowPanel()
        self._applyWidthSafeLabels()

    def _applyWidthSafeLabels(self):
        """Stop variable-length labels from forcing the module panel wider.

        A QLabel with word-wrap OFF reports its full text width as its minimum
        size hint, and Slicer's module panel grows (and then locks) to satisfy
        the widest child's minimum. The workflow header's title + status are the
        offenders: when the status becomes its longest value ("Waiting for your
        interaction" at the first interaction step, right after step 9) the panel
        jumps wider and can no longer be dragged narrower. Word-wrapping drops
        each label's minimum width to its widest single word, so the panel stops
        auto-widening and the width the user set sticks. Applied at runtime so it
        covers both the .ui-loaded and the programmatic-fallback widgets.
        """
        labels = [
            getattr(self, "_workflowTitleLabel", None),
            getattr(self, "_workflowStatusLabel", None),
            getattr(self, "_workflowStepLabel", None),
            getattr(self, "statusLabel", None),  # main agent status row
        ]
        for label in labels:
            if label is None:
                continue
            try:
                label.setWordWrap(True)
                label.setMinimumWidth(0)
            except Exception:
                logger.debug("width-safe label setup failed", exc_info=True)

    def _positionWorkflowUserPanel(self):
        """Place the workflow panel below Debug and above the prompt input area."""
        if not getattr(self, "_workflowUserFrame", None):
            return
        debug_group = self.ui.findChild(ctk.ctkCollapsibleGroupBox, "debugGroupBox") if getattr(self, "ui", None) else None
        if not debug_group:
            return
        parent = debug_group.parent()
        parent_layout = parent.layout() if parent else None
        if not parent_layout:
            return
        workflow_index = parent_layout.indexOf(self._workflowUserFrame)
        debug_index = parent_layout.indexOf(debug_group)
        if debug_index < 0:
            return
        if workflow_index >= 0:
            parent_layout.removeWidget(self._workflowUserFrame)
            if workflow_index < debug_index:
                debug_index -= 1
        parent_layout.insertWidget(debug_index + 1, self._workflowUserFrame)

    def _updateWorkflowPanel(self, result_or_state=None):
        """Render generated-CLI or traditional task state into the workflow panel."""
        state = result_or_state if isinstance(result_or_state, dict) else {}
        should_map_runtime_result = (
            not state
            or any(key in state for key in ("type", "step_id", "tool", "next_step"))
        )
        if self._workflowRuntime and self._workflowRuntime.session and should_map_runtime_result:
            state = self._workflowRuntime.state_for_ui(state)
        elif should_map_runtime_result and not state.get("active"):
            state = self._workflowUiStateFromStepResult(state)

        self._currentWorkflowUiState = dict(state or {"active": False})
        if not getattr(self, "_workflowUserFrame", None):
            return

        if not self._currentWorkflowUiState.get("active"):
            self._workflowUserFrame.setVisible(False)
            return

        self._workflowUserFrame.setVisible(True)
        title = (
            self._currentWorkflowUiState.get("workflow_title")
            or self._currentWorkflowUiState.get("extension_name")
            or "Task"
        )
        status = self._currentWorkflowUiState.get("status") or "Running"
        total = int(self._currentWorkflowUiState.get("total_steps") or 0)
        completed = int(self._currentWorkflowUiState.get("completed_steps") or 0)
        current_index = int(self._currentWorkflowUiState.get("current_index") or 0)

        self._workflowTitleLabel.setText(str(title))
        self._workflowStatusLabel.setText(str(status))
        if total > 0:
            self._workflowProgressBar.setRange(0, total)
            self._workflowProgressBar.setValue(max(0, min(completed, total)))
            self._workflowProgressBar.setFormat(f"{completed}/{total}")
            step_text = f"Step {current_index or completed} of {total}"
            repeat_progress = self._currentWorkflowUiState.get("repeat_progress") or {}
            repeat_total = int(repeat_progress.get("total") or 0)
            repeat_current = int(repeat_progress.get("current") or 0)
            if repeat_total > 0 and repeat_current > 0:
                object_label = self._currentWorkflowUiState.get("object_label") or "Item"
                step_text += f" - {str(object_label).title()} {repeat_current} of {repeat_total}"
            elif repeat_current > 0:
                step_text += f" - Repeat iteration {repeat_current}"
            self._workflowStepLabel.setText(step_text)
            self._workflowStepLabel.setVisible(True)
        else:
            self._workflowProgressBar.setRange(0, 1)
            self._workflowProgressBar.setValue(0)
            self._workflowProgressBar.setFormat("")
            self._workflowStepLabel.setVisible(False)

        description = self._currentWorkflowUiState.get("description") or ""
        instructions = self._currentWorkflowUiState.get("instructions") or ""
        self._workflowActionLabel.setText(str(description))
        self._workflowActionLabel.setVisible(bool(description))
        self._workflowInstructionLabel.setText(str(instructions))
        self._workflowInstructionLabel.setVisible(bool(instructions))

        self._renderWorkflowChoices(self._currentWorkflowUiState)
        self._updateReplayControls(self._currentWorkflowUiState)

        self._workflowDoneButton.setVisible(bool(self._currentWorkflowUiState.get("can_done")))
        self._workflowSkipButton.setVisible(bool(self._currentWorkflowUiState.get("can_skip")))
        self._workflowCancelButton.setVisible(bool(self._currentWorkflowUiState.get("can_cancel")))
        self._workflowDoneButton.setEnabled(bool(self._currentWorkflowUiState.get("can_done")))
        self._workflowSkipButton.setEnabled(bool(self._currentWorkflowUiState.get("can_skip")))
        self._workflowCancelButton.setEnabled(bool(self._currentWorkflowUiState.get("can_cancel")))
        done_label = self._currentWorkflowUiState.get("done_label") or "Done"
        self._workflowDoneButton.setText(str(done_label) if self._currentWorkflowUiState.get("can_done") else "Done")

    def _workflowUiStateFromStepResult(self, result):
        """Fallback panel state for workflow results not tracked by WorkflowRuntime."""
        if not isinstance(result, dict) or not result:
            return {"active": False}
        result_type = result.get("type", "")
        choices = []
        for choice in result.get("choices") or []:
            if isinstance(choice, dict):
                label = choice.get("label") or choice.get("value") or "Choice"
                value = choice.get("value", label)
                choices.append({"label": label, "value": value})
        status = "Running"
        guidance = result.get("ui_guidance") if isinstance(result.get("ui_guidance"), dict) else {}
        if result_type in ("interactive", "mixed"):
            status = "Waiting for your interaction"
        elif result_type == "user_choice":
            status = "Waiting for your choice"
        elif result.get("workflow_completed"):
            status = "Completed"
        is_repeat_decision = result_type == "user_choice" and bool(result.get("repeat_decision"))
        if is_repeat_decision:
            # Loop continue/exit decision: show its own question/instruction so
            # the Yes/No buttons are unambiguous (not the step's guidance).
            description = result.get("question") or guidance.get("title") or ""
        elif result_type == "user_choice":
            description = guidance.get("title") or result.get("question") or ""
        else:
            description = guidance.get("title") or result.get("explanation") or result.get("instruction") or ""
        if is_repeat_decision:
            instructions = result.get("instruction") or guidance.get("instruction") or ""
        else:
            instructions = (
                guidance.get("instruction")
                or (result.get("interaction") or {}).get("placement_instructions")
                or result.get("interaction_instructions")
                or ""
            )
        return {
            "active": True,
            "workflow_title": result.get("tool", "Workflow"),
            "current_step": result.get("step_id"),
            "current_index": 0,
            "completed_steps": 0,
            "total_steps": 0,
            "status": status,
            "description": description,
            "instructions": instructions,
            "choices": choices,
            "default_value": result.get("default_value"),
            "parameter_name": result.get("parameter_name", ""),
            "choice_label": guidance.get("choice_label", ""),
            "input_label": guidance.get("input_label", ""),
            "done_label": guidance.get("done_label", "Done") or "Done",
            "object_label": guidance.get("object_label", ""),
            "repeat_progress": result.get("repeat_progress") or {},
            "needs_choice_input": result_type == "user_choice" and not choices,
            "can_done": result_type in ("interactive", "mixed"),
            "can_skip": bool(result.get("is_optional")),
            "can_cancel": not result.get("workflow_completed"),
        }

    def _renderWorkflowChoices(self, state):
        """Render choice buttons for generated CLI user_choice steps."""
        if getattr(self, "_workflowChoiceInput", None) is not None:
            if self._workflowChoiceLayout is not None:
                self._workflowChoiceLayout.removeWidget(self._workflowChoiceInput)
            self._workflowChoiceInput.setParent(None)
            self._workflowChoiceInput = None
        if getattr(self, "_workflowChoiceSubmitButton", None) is not None:
            if self._workflowChoiceLayout is not None:
                self._workflowChoiceLayout.removeWidget(self._workflowChoiceSubmitButton)
            self._workflowChoiceSubmitButton.setParent(None)
            self._workflowChoiceSubmitButton = None
        for button in getattr(self, "_workflowChoiceButtons", []):
            if self._workflowChoiceLayout is not None:
                self._workflowChoiceLayout.removeWidget(button)
            button.setParent(None)
        self._workflowChoiceButtons = []

        choices = state.get("choices") or []
        step_id = state.get("current_step")
        needs_input = bool(state.get("needs_choice_input"))
        if self._workflowChoiceContainer is not None:
            self._workflowChoiceContainer.setVisible(bool(choices) or needs_input)
        if self._workflowChoiceLayout is None:
            return
        if not choices and needs_input:
            default_value = state.get("default_value")
            self._workflowChoiceInput = qt.QLineEdit()
            input_label = state.get("input_label") or state.get("choice_label") or "value"
            self._workflowChoiceInput.setPlaceholderText(f"Enter {input_label}")
            if default_value is not None:
                self._workflowChoiceInput.setText(str(default_value))
            self._workflowChoiceInput.returnPressed.connect(self._onWorkflowChoiceInputSubmitted)

            self._workflowChoiceSubmitButton = qt.QPushButton("Set")
            self._workflowChoiceSubmitButton.setToolTip("Use this value")
            self._workflowChoiceSubmitButton.clicked.connect(self._onWorkflowChoiceInputSubmitted)

            self._workflowChoiceLayout.addWidget(self._workflowChoiceInput, 1)
            self._workflowChoiceLayout.addWidget(self._workflowChoiceSubmitButton)
            self._workflowChoiceInput.setVisible(True)
            self._workflowChoiceSubmitButton.setVisible(True)
            return
        if not choices:
            return

        for choice in choices:
            label = str(choice.get("label") or choice.get("value") or "Choice")
            value = choice.get("value", label)
            # Cap the visible label so a long choice (e.g. a long node name) can't
            # make a wide button that forces the whole module panel wider; the
            # full text stays available in the tooltip.
            display = label if len(label) <= 40 else (label[:39] + "…")
            button = qt.QPushButton(display)
            button.setToolTip(label if display != label else f"Select {label}")
            button.clicked.connect(lambda checked=False, sid=step_id, val=value: self._onWorkflowChoiceClicked(sid, val))
            self._workflowChoiceLayout.addWidget(button)
            button.setVisible(True)
            self._workflowChoiceButtons.append(button)

    def _showWorkflowInteraction(self, result):
        """Show an interactive or mixed workflow wait state."""
        self._updateWorkflowPanel(result)

    def _showWorkflowChoice(self, result):
        """Show a user-choice workflow step as buttons when choices are known."""
        self._updateWorkflowPanel(result)

    def _clearWorkflowPanel(self):
        """Hide and reset the user-facing workflow panel."""
        self._currentWorkflowUiState = {"active": False}
        self._taskWorkflowPanelActive = False
        if not getattr(self, "_workflowUserFrame", None):
            return
        self._workflowUserFrame.setVisible(False)
        self._workflowTitleLabel.setText("Workflow")
        self._workflowStatusLabel.setText("Idle")
        self._workflowProgressBar.setRange(0, 1)
        self._workflowProgressBar.setValue(0)
        self._workflowStepLabel.setText("Step 0 of 0")
        self._workflowActionLabel.setText("")
        self._workflowInstructionLabel.setText("")
        self._renderWorkflowChoices({})
        self._updateReplayControls({})
        self._workflowDoneButton.setVisible(False)
        self._workflowSkipButton.setVisible(False)
        self._workflowCancelButton.setVisible(False)
        self._workflowDoneButton.setText("Done")

    def _onWorkflowDoneClicked(self):
        self._closeFloatingWorkflowControl()
        current_step = self._currentWorkflowUiState.get("current_step")
        if current_step:
            self.sendButton.setEnabled(False)
            # The interaction for this step is over: drop any observers and
            # debounce timers the runtime registered, so they cannot
            # accumulate across repeat iterations and consecutive
            # interactive steps (a generic cause of degraded/locked
            # interaction state after several placements).
            try:
                self._interactionManager.cleanup()
            except Exception:
                logger.debug("Interaction cleanup on Done failed", exc_info=True)
            self._runWorkflowStepDirect(current_step, "proceed")

    def _onWorkflowSkipClicked(self):
        current_step = self._currentWorkflowUiState.get("current_step")
        if current_step:
            self.sendButton.setEnabled(False)
            self._runWorkflowStepDirect(current_step, "skip")

    def _onWorkflowCancelClicked(self):
        self._closeFloatingWorkflowControl()
        current_step = self._currentWorkflowUiState.get("current_step")
        self.sendButton.setEnabled(False)
        self._runWorkflowStepDirect(current_step, "cancel")

    def _onWorkflowChoiceClicked(self, step_id, value):
        if step_id:
            self.sendButton.setEnabled(False)
            self._runWorkflowStepDirect(step_id, "choice_made", args={"choice_value": value})

    def _onWorkflowChoiceInputSubmitted(self):
        step_id = self._currentWorkflowUiState.get("current_step")
        if not step_id or self._workflowChoiceInput is None:
            return
        value = self._workflowChoiceInput.text.strip()
        if not value:
            value = str(self._currentWorkflowUiState.get("default_value") or "").strip()
        if not value:
            return
        self.sendButton.setEnabled(False)
        self._runWorkflowStepDirect(step_id, "choice_made", args={"choice_value": value})

    def _enterWorkflowWait(self, step_info):
        """
        Enter wait state for an interactive workflow step.
        Shows user instructions in the Workflow panel. Text commands remain a fallback.
        """
        step_desc = (
            step_info.get("explanation")
            or step_info.get("step_info", {}).get("description")
            or "Interactive step"
        )

        self._waitingForUser = True
        self._currentWorkflowStepInfo = step_info
        self._showWorkflowInteraction(step_info)
        # The interaction is shown ONLY in the inline workflow panel (module UI).
        # The separate floating "AI Agent — workflow step" pop-up was removed at
        # the user's request; the panel's Done/Cancel buttons drive the workflow.

        # Placement guard: shortly after the wait state is shown (so the pre
        # code has settled), verify Slicer is actually armed for the
        # interaction; re-arm if anything upstream dropped placement mode.
        try:
            qt.QTimer.singleShot(600, lambda: self._ensurePlacementArmed(step_info))
        except Exception:
            logger.debug("Placement guard scheduling failed", exc_info=True)

        self._setAgentStatus("Workflow", f"Waiting: {step_desc}")
        logger.info(f"[Workflow] Entered wait state for step: {step_desc}")

    def _ensurePlacementArmed(self, step_info):
        """Re-arm markup placement if the waited-on step lost it.

        Generic guard for interactive markup steps: a post template, an
        extension callback, or a layout rebuild can leave Slicer outside
        place mode while the workflow is waiting for the user to place
        points — the visible symptom is "interaction tools hidden". When the
        runtime knows the step's interaction node, placement is restored
        deterministically (active list + single place mode). Fail-open.
        """
        try:
            if not self._waitingForUser or not isinstance(step_info, dict):
                return
            current = getattr(self, "_currentWorkflowStepInfo", None)
            if current is not step_info:
                return  # a newer step superseded this wait
            interaction = step_info.get("interaction") or {}
            node_class = str(interaction.get("node_class") or "")
            if not node_class.startswith("vtkMRMLMarkups") and step_info.get(
                "interaction_type", ""
            ) not in ("plane", "curve", "line", "fiducial"):
                return

            interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
            selectionNode = slicer.app.applicationLogic().GetSelectionNode()
            in_place_mode = bool(
                interactionNode
                and interactionNode.GetCurrentInteractionMode() == interactionNode.Place
            )
            has_active_place_node = bool(
                selectionNode and selectionNode.GetActivePlaceNodeID()
            )
            if in_place_mode and has_active_place_node:
                return  # armed — nothing to do

            from SlicerAIAgentLib.workflow_state import latest_interaction_node_for_step
            node = latest_interaction_node_for_step(step_info.get("step_id", ""))
            if node is None:
                logger.info(
                    "[Workflow] Placement not armed for step %s and no remembered "
                    "node to re-arm with", step_info.get("step_id", "?"),
                )
                return
            slicer.modules.markups.logic().SetActiveListID(node)
            if interactionNode:
                interactionNode.SwitchToSinglePlaceMode()
            self._recordRoleEvent("Executor", "placement_rearmed", {
                "step_id": step_info.get("step_id", ""),
                "node": node.GetName(),
            })
            logger.info(
                "[Workflow] Re-armed placement for step %s on node %s",
                step_info.get("step_id", "?"), node.GetName(),
            )
        except Exception:
            logger.debug("Placement guard failed open", exc_info=True)

    def _exitWorkflowWait(self):
        """Exit workflow wait state and restore normal state."""
        self._waitingForUser = False
        self._currentWorkflowStepInfo = None
        self._closeFloatingWorkflowControl()
        self._setReadyStatus()

    def _closeFloatingWorkflowControl(self):
        window = getattr(self, "_floatingWorkflowControl", None)
        self._floatingWorkflowControl = None
        if window is not None:
            try:
                window.close()
                window.deleteLater()
            except Exception:
                logger.debug("Floating workflow control close failed", exc_info=True)

    def _autoProceedWorkflowStep(self, next_step_info):
        """Automatically prompt the LLM to execute the next workflow step."""
        step_id = next_step_info.get("step_id")
        step_type = next_step_info.get("step_type")
        description = next_step_info.get("description", "")

        if step_type == "branch":
            # Ask the user about the branch decision
            self._updateWorkflowPanel({
                "active": True,
                "workflow_title": self._currentWorkflowUiState.get("workflow_title", "Workflow"),
                "status": "Waiting for your choice",
                "current_step": step_id,
                "current_index": self._currentWorkflowUiState.get("current_index", 0),
                "completed_steps": self._currentWorkflowUiState.get("completed_steps", 0),
                "total_steps": self._currentWorkflowUiState.get("total_steps", 0),
                "description": description,
                "instructions": "This step is optional.",
                "can_done": True,
                "can_skip": True,
                "can_cancel": True,
            })
            self.sendButton.setEnabled(True)
            return

        # Auto-send a prompt to proceed with the next step
        self.promptInput.setPlainText(f"Proceed with step '{step_id}': {description}")
        self.onSendButtonClicked()

    def _getWorkflowTemplateFiller(self):
        """
        Return a template filler callable that reads and fills .py.tpl files
        from the active workflow's CLI directory.
        """
        if not self._workflowOrchestrator or not self._activeWorkflowId:
            return None

        state = self._workflowOrchestrator._get_state(self._activeWorkflowId)
        if not state:
            return None

        ext_name = state.extension_name
        from SlicerAIAgentLib.ExtensionCLILoader import _fill_template, _ensure_cache
        _ensure_cache()
        import os
        cli_dir = os.path.join(
            SLICER_AI_AGENT_ROOT, "Resources", "extension_CLI", ext_name
        )

        def filler(template_path, args):
            full_path = os.path.join(cli_dir, template_path)
            if not os.path.exists(full_path):
                return None
            with open(full_path, "r") as f:
                template_text = f.read()
            return _fill_template(template_text, args)

        return filler

    def _applyWorkflowDisplayProperties(self, step_info):
        """Apply display properties from the workflow step to newly created markup nodes."""
        display_props = step_info.get("display_properties")
        if not display_props:
            return

        try:
            # Find recently created markup nodes matching the step's node class
            node_class = step_info.get("node_class", "")
            interaction_type = step_info.get("interaction_type", "")
            step_id = step_info.get("step_id", "")

            # Try to find the node by the template variable convention
            ext_name = step_info.get("tool", "")
            node_var = f"_{ext_name.lower()}_{step_id}_id"
            import __main__
            node_id = getattr(__main__, node_var, None)

            if node_id:
                node = slicer.mrmlScene.GetNodeByID(node_id)
            else:
                # Fallback: find the most recently added markup node of the expected class
                node = None
                all_nodes = slicer.mrmlScene.GetNodesByClass(node_class) if node_class else None
                if all_nodes:
                    all_nodes.UnRegister(None)
                    count = all_nodes.GetNumberOfItems()
                    if count > 0:
                        node = all_nodes.GetItemAsObject(count - 1)

            if not node:
                logger.warning(
                    f"[Workflow] Could not find markup node for step '{step_id}' "
                    f"to apply display properties"
                )
                return

            # Check for unresolved symbolic view tags and attempt fallback resolution
            view_ids = display_props.get("addViewNodeIDs", [])
            resolved_ids = []
            unresolved = []
            for ref in view_ids:
                vid = self._interactionManager._resolve_view_node_ref(ref)
                if vid:
                    resolved_ids.append(vid)
                else:
                    tag = ref.get("tag", "?")
                    unresolved.append(tag)
                    # Fallback: resolve symbolic tag via slicer module globals
                    # (set by the create_bone_models template or extension init)
                    if ref.get("symbolic"):
                        try:
                            tag_val = getattr(slicer, ref["tag"], None)
                            if tag_val is not None:
                                cls = ref.get("class", "vtkMRMLViewNode")
                                vn = slicer.mrmlScene.GetSingletonNode(str(tag_val), cls)
                                if vn:
                                    resolved_ids.append(vn.GetID())
                                    unresolved.pop()
                        except Exception:
                            pass

            if resolved_ids:
                # Replace symbolic refs with resolved IDs
                display_props = dict(display_props)
                display_props["addViewNodeIDs"] = resolved_ids

            if unresolved:
                logger.warning(
                    f"[Workflow] Could not resolve view tags for step '{step_id}': {unresolved}. "
                    f"Markup will be visible in all views."
                )

            display_node = node.GetDisplayNode()
            if display_node:
                self._interactionManager._apply_display_properties(display_node, display_props)

                # Verify: log what was actually applied
                applied_views = []
                if hasattr(display_node, "GetNumberOfViewNodeIDs"):
                    for i in range(display_node.GetNumberOfViewNodeIDs()):
                        applied_views.append(display_node.GetNthViewNodeID(i))
                logger.info(
                    f"[Workflow] Applied display properties to '{node.GetName()}' "
                    f"for step '{step_id}': views={applied_views}, "
                    f"props={list(display_props.keys())}"
                )

            # Apply locked state on the node itself
            if display_props.get("locked") is not None:
                node.SetLocked(display_props["locked"])

        except Exception as e:
            logger.warning(f"[Workflow] Failed to apply display properties: {e}")

    def _handleCliProgress(self, stage_num, stage_name, detail):
        """Handle CLI generator progress updates on the main thread."""
        self._cliProgressDisplay.append(f"  Phase {stage_num}: {stage_name} — {detail}")

    def _handleCliProbeRequest(self, payload):
        """Execute a CLI live-API probe on the Qt/Slicer main thread."""
        response_queue = payload.get('response_queue')
        probe_code = payload.get('probe_code', '')
        try:
            from SlicerAIAgentLib.ExtensionCLIAnalyzer import ExtensionCLIAnalyzer
            result = ExtensionCLIAnalyzer._execute_probe(probe_code)
        except Exception as exc:
            result = {"error": f"{type(exc).__name__}: {exc}"}
        if response_queue is not None:
            response_queue.put(result)

    def _handleCliComplete(self, result):
        """Handle CLI generator completion on the main thread."""
        self._cliGeneratorRunning = False
        self._analyzeGenerateButton.setEnabled(True)

        if result.get("success"):
            # Generation is pure background analysis — it must NOT touch the live
            # MRML scene/viewport. Runtime (live-execution) validation is deferred
            # to the Repair button, which runs the steps deliberately and invisibly.
            self._finalizeCliValidation(result, {})

        else:
            self._cliStatusLabel.setText("Failed")
            self._cliStatusLabel.setStyleSheet("font-weight: bold; color: red;")
            error = result.get("error", "Unknown error")
            self._cliProgressDisplay.append(f"FAILED: {error}")

            stages = result.get("phases_completed") or result.get("stages_completed", [])
            if stages:
                self._cliProgressDisplay.append(
                    f"Completed phases: {stages}"
                )

            # Auto-revise if templates were generated but validation failed
            if result.get("validation_result") and not result["validation_result"].get("valid"):
                self._cliProgressDisplay.append("Auto-revising with LLM...")
                self._autoReviseCli(result)

    # Maximum live-exec → repair → re-exec passes before giving up on a defect.
    _MAX_LIVE_REPAIR_PASSES = 3

    def _runCliLiveValidation(self, result, outer_iter=0):
        """Live-execute generated steps; repair runtime defects; re-validate.

        Runs on the Qt main thread (SafeExecutor needs slicer.mrmlScene). Each
        pass executes every runnable step's template for real; any step that
        raises (status failed_bug) is sent to a targeted LLM repair, then this
        method is re-entered to confirm the fix. Precondition-skipped steps never
        block. Bounded by _MAX_LIVE_REPAIR_PASSES.
        """
        cli_dir = result.get("cli_dir")
        if not cli_dir or not os.path.isdir(cli_dir):
            self._finalizeCliValidation(result, {})
            return

        try:
            from SlicerAIAgentLib.SafeExecutor import SafeExecutor
            from SlicerAIAgentLib.ExtensionCLIAnalyzer import ExtensionCLIAnalyzer
            from SlicerAIAgentLib.CodeValidator import CodeValidator
            executor = SafeExecutor()
            analyzer = ExtensionCLIAnalyzer(
                llm_client=self.logic.llmClient,
                output_base_dir=os.path.join(
                    SLICER_AI_AGENT_ROOT, "Resources", "extension_CLI"
                ),
                code_validator=CodeValidator(),
            )
            self._cliProgressDisplay.append(
                f"Live-validating generated steps (pass {outer_iter + 1})..."
            )
            live_results = analyzer.live_validate_templates(cli_dir, executor)
        except Exception as e:
            self._cliProgressDisplay.append(f"Live validation error: {e}")
            self._finalizeCliValidation(result, {})
            return

        self._writeLiveExecutionArtifact(cli_dir, live_results, outer_iter)

        failures = [
            r for r in live_results.values()
            if r.get("status") == "failed_bug"
        ]
        n_valid = sum(1 for r in live_results.values() if r.get("status") == "live_valid")
        n_skip = sum(
            1 for r in live_results.values()
            if str(r.get("status", "")).startswith("skipped")
        )
        self._cliProgressDisplay.append(
            f"Live validation: {n_valid} ran clean, {len(failures)} failed, "
            f"{n_skip} skipped (preconditions/interaction)."
        )

        if failures and outer_iter < self._MAX_LIVE_REPAIR_PASSES:
            self._cliLiveResult = result
            self._cliLiveIter = outer_iter
            self._cliLiveResults = live_results
            self._cliGeneratorRunning = True
            self._cliStatusLabel.setText("Repairing live failures...")
            self._cliStatusLabel.setStyleSheet("font-weight: bold; color: orange;")

            ext_name = (result.get("manifest", {}) or {}).get("extension_name", "")
            data = self._getSelectedExtensionData() or {}
            source_path = data.get("path", "")

            def _run_live_repair():
                try:
                    from SlicerAIAgentLib.ExtensionCLIAnalyzer import ExtensionCLIAnalyzer
                    from SlicerAIAgentLib.CodeValidator import CodeValidator
                    repair_analyzer = ExtensionCLIAnalyzer(
                        llm_client=self.logic.llmClient,
                        output_base_dir=os.path.join(
                            SLICER_AI_AGENT_ROOT, "Resources", "extension_CLI"
                        ),
                        code_validator=CodeValidator(),
                        on_progress=lambda n, s, d: self._streamQueue.put(
                            ('cli_progress', {'stage': n, 'name': s, 'detail': d})
                        ),
                        on_error=lambda e: self._streamQueue.put(('cli_error', e)),
                    )
                    repair = repair_analyzer.repair_live_failures(
                        ext_name, failures, source_path=source_path
                    )
                    self._streamQueue.put(('cli_live_repair_complete', repair))
                except Exception as e:
                    self._streamQueue.put(('cli_error', str(e)))

            threading.Thread(target=_run_live_repair, daemon=True).start()
            return

        # No failures, or repair budget exhausted: finalize on these results.
        self._finalizeCliValidation(result, live_results)

    def _handleCliLiveRepairComplete(self, repair):
        """Resume the live-validation loop after a targeted live repair."""
        self._cliGeneratorRunning = False
        result = getattr(self, "_cliLiveResult", None)
        outer_iter = getattr(self, "_cliLiveIter", 0)
        if not result:
            return
        if repair.get("success"):
            self._cliProgressDisplay.append(
                f"Live repair rewrote {len(repair.get('repaired', []))} "
                f"template(s); re-validating..."
            )
            self._runCliLiveValidation(result, outer_iter + 1)
        else:
            # No change produced — re-validating again would loop on the same
            # defect. Finalize honestly with the last known live results.
            self._cliProgressDisplay.append(
                f"Live repair produced no change ({repair.get('error', 'unknown')})."
            )
            self._finalizeCliValidation(
                result, getattr(self, "_cliLiveResults", {})
            )

    def _writeLiveExecutionArtifact(self, cli_dir, live_results, outer_iter):
        """Persist a per-step live-execution report under debug/ for transparency."""
        try:
            debug_dir = os.path.join(cli_dir, "debug")
            os.makedirs(debug_dir, exist_ok=True)
            steps = []
            for tpl_key, rec in sorted(live_results.items()):
                steps.append({
                    "template_key": tpl_key,
                    "step_id": rec.get("step_id", ""),
                    "operation_type": rec.get("operation_type", ""),
                    "status": rec.get("status", ""),
                    "error": rec.get("error"),
                    "execution_time": rec.get("execution_time", 0),
                })
            payload = {
                "pass": outer_iter + 1,
                "summary": {
                    "live_valid": sum(1 for s in steps if s["status"] == "live_valid"),
                    "failed_bug": sum(1 for s in steps if s["status"] == "failed_bug"),
                    "skipped": sum(
                        1 for s in steps if str(s["status"]).startswith("skipped")
                    ),
                },
                "steps": steps,
            }
            with open(
                os.path.join(debug_dir, "live_execution.json"), "w", encoding="utf-8"
            ) as f:
                json.dump(payload, f, indent=2)
        except Exception:
            logger.debug("Failed to write live_execution.json", exc_info=True)

    def _persistLiveValidationStatus(self, result, failed_keys, n_valid, n_skipped):
        """Reflect the live-execution outcome in the manifest status gate.

        A package with any failed_bug step is downgraded to validation_failed so
        the runtime loader does not surface a step that crashes on use. Skipped
        (precondition/interaction) steps never block — they are validated by
        static checks and recorded for transparency.
        """
        cli_dir = result.get("cli_dir")
        if not cli_dir:
            return
        manifest_path = os.path.join(cli_dir, "manifest.json")
        if not os.path.isfile(manifest_path):
            return
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            manifest["live_validation"] = {
                "passed": not failed_keys,
                "live_valid_count": n_valid,
                "failed_steps": sorted(failed_keys),
                "skipped_count": n_skipped,
            }
            if failed_keys:
                # Preserve the generation status once so a later clean pass can
                # restore it rather than leaving the package stuck as failed.
                if manifest.get("status") != "validation_failed":
                    manifest["_pre_live_status"] = manifest.get("status")
                manifest["status"] = "validation_failed"
            else:
                # Clean live pass: restore the generation status if a prior live
                # run had downgraded it.
                if manifest.get("status") == "validation_failed":
                    manifest["status"] = manifest.pop(
                        "_pre_live_status", "validated_with_warnings"
                    )
                else:
                    manifest.pop("_pre_live_status", None)
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
        except Exception:
            logger.debug("Failed to persist live validation status", exc_info=True)

    def _finalizeCliValidation(self, result, live_results):
        """Finalize the CLI generation UI after validation (static + live).

        Args:
            result: The original generation result dict from the analyzer.
            live_results: Dict from live_validate_templates, or {} if live
                validation was skipped. Only status == 'failed_bug' counts as a
                failure; 'skipped_*' statuses do not block validation.
        """
        failed_keys = [
            tpl_key for tpl_key, tpl_res in live_results.items()
            if tpl_res.get("status") == "failed_bug"
        ]
        n_valid = sum(
            1 for r in live_results.values() if r.get("status") == "live_valid"
        )
        n_skipped = sum(
            1 for r in live_results.values()
            if str(r.get("status", "")).startswith("skipped")
        )
        # Only stamp a live-validation outcome when live execution actually ran;
        # a background-only generation finalize (live_results == {}) must not claim
        # a live result.
        if live_results:
            self._persistLiveValidationStatus(result, failed_keys, n_valid, n_skipped)

        if failed_keys:
            self._cliStatusLabel.setText(
                f"Live validation: {len(failed_keys)} step(s) failing"
            )
            self._cliStatusLabel.setStyleSheet("font-weight: bold; color: red;")
            self._cliProgressDisplay.append(
                "Live validation could not repair: " + ", ".join(sorted(failed_keys))
            )
            self._cliResultGroup.setVisible(True)
            self._cliGeneratorRunning = False
            self._analyzeGenerateButton.setEnabled(True)
            self._refreshCliActionButtons()
            return

        # All validations passed
        has_live = bool(live_results)
        status_text = "Live-Validated ✓" if has_live else "Validated"
        self._cliStatusLabel.setText(status_text)
        self._cliStatusLabel.setStyleSheet("font-weight: bold; color: green;")
        self._cliResultGroup.setVisible(True)
        self._cliGeneratorRunning = False
        self._analyzeGenerateButton.setEnabled(True)
        self._refreshCliActionButtons()

        manifest = result.get("manifest", {})
        stages = manifest.get("stages", [])
        live_info = (
            f" ({n_valid} steps live-executed, {n_skipped} skipped)" if has_live else ""
        )
        self._cliResultSummary.setText(
            f"Generated CLI for {manifest.get('extension_name', '?')} "
            f"(workflow steps: {', '.join(stages)}).{live_info} "
            f"Saved to: {result.get('cli_dir', '?')}"
        )
        self._cliProgressDisplay.append(f"CLI generation complete: {status_text}!")

        # Refresh the extension selector to show updated status, preserving selection
        ext_name = manifest.get("extension_name", "")
        self._onRefreshExtensionsClicked()
        if ext_name:
            for i in range(self._extensionSelector.count):
                if ext_name in self._extensionSelector.itemText(i):
                    self._extensionSelector.setCurrentIndex(i)
                    break

    def _handleCliRevisionComplete(self, result):
        """Handle automatic CLI revision completion (generation-failure fallback)."""
        self._cliGeneratorRunning = False
        self._analyzeGenerateButton.setEnabled(True)

        if result.get("success"):
            self._cliStatusLabel.setText("Revised & Validated")
            self._cliStatusLabel.setStyleSheet("font-weight: bold; color: green;")
            self._cliProgressDisplay.append(
                f"Revision succeeded after {result.get('attempts', '?')} attempts."
            )
        else:
            self._cliStatusLabel.setText("Revision Failed")
            self._cliStatusLabel.setStyleSheet("font-weight: bold; color: red;")
            self._cliProgressDisplay.append(
                f"Revision failed: {result.get('error', 'unknown')}"
            )
        self._refreshCliActionButtons()

    def _handleCliRepairComplete(self, repair):
        """Resume after the LLM template repair (Repair button), then live-validate.

        The off-thread `repair_generated_cli` has rewritten templates from recorded
        runtime API errors + the user's function-error descriptions. Now live-execute
        the rewritten templates to catch any API crash (introduced or pre-existing
        in a precondition-free step) and auto-repair it, then finalize.
        """
        result = getattr(self, "_cliRepairResult", None)
        if repair.get("repaired"):
            self._cliProgressDisplay.append(
                f"Repair rewrote {len(repair.get('repaired', []))} template(s) "
                f"(recorded API errors: {repair.get('runtime_error_count', 0)}, "
                f"function errors: {repair.get('function_error_count', 0)}). "
                "Live-validating…"
            )
            if getattr(self, "_cliFunctionErrorInput", None):
                self._cliFunctionErrorInput.clear()
        else:
            self._cliProgressDisplay.append(
                f"Repair made no template changes ({repair.get('error', 'nothing to fix')})."
            )
        self._cliGeneratorRunning = False
        if result:
            self._runCliLiveValidation(result, outer_iter=0)
        else:
            self._analyzeGenerateButton.setEnabled(True)
            self._refreshCliActionButtons()

    def _handleCliError(self, error_msg):
        """Handle CLI generator error on the main thread."""
        self._cliGeneratorRunning = False
        self._analyzeGenerateButton.setEnabled(True)
        self._cliStatusLabel.setText("Error")
        self._cliStatusLabel.setStyleSheet("font-weight: bold; color: red;")
        self._cliProgressDisplay.append(f"ERROR: {error_msg}")
        self._refreshCliActionButtons()

    def enter(self):
        if (hasattr(self, 'chatHistory') and self.chatHistory is not None and
            self.logic and not self.logic.hasApiKey()):
            self.appendToChat("System", "Please configure your API key in Settings before using the agent.")

    def exit(self):
        pass
