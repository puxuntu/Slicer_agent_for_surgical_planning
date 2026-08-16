"""Voice control: the Qt half.

The whole feature is one microphone button above Send plus a Settings section,
and everything it does resolves to *calling the same panel handler the mouse
would have called*. That equivalence is the design: the guided runtime's claim
is that a validated, offline-analysed procedure drives the scene, and a voice
layer that dispatched the runtime directly would be a second, unreviewed way to
drive it. So every action here goes through the widget method the button uses --
``_onWorkflowDoneClicked``, ``_commitWorkflowChoice``, ``_onWorkflowRangeSelected``
-- and never through ``WorkflowRuntime.run_step``.

Three consequences of that rule are load-bearing, and each one is a bug if you
shortcut it:

* ``_onWorkflowDoneClicked`` also runs ``_interactionManager.cleanup()``. Going
  straight to ``_runWorkflowStepDirect(step, "proceed")`` leaves the previous
  placement's VTK observers and debounce timers attached.
* ``_onWorkflowRangeSelected`` also runs ``_commitThresholdToSegment`` and
  ``_clearThresholdPreview``. Committing ``[min, max]`` on its own produces an
  empty segment and leaks a preview labelmap into the scene.
* the scalar slider, the segment-name picker and the multi-choice form each
  drive the *extension's own* control first, so its connected handler fires and
  its parameter binding updates. Committing the value alone skips that.

**Capture is gated by the Space bar.** Holding it records; releasing it sends.
The key is the detector, which removes an entire class of failure the energy
detector has: a sentence chopped at a pause because the speaker's level sat
close to the threshold, or never triggered because it sat under it. It also
means nothing said in the room is ever transmitted unless somebody is holding a
key down, which is a stronger privacy property than any amount of matching
discipline.

The original **always-on** mode is still there behind a Settings checkbox, for
hands-free use where a key is not reachable. It keeps the energy detector, the
room-noise calibration and its adaptive floor. Everything below applies to both.

Four things stop a mis-recognition from driving the scene:

1. the matcher declines by default (``voice/commands.py``) -- an utterance only
   resolves against the closed vocabulary the step actually offers;
2. the mic is muted while the app is speaking, so the synthesized guidance
   coming out of the speakers is never transcribed as a command. Pressing the
   key CUTS the announcement (barge-in) and unmutes, so push-to-talk is never
   waiting behind twenty seconds of speech;
3. every committing action is announced ("Selecting Red box."). Be precise about
   what this buys: the line is ENQUEUED before the action is applied, but
   synthesis is a network round trip, so it is heard a second or so after the
   scene has already changed. It makes a mis-hearing audible at the moment it
   happens instead of three steps later; it is not a veto. Naming the LABEL
   rather than the value is what makes it work at all -- a surgeon who said
   "left" hears "Selecting Blue box" and can act on the mismatch;
4. an optional confirm mode, which IS a veto: it arms the action and waits for
   "yes" instead of running it.

Threading: capture and the ASR round trip are off the Qt main thread and touch
neither MRML nor a widget. Everything crosses back through the existing
``_streamQueue``, drained by the 50 ms timer. Deferred work carries the guided
session epoch and drops out when the user has exited, exactly as a
self-correction round trip does.
"""

from .common import *


VOICE_SETTINGS_GROUP = "SlicerAIAgent"

#: How long after speech ends before the microphone is live again. Long enough
#: for the speaker's tail and any room reverb, short enough that answering
#: immediately after the prompt still works.
VOICE_UNMUTE_TAIL_MS = 350

#: A transcript this short is a click, a cough or a door. Below it nothing is
#: even matched, so the log stays readable.
VOICE_MIN_TRANSCRIPT_CHARS = 2

#: Whether what the microphone hears is written into the run folder. OFF, and
#: that is a privacy decision, not a performance one: this microphone is always
#: on in an operating theatre, so most of what it transcribes is conversation
#: about a patient, and run folders are copied, shared and attached to papers.
#: Turn it on deliberately for an evaluation that needs the utterances; the
#: byte counts, durations and resolved ACTIONS are recorded either way, so an
#: artifact still evidences what the feature did.
VOICE_LOG_TRANSCRIPTS = False

#: Consecutive transcription failures before the session gives up and says so.
#: A wrong region or a bad key fails EVERY utterance identically, and without
#: this the only symptom is a microphone that appears to work and never acts --
#: the status line it writes lives in a collapsed group.
VOICE_MAX_CONSECUTIVE_ASR_ERRORS = 3

#: Spoken requests only start a procedure when they open like a request. Without
#: this every sentence in the room becomes a routing call plus, on a non-match, a
#: modal refusal -- the router is an LLM call, so an idle hot mic would bill and
#: interrupt continuously.
VOICE_REQUEST_LEAD_INS = (
    "plan", "start", "begin", "run", "plan the", "open", "plan a",
    "perform", "plan for", "do the", "set up", "lets plan", "let's plan",
    "i want to plan", "i would like to plan", "load", "prepare",
)

#: Trace every stage of the voice chain to the Python console. On by default:
#: this feature has more places to stop silently than anything else in the
#: extension -- an unheard utterance, an empty transcript, a refused match and a
#: workflow that simply had no such option all look identical from the panel.
#: Turn it off from the console with
#: ``from SlicerAIAgentLib.app import widget_voice; widget_voice.VOICE_DEBUG = False``
#: (the flag is read per call, so it takes effect immediately).
VOICE_DEBUG = True

#: Per-attempt HTTP timeout for a transcription, well under the client's own
#: 60 s default. Two reasons, both specific to an always-on microphone: a
#: sentence transcribed a minute late is worse than useless, and the call holds
#: the listener's SINGLE dispatch thread, so a stuck one blocks every later
#: utterance and starts overflowing the (bounded) capture queue. Failing fast
#: and saying so beats waiting.
VOICE_ASR_TIMEOUT_SECONDS = 20


class _VoicePushToTalkFilter(qt.QObject):
    """Application-wide watcher for one key going down and coming back up.

    An event filter rather than a ``QShortcut`` because a shortcut only fires on
    PRESS -- there is no release signal in Qt -- and push-to-talk is defined by
    the release. Installed on the QApplication so it sees the key wherever focus
    happens to be: during a guided workflow the user is clicking in the slice
    views, not in the module panel.

    The callbacks return True when they acted, and that answer becomes the
    event's "handled" flag, so Space is consumed ONLY when it actually started
    or stopped a recording. Every other Space -- typing, a focused button, a
    session that is not armed -- passes through untouched.
    """

    #: Sent to ourselves at install time to prove the filter is really being
    #: called. PythonQt's support for overriding a C++ virtual from Python is
    #: not guaranteed, and a filter that is silently never invoked would present
    #: as "the key does nothing", which is indistinguishable from a dozen other
    #: faults. F35 is chosen because no keyboard has one.
    PROBE_KEY = getattr(qt.Qt, "Key_F35", None)

    #: Only the four real modifiers are compared. Keypad and group-switch bits
    #: ride along on ordinary keystrokes on some layouts, and comparing the raw
    #: value against NoModifier would then never match.
    _MOD_MASK = int(qt.Qt.ShiftModifier | qt.Qt.ControlModifier
                    | qt.Qt.AltModifier | qt.Qt.MetaModifier)

    def __init__(self, key, modifiers, on_press, on_release):
        qt.QObject.__init__(self)
        self._key = key
        self._modifiers = int(modifiers) & self._MOD_MASK
        self._on_press = on_press
        self._on_release = on_release
        #: The REAL state of the hold. isAutoRepeat() alone is not enough:
        #: Windows repeats KeyPress only, X11 can synthesise release/press
        #: pairs, and a filter that trusted the flag would behave differently
        #: on the two.
        self._held = False
        self.probe_seen = False

    def eventFilter(self, obj, event):
        try:
            event_type = event.type()

            # A hold that is never released leaves the microphone open. The
            # release is not guaranteed: alt-tabbing, or a modal opening over
            # the window, takes focus away and the key comes up somewhere else.
            if event_type == qt.QEvent.WindowDeactivate and self._held:
                self._held = False
                self._on_release()
                return False

            if event_type not in (qt.QEvent.ShortcutOverride,
                                  qt.QEvent.KeyPress, qt.QEvent.KeyRelease):
                return False
            key = event.key()
            if self.PROBE_KEY is not None and key == self.PROBE_KEY:
                self.probe_seen = True
                return False
            if key != self._key:
                return False
            if (int(event.modifiers()) & self._MOD_MASK) != self._modifiers:
                # Ctrl+Shift+Space is Slicer's markups Place toggle and is live
                # at all times. Matching on the key alone would eat it.
                return False

            # Qt resolves SHORTCUTS before it delivers key events, so a
            # KeyPress-only filter loses to any existing QShortcut on the same
            # key -- Segment Editor binds bare Space. Accepting ShortcutOverride
            # is what makes the key arrive here as an ordinary KeyPress instead.
            if event_type == qt.QEvent.ShortcutOverride:
                if self._on_press(probe_only=True):
                    event.accept()
                    return True
                return False

            if event_type == qt.QEvent.KeyPress:
                if event.isAutoRepeat():
                    # Swallow repeats ONLY while we own the hold. Returning True
                    # unconditionally would eat every repeat of a key we
                    # declined -- so holding Space in the prompt box would type
                    # one space and then go dead.
                    return self._held
                if self._on_press():
                    self._held = True
                    return True
                return False

            if event.isAutoRepeat():
                return self._held
            if self._held:
                self._held = False
                self._on_release()
                return True
            return False
        except Exception:
            # Never let a filter raise: it runs for every event in the
            # application, and an exception here would be a storm.
            return False


def _voice_debug(message, *args):
    """One tagged line per event, on the Python console.

    ``print`` rather than ``logger.info``: Slicer routes the logging module into
    the application's error-log window, which is not where somebody watching
    voice control is looking. Safe from any thread.

    This trace is EPHEMERAL -- it is never written to a run folder -- which is
    why it may carry the transcript that the artifacts deliberately withhold
    (see ``VOICE_LOG_TRANSCRIPTS``). It is the same text the Debug conversation
    already shows on screen.
    """
    if not VOICE_DEBUG:
        return
    try:
        text = message % args if args else message
    except Exception:
        text = "%s %r" % (message, (args,))
    try:
        stamp = qt.QDateTime.currentDateTime().toString("hh:mm:ss.zzz")
    except Exception:
        stamp = ""
    try:
        print("[voice %s] %s" % (stamp, text))
    except Exception:
        pass


class WidgetVoiceMixin:

    # Slicer 5.10 ships no microphone icon anywhere -- the only audio-adjacent
    # resources in the whole install are the NA-MIC logo and QtTesting's
    # record.png. The Sequences module's record dot is the closest thing that
    # reads correctly, and like the other :/Icons/ paths this repo uses it lives
    # in a MODULE library rather than in core, so it may not be registered.
    # Hence the ladder, ending in a BMP glyph rather than an emoji: the row's
    # other fallbacks are all single BMP characters and an emoji renders as a
    # tofu box on some Windows font stacks.
    _MIC_ICON_RESOURCES = (
        ":/Icons/VcrRecord16.png",
        ":/Icons/Record.png",
        ":/Icons/Chat.png",
    )
    _MIC_GLYPH_IDLE = "●"

    _VOICE_IDLE_STYLE = ""
    _VOICE_LISTENING_STYLE = (
        "QToolButton { background-color: #ffe3e3; border: 1px solid #e06c6c; "
        "border-radius: 3px; }"
    )
    _VOICE_SPEAKING_STYLE = (
        "QToolButton { background-color: #e3f0ff; border: 1px solid #6c9ee0; "
        "border-radius: 3px; }"
    )

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setupVoiceControls(self):
        """Build the Settings section and the mic button. Never raises.

        Called from ``setup()`` BEFORE ``_relaxContentWidth`` so the section's
        combos and line edits are swept by it -- anything built later has to
        apply the width policy itself, and a field with a real width hint in a
        collapsed group still widens Slicer's module panel.
        """
        try:
            self._buildVoiceSettingsSection()
        except Exception:
            logger.debug("Voice settings section build failed", exc_info=True)
        try:
            self._insertVoiceButtonAboveSend()
        except Exception:
            logger.debug("Voice button insertion failed", exc_info=True)

    def _voiceIcon(self):
        for resource in self._MIC_ICON_RESOURCES:
            icon = self._nativeIcon(resource)
            if icon is not None:
                return icon
        try:
            icon = slicer.app.style().standardIcon(qt.QStyle.SP_MediaVolume)
            if not icon.isNull():
                return icon
        except Exception:
            logger.debug("Standard mic icon lookup failed", exc_info=True)
        return None

    def _insertVoiceButtonAboveSend(self):
        """Put the mic directly above Send, inside the existing input row.

        ``inputLayout`` is a bare QHBoxLayout item inside ``verticalLayout``, so
        ``indexOf`` on the outer layout cannot find it; and the programmatic
        fallback builds it with no objectName at all. It is located
        structurally, the same way ``_insertBaselineRowAboveInput`` does: the
        outer item whose sub-layout contains ``promptInput``.
        """
        if getattr(self, "_voiceButton", None) is not None:
            return
        prompt = getattr(self, "promptInput", None)
        send = getattr(self, "sendButton", None)
        if prompt is None or send is None:
            return
        parent = prompt.parent()
        outer = parent.layout() if parent is not None else None
        if outer is None:
            return

        input_layout = None
        for index in range(outer.count()):
            item = outer.itemAt(index)
            sub = item.layout() if item is not None else None
            if sub is not None and sub.indexOf(prompt) >= 0:
                input_layout = sub
                break
        if input_layout is None:
            return

        button = qt.QToolButton()
        icon = self._voiceIcon()
        if icon is not None:
            button.setIcon(icon)
        else:
            button.setText(self._MIC_GLYPH_IDLE)
        button.setCheckable(True)
        button.setAutoRaise(True)
        button.setToolTip(self._voiceButtonTooltip())
        button.clicked.connect(self._onVoiceButtonClicked)
        try:
            # Fixed, and icon-only: sendButton is pinned Fixed for the same
            # reason (widget_core._relaxContentWidth), and a text caption here
            # would add its width to the row's permanent minimum.
            button.setSizePolicy(qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed)
        except Exception:
            logger.debug("Voice button size policy failed", exc_info=True)
        self._voiceButton = button

        position = input_layout.indexOf(send)
        if position < 0:
            position = input_layout.count()
        # Detaching Send and re-parenting it into a new column is the one step
        # here that can leave the panel WORSE than before: if anything between
        # removeWidget and insertLayout raises, Send is orphaned and there is no
        # way to submit anything at all. Put it back on any failure -- losing
        # the mic button is a missing feature, losing Send is a broken module.
        input_layout.removeWidget(send)
        try:
            column = qt.QVBoxLayout()
            column.setContentsMargins(0, 0, 0, 0)
            column.setSpacing(2)
            column.addWidget(button, 0, qt.Qt.AlignHCenter)
            column.addWidget(send)
            input_layout.insertLayout(position, column)
        except Exception:
            logger.debug("Voice button column failed; restoring Send", exc_info=True)
            try:
                send.setParent(None)
                input_layout.insertWidget(position, send)
            except Exception:
                logger.error("Could not restore the Send button after a failed "
                             "voice-button insertion", exc_info=True)
            self._voiceButton = None
            return
        self._voiceButtonColumn = column

    def _voiceButtonTooltip(self, extra=""):
        if not self._voiceAsrConfigured():
            base = ("Voice control is not configured.\n"
                    "Open Settings ▸ Voice control and set the speech API key.")
        elif self._voicePttEnabled():
            base = ("Voice control — click to arm.\n"
                    "Then HOLD the Space bar while you speak and release to "
                    "send. Space still types normally in a text box.")
        else:
            base = ("Voice control — click to start listening.\n"
                    "The microphone stays open; say \"stop listening\" to close it.")
        return base + (("\n" + extra) if extra else "")

    # ------------------------------------------------------------------
    # Settings section
    # ------------------------------------------------------------------

    def _buildVoiceSettingsSection(self):
        if getattr(self, "_voiceGroup", None) is not None:
            return
        root = getattr(self, "ui", None)
        if root is None:
            return
        settings_group = root.findChild(ctk.ctkCollapsibleGroupBox, "settingsGroupBox")
        parent_layout = settings_group.layout() if settings_group is not None else None

        from SlicerAIAgentLib.voice import asr_client as _asr
        from SlicerAIAgentLib.voice import tts_client as _tts

        group = ctk.ctkCollapsibleGroupBox()
        group.title = "Voice control"
        group.collapsed = True
        form = qt.QFormLayout(group)
        self._voiceGroup = group

        # FIRST row, and red: this is the one condition that makes every control
        # below it inert, so it has to be read before any of them are touched.
        # Selectable, because its whole point is the install line -- a remedy the
        # user cannot copy is a remedy they have to retype from a screenshot.
        self._voiceBackendBanner = qt.QLabel("")
        self._voiceBackendBanner.setWordWrap(True)
        self._voiceBackendBanner.setMinimumWidth(0)
        self._voiceBackendBanner.setStyleSheet(
            "QLabel { color: #b3261e; background-color: #fdecea; "
            "border: 1px solid #f2b8b5; border-radius: 3px; padding: 6px; }")
        try:
            self._voiceBackendBanner.setTextInteractionFlags(
                qt.Qt.TextSelectableByMouse | qt.Qt.TextSelectableByKeyboard)
            self._voiceBackendBanner.setCursor(qt.QCursor(qt.Qt.IBeamCursor))
        except Exception:
            logger.debug("Voice banner selection setup failed", exc_info=True)
        self._voiceBackendBanner.setVisible(False)
        form.addRow(self._voiceBackendBanner)

        self._voiceEnabledCheck = qt.QCheckBox("Enable voice control")
        self._voiceEnabledCheck.setToolTip(
            "When off, the microphone button is disabled and nothing is recorded.")
        form.addRow(self._voiceEnabledCheck)

        self._voicePttKeyCombo = qt.QComboBox()
        # (label, Qt key attribute, modifier attribute). Space is the default
        # because it is what was asked for and it is the natural talk key -- but
        # it is the ONLY option here that Slicer already uses (Segment Editor
        # binds bare Space to swap the last two effects), so the alternatives
        # are offered beside it rather than buried.
        for label, key_name, mod_name in (
            ("Space", "Key_Space", "NoModifier"),
            ("F4 (no conflicts)", "Key_F4", "NoModifier"),
            ("F8 (no conflicts)", "Key_F8", "NoModifier"),
            ("Ctrl+Space", "Key_Space", "ControlModifier"),
        ):
            self._voicePttKeyCombo.addItem(label, "%s|%s" % (key_name, mod_name))
        self._voicePttKeyCombo.setToolTip(
            "Which key to hold while speaking.\n\n"
            "Space is the natural choice, but Slicer's Segment Editor already "
            "binds bare Space to switch between the last two effects — while "
            "voice is armed, this takes it over and that toggle stops working. "
            "F4 and F8 are bound to nothing in Slicer and avoid the clash "
            "entirely.\n\n"
            "Ctrl+Shift+Space (markups Place mode) is never intercepted, "
            "whichever option you pick.")
        form.addRow("Talk key:", self._voicePttKeyCombo)

        self._voicePttCheck = qt.QCheckBox("Hold the talk key (push-to-talk)")
        self._voicePttCheck.setToolTip(
            "Recommended. The microphone captures only while the Space bar is "
            "held down, and the key itself marks where your sentence starts and "
            "ends — so nothing said in the room is ever sent, and a sentence is "
            "never cut at a pause.\n\n"
            "Space is ignored while you are typing in a text field.\n\n"
            "Unchecked, the microphone stays open and an energy detector decides "
            "what is speech. That is hands-free, but it hears every conversation "
            "in the room and has to guess where each sentence ends.")
        form.addRow(self._voicePttCheck)

        self._voiceRegionCombo = qt.QComboBox()
        for key in ("us", "intl", "cn"):
            entry = _asr.REGIONS.get(key)
            if entry:
                self._voiceRegionCombo.addItem(entry.get("label") or key, key)
        self._voiceRegionCombo.currentIndexChanged.connect(self._onVoiceRegionChanged)
        form.addRow("Region:", self._voiceRegionCombo)

        self._voiceAsrModelCombo = qt.QComboBox()
        self._voiceAsrModelCombo.setEditable(True)
        form.addRow("Speech model:", self._voiceAsrModelCombo)

        self._voiceAsrEndpointInput = qt.QLineEdit()
        self._voiceAsrEndpointInput.setPlaceholderText(_asr.DEFAULT_ENDPOINT)
        form.addRow("Endpoint:", self._voiceAsrEndpointInput)

        key_row = qt.QHBoxLayout()
        self._voiceApiKeyInput = qt.QLineEdit()
        self._voiceApiKeyInput.setEchoMode(qt.QLineEdit.Password)
        self._voiceApiKeyInput.setPlaceholderText("DashScope API key for this region")
        self._voiceApiKeyInput.setToolTip(
            "DashScope keys are per-region and are NOT the same as the agent's "
            "chat key unless you use the same account and region.\n\n"
            "Stored in Slicer's application settings when you press Save, and "
            "reloaded on every launch — you only enter it once.")
        key_row.addWidget(self._voiceApiKeyInput)
        self._voiceTestButton = qt.QPushButton("Test")
        self._voiceTestButton.setToolTip(
            "Send half a second of silence to the speech endpoint. It checks the "
            "key, the region and the model without needing a microphone.")
        self._voiceTestButton.clicked.connect(self._onVoiceTestAsr)
        key_row.addWidget(self._voiceTestButton)
        form.addRow("Speech API key:", key_row)

        self._voiceLanguageCombo = qt.QComboBox()
        for code, label in _asr.LANGUAGES:
            self._voiceLanguageCombo.addItem(label, code)
        form.addRow("Spoken language:", self._voiceLanguageCombo)

        device_row = qt.QHBoxLayout()
        self._voiceDeviceCombo = qt.QComboBox()
        device_row.addWidget(self._voiceDeviceCombo)
        self._voiceDeviceRefresh = qt.QPushButton("Refresh")
        self._voiceDeviceRefresh.clicked.connect(self._onVoiceRefreshDevices)
        device_row.addWidget(self._voiceDeviceRefresh)
        form.addRow("Microphone:", device_row)

        self._voiceSensitivitySlider = ctk.ctkSliderWidget()
        self._voiceSensitivitySlider.minimum = 1.5
        self._voiceSensitivitySlider.maximum = 8.0
        self._voiceSensitivitySlider.singleStep = 0.1
        self._voiceSensitivitySlider.value = 3.0
        self._voiceSensitivitySlider.setToolTip(
            "How far above the measured room noise a sound must be to count as "
            "speech. Raise it in a noisy theatre; lower it if quiet speech is "
            "missed.\n\nApplies immediately while listening — the room noise is "
            "re-measured, so this is also the fix for a session that calibrated "
            "during a loud moment and has been deaf ever since.")
        self._voiceSensitivitySlider.valueChanged.connect(self._onVoiceSensitivityChanged)
        form.addRow("Noise margin:", self._voiceSensitivitySlider)

        self._voiceSilenceSlider = ctk.ctkSliderWidget()
        self._voiceSilenceSlider.minimum = 300
        self._voiceSilenceSlider.maximum = 2500
        self._voiceSilenceSlider.singleStep = 50
        self._voiceSilenceSlider.value = 900
        try:
            # Cosmetic only, and the one property here not already exercised
            # elsewhere in this codebase -- losing it must not cost the section.
            self._voiceSilenceSlider.suffix = " ms"
        except Exception:
            logger.debug("Silence slider suffix unsupported", exc_info=True)
        self._voiceSilenceSlider.setToolTip(
            "Silence after which a sentence is considered finished and sent.")
        form.addRow("End of sentence:", self._voiceSilenceSlider)

        speak_row = qt.QHBoxLayout()
        self._voiceSpeakCheck = qt.QCheckBox("Read step guidance aloud")
        speak_row.addWidget(self._voiceSpeakCheck)
        self._voiceTestTtsButton = qt.QPushButton("Test voice")
        self._voiceTestTtsButton.clicked.connect(self._onVoiceTestTts)
        speak_row.addWidget(self._voiceTestTtsButton)
        form.addRow(speak_row)

        self._voiceTtsModelInput = qt.QLineEdit()
        self._voiceTtsModelInput.setPlaceholderText(_tts.DEFAULT_MODEL)
        form.addRow("Speech-out model:", self._voiceTtsModelInput)

        self._voiceVoiceCombo = qt.QComboBox()
        self._voiceVoiceCombo.setEditable(True)
        self._voiceVoiceCombo.addItems(list(_tts.VOICES))
        self._voiceVoiceCombo.setToolTip(
            "Any voice documented for the model can be typed in; the listed ones "
            "are only the confirmed subset.")
        form.addRow("Voice:", self._voiceVoiceCombo)

        self._voiceTtsLanguageCombo = qt.QComboBox()
        self._voiceTtsLanguageCombo.addItems(list(_tts.LANGUAGE_TYPES))
        form.addRow("Speech-out language:", self._voiceTtsLanguageCombo)

        self._voiceFallbackCheck = qt.QCheckBox("Ask the model when unsure")
        self._voiceFallbackCheck.setToolTip(
            "When plain matching cannot place an utterance, send one small "
            "request to the configured LLM, constrained to this step's options.")
        form.addRow(self._voiceFallbackCheck)

        self._voiceConfirmCheck = qt.QCheckBox("Confirm before acting")
        self._voiceConfirmCheck.setToolTip(
            "Speak the resolved action back and wait for \"yes\" before applying it.")
        form.addRow(self._voiceConfirmCheck)

        # Its own Save, inside the group. The Settings form's Save button is a
        # row ABOVE this group (the group is appended after it), so saving what
        # you just typed would mean scrolling back up past every field --
        # exactly the way an API key ends up being retyped every launch. It
        # calls the SHARED onSaveSettings, not a private path, so there is still
        # only one save and the two sections cannot drift apart.
        self._voiceSaveButton = qt.QPushButton("Save voice settings")
        self._voiceSaveButton.setToolTip(
            "Store these settings — including the API key — in Slicer's "
            "application settings. They are reloaded on every launch.\n"
            "Same action as the Save Settings button above.")
        self._voiceSaveButton.clicked.connect(self.onSaveSettings)
        form.addRow(self._voiceSaveButton)

        self._voiceStatusLabel = qt.QLabel("")
        self._voiceStatusLabel.setWordWrap(True)
        self._voiceStatusLabel.setMinimumWidth(0)
        self._voiceStatusLabel.setStyleSheet("color: #555;")
        form.addRow(self._voiceStatusLabel)

        if parent_layout is not None:
            try:
                # Spans both columns, like saveSettingsButton does in the .ui.
                parent_layout.addRow(group)
            except Exception:
                parent_layout.addWidget(group)
        else:
            # No .ui: the programmatic fallback builds its Settings group with
            # no objectName, so findChild cannot reach it. Parent under
            # ``self.ui`` all the same -- _relaxContentWidth only sweeps that
            # subtree, and a group outside it keeps a real width hint and
            # widens Slicer's module panel.
            host = root.layout() if hasattr(root, "layout") else None
            if host is not None:
                host.addWidget(group)
            else:
                self.layout.insertWidget(1, group)

        self._onVoiceRefreshDevices()

    def _onVoiceRegionChanged(self, *_args):
        """Re-seed the model list and endpoint when the region changes.

        DashScope model ids are region-suffixed (``qwen3-asr-flash-us``) and the
        OpenAI-compatible mode does not exist for ASR in the US region at all,
        so region is not a cosmetic choice -- getting it wrong is a 404 that
        reads like a broken key.
        """
        combo = getattr(self, "_voiceRegionCombo", None)
        if combo is None:
            return
        from SlicerAIAgentLib.voice import asr_client as _asr
        from SlicerAIAgentLib.voice import tts_client as _tts
        region = combo.itemData(combo.currentIndex) or _asr.DEFAULT_REGION
        models = _asr.models_for_region(region)
        model_combo = getattr(self, "_voiceAsrModelCombo", None)
        if model_combo is not None:
            current = model_combo.currentText
            model_combo.clear()
            model_combo.addItems(models)
            model_combo.setCurrentText(current if current in models else (models[0] if models else ""))
        endpoint = getattr(self, "_voiceAsrEndpointInput", None)
        if endpoint is not None:
            endpoint.text = _asr.endpoint_for_region(region)
        model = getattr(self, "_voiceTtsModelInput", None)
        if model is not None and not model.text:
            model.text = _tts.DEFAULT_MODEL

    def _onVoiceSensitivityChanged(self, value=None):
        """Retune a LIVE session, not just the next one.

        The detection threshold is derived once, from the room noise measured in
        the first second of a session. If that second happened to be loud, the
        threshold is pinned above normal speech for the rest of the session and
        the microphone simply never triggers -- with no error anywhere, because
        nothing has failed. Making this slider re-measure turns that from a
        restart into a drag.
        """
        listener = getattr(self, "_voiceListener", None)
        if listener is None:
            return
        try:
            listener.threshold_multiplier = float(
                self._voiceSetting("_voiceSensitivitySlider", "number", 3.0))
            listener.recalibrate()
            self._setVoiceStatus("Re-measuring room noise…")
        except Exception:
            logger.debug("Voice sensitivity change failed", exc_info=True)

    def _onVoiceRefreshDevices(self):
        combo = getattr(self, "_voiceDeviceCombo", None)
        if combo is None:
            return
        from SlicerAIAgentLib.voice import audio as _audio
        previous = combo.itemData(combo.currentIndex) if combo.count else None
        combo.clear()
        combo.addItem("System default", -1)
        devices = []
        try:
            devices = _audio.list_input_devices()
        except Exception:
            logger.debug("Listing input devices failed", exc_info=True)
        for device in devices:
            combo.addItem(str(device.get("name") or "Input"), int(device.get("index", -1)))
        if previous is not None:
            for index in range(combo.count):
                if combo.itemData(index) == previous:
                    combo.setCurrentIndex(index)
                    break
        self._refreshVoiceBackendBanner()
        if not devices and not self._voiceBackendMissing():
            # The backend is present and still reports no input: that is a
            # device or permission problem, and the banner would be wrong.
            self._setVoiceStatus("No input device found. Check that a microphone "
                                 "is connected and enabled for this application.")

    def _voiceBackendMissing(self):
        from SlicerAIAgentLib.voice import audio as _audio
        try:
            # auto_install=False: drawing a settings panel must never trigger a
            # network install as a side effect.
            return not _audio.ensure_audio_backend(auto_install=False)
        except Exception:
            logger.debug("Audio backend probe failed", exc_info=True)
            return False

    def _revealVoiceSettings(self):
        """Expand Settings and the Voice group so the banner is on screen.

        Both are collapsed by default, and a red banner nobody can see is the
        same as no banner.
        """
        try:
            root = getattr(self, "ui", None)
            settings = (root.findChild(ctk.ctkCollapsibleGroupBox, "settingsGroupBox")
                        if root is not None else None)
            if settings is not None:
                settings.collapsed = False
            group = getattr(self, "_voiceGroup", None)
            if group is not None:
                group.collapsed = False
        except Exception:
            logger.debug("Revealing the voice settings failed", exc_info=True)

    def _refreshVoiceBackendBanner(self):
        """Show or hide the red 'no audio backend' banner at the top."""
        banner = getattr(self, "_voiceBackendBanner", None)
        if banner is None:
            return
        from SlicerAIAgentLib.voice import audio as _audio
        text = ""
        if self._voiceBackendMissing():
            try:
                text = _audio.audio_backend_error()
            except Exception:
                logger.debug("Audio backend error read failed", exc_info=True)
            if not text:
                text = ("Microphone support is unavailable in this Python "
                        "environment. Voice stays off; the panel still works "
                        "with typed text.")
        try:
            banner.setText(text)
            banner.setVisible(bool(text))
        except Exception:
            logger.debug("Voice banner update failed", exc_info=True)

    # ------------------------------------------------------------------
    # Persistence. Chained onto the existing Save/Load so one button covers
    # both sections -- a separate Save here would be a second thing to forget.
    # ------------------------------------------------------------------

    def onSaveSettings(self):
        try:
            self._saveVoiceSettings()
        except Exception:
            logger.debug("Voice settings save failed", exc_info=True)
        return super(WidgetVoiceMixin, self).onSaveSettings()

    def loadSettings(self):
        result = super(WidgetVoiceMixin, self).loadSettings()
        try:
            self._loadVoiceSettings()
        except Exception:
            logger.debug("Voice settings load failed", exc_info=True)
        return result

    _VOICE_SETTING_WIDGETS = (
        ("voiceEnabled", "_voiceEnabledCheck", "check", False),
        ("voicePushToTalk", "_voicePttCheck", "check", True),
        ("voicePttKey", "_voicePttKeyCombo", "combo_text", "Space"),
        ("voiceAsrModel", "_voiceAsrModelCombo", "combo_text", ""),
        ("voiceAsrEndpoint", "_voiceAsrEndpointInput", "text", ""),
        ("voiceApiKey", "_voiceApiKeyInput", "text", ""),
        ("voiceSensitivity", "_voiceSensitivitySlider", "number", 3.0),
        ("voiceSilenceMs", "_voiceSilenceSlider", "number", 900.0),
        ("voiceSpeak", "_voiceSpeakCheck", "check", True),
        ("voiceTtsModel", "_voiceTtsModelInput", "text", ""),
        ("voiceTtsVoice", "_voiceVoiceCombo", "combo_text", ""),
        ("voiceTtsLanguage", "_voiceTtsLanguageCombo", "combo_text", "Auto"),
        ("voiceLlmFallback", "_voiceFallbackCheck", "check", True),
        ("voiceConfirm", "_voiceConfirmCheck", "check", False),
    )

    def _saveVoiceSettings(self):
        if getattr(self, "_voiceGroup", None) is None:
            return
        settings = qt.QSettings()
        settings.beginGroup(VOICE_SETTINGS_GROUP)
        for key, attribute, kind, _default in self._VOICE_SETTING_WIDGETS:
            widget = getattr(self, attribute, None)
            if widget is None:
                continue
            if kind == "check":
                settings.setValue(key, bool(widget.checked))
            elif kind == "text":
                settings.setValue(key, widget.text)
            elif kind == "combo_text":
                settings.setValue(key, widget.currentText)
            elif kind == "number":
                settings.setValue(key, float(widget.value))
        region = getattr(self, "_voiceRegionCombo", None)
        if region is not None:
            settings.setValue("voiceRegion", region.itemData(region.currentIndex))
        language = getattr(self, "_voiceLanguageCombo", None)
        if language is not None:
            settings.setValue("voiceLanguage", language.itemData(language.currentIndex))
        device = getattr(self, "_voiceDeviceCombo", None)
        if device is not None:
            settings.setValue("voiceInputDevice", int(device.itemData(device.currentIndex) or -1))
        settings.endGroup()
        self._applyVoiceSettingsToClients()
        # Without this, ticking "Enable voice control" and pressing Save leaves
        # the microphone button greyed out until Slicer is restarted -- the
        # button's enabled state is only recomputed here and on load.
        self._refreshVoiceButtonEnabled()

    def _loadVoiceSettings(self):
        if getattr(self, "_voiceGroup", None) is None:
            return
        from SlicerAIAgentLib.voice import asr_client as _asr
        from SlicerAIAgentLib.voice import tts_client as _tts

        settings = qt.QSettings()
        settings.beginGroup(VOICE_SETTINGS_GROUP)

        # Region FIRST: its change handler rewrites the model list and the
        # endpoint, so a stored endpoint applied before it would be discarded on
        # every startup -- the same ordering trap loadSettings already has with
        # provider/baseUrl.
        region_value = settings.value("voiceRegion", _asr.DEFAULT_REGION)
        combo = getattr(self, "_voiceRegionCombo", None)
        if combo is not None:
            for index in range(combo.count):
                if combo.itemData(index) == region_value:
                    combo.setCurrentIndex(index)
                    break
            self._onVoiceRegionChanged()

        for key, attribute, kind, default in self._VOICE_SETTING_WIDGETS:
            widget = getattr(self, attribute, None)
            if widget is None:
                continue
            raw = settings.value(key, default)
            try:
                if kind == "check":
                    widget.checked = _as_bool(raw, default)
                elif kind == "text":
                    if raw:
                        widget.text = str(raw)
                elif kind == "combo_text":
                    if raw:
                        widget.setCurrentText(str(raw))
                elif kind == "number":
                    widget.value = float(raw)
            except Exception:
                logger.debug("Voice setting %s could not be applied", key, exc_info=True)

        language = getattr(self, "_voiceLanguageCombo", None)
        stored_language = settings.value("voiceLanguage", "")
        if language is not None:
            for index in range(language.count):
                if (language.itemData(index) or "") == (stored_language or ""):
                    language.setCurrentIndex(index)
                    break

        device = getattr(self, "_voiceDeviceCombo", None)
        stored_device = settings.value("voiceInputDevice", -1)
        if device is not None:
            try:
                stored_device = int(stored_device)
            except (TypeError, ValueError):
                stored_device = -1
            for index in range(device.count):
                if device.itemData(index) == stored_device:
                    device.setCurrentIndex(index)
                    break

        model = getattr(self, "_voiceTtsModelInput", None)
        if model is not None and not model.text:
            model.text = _tts.DEFAULT_MODEL
        settings.endGroup()
        self._applyVoiceSettingsToClients()
        self._refreshVoiceButtonEnabled()

    # ------------------------------------------------------------------
    # Clients
    # ------------------------------------------------------------------

    def _applyVoiceSettingsToClients(self):
        asr = getattr(self, "_voiceAsrClient", None)
        if asr is not None:
            asr.setApiKey(self._voiceSetting("_voiceApiKeyInput", "text", ""))
            asr.setEndpoint(self._voiceSetting("_voiceAsrEndpointInput", "text", ""))
            asr.setModel(self._voiceSetting("_voiceAsrModelCombo", "combo_text", ""))
            asr.setLanguage(self._voiceLanguageCode())
        tts = getattr(self, "_voiceTtsClient", None)
        if tts is not None:
            tts.setApiKey(self._voiceSetting("_voiceApiKeyInput", "text", ""))
            tts.setEndpoint(self._voiceTtsEndpoint())
            tts.setModel(self._voiceSetting("_voiceTtsModelInput", "text", ""))
            tts.setVoice(self._voiceSetting("_voiceVoiceCombo", "combo_text", "Cherry"))
            tts.setLanguageType(self._voiceSetting("_voiceTtsLanguageCombo", "combo_text", "Auto"))

    def _voiceSetting(self, attribute, kind, default):
        widget = getattr(self, attribute, None)
        if widget is None:
            return default
        try:
            if kind == "text":
                return widget.text or default
            if kind == "combo_text":
                return widget.currentText or default
            if kind == "check":
                return bool(widget.checked)
            if kind == "number":
                return float(widget.value)
        except Exception:
            logger.debug("Reading voice setting %s failed", attribute, exc_info=True)
        return default

    def _voiceLanguageCode(self):
        combo = getattr(self, "_voiceLanguageCombo", None)
        if combo is None:
            return ""
        return combo.itemData(combo.currentIndex) or ""

    def _voiceTtsEndpoint(self):
        """Speech-out shares the region the speech-in endpoint was chosen for.

        Both are the same DashScope multimodal-generation path, and one API key
        is entered for both, so deriving it removes a field that could only ever
        be set to a value inconsistent with the key.
        """
        from SlicerAIAgentLib.voice import asr_client as _asr
        from SlicerAIAgentLib.voice import tts_client as _tts
        endpoint = self._voiceSetting("_voiceAsrEndpointInput", "text", "")
        # region_for_endpoint returns "" (not a default) for an endpoint it does
        # not recognise, deliberately -- labelling a mistyped host "us" would
        # silently offer the US model list. Here an unknown host just means we
        # cannot derive a region, so fall back explicitly.
        region = (_asr.region_for_endpoint(endpoint) if endpoint else "") or _asr.DEFAULT_REGION
        return _tts.ENDPOINTS.get(region) or _tts.DEFAULT_ENDPOINT

    def _voiceAsr(self):
        if getattr(self, "_voiceAsrClient", None) is None:
            from SlicerAIAgentLib.voice.asr_client import QwenASRClient
            self._voiceAsrClient = QwenASRClient(
                log_transcripts=VOICE_LOG_TRANSCRIPTS,
                timeout=VOICE_ASR_TIMEOUT_SECONDS)
            self._applyVoiceSettingsToClients()
        return self._voiceAsrClient

    def _voiceTts(self):
        if getattr(self, "_voiceTtsClient", None) is None:
            from SlicerAIAgentLib.voice.tts_client import QwenTTSClient
            self._voiceTtsClient = QwenTTSClient()
            self._applyVoiceSettingsToClients()
        return self._voiceTtsClient

    def _voiceAsrConfigured(self):
        try:
            return bool(self._voiceSetting("_voiceApiKeyInput", "text", "")
                        and self._voiceSetting("_voiceAsrEndpointInput", "text", "")
                        and self._voiceSetting("_voiceAsrModelCombo", "combo_text", ""))
        except Exception:
            return False

    def _voiceEnabled(self):
        return bool(self._voiceSetting("_voiceEnabledCheck", "check", False))

    def _refreshVoiceButtonEnabled(self):
        button = getattr(self, "_voiceButton", None)
        if button is None:
            return
        usable = self._voiceEnabled() and self._voiceAsrConfigured()
        try:
            button.setEnabled(bool(usable) or bool(getattr(self, "_voiceListening", False)))
            button.setToolTip(self._voiceButtonTooltip())
        except Exception:
            logger.debug("Voice button refresh failed", exc_info=True)

    def _setVoiceStatus(self, text):
        """Status goes three places, because each is invisible in some state.

        The Settings label is authoritative but that group is collapsed by
        default; the Debug conversation has the full transcript but is also
        collapsed; the mic button's tooltip is the only one reachable without
        opening anything, so the latest line lives there too.
        """
        label = getattr(self, "_voiceStatusLabel", None)
        if label is not None:
            try:
                label.setText(str(text or ""))
            except Exception:
                logger.debug("Voice status write failed", exc_info=True)
        button = getattr(self, "_voiceButton", None)
        if button is not None:
            try:
                button.setToolTip(self._voiceButtonTooltip(str(text or "")))
            except Exception:
                logger.debug("Voice tooltip write failed", exc_info=True)
        if text:
            logger.info("Voice: %s", text)

    # ------------------------------------------------------------------
    # Test buttons
    # ------------------------------------------------------------------

    def _onVoiceTestAsr(self):
        self._applyVoiceSettingsToClients()
        client = self._voiceAsr()
        self._setVoiceStatus("Testing the speech endpoint…")
        slicer.app.processEvents()
        # A probe runs synchronously on the Qt thread, exactly like the agent's
        # own Test Connection -- but the working timeout is 60 s and the retry
        # budget is 3, so an unreachable host would freeze Slicer for minutes.
        # A test is allowed to be impatient in a way a real transcription is not.
        original_timeout = client.timeout
        try:
            client.timeout = 15
            result = client.test_connection()
        finally:
            client.timeout = original_timeout
        if result.get("success"):
            self._setVoiceStatus("Speech endpoint reachable (%.1f s)." % result.get("seconds", 0.0))
            slicer.util.infoDisplay(
                "Speech recognition is reachable.\n\n"
                "Model: %s\nEndpoint: %s" % (client.model, client.endpoint))
        else:
            self._setVoiceStatus(result.get("error") or "Speech endpoint test failed.")
            slicer.util.warningDisplay("Speech recognition test failed:\n\n%s"
                                       % (result.get("error") or "Unknown error"))

    def _onVoiceTestTts(self):
        self._applyVoiceSettingsToClients()
        client = self._voiceTts()
        reason = client.unavailable_reason()
        if reason:
            slicer.util.warningDisplay(reason)
            return
        self._setVoiceStatus("Synthesising a test phrase…")
        slicer.app.processEvents()
        try:
            result = client.synthesize(
                "Voice control is ready. I will read each step aloud.")
        except Exception as error:
            self._setVoiceStatus(str(error))
            slicer.util.warningDisplay("Speech output test failed:\n\n%s" % error)
            return
        player = self._voicePlayerInstance()
        played = player.play(result.audio, result.audio_format)
        if played:
            self._setVoiceStatus("Spoke a test phrase (%s, %d KB)."
                                 % (result.audio_format or "unknown",
                                    len(result.audio) // 1024))
        else:
            # Synthesis worked and playback did not -- naming which half failed
            # is the difference between "check your key" and "install a codec".
            self._setVoiceStatus(player.last_error or "Playback failed.")
            slicer.util.warningDisplay(
                "The speech was synthesised (%s, %d bytes) but could not be "
                "played:\n\n%s" % (result.audio_format or "unknown",
                                   len(result.audio), player.last_error))

    def _voicePlayerInstance(self):
        if getattr(self, "_voicePlayer", None) is None:
            from SlicerAIAgentLib.voice.audio import AudioPlayer
            self._voicePlayer = AudioPlayer()
        return self._voicePlayer

    # ------------------------------------------------------------------
    # Listening session
    # ------------------------------------------------------------------

    def _onVoiceButtonClicked(self):
        if getattr(self, "_voiceListening", False):
            self._stopVoiceListening("stopped by the user")
            return
        self._startVoiceListening()

    def _startVoiceListening(self):
        if getattr(self, "_voiceListening", False):
            return
        if not self._voiceEnabled():
            slicer.util.warningDisplay(
                "Voice control is switched off.\n\n"
                "Settings ▸ Voice control ▸ Enable voice control.")
            self._setVoiceButtonChecked(False)
            return
        self._applyVoiceSettingsToClients()
        reason = self._voiceAsr().unavailable_reason()
        if reason:
            slicer.util.warningDisplay(reason)
            self._setVoiceButtonChecked(False)
            return

        self._setVoiceStatus("Preparing the microphone…")
        self._setVoiceButtonChecked(True)
        self._setVoiceButtonStyle(self._VOICE_LISTENING_STYLE)
        self._voiceListening = True
        # A microphone SESSION token, separate from the guided-session epoch.
        # MicListener.stop() emits a final "stopped" state, which lands in
        # _streamQueue and is handled up to 50 ms later -- by which time the user
        # may have already clicked the button back on. Without this token that
        # stale event tears down the session that just started, and the mic
        # appears to refuse to stay on.
        self._voiceSessionSeq = getattr(self, "_voiceSessionSeq", 0) + 1
        session = self._voiceSessionSeq
        self._voicePendingCommand = None
        self._voicePendingStep = None
        self._voiceSpokenStepKey = None
        self._voiceRefreshLogDir()

        device = getattr(self, "_voiceDeviceCombo", None)
        device_index = device.itemData(device.currentIndex) if device is not None else -1
        device_index = None if device_index in (None, -1) else int(device_index)

        # The FIRST start may pip-install the audio backend, which blocks for
        # tens of seconds. Doing it on the Qt thread would freeze Slicer with no
        # explanation, so the whole start-up runs on a worker and reports back
        # through the stream queue like every other background producer here.
        silence_ms = int(self._voiceSetting("_voiceSilenceSlider", "number", 900.0))
        margin = float(self._voiceSetting("_voiceSensitivitySlider", "number", 3.0))
        push_to_talk = self._voicePttEnabled()
        self._voicePttActive = push_to_talk

        asr = self._voiceAsr()
        tts = self._voiceTts()
        _voice_debug("session %d starting | mode=%s device=%s silence=%dms margin=%.1f",
                     session, "push-to-talk (Space)" if push_to_talk else "always-on",
                     device_index if device_index is not None else "default",
                     silence_ms, margin)
        _voice_debug("  asr: %s | model=%s | lang=%s | key=%s",
                     asr.endpoint, asr.model, asr.language or "auto",
                     "set" if asr.api_key else "MISSING")
        _voice_debug("  tts: %s | model=%s | voice=%s | speak=%s",
                     tts.endpoint, tts.model, tts.voice,
                     self._voiceSetting("_voiceSpeakCheck", "check", True))
        _voice_debug("  llm fallback=%s | confirm=%s | transcripts logged=%s",
                     self._voiceSetting("_voiceFallbackCheck", "check", True),
                     self._voiceSetting("_voiceConfirmCheck", "check", False),
                     VOICE_LOG_TRANSCRIPTS)

        def _start():
            try:
                from SlicerAIAgentLib.voice import audio as _audio
                if not _audio.ensure_audio_backend():
                    raise _audio.AudioUnavailable(
                        _audio.audio_backend_error()
                        or "The audio backend could not be installed.")
                listener = _audio.MicListener(
                    on_utterance=(lambda wav, secs, _s=session:
                                  self._voiceOnUtterance(wav, secs, _s)),
                    on_state=(lambda state, detail, _s=session:
                              self._voiceOnListenerState(state, detail, _s)),
                    device=device_index,
                    silence_ms=silence_ms,
                    threshold_multiplier=margin,
                    push_to_talk=push_to_talk,
                )
                listener.start()
                if session != getattr(self, "_voiceSessionSeq", 0):
                    # Stopped again while the backend was installing.
                    _voice_debug("session %d abandoned: stopped during start-up",
                                 session)
                    listener.stop()
                    return
                _voice_debug("session %d live | %d Hz, %d ms blocks, preroll %d ms",
                             session, listener.sample_rate, listener.block_ms,
                             listener.preroll_ms)
                self._voiceListener = listener
                self._streamQueue.put(("voice_state", {"state": "started",
                                                       "session": session}))
            except Exception as error:
                # Clear the flags HERE as well as through the event. Exit drains
                # _streamQueue wholesale, so the fatal event can be swallowed --
                # and then the widget would believe it is listening with no
                # listener, and the button would refuse to start a new one.
                self._voiceListening = False
                self._voiceListener = None
                self._streamQueue.put(("voice_error", {
                    "message": str(error), "fatal": True, "session": session}))

        threading.Thread(target=_start, daemon=True).start()

    def _stopVoiceListening(self, reason="", announce=True, synchronous=False):
        """Close the session. Safe to call twice and from any exit path.

        ``MicListener.stop()`` joins its capture and dispatch threads with a 2 s
        timeout each, and the dispatch thread is where a transcription HTTP call
        lives -- so switching the microphone off mid-sentence could freeze the
        Qt main thread for seconds. The listener is detached from this widget
        first and then shut down on a worker, since it is safe to stop from any
        thread and nothing here waits on the result. ``synchronous=True`` is for
        teardown, where the thread must be gone before the module unloads.
        """
        # Give Space back FIRST. It is a global key hook, so leaving it behind
        # would keep stealing the key from the rest of the application after
        # voice control is off -- the worst kind of leak.
        self._removeVoicePttHook()
        self._voicePttActive = False
        listener = getattr(self, "_voiceListener", None)
        self._voiceListener = None
        self._voiceListening = False
        self._voiceTranscribing = False
        self._voicePendingCommand = None
        self._voicePendingStep = None
        # Retire the microphone session BEFORE stopping the listener: stop()
        # emits a final "stopped" state, and it must not be able to tear down a
        # session the user starts again in the next few milliseconds.
        self._voiceSessionSeq = getattr(self, "_voiceSessionSeq", 0) + 1
        # Invalidate anything queued or mid-synthesis. The worker checks the
        # generation before it plays, so nothing from the closed session speaks.
        lock = getattr(self, "_voiceSpeechLock", None)
        if lock is not None:
            with lock:
                del self._voiceSpeechQueue[:]
                self._voiceSpeechSeq = getattr(self, "_voiceSpeechSeq", 0) + 1
        else:
            self._voiceSpeechSeq = getattr(self, "_voiceSpeechSeq", 0) + 1
        if listener is not None:
            def _shutdown():
                try:
                    listener.stop()
                except Exception:
                    logger.debug("Mic listener stop failed", exc_info=True)
            if synchronous:
                _shutdown()
            else:
                threading.Thread(target=_shutdown, daemon=True).start()
        player = getattr(self, "_voicePlayer", None)
        if player is not None:
            try:
                player.stop()
            except Exception:
                logger.debug("Voice playback stop failed", exc_info=True)
        self._setVoiceButtonChecked(False)
        self._setVoiceButtonStyle(self._VOICE_IDLE_STYLE)
        if announce and reason:
            self._setVoiceStatus("Microphone off — %s." % reason)
        _voice_debug("session %d closed%s",
                     getattr(self, "_voiceSessionSeq", 0),
                     (" (%s)" % reason) if reason else "")
        self._refreshVoiceButtonEnabled()

    def _setVoiceButtonChecked(self, checked):
        button = getattr(self, "_voiceButton", None)
        if button is None:
            return
        try:
            button.blockSignals(True)
            button.setChecked(bool(checked))
        except Exception:
            logger.debug("Voice button check failed", exc_info=True)
        finally:
            try:
                button.blockSignals(False)
            except Exception:
                pass

    def _setVoiceButtonStyle(self, style):
        button = getattr(self, "_voiceButton", None)
        if button is None:
            return
        try:
            button.setStyleSheet(style or "")
        except Exception:
            logger.debug("Voice button style failed", exc_info=True)

    # -- worker-thread callbacks -----------------------------------------

    def _voiceOnListenerState(self, state, detail, session=None):
        """Capture-thread state change. Only queues; touches nothing."""
        detail = dict(detail or {})
        if state != "idle" or detail:
            _voice_debug("vad: %-11s %s", state,
                         " ".join("%s=%s" % (k, _fmt_debug(v))
                                  for k, v in sorted(detail.items())))
        try:
            self._streamQueue.put(("voice_state", {"state": state,
                                                   "detail": detail,
                                                   "session": session}))
        except Exception:
            logger.debug("Voice state queue failed", exc_info=True)

    def _voiceOnUtterance(self, wav_bytes, seconds, session=None):
        """One captured sentence: transcribe it and queue the transcript.

        Runs on the listener's dispatch thread. TWO fences apply and they are
        not the same thing: ``session`` retires an utterance captured by a
        microphone session the user has since closed, and the guided-session
        ``epoch`` -- captured HERE rather than at listen time, so a sentence
        spoken after one workflow ends and another starts belongs to the one it
        was spoken in -- retires it against a workflow that has been exited.
        """
        if session is not None and session != getattr(self, "_voiceSessionSeq", 0):
            _voice_debug("utterance dropped: session %s is closed", session)
            return
        epoch = getattr(self, "_guidedSessionEpoch", 0)
        _voice_debug("utterance: %.2fs, %d bytes -> asr", seconds, len(wav_bytes or b""))
        try:
            client = self._voiceAsr()
            client.setDebugOutputDir(getattr(self, "_voiceLogDir", None))
            result = client.transcribe(wav_bytes, audio_seconds=seconds)
        except Exception as error:
            _voice_debug("asr FAILED: %s", error)
            self._streamQueue.put(("voice_error", {"message": str(error),
                                                   "fatal": False,
                                                   "session": session}))
            return
        _voice_debug("asr: %.2fs -> %r (lang=%s)", result.seconds,
                     (result.text or "")[:120], result.language or "?")
        if session is not None and session != getattr(self, "_voiceSessionSeq", 0):
            # The user switched the microphone off while this was in the API.
            _voice_debug("transcript dropped: session %s closed during the call",
                         session)
            return
        text = (result.text or "").strip()
        if len(text) < VOICE_MIN_TRANSCRIPT_CHARS:
            # A clip loud enough to trigger the detector went to the recogniser
            # and came back with nothing. Reported as its OWN state rather than
            # as idle: "the microphone hears nothing" and "the recogniser
            # understood nothing" have different remedies, and collapsing them
            # into "Listening." is what makes a broken setup look like a working
            # one that is simply waiting.
            logger.info("Voice: %.2fs of audio transcribed to nothing", seconds)
            self._streamQueue.put(("voice_state", {"state": "no_speech",
                                                   "seconds": seconds,
                                                   "session": session}))
            return
        logger.info("Voice heard (%d chars, %.2fs audio, %.2fs call)",
                    len(text), seconds, result.seconds)
        self._streamQueue.put(("voice_transcript", {
            "text": text,
            "epoch": epoch,
            "session": session,
            "seconds": result.seconds,
            "audio_seconds": result.audio_seconds,
            "language": result.language,
        }))

    # ------------------------------------------------------------------
    # Main-thread event handlers (dispatched from _drainStreamQueue)
    # ------------------------------------------------------------------

    def _voiceArmTranscribeWatchdog(self, pending, seconds):
        """Say so when a transcription is taking an unreasonable time.

        The recogniser runs on the listener's single dispatch thread, so a call
        that hangs does not merely lose one sentence: it blocks every later one
        until it returns, and the capture queue (bounded at 3) starts dropping.
        A hang therefore has to be *visible* rather than inferred from an
        absence of output — which is exactly how it presented.
        """
        def _check(elapsed):
            if not getattr(self, "_voiceTranscribing", False):
                return
            if getattr(self, "_voiceUtteranceSeq", 0) != pending:
                return
            client = getattr(self, "_voiceAsrClient", None)
            _voice_debug("asr STILL PENDING after %ds (%.1fs of audio, endpoint=%s, "
                         "model=%s, timeout=%ss)", elapsed, seconds,
                         getattr(client, "endpoint", "?"),
                         getattr(client, "model", "?"),
                         getattr(client, "timeout", "?"))
            self._setVoiceStatus(
                "Still transcribing after %d s. The speech endpoint is not "
                "answering — check the region, the key and the network, then "
                "press Test." % elapsed)

        for delay in (5000, 15000, 30000):
            qt.QTimer.singleShot(delay, lambda d=delay: _check(d // 1000))

    def _voiceEndTranscribing(self):
        self._voiceTranscribing = False

    # ------------------------------------------------------------------
    # Push-to-talk: the Space bar
    # ------------------------------------------------------------------

    def _voicePttEnabled(self):
        return bool(self._voiceSetting("_voicePttCheck", "check", True))

    def _voicePttBinding(self):
        """(qt key, qt modifiers, label, windows virtual-key) for the talk key."""
        combo = getattr(self, "_voicePttKeyCombo", None)
        spec = None
        label = "Space"
        if combo is not None:
            try:
                spec = combo.itemData(combo.currentIndex)
                label = combo.currentText
            except Exception:
                logger.debug("Talk-key read failed", exc_info=True)
        key_name, _, mod_name = (spec or "Key_Space|NoModifier").partition("|")
        key = getattr(qt.Qt, key_name, qt.Qt.Key_Space)
        modifiers = getattr(qt.Qt, mod_name or "NoModifier", qt.Qt.NoModifier)
        # Virtual-key codes for the polling fallback (Windows only).
        virtual_keys = {"Key_Space": 0x20, "Key_F4": 0x73, "Key_F8": 0x77}
        return key, modifiers, label, virtual_keys.get(key_name, 0x20)

    def _voicePttKeyLabel(self):
        return self._voicePttBinding()[2]

    def _installVoicePttHook(self):
        """Start watching for Space. Prefers an event filter, proves it works."""
        if getattr(self, "_voiceKeyFilter", None) is not None:
            return
        if getattr(self, "_voicePttPoller", None) is not None:
            return
        app = qt.QApplication.instance()
        key, modifiers, label, virtual_key = self._voicePttBinding()
        self._voicePttVirtualKey = virtual_key
        try:
            hook = _VoicePushToTalkFilter(key, modifiers,
                                          self._onVoicePttPress,
                                          self._onVoicePttRelease)
            app.installEventFilter(hook)
            self._voiceKeyFilter = hook
            if self._voicePttFilterVerified(hook):
                _voice_debug("ptt: %s watched by an application event filter", label)
                return
            app.removeEventFilter(hook)
            self._voiceKeyFilter = None
            _voice_debug("ptt: the event filter was never called; falling back "
                         "to polling the key state")
        except Exception as error:
            self._voiceKeyFilter = None
            _voice_debug("ptt: event filter unavailable (%s); falling back to "
                         "polling", error)
        self._startVoicePttPolling()

    def _voicePttFilterVerified(self, hook):
        """Send one synthetic key event and check the filter saw it.

        PythonQt cannot always dispatch a C++ virtual to a Python override, and
        a filter that is never called looks exactly like a key that does
        nothing. Better to find out at arm time, in one event, than to leave the
        user pressing Space at a microphone that will never hear them.
        """
        if _VoicePushToTalkFilter.PROBE_KEY is None:
            return False
        try:
            hook.probe_seen = False
            target = slicer.util.mainWindow() or qt.QApplication.instance()
            probe = qt.QKeyEvent(qt.QEvent.KeyPress,
                                 _VoicePushToTalkFilter.PROBE_KEY,
                                 qt.Qt.NoModifier)
            qt.QApplication.sendEvent(target, probe)
            return bool(hook.probe_seen)
        except Exception:
            logger.debug("Push-to-talk filter probe failed", exc_info=True)
            return False

    def _startVoicePttPolling(self):
        """Fallback: ask the OS whether Space is down, 30 times a second.

        Windows-only, because it is the only place this fallback is needed and
        ``GetAsyncKeyState`` is the only dependency-free way to ask. It reads
        the key state directly, so unlike an event filter it cannot miss a
        release delivered to a widget that has since lost focus -- but it is
        global, hence the active-window guard in the poll.
        """
        try:
            import ctypes
            self._voicePttUser32 = ctypes.windll.user32
        except Exception as error:
            self._voicePttUser32 = None
            _voice_debug("ptt: no key-state fallback on this platform (%s). "
                         "Push-to-talk is unavailable; use the always-on mode.",
                         error)
            self._setVoiceStatus(
                "Push-to-talk could not attach to the Space key on this "
                "platform. Untick it in Settings to use the always-on "
                "microphone instead.")
            return
        timer = qt.QTimer()
        timer.setInterval(30)
        timer.timeout.connect(self._pollVoicePttKey)
        timer.start()
        self._voicePttPoller = timer
        _voice_debug("ptt: talk key watched by key-state polling (30 ms)")

    def _pollVoicePttKey(self):
        user32 = getattr(self, "_voicePttUser32", None)
        if user32 is None:
            return
        try:
            virtual_key = int(getattr(self, "_voicePttVirtualKey", 0x20))
            down = bool(user32.GetAsyncKeyState(virtual_key) & 0x8000)
        except Exception:
            return
        if down == bool(getattr(self, "_voicePttDown", False)):
            return
        if down:
            # Polling cannot CONSUME the key, so Qt still delivers it. Space on
            # a focused QAbstractButton is "click me" -- and the button that
            # most often has focus here is the one the user just pressed, so
            # holding Space to talk would re-activate Done and advance the step
            # a second time. Take focus off it first. (The event-filter path
            # does not need this: it consumes the key, so the button never
            # sees it.)
            self._voiceDefocusButton()
            if self._onVoicePttPress():
                self._voicePttDown = True
        else:
            self._voicePttDown = False
            self._onVoicePttRelease()

    def _voiceDefocusButton(self):
        try:
            widget = qt.QApplication.focusWidget()
            if widget is not None and widget.inherits("QAbstractButton"):
                widget.clearFocus()
        except Exception:
            logger.debug("Clearing button focus failed", exc_info=True)

    def _removeVoicePttHook(self):
        hook = getattr(self, "_voiceKeyFilter", None)
        self._voiceKeyFilter = None
        if hook is not None:
            try:
                qt.QApplication.instance().removeEventFilter(hook)
            except Exception:
                logger.debug("Removing the push-to-talk filter failed", exc_info=True)
        timer = getattr(self, "_voicePttPoller", None)
        self._voicePttPoller = None
        if timer is not None:
            try:
                timer.stop()
            except Exception:
                logger.debug("Stopping the push-to-talk poller failed", exc_info=True)
        self._voicePttDown = False

    def _voiceKeyGoesToTextEntry(self):
        """True when Space belongs to whatever the user is typing in.

        Taking Space away from a text field would be an immediate, obvious
        regression -- the prompt box is right below the microphone button.
        """
        try:
            widget = qt.QApplication.focusWidget()
        except Exception:
            return False
        if widget is None:
            return False
        for class_name in ("QLineEdit", "QTextEdit", "QPlainTextEdit",
                           "QAbstractSpinBox", "QKeySequenceEdit"):
            try:
                if widget.inherits(class_name):
                    return True
            except Exception:
                continue
        try:
            if widget.inherits("QComboBox") and widget.isEditable():
                return True
        except Exception:
            logger.debug("Editable-combo focus probe failed", exc_info=True)
        return False

    def _voicePttWouldClaimKey(self):
        """Whether the key belongs to us right now. No side effects.

        Shared by the ShortcutOverride probe and the real press, so the two can
        never disagree about who owns the key.
        """
        if not getattr(self, "_voiceListening", False):
            return False
        if not getattr(self, "_voicePttActive", False):
            return False
        if self._voiceKeyGoesToTextEntry():
            return False
        try:
            # A modal is the user's whole world while it is up, and Space
            # activates its default button. The Exit-confirmation dialog is
            # modal -- stealing Space there would leave it undismissable from
            # the keyboard.
            if qt.QApplication.activeModalWidget() is not None:
                return False
            if qt.QApplication.activePopupWidget() is not None:
                return False
        except Exception:
            logger.debug("Modal/popup probe failed", exc_info=True)
        try:
            window = slicer.util.mainWindow()
            if window is not None and not window.isActiveWindow():
                # The polling fallback is global; without this it would record
                # while the user is pressing the key in another application.
                return False
        except Exception:
            logger.debug("Active-window probe failed", exc_info=True)
        return getattr(self, "_voiceListener", None) is not None

    def _onVoicePttPress(self, probe_only=False):
        """Key down. Returns True when it started (or would start) a recording."""
        if not self._voicePttWouldClaimKey():
            return False
        if probe_only:
            return True
        listener = getattr(self, "_voiceListener", None)
        if listener is None:
            return False
        # Barge-in. Pressing the key means "I am talking now", which is exactly
        # the moment to stop the app talking -- and the mic is muted while it
        # speaks, so without this the key would start a recording of silence.
        self._voiceStopSpeaking()
        try:
            listener.begin_talk()
        except Exception:
            logger.debug("begin_talk failed", exc_info=True)
            return False
        _voice_debug("ptt: key down -- recording")
        self._setVoiceStatus("Recording — keep %s held, release to send."
                             % self._voicePttKeyLabel())
        self._setVoiceButtonStyle(self._VOICE_LISTENING_STYLE)
        return True

    def _onVoicePttRelease(self):
        """Space up. Returns True when it ended a recording."""
        listener = getattr(self, "_voiceListener", None)
        if listener is None:
            return False
        if not listener.is_talking():
            return False
        try:
            listener.end_talk()
        except Exception:
            logger.debug("end_talk failed", exc_info=True)
            return False
        _voice_debug("ptt: key up -- sending")
        self._setVoiceStatus("Sending…")
        return True

    def _voiceStopSpeaking(self):
        """Cut any announcement immediately and give the microphone back."""
        lock = getattr(self, "_voiceSpeechLock", None)
        if lock is not None:
            with lock:
                del self._voiceSpeechQueue[:]
                self._voiceSpeechSeq = getattr(self, "_voiceSpeechSeq", 0) + 1
        player = getattr(self, "_voicePlayer", None)
        if player is not None:
            try:
                player.stop()
            except Exception:
                logger.debug("Barge-in playback stop failed", exc_info=True)
        listener = getattr(self, "_voiceListener", None)
        if listener is not None:
            try:
                listener.unmute()
            except Exception:
                logger.debug("Barge-in unmute failed", exc_info=True)

    def _voiceListenerLevel(self):
        listener = getattr(self, "_voiceListener", None)
        try:
            return float(listener.level) if listener is not None else 0.0
        except Exception:
            return 0.0

    def _voiceListenerThreshold(self):
        listener = getattr(self, "_voiceListener", None)
        try:
            return float(listener.threshold) if listener is not None else 0.0
        except Exception:
            return 0.0

    def _voiceEventIsCurrent(self, payload):
        """Drop an event belonging to a microphone session already closed."""
        session = (payload or {}).get("session")
        return session is None or session == getattr(self, "_voiceSessionSeq", 0)

    def _handleVoiceState(self, payload):
        if not self._voiceEventIsCurrent(payload):
            return
        state = str((payload or {}).get("state") or "")
        if state == "started":
            if getattr(self, "_voicePttActive", False):
                # The hook goes on only once the stream is actually open, so
                # Space is never taken over by a session that failed to start.
                self._installVoicePttHook()
                self._setVoiceStatus(
                    "Ready. Hold %s, speak, then release. It still behaves "
                    "normally in a text box." % self._voicePttKeyLabel())
            elif (getattr(self, "_currentWorkflowUiState", None) or {}).get("active"):
                self._setVoiceStatus(
                    "Listening. Answer the step, or say \"stop listening\".")
            else:
                # Say what actually starts a run. This is text only -- speaking
                # it would mute the microphone for the first thing said to it.
                self._setVoiceStatus(
                    "Listening. Say \"plan …\" or \"start …\" followed by the "
                    "procedure, for example \"plan the orbital fracture "
                    "reconstruction\".")
            self._refreshVoiceButtonEnabled()
            # The backend is demonstrably present now -- if the banner was up
            # (installed in this session, or a stale probe), take it down.
            self._refreshVoiceBackendBanner()
            # Announce whatever is already on screen, so starting the mic
            # mid-procedure does not leave the user waiting for a prompt that
            # only fires on the NEXT step.
            self._voiceMaybeAnnounceStep(force=True)
        elif state == "calibrating":
            self._setVoiceStatus("Measuring room noise…")
        elif state == "speech":
            detail = (payload or {}).get("detail") or {}
            self._setVoiceStatus("Hearing you… (level %.3f, threshold %.3f)"
                                 % (float(detail.get("level") or 0.0),
                                    self._voiceListenerThreshold()))
        elif state == "captured":
            detail = (payload or {}).get("detail") or {}
            seconds = float(detail.get("seconds") or 0.0)
            # The capture thread emits "idle" microseconds after "captured" --
            # it has finished with the microphone and is ready for the next
            # sentence. Without this flag that idle immediately overwrote
            # "Transcribing…" with "nothing heard yet", i.e. the panel claimed
            # to have heard nothing while it was busy transcribing 2.4 s of
            # audio. Cleared by every outcome: transcript, no-speech, or error.
            self._voiceTranscribing = True
            self._voiceUtteranceSeq = getattr(self, "_voiceUtteranceSeq", 0) + 1
            pending = self._voiceUtteranceSeq
            self._setVoiceStatus("Transcribing %.1f s of audio…" % seconds)
            self._voiceArmTranscribeWatchdog(pending, seconds)
        elif state == "muted":
            self._setVoiceStatus("Microphone paused while speaking.")
        elif state == "dropped":
            detail = (payload or {}).get("detail") or {}
            self._setVoiceStatus(
                "Dropped a %.1f s utterance — %s. Wait for \"Listening\" before "
                "speaking again."
                % (float(detail.get("seconds") or 0.0),
                   detail.get("reason") or "the recogniser is behind"))
        elif state == "no_speech":
            self._voiceEndTranscribing()
            # NOT the same as idle, and reverting to "Listening." here is what
            # made three different failures look identical. Sound loud enough to
            # trigger the detector reached the recogniser and came back empty:
            # too quiet, the wrong input device, or the wrong spoken language.
            self._setVoiceStatus(
                "Captured %.1f s of audio but recognised no words. Check the "
                "microphone in this section, speak closer to it, and confirm "
                "the spoken language." % float((payload or {}).get("seconds") or 0.0))
        elif state == "idle":
            detail = (payload or {}).get("detail") or {}
            if not getattr(self, "_voiceListening", False):
                pass
            elif getattr(self, "_voiceTranscribing", False):
                # The microphone is idle; the recogniser is not. Saying
                # "nothing heard yet" here is simply false.
                pass
            elif detail.get("discarded"):
                self._setVoiceStatus(
                    "That was too short to be a command — hold the talk key "
                    "for the whole phrase."
                    if getattr(self, "_voicePttActive", False) else
                    "That was too short to be a command — say the whole phrase "
                    "in one breath.")
            elif getattr(self, "_voicePttActive", False):
                # No threshold is involved in push-to-talk, so quoting one would
                # be meaningless. The level still helps: it says whether the
                # device is delivering anything at all.
                self._setVoiceStatus("Ready. Hold %s to talk. (level %.3f)"
                                     % (self._voicePttKeyLabel(),
                                        self._voiceListenerLevel()))
            else:
                self._setVoiceStatus("Listening. (nothing heard yet — level %.3f, "
                                     "threshold %.3f)"
                                     % (self._voiceListenerLevel(),
                                        self._voiceListenerThreshold()))
        elif state == "stopped":
            self._stopVoiceListening("the input stream closed")
        elif state == "error":
            detail = (payload or {}).get("detail") or {}
            self._setVoiceStatus(str(detail.get("error") or "Microphone error."))

    def _handleVoiceError(self, payload):
        if not self._voiceEventIsCurrent(payload):
            return
        payload = payload or {}
        message = str(payload.get("message") or "Voice error.")
        self._voiceEndTranscribing()
        self._setVoiceStatus(message)
        if payload.get("fatal"):
            self._stopVoiceListening("", announce=False)
            self._setVoiceStatus(message)
            # A failed start is most often the missing backend. The modal still
            # fires -- the user pressed a button and deserves an answer -- but
            # the banner is where the remedy LIVES, because a modal is dismissed
            # and gone while the install line has to be copied. Open the group
            # so the banner is actually on screen: it is collapsed by default.
            self._refreshVoiceBackendBanner()
            self._revealVoiceSettings()
            slicer.util.warningDisplay("Voice control could not start:\n\n%s\n\n"
                                       "The same message is in Settings ▸ Voice "
                                       "control, where it can be copied."
                                       % message)
            return
        # A wrong region, a bad key or a model id that does not exist there
        # fails EVERY utterance in exactly the same way. Treating each one as a
        # transient blip leaves a microphone that looks alive and never acts,
        # with the only symptom in a collapsed group. After a few identical
        # failures, stop and say so where it cannot be missed.
        streak = getattr(self, "_voiceAsrErrorStreak", 0) + 1
        self._voiceAsrErrorStreak = streak
        if streak >= VOICE_MAX_CONSECUTIVE_ASR_ERRORS:
            self._stopVoiceListening("", announce=False)
            self._setVoiceStatus(message)
            slicer.util.warningDisplay(
                "Voice control stopped after %d failed transcriptions.\n\n%s\n\n"
                "Check the region, the speech model and the API key in "
                "Settings ▸ Voice control, then press Test." % (streak, message))

    def _handleVoiceSpeechDone(self, payload):
        """The speech queue drained. The microphone was already given back by
        the speech thread; this is only the UI half."""
        payload = payload or {}
        if not payload.get("idle"):
            return  # another speaker took over; it owns the button state
        self._setVoiceButtonStyle(
            self._VOICE_LISTENING_STYLE if getattr(self, "_voiceListening", False)
            else self._VOICE_IDLE_STYLE)
        error = payload.get("error")
        if error:
            self._setVoiceStatus(str(error))
        elif getattr(self, "_voiceListening", False):
            self._setVoiceStatus("Listening.")

    def _handleVoiceTranscript(self, payload):
        if not self._voiceEventIsCurrent(payload):
            return
        payload = payload or {}
        text = str(payload.get("text") or "").strip()
        if not text:
            return
        if not self._guidedSessionAlive(payload.get("epoch")):
            logger.info("Dropping voice transcript: the guided session was reset")
            return
        # _drainStreamQueue is RE-ENTRANT: it pumps the Qt event loop, and so
        # does everything applying a command does (_runWorkflowStepDirect
        # executes template code). Without this guard a second utterance queued
        # while the first is being applied is handled INSIDE the first, and the
        # step is dispatched twice -- placing two markups, or answering a step
        # and then answering the one after it with the same word.
        if getattr(self, "_voiceHandlingTranscript", False):
            logger.info("Voice: deferring a transcript that arrived mid-dispatch")
            self._voiceDeferredTranscripts.append(payload)
            return
        self._voiceHandlingTranscript = True
        try:
            self._handleVoiceTranscriptInner(payload, text)
        finally:
            self._voiceHandlingTranscript = False
        self._voiceDrainDeferred()

    def _voiceDrainDeferred(self):
        """Replay whatever was parked during a dispatch, at top level.

        BOTH queues, in both drains: a tier-2 answer that landed while a
        transcript was being applied is parked in the command queue, and only
        the transcript drain is about to run -- leaving it stranded until the
        next utterance happened to arrive.
        """
        while True:
            if getattr(self, "_voiceDeferredTranscripts", None):
                self._handleVoiceTranscript(self._voiceDeferredTranscripts.pop(0))
                continue
            if getattr(self, "_voiceDeferredCommands", None):
                self._handleVoiceCommand(self._voiceDeferredCommands.pop(0))
                continue
            return

    def _handleVoiceTranscriptInner(self, payload, text):
        # A transcript arrived, so whatever was failing has stopped failing.
        self._voiceAsrErrorStreak = 0
        self._voiceEndTranscribing()
        self.appendToChat("Voice", text)
        self._setVoiceStatus("Heard: %s" % text)

        step = self._voiceStepGrammar()
        from SlicerAIAgentLib.voice import commands as _commands
        pending = getattr(self, "_voicePendingCommand", None)
        if pending is not None and getattr(self, "_voicePendingStep", None) != step.step_id:
            # The workflow moved while the user was deciding. A "yes" now would
            # commit a value resolved against a step that is no longer on
            # screen -- on a node pick, a node name the new step never offered.
            logger.info("Voice: dropping a pending command; the step changed")
            self._voicePendingCommand = None
            self._voicePendingStep = None
            pending = None
        _voice_debug("step: family=%s id=%s can_done=%s can_skip=%s preview=%s",
                     step.family, step.step_id or "-", step.can_done, step.can_skip,
                     step.replay_previewing)
        options = step.option_labels()
        if options:
            _voice_debug("  options: %s", ", ".join(str(o) for o in options[:12])
                         + (" …(+%d)" % (len(options) - 12) if len(options) > 12 else ""))

        # Tier 1 only, here. It is pure computation and belongs beside the panel
        # it reads; tier 2 is an HTTP round trip and would freeze the Qt main
        # thread for the length of the call plus its retries.
        command = _commands.resolve(
            text, step, allow_llm=False,
            confirmation_pending=pending is not None,
        )
        if command.action == _commands.ACTION_NONE:
            scores = _commands.explain(text, step)
            if scores:
                _voice_debug("  no match (accept >= %.2f). scores: %s",
                             _commands.ACCEPT_SCORE,
                             ", ".join("%s=%.2f" % (label, score)
                                       for label, score in scores))
            elif command.rationale:
                _voice_debug("  no match: %s", command.rationale)
        else:
            _voice_debug("  resolved: %s value=%r label=%r conf=%.2f via %s",
                         command.action, command.value, command.label,
                         command.confidence, command.source)
        # An AMBIGUOUS result (command.options non-empty) deliberately does NOT
        # go to the model: two options fitting equally well is a question for
        # the surgeon, not a coin flip delegated to a second opinion.
        if (command.action == _commands.ACTION_NONE
                and not command.options
                and pending is None
                and step.expects_value()
                and self._voiceSetting("_voiceFallbackCheck", "check", True)):
            if self._voiceStartFallback(text, step, payload):
                return

        self._voiceHandleResolvedCommand(command, step, pending)

    def _voiceStartFallback(self, text, step, payload):
        """Run tier 2 on a worker. True when it was actually started.

        The step grammar is a flat snapshot with no live VTK or Qt objects in
        it, which is exactly what makes handing it to a worker legal.
        """
        llm_call = self._voiceLlmFallback()
        if llm_call is None:
            return False
        self._setVoiceStatus("Heard: %s — asking the model…" % text)
        epoch = (payload or {}).get("epoch")
        session = (payload or {}).get("session")

        def _ask():
            command = None
            try:
                from SlicerAIAgentLib.voice import commands as _commands
                command = _commands.resolve_llm(text, step, llm_call)
            except Exception:
                logger.debug("Voice fallback failed", exc_info=True)
            try:
                self._streamQueue.put(("voice_command", {
                    "command": command, "step": step,
                    "epoch": epoch, "session": session, "transcript": text}))
            except Exception:
                logger.debug("Voice command queue failed", exc_info=True)

        threading.Thread(target=_ask, daemon=True).start()
        return True

    def _handleVoiceCommand(self, payload):
        """A tier-2 result came back. Re-check that it still applies."""
        if not self._voiceEventIsCurrent(payload):
            return
        payload = payload or {}
        if not self._guidedSessionAlive(payload.get("epoch")):
            return
        if getattr(self, "_voiceHandlingTranscript", False):
            # Same re-entrancy hazard as _handleVoiceTranscript, reached through
            # the pumped event loop of a command already being applied.
            self._voiceDeferredCommands.append(payload)
            return
        self._voiceHandlingTranscript = True
        try:
            self._handleVoiceCommandInner(payload)
        finally:
            self._voiceHandlingTranscript = False
        self._voiceDrainDeferred()

    def _handleVoiceCommandInner(self, payload):
        step = payload.get("step")
        command = payload.get("command")
        current = (getattr(self, "_currentWorkflowUiState", None) or {}).get("current_step")
        if step is not None and step.step_id and step.step_id != current:
            # The workflow moved on while the model was answering. Applying now
            # would answer a step that is no longer on screen.
            logger.info("Dropping voice fallback: the step changed while it ran")
            self._setVoiceStatus("The step changed before that could be applied.")
            return
        if command is None:
            from SlicerAIAgentLib.voice import commands as _commands
            command = _commands.VoiceCommand(transcript=payload.get("transcript") or "",
                                             rationale="no confident match")
        self._voiceHandleResolvedCommand(command, step, None)

    def _voiceHandleResolvedCommand(self, command, step, pending):
        """Shared tail of both tiers: confirm-mode, refusal, or apply."""
        from SlicerAIAgentLib.voice import commands as _commands
        self._voiceRecordCommand(command)

        if pending is not None:
            if command.action == _commands.ACTION_CONFIRM:
                self._voicePendingCommand = None
                self._voicePendingStep = None
                self._voiceApply(pending)
                return
            if command.action == _commands.ACTION_ABORT:
                self._voicePendingCommand = None
                self._voicePendingStep = None
                self._voiceSpeak("Cancelled.")
                return
            # Anything else supersedes the pending command rather than queueing
            # behind it: the user has moved on.
            self._voicePendingCommand = None
            self._voicePendingStep = None

        if command.action == _commands.ACTION_NONE:
            self._voiceReportNoMatch(command, step)
            return

        if (self._voiceSetting("_voiceConfirmCheck", "check", False)
                and command.is_committing()):
            self._voicePendingCommand = command
            self._voicePendingStep = step.step_id if step is not None else None
            self._voiceSpeak("%s Say yes to confirm." % command.describe())
            return

        self._voiceApply(command)

    def _voiceReportNoMatch(self, command, step):
        from SlicerAIAgentLib.voice import grammar as _grammar
        if command.options:
            self._voiceSpeak("Did you mean %s?"
                             % _grammar._spoken_option_list(command.options, 4))
            return
        if command.rationale and command.confidence > 0:
            # A refusal with a reason (out of range, ambiguous) is worth saying;
            # a plain non-match is not, or the room would be answered constantly.
            self._voiceSpeak(command.rationale.capitalize() + ".")
            return
        self._setVoiceStatus("Heard: %s — no matching command." % command.transcript)

    def _voiceRecordCommand(self, command):
        try:
            # role_trace.json goes into the run folder, so the utterance itself
            # is withheld on the same terms as the ASR artifact -- what was
            # DECIDED is always recorded, what was overheard is opt-in.
            self._recordRoleEvent(
                "Voice", "command_resolved",
                command.to_log(include_transcript=VOICE_LOG_TRANSCRIPTS))
        except Exception:
            logger.debug("Voice role event failed", exc_info=True)

    def _voiceLlmFallback(self):
        """A callable for the second tier, or None when there is no client.

        Mirrors ``WorkflowRouter._call``: the low-level request path, so the call
        inherits provider handling and retries without writing
        ``conversation_history`` or bumping the turn counter -- a voice command
        is not a conversational turn.
        """
        logic = getattr(self, "logic", None)
        client = getattr(logic, "llmClient", None) if logic is not None else None
        if client is None or not getattr(client, "api_key", ""):
            return None

        def _call(system_prompt, user_prompt):
            messages = [{"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}]
            payload = client._buildPayload(
                messages, stream=False, tools=None, thinking=False,
                reasoning_effort="low", options={"temperature": 0.0})
            request = client._buildRequest(client._getChatUrl(), payload)
            data = client._fetchWithDiagnostics(request)
            if client._isClaude():
                data = client._normalizeClaudeResponse(data)
            return client._coerceText(data["choices"][0]["message"].get("content", ""))

        return _call

    # ------------------------------------------------------------------
    # Grammar: what the step on screen accepts
    # ------------------------------------------------------------------

    def _voiceStepGrammar(self):
        """Snapshot the panel. Main thread only -- it reads MRML and widgets."""
        from SlicerAIAgentLib.voice import grammar as _grammar
        state = dict(getattr(self, "_currentWorkflowUiState", None) or {"active": False})
        if not state.get("active"):
            return _grammar.build_step_grammar(state)

        nodes = []
        node_class = state.get("node_class") or ""
        if node_class:
            try:
                nodes = [{"id": entry.get("id"), "name": entry.get("name")}
                         for entry in self._workflowNodeCandidateList(state, node_class)]
            except Exception:
                logger.debug("Voice node candidate read failed", exc_info=True)

        segment_names, segments = [], []
        try:
            combo = getattr(self, "_workflowSegmentNameCombo", None)
            if combo is not None:
                segment_names = [combo.itemText(i) for i in range(combo.count)]
        except Exception:
            logger.debug("Voice segment-name read failed", exc_info=True)
        try:
            segments = self._voiceSegmentRows()
        except Exception:
            logger.debug("Voice segment row read failed", exc_info=True)

        multi_items = []
        try:
            # _workflowMultiChoiceOrdered is [(combo, options, question)] in the
            # order the selectors must be driven; the question is the label the
            # panel shows, and it is far better spoken than the parameter name
            # ("1st Instrumented Level" vs "c_1st_instrumented_level").
            combos = getattr(self, "_workflowMultiChoiceCombos", None) or {}
            for combo, options, question in (
                    getattr(self, "_workflowMultiChoiceOrdered", None) or []):
                param = None
                for name, widget in combos.items():
                    if widget is combo:
                        param = name
                        break
                multi_items.append({
                    "param": param,
                    "label": str(question or param or ""),
                    "options": [str(o) for o in (options or [])],
                })
        except Exception:
            logger.debug("Voice multi-choice read failed", exc_info=True)

        scalar_live, range_live = {}, {}
        try:
            widget = getattr(self, "_workflowScalarWidget", None)
            if widget is not None:
                scalar_live = {"min": float(widget.minimum), "max": float(widget.maximum),
                               "default": float(widget.value)}
        except Exception:
            logger.debug("Voice scalar bounds read failed", exc_info=True)
        try:
            widget = getattr(self, "_workflowRangeWidget", None)
            if widget is not None:
                range_live = {"min": float(widget.minimum), "max": float(widget.maximum),
                              "current_min": float(widget.minimumValue),
                              "current_max": float(widget.maximumValue)}
        except Exception:
            logger.debug("Voice range bounds read failed", exc_info=True)

        auto_pending = False
        try:
            auto_pending = self._soleNodeAutoSelectCandidate(state) is not None
        except Exception:
            logger.debug("Voice auto-select probe failed", exc_info=True)

        return _grammar.build_step_grammar(
            state, nodes=nodes, segment_names=segment_names, segments=segments,
            multi_items=multi_items, scalar_live=scalar_live, range_live=range_live,
            notice=getattr(self, "_workflowNoticeText", ""),
            auto_select_pending=auto_pending,
        )

    def _voiceSegmentationNode(self):
        """The segmentation the segments table is currently showing.

        PythonQt exposes a C++ getter either as a callable or, when it is a
        Q_PROPERTY, as a plain attribute -- and which one you get varies with the
        class and the build. Accept both rather than guessing: getting it wrong
        is a TypeError inside a voice command, i.e. a feature that silently does
        nothing on one Slicer version.
        """
        table = getattr(self, "_workflowSegmentsTable", None)
        if table is None:
            return None
        accessor = getattr(table, "segmentationNode", None)
        try:
            return accessor() if callable(accessor) else accessor
        except Exception:
            logger.debug("Segments table node read failed", exc_info=True)
            return None

    def _voiceSegmentRows(self):
        """Segments of the segmentation the segments table is bound to."""
        node = self._voiceSegmentationNode()
        if node is None:
            return []
        segmentation = node.GetSegmentation()
        display = node.GetDisplayNode()
        rows = []
        for index in range(segmentation.GetNumberOfSegments()):
            segment_id = segmentation.GetNthSegmentID(index)
            segment = segmentation.GetNthSegment(index)
            visible = True
            if display is not None:
                try:
                    visible = bool(display.GetSegmentVisibility(segment_id))
                except Exception:
                    logger.debug("Segment visibility read failed", exc_info=True)
            rows.append({"id": segment_id,
                         "name": str(segment.GetName() or segment_id),
                         "visible": visible})
        return rows

    # ------------------------------------------------------------------
    # Applying a command -- always through the control the mouse would use
    # ------------------------------------------------------------------

    def _voiceApply(self, command):
        from SlicerAIAgentLib.voice import commands as _commands
        action = command.action
        _voice_debug("apply: %s value=%r", action, command.value)

        if action == _commands.ACTION_STOP_LISTENING:
            self._voiceSpeak("Microphone off.", interrupt=True)
            self._stopVoiceListening("stopped by voice")
            return
        if action == _commands.ACTION_REPEAT:
            # With nothing running there is no step to repeat, and the announcer
            # is deliberately silent there -- answer with where we actually are.
            if (getattr(self, "_currentWorkflowUiState", None) or {}).get("active"):
                self._voiceMaybeAnnounceStep(force=True)
            else:
                self._voiceSpeakStatus()
            return
        if action == _commands.ACTION_DETAILS:
            self._voiceMaybeAnnounceStep(force=True, detailed=True)
            return
        if action == _commands.ACTION_OPTIONS:
            self._voiceSpeakOptions()
            return
        if action == _commands.ACTION_STATUS:
            self._voiceSpeakStatus()
            return

        state = getattr(self, "_currentWorkflowUiState", None) or {}
        if action == _commands.ACTION_START_WORKFLOW:
            self._voiceStartRequest(command.value)
            return

        # While the user is scrubbing the replay timeline, every COMMIT routes
        # into _rerunFromCheckpoint, which deletes downstream nodes and can
        # raise a modal -- not something a spoken word should trigger by
        # accident. Navigation and Exit are the opposite: they are how the user
        # gets out of the preview, so blocking them would make a spoken "step
        # back" a one-way trip into a state voice cannot leave.
        _NAVIGATION = (_commands.ACTION_BACK, _commands.ACTION_FORWARD,
                       _commands.ACTION_EXIT)
        if state.get("replay_previewing") and action not in _NAVIGATION:
            self._voiceSpeak("You are reviewing an earlier step. "
                             "Use Run from here on the panel to resume.")
            return

        self._voiceSpeak(command.describe())

        if action == _commands.ACTION_PROCEED:
            self._onWorkflowDoneClicked()
        elif action == _commands.ACTION_SKIP:
            self._onWorkflowSkipClicked()
        elif action == _commands.ACTION_BACK:
            self._onReplayBack()
        elif action == _commands.ACTION_FORWARD:
            self._onReplayForward()
        elif action == _commands.ACTION_EXIT:
            # Always saving, and never closing the scene. Both halves follow the
            # same rule: what a spoken word may do is bounded by what is
            # recoverable if the word was misheard. Deleting the run folder and
            # discarding the scene are not, so they stay behind the button and
            # its dialog. Routing this through that dialog instead was
            # considered and rejected -- the push-to-talk key is SPACE, a modal
            # stands the key filter down, and Space activates a QMessageBox's
            # default button, so the very act of trying to say "no, cancel"
            # would confirm the exit.
            if self._resetGuidedSession(reason="user_exit", save=True,
                                        close_scene=False):
                self.appendToChat(
                    "System",
                    "Workflow exited and saved by voice. The scene is still "
                    "open — press Exit (or File > Close Scene) to clear it "
                    "before the next procedure.",
                )
        elif action == _commands.ACTION_CHOICE:
            self._onWorkflowChoiceClicked(state.get("current_step"), command.value)
        elif action == _commands.ACTION_NODE:
            self._voiceApplyNode(command)
        elif action == _commands.ACTION_SEGMENT_NAME:
            self._voiceApplySegmentName(command)
        elif action == _commands.ACTION_SEGMENT_VISIBILITY:
            self._voiceApplySegmentVisibility(command)
        elif action == _commands.ACTION_SCALAR:
            self._voiceApplyScalar(command)
        elif action == _commands.ACTION_RANGE:
            self._voiceApplyRange(command)
        elif action == _commands.ACTION_TEXT:
            self._voiceApplyText(command)
        elif action == _commands.ACTION_MULTI:
            self._voiceApplyMulti(command)

    def _voiceLooksLikeRequest(self, text):
        """Whether an idle-session utterance is addressed to the application.

        With no workflow running there is no closed vocabulary to match
        against, so the matcher hands everything through as a request. Sending
        it all to the router would mean an LLM call -- and, on a non-match under
        GUIDED_ONLY_MODE, a modal refusal -- for every sentence spoken in the
        room. Requiring a request opener is the cheapest filter that a person
        naturally satisfies ("plan the orbital fracture reconstruction") and
        overheard conversation usually does not.
        """
        from SlicerAIAgentLib.voice import commands as _commands
        normalized = _commands.normalize(text)
        if len(normalized.split()) < 3:
            return False
        for lead in VOICE_REQUEST_LEAD_INS:
            opener = _commands.normalize(lead)
            if opener and (normalized == opener or normalized.startswith(opener + " ")):
                return True
        return False

    def _voiceStartRequest(self, text):
        """Hand a spoken request to the same path the Send button uses.

        The router decides whether it names a procedure; under GUIDED_ONLY_MODE
        a non-match ends in a modal refusal, so this is fenced against issuing a
        second request while the first is still on screen -- with an always-on
        microphone the room would otherwise stack dialogs.
        """
        if not self._voiceLooksLikeRequest(text):
            _voice_debug("request ignored: no opener. Say \"plan …\" / \"start …\" "
                         "(>= 3 words)")
            self._setVoiceStatus(
                "Heard: %s — say \"plan …\" or \"start …\" to begin a procedure." % text)
            return
        if getattr(self, "_voiceRequestInFlight", False):
            _voice_debug("request ignored: one is already in flight")
            self._setVoiceStatus("Still working on the previous request.")
            return
        if getattr(self, "_routerBusy", False):
            # Routing is asynchronous now, so onSendButtonClicked returns long
            # before the answer. Without this a second spoken request would
            # start a second routing call while the first is still out.
            _voice_debug("request ignored: routing is already in flight")
            self._setVoiceStatus("Still choosing the procedure — one moment.")
            return
        if getattr(self, "_streaming", False):
            _voice_debug("request ignored: a turn is already streaming")
            self._setVoiceStatus("A request is already running.")
            return
        prompt = getattr(self, "promptInput", None)
        if prompt is None:
            return
        self._voiceRequestInFlight = True
        try:
            prompt.setPlainText(str(text or ""))
            _voice_debug("request -> onSendButtonClicked(%r)", text)
            self.onSendButtonClicked()
            # Routing is asynchronous, so this returns long before a workflow
            # exists. Reporting the panel state here would print "active=False"
            # on every successful request.
            if getattr(self, "_routerBusy", False):
                _voice_debug("request accepted: choosing the procedure "
                             "(the answer arrives on the queue)")
                self._setVoiceStatus("Choosing the procedure…")
            else:
                state = getattr(self, "_currentWorkflowUiState", None) or {}
                _voice_debug("request handled synchronously: workflow active=%s step=%s",
                             state.get("active"), state.get("current_step"))
        except Exception as error:
            _voice_debug("request FAILED: %s", error)
            logger.debug("Voice request dispatch failed", exc_info=True)
        finally:
            self._voiceRequestInFlight = False

    def _voiceApplyNode(self, command):
        """Drive the tree's highlight, then commit the node NAME.

        The name, not the ID: ``_onWorkflowNodeTreeSelected`` commits
        ``node.GetName()`` and the materialization code resolves by name.
        """
        tree = getattr(self, "_workflowNodeTree", None)
        node_id = (command.extra or {}).get("node_id")
        if tree is not None and node_id:
            try:
                node = slicer.mrmlScene.GetNodeByID(node_id)
                if node is not None:
                    tree.setCurrentNode(node)
            except Exception:
                logger.debug("Voice node highlight failed", exc_info=True)
        self._commitWorkflowChoice(command.value)

    def _voiceApplySegmentName(self, command):
        """Go through the combo so the extension's own control is driven too.

        ``_onWorkflowSegmentNamePreview`` mirrors the pick onto the extension's
        combobox so its handler fires and its 3D handles move. Committing the
        value directly would set the workflow answer and leave the extension
        showing the previous segment.
        """
        combo = getattr(self, "_workflowSegmentNameCombo", None)
        if combo is not None:
            for index in range(combo.count):
                if combo.itemText(index) == command.value:
                    combo.setCurrentIndex(index)
                    self._onWorkflowSegmentNameSelected()
                    return
        self._commitWorkflowChoice(command.value)

    def _voiceApplySegmentVisibility(self, command):
        """The eye column writes straight to the display node; so does this."""
        node = self._voiceSegmentationNode()
        if node is None:
            return
        try:
            display = node.GetDisplayNode()
            if display is None:
                return
            display.SetSegmentVisibility(command.value,
                                         bool((command.extra or {}).get("visible")))
        except Exception:
            logger.debug("Voice segment visibility failed", exc_info=True)

    def _voiceApplyScalar(self, command):
        widget = getattr(self, "_workflowScalarWidget", None)
        if widget is None:
            return
        widget.value = float(command.value)
        self._onWorkflowScalarSelected()

    def _voiceApplyRange(self, command):
        widget = getattr(self, "_workflowRangeWidget", None)
        if widget is None:
            return
        low, high = command.value
        widget.setMinimumValue(float(low))
        widget.setMaximumValue(float(high))
        self._onWorkflowRangeSelected()

    def _voiceApplyText(self, command):
        box = getattr(self, "_workflowChoiceInput", None)
        if box is not None:
            box.setText(str(command.value))
            self._onWorkflowChoiceInputSubmitted()
            return
        self._commitWorkflowChoice(command.value)

    def _voiceApplyMulti(self, command):
        """Fill the selectors that were named; confirm only when all are set.

        ``_onWorkflowMultiChoiceConfirmed`` refuses to commit while any combo is
        still on its placeholder, so a partial spoken answer leaves the form
        half-filled and waiting rather than failing.
        """
        combos = getattr(self, "_workflowMultiChoiceCombos", None) or {}
        for param, value in (command.value or {}).items():
            combo = combos.get(param)
            if combo is not None:
                combo.setCurrentText(str(value))
        labels = {}
        for _combo, _options, question in (
                getattr(self, "_workflowMultiChoiceOrdered", None) or []):
            for name, widget in combos.items():
                if widget is _combo:
                    labels[name] = str(question or name)
        remaining = []
        for param, combo in combos.items():
            try:
                # Index 0 is the inert "-- Select --" placeholder; the confirm
                # handler refuses to commit while any combo is still on it. A
                # selector whose options could NOT be resolved is built editable
                # with no items at all, so its index is permanently -1 -- for
                # those, typed text is what counts as answered.
                if combo.isEditable() and combo.count == 0:
                    if not str(combo.currentText or "").strip():
                        remaining.append(labels.get(param, param))
                elif combo.currentIndex <= 0:
                    remaining.append(labels.get(param, param))
            except Exception:
                logger.debug("Voice multi-choice state read failed", exc_info=True)
        if remaining:
            self._voiceSpeak("Still need %s." % ", ".join(remaining))
            return
        self._onWorkflowMultiChoiceConfirmed()

    # ------------------------------------------------------------------
    # Speaking
    # ------------------------------------------------------------------

    def _voiceSpeak(self, text, interrupt=False):
        """Queue ``text`` to be spoken, muting the microphone while it plays.

        Muting is not a nicety: with an always-on microphone the synthesized
        guidance goes out of the speakers and straight back into the input, and
        the words the app just spoke are exactly the words most likely to match
        the step's own option labels.

        Utterances are **queued and spoken in order**, not "latest wins". An
        acknowledgement and the next step's prompt are produced microseconds
        apart -- ``_voiceApply`` speaks "Selecting Red box." and the panel
        handler it then calls advances the step, which announces the new one --
        so a newest-wins policy silently drops the acknowledgement almost every
        time, which is exactly the safety property it exists to provide. Only an
        explicit ``interrupt`` (a repeat/explain request, or the session
        closing) discards what is pending.
        """
        text = str(text or "").strip()
        if not text or not self._voiceSetting("_voiceSpeakCheck", "check", True):
            return
        tts = self._voiceTts()
        if tts.unavailable_reason():
            return

        if getattr(self, "_voiceSpeechLock", None) is None:
            self._voiceSpeechLock = threading.Lock()
            self._voiceSpeechQueue = []
            self._voiceSpeechWorker = None

        player = self._voicePlayerInstance()
        start_worker = False
        with self._voiceSpeechLock:
            if interrupt:
                del self._voiceSpeechQueue[:]
                # Bumping the generation is what makes an already-synthesising
                # item drop itself instead of playing over the new one.
                self._voiceSpeechSeq = getattr(self, "_voiceSpeechSeq", 0) + 1
            self._voiceSpeechQueue.append((text, getattr(self, "_voiceSpeechSeq", 0)))
            # A backlog means the user is ahead of the speech; the OLDEST lines
            # are the stalest, and reading a queue of five is worse than silence.
            if len(self._voiceSpeechQueue) > 3:
                del self._voiceSpeechQueue[:len(self._voiceSpeechQueue) - 3]
            if self._voiceSpeechWorker is None:
                start_worker = True
                self._voiceSpeechWorker = threading.Thread(
                    target=self._voiceSpeechLoop, args=(player,), daemon=True)
                worker = self._voiceSpeechWorker

        # OUTSIDE the lock, deliberately. AudioPlayer.stop() joins the playback
        # thread, and on the blocking path that thread IS _voiceSpeechLoop --
        # which needs this lock to take its next item. Calling stop() while
        # holding it stalls the Qt main thread for the whole join timeout on
        # every barge-in.
        if interrupt:
            try:
                player.stop()
            except Exception:
                logger.debug("Voice playback interrupt failed", exc_info=True)

        # Mute BEFORE the worker can start playing, and from whichever thread
        # asked to speak -- mute/unmute are threading.Event flips.
        listener = getattr(self, "_voiceListener", None)
        if listener is not None:
            try:
                listener.mute()
            except Exception:
                logger.debug("Mic mute failed", exc_info=True)
        self._setVoiceButtonStyle(self._VOICE_SPEAKING_STYLE)
        if start_worker:
            worker.start()

    def _voiceSpeechLoop(self, player):
        """Drain the speech queue serially. Worker thread; touches no widget."""
        import time as _time
        tts = self._voiceTts()
        error = ""
        while True:
            with self._voiceSpeechLock:
                if not self._voiceSpeechQueue:
                    self._voiceSpeechWorker = None
                    break
                text, sequence = self._voiceSpeechQueue.pop(0)
            try:
                tts.setDebugOutputDir(getattr(self, "_voiceLogDir", None))
                _voice_debug("speak: %r", text[:120])
                result = tts.synthesize(text)
                if sequence != getattr(self, "_voiceSpeechSeq", 0):
                    _voice_debug("speak superseded (gen %s -> %s)", sequence,
                                 getattr(self, "_voiceSpeechSeq", 0))
                    continue  # superseded while it was being synthesised
                if not result:
                    error = "Speech synthesis returned no audio."
                    _voice_debug("speak FAILED: %s", error)
                elif not player.play(result.audio, result.audio_format, blocking=True):
                    error = player.last_error or "Playback failed."
                    _voice_debug("speak FAILED at playback: %s", error)
                else:
                    _voice_debug("speak played: %s, %d bytes, %.2fs",
                                 result.audio_format or "?", len(result.audio),
                                 result.seconds)
            except Exception as exc:
                error = str(exc)
                _voice_debug("speak FAILED: %s", error)

        # Unmute from THIS thread, not from the queue handler: Exit drains
        # _streamQueue wholesale, so a speech-done event in flight when the user
        # exits would never be delivered and the microphone would stay muted for
        # the rest of the session.
        try:
            _time.sleep(VOICE_UNMUTE_TAIL_MS / 1000.0)
        except Exception:
            logger.debug("Voice unmute tail failed", exc_info=True)
        with self._voiceSpeechLock:
            # A new speaker may have claimed the slot during the tail; it has
            # already muted, so this one must not undo that.
            idle = self._voiceSpeechWorker is None
        if idle:
            live = getattr(self, "_voiceListener", None)
            if live is not None:
                try:
                    live.unmute()
                except Exception:
                    logger.debug("Mic unmute failed", exc_info=True)
        try:
            self._streamQueue.put(("voice_speech_done",
                                   {"idle": idle, "error": error}))
        except Exception:
            logger.debug("Voice speech-done queue failed", exc_info=True)

    def _voiceSpeakOptions(self):
        from SlicerAIAgentLib.voice import grammar as _grammar
        step = self._voiceStepGrammar()
        options = step.option_labels()
        if options:
            self._voiceSpeak("You can say " + _grammar._spoken_option_list(options, 8) + ".")
        elif step.can_done:
            self._voiceSpeak('Say "done" when you have finished, or "explain".')
        else:
            self._voiceSpeak("This step has nothing to choose.")

    def _voiceSpeakStatus(self):
        step = self._voiceStepGrammar()
        if not step.workflow_active:
            self._voiceSpeak("No procedure is running.")
            return
        self._voiceSpeak("%s, step %s of %s. %s"
                         % (step.workflow_title or "The procedure",
                            step.step_index, step.total_steps, step.description))

    def _voiceAnnounceKey(self, step):
        """Identity of a step OCCURRENCE, so repaints do not re-announce.

        ``_updateWorkflowPanel`` runs several times per opening, and a repeat
        block re-visits the same step id, so the id alone is neither unique nor
        stable. The completed-instance count is what separates the two, and it
        is the same key the sole-node auto-select uses for the same reason.
        """
        session = None
        runtime = getattr(self, "_workflowRuntime", None)
        if runtime is not None:
            session = runtime.session
        instances = len(getattr(session, "completed_instances", ()) or ()) if session else 0
        workflow_id = getattr(session, "workflow_id", "") if session else ""
        return (workflow_id, step.step_id, instances, step.family, step.status)

    def _voiceMaybeAnnounceStep(self, force=False, detailed=False):
        """Read the step aloud, once per step, only where a person is needed.

        Automated steps are dispatched and gone before a sentence could finish,
        so speaking them would mean the guidance always lags the scene by one
        step. And a node-pick step that is about to auto-answer itself (single
        candidate, ~600 ms settle) is deliberately silent: the prompt would be
        answered by the runtime before the user finished hearing it.
        """
        if not getattr(self, "_voiceListening", False):
            return
        if not self._voiceSetting("_voiceSpeakCheck", "check", True):
            return
        step = self._voiceStepGrammar()
        if not step.workflow_active:
            # A run that FINISHED says so, once, on the transition (the panel
            # goes inactive on every idle repaint too, hence the key guard).
            #
            # An idle panel says NOTHING, and the ``force`` flag must not
            # override that. It briefly did, which produced the worst possible
            # first impression: pressing the microphone announced "The procedure
            # is complete." when no procedure had ever run -- and, because the
            # microphone is muted for the whole of any announcement, it was
            # deaf for the two seconds in which the user was saying their first
            # command. Silence on an idle start is not a missing feature; it is
            # what leaves the microphone listening when it is first spoken to.
            if step.workflow_done and getattr(self, "_voiceSpokenStepKey", None) != "__done__":
                self._voiceSpokenStepKey = "__done__"
                self._voiceSpeak("The procedure is complete.")
            return
        if not step.is_waiting_for_user():
            return
        if step.auto_select_pending and not force:
            return
        key = self._voiceAnnounceKey(step)
        if not force and key == getattr(self, "_voiceSpokenStepKey", None):
            return
        self._voiceSpokenStepKey = key
        from SlicerAIAgentLib.voice import grammar as _grammar
        # A "repeat"/"explain"/first-open announcement replaces whatever is
        # queued -- the user asked for it now. The ordinary per-step one is
        # appended, so the acknowledgement that preceded it is still spoken.
        self._voiceSpeak(_grammar.spoken_prompt(step, include_detail=detailed),
                         interrupt=bool(force))

    def _voiceOnWorkflowPanelUpdated(self):
        """Hook called at the end of every ``_updateWorkflowPanel``."""
        if not getattr(self, "_voiceListening", False):
            return
        try:
            self._voiceRefreshLogDir()
            self._voiceMaybeAnnounceStep()
        except Exception:
            logger.debug("Voice step announcement failed", exc_info=True)

    def _voiceRefreshLogDir(self):
        """Point both clients' artifacts at the step folder that is open now.

        Read on the main thread and cached, because the worker that transcribes
        must not go looking for the current step while the panel is changing.
        """
        try:
            self._voiceLogDir = (getattr(self, "_currentStepLogDir", "")
                                 or getattr(self, "_currentLogDir", None))
        except Exception:
            self._voiceLogDir = None

    # ------------------------------------------------------------------
    # Teardown
    # ------------------------------------------------------------------

    def _teardownVoice(self):
        """Stop capture and playback. Called from ``cleanup()``.

        A daemon capture thread left running survives a module reload and posts
        events into a widget that no longer exists.

        Deliberately NOT wired to ``onSceneEndClose``. Closing the scene ends a
        guided session, but it does not end the surgeon's use of the
        microphone: the next thing they do is load another case and say "plan
        the …", and switching the mic off under them would mean reaching for
        the mouse to switch it back on. The session-epoch fence already stops
        anything in flight from acting on the closed session.
        """
        try:
            self._stopVoiceListening("", announce=False, synchronous=True)
        except Exception:
            logger.debug("Voice teardown failed", exc_info=True)


def _fmt_debug(value):
    """Compact rendering for the trace: floats short, everything else as-is."""
    if isinstance(value, float):
        return "%.4f" % value
    return value


def _as_bool(value, default=False):
    """QSettings hands booleans back as 'true'/'false' strings on some platforms."""
    if isinstance(value, bool):
        return value
    if value is None:
        return bool(default)
    text = str(value).strip().lower()
    if text in ("true", "1", "yes", "on"):
        return True
    if text in ("false", "0", "no", "off", ""):
        return False
    return bool(default)
