from .common import *


class WidgetExecutionFlowMixin:
    def _saveGeneratedCodeToFile(self, code, suffix=""):
        """Save the generated code to a local text file for user reference.

        Args:
            code: The generated Python code string.
            suffix: Optional suffix for the filename (e.g. '_correction_1').
        """
        try:
            turn_number = getattr(self, '_currentTurn', 1)
            latestPath = os.path.join(self._getCurrentLogDir(), f'{turn_number}{suffix}_code.txt')
            with open(latestPath, 'w', encoding='utf-8') as f:
                f.write(code)
        except Exception as e:
            logger.warning(f"Failed to save generated code to file: {e}")

    def _saveAgentPlanToFile(self, plan, suffix=""):
        """Persist the parsed agent_plan JSON as a standalone debug artifact."""
        if not isinstance(plan, dict):
            return
        try:
            turn_number = getattr(self, '_currentTurn', 1)
            path = os.path.join(self._getCurrentLogDir(), f'{turn_number}{suffix}_agent_plan.json')
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(plan, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save agent plan to file: {e}")

    def _createRunLogDir(self, turn_number):
        """Create logs/YYYYmmdd_HHMMSS_turnN for all artifacts from one run."""
        from datetime import datetime
        moduleDir = SLICER_AI_AGENT_ROOT
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = os.path.join(moduleDir, "logs", f"{stamp}_turn{turn_number}")
        os.makedirs(log_dir, exist_ok=True)
        return log_dir

    def _getCurrentLogDir(self):
        """Return current run log directory, creating a fallback if needed."""
        if not self._currentLogDir:
            self._currentLogDir = self._createRunLogDir(getattr(self, "_currentTurn", 1))
            if self.logic and self.logic.llmClient:
                self.logic.llmClient.setDebugOutputDir(self._currentLogDir)
        os.makedirs(self._currentLogDir, exist_ok=True)
        return self._currentLogDir

    def _recordRoleEvent(self, role, event, details=None):
        """Record a structured event for the role-composed agent trace."""
        import time
        entry = {
            "time": round(time.time(), 3),
            "role": role,
            "event": event,
            "details": details or {},
        }
        self._roleTrace.append(entry)
        if self._timing is not None:
            self._timing["role_trace"] = list(self._roleTrace)

    def _saveRoleTraceToFile(self, suffix=""):
        """Persist the current role trace for academic/debug inspection."""
        try:
            turn_number = getattr(self, '_currentTurn', 1)
            path = os.path.join(self._getCurrentLogDir(), f'{turn_number}{suffix}_role_trace.json')
            payload = {
                "turn": turn_number,
                "prompt": getattr(self, "_lastUserPrompt", ""),
                "events": self._roleTrace,
            }
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save role trace: {e}")

    def _displayAgentPlanSummary(self, plan):
        """Show a compact plan summary in chat without adding a new UI surface."""
        if not plan:
            self.appendToChat("System", "No valid agent_plan block was returned. Auto-execution will be blocked.")
            return
        try:
            summary = plan.get("task_summary", "No task summary")
            overall_confidence = plan.get("overall_confidence") or self._deriveOverallPlanConfidence(plan)
            steps = plan.get("steps", [])
            step_lines = []
            for i, step in enumerate(steps[:5], start=1):
                if isinstance(step, dict):
                    action = step.get("action", "Unnamed step")
                    confidence = step.get("confidence", "unknown")
                    step_lines.append(f"{i}. {action} [{confidence}]")
            extra = "" if len(steps) <= 5 else f"\n... {len(steps) - 5} more step(s)"
            self.appendToChat(
                "System",
                "Verified plan received.\n"
                f"Task: {summary}\n"
                f"Overall confidence: {overall_confidence}\n"
                + ("\n".join(step_lines) if step_lines else "No steps listed")
                + extra
            )
        except Exception as e:
            logger.warning(f"Failed to display agent plan: {e}")

    def _deriveOverallPlanConfidence(self, plan):
        """Estimate whole-plan confidence for display when the plan lacks the field."""
        if not isinstance(plan, dict):
            return "unknown"
        steps = plan.get("steps", [])
        if not isinstance(steps, list) or not steps:
            return "unknown"
        confidence_values = [
            str(step.get("confidence", "unknown")).lower()
            for step in steps
            if isinstance(step, dict)
        ]
        if not confidence_values:
            return "unknown"
        if any(value in ("low", "needs_lookup", "unknown") for value in confidence_values):
            return "low"
        if any(value == "medium" for value in confidence_values):
            return "medium"
        return "high"

    def _validateAgentPlan(self, plan):
        """Validate the structured plan enough to prevent blind execution."""
        errors = []
        warnings = []
        if not isinstance(plan, dict):
            return {
                "valid": False,
                "requires_confirmation": False,
                "errors": ["Missing or invalid agent_plan JSON block"],
                "warnings": [],
            }

        steps = plan.get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append("agent_plan.steps must be a non-empty list")

        risk = str(plan.get("risk_level", "unknown")).lower()
        plan_requires_confirmation = bool(plan.get("requires_confirmation")) or risk == "high"
        unresolved = plan.get("unverified_assumptions", [])
        if unresolved is None:
            unresolved = []
        if not isinstance(unresolved, list):
            warnings.append("agent_plan.unverified_assumptions should be a list")
            unresolved = [str(unresolved)]

        high_conf_steps = 0
        high_conf_without_evidence = 0
        needs_lookup = []
        if isinstance(steps, list):
            for idx, step in enumerate(steps, start=1):
                if not isinstance(step, dict):
                    errors.append(f"Step {idx} must be an object")
                    continue
                if not step.get("action"):
                    errors.append(f"Step {idx} is missing action")
                confidence = str(step.get("confidence", "unknown")).lower()
                if confidence == "needs_lookup":
                    needs_lookup.append(step.get("action", f"step {idx}"))
                if confidence == "high":
                    high_conf_steps += 1
                    evidence = step.get("evidence")
                    if not evidence:
                        high_conf_without_evidence += 1
                # Validate expected_scene_change
                expected = step.get("expected_scene_change")
                if not isinstance(expected, dict) or not expected.get("type"):
                    errors.append(f"Step {idx} is missing required 'expected_scene_change'. Use 'not_checked' if this step has no scene effect.")
                else:
                    valid_types = {"node_count_delta", "node_exists", "node_modified",
                                   "node_has_display", "node_name_matches", "layout_changed",
                                   "selection_changed", "module_entered", "property_true", "not_checked"}
                    if str(expected.get("type")).lower() not in valid_types:
                        warnings.append(f"Step {idx} has unsupported expected_scene_change type '{expected.get('type')}'")

        if needs_lookup:
            errors.append("Plan still contains needs_lookup step(s): " + ", ".join(needs_lookup[:3]))
        if high_conf_steps and high_conf_without_evidence == high_conf_steps and high_conf_steps >= 2:
            warnings.append("Most high-confidence API steps have no explicit evidence")

        return {
            "valid": len(errors) == 0,
            "requires_confirmation": plan_requires_confirmation,
            "errors": errors,
            "warnings": warnings,
        }

    def _askExecutionConfirmation(self, reason, resume_callback):
        """Ask the user before executing high-risk or destructive code."""
        message_box = qt.QMessageBox(slicer.util.mainWindow())
        message_box.setWindowTitle("Confirm Agent Execution")
        message_box.setText("The generated plan or code requires confirmation before execution.")
        message_box.setInformativeText(reason)
        message_box.setStandardButtons(qt.QMessageBox.Yes | qt.QMessageBox.No)
        message_box.setDefaultButton(qt.QMessageBox.No)
        result = message_box.exec_()
        if result == qt.QMessageBox.Yes:
            self._recordRoleEvent("SafetyCritic", "execution_confirmed_by_user", {
                "reason": reason,
            })
            resume_callback()
        else:
            self._setReadyStatus()
            self.sendButton.setEnabled(True)
            self._recordRoleEvent("SafetyCritic", "execution_cancelled_by_user", {
                "reason": reason,
            })
            self._saveRoleTraceToFile()
            self.appendToChat("System", "Execution cancelled by user.")

    def _autoExecuteCode(self, attempt=1, max_attempts=5):
        """Auto-execute generated code with pre-validation and self-correction on failure."""
        if not hasattr(self, 'currentCode') or not self.currentCode:
            return

        self._setAgentStatus("Safety Critic", "Validating plan...")
        plan_validation = self._validateAgentPlan(getattr(self, "currentAgentPlan", None))
        self._recordRoleEvent("SafetyCritic", "plan_validation_completed", {
            "valid": plan_validation.get("valid"),
            "requires_confirmation": plan_validation.get("requires_confirmation"),
            "errors": plan_validation.get("errors", []),
            "warnings": plan_validation.get("warnings", []),
        })
        if not plan_validation["valid"]:
            error_msg = "; ".join(plan_validation["errors"])
            if attempt >= max_attempts:
                self._setReadyStatus()
                self.sendButton.setEnabled(True)
                self._recordRoleEvent("Repairer", "max_attempts_reached", {
                    "attempts": max_attempts,
                    "final_error": error_msg,
                    "stage": "plan_validation",
                })
                self._saveRoleTraceToFile()
                self.appendToChat(
                    "Error",
                    f"Plan validation failed after {max_attempts} attempts.\nFinal error: {error_msg}"
                )
                return
            self.appendToChat(
                "System",
                f"Plan validation failed (attempt {attempt}/{max_attempts}).\n"
                f"Error: {error_msg}\n"
                "Auto-correcting..."
            )
            if self.logic:
                self.logic.addExecutionFeedback(
                    f"Agent plan validation failed (attempt {attempt}/{max_attempts}):\n"
                    f"Error: {error_msg}\n"
                    "The response must include a valid ```agent_plan JSON block before the Python code."
                )
            self._selfCorrectCode(error_msg, attempt, max_attempts)
            return

        # Pre-validation: check for syntax errors and common issues
        import time
        if self._timing:
            self._timing['validation_start'] = time.time()

        validation = None
        if self.logic and hasattr(self.logic, 'codeValidator'):
            self._setAgentStatus("Safety Critic", "Validating code...")
            validation = self.logic.codeValidator.validate(self.currentCode)
            self._recordRoleEvent("SafetyCritic", "code_validation_completed", {
                "valid": validation.get("valid"),
                "requires_confirmation": validation.get("requires_confirmation"),
                "destructive_ops": validation.get("destructive_ops", []),
                "warnings": validation.get("warnings", []),
                "reason": validation.get("reason"),
            })
            if self._timing:
                self._timing['validation_end'] = time.time()
            if not validation['valid']:
                # Syntax error detected before execution
                error_msg = validation['reason']
                if attempt >= max_attempts:
                    self._setReadyStatus()
                    self.sendButton.setEnabled(True)
                    self._recordRoleEvent("Repairer", "max_attempts_reached", {
                        "attempts": max_attempts,
                        "final_error": error_msg,
                        "stage": "code_validation",
                    })
                    self._saveRoleTraceToFile()
                    self.appendToChat(
                        "Error",
                        f"Pre-validation failed after {max_attempts} attempts.\nFinal error: {error_msg}"
                    )
                    return
                self.appendToChat("System",
                    f"Pre-validation failed (attempt {attempt}/{max_attempts}).\n"
                    f"Error: {error_msg}\n"
                    f"Auto-correcting...")
                if self.logic:
                    self.logic.addExecutionFeedback(
                        f"Code pre-validation failed (attempt {attempt}/{max_attempts}):\n"
                        f"Error: {error_msg}\n"
                        "The code had syntax errors or violated safety rules before execution."
                    )
                self._selfCorrectCode(error_msg, attempt, max_attempts)
                return
        else:
            if self._timing:
                self._timing['validation_end'] = time.time()

        # Live API sanity check (fail-open, runs on the Qt main thread):
        # resolve module-rooted attribute chains against the running Slicer
        # before execution. A confirmed-missing API goes straight to
        # self-correction with close-match evidence, skipping the doomed
        # execute/rollback cycle a runtime AttributeError would cost.
        try:
            from ..ApiSanityChecker import check_code, check_extension_methods, format_failures
            sanity = check_code(self.currentCode or "")
            # Also verify methods called on extension Logic/Widget instances
            # exist on the live runtime class (check_code only covers
            # slicer/vtk/qt/ctk roots). Catches a hallucinated extension method
            # — e.g. logic.rotation_p_stop() absent from the installed version —
            # before execution and before the correction loop re-invents it.
            ext_sanity = check_extension_methods(self.currentCode or "")
            if not ext_sanity.get("ok"):
                sanity = dict(sanity)
                sanity["missing"] = list(sanity.get("missing", [])) + ext_sanity["missing"]
                sanity["ok"] = False
            if self._timing is not None:
                self._timing['api_sanity'] = {
                    'elapsed': sanity.get('elapsed', 0.0),
                    'checked': sanity.get('checked', 0),
                    'missing': len(sanity.get('missing', [])),
                }
            if not sanity.get("ok"):
                error_msg = format_failures(sanity["missing"])
                self._recordRoleEvent("SafetyCritic", "api_sanity_failed", {
                    "missing": [item.get("chain") for item in sanity["missing"]],
                    "checked": sanity.get("checked", 0),
                })
                if attempt >= max_attempts:
                    self._setReadyStatus()
                    self.sendButton.setEnabled(True)
                    self._recordRoleEvent("Repairer", "max_attempts_reached", {
                        "attempts": max_attempts,
                        "final_error": error_msg,
                        "stage": "api_sanity",
                    })
                    self._saveRoleTraceToFile()
                    self.appendToChat(
                        "Error",
                        f"Pre-execution API check failed after {max_attempts} attempts.\n{error_msg}"
                    )
                    return
                self.appendToChat(
                    "System",
                    f"Pre-execution API check failed (attempt {attempt}/{max_attempts}).\n"
                    f"{error_msg}\nAuto-correcting..."
                )
                if self.logic:
                    self.logic.addExecutionFeedback(
                        f"Pre-execution API sanity check failed (attempt {attempt}/{max_attempts}):\n"
                        f"{error_msg}"
                    )
                self._selfCorrectCode(error_msg, attempt, max_attempts)
                return
        except Exception:
            logger.debug("ApiSanityChecker failed open", exc_info=True)

        requires_confirmation = plan_validation.get("requires_confirmation", False)
        confirmation_reasons = []
        if plan_validation.get("warnings"):
            for warning in plan_validation["warnings"]:
                logger.warning(f"Agent plan warning: {warning}")
        if requires_confirmation:
            confirmation_reasons.append(
                f"Plan risk level: {getattr(self, 'currentAgentPlan', {}).get('risk_level', 'unknown')}"
            )
        if validation and validation.get("requires_confirmation"):
            destructive_ops = ", ".join(validation.get("destructive_ops", []))
            confirmation_reasons.append(f"Potentially destructive operation(s): {destructive_ops}")
        if confirmation_reasons:
            reason = "\n".join(confirmation_reasons)
            logger.info(f"Auto-approving execution with warnings: {reason}")
            self.appendToChat("Warning", f"Executing with potentially destructive operations: {reason}")
            self._recordRoleEvent("SafetyCritic", "confirmation_required", {
                "reason": reason,
            })

        self._autoExecuteCodeConfirmed(attempt, max_attempts)

    def _persistGeneratedTemplateRepair(self, step_info, corrected_code, error_detail):
        """Write a runtime self-correction fix back into the step's code template.

        After self-correction fixes a generated-CLI step at runtime, persist the
        working code into that step's template so future runs load the corrected
        template and skip self-correction entirely. The pre-revision templates are
        backed up first (versions/runtime_fix_<ts>/). Fail-soft throughout.
        """
        import time
        from SlicerAIAgentLib.ExtensionCLILoader import get_cli_base_dir

        if not isinstance(step_info, dict):
            return
        corrected_code = str(corrected_code or "")
        if not corrected_code.strip():
            return
        step_id = str(step_info.get("step_id", "") or "")
        session = getattr(getattr(self, "_workflowRuntime", None), "session", None)
        ext_name = str(
            step_info.get("extension")
            or step_info.get("tool")
            or getattr(session, "extension_name", "")
            or ""
        )
        if not ext_name or not step_id:
            return
        cli_dir = os.path.join(get_cli_base_dir(), ext_name)
        if not os.path.isdir(cli_dir):
            return

        # Which template file does this step use? (pre/post for interactive steps.)
        tpl_rel = self._templateFileForStep(cli_dir, step_id, str(step_info.get("type", "")))
        if not tpl_rel:
            return
        tpl_path = os.path.join(cli_dir, tpl_rel)
        if not os.path.isfile(tpl_path):
            return

        # Recover template-level content from the runtime-executed code: drop any
        # injected workflow prelude (re-added fresh on every dispatch) and escape
        # braces so _fill_template restores the concrete body verbatim next run.
        body = self._stripRuntimePrelude(corrected_code)
        safe_body = body.replace("{", "{{").replace("}", "}}")
        ts = time.strftime("%Y%m%d_%H%M%S")
        first_error_line = ""
        if error_detail:
            _err_lines = str(error_detail).strip().splitlines()
            first_error_line = _err_lines[0][:200] if _err_lines else ""
        header = (
            "# [runtime-fixed] Auto-revised by runtime self-correction at "
            f"{ts}.\n"
            f"# Pre-revision templates backed up under versions/runtime_fix_{ts}/.\n"
        )
        if first_error_line:
            header += f"# Fixed runtime error: {first_error_line}\n"
        new_tpl = header + safe_body
        if not new_tpl.endswith("\n"):
            new_tpl += "\n"

        # Back up the whole templates/ package once before overwriting (pre-revision).
        try:
            from SlicerAIAgentLib.cli_artifacts import snapshot_package_version
            snapshot_package_version(cli_dir, f"runtime_fix_{ts}")
        except Exception:
            logger.debug("Pre-revision template backup failed", exc_info=True)

        try:
            with open(tpl_path, "w", encoding="utf-8") as f:
                f.write(new_tpl)
        except Exception:
            logger.debug("Template write-back failed", exc_info=True)
            return

        # Keep the cross-run repair-memory learning signal (shared with generation).
        try:
            from SlicerAIAgentLib.extension_cli_analyzer.repair_memory import RepairMemory
            RepairMemory(get_cli_base_dir()).record(
                "RuntimeExecutionFailure", "runtime_api",
                str(error_detail)[:160],
                "main_agent_correction", "succeeded",
                f"step {step_id}: corrected at runtime; fix written into {tpl_rel}",
            )
        except Exception:
            logger.debug("Repair memory record for runtime repair failed", exc_info=True)

        self._recordRoleEvent("Repairer", "runtime_template_revised", {
            "extension": ext_name,
            "step_id": step_id,
            "template": tpl_rel,
        })
        logger.info(
            "Runtime fix written into template %s for %s/%s (backup: versions/runtime_fix_%s)",
            tpl_rel, ext_name, step_id, ts,
        )

    def _templateFileForStep(self, cli_dir, step_id, step_type):
        """Resolve a step's template file (relative to cli_dir) from code_generators.json.

        Interactive steps have separate pre/post templates; pick by the dispatch
        result type (``interactive`` -> pre, ``interactive_done`` -> post).
        """
        try:
            with open(os.path.join(cli_dir, "code_generators.json"), encoding="utf-8") as f:
                generators = json.load(f)
        except Exception:
            return ""
        for gen in generators if isinstance(generators, list) else []:
            if not isinstance(gen, dict):
                continue
            if gen.get("param_signature", {}).get("workflow_step") == step_id:
                if step_type == "interactive_done":
                    return gen.get("post_template_file") or ""
                if step_type == "interactive":
                    return gen.get("pre_template_file") or ""
                return (
                    gen.get("template_file")
                    or gen.get("code_template")
                    or gen.get("pre_template_file")
                    or ""
                )
        return ""

    @staticmethod
    def _stripRuntimePrelude(code):
        """Drop the runtime-injected workflow prelude from corrected code, leaving
        template-level content.

        The prelude (metadata-apply, hidden runtime globals, input guard) is
        re-added fresh on every dispatch, so it must not be baked into the saved
        template. Only acts when a distinctive prelude marker is present (the
        corrected code is usually already prelude-free); then cuts everything before
        the template's first ``import slicer``.
        """
        markers = (
            "# [Workflow metadata] Apply source-derived defaults",
            "# [Workflow runtime] Hidden generated-CLI workflow context",
            "# [Workflow preconditions]",
        )
        if not any(m in code for m in markers):
            return code
        lines = code.splitlines()
        for i, line in enumerate(lines):
            if line.strip() == "import slicer":
                return "\n".join(lines[i:])
        return code

    # ------------------------------------------------------------------
    # Structural detector for a printed-but-not-raised failure in captured
    # execution output. This replaces a bare substring test
    # (``'error' in output`` etc.) that false-positived on benign metric text
    # such as "Screw 1 alignment error: 0.0000 mm" or "0 errors" — which used
    # to drag a fully-successful run into an endless self-correction loop.
    #
    # Every signal is structural/typographic, NOT a domain word blacklist, and
    # capitalization is used as a discriminator on purpose: Python exception
    # classes are CamelCase and log levels are uppercase, so lowercasing (what
    # the old net did) is exactly what made "alignment error:" collide with
    # "ValueError:". Feed these the ORIGINAL-CASE, VTK-stripped output.
    # ------------------------------------------------------------------

    # A Python traceback header, plus the two chained-exception connector lines.
    _PRINTED_TRACEBACK_RE = re.compile(
        r'^\s*(?:Traceback \(most recent call last\):'
        r'|During handling of the above exception,'
        r'|The above exception was the direct cause)',
        re.MULTILINE,
    )
    # An exception repr anchored at line start: a (possibly dotted) identifier
    # whose final component ends in ``Error``/``Exception``, immediately followed
    # by a colon — e.g. "ValueError:", "slicer.util.MRMLNodeNotFoundException:".
    # "Screw 1 alignment error:" cannot anchor here: the identifier must run
    # unbroken from the line start, and the spaces before "error" break it.
    _PRINTED_EXCEPTION_LINE_RE = re.compile(
        r'^\s*[A-Za-z_][\w.]*(?:Error|Exception):', re.MULTILINE,
    )
    # Explicit failure sigils: cross/ballot glyphs (❌ ✗ ✘, given as codepoint
    # escapes so source encoding is irrelevant), and bracketed or
    # colon-terminated UPPERCASE log levels (uppercase distinguishes a log level
    # from the lowercase noun in "reprojection error: 0.3").
    _PRINTED_FAILURE_SIGIL_RE = re.compile(
        r'[❌✗✘]'  # cross/ballot marks: ❌ ✗ ✘
        r'|\[(?:ERROR|FATAL|CRITICAL)\]'
        r'|(?:^|\s)(?:ERROR|FATAL|CRITICAL):',
        re.MULTILINE,
    )

    @classmethod
    def _outputIndicatesFailure(cls, output):
        """True iff captured stdout/stderr shows a printed-but-not-raised failure.

        Secondary net only — genuinely raised exceptions already surface as
        ``result['success'] == False`` and are handled on that branch. Pass the
        ORIGINAL-CASE, VTK-stripped output. Fail-open (returns False on any
        internal error) so a detector bug can never fabricate a failure and
        re-arm self-correction on a successful run.
        """
        if not output:
            return False
        try:
            return bool(
                cls._PRINTED_TRACEBACK_RE.search(output)
                or cls._PRINTED_EXCEPTION_LINE_RE.search(output)
                or cls._PRINTED_FAILURE_SIGIL_RE.search(output)
            )
        except Exception:
            return False

    def _autoExecuteCodeConfirmed(self, attempt=1, max_attempts=5):
        """Run already-validated code after optional confirmation has passed."""
        import time

        self._setAgentStatus("Executor", f"Executing (attempt {attempt}/{max_attempts})...")
        slicer.app.processEvents()

        if self._timing and 'execution_start' not in self._timing:
            self._timing['execution_start'] = time.time()
        if self._timing:
            self._timing['execution_async_call'] = time.time()

        self._recordRoleEvent("Executor", "execution_scheduled", {
            "attempt": attempt,
            "code_chars": len(self.currentCode or ""),
        })

        # Capture scene state BEFORE execution for semantic verification
        before_snapshot = None
        if hasattr(self, 'buildSceneSnapshot'):
            try:
                before_snapshot = self.buildSceneSnapshot()
            except Exception as e:
                logger.warning(f"Failed to build pre-execution scene snapshot: {e}")

        def onExecutionComplete(result):
            if self._timing:
                self._timing['execution_callback_start'] = time.time()
            feedback_lines = []
            output_has_errors = False
            step_info = getattr(self, '_currentWorkflowStepInfo', None)
            runtime_managed = bool(self._workflowRuntime and self._workflowRuntime.session and step_info)
            self._recordRoleEvent("Executor", "execution_completed", {
                "success": result.get("success"),
                "timed_out": result.get("timed_out", False),
                "execution_time": result.get("execution_time", 0),
                "error": result.get("error"),
            })
            if result.get("timed_out", False):
                self._setReadyStatus()
                output = result.get('output', 'No output')
                exec_time = result.get('execution_time', 30)
                msg = f"Code execution timed out after {exec_time:.1f}s."
                if output:
                    msg += f"\nOutput: {output}"
                self.appendToChat("Warning", msg)
                if runtime_managed:
                    self._updateWorkflowPanel({
                        "active": True,
                        "workflow_title": self._currentWorkflowUiState.get("workflow_title", "Workflow"),
                        "status": "Failed",
                        "description": msg,
                        "total_steps": self._currentWorkflowUiState.get("total_steps", 0),
                        "completed_steps": self._currentWorkflowUiState.get("completed_steps", 0),
                        "current_index": self._currentWorkflowUiState.get("current_index", 0),
                        "can_cancel": True,
                    })
                feedback_lines.append(f"Status: timed_out\nExecution time: {exec_time:.1f}s\nOutput: {output}")
            elif result["success"]:
                output = result.get('output', 'No output')
                execution_time = result.get('execution_time', 0)
                msg = f"Code executed successfully in {execution_time:.2f}s."
                if output:
                    msg += f"\nOutput: {output}"
                if not runtime_managed:
                    self.appendToChat("System", msg)
                feedback_lines.append(f"Status: success\nExecution time: {execution_time:.2f}s\nOutput: {output}")
                # Detect a printed-but-not-raised failure. A genuinely raised
                # exception already surfaces as success=False (handled below);
                # this is only a SECONDARY net. Strip VTK output lines first
                # (they carry "error" in benign messages) but KEEP original case,
                # then use the structural detector — a bare substring match on
                # "error"/"failed" false-positives on benign metric text like
                # "Screw 1 alignment error: 0.0000 mm", which used to drag a
                # successful run into an endless self-correction loop.
                non_vtk_output = "\n".join(
                    line for line in output.split("\n")
                    if not line.strip().startswith("[VTK")
                )
                if self._outputIndicatesFailure(non_vtk_output):
                    output_has_errors = True
                    feedback_lines.append("Warning: execution output contains error indicators even though no uncaught exception was raised.")
                self._lastExecutionResult = dict(result)
                self._lastOutputHasErrors = output_has_errors
                # Re-assert the chosen scalar volume as the slice background after
                # this workflow step. Extension steps (e.g. "Create bone models")
                # re-run the extension's enter()/GUI sync, which can default-select
                # the first volume (the fibula) and leave the user's chosen volume
                # unshown. This puts the chosen volume back — background layer only,
                # so interaction handles/lock state are untouched.
                if runtime_managed:
                    self._applyChosenVolumeBackground()
                # Closed loop: a successful correction of a generated workflow
                # step is persisted back to the CLI package so the next
                # revision/regeneration learns from it instead of every future
                # session re-paying the same runtime failure + correction.
                if (
                    attempt > 1
                    and runtime_managed
                    and isinstance(step_info, dict)
                    and step_info.get("origin") == "generated_template"
                ):
                    try:
                        self._persistGeneratedTemplateRepair(
                            step_info,
                            self.currentCode or "",
                            getattr(self, "_lastCorrectionError", ""),
                        )
                    except Exception:
                        logger.debug("Runtime-repair feedback failed", exc_info=True)
            else:
                # Execution failed
                error_msg = result.get('error', 'Unknown error')
                if "[GeneratedWorkflowPrecondition]" in error_msg:
                    result["failure_category"] = "generated_workflow_precondition"
                    self._recordRoleEvent("SafetyCritic", "generated_precondition_failed", {
                        "error": error_msg[:1000],
                    })
                execution_time = result.get('execution_time', 0)
                msg = f"Execution failed (attempt {attempt}/{max_attempts}).\nError: {error_msg[:200]}"
                self.appendToChat("System", msg)
                feedback_lines.append(f"Status: failed\nExecution time: {execution_time:.2f}s\nError: {error_msg[:500]}")
                self._lastExecutionResult = dict(result)
                self._lastOutputHasErrors = True

            # Semantic scene verification: compare before/after snapshots against agent_plan expectations
            if result.get("success") and not result.get("timed_out", False) and before_snapshot:
                try:
                    if hasattr(self, 'buildSceneSnapshot') and hasattr(self, 'verifySceneAgainstPlan'):
                        after_snapshot = self.buildSceneSnapshot()
                        plan = getattr(self, 'currentAgentPlan', None)
                        if plan:
                            verification = self.verifySceneAgainstPlan(before_snapshot, after_snapshot, plan)
                            if not verification.get("valid", True):
                                output_has_errors = True
                                verr = "; ".join(verification.get("errors", []))
                                feedback_lines.append(f"Scene verification failed: {verr}")
                                self.appendToChat("System", f"Scene verification failed: {verr}")
                                self._recordRoleEvent("SafetyCritic", "scene_verification_failed", {
                                    "errors": verification.get("errors", []),
                                    "warnings": verification.get("warnings", []),
                                    "diagnostics": verification.get("diagnostics", []),
                                })
                            elif verification.get("warnings"):
                                self._recordRoleEvent("SafetyCritic", "scene_verification_warnings", {
                                    "warnings": verification.get("warnings", []),
                                })
                except Exception as e:
                    logger.warning(f"Scene verification raised exception: {e}")

            # Add execution feedback to conversation history
            if self.logic:
                feedback_text = "Code execution result:\n" + "\n".join(feedback_lines) + "\nThe MRML scene has been updated. Refer to the CURRENT SLICER SCENE in the next system prompt for the complete raw MRML."
                self.logic.addExecutionFeedback(feedback_text)

            # Record execution timing
            if self._timing:
                self._timing['execution_end'] = time.time()
                self._timing['execution_result'] = 'success' if result.get('success') else 'failed'
                # Record executor internal timing
                if 'executor_scheduled' in result:
                    self._timing['executor_scheduled'] = result['executor_scheduled']
                if 'executor_actual_start' in result:
                    self._timing['executor_actual_start'] = result['executor_actual_start']
                self._writeTimingReport()

            if result.get("success") and runtime_managed:
                updated_step = self._workflowRuntime.handle_execution_result(step_info, result)
                self._currentWorkflowStepInfo = updated_step
                self._applyWorkflowDisplayProperties(updated_step)
                self._updateWorkflowPanel(updated_step)
                if updated_step.get("type") in ("interactive", "mixed"):
                    self._recordRoleEvent("Workflow", "entering_wait", {
                        "step_id": updated_step.get("step_id"),
                    })
                    self._streamQueue.put(('workflow_wait', updated_step))
                    return
                if updated_step.get("type") == "user_choice":
                    self._displayWorkflowChoice(updated_step)
                    self._setReadyStatus()
                    self.sendButton.setEnabled(True)
                    return
                next_step = updated_step.get("next_step")
                if next_step:
                    completed_step_id = updated_step.get("step_id", "")
                    self._updateWorkflowPanel(self._workflowRuntime.state_for_ui(updated_step))
                    self._autoAdvanceWorkflowStep = next_step
                elif updated_step.get("workflow_completed"):
                    self._updateWorkflowPanel(updated_step)
                    self.appendToChat("System", "Generated CLI workflow complete.")
                    self._clearCompletedWorkflowState()
                    self._flushQueuedWorkflowPrompts()

            # Interactive workflow detection: if an interactive step just executed,
            # transition to waiting_for_user and enter wait mode.
            if (result.get("success")
                and self._workflowOrchestrator
                and self._activeWorkflowId
                and self._workflowOrchestrator.is_workflow_active()
                and not runtime_managed):
                wf_state = self._workflowOrchestrator._get_state(self._activeWorkflowId)
                if wf_state and wf_state.status == "running":
                    step_info = getattr(self, '_currentWorkflowStepInfo', None)
                    if step_info and step_info.get("type") in ("interactive", "mixed"):
                        # Apply display properties before entering wait state
                        self._applyWorkflowDisplayProperties(step_info)
                        wf_state.status = "waiting_for_user"
                        self._recordRoleEvent("Workflow", "entering_wait", {
                            "step_id": wf_state.current_step,
                        })
                        self._streamQueue.put(('workflow_wait', step_info))
                        return
                    # user_choice steps: no UI state change — the LLM handles the
                    # question/answer via normal chat turns. Just keep chat enabled.
                    if step_info and step_info.get("type") == "user_choice":
                        wf_state.status = "waiting_for_choice"
                        self._recordRoleEvent("Workflow", "waiting_for_choice", {
                            "step_id": wf_state.current_step,
                        })
                        self._displayWorkflowChoice(step_info)
                    # Automated step completed — auto-advance to next step
                    if step_info and step_info.get("type") == "repeat_next":
                        next_step = step_info.get("next_step")
                        if next_step:
                            self._updateWorkflowPanel(step_info)
                            self._autoAdvanceWorkflowStep = next_step
                    elif step_info and step_info.get("type") in (
                        "automated", "skipped", "choice_made",
                        "interactive_done", "mixed_done",
                    ):
                        # Apply display properties for automated steps
                        self._applyWorkflowDisplayProperties(step_info)
                        completed_step_id = step_info.get("step_id", "")
                        # Mark current step complete in both tracking systems
                        from SlicerAIAgentLib.ExtensionCLILoader import _find_next_step_local, _workflow_completed_steps
                        done = _workflow_completed_steps.setdefault(step_info.get("tool", ""), set())
                        done.add(completed_step_id)
                        # Also mark in WorkflowOrchestrator's state so
                        # complete_interaction()/_find_next_step stays in sync
                        if self._activeWorkflowId:
                            wf_st = self._workflowOrchestrator._get_state(self._activeWorkflowId)
                            if wf_st and completed_step_id not in wf_st.completed_steps:
                                wf_st.completed_steps.append(completed_step_id)
                            # Advance current_step so prompt fragment doesn't advertise the skipped step
                            if wf_st and step_info.get("type") == "skipped":
                                wf_st.current_step = None
                        # Load workflow graph for next-step lookup
                        try:
                            import os, json
                            from SlicerAIAgentLib.ExtensionCLILoader import get_cli_base_dir
                            ext_name = step_info.get("tool", "")
                            wf_path = os.path.join(get_cli_base_dir(), ext_name, "workflow.json")
                            if os.path.isfile(wf_path):
                                with open(wf_path) as wf_f:
                                    wf_graph = json.load(wf_f)
                                next_step = _find_next_step_local(wf_graph, done)
                                if next_step:
                                    self._updateWorkflowPanel(step_info)
                                    # Trigger a new turn with the next step
                                    self._autoAdvanceWorkflowStep = next_step
                                elif step_info.get("type") == "skipped":
                                    # No more steps after the skipped one — end the workflow
                                    if wf_st:
                                        wf_st.status = "completed"
                                    self._updateWorkflowPanel({
                                        "active": True,
                                        "workflow_title": step_info.get("tool", "Workflow"),
                                        "status": "Completed",
                                        "description": "Workflow complete.",
                                        "can_done": False,
                                        "can_skip": False,
                                        "can_cancel": False,
                                    })
                                    self._clearCompletedWorkflowState()
                        except Exception as e:
                            logger.warning(f"Workflow auto-advance failed: {e}")

            # Self-correction for failures or suspicious outputs (but not timeouts)
            # Skip self-correction during active workflow steps that succeeded —
            # VTK noise should not derail the workflow sequence.
            workflow_active = (
                (
                    self._workflowRuntime
                    and self._workflowRuntime.has_active_workflow()
                )
                or (
                    self._workflowOrchestrator
                    and self._activeWorkflowId
                    and self._workflowOrchestrator.is_workflow_active()
                )
            )
            # ``runtime_managed`` was snapshotted at callback entry, BEFORE the
            # workflow-completed branch above ran _clearCompletedWorkflowState().
            # On the FINAL workflow step, handle_execution_result flips the
            # session to "completed" (so workflow_active is already False here),
            # yet the step is still a workflow-managed one that merely succeeded.
            # Without this term, a benign "…error…" line in the final step's own
            # output would satisfy ``output_has_errors and not workflow_active``
            # and drive a spurious self-correction loop after the workflow is
            # done. A genuine failure still corrects: result["success"] is False
            # then, which short-circuits the OR regardless of runtime_managed.
            if not result.get("timed_out", False) and (
                not result["success"]
                or (output_has_errors and not workflow_active and not runtime_managed)
            ):
                if attempt < max_attempts:
                    self.appendToChat("System", "Auto-correcting...")
                    error_for_correction = result.get('error', '')
                    if not error_for_correction and output_has_errors:
                        # success=True but output contains clear failure keywords
                        error_for_correction = "\n".join(feedback_lines) or output

                    # Revision D: triage by failure type. If the failing code
                    # came from a generated CLI template AND the error is
                    # syntax/name-level (i.e. a generator-side bug), skip the
                    # LLM repair loop — it can't see the generator, so it
                    # would burn ~100s looking for a fix that has to come
                    # from regenerating the CLI. Fall through to repair on
                    # runtime/scene errors or any ambiguity.
                    step_info_for_triage = getattr(self, '_currentWorkflowStepInfo', None) or {}
                    if self._shouldSkipSelfCorrectionForGeneratedTemplate(
                        step_info_for_triage, error_for_correction,
                    ):
                        self._handleGeneratedTemplateGeneratorBug(
                            step_info_for_triage, error_for_correction,
                        )
                        return

                    self._recordRoleEvent("Repairer", "correction_requested", {
                        "attempt": attempt + 1,
                        "reason": error_for_correction[:1000] if error_for_correction else "",
                    })
                    self._selfCorrectCode(error_for_correction, attempt, max_attempts)
                else:
                    final_error = result.get('error', 'Unknown error') if not result["success"] else "Output contains errors"
                    if getattr(self, "_taskWorkflowPanelActive", False):
                        self._updateWorkflowPanel({
                            "active": True,
                            "mode": "task",
                            "workflow_title": "Task",
                            "status": "Failed",
                            "description": str(final_error),
                            "instructions": "Generated code and execution details are available in Debug.",
                            "total_steps": 0,
                            "can_done": False,
                            "can_skip": False,
                            "can_cancel": False,
                        })
                        self._taskWorkflowPanelActive = False
                    self._setReadyStatus()
                    self.appendToChat("Error",
                        f"Execution failed after {max_attempts} attempts.\n"
                        f"Final error: {final_error}")
                    self._recordRoleEvent("Repairer", "max_attempts_reached", {
                        "attempts": max_attempts,
                        "final_error": final_error,
                    })
                    self._saveRoleTraceToFile()
            else:
                self._recordRoleEvent("Executor", "task_completed", {
                    "execution_success": result.get("success"),
                })
                self._saveRoleTraceToFile()

                # Auto-advance workflow: if an automated step just completed and
                # there's a next step queued, trigger it automatically.
                next_step = getattr(self, '_autoAdvanceWorkflowStep', None)
                if next_step and result.get("success"):
                    self._autoAdvanceWorkflowStep = None
                    tool_name = next_step.get("step_id", "")
                    # Use a timer to schedule the next step as a new user-like turn
                    step_id = next_step["step_id"]
                    # Schedule the auto-advance on the Qt main thread
                    qt.QTimer.singleShot(100, lambda: self._autoAdvanceNextStep(next_step))
                else:
                    self._setReadyStatus()

        # Apply per-step prelude globals (workflow metadata as Python objects)
        # so the new compact prelude can reference _workflow_choices etc.
        # without round-tripping them through source text.
        self._applyPreludeGlobals()

        # Keep the agent IN its own module. Generated steps carry a
        # `selectModule('<Ext>')` precondition (only there to fire the extension's
        # enter() lifecycle); executing it makes the extension the active module,
        # and SafeExecutor's restore then switches back — firing the extension's
        # exit(), which for BoneReconstructionPlanner HIDES the plane interaction
        # handles and LOCKS the planes (BoneReconstructionPlanner.py exit(), lines
        # ~500-504). That breaks later interactive adjustment (step 29). So fire
        # enter() once invisibly and strip the switch, so exit() never runs.
        exec_code = self._prepareGeneratedStepCode(self.currentCode)

        # Execute asynchronously
        self.logic.executeCodeAsync(exec_code, onExecutionComplete)

    def _prepareGeneratedStepCode(self, code):
        """Strip a generated step's module-switch precondition (and fire the
        extension's enter() once, invisibly), so the active module never changes
        and the extension's exit() lifecycle never runs.

        The precondition is a marker-delimited block that runs
        `slicer.util.selectModule('<Ext>')` purely to trigger the extension
        module's enter(). We extract the module name from it, fire enter() once
        per session WITHOUT switching the visible/active module, then remove the
        block. Code without the marker is returned unchanged.
        """
        if not isinstance(code, str) or "# precondition:begin" not in code:
            return code
        try:
            match = re.search(r"selectModule\(\s*['\"]([^'\"]+)['\"]\s*\)", code)
            if match:
                self._ensureModuleEnteredInvisibly(match.group(1))
            stripped = re.sub(
                r"[ \t]*#\s*precondition:begin.*?#\s*precondition:end[ \t]*\n?",
                "",
                code,
                flags=re.DOTALL,
            )
            return stripped
        except Exception:
            logger.debug("Precondition strip failed; running code as-is", exc_info=True)
            return code

    def _ensureModuleEnteredInvisibly(self, module_name):
        """Fire a module's enter() lifecycle once per session WITHOUT switching
        the visible/active module.

        `getModuleWidget` creates/sets up the module's widget without showing it;
        calling enter() on it runs the extension's setup (parameter node, plane
        observers) so its steps behave as after a normal entry. Crucially, because
        the active module never changes, Slicer never calls the extension's exit()
        — so it never tears down the interaction handles / lock state. Fail-open:
        if enter() cannot run out of context, the step's own logic usually copes.
        """
        if not module_name:
            return
        entered = getattr(self, "_invisiblyEnteredModules", None)
        if entered is None:
            entered = self._invisiblyEnteredModules = set()
        if module_name in entered:
            return
        # Mark first so a partial failure never retries on every step.
        entered.add(module_name)
        try:
            module_widget = slicer.util.getModuleWidget(module_name)
            if module_widget is not None and hasattr(module_widget, "enter"):
                module_widget.enter()
                logger.info(
                    "[Workflow] Fired %s.enter() without switching the active module",
                    module_name,
                )
        except Exception:
            logger.debug(
                "Invisible enter() failed for %s (continuing without it)",
                module_name, exc_info=True,
            )

    def _applyPreludeGlobals(self):
        """Inject the current workflow step's _prelude_globals into __main__.

        The dispatch result attaches ``_prelude_globals`` (a dict of Python
        objects: choices/bindings/defaults/required_bindings) when the new
        compact prelude would otherwise reference them as undefined names.
        This registers each key on the executor's __main__ namespace before
        exec, then schedules cleanup so stale metadata from step N doesn't
        leak into step N+1.
        """
        try:
            executor = getattr(self.logic, 'executor', None)
            if executor is None or not hasattr(executor, 'addGlobal'):
                return
        except Exception:
            return

        step_info = getattr(self, '_currentWorkflowStepInfo', None) or {}
        prelude_globals = step_info.get('_prelude_globals') if isinstance(step_info, dict) else None
        if not isinstance(prelude_globals, dict):
            prelude_globals = {}

        # Cleanup-on-entry: remove keys injected by the previous step so they
        # don't leak across steps. Tracked in self._lastInjectedPreludeKeys.
        previous_keys = getattr(self, '_lastInjectedPreludeKeys', None) or []
        for key in previous_keys:
            try:
                executor.removeGlobal(key)
            except Exception:
                pass

        if not prelude_globals:
            self._lastInjectedPreludeKeys = []
            return

        for key, value in prelude_globals.items():
            try:
                executor.addGlobal(key, value)
            except Exception:
                pass
        self._lastInjectedPreludeKeys = list(prelude_globals.keys())

    # ================================================================
    # Revision D: Self-correction triage for generated CLI templates
    # ================================================================

    # Substrings that signal a runtime/scene error even when the code parses
    # cleanly. Their presence biases the classifier away from "syntax_or_name".
    _GENERATED_TEMPLATE_RUNTIME_ERROR_MARKERS = (
        "[GeneratedWorkflowPrecondition]",
        "Missing required node reference",
        "Missing conditional node reference",
        "RuntimeError",
        "ValueError",
        "AttributeError",
        "TypeError",
        "vtkMRML",
        "slicer.mrmlScene",
        "GetParameterNode",
        "Node reference",
    )

    def _classifyExecutionError(self, error_msg: str, code: str) -> str:
        """Classify an execution error for self-correction triage.

        Returns one of:
            ``"syntax_or_name"`` — code failed to parse, or execution raised
                a Python-level ``NameError``/``SyntaxError``. Suggests a
                generator-side bug for generated-template code.
            ``"runtime_or_scene"`` — code parsed fine but raised a runtime/
                scene error (missing node, bad VTK call, etc.). The existing
                LLM repair path can handle these.
            ``"other"`` — ambiguous; caller should fall through to existing
                repair to avoid blocking on uncertain classification.
        """
        if not error_msg:
            return "other"
        lowered = error_msg.lower()
        # Strong syntax/name signals — note that NameError's actual message
        # text is ``name 'X' is not defined`` (no exception type name), so we
        # also match that pattern directly. This catches the JSON-vs-Python
        # boolean bug class (``name 'false' is not defined``).
        import re as _re
        name_error_pattern = _re.compile(r"name\s+['\\\"][^'\"]+['\\\"]\s+is\s+not\s+defined")
        syntax_signals = (
            "syntaxerror" in lowered
            or "nameerror" in lowered
            or "indentationerror" in lowered
            or name_error_pattern.search(lowered) is not None
        )
        if syntax_signals:
            # But runtime errors sometimes mention these names too — confirm
            # the runtime markers aren't present before classifying as syntax.
            for marker in self._GENERATED_TEMPLATE_RUNTIME_ERROR_MARKERS:
                if marker.lower() in lowered:
                    return "runtime_or_scene"
            return "syntax_or_name"

        # ast.parse as a secondary signal: code that won't parse at all is
        # definitely syntax-level. (Generator bugs that produce unparseable
        # output land here.)
        if code:
            try:
                import ast as _ast
                _ast.parse(code)
            except (SyntaxError, IndentationError, ValueError):
                return "syntax_or_name"

        # Explicit runtime/scene markers
        for marker in self._GENERATED_TEMPLATE_RUNTIME_ERROR_MARKERS:
            if marker.lower() in lowered:
                return "runtime_or_scene"

        return "other"

    def _shouldSkipSelfCorrectionForGeneratedTemplate(
        self,
        step_info: dict,
        error_msg: str,
    ) -> bool:
        """Return True iff the failing code came from a generated CLI
        template AND the error is a generator-side syntax/name bug.

        Conservative: returns False (proceed with existing repair) on any
        ambiguity, on non-generated-template code, or on runtime/scene errors.
        """
        if not isinstance(step_info, dict):
            return False
        if step_info.get("origin") != "generated_template":
            return False
        code = self.currentCode or ""
        classification = self._classifyExecutionError(error_msg or "", code)
        return classification == "syntax_or_name"

    def _handleGeneratedTemplateGeneratorBug(
        self,
        step_info: dict,
        error_msg: str,
    ):
        """Surface a structured 'regenerate the CLI' error and cancel the workflow.

        Called when self-correction is skipped for a generated-template syntax
        error. The LLM repair path can't see the generator, so this would have
        been wasted effort. Instead we tell the user to regenerate the CLI.
        """
        step_id = (step_info or {}).get("step_id", "<unknown>")
        ext_name = (step_info or {}).get("tool", "<unknown>")
        # tool name is usually ``<ExtensionName>`` — strip a trailing suffix
        # if present.
        message = (
            f"CLI generator produced invalid code for step '{step_id}'. "
            f"This is a bug in the generation pipeline, not a runtime scene "
            f"issue. Original error: {error_msg or 'unknown'}. "
            f"Please regenerate the {ext_name} CLI."
        )
        self.appendToChat("Error", message)
        self._setReadyStatus()
        try:
            self.sendButton.setEnabled(True)
        except Exception:
            pass
        self._recordRoleEvent("Repairer", "generator_bug_detected", {
            "step_id": step_id,
            "extension": ext_name,
            "error": (error_msg or "")[:1000],
            "skipped_self_correction": True,
        })
        try:
            self._saveRoleTraceToFile()
        except Exception:
            pass
