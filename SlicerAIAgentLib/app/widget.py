from .common import *
from .logic import SlicerAIAgentLogic
from .widget_core import WidgetCoreMixin
from .widget_cli import WidgetCLIMixin
from .widget_workflow import WidgetWorkflowMixin
from .widget_replay import WidgetReplayMixin
from .widget_streaming import WidgetStreamingMixin
from .widget_execution import WidgetExecutionMixin
from .widget_settings import WidgetSettingsMixin


class SlicerAIAgentWidget(
    WidgetCoreMixin,
    WidgetCLIMixin,
    WidgetWorkflowMixin,
    WidgetReplayMixin,
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
        self._currentLogDir = None
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
        self._currentWorkflowUiState = {"active": False}
        self._taskWorkflowPanelActive = False
        self._announcedWorkflowIds = set()
        self._currentWorkflowStepInfo = None
        # Replay stepper UI (Back / Forward / Run-from-here around the progress bar)
        self._replayControlsRow = None
        self._replayBackButton = None
        self._replayForwardButton = None
        self._replayActionButton = None
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
