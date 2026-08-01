"""Replay stepper for guided generated-CLI workflows.

A minimal three-button control wrapped around the workflow progress bar:

    [ Back ]  [====== progress ======]  [ Forward ]  [ Run from here ]

Back/Forward are non-destructive navigation through the per-step checkpoints
recorded by WorkflowRuntime: each restores that step's scene (a hidden
vtkMRMLSceneViewNode) and updates the guidance text, nothing is discarded.
"Run from here" (Action) commits: it truncates to the previewed step and
re-executes the workflow forward from there via the normal dispatch loop.
"""

from .common import *


class WidgetReplayMixin:
    # ------------------------------------------------------------------ setup
    def _setupReplayControls(self):
        """Wrap the workflow progress bar with Back / Forward / Run-from-here.

        Called unconditionally from _setupWorkflowUserPanel: the workflow frame
        may be built programmatically or loaded from the .ui file, so this finds
        the progress bar in whichever frame exists and wraps it in place.
        Idempotent.
        """
        if getattr(self, "_replayControlsRow", None) is not None:
            return
        frame = getattr(self, "_workflowUserFrame", None)
        if frame is None:
            return
        frame_layout = frame.layout()
        if frame_layout is None:
            return
        progress_bar = getattr(self, "_workflowProgressBar", None)
        if progress_bar is None:
            return
        bar_index = frame_layout.indexOf(progress_bar)
        if bar_index < 0:
            return

        self._replayBackButton = self._makeReplayButton(
            ":/Icons/pqVcrBack24.png", "◀",
            "Go back one step (restores the 3D scene and guidance)",
            self._onReplayBack,
        )
        self._replayForwardButton = self._makeReplayButton(
            ":/Icons/pqVcrForward24.png", "▶",
            "Go forward one step",
            self._onReplayForward,
        )
        self._replayActionButton = self._makeReplayButton(
            ":/Icons/pqVcrPlay24.png", "▷",
            "Re-run the workflow from this step",
            self._onReplayAction,
        )
        # Baseline comparison: re-run THIS step with an alternative code
        # producer instead of the generated CLI template. Text-only so it reads
        # as a different kind of action from the three transport controls.
        self._baselineToggleButton = self._makeReplayButton(
            None, "⚖",
            "Run this step with a comparison baseline "
            "(pure LLM / online only / Claude Code + Slicer skill)",
            self._onBaselineToggleClicked,
        )
        # Checkable so the armed state stays legible even where the selector row
        # is hidden — which it is on any step the pipeline does not answer with
        # generated code (user_choice / user_interaction / branch_op / review_op).
        try:
            self._baselineToggleButton.setCheckable(True)
        except Exception:
            logger.debug("Baseline toggle checkable failed", exc_info=True)

        # Move the progress bar out of the vertical layout and into a row that
        # also holds the three buttons; insert the row where the bar used to be.
        frame_layout.removeWidget(progress_bar)
        row = qt.QWidget()
        row_layout = qt.QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(3)
        row_layout.addWidget(self._replayBackButton)
        row_layout.addWidget(progress_bar, 1)
        row_layout.addWidget(self._replayForwardButton)
        row_layout.addWidget(self._replayActionButton)
        row_layout.addWidget(self._baselineToggleButton)
        frame_layout.insertWidget(bar_index, row)
        self._replayControlsRow = row

        for button in (self._replayBackButton, self._replayForwardButton,
                       self._replayActionButton, self._baselineToggleButton):
            button.setVisible(False)

    def _makeReplayButton(self, icon_resource, fallback_text, tooltip, handler):
        button = qt.QToolButton()
        icon = self._nativeIcon(icon_resource) if icon_resource else None
        if icon is not None:
            button.setIcon(icon)
        else:
            button.setText(fallback_text)
        button.setToolTip(tooltip)
        button.setAutoRaise(True)
        button.clicked.connect(handler)
        return button

    def _nativeIcon(self, resource):
        """Return a native Slicer Qt-resource QIcon, or None if not registered."""
        try:
            icon = qt.QIcon(resource)
            return None if icon.isNull() else icon
        except Exception:
            return None

    # ----------------------------------------------------------------- render
    def _updateReplayControls(self, state):
        """Show/enable the stepper buttons from a UI-state dict.

        Also drives the baseline toggle, so every caller of this method
        (_updateWorkflowPanel, _clearWorkflowPanel, _clearCompletedWorkflowState)
        keeps the two rows consistent without having to know about both.
        """
        if getattr(self, "_replayControlsRow", None) is None:
            return
        state = state or {}
        has_replay = bool(state.get("can_replay") or state.get("replay_previewing"))
        for button in (self._replayBackButton, self._replayForwardButton,
                       self._replayActionButton):
            if button is not None:
                button.setVisible(has_replay)
        if has_replay:
            self._replayBackButton.setEnabled(bool(state.get("replay_can_back")))
            self._replayForwardButton.setEnabled(bool(state.get("replay_can_forward")))
            self._replayActionButton.setEnabled(bool(state.get("replay_can_action")))
        try:
            self._updateBaselineControls(state)
        except Exception:
            logger.debug("Baseline control refresh failed", exc_info=True)

    # --------------------------------------------------------------- handlers
    def _onReplayBack(self):
        runtime = getattr(self, "_workflowRuntime", None)
        if runtime is None or runtime.session is None:
            return
        # Every step is judged on its own: leave baseline mode and empty the
        # prompt box BEFORE moving, so the panel re-renders for the step we land
        # on rather than carrying the previous step's mode and text along.
        if not self._resetBaselineForNavigation():
            return
        # _updateWorkflowPanel renders the returned state verbatim (no
        # type/step_id/tool/next_step keys) and refreshes the controls.
        self._updateWorkflowPanel(runtime.navigate_back())

    def _onReplayForward(self):
        runtime = getattr(self, "_workflowRuntime", None)
        if runtime is None or runtime.session is None:
            return
        if not self._resetBaselineForNavigation():
            return
        self._updateWorkflowPanel(runtime.navigate_forward())

    def _onReplayAction(self):
        """Re-run the workflow from the previewed step with its recorded choice."""
        runtime = getattr(self, "_workflowRuntime", None)
        if runtime is None or runtime.session is None:
            return
        # Same rule as Back/Forward: this hands the step back to the pipeline,
        # so the comparison arm is disengaged first — Send must not stay amber
        # and baseline-routed while the pipeline is driving.
        if not self._resetBaselineForNavigation():
            return
        self._rerunFromCheckpoint(runtime.session.preview_index)

    def _prepareReplayRewind(self, index, modified_args=None):
        """Confirm, restore the scene to BEFORE checkpoint ``index``, truncate state.

        Shared by "Run from here" and the baseline harness: both need the scene
        and the workflow state put back exactly as they were before that step
        ran, they only differ in what produces the step's code afterwards.
        Returns the {step_id, action, args} descriptor, or None when the user
        declined or the rewind failed (the caller has already been told).
        """
        runtime = getattr(self, "_workflowRuntime", None)
        if runtime is None or runtime.session is None or index is None:
            return None
        if not self._confirmReplayRewind(index):
            return None
        try:
            self._interactionManager.cleanup()
        except Exception:
            logger.debug("Interaction cleanup before rewind failed", exc_info=True)

        self.sendButton.setEnabled(False)
        self._recordRoleEvent("Workflow", "replay_action", {
            "index": index, "modified": modified_args is not None,
        })
        descriptor = runtime.rewind_to_checkpoint(index, modified_args)
        if not isinstance(descriptor, dict) or descriptor.get("error"):
            self.appendToChat("Error", (descriptor or {}).get("error", "Replay failed."))
            self._setReadyStatus()
            self._setSendEnabled(True)
            return None

        # The sole-candidate auto-select memo is keyed on
        # len(completed_instances), which the rewind has just truncated. Drop the
        # keys at or beyond the new length so a step re-run from here can
        # auto-select again -- otherwise re-running a rewound node pick would sit
        # on its one-item picker forever.
        seen = getattr(self, "_autoSelectedNodeSteps", None)
        if seen:
            reached = len(runtime.session.completed_instances)
            self._autoSelectedNodeSteps = {k for k in seen if k[2] < reached}

        self._updateWorkflowPanel(runtime.state_for_ui())
        try:
            self._applyChosenVolumeBackground()
        except Exception:
            logger.debug("Re-asserting slice background after rewind failed", exc_info=True)
        return descriptor

    def _rerunFromCheckpoint(self, index, modified_args=None):
        """Rewind to checkpoint ``index`` and re-execute the workflow from there.

        ``modified_args`` overrides the recorded args (e.g. a different choice
        the user clicked while scrubbing). The checkpoint's own action drives
        the re-dispatch: "choice_made" for choice/loop steps (so the value is
        applied), "start" for interactive/automated steps (re-present/re-run).
        """
        descriptor = self._prepareReplayRewind(index, modified_args)
        if descriptor is None:
            return
        self.appendToChat(
            "System",
            f"Re-running workflow from step '{descriptor.get('step_id')}'.",
        )
        self._runWorkflowStepDirect(
            descriptor.get("step_id"),
            descriptor.get("action", "start"),
            args=descriptor.get("args") or {},
        )

    def _confirmReplayRewind(self, index):
        """Confirm when re-running would delete scene nodes added outside the workflow."""
        try:
            import slicer
        except Exception:
            return True
        runtime = getattr(self, "_workflowRuntime", None)
        session = getattr(runtime, "session", None) if runtime else None
        if session is None:
            return True
        known = set(getattr(session, "baseline_node_ids", []) or [])
        for cp in session.checkpoints:
            known.update(cp.created_node_ids or [])
        manual = []
        try:
            for i in range(slicer.mrmlScene.GetNumberOfNodes()):
                node = slicer.mrmlScene.GetNthNode(i)
                if node is None or not node.GetID():
                    continue
                if node.IsA("vtkMRMLSceneViewNode"):
                    continue
                if not node.GetSaveWithScene() or node.GetHideFromEditors():
                    continue
                if node.GetID() not in known:
                    manual.append(node.GetName() or node.GetID())
        except Exception:
            return True
        if not manual:
            return True
        preview = ", ".join(manual[:5]) + (" …" if len(manual) > 5 else "")
        message = (
            "Re-running from this step restores an earlier scene state and will "
            f"remove {len(manual)} node(s) not produced by the workflow:\n\n{preview}\n\n"
            "Continue?"
        )
        try:
            return slicer.util.confirmYesNoDisplay(message)
        except Exception:
            return True
