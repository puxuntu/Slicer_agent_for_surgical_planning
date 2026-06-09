from .common import *


class WidgetStreamingMixin:
    def onSceneStartClose(self, caller, event):
        if self.logic:
            self.logic.pauseProcessing()

    def onSceneEndClose(self, caller, event):
        if self.logic:
            self.logic.resumeProcessing()

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
        self._setChatHtml(''.join(self._chatEntriesHtml) + self._buildStreamingEntryHtml())

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
                "can_cancel": False,
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
            "can_cancel": False,
        })

    def _autoAdvanceNextStep(self, next_step):
        """Auto-advance to the next workflow step after an automated step completes."""
        step_id = next_step.get("step_id", "")
        is_optional = next_step.get("is_optional", False)
        if is_optional:
            # For optional steps, just ask the user
            self._updateWorkflowPanel({
                "active": True,
                "workflow_title": self._currentWorkflowUiState.get("workflow_title", "Workflow"),
                "status": "Waiting for your choice",
                "current_step": step_id,
                "current_index": self._currentWorkflowUiState.get("current_index", 0),
                "completed_steps": self._currentWorkflowUiState.get("completed_steps", 0),
                "total_steps": self._currentWorkflowUiState.get("total_steps", 0),
                "description": next_step.get("description", ""),
                "instructions": "This step is optional.",
                "can_done": True,
                "can_skip": True,
                "can_cancel": True,
            })
            self._setReadyStatus()
            return
        self._runWorkflowStepDirect(step_id, "start")

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

    def _clearCompletedWorkflowState(self):
        """Drop transient generated-CLI workflow state after completion or cancel."""
        self._clearWorkflowResultMarkers()
        self._currentWorkflowStepInfo = None
        self._waitingForUser = False
        self._autoAdvanceWorkflowStep = None
        self._activeWorkflowId = None
        self._taskWorkflowPanelActive = False

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
        """Initialize compact per-turn state for a deterministic CLI step."""
        import time
        self._currentLogDir = self._createRunLogDir(getattr(self, "_currentTurn", 1))
        if self.logic and self.logic.llmClient:
            self.logic.llmClient.setDebugOutputDir(self._currentLogDir)
        if self._workflowRuntime:
            self._workflowRuntime.log_dir = self._currentLogDir
        self._roleTrace = []
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
        if route.route_type == ROUTE_WORKFLOW_CONFLICT:
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
            self.sendButton.setEnabled(True)
            return True

        if route.route_type == ROUTE_WORKFLOW_UNRESOLVED:
            self.appendToChat(
                "System",
                "I could not confidently map that message to an allowed workflow "
                f"action, so the workflow state was not changed. {route.reason}",
            )
            self._setReadyStatus()
            self.sendButton.setEnabled(True)
            return True

        if route.route_type != ROUTE_WORKFLOW_CONTROL:
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
            self.sendButton.setEnabled(True)
            return

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
        self._handleWorkflowRuntimeResult(result)

    def _handleWorkflowRuntimeResult(self, result):
        """Handle a deterministic generated CLI dispatcher result."""
        if not isinstance(result, dict):
            self.appendToChat("Error", "Generated CLI workflow returned an invalid result.")
            self._setReadyStatus()
            self.sendButton.setEnabled(True)
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
                "can_cancel": bool(self._workflowRuntime and self._workflowRuntime.has_active_workflow()),
            })
            self._recordRoleEvent("Workflow", "dispatch_failed", {"error": result["error"]})
            self._saveRoleTraceToFile()
            self._setReadyStatus()
            self.sendButton.setEnabled(True)
            return

        self._registerWorkflowRuntimeResult(result)
        self._currentWorkflowStepInfo = result
        result_type = result.get("type")

        if result_type == "cancelled":
            self.appendToChat("System", result.get("message", "Workflow cancelled."))
            self._updateWorkflowPanel(result)
            self._clearCompletedWorkflowState()
            self._recordRoleEvent("Workflow", "cancelled", {})
            self._saveRoleTraceToFile()
            self._setReadyStatus()
            self.sendButton.setEnabled(True)
            return

        if result_type == "user_choice":
            resolved = self._tryResolveWorkflowNodeChoice(result)
            if resolved.get("selected"):
                self.appendToChat(
                    "System",
                    "Automatically selected "
                    f"'{resolved.get('selected_node_name')}' for workflow step "
                    f"{result.get('step_id')} using LLM name matching "
                    f"(confidence {resolved.get('confidence', 0):.2f}).",
                )
                self._recordRoleEvent("Workflow", "llm_node_choice_resolved", {
                    "step_id": result.get("step_id"),
                    "selected_node_id": resolved.get("selected_node_id"),
                    "selected_node_name": resolved.get("selected_node_name"),
                    "confidence": resolved.get("confidence"),
                    "reason": resolved.get("reason"),
                })
                self._runWorkflowStepDirect(
                    result.get("step_id"),
                    "choice_made",
                    args={"choice_value": resolved.get("choice_value")},
                )
                return
            if resolved.get("attempted"):
                self._recordRoleEvent("Workflow", "llm_node_choice_unresolved", {
                    "step_id": result.get("step_id"),
                    "reason": resolved.get("reason"),
                    "confidence": resolved.get("confidence"),
                })
            self._displayWorkflowChoice(result)
            self._recordRoleEvent("Workflow", "waiting_for_choice", {
                "step_id": result.get("step_id"),
            })
            self._saveRoleTraceToFile()
            self._setReadyStatus()
            self.sendButton.setEnabled(True)
            return

        code = result.get("code") or result.get("pre_code") or result.get("post_code")
        if code:
            self.currentCode = code
            self.currentAgentPlan = self._buildWorkflowAgentPlan(result)
            self.codeDisplay.setPlainText(code)
            self._saveAgentPlanToFile(self.currentAgentPlan)
            self._saveGeneratedCodeToFile(code, suffix=f"_{result.get('step_id', 'workflow')}")
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
        """Show a generated CLI user-choice question without asking the LLM."""
        self._showWorkflowChoice(step_info)

    def _tryResolveWorkflowNodeChoice(self, step_info):
        """Use a narrow LLM call to resolve ambiguous scene-node choices."""
        node_class = step_info.get("node_class") or (step_info.get("binding") or {}).get("node_class")
        if not node_class or step_info.get("choices"):
            return {"selected": False, "attempted": False, "reason": "not_open_scene_node_choice"}
        candidates = self._collectWorkflowNodeCandidates(node_class)
        if len(candidates) <= 1:
            return {"selected": False, "attempted": False, "reason": "not_ambiguous_candidate_set"}
        if not self.logic or not self.logic.llmClient:
            return {"selected": False, "attempted": False, "reason": "llm_unavailable"}
        try:
            if self._nodeChoiceResolver is None:
                from SlicerAIAgentLib.NodeChoiceResolver import NodeChoiceResolver
                self._nodeChoiceResolver = NodeChoiceResolver(self.logic.llmClient)
            self._setAgentStatus("Workflow", "Resolving node choice...")
            resolved = self._nodeChoiceResolver.resolve(step_info, candidates)
            resolved["attempted"] = True
            return resolved
        except Exception as exc:
            logger.warning(f"Workflow node-choice resolver failed: {exc}")
            return {"selected": False, "attempted": True, "reason": str(exc)}

    def _collectWorkflowNodeCandidates(self, node_class):
        """Collect existing MRML nodes for LLM name-only matching."""
        candidates = []
        try:
            nodes = slicer.mrmlScene.GetNodesByClass(node_class)
            for index in range(nodes.GetNumberOfItems()):
                node = nodes.GetItemAsObject(index)
                if node is None:
                    continue
                item = {
                    "id": node.GetID() or "",
                    "name": node.GetName() or "",
                    "class": node.GetClassName() if hasattr(node, "GetClassName") else node_class,
                }
                try:
                    storage = node.GetStorageNode()
                    if storage and storage.GetFileName():
                        item["storageFileName"] = os.path.basename(storage.GetFileName())
                except Exception:
                    pass
                candidates.append(item)
        except Exception as exc:
            logger.warning(f"Failed to collect workflow node candidates for {node_class}: {exc}")
        return candidates

    def _completeWorkflowResultWithoutCode(self, result):
        """Advance deterministic workflow state for a no-code control result."""
        if self._workflowRuntime:
            result = self._workflowRuntime.handle_execution_result(
                result,
                {"success": True, "execution_time": 0.0, "output": ""},
            )
        next_step = result.get("next_step")
        if result.get("workflow_completed"):
            self._updateWorkflowPanel(result)
            self.appendToChat("System", "Generated CLI workflow complete.")
            self._clearCompletedWorkflowState()
            self._flushQueuedWorkflowPrompts()
            self._setReadyStatus()
            self.sendButton.setEnabled(True)
            return
        if next_step:
            self._updateWorkflowPanel(result)
            self._autoAdvanceWorkflowStep = next_step
            qt.QTimer.singleShot(100, lambda: self._autoAdvanceNextStep(next_step))
        else:
            self._setReadyStatus()
            self.sendButton.setEnabled(True)

    def _flushQueuedWorkflowPrompts(self):
        """Replay queued traditional prompts after a generated CLI workflow ends."""
        if not self._workflowRuntime:
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
            self._chatEntriesHtml.append(self._buildStreamingEntryHtml())
            self._setChatHtml(''.join(self._chatEntriesHtml))

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
            elif event_type == 'cli_error':
                self._handleCliError(payload)
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
        self._chatEntriesHtml.append(html)
        self._setChatHtml(''.join(self._chatEntriesHtml) + self._buildStreamingEntryHtml())

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
            self.codeDisplay.setPlainText(response["code"])
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
        self.sendButton.setEnabled(True)

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
                "can_cancel": False,
            })
            self._taskWorkflowPanelActive = False
        self._stopThinkingTimer("Error")
        self._setReadyStatus()
        self.sendButton.setEnabled(True)
