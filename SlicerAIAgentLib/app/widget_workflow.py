from .common import *

#: Answer a node-pick ``user_choice`` step automatically when the scene holds
#: exactly ONE legitimate candidate, instead of making the user confirm a
#: one-item picker. Set False to always show the picker (the behaviour before
#: this existed) -- a one-line revert, in the style of
#: ``WorkflowRouter.ROUTER_ENABLED``. Every code path returns early when False.
#:
#: Deliberately narrow: it fires only where the panel would have rendered the
#: node tree, only when the workflow does not need two nodes of that class, only
#: on an exact class match, and only if the count is still one after the settle
#: window. Everything else -- numeric ranges, sliders, segment pickers,
#: enumerated choices -- is untouched.
AUTO_SELECT_SOLE_NODE_ENABLED = True

#: Settle window before an auto-commit fires. The candidate count is a single
#: instant while the scene may still be filling (a multi-series DICOM import, an
#: async CLI writing its output, a template yielding via processEvents), so the
#: count is re-taken when the timer fires and the commit is abandoned if it is no
#: longer one. It doubles as the visible trace: the one-item picker, naming the
#: node, is on screen for this long before the step advances.
AUTO_SELECT_SOLE_NODE_SETTLE_MS = 600


class WidgetWorkflowMixin:
    # Inert first item for every multi-selection combo: no option is pre-selected, so
    # the user must ACTIVELY pick each selector. Picking a real option is what drives
    # the extension's live combo (and thus activates the corresponding geometry). A
    # pre-selected default would show a value the extension never activated. Excluded
    # from the option list used to match/drive the live combo, so it never drives.
    _MULTI_CHOICE_PLACEHOLDER = "-- Select --"

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

            # "Show brief" toggle + the terse instruction body, hidden until the
            # toggle is clicked. The primary label shows the detailed (clinical)
            # instruction by default; this reveals the terse "what to do" version.
            self._workflowDetailToggle = qt.QToolButton()
            self._workflowDetailToggle.setText("Show brief ▸")
            self._workflowDetailToggle.setAutoRaise(True)
            self._workflowDetailToggle.setStyleSheet("color: #3b6f9e; border: none; padding: 0;")
            self._workflowDetailToggle.clicked.connect(self._onToggleWorkflowDetails)
            self._workflowDetailLabel = qt.QLabel("")
            self._workflowDetailLabel.setWordWrap(True)
            self._workflowDetailLabel.setStyleSheet("color: #444;")
            layout.addWidget(self._workflowDetailToggle)
            layout.addWidget(self._workflowDetailLabel)

            # Persistent notice for a choice the runtime made FOR the user (a
            # sole-candidate node auto-select). It must not live in the action or
            # instruction labels: those are rewritten on every panel render, and
            # the chat log is inside a collapsed Debug group. An automatic pick
            # the surgeon never saw is the one failure mode this feature can
            # have, so the notice survives until the next step opens.
            self._workflowNoticeLabel = qt.QLabel("")
            self._workflowNoticeLabel.setWordWrap(True)
            self._workflowNoticeLabel.setStyleSheet(
                "color: #7a4d00; background: #fff4d6; border: 1px solid #e0c78a; padding: 3px;"
            )
            self._workflowNoticeLabel.setVisible(False)
            layout.addWidget(self._workflowNoticeLabel)

            self._workflowChoiceContainer = qt.QWidget()
            self._workflowChoiceLayout = qt.QHBoxLayout(self._workflowChoiceContainer)
            self._workflowChoiceLayout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self._workflowChoiceContainer)

            controls = qt.QHBoxLayout()
            controls.setObjectName("workflowControlLayout")
            self._workflowDoneButton = qt.QPushButton("Done")
            self._workflowSkipButton = qt.QPushButton("Skip")
            controls.addWidget(self._workflowDoneButton)
            controls.addWidget(self._workflowSkipButton)
            # Left-align Done/Skip. (Exit is not here -- it lives at the right
            # end of the replay row; see _setupWorkflowExitControl.)
            controls.addStretch(1)
            layout.addLayout(controls)
            self.layout.addWidget(self._workflowUserFrame)

        self._workflowBannerLabel = self._workflowTitleLabel
        self._workflowInstructionsLabel = self._workflowInstructionLabel
        self._workflowChoiceButtons = []
        self._workflowChoiceInput = None
        self._workflowChoiceSubmitButton = None
        self._workflowNodeTree = None
        self._workflowNodeTreeSelectButton = None
        self._workflowNodeTreeContainer = None
        self._workflowSegmentsTable = None
        self._workflowSegmentsCombo = None
        self._workflowSegmentsContainer = None
        self._workflowRangeWidget = None
        self._workflowRangeContainer = None
        self._workflowScalarWidget = None
        self._workflowScalarContainer = None
        # step_id -> value inherited from an earlier step, so every re-render of
        # that step's slider seeds identically. Cleared per workflow, never across.
        self._workflowInheritedDefaults = {}

        if getattr(self, "_workflowDoneButton", None):
            self._workflowDoneButton.clicked.connect(self._onWorkflowDoneClicked)
        if getattr(self, "_workflowSkipButton", None):
            self._workflowSkipButton.clicked.connect(self._onWorkflowSkipClicked)

        # Build the replay stepper unconditionally: the workflow frame can be
        # loaded from the .ui file (widget_core.py) instead of built here, in
        # which case the programmatic block above is skipped. This wraps the
        # progress bar with the Back / Forward / Run-from-here buttons.
        self._setupReplayControls()
        # One Exit control, at the right end of that same row. Must run AFTER
        # _setupReplayControls, which is what creates the row it goes into.
        self._setupWorkflowExitControl()
        # Baseline comparison section, inserted directly under the replay row.
        self._setupBaselinePanel()

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

        # Step numbers are NEVER taken from the caller. A hand-built panel dict that
        # copies current_index / completed_steps / total_steps from the previous
        # render shows the PREVIOUS step's numbers beside the NEW step's text -- the
        # cause of a step-17 panel captioned "Step 16 of 27". While a session is live
        # the runtime is the sole authority, so no call site can reintroduce it.
        # Exception: while scrubbing the replay, the runtime itself supplies the
        # checkpoint's PREFIX counters (completed_prefix, not the live completed set),
        # which is the whole point of a preview -- leave those alone.
        _session = self._workflowRuntime.session if self._workflowRuntime else None
        if _session and state.get("active") and _session.preview_index is None:
            state = dict(state)
            state.update(self._workflowRuntime.panel_counters(
                state.get("current_step") or _session.current_step
            ))

        self._currentWorkflowUiState = dict(state or {"active": False})
        # An auto-select notice belongs to the step it was raised on. It must
        # survive that step's repaints (hence its own label) but not outlive it.
        if getattr(self, "_workflowNoticeText", ""):
            if self._currentWorkflowUiState.get("current_step") != getattr(
                self, "_workflowNoticeStep", None
            ):
                self._clearWorkflowNotice()
        if not getattr(self, "_workflowUserFrame", None):
            return

        if not self._currentWorkflowUiState.get("active"):
            self._workflowUserFrame.setVisible(False)
            # The voice layer has to see this too: the panel going inactive is
            # how a run ENDS, and it is the only chance to say so aloud.
            self._voiceOnWorkflowPanelUpdated()
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

        workflow_done = bool(self._currentWorkflowUiState.get("workflow_done")) or \
            self._currentWorkflowUiState.get("raw_status") in ("completed", "cancelled")
        if workflow_done:
            self._releaseModuleSessionTools()
        self._workflowTitleLabel.setText(str(title))
        self._workflowStatusLabel.setText(str(status))
        if total > 0:
            self._workflowProgressBar.setRange(0, total)
            self._workflowProgressBar.setValue(max(0, min(completed, total)))
            self._workflowProgressBar.setFormat(f"{completed}/{total}")
            if workflow_done:
                step_text = f"Complete — {total} of {total} steps done"
            else:
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
        simple = self._currentWorkflowUiState.get("instructions") or ""
        detailed = self._currentWorkflowUiState.get("instructions_detailed") or ""
        # Show the detailed (clinical) instruction as the primary text by default;
        # fall back to the terse simple text when a step has no detailed version.
        primary = detailed or simple
        # Offer the terse "brief" version behind the toggle, only when it adds
        # something (a detailed version exists and the simple text differs).
        brief = simple if (detailed and simple and simple.strip() != detailed.strip()) else ""
        self._workflowActionLabel.setText(str(description))
        self._workflowActionLabel.setVisible(bool(description))
        if workflow_done:
            # Terminal state: show only the completion banner (the action label);
            # no per-step instruction / brief toggle.
            self._workflowInstructionLabel.setVisible(False)
            self._renderWorkflowDetails("")
        else:
            self._workflowInstructionLabel.setText(str(primary))
            self._workflowInstructionLabel.setVisible(bool(primary))
            self._renderWorkflowDetails(brief)

        self._renderWorkflowChoices(self._currentWorkflowUiState)
        self._updateReplayControls(self._currentWorkflowUiState)

        self._workflowDoneButton.setVisible(bool(self._currentWorkflowUiState.get("can_done")))
        self._workflowSkipButton.setVisible(bool(self._currentWorkflowUiState.get("can_skip")))
        self._workflowDoneButton.setEnabled(bool(self._currentWorkflowUiState.get("can_done")))
        self._workflowSkipButton.setEnabled(bool(self._currentWorkflowUiState.get("can_skip")))
        # Exit is unconditional while the panel is up. It is the only way out of
        # a guided run now, so it must not be keyed on the step: a completed
        # workflow, a step with no controls, and the panel a dispatch error
        # leaves behind (no current_step at all) each need it most.
        self._setWorkflowExitVisible(True)
        done_label = self._currentWorkflowUiState.get("done_label") or "Done"
        if self._currentWorkflowUiState.get("review_selection") and done_label == "Done":
            # A review checkpoint's action is confirmation, not task completion.
            done_label = "Confirm"
        self._workflowDoneButton.setText(str(done_label) if self._currentWorkflowUiState.get("can_done") else "Done")
        self._updateInteractionCountGate()
        # Last, and only when the microphone is open: the voice layer reads the
        # state this method just finished writing, and speaks a step's guidance
        # once per step OCCURRENCE (this method is a repaint event that runs
        # several times per opening -- see _voiceAnnounceKey).
        self._voiceOnWorkflowPanelUpdated()

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
                # A null value means the label IS the value (see _renderWorkflowChoices).
                if value is None:
                    value = label
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
            "can_done": result_type in ("interactive", "mixed", "user_review"),
            "review_selection": result_type == "user_review",
            "review_table": result.get("review_table") or {},
            "can_skip": bool(result.get("is_optional")),
        }

    # Qt/Slicer selection-widget class -> renderer family. Keyed purely on the
    # class the *original* extension uses (recorded by the pipeline), so the
    # reproduced panel matches the source UI. Only the ``segments_table`` family
    # changes dispatch precedence; ``node_tree`` / ``choice`` intentionally defer
    # to the existing heuristic (which already produces the same widget for those
    # steps), so node-selection extensions (Orbit/BRP) are byte-identical.
    _WORKFLOW_WIDGET_FAMILIES = {
        "qMRMLSegmentsTableView": "segments_table",
        "qMRMLNodeComboBox": "node_tree",
        "qMRMLSubjectHierarchyComboBox": "node_tree",
        "qMRMLSubjectHierarchyTreeView": "node_tree",
        "qMRMLCheckableNodeComboBox": "node_tree",
        "QComboBox": "choice",
        "ctkComboBox": "choice",
        "ctkRangeWidget": "range_slider",
        "qMRMLRangeWidget": "range_slider",
        "ctkDoubleRangeSlider": "range_slider",
        "ctkRangeSlider": "range_slider",
        "ctkSliderWidget": "scalar_slider",
        "qMRMLSliderWidget": "scalar_slider",
        "ctkDoubleSlider": "scalar_slider",
        "ctkSliderSpinBoxWidget": "scalar_slider",
    }

    @staticmethod
    def _workflowWidgetFamily(widget_class):
        """Render family for the original selection widget class, or "" (unknown)
        to defer to the heuristic. Generic: no extension/step-specific names."""
        return WidgetWorkflowMixin._WORKFLOW_WIDGET_FAMILIES.get(
            str(widget_class or "").strip(), ""
        )

    @staticmethod
    def _workflowPrimaryLabel(state, default):
        """Per-step override for a step's primary advance button (Done/Confirm/Set).

        Returns the user-authored label from the "Step instructions" panel
        (``state['primary_label']``, sourced from step_instructions.json) when
        non-empty, else the built-in default. Purely presentational.
        """
        try:
            override = str((state or {}).get("primary_label") or "").strip()
        except Exception:
            override = ""
        return override or default

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
        if getattr(self, "_workflowNodeTree", None) is not None:
            # Drop the selection-change observer before destroying the tree, so it
            # cannot dangle / accumulate across steps.
            try:
                self._workflowNodeTree.currentItemChanged.disconnect(self._onWorkflowNodeTreeSelectionChanged)
            except Exception:
                pass
            self._workflowNodeTree = None
        self._workflowNodeCandidates = None
        self._workflowNodeTreeSelectButton = None
        if getattr(self, "_workflowNodeTreeContainer", None) is not None:
            # The container owns the tree + Select button; reparenting it to None
            # destroys all three together.
            if self._workflowChoiceLayout is not None:
                self._workflowChoiceLayout.removeWidget(self._workflowNodeTreeContainer)
            self._workflowNodeTreeContainer.setParent(None)
            self._workflowNodeTreeContainer = None
        if getattr(self, "_workflowSegmentsCombo", None) is not None:
            # Drop the segmentation-picker observer before destroying it (mirrors
            # the node-tree teardown).
            try:
                self._workflowSegmentsCombo.currentNodeChanged.disconnect(self._onWorkflowSegmentsComboChanged)
            except Exception:
                pass
            self._workflowSegmentsCombo = None
        self._workflowSegmentsTable = None
        if getattr(self, "_workflowSegmentsContainer", None) is not None:
            # The container owns the segments table (+ optional combo + Done button);
            # reparenting it to None destroys them together.
            if self._workflowChoiceLayout is not None:
                self._workflowChoiceLayout.removeWidget(self._workflowSegmentsContainer)
            self._workflowSegmentsContainer.setParent(None)
            self._workflowSegmentsContainer = None
        if getattr(self, "_workflowSegmentNameCombo", None) is not None:
            # Drop the live-preview observer before destroying the combo.
            try:
                self._workflowSegmentNameCombo.currentIndexChanged.disconnect(self._onWorkflowSegmentNamePreview)
            except Exception:
                pass
        self._workflowSegmentNameCombo = None
        if getattr(self, "_workflowSegmentNameContainer", None) is not None:
            # The container owns the name combobox + Select button; reparenting to
            # None destroys them together.
            if self._workflowChoiceLayout is not None:
                self._workflowChoiceLayout.removeWidget(self._workflowSegmentNameContainer)
            self._workflowSegmentNameContainer.setParent(None)
            self._workflowSegmentNameContainer = None
        if getattr(self, "_workflowRangeWidget", None) is not None:
            # Drop the live-preview observers before destroying the range widget.
            for _sig in ("minimumValueChanged", "maximumValueChanged"):
                try:
                    getattr(self._workflowRangeWidget, _sig).disconnect(self._onWorkflowRangePreview)
                except Exception:
                    pass
            self._workflowRangeWidget = None
        if getattr(self, "_workflowRangeContainer", None) is not None:
            # The container owns the range slider + Set button; reparenting to None
            # destroys them together.
            if self._workflowChoiceLayout is not None:
                self._workflowChoiceLayout.removeWidget(self._workflowRangeContainer)
            self._workflowRangeContainer.setParent(None)
            self._workflowRangeContainer = None
        if getattr(self, "_workflowScalarWidget", None) is not None:
            # Drop the live-preview observer before destroying the scalar slider.
            try:
                self._workflowScalarWidget.valueChanged.disconnect(self._onWorkflowScalarPreview)
            except Exception:
                pass
            self._workflowScalarWidget = None
        if getattr(self, "_workflowScalarContainer", None) is not None:
            # The container owns the single-value slider + Set button; reparenting to
            # None destroys them together.
            if self._workflowChoiceLayout is not None:
                self._workflowChoiceLayout.removeWidget(self._workflowScalarContainer)
            self._workflowScalarContainer.setParent(None)
            self._workflowScalarContainer = None
        for button in getattr(self, "_workflowChoiceButtons", []):
            if self._workflowChoiceLayout is not None:
                self._workflowChoiceLayout.removeWidget(button)
            button.setParent(None)
        self._workflowChoiceButtons = []
        if getattr(self, "_workflowReviewContainer", None) is not None:
            # The container owns the read-only results table; reparenting to None
            # destroys it.
            if self._workflowChoiceLayout is not None:
                self._workflowChoiceLayout.removeWidget(self._workflowReviewContainer)
            self._workflowReviewContainer.setParent(None)
            self._workflowReviewContainer = None
        self._workflowMultiChoiceCombos = {}
        # Cleared with the combos it points at. The container below DESTROYS
        # them (reparent to None), so a surviving ordered list would hand
        # _onWorkflowMultiChoiceConfirmed freed C++ objects on the next
        # multi-selection step -- a crash in PythonQt, not an exception.
        self._workflowMultiChoiceOrdered = []
        if getattr(self, "_workflowMultiChoiceContainer", None) is not None:
            # The container owns the per-selector combos + Confirm; reparenting to
            # None destroys them together.
            if self._workflowChoiceLayout is not None:
                self._workflowChoiceLayout.removeWidget(self._workflowMultiChoiceContainer)
            self._workflowMultiChoiceContainer.setParent(None)
            self._workflowMultiChoiceContainer = None
        self._nativeWidgetLiveTable = None
        self._nativeWidgetComboCol = None
        self._nativeWidgetRowCombos = []
        if getattr(self, "_workflowNativeWidgetContainer", None) is not None:
            # The container owns the reproduced per-row-combo table + Confirm.
            if self._workflowChoiceLayout is not None:
                self._workflowChoiceLayout.removeWidget(self._workflowNativeWidgetContainer)
            self._workflowNativeWidgetContainer.setParent(None)
            self._workflowNativeWidgetContainer = None

        choices = state.get("choices") or []
        step_id = state.get("current_step")
        needs_input = bool(state.get("needs_choice_input"))
        review = bool(state.get("review_selection"))
        native_widget = bool(state.get("native_widget"))
        if self._workflowChoiceContainer is not None:
            self._workflowChoiceContainer.setVisible(
                bool(choices) or needs_input or review or native_widget)
        if self._workflowChoiceLayout is None:
            return
        if native_widget:
            # Reproduce the extension's OWN selection widget (its module panel is
            # entered invisibly, so the real widget is never on screen). Own Confirm
            # button writes selections back to the live widget and advances.
            self._renderWorkflowNativeWidget(state)
            return
        if review:
            # Review checkpoint: show the generated results read-only; the existing
            # Done button (relabeled Confirm) advances. No choice input.
            self._renderWorkflowReviewTable(state)
            return
        if state.get("multi_choice") and needs_input:
            # Multi-selection step: every selector on one form, one Confirm,
            # committed together as a {param: value} dict.
            if self._renderWorkflowMultiChoiceForm(state):
                return
        if not choices and needs_input:
            default_value = state.get("default_value")
            # The original extension's selection widget class (recorded by the
            # pipeline) is authoritative for the render family, so the reproduced
            # panel matches the source UI rather than a node_class-inferred guess.
            family = self._workflowWidgetFamily(state.get("source_widget_class"))
            if family == "segments_table":
                # Source widget was a qMRMLSegmentsTableView: reproduce it so the
                # user unticks individual segments/fragments exactly like the
                # extension. Authoritative — if no segmentation resolves we fall to
                # the free-text box below, never the generic node tree (which would
                # silently substitute whole-node selection for segment selection).
                if self._renderWorkflowSegmentsTable(state):
                    return
            else:
                # Segment-selection step (original extension used a qMRMLSegmentsTableView):
                # let the user untick individual segments/fragments on a segmentation node
                # exactly like the source. More specific than the generic node tree, so it
                # takes precedence; falls through if no segmentation resolves.
                if state.get("segment_selection") and self._renderWorkflowSegmentsTable(state):
                    return
                # Segment-NAME selection step (the source used a content combobox of
                # a segmentation's segment names, e.g. a "Fragment" box): offer a
                # single-pick dropdown of those names instead of a scene-node tree.
                # More specific than the node tree, so it takes precedence; falls
                # through (to free-text, never the node tree) if none resolves.
                if state.get("segment_name_selection") and self._renderWorkflowSegmentNamePicker(state):
                    return
                # Single-value slider step (the source used a single-handle numeric
                # control, e.g. an extension's "Crop radius (mm)" ctkSliderWidget):
                # render ONE draggable slider seeded from the extension's live widget
                # / captured .ui limits, instead of a min/max range bar or free-text
                # box. Source-widget-authoritative, so a single-handle control never
                # renders as a two-handle range even if value_kind drifted to "range".
                if state.get("scalar_selection") and self._renderWorkflowScalarSlider(state):
                    return
                # Numeric RANGE step (the source used a double-handled range widget,
                # e.g. the Segment Editor Threshold range): render a draggable
                # min/max slider seeded from the live target / source volume, instead
                # of a literal button or free-text box. More specific than the node
                # tree; falls through to free-text if sensible limits can't resolve.
                if state.get("range_selection") and self._renderWorkflowRangeSlider(state):
                    return
                # Node-selection step: offer a Data-module-style subject-hierarchy tree
                # of the matching scene nodes (with the native eye / opacity / color
                # controls) instead of a free-text box, so the user can identify which
                # node is which before picking. Falls back to the text box only if no
                # matching node exists. (The LLM auto-match still runs first and may
                # auto-advance before this UI is ever shown.)
                node_class = state.get("node_class")
                if node_class and self._renderWorkflowNodeTree(state, node_class, default_value):
                    return
            self._workflowChoiceInput = qt.QLineEdit()
            input_label = state.get("input_label") or state.get("choice_label") or "value"
            self._workflowChoiceInput.setPlaceholderText(f"Enter {input_label}")
            if default_value is not None:
                self._workflowChoiceInput.setText(str(default_value))
            self._workflowChoiceInput.returnPressed.connect(self._onWorkflowChoiceInputSubmitted)

            self._workflowChoiceSubmitButton = qt.QPushButton(self._workflowPrimaryLabel(state, "Set"))
            self._workflowChoiceSubmitButton.setToolTip("Use this value")
            self._workflowChoiceSubmitButton.clicked.connect(self._onWorkflowChoiceInputSubmitted)

            self._workflowChoiceLayout.addWidget(self._workflowChoiceInput, 1)
            self._workflowChoiceLayout.addWidget(self._workflowChoiceSubmitButton)
            self._workflowChoiceInput.setVisible(True)
            self._workflowChoiceSubmitButton.setVisible(True)
            return
        if not choices:
            return

        choice_overrides = state.get("choice_label_overrides") or {}
        for choice in choices:
            base_label = str(choice.get("label") or choice.get("value") or "Choice")
            value = choice.get("value", base_label)
            # A Yes/No decision (branch_op loop/guard) carries its accept/decline
            # polarity in the LABEL, but the LLM attaches an inconsistent value --
            # null, or an arbitrary string ("done"/"not_done"). Map a Yes/No label
            # to True/False so the loop-polarity reader normalizes it. Without this
            # the value never matches the boolean exit_value and the loop can't
            # exit (Yes keeps looping back). Enumerated options (Left/Right, …) keep
            # their own values -- only exact Yes/No synonyms are coerced.
            _bl = base_label.strip().lower()
            if _bl in ("yes", "true", "y"):
                value = True
            elif _bl in ("no", "false", "n"):
                value = False
            elif value is None:
                value = base_label
            # Per-step label override (edited in the "Step instructions" panel),
            # keyed by the choice value; falls back to the recorded label.
            label = str(choice_overrides.get(str(value)) or base_label)
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

    def _renderWorkflowDetails(self, brief):
        """Show the 'Show brief' toggle when a terse instruction is available.

        The primary instruction label now shows the detailed (clinical) text by
        default; this toggle reveals the terse "what to do now" version.
        """
        toggle = getattr(self, "_workflowDetailToggle", None)
        label = getattr(self, "_workflowDetailLabel", None)
        if toggle is None or label is None:
            return
        brief = str(brief or "")
        self._workflowDetailText = brief
        if not brief:
            toggle.setVisible(False)
            label.setVisible(False)
            return
        # New step: show the toggle collapsed (brief hidden) by default.
        toggle.setVisible(True)
        toggle.setText("Show brief ▸")
        label.setText(brief)
        label.setVisible(False)

    def _onToggleWorkflowDetails(self):
        label = getattr(self, "_workflowDetailLabel", None)
        toggle = getattr(self, "_workflowDetailToggle", None)
        if label is None or toggle is None:
            return
        expanded = not label.visible
        label.setVisible(expanded)
        toggle.setText("Hide brief ▾" if expanded else "Show brief ▸")

    def _showWorkflowInteraction(self, result):
        """Show an interactive or mixed workflow wait state."""
        self._updateWorkflowPanel(result)

    def _showWorkflowChoice(self, result):
        """Show a user-choice workflow step as buttons when choices are known."""
        self._updateWorkflowPanel(result)
        # A user_choice step just OPENED. This method's sole caller,
        # _displayWorkflowChoice, is the funnel for every path that presents one,
        # which makes it the only "opened" event -- _updateWorkflowPanel /
        # _renderWorkflowChoices are repaint events and run several times per
        # opening. Runs after the panel update so _currentWorkflowUiState holds
        # the mapped state and the picker is already on screen behind the notice.
        self._maybeAutoSelectSoleNode()

    def _clearWorkflowPanel(self):
        """Hide and reset the user-facing workflow panel."""
        self._currentWorkflowUiState = {"active": False}
        self._taskWorkflowPanelActive = False
        # Per-workflow, never across: a later run's step ids would otherwise
        # inherit a stale value from the previous run.
        self._workflowInheritedDefaults = {}
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
        self._renderWorkflowDetails("")
        self._renderWorkflowChoices({})
        self._updateReplayControls({})
        self._workflowDoneButton.setVisible(False)
        self._workflowSkipButton.setVisible(False)
        self._setWorkflowExitVisible(False)
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

    # ------------------------------------------------------------------
    # Exit: close and reset the guided pipeline
    #
    # Replaces the per-step Cancel button. Cancel was a workflow ACTION -- it
    # dispatched ``user_action="cancel"`` through the runtime, so it only worked
    # where the runtime could take an action, and it was hidden exactly where a
    # user most needs a way out (a completed run, a step with no controls, a
    # panel left behind by a dispatch error). Exit is a LOCAL reset instead: it
    # never asks the runtime for permission, so it works in every one of those
    # states, and it puts the widget back to the state it had before any
    # workflow started so the next prompt begins from a clean session.
    #
    # It DOES close the MRML scene -- see EXIT_CLOSES_SCENE below. It used not
    # to, on the principle that exiting a UI is not consent to delete data, and
    # that principle has not changed: what changed is that the deletion is now
    # asked for explicitly in the dialog, and that leaving the scene up was
    # itself unsafe. A run left its nodes behind for the next procedure to find
    # by name, and closing the scene is also the only thing that reliably
    # re-binds the driven extension (onSceneEndClose -> re-enter()), so
    # "remember to close the scene" was a manual step whose omission silently
    # changed the next run.
    # ------------------------------------------------------------------
    #: Ask before closing a run. Shown UNCONDITIONALLY -- including when there is
    #: no progress to lose -- because the dialog is also where the user chooses
    #: whether to save, and saving is the main thing Exit does on a *finished*
    #: workflow. Set False for a one-click exit that always saves AND closes the
    #: scene without asking.
    EXIT_CONFIRM_ENABLED = True

    #: Tried in order; the first that resolves is used. Slicer's icon resources
    #: vary between versions, and a null QIcon renders as an invisible button,
    #: so a Qt built-in backs them up and plain text backs that up.
    _EXIT_ICON_RESOURCES = (
        ":/Icons/Small/SlicerCloseScene.png",
        ":/Icons/SlicerCloseScene.png",
        ":/Icons/Cancel.png",
    )

    def _setupWorkflowExitControl(self):
        """Add the Exit button to the right end of the replay row. Idempotent.

        Added programmatically rather than in the .ui, for the same reason the
        replay stepper is: the frame is built either from the .ui file or from
        the fallback above, and a widget declared in only one of them silently
        disappears in the other.

        It goes LAST in ``[◀] [progress] [▶] [▷] [⚖] [✕]``, i.e. immediately
        right of "Run from here" whenever the baseline toggle is hidden (which
        it is on every step the pipeline does not answer with generated code).
        Anchoring it to the row's right edge rather than adjacent to a specific
        button keeps it in one place instead of shifting as ⚖ appears and
        disappears. Icon-only like its neighbours: a text label would add its
        width to the row's minimum and can force the module panel wider (see
        _applyWidthSafeLabels). Falls back to its own bottom row if the replay
        row was never built.
        """
        if getattr(self, "_workflowExitButton", None) is not None:
            return
        frame = getattr(self, "_workflowUserFrame", None)
        if frame is None:
            return

        button = qt.QToolButton()
        icon = None
        for resource in self._EXIT_ICON_RESOURCES:
            icon = self._nativeIcon(resource)
            if icon is not None:
                break
        if icon is None:
            try:
                icon = slicer.app.style().standardIcon(qt.QStyle.SP_DialogCloseButton)
                if icon.isNull():
                    icon = None
            except Exception:
                icon = None
        if icon is not None:
            button.setIcon(icon)
        else:
            button.setText("✕")
        button.setToolTip(
            "Exit: close this guided workflow, optionally save its record, and "
            "close the scene, so the next request starts from a clean slate."
        )
        button.setAutoRaise(True)
        button.clicked.connect(self._onWorkflowExitClicked)

        row = getattr(self, "_replayControlsRow", None)
        row_layout = row.layout() if row is not None else None
        if row_layout is not None:
            row_layout.addWidget(button)
            self._workflowExitRow = None
        else:
            # Replay row unavailable (its setup bails when the progress bar is
            # not found): fall back to a right-aligned row of our own, so the
            # only way out of a guided run is never missing.
            fallback = qt.QWidget()
            fallback_layout = qt.QHBoxLayout(fallback)
            fallback_layout.setContentsMargins(0, 0, 0, 0)
            fallback_layout.addStretch(1)
            fallback_layout.addWidget(button)
            frame_layout = frame.layout()
            if frame_layout is None:
                return
            frame_layout.addWidget(fallback)
            self._workflowExitRow = fallback
            fallback.setVisible(False)
        self._workflowExitButton = button
        button.setVisible(False)

    def _setWorkflowExitVisible(self, visible):
        """Show/hide Exit. Not driven by _updateReplayControls, which touches
        only the three stepper buttons and the ⚖ toggle -- Exit is available
        whenever the panel is up, including where replay is not."""
        visible = bool(visible)
        button = getattr(self, "_workflowExitButton", None)
        row = getattr(self, "_workflowExitRow", None)
        try:
            if button is not None:
                button.setVisible(visible)
            if row is not None:
                row.setVisible(visible)
        except Exception:
            logger.debug("Exit control visibility failed", exc_info=True)

    #: The three outcomes of the Exit confirmation.
    #:
    #: Three, not two, because "leave the panel" and "keep the record" are
    #: independent decisions and a Yes/No dialog welds them together. Saving
    #: writes a full copy of the scene, which on a segmented CT is hundreds of
    #: megabytes and tens of seconds; a user who just wants out of a panel --
    #: after a mis-started run, a scratch experiment, a procedure they are about
    #: to redo -- had no way to say so, and their only alternative was to sit
    #: through a save and delete the folder afterwards.
    EXIT_SAVE = "save"
    EXIT_NO_SAVE = "nosave"
    EXIT_CANCEL = "cancel"
    #: The dialog could not be shown, so the exit proceeds on an ASSUMED answer.
    #: Same as EXIT_SAVE for the workflow, but the scene is left open: an
    #: assumption is enough to close a panel and not enough to discard a scene.
    EXIT_SAVE_UNCONFIRMED = "save_unconfirmed"

    #: Whether pressing Exit also CLOSES the scene (both answers, not just save).
    #:
    #: It does, because "exit the workflow" and "close the scene" were never
    #: independent in practice: the next run of any procedure starts by loading
    #: its own data, so a scene left holding the previous run's segmentations,
    #: models and markups is never what the user wants -- and, worse, is not
    #: inert. A leftover node with the name the next run's template looks up is
    #: silently adopted by it, and every extension this runtime drives keeps
    #: Python references to the nodes it made, which only a scene close (plus the
    #: re-``enter()`` it forces, see WidgetStreamingMixin.onSceneEndClose)
    #: reliably breaks. Closing it here is also what makes the manual step the
    #: user had to remember unnecessary, and a forgotten manual step is exactly
    #: how one run's leftovers reach the next.
    #:
    #: Set False to restore the previous behaviour (Exit leaves the scene alone).
    EXIT_CLOSES_SCENE = True

    def _onWorkflowExitClicked(self):
        choice = self.EXIT_SAVE
        if self.EXIT_CONFIRM_ENABLED:
            choice = self._askExitChoice()
        if choice == self.EXIT_CANCEL:
            return
        self._resetGuidedSession(
            reason="user_exit",
            save=(choice != self.EXIT_NO_SAVE),
            # Every answer the user actually gave closes the scene; an assumed
            # one does not. EXIT_CONFIRM_ENABLED=False is a deliberate
            # developer opt-out of being asked, so it counts as an answer.
            close_scene=(choice != self.EXIT_SAVE_UNCONFIRMED),
        )

    def _askExitChoice(self):
        """Exit and save / Exit without saving / Cancel -> one of ``EXIT_*``.

        A three-button ``QMessageBox`` rather than ``confirmYesNoDisplay``,
        which offers exactly two.

        The answer is read back as a ROLE, never as button identity or position.
        Position is wrong because Qt reorders the buttons per platform
        convention (the same three sit in a different order on Windows, macOS
        and KDE), and identity is wrong because PythonQt can return a fresh
        Python wrapper for the same underlying ``QAbstractButton`` -- so
        ``clickedButton() is save`` may be False for the button just clicked.
        ``buttonRole()`` resolves the C++ pointer inside Qt, so neither matters.

        On failure the fallback depends on WHERE it failed. Before the dialog
        appeared, ``EXIT_SAVE_UNCONFIRMED`` -- a full, saving exit, because a
        button that silently does nothing would be worse, but with the scene
        left open, because closing it is the half of Exit that destroys
        something and no answer was actually given. After the user answered,
        ``EXIT_CANCEL``: their answer is unknown, and changing nothing is the
        only option that cannot act against it (they can press Exit again).
        """
        answered = False
        try:
            headline, detail = self._exitConfirmMessage()
            box = qt.QMessageBox(slicer.util.mainWindow())
            box.setIcon(qt.QMessageBox.Question)
            box.setWindowTitle("Exit guided workflow")
            box.setText(headline)
            box.setInformativeText(detail)
            save = box.addButton("Exit and save", qt.QMessageBox.AcceptRole)
            box.addButton("Exit without saving", qt.QMessageBox.DestructiveRole)
            cancel = box.addButton("Cancel", qt.QMessageBox.RejectRole)
            # Saving is the default: it is the non-destructive answer, and
            # Return should not be the key that discards a run's record.
            box.setDefaultButton(save)
            box.setEscapeButton(cancel)
            # BEFORE exec_(), which is Slicer's own idiom (slicer.util.messageBox
            # does the same). Without it the dialog is only hidden, never
            # destroyed -- it stays parented to the main window until Slicer
            # quits, and Windows 10's taskbar peek re-shows such windows when
            # hovering the Slicer icon. Placed here rather than after the
            # read-back so a failure below cannot skip it.
            box.deleteLater()
            box.exec_()
            answered = True
            # None when the dialog was dismissed without a button (the window's
            # close box); buttonRole(None) is InvalidRole, which lands on Cancel.
            role = box.buttonRole(box.clickedButton())
        except Exception:
            logger.debug("Exit choice dialog failed", exc_info=True)
            return self.EXIT_CANCEL if answered else self.EXIT_SAVE_UNCONFIRMED
        if role == qt.QMessageBox.DestructiveRole:
            return self.EXIT_NO_SAVE
        if role == qt.QMessageBox.AcceptRole:
            return self.EXIT_SAVE
        return self.EXIT_CANCEL

    def _exitConfirmMessage(self):
        """``(headline, detail)`` for the Exit dialog.

        Deliberately terse: this is a confirmation the user meets often, so it
        states the three facts that could change their answer (unfinished
        progress is lost, the scene is untouched whichever button is pressed,
        and what saving actually writes) and nothing else. The long-form
        explanation of what lands in Statistic/ belongs in the docs, not in
        front of someone who has already decided.

        Still shown when there is no progress to lose, because saving the run's
        timing and scene is the main thing this button does on a finished
        workflow -- a dialog seen only when something is about to be destroyed
        would never mention it on the path taken most.
        """
        from SlicerAIAgentLib import RunLog
        lines = []
        if self._guidedRunHasProgress():
            session = self._workflowRuntime.session
            done = len(getattr(session, "completed_steps", None) or [])
            total = int(self._currentWorkflowUiState.get("total_steps") or 0)
            progress = f"{done} of {total} steps" if total else f"{done} step(s)"
            lines.append(f"Not finished ({progress}) - progress cannot be resumed.")
        # Both buttons are spelled out, because BOTH destroy something: one
        # deletes the run folder, and both now close the scene. The run folder is
        # written incrementally while the workflow runs, so declining to save is
        # a removal, not a non-write -- a dialog that only described what saving
        # adds would be describing the harmless half. And the scene line has to
        # come first and say "closed", because that is the sentence that decides
        # whether the user presses Exit at all.
        if self.EXIT_CLOSES_SCENE:
            lines.append(
                "The scene is CLOSED either way, so the next workflow starts "
                "clean. Anything in it that you have not saved yourself is lost."
            )
        else:
            lines.append("Your scene is left untouched either way.")
        lines.append(
            f"Save: adds timing.txt and a copy of the scene (can be large) "
            f"under logs/{self._statisticRunName()}/{RunLog.STATISTIC_DIRNAME}/."
        )
        lines.append(
            f"Without saving: DELETES logs/{self._statisticRunName()}/ and this "
            f"run's baseline folders. No record of the run is kept."
        )
        return "Exit this guided workflow?", "\n".join(lines)

    # ------------------------------------------------------------------
    # Statistics written when a run is closed
    # ------------------------------------------------------------------
    def _runRootDir(self):
        """``logs/<run>/`` -- the folder holding ``runtime/`` and ``Statistic/``.

        Derived defensively rather than read straight off ``_currentRunRoot``:
        that attribute is set when the folder is created, but this is also
        reached from the fallback path in ``_getCurrentLogDir``, and from run
        folders written before the two-subfolder layout existed (whose
        ``_currentLogDir`` IS the root).
        """
        from SlicerAIAgentLib import RunLog
        root = getattr(self, "_currentRunRoot", None)
        if root:
            return str(root)
        log_dir = str(self._getCurrentLogDir() or "").rstrip("/\\")
        if os.path.basename(log_dir) == RunLog.RUNTIME_DIRNAME:
            return os.path.dirname(log_dir)
        return log_dir

    def _statisticRunName(self):
        """Name shared by this run's timing file and its scene folder."""
        root = self._runRootDir()
        if root:
            return os.path.basename(str(root).rstrip("/\\"))
        session = getattr(getattr(self, "_workflowRuntime", None), "session", None)
        return getattr(session, "workflow_id", "") or "run"

    def _statisticDir(self):
        """``logs/<run>/Statistic/`` -- beside ``runtime/``, not inside it."""
        from SlicerAIAgentLib import RunLog
        return RunLog.ensure_dir(os.path.join(
            self._runRootDir(), RunLog.STATISTIC_DIRNAME
        ))

    #: File name of the flat scene save. Fixed rather than derived from the
    #: scene's own name, so a script walking logs/*/Statistic/scene/ knows where
    #: the MRML file is without looking.
    SCENE_FILE_NAME = "scene.mrml"

    def _saveSceneFlat(self, directory, progress=None):
        """Save the scene as ONE flat folder: ``scene.mrml`` beside every node's file.

        This is what File > Save Data produces with every row pointed at one
        directory, which is the layout asked for. ``slicer.util.saveScene(<dir>)``
        cannot give it: a directory path routes to
        ``qSlicerSceneWriter::writeToDirectory`` ->
        ``SaveSceneToSlicerDataBundleDirectory``, which builds ``Data/`` and
        ``private/`` subfolders.

        Mirrors ``qSlicerSaveDataDialogPrivate`` exactly: skip nodes that are not
        storable, are hidden from editors, or are not ``SaveWithScene``; give
        each remaining node a default storage node and skip it if it does not
        need one (it is stored inside the scene); name its file
        ``<sanitised node name>.<default write extension>``; and save the nodes
        FIRST, the scene last, so the ``.mrml`` records the paths the nodes were
        just written to.

        Every mutation it makes to the live scene -- storage-node file names, the
        scene URL and root directory, and the storable-modified flags that
        writing clears -- is undone afterwards, so the surgeon's own File > Save
        Data still offers their chosen directory and still shows their work as
        unsaved. Returns ``(files_written, note)``.

        ``progress(done, total, name)`` is called once per candidate node -- on
        the FULL storable list, including the ones filtered out below, so the bar
        advances monotonically instead of stalling through a run of skipped
        nodes. Optional and never allowed to fail the save.
        """
        scene = slicer.mrmlScene
        original_url = scene.GetURL()
        original_root = scene.GetRootDirectory()
        restore = {}          # storage node ID -> (node, name, [list], URI, crop)
        used_names = set()
        written, skipped, failed = 0, 0, []
        try:
            # The root directory FIRST, before a single node is written. Every
            # path a storage node records while writing is relativised against
            # scene->GetRootDirectory() AS IT STANDS AT THAT MOMENT, not against
            # the .mrml written afterwards: vtkMRMLVolumeArchetypeStorageNode::
            # UpdateFileList (called unconditionally from WriteDataInternal)
            # stores its file-list entries relative to it, and
            # vtkMRMLStorageNode::WriteXML writes an already-relative entry out
            # verbatim. Leave the user's own root in place and a volume's
            # fileListMember paths end up relative to THEIR folder while the
            # scene resolves them from this one -- so the saved scene does not
            # reload. Both references set it first for exactly this reason
            # (qSlicerSaveDataDialogPrivate::save, and
            # vtkMRMLScene::SaveSceneToSlicerDataBundleDirectory). The `finally`
            # below puts the user's root back.
            scene.SetRootDirectory(str(directory).replace("\\", "/"))
            nodes = scene.GetNodesByClass("vtkMRMLStorableNode")
            nodes.UnRegister(None)
            candidates = nodes.GetNumberOfItems()
            for index in range(candidates):
                node = nodes.GetItemAsObject(index)
                if progress is not None:
                    try:
                        progress(index, candidates,
                                 (node.GetName() if node is not None else "") or "")
                    except Exception:
                        logger.debug("Scene-save progress callback failed", exc_info=True)
                if node is None or node.GetHideFromEditors() or not node.GetSaveWithScene():
                    skipped += 1
                    continue
                storage = node.GetStorageNode()
                if storage is None:
                    if not node.AddDefaultStorageNode():
                        skipped += 1
                        continue
                    storage = node.GetStorageNode()
                if storage is None:
                    skipped += 1      # no storage node needed: lives in the scene
                    continue
                # The dialog drops nodes with no writer rather than listing them;
                # without this they would be reported as save failures.
                try:
                    if slicer.app.coreIOManager().fileWriterFileType(node) == "NoFile":
                        skipped += 1
                        continue
                except Exception:
                    logger.debug("fileWriterFileType probe failed", exc_info=True)
                name = self._safeFileName(node.GetName() or node.GetID() or "node")
                extension = storage.GetDefaultWriteFileExtension() or ""
                if extension and not extension.startswith("."):
                    extension = "." + extension
                candidate = f"{name}{extension}"
                # Two nodes may share a name; the dialog would collide and warn,
                # and a silent overwrite here would lose one of them.
                suffix = 1
                while candidate.lower() in used_names:
                    suffix += 1
                    candidate = f"{name}_{suffix}{extension}"
                used_names.add(candidate.lower())
                # Writing mutates more than the file name, so snapshot all of
                # it: a volume write runs UpdateFileList, which RESETS the
                # storage node's file-name list and repopulates it with paths
                # into this folder (so a DICOM series' original slice list would
                # be destroyed, and the bogus entries would later be written
                # into the surgeon's OWN .mrml as fileListMember);
                # qSlicerNodeWriter::write clears the URI; and the segmentation
                # writer forces CropToMinimumExtent off because
                # slicer.util.saveNode supplies no such property. Keyed by
                # storage node so two storables sharing one cannot record each
                # other's already-repointed path.
                key = storage.GetID()
                if key not in restore:
                    restore[key] = (
                        storage,
                        storage.GetFileName(),
                        [storage.GetNthFileName(i)
                         for i in range(storage.GetNumberOfFileNames())],
                        storage.GetURI(),
                        (storage.GetCropToMinimumExtent()
                         if hasattr(storage, "GetCropToMinimumExtent") else None),
                    )
                path = os.path.join(directory, candidate)
                try:
                    if slicer.util.saveNode(node, path):
                        written += 1
                    else:
                        failed.append(candidate)
                except Exception as exc:
                    logger.debug("Saving node %s failed: %s", candidate, exc, exc_info=True)
                    failed.append(candidate)
            # The scene last, so the .mrml records the paths the nodes were just
            # written to. writeToMRML re-asserts the URL and root directory that
            # were already set above.
            scene_path = os.path.join(directory, self.SCENE_FILE_NAME)
            if progress is not None:
                try:
                    progress(candidates, candidates, self.SCENE_FILE_NAME)
                except Exception:
                    logger.debug("Scene-save progress callback failed", exc_info=True)
            if not slicer.util.saveScene(scene_path):
                failed.append(self.SCENE_FILE_NAME)
        finally:
            for storage, name, name_list, uri, crop in restore.values():
                try:
                    # Same order as the reference restore pass: reset the list,
                    # put the primary name back, then re-add each member.
                    storage.ResetFileNameList()
                    storage.SetFileName(name)
                    for extra in name_list:
                        if extra is not None:
                            storage.AddFileName(extra)
                    storage.SetURI(uri)
                    if crop is not None:
                        storage.SetCropToMinimumExtent(crop)
                except Exception:
                    logger.debug("Restoring a storage node's save state failed",
                                 exc_info=True)
            try:
                scene.SetURL(original_url)
                scene.SetRootDirectory(original_root)
                # Writing every node stamps its StoredTime, which clears
                # GetModifiedSinceRead() scene-wide -- the surgeon's own work
                # would then show as "Not Modified" in File > Save Data and
                # Slicer would not warn about it on quit, while the only copy on
                # disk sat in logs/. Slicer's MRB writer does the same restore
                # for the same reason (qSlicerSceneWriter::writeToMRB).
                scene.SetStorableNodesModifiedSinceRead()
            except Exception:
                logger.debug("Restoring scene save state failed", exc_info=True)

        note = f"{written} node file(s) + {self.SCENE_FILE_NAME}"
        if skipped:
            note += f", {skipped} node(s) stored inside the scene"
        if failed:
            note += f". FAILED: {', '.join(failed[:6])}"
        return written, note

    @staticmethod
    def _safeFileName(name):
        """Slicer's own filename rule (qSlicerCoreIOManager::fileNameRegularExpression)."""
        allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                      "0123456789 -_.()$!~#'%^{}")
        cleaned = "".join(ch for ch in str(name or "") if ch in allowed).strip()
        return cleaned[:255] or "node"

    # ------------------------------------------------------------------
    # "Working..." dialog for the Exit teardown
    #
    # Saving the scene is the slowest thing this module does -- every storable
    # node written to disk, then the .mrml -- and it runs SYNCHRONOUSLY on the Qt
    # main thread, because MRML access is main-thread only and there is no
    # asynchronous node writer to hand it to. So Slicer stops repainting for the
    # seconds it takes, which is indistinguishable from a freeze on a large
    # scene. A modal progress dialog is the honest fix: it says what is
    # happening, names the file being written, and cannot be cancelled, because
    # a half-written run folder is worse than waiting.
    # ------------------------------------------------------------------
    EXIT_PROGRESS_TITLE = "Closing the guided workflow"

    def _beginExitProgress(self):
        """Show the modal "working..." dialog. Returns it, or None if unavailable."""
        try:
            dialog = qt.QProgressDialog(slicer.util.mainWindow())
            dialog.setWindowTitle(self.EXIT_PROGRESS_TITLE)
            dialog.setLabelText("Closing the workflow...")
            dialog.setMinimum(0)
            dialog.setMaximum(0)          # indeterminate until the node count is known
            dialog.setMinimumDuration(0)  # NOW, not after Qt's default 4 s
            dialog.setAutoClose(False)    # closed explicitly, in a finally
            dialog.setAutoReset(False)
            dialog.setWindowModality(qt.Qt.ApplicationModal)
            try:
                # There is nothing to cancel: the teardown has already begun and
                # stopping half-way would leave the session neither open nor
                # closed. Removing the button is clearer than disabling it.
                dialog.setCancelButton(None)
            except Exception:
                dialog.setCancelButtonText("")
            dialog.show()
            slicer.app.processEvents()
            return dialog
        except Exception:
            logger.debug("Could not create the exit progress dialog", exc_info=True)
            return None

    def _setExitProgress(self, dialog, text, value=None, maximum=None):
        """Update the dialog and let Qt actually paint it.

        ``processEvents()`` is what makes the dialog visible at all -- the
        teardown never returns to the event loop until it has finished. It is
        safe *here* specifically: it runs after the session epoch has been bumped
        and the stream queue drained, so any deferred continuation it delivers is
        already fenced out, the dialog is application-modal so nothing new can be
        started from the UI, and ``_guidedExitInProgress`` refuses a re-entrant
        reset.
        """
        if dialog is None:
            return
        try:
            if maximum is not None:
                dialog.setMaximum(maximum)
            if value is not None:
                dialog.setValue(value)
            dialog.setLabelText(text)
            slicer.app.processEvents()
        except Exception:
            logger.debug("Exit progress update failed", exc_info=True)

    def _endExitProgress(self, dialog):
        """Close it automatically -- the user never dismisses this one."""
        if dialog is None:
            return
        try:
            dialog.close()
            dialog.deleteLater()
            slicer.app.processEvents()
        except Exception:
            logger.debug("Closing the exit progress dialog failed", exc_info=True)

    def _releaseRunLogDir(self):
        """Cut every reference to the run folder before it is deleted.

        ``LLMClient._debugPath`` and ``RunManifest.write`` both call
        ``os.makedirs(..., exist_ok=True)`` on every write, so ONE later write
        re-creates the folder that was just removed -- leaving a half-empty
        directory that reads as a crashed run. The references go first.
        """
        try:
            if self.logic and self.logic.llmClient:
                self.logic.llmClient.setDebugOutputDir(None)
        except Exception:
            logger.debug("Clearing the client debug dir failed", exc_info=True)
        self._currentRunManifest = None
        self._pipelineRunManifest = None
        self._currentLogDir = None
        self._currentRunRoot = None
        self._pipelineLogDir = None
        self._pipelineRunRoot = None
        self._currentStepLogDir = ""
        self._pipelineStepLogDir = ""
        runtime = getattr(self, "_workflowRuntime", None)
        if runtime is not None:
            runtime.log_dir = ""

    def _discardRunLogDirs(self):
        """Delete this session's run folders. Returns ``(deleted, failed)`` names.

        "Exit without saving" has to mean nothing from the run is left in
        ``logs/``, and the artifacts are written *incrementally as the workflow
        executes* -- there is no "don't write it" to choose, only a removal. So
        this takes the whole folder: per-step code, plans, execution results,
        role traces, the manifest and the routing call, plus any baseline
        folders opened off this run's steps (``_sessionLogDirs``).

        ``rmtree`` is the only irreversible thing in this module, so it is gated
        on a CONTAINMENT CHECK rather than on the caller having passed the right
        path: each entry must resolve to a direct child of this extension's own
        ``logs/``. Anything else -- an absolute path elsewhere, a ``..``
        traversal, a symlink pointing out of the tree, or ``logs/`` itself -- is
        refused and logged, never deleted. The check is on the REAL path, so a
        junction cannot smuggle a target past it.
        """
        import shutil
        root = os.path.normcase(os.path.realpath(
            os.path.join(SLICER_AI_AGENT_ROOT, "logs")))
        deleted, failed = [], []
        # dict.fromkeys: de-duplicate while keeping order, since a run folder can
        # be recorded twice (parked and restored around a baseline).
        for path in dict.fromkeys(getattr(self, "_sessionLogDirs", None) or []):
            if not path:
                continue
            resolved = os.path.normcase(os.path.realpath(str(path)))
            if resolved == root or os.path.dirname(resolved) != root:
                logger.warning("Refusing to delete %s: not a run folder inside logs/",
                               path)
                failed.append(os.path.basename(str(path)) or str(path))
                continue
            if not os.path.isdir(resolved):
                continue        # never created, or already gone
            try:
                shutil.rmtree(resolved)
                deleted.append(os.path.basename(resolved))
            except Exception as exc:
                # Usually a file still open (Windows locks it) -- report it
                # rather than leaving the user thinking the folder is gone.
                logger.warning("Could not delete run folder %s: %s", path, exc)
                failed.append(os.path.basename(resolved))
        self._sessionLogDirs = []
        return deleted, failed

    def _saveRunStatistics(self, exit_epoch, progress=None):
        """Write ``logs/Statistic/<run>_timing.txt`` and ``<run>_scene/``.

        Called from the Exit button only. Fail-soft in both halves and in both
        directions: a scene that cannot be saved still produces the timing
        report (with the failure recorded in it), and a timing report that
        cannot be written never blocks the reset the user asked for.

        Runs AFTER the replay timeline is torn down, so the ~one hidden
        ``vtkMRMLSceneViewNode`` per step is already gone — otherwise the saved
        scene would carry a full copy of every intermediate state.

        Returns True only when a scene copy demonstrably landed on disk. The
        caller closes the scene on the strength of that, so it is deliberately a
        POSITIVE check (the .mrml exists and at least one node was written)
        rather than the absence of an exception: nothing in the save path
        raises — a node that cannot be written appends its name to a human
        readable note, and ``saveScene`` returning False does the same — so
        "no exception" would report success for a save that wrote nothing.
        """
        from SlicerAIAgentLib import RunLog
        manifest = self._runManifest()
        if manifest is None:
            logger.info("No run manifest to write statistics for")
            return False
        run_name = self._statisticRunName()
        try:
            stats_dir = self._statisticDir()
        except Exception:
            logger.debug("Statistic directory unavailable", exc_info=True)
            return False

        scene_dir, scene_note = "", ""
        written = 0
        try:
            scene_dir = RunLog.ensure_dir(os.path.join(stats_dir, "scene"))
            self._setExitProgress(progress, "Saving the scene...")
            written, note = self._saveSceneFlat(
                scene_dir,
                progress=(lambda done, total, name: self._setExitProgress(
                    progress,
                    f"Saving the scene:  {name}" if name else "Saving the scene...",
                    value=done, maximum=total,
                )) if progress is not None else None,
            )
            scene_note = note
            if written:
                scene_note += " -- " + self._describeSavedScene(scene_dir)
        except Exception as exc:
            logger.warning("Saving the scene for statistics failed: %s", exc)
            scene_note = f"Scene save raised: {exc}"

        self._setExitProgress(progress, "Writing timing.txt...", value=0, maximum=0)
        try:
            text = RunLog.build_run_statistics(
                manifest.data, exit_epoch, scene_dir=scene_dir, scene_note=scene_note,
            )
            path = RunLog.write_text(os.path.join(stats_dir, "timing.txt"), text)
            if path:
                logger.info("[Statistic] Run timing written to %s", path)
                self.appendToChat(
                    "System",
                    f"Run statistics saved: logs/{run_name}/"
                    f"{RunLog.STATISTIC_DIRNAME}/timing.txt (and scene/ beside it).",
                )
        except Exception:
            logger.warning("Writing the run statistics failed", exc_info=True)

        try:
            scene_saved = bool(written) and os.path.isfile(
                os.path.join(scene_dir, self.SCENE_FILE_NAME)
            )
        except Exception:
            scene_saved = False
        if not scene_saved:
            logger.warning(
                "[Statistic] No scene copy landed in %s (%s)", scene_dir, scene_note,
            )
        return scene_saved

    def _describeSavedScene(self, scene_dir):
        """One line about what landed in the scene folder, for the report."""
        try:
            files = 0
            size = 0
            for root, _dirs, names in os.walk(scene_dir):
                for name in names:
                    files += 1
                    try:
                        size += os.path.getsize(os.path.join(root, name))
                    except OSError:
                        pass
            nodes = slicer.mrmlScene.GetNumberOfNodes()
            return (f"{files} file(s), {size / (1024 * 1024):.1f} MB, "
                    f"from a scene of {nodes} MRML node(s).")
        except Exception:
            return "Saved."

    def _guidedRunHasProgress(self):
        """True when exiting would discard work (so the confirm is worth it)."""
        runtime = getattr(self, "_workflowRuntime", None)
        session = getattr(runtime, "session", None) if runtime else None
        if session is None:
            return False
        if getattr(session, "status", "") in ("completed", "cancelled"):
            return False
        return bool(getattr(session, "completed_steps", None))

    def _resetGuidedSession(self, reason="exit", announce=True, save=None,
                            close_scene=None):
        """Close the guided workflow and put the widget back to a clean start.

        ``save`` writes the run's statistics + a flat copy of the scene into
        ``logs/<run>/Statistic/``. ``None`` derives it from ``reason``, which
        keeps the three non-Exit callers (a runtime cancel, a scene close, the
        bare default) behaving exactly as before; the Exit button passes it
        explicitly, because that is the one path where the user chose.

        ``close_scene`` likewise defaults to "only a user Exit". It is a
        separate parameter rather than a second reading of ``reason`` because
        there is one case where the user pressed Exit and the scene must still
        NOT be closed: the confirmation dialog failed to appear, so
        ``_askExitChoice`` fell back to a full exit the user never actually
        agreed to. Closing an unsaved scene on the strength of an assumed
        answer is the one mistake here that cannot be undone.

        The ORDER below is load-bearing and each step is commented, because the
        cost of getting it wrong is silent: state that survives here does not
        raise, it corrupts the NEXT workflow.

        Returns False (and changes nothing) while a baseline run or a stream is
        in flight -- tearing the session out from under either would orphan its
        record and leave a thread writing into a session that no longer exists.
        """
        # Already tearing down. The save below pumps the event loop so the
        # progress dialog can paint, and a scene close (or any other caller)
        # delivered during that pump would otherwise run a second teardown
        # through state the first one is halfway through dismantling.
        if getattr(self, "_guidedExitInProgress", False):
            return False
        if self._baselineBusy():
            self._setBaselineStatus(
                "A baseline run is in progress — wait for it to finish (or press "
                "Send to stop waiting for Claude Code) before exiting."
            )
            return False
        if self._reviseBusy():
            # Same reason as a baseline: the revision is mid-flight in the API
            # and will come back to write a template. Exiting would bump the
            # epoch, the reply would be dropped, and the user would be left with
            # a request that silently did nothing.
            self._setReviseStatus(
                "A revision is in progress — wait for it to finish before exiting."
            )
            return False
        if getattr(self, "_streaming", False):
            self.appendToChat(
                "System", "A request is still running — wait for it to finish before exiting."
            )
            return False

        if save is None:
            save = (reason == "user_exit")
        if close_scene is None:
            close_scene = (reason == "user_exit")
        close_scene = bool(close_scene) and self.EXIT_CLOSES_SCENE

        # 0. Stamp the end of the run before anything is torn down, so the
        #    "Send to Exit" total is measured to the click and not to whenever
        #    the teardown below happens to finish.
        import time as _time
        exit_epoch = _time.time()

        # 1. Invalidate everything already in flight. Deferred work (a QTimer
        #    auto-advance, a self-correction thread that is still waiting on the
        #    API) cannot be cancelled, so it is fenced instead: each continuation
        #    compares the epoch it captured against this one and drops out.
        self._guidedSessionEpoch = getattr(self, "_guidedSessionEpoch", 0) + 1

        # 2. Events already queued by a worker belong to the session being
        #    closed; draining them stops them being applied to the next one.
        try:
            while True:
                self._streamQueue.get_nowait()
        except Exception:
            pass

        # 2b. Anything whose "I am finished" event was in that queue must have
        #     its flag cleared HERE, or it stays set for the rest of the
        #     session. A routing call in flight is the case that matters: its
        #     router_decision event has just been discarded, so _routerBusy
        #     would never be cleared and every later request would be answered
        #     with "still choosing workflow" -- a permanently deaf Send button.
        #     The worker itself is fenced by the epoch bumped in step 1.
        self._routerBusy = False
        self._voiceTranscribing = False

        # 3. Baseline harness: stop the MCP endpoint, hand the run log back to
        #    the pipeline (_teardownBaselineMcp does that), leave baseline mode.
        try:
            self._teardownBaselineMcp()
            self._exitBaselineMode()
            self._clearBaselinePrompt()
        except Exception:
            logger.debug("Baseline teardown on exit failed", exc_info=True)

        # 3b. Revise mode, for the same reason and it must be HERE, before step
        #     6. `_prepareCleanRuntime` sets `_reviseActive = False` as a raw
        #     attribute write, and `_updateReviseControls` (step 8, via
        #     `_clearWorkflowPanel`) only tears the mode down when it finds that
        #     flag still True -- so by the time the self-healing path runs it has
        #     nothing to heal, and the purple status row is left parked above the
        #     prompt box for the rest of the session.
        try:
            self._exitReviseMode()
            self._clearRevisePrompt()
        except Exception:
            logger.debug("Revise teardown on exit failed", exc_info=True)

        # 4. Live Slicer state the workflow switched on. Placement mode and the
        #    threshold preview outlive the panel, so a user who exits mid-step
        #    would otherwise be left clicking fiducials into an empty session.
        for step in (
            self._closeFloatingWorkflowControl,
            self._clearThresholdPreview,
            self._releaseModuleSessionTools,
        ):
            try:
                step()
            except Exception:
                logger.debug("Workflow teardown step failed on exit", exc_info=True)
        manager = getattr(self, "_interactionManager", None)
        if manager is not None:
            for call in (manager.exit_placement_mode, manager.cleanup):
                try:
                    call()
                except Exception:
                    logger.debug("Interaction teardown on exit failed", exc_info=True)

        # 5. Seal the run folder and drop the replay timeline -- WHILE the
        #    session still exists. clear_checkpoints() restores the live scene if
        #    the user was mid-preview and deletes the hidden sceneview nodes, and
        #    every line of it is a no-op once `session` is None.
        #
        #    From here to the end of 5b is the only part of the teardown the user
        #    can WAIT on, so it is the only part that gets the progress dialog --
        #    and the only part that pumps the event loop, hence the re-entrancy
        #    guard around exactly this span. The dialog is tied to `save`, not to
        #    the Exit button: without the scene write the rest of this is
        #    milliseconds, and a modal that flashes is worse than none.
        # The guard goes up FIRST: _beginExitProgress ends in show() +
        # processEvents(), so the very first pump is inside the teardown and
        # would otherwise be the one moment a scene close could start a second
        # one.
        self._guidedExitInProgress = True
        progress = self._beginExitProgress() if save else None
        try:
            self._setExitProgress(progress, "Closing the replay timeline...")
            try:
                self._clearCompletedWorkflowState(clear_replay=True)
            except Exception:
                logger.debug("Workflow state clear on exit failed", exc_info=True)

            # 5b. Write the run's statistics + save the scene. Deliberately
            #     HERE: after step 5 the replay sceneviews are gone (so the saved
            #     scene is the live one, not one copy per step) and the manifest
            #     is sealed and complete, but _currentLogDir and
            #     _currentRunManifest are still set — step 7 below drops both.
            if save:
                saved_ok = False
                try:
                    saved_ok = self._saveRunStatistics(exit_epoch, progress=progress)
                except Exception:
                    logger.warning("Run statistics save failed", exc_info=True)
                # The user asked for the record AND (implicitly) for the scene
                # to be closed. If the record did not materialise, honouring
                # only the second half destroys the scene and keeps nothing --
                # the worst of the four outcomes, and the one they would never
                # have chosen. So the close is abandoned and the reason is said
                # out loud; the panel is closed either way, so they are not
                # stuck, and File > Close Scene is one menu away.
                if close_scene and not saved_ok:
                    close_scene = False
                    self.appendToChat(
                        "System",
                        "The scene could NOT be saved to logs/, so it has been "
                        "left open rather than closed — save it yourself "
                        "(File > Save Data) before closing it. See the "
                        "application log for what failed.",
                    )
            elif reason == "user_exit":
                # "Without saving" means nothing of this run stays in logs/, so
                # the folder it has been writing into all along goes too.
                # Guarded like its sibling above: a failure here must not
                # abandon the teardown half-done.
                try:
                    self._releaseRunLogDir()
                    deleted, failed = self._discardRunLogDirs()
                    note = (f"Exited without saving. Deleted "
                            f"{len(deleted)} run folder(s) from logs/."
                            if deleted else
                            "Exited without saving. Nothing was written to logs/.")
                    if failed:
                        note += (f" Could NOT delete: {', '.join(failed[:4])}"
                                 f" -- see the log for why.")
                    self.appendToChat("System", note)
                except Exception:
                    logger.warning("Discarding the run folder failed", exc_info=True)
        finally:
            # Closes itself: the user asked to exit, not to read a report.
            self._endExitProgress(progress)
            self._guidedExitInProgress = False

        # 6. Now the session itself, plus everything else whose lifetime is this
        #    run. _prepareCleanRuntime does the second half (it is shared with
        #    workflow START, so the two can never drift apart) and is what
        #    clears the module-global mirrors -- for ALL extensions, not just
        #    this one: they are keyed by extension name, so a per-extension
        #    reset would leave a run of a DIFFERENT procedure inheriting this
        #    one's completions, choices and loop counters.
        #
        #    After 5b, so the statistics save still had its manifest and log
        #    dir; the module rebuild is not asked for here (no extension name),
        #    since the run that needs a fresh widget is the next one.
        runtime = getattr(self, "_workflowRuntime", None)
        if runtime is not None:
            runtime.session = None
            runtime.log_dir = ""
        orchestrator = getattr(self, "_workflowOrchestrator", None)
        if orchestrator is not None and getattr(self, "_activeWorkflowId", None):
            try:
                orchestrator.cancel_workflow(self._activeWorkflowId)
            except Exception:
                logger.debug("Orchestrator cancel on exit failed", exc_info=True)
        # AFTER cancel_workflow, not before: that call reads the very state
        # _prepareCleanRuntime empties (its own workflow entry, and the
        # interaction manager's created-node list, which it uses to DELETE those
        # nodes). Clearing first would turn it into a silent no-op and change
        # what Exit does to the scene.
        try:
            self._prepareCleanRuntime(reason=reason)
        except Exception:
            logger.debug("Clean-runtime reset on exit failed", exc_info=True)

        # 7. Per-run widget state. Anything keyed by step id or node id belongs
        #    to the run just closed and would be read back by the next one.
        self._activeWorkflowId = None
        self._currentWorkflowStepInfo = None
        self._currentWorkflowUiState = {"active": False}
        self._waitingForUser = False
        self._autoAdvanceWorkflowStep = None
        self._taskWorkflowPanelActive = False
        self._announcedWorkflowIds = set()
        self._workflowInheritedDefaults = {}
        self._autoSelectedNodeSteps = set()
        self.currentCode = None
        self.currentAgentPlan = None
        self._lastRouterDecision = None
        self._lastRouter = None
        self._lastRouterRejection = None
        self._currentLogDir = None
        self._currentRunRoot = None
        # Belongs to the run just closed: a stale entry would put a previous
        # run's folder on the next "Exit without saving" delete list.
        self._sessionLogDirs = []
        try:
            self._clearWorkflowNotice()
        except Exception:
            logger.debug("Notice clear on exit failed", exc_info=True)

        # 8. Repaint empty, and give the prompt box and Send back -- the gate
        #    that switched them off keys on an active workflow, and there is
        #    none now. _refreshInputAvailability is last and is the only thing
        #    that touches Send here, so the button follows the (now empty) box
        #    rather than being forced on with nothing to send.
        self._clearWorkflowPanel()
        self._setReadyStatus()
        self._refreshInputAvailability()

        # 9. Close the scene -- LAST, and only for the Exit button.
        #
        #    Last, because everything above needs the scene: the statistics save
        #    writes it, clear_checkpoints restores from its sceneview snapshots,
        #    and the interaction/threshold teardown removes observers from nodes
        #    that must still exist. And by here `runtime.session` is already None
        #    (step 6), so the EndCloseEvent this fires reaches
        #    onSceneEndClose and does the ONE thing we want from it -- dropping
        #    the entered-module cache so the next run re-binds the extension --
        #    without re-entering this method.
        #
        #    `close_scene` was resolved at the top and may have been withdrawn
        #    above (a save that did not land). The other two callers are a
        #    runtime cancel and a scene close that has already happened, and
        #    closing the scene under either would destroy the user's data
        #    without them asking, so neither reaches here.
        if close_scene:
            close_scene = self._closeSceneOnExit()

        if announce:
            self.appendToChat(
                "System",
                "Guided workflow closed and reset"
                + (" (scene closed). " if close_scene else ". ")
                + "Load your data and type a new request to start another one.",
            )
        logger.info("Guided workflow session reset (%s)", reason)
        return True

    # ------------------------------------------------------------------
    # Cross-run state: making run N+1 start where run 1 started
    #
    # A guided run is supposed to be reproducible, and the only thing that
    # actually guaranteed that was restarting Slicer. Everything below is state
    # whose natural lifetime is the PROCESS while the thing it describes has the
    # lifetime of a RUN (or of a scene), so run 2 in one session began from a
    # place run 1 never saw. The failures are silent by construction -- nothing
    # raises, the workflow just behaves differently -- so the list is enumerated
    # explicitly rather than discovered.
    #
    # The worst of them, and the one that motivated this: every generated
    # template reaches its extension through
    #
    #     try:    logic = _<ext>_logic
    #     except NameError: logic = <Ext>Logic()
    #
    # which is the intended hand-off from step N to step N+1 -- and, because
    # __main__ outlives the run, also an unintended hand-off from run 1 to run 2.
    # The reused object carries the previous run's node attributes, so a guard
    # like `if self.fullBoneNode is not None:` reads "that stage is already
    # done" while the scene says otherwise, and steps reveal, skip or recompute
    # against a patient's data that is no longer there.
    # ------------------------------------------------------------------

    #: Whether starting a workflow rebuilds the driven extension's module widget.
    #:
    #: ``slicer.util.reloadScriptedModule`` is Slicer's own "as if just
    #: launched" for a scripted module: it re-imports the source, calls the old
    #: widget's ``cleanup()`` and builds a new one through ``setup()``. It is
    #: the only generic way to clear what the runtime cannot enumerate -- the
    #: extension's own widget/logic attributes and the state of its Qt controls
    #: (a combobox left on run 1's answer is read by the extension's handlers at
    #: click time, which is exactly why the runtime drives those controls at
    #: all).
    #:
    #: Set False if a reload ever proves worse than the staleness it removes;
    #: the rest of _prepareCleanRuntime still applies.
    RESET_EXTENSION_MODULE_ON_START = True

    def _prepareCleanRuntime(self, extension_name="", reason="start"):
        """Return the process to the state a freshly launched Slicer is in.

        Idempotent and fail-soft item by item: this runs on the way IN to a
        workflow (where a previous run may have ended in any way at all,
        including not ending) and on the way OUT of one. Neither caller may be
        aborted by a single stale attribute refusing to clear, so every step is
        guarded on its own.

        ``extension_name`` is the procedure about to run, and is used only for
        the module rebuild -- everything else is cleared for ALL extensions,
        deliberately: these are keyed by extension name, and clearing only the
        one named here would leave the NEXT procedure inheriting a different
        one's completions, choices and loop counters.
        """
        cleared = []

        # 1. The __main__ residue. First, because it is the one that changes
        #    what the templates DO rather than what the panel shows.
        try:
            executor = getattr(getattr(self, "logic", None), "executor", None)
            if executor is not None and hasattr(executor, "clearIntroducedGlobals"):
                names = executor.clearIntroducedGlobals()
                if names:
                    cleared.append(f"{len(names)} __main__ name(s)")
                    logger.info(
                        "[CleanRuntime] Unbound %d name(s) left in __main__ by "
                        "generated code: %s",
                        len(names),
                        ", ".join(sorted(names)[:12])
                        + (" ..." if len(names) > 12 else ""),
                    )
        except Exception:
            logger.debug("Clearing generated __main__ names failed", exc_info=True)
        # The per-step prelude cleanup is lazy -- it drops the PREVIOUS step's
        # keys when the next one is dispatched -- so a run that ended mid-step
        # leaves its keys bound. They have just been unbound above; this stops
        # the next dispatch trying to remove them a second time.
        self._lastInjectedPreludeKeys = []

        # 2. Our own module-global mirrors, for every extension.
        try:
            from SlicerAIAgentLib.ExtensionCLILoader import reset_workflow_state
            reset_workflow_state(None)
            cleared.append("workflow mirrors")
        except Exception:
            logger.debug("Generated CLI workflow state reset failed", exc_info=True)

        # 3. "This module is entered" -- held in two independent places, and
        #    both are wrong after a run ends. enter() is the extension binding
        #    itself to the current scene, so the next run must fire it again;
        #    and the runtime's copy additionally gates the wizard-page probe,
        #    which on a fresh launch answers False and here would answer True.
        try:
            entered = getattr(self, "_invisiblyEnteredModules", None)
            if entered:
                entered.clear()
                cleared.append("entered modules")
        except Exception:
            logger.debug("Clearing the entered-module cache failed", exc_info=True)
        try:
            runtime = getattr(self, "_workflowRuntime", None)
            runtime_entered = getattr(runtime, "_entered_modules", None)
            if runtime_entered:
                runtime_entered.clear()
        except Exception:
            logger.debug("Clearing the runtime entered-module set failed", exc_info=True)

        # 4. Interaction + orchestrator bookkeeping. Both are normally emptied
        #    through cancel_workflow, which _resetGuidedSession only reaches
        #    when _activeWorkflowId is still set -- so a run that completed
        #    (which clears it) never got there.
        try:
            manager = getattr(self, "_interactionManager", None)
            created = getattr(manager, "_all_created_node_ids", None)
            if created:
                # The IDs only, never the nodes: cleanup_all_created_nodes()
                # DELETES them, and what the procedure produced is the user's.
                del created[:]
        except Exception:
            logger.debug("Clearing created-node ids failed", exc_info=True)
        try:
            orchestrator = getattr(self, "_workflowOrchestrator", None)
            active = getattr(orchestrator, "_active_workflows", None)
            if active:
                active.clear()
        except Exception:
            logger.debug("Clearing orchestrator workflows failed", exc_info=True)

        # 5. Per-run widget bookkeeping that outlives its run. Each of these
        #    reads back into a decision: _lastSliceFitLayout SKIPS the slice fit
        #    when run 2 opens on the layout run 1 ended on (its "__unset__"
        #    sentinel is what makes a fresh launch always fit); the preview
        #    ranges pre-seed the threshold throttle with run 1's last range;
        #    _lastCorrectionError is quoted into the next repair prompt.
        self._lastSliceFitLayout = "__unset__"
        for attr, value in (
            ("_pendingPreviewRange", None),
            ("_lastPreviewRange", None),
            ("_lastExecutionResult", None),
            ("_lastVerificationResult", None),
            ("_lastSceneAfter", None),
            ("_lastOutputHasErrors", False),
            ("_lastCorrectionError", None),
            ("_baselineAttemptCounts", {}),
            # Revision state. `_reviseAttemptCounts` names the artifact folder
            # (revision_1/, revision_2/ ...) under the step it revises, so a
            # second run inheriting run 1's counter would start numbering at 2
            # in a folder that has no 1. `_reviseActiveRun` cannot survive here
            # -- Exit refuses while one is in flight -- but it is listed so a
            # future path that ends a run some other way cannot leak it.
            ("_reviseAttemptCounts", {}),
            ("_reviseActiveRun", None),
            ("_reviseActive", False),
            # Keyed on (cli_dir, step_id), so it would survive a REGENERATION of
            # the package between two runs and keep answering from the old
            # step->file mapping.
            ("_reviseEligibilityMemo", {}),
            # Log bookkeeping: the manifest object is documented as outliving
            # its run (a first-seal-wins guard covers the re-entry), and the
            # parked _pipeline* copies belong to whichever run a baseline
            # interrupted.
            ("_currentRunManifest", None),
            ("_currentStepLogDir", None),
            ("_currentStepId", None),
            ("_currentCorrectionDir", None),
            ("_stepTraceStart", None),
            ("_pipelineLogDir", None),
            ("_pipelineRunRoot", None),
            ("_pipelineRunManifest", None),
            ("_pipelineStepLogDir", None),
            ("_pipelineStepId", None),
            ("_pipelineRoleTrace", None),
        ):
            try:
                if hasattr(self, attr):
                    setattr(self, attr, dict(value) if isinstance(value, dict) else value)
            except Exception:
                logger.debug("Resetting %s failed", attr, exc_info=True)

        # 6. Voice: a command awaiting "yes", or an utterance parked by the
        #    re-entrancy guard, belongs to the run it was spoken in. The epoch
        #    fence retires work already dispatched; these are the queues it
        #    cannot reach. _teardownVoice is deliberately NOT called -- the
        #    microphone staying armed across runs is the point of arming it.
        for attr, value in (
            ("_voicePendingCommand", None),
            ("_voicePendingStep", None),
            ("_voiceDeferredTranscripts", []),
            ("_voiceDeferredCommands", []),
            ("_voiceAsrErrorStreak", 0),
            ("_voiceSpokenStepKey", None),
        ):
            try:
                if hasattr(self, attr):
                    setattr(self, attr, list(value) if isinstance(value, list) else value)
            except Exception:
                logger.debug("Resetting %s failed", attr, exc_info=True)

        # 7. Live Slicer state a previous run may have left switched on. The
        #    teardown does this too; repeating it here is what covers a run that
        #    never reached a teardown.
        for step in (
            getattr(self, "_clearThresholdPreview", None),
            getattr(self, "_releaseModuleSessionTools", None),
        ):
            if step is None:
                continue
            try:
                step()
            except Exception:
                logger.debug("Clean-runtime teardown step failed", exc_info=True)

        # 8. The extension's own widget. Last, because it is the only step that
        #    can take visible time, and the only one that rebuilds rather than
        #    clears.
        if extension_name and self.RESET_EXTENSION_MODULE_ON_START:
            if self._resetExtensionModuleState(extension_name):
                cleared.append(f"{extension_name} module")

        logger.info(
            "[CleanRuntime] Prepared a clean runtime (%s)%s",
            reason,
            (": " + ", ".join(cleared)) if cleared else "",
        )

    def _resetExtensionModuleState(self, extension_name):
        """Rebuild a scripted module's widget, so it starts factory-fresh.

        The runtime cannot enumerate what a third-party extension keeps on
        itself, and two kinds of it survive everything else here. Python
        attributes on the widget and its logic: an extension's own scene-close
        hook resets ``self.logic``, but the generated templates hold a SECOND,
        independent logic instance, so an extension whose reset looks correct in
        review still leaks under this runtime. And the state of its Qt controls:
        the runtime drives those controls precisely because the extension's
        handlers read them at click time, so a combobox left on run 1's answer
        is an answer run 2 never gave.

        ``reloadScriptedModule`` is Slicer's own answer to this (it is what the
        Reload button runs) and is generic -- no extension is named here.

        Never fatal. A module that will not reload leaves the previous widget in
        place, which is exactly today's behaviour, so the cost of failing is
        losing an improvement rather than breaking a run. The entered-module
        caches are cleared first regardless, because a rebuilt widget has
        certainly not been entered -- and if the reload fails half-way,
        re-entering is still the safer belief.
        """
        # The name here is the CLI package's, which for every shipped package is
        # also the scripted module's -- but that is a convention, not a
        # guarantee (an extension may ship several modules under one name). Ask
        # Slicer's own registry rather than assume: a name that is not a module
        # must be skipped, not handed to reloadScriptedModule, whose failure
        # mode on a C++ or CLI module is an unrelated-looking path error.
        try:
            if not hasattr(slicer.modules, str(extension_name).lower()):
                logger.debug(
                    "%s is not a registered module; skipping the widget rebuild",
                    extension_name,
                )
                return False
        except Exception:
            return False
        try:
            entered = getattr(self, "_invisiblyEnteredModules", None)
            if entered:
                entered.discard(extension_name)
        except Exception:
            pass
        try:
            slicer.util.reloadScriptedModule(extension_name)
            logger.info(
                "[CleanRuntime] Rebuilt the %s module widget (fresh logic, "
                "factory-default controls)", extension_name,
            )
            return True
        except Exception as exc:
            # Debug, not warning: an extension that is not a scripted module, or
            # is not installed, reaches here on every run and is not a fault.
            logger.debug(
                "Could not rebuild the %s module widget (%s); continuing with "
                "the existing one", extension_name, exc, exc_info=True,
            )
            return False

    def _closeSceneOnExit(self):
        """Close the MRML scene exactly the way File > Close Scene does.

        ``Clear(0)`` plus ``SetURL("")`` is the whole of
        ``qSlicerMainWindow::on_FileCloseSceneAction_triggered`` minus its
        ``confirmCloseScene()`` prompt -- which is deliberately not reproduced:
        the Exit dialog the user has just answered already says the scene is
        closed and that unsaved work is lost, and a second modal asking the same
        question is how a confirmation stops being read. ``SetURL("")`` matters
        for the same reason Slicer does it: without it the next File > Save
        would silently target the previous case's scene file.

        Fail-soft. A scene that will not close must not turn Exit into a button
        that appears to do nothing -- the workflow is already torn down by the
        time this runs, so reporting and continuing is strictly better than
        raising.
        """
        try:
            slicer.mrmlScene.Clear(0)
            try:
                slicer.mrmlScene.SetURL("")
            except Exception:
                logger.debug("Clearing the scene URL failed", exc_info=True)
            logger.info("[Workflow] Scene closed on exit")
            return True
        except Exception as exc:
            logger.warning("Closing the scene on exit failed: %s", exc, exc_info=True)
            self.appendToChat(
                "System",
                f"The guided workflow is closed, but the scene could not be "
                f"closed automatically ({exc}). Use File > Close Scene before "
                f"starting the next run.",
            )
            return False

    def _onWorkflowChoiceClicked(self, step_id, value):
        # While scrubbing the replay, the choices belong to a past step: clicking
        # one re-runs the workflow from that step with the chosen value.
        if self._currentWorkflowUiState.get("replay_previewing"):
            index = self._currentWorkflowUiState.get("preview_index")
            if index is not None:
                self._rerunFromCheckpoint(index, {"choice_value": value})
            return
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
        if self._currentWorkflowUiState.get("replay_previewing"):
            index = self._currentWorkflowUiState.get("preview_index")
            if index is not None:
                self._rerunFromCheckpoint(index, {"choice_value": value})
            return
        self.sendButton.setEnabled(False)
        self._runWorkflowStepDirect(step_id, "choice_made", args={"choice_value": value})

    def _renderWorkflowNodeTree(self, state, node_class, default_value):
        """Show the Data-module node tree (qMRMLSubjectHierarchyTreeView) filtered
        to ``node_class`` -- a "Node" list with the eye/visibility column and a
        Select button beneath it.

        The tree's ``nodeTypes`` filter lists only nodes of this class (it filtered
        correctly once ``node_class`` was actually supplied -- the earlier "shows
        every node/folder" was a stale-library reload bug that left node_class
        empty, now fixed). ``hideEmptyHierarchyItems`` drops folders/studies with
        no matching child. The candidate gate below (getNodesByClass minus
        HideFromEditors) provides the "no node -> free-text" fallback.

        Returns True if it rendered (>=1 selectable node of this class exists), or
        False to let the caller fall back to the free-text box.
        """
        # Candidate list = scene nodes of node_class, minus HideFromEditors. This
        # both replicates the old combo's "no node -> free text" empty gate and
        # supplies the candidates for the _bestNodeMatchIndex default guess. We
        # mirror the tree's own HideFromEditors exclusion here so the emptiness
        # check matches exactly what the tree will actually display.
        # In replay, nodes created AFTER the reviewed step carry a subject-hierarchy
        # item tag (set by WorkflowRuntime._hide_nodes_after); skip them so the
        # candidate list matches the forward view (and so the default selection is a
        # step-era node). The tree itself excludes them via the same attribute.
        candidates = self._workflowNodeCandidateList(state, node_class)
        if not candidates:
            return False
        # The tree applies the same replay exclusion the candidate list does, via
        # the subject-hierarchy attribute filter set below.
        from SlicerAIAgentLib.WorkflowRuntime import WorkflowRuntime as _WFRT
        _replay_attr = _WFRT.REPLAY_HIDDEN_SH_ATTR
        _in_replay = bool(state.get("replay_previewing"))

        # Container stacks the tree above its Select button (the choice layout is a
        # QHBoxLayout; a tall tree reads better over the button than beside it).
        container = qt.QWidget()
        vbox = qt.QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)

        # The Data-module node tree (qMRMLSubjectHierarchyTreeView): a "Node" list
        # with the eye/visibility column, so the user can toggle a node's
        # visibility to see which scene object it is before committing. Its
        # ``nodeTypes`` filter is honored (it correctly shows only the class's
        # nodes when ``node_class`` is set); the earlier "shows everything" was a
        # stale-library reload bug (node_class arrived empty), now fixed. The
        # candidate gate above already guarantees >=1 node of this class exists.
        segment_ref = bool(state.get("segment_ref_selection"))
        tree = slicer.qMRMLSubjectHierarchyTreeView()
        tree.setMRMLScene(slicer.mrmlScene)     # scene BEFORE filtering
        tree.nodeTypes = [node_class]           # exact class, subclass-inclusive
        # Hide subject-hierarchy folders/studies left EMPTY after the nodeTypes
        # filter (e.g. an extension's output "…Plan" folder, which holds only
        # other-class outputs). The proxy property is ``showEmptyHierarchyItems``
        # (set False), driven via its setter -- a bare attribute assignment does
        # not bind through PythonQt here. Generic; no extension-specific attrs.
        # NOT for a segment pick: a segment row is itself a data-node-less, childless
        # hierarchy item, so hiding empty hierarchy items rejects the very rows the
        # user must click. The source extension leaves this at its default for the
        # same reason.
        if not segment_ref:
            try:
                tree.sortFilterProxyModel().setShowEmptyHierarchyItems(False)
            except Exception:
                logger.debug("Tree setShowEmptyHierarchyItems setup failed", exc_info=True)
        # Exclude subject-hierarchy items tagged as created-after-this-step during
        # replay (see WorkflowRuntime.REPLAY_HIDDEN_SH_ATTR): with those data nodes
        # excluded, their output folder reads empty and is hidden too, so a
        # stepped-back view matches the forward one. Applied ONLY while reviewing
        # (replay); never in the live/forward flow. Generic; no extension attrs.
        if _in_replay:
            # Set on the TREE (which owns this Q_PROPERTY and forwards it to its
            # proxy) rather than the proxy directly -- the tree re-syncs its own
            # filter properties, so a proxy-only set can be overwritten.
            try:
                tree.setExcludeItemAttributeNamesFilter([_replay_attr])
            except Exception:
                logger.debug("Tree setExcludeItemAttributeNamesFilter setup failed", exc_info=True)
        # Trim columns the narrow panel has no room for; keep the eye column.
        for _attr in ("idColumnVisible", "transformColumnVisible", "descriptionColumnVisible"):
            try:
                setattr(tree, _attr, False)
            except Exception:
                logger.debug("Tree column setup (%s) failed", _attr, exc_info=True)
        tree.setMinimumHeight(120)
        tree.setMaximumHeight(220)
        tree.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed)
        self._workflowNodeTree = tree

        # Default to the best keyword/name match (only a guess; user can change).
        try:
            # On replay a segment-ref step's recorded value is the compound pair, whose
            # str() matches no node name; match on the segmentation it names instead.
            match_value = default_value
            if segment_ref and isinstance(default_value, dict):
                match_value = default_value.get("node_name") or ""
            idx = self._bestNodeMatchIndex(
                candidates, match_value, state.get("node_keywords") or []
            )
            if 0 <= idx < len(candidates):
                tree.setCurrentNode(candidates[idx]["node"])
                if segment_ref:
                    # The pick must land on a SEGMENT row, so open the segmentation to
                    # show its segments; with >1 segment Select stays disabled until the
                    # user picks one, exactly as the source extension requires.
                    try:
                        shNode = tree.subjectHierarchyNode()
                        tree.expandItem(shNode.GetItemByDataNode(candidates[idx]["node"]))
                    except Exception:
                        logger.debug("Expanding segmentation row failed", exc_info=True)
        except Exception:
            logger.debug("Defaulting node tree selection failed", exc_info=True)

        button = qt.QPushButton("Select")
        button.setToolTip(
            "Expand the segmentation and select the segment to use"
            if segment_ref else "Use the selected node"
        )
        button.clicked.connect(self._onWorkflowNodeTreeSelected)
        self._workflowNodeTreeSelectButton = button

        # Enable Select only while a real data node of node_class is current.
        tree.currentItemChanged.connect(self._onWorkflowNodeTreeSelectionChanged)
        self._updateNodeTreeSelectButtonEnabled()

        vbox.addWidget(tree, 1)
        vbox.addWidget(button)
        self._workflowNodeTreeContainer = container
        self._workflowChoiceLayout.addWidget(container, 1)
        container.setVisible(True)
        return True

    # ------------------------------------------------------------------
    # Sole-candidate node auto-select
    # ------------------------------------------------------------------
    def _soleNodeAutoSelectCandidate(self, state):
        """The one node this step may be answered with automatically, else None.

        Deliberately STRICTER than the render dispatch. Each specialised family
        line in ``_renderWorkflowChoices`` reads ``if state.get(flag) and
        self._renderX(state): return`` -- so when a specialised renderer DECLINES
        (no segmentation resolves, no sensible slider limits) control falls
        through and CAN reach the node tree. A human clicking a node in that
        fallback tree is a recoverable mistake; auto-committing a node NAME as the
        answer to a threshold-range or segment-name step is not. So every family
        flag must be OFF, never merely "the specialised renderer declined".

        Two families that do reach the node tree are excluded on purpose:
        ``segment_ref_selection`` (the answer is a (node, segment) PAIR, and one
        segmentation does not imply one segment) and ``segment_name_selection``
        (not a node pick, and its candidate set is itself a heuristic guess).
        """
        if not AUTO_SELECT_SOLE_NODE_ENABLED:
            return None
        state = state or {}
        runtime = getattr(self, "_workflowRuntime", None)
        session = getattr(runtime, "session", None) if runtime is not None else None
        if session is None or not runtime.has_active_workflow():
            return None

        # A. Never while REVIEWING the replay timeline. The preview deliberately
        # re-surfaces the picker with an even narrower candidate list, so "exactly
        # one" is MORE likely there -- and a commit in preview routes to
        # _rerunFromCheckpoint, i.e. a destructive re-run of a step the user was
        # only looking at. Checked twice because the fallback state dict
        # (_workflowUiStateFromStepResult) carries no replay_previewing key.
        if state.get("replay_previewing") or session.preview_index is not None:
            return None

        # B. Never in baseline mode: the comparison's whole point is that a
        # condition answers the step itself.
        if getattr(self, "_baselineActive", False):
            return None
        try:
            if self._baselineBusy():
                return None
        except Exception:
            pass

        # C. The step must be genuinely waiting for a choice right now.
        # state_for_ui falls back to session.last_result, so a refresh with no new
        # result re-serves the previous user_choice while the committed step is
        # already dispatching.
        if state.get("raw_status") != "waiting_for_choice":
            return None
        if state.get("result_type") != "user_choice":
            return None
        if not state.get("current_step"):
            return None

        # D. Must be the plain node-tree family: no enumerated choices, a free
        # input expected, and every specialised family off.
        if state.get("choices"):
            return None
        if not state.get("needs_choice_input"):
            return None
        for flag in ("review_selection", "native_widget", "multi_choice",
                     "segment_selection", "segment_name_selection",
                     "segment_ref_selection", "range_selection", "scalar_selection"):
            if state.get(flag):
                return None
        # An optional step has a second legitimate answer (Skip), so one candidate
        # is not one possible outcome.
        if state.get("can_skip"):
            return None
        # The source extension's own widget class is authoritative: a recorded
        # slider / combo / segments table must never auto-commit a node name.
        family = self._workflowWidgetFamily(state.get("source_widget_class"))
        if family not in ("", "node_tree"):
            return None

        node_class = state.get("node_class")
        if not node_class:
            return None

        # E. Refuse when the workflow needs SEVERAL nodes of this class. Then a
        # lone candidate means an input is missing, and answering both steps with
        # it registers an object to itself -- an identity transform that renders
        # as a flawless fit (e.g. a reference and a moving segmentation, or an
        # orbit model and a plate model).
        if int(state.get("node_class_demand") or 0) > 1:
            return None

        candidates = self._workflowNodeCandidateList(state, node_class)
        if len(candidates) != 1:
            return None
        node = candidates[0].get("node")
        if node is None:
            return None

        # F. Exact class, WHEN a node could actually have that class. getNodesByClass
        # and the tree's nodeTypes filter match by IsA, so a labelmap (a ScalarVolume
        # subclass) would qualify as a Segment Editor source volume; the picker may
        # offer subclasses -- a human can see what they are -- but the automatic path
        # must not choose between siblings.
        #
        # That reasoning only applies to a class a node can HAVE. Against an abstract
        # base (``vtkMRMLVolumeNode``, which a decomposition writes when it means "a
        # volume") the comparison is unsatisfiable rather than selective: no node's
        # GetClassName() is ever an abstract name, so the gate never passed and the
        # step waited for a click it did not need. It also disagreed with the manual
        # path, which accepts the same node through ``IsA`` in
        # _nodeTreeValidCurrentNode -- so the two answers to "is this node valid for
        # this step?" differed by which one gave it. The sibling protection is intact:
        # there the demanded class is concrete, so the exact check still runs.
        try:
            if node.GetClassName() != node_class and self._nodeClassIsInstantiable(node_class):
                return None
        except Exception:
            return None
        return node

    def _nodeClassIsInstantiable(self, node_class):
        """Whether any node can have ``node_class`` as its own class name.

        Asked of the scene's own registry (``IsNodeClassRegistered``), so no list
        of abstract MRML base classes has to be maintained here and none can go
        stale: a class is registered by handing the scene an INSTANCE of it, so an
        abstract class is never in that list. ``vtkMRMLVolumeNode`` declares
        ``CreateNodeInstance() override = 0``, which is why nothing can register
        it and why no node's ``GetClassName()`` is ever that string.

        Read-only on purpose. The obvious alternative -- creating a probe node with
        ``CreateNodeByClass`` and testing for None -- also answers the question,
        but ``vtkMRMLScene::CreateNodeByClass`` dereferences its result without a
        null check when a default node is registered for the class
        (``node->Reset(defaultNode)``), so probing an abstract class can segfault
        Slicer. Not a risk worth taking to save a click.

        Answers True on any uncertainty, keeping the strict comparison -- and so
        today's behaviour -- for every class this cannot decide. Cached per class:
        it runs whenever a node-pick step opens, and the answer is a property of
        the class, not of the scene.
        """
        cache = getattr(self, "_nodeClassInstantiableCache", None)
        if cache is None:
            cache = self._nodeClassInstantiableCache = {}
        if node_class in cache:
            return cache[node_class]
        instantiable = True
        try:
            scene = slicer.mrmlScene
            if hasattr(scene, "IsNodeClassRegistered"):
                instantiable = bool(scene.IsNodeClassRegistered(node_class))
            else:
                # Same registry, enumerated. Kept so a Slicer without the
                # convenience method degrades to the right answer rather than
                # silently back to the strict comparison.
                instantiable = False
                for index in range(scene.GetNumberOfRegisteredNodeClasses()):
                    registered = scene.GetNthRegisteredNodeClass(index)
                    if registered is not None and registered.GetClassName() == node_class:
                        instantiable = True
                        break
        except Exception:
            logger.debug("Node-class registry probe failed for %s", node_class,
                         exc_info=True)
            instantiable = True
        cache[node_class] = instantiable
        return instantiable

    def _maybeAutoSelectSoleNode(self):
        """Auto-answer a node-pick step that has exactly one candidate.

        Called when a user_choice step OPENS (from _showWorkflowChoice, whose sole
        caller funnels every presentation path). Commits after a settle window and
        only if the count is still one, so a scene that is still filling cannot be
        answered from a momentary count of one.
        """
        state = self._currentWorkflowUiState or {}
        node = self._soleNodeAutoSelectCandidate(state)
        if node is None:
            return
        runtime = self._workflowRuntime
        session = runtime.session
        step_id = state.get("current_step")
        # Once per step OCCURRENCE. _updateWorkflowPanel is a repaint event that
        # runs several times per opening, and the dispatcher has two paths that
        # re-present a waiting step. len(completed_instances) is strictly
        # monotonic forward (_clear_repeat_body truncates completed_steps but not
        # completed_instances) and is truncated on rewind, so two presentations of
        # one opening share a key while a later loop iteration -- which has the
        # terminal step's completion in between -- gets a fresh one.
        key = (session.workflow_id, step_id, len(session.completed_instances))
        seen = getattr(self, "_autoSelectedNodeSteps", None)
        if seen is None:
            seen = self._autoSelectedNodeSteps = set()
        if key in seen:
            return
        seen.add(key)

        node_id = node.GetID()
        node_name = str(node.GetName() or "").strip()
        if not node_name:
            return

        def _commit():
            # Re-check: the scene may have gained a node during the settle window,
            # and the user may have navigated, cancelled or picked manually.
            live = self._currentWorkflowUiState or {}
            if live.get("current_step") != step_id:
                return
            if self._soleNodeAutoSelectCandidate(live) is None:
                return
            candidates = self._workflowNodeCandidateList(live, live.get("node_class"))
            if len(candidates) != 1 or candidates[0].get("id") != node_id:
                logger.info(
                    "Auto-select abandoned for %s: candidate set changed during settle",
                    step_id,
                )
                return
            self._noteAutoSelectedNode(step_id, node_name)
            self._commitWorkflowChoice(node_name)

        # Deferred, not immediate: _commitWorkflowChoice -> _runWorkflowStepDirect
        # re-enters _updateWorkflowPanel BEFORE the step actually runs, so a
        # synchronous commit would recurse through consecutive single-candidate
        # steps and let an inner render tear down containers an outer render is
        # still building.
        qt.QTimer.singleShot(AUTO_SELECT_SOLE_NODE_SETTLE_MS, _commit)

    def _appendWorkflowNotice(self, text, step_id=None):
        """Show a persistent notice in the workflow panel until the next step.

        Deliberately its own label: the action / instruction labels are rewritten
        on every render, so a notice placed there would vanish on the next repaint
        -- which for an automatic choice is the difference between "the user was
        told" and "it happened silently".
        """
        label = getattr(self, "_workflowNoticeLabel", None)
        if label is None:
            return
        self._workflowNoticeText = str(text or "")
        self._workflowNoticeStep = step_id
        label.setText(self._workflowNoticeText)
        label.setVisible(bool(self._workflowNoticeText))

    def _clearWorkflowNotice(self):
        self._workflowNoticeText = ""
        label = getattr(self, "_workflowNoticeLabel", None)
        if label is not None:
            label.setText("")
            label.setVisible(False)

    def _noteAutoSelectedNode(self, step_id, node_name):
        """Record and surface an automatic pick, so it is never silent."""
        try:
            self._recordRoleEvent(
                "Workflow", "choice_auto_selected",
                f"{step_id}: auto-selected '{node_name}' (only candidate)",
            )
        except Exception:
            logger.debug("Recording auto-select role event failed", exc_info=True)
        try:
            self._appendWorkflowNotice(
                f"Auto-selected '{node_name}' — the only matching node in the scene. "
                "Step Back to choose a different one.",
                step_id=step_id,
            )
        except Exception:
            logger.debug("Surfacing auto-select notice failed", exc_info=True)
        logger.info("Workflow %s: auto-selected sole candidate '%s'", step_id, node_name)

    def _workflowNodeCandidateList(self, state, node_class):
        """Scene nodes of ``node_class`` the node picker would offer, in scene order.

        The ONE definition of "the nodes in the widget": scene nodes of the class,
        minus HideFromEditors, minus (in replay) nodes created after the reviewed
        step. It supplies the picker's "no node -> free text" empty gate, the
        _bestNodeMatchIndex default guess, AND the sole-candidate auto-select --
        sharing it is what stops "one node shown" and "one node counted" from ever
        drifting apart.

        In replay, nodes created AFTER the reviewed step carry a subject-hierarchy
        tag (WorkflowRuntime._hide_nodes_after); skipping them keeps the candidate
        list matching the forward view. The exclusion is applied ONLY while
        reviewing, so a stray lingering tag can never hide a node from the live
        picker.
        """
        from SlicerAIAgentLib.WorkflowRuntime import WorkflowRuntime as _WFRT
        _replay_attr = _WFRT.REPLAY_HIDDEN_SH_ATTR
        _in_replay = bool((state or {}).get("replay_previewing"))
        try:
            _shNode = slicer.mrmlScene.GetSubjectHierarchyNode() if _in_replay else None
        except Exception:
            _shNode = None

        def _isReplayHidden(node):
            if _shNode is None:
                return False
            try:
                item = _shNode.GetItemByDataNode(node)
                return bool(item) and _shNode.GetItemAttribute(item, _replay_attr) == "1"
            except Exception:
                return False

        candidates = []
        try:
            for node in slicer.util.getNodesByClass(node_class):
                if node is None:
                    continue
                try:
                    if node.GetHideFromEditors():
                        continue
                except Exception:
                    pass
                if _in_replay and _isReplayHidden(node):
                    continue
                candidates.append({"id": node.GetID(), "name": node.GetName(), "node": node})
        except Exception:
            logger.debug("Enumerating node candidates failed", exc_info=True)
            candidates = []
        return candidates

    def _sceneNodeCount(self, node_class):
        """How many nodes of ``node_class`` the workflow's picker would offer.

        Deliberately routed through ``_workflowNodeCandidateList`` rather than
        ``slicer.util.getNodesByClass`` directly, so "what the precheck counts"
        and "what the picker will show" cannot disagree. The difference is not
        theoretical: a fresh Slicer scene holds three HideFromEditors slice-view
        models, and the naive call reports them as ``vtkMRMLModelNode``s -- which
        would let a two-model procedure start on an empty scene.

        Passes an empty state because the only key the helper reads is
        ``replay_previewing``, and no replay can exist before a workflow starts.
        """
        try:
            return len(self._workflowNodeCandidateList({}, node_class))
        except Exception:
            logger.debug("Scene node count failed for %s", node_class, exc_info=True)
            return 0

    def _nodeTreeValidCurrentNode(self):
        """Return the tree's current node iff it is a real data node of the step's
        ``node_class`` (not a folder/hierarchy row), else None."""
        tree = getattr(self, "_workflowNodeTree", None)
        if tree is None:
            return None
        try:
            node = tree.currentNode()
        except Exception:
            return None
        if node is None:
            return None
        node_class = (self._currentWorkflowUiState or {}).get("node_class")
        if node_class:
            try:
                if not node.IsA(node_class):
                    return None
            except Exception:
                return None
        return node

    # ------------------------------------------------------------------
    # Interaction count gate (expected_count > 0 on a placement step)
    # ------------------------------------------------------------------
    def _resolveInteractionCountNode(self):
        """The markups node whose points the current interaction step counts.

        Resolution: the node the runtime recorded for this step's interaction,
        then the live markups place widget's current node (a wizard page's own
        place button targets it), then the newest fiducial node. None disables the
        gate rather than guessing wrong."""
        step_id = (self._currentWorkflowUiState or {}).get("current_step")
        try:
            from SlicerAIAgentLib.workflow_state import latest_interaction_node_for_step
            _session = self._workflowRuntime.session
            node = latest_interaction_node_for_step(
                step_id,
                getattr(_session, "extension_name", ""),
                getattr(_session, "workflow_id", ""),
            )
            if node is not None:
                return node
        except Exception:
            pass
        try:
            ext = self._workflowRuntime.session.extension_name
            from SlicerAIAgentLib.extension_cli_loader import get_validated_extensions
            metadata = (get_validated_extensions().get(ext) or {}).get("workflow_metadata", {}) or {}
            module_name = str(metadata.get("extension_module_name") or "").strip() or ext
            root = slicer.util.getModule(module_name).widgetRepresentation()
            for pw in slicer.util.findChildren(root, className="qSlicerMarkupsPlaceWidget"):
                try:
                    node = pw.currentNode()
                    if node is not None:
                        return node
                except Exception:
                    continue
        except Exception:
            pass
        return None

    def _updateInteractionCountGate(self):
        """Show placed-vs-expected progress on the Done button while a counted
        placement step waits.

        Advisory, never blocking: the Done button stays ENABLED throughout. The
        cookbook's stated count can be wrong for the path the user actually took
        (e.g. "three times ..." holds for the both-sides choice but the extension
        needs only two-per-level for a single side), and a hard gate would leave
        Cancel as the only way out. The progress text carries the expectation; the
        user decides when the placement is complete."""
        state = self._currentWorkflowUiState or {}
        expected = int(state.get("expected_count") or 0)
        timer = getattr(self, "_workflowCountTimer", None)
        done_label = state.get("done_label") or "Done"
        if expected <= 0 or not state.get("can_done") or state.get("workflow_done"):
            if timer is not None and timer.isActive():
                timer.stop()
            return
        node = self._resolveInteractionCountNode()
        if node is None:
            if timer is not None and timer.isActive():
                timer.stop()
            self._workflowDoneButton.setEnabled(bool(state.get("can_done")))
            self._workflowDoneButton.setText(str(done_label))
            return
        try:
            count = int(node.GetNumberOfDefinedControlPoints())
        except Exception:
            try:
                count = int(node.GetNumberOfControlPoints())
            except Exception:
                count = 0
        self._workflowDoneButton.setEnabled(True)
        self._workflowDoneButton.setText(f"{done_label} ({count}/{expected} points)")
        if timer is None:
            timer = qt.QTimer()
            timer.setInterval(500)
            timer.timeout.connect(self._updateInteractionCountGate)
            self._workflowCountTimer = timer
        if not timer.isActive():
            timer.start()

    def _liveComboItemsByAnchor(self, anchor):
        """Items of the LIVE module combobox whose placeholder first row matches
        ``anchor`` (minus that placeholder). A dynamically-populated source combo
        carries its real items only at runtime; its placeholder row restates the
        question, which is what identifies it among sibling combos."""
        from SlicerAIAgentLib.extension_cli_loader import _norm_anchor_text
        anchor = _norm_anchor_text(anchor)
        if not anchor:
            return []
        try:
            ext = self._workflowRuntime.session.extension_name
            from SlicerAIAgentLib.extension_cli_loader import get_validated_extensions
            metadata = (get_validated_extensions().get(ext) or {}).get("workflow_metadata", {}) or {}
            module_name = str(metadata.get("extension_module_name") or "").strip() or ext
            root = slicer.util.getModule(module_name).widgetRepresentation()
            if root is None:
                return []
        except Exception:
            return []
        for cls in ("ctkComboBox", "QComboBox"):
            try:
                combos = slicer.util.findChildren(root, className=cls)
            except Exception:
                combos = []
            for combo in combos:
                try:
                    items = [combo.itemText(i) for i in range(combo.count)]
                except Exception:
                    continue
                if items and _norm_anchor_text(items[0]) == anchor:
                    return [i for i in items[1:] if str(i).strip()]
        return []

    def _findLiveWizardCombo(self, options, anchor):
        """The extension's live combobox this multi-choice item drives: the one whose
        items contain all `options` (a static list), else whose placeholder first
        item matches `anchor` (a dynamic list). None if not found. Same content
        matching the loader's drive code uses -- no captured widget name needed."""
        from SlicerAIAgentLib.extension_cli_loader import _norm_anchor_text
        anchor_n = _norm_anchor_text(anchor)
        opts = [str(o) for o in (options or [])]
        try:
            ext = self._workflowRuntime.session.extension_name
            from SlicerAIAgentLib.extension_cli_loader import get_validated_extensions
            metadata = (get_validated_extensions().get(ext) or {}).get("workflow_metadata", {}) or {}
            module_name = str(metadata.get("extension_module_name") or "").strip() or ext
            root = slicer.util.getModule(module_name).widgetRepresentation()
            if root is None:
                return None
        except Exception:
            return None
        for cls in ("ctkComboBox", "QComboBox"):
            try:
                combos = slicer.util.findChildren(root, className=cls)
            except Exception:
                combos = []
            for combo in combos:
                try:
                    items = [combo.itemText(i) for i in range(combo.count)]
                except Exception:
                    continue
                if not items:
                    continue
                if opts and all(o in items for o in opts):
                    return combo
                if not opts and _norm_anchor_text(items[0]) == anchor_n:
                    return combo
        return None

    def _driveMultiChoicePreview(self, options, anchor, agent_combo):
        """Drive the extension's live combo to the agent combo's current text so its
        connected handler fires (e.g. sSelector_chosen -> camera focus + slice-plane
        update), giving the same immediate 2D-view feedback as the original widget.
        setCurrentText alone does not fire ctk/Qt 'activated'; emit it explicitly."""
        live = self._findLiveWizardCombo(options, anchor)
        if live is None:
            return
        try:
            text = str(agent_combo.currentText)
        except Exception:
            return
        if not text:
            return
        try:
            live.setCurrentText(text)
        except Exception:
            pass
        try:
            live.activated(text)
        except Exception:
            try:
                live.activated(live.currentIndex)
            except Exception:
                pass

    def _renderWorkflowMultiChoiceForm(self, state):
        """One form for a multi-selection step: a labeled combo per item, one
        Confirm; commits {parameter_name: text} for every item at once. Each combo
        also drives its extension counterpart LIVE on selection, so the 2D views
        update immediately as in the original widget."""
        items = [i for i in (state.get("choice_items") or []) if isinstance(i, dict)]
        if len(items) < 2:
            return False
        container = qt.QWidget()
        form = qt.QFormLayout(container)
        form.setContentsMargins(0, 0, 0, 0)
        self._workflowMultiChoiceCombos = {}
        self._workflowMultiChoiceOrdered = []
        ordered = []  # (combo, options, anchor) in item order (drive order matters)
        for item in items:
            param = str(item.get("parameter_name") or "")
            if not param:
                continue
            options = [
                str(c.get("label", c.get("value", "")))
                for c in (item.get("choices") or []) if isinstance(c, dict)
            ]
            if not options and item.get("live_items"):
                options = [str(o) for o in self._liveComboItemsByAnchor(item.get("question"))]
            combo = qt.QComboBox()
            if options:
                # Lead with an inert placeholder; do NOT pre-select any real option.
                # The user must actively pick, and that pick is what activates the
                # extension geometry (see _MULTI_CHOICE_PLACEHOLDER). Deliberately no
                # default_value: mirrors the original combo, which starts unselected.
                combo.addItem(self._MULTI_CHOICE_PLACEHOLDER)
            for option in options:
                combo.addItem(option)
            combo.setEditable(not options)  # free text only when nothing resolved
            if options:
                combo.setCurrentIndex(0)  # the placeholder -- nothing chosen yet
            form.addRow(str(item.get("question") or param), combo)
            self._workflowMultiChoiceCombos[param] = combo
            ordered.append((combo, options, item.get("question")))
        if not self._workflowMultiChoiceCombos:
            container.setParent(None)
            return False
        self._workflowMultiChoiceOrdered = list(ordered)
        # Wire each combo to drive its live counterpart on USER selection, for the
        # immediate 2D-view feedback the original widget gives. Deliberately NOT
        # driven on initial render: on a loop-back re-entry the combos default to the
        # first (already-configured) item, and some handlers are destructive (PSP's
        # diameter handler calls Helper.Screw, which delNode()s + recreates the screw
        # line at a DEFAULT position). Driving on render would silently reset the
        # item the user already fixed in a prior iteration. The FINAL selections are
        # driven once, in item order, at commit instead (see the confirm handler).
        for combo, options, anchor in ordered:
            combo.currentIndexChanged.connect(
                lambda *a, o=options, an=anchor, cb=combo:
                    self._driveMultiChoicePreview(o, an, cb)
            )
        button = qt.QPushButton("Confirm")
        button.setToolTip("Apply these selections and continue")
        button.clicked.connect(self._onWorkflowMultiChoiceConfirmed)
        form.addRow(button)
        self._workflowMultiChoiceContainer = container
        self._workflowChoiceLayout.addWidget(container, 1)
        container.setVisible(True)
        return True

    def _onWorkflowMultiChoiceConfirmed(self):
        combos = getattr(self, "_workflowMultiChoiceCombos", {}) or {}
        values = {}
        for param, combo in combos.items():
            try:
                text = str(combo.currentText).strip()
            except Exception:
                text = ""
            if text and text != self._MULTI_CHOICE_PLACEHOLDER:
                values[param] = text
        if len(values) < len(combos):
            return  # every selector needs a real (non-placeholder) answer before committing
        # Drive the extension's live combos to the FINAL selections, in item order,
        # so every connected handler fires for the CURRENT item -- covers combos the
        # user left at their default (no change event) and guarantees the ordering a
        # later handler depends on (e.g. the diameter handler reads the fiducial index
        # the puncture-site handler set). This targets only the item the user is
        # configuring now (its selected index), never a previously fixed one.
        for combo, options, anchor in getattr(self, "_workflowMultiChoiceOrdered", []) or []:
            self._driveMultiChoicePreview(options, anchor, combo)
        self._commitWorkflowChoice(values)

    @staticmethod
    def _isComboWidget(widget):
        """True for a QComboBox / ctkComboBox cell widget. Duck-typed: the Qt class
        name first, then the combo-specific API (``itemText`` + ``count``), so it
        works for whatever PythonQt hands back as the cell widget."""
        if widget is None:
            return False
        try:
            if "ComboBox" in widget.className():
                return True
        except Exception:
            pass
        try:
            widget.itemText  # combo-specific method
            _ = widget.count  # combo-specific property
            return True
        except Exception:
            return False

    def _findLivePerRowComboTable(self):
        """The extension's live QTableWidget that has per-row combo cell widgets
        (e.g. the landmarks Level/Side/Landmarks table). None when none exists.

        Searches the whole module representation -- the same root
        ``_snapshot_review_table`` uses (a wizard's ``workflow.currentStep()`` is a
        step CONTROLLER, not a QWidget, so findChildren on it reaches nothing). The
        per-row-combo filter uniquely identifies the table: only this kind carries
        combo cell widgets (a results table is item-based). When several qualify,
        the one with the most rows wins.
        """
        try:
            ext = self._workflowRuntime.session.extension_name
            from SlicerAIAgentLib.extension_cli_loader import get_validated_extensions
            metadata = (get_validated_extensions().get(ext) or {}).get("workflow_metadata", {}) or {}
            module_name = str(metadata.get("extension_module_name") or "").strip() or ext
            root = slicer.util.getModule(module_name).widgetRepresentation()
        except Exception:
            return None
        try:
            tables = slicer.util.findChildren(root, className="QTableWidget")
        except Exception:
            tables = []
        best = None
        best_rows = 0
        for table in tables:
            try:
                has_combo = False
                for c in range(table.columnCount):
                    for r in range(table.rowCount):
                        if self._isComboWidget(table.cellWidget(r, c)):
                            has_combo = True
                            break
                    if has_combo:
                        break
                if has_combo and table.rowCount > best_rows:
                    best, best_rows = table, table.rowCount
            except Exception:
                continue
        return best

    def _renderWorkflowNativeWidget(self, state):
        """Reproduce the extension's own per-row-combo selection table in the agent
        panel, populated from the live widget, with a Confirm button that writes the
        selections back to the live combos and advances. Falls back to a plain
        Confirm when no such table resolves (still lets the user proceed)."""
        container = qt.QWidget()
        vbox = qt.QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        self._nativeWidgetLiveTable = None
        self._nativeWidgetComboCol = None
        self._nativeWidgetRowCombos = []

        live = self._findLivePerRowComboTable()
        if live is not None:
            try:
                cols, rows = live.columnCount, live.rowCount
                combo_col = None
                for c in range(cols):
                    if any(self._isComboWidget(live.cellWidget(r, c)) for r in range(rows)):
                        combo_col = c
                        break
                headers = []
                for c in range(cols):
                    h = live.horizontalHeaderItem(c)
                    headers.append(str(h.text()) if h is not None else f"Col {c + 1}")
                agent = qt.QTableWidget(rows, cols)
                agent.setHorizontalHeaderLabels(headers)
                agent.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)
                agent.verticalHeader().setVisible(False)
                agent.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
                for r in range(rows):
                    for c in range(cols):
                        if c == combo_col and self._isComboWidget(live.cellWidget(r, c)):
                            live_combo = live.cellWidget(r, c)
                            combo = qt.QComboBox()
                            for i in range(live_combo.count):
                                combo.addItem(live_combo.itemText(i))
                            try:
                                combo.setCurrentIndex(live_combo.currentIndex)
                            except Exception:
                                pass
                            agent.setCellWidget(r, c, combo)
                            self._nativeWidgetRowCombos.append((r, combo))
                        else:
                            item = live.item(r, c)
                            agent.setItem(r, c, qt.QTableWidgetItem(
                                str(item.text()) if item is not None else ""))
                agent.setMinimumHeight(110)
                agent.setMaximumHeight(260)
                vbox.addWidget(agent)
                self._nativeWidgetLiveTable = live
                self._nativeWidgetComboCol = combo_col
            except Exception:
                logger.debug("Reproducing the extension's per-row table failed", exc_info=True)
                self._nativeWidgetLiveTable = None
                self._nativeWidgetRowCombos = []

        button = qt.QPushButton("Confirm")
        button.setToolTip("Apply these selections in the module and continue")
        button.clicked.connect(self._onWorkflowNativeWidgetConfirmed)
        vbox.addWidget(button)
        self._workflowNativeWidgetContainer = container
        self._workflowChoiceLayout.addWidget(container, 1)
        container.setVisible(True)
        return True

    def _onWorkflowNativeWidgetConfirmed(self):
        # Write each reproduced selection back to the extension's live combo so its
        # own connected handlers / downstream steps see the state a manual user
        # would have left. Fail-soft per row.
        live = getattr(self, "_nativeWidgetLiveTable", None)
        combo_col = getattr(self, "_nativeWidgetComboCol", None)
        if live is not None and combo_col is not None:
            for row, agent_combo in getattr(self, "_nativeWidgetRowCombos", []):
                try:
                    live_combo = live.cellWidget(row, combo_col)
                    if self._isComboWidget(live_combo):
                        live_combo.setCurrentIndex(agent_combo.currentIndex)
                        try:
                            live_combo.activated(agent_combo.currentIndex)
                        except Exception:
                            pass
                except Exception:
                    logger.debug("Native-widget write-back (row %s) failed", row, exc_info=True)
        # Advance the step (the extension's widget holds the selection; no value).
        if self._currentWorkflowUiState.get("replay_previewing"):
            index = self._currentWorkflowUiState.get("preview_index")
            if index is not None:
                self._rerunFromCheckpoint(index, {"choice_value": ""})
            return
        step_id = self._currentWorkflowUiState.get("current_step")
        if step_id:
            self.sendButton.setEnabled(False)
            self._runWorkflowStepDirect(step_id, "proceed")

    def _renderWorkflowReviewTable(self, state):
        """Read-only results table for a review checkpoint (review_op).

        Renders the snapshot the loader read from the extension's own UI (or a
        table node). With no snapshot the step still works as instructions +
        Confirm -- the results are visible in the module panel itself.
        """
        table_data = state.get("review_table") or {}
        headers = [str(h) for h in (table_data.get("headers") or [])]
        rows = table_data.get("rows") or []
        if not headers or not rows:
            return
        container = qt.QWidget()
        vbox = qt.QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        table = qt.QTableWidget(len(rows), len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(qt.QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(qt.QAbstractItemView.NoSelection)
        table.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        for r, row in enumerate(rows):
            for c in range(len(headers)):
                value = str(row[c]) if c < len(row) else ""
                table.setItem(r, c, qt.QTableWidgetItem(value))
        table.setMinimumHeight(110)
        table.setMaximumHeight(240)
        vbox.addWidget(table)
        self._workflowReviewContainer = container
        self._workflowChoiceLayout.addWidget(container, 1)
        container.setVisible(True)

    def _nodeTreeCurrentSegmentRef(self):
        """``(segmentationNode, segmentId)`` for the tree's current row, else
        ``(None, "")`` — for steps whose source selector picks a SEGMENT.

        Mirrors the resolution any such extension must perform, using Slicer's own
        segment-row contract: a segment row carries the segmentID subject-hierarchy
        attribute, and a segmentation row is unambiguous only when it holds exactly one
        segment. ``currentNode()`` is structurally unusable here — a segment row has no
        data node — which is why this reads ``currentItem()``.
        """
        tree = getattr(self, "_workflowNodeTree", None)
        if tree is None:
            return None, ""
        try:
            shNode = tree.subjectHierarchyNode()
            itemId = tree.currentItem()
            if shNode is None or not itemId:
                return None, ""
            segmentId = shNode.GetItemAttribute(
                itemId, slicer.vtkMRMLSegmentationNode.GetSegmentIDAttributeName())
            segNode = slicer.vtkSlicerSegmentationsModuleLogic.\
                GetSegmentationNodeForSegmentSubjectHierarchyItem(itemId, slicer.mrmlScene)
            if segNode is None:
                return None, ""
            if not segmentId:
                # The segmentation's own row: only unambiguous with a single segment.
                segmentation = segNode.GetSegmentation()
                if segmentation is not None and segmentation.GetNumberOfSegments() == 1:
                    ids = vtk.vtkStringArray()
                    segmentation.GetSegmentIDs(ids)
                    segmentId = ids.GetValue(0)
            return segNode, segmentId
        except Exception:
            logger.debug("Segment-ref resolution from node tree failed", exc_info=True)
            return None, ""

    def _updateNodeTreeSelectButtonEnabled(self):
        button = getattr(self, "_workflowNodeTreeSelectButton", None)
        if button is None:
            return
        if (self._currentWorkflowUiState or {}).get("segment_ref_selection"):
            # A segment pick is only complete once a segment is actually resolved:
            # an empty id is what the source's own enable-guard rejects, and it makes
            # the downstream step fail rather than merely pick wrongly.
            node, segmentId = self._nodeTreeCurrentSegmentRef()
            button.setEnabled(node is not None and bool(segmentId))
            return
        button.setEnabled(self._nodeTreeValidCurrentNode() is not None)

    def _onWorkflowNodeTreeSelectionChanged(self, *args):
        self._updateNodeTreeSelectButtonEnabled()

    def _bestNodeMatchIndex(self, candidates, default_value, keywords):
        """Best candidate index: exact recorded name → keyword substring → first.

        Keyword scoring uses substring containment (case-insensitive) so prefix
        keywords like 'mandib' match the node name 'MandibleSegmentation'; the
        distinctive keywords then break the tie against shared words like
        'segmentation'. It is only a default guess — the user picks from the
        node tree.
        """
        names = [str(c.get("name") or "") for c in candidates]
        dv = str(default_value or "").strip()
        if dv:
            for i, name in enumerate(names):
                if name == dv:
                    return i
        kws = [str(k).strip().lower() for k in (keywords or []) if len(str(k).strip()) >= 3]
        if kws:
            best_i, best_score = 0, 0
            for i, name in enumerate(names):
                low = name.lower()
                score = sum(1 for k in kws if k in low)
                if score > best_score:
                    best_i, best_score = i, score
            if best_score > 0:
                return best_i
        return 0

    def _commitWorkflowChoice(self, value):
        """Hand a chosen value to the runtime (replay-preview or live), the shared tail
        of every node-tree commit."""
        if self._currentWorkflowUiState.get("replay_previewing"):
            index = self._currentWorkflowUiState.get("preview_index")
            if index is not None:
                self._rerunFromCheckpoint(index, {"choice_value": value})
            return
        step_id = self._currentWorkflowUiState.get("current_step")
        if step_id:
            self.sendButton.setEnabled(False)
            self._runWorkflowStepDirect(step_id, "choice_made", args={"choice_value": value})

    def _onWorkflowNodeTreeSelected(self):
        if (self._currentWorkflowUiState or {}).get("segment_ref_selection"):
            # A segment pick is a (node, segment id) PAIR: the segment id is what the
            # source's handler stores, and a name cannot identify a segment (segment
            # names are not unique). Commit both halves.
            node, segmentId = self._nodeTreeCurrentSegmentRef()
            if node is None or not segmentId:
                return
            segmentName = ""
            try:
                segment = node.GetSegmentation().GetSegment(segmentId)
                segmentName = str(segment.GetName() or "") if segment else ""
            except Exception:
                logger.debug("Segment name lookup failed", exc_info=True)
            return self._commitWorkflowChoice({
                "node_id": node.GetID(),
                "node_name": str(node.GetName() or ""),
                "segment_id": segmentId,
                "segment_name": segmentName,
            })
        node = self._nodeTreeValidCurrentNode()
        if node is None:
            return
        name = ""
        try:
            name = str(node.GetName() or "").strip()
        except Exception:
            name = ""
        if not name:
            return
        self._commitWorkflowChoice(name)

    # ------------------------------------------------------------------
    # Segment-selection step (qMRMLSegmentsTableView)
    # ------------------------------------------------------------------
    def _resolveParamNodeFieldNodeID(self, field):
        """Live MRML node ID held by a parameterNodeWrapper ``field`` on the active
        workflow extension's parameter node, or "" if it cannot be resolved.

        Used to bind a segments table to the exact segmentation the source binds it
        to (e.g. ``OutputFracSeg``), captured by the pipeline as
        ``segmentation_target_param``. Best-effort: runs in the agent's own Python
        (not the sandbox), so attribute access is fine; any failure returns "" and
        the caller falls back to keyword best-match.
        """
        field = str(field or "").strip()
        if not field:
            return ""
        runtime = getattr(self, "_workflowRuntime", None)
        session = getattr(runtime, "session", None) if runtime is not None else None
        ext = getattr(session, "extension_name", None) if session is not None else None
        if not ext:
            return ""
        module_name = ext
        try:
            from SlicerAIAgentLib.ExtensionCLILoader import get_validated_extensions
            meta = (get_validated_extensions().get(ext) or {}).get("workflow_metadata", {}) or {}
            module_name = meta.get("extension_module_name") or ext
        except Exception:
            module_name = ext
        widget = None
        try:
            widget = slicer.util.getModuleWidget(module_name)
        except Exception:
            widget = None
        if widget is None:
            return ""
        paramNode = None
        for getter in (
            lambda: widget.logic.getParameterNode(),
            lambda: widget._parameterNode,
            lambda: widget.getParameterNode(),
        ):
            try:
                pn = getter()
            except Exception:
                pn = None
            if pn is not None:
                paramNode = pn
                break
        if paramNode is None:
            return ""
        try:
            node = getattr(paramNode, field, None)
            if node is not None and hasattr(node, "GetID"):
                return str(node.GetID() or "")
        except Exception:
            return ""
        return ""

    def _preferredSegmentationIndex(self, candidates, state):
        """Index of the segmentation to default-select among ``candidates``:
        the exact pipeline-captured target field first, then name/keyword
        best-match, then the first candidate."""
        target_param = str(state.get("segmentation_target_param") or "").strip()
        if target_param:
            try:
                target_id = self._resolveParamNodeFieldNodeID(target_param)
                if target_id:
                    for i, c in enumerate(candidates):
                        if c.get("id") == target_id:
                            return i
            except Exception:
                logger.debug("Resolving segmentation target_param failed", exc_info=True)
        try:
            return self._bestNodeMatchIndex(
                candidates, state.get("default_value"), state.get("segmentation_keywords") or []
            )
        except Exception:
            logger.debug("Segmentation best-match failed", exc_info=True)
        return 0

    def _renderWorkflowSegmentsTable(self, state):
        """Show a real qMRMLSegmentsTableView so the user can untick individual
        segments/fragments on a segmentation node, exactly like the original
        extension's selector. Toggling the eye column sets per-segment visibility
        (``vtkMRMLSegmentationDisplayNode.SetSegmentVisibility``), which is the
        same state the extension's downstream code reads; clicking Done simply
        advances (no choice value is invented).

        Returns True if it rendered (>=1 selectable segmentation exists), or False
        to let the caller fall back to the node tree / free-text box.
        """
        node_class = state.get("segmentation_node_class") or "vtkMRMLSegmentationNode"
        # Candidate segmentations = scene nodes of node_class, minus HideFromEditors
        # (mirrors the node tree's exclusion / empty gate).
        candidates = []
        try:
            for node in slicer.util.getNodesByClass(node_class):
                if node is None:
                    continue
                try:
                    if node.GetHideFromEditors():
                        continue
                except Exception:
                    pass
                candidates.append({"id": node.GetID(), "name": node.GetName(), "node": node})
        except Exception:
            logger.debug("Enumerating segmentation candidates failed", exc_info=True)
            candidates = []
        if not candidates:
            return False

        container = qt.QWidget()
        vbox = qt.QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)

        # Which segmentation to show. Prefer the exact target the source binds the
        # table to (segmentation_target_param -> a parameterNodeWrapper field,
        # captured by the pipeline); else default-guess by name keywords (e.g.
        # 'fracture' vs 'pelvis'); else the first. With more than one, also offer a
        # combo so the user can switch.
        idx = self._preferredSegmentationIndex(candidates, state)
        if not (0 <= idx < len(candidates)):
            idx = 0
        seg_node = candidates[idx]["node"]
        if len(candidates) > 1:
            combo = slicer.qMRMLNodeComboBox()
            combo.nodeTypes = [node_class]
            combo.addEnabled = False
            combo.removeEnabled = False
            combo.renameEnabled = False
            combo.noneEnabled = False
            combo.showHidden = False
            combo.setMRMLScene(slicer.mrmlScene)
            try:
                combo.setCurrentNodeID(candidates[idx]["id"])
                seg_node = candidates[idx]["node"]
            except Exception:
                logger.debug("Defaulting segmentation combo failed", exc_info=True)
            cur = combo.currentNode()
            if cur is not None:
                seg_node = cur
            combo.currentNodeChanged.connect(self._onWorkflowSegmentsComboChanged)
            self._workflowSegmentsCombo = combo
            vbox.addWidget(combo)

        table = slicer.qMRMLSegmentsTableView()
        try:
            table.setMRMLScene(slicer.mrmlScene)
        except Exception:
            logger.debug("Segments table setMRMLScene failed", exc_info=True)
        # Reproduce the source selector's columns: per-segment eye (visibility),
        # colour and opacity (the original qMRMLSegmentsTableView shows all three).
        # Keep the segmentation-editor status column hidden — it is not part of the
        # extension's fragment selector. Wrapped individually because the available
        # column setters vary across Slicer builds.
        for _meth, _arg in (
            ("setVisibilityColumnVisible", True),
            ("setColorColumnVisible", True),
            ("setOpacityColumnVisible", True),
            ("setStatusColumnVisible", False),
            ("setHeaderVisible", True),
        ):
            try:
                getattr(table, _meth)(_arg)
            except Exception:
                logger.debug("Segments table %s failed", _meth, exc_info=True)
        try:
            table.setSelectionMode(qt.QAbstractItemView.NoSelection)
        except Exception:
            logger.debug("Segments table selection-mode setup failed", exc_info=True)
        table.setMinimumHeight(140)
        table.setMaximumHeight(260)
        table.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Fixed)
        self._workflowSegmentsTable = table
        self._bindSegmentsTable(seg_node)

        button = qt.QPushButton(state.get("done_label") or "Done")
        button.setToolTip("Finish selecting and continue")
        button.clicked.connect(self._onWorkflowSegmentsDone)

        vbox.addWidget(table, 1)
        vbox.addWidget(button)
        self._workflowSegmentsContainer = container
        self._workflowChoiceLayout.addWidget(container, 1)
        container.setVisible(True)
        return True

    def _renderWorkflowSegmentNamePicker(self, state):
        """Show a single-pick combobox reproducing the extension's own content
        combobox (its "Template" / "Fragment" / "Screw" selector), so the user picks
        from a LIST instead of typing into a text box. The picked name flows through
        choice_made -> choice_value identically to a literal-choice step, and the
        preview mirrors it onto the live source combobox so its connected handler
        fires.

        Two sources of the option list, in this order:

        1. The live source combobox's own items. Authoritative whenever available,
           because these ARE the options the extension offers.
        2. The segment names of the segmentation the step points at -- the original
           behaviour, kept for a step whose source control is not reachable or not
           yet populated.

        The order matters. An extension's content combobox is often filled at
        runtime from nodes it just made, so its items may be model names with no
        segmentation behind them at all; reconstruction then finds nothing, and
        before (1) existed the panel fell back to a free-TEXT box asking the surgeon
        to type an option they were meant to choose from a list.

        Returns True if it rendered, or False so the caller falls back to the
        free-text box (never the node tree).
        """
        names = self._liveSourceComboItems(state) or self._segmentNamesForPicker(state)
        if not names:
            return False
        return self._buildWorkflowSegmentNamePicker(state, names)

    def _liveSourceComboItems(self, state):
        """The items currently in the extension's OWN source combobox, or [].

        This is the authoritative answer whenever it is available, and it is tried
        BEFORE reconstructing names from a segmentation. An extension's content
        combobox is frequently populated at runtime from nodes it just made --
        ``for node in self._templateModelNodes: self.ui.templateSelector.addItem(
        node.GetName())`` -- so its items are model names, not any segmentation's
        segments, and no static reconstruction can produce them: they do not exist
        until the extension builds them. Reconstruction then finds nothing, the
        picker declines, and the panel falls back to a free-TEXT box asking the
        surgeon to type an option they were supposed to choose from a list.

        Reading the live control removes the inference entirely -- the options
        shown are the options the extension itself offers, whatever filled them.
        Silent [] on any miss (module not entered, no such widget, empty combo), so
        the segmentation path and then free text still follow.
        """
        source_widget = str(state.get("segment_name_source_widget") or "").strip()
        control = self._resolveLiveSourceControl(source_widget)
        if control is None:
            return []
        try:
            count = int(control.count)
        except Exception:
            return []
        items = []
        for index in range(count):
            try:
                text = str(control.itemText(index) or "").strip()
            except Exception:
                continue
            if text:
                items.append(text)
        return items

    def _resolveLiveSourceControl(self, source_widget):
        """The extension's live control named `source_widget`, or None.

        Mirrors the generator's own resolution order (``_resolve_qt_control_lines``):
        the loaded ``.ui`` object, then a direct attribute, then an objectName search
        of the widget tree. A control built in code rather than in Qt Designer has no
        ``.ui`` entry, so stopping at the first form would miss it.
        """
        if not source_widget:
            return None
        module_name = self._workflowModuleName()
        if not module_name:
            return None
        try:
            widget = slicer.util.getModuleWidget(module_name)
        except Exception:
            widget = None
        if widget is None:
            return None
        control = getattr(getattr(widget, "ui", None), source_widget, None)
        if control is None:
            control = getattr(widget, source_widget, None)
        if control is None:
            try:
                found = slicer.util.findChildren(widget, name=source_widget)
                control = found[0] if found else None
            except Exception:
                control = None
        return control

    def _segmentNamesForPicker(self, state):
        """Segment names reconstructed from the segmentation this step points at, or [].

        The original resolution: find the segmentation (by bound target field or by
        widget-name keyword when several exist) and list its segments in order.
        """
        node_class = state.get("segmentation_node_class") or "vtkMRMLSegmentationNode"
        candidates = []
        try:
            for node in slicer.util.getNodesByClass(node_class):
                if node is None:
                    continue
                try:
                    if node.GetHideFromEditors():
                        continue
                except Exception:
                    pass
                candidates.append({"id": node.GetID(), "name": node.GetName(), "node": node})
        except Exception:
            logger.debug("Enumerating segmentation candidates failed", exc_info=True)
            candidates = []
        if not candidates:
            return []
        # Safety for the deterministic content-combobox signal: with more than one
        # segmentation and no way to pick the right one (no bound target field and
        # no widget-name keyword match), do NOT guess -- fall through to the
        # free-text box so a non-segment content combobox isn't shown a random
        # segmentation's segments.
        if len(candidates) > 1:
            target = str(state.get("segmentation_target_param") or "").strip()
            kws = [str(k).lower() for k in (state.get("segmentation_keywords") or []) if len(str(k)) >= 3]
            resolved = bool(target and self._resolveParamNodeFieldNodeID(target))
            if not resolved and kws:
                resolved = any(
                    any(k in str(c.get("name") or "").lower() for k in kws) for c in candidates
                )
            if not resolved:
                return []
        idx = self._preferredSegmentationIndex(candidates, state)
        if not (0 <= idx < len(candidates)):
            idx = 0
        seg_node = candidates[idx]["node"]
        # Segment names in segment order (the source combobox lists them all).
        names = []
        try:
            seg = seg_node.GetSegmentation()
            for i in range(seg.GetNumberOfSegments()):
                sid = seg.GetNthSegmentID(i)
                nm = seg.GetSegment(sid).GetName() if sid else ""
                if nm:
                    names.append(str(nm))
        except Exception:
            logger.debug("Enumerating segment names failed", exc_info=True)
            names = []
        return names

    def _buildWorkflowSegmentNamePicker(self, state, names):
        """Render the single-pick combobox over `names` and wire it up."""
        container = qt.QWidget()
        vbox = qt.QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        combo = qt.QComboBox()
        for nm in names:
            combo.addItem(nm)
        # Restore the recorded pick when replaying back to this step; index 0 only when
        # there is nothing to restore (the live path, where default_value is unset).
        _recorded = str(state.get("default_value") or "").strip()
        _recorded_index = names.index(_recorded) if _recorded in names else 0
        combo.setCurrentIndex(_recorded_index)
        button = qt.QPushButton(state.get("choice_label") or "Select")
        button.setToolTip("Pick this item and continue")
        button.clicked.connect(self._onWorkflowSegmentNameSelected)
        vbox.addWidget(combo)
        vbox.addWidget(button)
        self._workflowSegmentNameCombo = combo
        self._workflowSegmentNameContainer = container
        # Live preview: as the user changes the selection, drive the extension's own
        # source combobox so its connected handler fires immediately (the 3D
        # interaction handles track the selection, like the original extension).
        # Connected after populate/setCurrentIndex so it doesn't fire on build.
        try:
            combo.currentIndexChanged.connect(self._onWorkflowSegmentNamePreview)
        except Exception:
            pass
        self._workflowChoiceLayout.addWidget(container, 1)
        container.setVisible(True)
        # Show the default (first) fragment's handles right away.
        self._onWorkflowSegmentNamePreview()
        return True

    def _onWorkflowSegmentNameSelected(self):
        combo = getattr(self, "_workflowSegmentNameCombo", None)
        if combo is None:
            return
        try:
            name = str(combo.currentText or "").strip()
        except Exception:
            name = ""
        if not name:
            return
        if self._currentWorkflowUiState.get("replay_previewing"):
            index = self._currentWorkflowUiState.get("preview_index")
            if index is not None:
                self._rerunFromCheckpoint(index, {"choice_value": name})
            return
        step_id = self._currentWorkflowUiState.get("current_step")
        if step_id:
            self.sendButton.setEnabled(False)
            self._runWorkflowStepDirect(step_id, "choice_made", args={"choice_value": name})

    def _workflowModuleName(self):
        """The active workflow extension's Slicer module name (for getModuleWidget),
        resolved like _resolveParamNodeFieldNodeID. "" if unavailable."""
        runtime = getattr(self, "_workflowRuntime", None)
        session = getattr(runtime, "session", None) if runtime is not None else None
        ext = getattr(session, "extension_name", None) if session is not None else None
        if not ext:
            return ""
        try:
            from SlicerAIAgentLib.ExtensionCLILoader import get_validated_extensions
            meta = (get_validated_extensions().get(ext) or {}).get("workflow_metadata", {}) or {}
            return meta.get("extension_module_name") or ext
        except Exception:
            return ext

    def _onWorkflowSegmentNamePreview(self, _index=None):
        """Mirror the picker's current selection onto the extension's live source
        combobox (e.g. fragmentSelector) so its connected handler (onFragmentSelected)
        fires immediately -- the 3D interaction handles track the selection, like the
        original extension. Visual only; the authoritative choice is committed by the
        Select button. Runs in the agent process (not the sandbox); any miss (no
        module widget / no ui / no such widget / name absent) is a silent no-op."""
        state = getattr(self, "_currentWorkflowUiState", None) or {}
        if state.get("replay_previewing"):
            return
        source_widget = str(state.get("segment_name_source_widget") or "").strip()
        if not source_widget:
            return
        combo = getattr(self, "_workflowSegmentNameCombo", None)
        if combo is None:
            return
        try:
            name = str(combo.currentText or "").strip()
        except Exception:
            name = ""
        if not name:
            return
        module_name = self._workflowModuleName()
        if not module_name:
            return
        try:
            widget = slicer.util.getModuleWidget(module_name)
        except Exception:
            widget = None
        sel = getattr(getattr(widget, "ui", None), source_widget, None) if widget is not None else None
        if sel is None:
            return
        try:
            idx = sel.findText(name)
            if idx >= 0:
                sel.setCurrentIndex(idx)
        except Exception:
            pass

    def _releaseModuleSessionTools(self):
        """Release any core-module tool a finished workflow left active.

        A generated session drives the Segment Editor widget directly and never enters
        the module, so Slicer's own ``SegmentEditor.exit()`` -- which does
        ``setActiveEffect(None)`` -- never runs. The last effect a session activated
        (e.g. Islands) therefore keeps its cursor and view observations installed in
        every slice view after the workflow ends, so the pointer carries the effect's
        icon around the 2D views. Reproduce that exit contract.

        The generated session tears itself down at the end of its run; this is the net
        for the paths that never reach it (cancelled mid-session, an older generated
        CLI, a module with no session driver). Idempotent and fail-soft: a no-op when
        nothing is active.
        """
        try:
            editor = slicer.modules.segmenteditor.widgetRepresentation().self().editor
            if editor.activeEffect() is not None:
                editor.setActiveEffect(None)
        except Exception:
            logger.debug("Releasing module-session tools failed", exc_info=True)

    # ---- Numeric range slider (e.g. Segment Editor Threshold range) ----------
    def _activeSegmentEditorEffect(self):
        """The active Segment Editor effect (qSlicer...Effect) or None. Generic:
        the same shared editor the generated steps drive."""
        try:
            editor = slicer.modules.segmenteditor.widgetRepresentation().self().editor
            return editor.activeEffect()
        except Exception:
            return None

    def _activeEffectRangeWidget(self):
        """A live double-handled range widget (ctkRangeWidget) inside the active
        Segment Editor effect's options, or None. Generic: searches the effect's
        options frame for any range widget rather than assuming a specific effect
        or attribute name, so it works for the Threshold effect or any other
        range-driven effect."""
        effect = self._activeSegmentEditorEffect()
        if effect is None:
            return None
        try:
            frame = effect.optionsFrame()
        except Exception:
            frame = None
        if frame is None:
            return None
        try:
            found = slicer.util.findChildren(frame, className="ctkRangeWidget")
        except Exception:
            found = []
        return found[0] if found else None

    def _activeSourceVolume(self):
        """The volume whose scalar range seeds the slider limits: prefer the
        Segment Editor's bound source volume, else the most-recent non-labelmap
        scalar volume with image data. None if none available. Generic."""
        try:
            editor = slicer.modules.segmenteditor.widgetRepresentation().self().editor
            vol = editor.sourceVolumeNode()
            if vol is not None and vol.GetImageData() is not None:
                return vol
        except Exception:
            pass
        try:
            nodes = list(slicer.util.getNodesByClass("vtkMRMLScalarVolumeNode"))
            for vol in reversed(nodes):
                if (vol is not None
                        and not vol.IsA("vtkMRMLLabelMapVolumeNode")
                        and vol.GetImageData() is not None):
                    return vol
        except Exception:
            pass
        return None

    def _renderWorkflowRangeSlider(self, state):
        """Render a draggable double-handled min/max slider for a numeric RANGE
        step (like the Segment Editor Threshold range), instead of a literal
        button or free-text box. Limits + current handles are seeded, in order,
        from: the live active effect's range widget; the extension's captured
        .ui min/max; the source-volume scalar range. Dragging live-previews the
        target; the Set button commits [min, max] via choice_made.

        Returns True if it rendered, or False so the caller falls back to the
        free-text box (never a node tree). Generic: no extension/step-specific
        strings.
        """
        limit_lo = limit_hi = cur_min = cur_max = single_step = None

        # 1. Mirror the live active effect's range widget exactly (fully generic).
        live = self._activeEffectRangeWidget()
        if live is not None:
            try:
                limit_lo, limit_hi = float(live.minimum), float(live.maximum)
                cur_min, cur_max = float(live.minimumValue), float(live.maximumValue)
                single_step = float(live.singleStep)
            except Exception:
                limit_lo = limit_hi = cur_min = cur_max = None

        # 2. Extension's own .ui range widget limits (authoritative path).
        if limit_lo is None:
            rmin, rmax = state.get("range_min"), state.get("range_max")
            if rmin is not None and rmax is not None:
                try:
                    limit_lo, limit_hi = float(rmin), float(rmax)
                    single_step = float(state.get("range_step")) if state.get("range_step") else None
                except Exception:
                    limit_lo = limit_hi = None

        # 3. Derive from the source-volume scalar range (e.g. Threshold effect).
        if limit_lo is None:
            vol = self._activeSourceVolume()
            if vol is not None:
                try:
                    limit_lo, limit_hi = (float(x) for x in vol.GetImageData().GetScalarRange())
                except Exception:
                    limit_lo = limit_hi = None

        if limit_lo is None or limit_hi is None or limit_hi <= limit_lo:
            return False  # no sensible limits -> free-text fallback

        # A default INHERITED from an earlier step ("The default threshold is the
        # same as in Step 5") outranks the live widget: re-activating the tool for
        # this pass has just reset that widget to the tool's own factory default,
        # so the live value is precisely what the cookbook says NOT to use. Limits
        # still come from the sources above; only the handles move.
        inherited = state.get("inherited_default")
        # The panel re-renders the same step's slider more than once per step, and
        # the LAST render is what the user sees. A later refresh can carry a state
        # dict built without this key, which would silently fall back to the live
        # widget — the tool's factory default — undoing the inheritance. Remember
        # the value per step so every render of that step seeds identically.
        step_key = str(state.get("current_step") or "")
        memo = getattr(self, "_workflowInheritedDefaults", None)
        if memo is None:
            memo = {}
            self._workflowInheritedDefaults = memo
        if step_key:
            if inherited is not None:
                memo[step_key] = inherited
            else:
                inherited = memo.get(step_key)
        _live_seed = [cur_min, cur_max]
        _seed_source = "live" if cur_min is not None else "none"
        if isinstance(inherited, (list, tuple)) and len(inherited) == 2:
            try:
                cur_min, cur_max = float(inherited[0]), float(inherited[1])
                _seed_source = "inherited"
            except (TypeError, ValueError):
                pass
        # Record how the handles were seeded into the run's event log, so a wrong
        # default stays diagnosable from the artifacts. Log only — never printed.
        try:
            _rt = getattr(self, "_workflowRuntime", None)
            if _rt is not None:
                _rt._write_event("range_slider_seeded", {
                    "step_id": step_key,
                    "seed_source": _seed_source,
                    "inherited_default": inherited,
                    "state_has_key": "inherited_default" in state,
                    "live": _live_seed,
                    "limits": [limit_lo, limit_hi],
                    "seeded": [cur_min, cur_max],
                })
        except Exception:
            pass

        # Seed the handles: live values, else a declared default, else 25%-100%
        # (matches the Threshold effect's own default).
        if cur_min is None or cur_max is None:
            default = state.get("range_default")
            if isinstance(default, (list, tuple)) and len(default) == 2:
                try:
                    cur_min, cur_max = float(default[0]), float(default[1])
                except Exception:
                    cur_min = cur_max = None
            if cur_min is None or cur_max is None:
                cur_min = limit_lo + 0.25 * (limit_hi - limit_lo)
                cur_max = limit_hi
        cur_min = max(limit_lo, min(cur_min, limit_hi))
        cur_max = max(limit_lo, min(cur_max, limit_hi))

        container = qt.QWidget()
        vbox = qt.QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        rangeWidget = ctk.ctkRangeWidget()
        rangeWidget.setRange(limit_lo, limit_hi)
        rangeWidget.singleStep = single_step or max((limit_hi - limit_lo) / 1000.0, 1e-6)
        # Set values BEFORE connecting signals so build doesn't fire the preview.
        # setMinimumValue/setMaximumValue are the canonical ctkRangeWidget setters
        # (the Threshold effect drives its own slider the same way).
        rangeWidget.setMinimumValue(cur_min)
        rangeWidget.setMaximumValue(cur_max)
        # A clear ACTION label, never the value noun (choice_label). A per-step
        # override (Step instructions panel) can rename it.
        button = qt.QPushButton(self._workflowPrimaryLabel(state, "Confirm"))
        button.setToolTip("Use this range and continue")
        button.clicked.connect(self._onWorkflowRangeSelected)
        vbox.addWidget(rangeWidget)
        vbox.addWidget(button)
        self._workflowRangeWidget = rangeWidget
        self._workflowRangeContainer = container
        try:
            rangeWidget.minimumValueChanged.connect(self._onWorkflowRangePreview)
            rangeWidget.maximumValueChanged.connect(self._onWorkflowRangePreview)
        except Exception:
            pass
        self._workflowChoiceLayout.addWidget(container, 1)
        container.setVisible(True)
        # Re-assert the handles AFTER the widget is parented and shown. ctkRangeWidget
        # finalizes its spinboxes/slider on first show, and a value written before
        # that can be discarded — which silently loses an inherited default and
        # leaves the tool's own value on screen. Idempotent; the signals are already
        # connected, so the preview follows the corrected values.
        if (abs(float(rangeWidget.minimumValue) - cur_min) > 1e-6
                or abs(float(rangeWidget.maximumValue) - cur_max) > 1e-6):
            rangeWidget.setMinimumValue(cur_min)
            rangeWidget.setMaximumValue(cur_max)
        # Drive the live target to the seeded values so the preview matches at once.
        self._onWorkflowRangePreview()
        # Last line of defence: re-assert once more after the event loop settles.
        # The widget's show/polish and the module's own observers run deferred, and
        # either can rewrite the handles after this function returns — which is
        # indistinguishable, on screen, from the seed never having been applied.
        self._reassertWorkflowRange(rangeWidget, cur_min, cur_max, step_key)
        return True

    def _reassertWorkflowRange(self, rangeWidget, cur_min, cur_max, step_key=""):
        """Re-apply seeded range handles once the Qt event loop has settled."""
        def _apply():
            try:
                if getattr(self, "_workflowRangeWidget", None) is not rangeWidget:
                    return  # a newer step/render owns the panel now
                drifted = (abs(float(rangeWidget.minimumValue) - cur_min) > 1e-6
                           or abs(float(rangeWidget.maximumValue) - cur_max) > 1e-6)
                if drifted:
                    rangeWidget.setMinimumValue(cur_min)
                    rangeWidget.setMaximumValue(cur_max)
                    logger.debug(
                        "Range handles for %s drifted after show; re-asserted to [%s, %s]",
                        step_key, cur_min, cur_max,
                    )
            except Exception:
                logger.debug("Deferred range re-assert failed", exc_info=True)
        try:
            qt.QTimer.singleShot(0, _apply)
        except Exception:
            logger.debug("Could not schedule deferred range re-assert", exc_info=True)

    def _onWorkflowRangePreview(self, _value=None):
        """Show a live threshold mask as the user drags the range slider. The
        Segment Editor Threshold effect's own preview is unusable here (it crashes
        every timer tick when the module isn't entered), so this DEACTIVATES the
        effect and thresholds the source volume straight into the target segment
        (debounced). Visual only; the committed value is sent by the Set button.
        Silent no-op outside a Segment Editor session (runs in the agent process)."""
        state = getattr(self, "_currentWorkflowUiState", None) or {}
        if state.get("replay_previewing"):
            return
        panel = getattr(self, "_workflowRangeWidget", None)
        if panel is None:
            return
        try:
            v_min, v_max = float(panel.minimumValue), float(panel.maximumValue)
        except Exception:
            return
        # Prefer the NATIVE Segment Editor Threshold preview — a GPU, per-visible-
        # slice pipeline that is as fast as the module's own bar. Its ONLY crash
        # (GetCustomSegmentRendererTag arg2) is a NULL selected segment, so bind a
        # valid target segment + source + slice background first. Driving the effect
        # parameters then updates the preview instantly (no CPU whole-volume pass).
        if self._ensureThresholdEffectReady():
            eff = self._activeSegmentEditorEffect()
            if eff is not None:
                try:
                    eff.setParameter("MinimumThreshold", v_min)
                    eff.setParameter("MaximumThreshold", v_max)
                    return
                except Exception:
                    pass
        # Fallback (effect can't be made ready): a throttled direct labelmap preview.
        try:
            editor = slicer.modules.segmenteditor.widgetRepresentation().self().editor
            if editor.activeEffect() is not None:
                editor.setActiveEffectByName("")
        except Exception:
            pass
        self._pendingPreviewRange = (v_min, v_max)
        timer = getattr(self, "_workflowRangePreviewTimer", None)
        if timer is None:
            timer = qt.QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(self._onLivePreviewTick)
            self._workflowRangePreviewTimer = timer
        if not timer.isActive():
            self._applyLivePreviewThreshold()
            timer.start(60)

    def _ensureThresholdEffectReady(self):
        """Bind the Segment Editor Threshold effect so its NATIVE preview renders
        from the agent module: shared editor + session segmentation + source volume
        + a VALID selected segment (a null id is the effect's only preview-crash
        cause) + the source volume in the slice background + the segment visible.
        Returns True only when it is safe + ready to drive the native preview."""
        try:
            editor = slicer.modules.segmenteditor.widgetRepresentation().self().editor
            editor.setMRMLScene(slicer.mrmlScene)
            en = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentEditorNode")
            if en is None:
                en = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
            editor.setMRMLSegmentEditorNode(en)
            seg = self._sessionSegmentationNode()
            if seg is None:
                return False
            editor.setSegmentationNode(seg)
            vol = self._activeSourceVolume()
            if vol is None or vol.GetImageData() is None:
                return False
            editor.setSourceVolumeNode(vol)
            g = seg.GetSegmentation()
            sid = en.GetSelectedSegmentID()
            if not sid or g.GetSegment(sid) is None:
                sid = seg.GetAttribute("SlicerAIAgent.SegmentEditorTargetSegmentID")
                if not sid or g.GetSegment(sid) is None:
                    sid = g.GetNthSegmentID(0) if g.GetNumberOfSegments() else ""
            if not sid:
                return False  # no segment -> native preview would crash
            en.SetSelectedSegmentID(sid)
            try:
                editor.setCurrentSegmentID(sid)
            except Exception:
                pass
            disp = slicer.vtkMRMLSegmentationDisplayNode.SafeDownCast(seg.GetDisplayNode())
            if disp is not None:
                disp.SetVisibility(True)
                disp.SetSegmentVisibility(sid, True)
            try:
                slicer.util.setSliceViewerLayers(background=vol)
            except Exception:
                pass
            editor.setActiveEffectByName("Threshold")
            return editor.activeEffect() is not None
        except Exception:
            return False

    def _onLivePreviewTick(self):
        """Throttle tick: if the slider moved during the rate-limit window, apply the
        latest range and keep the throttle running until it settles (trailing edge)."""
        if getattr(self, "_pendingPreviewRange", None) != getattr(self, "_lastPreviewRange", None):
            self._applyLivePreviewThreshold()
            try:
                self._workflowRangePreviewTimer.start(60)
            except Exception:
                pass

    def _applyLivePreviewThreshold(self):
        """FAST live threshold preview. Threshold the source volume between the
        slider's [min, max] into a REUSED labelmap volume shown as the slice label
        layer, via ``updateVolumeFromArray`` (a deep-copy memcpy). This replaces the
        earlier per-tick ``updateSegmentBinaryLabelmapFromArray`` — a full segment
        import that re-contoured the whole segmentation every tick and made dragging
        lag. The chosen value is written into the ACTUAL segment ONCE, on the Set
        button (_onWorkflowRangeSelected -> _commitThresholdToSegment)."""
        rng = getattr(self, "_pendingPreviewRange", None)
        if not rng:
            return
        v_min, v_max = rng
        self._lastPreviewRange = rng  # throttle bookkeeping (see _onLivePreviewTick)
        try:
            import numpy as np
            # The effect's own preview crashes without the module entered — keep it off.
            vol = None
            try:
                editor = slicer.modules.segmenteditor.widgetRepresentation().self().editor
                if editor.activeEffect() is not None:
                    editor.setActiveEffectByName("")
                vol = editor.sourceVolumeNode()
            except Exception:
                vol = None
            if vol is None or vol.GetImageData() is None:
                vol = self._activeSourceVolume()
            # Only preview inside a Segment Editor threshold context.
            if vol is None or vol.GetImageData() is None or self._sessionSegmentationNode() is None:
                return
            arr = slicer.util.arrayFromVolume(vol)
            mask = ((arr >= v_min) & (arr <= v_max)).astype("uint8")
            lm = self._ensureThresholdPreviewLabelmap(vol)
            if lm is None:
                return
            slicer.util.updateVolumeFromArray(lm, mask)  # fast memcpy; auto-refreshes the label layer
            if not getattr(self, "_thresholdPreviewShown", False):
                try:
                    slicer.util.setSliceViewerLayers(label=lm, labelOpacity=0.5)
                except Exception:
                    pass
                self._thresholdPreviewShown = True
        except Exception:
            logger.debug("Live threshold preview failed", exc_info=True)

    def _ensureThresholdPreviewLabelmap(self, vol):
        """Reuse (create once) a temporary labelmap volume matching ``vol``'s
        geometry for the fast threshold preview. None on failure."""
        lm = getattr(self, "_thresholdPreviewLabelmap", None)
        try:
            if lm is not None and slicer.mrmlScene.IsNodePresent(lm):
                return lm
        except Exception:
            pass
        try:
            lm = slicer.modules.volumes.logic().CreateAndAddLabelVolume(vol, "AIAgentThresholdPreview")
        except Exception:
            lm = None
        self._thresholdPreviewLabelmap = lm
        self._thresholdPreviewShown = False
        return lm

    def _clearThresholdPreview(self):
        """Drop the fast-preview label layer + its temporary labelmap volume."""
        try:
            slicer.util.setSliceViewerLayers(label=None)
        except Exception:
            pass
        self._thresholdPreviewShown = False
        lm = getattr(self, "_thresholdPreviewLabelmap", None)
        if lm is not None:
            try:
                slicer.mrmlScene.RemoveNode(lm)
            except Exception:
                pass
        self._thresholdPreviewLabelmap = None

    def _commitThresholdToSegment(self, rng):
        """On Set: write the chosen threshold ONCE into the tracked target segment,
        so the mask is really in the segment for the Islands step (robust to a flaky
        effect onApply). One write — not per drag tick, so cost is irrelevant here."""
        if not rng:
            return
        v_min, v_max = rng
        try:
            import numpy as np
            seg = sid = vol = None
            try:
                editor = slicer.modules.segmenteditor.widgetRepresentation().self().editor
                if editor.activeEffect() is not None:
                    editor.setActiveEffectByName("")
                en = editor.mrmlSegmentEditorNode()
                seg = en.GetSegmentationNode() if en else None
                sid = en.GetSelectedSegmentID() if en else None
                vol = en.GetSourceVolumeNode() if en else None
            except Exception:
                pass
            if seg is None:
                seg = self._sessionSegmentationNode()
            if seg is not None:
                g = seg.GetSegmentation()
                if not sid or g.GetSegment(sid) is None:
                    sid = seg.GetAttribute("SlicerAIAgent.SegmentEditorTargetSegmentID")
                    if not sid or g.GetSegment(sid) is None:
                        sid = g.GetNthSegmentID(0) if g.GetNumberOfSegments() else ""
            if vol is None or vol.GetImageData() is None:
                vol = self._activeSourceVolume()
            if seg is None or not sid or vol is None or vol.GetImageData() is None:
                return
            arr = slicer.util.arrayFromVolume(vol)
            mask = ((arr >= v_min) & (arr <= v_max)).astype("uint8")
            slicer.util.updateSegmentBinaryLabelmapFromArray(mask, seg, sid, vol)
            disp = slicer.vtkMRMLSegmentationDisplayNode.SafeDownCast(seg.GetDisplayNode())
            if disp is None:
                seg.CreateDefaultDisplayNodes()
                disp = slicer.vtkMRMLSegmentationDisplayNode.SafeDownCast(seg.GetDisplayNode())
            if disp is not None:
                disp.SetVisibility(True)
                disp.SetVisibility2DFill(True)
                disp.SetVisibility2DOutline(True)
                disp.SetSegmentVisibility(sid, True)
        except Exception:
            logger.debug("Commit threshold to segment failed", exc_info=True)

    def _sessionSegmentationNode(self):
        """The Segment Editor session's segmentation: the one marked by the session
        driver (``SlicerAIAgent.SegmentEditorSession == '1'``), else the
        most-recently-added segmentation. None if the scene has none."""
        marked = None
        last = None
        try:
            for seg in slicer.util.getNodesByClass("vtkMRMLSegmentationNode"):
                if seg is None:
                    continue
                last = seg
                if seg.GetAttribute("SlicerAIAgent.SegmentEditorSession") == "1":
                    marked = seg
        except Exception:
            return None
        return marked or last

    def _onWorkflowRangeSelected(self):
        panel = getattr(self, "_workflowRangeWidget", None)
        if panel is None:
            return
        try:
            value = [float(panel.minimumValue), float(panel.maximumValue)]
        except Exception:
            return
        if self._currentWorkflowUiState.get("replay_previewing"):
            index = self._currentWorkflowUiState.get("preview_index")
            if index is not None:
                self._rerunFromCheckpoint(index, {"choice_value": value})
            return
        # Commit the chosen threshold into the real segment ONCE, then drop the fast
        # label-layer preview so only the segment mask remains.
        self._commitThresholdToSegment(value)
        self._clearThresholdPreview()
        step_id = self._currentWorkflowUiState.get("current_step")
        if step_id:
            self.sendButton.setEnabled(False)
            self._runWorkflowStepDirect(step_id, "choice_made", args={"choice_value": value})

    # ---- Single-value slider (e.g. an extension's "Crop radius (mm)") ---------
    def _liveExtensionSliderWidget(self, widget_name):
        """The extension's own live single-value slider widget (by its ``.ui``
        object name) on the running module widget, or None. Generic: the same
        getModuleWidget + ``ui.<name>`` lookup the segment-name picker uses to
        drive the source combobox."""
        widget_name = str(widget_name or "").strip()
        if not widget_name:
            return None
        module_name = self._workflowModuleName()
        if not module_name:
            return None
        try:
            widget = slicer.util.getModuleWidget(module_name)
        except Exception:
            widget = None
        if widget is None:
            return None
        return getattr(getattr(widget, "ui", None), widget_name, None)

    def _renderWorkflowScalarSlider(self, state):
        """Render a single-handle numeric slider for a scalar-value step (like an
        extension's "Crop radius (mm)" ctkSliderWidget), instead of a min/max
        range bar or free-text box. Limits + current value are seeded, in order,
        from: the extension's own live slider widget; the captured ``.ui``
        minimum/maximum/singleStep/value. Dragging live-drives the extension's own
        widget (its connected handler previews, and the parameter node updates via
        the widget's SlicerParameterName binding); the Set button commits the
        single value via choice_made.

        Returns True if it rendered, or False so the caller falls back to the
        free-text box (never a node tree). Generic: no extension/step-specific
        strings.
        """
        limit_lo = limit_hi = cur = single_step = None
        source_widget = str(state.get("scalar_source_widget") or "").strip()

        # 1. Mirror the extension's own live slider widget exactly.
        live = self._liveExtensionSliderWidget(source_widget)
        if live is not None:
            try:
                limit_lo, limit_hi = float(live.minimum), float(live.maximum)
                cur = float(live.value)
                single_step = float(live.singleStep)
            except Exception:
                limit_lo = limit_hi = cur = None

        # 2. Extension's captured .ui limits (authoritative fallback).
        if limit_lo is None:
            smin, smax = state.get("scalar_min"), state.get("scalar_max")
            if smin is not None and smax is not None:
                try:
                    limit_lo, limit_hi = float(smin), float(smax)
                    single_step = float(state.get("scalar_step")) if state.get("scalar_step") else None
                except Exception:
                    limit_lo = limit_hi = None

        if limit_lo is None or limit_hi is None or limit_hi <= limit_lo:
            return False  # no sensible limits -> free-text fallback

        # A default inherited from an earlier step outranks the live widget, for
        # the same reason as the range slider: this pass has re-initialized the
        # source widget, so its current value is the factory default, not the one
        # the cookbook points at.
        inherited = state.get("inherited_default")
        if isinstance(inherited, (list, tuple)) and len(inherited) == 1:
            inherited = inherited[0]
        if isinstance(inherited, (int, float, str)) and not isinstance(inherited, bool):
            try:
                cur = float(inherited)
            except (TypeError, ValueError):
                pass

        # Seed the handle: live value, else a declared .ui default, else midpoint.
        if cur is None:
            default = state.get("scalar_default")
            try:
                cur = float(default) if default is not None else None
            except Exception:
                cur = None
            if cur is None:
                cur = limit_lo + 0.5 * (limit_hi - limit_lo)
        cur = max(limit_lo, min(cur, limit_hi))

        container = qt.QWidget()
        vbox = qt.QVBoxLayout(container)
        vbox.setContentsMargins(0, 0, 0, 0)
        sliderWidget = ctk.ctkSliderWidget()
        sliderWidget.minimum = limit_lo
        sliderWidget.maximum = limit_hi
        sliderWidget.singleStep = single_step or max((limit_hi - limit_lo) / 1000.0, 1e-6)
        # Set the value BEFORE connecting the signal so build doesn't fire preview.
        sliderWidget.value = cur
        # A clear ACTION label ("Confirm"), never the value noun (choice_label is
        # e.g. "Radius", which reads as a mislabelled button); the number itself is
        # shown in the slider's spinbox. A per-step override can rename it.
        button = qt.QPushButton(self._workflowPrimaryLabel(state, "Confirm"))
        button.setToolTip("Use this value and continue")
        button.clicked.connect(self._onWorkflowScalarSelected)
        vbox.addWidget(sliderWidget)
        vbox.addWidget(button)
        self._workflowScalarWidget = sliderWidget
        self._workflowScalarContainer = container
        try:
            sliderWidget.valueChanged.connect(self._onWorkflowScalarPreview)
        except Exception:
            pass
        self._workflowChoiceLayout.addWidget(container, 1)
        container.setVisible(True)
        # Drive the live widget to the seeded value so the preview matches at once.
        self._onWorkflowScalarPreview()
        return True

    def _onWorkflowScalarPreview(self, _value=None):
        """Drive the extension's own live slider so its connected handler previews
        (e.g. cropRadiusSliderWidget -> _onCropRadiusChanged -> previewCutCylinder)
        and the parameter node updates via the widget's SlicerParameterName
        binding, as the user drags. Visual only; the committed value is sent by
        the Set button. Silent no-op if no live widget (runs in the agent
        process, not the sandbox)."""
        state = getattr(self, "_currentWorkflowUiState", None) or {}
        if state.get("replay_previewing"):
            return
        panel = getattr(self, "_workflowScalarWidget", None)
        if panel is None:
            return
        try:
            v = float(panel.value)
        except Exception:
            return
        live = self._liveExtensionSliderWidget(str(state.get("scalar_source_widget") or "").strip())
        if live is not None and live is not panel:
            try:
                live.value = v
            except Exception:
                pass

    def _onWorkflowScalarSelected(self):
        panel = getattr(self, "_workflowScalarWidget", None)
        if panel is None:
            return
        try:
            value = float(panel.value)
        except Exception:
            return
        if self._currentWorkflowUiState.get("replay_previewing"):
            index = self._currentWorkflowUiState.get("preview_index")
            if index is not None:
                self._rerunFromCheckpoint(index, {"choice_value": value})
            return
        step_id = self._currentWorkflowUiState.get("current_step")
        if step_id:
            self.sendButton.setEnabled(False)
            self._runWorkflowStepDirect(step_id, "choice_made", args={"choice_value": value})

    def _bindSegmentsTable(self, seg_node):
        """Bind the segments table to ``seg_node``, ensuring a display node exists
        so the eye column can write per-segment visibility."""
        table = getattr(self, "_workflowSegmentsTable", None)
        if table is None or seg_node is None:
            return
        try:
            seg_node.CreateDefaultDisplayNodes()
        except Exception:
            logger.debug("CreateDefaultDisplayNodes failed", exc_info=True)
        try:
            table.setSegmentationNode(seg_node)
        except Exception:
            logger.debug("setSegmentationNode failed", exc_info=True)

    def _onWorkflowSegmentsComboChanged(self, *args):
        # Read the node from the combo (currentNodeChanged has overloaded
        # signatures; the positional arg may be a bool).
        combo = getattr(self, "_workflowSegmentsCombo", None)
        if combo is not None:
            try:
                self._bindSegmentsTable(combo.currentNode())
            except Exception:
                logger.debug("Segments combo change rebind failed", exc_info=True)

    def _onWorkflowSegmentsDone(self):
        # The user edited per-segment visibility directly on the scene; advance the
        # step with no fabricated choice value (downstream code reads visibility).
        if self._currentWorkflowUiState.get("replay_previewing"):
            index = self._currentWorkflowUiState.get("preview_index")
            if index is not None:
                self._rerunFromCheckpoint(index, {})
            return
        step_id = self._currentWorkflowUiState.get("current_step")
        if step_id:
            self.sendButton.setEnabled(False)
            self._runWorkflowStepDirect(step_id, "proceed")

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

        # Filter benign, high-frequency VTK render-loop warnings (interaction
        # handle index vs control-point count) for the lifetime of this
        # interactive wait — interaction handles are active during "adjust"
        # steps and Slicer emits these harmless messages on every render. Real
        # errors still reach the console. General across extensions; removed in
        # _exitWorkflowWait.
        try:
            from SlicerAIAgentLib.WorkflowRuntime import install_filtered_vtk_output
            self._vtkOutputRestore = install_filtered_vtk_output()
        except Exception:
            self._vtkOutputRestore = None

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
            ) not in ("plane", "curve", "line", "fiducial", "angle", "roi"):
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
            _session = getattr(getattr(self, "_workflowRuntime", None), "session", None)
            node = latest_interaction_node_for_step(
                step_info.get("step_id", ""),
                getattr(_session, "extension_name", ""),
                getattr(_session, "workflow_id", ""),
                node_class,
            )
            if node is None:
                logger.info(
                    "[Workflow] Placement not armed for step %s and no remembered "
                    "node to re-arm with", step_info.get("step_id", "?"),
                )
                return
            # Placement already produced at least one control point and place
            # mode is no longer active: the interaction has completed (e.g.
            # single place mode auto-exited after the expected point). Re-arming
            # would let the user add unintended extra points, so leave it done.
            try:
                if not in_place_mode and node.GetNumberOfControlPoints() > 0:
                    return
            except Exception:
                pass
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

        # Restore the original VTK output window installed on wait entry, so the
        # benign-message filter is active only during the interactive wait.
        _restore = getattr(self, "_vtkOutputRestore", None)
        self._vtkOutputRestore = None
        if _restore is not None:
            try:
                _restore()
            except Exception:
                pass

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
            })
            self._setSendEnabled(True)
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

    def _handleCliProgress(self, stage_num, stage_name, detail, extension=""):
        """Handle CLI generator progress updates on the main thread.

        Routed to the extension's OWN tab: parallel runs emit interleaved
        phases, and a shared pane would leave none of them readable.
        """
        self._cliLog(extension, f"  Phase {stage_num}: {stage_name} — {detail}")

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
        extension = (result or {}).get("extension_name", "")
        if extension and extension in (getattr(self, "_cliBatch", None) or {}):
            self._cliBatchFinish(extension, bool((result or {}).get("success")),
                                 str((result or {}).get("error", ""))[:200])
        else:
            self._cliGeneratorRunning = False
            self._analyzeGenerateButton.setEnabled(True)

        if result.get("success"):
            # Generation is pure background analysis — it must NOT touch the live
            # MRML scene/viewport, so nothing here executes a generated template.
            # A step that validates statically and only misbehaves at USE time is
            # fixed by the ✍ Revise button during the guided run, against the
            # scene it actually misbehaved in (see app/widget_revise.py).
            self._finalizeCliValidation(result)

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

    def _finalizeCliValidation(self, result):
        """Finalize the CLI generation UI after the analyzer's static validation.

        Static only, by construction: generation runs on background threads (up
        to CLI_MAX_PARALLEL at once) and must never touch the MRML scene, so no
        generated template is executed here. What a template does when it runs is
        answered where it runs -- by the runtime's own self-correction, and by
        the ✍ Revise button on the step in front of the user.
        """
        self._cliStatusLabel.setText("Validated")
        self._cliStatusLabel.setStyleSheet("font-weight: bold; color: green;")
        self._cliResultGroup.setVisible(True)
        self._cliGeneratorRunning = False
        self._analyzeGenerateButton.setEnabled(True)

        manifest = result.get("manifest", {})
        stages = manifest.get("stages", [])
        self._cliResultSummary.setText(
            f"Generated CLI for {manifest.get('extension_name', '?')} "
            f"(workflow steps: {', '.join(stages)}). "
            f"Saved to: {result.get('cli_dir', '?')}"
        )
        self._cliProgressDisplay.append("CLI generation complete: Validated!")

        # Refresh the extension selector to show updated status, preserving selection
        ext_name = manifest.get("extension_name", "")
        self._onRefreshExtensionsClicked()
        if ext_name:
            for i in range(self._extensionItemCount()):
                if ext_name in self._extensionItemText(i):
                    self._setCurrentExtensionIndex(i)
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

    def _handleCliError(self, payload):
        """Handle CLI generator error on the main thread.

        Accepts the old bare string as well as the routed dict, because the
        auto-revision path still emits the former.
        """
        if isinstance(payload, dict):
            extension = payload.get("extension", "")
            error_msg = payload.get("error", "")
        else:
            extension, error_msg = "", payload
        self._cliLog(extension, f"ERROR: {error_msg}")
        if extension and extension in (getattr(self, "_cliBatch", None) or {}):
            # One extension failing must not end the others: only its own slot
            # is closed, and the batch wraps up when the last one lands.
            self._cliBatchFinish(extension, False, str(error_msg)[:200])
            return
        self._cliGeneratorRunning = False
        self._analyzeGenerateButton.setEnabled(True)
        self._cliStatusLabel.setText("Error")
        self._cliStatusLabel.setStyleSheet("font-weight: bold; color: red;")

    def enter(self):
        if (hasattr(self, 'chatHistory') and self.chatHistory is not None and
            self.logic and not self.logic.hasApiKey()):
            self.appendToChat("System", "Please configure your API key in Settings before using the agent.")

    def exit(self):
        pass
