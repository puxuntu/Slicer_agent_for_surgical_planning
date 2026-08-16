"""What the step on screen will accept, as data a matcher can work on.

The panel decides which control to render by branching through
``_renderWorkflowChoices`` over a dozen flags of ``state_for_ui()``. A voice
layer has to reach the *same* conclusion or it will answer a question the user
is not being asked -- so the branch order here is a deliberate mirror of
``WidgetWorkflowMixin._renderWorkflowChoices`` (widget_workflow.py:584-651), and
the two must be changed together.

The result is a ``StepGrammar``: a flat, Qt-free, picklable description of every
utterance the step can legally consume. It carries no live VTK objects, which is
what lets the matcher run off the Qt main thread while the scene keeps changing
underneath it -- the node names and segment names are read ONCE, on the main
thread, by the caller and handed in.

Three things it deliberately preserves rather than normalising, because each
loses a fact the runtime needs:

* the choice value is whatever **the button would send**, which is not always
  what the artifact declares. ``_renderWorkflowChoices`` coerces a Yes/No LABEL
  to ``True``/``False`` regardless of the declared value (widget_workflow.py:
  682-688), so the panel state's ``"true"`` string and PedicleScrewPlanner
  ``cb_step_14``'s ``"done"`` both leave the panel as booleans. That coercion is
  reproduced here verbatim. Reading ``choices[i]["value"]`` straight out of the
  state instead would make voice and click disagree -- and on a repeat block the
  string never equals the boolean ``exit_value``, so the loop could not exit.
* the spoken alias set keeps the label AND its first clause AND the value word.
  6 of the 27 finite option lists in the shipped packages carry a parenthetical
  ("No (go to step 12)", "Yes (check box)"), which nobody says out loud.
* ``node_class`` arrives already normalised from the caller; grammar never
  filters the scene itself.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# Render families, mirroring _WORKFLOW_WIDGET_FAMILIES + the branch order in
# _renderWorkflowChoices. "none" means the step is on screen but has no control
# a voice command can drive (an automated step mid-dispatch, or a completed run).
FAMILY_NONE = "none"
FAMILY_CHOICES = "choices"
FAMILY_NODE = "node"
FAMILY_SEGMENTS_TABLE = "segments_table"
FAMILY_SEGMENT_NAME = "segment_name"
FAMILY_SEGMENT_REF = "segment_ref"
FAMILY_SCALAR = "scalar"
FAMILY_RANGE = "range"
FAMILY_MULTI = "multi"
FAMILY_REVIEW = "review"
FAMILY_NATIVE = "native"
FAMILY_TEXT = "text"
FAMILY_WAIT = "wait"

#: Families whose answer is a value the user speaks.
VALUE_FAMILIES = frozenset({
    FAMILY_CHOICES, FAMILY_NODE, FAMILY_SEGMENT_NAME, FAMILY_SEGMENT_REF,
    FAMILY_SCALAR, FAMILY_RANGE, FAMILY_MULTI, FAMILY_TEXT,
})


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _coerce_choice_value(label: str, value: Any) -> Any:
    """Reproduce the render loop's label->value coercion, verbatim in effect.

    widget_workflow.py:682-688. A Yes/No decision carries its polarity in the
    LABEL while the generator attaches an inconsistent value (null, or an
    arbitrary string). The button sends the coerced bool; the panel state keeps
    the raw string. Sending the raw string makes a repeat block loop forever,
    because it never equals the boolean ``exit_value``.
    """
    lowered = _clean(label).lower()
    if lowered in ("yes", "true", "y"):
        return True
    if lowered in ("no", "false", "n"):
        return False
    if value is None:
        return label
    return value


class StepGrammar(object):
    """Everything the step on screen will accept, with nothing live in it."""

    __slots__ = (
        "active", "workflow_active", "workflow_done", "step_id", "family",
        "workflow_title", "status", "step_index", "total_steps",
        "description", "instructions", "instructions_detailed", "notice",
        "can_done", "can_skip", "done_label", "primary_label",
        "choice_label", "input_label", "object_label", "parameter_name",
        "choices", "nodes", "segment_names", "segments", "multi_items",
        "scalar", "range", "default_value", "node_class",
        "replay_previewing", "can_back", "can_forward", "can_replay",
        "auto_select_pending", "extension_name",
    )

    def __init__(self, **kwargs):
        for name in self.__slots__:
            setattr(self, name, kwargs.get(name))
        self.choices = self.choices or []
        self.nodes = self.nodes or []
        self.segment_names = self.segment_names or []
        self.segments = self.segments or []
        self.multi_items = self.multi_items or []
        self.scalar = self.scalar or {}
        self.range = self.range or {}

    # -- queries the matcher and the announcer both need -------------------

    def expects_value(self) -> bool:
        return self.family in VALUE_FAMILIES

    def is_waiting_for_user(self) -> bool:
        """True when the panel is parked on this step waiting for a person.

        This -- not the operation type -- is what decides whether the step is
        worth speaking aloud. An ``extension_op`` is dispatched and gone before
        a sentence could finish.
        """
        if not self.workflow_active or self.workflow_done:
            return False
        return bool(self.can_done or self.can_skip or self.expects_value()
                    or self.family in (FAMILY_REVIEW, FAMILY_NATIVE,
                                       FAMILY_SEGMENTS_TABLE, FAMILY_WAIT))

    def option_labels(self) -> List[str]:
        """Human-facing option list, for the spoken prompt and the fallback."""
        if self.family == FAMILY_CHOICES:
            return [c.get("label", "") for c in self.choices]
        if self.family == FAMILY_NODE:
            return [n.get("name", "") for n in self.nodes]
        if self.family in (FAMILY_SEGMENT_NAME, FAMILY_SEGMENT_REF):
            return list(self.segment_names)
        if self.family == FAMILY_SEGMENTS_TABLE:
            return [s.get("name", "") for s in self.segments]
        if self.family == FAMILY_MULTI:
            out = []
            for item in self.multi_items:
                out.append("%s: %s" % (item.get("label") or item.get("param"),
                                       ", ".join(item.get("options") or [])))
            return out
        return []

    def to_dict(self) -> Dict[str, Any]:
        """Compact form handed to the LLM fallback (see commands.py).

        Deliberately omits everything the model cannot act on -- no code, no
        template names, no step metadata -- so the fallback call stays small and
        cannot be talked into inventing an action outside the allow-list.
        """
        payload = {
            "step_id": self.step_id,
            "control": self.family,
            "question": self.description,
            "instruction": self.instructions,
            "can_done": bool(self.can_done),
            "can_skip": bool(self.can_skip),
        }
        if self.family == FAMILY_CHOICES:
            payload["options"] = [
                {"index": i, "label": c.get("label", "")}
                for i, c in enumerate(self.choices)
            ]
        elif self.family == FAMILY_NODE:
            payload["options"] = [
                {"index": i, "label": n.get("name", "")}
                for i, n in enumerate(self.nodes)
            ]
            payload["node_class"] = self.node_class
        elif self.family in (FAMILY_SEGMENT_NAME, FAMILY_SEGMENT_REF):
            payload["options"] = [
                {"index": i, "label": name}
                for i, name in enumerate(self.segment_names)
            ]
        elif self.family == FAMILY_SEGMENTS_TABLE:
            payload["segments"] = [
                {"index": i, "label": s.get("name", ""),
                 "visible": bool(s.get("visible"))}
                for i, s in enumerate(self.segments)
            ]
        elif self.family == FAMILY_SCALAR:
            payload["number"] = {
                "label": self.choice_label or self.parameter_name,
                "min": self.scalar.get("min"),
                "max": self.scalar.get("max"),
                "default": self.scalar.get("default"),
            }
        elif self.family == FAMILY_RANGE:
            payload["range"] = {
                "label": self.choice_label or self.parameter_name,
                "min": self.range.get("min"),
                "max": self.range.get("max"),
                "current": [self.range.get("current_min"),
                            self.range.get("current_max")],
            }
        elif self.family == FAMILY_MULTI:
            payload["selectors"] = [
                {"param": item.get("param"),
                 "label": item.get("label"),
                 "options": list(item.get("options") or [])}
                for item in self.multi_items
            ]
        elif self.family == FAMILY_TEXT:
            payload["free_text_label"] = self.input_label or self.choice_label
        return payload


def _family_for_state(state: Dict[str, Any]) -> str:
    """Mirror of _renderWorkflowChoices' branch order (widget_workflow.py:584).

    Order matters and is not alphabetical: a segments-table step also carries a
    ``node_class`` (its segmentation), and a range step also carries a
    ``parameter_name``. Taking the branches in the panel's order is the only way
    to land on the control the user is actually looking at.
    """
    if state.get("native_widget"):
        return FAMILY_NATIVE
    if state.get("review_selection"):
        return FAMILY_REVIEW
    if state.get("multi_choice"):
        return FAMILY_MULTI
    if state.get("segment_selection"):
        return FAMILY_SEGMENTS_TABLE
    if state.get("segment_name_selection"):
        return FAMILY_SEGMENT_NAME
    if state.get("segment_ref_selection"):
        return FAMILY_SEGMENT_REF
    if state.get("scalar_selection"):
        return FAMILY_SCALAR
    if state.get("range_selection"):
        return FAMILY_RANGE
    if state.get("choices"):
        return FAMILY_CHOICES
    if state.get("node_class"):
        return FAMILY_NODE
    if state.get("needs_choice_input"):
        return FAMILY_TEXT
    if state.get("can_done"):
        return FAMILY_WAIT
    return FAMILY_NONE


def build_step_grammar(state: Optional[Dict[str, Any]],
                       nodes: Optional[List[Dict[str, Any]]] = None,
                       segment_names: Optional[List[str]] = None,
                       segments: Optional[List[Dict[str, Any]]] = None,
                       multi_items: Optional[List[Dict[str, Any]]] = None,
                       scalar_live: Optional[Dict[str, Any]] = None,
                       range_live: Optional[Dict[str, Any]] = None,
                       notice: str = "",
                       auto_select_pending: bool = False) -> StepGrammar:
    """Snapshot the panel state as a voice grammar.

    ``nodes`` / ``segment_names`` / ``segments`` / ``multi_items`` come from the
    caller because they are reads of the live MRML scene and of live Qt widgets,
    both of which are main-thread-only. ``scalar_live`` / ``range_live`` carry
    the bounds the renderer derived from the extension's own widget -- the
    artifacts almost never declare them (only ZygomaticImplantPlanner
    ``cb_step_13`` ships real min/max), so without this the spoken prompt could
    not say what range is legal.
    """
    state = dict(state or {})
    family = _family_for_state(state)

    choices = []
    for choice in (state.get("choices") or []):
        label = _clean(choice.get("label") or choice.get("value") or "Choice")
        value = _coerce_choice_value(label, choice.get("value", label))
        overrides = state.get("choice_label_overrides") or {}
        display = _clean(overrides.get(str(value)) or label)
        choices.append({"label": display, "raw_label": label, "value": value})

    scalar = {
        "param": state.get("scalar_param") or state.get("parameter_name"),
        "min": state.get("scalar_min"),
        "max": state.get("scalar_max"),
        "step": state.get("scalar_step"),
        "default": state.get("scalar_default"),
    }
    scalar.update({k: v for k, v in (scalar_live or {}).items() if v is not None})

    band = {
        "param": state.get("range_param") or state.get("parameter_name"),
        "min": state.get("range_min"),
        "max": state.get("range_max"),
        "step": state.get("range_step"),
        "default": state.get("range_default"),
    }
    band.update({k: v for k, v in (range_live or {}).items() if v is not None})

    return StepGrammar(
        active=bool(state.get("active")),
        workflow_active=bool(state.get("active")) and not state.get("workflow_done"),
        workflow_done=bool(state.get("workflow_done")),
        extension_name=_clean(state.get("extension_name")),
        step_id=_clean(state.get("current_step")),
        family=family,
        workflow_title=_clean(state.get("workflow_title")),
        status=_clean(state.get("status")),
        step_index=state.get("current_index"),
        total_steps=state.get("total_steps"),
        description=_clean(state.get("description")),
        instructions=_clean(state.get("instructions")),
        instructions_detailed=_clean(state.get("instructions_detailed")),
        notice=_clean(notice),
        can_done=bool(state.get("can_done")),
        can_skip=bool(state.get("can_skip")),
        done_label=_clean(state.get("done_label")) or "Done",
        primary_label=_clean(state.get("primary_label")),
        choice_label=_clean(state.get("choice_label")),
        input_label=_clean(state.get("input_label")),
        object_label=_clean(state.get("object_label")),
        parameter_name=_clean(state.get("parameter_name")),
        choices=choices,
        nodes=list(nodes or []),
        segment_names=[_clean(n) for n in (segment_names or []) if _clean(n)],
        segments=list(segments or []),
        multi_items=list(multi_items or []),
        scalar=scalar,
        range=band,
        default_value=state.get("default_value"),
        node_class=_clean(state.get("node_class")),
        replay_previewing=bool(state.get("replay_previewing")),
        can_back=bool(state.get("replay_can_back")),
        can_forward=bool(state.get("replay_can_forward")),
        can_replay=bool(state.get("can_replay")),
        auto_select_pending=bool(auto_select_pending),
    )


def spoken_prompt(grammar: StepGrammar, include_detail: bool = False,
                  max_options: int = 8) -> str:
    """The sentence(s) read aloud when a step opens.

    ``description`` first because on a step with enumerated choices the runtime
    has already replaced the generated topic title with the step's own QUESTION
    (WorkflowRuntime.py:626-635) -- so it is the thing to ask before listing the
    options. Then the terse clinical line (``instructions``), never the detailed
    one: ``detailed`` runs to 600 characters and is what the panel shows on
    screen, which is exactly the length that is unbearable spoken. "Explain"
    fetches it on demand.
    """
    parts = []
    if grammar.description:
        parts.append(grammar.description)
    if include_detail and grammar.instructions_detailed:
        parts.append(grammar.instructions_detailed)
    elif grammar.instructions and grammar.instructions != grammar.description:
        parts.append(grammar.instructions)

    options = grammar.option_labels()
    if grammar.family == FAMILY_CHOICES and options:
        parts.append("Say " + _spoken_option_list(options, max_options) + ".")
    elif grammar.family == FAMILY_NODE:
        if not options:
            parts.append("No matching node is in the scene yet.")
        elif len(options) == 1:
            parts.append("The only candidate is %s." % options[0])
        else:
            parts.append("Choose " + _spoken_option_list(options, max_options) + ".")
    elif grammar.family in (FAMILY_SEGMENT_NAME, FAMILY_SEGMENT_REF) and options:
        parts.append("Choose " + _spoken_option_list(options, max_options) + ".")
    elif grammar.family == FAMILY_SCALAR:
        parts.append(_number_prompt(grammar, "Say a value"))
    elif grammar.family == FAMILY_RANGE:
        parts.append(_number_prompt(grammar, "Say a range, for example three hundred to three thousand"))
    elif grammar.family == FAMILY_MULTI:
        for item in grammar.multi_items:
            label = item.get("label") or item.get("param")
            opts = item.get("options") or []
            parts.append("%s: %s." % (label, _spoken_option_list(opts, max_options)))
    elif grammar.family == FAMILY_TEXT:
        label = grammar.input_label or grammar.choice_label or "a value"
        parts.append('Say "set" followed by %s.' % label)
    elif grammar.family in (FAMILY_WAIT, FAMILY_REVIEW, FAMILY_NATIVE,
                            FAMILY_SEGMENTS_TABLE):
        parts.append('Say "done" when you have finished.')

    if grammar.notice:
        parts.append(grammar.notice)
    return " ".join(p for p in parts if p)


def _number_prompt(grammar: StepGrammar, fallback: str) -> str:
    source = grammar.scalar if grammar.family == FAMILY_SCALAR else grammar.range
    low, high = source.get("min"), source.get("max")
    if low is None or high is None:
        return fallback + "."
    return "%s between %s and %s." % (fallback, _tidy_number(low), _tidy_number(high))


def _tidy_number(value: Any) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return ("%.2f" % number).rstrip("0").rstrip(".")


def _spoken_option_list(options: List[str], limit: int) -> str:
    """Join options the way a person would say them, and admit truncation.

    PedicleScrewPlanner ``cb_step_4`` offers 25 vertebral levels. Reading all of
    them takes half a minute, so the list is cut -- but it says so, because a
    silently truncated list would make the user believe the option they wanted
    is not on offer.
    """
    cleaned = [str(o).strip() for o in options if str(o).strip()]
    if not cleaned:
        return "nothing"
    shown = cleaned[:limit]
    tail = len(cleaned) - len(shown)
    joined = ", ".join(shown[:-1]) + (", or " if len(shown) > 1 else "") + shown[-1]
    if tail > 0:
        joined += ", or any of %d more" % tail
    return joined
