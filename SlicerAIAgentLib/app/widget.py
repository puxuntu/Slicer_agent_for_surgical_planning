from .common import *
from .logic import SlicerAIAgentLogic
from .widget_core import WidgetCoreMixin
from .widget_cli import WidgetCLIMixin
from .widget_experiments import WidgetExperimentsMixin
from .widget_workflow import WidgetWorkflowMixin
from .widget_replay import WidgetReplayMixin
from .widget_baseline import WidgetBaselineMixin
from .widget_revise import WidgetReviseMixin
from .widget_streaming import WidgetStreamingMixin
from .widget_execution import WidgetExecutionMixin
from .widget_voice import WidgetVoiceMixin
from .widget_settings import WidgetSettingsMixin


class SlicerAIAgentWidget(
    WidgetCoreMixin,
    WidgetCLIMixin,
    WidgetExperimentsMixin,
    WidgetWorkflowMixin,
    WidgetReplayMixin,
    # Both of these take over promptInput + sendButton, so both must precede
    # WidgetSendMixin (reached through WidgetExecutionMixin) for their
    # onSendButtonClicked / onPromptTextChanged overrides to win. Baseline
    # first: its override runs, and super() carries an unengaged click through
    # revise and on to the default handler. They are mutually exclusive anyway
    # (engaging one disengages the other), so the order only fixes precedence.
    WidgetBaselineMixin,
    WidgetReviseMixin,
    WidgetStreamingMixin,
    WidgetExecutionMixin,
    # Before WidgetSettingsMixin, so its onSaveSettings/loadSettings overrides
    # can super() into the originals -- one Save button covers both sections.
    WidgetVoiceMixin,
    WidgetSettingsMixin,
    ScriptedLoadableModuleWidget,
    VTKObservationMixin,
):
    """Main UI widget for SlicerAIAgent."""

    def __init__(self, parent=None):
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False
        self._chatEntriesHtml = []
        # Debug-view isolation: the pipeline and each baseline keep their own
        # Conversation/Generated-Code content (see WidgetStreamingMixin).
        self._debugBuffers = {}
        self._debugContext = "pipeline"
        self._debugWriteContext = "pipeline"
        # Streaming state
        self._streamReasoning = ""
        self._streamContent = ""
        self._streaming = False
        # Thinking display state (shown during streaming, hidden after)
        self._thinkingDisplayText = ""
        self._thinkingDisplayed = False
        # Thread-safe queue for streaming events (filled by worker, drained on main thread)
        self._streamQueue = queue.Queue()
        self._streamPollTimer = None
        # Timing data for performance analysis
        self._timing = None
        self.currentAgentPlan = None
        self._pendingConfirmation = None
        self._roleTrace = []
        # Run-log state (see SlicerAIAgentLib/RunLog.py and _createRunLogDir):
        # _currentLogDir is the RUN folder; _currentStepLogDir is the per-step
        # subfolder every artifact goes into while a workflow step is running.
        self._currentLogDir = None
        # The run FOLDER, holding runtime/ (== _currentLogDir) and Statistic/.
        self._currentRunRoot = None
        self._currentStepLogDir = ""
        self._currentStepId = ""
        self._currentRunManifest = None
        # Every run folder this guided session opened (the pipeline's own plus
        # any baseline folders). "Exit without saving" deletes exactly these.
        self._sessionLogDirs = []
        self._currentCorrectionDir = ""
        self._stepTraceStart = 0
        self._baselineAttemptCounts = {}
        # The pipeline's run folder, parked while a baseline owns _currentLogDir
        # so the pipeline's next step does not log inside the baseline's folder.
        self._pipelineLogDir = None
        self._pipelineRunRoot = None
        self._pipelineRunManifest = None
        self._pipelineStepLogDir = ""
        self._pipelineStepId = ""
        self._pipelineRoleTrace = []
        # Router instance kept when it DECLINED, so the full turn that runs
        # instead can still record the routing call it paid for.
        self._lastRouter = None
        # A routing call is in flight on a worker thread. It used to run inline
        # on the Qt thread, which froze Slicer for as long as the network took
        # -- 174 s on a throttled link, with the window marked "not responding".
        # The flag stops a second Send (or a second spoken request) racing a
        # second answer into a second workflow.
        self._routerBusy = False
        # Set only while _finishRouterTurn re-enters Send to run the traditional
        # turn, so the router is not asked the same question twice.
        self._routerAlreadyDeclined = False
        self._currentAgentRole = "Idle"
        self._lastExecutionResult = None
        self._lastVerificationResult = None
        self._lastSceneAfter = None
        self._lastOutputHasErrors = False
        # Interactive workflow state
        self._workflowOrchestrator = None
        self._workflowRuntime = None
        self._activeWorkflowId = None
        self._waitingForUser = False
        self._workflowBannerLabel = None
        self._autoAdvanceWorkflowStep = None
        self._workflowInstructionsLabel = None
        self._workflowChoiceButtons = []
        self._workflowChoiceInput = None
        self._workflowChoiceSubmitButton = None
        self._workflowNodeTree = None
        self._workflowNodeCandidates = None
        self._workflowNodeTreeSelectButton = None
        self._workflowNodeTreeContainer = None
        self._workflowSegmentsTable = None
        self._workflowSegmentsCombo = None
        self._workflowSegmentsContainer = None
        self._workflowDetailToggle = None
        self._workflowDetailLabel = None
        self._workflowDetailText = ""
        # Experiments panel (per-extension analysis of a procedure's runs).
        # Content is built by a registered per-extension builder; empty until one
        # is registered. See app/widget_experiments.py.
        self._experimentsGroup = None
        self._experimentSelector = None
        self._experimentContent = None
        self._experimentContentLayout = None
        self._experimentDataMap = {}
        # Extension CLI generator: parallel generation state. `_cliBatch` maps
        # extension -> None while running, then {"ok": bool}; the batch is over
        # when no value is None. `_cliQueue` holds what has not started yet
        # (CLI_MAX_PARALLEL at a time) and `_cliProgressPanes` the per-extension
        # output tabs.
        self._cliBatch = {}
        self._cliQueue = []
        self._cliStarted = set()
        self._cliProgressTabs = None
        self._cliProgressPanes = {}
        # Per-step instruction editor (CLI generator panel)
        self._stepInstrStepCombo = None
        self._stepInstrTitle = None
        self._stepInstrSimple = None
        self._stepInstrDetailed = None
        # Per-step button-label editor (fixed-default buttons only)
        self._stepInstrButtonsContainer = None
        self._stepInstrButtonsForm = None
        self._stepInstrButtonFields = {}
        self._currentWorkflowUiState = {"active": False}
        self._taskWorkflowPanelActive = False
        self._announcedWorkflowIds = set()
        self._currentWorkflowStepInfo = None
        # Exit control: one button, bottom right of the workflow panel, that
        # closes and resets the guided session (it replaced the per-step Cancel).
        self._workflowExitButton = None
        self._workflowExitRow = None
        # Bumped by every guided-session reset. Deferred work started by the old
        # session (a QTimer auto-advance, a self-correction still in the API)
        # cannot be cancelled, so it captures this number and drops out when it
        # no longer matches -- otherwise code lands in a scene the user has
        # already exited from. See _resetGuidedSession.
        self._guidedSessionEpoch = 0
        # Replay stepper UI (Back / Forward / Run-from-here around the progress bar)
        self._replayControlsRow = None
        self._replayBackButton = None
        self._replayForwardButton = None
        self._replayActionButton = None
        # Baseline comparison (pure LLM / online only / Claude Code MCP). The
        # harness drives the EXISTING promptInput + sendButton; the only extra
        # widget is one selector row inserted above them.
        self._baselineToggleButton = None
        self._baselineRow = None
        self._baselineModeCombo = None
        self._baselineInfoLabel = None
        self._baselineActive = False
        self._baselineSendText = "Send"
        self._baselineSendStyle = ""
        self._baselineMcpServer = None
        # The skill's slicer-mcp-server.py is started automatically when the
        # Claude Code condition is selected; tried once per session on a passive
        # refresh, and again on every explicit arm.
        self._mcpAutoStartAttempted = False
        self._mcpAutoStartError = ""
        self._baselineActiveRun = None
        self._baselineRejection = ""
        # Runtime template revision (see app/widget_revise.py and
        # SlicerAIAgentLib/TemplateReviser.py). Same two-notion shape as the
        # baseline harness: `_reviseActive` is the ✎ toggle's intent, while
        # `_reviseActiveRun` being non-None is what "busy" means -- and busy is
        # always engaged, so the row cannot vanish under a running revision.
        self._reviseButton = None
        self._reviseRow = None
        self._reviseInfoLabel = None
        self._reviseActive = False
        self._reviseActiveRun = None
        self._reviseSendText = "Send"
        self._reviseSendStyle = ""
        # Per-step revision counter, so two revisions of the same step do not
        # write into one another's artifact folder.
        self._reviseAttemptCounts = {}
        # (cli_dir, step_id) -> (ok, reason). The eligibility answer reads two
        # JSON files and is consulted on every repaint while the mode is armed.
        self._reviseEligibilityMemo = {}
        # Last fast-router decision that DECLINED, so the turn that follows can
        # account for its cost (see WidgetStreamingMixin's router path).
        self._lastRouterDecision = None
        # Why the router declined, in a form the refusal dialog can explain --
        # "no API key" and "no procedure does this" need opposite remedies.
        self._lastRouterRejection = None
        self._lastInjectedPreludeKeys = []
        # Voice control (see app/widget_voice.py and SlicerAIAgentLib/voice/).
        # The microphone is ALWAYS ON while a session is live -- there is no
        # wake word -- so the mute flag around speech output and the epoch
        # carried by each utterance are what keep it safe, not an arming step.
        self._voiceButton = None
        self._voiceButtonColumn = None
        self._voiceGroup = None
        self._voiceStatusLabel = None
        self._voiceSaveButton = None
        # Red, selectable, first row of the Voice group: the "no audio backend"
        # remedy, which is a line the user has to copy into Slicer's console.
        self._voiceBackendBanner = None
        self._voiceListener = None
        self._voicePlayer = None
        self._voiceAsrClient = None
        self._voiceTtsClient = None
        self._voiceListening = False
        # Microphone SESSION token, distinct from _guidedSessionEpoch: it
        # retires events (and in-flight transcriptions) from a mic session the
        # user has closed, so the final "stopped" state of one session cannot
        # tear down the next one started milliseconds later.
        self._voiceSessionSeq = 0
        # Speech is QUEUED and spoken in order, not newest-wins: an
        # acknowledgement and the step announcement that follows it are produced
        # microseconds apart, and newest-wins drops the acknowledgement -- the
        # one thing that makes a mis-heard command audible. The generation
        # counter is bumped only by an explicit interrupt.
        self._voiceSpeechSeq = 0
        self._voiceSpeechLock = None
        self._voiceSpeechQueue = []
        self._voiceSpeechWorker = None
        # Identity of the step occurrence already read aloud. _updateWorkflowPanel
        # is a repaint event that runs several times per opening.
        self._voiceSpokenStepKey = None
        # Set when "confirm before acting" is on and a command is awaiting
        # "yes". The step it was resolved against is kept beside it: the
        # workflow can move on while the user is deciding, and a "yes" then
        # would commit a value the new step never offered.
        self._voicePendingCommand = None
        self._voicePendingStep = None
        self._voiceRequestInFlight = False
        self._voiceLogDir = None
        # _drainStreamQueue re-enters itself (applying a command pumps the Qt
        # event loop), so a second utterance must not be handled INSIDE the
        # first -- that dispatches a step twice. It is parked here and handled
        # at top level once the first finishes.
        self._voiceHandlingTranscript = False
        self._voiceDeferredTranscripts = []
        self._voiceDeferredCommands = []
        # Consecutive transcription failures. A wrong region or a bad key fails
        # every utterance identically, so a streak is the signal to stop and say
        # so rather than to keep looking alive.
        self._voiceAsrErrorStreak = 0
        # True between "captured" and whichever outcome the transcription has.
        # The capture thread returns to idle immediately after handing an
        # utterance over, so without this the panel says "nothing heard yet"
        # while the recogniser is still working on 2.4 s of audio.
        self._voiceTranscribing = False
        self._voiceUtteranceSeq = 0
        # Push-to-talk: the Space bar gates capture. _voiceKeyFilter is the
        # application-wide event filter when PythonQt can dispatch to it, and
        # _voicePttPoller is the key-state fallback when it cannot. Exactly one
        # is ever live, and both are torn down with the session -- a global key
        # hook left behind would keep stealing Space from the whole app.
        self._voicePttActive = False
        self._voiceKeyFilter = None
        self._voicePttPoller = None
        self._voicePttUser32 = None
        self._voicePttDown = False
        self._voicePttVirtualKey = 0x20

    def onReload(self):
        """Reload the module AND its ``SlicerAIAgentLib`` library.

        Slicer's default Reload only re-execs the thin ``SlicerAIAgent.py`` entry
        point, which re-imports the ALREADY-CACHED ``SlicerAIAgentLib`` submodules
        from ``sys.modules`` -- so edits to the library (widgets, runtime, loader,
        the CLI generation pipeline) do NOT take effect on Reload, only on a full
        Slicer restart. Purge the library from ``sys.modules`` first so the reload
        re-imports it fresh. Best-effort: if anything goes wrong, fall back to the
        default reload (a restart still applies the changes)."""
        try:
            import sys
            for _name in [
                _m for _m in list(sys.modules)
                if _m == "SlicerAIAgentLib" or _m.startswith("SlicerAIAgentLib.")
            ]:
                sys.modules.pop(_name, None)
        except Exception:
            logging.getLogger(__name__).debug("SlicerAIAgentLib purge failed", exc_info=True)
        ScriptedLoadableModuleWidget.onReload(self)
