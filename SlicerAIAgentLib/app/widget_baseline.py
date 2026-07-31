"""Manual baseline-comparison harness for the guided-workflow runtime.

Once a workflow has been run and the user has stepped Back to a step, the
``Baseline`` button next to "Re-run the workflow from this step" puts the panel
into BASELINE MODE. That does not add a second prompt box: it drives the
agent's EXISTING prompt box and Send button, and only inserts one compact row
above them holding the baseline selector.

    [ Baseline: 1. Pure LLM (no grounding)  v ]  [Copy MCP config]
    [ type the prompt here ...................]  [   Run       ]
                                                 [   Pure LLM  ]

Send's caption follows the selector, so the button always says which producer
it will invoke, and Send routes to that producer instead of a normal agent turn
until baseline mode is switched off again.

The three producers:

    1. Pure LLM     one bare model call: no retrieval, no tools, no CLI
    2. Online only  full retrieval + search-tool loop, generated CLI ablated
    3. Claude Code  code arrives over MCP from an external Claude Code session
                    running the Slicer skill (the prompt box is unused; Send
                    arms/disarms the endpoint instead)

All three share the tail of the real pipeline -- CodeValidator, SafeExecutor,
WorkflowRuntime step completion and auto-advance -- so the only thing that
differs between conditions is where the code came from. They deliberately do
NOT get the pipeline's plan validation, live API sanity check or self-correction
loop: those are properties of the system under test, not of the baselines, and
handing them to a baseline would flatter it.

Each run writes a JSON record next to the turn's other artifacts and appends one
line to ``logs/baseline_runs.jsonl`` so a whole evaluation session can be
collected from a single file. The generated code goes to the usual Debug >
Generated Code view.
"""

from .common import *

from SlicerAIAgentLib import BaselineRunner, RunLog
from SlicerAIAgentLib.BaselineRunner import (
    MODE_CLAUDE_CODE,
    MODE_ONLINE_ONLY,
    MODE_PURE_LLM,
)


class WidgetBaselineMixin:
    # ------------------------------------------------------------------ setup
    def _setupBaselinePanel(self):
        """Insert the baseline selector row directly above the prompt/Send row.

        Called unconditionally from ``_setupWorkflowUserPanel``. Idempotent.
        The row is hidden until the user turns baseline mode on.
        """
        if getattr(self, "_baselineRow", None) is not None:
            return
        prompt = getattr(self, "promptInput", None)
        button = getattr(self, "sendButton", None)
        if prompt is None or button is None:
            return

        # Remember what Send normally looks like so exiting restores it exactly.
        try:
            self._baselineSendText = str(button.text)
            self._baselineSendStyle = str(button.styleSheet)
        except Exception:
            self._baselineSendText = "Send"
            self._baselineSendStyle = ""

        row = qt.QWidget()
        row.setObjectName("baselineSelectorRow")
        layout = qt.QVBoxLayout(row)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(2)

        top = qt.QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        caption = qt.QLabel("Baseline:")
        caption.setStyleSheet("font-weight: bold; color: #7a4a00;")
        top.addWidget(caption)

        self._baselineModeCombo = qt.QComboBox()
        for mode in BaselineRunner.BASELINE_MODES:
            self._baselineModeCombo.addItem(mode["label"], mode["id"])
        # Ignored horizontally + stretch 1: never widens the module panel, but
        # still takes the row's slack (see WidgetCoreMixin._relaxContentWidth).
        self._applyBaselineWidthPolicy(self._baselineModeCombo)
        self._baselineModeCombo.currentIndexChanged.connect(self._onBaselineModeChanged)
        top.addWidget(self._baselineModeCombo, 1)

        layout.addLayout(top)

        self._baselineInfoLabel = qt.QLabel("")
        self._baselineInfoLabel.setWordWrap(True)
        self._baselineInfoLabel.setMinimumWidth(0)
        self._baselineInfoLabel.setTextInteractionFlags(qt.Qt.TextSelectableByMouse)
        self._baselineInfoLabel.setStyleSheet("color: #555; font-size: 11px;")
        layout.addWidget(self._baselineInfoLabel)

        self._insertBaselineRowAboveInput(row)
        self._baselineRow = row
        row.setVisible(False)
        self._onBaselineModeChanged()

    @staticmethod
    def _applyBaselineWidthPolicy(widget):
        """Demand no width of the module panel, but still fill the row."""
        try:
            policy = qt.QSizePolicy(qt.QSizePolicy.Ignored, qt.QSizePolicy.Fixed)
            policy.setHorizontalStretch(1)
            widget.setMinimumWidth(0)
            widget.setSizePolicy(policy)
        except Exception:
            logger.debug("Baseline width policy failed", exc_info=True)

    def _insertBaselineRowAboveInput(self, row):
        """Put ``row`` immediately above the prompt/Send row.

        ``inputLayout`` is a nested QHBoxLayout, so it cannot be located by
        ``indexOf`` on the outer layout. Find it structurally instead: the outer
        item whose sub-layout contains ``promptInput``. Falls back to appending
        at the bottom of the outer layout.
        """
        try:
            parent_layout = self.promptInput.parent().layout()
            if parent_layout is None:
                return
            target = -1
            for index in range(parent_layout.count()):
                item = parent_layout.itemAt(index)
                sub = item.layout() if item is not None else None
                if sub is not None and sub.indexOf(self.promptInput) >= 0:
                    target = index
                    break
            if target < 0:
                parent_layout.addWidget(row)
            else:
                parent_layout.insertWidget(target, row)
        except Exception:
            logger.debug("Baseline row insertion failed", exc_info=True)

    # ----------------------------------------------------------------- render
    DEFAULT_TOGGLE_TIP = (
        "Run this step with a comparison baseline "
        "(pure LLM / online only / Claude Code + Slicer skill)"
    )

    def _baselineEngaged(self, state=None):
        """Baseline mode is on AND this step can actually take a baseline.

        ``_baselineActive`` is the user's toggle intent and survives scrubbing;
        *engaged* is that intent resolved against the step now in view. Only two
        operation types are comparable, so stepping onto a user_choice /
        user_interaction / branch_op / review_op step disengages: the selector
        row and its prompt are hidden (there is nothing to run there) and the
        input row goes back to the guided workflow. Stepping back onto a
        comparable step re-engages, with the toggle never having been touched.

        A run in flight is always engaged, so the row cannot vanish underneath
        an executing baseline.
        """
        if not getattr(self, "_baselineActive", False):
            return False
        if self._baselineBusy():
            return True
        runtime = getattr(self, "_workflowRuntime", None)
        if runtime is None or getattr(runtime, "session", None) is None:
            return False
        try:
            ok, _reason = runtime.external_step_eligibility(
                self._baselineTargetStepId(state)
            )
        except Exception:
            logger.debug("Baseline eligibility check failed", exc_info=True)
            return False
        return bool(ok)

    def _updateBaselineControls(self, state):
        """Drive the ⚖ toggle and the selector row from replay + eligibility."""
        state = state or {}
        available = bool(state.get("can_replay") or state.get("replay_previewing"))
        runtime = getattr(self, "_workflowRuntime", None)
        has_session = bool(getattr(runtime, "session", None)) if runtime else False

        # Only extension_op / slicer_op steps are answered by the pipeline with
        # generated code, so only those can be compared against a baseline.
        eligible, reason = True, ""
        if runtime is not None and available:
            eligible, reason = runtime.external_step_eligibility(
                self._baselineTargetStepId(state)
            )

        # The arm cannot outlive the step it was set on. Back/Forward already
        # reset it, but the workflow can also auto-advance onto a step that
        # takes no baseline (after a successful run); disarm there too, so
        # `_baselineActive` is only ever true on a comparable step. That is what
        # makes it safe to HIDE the toggle below rather than merely disable it —
        # a hidden armed toggle would be unreachable.
        if (getattr(self, "_baselineActive", False) and not eligible
                and not self._baselineBusy() and getattr(self, "_baselineRow", None) is not None):
            self._exitBaselineMode()
            self._clearBaselinePrompt()

        button = getattr(self, "_baselineToggleButton", None)
        if button is not None:
            # Hidden outright on a step whose operation type cannot be compared:
            # there is nothing to offer there, so the icon should not be present.
            show = available and (eligible or self._baselineBusy())
            button.setVisible(show)
            button.setEnabled(show and not self._baselineBusy())
            button.setToolTip(self.DEFAULT_TOGGLE_TIP)
            try:
                button.setChecked(bool(getattr(self, "_baselineActive", False)))
            except Exception:
                logger.debug("Baseline toggle check-state failed", exc_info=True)

        if getattr(self, "_baselineRow", None) is None:
            self._refreshInputAvailability()
            return

        # Baseline mode ends only when the workflow itself goes away. It must
        # NOT end merely because `can_replay` dropped: committing a rewind
        # truncates the checkpoint list (to empty when rewinding to step 1),
        # which happens in the middle of starting a baseline run.
        if not has_session and not self._baselineBusy():
            if getattr(self, "_baselineActive", False):
                self._exitBaselineMode()
            else:
                self._refreshInputAvailability()
            return

        engaged = self._baselineEngaged(state)
        self._baselineRow.setVisible(engaged)
        if engaged:
            self._refreshBaselineTarget(state)
        else:
            self._baselineRejection = reason
            self._syncBaselineSendButton()
        self._refreshInputAvailability()

    def _refreshBaselineTarget(self, state=None):
        """Gate ineligible steps and retarget the info line.

        The prompt box is deliberately NOT pre-filled: the prompt is the
        independent variable of the comparison, so it is the user's to write.
        The box is only ever emptied (on Back/Forward), never authored.
        """
        state = state or getattr(self, "_currentWorkflowUiState", {}) or {}
        step_id = self._baselineTargetStepId(state)

        runtime = getattr(self, "_workflowRuntime", None)
        if runtime is None or self._baselineBusy():
            return
        # Gate up front rather than on Send: a value-pick or 3D-interaction step
        # generates no code, so no baseline can stand in for it.
        ok, reason = runtime.external_step_eligibility(step_id)
        self._baselineRejection = "" if ok else reason
        self._syncBaselineSendButton()
        self._updateBaselineInfo()

    def _clearBaselinePrompt(self):
        """Empty the prompt box so each step starts from a blank one."""
        box = getattr(self, "promptInput", None)
        if box is None:
            return
        try:
            box.setPlainText("")
        except Exception:
            logger.debug("Baseline prompt clear failed", exc_info=True)

    def _resetBaselineForNavigation(self):
        """Leave baseline mode and clear the prompt on any Back/Forward step.

        Stepping IS how the user picks which step to compare, so arriving at a
        new one starts from a clean slate: the ⚖ toggle goes back to unclicked
        and the box is emptied, and the user re-arms deliberately if this step
        supports it. Otherwise the previous step's mode and prompt text would
        follow them along the timeline.

        Returns False when a baseline run is in flight, in which case the caller
        must not navigate -- yanking the timeline out from under an executing
        baseline would orphan its checkpoint and its record.
        """
        if self._baselineBusy():
            self._setBaselineStatus(
                "A baseline run is in progress — wait for it to finish (or press "
                "Send to stop waiting for Claude Code) before stepping."
            )
            return False
        if getattr(self, "_baselineActive", False):
            self._exitBaselineMode()
        self._clearBaselinePrompt()
        return True

    def _updateBaselineInfo(self):
        """The single producer of the info line, so the two refresh paths
        (mode change and step change) cannot clobber each other. Never runs
        during a run, so it cannot overwrite live progress text."""
        if not self._baselineEngaged() or self._baselineBusy():
            return
        if getattr(self, "_baselineRejection", ""):
            self._setBaselineStatus(self._baselineRejection)
            return
        mode = self._baselineMode()
        description = BaselineRunner.mode_info(mode).get("description", "")
        step_id = self._baselineTargetStepId()
        if mode == MODE_CLAUDE_CODE:
            # Say plainly that the button is not a prompt-send, since it shares
            # the widget with one: the prompt for THIS condition is typed in
            # Claude Code, and the button only rewinds + attaches. The attach
            # state is reported here on every refresh, which is why there is no
            # "check the server" button — the skill's own script already prints
            # the client config when it is pasted.
            server = getattr(self, "_baselineMcpServer", None)
            if server is not None and server.armed:
                return
            available, url = self._baselineBridgeStatus()
            if not available:
                # Selecting this condition starts the skill's own server, so the
                # user never has to paste it into the Python console.
                available, url = self._autoStartSkillMcpServer()
            if not available:
                self._setBaselineStatus(
                    f"Step {step_id} — could not start the Slicer skill's MCP "
                    f"server automatically. {self._mcpAutoStartError} You can "
                    "still paste slicer-mcp-server.py into Slicer's Python "
                    "console by hand, then press 'Arm this step'."
                )
                return
            self._setBaselineStatus(
                f"Step {step_id} — MCP server detected at {url}. Press 'Arm this "
                "step' to rewind the scene and attach. Nothing is sent from here; "
                "type the request in Claude Code afterwards."
            )
            return
        self._setBaselineStatus(
            f"Step {step_id} — {description}" if step_id else description
        )

    def _onBaselineModeChanged(self, *_args):
        mode = self._baselineMode()
        info = BaselineRunner.mode_info(mode)
        combo = getattr(self, "_baselineModeCombo", None)
        if combo is not None:
            combo.setToolTip(info.get("description", ""))
        # Each baseline owns its own Conversation / Generated Code content, so
        # changing the selector changes which transcript the Debug pages show.
        if self._baselineEngaged() and not self._baselineBusy():
            self._showBaselineDebugContext()
        self._syncBaselineSendButton()
        self._updateBaselineInfo()

    def _syncBaselineSendButton(self):
        """Make Send read (and do) whatever the selected baseline needs."""
        button = getattr(self, "sendButton", None)
        if button is None:
            return
        if not self._baselineEngaged():
            button.setText(getattr(self, "_baselineSendText", "Send") or "Send")
            button.setStyleSheet(getattr(self, "_baselineSendStyle", "") or "")
            button.setToolTip("")
            # Routed: with baseline mode off, a guided workflow owns the row.
            self._setSendEnabled(bool(self.promptInput.toPlainText().strip()))
            return

        mode = self._baselineMode()
        info = BaselineRunner.mode_info(mode)
        server = getattr(self, "_baselineMcpServer", None)
        armed = bool(server is not None and server.armed)
        label = info.get("send_label_active") if armed else info.get("send_label")
        button.setText(label or "Run\nBaseline")
        # Amber, so a baseline Send never looks like a normal agent turn.
        button.setStyleSheet(
            "QPushButton { background-color: #e08a00; color: white; border: none;"
            " font-weight: bold; border-radius: 4px; }"
            "QPushButton:hover { background-color: #c47700; }"
            "QPushButton:disabled { background-color: #cccccc; }"
        )
        button.setToolTip(info.get("description", ""))
        if getattr(self, "_baselineRejection", ""):
            button.setEnabled(False)
        elif armed or not info.get("needs_prompt_box", True):
            self._setSendEnabled(True)
        else:
            self._setSendEnabled(bool(self.promptInput.toPlainText().strip()))

    def _onBaselineToggleClicked(self):
        """Turn baseline mode on/off (the scales button in the replay row)."""
        if getattr(self, "_baselineRow", None) is None:
            return
        if getattr(self, "_baselineActive", False):
            if self._baselineBusy():
                self._setBaselineStatus("A baseline run is in progress; stop it first.")
                return
            self._exitBaselineMode()
            return
        self._baselineActive = True
        # Visible only where a baseline can actually run; _updateBaselineControls
        # re-decides this on every scrub.
        engaged = self._baselineEngaged()
        self._baselineRow.setVisible(engaged)
        # Baseline mode hands the prompt box + Send back to the user; the
        # guided workflow had them switched off.
        self._refreshInputAvailability()
        if engaged:
            self._showBaselineDebugContext()
            self._refreshBaselineTarget()
        self._onBaselineModeChanged()

    def _exitBaselineMode(self):
        self._baselineActive = False
        self._baselineRejection = ""
        row = getattr(self, "_baselineRow", None)
        if row is not None:
            row.setVisible(False)
        # Put the Debug pages back on the pipeline's own transcript and code.
        # Anything the pipeline produced while a baseline view was open was
        # written to that buffer all along, so it reappears complete.
        self._switchDebugContext(self.PIPELINE_DEBUG_CONTEXT)
        self._syncBaselineSendButton()
        # Guided workflow still running? Then it takes the input row back.
        self._refreshInputAvailability()

    # ------------------------------------------------- Debug-view isolation
    @staticmethod
    def _baselineDebugKey(mode):
        return f"baseline:{mode}"

    def _showBaselineDebugContext(self):
        """Point the Debug pages at the selected baseline's own buffer."""
        mode = self._baselineMode()
        label = BaselineRunner.mode_label(mode)
        banner = (
            '<div style="margin: 8px 0; padding: 6px 10px; background-color: #fff6e5;'
            ' border-left: 4px solid #e08a00;">'
            f'<b style="color: #7a4a00;">Baseline view — {self.escapeHtml(label)}</b>'
            '<div style="color: #7a4a00; font-size: 11px;">'
            'Only this baseline\'s runs appear here. The pipeline\'s own conversation '
            'and generated code are kept separately and come back when you close the '
            'baseline row.</div></div>'
        )
        self._switchDebugContext(self._baselineDebugKey(mode), banner_html=banner)

    def _commitBaselineChatEntry(self, title, reasoning="", message="", color="#009900"):
        """Append a permanent Conversation entry for the running baseline.

        Unlike the pipeline's streaming entry, the reasoning block is KEPT in
        the committed HTML: seeing how each baseline reasoned is the point of
        the comparison. Long reasoning is capped for QTextEdit's sake; the full
        text still goes to the run folder's thinking history.
        """
        parts = []
        if reasoning:
            shown = str(reasoning)
            if len(shown) > 20000:
                shown = shown[:20000] + "\n… (truncated; see the run folder's thinking history)"
            parts.append(
                '<div style="margin-left: 10px; margin-top: 5px; padding: 8px;'
                ' background-color: #f5f5f0; border-left: 3px solid #ccc;'
                ' color: #888; font-style: italic;">'
                f'{self.escapeHtml(shown).replace(chr(10), "<br>")}</div>'
            )
        if message:
            parts.append(
                '<div style="margin-left: 10px; margin-top: 5px;">'
                f'{self.escapeHtml(str(message)).replace(chr(10), "<br>")}</div>'
            )
        if not parts:
            return
        timestamp = qt.QDateTime.currentDateTime().toString("hh:mm:ss")
        html = (
            '<div style="margin: 10px 0;">'
            f'<span style="color: #999; font-size: 10px;">[{timestamp}]</span> '
            f'<span style="color: {color}; font-weight: bold;">{self.escapeHtml(title)}:</span>'
            f'{"".join(parts)}</div>'
            '<hr style="border: none; border-top: 1px solid #eee; margin: 5px 0;">'
        )
        self._debugWriteEntries().append(html)
        # The live streaming fragment has been folded into this entry.
        self._streaming = False
        self._streamContent = ""
        self._thinkingDisplayText = ""
        self._thinkingDisplayed = False
        self._renderChatIfVisible()

    def _handleBaselineThinkingRound(self, payload):
        """Commit one completed reasoning round from the online-only tool loop."""
        run = getattr(self, "_baselineActiveRun", None)
        if run is None:
            return
        text = str((payload or {}).get("text", "")).strip()
        if not text:
            return
        run["thinking_rounds"] = int(run.get("thinking_rounds", 0)) + 1
        self._commitBaselineChatEntry(
            f"Thinking (round {run['thinking_rounds']})", reasoning=text, color="#7a4a00",
        )
        try:
            self._appendThinkingToFile(text, turn=getattr(self, "_currentTurn", 1))
        except Exception:
            logger.debug("Baseline thinking history write failed", exc_info=True)

    def _setBaselineStatus(self, message):
        """Set the baseline row's info line.

        Deliberately does NOT call processEvents: this also runs inside the MCP
        request handler, where re-entering the event loop would let a second
        HTTP request interleave with the first.
        """
        label = getattr(self, "_baselineInfoLabel", None)
        if label is not None:
            label.setText(str(message or ""))

    # ------------------------------------------------- shared Send / prompt box
    def onSendButtonClicked(self):
        """Route Send to the selected baseline while one is engaged."""
        if not self._baselineEngaged():
            super().onSendButtonClicked()
            return
        server = getattr(self, "_baselineMcpServer", None)
        if server is not None and server.armed:
            self._onBaselineDisarmClicked()
            return
        if self._baselineMode() == MODE_CLAUDE_CODE:
            self._onBaselineArmClicked()
            return
        self._runBaselineFromPrompt()

    def onPromptTextChanged(self):
        """Keep Send enabled in the mode that takes no prompt here."""
        if self._baselineEngaged():
            self._syncBaselineSendButton()
            return
        super().onPromptTextChanged()

    # ------------------------------------------------------------------ state
    def _baselineMode(self):
        combo = getattr(self, "_baselineModeCombo", None)
        if combo is None:
            return MODE_PURE_LLM
        data = combo.itemData(combo.currentIndex)
        return str(data or MODE_PURE_LLM)

    def _baselineBusy(self):
        return bool(getattr(self, "_baselineActiveRun", None))

    def _baselineTargetStepId(self, state=None):
        """Step the baseline would act on: the previewed one, else the live one."""
        runtime = getattr(self, "_workflowRuntime", None)
        session = getattr(runtime, "session", None) if runtime else None
        if session is None:
            return ""
        index = session.preview_index
        if index is not None and 0 <= index < len(session.checkpoints):
            return session.checkpoints[index].step_id
        state = state or getattr(self, "_currentWorkflowUiState", {}) or {}
        return str(state.get("current_step") or session.current_step or "")

    #: Where the Claude Code condition reads its step brief from. This is that
    #: session's own workspace, so it needs no --add-dir and no extra MCP tool —
    #: the skill's tool surface stays exactly as it ships.
    CLAUDE_CODE_WORKSPACE = "MCPConnection"

    def _publishClaudeCodeStepBrief(self, step_context):
        """Write the step brief where the external Claude Code session can read it.

        Without this, Claude Code would be the only condition working from the
        user's sentence alone, while pure-LLM and online-only each get ~1.8 KB of
        task context injected into their messages — which would make any
        comparison against it a comparison of briefings, not of approaches.

        Identical text, identical allow-list (BaselineRunner.TASK_STEP_KEYS);
        only the delivery differs, because that session takes its prompt
        elsewhere. A copy also goes to the run folder, so what the condition was
        given is auditable after the fact.
        """
        import time
        try:
            document = BaselineRunner.render_step_brief_document(
                step_context, armed_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            )
        except Exception:
            logger.warning("Could not render the Claude Code step brief", exc_info=True)
            return ""
        target = os.path.join(
            SLICER_AI_AGENT_ROOT, self.CLAUDE_CODE_WORKSPACE,
            BaselineRunner.CLAUDE_CODE_BRIEF_NAME,
        )
        written = RunLog.write_text(target, document)
        if not written:
            self._setBaselineStatus(
                f"Warning: could not write {BaselineRunner.CLAUDE_CODE_BRIEF_NAME} — "
                "Claude Code will not see the step brief."
            )
        # Same bytes into the run folder, so a reviewer can confirm later what
        # this condition was actually told.
        RunLog.write_text(
            os.path.join(self._currentLogDir, BaselineRunner.CLAUDE_CODE_BRIEF_NAME),
            document,
        )
        self._recordRoleEvent("Baseline", "step_brief_published", {
            "path": written,
            "chars": len(document),
        })
        return written

    def _nextBaselineAttempt(self, mode, step_id):
        """1-based attempt number for this (condition, step) in this session.

        Retrying a step under the same condition must not collide on the folder
        name, and how many tries a condition needed is itself a result — so the
        count is visible in the folder name (``_a2``) rather than averaged away.
        """
        counts = getattr(self, "_baselineAttemptCounts", None)
        if counts is None:
            counts = self._baselineAttemptCounts = {}
        key = (str(mode), str(step_id))
        counts[key] = int(counts.get(key, 0)) + 1
        return counts[key]

    # ------------------------------------------------------------------ start
    def _beginBaselineRun(self, mode, prompt):
        """Rewind (when previewing) and open the step for an external producer.

        Returns the run-state dict, or None when the run could not start (the
        caller has already been told why).
        """
        runtime = getattr(self, "_workflowRuntime", None)
        session = getattr(runtime, "session", None) if runtime else None
        if session is None:
            self._setBaselineStatus("No active workflow session.")
            return None
        if self._baselineBusy():
            self._setBaselineStatus("A baseline run is already in progress.")
            return None

        # Refuse steps that generate no code (a value pick or a 3D interaction)
        # BEFORE rewinding, so a rejected attempt does not destroy the timeline.
        ok, reason = runtime.external_step_eligibility(self._baselineTargetStepId())
        if not ok:
            self._setBaselineStatus(reason)
            return None

        index = session.preview_index
        descriptor = {}
        if index is not None:
            descriptor = self._prepareReplayRewind(index)
            if descriptor is None:
                self._setBaselineStatus("Rewind cancelled.")
                return None
            step_id = descriptor.get("step_id", "")
        else:
            step_id = self._baselineTargetStepId()
        if not step_id:
            self._setBaselineStatus("Could not resolve which step to run.")
            return None

        # Carry the checkpoint's recorded action/args forward, so the checkpoint
        # this run records is as faithful as a template-driven one.
        step_result = runtime.begin_external_step(
            step_id,
            action=descriptor.get("action", "start") or "start",
            args=descriptor.get("args") or {},
            origin=f"baseline_{mode}",
        )
        if not isinstance(step_result, dict) or step_result.get("error"):
            self._setBaselineStatus(
                (step_result or {}).get("error", "Could not open the step.")
            )
            return None

        import time
        from SlicerAIAgentLib import RunLog
        # A baseline gets its OWN run folder, named for the condition, the
        # procedure, the step and the attempt, e.g.
        #   logs/20260730_143512_pureLLM_BoneReconstructionPlanner_cb_step_08_a1/
        # so it can never be confused with the pipeline's own folder for the
        # same step.
        attempt = self._nextBaselineAttempt(mode, step_id)
        # Park the pipeline's own run folder. When this baseline finishes it
        # auto-advances the workflow, and that next step is dispatched by the
        # PIPELINE — its artifacts must not end up nested inside this baseline's
        # folder. Restored in _restoreAfterBaseline, before the advance fires.
        # Guarded: a retry that re-arms before the previous restore would
        # otherwise park the BASELINE's folder as if it were the pipeline's.
        if not getattr(self, "_pipelineLogDir", None):
            self._pipelineLogDir = self._currentLogDir
            self._pipelineRunManifest = getattr(self, "_currentRunManifest", None)
            self._pipelineStepLogDir = getattr(self, "_currentStepLogDir", "")
            self._pipelineStepId = getattr(self, "_currentStepId", "")
            # The role trace is parked too. It is cleared below for the
            # baseline's own events; without parking, the pipeline's run-root
            # trace would come back holding the BASELINE's events and none of
            # its own (observed: a 10-step run whose run-root trace held 5
            # events, 3 of them Baseline).
            self._pipelineRoleTrace = list(getattr(self, "_roleTrace", []) or [])
        self._currentLogDir = self._createRunLogDir(
            getattr(self, "_currentTurn", 1),
            condition=mode,
            extension=session.extension_name,
            step_id=step_id,
            attempt=attempt,
            transport=(
                getattr(getattr(self, "_baselineMcpServer", None), "transport", "")
                if mode == MODE_CLAUDE_CODE else None
            ),
        )
        self._roleTrace = []
        self._timing = {"turn_start": time.time(), "prompt": prompt, "mode": f"baseline_{mode}"}
        self._recordRoleEvent("Baseline", "run_started", {
            "mode": mode,
            "step_id": step_id,
            "prompt_length": len(prompt or ""),
        })

        run = {
            "mode": mode,
            "prompt": prompt,
            # Which transport carried the code, recorded so a reader never has
            # to infer it (only meaningful for the Claude Code condition).
            "transport": (
                getattr(getattr(self, "_baselineMcpServer", None), "transport", "")
                if mode == MODE_CLAUDE_CODE else ""
            ),
            "step_id": step_id,
            "step_result": step_result,
            "extension": session.extension_name,
            "started": time.time(),
            "before": self._baselineSnapshot(),
            "log_dir": self._currentLogDir,
            "attempt": attempt,
            # Computed HERE, for every mode, so all three conditions are given
            # the identical task brief. The two prompt-driven modes get it
            # injected into their messages; Claude Code reads it from a file in
            # its workspace (see _publishClaudeCodeStepBrief).
            "step_context": self._baselineStepContext(step_id),
        }
        self._baselineActiveRun = run
        # The step this baseline stands in for, written up front so a run folder
        # is self-explanatory even if the run never finishes.
        self._saveStepDescriptorToFile(step_result)
        RunLog.write_text(os.path.join(self._currentLogDir, "prompt.txt"), prompt or "")
        if mode == MODE_CLAUDE_CODE:
            self._publishClaudeCodeStepBrief(run["step_context"])
        # Everything this run produces — chat, thinking, generated code — is
        # written to THIS baseline's buffer, never the pipeline's.
        self._debugWriteContext = self._baselineDebugKey(mode)
        self._showBaselineDebugContext()
        self._setBaselineRunUiEnabled(False)
        self._updateWorkflowPanel(runtime.state_for_ui())
        return run

    def _restorePipelineLogDir(self):
        """Point run-log writing back at the pipeline's folder after a baseline.

        No-op when nothing was parked (a baseline that never started, or a
        second call), so it is safe on every exit path.
        """
        parked = getattr(self, "_pipelineLogDir", None)
        if not parked:
            return
        self._currentLogDir = parked
        self._currentRunManifest = getattr(self, "_pipelineRunManifest", None)
        self._currentStepLogDir = getattr(self, "_pipelineStepLogDir", "")
        self._currentStepId = getattr(self, "_pipelineStepId", "")
        # Give the pipeline its own event history back, so the run-root trace
        # is the pipeline's story and the baseline's stays in its own folder.
        self._roleTrace = list(getattr(self, "_pipelineRoleTrace", []) or [])
        self._stepTraceStart = len(self._roleTrace)
        self._pipelineRoleTrace = []
        self._pipelineLogDir = None
        self._pipelineRunManifest = None
        if self.logic and self.logic.llmClient:
            self.logic.llmClient.setDebugOutputDir(
                self._currentStepLogDir or self._currentLogDir
            )

    def _setBaselineRunUiEnabled(self, enabled):
        for name in ("_baselineModeCombo", "_baselineToggleButton"):
            widget = getattr(self, name, None)
            if widget is not None:
                widget.setEnabled(bool(enabled))
        self._setSendEnabled(bool(enabled))

    def _baselineSnapshot(self):
        """Scene snapshot for the run record.

        ``buildSceneSnapshot`` lives on the LOGIC (``LogicSceneMixin``), not on
        the widget — calling it bare would raise AttributeError, and the record
        would silently carry an empty scene_delta for every run.
        """
        if not self.logic:
            return None
        try:
            return self.logic.buildSceneSnapshot()
        except Exception:
            logger.warning("Baseline scene snapshot failed", exc_info=True)
            return None

    # ----------------------------------------------------- modes 1 and 2 (LLM)
    def _runBaselineFromPrompt(self):
        """Send pressed in a prompt-driven baseline mode."""
        mode = self._baselineMode()
        prompt = self.promptInput.toPlainText().strip()
        if not prompt:
            self._setBaselineStatus("Type the prompt for this step first.")
            return
        if not (self.logic and self.logic.llmClient and self.logic.hasApiKey()):
            self._setBaselineStatus("Configure the API key in Settings first.")
            return

        run = self._beginBaselineRun(mode, prompt)
        if run is None:
            return
        # Clear the box once the run has actually started. Only after
        # _beginBaselineRun returns non-None: an attempt refused before that
        # (ineligible step, rewind cancelled, run already in flight) must leave
        # the text the user typed intact, or the refusal costs them their prompt.
        #
        # The prompt is not lost — it is echoed to the transcript below, stored
        # on the run, and written to prompt.txt in the run folder.
        self._clearBaselinePrompt()
        self.appendToChat("You", f"[{BaselineRunner.mode_label(mode)}] {prompt}")
        self._setBaselineStatus(
            f"{BaselineRunner.mode_label(mode)}: generating code for {run['step_id']}…"
        )
        # Open a live streaming entry so reasoning deltas render on the
        # Conversation page as they arrive, exactly like a normal turn.
        self._streamReasoning = ""
        self._streamContent = ""
        self._streaming = True
        self._thinkingDisplayText = ""
        self._thinkingDisplayed = False
        self._streamTimestamp = qt.QDateTime.currentDateTime().toString("hh:mm:ss")
        self._renderStreamingEntry()
        # Read the MRML scene HERE, on the Qt main thread. The generation call
        # itself is network I/O and moves to a worker thread, which must never
        # touch the scene (the production path does the same in
        # WidgetSendMixin.onSendButtonClicked).
        try:
            scene = self.logic._buildSceneContext()
        except Exception:
            logger.debug("Baseline scene context failed", exc_info=True)
            scene = None
        # The step brief was computed once in _beginBaselineRun, so every
        # condition works from exactly the same text. Node properties read live
        # MRML state, so they are gathered here, before the worker starts.
        step_context = run["step_context"]
        node_details = (
            self._baselineNodeDetails(scene) if mode == MODE_PURE_LLM else None
        )

        def _generate():
            import time
            started = time.time()
            try:
                if mode == MODE_PURE_LLM:
                    payload = self._generatePureLlmCode(
                        prompt, scene, step=step_context, node_details=node_details,
                    )
                elif mode == MODE_ONLINE_ONLY:
                    payload = self._generateOnlineOnlyCode(prompt, scene, step=step_context)
                else:
                    raise RuntimeError(f"Unsupported prompt-driven baseline: {mode}")
                payload["seconds"] = round(time.time() - started, 3)
                self._streamQueue.put(("baseline_generated", payload))
            except Exception as exc:
                self._streamQueue.put(("baseline_generated", {
                    "error": str(exc),
                    "seconds": round(time.time() - started, 3),
                }))

        threading.Thread(target=_generate, daemon=True).start()

    # ------------------------------------------------------- step context
    #
    # What a baseline is told about the step it stands in for. The boundary --
    # task/world facts yes, offline-analysis artefacts no -- is defined and
    # justified in BaselineRunner (TASK_STEP_KEYS / WITHHELD_STEP_KEYS); these
    # methods only gather the allowed side of it from live runtime state.

    #: Node classes worth pushing full properties for. Bulk display/view/storage
    #: nodes are excluded: they bloat the prompt without describing the patient.
    _BASELINE_DETAIL_CLASSES = (
        "vtkMRMLScalarVolumeNode", "vtkMRMLLabelMapVolumeNode",
        "vtkMRMLSegmentationNode", "vtkMRMLModelNode",
        "vtkMRMLMarkupsFiducialNode", "vtkMRMLMarkupsCurveNode",
        "vtkMRMLMarkupsClosedCurveNode", "vtkMRMLMarkupsLineNode",
        "vtkMRMLMarkupsPlaneNode", "vtkMRMLMarkupsROINode",
        "vtkMRMLMarkupsAngleNode", "vtkMRMLLinearTransformNode",
        "vtkMRMLTransformNode", "vtkMRMLTableNode",
    )
    _BASELINE_DETAIL_LIMIT = 14

    #: How many upcoming steps' DESCRIPTIONS to include, marked "context only".
    #:
    #: This is the one piece of forward-looking information a baseline gets, and
    #: it is a deliberate choice rather than an oversight. It is cookbook prose —
    #: no code, no step ids, no metadata — and it is what a surgeon following the
    #: written procedure can see on the next page. It helps a condition leave the
    #: scene in a state the procedure can continue from, which is part of doing
    #: the step well.
    #:
    #: Note it is more than the PIPELINE has: the pipeline dispatches the step's
    #: template with no lookahead at all. So this favours the baselines, in the
    #: spirit of "give each condition every chance". Set to 0 for a strict
    #: no-forward-information ablation; nothing else needs to change.
    BASELINE_LOOKAHEAD_STEPS = 3

    def _baselineStepContext(self, step_id):
        """Task-side brief for ``step_id``, assembled from live runtime state."""
        runtime = getattr(self, "_workflowRuntime", None)
        session = getattr(runtime, "session", None) if runtime else None
        if not (runtime and session and step_id):
            return {}

        try:
            from SlicerAIAgentLib.ExtensionCLILoader import get_workflow_graph
            graph = get_workflow_graph(session.extension_name) or {}
        except Exception:
            logger.debug("Baseline step context: workflow graph unavailable", exc_info=True)
            graph = {}
        steps = [s for s in (graph.get("steps") or []) if isinstance(s, dict)]
        step_ids = [s.get("step_id") for s in steps]
        index = step_ids.index(step_id) + 1 if step_id in step_ids else 0

        meta = {}
        for candidate in steps:
            if candidate.get("step_id") == step_id:
                # ALLOW-list: only the task-describing keys cross this line.
                meta = {k: candidate.get(k) for k in BaselineRunner.TASK_STEP_KEYS}
                break

        instructions = {}
        try:
            instructions = runtime._step_instructions_for(step_id) or {}
        except Exception:
            logger.debug("Baseline step context: instructions unavailable", exc_info=True)

        completed = []
        done = set(session.completed_steps or [])
        for candidate in steps:
            sid = candidate.get("step_id")
            if sid in done and sid != step_id:
                completed.append({
                    "step_id": sid,
                    "description": " ".join(str(candidate.get("description") or "").split()),
                })

        remaining = []
        if index and self.BASELINE_LOOKAHEAD_STEPS > 0:
            for candidate in steps[index:index + self.BASELINE_LOOKAHEAD_STEPS]:
                text = " ".join(str(candidate.get("description") or "").split())
                if text:
                    remaining.append(text)

        choices = {}
        try:
            from SlicerAIAgentLib.ExtensionCLILoader import get_workflow_choices
            choices = dict(get_workflow_choices(session.extension_name) or {})
        except Exception:
            logger.debug("Baseline step context: choices unavailable", exc_info=True)

        context = {
            "extension": session.extension_name,
            "index": index,
            "total": graph.get("step_count") or len(steps),
            "title": instructions.get("title", ""),
            "simple": instructions.get("simple", ""),
            "detailed": instructions.get("detailed", ""),
            "completed": completed,
            "remaining": remaining,
            "choices": choices,
        }
        context.update(meta)
        context.setdefault("step_id", step_id)
        return context

    def _baselineNodeDetails(self, scene):
        """Full properties of the data nodes in play, for the tool-free condition.

        The pipeline's agent can call ``GetNodeProperties`` mid-turn; the pure
        LLM cannot, so the same observable state is pushed to it up front rather
        than being an advantage the comparison never intended to test.
        """
        nodes = (scene or {}).get("scene_summary") or []
        wanted = [
            entry.get("id") for entry in nodes
            if isinstance(entry, dict)
            and entry.get("id")
            and str(entry.get("class") or "") in self._BASELINE_DETAIL_CLASSES
        ]
        if not wanted:
            return {}
        details = {}
        try:
            from SlicerAIAgentLib import SceneTools
            for node_id in wanted[: self._BASELINE_DETAIL_LIMIT]:
                details[node_id] = SceneTools.getNodeProperties(node_id)
        except Exception:
            logger.debug("Baseline node details failed", exc_info=True)
            return {}
        return details

    def _saveBaselineMessages(self, messages, tools=None):
        """Persist the EXACT payload a baseline was sent.

        This is the artefact the comparison rests on: a reviewer has to be able
        to confirm what each condition was told, and in particular that no
        offline-analysis artefact reached it (see BaselineRunner.TASK_STEP_KEYS).
        Written from the worker thread, which is safe — it touches only files.
        """
        try:
            log_dir = (getattr(self, "_baselineActiveRun", None) or {}).get("log_dir") \
                or self._getCurrentLogDir()
            body = []
            for i, message in enumerate(messages or []):
                body.append("=" * 60)
                body.append(f"MESSAGE {i + 1} | role: {message.get('role', 'unknown')}")
                body.append("=" * 60)
                body.append(f"{message.get('content', '')}\n")
            RunLog.write_text(os.path.join(log_dir, "messages_sent.txt"), "\n".join(body))
            RunLog.write_json(os.path.join(log_dir, "messages_sent.json"), {
                "message_count": len(messages or []),
                "prompt_chars": sum(
                    len(m.get("content", "") or "") for m in (messages or [])
                ),
                "per_message_chars": [
                    {"role": m.get("role"), "chars": len(m.get("content", "") or "")}
                    for m in (messages or [])
                ],
                "tools_offered": sorted(
                    filter(None, (BaselineRunner._tool_name(t) for t in (tools or [])))
                ),
            })
        except Exception:
            logger.debug("Baseline message dump failed", exc_info=True)

    def _generatePureLlmCode(self, prompt, scene, step=None, node_details=None):
        """One bare call: no retrieval, no tools, no CLI, no history."""
        client = self.logic.llmClient
        messages = BaselineRunner.build_pure_llm_messages(
            prompt, scene=scene, step=step, node_details=node_details,
        )
        self._saveBaselineMessages(messages)
        response = client.chatIsolated(messages)
        return {
            "code": response.get("code"),
            "message": response.get("message", ""),
            "reasoning_content": response.get("reasoning_content", ""),
            "tokens": response.get("tokens"),
            "cost": response.get("cost"),
            "model": client.model,
            "provider": getattr(client, "provider", ""),
            "prompt_chars": sum(len(m.get("content", "")) for m in messages),
        }

    #: Tool-round budget for the online-only condition.
    #:
    #: Higher than the production turn's 10 on purpose. This condition's entire
    #: thesis is "can it find the API by searching, without the offline
    #: analysis?", so cutting it off mid-search would measure the budget rather
    #: than the approach. It must reach its own natural stopping point -- or
    #: demonstrably fail to.
    BASELINE_ONLINE_TOOL_ROUNDS = 16

    def _generateOnlineOnlyCode(self, prompt, scene, step=None):
        """Full retrieval + built-in tool loop, generated CLI ablated.

        Isolated from ``conversation_history`` so the baseline neither reads the
        real run's context nor pollutes it, and the generated-CLI tool schemas
        are filtered out of the tool list by identity (see
        ``BaselineRunner.strip_generated_cli_tools``).

        The *raw* extension source trees stay searchable and are advertised in
        the prompt: what is ablated is the offline analysis, not the code base.
        """
        client = self.logic.llmClient
        context = {"scene": scene}
        retrieval_timing = {}
        retrieval = self.logic._buildRetrievalContext(prompt, retrieval_timing)
        if retrieval:
            context["retrieval_results"] = retrieval
        messages = BaselineRunner.build_online_only_messages(
            client, prompt, context,
            step=step,
            source_roots_block=BaselineRunner.extension_source_roots_block(),
        )
        tools = BaselineRunner.strip_generated_cli_tools(getattr(self.logic, "skillTools", []))
        self._saveBaselineMessages(messages, tools)
        response = client.chatWithToolsIsolated(
            messages=messages,
            tools=tools,
            tool_executor=self.logic._executeTool,
            max_tool_rounds=self.BASELINE_ONLINE_TOOL_ROUNDS,
            on_status=lambda text: self._streamQueue.put(("baseline_status", text)),
            # Same event shapes the production turn uses, so tool-search
            # progress and live thinking render on the Conversation page.
            on_progress=lambda progress: self._streamQueue.put(("delta", dict(progress))),
            on_reasoning_delta=lambda chunk: self._streamQueue.put(("thinking_delta", chunk)),
            on_reasoning=lambda text, _round: self._streamQueue.put(
                ("baseline_thinking", {"text": text})
            ),
        )
        timing_report = response.get("timing_report") or {}
        return {
            "code": response.get("code"),
            "message": response.get("message", ""),
            "reasoning_content": response.get("reasoning_content", ""),
            "tokens": response.get("tokens"),
            "cost": response.get("cost"),
            "model": client.model,
            "provider": getattr(client, "provider", ""),
            "tool_rounds": timing_report.get("tool_rounds"),
            "tool_calls": len(response.get("tool_calls_history") or []),
            "retrieval_timing": retrieval_timing,
            "prompt_chars": sum(len(m.get("content", "")) for m in messages),
        }

    def _handleBaselineGenerated(self, payload):
        """Main-thread continuation once a baseline model call has returned."""
        run = getattr(self, "_baselineActiveRun", None)
        if run is None:
            return
        payload = payload or {}
        run["generation"] = payload

        # Commit the model's reasoning + answer to this baseline's Conversation
        # page. Only commit the final reasoning when no per-round reasoning was
        # already committed (the online-only tool loop reports rounds; the
        # single pure-LLM call does not), so nothing is shown twice.
        reasoning = ""
        if not int(run.get("thinking_rounds", 0)):
            reasoning = str(payload.get("reasoning_content", "") or "")
            if reasoning:
                try:
                    self._appendThinkingToFile(reasoning, turn=getattr(self, "_currentTurn", 1))
                except Exception:
                    logger.debug("Baseline thinking history write failed", exc_info=True)
        self._commitBaselineChatEntry(
            f"Assistant ({BaselineRunner.mode_label(run['mode'])})",
            reasoning=reasoning,
            message=str(payload.get("message", "") or ""),
        )

        if payload.get("error"):
            self._finishBaselineRun(None, error=f"Generation failed: {payload['error']}")
            return
        code = payload.get("code")
        if not code or not str(code).strip():
            self._finishBaselineRun(None, error="The model returned no ```python block.")
            return
        run["code"] = code
        self._showBaselineCode(code)
        self._setBaselineStatus(
            f"Generated {len(code)} chars in {payload.get('seconds', 0)}s — executing…"
        )
        self._recordRoleEvent("Baseline", "code_generated", {
            "mode": run["mode"],
            "code_chars": len(code),
            "seconds": payload.get("seconds"),
        })
        try:
            # No suffix: a baseline folder is flat and already named for its
            # condition, so `code_baseline_online_only.py` only repeated it.
            self._saveGeneratedCodeToFile(code)
        except Exception:
            logger.debug("Baseline code artifact write failed", exc_info=True)

        self.logic.executeCodeAsync(code, self._onBaselineExecutionComplete)

    def _onBaselineExecutionComplete(self, result):
        self._finishBaselineRun(result or {})

    # -------------------------------------------------------- mode 3 (MCP)
    def _ensureBaselineMcpServer(self):
        """Attach to the skill's OWN pasted server — never one we host.

        Keeping the shipped ``slicer-mcp-server.py`` as the transport is what
        makes this condition "Claude Code + the Slicer skill as documented": the
        skill's MCP config section, its ``--add-dir``, and its console script
        are all unchanged, and every other tool it exposes is untouched. We only
        borrow ``execute_python`` while a step is armed.

        If the script has not been pasted there is nothing to attach to, and we
        say so rather than silently substituting a different endpoint — which
        transport carried the code must never be ambiguous in the records.
        """
        bridge = getattr(self, "_baselineMcpServer", None)
        if bridge is None:
            from SlicerAIAgentLib.BaselineMCPServer import BaselineMCPBridge
            bridge = BaselineMCPBridge.instance()
            self._baselineMcpServer = bridge
        if not bridge.available:
            # Arming is an explicit user action, so it always gets a fresh
            # start attempt — unlike the passive panel refresh, which tries
            # once per session. This is also the path that recovers when the
            # server was stopped mid-session with mcpLogic.stop().
            self._mcpAutoStartAttempted = False
            self._autoStartSkillMcpServer()
        if not bridge.available:
            self._setBaselineStatus(
                getattr(self, "_mcpAutoStartError", "") or bridge.NOT_FOUND_MESSAGE
            )
            return None
        return bridge

    def _baselineBridgeStatus(self):
        """Quiet probe of the skill's MCP server: ``(available, url)``.

        Side-effect free, unlike ``_ensureBaselineMcpServer`` (which writes the
        status line), so the info line can report attach state on every refresh
        without a button to press.
        """
        try:
            from SlicerAIAgentLib.BaselineMCPServer import BaselineMCPBridge
            bridge = getattr(self, "_baselineMcpServer", None)
            if bridge is None:
                bridge = BaselineMCPBridge.instance()
                self._baselineMcpServer = bridge
            return bool(bridge.available), bridge.url
        except Exception:
            logger.debug("MCP bridge probe failed", exc_info=True)
            return False, ""

    def _autoStartSkillMcpServer(self):
        """Run the skill's ``slicer-mcp-server.py`` so the user need not paste it.

        Returns ``(available, url)``. Attempted at most once per session unless
        the previous attempt succeeded — a failing script must not be re-executed
        on every panel refresh, which would spam the console and the log.

        The script itself is unmodified and runs in ``__main__``, so what Claude
        Code connects to is the skill's own server with its own five tools; only
        the copy-paste step is automated. Refused while a step is ARMED, because
        re-running rebuilds ``TOOL_HANDLERS`` and would silently drop the armed
        ``execute_python`` wrapper.
        """
        server = getattr(self, "_baselineMcpServer", None)
        if server is not None and server.armed:
            return True, server.url
        if getattr(self, "_mcpAutoStartAttempted", False):
            return self._baselineBridgeStatus()

        self._mcpAutoStartAttempted = True
        from SlicerAIAgentLib.BaselineMCPServer import (
            run_skill_mcp_script, skill_mcp_script_path,
        )
        script = skill_mcp_script_path()
        self._setBaselineStatus(
            f"Starting the Slicer skill's MCP server ({os.path.basename(script) or 'slicer-mcp-server.py'})…"
        )
        slicer.app.processEvents()

        ok, detail = run_skill_mcp_script(script)
        available, url = self._baselineBridgeStatus()
        if ok and available:
            self._mcpAutoStartError = ""
            self.appendToChat(
                "System",
                f"Started the Slicer skill's MCP server at {url} "
                f"(ran {detail} — the skill's own script, unmodified). "
                "Stop it later with mcpLogic.stop() in the Python console.",
            )
            self._recordRoleEvent("Baseline", "mcp_server_autostarted", {
                "script": detail, "url": url,
            })
        else:
            # ok-but-unavailable means the script ran without defining the
            # handler registry -- report that, not a misleading success.
            self._mcpAutoStartError = detail if not ok else (
                "The script ran but did not register its tools."
            )
            logger.warning("MCP auto-start unsuccessful: %s", self._mcpAutoStartError)
        return available, url

    def _onBaselineArmClicked(self):
        server = self._ensureBaselineMcpServer()
        if server is None:
            return
        run = self._beginBaselineRun(MODE_CLAUDE_CODE, "")
        if run is None:
            return
        label = f"{run['extension']} step {run['step_id']}"
        # Can still fail if the console script was re-pasted between the
        # availability check and here; that rebuilds TOOL_HANDLERS.
        if not server.arm(self._onBaselineMcpCode, label=label):
            self._finishBaselineRun(
                None, error=server.last_error or "Could not attach to the MCP server."
            )
            return
        # Send becomes "Stop waiting" while armed; _beginBaselineRun disabled it.
        self._setBaselineRunUiEnabled(True)
        self._syncBaselineSendButton()
        self._setBaselineStatus(
            f"Attached to the Slicer skill's MCP server at {server.url} — "
            f"waiting for step {run['step_id']}. Type your request in Claude "
            "Code; the code it sends runs here. Press Send again to stop waiting."
        )
        self.appendToChat(
            "System",
            f"Baseline armed: waiting for Claude Code over MCP at {server.url} "
            f"for step {run['step_id']}.",
        )

    def _onBaselineDisarmClicked(self):
        server = getattr(self, "_baselineMcpServer", None)
        if server is not None:
            server.disarm()
        run = getattr(self, "_baselineActiveRun", None)
        if run is not None and run.get("mode") == MODE_CLAUDE_CODE:
            self._finishBaselineRun(None, error="Cancelled while waiting for Claude Code.")
        self._syncBaselineSendButton()

    def _onBaselineMcpCode(self, code):
        """Execute code that arrived over MCP. Runs on the Qt main thread.

        Synchronous on purpose: the MCP response carries the real stdout/stderr
        back to Claude Code, so it sees what happened and can iterate exactly as
        it would against the plain server. Advancing the workflow is deferred to
        the next event-loop turn so the HTTP response is sent first.
        """
        run = getattr(self, "_baselineActiveRun", None)
        if run is None or run.get("mode") != MODE_CLAUDE_CODE:
            return {
                "success": False,
                "error": "No baseline step is armed in the SlicerAIAgent panel.",
            }
        code = str(code or "")
        run["code"] = code
        self._showBaselineCode(code)
        self._setBaselineStatus(f"Received {len(code)} chars from Claude Code — executing…")
        self._recordRoleEvent("Baseline", "mcp_code_received", {
            "step_id": run.get("step_id"),
            "code_chars": len(code),
        })
        try:
            self._saveGeneratedCodeToFile(code)
        except Exception:
            logger.debug("Baseline code artifact write failed", exc_info=True)

        validation = self.logic.codeValidator.validate(code)
        if not validation.get("valid"):
            result = {
                "success": False,
                "output": "",
                "error": f"Code validation failed: {validation.get('reason', '')}",
                "execution_time": 0.0,
            }
        else:
            result = self.logic.executor.execute(code)

        run["mcp_result"] = result
        qt.QTimer.singleShot(0, lambda: self._finishBaselineRun(result))
        if result.get("success"):
            note = "The SlicerAIAgent workflow will advance to the next step."
        else:
            note = "The step was NOT advanced; fix the code and call execute_python again."
        return {
            "success": bool(result.get("success")),
            "output": result.get("output", ""),
            "error": result.get("error", ""),
            "note": note,
        }

    # ----------------------------------------------------------------- finish
    def _showBaselineCode(self, code):
        """Show the code on Debug > Generated Code, in THIS baseline's buffer."""
        self._setGeneratedCode(code)

    def _finishBaselineRun(self, execution, error=""):
        """Record the run, then advance the workflow when the code succeeded."""
        run = getattr(self, "_baselineActiveRun", None)
        if run is None:
            return

        server = getattr(self, "_baselineMcpServer", None)
        succeeded = bool(execution and execution.get("success")) and not (
            execution or {}
        ).get("timed_out", False)
        # A failed Claude Code attempt keeps the run open: the MCP reply told
        # Claude Code to fix the code and call execute_python again, and the
        # server is still armed, so the retry must find a live run. Clearing it
        # here would make every retry bounce off the "nothing is armed" guard.
        # An explicit cancel disarms first, so `server.armed` is False by then.
        keep_waiting = (
            run.get("mode") == MODE_CLAUDE_CODE
            and not succeeded
            and not error
            and server is not None
            and server.armed
        )
        if not keep_waiting:
            self._baselineActiveRun = None
        if server is not None and run.get("mode") == MODE_CLAUDE_CODE and succeeded:
            server.disarm()

        attempt = int(run.get("attempt", 1))
        delta = BaselineRunner.scene_delta(run.get("before"), self._baselineSnapshot())
        record = BaselineRunner.build_record(
            mode=run["mode"],
            extension_name=run.get("extension", ""),
            step_id=run.get("step_id", ""),
            prompt=run.get("prompt", ""),
            code=run.get("code", ""),
            execution=execution or {},
            generation=run.get("generation") or {},
            delta=delta,
            error=error,
            attempt=attempt,
            transport=run.get("transport", ""),
            step_context=run.get("step_context") or {},
        )
        log_dir = run.get("log_dir") or self._getCurrentLogDir()
        path = BaselineRunner.write_record(log_dir, record)
        # The same detail the pipeline now keeps per step, so the four
        # conditions are read the same way.
        RunLog.write_execution(log_dir, execution, extra={
            "step_id": run.get("step_id"),
            "attempt": attempt,
            "code_chars": len(run.get("code") or ""),
            "scene_delta": delta,
        })
        RunLog.write_json(os.path.join(log_dir, "step_context.json"),
                          run.get("step_context") or {})
        manifest = self._runManifest()
        if manifest is not None:
            generation = run.get("generation") or {}
            manifest.add_step(
                run.get("step_id", ""),
                attempt=attempt,
                status="ok" if succeeded else "failed",
                seconds=(execution or {}).get("execution_time"),
                code_chars=len(run.get("code") or ""),
                error=(error or (execution or {}).get("error") or "")[:500] or None,
            )
            manifest.set_totals(
                generation_seconds=generation.get("seconds"),
                prompt_chars=generation.get("prompt_chars"),
                tokens=generation.get("tokens"),
                cost=generation.get("cost"),
                tool_rounds=generation.get("tool_rounds"),
                tool_calls=generation.get("tool_calls"),
            )
            manifest.finish(
                "completed" if succeeded else ("waiting" if keep_waiting else "failed"),
                record=os.path.basename(path) if path else None,
            )
        self._recordRoleEvent("Baseline", "run_finished", {
            "mode": run["mode"],
            "step_id": run.get("step_id"),
            "attempt": attempt,
            "success": succeeded,
            "record": path,
        })
        self._saveRoleTraceToFile()

        label = BaselineRunner.mode_label(run["mode"])
        if keep_waiting:
            # Still armed: log the failed attempt and wait for the next one.
            run["attempt"] = attempt + 1
            run["code"] = ""
            detail = (execution or {}).get("error") or "Execution failed."
            rolled = self._rollbackFailedBaselineStep(run)
            self._setBaselineStatus(
                f"{label}: attempt {attempt} failed — still waiting for Claude Code "
                f"at {server.url}. {detail[:220]}"
            )
            self.appendToChat(
                "System",
                f"Baseline ({label}) attempt {attempt} failed on step "
                f"{run.get('step_id')}; still armed for a retry.{rolled}",
            )
            self._setBaselineRunUiEnabled(True)
            self._syncBaselineSendButton()
            return

        if error and not execution:
            rolled = self._rollbackFailedBaselineStep(run)
            self._setBaselineStatus(f"{label}: {error}")
            self.appendToChat("Error", f"Baseline ({label}) failed: {error}{rolled}")
            self._restoreAfterBaseline(advanced=False)
            return

        if not succeeded:
            detail = (execution or {}).get("error") or "Execution failed."
            rolled = self._rollbackFailedBaselineStep(run)
            self._setBaselineStatus(
                f"{label}: execution failed — the step was not advanced. {detail[:300]}"
            )
            self.appendToChat(
                "Error",
                f"Baseline ({label}) execution failed:\n{detail[:1000]}{rolled}",
            )
            self._restoreAfterBaseline(advanced=False)
            return

        seconds = (execution or {}).get("execution_time", 0) or 0
        self._setBaselineStatus(
            f"{label}: executed in {seconds:.2f}s. "
            f"Record: {os.path.basename(path) if path else 'not written'}"
        )
        self.appendToChat(
            "System",
            f"Baseline ({label}) completed step {run.get('step_id')} in {seconds:.2f}s. "
            "Advancing the workflow.",
        )
        self._advanceAfterBaseline(run, execution or {})

    def _advanceAfterBaseline(self, run, execution):
        """Mark the substituted step complete and continue the normal workflow."""
        runtime = getattr(self, "_workflowRuntime", None)
        if runtime is None or runtime.session is None:
            self._restoreAfterBaseline(advanced=False)
            return
        try:
            updated = runtime.handle_execution_result(run["step_result"], execution)
        except Exception as exc:
            logger.warning("Baseline step completion failed: %s", exc, exc_info=True)
            self._setBaselineStatus(f"Could not advance the workflow: {exc}")
            self._restoreAfterBaseline(advanced=False)
            return

        self._currentWorkflowStepInfo = updated
        try:
            self._applyWorkflowDisplayProperties(updated)
        except Exception:
            logger.debug("Baseline display properties failed", exc_info=True)
        try:
            self._applyChosenVolumeBackground()
        except Exception:
            logger.debug("Baseline background re-assert failed", exc_info=True)

        self._restoreAfterBaseline(advanced=True)

        if updated.get("type") in ("interactive", "mixed"):
            self._streamQueue.put(("workflow_wait", updated))
            return
        if updated.get("type") == "user_choice":
            self._displayWorkflowChoice(updated)
            self._setReadyStatus()
            return
        next_step = updated.get("next_step")
        if next_step:
            self._updateWorkflowPanel(runtime.state_for_ui(updated))
            self._autoAdvanceWorkflowStep = None
            qt.QTimer.singleShot(150, lambda: self._autoAdvanceNextStep(next_step))
            return
        if updated.get("workflow_completed"):
            self._updateWorkflowPanel(updated)
            self.appendToChat("System", "Generated CLI workflow complete.")
            self._clearCompletedWorkflowState()
            # Leave baseline mode BEFORE flushing. The workflow is over, so
            # there is no step left to compare — and the flush fills the prompt
            # box and auto-presses Send. With baseline mode still engaged, that
            # Send routes through this mixin's override and would start an
            # unintended baseline run on a queued *traditional* request.
            self._exitBaselineMode()
            self._flushQueuedWorkflowPrompts()
        self._setReadyStatus()

    def _rollbackFailedBaselineStep(self, run):
        """Undo a failed baseline attempt so the next one starts clean.

        Without this, whatever a failed attempt half-built stays in the scene
        and belongs to no checkpoint, so no later rewind can remove it — the
        NEXT condition tested on the same step would then start from this one's
        debris. That is the one way the per-step comparison silently stops being
        a comparison, so it is repaired at the moment of failure rather than
        left for the next rewind to miss.

        Returns a short suffix for the chat message (empty when nothing was
        removed), so the user can see it happened.
        """
        runtime = getattr(self, "_workflowRuntime", None)
        if runtime is None or not (run or {}).get("step_id"):
            return ""
        try:
            outcome = runtime.rollback_failed_step(run["step_id"])
        except Exception:
            logger.warning("Failed-step rollback raised", exc_info=True)
            return ""
        self._recordRoleEvent("Baseline", "failed_step_rolled_back", dict(outcome))
        removed = int(outcome.get("removed") or 0)
        if removed:
            return f" Rolled back {removed} node(s) it had created, so the scene is clean again."
        if outcome.get("rolled_back"):
            return " The scene was restored to its pre-step state."
        return ""

    def _restoreAfterBaseline(self, advanced):
        """Re-enable the panel; refresh the workflow view when we did not advance.

        Also hands BOTH shared write targets back to the pipeline — the Debug
        pages' write pointer and the run-log folder. Called before the
        auto-advance timer fires, so the pipeline's next step writes its
        conversation, code and artifacts to the pipeline's own destinations even
        while the baseline view is still the one on screen.
        """
        self._debugWriteContext = self.PIPELINE_DEBUG_CONTEXT
        self._restorePipelineLogDir()
        self._setBaselineRunUiEnabled(True)
        self._syncBaselineSendButton()
        if advanced:
            return
        runtime = getattr(self, "_workflowRuntime", None)
        if runtime is not None and runtime.session is not None:
            self._updateWorkflowPanel(runtime.state_for_ui())
        self._setReadyStatus()

    # ---------------------------------------------------------------- cleanup
    def _teardownBaselineMcp(self):
        server = getattr(self, "_baselineMcpServer", None)
        if server is not None:
            try:
                server.stop()
            except Exception:
                logger.debug("Baseline MCP teardown failed", exc_info=True)
        self._baselineMcpServer = None
        self._baselineActiveRun = None
        self._debugWriteContext = self.PIPELINE_DEBUG_CONTEXT
        self._restorePipelineLogDir()
