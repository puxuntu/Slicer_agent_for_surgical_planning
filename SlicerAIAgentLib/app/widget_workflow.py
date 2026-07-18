from .common import *


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
        self._workflowCancelButton.setVisible(bool(self._currentWorkflowUiState.get("can_cancel")))
        self._workflowDoneButton.setEnabled(bool(self._currentWorkflowUiState.get("can_done")))
        self._workflowSkipButton.setEnabled(bool(self._currentWorkflowUiState.get("can_skip")))
        self._workflowCancelButton.setEnabled(bool(self._currentWorkflowUiState.get("can_cancel")))
        done_label = self._currentWorkflowUiState.get("done_label") or "Done"
        if self._currentWorkflowUiState.get("review_selection") and done_label == "Done":
            # A review checkpoint's action is confirmation, not task completion.
            done_label = "Confirm"
        self._workflowDoneButton.setText(str(done_label) if self._currentWorkflowUiState.get("can_done") else "Done")
        self._updateInteractionCountGate()

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
            "can_cancel": not result.get("workflow_completed"),
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
        self._renderWorkflowDetails("")
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
        self._clearThresholdPreview()
        current_step = self._currentWorkflowUiState.get("current_step")
        self.sendButton.setEnabled(False)
        self._runWorkflowStepDirect(current_step, "cancel")

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
        from SlicerAIAgentLib.WorkflowRuntime import WorkflowRuntime as _WFRT
        _replay_attr = _WFRT.REPLAY_HIDDEN_SH_ATTR
        # Only apply the created-after-this-step exclusion while REVIEWING (replay);
        # in the live/forward flow nothing is tagged, and gating here means a stray
        # lingering tag can never hide a node from the live picker.
        _in_replay = bool(state.get("replay_previewing"))
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
        if not candidates:
            return False

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
            node = latest_interaction_node_for_step(step_id)
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
        """Show a single-pick combobox of the SEGMENT NAMES of a segmentation, so
        the user picks one fragment/segment by name exactly like the extension's
        own content combobox (e.g. the "Fragment" selector), instead of a tree of
        whole scene nodes. The picked name flows through choice_made -> choice_value
        identically to a literal-choice step (and Part 4 mirrors it onto the live
        source combobox so its connected handler fires).

        Returns True if it rendered (a segmentation with >=1 segment resolved), or
        False so the caller falls back to the free-text box (never the node tree).
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
            return False
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
                return False
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
        if not names:
            return False

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
        # Drive the live target to the seeded values so the preview matches at once.
        self._onWorkflowRangePreview()
        return True

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
            node = latest_interaction_node_for_step(step_info.get("step_id", ""))
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

        The off-thread `repair_generated_cli` has rewritten templates from the user's
        function-error descriptions. Now live-execute the rewritten templates to catch
        any API crash (introduced or pre-existing in a precondition-free step) and
        auto-repair it, then finalize.
        """
        result = getattr(self, "_cliRepairResult", None)
        if repair.get("repaired"):
            self._cliProgressDisplay.append(
                f"Repair rewrote {len(repair.get('repaired', []))} template(s) "
                f"({repair.get('function_error_count', 0)} function error(s)). "
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
