from .common import *
from .logic import SlicerAIAgentLogic
from .widget_core import WidgetCoreMixin
from .widget_cli import WidgetCLIMixin
from .widget_workflow import WidgetWorkflowMixin
from .widget_replay import WidgetReplayMixin
from .widget_baseline import WidgetBaselineMixin
from .widget_streaming import WidgetStreamingMixin
from .widget_execution import WidgetExecutionMixin
from .widget_settings import WidgetSettingsMixin


class SlicerAIAgentWidget(
    WidgetCoreMixin,
    WidgetCLIMixin,
    WidgetWorkflowMixin,
    WidgetReplayMixin,
    WidgetBaselineMixin,
    WidgetStreamingMixin,
    WidgetExecutionMixin,
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
        self._currentStepLogDir = ""
        self._currentStepId = ""
        self._currentRunManifest = None
        self._currentCorrectionDir = ""
        self._stepTraceStart = 0
        self._baselineAttemptCounts = {}
        # The pipeline's run folder, parked while a baseline owns _currentLogDir
        # so the pipeline's next step does not log inside the baseline's folder.
        self._pipelineLogDir = None
        self._pipelineRunManifest = None
        self._pipelineStepLogDir = ""
        self._pipelineStepId = ""
        self._pipelineRoleTrace = []
        # Router instance kept when it DECLINED, so the full turn that runs
        # instead can still record the routing call it paid for.
        self._lastRouter = None
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
        # Last fast-router decision that DECLINED, so the full turn that follows
        # can account for its cost (see WidgetStreamingMixin's router path).
        self._lastRouterDecision = None
        self._lastInjectedPreludeKeys = []

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
