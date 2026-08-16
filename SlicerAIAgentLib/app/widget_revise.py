"""Revise the step in front of you: the ✎ button beside the microphone.

The Qt half of :mod:`SlicerAIAgentLib.TemplateReviser`. While a guided workflow
is open, ✎ hands the prompt box and Send to a revision agent instead of to the
pipeline: the user describes what the step on screen should have done, and one
step's ``.tpl`` is rewritten, checked, and written into the package with its
predecessor kept under ``versions/revision_<ts>/``.

It reuses the runtime's own repair machinery rather than inventing a second one.
The call is ``chatWithToolsIsolated`` with the built-in search tools and the
generated-CLI schemas stripped -- the same shape ``_selfCorrectCode`` uses, and
for the same reason: a revision must be able to read the extension's source
through ``ext:`` before it writes a call, but it must not be able to *dispatch* a
workflow step while doing so. The result goes through the same CodeValidator, and
the re-run goes through the existing ``▷ Run from here``.

Four seams are shared with the baseline harness, and this mixin copies each
deliberately rather than approximating it:

* it sits ahead of ``WidgetSendMixin`` in the MRO and overrides
  ``onSendButtonClicked`` / ``onPromptTextChanged`` with a single
  ``if not engaged: super()`` guard;
* ``_guidedWorkflowOwnsInput`` learns about it, or the guided workflow keeps the
  prompt box switched off and the mode looks dead;
* *intent* (``_reviseActive``) and *engagement* (``_reviseEngaged``) stay two
  different things, so the row cannot vanish under a running revision;
* the debug write context is moved for the duration and handed back on every
  exit path, so a revision's transcript never mixes with the pipeline's.

The two modes are mutually exclusive: engaging one disengages the other. Both
rewrite Send's caption and restore it from a value captured at setup, and two
owners of one button is how a caption gets left behind.
"""

import time

from .common import *

from .. import TemplateReviser


class WidgetReviseMixin:

    # TEXT, not an icon. Slicer core ships no pencil at a path that is reliably
    # registered, and `qt.QIcon(":/Icons/…")` on an unregistered path returns a
    # NULL icon rather than raising -- which renders as a button with nothing in
    # it. The baseline toggle is text-only "⚖" for the same reason, and it also
    # makes ✎ read as a different kind of control from the icon buttons around
    # it. BMP, never an emoji: an emoji renders as a tofu box on some Windows
    # font stacks (see the microphone's own note).
    _REVISE_GLYPH = "✎"

    #: Deliberately NOT baseline's amber (#e08a00). Both modes recolour the same
    #: button, and two modes that look alike are worse than two that look
    #: nothing alike -- Send doing something other than sending is the whole
    #: signal.
    _REVISE_SEND_STYLE = (
        "QPushButton { background-color: #6a4c93; color: white; border: none; "
        "font-weight: bold; border-radius: 4px; } "
        "QPushButton:hover { background-color: #553c76; } "
        "QPushButton:disabled { background-color: #cccccc; }"
    )
    _REVISE_SEND_TEXT = "Revise\nstep"

    _REVISE_TIP = (
        "Revise this step's generated code.\n"
        "Describe what the step should have done and press Revise; the step's "
        "template is rewritten and the original kept under versions/."
    )

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setupReviseControls(self):
        """Build the ✎ button and its status row. Never raises.

        Called from ``setup()`` AFTER ``_setupVoiceControls`` -- the button is
        anchored on the column that method builds, so before it there is nothing
        to sit beside -- and before ``_relaxContentWidth``, so the status label
        is swept by it and cannot widen Slicer's module panel.
        """
        try:
            self._insertReviseButtonBesideVoice()
        except Exception:
            logger.debug("Revise button insertion failed", exc_info=True)
        try:
            self._insertReviseRowAboveInput()
        except Exception:
            logger.debug("Revise status row insertion failed", exc_info=True)

    def _insertReviseButtonBesideVoice(self):
        """Put ✎ next to the microphone, above Send.

        The mic already took Send's slot in ``inputLayout`` and lives in a
        QVBoxLayout column holding ``[mic, sendButton]``, so this converts that
        column's top slot into a ``[mic][revise]`` row. Nothing here detaches
        Send: losing this button is a missing feature, losing Send is a broken
        module, and the voice insertion already carries that risk once.

        When the voice column does not exist -- its whole builder is best-effort
        and returns early if the input row cannot be found -- the button is
        inserted straight above Send instead, so ✎ does not depend on voice
        control having worked.
        """
        if getattr(self, "_reviseButton", None) is not None:
            return
        send = getattr(self, "sendButton", None)
        if send is None:
            return

        button = qt.QToolButton()
        button.setText(self._REVISE_GLYPH)
        button.setCheckable(True)
        button.setAutoRaise(True)
        button.setToolTip(self._REVISE_TIP)
        button.clicked.connect(self._onReviseToggleClicked)
        try:
            # Icon-only and Fixed, for the same reason the mic and Send are:
            # a caption's width joins the row's permanent minimum.
            button.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        except Exception:
            logger.debug("Revise button size policy failed", exc_info=True)

        column = getattr(self, "_voiceButtonColumn", None)
        mic = getattr(self, "_voiceButton", None)
        placed = False
        if column is not None and mic is not None:
            index = column.indexOf(mic)
            if index >= 0:
                column.removeWidget(mic)
                try:
                    row = qt.QHBoxLayout()
                    row.setContentsMargins(0, 0, 0, 0)
                    row.setSpacing(2)
                    # The two stretches reproduce the AlignHCenter the mic had
                    # when it was the column's only widget.
                    row.addStretch(1)
                    row.addWidget(mic)
                    row.addWidget(button)
                    row.addStretch(1)
                    column.insertLayout(index, row)
                    placed = True
                except Exception:
                    logger.debug("Revise/mic row failed; restoring the mic",
                                 exc_info=True)
                    try:
                        mic.setParent(None)
                        column.insertWidget(index, mic, 0, qt.Qt.AlignHCenter)
                    except Exception:
                        logger.error("Could not restore the microphone button "
                                     "after a failed revise insertion",
                                     exc_info=True)
                    return

        if not placed:
            # No voice column (voice setup bailed out): stack ✎ above Send in
            # whatever layout Send is in.
            parent_layout = send.parent().layout() if send.parent() else None
            target = self._inputRowLayout()
            layout = target if target is not None else parent_layout
            if layout is None:
                return
            index = layout.indexOf(send)
            if index < 0:
                index = layout.count()
            try:
                layout.insertWidget(index, button, 0, qt.Qt.AlignHCenter)
            except Exception:
                logger.debug("Revise button fallback insertion failed",
                             exc_info=True)
                return

        self._reviseButton = button
        # Visible from the moment the panel is built, like the microphone beside
        # it. It used to start hidden and be revealed by `_updateReviseControls`
        # — but that runs only from `_updateReplayControls`, i.e. only when the
        # workflow panel repaints, so before any procedure started there was no
        # button at all and the feature looked missing. Disabled-with-a-reason is
        # discoverable; absent is not.
        button.setEnabled(False)
        button.setToolTip(
            "Revise this step's generated code.\n"
            "Available while a guided procedure is running: step to the step "
            "that behaved wrongly, press this, and describe what it should "
            "have done."
        )

        # Capture Send's untouched look ONCE, before any mode has changed it, so
        # exiting restores the original rather than whatever the other mode left.
        try:
            self._reviseSendText = str(send.text)
            self._reviseSendStyle = str(send.styleSheet)
        except Exception:
            self._reviseSendText, self._reviseSendStyle = "Send", ""

    def _inputRowLayout(self):
        """The bare QHBoxLayout holding promptInput, located structurally.

        It has no objectName in the .ui and none at all in the programmatic
        fallback, so ``indexOf`` on the outer layout cannot find it. Same search
        as ``_insertVoiceButtonAboveSend`` / ``_insertBaselineRowAboveInput``.
        """
        prompt = getattr(self, "promptInput", None)
        if prompt is None:
            return None
        parent = prompt.parent()
        outer = parent.layout() if parent is not None else None
        if outer is None:
            return None
        for index in range(outer.count()):
            item = outer.itemAt(index)
            sub = item.layout() if item is not None else None
            if sub is not None and sub.indexOf(prompt) >= 0:
                return sub
        return None

    def _insertReviseRowAboveInput(self):
        """One wordwrapped status line above the input row, hidden until armed.

        A revision takes tens of seconds and does most of its work searching, so
        it needs somewhere to say so. The Debug group's conversation view is
        collapsed by default, which makes it the wrong place for the only
        feedback a user has that anything is happening.
        """
        if getattr(self, "_reviseRow", None) is not None:
            return
        prompt = getattr(self, "promptInput", None)
        if prompt is None:
            return

        row = qt.QWidget()
        layout = qt.QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        caption = qt.QLabel("Revise:")
        caption.setStyleSheet("font-weight: bold; color: #6a4c93;")
        layout.addWidget(caption)
        self._reviseInfoLabel = qt.QLabel("")
        self._reviseInfoLabel.setWordWrap(True)
        # setMinimumWidth(0) and NOTHING else, exactly as `_baselineInfoLabel`
        # is treated. `_applyBaselineWidthPolicy` REPLACES a widget's size
        # policy, and QLabel implements word wrap by setting heightForWidth on
        # its own policy -- overwriting it after setWordWrap(True) throws the
        # wrapped height away and the label reports a single line. This label is
        # the mode's only feedback, and its longest messages are the ones that
        # matter most ("nothing was changed", "NOT FULLY APPLIED ... restore
        # with versions/...").
        try:
            self._reviseInfoLabel.setMinimumWidth(0)
        except Exception:
            logger.debug("Revise label width failed", exc_info=True)
        layout.addWidget(self._reviseInfoLabel, 1)

        parent = prompt.parent()
        parent_layout = parent.layout() if parent is not None else None
        if parent_layout is None:
            return
        target = parent_layout.count()
        for index in range(parent_layout.count()):
            item = parent_layout.itemAt(index)
            sub = item.layout() if item is not None else None
            if sub is not None and sub.indexOf(prompt) >= 0:
                target = index
                break
        try:
            parent_layout.insertWidget(target, row)
        except Exception:
            parent_layout.addWidget(row)
        row.setVisible(False)
        self._reviseRow = row

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def _reviseBusy(self):
        """True while a revision round is in the API or being applied."""
        return bool(getattr(self, "_reviseActiveRun", None))

    def _reviseTargetStepId(self, state=None):
        """The step ✎ acts on: the previewed one, else the live one."""
        runtime = getattr(self, "_workflowRuntime", None)
        session = getattr(runtime, "session", None) if runtime else None
        if session is None:
            return ""
        index = session.preview_index
        if index is not None and 0 <= index < len(session.checkpoints):
            return session.checkpoints[index].step_id
        state = state or getattr(self, "_currentWorkflowUiState", {}) or {}
        return str(state.get("current_step") or session.current_step or "")

    def _reviseExtensionName(self):
        runtime = getattr(self, "_workflowRuntime", None)
        session = getattr(runtime, "session", None) if runtime else None
        return str(getattr(session, "extension_name", "") or "")

    def _reviseCliDir(self):
        name = self._reviseExtensionName()
        if not name:
            return ""
        try:
            from SlicerAIAgentLib.ExtensionCLILoader import get_cli_base_dir
            return os.path.join(get_cli_base_dir(), name)
        except Exception:
            logger.debug("Revise CLI dir lookup failed", exc_info=True)
            return ""

    def _reviseEligibility(self, state=None):
        """``(ok, reason)`` — can the step now in view be revised at all?

        Broader than the baseline harness's allow-list on purpose. A baseline
        substitutes a *code producer*, so it needs a step the pipeline answers
        with code; a revision edits a *file*, so it works on anything that HAS
        one -- including the pre/post templates of an interactive step and a
        branch action, which are exactly the places a "it did the wrong thing"
        report tends to come from.
        """
        runtime = getattr(self, "_workflowRuntime", None)
        if runtime is None or getattr(runtime, "session", None) is None:
            return False, "No guided procedure is running."
        cli_dir = self._reviseCliDir()
        step_id = self._reviseTargetStepId(state)

        # Memoised per (package, step). The answer reads code_generators.json and
        # workflow.json, and this runs inside `_guidedWorkflowOwnsInput`, which
        # every `_setSendEnabled` consults -- roughly eight times per panel
        # repaint while the mode is armed. The step->file mapping cannot change
        # under a running session (a revision rewrites template CONTENT, never
        # the generator entries), so caching it is safe; the template TEXT is
        # re-read by `resolve_target` on every run and is not cached.
        key = (cli_dir, step_id)
        memo = getattr(self, "_reviseEligibilityMemo", None)
        if memo is not None and key in memo:
            return memo[key]
        try:
            verdict = TemplateReviser.revise_eligibility(cli_dir, step_id)
        except Exception:
            logger.debug("Revise eligibility check failed", exc_info=True)
            verdict = (False, "Could not read this procedure's generated package.")
        if memo is None:
            memo = {}
            self._reviseEligibilityMemo = memo
        memo[key] = verdict
        return verdict

    def _reviseEngaged(self, state=None):
        """Revise mode is armed AND this step actually has a template.

        A run in flight is always engaged, so the row and the amber Send cannot
        disappear from under an executing revision.
        """
        if not getattr(self, "_reviseActive", False):
            return False
        if self._reviseBusy():
            return True
        ok, _reason = self._reviseEligibility(state)
        return bool(ok)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _updateReviseControls(self, state):
        """Drive ✎ and the status row from the step now in view.

        Called from ``_updateReplayControls``, i.e. on every panel repaint, next
        to ``_updateBaselineControls``.
        """
        state = state or {}
        button = getattr(self, "_reviseButton", None)
        runtime = getattr(self, "_workflowRuntime", None)
        has_session = bool(getattr(runtime, "session", None)) if runtime else False

        ok, reason = (False, "")
        if has_session:
            ok, reason = self._reviseEligibility(state)

        # Disarm when the step in view cannot be revised, so `_reviseActive` is
        # only ever true somewhere it means something -- the same invariant that
        # makes the baseline toggle safe to hide.
        if (getattr(self, "_reviseActive", False) and not ok
                and not self._reviseBusy()):
            self._exitReviseMode()

        if button is not None:
            # ALWAYS visible, enabled only where there is a template to revise.
            # Unlike ⚖ (which lives in the replay row and can be hidden freely)
            # this button sits in the input column, and one that appears and
            # disappears there makes the row jump under the user's cursor — and,
            # since this method only runs on a workflow-panel repaint, a hidden
            # default meant the button did not exist until a procedure started.
            # A disabled button with a reason in its tooltip says more than an
            # absent one.
            # Off while a BASELINE run is in flight too: that run has repointed
            # _currentLogDir and _currentRunManifest at its own folder, so a
            # revision started underneath it would file its record — and the
            # `revisions` counter — against the baseline's run instead of the
            # pipeline's, which is precisely the provenance the run-folder copy
            # exists to establish.
            button.setEnabled(has_session and ok
                              and not self._reviseBusy()
                              and not self._baselineBusy())
            button.setToolTip(self._REVISE_TIP if ok else (reason or self._REVISE_TIP))
            self._setReviseChecked(getattr(self, "_reviseActive", False))

        if not has_session and not self._reviseBusy():
            if getattr(self, "_reviseActive", False):
                self._exitReviseMode()
            return

        row = getattr(self, "_reviseRow", None)
        if row is not None:
            row.setVisible(self._reviseEngaged(state))
        self._syncReviseSendButton()
        self._refreshInputAvailability()

    def _syncReviseSendButton(self):
        """Sole owner of Send's caption while revise mode is engaged."""
        button = getattr(self, "sendButton", None)
        if button is None:
            return
        if not self._reviseEngaged():
            # Only restore what WE changed: baseline may legitimately own the
            # button right now, and stamping the captured original over its
            # amber would leave the user with a Send that lies about what it
            # does. The two modes are mutually exclusive, so "not engaged and
            # baseline not engaged" is the only case that is ours.
            if not getattr(self, "_baselineActive", False):
                try:
                    button.setText(getattr(self, "_reviseSendText", "") or "Send")
                    button.setStyleSheet(getattr(self, "_reviseSendStyle", "") or "")
                    button.setToolTip("")
                except Exception:
                    logger.debug("Revise Send restore failed", exc_info=True)
            return
        try:
            button.setText("Working…" if self._reviseBusy() else self._REVISE_SEND_TEXT)
            button.setStyleSheet(self._REVISE_SEND_STYLE)
            button.setToolTip(self._REVISE_TIP)
        except Exception:
            logger.debug("Revise Send sync failed", exc_info=True)
        if self._reviseBusy():
            try:
                button.setEnabled(False)
            except Exception:
                logger.debug("Revise Send disable failed", exc_info=True)
        else:
            self._setSendEnabled(bool(self.promptInput.toPlainText().strip()))

    def _setReviseChecked(self, checked):
        """Stamp the toggle's check state without re-entering the handler.

        Qt flips a checkable QToolButton's state ITSELF before emitting
        ``clicked``, so every path that declines a click has to put it back or
        the button ends up reading the opposite of the mode it controls.
        """
        button = getattr(self, "_reviseButton", None)
        if button is None:
            return
        try:
            button.blockSignals(True)
            button.setChecked(bool(checked))
        except Exception:
            logger.debug("Revise toggle check-state failed", exc_info=True)
        finally:
            try:
                button.blockSignals(False)
            except Exception:
                logger.debug("Revise toggle unblock failed", exc_info=True)

    def _setReviseRunUiEnabled(self, enabled):
        """Freeze the mode's own control while a revision is in flight.

        Nothing repaints the panel during a revision (it dispatches no workflow
        step), so `_updateReviseControls` -- the only other place that touches
        this button -- does not run for the whole round trip. Without this the
        toggle stays live for up to three rounds of twelve search calls, and one
        impatient click leaves it reading "off" while the mode is on.
        """
        button = getattr(self, "_reviseButton", None)
        if button is None:
            return
        try:
            button.setEnabled(bool(enabled))
        except Exception:
            logger.debug("Revise toggle enable failed", exc_info=True)
        self._setReviseChecked(getattr(self, "_reviseActive", False))

    def _onReviseToggleClicked(self):
        if self._reviseBusy():
            self._setReviseStatus("A revision is in progress — wait for it to finish.")
            self._setReviseChecked(True)
            self._syncReviseSendButton()
            return
        if getattr(self, "_reviseActive", False):
            self._exitReviseMode()
            return

        ok, reason = self._reviseEligibility()
        if self._baselineBusy():
            ok, reason = False, ("A baseline run is in progress — wait for it "
                                 "to finish before revising.")
        if not ok:
            self._setReviseStatus(reason or "This step cannot be revised.")
            self._setReviseChecked(False)
            return

        # Mutually exclusive with the comparison harness: both own the prompt
        # box, Send's caption and the debug view, and there is no meaning to
        # "compare this step with a baseline while rewriting its template".
        if getattr(self, "_baselineActive", False):
            try:
                self._exitBaselineMode()
            except Exception:
                logger.debug("Leaving baseline mode for revise failed", exc_info=True)

        self._reviseActive = True
        row = getattr(self, "_reviseRow", None)
        if row is not None:
            row.setVisible(True)
        self._clearRevisePrompt()
        step_id = self._reviseTargetStepId()
        self._setReviseStatus(
            "Describe what step %s should have done, then press Revise. Its "
            "template is rewritten; the original is kept." % (step_id or "?")
        )
        self._showReviseDebugContext()
        self._refreshInputAvailability()
        self._syncReviseSendButton()

    def _exitReviseMode(self):
        """Full teardown, in the order the baseline mixin uses."""
        self._reviseActive = False
        row = getattr(self, "_reviseRow", None)
        if row is not None:
            row.setVisible(False)
        button = getattr(self, "_reviseButton", None)
        if button is not None:
            try:
                button.setChecked(False)
            except Exception:
                logger.debug("Revise toggle uncheck failed", exc_info=True)
        try:
            self._switchDebugContext(self.PIPELINE_DEBUG_CONTEXT)
        except Exception:
            logger.debug("Revise debug context restore failed", exc_info=True)
        self._debugWriteContext = self.PIPELINE_DEBUG_CONTEXT
        self._syncReviseSendButton()
        self._refreshInputAvailability()

    def _resetReviseForNavigation(self):
        """Leave revise mode on Back / Forward / Run-from-here.

        Stepping IS how the user picks which step to revise, so arriving at a new
        one starts from a clean slate. Returns False while a revision is running,
        and the caller must then abandon the navigation -- a rewind underneath an
        in-flight revision would rewrite a template for a step the user has left.
        """
        if self._reviseBusy():
            self._setReviseStatus(
                "A revision is in progress — wait for it to finish before stepping."
            )
            return False
        if getattr(self, "_reviseActive", False):
            self._exitReviseMode()
            self._clearRevisePrompt()
        return True

    def _clearRevisePrompt(self):
        box = getattr(self, "promptInput", None)
        if box is None:
            return
        try:
            box.setPlainText("")
        except Exception:
            logger.debug("Revise prompt clear failed", exc_info=True)

    def _setReviseStatus(self, message):
        """The single producer of the status line. Never pumps the event loop."""
        label = getattr(self, "_reviseInfoLabel", None)
        if label is not None:
            try:
                label.setText(str(message or ""))
            except Exception:
                logger.debug("Revise status write failed", exc_info=True)
        logger.info("[Revise] %s", message)

    # ------------------------------------------------------------------
    # Send takeover
    # ------------------------------------------------------------------

    def onSendButtonClicked(self):
        if not self._reviseEngaged():
            super().onSendButtonClicked()
            return
        if self._reviseBusy():
            self._setReviseStatus("A revision is already running.")
            return
        request = ""
        try:
            request = self.promptInput.toPlainText().strip()
        except Exception:
            logger.debug("Revise prompt read failed", exc_info=True)
        if not request:
            self._setReviseStatus(
                "Say what the step should have done — e.g. \"the curve should "
                "show in the 3D view and the red slice only\"."
            )
            return
        self._beginRevisionRun(request)

    def onPromptTextChanged(self):
        if self._reviseEngaged():
            self._syncReviseSendButton()
            return
        super().onPromptTextChanged()

    # ------------------------------------------------------------------
    # The run
    # ------------------------------------------------------------------

    def _reviseDebugKey(self):
        return "revise:%s" % (self._reviseTargetStepId() or "step")

    def _showReviseDebugContext(self):
        banner = (
            "<div style='color:#6a4c93;'><b>Revision — %s / %s</b><br>"
            "Rewriting this step's generated template.</div>"
            % (self._reviseExtensionName() or "?",
               self._reviseTargetStepId() or "?")
        )
        try:
            self._switchDebugContext(self._reviseDebugKey(), banner_html=banner)
        except Exception:
            logger.debug("Revise debug context switch failed", exc_info=True)

    def _beginRevisionRun(self, request):
        """Resolve the target, gather the evidence, start round 1.

        Everything that reads the MRML scene happens HERE, on the Qt main
        thread; the worker started at the end touches only the LLM client and
        files.
        """
        cli_dir = self._reviseCliDir()
        step_id = self._reviseTargetStepId()
        extension = self._reviseExtensionName()
        try:
            target = TemplateReviser.resolve_target(cli_dir, extension, step_id)
        except Exception:
            logger.debug("Revise target resolution failed", exc_info=True)
            target = None
        if target is None:
            self._setReviseStatus(
                "Could not find a template for step %s in %s."
                % (step_id or "?", extension or "?"))
            return

        context = self._reviseContext(target)
        try:
            system_prompt = TemplateReviser.revision_system_prompt(
                blocked_modules=self._reviseValidatorList("BLOCKED_MODULES"),
                blocked_functions=self._reviseValidatorList("BLOCKED_FUNCTIONS"),
                allowed_modules=self._reviseValidatorList("ALLOWED_MODULES"),
                source_roots=self._reviseSourceRoots(),
            )
            messages = TemplateReviser.build_messages(
                target, request, context, system_prompt=system_prompt)
        except Exception as exc:
            logger.debug("Revise message build failed", exc_info=True)
            self._setReviseStatus("Could not build the revision request: %s" % exc)
            return

        if getattr(self, "_reviseAttemptCounts", None) is None:
            self._reviseAttemptCounts = {}
        attempt = int(self._reviseAttemptCounts.get(step_id, 0)) + 1
        self._reviseAttemptCounts[step_id] = attempt

        self._reviseActiveRun = {
            "target": target,
            "request": request,
            "messages": messages,
            "round": 1,
            "attempt": attempt,
            # A revision is a background round-trip and the user can press Exit
            # while it is in the API. The epoch is what stops the reply landing
            # in a session that no longer exists -- and, worse, writing a
            # template for a procedure the user has moved on from.
            "epoch": getattr(self, "_guidedSessionEpoch", 0),
            "artifact_dir": self._reviseArtifactDir(step_id, attempt),
            "started": time.time(),
        }

        self._clearRevisePrompt()
        self._debugWriteContext = self._reviseDebugKey()
        self._showReviseDebugContext()
        self._commitReviseChatEntry("You (revision request)", request)
        self._setReviseStatus(
            "Reading %s and the extension source…"
            % ", ".join(target.rel_paths))
        self._setReviseRunUiEnabled(False)
        self._syncReviseSendButton()
        self._startRevisionRound()

    def _reviseValidatorList(self, attribute):
        try:
            from SlicerAIAgentLib.CodeValidator import CodeValidator
            return ", ".join(sorted(getattr(CodeValidator, attribute, set())))
        except Exception:
            logger.debug("Revise validator list read failed", exc_info=True)
            return ""

    def _reviseSourceRoots(self):
        try:
            from SlicerAIAgentLib.BaselineRunner import extension_source_roots_block
            block = extension_source_roots_block()
        except Exception:
            logger.debug("Revise source roots read failed", exc_info=True)
            return ""
        if not block:
            return ""
        return ("Extension source trees you can Grep and ReadFile:\n" + block)

    def _reviseContext(self, target):
        """Everything about this step that a revision is entitled to see."""
        state = getattr(self, "_currentWorkflowUiState", {}) or {}
        runtime = getattr(self, "_workflowRuntime", None)
        session = getattr(runtime, "session", None) if runtime else None
        context = {}

        index = state.get("current_index")
        total = state.get("total_steps")
        if index and total:
            context["position"] = "step %s of %s" % (index, total)

        brief = []
        for key in ("instructions", "description"):
            value = state.get(key)
            if value:
                brief.append(str(value))
        detail = getattr(self, "_workflowDetailText", "")
        if detail and detail not in brief:
            brief.append(str(detail))
        context["step_brief"] = "\n\n".join(brief)

        if session is not None:
            completed = list(getattr(session, "completed_steps", []) or [])
            if completed:
                context["completed"] = ", ".join(str(s) for s in completed)

        choices = self._reviseRecordedChoices()
        if choices:
            context["choices"] = "\n".join(
                "- %s = %r" % (name, value) for name, value in sorted(choices.items()))
            context["fill_values"] = {
                name: repr(value) for name, value in choices.items()}

        code = getattr(self, "currentCode", "") or ""
        if code and self._reviseCodeBelongsToStep(target.step_id):
            context["dispatched_code"] = code[:20000]

        context["execution"] = self._reviseExecutionSummary()
        context["scene"] = self._reviseSceneSummary()

        try:
            history = TemplateReviser.revision_history(target.cli_dir, target.step_id)
        except Exception:
            logger.debug("Revise history read failed", exc_info=True)
            history = []
        if history:
            context["history"] = "\n".join(
                "- %s: %s -> %s" % (entry.get("time", "?"),
                                    entry.get("request", "")[:200],
                                    entry.get("summary", "")[:200])
                for entry in history[-5:])
        return context

    def _reviseCodeBelongsToStep(self, step_id):
        """True when ``currentCode`` is this step's code and not a later one's.

        After a step completes the workflow auto-advances, so ``currentCode``
        may already belong to the NEXT step. Showing that as "the code that ran"
        would be a lie the model has no way to detect.
        """
        info = getattr(self, "_currentWorkflowStepInfo", None)
        if not isinstance(info, dict):
            return False
        return str(info.get("step_id", "")) == str(step_id)

    def _reviseRecordedChoices(self):
        """The answers the user gave, as ``{parameter_name: value}``."""
        extension = self._reviseExtensionName()
        if not extension:
            return {}
        try:
            from SlicerAIAgentLib.extension_cli_loader.workflow_state import (
                get_workflow_choices,
            )
            values = get_workflow_choices(extension)
            return dict(values) if isinstance(values, dict) else {}
        except Exception:
            logger.debug("Revise choice read failed", exc_info=True)
            return {}

    def _reviseExecutionSummary(self):
        """What the last execution of this step printed, raised or changed."""
        result = getattr(self, "_lastExecutionResult", None)
        if not isinstance(result, dict):
            return ""
        lines = ["success: %s" % bool(result.get("success"))]
        if result.get("error"):
            lines.append("error: %s" % str(result.get("error"))[:2000])
        output = str(result.get("output", "") or "")
        if output.strip():
            lines.append("stdout/stderr:\n%s" % output[:4000])
        if not result.get("error") and not output.strip():
            lines.append(
                "The step produced no output and raised nothing — which is why "
                "nothing automatic could have caught this."
            )
        return "\n".join(lines)

    def _reviseSceneSummary(self):
        try:
            return str(self.logic._buildSceneContext() or "")[:8000]
        except Exception:
            logger.debug("Revise scene read failed", exc_info=True)
            return ""

    def _reviseArtifactDir(self, step_id, attempt):
        """``<run>/runtime/<padded step>/revision_<n>/``.

        Built directly rather than through ``_setStepLogContext``: that method
        repoints the LLM client's dump directory and resets the role-trace
        offset, which belong to the step the PIPELINE is running, and a revision
        must not disturb either.
        """
        try:
            from SlicerAIAgentLib import RunLog
            return RunLog.ensure_dir(os.path.join(
                self._getCurrentLogDir(), RunLog.pad_step(step_id),
                "revision_%d" % attempt))
        except Exception:
            logger.debug("Revise artifact dir failed", exc_info=True)
            return ""

    def _reviseTools(self):
        """Search tools only — the generated CLI schemas are stripped.

        By identity (``strip_generated_cli_tools``) rather than by name, so an
        extension added later is still covered. A revision that could call a
        workflow tool would be able to dispatch a step while deciding how to
        rewrite it.
        """
        tools = list(getattr(self.logic, "skillTools", []) or [])
        try:
            from SlicerAIAgentLib.BaselineRunner import strip_generated_cli_tools
            return strip_generated_cli_tools(tools)
        except Exception:
            logger.debug("Revise tool ablation failed", exc_info=True)
            return tools

    def _startRevisionRound(self):
        """One LLM round on a daemon thread; the reply comes back via the queue."""
        run = getattr(self, "_reviseActiveRun", None)
        if not run:
            return
        logic = self.logic
        messages = run["messages"]
        tools = self._reviseTools()
        epoch = run["epoch"]
        round_number = run["round"]

        def _work():
            try:
                response = logic.llmClient.chatWithToolsIsolated(
                    messages=messages,
                    tools=tools,
                    tool_executor=logic._executeTool,
                    max_tool_rounds=TemplateReviser.TOOL_ROUNDS,
                    on_progress=lambda progress: self._streamQueue.put(
                        ("revise_progress", dict(progress or {}))),
                    options={"temperature": 0.2},
                )
                self._streamQueue.put(("revise_reply", {
                    "response": response, "epoch": epoch, "round": round_number,
                }))
            except Exception as exc:
                import traceback as _tb
                logger.debug("Revision round failed:\n%s", _tb.format_exc())
                self._streamQueue.put(("revise_error", {
                    "error": str(exc), "epoch": epoch,
                }))

        threading.Thread(target=_work, daemon=True).start()

    # ------------------------------------------------------------------
    # Queue handlers (main thread)
    # ------------------------------------------------------------------

    def _handleReviseProgress(self, payload):
        """Keep the status line moving while the agent searches.

        The keys are the ones ``llm_client._runToolLoop`` actually emits --
        ``reasoning_content`` / ``round`` / ``phase`` / ``tools`` -- and nothing
        else. A handler that reads a key the producer never sends is a status
        line that never changes, which for a multi-minute search is
        indistinguishable from a hang; and the whole reason this row exists is
        that the Debug group is collapsed by default.
        """
        run = getattr(self, "_reviseActiveRun", None)
        if not run:
            return
        payload = payload or {}
        tools = payload.get("tools") or []
        note = ""
        if tools:
            note = "searching: " + ", ".join(str(name) for name in tools[:4])
        else:
            body = str(payload.get("reasoning_content")
                       or payload.get("content") or "").strip()
            if body:
                note = body.splitlines()[0][:160]
            elif payload.get("phase"):
                note = str(payload.get("phase"))
        if not note:
            return
        round_number = payload.get("round")
        prefix = "Round %s of %s — " % (run.get("round", 1),
                                        TemplateReviser.MAX_ROUNDS)
        if round_number:
            prefix = "Round %s.%s — " % (run.get("round", 1), round_number)
        self._setReviseStatus((prefix + note)[:240])

    def _handleReviseError(self, payload):
        payload = payload or {}
        if not self._guidedSessionAlive(payload.get("epoch")):
            self._reviseActiveRun = None
            return
        self._finishRevisionRun(False, "Revision failed: %s" % payload.get("error", "?"))

    def _handleReviseReply(self, payload):
        """Parse, validate, and either retry, refuse or apply."""
        payload = payload or {}
        if not self._guidedSessionAlive(payload.get("epoch")):
            # The user exited (or started another procedure) while this was in
            # the API. Dropping it is the whole point of the epoch: writing a
            # template now would edit a package for a run nobody is in.
            #
            # Clear the run slot on the way out even though _prepareCleanRuntime
            # already does: a mode whose "busy" flag outlives its run leaves Send
            # disabled with no way back short of a restart, and that is too
            # expensive a failure to leave resting on one other method.
            logger.info("[Revise] Dropping a reply from an exited session.")
            self._reviseActiveRun = None
            return
        run = getattr(self, "_reviseActiveRun", None)
        if not run:
            return

        response = payload.get("response") or {}
        reply = str(response.get("message", "") or "")
        run["reply"] = reply
        self._reviseAccountForTokens(response)
        if reply:
            self._commitReviseChatEntry("Revision agent", reply[:6000])

        target = run["target"]
        parsed = TemplateReviser.parse_reply(reply, target.rel_paths)
        if parsed.blocked:
            self._finishRevisionRun(False, "Not revised — %s" % parsed.blocked)
            return
        if parsed.error:
            self._retryOrGiveUp(parsed, [])
            return

        validator = getattr(getattr(self, "logic", None), "codeValidator", None)
        checks = []
        for rel, new_text in sorted(parsed.templates.items()):
            original = target.template_for(rel)
            checks.append(TemplateReviser.validate_revision(
                original.text if original else "", new_text,
                code_validator=validator, rel_path=rel))
        failed = [check for check in checks if not check.ok]
        if failed:
            self._retryOrGiveUp(parsed, checks)
            return

        self._applyRevision(parsed, checks)

    def _reviseAccountForTokens(self, response):
        """Fold the revision's cost into the turn's totals, as a correction does.

        A revision is an LLM call the run paid for; leaving it out of the label
        would make the run's reported cost smaller than the run's actual cost,
        which is exactly the kind of quiet under-count the timing work exists to
        prevent.
        """
        try:
            tokens = response.get("tokens")
            if not tokens:
                return
            # getattr with a default, not `+=` on the bare attribute: the
            # counters are initialised by WidgetSendMixin.onSendButtonClicked,
            # which this mode overrides and never calls, so on the first
            # revision of a session they may not exist yet.
            self._currentTurnTokens = getattr(self, "_currentTurnTokens", 0) + int(tokens)
            self._currentTurnCost = (getattr(self, "_currentTurnCost", 0)
                                     + (response.get("cost") or 0))
            self._updateTokenLabel()
        except Exception:
            logger.debug("Revise token accounting skipped", exc_info=True)

    def _retryOrGiveUp(self, parsed, checks):
        """Hand the model its own rejection, or stop after MAX_ROUNDS."""
        run = getattr(self, "_reviseActiveRun", None)
        if not run:
            return
        problems = [error for check in checks for error in check.errors]
        if parsed.error:
            problems.append(parsed.error)
        if run["round"] >= TemplateReviser.MAX_ROUNDS:
            self._finishRevisionRun(False, (
                "Could not produce a template that passes the checks after %d "
                "rounds. Nothing was changed. Last problem: %s"
                % (run["round"], problems[0] if problems else "unknown")))
            return
        run["round"] += 1
        run["messages"].append({
            "role": "user",
            "content": TemplateReviser.build_retry_message(checks, parsed),
        })
        self._setReviseStatus(
            "The rewritten template was rejected (%s). Asking again — round %d of %d."
            % (problems[0] if problems else "unknown",
               run["round"], TemplateReviser.MAX_ROUNDS))
        self._startRevisionRound()

    def _applyRevision(self, parsed, checks):
        """Snapshot, write, log — then offer to re-run the step."""
        run = getattr(self, "_reviseActiveRun", None)
        if not run:
            return
        target = run["target"]
        record = TemplateReviser.apply_revision(
            target,
            parsed.templates,
            request=run["request"],
            summary=parsed.summary,
            analysis=parsed.analysis,
            checks=checks,
            messages=run["messages"],
            reply=run.get("reply", ""),
            rounds=run["round"],
        )
        if record.get("error") and not record.get("applied"):
            self._finishRevisionRun(False, record["error"], record=record)
            return

        self._recordRoleEvent("Reviser", "template_revised", {
            "extension": target.extension,
            "step_id": target.step_id,
            "templates": record.get("applied", []),
            "backup": record.get("backup", ""),
            "rounds": run["round"],
        })
        manifest = self._runManifest()
        if manifest is not None:
            try:
                manifest.update(revisions=int(manifest.data.get("revisions", 0)) + 1)
            except Exception:
                logger.debug("Revise manifest bump failed", exc_info=True)

        # An "identical to the original" warning on a template that was returned
        # unchanged is noise, not information: apply_revision already skipped it.
        unchanged = set(record.get("unchanged", []))
        warnings = [note for check in checks for note in check.warnings
                    if not (check.rel_path in unchanged and "identical" in note)]
        summary = parsed.summary or "template rewritten"
        message = "Revised %s — %s. Original kept in %s." % (
            ", ".join(record.get("applied", [])), summary, record.get("backup", "versions/"))
        if unchanged:
            message += " (%s returned unchanged, left alone.)" % ", ".join(sorted(unchanged))
        if record.get("error"):
            # A partial write: the snapshot was taken and at least one template
            # landed, but not all of them. Say so — a step whose pre template was
            # rewritten and whose post template was not is a step in two minds,
            # and the user is the only one who can decide to restore.
            message += (" NOT FULLY APPLIED: %s. Restore with versions/%s if the "
                        "step now misbehaves."
                        % (record["error"], record.get("label", "")))
        if warnings:
            message += " Warnings: " + "; ".join(warnings)
        self._commitReviseChatEntry("Revision applied", message)
        step_id = target.step_id
        self._finishRevisionRun(True, message, record=record)
        # Deferred to the next event-loop turn, NOT called here. This runs inside
        # _drainStreamQueue, and re-running executes template code, which pumps
        # the Qt event loop — so the drain timer would fire again and a second
        # queue event would be handled INSIDE this one. Same trick the baseline
        # harness uses to leave its own handler before advancing the workflow.
        epoch = getattr(self, "_guidedSessionEpoch", 0)
        qt.QTimer.singleShot(
            0, lambda: self._rerunAfterRevisionIfAlive(step_id, epoch))

    def _rerunAfterRevisionIfAlive(self, step_id, epoch):
        if not self._guidedSessionAlive(epoch):
            return
        self._rerunAfterRevision(step_id)

    def _writeRevisionRunArtifacts(self, record):
        """Mirror the package-side record into the run folder.

        Both copies exist on purpose: the package's ``debug/revision_<ts>/`` is
        the history of the PACKAGE and survives being copied to another machine,
        while the run folder's copy is what makes a run self-contained -- the
        thing a reader of ``logs/<run>/`` needs to know why step 12's code is not
        the code the package shipped with.
        """
        run = getattr(self, "_reviseActiveRun", None)
        directory = (run or {}).get("artifact_dir", "")
        if not directory:
            return
        try:
            from SlicerAIAgentLib import RunLog
            RunLog.write_json(os.path.join(directory, "revision.json"), record)
            RunLog.write_text(os.path.join(directory, "request.txt"),
                              (run or {}).get("request", ""))
            RunLog.write_text(os.path.join(directory, "reply.txt"),
                              (run or {}).get("reply", ""))
            rendered = []
            for index, message in enumerate((run or {}).get("messages", [])):
                rendered.append("===== MESSAGE %d | %s =====" % (
                    index, message.get("role", "?")))
                rendered.append(str(message.get("content", "")))
                rendered.append("")
            RunLog.write_text(os.path.join(directory, "messages_sent.txt"),
                              "\n".join(rendered))
        except Exception:
            logger.debug("Revision run artifacts failed", exc_info=True)

    def _finishRevisionRun(self, ok, message, record=None):
        """End the round: persist what happened, hand the row and view back."""
        # Written on EVERY outcome, not only on a successful write. A refusal
        # ("the extension has no such method, I looked for X") and an exhausted
        # round budget are the two answers a later reader most needs, and the
        # reasoning behind them lives only in the revise debug buffer, which is
        # discarded with the panel. A failed attempt would otherwise leave an
        # empty numbered folder and nothing else.
        self._writeRevisionRunArtifacts(record or {
            "status": "applied" if ok else "not applied",
            "message": message,
            "step_id": self._reviseTargetStepId(),
            "extension": self._reviseExtensionName(),
            "rounds": (getattr(self, "_reviseActiveRun", None) or {}).get("round", 0),
            "applied": [],
        })
        self._reviseActiveRun = None
        self._setReviseStatus(message)
        if not ok:
            self._commitReviseChatEntry("Revision", message)
        self._debugWriteContext = self.PIPELINE_DEBUG_CONTEXT
        self._setReviseRunUiEnabled(True)
        self._syncReviseSendButton()
        self._refreshInputAvailability()

    def _commitReviseChatEntry(self, title, body):
        """Append to the revision's own debug buffer, never the pipeline's."""
        try:
            self.appendToChat(title, body)
        except Exception:
            logger.debug("Revise chat append failed", exc_info=True)

    def _completedCheckpointIndex(self, session, step_id):
        """The LAST committed checkpoint for ``step_id``, or ``None``.

        Last, not first: a repeat block re-visits a step, and the most recent
        visit is the one whose scene the user just looked at.
        """
        checkpoints = list(getattr(session, "checkpoints", []) or [])
        for position in range(len(checkpoints) - 1, -1, -1):
            if getattr(checkpoints[position], "step_id", None) == step_id:
                return position
        return None

    def _rerunAfterRevision(self, step_id):
        """Run the revised step again, immediately, with no click from the user.

        Three ways in, because a step can be revised from three states, and only
        the first has a committed checkpoint:

        1. **Scrubbed back to it** (``preview_index`` set) — the normal way in.
           ``_rerunFromCheckpoint`` restores the pre-step scene, truncates the
           workflow state, and re-dispatches.
        2. **Standing IN it** — the step is open: an interactive step waiting for
           Done, or one that just ran. It has no committed checkpoint (those are
           recorded on completion) but it DOES have a *pending* one, holding the
           scene view and node set from the moment it opened. That is what
           ``rollback_failed_step`` restores from, and it deliberately keeps the
           pending checkpoint so the retry starts from the identical state. This
           is the case that used to dead-end in "no scene state to restore" —
           with ▷ greyed out, because there was nothing to replay to.
        3. **Completed and left behind** — re-run from its last checkpoint.

        The scene is always put back first. Re-dispatching a step on top of its
        own output is how a PRE template that creates a node creates a second
        one, after which the POST template's "last node of this class" picks the
        wrong one — silently wrong, which is worse than losing an in-progress
        manual adjustment the user is re-running anyway.

        Template CONTENT is read fresh from disk on every dispatch, so no cache
        invalidation is needed for the rewrite to take effect.
        """
        runtime = getattr(self, "_workflowRuntime", None)
        session = getattr(runtime, "session", None) if runtime else None
        if session is None:
            self._setReviseStatus("Revised %s." % step_id)
            return

        # Leave revise mode BEFORE re-running: this hands the step back to the
        # pipeline, and Send must not stay purple and revision-routed while the
        # pipeline is driving.
        self._exitReviseMode()

        index = getattr(session, "preview_index", None)
        if index is None and getattr(session, "current_step", None) != step_id:
            index = self._completedCheckpointIndex(session, step_id)

        if index is not None:
            self._setReviseStatus(
                "Re-running %s with the revised template…" % step_id)
            try:
                # `_rerunFromCheckpoint` still confirms first when the rewind
                # would delete nodes the workflow did not create — that prompt
                # protects the surgeon's own data and is not ours to skip.
                self._rerunFromCheckpoint(index)
            except Exception:
                logger.debug("Revise re-run from checkpoint failed", exc_info=True)
                self._setReviseStatus(
                    "Revised, but the automatic re-run failed — press ▷ to run "
                    "%s again." % step_id)
            return

        if getattr(session, "current_step", None) == step_id:
            self._rerunOpenStepAfterRevision(step_id)
            return

        self._setReviseStatus(
            "Revised %s. It is not the step in view and has no checkpoint, so "
            "it was not re-run — step to it and press ▷." % step_id)

    def _rerunOpenStepAfterRevision(self, step_id):
        """Restart the step the workflow is standing in, from its pending state."""
        runtime = getattr(self, "_workflowRuntime", None)
        self._setReviseStatus(
            "Re-running %s from its starting state with the revised template…"
            % step_id)
        # The interaction for this attempt is over: drop the observers and
        # debounce timers the runtime registered, exactly as Done does, so they
        # cannot accumulate across the re-dispatch.
        try:
            self._interactionManager.cleanup()
        except Exception:
            logger.debug("Interaction cleanup before revise re-run failed",
                         exc_info=True)
        # Undo whatever this attempt put in the scene, from the snapshot taken
        # when the step opened. Named for the failure case it was written for,
        # but this is the same situation: an attempt at `step_id` that is being
        # thrown away and retried from the identical starting state.
        try:
            outcome = runtime.rollback_failed_step(step_id)
            if not (outcome or {}).get("rolled_back"):
                logger.info("[Revise] No pre-step state to restore for %s (%s); "
                            "re-dispatching on the current scene.",
                            step_id, (outcome or {}).get("reason", ""))
        except Exception:
            logger.debug("Revise pre-step rollback failed", exc_info=True)
        # The wait this step was in has been abandoned; the re-dispatch enters a
        # new one through the normal interactive path.
        self._waitingForUser = False
        try:
            self._runWorkflowStepDirect(step_id, "start")
        except Exception:
            logger.debug("Revise re-dispatch failed", exc_info=True)
            self._setReviseStatus(
                "Revised, but %s could not be re-dispatched automatically."
                % step_id)
