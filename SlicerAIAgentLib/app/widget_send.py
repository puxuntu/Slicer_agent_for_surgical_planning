from .common import *


class WidgetSendMixin:
    def onSendButtonClicked(self):
        prompt = self.promptInput.toPlainText().strip()
        if not prompt:
            return

        # A routing call is already out. This has to be checked BEFORE anything
        # below mutates state, because all of it is user-visible bookkeeping:
        # clearing the box CONSUMES the request, and _lastUserPrompt /
        # _sendClickedEpoch are what the run manifest records. Routing became
        # asynchronous, so the window in which a second Send is possible is the
        # whole network wait -- and on a slow link that is minutes.
        resumed = getattr(self, "_routerAlreadyDeclined", False)
        if getattr(self, "_routerBusy", False) and not resumed:
            self._noteRouterStillBusy()
            return

        if not resumed:
            # The user-visible start of a run. Taken here rather than from the
            # manifest's own `started_epoch`, which is stamped only once the
            # router has answered -- several seconds of the run the surgeon sat
            # through would otherwise be missing from "Send to Exit".
            import time as _time
            self._sendClickedEpoch = _time.time()
            self.appendToChat("You", prompt)
            self._lastUserPrompt = prompt  # Saved for isolated self-correction

        # On the resumed path the prompt was put BACK in the box by
        # _finishRouterTurn so this method could read it; the click's own
        # bookkeeping already happened and must not happen twice.
        self.promptInput.clear()

        # Record the current turn number for consistent debug file naming
        if self.logic and hasattr(self.logic, 'llmClient') and self.logic.llmClient:
            self._currentTurn = getattr(self.logic.llmClient, 'turn_number', 1)
        else:
            self._currentTurn = 1

        # Reset per-turn cumulative token/cost counters
        self._currentTurnTokens = 0
        self._currentTurnCost = 0.0

        if self._handleDirectWorkflowTurnIfNeeded(prompt):
            return

        # Opening turn: if the request names a guided planning workflow, enter it
        # through one small routing call instead of the full agent turn (whose
        # only output would be the same tool call). Returns False for anything
        # else, and the unchanged full turn below handles it.
        if self._handleWorkflowRouterTurnIfNeeded(prompt):
            return

        # Guided-only: the router's decision is final. Everything below this
        # point is the traditional search-and-generate turn -- dense retrieval,
        # the tool loop, free-form code -- which this runtime deliberately does
        # not offer. The router recorded WHY it declined; the refusal reports it
        # and hands the prompt back. One flag away from the old fall-through.
        from SlicerAIAgentLib.WorkflowRouter import GUIDED_ONLY_MODE
        if GUIDED_ONLY_MODE:
            self._refuseUnsupportedRequest(prompt)
            return

        if not (self._workflowRuntime and self._workflowRuntime.has_active_workflow()):
            self._clearWorkflowResultMarkers()

        self.sendButton.setEnabled(False)
        self._taskWorkflowPanelActive = True
        self._updateWorkflowPanel({
            "active": True,
            "mode": "task",
            "workflow_title": "Task",
            "status": "Planning",
            "description": prompt,
            "instructions": "",
            "total_steps": 0,
            "can_done": False,
            "can_skip": False,
        })
        slicer.app.processEvents()

        # Reset streaming accumulators
        self._streamReasoning = ""
        self._streamContent = ""
        self._streaming = True
        self._thinkingDisplayText = ""
        self._thinkingDisplayed = False
        self._streamTimestamp = qt.QDateTime.currentDateTime().toString("hh:mm:ss")
        self._renderStreamingEntry()

        # Initialize timing
        import time
        self._timing = {
            'turn_start': time.time(),
            'prompt': prompt,
        }
        # If the fast workflow router looked at this prompt and declined, its
        # cost belongs to THIS turn -- record it so the performance log accounts
        # for every API call the turn made, not just the ones below.
        declined = getattr(self, '_lastRouterDecision', None)
        if declined is not None:
            self._timing['router_declined'] = {
                'confidence': declined.confidence,
                'reason': declined.reason or declined.error,
                'seconds': declined.seconds,
                'prompt_chars': declined.prompt_chars,
                'tokens': declined.tokens,
            }
            self._lastRouterDecision = None
        # A general (non-workflow) turn: logs/<stamp>_pipeline_task_turnN/
        from SlicerAIAgentLib import RunLog
        self._currentLogDir = self._createRunLogDir(
            getattr(self, "_currentTurn", 1),
            condition=RunLog.CONDITION_PIPELINE,
            router_declined=self._timing.get("router_declined"),
        )
        if self.logic and self.logic.llmClient:
            self.logic.llmClient.setDebugOutputDir(self._currentLogDir)
        # A router call that DECLINED still happened and still cost tokens;
        # record it in the folder of the turn that ran instead.
        router = getattr(self, '_lastRouter', None)
        if router is not None:
            router.write_artifacts(self._currentLogDir)
            self._lastRouter = None
        self._roleTrace = []
        self._setAgentStatus("Observer", "Reading request...")
        self._recordRoleEvent("Observer", "received_prompt", {
            "prompt_length": len(prompt),
            "turn": getattr(self, "_currentTurn", 1),
        })

        # Start real-time thinking timer
        self._startThinkingTimer()

        # Build context on the main thread (it reads the MRML scene)
        import time as _time
        ctx_start = _time.time()
        context = {"scene": self.logic._buildSceneContext()} if self.logic else None

        # Inject active workflow state into context
        if self._workflowRuntime and self._workflowRuntime.has_active_workflow():
            wf_fragment = self._workflowRuntime.get_prompt_fragment()
            if wf_fragment and context:
                context["workflow_state"] = wf_fragment
        elif self._workflowOrchestrator and self._activeWorkflowId:
            wf_fragment = self._workflowOrchestrator.get_active_workflow_prompt_fragment()
            if wf_fragment and context:
                context["workflow_state"] = wf_fragment

        if self._timing:
            self._timing['context_build_time'] = _time.time() - ctx_start
        self._recordRoleEvent("Observer", "captured_scene_context", {
            "has_scene_context": bool(context and context.get("scene")),
            "elapsed_sec": round(_time.time() - ctx_start, 3),
        })
        self._setAgentStatus("Retriever", "Retrieving...")

        # Launch the streaming request in a background thread
        def _backgroundStream():
            try:
                def _onDelta(delta):
                    self._streamQueue.put(('delta', dict(delta)))

                def _onStatus(status_text):
                    self._streamQueue.put(('status', status_text))

                def _onReasoning(reasoning_text, round_num):
                    self._appendThinkingToFile(reasoning_text, turn=getattr(self, '_currentTurn', 1))
                    # Hide thinking from UI when the round completes
                    self._streamQueue.put(('thinking_done', None))

                def _onReasoningDelta(chunk):
                    self._streamQueue.put(('thinking_delta', chunk))

                import time as _time
                gen_start = _time.time()
                if self._timing:
                    self._timing['generation_start'] = gen_start
                response = self.logic.generateResponseStream(prompt, context, _onDelta, on_status=_onStatus, on_reasoning=_onReasoning, on_reasoning_delta=_onReasoningDelta)
                if self._timing:
                    self._timing['generation_end'] = _time.time()
                self._streamQueue.put(('role_trace', {
                    'role': 'Retriever',
                    'event': 'retrieval_and_tool_loop_completed',
                    'details': {
                        'has_retrieval_timing': bool(response.get('retrieval_timing')),
                        'tool_rounds': response.get('timing_report', {}).get('tool_rounds', 0),
                        'api_calls': response.get('timing_report', {}).get('api_calls', 0),
                    },
                }))
                self._streamQueue.put(('complete', dict(response)))
            except Exception as e:
                self._streamQueue.put(('error', str(e)))

        thread = threading.Thread(target=_backgroundStream, daemon=True)
        thread.start()

    def onPromptTextChanged(self):
        hasText = bool(self.promptInput.toPlainText().strip())
        self._setSendEnabled(hasText)

    def generateResponse(self, prompt):
        """Legacy non-streaming path (kept for backward compatibility)."""
        try:
            response = self.logic.generateResponse(prompt)
            self.appendToChat("Assistant", response["message"])

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
                self._autoExecuteCode()

            if response.get("tokens"):
                self._currentTurnTokens += response["tokens"]
                self._currentTurnCost += response.get("cost", 0)
                self._updateTokenLabel()
                if self._timing:
                    self._timing['tokens'] = self._currentTurnTokens
                    self._timing['cost'] = self._currentTurnCost

            # Persist thinking/reasoning content to file (non-streaming path)
            if response.get('reasoning_content'):
                self._appendThinkingToFile(response['reasoning_content'], turn=getattr(self, '_currentTurn', 1))

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            self.appendToChat("Error", f"Failed to generate response: {str(e)}")
        finally:
            self._setReadyStatus()
            self._setSendEnabled(True)
