from .common import *


class WidgetStreamingMixin:
    def onSceneStartClose(self, caller, event):
        if self.logic:
            self.logic.pauseProcessing()

    def onSceneEndClose(self, caller, event):
        if self.logic:
            self.logic.resumeProcessing()
        # The extensions this runtime drives bound themselves to the scene that
        # was just closed, and it never enters their modules, so Slicer's own
        # `if self.parent.isEntered` recovery hook cannot re-bind them. Drop the
        # entered-module cache so the next step fires enter() again.
        try:
            self._invalidateInvisibleModuleEntries("scene closed")
        except Exception:
            logger.debug("Invisible module-entry invalidation failed", exc_info=True)
        # File > Close Scene deletes everything a running workflow was driving,
        # so the session cannot continue. Without this it stays "active", and
        # since an active workflow switches the prompt box and Send off -- and
        # there is no traditional turn to escape through -- the module would be
        # locked with no way back in.
        runtime = getattr(self, "_workflowRuntime", None)
        if runtime is not None and getattr(runtime, "session", None) is not None:
            try:
                self._resetGuidedSession(reason="scene_closed", announce=False)
            except Exception:
                logger.debug("Guided session reset on scene close failed", exc_info=True)

    # ------------------------------------------------------------------
    # Debug-view contexts
    #
    # The Debug section's two pages (Conversation = chatHistory, Generated Code
    # = codeDisplay) are shared by the real pipeline and by each comparison
    # baseline, but their content must never mix: a baseline's thinking and code
    # belong to that baseline alone, and the pipeline's belong to the pipeline.
    #
    # Two independent pointers do that:
    #   _debugContext       which buffer is DISPLAYED (the user's ⚖ toggle /
    #                       baseline selector picks this)
    #   _debugWriteContext  which buffer new content is WRITTEN to (the producer
    #                       currently running picks this)
    #
    # They are usually equal. They diverge exactly when a baseline run finishes
    # and hands control back to the pipeline's auto-advance while the baseline
    # view is still open: the pipeline's output then accumulates invisibly in
    # the "pipeline" buffer and appears intact the moment the user closes the
    # baseline section. `_chatEntriesHtml` and the two widgets always hold the
    # DISPLAYED buffer; the others are parked in `_debugBuffers` and swapped in
    # by _switchDebugContext.
    # ------------------------------------------------------------------
    PIPELINE_DEBUG_CONTEXT = "pipeline"

    def _debugBuffer(self, key):
        return self._debugBuffers.setdefault(key, {"entries": [], "code": ""})

    def _debugWriteIsVisible(self):
        return getattr(self, "_debugWriteContext", self.PIPELINE_DEBUG_CONTEXT) == \
            getattr(self, "_debugContext", self.PIPELINE_DEBUG_CONTEXT)

    def _debugWriteEntries(self):
        """The chat-entry list new content must be appended to."""
        if self._debugWriteIsVisible():
            return self._chatEntriesHtml
        return self._debugBuffer(self._debugWriteContext)["entries"]

    def _renderChatIfVisible(self, with_streaming=False):
        """Repaint the Conversation page, but only for the displayed buffer."""
        if not self._debugWriteIsVisible():
            return
        html = ''.join(self._chatEntriesHtml)
        if with_streaming:
            html += self._buildStreamingEntryHtml()
        self._setChatHtml(html)

    def _setGeneratedCode(self, code):
        """Write the Generated Code page for the CURRENT write context."""
        text = str(code or "")
        if not self._debugWriteIsVisible():
            self._debugBuffer(self._debugWriteContext)["code"] = text
            return
        try:
            self.codeDisplay.setPlainText(text)
        except Exception:
            logger.debug("Generated-code display write failed", exc_info=True)

    def _switchDebugContext(self, key, banner_html=""):
        """Show a different Debug buffer, stashing the current one intact."""
        key = key or self.PIPELINE_DEBUG_CONTEXT
        if key == getattr(self, "_debugContext", self.PIPELINE_DEBUG_CONTEXT):
            return
        current = self._debugBuffer(self._debugContext)
        current["entries"] = list(self._chatEntriesHtml)
        try:
            current["code"] = self.codeDisplay.toPlainText()
        except Exception:
            logger.debug("Generated-code stash failed", exc_info=True)

        target = self._debugBuffer(key)
        if banner_html and not target["entries"]:
            target["entries"].append(banner_html)
        self._chatEntriesHtml = list(target["entries"])
        self._debugContext = key

        # Drop any half-rendered streaming fragment: it belongs to the buffer we
        # just left and would otherwise bleed into the one we are entering.
        self._streaming = False
        self._streamContent = ""
        self._streamReasoning = ""
        self._thinkingDisplayText = ""
        self._thinkingDisplayed = False

        self._setChatHtml(''.join(self._chatEntriesHtml))
        try:
            self.codeDisplay.setPlainText(target["code"])
        except Exception:
            logger.debug("Generated-code restore failed", exc_info=True)

    # ------------------------------------------------------------------
    # Streaming chat display helpers
    # ------------------------------------------------------------------
    def _setChatHtml(self, html):
        """Replace the chat box contents and keep it scrolled to the bottom."""
        self.chatHistory.setHtml(html)
        scrollbar = self.chatHistory.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum)

    def _buildStreamingEntryHtml(self):
        """Build HTML for the current streaming assistant entry."""
        timestamp = getattr(self, '_streamTimestamp', '')
        parts = []

        # Thinking section — shown during streaming, hidden after thinking_done
        if getattr(self, '_thinkingDisplayed', False) and self._thinkingDisplayText:
            escaped = self.escapeHtml(self._thinkingDisplayText).replace(chr(10), '<br>')
            # Truncate display to last ~2000 chars to avoid UI lag
            if len(escaped) > 2000:
                escaped = '...' + escaped[-2000:]
            parts.append(
                f'<div style="margin-left: 10px; margin-top: 5px; padding: 8px; '
                f'background-color: #f5f5f0; border-left: 3px solid #ccc; '
                f'color: #888; font-style: italic; max-height: 300px; overflow-y: auto;">'
                f'{escaped}</div>'
            )

        # Content section
        if self._streamContent:
            escaped_content = self.escapeHtml(self._streamContent).replace(chr(10), '<br>')
            parts.append(
                f'<div style="margin-left: 10px; margin-top: 5px;">{escaped_content}</div>'
            )

        if not parts:
            parts.append('<div style="margin-left: 10px; margin-top: 5px; color: #aaa;">...</div>')

        body = ''.join(parts)
        return (
            f'<div style="margin: 10px 0;">'
            f'<span style="color: #999; font-size: 10px;">[{timestamp}]</span> '
            f'<span style="color: #009900; font-weight: bold;">Assistant:</span>'
            f'{body}'
            f'</div>'
            f'<hr style="border: none; border-top: 1px solid #eee; margin: 5px 0;">'
        )

    def _renderStreamingEntry(self):
        """Re-render the current streaming assistant entry in the chat box."""
        if not hasattr(self, 'chatHistory') or self.chatHistory is None:
            return
        self._renderChatIfVisible(with_streaming=True)

    def _updateThinkingTimer(self):
        """Update the thinking timer display every 100ms."""
        if self._thinkingStartTime is not None:
            import time
            elapsed = time.time() - self._thinkingStartTime
            self.thinkingTimerLabel.text = f"⏱ {elapsed:.1f}s"

    def _startThinkingTimer(self):
        """Start the thinking timer."""
        import time
        self._thinkingStartTime = time.time()
        self.thinkingTimerLabel.text = "⏱ 0.0s"
        self._thinkingTimer.start()

    def _stopThinkingTimer(self, final_status=None):
        """Stop the thinking timer and show final elapsed time."""
        self._thinkingTimer.stop()
        if self._thinkingStartTime is not None:
            import time
            elapsed = time.time() - self._thinkingStartTime
            if final_status:
                self.thinkingTimerLabel.text = f"⏱ {final_status} {elapsed:.1f}s"
            else:
                self.thinkingTimerLabel.text = f"⏱ {elapsed:.1f}s"
        self._thinkingStartTime = None

    def _setAgentStatus(self, role, status):
        """Show current role-composed agent phase in the existing status label."""
        self._currentAgentRole = role or "Agent"
        if hasattr(self, 'statusLabel') and self.statusLabel is not None:
            # Truncate very long status text so the QLabel doesn't force the panel wide
            truncated = status[:80] + "..." if len(status) > 80 else status
            self.statusLabel.text = f"{self._currentAgentRole}: {truncated}"
        if (
            getattr(self, "_taskWorkflowPanelActive", False)
            and str(role or "") != "Workflow"
            and not (self._workflowRuntime and self._workflowRuntime.has_active_workflow())
        ):
            self._updateTraditionalTaskPanel(role, status)

    # ------------------------------------------------------------------
    # Free-text input availability
    #
    # In the guided step-by-step pipeline every step is dispatched by the
    # runtime and driven from the workflow panel's own controls -- the user
    # never needs to type. The prompt box and Send are therefore switched off
    # for the duration of a generated-CLI workflow, and switched back on when
    # baseline mode is engaged (the ⚖ button), which is exactly the mode that
    # needs them: the baselines take their prompt in that same box.
    #
    # Every site that ENABLES Send goes through _setSendEnabled so the gate
    # cannot be bypassed; the sites that disable it are left alone, since
    # disabling is always safe.
    # ------------------------------------------------------------------
    def _guidedWorkflowOwnsInput(self):
        """True while a guided workflow is driving and no baseline is engaged.

        Keyed on ENGAGED, not on the raw toggle: on a step that cannot take a
        baseline the selector row is hidden, so the input row must go back to
        the workflow rather than sit enabled with nothing to drive.
        """
        if self._baselineEngaged():
            return False
        runtime = getattr(self, "_workflowRuntime", None)
        try:
            return bool(runtime and runtime.has_active_workflow())
        except Exception:
            return False

    def _setSendEnabled(self, enabled):
        """Single funnel for the Send button's enabled state."""
        guided = self._guidedWorkflowOwnsInput()
        try:
            self.sendButton.setEnabled(bool(enabled) and not guided)
        except Exception:
            logger.debug("Send enable failed", exc_info=True)
        self._refreshPromptAvailability(guided)

    def _refreshPromptAvailability(self, guided=None):
        """Grey out the prompt box exactly while the guided workflow owns input.

        Kept independent of Send's transient state: during a normal turn Send is
        disabled but the user may still type ahead, so the box follows only the
        guided/baseline gate.
        """
        if guided is None:
            guided = self._guidedWorkflowOwnsInput()
        box = getattr(self, "promptInput", None)
        if box is None:
            return
        try:
            box.setEnabled(not guided)
            box.setToolTip(
                "The guided workflow is driving these steps — use the panel's "
                "controls, or press ⚖ to run a comparison baseline here."
                if guided else ""
            )
        except Exception:
            logger.debug("Prompt availability refresh failed", exc_info=True)

    def _refreshInputAvailability(self):
        """Re-apply the gate after any workflow/baseline state change."""
        if getattr(self, "promptInput", None) is None or getattr(self, "sendButton", None) is None:
            return
        guided = self._guidedWorkflowOwnsInput()
        self._refreshPromptAvailability(guided)
        if guided:
            try:
                self.sendButton.setEnabled(False)
            except Exception:
                logger.debug("Send disable failed", exc_info=True)
        elif not getattr(self, "_streaming", False) and not self._baselineBusy():
            # Not guided and nothing in flight: Send follows the prompt box,
            # except in baseline mode where some producers need no prompt.
            self._setSendEnabled(bool(self.promptInput.toPlainText().strip())
                                 or self._baselineEngaged())

    def _setReadyStatus(self):
        """Reset status label after a turn finishes or is cancelled."""
        self._currentAgentRole = "Idle"
        if hasattr(self, 'statusLabel') and self.statusLabel is not None:
            self.statusLabel.text = "Ready"
        if (
            getattr(self, "_taskWorkflowPanelActive", False)
            and not (self._workflowRuntime and self._workflowRuntime.has_active_workflow())
        ):
            self._updateWorkflowPanel({
                "active": True,
                "mode": "task",
                "workflow_title": "Task",
                "status": "Done",
                "description": "Task completed.",
                "instructions": "Generated code and execution details are available in Debug.",
                "total_steps": 0,
                "can_done": False,
                "can_skip": False,
            })
            self._taskWorkflowPanelActive = False

    def _updateTraditionalTaskPanel(self, role, status):
        """Show compact progress for traditional one-shot tasks."""
        role_text = str(role or "")
        status_text = str(status or "")
        phase = "Planning"
        if "fail" in status_text.lower() or "error" in status_text.lower():
            phase = "Failed"
        elif role_text == "Retriever":
            phase = "Searching"
        elif role_text in ("Executor", "Safety Critic", "Verifier", "Repairer"):
            phase = "Executing"
        self._updateWorkflowPanel({
            "active": True,
            "mode": "task",
            "workflow_title": "Task",
            "status": phase,
            "description": status_text,
            "instructions": "",
            "total_steps": 0,
            "can_done": False,
            "can_skip": False,
        })

    def _autoAdvanceNextStep(self, next_step, epoch=None):
        """Auto-advance to the next workflow step after an automated step completes.

        EVERY step is opened by dispatch, whatever its operation type and whether or
        not it is optional. An earlier version short-circuited here for an optional
        step that was not an ``extension_op`` / ``slicer_op``, hand-building a
        Done/Skip panel instead of dispatching. That skipped the step's OPENING
        action, so the user's only exits sent its COMPLETION actions ("proceed" /
        "skip") to a step that had never started -- which silently corrupted two
        step types: a ``branch_op`` never rendered its real question or its Yes/No
        choices (and "proceed" recorded an empty choice, entering the optional body
        without asking, with the on-accept action never attached), and a
        ``user_interaction`` ran its POST template though the PRE template had never
        created the markup node ("Node not found for step ...").

        Dispatch already provides everything the short-circuit did: the runtime's own
        panel offers Skip for exactly the optional steps (``can_skip``), offers Done
        when the step is genuinely waiting on the user, and additionally renders the
        step's real controls. Optionality is a property of the step the runtime
        presents, not a reason to avoid presenting it.

        Always reached through a QTimer, which cannot be cancelled once armed, so
        it re-checks that the session it was scheduled for is still the live one.
        """
        if not self._guidedSessionAlive(epoch):
            return
        step_id = next_step.get("step_id", "")
        self._runWorkflowStepDirect(step_id, "start")

    def _guidedSessionAlive(self, epoch=None):
        """False once the session that scheduled this work has been reset.

        ``epoch is None`` means the caller predates the fence (or is not tied to
        a session), so it passes -- the guard only ever stops work whose origin
        is known to be stale.
        """
        if epoch is None:
            return True
        return epoch == getattr(self, "_guidedSessionEpoch", 0)

    def _workflowRuntimeState(self):
        """Return compact workflow state for turn routing."""
        if self._workflowRuntime:
            return self._workflowRuntime.state_for_router()
        return {"active": False}

    def _workflowStepMarkerKey(self, step_info):
        """Return a stable key for comparing cached workflow dispatch results."""
        if not isinstance(step_info, dict):
            return None
        return (
            step_info.get("tool"),
            step_info.get("step_id"),
            step_info.get("type"),
        )

    def _sameWorkflowStepMarker(self, first, second):
        """Return True when two cached workflow results represent the same step."""
        first_key = self._workflowStepMarkerKey(first)
        second_key = self._workflowStepMarkerKey(second)
        return bool(first_key and first_key == second_key)

    def _clearWorkflowResultMarkers(self):
        """Clear cached CLI tool results that are only valid for the current turn."""
        if not self.logic:
            return
        if hasattr(self.logic, "_lastInteractiveStep"):
            self.logic._lastInteractiveStep = None
        if hasattr(self.logic, "_lastWorkflowStep"):
            self.logic._lastWorkflowStep = None

    def _clearCompletedWorkflowState(self, clear_replay=False):
        """Drop transient generated-CLI workflow state after completion or cancel.

        The replay timeline (and its scene snapshots) is KEPT after a normal
        completion so the user can still rewind and re-run from any step. It is
        only torn down on an explicit cancel (``clear_replay=True``) or when a
        new workflow session starts.
        """
        # Seal the run manifest: `cancelled` when the user stopped it, otherwise
        # `completed`. Left as `running` if we never get here (a Slicer crash),
        # which is itself the honest record of what happened.
        #
        # FIRST SEAL WINS. The manifest object outlives its run -- nothing clears
        # `_currentRunManifest` when one ends -- so pressing Exit after a normal
        # completion re-enters here with clear_replay=True on the SAME manifest,
        # and without this guard would relabel a completed procedure "cancelled"
        # and reset its finished/seconds to the moment the panel was closed.
        # Exiting a finished run to start the next one is the ordinary path, so
        # this would have mislabelled most successful runs on disk.
        manifest = self._runManifest()
        if manifest is not None and manifest.data.get("status", "running") == "running":
            try:
                manifest.set_totals(
                    tokens=getattr(self, "_currentTurnTokens", 0),
                    cost=round(getattr(self, "_currentTurnCost", 0.0), 6),
                )
                manifest.finish("cancelled" if clear_replay else "completed")
            except Exception:
                logger.debug("Run manifest finish failed", exc_info=True)
        self._setStepLogContext("")
        self._clearWorkflowResultMarkers()
        self._currentWorkflowStepInfo = None
        self._waitingForUser = False
        self._autoAdvanceWorkflowStep = None
        self._activeWorkflowId = None
        self._taskWorkflowPanelActive = False
        if clear_replay:
            try:
                if self._workflowRuntime:
                    self._workflowRuntime.clear_checkpoints()
            except Exception:
                logger.debug("Clearing replay checkpoints failed", exc_info=True)
            self._updateReplayControls({})

    def _registerWorkflowRuntimeResult(self, step_info):
        """Ensure generated CLI workflow results are tracked by the runtime."""
        if not isinstance(step_info, dict) or not step_info.get("tool"):
            return
        try:
            if not self._workflowRuntime:
                from SlicerAIAgentLib.WorkflowRuntime import WorkflowRuntime
                self._workflowRuntime = WorkflowRuntime(log_dir=self._getCurrentLogDir())
            self._workflowRuntime.log_dir = self._getCurrentLogDir()
            session = self._workflowRuntime.start_from_result(step_info)
            if session:
                self._taskWorkflowPanelActive = False
                if session.workflow_id not in self._announcedWorkflowIds:
                    self._announcedWorkflowIds.add(session.workflow_id)
                    self.appendToChat("System", f"Workflow started: {session.extension_name}.")
                self._activeWorkflowId = session.workflow_id
                self._updateWorkflowPanel(step_info)
        except Exception as exc:
            logger.warning(f"Failed to register workflow runtime result: {exc}")

    def _beginWorkflowRuntimeTurn(self, prompt, route):
        """Initialize compact per-turn state for a deterministic CLI step.

        A workflow run is ONE run folder. Chat turns that drive an already-active
        workflow ("done", a choice, "yes") keep writing into it rather than each
        opening a new one — otherwise a 33-step procedure with ten interactions
        scattered itself across eleven identically-named folders. The role trace
        is likewise not reset, so the run root's trace is the whole procedure.
        """
        import time
        from SlicerAIAgentLib import RunLog
        active = bool(self._workflowRuntime and self._workflowRuntime.has_active_workflow())
        if not (active and self._currentLogDir):
            session = getattr(self._workflowRuntime, "session", None)
            self._currentLogDir = self._createRunLogDir(
                getattr(self, "_currentTurn", 1),
                condition=RunLog.CONDITION_PIPELINE,
                extension=getattr(session, "extension_name", "") or "",
            )
            self._roleTrace = []
        if self.logic and self.logic.llmClient:
            self.logic.llmClient.setDebugOutputDir(self._currentLogDir)
        if self._workflowRuntime:
            self._workflowRuntime.log_dir = self._currentLogDir
        self._timing = {
            "turn_start": time.time(),
            "prompt": prompt,
            "mode": "generated_cli_workflow",
            "route": getattr(route, "route_type", ""),
            "route_reason": getattr(route, "reason", ""),
            "retrieval_timing": {
                "skipped": True,
                "skip_reason": "deterministic_generated_cli_workflow",
            },
        }
        self._recordRoleEvent("Observer", "received_workflow_control_prompt", {
            "prompt_length": len(prompt),
            "route": getattr(route, "route_type", ""),
            "action": getattr(route, "action", None),
            "step_id": getattr(route, "step_id", None),
        })

    def _handleDirectWorkflowTurnIfNeeded(self, prompt):
        """Resolve active generated-workflow chat turns with a narrow LLM call."""
        from SlicerAIAgentLib.TurnRouter import (
            ROUTE_WORKFLOW_CONFLICT,
            ROUTE_WORKFLOW_CONTROL,
            ROUTE_WORKFLOW_UNRESOLVED,
        )
        from SlicerAIAgentLib.WorkflowIntentResolver import WorkflowIntentResolver

        state = self._workflowRuntimeState()
        if not state.get("active"):
            return False
        resolver = WorkflowIntentResolver(
            self.logic.llmClient if self.logic else None
        )
        route = resolver.resolve(
            prompt,
            state,
            getattr(self, "_currentWorkflowStepInfo", None) or {},
        )
        from SlicerAIAgentLib.WorkflowRouter import GUIDED_ONLY_MODE

        if route.route_type == ROUTE_WORKFLOW_CONFLICT:
            # Queueing exists to defer a separate task until the workflow ends.
            # Under guided-only there is nothing to defer it TO -- the queue is
            # drained by replaying it as a traditional turn -- so accepting it
            # would promise an answer that never comes. Refuse it now instead.
            if GUIDED_ONLY_MODE:
                self._refuseUnsupportedRequest(prompt, {"kind": "workflow_active"})
                return True
            count = 0
            if self._workflowRuntime:
                count = self._workflowRuntime.queue_traditional_prompt(prompt)
            self.appendToChat(
                "System",
                "A generated CLI workflow is active, so I queued this request "
                f"until the workflow finishes. Queued requests: {count}.",
            )
            queued_state = self._workflowRuntime.state_for_ui() if self._workflowRuntime else {}
            if queued_state:
                queued_state["status"] = "Queued request"
                self._updateWorkflowPanel(queued_state)
            self._setReadyStatus()
            self._setSendEnabled(True)
            return True

        if route.route_type == ROUTE_WORKFLOW_UNRESOLVED:
            self.appendToChat(
                "System",
                "I could not confidently map that message to an allowed workflow "
                f"action, so the workflow state was not changed. {route.reason} "
                "Use the workflow panel's own controls, or press Exit at the "
                "bottom of the panel to close and reset the workflow.",
            )
            self._setReadyStatus()
            self._setSendEnabled(True)
            return True

        if route.route_type != ROUTE_WORKFLOW_CONTROL:
            # Currently unreachable (the only other route type is TRADITIONAL,
            # which the resolver returns only for an inactive workflow, already
            # excluded above). Refused rather than passed through, so a route
            # type added later cannot silently re-open the traditional pipeline.
            if GUIDED_ONLY_MODE:
                self._refuseUnsupportedRequest(prompt, {"kind": "workflow_active"})
                return True
            return False

        self.sendButton.setEnabled(False)
        self._beginWorkflowRuntimeTurn(prompt, route)
        action = route.action or "start"
        args = {}
        if action == "choice_made":
            args["choice_value"] = route.choice_value
        elif action == "proceed" and state.get("status") != "waiting_for_user":
            action = "start"
        self._runWorkflowStepDirect(route.step_id, action, args=args)
        return True

    def _handleWorkflowRouterTurnIfNeeded(self, prompt):
        """Enter a guided workflow directly when the opening request names one.

        Every step of a generated-CLI workflow is dispatched by the runtime, so
        the ONLY decision the model makes on the first turn is which workflow the
        request means. Making that decision through the full agent turn costs
        ~140,000 characters of system prompt (the coding manual, dense-retrieval
        snippets and all nine CLI prompt fragments) to produce one tool call.
        The router does it with ~6,000.

        Returns True when the turn was handled here. Every other outcome --
        router disabled, no workflows loaded, no key, no match, low confidence,
        API failure -- returns False.

        What the caller does with that False is the difference between the two
        modes. Historically it ran the full agent turn, so the router could only
        ever SKIP work. Under ``GUIDED_ONLY_MODE`` there is no turn to fall back
        to and the False becomes a refusal, so each one now also records WHY in
        ``_lastRouterRejection`` -- seven distinct causes that a single "not
        supported" string would make undiagnosable, several of which mean the
        install is misconfigured rather than the request unsupported.
        """
        from SlicerAIAgentLib.WorkflowRouter import ROUTER_ENABLED, WorkflowRouter

        self._lastRouterRejection = None
        if not ROUTER_ENABLED:
            self._lastRouterRejection = {"kind": "router_disabled"}
            return False
        if not (self.logic and self.logic.llmClient):
            self._lastRouterRejection = {"kind": "no_client"}
            return False
        # An active workflow is handled by _handleDirectWorkflowTurnIfNeeded.
        if self._workflowRuntime and self._workflowRuntime.has_active_workflow():
            self._lastRouterRejection = {"kind": "workflow_active"}
            return False

        router = WorkflowRouter(self.logic.llmClient)
        unavailable = router.unavailable_reason()
        if unavailable:
            self._lastRouterRejection = {"kind": unavailable}
            return False

        self._setAgentStatus("Router", "Choosing workflow...")
        slicer.app.processEvents()
        decision = router.resolve(prompt)

        if not decision.matched:
            self._lastRouterRejection = {
                "kind": "router_error" if decision.error else "not_matched",
                "confidence": decision.confidence,
                "reason": decision.reason or decision.error,
                "rejected_extension": decision.rejected_extension,
                "error": decision.error,
            }
            # Nothing is recorded to the role trace here: the turn that runs
            # instead (the full agent turn, or the refusal) opens its own folder
            # and clears the trace, and this decision belongs to that turn's
            # story, which _timing['router_declined'] carries instead.
            logger.info(
                "Workflow router declined (confidence=%.2f, reason=%s)",
                decision.confidence, decision.reason or decision.error,
            )
            # Whichever turn runs instead creates the folder; hand it the router
            # so the declined call is recorded there rather than lost. Under
            # GUIDED_ONLY_MODE that turn is _refuseUnsupportedRequest, which is
            # the only remaining writer of this evidence.
            self._lastRouterDecision = decision
            self._lastRouter = router
            return False

        # Establish this turn's log dir BEFORE the session starts, so the
        # runtime's own workflow_started event lands in the right run folder.
        # This also resets _roleTrace, so the decision event is recorded after.
        self._beginWorkflowRouterTurn(prompt, decision)
        # Now that the folder exists (it is named after the decision), flush the
        # routing call into it. This is the ONLY model call a guided run makes,
        # so without it the run has no record of the evidence behind its choice.
        router.write_artifacts(self._currentLogDir)
        self._recordRoleEvent("Router", "workflow_route_decided", {
            "extension": decision.extension,
            "confidence": decision.confidence,
            "reason": decision.reason,
            "seconds": decision.seconds,
            "prompt_chars": decision.prompt_chars,
            "tokens": decision.tokens,
        })
        try:
            if not self._workflowRuntime:
                from SlicerAIAgentLib.WorkflowRuntime import WorkflowRuntime
                self._workflowRuntime = WorkflowRuntime(log_dir=self._currentLogDir)
            self._workflowRuntime.log_dir = self._currentLogDir
            session = self._workflowRuntime.start_for_extension(decision.extension)
        except Exception as exc:
            logger.warning("Workflow router could not start %s: %s", decision.extension, exc)
            self._recordRoleEvent("Router", "workflow_start_failed", {
                "extension": decision.extension,
                "error": str(exc),
            })
            self._lastRouterRejection = {
                "kind": "start_failed",
                "rejected_extension": decision.extension,
                "reason": str(exc),
            }
            return False

        first_step = getattr(session, "current_step", None)
        if not first_step:
            # A graph with no dependency-satisfiable first step is broken; drop
            # the half-started session so has_active_workflow() stays honest.
            logger.warning(
                "Workflow %s has no runnable first step", decision.extension,
            )
            self._workflowRuntime.session = None
            self._lastRouterRejection = {
                "kind": "no_first_step",
                "rejected_extension": decision.extension,
            }
            return False

        # Claim the announcement so _registerWorkflowRuntimeResult does not add a
        # second, less informative "Workflow started" line for the same session.
        self._announcedWorkflowIds.add(session.workflow_id)
        self.appendToChat(
            "System",
            f"Entering the {decision.extension} guided workflow "
            f"(router confidence {decision.confidence:.2f}).",
        )
        self.sendButton.setEnabled(False)
        self._runWorkflowStepDirect(first_step, "start")
        return True

    # ------------------------------------------------------------------
    # Guided-only refusal
    #
    # With WorkflowRouter.GUIDED_ONLY_MODE on, a request the router cannot place
    # is refused instead of being handed to the full agent turn. The refusal is
    # a modal dialog because it ENDS the request: a chat line alone would let an
    # unanswered prompt scroll away inside a collapsed Debug group while the user
    # waits for a scene that is never going to change.
    #
    # Seven causes reach here and only two of them are "your request is not
    # covered" -- the rest mean the install is unconfigured or a workflow graph
    # is broken. The full agent turn used to paper over all seven identically,
    # which is exactly why they have to be told apart now.
    # ------------------------------------------------------------------
    _REFUSAL_TITLE = "Guided workflow required"

    def _refusalMessage(self, rejection):
        """``(headline, body, is_config_problem)`` for one refusal cause."""
        rejection = rejection or {}
        kind = rejection.get("kind") or "not_matched"
        named = rejection.get("rejected_extension") or ""
        reason = str(rejection.get("reason") or "")
        if named:
            from SlicerAIAgentLib.WorkflowRouter import display_name
            named = display_name(named)

        if kind == "router_disabled":
            return (
                "The guided workflow router is switched off.",
                "WorkflowRouter.ROUTER_ENABLED is False, so no request can be "
                "routed to a workflow, and this runtime supports nothing else. "
                "Set it back to True to use the agent.",
                True,
            )
        if kind == "no_client":
            return (
                "The AI provider is not configured.",
                "Open the Settings section, choose a provider and model, and "
                "save the settings before sending a request.",
                True,
            )
        if kind == "no_api_key":
            return (
                "No API key is configured.",
                "The router needs one model call to decide which procedure your "
                "request means. Enter an API key in the Settings section and "
                "save it, then send the request again.",
                True,
            )
        if kind == "no_workflows":
            return (
                "No guided workflows are installed.",
                "This runtime only runs generated extension CLI workflows, and "
                "none were found under Resources/extension_CLI. Use the "
                "Extension CLI generator to analyze an extension first.",
                True,
            )
        if kind == "workflow_active":
            return (
                "A guided workflow is already running.",
                "Finish the current procedure, or press Exit at the bottom of "
                "the workflow panel to close and reset it, before making a new "
                "request.",
                False,
            )
        if kind == "router_error":
            return (
                "The routing call failed, so the request could not be placed.",
                (reason or "The provider returned an error.")
                + "\n\nCheck the API key, the base URL and the network, then try "
                "again.",
                True,
            )
        if kind == "start_failed":
            return (
                f"The {named or 'matched'} workflow could not be started.",
                (reason or "The workflow package could not be loaded.")
                + "\n\nRe-generate this extension's CLI, then try again.",
                True,
            )
        if kind == "no_first_step":
            return (
                f"The {named or 'matched'} workflow has no runnable first step.",
                "Its workflow graph has no step whose dependencies can be "
                "satisfied, which means the generated package is broken. "
                "Re-generate this extension's CLI.",
                True,
            )
        # not_matched: the ordinary case, and the only one that is about the
        # request rather than the install.
        body = (
            "This runtime only carries out the guided, step-by-step procedures "
            "listed below — it does not write free-form Slicer code."
        )
        if named:
            body += (
                f"\n\nThe closest match was {named}, but not confidently enough "
                f"to enter a whole procedure on it"
            )
            confidence = rejection.get("confidence")
            if isinstance(confidence, (int, float)):
                body += f" (confidence {float(confidence):.2f})"
            body += ". If that is the procedure you meant, say so by name."
        elif reason:
            body += f"\n\nRouter: {reason}"
        return ("That request is not one of the supported procedures.", body, False)

    def _showGuidedOnlyRefusal(self, headline, body, config_problem=False):
        """Modal 'not supported' notice. Main thread only; never raises."""
        details = ""
        try:
            from SlicerAIAgentLib.WorkflowRouter import describe_available_workflows
            lines = describe_available_workflows()
            if lines:
                details = "Supported procedures:\n" + "\n".join(lines)
        except Exception:
            logger.debug("Workflow catalog unavailable for refusal dialog", exc_info=True)
        try:
            box = qt.QMessageBox(slicer.util.mainWindow())
            box.setWindowTitle(self._REFUSAL_TITLE)
            box.setIcon(qt.QMessageBox.Critical if config_problem else qt.QMessageBox.Information)
            box.setText(headline)
            box.setInformativeText(body)
            if details:
                box.setDetailedText(details)
            box.setStandardButtons(qt.QMessageBox.Ok)
            box.exec_()
        except Exception:
            # A dialog that cannot open must not swallow the refusal itself.
            logger.warning("Refusal dialog failed; message was: %s / %s", headline, body)

    def _refuseUnsupportedRequest(self, prompt, rejection=None):
        """End an unsupported request: log it, say why, hand the prompt back.

        The prompt text is restored into the box rather than discarded. The
        request was never consumed -- rephrasing it in the procedure's own words
        is the usual way past a near miss -- so making the user retype it would
        punish exactly the case the dialog is asking them to retry.
        """
        rejection = rejection or getattr(self, "_lastRouterRejection", None) or {}
        headline, body, config_problem = self._refusalMessage(rejection)
        self._recordRefusedRequest(prompt, rejection, headline)
        self.appendToChat("System", f"{headline} {body}")
        # All three belong to the turn just closed; a later turn must not adopt
        # this one's routing call or its rejection.
        self._lastRouterRejection = None
        self._lastRouter = None
        self._lastRouterDecision = None
        self._setReadyStatus()
        self._setSendEnabled(True)
        try:
            if self.promptInput is not None and not self.promptInput.toPlainText().strip():
                self.promptInput.setPlainText(prompt)
        except Exception:
            logger.debug("Prompt restore after refusal failed", exc_info=True)
        self._refreshInputAvailability()
        self._showGuidedOnlyRefusal(headline, body, config_problem)

    def _recordRefusedRequest(self, prompt, rejection, headline):
        """Persist a refused turn under ``logs/<stamp>_pipeline_refused/``.

        A refusal is now the single most common outcome of the runtime, and it
        was the only outcome with no artifact at all: the declined router call
        used to be flushed by the full agent turn's folder, which no longer
        exists. Leaving it unlogged would put a growing gap between the prompts
        a user typed and the runs ``scripts/collect_runs.py`` can see.

        A refusal raised while a workflow is RUNNING gets no folder of its own:
        opening one would repoint ``_currentLogDir`` and replace the manifest of
        the run in progress, so the rest of that procedure would log into the
        wrong place. It is recorded as an event of the run it interrupted.
        """
        runtime = getattr(self, "_workflowRuntime", None)
        if runtime is not None and runtime.has_active_workflow():
            self._recordRoleEvent("Router", "request_refused_during_workflow", {
                "prompt_length": len(prompt or ""),
                "kind": (rejection or {}).get("kind"),
            })
            return
        try:
            from SlicerAIAgentLib import RunLog
            # The prompt is written by _createRunLogDir itself, from
            # _lastUserPrompt -- passing it again would collide on the keyword.
            log_dir = self._createRunLogDir(
                getattr(self, "_currentTurn", 1),
                condition=RunLog.CONDITION_PIPELINE,
                extension="refused",
                refusal={"headline": headline, **(rejection or {})},
            )
            self._currentLogDir = log_dir
            router = getattr(self, "_lastRouter", None)
            if router is not None:
                router.write_artifacts(log_dir)
            manifest = self._runManifest()
            if manifest is not None:
                manifest.finish("refused")
        except Exception:
            logger.debug("Refused-request logging failed", exc_info=True)

    def _beginWorkflowRouterTurn(self, prompt, decision):
        """Per-turn bookkeeping for a router-dispatched workflow start."""
        import time
        from SlicerAIAgentLib import RunLog
        self._lastUserPrompt = prompt
        # Names the folder after the procedure it runs, e.g.
        # logs/20260730_143210_pipeline_BoneReconstructionPlanner/
        self._currentLogDir = self._createRunLogDir(
            getattr(self, "_currentTurn", 1),
            condition=RunLog.CONDITION_PIPELINE,
            extension=decision.extension,
            # Anchors "total run time" to the Send click, not to this moment --
            # the routing call has already happened by the time we get here.
            send_clicked_epoch=getattr(self, "_sendClickedEpoch", None),
            router={
                "extension": decision.extension,
                "confidence": decision.confidence,
                "reason": decision.reason,
                "seconds": decision.seconds,
                "prompt_chars": decision.prompt_chars,
                "tokens": decision.tokens,
            },
        )
        if self.logic and self.logic.llmClient:
            self.logic.llmClient.setDebugOutputDir(self._currentLogDir)
        if self._workflowRuntime:
            self._workflowRuntime.log_dir = self._currentLogDir
        self._roleTrace = []
        self._timing = {
            "turn_start": time.time(),
            "prompt": prompt,
            "mode": "workflow_router_start",
            "route": "workflow_router",
            "route_reason": decision.reason,
            # The headline efficiency number for this path: what the routing
            # decision actually cost, against the full agent turn it replaced.
            "router": {
                "extension": decision.extension,
                "confidence": decision.confidence,
                "seconds": decision.seconds,
                "prompt_chars": decision.prompt_chars,
                "tokens": decision.tokens,
            },
            "retrieval_timing": {
                "skipped": True,
                "skip_reason": "workflow_router_start",
            },
        }

    def _buildWorkflowAgentPlan(self, result):
        """Create a valid lightweight plan for deterministic generated code."""
        step_id = result.get("step_id", "workflow_step")
        action = result.get("explanation") or result.get("instruction") or f"Run generated CLI workflow step {step_id}"
        return {
            "summary": f"Execute generated CLI workflow step {step_id}.",
            "steps": [
                {
                    "action": action,
                    "confidence": "high",
                    "evidence": "Validated generated extension CLI template.",
                    "expected_scene_change": {"type": "not_checked"},
                }
            ],
            "risk_level": "low",
            "requires_confirmation": False,
            "unverified_assumptions": [],
        }

    def _runWorkflowStepDirect(self, step_id, action="start", args=None):
        """Dispatch a generated CLI workflow step directly and execute its code."""
        if not self._workflowRuntime:
            self.appendToChat("Error", "No active generated CLI workflow runtime.")
            self._setReadyStatus()
            self._setSendEnabled(True)
            return

        # Open this step's own artifact folder. Every artifact written from here
        # on (code, plan, execution, thinking, timing, corrections, and the LLM
        # client's prompt dumps) lands in it, so a 33-step workflow keeps 33
        # complete records instead of overwriting one.
        self._setStepLogContext(step_id)
        manifest = self._runManifest()
        if manifest is not None and step_id:
            meta = self._workflowRuntime._step_meta(step_id) if self._workflowRuntime else {}
            # open_step, not add_step: it stamps opened_epoch only the FIRST
            # time this step is dispatched, so the wall clock for a step the
            # user answers still starts when the picker appeared rather than
            # when they answered it.
            manifest.open_step(
                step_id,
                action=action,
                status="running",
                operation_type=(meta or {}).get("operation_type"),
                description=" ".join(str((meta or {}).get("description") or "").split()) or None,
            )

        self._setAgentStatus("Workflow", f"Running {step_id or 'current step'}...")
        if self._workflowRuntime and self._workflowRuntime.session:
            state = self._workflowRuntime.state_for_ui()
            state["status"] = "Running"
            self._updateWorkflowPanel(state)
        self._recordRoleEvent("Workflow", "dispatch_step_direct", {
            "step_id": step_id,
            "action": action,
        })
        result = self._workflowRuntime.run_step(step_id, action, args=args)
        if action == "choice_made":
            # The choice is now recorded; reflect a chosen scalar volume (e.g.
            # "Current Scalar Volume") in the slice views immediately. Guided
            # extensions normally do this through their own parameter-node sync,
            # which the agent does not drive reliably (the per-step module switch
            # is stripped to preserve interaction handles). We apply it the
            # extension-agnostic way — background layer only, never markup
            # handles/lock — so the chosen volume is shown.
            self._applyChosenVolumeBackground()
        self._handleWorkflowRuntimeResult(result)

    def _handleWorkflowRuntimeResult(self, result):
        """Handle a deterministic generated CLI dispatcher result."""
        if not isinstance(result, dict):
            self.appendToChat("Error", "Generated CLI workflow returned an invalid result.")
            self._setReadyStatus()
            self._setSendEnabled(True)
            return
        if result.get("error"):
            self.appendToChat("Error", result["error"])
            self._updateWorkflowPanel({
                "active": True,
                "workflow_title": "Workflow",
                "status": "Failed",
                "description": result["error"],
                "total_steps": 0,
                "can_done": False,
                "can_skip": False,
            })
            self._recordRoleEvent("Workflow", "dispatch_failed", {"error": result["error"]})
            self._saveRoleTraceToFile()
            self._setReadyStatus()
            self._setSendEnabled(True)
            return

        self._registerWorkflowRuntimeResult(result)
        self._currentWorkflowStepInfo = result
        # Every step gets a descriptor, not only the ones that produce code —
        # a user_choice or an interaction is part of the run's story too.
        self._saveStepDescriptorToFile(result)
        result_type = result.get("type")

        if result_type == "cancelled":
            # Same teardown as the Exit button, so the two ways a session can end
            # early cannot drift apart. (Reachable only from the runtime's own
            # "cancel" action now that the Cancel button is gone.)
            self.appendToChat("System", result.get("message", "Workflow cancelled."))
            self._recordRoleEvent("Workflow", "cancelled", {})
            self._saveRoleTraceToFile()
            self._resetGuidedSession(reason="runtime_cancel", announce=False)
            return

        if result_type == "user_choice":
            # Node selection is always manual: show the choice (a dropdown of
            # the matching scene nodes, built in _renderWorkflowChoices) and wait
            # for the user. No automatic LLM node matching.
            self._displayWorkflowChoice(result)
            self._recordRoleEvent("Workflow", "waiting_for_choice", {
                "step_id": result.get("step_id"),
            })
            self._saveRoleTraceToFile()
            self._setReadyStatus()
            self._setSendEnabled(True)
            return

        code = result.get("code") or result.get("pre_code") or result.get("post_code")
        if code:
            self.currentCode = code
            self.currentAgentPlan = self._buildWorkflowAgentPlan(result)
            self._setGeneratedCode(code)
            self._saveAgentPlanToFile(self.currentAgentPlan)
            self._saveGeneratedCodeToFile(code)
            self._recordRoleEvent("Programmer", "workflow_template_received", {
                "step_id": result.get("step_id"),
                "type": result_type,
                "code_chars": len(code),
            })
            self._autoExecuteCode()
            return

        # Pure control result, such as skip with no executable code.
        self._completeWorkflowResultWithoutCode(result)

    def _displayWorkflowChoice(self, step_info):
        """Show a generated CLI user-choice question (buttons / node dropdown)."""
        self._showWorkflowChoice(step_info)

    def _applyChosenVolumeBackground(self):
        """Show the active workflow's chosen scalar volume as the slice background.

        A guided extension keeps its slice background synced to a chosen "current
        volume" via a parameter-node observer wired in enter(). The agent cannot
        rely on that: the extension is never the active module (the per-step
        module switch is stripped so its exit() never hides the interaction
        handles), so the observer may not fire — and the extension's enter() can
        even default-select the first scalar volume (often the wrong one, e.g.
        the fibula). We therefore re-apply the recorded scalar-volume choice to
        the views ourselves, the extension-agnostic way: Slicer's slice-viewer
        layers, background layer only. This never touches markup handles or lock
        state, so the handle behavior is unaffected. Called both when a choice is
        made and after each workflow code step, so the chosen volume survives the
        extension's own enter()/processing churn. No-op when no scalar-volume
        choice is recorded; fail-open.
        """
        try:
            runtime = getattr(self, "_workflowRuntime", None)
            session = getattr(runtime, "session", None) if runtime else None
            ext_name = getattr(session, "extension_name", None) if session else None
            if not ext_name:
                return
            from SlicerAIAgentLib.extension_cli_loader.templates import _workflow_choices
            from SlicerAIAgentLib.extension_cli_loader.cache import get_validated_extensions
            choices = _workflow_choices.get(ext_name, {}) or {}
            if not choices:
                return
            metadata = (get_validated_extensions().get(ext_name) or {}).get("workflow_metadata", {}) or {}
            bindings = metadata.get("parameter_bindings", {}) or {}
            for role, value in choices.items():
                if not value:
                    continue
                # Only a scalar-volume choice drives the slice background.
                if (bindings.get(role) or {}).get("node_class") != "vtkMRMLScalarVolumeNode":
                    continue
                node = self._findSceneNodeByNameOrId(value, "vtkMRMLScalarVolumeNode")
                # Skip label maps (a ScalarVolume subclass) — not a background.
                if node is None or node.IsA("vtkMRMLLabelMapVolumeNode"):
                    continue
                # Apply and fit only when the background actually changes, so the
                # volume is optimally framed when first shown (matching the
                # extension's own resetSliceViews()) without resetting the user's
                # manual zoom/pan on the later re-assertions.
                if self._setSliceBackgroundIfChanged(node):
                    logger.info(
                        "[Workflow] Slice background set to chosen volume '%s' (views fit)",
                        node.GetName(),
                    )
                return
        except Exception:
            logger.debug("Applying chosen volume to slice display failed", exc_info=True)

    def _setSliceBackgroundIfChanged(self, node):
        """Set the slice background to ``node`` and fit the views when needed.

        Fits the field of view (reproducing the extension's resetSliceViews()
        framing) when the displayed background changes OR the layout changes —
        the latter because a layout switch reveals slice views (e.g. Green/Yellow
        in the Conventional layout) whose framing is stale. When the background
        and layout are both unchanged, the views are left alone, so a user's
        manual zoom/pan during a stable interactive step is preserved. Returns
        True when it applied a change.
        """
        layout_manager = slicer.app.layoutManager()
        if layout_manager is None:
            return False
        node_id = node.GetID()
        background_differs = False
        slice_logics = layout_manager.mrmlSliceLogics()
        for index in range(slice_logics.GetNumberOfItems()):
            slice_logic = slice_logics.GetItemAsObject(index)
            if slice_logic is None:
                continue
            composite_node = slice_logic.GetSliceCompositeNode()
            if composite_node is not None and composite_node.GetBackgroundVolumeID() != node_id:
                background_differs = True
                break
        try:
            layout_id = layout_manager.layout
        except Exception:
            layout_id = None
        # First call (attribute absent) counts as a layout change, so the initial
        # application always fits.
        layout_changed = getattr(self, "_lastSliceFitLayout", "__unset__") != layout_id
        if not (background_differs or layout_changed):
            return False
        slicer.util.setSliceViewerLayers(background=node, fit=True)
        self._lastSliceFitLayout = layout_id
        return True

    def _findSceneNodeByNameOrId(self, value, node_class):
        """Resolve a choice value (a node ID or name) to an MRML node."""
        try:
            node = slicer.mrmlScene.GetNodeByID(value)
            if node is not None:
                return node
        except Exception:
            pass
        try:
            nodes = slicer.mrmlScene.GetNodesByClass(node_class)
            for index in range(nodes.GetNumberOfItems()):
                node = nodes.GetItemAsObject(index)
                if node is not None and node.GetName() == value:
                    return node
        except Exception:
            pass
        return None

    def _completeWorkflowResultWithoutCode(self, result):
        """Advance deterministic workflow state for a no-code control result."""
        if self._workflowRuntime:
            result = self._workflowRuntime.handle_execution_result(
                result,
                {"success": True, "execution_time": 0.0, "output": ""},
            )
        next_step = result.get("next_step")
        # A step that produces no code (a skip, a branch decision, a choice whose
        # value only feeds later steps) completes HERE and nowhere else. Without
        # this it never left `running` in the manifest -- four steps of a
        # completed 27-step run were recorded that way -- and so had no wall
        # clock at all.
        #
        # Gated on the workflow actually having MOVED ON. This method is also
        # reached by a result that puts the step into a wait (an `interactive`
        # or `user_review` step with no pre-code): the step is on screen waiting
        # for Done, not finished, and stamping it complete here would end its
        # clock before the user has touched it.
        manifest = self._runManifest()
        step_id = str(result.get("step_id") or getattr(self, "_currentStepId", "") or "")
        if manifest is not None and step_id and (next_step or result.get("workflow_completed")):
            # No exec_seconds: no code ran, so the step must not be credited
            # with an execution. The report shows "-" in the exec column, which
            # is the honest answer for a review checkpoint or a skip.
            manifest.finish_step(step_id, status="ok")
        if result.get("workflow_completed"):
            self._updateWorkflowPanel(result)
            self.appendToChat("System", "Generated CLI workflow complete.")
            self._clearCompletedWorkflowState()
            self._flushQueuedWorkflowPrompts()
            self._setReadyStatus()
            self._setSendEnabled(True)
            return
        if next_step:
            self._updateWorkflowPanel(result)
            self._autoAdvanceWorkflowStep = next_step
            _epoch = getattr(self, "_guidedSessionEpoch", 0)
            qt.QTimer.singleShot(100, lambda: self._autoAdvanceNextStep(next_step, _epoch))
        else:
            self._setReadyStatus()
            self._setSendEnabled(True)

    def _flushQueuedWorkflowPrompts(self):
        """Replay queued traditional prompts after a generated CLI workflow ends.

        The one path in the whole widget that can start a turn with no user
        click (it writes the prompt box and fires Send on a timer), so under
        guided-only it is inert by construction: nothing is queued any more
        (``_handleDirectWorkflowTurnIfNeeded`` refuses instead), and anything
        left over from a session started before the flag flipped is dropped
        rather than replayed into a pipeline that no longer exists.
        """
        if not self._workflowRuntime:
            return
        from SlicerAIAgentLib.WorkflowRouter import GUIDED_ONLY_MODE
        if GUIDED_ONLY_MODE:
            self._workflowRuntime.pop_queued_prompts()
            return
        queued = self._workflowRuntime.pop_queued_prompts()
        if not queued:
            return
        prompt = "\n\n".join(queued)
        self.appendToChat(
            "System",
            f"Workflow finished. Running {len(queued)} queued traditional request(s).",
        )
        self.promptInput.setPlainText(prompt)
        qt.QTimer.singleShot(100, self.onSendButtonClicked)

    def _roleForStatus(self, status_text):
        """Map low-level API status messages to the composed role shown in the UI."""
        normalized = str(status_text or "").lower()
        if "retriev" in normalized or "search" in normalized or "read" in normalized or "tool" in normalized:
            return "Retriever"
        if "generat" in normalized:
            return "Planner/Programmer"
        if "think" in normalized:
            return "Retriever"
        if "validat" in normalized:
            return "Safety Critic"
        if "execut" in normalized:
            return "Executor"
        if "verify" in normalized:
            return "Verifier"
        if "correct" in normalized:
            return "Repairer"
        return self._currentAgentRole or "Agent"

    def _finalizeStreamingEntry(self):
        """Commit the current streaming assistant entry into chat history."""
        if self._streaming or self._streamReasoning or self._streamContent:
            self._debugWriteEntries().append(self._buildStreamingEntryHtml())
            self._renderChatIfVisible()

    def _drainStreamQueue(self):
        """Drain queued streaming events on the Qt main thread.

        Batches consecutive streaming deltas to avoid calling setHtml() hundreds
        of times per second, which blocks the main thread and delays complete/error
        events by tens of seconds.
        """
        # Collect all events currently in the queue
        events = []
        while True:
            try:
                events.append(self._streamQueue.get_nowait())
            except queue.Empty:
                break

        if not events:
            return

        # Batch consecutive non-round deltas into a single render pass
        i = 0
        while i < len(events):
            event_type, payload = events[i]

            if event_type == 'delta':
                if payload.get('round'):
                    # Tool progress deltas are committed entries, process immediately
                    self._onStreamDelta(payload)
                    i += 1
                else:
                    # Batch consecutive streaming deltas (content only)
                    batched_content = ""
                    batch_start = i
                    while i < len(events):
                        et, ep = events[i]
                        if et != 'delta' or ep.get('round'):
                            break
                        # reasoning_content is intentionally suppressed from the chat UI
                        batched_content += ep.get('content', '')
                        i += 1
                    # Apply batched deltas in one go
                    if batched_content:
                        self._streamContent += batched_content
                        self._renderStreamingEntry()
                    slicer.app.processEvents()
            elif event_type == 'complete':
                self._onStreamComplete(payload)
                i += 1
            elif event_type == 'error':
                self._onStreamError(payload)
                i += 1
            elif event_type == 'correction_complete':
                self._handleCorrectionResult(**payload)
                i += 1
            elif event_type == 'correction_error':
                self._handleCorrectionError(**payload)
                i += 1
            elif event_type == 'status':
                self._setAgentStatus(self._roleForStatus(payload), payload)
                i += 1
            elif event_type == 'role_trace':
                self._recordRoleEvent(
                    payload.get('role', 'Unknown'),
                    payload.get('event', 'event'),
                    payload.get('details', {})
                )
                i += 1
            elif event_type == 'cli_progress':
                self._handleCliProgress(payload['stage'], payload['name'], payload['detail'])
                i += 1
            elif event_type == 'cli_complete':
                self._handleCliComplete(payload)
                i += 1
            elif event_type == 'cli_revision_complete':
                self._handleCliRevisionComplete(payload)
                i += 1
            elif event_type == 'cli_live_repair_complete':
                self._handleCliLiveRepairComplete(payload)
                i += 1
            elif event_type == 'cli_repair_complete':
                self._handleCliRepairComplete(payload)
                i += 1
            elif event_type == 'cli_error':
                self._handleCliError(payload)
                i += 1
            elif event_type == 'cli_instructions_regenerated':
                self._handleInstructionsRegenerated(payload)
                i += 1
            elif event_type == 'cli_probe_request':
                self._handleCliProbeRequest(payload)
                i += 1
            elif event_type == 'thinking_delta':
                self._thinkingDisplayText += payload
                self._thinkingDisplayed = True
                self._renderStreamingEntry()
                i += 1
            elif event_type == 'thinking_done':
                self._thinkingDisplayed = False
                self._thinkingDisplayText = ""
                self._renderStreamingEntry()
                i += 1
            elif event_type == 'workflow_wait':
                self._enterWorkflowWait(payload)
                i += 1
            elif event_type == 'baseline_generated':
                self._handleBaselineGenerated(payload)
                i += 1
            elif event_type == 'baseline_status':
                self._setBaselineStatus(payload)
                i += 1
            elif event_type == 'baseline_thinking':
                self._handleBaselineThinkingRound(payload)
                i += 1
            else:
                i += 1

    def _onStreamDelta(self, delta):
        """Apply one streamed delta on the main thread."""
        if delta.get('round'):
            self._updateToolProgress(delta)
        else:
            # reasoning_content is intentionally not accumulated into the chat UI
            self._streamContent += delta.get('content', '')
            self._renderStreamingEntry()
        slicer.app.processEvents()

    def _updateToolProgress(self, delta):
        """Display tool execution progress as a separate committed entry."""
        progress_text = delta.get('reasoning_content', '').strip()
        if not progress_text:
            return

        timestamp = qt.QDateTime.currentDateTime().toString("hh:mm:ss")
        html = (
            f'<div style="margin: 5px 0; padding: 5px 10px; background-color: #f5f5f5; border-left: 3px solid #999;">'
            f'<span style="color: #999; font-size: 10px;">[{timestamp}]</span> '
            f'<span style="color: #666; font-weight: bold;">Search:</span>'
            f'<div style="margin-left: 10px; margin-top: 3px; white-space: pre-wrap; color: #555;">{self.escapeHtml(progress_text).replace(chr(10), "<br>")}</div>'
            f'</div>'
        )
        self._debugWriteEntries().append(html)
        self._renderChatIfVisible(with_streaming=True)

    def _onStreamComplete(self, response):
        """Called on the main thread when streaming finishes successfully."""
        self._streaming = False
        self._thinkingDisplayed = False
        self._thinkingDisplayText = ""
        self._finalizeStreamingEntry()

        # Record LLM internal timing and token usage
        if self._timing:
            self._timing['llm_timing'] = response.get('timing_report', {})
            if 'retrieval_timing' in response:
                self._timing['retrieval_timing'] = response['retrieval_timing']
            import time
            self._timing['generation_complete'] = time.time()
            if response.get('tokens'):
                self._timing['tokens'] = response['tokens']
            if response.get('cost') is not None:
                self._timing['cost'] = response['cost']

        # Thinking is already persisted per-round via on_reasoning callback — no need to write again here

        # Transfer workflow step info from Logic to Widget (for all response types)
        workflow_step_info = None
        _stepInfoFromInteractive = False
        if hasattr(self.logic, '_lastInteractiveStep') and self.logic._lastInteractiveStep:
            step_info = self.logic._lastInteractiveStep
            workflow_step_info = step_info
            self._currentWorkflowStepInfo = step_info
            self.logic._lastInteractiveStep = None
            if (hasattr(self.logic, '_lastWorkflowStep')
                and self._sameWorkflowStepMarker(step_info, self.logic._lastWorkflowStep)):
                self.logic._lastWorkflowStep = None
            _stepInfoFromInteractive = True
            self._registerWorkflowRuntimeResult(step_info)

            # Start or update the workflow if needed
            if self._workflowOrchestrator and step_info.get("step_id"):
                if not self._activeWorkflowId:
                    # Auto-start workflow for the extension
                    ext_name = step_info.get("tool", "")
                    try:
                        from SlicerAIAgentLib.ExtensionCLILoader import _ensure_cache, get_cli_base_dir
                        _ensure_cache()
                        import os, json
                        wf_path = os.path.join(get_cli_base_dir(), ext_name, "workflow.json")
                        if os.path.isfile(wf_path):
                            with open(wf_path, "r") as f:
                                wf_graph = json.load(f)
                            self._workflowOrchestrator.load_workflow_graph(ext_name, wf_graph)
                            state = self._workflowOrchestrator.start_workflow(ext_name)
                            self._activeWorkflowId = state.workflow_id
                    except Exception as e:
                        logger.warning(f"Failed to start workflow: {e}")

                # Set the orchestrator's current step to waiting
                if self._activeWorkflowId:
                    state = self._workflowOrchestrator._get_state(self._activeWorkflowId)
                    if state:
                        state.current_step = step_info.get("step_id")
                        state.status = "running"

        # Handle automated (non-interactive) workflow steps the same way
        if (not _stepInfoFromInteractive
            and hasattr(self.logic, '_lastWorkflowStep')
            and self.logic._lastWorkflowStep):
            step_info = self.logic._lastWorkflowStep
            workflow_step_info = step_info
            self._currentWorkflowStepInfo = step_info
            self.logic._lastWorkflowStep = None
            self._registerWorkflowRuntimeResult(step_info)

            if step_info.get("step_id"):
                if not self._activeWorkflowId:
                    ext_name = step_info.get("tool", "")
                    try:
                        from SlicerAIAgentLib.ExtensionCLILoader import _ensure_cache, get_cli_base_dir
                        _ensure_cache()
                        import os, json
                        wf_path = os.path.join(get_cli_base_dir(), ext_name, "workflow.json")
                        if os.path.isfile(wf_path):
                            with open(wf_path, "r") as f:
                                wf_graph = json.load(f)
                            self._workflowOrchestrator.load_workflow_graph(ext_name, wf_graph)
                            state = self._workflowOrchestrator.start_workflow(ext_name)
                            self._activeWorkflowId = state.workflow_id
                    except Exception as e:
                        logger.warning(f"Failed to start workflow for automated step: {e}")

                if self._activeWorkflowId:
                    state = self._workflowOrchestrator._get_state(self._activeWorkflowId)
                    if state:
                        state.current_step = step_info.get("step_id")
                        state.status = "running"

        if not response.get("code") and isinstance(workflow_step_info, dict):
            workflow_code = (
                workflow_step_info.get("code")
                or workflow_step_info.get("pre_code")
                or workflow_step_info.get("post_code")
            )
            if workflow_code:
                response["code"] = workflow_code
                response["agent_plan"] = self._buildWorkflowAgentPlan(workflow_step_info)
                self._recordRoleEvent("Workflow", "promoted_tool_result_code", {
                    "step_id": workflow_step_info.get("step_id"),
                    "type": workflow_step_info.get("type"),
                    "code_chars": len(workflow_code),
                })
            elif workflow_step_info.get("type") == "user_choice":
                response["workflow_wait"] = True

        # Display generated code if any and auto-execute
        if response.get("code"):
            self.currentCode = response["code"]
            self.currentAgentPlan = response.get("agent_plan")

            self._recordRoleEvent("Planner", "agent_plan_received", {
                "has_plan": bool(self.currentAgentPlan),
                "steps": len(self.currentAgentPlan.get("steps", [])) if isinstance(self.currentAgentPlan, dict) else 0,
                "risk_level": self.currentAgentPlan.get("risk_level") if isinstance(self.currentAgentPlan, dict) else None,
            })
            self._recordRoleEvent("Programmer", "code_received", {
                "code_chars": len(self.currentCode or ""),
            })
            self._setGeneratedCode(response["code"])
            self._displayAgentPlanSummary(self.currentAgentPlan)
            self._saveAgentPlanToFile(self.currentAgentPlan)
            self._saveGeneratedCodeToFile(response["code"])
            # Auto-execute the generated code
            if self._timing:
                self._timing['autoexecute_start'] = time.time()
            self._autoExecuteCode()

        elif response.get("workflow_wait"):
            # Workflow step is waiting for user input (e.g., user_choice)
            if self._currentWorkflowStepInfo and self._currentWorkflowStepInfo.get("type") == "user_choice":
                self._displayWorkflowChoice(self._currentWorkflowStepInfo)
            elif self._currentWorkflowStepInfo:
                self._showWorkflowInteraction(self._currentWorkflowStepInfo)

        # Update per-turn cumulative token usage
        if response.get("tokens"):
            self._currentTurnTokens += response["tokens"]
            self._currentTurnCost += response.get("cost", 0)
            self._updateTokenLabel()

        self._stopThinkingTimer("Done")
        self._setReadyStatus()
        self._setSendEnabled(True)

    def _onStreamError(self, error_msg):
        """Called on the main thread when the streaming request fails."""
        self._streaming = False
        self._finalizeStreamingEntry()
        logger.error(f"Error generating response: {error_msg}")

        if "timed out" in error_msg.lower() or "timeout" in error_msg.lower():
            self.appendToChat("Error",
                f"Request timed out.\n\n"
                f"Please check:\n"
                f"1. Your network connection\n"
                f"2. The model name is correct (e.g. 'kimi-k2.5', 'deepseek-v4-pro')\n"
                f"3. Your API key has access to K2.5 models\n\n"
                f"Technical details: {error_msg}")
        else:
            self.appendToChat("Error", f"Failed to generate response: {error_msg}")

        if getattr(self, "_taskWorkflowPanelActive", False):
            self._updateWorkflowPanel({
                "active": True,
                "mode": "task",
                "workflow_title": "Task",
                "status": "Failed",
                "description": str(error_msg),
                "instructions": "",
                "total_steps": 0,
                "can_done": False,
                "can_skip": False,
            })
            self._taskWorkflowPanelActive = False
        self._stopThinkingTimer("Error")
        self._setReadyStatus()
        self._setSendEnabled(True)
