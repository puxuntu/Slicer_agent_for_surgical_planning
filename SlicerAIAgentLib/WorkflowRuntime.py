"""Deterministic runtime for validated generated extension CLI workflows."""

from __future__ import annotations

import contextlib
import copy
import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def _silenced_vtk_output():
    """Suppress VTK C++ console output during an internal scene-view snapshot.

    Storing/restoring a ``vtkMRMLSceneViewNode`` makes MRML resolve every node
    reference by ID, which floods the console with ``ResolveUnresolvedItems:
    Unable to find data node with ID (nullptr)`` for any unresolved/null
    reference. This swaps the global ``vtkOutputWindow`` to a discard sink for the
    duration (same technique as SafeExecutor) -- generic: it silences ALL VTK
    chatter during our own bookkeeping, not a specific message string. Fail-soft:
    if VTK is unavailable the body still runs.
    """
    original = None
    try:
        import vtk
        original = vtk.vtkOutputWindow.GetInstance()
        sink = vtk.vtkFileOutputWindow()
        sink.SetFileName(os.devnull)
        try:
            sink.SetFlush(False)
        except Exception:
            pass
        vtk.vtkOutputWindow.SetInstance(sink)
    except Exception:
        original = None
    try:
        yield
    finally:
        if original is not None:
            try:
                import vtk
                vtk.vtkOutputWindow.SetInstance(original)
            except Exception:
                pass


# Benign, high-frequency VTK render-loop messages emitted by Slicer's markups /
# transform interaction-handle representations when a widget's handle index
# exceeds its current control-point count. They are harmless but flood the
# console while interaction handles are visible (e.g. during an interactive
# "adjust" step). Keyed on VTK-internal substrings, never on any extension name,
# so this stays general across every generated workflow.
_BENIGN_VTK_RENDER_SUBSTRINGS = (
    "GetInteractionHandlePositionWorld",
    "Invalid handle index",
)


def install_filtered_vtk_output(extra_substrings=()):
    """Route VTK console output through a filter that drops known benign,
    high-frequency render-loop warnings and forwards everything else to the
    previous output window unchanged.

    Returns a ``restore()`` callable that reinstalls the original window. The
    denylist keys on VTK-internal message substrings emitted for ANY extension
    that shows markups/transform interaction handles, so nothing
    extension-specific is hidden and real errors/warnings are still forwarded
    verbatim (self-correction and debugging keep seeing them). Fail-open: if VTK
    is unavailable or the build disallows subclassing ``vtkOutputWindow`` from
    Python, a no-op restore is returned and console output is left untouched.
    """
    try:
        import vtk
        original = vtk.vtkOutputWindow.GetInstance()
        denylist = tuple(_BENIGN_VTK_RENDER_SUBSTRINGS) + tuple(extra_substrings)

        class _FilteredOutputWindow(vtk.vtkOutputWindow):
            def DisplayText(self, text):
                if text and any(s in text for s in denylist):
                    return  # swallow benign render-loop noise
                if original is not None:
                    original.DisplayText(text)  # forward everything else verbatim

        vtk.vtkOutputWindow.SetInstance(_FilteredOutputWindow())
    except Exception:
        return lambda: None

    def _restore():
        try:
            import vtk
            vtk.vtkOutputWindow.SetInstance(original)
        except Exception:
            pass

    return _restore


from .ExtensionCLILoader import (
    clear_workflow_step_completions,
    dispatch_extension_cli_tool,
    find_next_workflow_step,
    get_validated_extensions,
    get_workflow_choices,
    get_workflow_graph,
    mark_workflow_step_completed,
    reset_workflow_session,
    set_all_workflow_repeat_states,
    set_workflow_choices,
    set_workflow_repeat_state,
    truncate_workflow_completions,
)


WAIT_TYPES = {"interactive", "user_interaction", "user_choice", "user_review"}
COMPLETE_TYPES = {
    "automated",
    "extension_op",
    "slicer_op",
    "interactive_done",
    "choice_made",
    "review_done",
    "skipped",
}


@dataclass
class WorkflowCheckpoint:
    """One rewindable point in a workflow run, recorded live as it executes.

    Back/Forward navigation shows/hides workflow nodes by step using
    ``before_node_ids`` / ``created_node_ids`` (never deletes, so display state
    is preserved). The commit (rewind_to_checkpoint) deletes the downstream
    ``created_node_ids``, truncates session/global state to the captured prefix,
    then re-dispatches ``step_id`` with ``action``/``args``. ``sceneview_node_id``
    is unused (kept only so older saved snapshots are cleaned up).
    """

    index: int
    step_id: str
    kind: str                       # automated | choice | interaction | loop_count | loop_decision
    action: str                     # replay user_action: start | proceed | choice_made | skip
    args: Dict[str, Any] = field(default_factory=dict)
    recorded_value: Any = None      # captured choice / placement summary (shown + editable)
    parameter_name: str = ""        # choice parameter name, "" when none
    editable: bool = False          # True for choice / loop_count / loop_decision
    choices: List[Dict[str, Any]] = field(default_factory=list)    # enumerated choices, [] = free-form
    guidance_description: str = ""  # the step's description shown in the panel (Back/Forward)
    guidance_instructions: str = "" # the step's instruction shown in the panel (Back/Forward)
    repeat: Dict[str, Any] = field(default_factory=dict)            # {"repeat_id", "iteration"} or {}
    repeat_states_snapshot: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    completed_prefix: List[str] = field(default_factory=list)       # completed_steps BEFORE this step
    completed_instances_len: int = 0                                # len(completed_instances) BEFORE this step
    choices_prefix: Dict[str, Any] = field(default_factory=dict)    # _workflow_choices[ext] BEFORE this step
    before_node_ids: List[str] = field(default_factory=list)        # scene node IDs BEFORE this step (clean-slate target)
    created_node_ids: List[str] = field(default_factory=list)       # scene nodes this step produced
    layout_before: int = -1                                         # layoutManager.layout BEFORE this step (-1 = unknown)
    sceneview_node_id: Optional[str] = None                         # vtkMRMLSceneViewNode (scene before step)
    summary: str = ""
    timestamp: float = 0.0


@dataclass
class WorkflowSession:
    """State for one generated CLI workflow run."""

    extension_name: str
    tool_name: str
    workflow_id: str
    current_step: Optional[str] = None
    status: str = "running"
    completed_steps: List[str] = field(default_factory=list)
    queued_prompts: List[str] = field(default_factory=list)
    repeat_states: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    completed_instances: List[Dict[str, Any]] = field(default_factory=list)
    last_result: Optional[Dict[str, Any]] = None
    started_at: float = field(default_factory=time.time)
    checkpoints: List[WorkflowCheckpoint] = field(default_factory=list)
    active_checkpoint_index: Optional[int] = None
    baseline_node_ids: List[str] = field(default_factory=list)   # scene nodes before step 1 (loaded inputs)
    preview_index: Optional[int] = None          # None = live; i = previewing step i
    live_layout: int = -1                        # layoutManager.layout at the live state (captured on first Back)
    live_sceneview_id: Optional[str] = None      # full snapshot of the live scene (captured on first Back)

    @property
    def active(self) -> bool:
        return self.status in {"running", "waiting_for_user", "waiting_for_choice"}


# ---------------------------------------------------------------------------
# Last-resort language classifier for a node-selection ``user_choice`` whose
# node class was NOT captured structurally (no ``value_kind == 'node'``, no
# recorded node-combo ``widget_class`` + ``node_class``, no ``choice_input``
# node role). This happens for extensions that build their node selector in
# PYTHON (e.g. ``self.tree = qMRMLSubjectHierarchyTreeView(); tree.nodeTypes =
# [...]``) with no ``.ui`` file, so the CLI pipeline records no widget class and
# the LLM decomposition leaves ``node_class`` empty and non-deterministic across
# regens. Without this the panel falls back to a free-text box.
#
# These sets are DUPLICATED (not imported) in
# ``extension_cli_loader/choice_helpers._node_class_from_choice_language`` so the
# render path and the materialization/drive path classify identically; keep them
# in sync (same convention as the mirrored ``_is_segment_name_selection`` /
# ``_is_range_selection`` helpers). Importing the loader/analyzer here would drag
# the generation pipeline onto the render hot-path (heavy + circular).
_CHOICE_SELECT_VERBS = frozenset({
    "choose", "select", "pick", "identify", "specify",
})
# Whole-word tokens that mark a VALUE/enum/boolean/count choice (never a node).
# Bias: over-inclusion here costs only a free-text fallback (safe); a missing
# token risks a wrong node tree — but the mandatory verb + family gates below are
# the primary guard, so this stays a curated value-noun list (no common English
# words like "on"/"set"/"use" that would over-exclude legitimate node phrasing).
_CHOICE_VALUE_STOPWORDS = frozenset({
    "number", "count", "many", "amount", "radius", "threshold", "thickness",
    "diameter", "distance", "length", "width", "height", "angle", "degree",
    "degrees", "unit", "units", "mm", "cm", "percent", "percentage", "opacity",
    "enable", "enabled", "disable", "disabled", "visible", "visibility",
    "checkbox", "toggle", "minimum", "maximum", "factor", "ratio", "smoothing",
    "iteration", "iterations", "spacing", "tolerance", "intensity",
    "brightness", "contrast", "true", "false", "yes", "no",
})
# Ordered (first match wins) map of a stable, unambiguous node-family noun -> the
# concrete MRML class. Class strings mirror the existing analyzer heuristics
# (cookbook_mapping._guess_node_class_for_role / workflow_templates.
# _node_class_for_reference_role). Deliberately small: this is a last resort, so
# it must map only nouns that unambiguously name one node family, never default
# to a base ``vtkMRMLNode``.
_CHOICE_NODE_FAMILY = (
    ("segmentation", "vtkMRMLSegmentationNode"),
    ("segments", "vtkMRMLSegmentationNode"),
    ("segment", "vtkMRMLSegmentationNode"),
    ("mask", "vtkMRMLSegmentationNode"),
    ("labelmap", "vtkMRMLLabelMapVolumeNode"),
    ("volume", "vtkMRMLScalarVolumeNode"),
    ("image", "vtkMRMLScalarVolumeNode"),
    ("scalar", "vtkMRMLScalarVolumeNode"),
    ("model", "vtkMRMLModelNode"),
    ("surface", "vtkMRMLModelNode"),
    ("mesh", "vtkMRMLModelNode"),
    ("curve", "vtkMRMLMarkupsCurveNode"),
    ("plane", "vtkMRMLMarkupsPlaneNode"),
    ("line", "vtkMRMLMarkupsLineNode"),
    ("fiducial", "vtkMRMLMarkupsFiducialNode"),
    ("landmark", "vtkMRMLMarkupsFiducialNode"),
    # "Point List" is Slicer's display name for a markups fiducial node; a param
    # like "entryPoints" / "pointList" names one. Plural/compound only, so a bare
    # singular "point" (often a coordinate/location, not a node) is not matched.
    ("points", "vtkMRMLMarkupsFiducialNode"),
    ("pointlist", "vtkMRMLMarkupsFiducialNode"),
    ("transform", "vtkMRMLTransformNode"),
    ("roi", "vtkMRMLMarkupsROINode"),
)

# Non-specific BASE MRML classes: a node_role / sub_op tagged with one of these
# says nothing about WHICH node to pick (every node IsA vtkMRMLNode), so a picker
# filtered to it lists unrelated nodes (e.g. a volume step showing the fiducial
# list too). The pipeline sometimes emits ``vtkMRMLNode`` as a placeholder
# choice_input node_class; such a value must NOT win over the language classifier
# that infers the concrete node family from the step text.
_NONSPECIFIC_NODE_CLASSES = frozenset({
    "vtkMRMLNode", "vtkMRMLStorableNode", "vtkMRMLDisplayableNode",
    "vtkMRMLTransformableNode", "vtkMRMLDisplayableHierarchyNode",
})


def _tokenize_choice_text(text: str) -> set:
    """Lowercased word-token set of ``text`` with camelCase split and every
    non-alphanumeric run (spaces, ``_``, punctuation) treated as a separator, so
    ``skull_segment_id`` -> ``{skull, segment, id}`` and ``thresholdRange`` ->
    ``{threshold, range}``. Token membership (not substring) so ``used`` never
    matches the verb ``use`` and ``outline`` never matches the family ``line``."""
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", str(text or ""))
    return {t for t in re.split(r"[^A-Za-z0-9]+", spaced.lower()) if t}


def _classify_node_choice_language(family_text: str, broad_text: str, priority_text: str = "") -> str:
    """Concrete MRML class for a node-selection choice inferred purely from its
    natural-language labels, or "" when it is not confidently a node pick.

    Gate (ALL must hold): an explicit select verb somewhere in ``broad_text``; NO
    value/enum/boolean/count stopword anywhere in ``broad_text``; and a recognized
    node-family noun in ``family_text`` (the narrow "what is being selected"
    fields only — object/choice/input labels, question, parameter name — never the
    noisy free-form description). Returns "" otherwise.

    ``priority_text`` (the parameter name — the most authoritative "what is being
    selected") is scanned for a family noun BEFORE ``family_text``, so a step whose
    question names a PURPOSE as well as the selected object reads as the selected
    object: "select the source VOLUME for segmentation" (param ``sourceVolume``)
    is a volume, not a segmentation. Without this, the global family order
    (segmentation before volume) would pick the purpose noun -> a node tree that
    finds nothing at that step -> a free-text fallback."""
    broad = _tokenize_choice_text(broad_text)
    if not (broad & _CHOICE_SELECT_VERBS):
        return ""
    if broad & _CHOICE_VALUE_STOPWORDS:
        return ""
    for source in (priority_text, family_text):
        tokens = _tokenize_choice_text(source)
        for token, node_class in _CHOICE_NODE_FAMILY:
            if token in tokens:
                return node_class
    return ""


class WorkflowRuntime:
    """Run generated CLI workflow steps without re-entering the LLM loop."""

    # Subject-hierarchy ITEM attribute set (during replay) on nodes created AFTER
    # the step being reviewed, so the node picker's tree excludes them (and their
    # now-empty output folder) -- making replay match the forward view. Item
    # metadata only: it does not touch the node or the hierarchy structure, and is
    # cleared on return to live.
    REPLAY_HIDDEN_SH_ATTR = "SlicerAIAgent.ReplayHiddenInPicker"

    def __init__(self, log_dir: Optional[str] = None):
        self.session: Optional[WorkflowSession] = None
        self.log_dir = log_dir
        # Snapshot captured at run_step (before dispatch), finalized into a
        # WorkflowCheckpoint when the step completes. One step is in flight at
        # a time, so a single pending slot is sufficient.
        self._pending_checkpoint: Optional[Dict[str, Any]] = None

    def has_active_workflow(self) -> bool:
        return bool(self.session and self.session.active)

    def state_for_router(self) -> Dict[str, Any]:
        if not self.session:
            return {"active": False}
        return {
            "active": self.session.active,
            "extension_name": self.session.extension_name,
            "tool_name": self.session.tool_name,
            "workflow_id": self.session.workflow_id,
            "current_step": self.session.current_step,
            "status": self.session.status,
            "completed_steps": list(self.session.completed_steps),
            "repeat_states": copy.deepcopy(self.session.repeat_states),
        }

    def state_for_ui(self, result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Return a compact, user-facing state for workflow progress UI."""
        if not self.session:
            return {"active": False}

        graph = get_workflow_graph(self.session.extension_name) or {}
        steps = graph.get("steps", []) if isinstance(graph, dict) else []
        step_ids = [step.get("step_id") for step in steps if step.get("step_id")]
        step_map = {step.get("step_id"): step for step in steps if step.get("step_id")}
        total_steps = graph.get("step_count") or len(steps)

        source = result if isinstance(result, dict) else self.session.last_result or {}
        next_step = source.get("next_step") or {}
        workflow_done = (
            self.session.status in ("completed", "cancelled")
            or bool(source.get("workflow_completed"))
        )
        if workflow_done:
            # The workflow finished (e.g. a branch_op "stop here" decline completed
            # it). The result still carries step_id=<the decided step> + its
            # choice_info; do NOT resurface them, or the panel shows "Step 12 of 15"
            # + Yes/No while the bar is at 15/15. Clear the current step so the panel
            # falls to the terminal state (current_index -> total, no options).
            current_step = None
        else:
            current_step = (
                source.get("step_id")
                or self.session.current_step
                or next_step.get("step_id")
            )
        current_meta = step_map.get(current_step, {})
        current_index = 0
        if current_step in step_ids:
            current_index = step_ids.index(current_step) + 1
        elif self.session.status == "completed" and total_steps:
            current_index = int(total_steps)

        completed_count = len(set(self.session.completed_steps))
        if self.session.status == "completed" and total_steps:
            completed_count = int(total_steps)

        result_type = source.get("type", "")
        status = self._ui_status_label(self.session.status, result_type)
        ui_guidance = self._ui_guidance_from_result(source, current_meta)
        guidance_title = str(ui_guidance.get("title", "") or "").strip()
        guidance_instruction = str(ui_guidance.get("instruction", "") or "").strip()
        is_repeat_decision = result_type == "user_choice" and bool(source.get("repeat_decision"))
        if is_repeat_decision:
            # A loop continue/exit decision: surface the decision's own question
            # and instruction, NOT the underlying step's guidance. Otherwise the
            # panel shows e.g. "Regenerate reconstruction / Repeat steps 27-30 if
            # needed" — making the Yes/No buttons read as "Yes = repeat" when Yes
            # actually accepts and exits the loop.
            description = (
                source.get("question")
                or guidance_title
                or current_meta.get("description")
                or ""
            )
            instructions = source.get("instruction") or guidance_instruction
        elif result_type == "user_choice":
            description = (
                guidance_title
                or source.get("question")
                or source.get("explanation")
                or current_meta.get("description")
                or ""
            )
            instructions = guidance_instruction or self._instructions_from_result(source)
        else:
            description = (
                guidance_title
                or source.get("explanation")
                or source.get("instruction")
                or current_meta.get("description")
                or ""
            )
            instructions = guidance_instruction or self._instructions_from_result(source)
        choices = self._choices_from_result(source, current_meta)
        if workflow_done:
            # A completed workflow has no pending choice -- drop any choices the
            # just-decided step's choice_info would otherwise resurface.
            choices = []
        # A node-pick user_choice must drive the scene node tree, not literal
        # cookbook-label buttons. Dropping stray literal choices flips
        # needs_choice_input True (below) so the panel reaches
        # _renderWorkflowNodeTree. Loop (repeat) decisions keep their synthetic
        # Yes/No buttons; segment-visibility steps are excluded by the helper.
        if (result_type == "user_choice"
                and not is_repeat_decision
                and self._is_node_selection_step(current_meta)):
            choices = []
        is_optional = bool(source.get("is_optional") or current_meta.get("is_optional"))
        choice_info = current_meta.get("choice_info", {}) if isinstance(current_meta, dict) else {}
        default_value = source.get("default_value")
        if default_value is None:
            default_value = choice_info.get("default_value")
        parameter_name = source.get("parameter_name") or choice_info.get("parameter_name") or ""
        repeat_progress = source.get("repeat_progress") or {}
        # Node-selection steps bind a parameter to a node class; surface it (and
        # its keywords) so the panel can offer a dropdown of matching scene
        # nodes instead of a free-text box.
        binding = source.get("binding") or self._node_binding_for_param(parameter_name)
        node_class = source.get("node_class") or binding.get("node_class", "")
        if not node_class and result_type == "user_choice":
            # No binding was inferred (e.g. a subject-hierarchy selector or a
            # parameterNodeWrapper-bound field): fall back to the node class the
            # step graph records so the panel still offers a node dropdown.
            node_class = self._node_class_from_step_meta(current_meta)
        node_keywords = binding.get("keywords", []) or []
        # Original selection widget recorded by the pipeline from the extension's
        # .ui. Authoritative for which render family the panel builds, so the
        # reproduced UI matches the source extension (e.g. a segments table stays a
        # segments table) rather than being inferred from node_class heuristics.
        source_widget_class = self._source_widget_class(current_meta) if result_type == "user_choice" else ""
        # Segment-selection step (qMRMLSegmentsTableView): the user unticks
        # individual segments on a segmentation node. Surface a flag + the
        # segmentation node class so the panel renders the segments table instead
        # of a node dropdown / free-text box. Trust the recorded widget class even
        # if value_kind ever drifts.
        segment_meta = self._segment_selection_meta(current_meta) if result_type == "user_choice" else {}
        if not segment_meta and source_widget_class == "qMRMLSegmentsTableView":
            segment_meta = {"segmentation_node_class": "vtkMRMLSegmentationNode"}
        if segment_meta:
            # A segments-table step is an interactive per-segment visibility toggle,
            # not an enumerated choice. The LLM sometimes co-emits a stray choice
            # (e.g. "Untick to exclude"); drop it so the step routes to the
            # segments-table renderer instead of a choice button.
            choices = []
        # Segment-NAME selection step (a content combobox like the extension's
        # "Fragment" box): the user picks ONE segment name from a segmentation.
        # Surface a flag so the panel renders a name dropdown sourced from the
        # resolved segmentation, not a scene-node tree.
        segment_name_meta = self._segment_name_selection_meta(current_meta) if result_type == "user_choice" else {}
        if segment_name_meta:
            choices = []
        # Segment-REF step: the source selector picks a SEGMENT inside a segmentation
        # (tree row), so the panel keeps the node tree but accepts a segment row and
        # commits the (node, segment id) pair the source's handler expects.
        segment_ref_meta = self._segment_ref_meta(current_meta) if result_type == "user_choice" else {}
        if segment_ref_meta:
            choices = []
        # native_widget: the panel reproduces the extension's OWN selection widget
        # (e.g. a per-row-combo table) from its live state -- distinct from a
        # read-only review snapshot, which item-based reads cannot capture for
        # cell-widget combos.
        native_widget = bool(source.get("native_widget"))
        # Review checkpoint: show the generated results (a table snapshot the loader
        # read from the extension's own UI) + a Confirm that advances. No choice.
        review_selection = (result_type == "user_review" or (
            str(current_meta.get("operation_type") or "") == "review_op"
            and self.session.status == "waiting_for_user"
        )) and not native_widget
        review_table = source.get("review_table") or {}
        if review_selection and not review_table:
            review_table = self._live_review_table()
        # Multi-selection step: several selectors answered together on one form
        # (one commit = a {param: value} dict). Literal choices are dropped so the
        # panel routes to the form renderer instead of per-choice buttons. NOT gated
        # on result_type == "user_choice": on the transient "choice_made" render at
        # commit time, the step's own choice_info.choices (e.g. 25 vertebral levels)
        # would otherwise surface as a flashing button row that expands the panel.
        multi_choice_items = (
            self._multi_choice_items(current_meta) if not is_repeat_decision else []
        )
        if multi_choice_items:
            choices = []
        # Numeric RANGE adjustment step (a double-handled min/max slider like the
        # Segment Editor Threshold range): surface a flag so the panel renders a
        # range bar. Drop the placeholder choice the LLM co-emits ("range") so
        # needs_choice_input becomes True and the step routes to the range renderer.
        range_meta = self._range_selection_meta(current_meta) if result_type == "user_choice" else {}
        if range_meta:
            choices = []
        # Single-value slider step (a single-handle numeric control like an
        # extension's "Crop radius (mm)" ctkSliderWidget): surface a flag so the
        # panel renders one draggable slider, not a min/max range bar. Drop the
        # placeholder choice the LLM co-emits so needs_choice_input becomes True.
        scalar_meta = self._scalar_slider_meta(current_meta) if result_type == "user_choice" else {}
        if scalar_meta:
            choices = []
        # Clinically-informed instructions override the terse ui_guidance when
        # present: title -> description, detailed -> the primary instruction text
        # (shown by default), simple -> the terse "Show brief" body. The widget
        # picks which to show. Re-looked up live so manual edits show at once.
        instr = self._step_instructions_for(current_step)
        # Per-step button-label overrides (edited in the "Step instructions"
        # panel, stored in step_instructions.json under "buttons"). Purely
        # user-authored presentational text; the generation pipeline neither
        # writes nor reads them, so they survive regeneration untouched.
        button_overrides = instr.get("buttons") if isinstance(instr.get("buttons"), dict) else {}
        if instr.get("title"):
            description = instr["title"]
        if instr.get("simple"):
            instructions = instr["simple"]
        instructions_detailed = instr.get("detailed", "")
        if workflow_done:
            # Terminal state: replace any leftover "Proceed by calling ..." text
            # with a clear completion banner so the panel reads as finished.
            description = (
                f"Workflow complete — the "
                f"{self._display_name(self.session.extension_name)} pipeline is finished."
            )
            instructions = ""
            instructions_detailed = ""
        active = self.session.active or self.session.status in {"completed", "cancelled"}

        return {
            "workflow_done": workflow_done,
            "active": active,
            "extension_name": self.session.extension_name,
            "workflow_title": self._display_name(self.session.extension_name),
            "tool_name": self.session.tool_name,
            "workflow_id": self.session.workflow_id,
            "current_step": current_step,
            "current_index": current_index,
            "completed_steps": completed_count,
            "total_steps": int(total_steps or 0),
            "status": status,
            "raw_status": self.session.status,
            "result_type": result_type,
            "description": description,
            "instructions": instructions,
            "instructions_detailed": instructions_detailed,
            "choices": choices,
            "default_value": default_value,
            "parameter_name": parameter_name,
            "node_class": node_class,
            "node_keywords": node_keywords,
            "source_widget_class": source_widget_class,
            "segment_selection": bool(segment_meta),
            "segment_name_selection": bool(segment_name_meta),
            # A segment-REF pick reuses the node tree (filtered to segmentations); this
            # tells the panel to accept a SEGMENT row and commit the (node, segment id)
            # pair the source's handler expects, instead of a node name.
            "segment_ref_selection": bool(segment_ref_meta),
            # Review checkpoint: the panel renders the results table read-only and
            # relabels Done as Confirm; confirming advances the workflow.
            "review_selection": bool(review_selection),
            "review_table": review_table if review_selection else {},
            # native_widget: reproduce the extension's own selection widget live.
            "native_widget": native_widget,
            # Multi-selection form: one combo/input per item, one Confirm, commit =
            # {parameter_name: value} dict.
            "multi_choice": bool(multi_choice_items),
            "choice_items": multi_choice_items,
            # Interaction count gate: >0 when the step's cookbook text states how
            # many points to place (literal or multiplier x an earlier choice); the
            # panel shows placed-vs-expected and gates Done until reached.
            "expected_count": (
                self._expected_interaction_count(current_meta)
                if result_type in ("interactive", "user_interaction", "mixed") else 0
            ),
            # The extension's own source combobox name (e.g. "fragmentSelector"),
            # so the picker can drive it live for immediate handle feedback.
            "segment_name_source_widget": segment_name_meta.get("source_widget", ""),
            # Segmentation-resolution keys serve EITHER the segments-table or the
            # segment-name picker (a step is only ever one of them).
            "segmentation_node_class": segment_meta.get("segmentation_node_class", "")
            or segment_name_meta.get("segmentation_node_class", ""),
            # Binding keywords win when present (classic extensions); else fall back
            # to widget-name-derived keywords so the table/picker defaults to the
            # right segmentation. target_param (Layer 2) enables exact resolution.
            "segmentation_keywords": node_keywords
            or segment_meta.get("keywords", [])
            or segment_name_meta.get("keywords", []),
            "segmentation_target_param": segment_meta.get("target_param", "")
            or segment_name_meta.get("target_param", ""),
            # Numeric range slider: flag + resolution metadata. min/max/default may
            # be None (derived at render time from the live target / source volume).
            "range_selection": bool(range_meta),
            "range_param": range_meta.get("param", ""),
            "range_min": range_meta.get("min"),
            "range_max": range_meta.get("max"),
            "range_step": range_meta.get("step"),
            "range_default": range_meta.get("default"),
            # Single-value slider: flag + resolution metadata. min/max/step/default
            # may be None (seeded at render time from the extension's live slider).
            "scalar_selection": bool(scalar_meta),
            "scalar_param": scalar_meta.get("param", ""),
            "scalar_min": scalar_meta.get("min"),
            "scalar_max": scalar_meta.get("max"),
            "scalar_step": scalar_meta.get("step"),
            "scalar_default": scalar_meta.get("default"),
            "scalar_source_widget": scalar_meta.get("source_widget", ""),
            "choice_label": ui_guidance.get("choice_label", ""),
            "input_label": ui_guidance.get("input_label", ""),
            "done_label": button_overrides.get("primary") or ui_guidance.get("done_label", "Done") or "Done",
            "object_label": ui_guidance.get("object_label", ""),
            # Per-step button-label overrides: the single "primary" advance button
            # (Done / Confirm / Set) and per-choice labels keyed by choice value.
            "primary_label": str(button_overrides.get("primary") or ""),
            "choice_label_overrides": button_overrides.get("choices") if isinstance(button_overrides.get("choices"), dict) else {},
            "repeat_progress": repeat_progress,
            "needs_choice_input": result_type == "user_choice" and not choices,
            # native_widget renders its OWN Confirm button (write-back + advance), so
            # the generic Done is suppressed to avoid a second, no-write-back path.
            "can_done": self.session.status == "waiting_for_user" and not native_widget,
            "can_skip": self.session.active and is_optional,
            "can_cancel": self.session.active,
            "timeline": self._timeline_for_ui(),
            "active_checkpoint_index": self.session.active_checkpoint_index,
            "can_replay": bool(self.session.checkpoints),
            "replay_can_back": bool(self.session.checkpoints),
            "replay_can_forward": self.session.preview_index is not None,
            "replay_can_action": self.session.preview_index is not None,
            "replay_previewing": self.session.preview_index is not None,
        }

    def start_from_result(self, result: Dict[str, Any]) -> Optional[WorkflowSession]:
        """Create a session from a generated CLI tool result if needed."""
        if not isinstance(result, dict) or not result.get("tool"):
            return self.session
        tool_name = result.get("tool")
        ext_name = self._extension_name_for_tool(tool_name) or tool_name
        if not ext_name:
            return self.session
        if self.session and self.session.extension_name == ext_name and self.session.active:
            if result.get("step_id"):
                self.session.current_step = result.get("step_id")
            self._apply_pre_execution_state(result)
            return self.session
        workflow_id = f"{ext_name}_{int(time.time() * 1000)}"
        reset_workflow_session(ext_name)
        # Drop any prior session's replay snapshots before starting fresh.
        self._delete_all_replay_sceneviews()
        self._pending_checkpoint = None
        self.session = WorkflowSession(
            extension_name=ext_name,
            tool_name=tool_name,
            workflow_id=workflow_id,
            current_step=result.get("step_id"),
        )
        self._apply_pre_execution_state(result)
        # The first step is dispatched via the LLM tool path (not run_step), so
        # capture its before-scene snapshot here so it is rewindable too. A
        # later run_step for the same step (a user_choice answer / interactive
        # Done) refreshes the args while keeping this before-scene.
        if result.get("step_id"):
            self._begin_pending_checkpoint(
                result.get("step_id"), {"user_action": "start"}
            )
        self._write_event("workflow_started", {"initial_result": self._compact_result(result)})
        return self.session

    def start_for_extension(self, extension_name: str, tool_name: Optional[str] = None) -> WorkflowSession:
        """Start a session explicitly for a validated generated extension."""
        ext_data = get_validated_extensions().get(extension_name)
        if not ext_data:
            raise ValueError(f"Validated extension CLI not found: {extension_name}")
        resolved_tool = tool_name or self._tool_name_for_extension(ext_data) or extension_name
        workflow_id = f"{extension_name}_{int(time.time() * 1000)}"
        reset_workflow_session(extension_name)
        self._delete_all_replay_sceneviews()
        self._pending_checkpoint = None
        graph = get_workflow_graph(extension_name)
        first_step = find_next_workflow_step(extension_name, set())
        self.session = WorkflowSession(
            extension_name=extension_name,
            tool_name=resolved_tool,
            workflow_id=workflow_id,
            current_step=(first_step or {}).get("step_id"),
        )
        self._write_event("workflow_started", {"workflow": graph.get("name", extension_name)})
        return self.session

    def run_step(
        self,
        step_id: Optional[str] = None,
        action: str = "start",
        args: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Dispatch one generated CLI step and return the generated result."""
        if not self.session:
            return {"type": "error", "error": "No active generated CLI workflow"}

        target_step = step_id or self.session.current_step
        if not target_step and action != "cancel":
            return {"type": "error", "error": "No current workflow step"}

        call_args = dict(args or {})
        call_args.setdefault("workflow_step", target_step)
        call_args.setdefault("user_action", action)
        call_args.setdefault("_workflow_id", self.session.workflow_id)

        self.session.current_step = target_step
        self.session.status = "running"
        # Record a replay checkpoint snapshot of the scene/state BEFORE this
        # step runs. Idempotent across an interactive step's start->proceed
        # pair (keeps the before-placement scene). Finalized in _mark_completed
        # (or for a loop decision, just below).
        self._begin_pending_checkpoint(target_step, call_args)
        repeat_decision = self._handle_pending_repeat_decision(
            target_step, action, call_args
        )
        if repeat_decision is not None:
            self._finalize_loop_decision_checkpoint(target_step, call_args, repeat_decision)
            self.session.last_result = repeat_decision
            self._apply_pre_execution_state(repeat_decision)
            next_step = repeat_decision.get("next_step")
            if next_step:
                self.session.current_step = next_step.get("step_id")
                self.session.status = "running"
            else:
                self.session.current_step = None
                self.session.status = "completed"
                repeat_decision["workflow_completed"] = True
            self._write_event(
                "repeat_decision",
                {"args": call_args, "result": self._compact_result(repeat_decision)},
            )
            return repeat_decision

        result = dispatch_extension_cli_tool(self.session.tool_name, call_args)
        if result is None:
            result = {"type": "error", "error": f"Unknown workflow tool: {self.session.tool_name}"}
        elif isinstance(result, dict):
            result = copy.deepcopy(result)
            result.setdefault("tool", self.session.extension_name)
            result.setdefault("step_id", target_step)

        self.session.last_result = result
        self._apply_pre_execution_state(result)
        self._write_event("step_dispatched", {"args": call_args, "result": self._compact_result(result)})
        return result

    def handle_execution_result(
        self,
        step_result: Dict[str, Any],
        execution_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update workflow state after generated code execution completes."""
        if not self.session:
            return step_result
        result = dict(step_result or {})
        result_type = result.get("type")
        step_id = result.get("step_id") or self.session.current_step
        success = bool(execution_result.get("success")) and not execution_result.get("timed_out", False)

        if not success:
            self.session.status = "running"
            self._write_event("step_execution_failed", {
                "step_id": step_id,
                "error": execution_result.get("error"),
            })
            return result

        if result_type in {"interactive", "user_interaction", "user_review"}:
            # A review checkpoint waits exactly like an interactive step: the user
            # inspects the results and clicks Confirm (dispatched as "proceed").
            self.session.status = "waiting_for_user"
            self.session.current_step = step_id
            self._write_event("step_waiting_for_user", {"step_id": step_id})
            return result

        if result_type == "user_choice":
            self.session.status = "waiting_for_choice"
            self.session.current_step = step_id
            self._write_event("step_waiting_for_choice", {"step_id": step_id})
            return result

        if result.get("repeat_decision"):
            # A loop continue/exit decision result is already fully transitioned
            # by _handle_pending_repeat_decision in run_step (body cleared +
            # iteration advanced for "repeat", or exit target chosen). Re-marking
            # its terminal step complete here would undo _clear_repeat_body and
            # make the loop skip its own body on the next pass. Just advance to
            # the already-computed next_step.
            next_step = result.get("next_step")
            if next_step:
                self.session.current_step = next_step.get("step_id")
                self.session.status = "running"
            else:
                self.session.current_step = None
                self.session.status = "completed"
                result["workflow_completed"] = True
            self._write_event("step_execution_completed", {
                "step_id": step_id,
                "result_type": result_type,
                "next_step": next_step,
                "workflow_completed": result.get("workflow_completed", False),
            })
            return result

        if result_type in COMPLETE_TYPES and step_id:
            self._mark_completed(step_id)
            repeat_transition = self._repeat_transition_after_completion(
                step_id, result
            )
            if repeat_transition:
                result.update(repeat_transition)
                result_type = result.get("type")
                if result_type == "user_choice":
                    self.session.last_result = result
                    self.session.status = "waiting_for_choice"
                    self.session.current_step = step_id
                    return result
            elif not result.get("next_step"):
                result["next_step"] = self._next_step()

        next_step = result.get("next_step")
        if next_step:
            self.session.current_step = next_step.get("step_id")
            self.session.status = "running"
        elif result_type in COMPLETE_TYPES:
            self.session.current_step = None
            self.session.status = "completed"
            result["workflow_completed"] = True

        self._write_event("step_execution_completed", {
            "step_id": step_id,
            "result_type": result_type,
            "next_step": next_step,
            "workflow_completed": result.get("workflow_completed", False),
        })
        return result

    def queue_traditional_prompt(self, prompt: str) -> int:
        if not self.session:
            return 0
        self.session.queued_prompts.append(prompt)
        self._write_event("traditional_prompt_queued", {"prompt": prompt})
        return len(self.session.queued_prompts)

    def pop_queued_prompts(self) -> List[str]:
        if not self.session:
            return []
        queued = list(self.session.queued_prompts)
        self.session.queued_prompts.clear()
        return queued

    def get_prompt_fragment(self) -> str:
        if not self.session or not self.session.active:
            return ""
        completed = ", ".join(self.session.completed_steps) or "none"
        return (
            f"### Active Generated CLI Workflow: {self.session.extension_name}\n"
            f"- Workflow ID: {self.session.workflow_id}\n"
            f"- Status: {self.session.status}\n"
            f"- Current step: {self.session.current_step}\n"
            f"- Completed steps: {completed}\n"
        )

    def _apply_pre_execution_state(self, result: Dict[str, Any]) -> None:
        if not self.session or not isinstance(result, dict):
            return
        result_type = result.get("type")
        if result_type == "cancelled":
            self.session.status = "cancelled"
            self.session.current_step = None
        elif result_type == "user_choice":
            self.session.status = "waiting_for_choice"
            self.session.current_step = result.get("step_id")
        elif result_type in {"interactive", "user_interaction"}:
            self.session.status = "running"
            self.session.current_step = result.get("step_id")
        elif result_type == "user_review":
            # A review result carries NO code, so no execution round-trip ever
            # re-renders the panel -- the waiting status must be set BEFORE the
            # register-time render or can_done stays False and the Confirm button
            # never appears.
            self.session.status = "waiting_for_user"
            self.session.current_step = result.get("step_id")
        elif result_type == "skipped" and result.get("step_id"):
            self._mark_completed(result["step_id"])
            next_step = result.get("next_step") or self._next_step()
            if next_step:
                result["next_step"] = next_step
                self.session.current_step = next_step.get("step_id")
                self.session.status = "running"
            else:
                self.session.current_step = None
                self.session.status = "completed"

    def _mark_completed(self, step_id: str) -> None:
        if not self.session or not step_id:
            return
        if step_id not in self.session.completed_steps:
            self.session.completed_steps.append(step_id)
            self.session.completed_instances.append({
                "step_id": step_id,
                "repeat": self._repeat_instance_for_step(step_id),
            })
        mark_workflow_step_completed(self.session.extension_name, step_id)
        self._finalize_checkpoint(step_id)

    def _next_step(self) -> Optional[Dict[str, Any]]:
        if not self.session:
            return None
        return find_next_workflow_step(
            self.session.extension_name,
            set(self.session.completed_steps),
        )

    def _repeat_blocks(self) -> List[Dict[str, Any]]:
        if not self.session:
            return []
        graph = get_workflow_graph(self.session.extension_name) or {}
        return [
            block for block in graph.get("repeat_blocks", []) or []
            if isinstance(block, dict) and block.get("repeat_id")
        ]

    def _repeat_instance_for_step(self, step_id: str) -> Dict[str, Any]:
        if not self.session:
            return {}
        for block in self._repeat_blocks():
            if step_id in (block.get("body_steps") or []):
                state = self.session.repeat_states.get(block["repeat_id"], {})
                return {
                    "repeat_id": block["repeat_id"],
                    "iteration": int(state.get("iteration", 1) or 1),
                }
        return {}

    def _sync_repeat_state(self, repeat_id: str) -> None:
        if not self.session:
            return
        state = self.session.repeat_states.get(repeat_id, {})
        set_workflow_repeat_state(
            self.session.extension_name,
            repeat_id,
            state,
        )

    def _clear_repeat_body(self, block: Dict[str, Any]) -> None:
        if not self.session:
            return
        body_steps = list(block.get("body_steps") or [])
        body_set = set(body_steps)
        self.session.completed_steps = [
            step_id for step_id in self.session.completed_steps
            if step_id not in body_set
        ]
        clear_workflow_step_completions(self.session.extension_name, body_steps)

    @staticmethod
    def _normalize_control_value(value: Any) -> Any:
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"true", "yes", "y", "1"}:
                return True
            if lowered in {"false", "no", "n", "0"}:
                return False
            try:
                return int(lowered)
            except ValueError:
                return value.strip()
        return value

    def _loop_should_exit(self, controller: Dict[str, Any], choice_value: Any) -> bool:
        """Whether an answer EXITS / skips a loop body — the single polarity source
        of truth for both the pre-guard (decision before the body) and the terminal
        loop-again decision.

        For a pre-guarded section (``controller.source_step`` present) the optional
        body is opt-in: it runs only if the user affirmatively accepts at the guard.
        The guard step's own ``choice_info`` is authoritative — its
        ``default_value`` is the "skip" answer, and a boolean guard's negative/No
        answer skips. This deliberately avoids ``exit_value`` (which the LLM has
        emitted inverted for pre-guards). For a source-less do-while loop the
        long-standing convention holds: exit when the answer equals ``exit_value``.
        Generic: keys only on ``source_step`` presence + the guard's choice_info.
        """
        norm = self._normalize_control_value(choice_value)
        # A deterministically SYNTHESIZED controller (backward-jump loop) carries
        # its own exit polarity: which clause loops back decides which answer
        # exits, and the guard step's LLM-authored default cannot know that (for a
        # decline-backward loop -- "if done jump forward, if not jump back" -- the
        # accept answer exits, the opposite of the default convention). The flag is
        # only ever written by the synthesis, never by the LLM.
        if controller.get("polarity") == "deterministic":
            return norm == self._normalize_control_value(controller.get("exit_value"))
        source_step = controller.get("source_step")
        if source_step:
            choice_info = (self._step_meta(source_step) or {}).get("choice_info") or {}
            default_value = choice_info.get("default_value")
            if default_value is not None:
                return norm == self._normalize_control_value(default_value)
            if isinstance(norm, bool):
                return norm is False
        return norm == self._normalize_control_value(controller.get("exit_value"))

    def _mark_skip_range(self, source_step: Optional[str], exit_step: Optional[str],
                         block: Dict[str, Any]) -> None:
        """Mark the steps a declined pre-guard skips as completed, by graph order.

        Generic: marks every step strictly between ``source_step`` and a forward
        ``exit_step`` (leaving ``exit_step`` for the finder to land on), or — when
        there is no forward target (stop / empty / unknown / backward) — from after
        ``source_step`` through the end so the workflow completes. Falls back to the
        block's ``body_steps`` if the ids do not resolve.
        """
        if not self.session:
            return
        graph = get_workflow_graph(self.session.extension_name) or {}
        ordered = [s.get("step_id") for s in graph.get("steps", []) or [] if s.get("step_id")]
        if source_step in ordered:
            src = ordered.index(source_step)
            exit_pos = ordered.index(exit_step) if exit_step in ordered else None
            skip = ordered[src + 1:exit_pos] if (exit_pos is not None and exit_pos > src) else ordered[src + 1:]
            for sid in skip:
                self._mark_completed(sid)
            return
        for sid in block.get("body_steps", []) or []:
            self._mark_completed(sid)

    def _repeat_transition_after_completion(
        self,
        step_id: str,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Return a control-flow transition after one atomic step succeeds."""
        if not self.session:
            return {}
        if result.get("repeat_decision"):
            return {}
        for block in self._repeat_blocks():
            repeat_id = block["repeat_id"]
            controller = block.get("controller", {}) or {}
            kind = controller.get("kind", "")
            state = self.session.repeat_states.setdefault(
                repeat_id, {"iteration": 1}
            )

            if kind == "count" and step_id == controller.get("source_step"):
                raw_target = self._normalize_control_value(result.get("choice_value"))
                try:
                    target = int(raw_target)
                except (TypeError, ValueError):
                    target = 0
                state.update({"iteration": 1, "target": max(0, target)})
                self._sync_repeat_state(repeat_id)
                if target <= 0:
                    for body_step in block.get("body_steps", []) or []:
                        self._mark_completed(body_step)
                    next_step = self._step_summary(block.get("exit_step"))
                    return {
                        "next_step": next_step,
                        "repeat_progress": {
                            "repeat_id": repeat_id,
                            "current": 0,
                            "completed": 0,
                            "total": 0,
                        },
                    }

            if (kind in {"until_choice", "while_choice"}
                    and step_id == controller.get("source_step")
                    and controller.get("source_step") != block.get("terminal_step")):
                # Pre-guard: the optional body is gated by the guard step's own
                # choice, evaluated BEFORE the body. Decline -> skip the body and
                # jump to the exit target (or stop when empty); accept -> enter the
                # body. A branch_op guard is a ONE-TIME conditional (body runs once,
                # then continues at the natural next step -- see the terminal
                # branch); a user_choice guard offers a loop-again decision there.
                # (A loop-back block, where source == terminal, is excluded above and
                # handled at the terminal branch so the body is CLEARED before
                # re-entry.)
                if self._loop_should_exit(controller, result.get("choice_value")):
                    self._mark_skip_range(
                        controller.get("source_step"), block.get("exit_step"), block
                    )
                    state.update({"iteration": 0, "waiting_for_decision": False})
                    self._sync_repeat_state(repeat_id)
                    return {
                        "next_step": self._step_summary(block.get("exit_step")),
                        "repeat_progress": {
                            "repeat_id": repeat_id, "current": 0,
                            "completed": 0, "total": 0,
                        },
                    }
                state.update({"iteration": 1, "waiting_for_decision": False})
                self._sync_repeat_state(repeat_id)
                return {
                    "next_step": self._step_summary(block.get("entry_step")),
                    "repeat_progress": {
                        "repeat_id": repeat_id, "current": 1,
                        "completed": 0, "total": 0,
                    },
                }

            if step_id != block.get("terminal_step"):
                continue

            iteration = int(state.get("iteration", 1) or 1)
            max_iterations = int(block.get("max_iterations", 20) or 20)
            if kind == "count":
                target = int(state.get("target", 1) or 1)
                if iteration < min(target, max_iterations):
                    self._clear_repeat_body(block)
                    state["iteration"] = iteration + 1
                    self._sync_repeat_state(repeat_id)
                    return {
                        "next_step": self._step_summary(block.get("entry_step")),
                        "repeat_progress": {
                            "repeat_id": repeat_id,
                            "current": iteration + 1,
                            "completed": iteration,
                            "total": target,
                        },
                    }
                return {
                    "next_step": self._step_summary(block.get("exit_step")),
                    "repeat_limit_reached": target > max_iterations,
                    "repeat_progress": {
                        "repeat_id": repeat_id,
                        "current": iteration,
                        "completed": iteration,
                        "total": target,
                    },
                }

            if kind in {"until_choice", "while_choice"}:
                # Decision-at-end LOOP-BACK: the terminal step IS the branch_op /
                # user_choice the user just answered, and ACCEPT jumps BACKWARD to
                # entry (a per-item loop, e.g. "adjust ANOTHER fragment? -> back to
                # the select step"). Distinct from a pre-guard (source precedes the
                # body) and the synthetic do-while (no explicit decision step). Must
                # run BEFORE the branch_op single-pass short-circuit below, which
                # keys on the SOURCE op type and would otherwise mis-classify
                # source==terminal==branch_op as single-pass.
                if controller.get("source_step") == block.get("terminal_step"):
                    should_exit = self._loop_should_exit(controller, result.get("choice_value"))
                    if should_exit or iteration >= max_iterations:
                        state.update({"iteration": 0, "waiting_for_decision": False})
                        self._sync_repeat_state(repeat_id)
                        return {
                            "next_step": self._step_summary(block.get("exit_step")),
                            "repeat_limit_reached": (not should_exit) and iteration >= max_iterations,
                            "repeat_progress": {
                                "repeat_id": repeat_id, "current": iteration,
                                "completed": iteration, "total": 0,
                            },
                        }
                    # Accept -> loop: re-arm the body and jump back to entry.
                    self._clear_repeat_body(block)
                    state["iteration"] = iteration + 1
                    self._sync_repeat_state(repeat_id)
                    return {
                        "next_step": self._step_summary(block.get("entry_step")),
                        "repeat_progress": {
                            "repeat_id": repeat_id, "current": iteration + 1,
                            "completed": iteration, "total": 0,
                        },
                    }
                # One-time conditional: a branch_op guard already decided (at the
                # source step) whether to run this body, and the body's own action
                # (e.g. unticking the checkbox) ends the section -- so it runs ONCE.
                # Do NOT re-ask a loop-again decision at the terminal; continue at
                # the natural next step. A user_choice-sourced or source-less
                # do-while block still loops (below).
                _src = controller.get("source_step")
                _src_meta = self._step_meta(_src) if _src else {}
                _src_op = (
                    (_src_meta or {}).get("operation_type")
                    or (_src_meta or {}).get("op_type")
                    or ""
                )
                if _src_op == "branch_op":
                    state.update({"iteration": 0, "waiting_for_decision": False})
                    self._sync_repeat_state(repeat_id)
                    return {
                        "next_step": self._next_step(),
                        "repeat_progress": {
                            "repeat_id": repeat_id,
                            "current": iteration,
                            "completed": iteration,
                            "total": 0,
                        },
                    }
                state["waiting_for_decision"] = True
                self._sync_repeat_state(repeat_id)
                prompt = controller.get("prompt") or "Continue the repeated workflow?"
                choices = [
                    {"label": "Yes", "value": True},
                    {"label": "No", "value": False},
                ]
                # Derive which answer exits vs repeats via _loop_should_exit, so the
                # instruction is correct for both source-less do-while loops and
                # pre-guarded sections (whose exit_value is inverted) -- and matches
                # how the decision is actually resolved.
                exit_label = next(
                    (c["label"] for c in choices
                     if self._loop_should_exit(controller, c["value"])),
                    "Yes",
                )
                loop_label = next(
                    (c["label"] for c in choices
                     if not self._loop_should_exit(controller, c["value"])),
                    "No",
                )
                decision_instruction = (
                    f'Choose "{loop_label}" to repeat this section and refine the '
                    f'result; choose "{exit_label}" to accept it and continue.'
                )
                return {
                    "type": "user_choice",
                    "question": prompt,
                    "instruction": decision_instruction,
                    "choices": choices,
                    "parameter_name": f"repeat_decision:{repeat_id}",
                    "repeat_decision": repeat_id,
                    "repeat_progress": {
                        "repeat_id": repeat_id,
                        "current": iteration,
                        "completed": iteration,
                        "total": 0,
                    },
                    "next_step": None,
                }
        return {}

    def _handle_pending_repeat_decision(
        self,
        step_id: str,
        action: str,
        args: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        if not self.session or action != "choice_made":
            return None
        for block in self._repeat_blocks():
            repeat_id = block["repeat_id"]
            state = self.session.repeat_states.get(repeat_id, {})
            if not state.get("waiting_for_decision"):
                continue
            if step_id != block.get("terminal_step"):
                continue
            controller = block.get("controller", {}) or {}
            choice = self._normalize_control_value(args.get("choice_value"))
            should_exit = self._loop_should_exit(controller, args.get("choice_value"))
            iteration = int(state.get("iteration", 1) or 1)
            max_iterations = int(block.get("max_iterations", 20) or 20)
            state["waiting_for_decision"] = False
            limit_reached = not should_exit and iteration >= max_iterations
            if should_exit or limit_reached:
                next_step = self._step_summary(block.get("exit_step"))
            else:
                self._clear_repeat_body(block)
                state["iteration"] = iteration + 1
                next_step = self._step_summary(block.get("entry_step"))
            self._sync_repeat_state(repeat_id)
            return {
                "tool": self.session.tool_name,
                "type": "choice_made",
                "step_id": step_id,
                "choice_value": choice,
                "repeat_decision": repeat_id,
                "repeat_limit_reached": limit_reached,
                "next_step": next_step,
                "repeat_progress": {
                    "repeat_id": repeat_id,
                    "current": int(state.get("iteration", iteration) or iteration),
                    "completed": iteration,
                    "total": 0,
                },
            }
        return None

    def _step_summary(self, step_id: Optional[str]) -> Optional[Dict[str, Any]]:
        if not self.session or not step_id:
            return None
        graph = get_workflow_graph(self.session.extension_name) or {}
        for step in graph.get("steps", []) or []:
            if step.get("step_id") == step_id:
                return {
                    "step_id": step_id,
                    "operation_type": (
                        step.get("operation_type")
                        or step.get("op_type")
                        or step.get("step_type", "extension_op")
                    ),
                    "step_type": step.get("step_type", "extension_op"),
                    "description": step.get("description", ""),
                    "is_optional": bool(step.get("is_optional", False)),
                    "ui_guidance": step.get("ui_guidance", {}),
                }
        return None

    @staticmethod
    def _instructions_from_result(result: Dict[str, Any]) -> str:
        if not isinstance(result, dict):
            return ""
        if result.get("type") == "user_choice":
            return ""
        interaction = result.get("interaction") or {}
        return (
            interaction.get("placement_instructions")
            or result.get("interaction_instructions")
            or ""
        )

    @staticmethod
    def _ui_guidance_from_result(result: Dict[str, Any], step_meta: Dict[str, Any]) -> Dict[str, Any]:
        """Return generated UI guidance from result or workflow metadata."""
        guidance = {}
        if isinstance(step_meta, dict) and isinstance(step_meta.get("ui_guidance"), dict):
            guidance.update(step_meta["ui_guidance"])
        if isinstance(result, dict) and isinstance(result.get("ui_guidance"), dict):
            guidance.update(result["ui_guidance"])
        if isinstance(result, dict):
            interaction = result.get("interaction") or {}
            if isinstance(interaction, dict) and isinstance(interaction.get("ui_guidance"), dict):
                guidance.update(interaction["ui_guidance"])
        return guidance

    @staticmethod
    def _choices_from_result(result: Dict[str, Any], step_meta: Dict[str, Any]) -> List[Dict[str, Any]]:
        source_choices = []
        if isinstance(result, dict):
            source_choices = result.get("choices") or []
        if not source_choices and isinstance(step_meta, dict):
            source_choices = (step_meta.get("choice_info") or {}).get("choices") or []
        if not source_choices and isinstance(result, dict):
            source_choices = WorkflowRuntime._choices_from_instruction(result.get("instruction", ""))
        choices = []
        for choice in source_choices:
            if not isinstance(choice, dict):
                continue
            label = str(choice.get("label", choice.get("value", ""))).strip()
            value = str(choice.get("value", label)).strip()
            if label or value:
                choices.append({"label": label or value, "value": value or label})
        return choices

    @staticmethod
    def _choices_from_instruction(instruction: str) -> List[Dict[str, Any]]:
        """Best-effort fallback for compact user_choice results."""
        choices = []
        for line in str(instruction or "").splitlines():
            match = re.match(r"\s*\d+[.)]\s+(.+?)\s*$", line)
            if not match:
                continue
            label = match.group(1).strip()
            if label:
                lowered = label.lower()
                if lowered == "yes":
                    value = "true"
                elif lowered == "no":
                    value = "false"
                else:
                    value = label
                choices.append({"label": label, "value": value})
        return choices

    @staticmethod
    def _ui_status_label(status: str, result_type: str = "") -> str:
        if status == "waiting_for_user":
            return "Waiting for your interaction"
        if status == "waiting_for_choice":
            return "Waiting for your choice"
        if status == "completed":
            return "Completed"
        if status == "cancelled":
            return "Cancelled"
        if result_type == "user_choice":
            return "Waiting for your choice"
        return "Running"

    @staticmethod
    def _display_name(name: str) -> str:
        text = str(name or "").replace("_", " ").replace("-", " ").strip()
        if not text:
            return "Workflow"
        return re.sub(r"(?<!^)(?=[A-Z])", " ", text).strip()

    @staticmethod
    def _tool_name_for_extension(ext_data: Dict[str, Any]) -> Optional[str]:
        for schema in ext_data.get("schemas", []):
            func = schema.get("function", {})
            if func.get("name"):
                return func["name"]
        return None

    @classmethod
    def _extension_name_for_tool(cls, tool_name: str) -> Optional[str]:
        for ext_name, ext_data in get_validated_extensions().items():
            if cls._tool_name_for_extension(ext_data) == tool_name:
                return ext_name
        return None

    @staticmethod
    def _compact_result(result: Dict[str, Any]) -> Dict[str, Any]:
        compact = {}
        for key in (
            "tool",
            "type",
            "step_id",
            "instruction",
            "explanation",
            "interaction_instructions",
            "question",
            "choices",
            "default_value",
            "ui_guidance",
            "repeat_progress",
            "next_step",
            "workflow_completed",
            "error",
        ):
            if key in result:
                compact[key] = result[key]
        if result.get("code"):
            compact["code_chars"] = len(result.get("code") or "")
        return compact

    # =====================================================================
    # Replay timeline — live checkpoint recording, rewind, scene snapshots
    # =====================================================================

    def _begin_pending_checkpoint(self, step_id: str, call_args: Dict[str, Any]) -> None:
        """Snapshot the scene + state BEFORE ``step_id`` dispatches.

        Idempotent across an interactive step's start->proceed pair: the second
        call keeps the before-placement scene captured at start and only
        refreshes the recorded args.
        """
        if not self.session or not step_id:
            return
        if self._pending_checkpoint and self._pending_checkpoint.get("step_id") == step_id:
            self._pending_checkpoint["call_args"] = dict(call_args or {})
            return
        # A different step's pending was never finalized (prior step failed or
        # was retried by self-correction); drop it first.
        self._discard_pending_checkpoint()
        self._pending_checkpoint = {
            "step_id": step_id,
            "call_args": dict(call_args or {}),
            "completed_prefix": list(self.session.completed_steps),
            "completed_instances_len": len(self.session.completed_instances),
            "repeat_states_snapshot": copy.deepcopy(self.session.repeat_states),
            "choices_prefix": get_workflow_choices(self.session.extension_name),
            "node_ids_before": self._scene_node_ids(),
            "layout_before": self._current_layout(),
            # Full before-step snapshot; restored by property-copy (never
            # delete) so ALL node state recovers without losing display nodes.
            "sceneview_node_id": self._capture_sceneview(step_id),
        }

    def _discard_pending_checkpoint(self) -> None:
        """Drop an un-finalized pending checkpoint and its orphan snapshot."""
        pending = self._pending_checkpoint
        self._pending_checkpoint = None
        if pending:
            self._delete_sceneview(pending.get("sceneview_node_id"))

    def _finalize_checkpoint(self, step_id: str) -> None:
        """Promote the pending snapshot for ``step_id`` into a WorkflowCheckpoint."""
        pending = self._pending_checkpoint
        if not pending or pending.get("step_id") != step_id:
            return
        self._pending_checkpoint = None
        self._record_checkpoint(pending)

    def _finalize_loop_decision_checkpoint(
        self,
        step_id: str,
        call_args: Dict[str, Any],
        repeat_decision: Dict[str, Any],
    ) -> None:
        """Record a checkpoint for a loop continue/exit decision (run_step path)."""
        if not self.session:
            return
        pending = self._pending_checkpoint
        if not pending or pending.get("step_id") != step_id:
            pending = {
                "step_id": step_id,
                "call_args": dict(call_args or {}),
                "completed_prefix": list(self.session.completed_steps),
                "completed_instances_len": len(self.session.completed_instances),
                "repeat_states_snapshot": copy.deepcopy(self.session.repeat_states),
                "choices_prefix": get_workflow_choices(self.session.extension_name),
                "node_ids_before": self._scene_node_ids(),
                "layout_before": self._current_layout(),
                "sceneview_node_id": self._capture_sceneview(step_id),
            }
        self._pending_checkpoint = None
        progress = repeat_decision.get("repeat_progress") or {}
        repeat = {
            "repeat_id": progress.get("repeat_id", "") or "",
            "iteration": progress.get("current") or progress.get("completed") or 0,
        }
        self._record_checkpoint(pending, force_kind="loop_decision", repeat=repeat)

    def _record_checkpoint(
        self,
        pending: Dict[str, Any],
        force_kind: Optional[str] = None,
        repeat: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not self.session:
            return
        step_id = pending["step_id"]
        meta = self._step_meta(step_id)
        op = (
            meta.get("operation_type")
            or meta.get("op_type")
            or meta.get("step_type")
            or "extension_op"
        )
        call_args = pending.get("call_args") or {}
        choice_value = call_args.get("choice_value")
        repeat_info = repeat if repeat is not None else self._repeat_instance_for_step(step_id)

        choices: List[Dict[str, Any]] = []
        if force_kind == "loop_decision":
            kind = "loop_decision"
            action = "choice_made"
            args = {"choice_value": choice_value}
            editable = True
            recorded_value = choice_value
            parameter_name = f"repeat_decision:{(repeat_info or {}).get('repeat_id', '')}"
            choices = [{"label": "Yes", "value": True}, {"label": "No", "value": False}]
        elif op == "user_choice" or choice_value is not None:
            kind = "loop_count" if self._is_loop_count_source(step_id) else "choice"
            action = "choice_made"
            args = {"choice_value": choice_value}
            editable = True
            recorded_value = choice_value
            choice_info = meta.get("choice_info") or {}
            parameter_name = choice_info.get("parameter_name", "") or ""
            choices = self._normalize_choices(choice_info.get("choices") or [])
        elif op == "user_interaction" or meta.get("step_type") in (
            "interactive", "mixed", "user_interaction",
        ):
            kind = "interaction"
            action = "start"
            args = {}
            editable = False
            recorded_value = self._interaction_summary(step_id)
            parameter_name = ""
        else:
            kind = "automated"
            action = "start"
            args = {}
            editable = False
            recorded_value = None
            parameter_name = ""

        before = pending.get("node_ids_before") or set()
        created = [nid for nid in self._scene_node_ids() if nid not in before]
        index = len(self.session.checkpoints)
        if index == 0 and not self.session.baseline_node_ids:
            # Scene before the first step = loaded inputs (e.g. the CT volume);
            # used by the UI to avoid warning about deleting them on rewind.
            self.session.baseline_node_ids = sorted(before)
        summary = self._checkpoint_summary(meta, kind, recorded_value, repeat_info)
        guidance = self._ui_guidance_from_result(self.session.last_result or {}, meta)
        guidance_description = (
            str(guidance.get("title", "") or "").strip()
            or str(meta.get("description", "") or "").strip()
        )
        guidance_instructions = (
            str(guidance.get("instruction", "") or "").strip()
            or self._instructions_from_result(self.session.last_result or {})
        )
        checkpoint = WorkflowCheckpoint(
            index=index,
            step_id=step_id,
            kind=kind,
            action=action,
            args=args,
            recorded_value=recorded_value,
            parameter_name=parameter_name,
            editable=editable,
            choices=choices,
            guidance_description=guidance_description,
            guidance_instructions=guidance_instructions,
            repeat=dict(repeat_info or {}),
            repeat_states_snapshot=pending.get("repeat_states_snapshot") or {},
            completed_prefix=list(pending.get("completed_prefix") or []),
            completed_instances_len=int(pending.get("completed_instances_len") or 0),
            choices_prefix=dict(pending.get("choices_prefix") or {}),
            before_node_ids=sorted(before),
            created_node_ids=created,
            layout_before=int(pending.get("layout_before", -1)),
            sceneview_node_id=pending.get("sceneview_node_id"),
            summary=summary,
            timestamp=round(time.time(), 3),
        )
        self.session.checkpoints.append(checkpoint)
        self.session.active_checkpoint_index = index
        self._write_event("checkpoint_recorded", {
            "index": index,
            "step_id": step_id,
            "kind": kind,
            "editable": editable,
            "repeat": repeat_info,
        })

    def _timeline_for_ui(self) -> List[Dict[str, Any]]:
        if not self.session:
            return []
        active = self.session.active_checkpoint_index
        items = []
        for cp in self.session.checkpoints:
            cp_repeat = cp.repeat or {}
            items.append({
                "index": cp.index,
                "step_id": cp.step_id,
                "kind": cp.kind,
                "summary": cp.summary,
                "repeat_id": cp_repeat.get("repeat_id", "") or "",
                "iteration": int(cp_repeat.get("iteration", 0) or 0),
                "is_current": cp.index == active,
                "recorded_value": cp.recorded_value,
                "parameter_name": cp.parameter_name,
                "editable": bool(cp.editable),
                "choices": list(cp.choices or []),
                "can_restore": bool(cp.sceneview_node_id),
            })
        return items

    # ---- Back/Forward navigation: full property recovery, never delete ----
    #
    # "Recover" means recover EVERYTHING at that step, not just node existence:
    # baseline-node display (e.g. the loaded segmentation's 3D surface/contours),
    # the layout, slice/view state, transforms, colors. We capture a full
    # vtkMRMLSceneViewNode per step but RESTORE it by COPYING the stored node
    # properties onto the matching live nodes (by ID) — never deleting or
    # re-creating a node, so display nodes are never lost. Nodes that did not
    # exist yet at that step are simply hidden. Slicer's own RestoreScene can't
    # be used here: removeNodes=False aborts when later nodes are present, and
    # removeNodes=True deletes+recreates (which is what drops display nodes).

    def navigate_back(self) -> Dict[str, Any]:
        """Step one step back: recover that step's full scene state. Non-destructive."""
        if not self.session or not self.session.checkpoints:
            return self._preview_ui_state()
        if self.session.preview_index is None:
            # Leaving the live state: snapshot it (scene + layout) so Forward can
            # return to it exactly.
            self.session.live_layout = self._current_layout()
            self.session.live_sceneview_id = self._capture_sceneview("live")
            self.session.preview_index = len(self.session.checkpoints) - 1
        elif self.session.preview_index > 0:
            self.session.preview_index -= 1
        else:
            return self._preview_ui_state()  # already at the first checkpoint
        self._restore_to_view(self.session.preview_index)
        self._write_event("replay_navigate", {
            "direction": "back", "preview_index": self.session.preview_index,
        })
        return self._preview_ui_state()

    def navigate_forward(self) -> Dict[str, Any]:
        """Step one step forward, or back to the live state. Non-destructive."""
        if not self.session or self.session.preview_index is None:
            return self._preview_ui_state()  # already live
        last = len(self.session.checkpoints) - 1
        if self.session.preview_index < last:
            self.session.preview_index += 1
            self._restore_to_view(self.session.preview_index)
        else:
            # Past the last checkpoint: recover the live state and exit preview.
            self._restore_to_view(None)
            self._delete_sceneview(self.session.live_sceneview_id)
            self.session.live_sceneview_id = None
            self.session.preview_index = None
        self._write_event("replay_navigate", {
            "direction": "forward", "preview_index": self.session.preview_index,
        })
        return self._preview_ui_state()

    def _restore_to_view(self, index: Optional[int]) -> None:
        """Recover the full scene state at step ``index`` (None = live)."""
        if not self.session:
            return
        if index is None:
            self._restore_scene_properties(self.session.live_sceneview_id)
            self._set_layout(self.session.live_layout)
            self._clear_replay_hidden_tags()
            return
        cp = self.session.checkpoints[index]
        # 1. Copy every stored node's properties onto its live counterpart —
        #    recovers baseline-node display, transforms, slice/view state, etc.
        self._restore_scene_properties(cp.sceneview_node_id)
        # 2. Hide nodes that did not exist yet at this step (the snapshot can't
        #    set their visibility because it doesn't contain them).
        self._hide_nodes_after(index)
        # 3. Restore the layout ("overlay").
        self._set_layout(cp.layout_before)

    def _all_workflow_node_ids(self) -> set:
        """All MRML node IDs the workflow has created across all checkpoints."""
        ids = set()
        if self.session:
            for cp in self.session.checkpoints:
                ids.update(cp.created_node_ids or [])
        return ids

    def _restore_scene_properties(self, sceneview_id: Optional[str]) -> None:
        """Copy stored node properties onto matching live nodes (never delete/add).

        This recovers ALL node state (display visibility/color/view assignments,
        transforms, slice/view nodes, layout node) to the snapshot without
        removing or re-creating any node, so no display node is ever lost.
        """
        if not sceneview_id:
            return
        try:
            import slicer
        except Exception:
            return
        try:
            sv = slicer.mrmlScene.GetNodeByID(sceneview_id)
            if sv is None:
                return
            with _silenced_vtk_output():
                stored = sv.GetStoredScene()
                if stored is None:
                    return
                for i in range(stored.GetNumberOfNodes()):
                    snode = stored.GetNthNode(i)
                    if snode is None or not snode.GetID():
                        continue
                    if snode.IsA("vtkMRMLSceneViewNode"):
                        continue
                    live = slicer.mrmlScene.GetNodeByID(snode.GetID())
                    if live is None or live is snode:
                        continue
                    try:
                        live.Copy(snode)
                    except Exception:
                        pass
        except Exception:
            logger.debug("Scene property restore failed", exc_info=True)

    def _hide_nodes_after(self, index: int) -> None:
        """Hide workflow nodes created at/after step ``index`` (not in its snapshot)."""
        try:
            import slicer
        except Exception:
            return
        if not self.session:
            return
        keep = set(self.session.checkpoints[index].before_node_ids or [])
        try:
            shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        except Exception:
            shNode = None
        try:
            for node_id in self._all_workflow_node_ids():
                after = node_id not in keep
                node = slicer.mrmlScene.GetNodeByID(node_id)
                if node is None:
                    continue
                # Tag the subject-hierarchy item of nodes created AFTER this step so
                # the picker tree excludes them (and empties their output folder);
                # UNtag those that existed. Non-destructive item metadata, cleared
                # on return to live (_restore_to_view(None)).
                if shNode is not None:
                    self._set_replay_hidden_tag(shNode, node, after)
                if after:
                    self._set_node_visibility(node, False)
        except Exception:
            logger.debug("Hide-after toggle failed", exc_info=True)
        # Also tag OUTPUT folders (SH folder items whose data-node descendants were
        # ALL created after this step) so the picker's exclude filter drops the
        # folder itself, not just its contents -- a folder is not a data node, so
        # tagging the child nodes alone leaves it visible. A folder holding any kept
        # (before-step) node is left untagged (visible).
        if shNode is not None:
            try:
                self._tag_after_step_folders(shNode, keep)
            except Exception:
                logger.debug("Folder replay-tag failed", exc_info=True)

    def _tag_after_step_folders(self, shNode, keep: set) -> None:
        """Tag/untag output-only subject-hierarchy FOLDER items for replay hiding."""
        import vtk
        try:
            import slicer
            folder_level = slicer.vtkMRMLSubjectHierarchyConstants.GetSubjectHierarchyLevelFolder()
        except Exception:
            folder_level = "Folder"
        all_items = vtk.vtkIdList()
        shNode.GetItemChildren(shNode.GetSceneItemID(), all_items, True)  # recursive
        for i in range(all_items.GetNumberOfIds()):
            item = all_items.GetId(i)
            try:
                if not shNode.IsItemLevel(item, folder_level):
                    continue
            except Exception:
                continue
            # Inspect this folder's data-node descendants.
            desc = vtk.vtkIdList()
            shNode.GetItemChildren(item, desc, True)
            has_data = False
            all_after = True
            for j in range(desc.GetNumberOfIds()):
                dn = shNode.GetItemDataNode(desc.GetId(j))
                if dn is not None and dn.GetID():
                    has_data = True
                    if dn.GetID() in keep:  # a node that existed at this step
                        all_after = False
                        break
            try:
                if has_data and all_after:
                    shNode.SetItemAttribute(item, WorkflowRuntime.REPLAY_HIDDEN_SH_ATTR, "1")
                else:
                    shNode.RemoveItemAttribute(item, WorkflowRuntime.REPLAY_HIDDEN_SH_ATTR)
            except Exception:
                pass

    @staticmethod
    def _set_replay_hidden_tag(shNode, node, hidden: bool) -> None:
        """Set/clear the picker-exclusion item attribute on ``node``'s SH item."""
        try:
            item = shNode.GetItemByDataNode(node)
            if not item:
                return
            if hidden:
                shNode.SetItemAttribute(item, WorkflowRuntime.REPLAY_HIDDEN_SH_ATTR, "1")
            else:
                shNode.RemoveItemAttribute(item, WorkflowRuntime.REPLAY_HIDDEN_SH_ATTR)
        except Exception:
            pass

    def _clear_replay_hidden_tags(self) -> None:
        """Remove the picker-exclusion tag from every SH item (return to live).

        Sweeps ALL subject-hierarchy items (data nodes AND folders), so nothing
        tagged during replay can linger and hide a node in the live picker.
        """
        import vtk
        try:
            import slicer
            shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        except Exception:
            shNode = None
        if shNode is None:
            return
        try:
            all_items = vtk.vtkIdList()
            shNode.GetItemChildren(shNode.GetSceneItemID(), all_items, True)
            for i in range(all_items.GetNumberOfIds()):
                try:
                    shNode.RemoveItemAttribute(all_items.GetId(i), WorkflowRuntime.REPLAY_HIDDEN_SH_ATTR)
                except Exception:
                    pass
        except Exception:
            logger.debug("Clear replay-hidden tags failed", exc_info=True)

    @staticmethod
    def _set_node_visibility(node, visible: bool) -> None:
        """Toggle a node's display visibility; create a display node if missing."""
        try:
            if not hasattr(node, "GetNumberOfDisplayNodes"):
                return
            count = node.GetNumberOfDisplayNodes()
            if count == 0 and visible:
                try:
                    node.CreateDefaultDisplayNodes()
                    count = node.GetNumberOfDisplayNodes()
                except Exception:
                    count = 0
            for i in range(count):
                dn = node.GetNthDisplayNode(i)
                if dn is not None:
                    dn.SetVisibility(1 if visible else 0)
        except Exception:
            pass

    @staticmethod
    def _current_layout() -> int:
        """Return the current Slicer layout id, or -1 if unavailable."""
        try:
            import slicer
            return int(slicer.app.layoutManager().layout)
        except Exception:
            return -1

    @staticmethod
    def _set_layout(layout_id: int) -> None:
        """Restore the Slicer layout (the conventional/extension view 'overlay')."""
        try:
            if layout_id is None or int(layout_id) < 0:
                return
            import slicer
            lm = slicer.app.layoutManager()
            if lm is not None and lm.layout != int(layout_id):
                lm.setLayout(int(layout_id))
        except Exception:
            logger.debug("Layout restore failed", exc_info=True)

    def _commit_node_state(self, index: int) -> None:
        """Recover the before-step state, then DELETE downstream nodes for a clean re-run."""
        try:
            import slicer
        except Exception:
            return
        if not self.session:
            return
        cp = self.session.checkpoints[index]
        # Recover all upstream/baseline node state to the before-step snapshot
        # (display, transforms, layout, slice/view) without deleting anything.
        self._restore_scene_properties(cp.sceneview_node_id)
        keep = set(cp.before_node_ids or [])
        try:
            removed = 0
            for node_id in self._all_workflow_node_ids():
                if node_id in keep:
                    continue
                node = slicer.mrmlScene.GetNodeByID(node_id)
                if node is not None:
                    try:
                        slicer.mrmlScene.RemoveNode(node)    # downstream: delete for re-run
                        removed += 1
                    except Exception:
                        pass
            if removed:
                logger.info("[Replay] Removed %d downstream node(s) for re-run", removed)
        except Exception:
            logger.debug("Commit node state failed", exc_info=True)
        self._set_layout(cp.layout_before)

    def _preview_ui_state(self) -> Dict[str, Any]:
        """UI-state dict for the current navigation position.

        When live (preview_index is None) this is the normal state_for_ui. When
        previewing checkpoint i it returns that step's guidance + progress AND
        the choice buttons / parameter input that the step originally showed, so
        the user can see (and re-pick) the recorded choice; clicking one re-runs
        from that step. Done/Skip stay hidden so only Back/Forward/Action and the
        choices drive.
        """
        if not self.session:
            return {"active": False}
        if self.session.preview_index is None:
            return self.state_for_ui()
        idx = self.session.preview_index
        cp = self.session.checkpoints[idx]
        graph = get_workflow_graph(self.session.extension_name) or {}
        steps = graph.get("steps", []) if isinstance(graph, dict) else []
        step_ids = [s.get("step_id") for s in steps if s.get("step_id")]
        total_steps = graph.get("step_count") or len(steps)
        current_index = (step_ids.index(cp.step_id) + 1) if cp.step_id in step_ids else 0
        # Re-surface the step's interactive elements from the checkpoint so they
        # reappear while scrubbing. Free-form params (no enumerated choices) show
        # a prefilled input; clicking/submitting re-runs from here with that value.
        meta = self._step_meta(cp.step_id)
        guidance = (meta.get("ui_guidance") or {}) if isinstance(meta, dict) else {}
        choices = list(cp.choices or [])
        # Mirror the live path: a node-pick step drives the scene node tree,
        # never the recorded literal buttons. Loop decisions (Yes/No) and
        # segment-visibility steps are left untouched.
        if cp.kind != "loop_decision" and self._is_node_selection_step(meta):
            choices = []
        needs_input = bool(cp.editable) and not choices
        binding = self._node_binding_for_param(cp.parameter_name)
        node_class = binding.get("node_class", "")
        if not node_class:
            # Mirror the live path EXACTLY: resolve the step graph's node class for
            # any node-selection step (``_node_class_from_step_meta`` returns "" for
            # non-node steps, so this is a no-op for them). The previous ``and
            # needs_input`` gate left node_class empty when the checkpoint was not
            # editable, so the replayed node tree fell back to nodeTypes=[""] and
            # displayed the WHOLE scene (every class + subject-hierarchy folders)
            # instead of just the matching nodes.
            node_class = self._node_class_from_step_meta(meta)
        # Mirror the live path's selection-widget reproduction so replaying back to
        # a segments-table step re-renders the table (not a free-text box).
        source_widget_class = self._source_widget_class(meta)
        segment_meta = self._segment_selection_meta(meta)
        if not segment_meta and source_widget_class == "qMRMLSegmentsTableView":
            segment_meta = {"segmentation_node_class": "vtkMRMLSegmentationNode"}
        if segment_meta:
            # A segments-table step is an interactive visibility toggle, not an
            # enumerated choice; mirror the live path so the table re-renders.
            choices = []
            needs_input = True
        # Mirror the live path for the two single-pick segment families too, so
        # replaying back to one re-renders its picker rather than a free-text box.
        segment_name_meta = self._segment_name_selection_meta(meta)
        if segment_name_meta:
            choices = []
            needs_input = True
        segment_ref_meta = self._segment_ref_meta(meta)
        if segment_ref_meta:
            choices = []
            needs_input = True
        # Mirror the live path: a multi-selection step re-renders its form.
        if self._multi_choice_items(meta):
            choices = []
            needs_input = True
        # Mirror the live path: a range step re-renders its slider on replay.
        range_meta = self._range_selection_meta(meta)
        if range_meta:
            choices = []
            needs_input = True
        scalar_meta = self._scalar_slider_meta(meta)
        if scalar_meta:
            choices = []
            needs_input = True
        # Clinically-informed instructions override the recorded guidance (live
        # lookup so manual edits show in replay too).
        instr = self._step_instructions_for(cp.step_id)
        button_overrides = instr.get("buttons") if isinstance(instr.get("buttons"), dict) else {}
        return {
            "active": True,
            "extension_name": self.session.extension_name,
            "workflow_title": self._display_name(self.session.extension_name),
            "current_step": cp.step_id,
            "current_index": current_index,
            "completed_steps": idx,
            "total_steps": int(total_steps or 0),
            "status": f"Reviewing step {idx + 1}",
            "description": instr.get("title") or cp.guidance_description or cp.summary,
            "instructions": instr.get("simple") or cp.guidance_instructions,
            "instructions_detailed": instr.get("detailed", ""),
            "choices": choices,
            "needs_choice_input": needs_input,
            "default_value": cp.recorded_value,
            "parameter_name": cp.parameter_name,
            "node_class": node_class,
            "node_keywords": binding.get("keywords", []) or [],
            "source_widget_class": source_widget_class,
            "segment_selection": bool(segment_meta),
            # Kept in step with the live path (state_for_ui): every selection-widget
            # family must appear at BOTH sites or replay silently degrades the step to
            # a free-text box.
            "segment_name_selection": bool(segment_name_meta),
            "segment_name_source_widget": segment_name_meta.get("source_widget", ""),
            "segment_ref_selection": bool(segment_ref_meta),
            # native_widget re-derived from the step's sub-op flag on replay.
            "native_widget": self._is_native_widget(meta),
            # Replaying back to a review step re-reads the LIVE results (the module
            # widget is still on screen); the checkpoint stores no table snapshot.
            "review_selection": str(meta.get("operation_type") or "") == "review_op"
            and not self._is_native_widget(meta),
            "review_table": (self._live_review_table()
                             if str(meta.get("operation_type") or "") == "review_op" else {}),
            # Mirror the live path: a multi-selection step re-renders its form.
            "multi_choice": bool(self._multi_choice_items(meta)),
            "choice_items": self._multi_choice_items(meta),
            # Reviewing a past interaction step: no live gate (the points already
            # exist); 0 disables the progress display.
            "expected_count": 0,
            "segmentation_node_class": segment_meta.get("segmentation_node_class", "")
            or segment_name_meta.get("segmentation_node_class", ""),
            # Mirror the live path: binding keywords win, else widget-name-derived.
            "segmentation_keywords": (binding.get("keywords", []) or [])
            or segment_meta.get("keywords", [])
            or segment_name_meta.get("keywords", []),
            "segmentation_target_param": segment_meta.get("target_param", "")
            or segment_name_meta.get("target_param", ""),
            "range_selection": bool(range_meta),
            "range_param": range_meta.get("param", ""),
            "range_min": range_meta.get("min"),
            "range_max": range_meta.get("max"),
            "range_step": range_meta.get("step"),
            "range_default": range_meta.get("default"),
            "scalar_selection": bool(scalar_meta),
            "scalar_param": scalar_meta.get("param", ""),
            "scalar_min": scalar_meta.get("min"),
            "scalar_max": scalar_meta.get("max"),
            "scalar_step": scalar_meta.get("step"),
            "scalar_default": scalar_meta.get("default"),
            "scalar_source_widget": scalar_meta.get("source_widget", ""),
            "choice_label": guidance.get("choice_label", ""),
            "input_label": guidance.get("input_label", ""),
            "primary_label": str(button_overrides.get("primary") or ""),
            "choice_label_overrides": button_overrides.get("choices") if isinstance(button_overrides.get("choices"), dict) else {},
            "repeat_progress": cp.repeat or {},
            "can_done": False,
            "can_skip": False,
            "can_cancel": True,
            "replay_can_back": idx > 0,
            "replay_can_forward": True,
            "replay_can_action": True,
            "replay_previewing": True,
            "preview_index": idx,
        }

    @staticmethod
    def _normalize_choices(source_choices) -> List[Dict[str, Any]]:
        choices = []
        for choice in source_choices or []:
            if not isinstance(choice, dict):
                continue
            label = str(choice.get("label", choice.get("value", ""))).strip()
            value = choice.get("value", label)
            if label or (value not in (None, "")):
                choices.append({"label": label or str(value), "value": value})
        return choices

    def rewind_to_checkpoint(
        self,
        index: int,
        modified_args: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Restore scene + truncate all state to BEFORE checkpoint ``index``.

        Returns a {step_id, action, args} descriptor for the widget to feed to
        _runWorkflowStepDirect; this method does not execute step code itself.
        """
        if not self.session:
            return {"error": "No active workflow session"}
        checkpoints = self.session.checkpoints
        if not isinstance(index, int) or index < 0 or index >= len(checkpoints):
            return {"error": f"Invalid checkpoint index: {index}"}
        cp = checkpoints[index]
        ext = self.session.extension_name

        # 1. Recover the before-step state (property-copy, no delete) then delete
        #    the downstream nodes so the re-run recreates them on a clean scene.
        self._commit_node_state(index)

        # 2. Truncate the in-memory session to the checkpoint prefix.
        self.session.completed_steps = list(cp.completed_prefix)
        self.session.completed_instances = (
            self.session.completed_instances[: cp.completed_instances_len]
        )
        self.session.repeat_states = copy.deepcopy(cp.repeat_states_snapshot)
        self.session.current_step = cp.step_id
        self.session.status = "running"
        self.session.last_result = None
        self._discard_pending_checkpoint()

        # 3. Truncate the module-global mirrors to the same prefix.
        truncate_workflow_completions(ext, set(cp.completed_prefix))
        set_workflow_choices(ext, dict(cp.choices_prefix))
        set_all_workflow_repeat_states(ext, cp.repeat_states_snapshot)

        # 4. Drop interaction-node memory for nodes the restore removed.
        try:
            from .workflow_state import prune_missing_interaction_nodes
            prune_missing_interaction_nodes(ext)
        except Exception:
            logger.debug("prune_missing_interaction_nodes failed", exc_info=True)

        # 5. Truncate the checkpoint list to the prefix and delete the discarded
        #    snapshots (and the live snapshot); re-running records new ones.
        for stale in checkpoints[index:]:
            self._delete_sceneview(stale.sceneview_node_id)
        self._delete_sceneview(self.session.live_sceneview_id)
        self.session.live_sceneview_id = None
        self.session.checkpoints = checkpoints[:index]
        self.session.active_checkpoint_index = index - 1 if index > 0 else None
        self.session.preview_index = None

        args = dict(modified_args) if modified_args else dict(cp.args)
        self._write_event("rewind_to_checkpoint", {
            "index": index,
            "step_id": cp.step_id,
            "action": cp.action,
            "modified": modified_args is not None,
        })
        return {"step_id": cp.step_id, "action": cp.action, "args": args}

    def clear_checkpoints(self) -> None:
        """Reset the timeline (cancel/complete). Recovers the live state if mid-navigation."""
        if self.session:
            # If the user was mid-navigation, restore the live scene first.
            if self.session.preview_index is not None and self.session.live_sceneview_id:
                self._restore_to_view(None)
            for cp in self.session.checkpoints:
                self._delete_sceneview(getattr(cp, "sceneview_node_id", None))
            self._delete_sceneview(self.session.live_sceneview_id)
            self.session.live_sceneview_id = None
            self.session.checkpoints = []
            self.session.active_checkpoint_index = None
            self.session.preview_index = None
        self._pending_checkpoint = None
        self._delete_all_replay_sceneviews()

    def _step_meta(self, step_id: str) -> Dict[str, Any]:
        if not self.session or not step_id:
            return {}
        graph = get_workflow_graph(self.session.extension_name) or {}
        for step in graph.get("steps", []) or []:
            if step.get("step_id") == step_id:
                return step
        return {}

    @staticmethod
    def _node_class_from_step_meta(meta: Dict[str, Any]) -> str:
        """Node class for a node-selection choice taken from the step graph itself.

        The pipeline's UI->parameter binding inference only recognizes the
        classic ``qMRMLNodeComboBox`` + ``parameterNode.SetNodeReferenceID``
        pattern. Selectors using a ``qMRMLSubjectHierarchyComboBox`` or the
        ``parameterNodeWrapper`` / ``connectGui`` declarative style yield no
        binding, so ``parameter_bindings`` / ``choice_binding`` carry no node
        class and the panel would fall back to a free-text box. The LLM
        decomposition still tags the choice's node class on the step's
        ``node_roles`` / ``sub_operations``; surface that as a fallback so any
        node-selection step still offers a dropdown of matching scene nodes.
        Returns "" for non-node choices (e.g. a boolean checkbox).
        """
        if not isinstance(meta, dict):
            return ""
        # A segment-NAME selection (content combobox of a segmentation's segment
        # names) is NOT a node pick -- exclude it before the choice_input/node_roles
        # fallbacks, which would otherwise return its segmentation class and route
        # it to the scene-node tree.
        if WorkflowRuntime._is_segment_name_selection(meta):
            return ""
        # A numeric range adjustment is not a node pick.
        if WorkflowRuntime._is_range_selection(meta):
            return ""
        # A single-value slider adjustment is not a node pick either.
        if WorkflowRuntime._is_scalar_slider_selection(meta):
            return ""
        roles = meta.get("node_roles") or []
        for role in roles:
            if isinstance(role, dict) and role.get("role_kind") == "choice_input":
                nc = str(role.get("node_class") or "").strip()
                if nc and nc not in _NONSPECIFIC_NODE_CLASSES:
                    return nc
        # A node pick: explicit ``value_kind == "node"``, OR the recorded source
        # widget is a node-combo class (some regenerations leave value_kind empty
        # but still record the .ui ``widget_class`` + ``node_class`` -- e.g.
        # PelvicFracturePlanning's ``inputSelector`` qMRMLNodeComboBox). Mirrors
        # the node_tree entries of WidgetWorkflowMixin._WORKFLOW_WIDGET_FAMILIES;
        # the segments table is excluded (routed via _segment_selection_meta).
        node_selector_widgets = (
            "qMRMLNodeComboBox", "qMRMLSubjectHierarchyComboBox",
            "qMRMLSubjectHierarchyTreeView", "qMRMLCheckableNodeComboBox",
        )
        for so in meta.get("sub_operations") or []:
            if not isinstance(so, dict):
                continue
            vk = str(so.get("value_kind") or "").strip()
            wc = str(so.get("widget_class") or "").strip()
            if (vk in ("segment_visibility_selection", "segment_name_selection")
                    or wc == "qMRMLSegmentsTableView"):
                continue
            if vk == "node" or wc in node_selector_widgets:
                nc = str(so.get("node_class") or "").strip()
                if nc and nc not in _NONSPECIFIC_NODE_CLASSES:
                    return nc
        for role in roles:
            if isinstance(role, dict):
                nc = str(role.get("node_class") or "").strip()
                if nc and nc not in _NONSPECIFIC_NODE_CLASSES:
                    return nc
        # Last resort: no structural node class was captured (common for
        # python-built selectors with no ``.ui``). Infer it from the step's
        # natural-language labels. Mirrored in choice_helpers so the pick also
        # drives the extension's live selector.
        return WorkflowRuntime._node_class_from_choice_language(meta)

    @staticmethod
    def _node_class_from_choice_language(meta: Dict[str, Any]) -> str:
        """Language-only node-class fallback for a node-selection ``user_choice``
        with no structurally-captured class (see ``_classify_node_choice_language``
        and the module-level rationale). Reads the FAMILY noun only from the narrow
        "what is being selected" fields (ui_guidance object/choice/input labels,
        choice_info question, parameter name) and the select-verb/stopword gate from
        the broader description text. Excludes segment-name / range picks (they own
        their renderers) before classifying. Returns "" for non-node choices.

        Mirror of ``extension_cli_loader.choice_helpers._node_class_from_choice_language``.
        """
        if not isinstance(meta, dict):
            return ""
        if (WorkflowRuntime._is_segment_name_selection(meta)
                or WorkflowRuntime._is_range_selection(meta)):
            return ""
        guidance = meta.get("ui_guidance") if isinstance(meta.get("ui_guidance"), dict) else {}
        choice_info = meta.get("choice_info") if isinstance(meta.get("choice_info"), dict) else {}
        family_parts = [
            guidance.get("object_label"), guidance.get("choice_label"),
            guidance.get("input_label"), choice_info.get("question"),
            choice_info.get("parameter_name"),
        ]
        broad_parts = list(family_parts) + [
            meta.get("description"), guidance.get("instruction"), guidance.get("title"),
        ]
        # The parameter name names WHAT is selected (authoritative), so it is
        # scanned for a family noun before the purpose-laden question text.
        priority_parts = [choice_info.get("parameter_name")]
        for so in meta.get("sub_operations") or []:
            if not isinstance(so, dict):
                continue
            family_parts.extend([so.get("question"), so.get("parameter_name")])
            broad_parts.extend([so.get("question"), so.get("parameter_name"), so.get("description")])
            priority_parts.append(so.get("parameter_name"))
        family_text = " ".join(str(p) for p in family_parts if p)
        broad_text = " ".join(str(p) for p in broad_parts if p)
        priority_text = " ".join(str(p) for p in priority_parts if p)
        return _classify_node_choice_language(family_text, broad_text, priority_text)

    @staticmethod
    def _source_widget_class(meta: Dict[str, Any]) -> str:
        """Qt class of the selection widget the *original* extension uses for this
        step, recorded by the CLI pipeline from the extension's ``.ui`` inventory
        (``stage4_decomposition._record_source_widget`` →
        ``sub_op["widget_class"]``).

        Surfaced so the runtime can reproduce the original widget instead of
        inferring one from ``node_class`` / ``value_kind`` heuristics: the captured
        class is authoritative for picking the render family (e.g. a
        ``qMRMLSegmentsTableView`` step must render the segments table, never the
        generic node tree). Scans all ``sub_operations`` (each step has one today,
        but be robust) and falls back to the binding's widget class so a
        node-combo selector is still recognized. Returns "" when none is recorded
        — the runtime then keeps its existing heuristic. Generic: no
        extension/step-specific strings.
        """
        if not isinstance(meta, dict):
            return ""
        for so in meta.get("sub_operations") or []:
            if not isinstance(so, dict):
                continue
            wc = str(so.get("widget_class") or "").strip()
            if wc:
                return wc
            binding = so.get("ui_parameter_binding")
            if isinstance(binding, dict):
                wc = str(binding.get("widget_class") or "").strip()
                if wc:
                    return wc
        return ""

    @staticmethod
    def _keywords_from_widget_name(*texts: str) -> List[str]:
        """Distinctive lowercase tokens from a widget/field name for best-match
        node scoring. Splits camelCase + snake_case + whitespace, drops a generic
        UI/segmentation stop-word set, keeps tokens >= 3 chars (deduped, ordered).

        Lets a segments-table step default to the right segmentation when the
        extension's parameter binding carries no keywords (e.g. a
        parameterNodeWrapper extension): e.g. ``fractureSegmentsTable`` ->
        ``["fracture"]`` matches "Fracture Segmentation" but not "Pelvis
        Segmentation". Generic: no extension/step-specific strings.
        """
        stop = {
            "segments", "segment", "seg", "table", "view", "selector", "widget",
            "combo", "combobox", "node", "nodes", "mrml", "qmrml", "list", "tree",
            "box", "panel", "frame", "output", "input", "the", "for",
        }
        tokens: List[str] = []
        seen = set()
        for text in texts:
            spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", str(text or ""))
            for tok in re.split(r"[^A-Za-z0-9]+", spaced):
                t = tok.strip().lower()
                if len(t) >= 3 and t not in stop and t not in seen:
                    seen.add(t)
                    tokens.append(t)
        return tokens

    @staticmethod
    def _segment_selection_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
        """Segment-selection metadata for a choice step backed by a
        ``qMRMLSegmentsTableView`` (the user unticks segments/fragments on a
        segmentation node rather than picking a whole node).

        Recognized when a sub-operation declares ``widget_class ==
        'qMRMLSegmentsTableView'`` or ``value_kind`` in the segment-selection set.
        Returns ``{"segmentation_node_class": <class>}`` (defaulting to
        ``vtkMRMLSegmentationNode``) for such steps, else ``{}``. Kept distinct
        from ``_node_class_from_step_meta`` (whose ``value_kind == 'node'`` path
        would otherwise route this to the generic node tree + node-materialization
        code).
        """
        if not isinstance(meta, dict):
            return {}
        for so in meta.get("sub_operations") or []:
            if not isinstance(so, dict):
                continue
            wc = str(so.get("widget_class") or "").strip()
            vk = str(so.get("value_kind") or "").strip()
            if wc == "qMRMLSegmentsTableView" or vk in ("segment_visibility_selection", "segment_selection"):
                nc = str(so.get("node_class") or "").strip() or "vtkMRMLSegmentationNode"
                # target_param: the parameterNodeWrapper field the source binds the
                # table to (captured by the pipeline, Layer 2) — lets the runtime
                # resolve the exact segmentation. keywords: a name-based fallback
                # so the right segmentation is preferred even without a target.
                target_param = str(so.get("segmentation_target_param") or "").strip()
                keywords = WorkflowRuntime._keywords_from_widget_name(
                    so.get("widget_name") or "", target_param
                )
                return {
                    "segmentation_node_class": nc,
                    "keywords": keywords,
                    "target_param": target_param,
                }
        return {}

    @staticmethod
    def _has_real_choices(choices) -> bool:
        """True when a step carries genuine literal choices (a static enum), vs an
        empty list or a placeholder ``{"value": None}`` header the LLM sometimes
        co-emits for a dynamically-populated content combobox. Lets the content-
        combobox detection ignore such placeholders."""
        for c in (choices or []):
            if isinstance(c, dict):
                if c.get("value") not in (None, ""):
                    return True
            elif c not in (None, ""):
                return True
        return False

    @staticmethod
    def _is_segment_name_selection(meta: Dict[str, Any]) -> bool:
        """True when a user_choice step reproduces a CONTENT combobox whose items
        are the segment NAMES of a segmentation (a single-pick fragment/segment
        chooser) -- NOT a scene-node pick and NOT the multi-untick segments table.

        Dual signal so it fires on already-generated artifacts (no regen):
        ``value_kind == "segment_name_selection"`` (self-describing, set by the
        capture stage), OR a plain combobox source widget (``QComboBox`` /
        ``ctkComboBox`` -- never a qMRML* node selector) whose step carries a
        ``choice_input`` node-role of class ``vtkMRMLSegmentationNode`` (the LLM's
        segmentation-related signal). Kept distinct from _is_node_selection_step /
        _segment_selection_meta so it renders a segment-name picker, not a node
        tree or a segments table. Generic: no extension/step-specific strings.
        """
        if not isinstance(meta, dict):
            return False
        sub_ops = [s for s in (meta.get("sub_operations") or []) if isinstance(s, dict)]
        for so in sub_ops:
            if str(so.get("value_kind") or "").strip() == "segment_name_selection":
                return True
        combo = any(
            str(so.get("widget_class") or "").strip() in ("QComboBox", "ctkComboBox")
            for so in sub_ops
        )
        if not combo:
            return False
        roles = list(meta.get("node_roles") or [])
        for so in sub_ops:
            roles.extend(so.get("node_roles") or [])
        for role in roles:
            if (isinstance(role, dict)
                    and role.get("role_kind") == "choice_input"
                    and str(role.get("node_class") or "").strip() == "vtkMRMLSegmentationNode"):
                return True
        # Deterministic fallback (the LLM's segmentation role is non-deterministic
        # across regens): a NAMED content combobox -- a plain combobox with no
        # static/literal choices whose name yields a distinctive token -- is
        # populated dynamically at runtime (e.g. a "Fragment" selector), unlike a
        # static enum combobox (which carries its items as choices). Surface it so
        # the renderer can resolve the segmentation by those name keywords; it falls
        # back to free-text when none matches, so a non-segment content combobox
        # degrades safely rather than guessing.
        for so in sub_ops:
            if (str(so.get("widget_class") or "").strip() in ("QComboBox", "ctkComboBox")
                    and not WorkflowRuntime._has_real_choices(so.get("choices"))
                    and WorkflowRuntime._keywords_from_widget_name(so.get("widget_name") or "")):
                return True
        return False

    @staticmethod
    def _segment_name_selection_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
        """Resolution metadata for a single-pick segment-NAME chooser (see
        _is_segment_name_selection): {segmentation_node_class, keywords,
        target_param} for resolving WHICH segmentation supplies the names at render
        time -- reusing the segments-table resolution (target_param / widget-name
        keywords). Returns {} when the step is not a segment-name selection.
        """
        if not isinstance(meta, dict) or not WorkflowRuntime._is_segment_name_selection(meta):
            return {}
        widget_name = ""
        target_param = ""
        node_class = "vtkMRMLSegmentationNode"
        for so in meta.get("sub_operations") or []:
            if not isinstance(so, dict):
                continue
            if not widget_name:
                widget_name = str(so.get("widget_name") or "").strip()
            if not target_param:
                target_param = str(so.get("segmentation_target_param") or "").strip()
            nc = str(so.get("node_class") or "").strip()
            if nc:
                node_class = nc
        return {
            "segmentation_node_class": node_class,
            "keywords": WorkflowRuntime._keywords_from_widget_name(widget_name, target_param),
            "target_param": target_param,
            # The extension's own source combobox (e.g. "fragmentSelector"); the
            # picker drives it live so the connected handler fires on selection.
            "source_widget": widget_name,
        }

    @staticmethod
    def _is_native_widget(meta: Dict[str, Any]) -> bool:
        """True when the step defers to the extension's OWN selection widget (the
        cookbook said "following the original selection widget"). Mirrors the
        native_widget flag the capture stage records on the sub-op."""
        if not isinstance(meta, dict):
            return False
        for so in meta.get("sub_operations") or []:
            if isinstance(so, dict) and so.get("native_widget"):
                return True
        return False

    @staticmethod
    def _multi_choice_items(meta: Dict[str, Any]) -> List[Dict[str, Any]]:
        """The step's multi-selection items ([] for a single-choice step).

        A cookbook step may drive SEVERAL selectors at once ("Choose the 'A'.
        Choose the 'B'. ..."); the pipeline records one choice item per selector in
        ``choice_info_list``. The panel renders them as ONE form with a single
        Confirm, and the commit is a {parameter_name: value} dict.
        """
        if not isinstance(meta, dict):
            return []
        items = meta.get("choice_info_list")
        if not isinstance(items, list) or len(items) < 2:
            return []
        return [i for i in items if isinstance(i, dict) and i.get("parameter_name")]

    def _expected_interaction_count(self, meta: Dict[str, Any]) -> int:
        """How many points the current interaction step expects, resolved from its
        structural count rule -- a literal, or multiplier x the value of an EARLIER
        recorded choice. 0 = no rule -> no progress display, no Done gate (exactly
        today's behavior). Fail-open: an unreadable rule resolves to 0, never
        blocking the workflow."""
        if not isinstance(meta, dict):
            return 0
        for so in meta.get("sub_operations") or []:
            if not isinstance(so, dict):
                continue
            rule = so.get("expected_count_rule")
            if not isinstance(rule, dict):
                continue
            try:
                if rule.get("count"):
                    return max(0, int(rule["count"]))
                multiplier = int(rule.get("multiplier") or 0)
                param = str(rule.get("param") or "")
                if multiplier > 0 and param and self.session:
                    choices = get_workflow_choices(self.session.extension_name) or {}
                    return max(0, multiplier * int(str(choices.get(param))))
            except (TypeError, ValueError):
                return 0
        return 0

    def _live_review_table(self) -> Dict[str, Any]:
        """Live results-table snapshot for a review step (delegates to the loader's
        reader, which resolves the fullest QTableWidget in the extension's own UI,
        then the newest table node). Empty dict when nothing resolves -- the panel
        falls back to instructions + Confirm."""
        try:
            from .extension_cli_loader import _snapshot_review_table
            module_name = ""
            try:
                ext_data = get_validated_extensions().get(self.session.extension_name) or {}
                metadata = ext_data.get("workflow_metadata", {}) or {}
                module_name = str(metadata.get("extension_module_name") or "").strip()
            except Exception:
                module_name = ""
            return _snapshot_review_table(module_name or self.session.extension_name) or {}
        except Exception:
            return {}

    @staticmethod
    def _segment_ref_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
        """Resolution metadata for a step whose source selector picks a SEGMENT inside
        a segmentation (rather than a whole node), else {}.

        Recognized by the ``selection_granularity == "segment"`` axis the capture stage
        reads off the extension's own selection-resolution code -- NOT by the Qt class
        (one qMRMLSubjectHierarchyTreeView serves both a node pick and a segment pick in
        the same extension) and NOT by step text (a cookbook may call a segment pick a
        "segmentation node"). Absent => a node pick, i.e. today's behavior.

        Kept distinct from _segment_name_selection_meta (a content COMBOBOX of segment
        names, where the segmentation is resolved for the user) and from
        _segment_selection_meta (the multi-untick segments TABLE): here the user picks
        the segmentation AND the segment together, by clicking a segment row in the tree.
        Deliberately does NOT suppress node_class -- the reproduced widget IS the node
        tree, filtered to segmentations; only which row is acceptable, and what gets
        committed, differ.
        """
        if not isinstance(meta, dict):
            return {}
        for so in meta.get("sub_operations") or []:
            if not isinstance(so, dict):
                continue
            if str(so.get("selection_granularity") or "").strip() != "segment":
                continue
            # The tree's node class arrives via the normal node_class path (the capture
            # stage writes the wrapper field's annotation onto the sub-op), so this
            # carries only what is specific to the segment pick.
            return {
                # The wrapper field holding the segment id (e.g. "referenceSegmentId").
                "segment_id_param": str(so.get("segment_id_param") or "").strip(),
                # The extension's own selector; the picker drives it live to the chosen
                # SEGMENT row so the source's connected handler writes both halves.
                "source_widget": str(so.get("widget_name") or "").strip(),
            }
        return {}

    # Qt classes of a double-handled numeric range control (min/max slider).
    # Shared by _is_range_selection / _range_selection_meta and the node-selection
    # exclusions so a range step never routes to the node tree / segments table.
    _RANGE_WIDGET_CLASSES = (
        "ctkRangeWidget", "qMRMLRangeWidget", "ctkDoubleRangeSlider", "ctkRangeSlider",
    )

    # Qt classes of a SINGLE-handle numeric control (one scalar value, not a
    # min/max band). Shared by _is_scalar_slider_selection and used to make
    # _is_range_selection source-widget-authoritative: such a control is a scalar
    # chooser even when the LLM tagged value_kind == "range".
    _SINGLE_SLIDER_WIDGET_CLASSES = (
        "ctkSliderWidget", "qMRMLSliderWidget", "ctkDoubleSlider",
        "ctkSliderSpinBoxWidget", "QSlider", "QDoubleSpinBox", "QSpinBox",
    )

    @staticmethod
    def _is_range_selection(meta: Dict[str, Any]) -> bool:
        """True when a user_choice step is a continuous numeric RANGE adjustment
        (a double-handled min/max slider), e.g. a Segment Editor Threshold range.

        Dual signal so it fires on already-generated artifacts (no regen):
        ``value_kind == "range"`` (self-describing, emitted by the LLM choice
        decomposition for any "adjust a range" step), OR a range widget source
        class recorded from the extension's ``.ui`` (``ctkRangeWidget`` etc.).
        Kept distinct from the node / segment families so it renders a range
        slider, not a node tree, segments table, or literal button. Generic: no
        extension/step-specific strings.

        SOURCE-WIDGET-AUTHORITATIVE: a recorded SINGLE-handle slider class
        (``ctkSliderWidget`` etc.) is a scalar chooser, never a min/max band --
        even if the LLM tagged ``value_kind == "range"`` from loose "range bar"
        cookbook wording. Such a step routes to the scalar-slider family, so it
        is NOT a range here.
        """
        if not isinstance(meta, dict):
            return False
        sub_ops = [s for s in (meta.get("sub_operations") or []) if isinstance(s, dict)]
        for so in sub_ops:
            if str(so.get("widget_class") or "").strip() in WorkflowRuntime._SINGLE_SLIDER_WIDGET_CLASSES:
                return False
        for so in sub_ops:
            if str(so.get("value_kind") or "").strip() == "range":
                return True
            if str(so.get("widget_class") or "").strip() in WorkflowRuntime._RANGE_WIDGET_CLASSES:
                return True
        return False

    @staticmethod
    def _is_scalar_slider_selection(meta: Dict[str, Any]) -> bool:
        """True when a user_choice step adjusts a SINGLE numeric value on a
        single-handle slider (e.g. an extension's ``ctkSliderWidget`` "Crop
        radius (mm)"), as opposed to a double-handled min/max range.

        Source-widget-authoritative: the recorded ``.ui`` widget class
        (``ctkSliderWidget`` etc.) is the primary signal, plus a self-describing
        ``value_kind`` (``scalar``/``number``) for regenerated artifacts. Kept
        distinct from the range family so it renders one handle, not two.
        Generic: keyed on the Qt widget class, no extension/step-specific names.
        """
        if not isinstance(meta, dict):
            return False
        sub_ops = [s for s in (meta.get("sub_operations") or []) if isinstance(s, dict)]
        for so in sub_ops:
            if str(so.get("widget_class") or "").strip() in WorkflowRuntime._SINGLE_SLIDER_WIDGET_CLASSES:
                return True
            if str(so.get("value_kind") or "").strip() in ("scalar", "scalar_slider", "number"):
                return True
        return False

    @staticmethod
    def _scalar_slider_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
        """Resolution metadata for a single-value slider chooser (see
        _is_scalar_slider_selection): ``{param, min, max, step, default,
        source_widget}``. ``min``/``max``/``step``/``default`` come from the
        extension's captured ``.ui`` numeric properties (minimum/maximum/
        singleStep/value) when present; otherwise ``None`` and the renderer seeds
        from the extension's live slider widget. Returns ``{}`` when the step is
        not a scalar-slider selection.
        """
        if not isinstance(meta, dict) or not WorkflowRuntime._is_scalar_slider_selection(meta):
            return {}
        param = ""
        widget_name = ""
        smin = smax = sstep = sdefault = None
        for so in meta.get("sub_operations") or []:
            if not isinstance(so, dict):
                continue
            if not param:
                param = str(so.get("parameter_name") or "").strip()
            if not widget_name:
                widget_name = str(so.get("widget_name") or "").strip()
            if smin is None:
                smin = so.get("range_min")
            if smax is None:
                smax = so.get("range_max")
            if sstep is None:
                sstep = so.get("range_step")
            if sdefault is None:
                sdefault = so.get("range_default")
        return {
            "param": param,
            "min": smin,
            "max": smax,
            "step": sstep,
            "default": sdefault,
            "source_widget": widget_name,
        }

    @staticmethod
    def _range_selection_meta(meta: Dict[str, Any]) -> Dict[str, Any]:
        """Resolution metadata for a numeric range chooser (see _is_range_selection):
        ``{param, min, max, step, default, source_widget}``. ``min``/``max``/``step``
        come from the extension's captured ``.ui`` numeric properties when present
        (an extension's own range widget); otherwise they are ``None`` and the
        renderer derives limits at run time from the live target (e.g. the Segment
        Editor Threshold effect / source-volume scalar range). Returns ``{}`` when
        the step is not a range selection.
        """
        if not isinstance(meta, dict) or not WorkflowRuntime._is_range_selection(meta):
            return {}
        param = ""
        widget_name = ""
        rmin = rmax = rstep = rdefault = None
        for so in meta.get("sub_operations") or []:
            if not isinstance(so, dict):
                continue
            if not param:
                param = str(so.get("parameter_name") or "").strip()
            if not widget_name:
                widget_name = str(so.get("widget_name") or "").strip()
            if rmin is None:
                rmin = so.get("range_min")
            if rmax is None:
                rmax = so.get("range_max")
            if rstep is None:
                rstep = so.get("range_step")
            if rdefault is None:
                rdefault = so.get("range_default")
        return {
            "param": param,
            "min": rmin,
            "max": rmax,
            "step": rstep,
            "default": rdefault,
            "source_widget": widget_name,
        }

    @staticmethod
    def _is_node_selection_step(meta: Dict[str, Any]) -> bool:
        """True when a user_choice step's selection is an MRML node pick.

        A node pick must drive the scene node tree, never literal cookbook-label
        buttons. The authoritative signal is a user_choice sub-op with
        ``value_kind == "node"``; a ``choice_input`` node-role carrying a
        ``node_class`` is accepted as a fallback for older artifacts. Segment-
        visibility steps (``value_kind == "segment_visibility_selection"``) are
        routed separately and excluded. Returns False for boolean / enum /
        numeric choices (no node_class) so those keep their buttons.
        """
        if not isinstance(meta, dict):
            return False
        sub_ops = [s for s in (meta.get("sub_operations") or []) if isinstance(s, dict)]
        kinds = {str(s.get("value_kind") or "").strip() for s in sub_ops}
        if "segment_visibility_selection" in kinds:
            return False
        # A segment-NAME selection renders its own picker, never the node tree.
        if WorkflowRuntime._is_segment_name_selection(meta):
            return False
        # A numeric range adjustment renders its own slider, never the node tree.
        if WorkflowRuntime._is_range_selection(meta):
            return False
        # A single-value slider adjustment renders its own slider, never the node tree.
        if WorkflowRuntime._is_scalar_slider_selection(meta):
            return False
        if "node" in kinds:
            return True
        # A node-combo source widget with a node_class is a node pick too, even if
        # the regeneration left value_kind empty (mirrors _node_class_from_step_meta).
        node_selector_widgets = (
            "qMRMLNodeComboBox", "qMRMLSubjectHierarchyComboBox",
            "qMRMLSubjectHierarchyTreeView", "qMRMLCheckableNodeComboBox",
        )
        for s in sub_ops:
            if (str(s.get("widget_class") or "").strip() in node_selector_widgets
                    and str(s.get("node_class") or "").strip()):
                return True
        for role in meta.get("node_roles") or []:
            if (isinstance(role, dict)
                    and role.get("role_kind") == "choice_input"
                    and str(role.get("node_class") or "").strip()):
                return True
        return False

    def _node_binding_for_param(self, parameter_name: str) -> Dict[str, Any]:
        """Return the parameter binding ({node_class, keywords, ...}) from metadata.

        Node-selection steps bind a parameter (e.g. mandibularSegmentation) to a
        node class; that mapping lives in workflow_metadata.parameter_bindings.
        Used to offer a dropdown of matching scene nodes. Fail-soft to {}.
        """
        if not self.session or not parameter_name:
            return {}
        try:
            ext_data = get_validated_extensions().get(self.session.extension_name) or {}
            metadata = ext_data.get("workflow_metadata", {}) or {}
            bindings = metadata.get("parameter_bindings", {}) or {}
            return dict(bindings.get(parameter_name, {}) or {})
        except Exception:
            return {}

    def _step_instructions_for(self, step_id: str) -> Dict[str, Any]:
        """Return the clinically-informed {title, simple, detailed} for a step, or {}.

        Read live from the loaded step_instructions.json so manual edits take
        effect on the next render (live and replay) without restarting.
        """
        if not self.session or not step_id:
            return {}
        try:
            ext_data = get_validated_extensions().get(self.session.extension_name) or {}
            steps = (ext_data.get("step_instructions", {}) or {}).get("steps", {}) or {}
            return dict(steps.get(step_id, {}) or {})
        except Exception:
            return {}

    def _is_loop_count_source(self, step_id: str) -> bool:
        for block in self._repeat_blocks():
            controller = block.get("controller", {}) or {}
            if controller.get("kind") == "count" and controller.get("source_step") == step_id:
                return True
        return False

    def _interaction_summary(self, step_id: str) -> str:
        try:
            from .workflow_state import latest_interaction_node_for_step
            node = latest_interaction_node_for_step(step_id)
            if node is not None:
                try:
                    return f"Placed {node.GetName()}"
                except Exception:
                    return "Placed markup"
        except Exception:
            pass
        return "Interaction"

    @staticmethod
    def _checkpoint_summary(
        meta: Dict[str, Any],
        kind: str,
        value: Any,
        repeat: Optional[Dict[str, Any]],
    ) -> str:
        desc = str(meta.get("description") or meta.get("step_id") or "Step").strip()
        if kind in ("choice", "loop_count"):
            label = (meta.get("choice_info") or {}).get("parameter_name") or desc
            return f"{label}: {WorkflowRuntime._format_choice_summary(value)}"
        if kind == "loop_decision":
            return f"Loop decision: {value}"
        return desc

    @staticmethod
    def _format_choice_summary(value: Any) -> str:
        """Human-readable form of a recorded choice for the replay timeline. Compound
        values (a segment pick) would otherwise render as a raw dict. Shape-keyed, so
        every scalar choice is unaffected."""
        if (isinstance(value, dict) and value.get("node_id") and value.get("segment_id")):
            node = str(value.get("node_name") or "").strip()
            segment = str(value.get("segment_name") or "").strip() or str(value.get("segment_id"))
            return f"{node} / {segment}" if node else segment
        if isinstance(value, dict):
            # Multi-selection commit: one {param: value} pair per selector.
            return ", ".join(f"{k}={v}" for k, v in value.items())
        return str(value)

    @staticmethod
    def _scene_node_ids() -> set:
        ids = set()
        try:
            import slicer
            for i in range(slicer.mrmlScene.GetNumberOfNodes()):
                node = slicer.mrmlScene.GetNthNode(i)
                if node is None or not node.GetID():
                    continue
                if node.IsA("vtkMRMLSceneViewNode"):
                    continue
                ids.add(node.GetID())
        except Exception:
            pass
        return ids

    def _prune_to_node_ids(self, keep_ids) -> None:
        """Delete storable, non-singleton nodes not in ``keep_ids`` after a restore.

        Belt-and-braces for RestoreScene: it should remove nodes created after a
        snapshot, but interactively-created markup/display nodes can survive,
        which breaks generated templates that assume a clean node set on re-run
        (e.g. a step that does GetFirstNodeByClass and expects exactly one
        curve). This removes those leftovers while preserving infrastructure
        (singletons such as views/slices/selection, replay snapshots) and the
        baseline inputs (which are in keep_ids). Node IDs are preserved across
        StoreScene/RestoreScene, so a restored node keeps its original ID and
        stays in keep_ids; only genuinely newer nodes are dropped.
        """
        try:
            import slicer
        except Exception:
            return
        keep = set(keep_ids or [])
        try:
            doomed = []
            for i in range(slicer.mrmlScene.GetNumberOfNodes()):
                node = slicer.mrmlScene.GetNthNode(i)
                if node is None or not node.GetID():
                    continue
                if node.GetID() in keep:
                    continue
                if node.IsA("vtkMRMLSceneViewNode"):
                    continue
                if node.GetSingletonTag():
                    continue
                try:
                    if not node.GetSaveWithScene():
                        continue
                except Exception:
                    continue
                doomed.append(node)
            for node in doomed:
                try:
                    slicer.mrmlScene.RemoveNode(node)
                except Exception:
                    pass
            if doomed:
                logger.info(
                    "[Replay] Pruned %d stale node(s) after scene restore", len(doomed)
                )
        except Exception:
            logger.debug("Replay node prune failed", exc_info=True)

    def _capture_sceneview(self, step_id: str) -> Optional[str]:
        try:
            import slicer
        except Exception:
            return None
        try:
            ext = self.session.extension_name if self.session else "wf"
            name = f"_wfReplay_{ext}_{step_id}_{int(time.time() * 1000)}"
            sv = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSceneViewNode", name)
            if sv is None:
                return None
            sv.SetHideFromEditors(True)
            sv.SetAttribute("SlicerAIAgentReplay", "1")
            # Keep replay snapshots out of saved scenes / node selectors; they
            # are transient, in-memory, current-session only.
            try:
                sv.SetSaveWithScene(False)
            except Exception:
                pass
            with _silenced_vtk_output():
                sv.StoreScene()
            return sv.GetID()
        except Exception:
            logger.debug("Replay scene snapshot failed", exc_info=True)
            return None

    def _restore_sceneview(self, sceneview_node_id: Optional[str]) -> bool:
        if not sceneview_node_id:
            return False
        try:
            import slicer
        except Exception:
            return False
        try:
            sv = slicer.mrmlScene.GetNodeByID(sceneview_node_id)
            if sv is None:
                return False
            with _silenced_vtk_output():
                sv.RestoreScene()
            return True
        except Exception:
            logger.debug("Replay scene restore failed", exc_info=True)
            return False

    def _delete_sceneview(self, sceneview_node_id: Optional[str]) -> None:
        if not sceneview_node_id:
            return
        try:
            import slicer
            sv = slicer.mrmlScene.GetNodeByID(sceneview_node_id)
            if sv is not None:
                slicer.mrmlScene.RemoveNode(sv)
        except Exception:
            logger.debug("Replay scene snapshot delete failed", exc_info=True)

    @staticmethod
    def _delete_all_replay_sceneviews() -> None:
        try:
            import slicer
        except Exception:
            return
        try:
            collection = slicer.mrmlScene.GetNodesByClass("vtkMRMLSceneViewNode")
            if collection is None:
                return
            collection.UnRegister(None)
            doomed = []
            for i in range(collection.GetNumberOfItems()):
                node = collection.GetItemAsObject(i)
                if node is not None and node.GetAttribute("SlicerAIAgentReplay") == "1":
                    doomed.append(node)
            for node in doomed:
                slicer.mrmlScene.RemoveNode(node)
        except Exception:
            logger.debug("Replay scene snapshot bulk delete failed", exc_info=True)

    def _write_event(self, event: str, payload: Dict[str, Any]) -> None:
        if not self.log_dir or not self.session:
            return
        try:
            os.makedirs(self.log_dir, exist_ok=True)
            path = os.path.join(self.log_dir, "workflow_runtime.jsonl")
            entry = {
                "time": round(time.time(), 3),
                "event": event,
                "workflow_id": self.session.workflow_id,
                "extension_name": self.session.extension_name,
                "current_step": self.session.current_step,
                "status": self.session.status,
                "payload": payload,
            }
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
        except Exception:
            pass
