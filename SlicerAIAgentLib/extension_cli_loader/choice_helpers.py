from __future__ import annotations

from .cache import *
from .templates import _workflow_choices, _workflow_repeat_state
from .workflow_state import _find_next_step_local


# ``{vol_lookup}`` is a structural placeholder some generated templates emit (see
# extension_cli_analyzer/template_generation.py) to stand in for "resolve the
# workflow's input scalar volume into ``inputVolume``". Generation-side validation
# expands it (live_revision._live_fill_template) and notes it "mirrors the
# generated runtime fill" -- this is that runtime fill, which the per-step path
# otherwise lacked. Generic snippet (no extension/param-specific names): reuse a
# volume an earlier step already resolved (a choice step sets a bare
# ``inputVolume = _chosen_node``), else the first scalar volume in the scene.
# Placed at column 0 (every generator emits the placeholder at top level). Must be
# CodeValidator-safe: globals()/locals()/vars() are BLOCKED, so resolve via a bare
# name reference + try/except NameError and slicer.mrmlScene.GetNodesByClass (the
# same idiom _build_node_choice_materialization_code already uses), never globals().
_VOL_LOOKUP_SNIPPET = (
    "try:\n"
    "    inputVolume  # reuse a volume an earlier step already resolved\n"
    "except NameError:\n"
    "    inputVolume = None\n"
    "if inputVolume is None:\n"
    "    _vn = slicer.mrmlScene.GetNodesByClass('vtkMRMLScalarVolumeNode')\n"
    "    for _i in range(_vn.GetNumberOfItems()):\n"
    "        _c = _vn.GetItemAsObject(_i)\n"
    "        if _c is not None:\n"
    "            inputVolume = _c\n"
    "            break"
)


# Qt classes of a double-handled numeric range control (mirrors
# WorkflowRuntime._RANGE_WIDGET_CLASSES).
_RANGE_WIDGET_CLASSES = (
    "ctkRangeWidget", "qMRMLRangeWidget", "ctkDoubleRangeSlider", "ctkRangeSlider",
)


def _is_range_value(value) -> bool:
    """True for a 2-element numeric [min, max] (not a bool pair)."""
    return (
        isinstance(value, (list, tuple))
        and len(value) == 2
        and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in value)
    )


def _is_segment_ref_value(value) -> bool:
    """True for a segment pick: the ``{node_id, segment_id, ...}`` pair committed by
    the node-tree picker for a step whose source selector selects a SEGMENT inside a
    segmentation. A dict is self-describing (it cannot collide with the list-shaped
    range value) and JSON-round-trips through checkpoints unchanged."""
    return (
        isinstance(value, dict)
        and bool(value.get("node_id"))
        and bool(value.get("segment_id"))
    )


def _segment_ref_stem(key: str) -> str:
    """Map a segment choice's parameter_name to the stem an independently-grounded
    template is likely to use: camelCase->snake, then drop a trailing
    'segment_id'/'segment'/'segmentation' segment. E.g. ``referenceSegmentId`` ->
    ``reference``. Same convention as _range_stem; generic, no extension-specific
    strings."""
    src = str(key or "")
    out = []
    for i, ch in enumerate(src):
        if ch.isupper() and i > 0 and (src[i - 1].islower() or src[i - 1].isdigit()):
            out.append("_")
        out.append(ch.lower())
    s = "".join(out)
    for suffix in ("_segment_id", "_segmentid", "_segmentation", "_segment"):
        if s.endswith(suffix):
            s = s[: -len(suffix)]
            break
    return s.strip("_")


def _range_stem(key: str) -> str:
    """Map a range choice's parameter_name to the stem an independently-grounded
    template is likely to use for its min/max placeholders: camelCase->snake, then
    drop a trailing 'range'/'ranges' segment. E.g. ``thresholdRange`` -> ``threshold``
    (so ``{threshold_min}``/``{threshold_max}`` fill). Generic naming convention,
    no extension/param-specific strings."""
    src = str(key or "")
    out = []
    for i, ch in enumerate(src):
        if ch.isupper() and i > 0 and (src[i - 1].islower() or src[i - 1].isdigit()):
            out.append("_")
        out.append(ch.lower())
    s = "".join(out)
    for suffix in ("_ranges", "_range", "ranges", "range"):
        if s.endswith(suffix):
            s = s[: -len(suffix)]
            break
    return s.strip("_")


def _build_format_kwargs(arguments: Dict, ext_name: str = "") -> Dict[str, str]:
    """Convert tool arguments to template format kwargs (repr-wrapped).

    Also merges the recorded workflow CHOICES for ``ext_name`` so a later step's
    grounded template can fill placeholders from an EARLIER user_choice (e.g. a
    threshold range chosen in step 5 fills the ``{threshold_min}``/``{threshold_max}``
    placeholders of the Apply step). A range value ``[lo, hi]`` is expanded to
    ``<key>_min``/``<key>_max`` AND a de-suffixed stem form (see _range_stem) so
    independently-grounded templates line up. Explicit tool arguments always win
    over merged choices. Generic: keyed on value shape, applied to every extension.
    """
    format_kwargs = {}
    for key, value in arguments.items():
        if isinstance(value, str):
            format_kwargs[key] = repr(value)
        elif value is None:
            format_kwargs[key] = "None"
        else:
            format_kwargs[key] = repr(value)
    # Merge recorded choices (do not overwrite explicit arguments).
    choices = _workflow_choices.get(ext_name, {}) if ext_name else {}
    for key, value in (choices or {}).items():
        if _is_segment_ref_value(value):
            # A segment pick is compound: expand it so a grounded template can take the
            # segmentation and the segment id as separate arguments (the shape every
            # segment-consuming extension method uses, e.g.
            # reconstruct(segmentationNode, segmentId)).
            #
            # Expanded BEFORE the bare {key} below, because a de-suffixed stem alias can
            # reproduce the key exactly: parameter_name "reference_segment_id" has stem
            # "reference", so its "_segment_id" alias IS "reference_segment_id". Filling
            # the alias first makes that placeholder mean the segment id under either
            # naming the LLM emits (reference_segment_id / referenceSegmentId), instead
            # of the dict repr no template asks for.
            stem = _segment_ref_stem(key)
            for suffix, part in (
                ("node_id", value.get("node_id")),
                ("node_name", value.get("node_name") or ""),
                ("segment_id", value.get("segment_id")),
                ("segment_name", value.get("segment_name") or ""),
            ):
                format_kwargs.setdefault(f"{key}_{suffix}", repr(part))
                if stem and stem != key:
                    format_kwargs.setdefault(f"{stem}_{suffix}", repr(part))
        format_kwargs.setdefault(key, repr(value))
        if _is_range_value(value):
            lo, hi = value[0], value[1]
            format_kwargs.setdefault(f"{key}_min", repr(lo))
            format_kwargs.setdefault(f"{key}_max", repr(hi))
            stem = _range_stem(key)
            if stem and stem != key:
                format_kwargs.setdefault(f"{stem}_min", repr(lo))
                format_kwargs.setdefault(f"{stem}_max", repr(hi))
                # ALSO fill the last word of the stem, so a QUALIFIED choice name
                # (e.g. ``referenceThresholdRange`` -> ``reference_threshold``) lines
                # up with a template that uses the generic effect-concept placeholder
                # (``{threshold_min}``, emitted by the Segment Editor driver's Apply
                # block, which cannot know the step's qualified parameter name).
                # Without this the Apply falls back to a hard-coded default range that
                # is meaningless for a non-Hounsfield volume. OVERWRITE (not
                # setdefault) so the MOST-RECENTLY-recorded range choice wins — this
                # keeps consecutive cycles correct (the reference cycle's range fills
                # the reference Apply; once the moving range is recorded it fills the
                # moving Apply) and respects replay truncation. Explicit tool
                # arguments still win (guarded below).
                last = stem.rsplit("_", 1)[-1]
                if last and last != stem:
                    if f"{last}_min" not in arguments:
                        format_kwargs[f"{last}_min"] = repr(lo)
                    if f"{last}_max" not in arguments:
                        format_kwargs[f"{last}_max"] = repr(hi)
    # Provide the structural vol_lookup expansion (raw code, not repr-wrapped) so
    # a template's bare {vol_lookup} fills instead of raising "placeholder not
    # filled". Harmless when the template has no such placeholder.
    format_kwargs.setdefault("vol_lookup", _VOL_LOOKUP_SNIPPET)
    return format_kwargs


def _build_next_step_instruction(tool_name: str, next_step: Optional[Dict], prefix: str = "") -> str:
    """Build the standard 'next step' instruction string."""
    if not next_step:
        return f"{prefix}All steps complete. Workflow is done." if prefix else "All steps complete. Workflow is done."
    is_opt = next_step.get("is_optional", False)
    if is_opt:
        return (
            f"{prefix}"
            f"Next step '{next_step['step_id']}' is optional: "
            f"{next_step['description']} "
            f"Ask the user if they want to proceed. "
            f"If yes, call {tool_name} with workflow_step='{next_step['step_id']}' user_action='start'. "
            f"If no, call with workflow_step='{next_step['step_id']}' user_action='skip'."
        )
    return (
        f"{prefix}"
        f"Proceed by calling {tool_name} with "
        f"workflow_step='{next_step['step_id']}' user_action='start'."
    )


def _semantic_tokens(text: str) -> set:
    """Tokenize names/questions for generic confidence matching."""
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", str(text or ""))
    words = re.findall(r"[A-Za-z][A-Za-z0-9]+", text.lower())
    stop = {
        "the", "and", "for", "with", "node", "select", "choose", "current",
        "which", "what", "option", "step", "user", "choice", "number",
        "many", "want", "volume", "segmentation", "model", "markup",
    }
    tokens = {w for w in words if w not in stop and len(w) > 2}
    tokens.update(w[:6] for w in list(tokens) if len(w) >= 6)
    return tokens


def _choice_is_closed_form(choices: List[Dict]) -> bool:
    """Return True for non-scene choices that should be asked explicitly."""
    if not choices:
        return False
    labels = {str(c.get("label", "")).strip().lower() for c in choices}
    values = {str(c.get("value", "")).strip().lower() for c in choices}
    labels_and_values = labels | values
    normalized = {
        re.sub(r"[^a-z0-9]+", " ", item).strip()
        for item in labels_and_values
        if item
    }
    compact = {item.replace(" ", "") for item in normalized}
    boolean_options = {"yes", "no", "true", "false"}
    side_options = {
        "left", "right", "left leg", "right leg",
        "left side", "right side", "left fibula", "right fibula",
    }
    compact_side_options = {item.replace(" ", "") for item in side_options}
    return (
        normalized <= boolean_options
        or compact <= boolean_options
        or normalized <= side_options
        or compact <= compact_side_options
    )


def _choice_is_count_question(choice_desc: Dict, step: Dict) -> bool:
    """Return True for numeric/count choices that should not auto-select nodes."""
    text = " ".join([
        str(choice_desc.get("parameter_name", "")),
        str(choice_desc.get("question", "")),
        str(step.get("description", "")),
    ]).lower()
    return any(token in text for token in ("how many", "number of", "count", "num", "amount"))


def _ui_guidance_for_context(ctx: _WorkflowContext, descriptor: Optional[Dict] = None) -> Dict:
    """Return the best available generated UI guidance for this step."""
    descriptor = descriptor or {}
    guidance = {}
    for source in (
        ctx.target_step.get("ui_guidance", {}),
        (ctx.target_gen or {}).get("ui_guidance", {}),
        descriptor.get("ui_guidance", {}),
    ):
        if isinstance(source, dict):
            guidance.update({k: v for k, v in source.items() if v not in (None, "")})
    return guidance


def _repeat_progress_for_context(ctx: _WorkflowContext) -> Dict:
    """Return repeat progress for one-item-at-a-time interaction UI."""
    repeat_group = (
        (ctx.target_gen or {}).get("repeat_block")
        or ctx.target_step.get("repeat_block")
        or (ctx.target_gen or {}).get("repeat_group")
        or (ctx.target_gen or {}).get("interaction_descriptor", {}).get("repeat_group")
        or (ctx.target_gen or {}).get("choice_descriptor", {}).get("repeat_group")
        or ctx.target_step.get("repeat_group")
    )
    if not repeat_group:
        return {}
    group_id = (
        repeat_group.get("repeat_id")
        or repeat_group.get("group_id")
        or ctx.workflow_step
    )
    state = _workflow_repeat_state.get(ctx.ext_name, {}).get(group_id, {})
    target = int(state.get("target", 0) or 0)
    iteration = int(state.get("iteration", 0) or 0)
    completed = int(state.get("completed", max(0, iteration - 1)) or 0)
    if target <= 0:
        return {
            "group_id": group_id,
            "current": iteration,
            "completed": completed,
            "total": 0,
        }
    current = min(iteration or completed + 1, target)
    return {
        "group_id": group_id,
        "current": current,
        "completed": completed,
        "total": target,
    }


def _norm_anchor_text(text) -> str:
    """Normalize a combo placeholder / question for identity matching: strip,
    drop a trailing colon, casefold. The SAME normalization must be applied on
    every side (pipeline label, emitted drive compare, panel live enumeration)
    or a cosmetic label tweak silently desyncs them."""
    return str(text or "").strip().rstrip(":").strip().lower()


def _multi_choice_items_for_step(ctx: _WorkflowContext) -> List[Dict]:
    """The step's multi-selection items ([] for single-choice steps). Mirrors
    WorkflowRuntime._multi_choice_items over the loader's ctx."""
    items = (ctx.target_step or {}).get("choice_info_list")
    if not isinstance(items, list) or len(items) < 2:
        return []
    return [i for i in items if isinstance(i, dict) and i.get("parameter_name")]


def _build_multi_choice_drive_code(ctx: _WorkflowContext, picks: List[Dict]) -> str:
    """Mirror every pick of a multi-selection step onto the extension's own combos.

    Each pick names its target combo by CONTENT, not by attribute path: a static
    combo is the one whose live items contain all the recorded options; a dynamic
    combo is the one whose first (placeholder) item matches the recorded question.
    That identification is what the scan recorded, needs no widget names, and holds
    for combos on wizard page objects (which have no .ui and mangled attrs).
    setCurrentText alone does not fire ctk/Qt 'activated' handlers, so the signal
    is invoked as a callable afterwards (a PythonQt signal emit), fail-soft.
    CodeValidator-safe: only slicer/method calls, no getattr/globals.
    """
    module_name = str((ctx.metadata or {}).get("extension_module_name") or "").strip() \
        or ctx.ext_name
    lines = [
        f"# --- {ctx.ext_name}: {ctx.workflow_step} multi-selection drive ---",
        "import slicer",
        "import qt",
        "_mc_root = None",
        "try:",
        f"    _mc_root = slicer.util.getModule({module_name!r}).widgetRepresentation()",
        "except Exception:",
        "    _mc_root = None",
        # Let a freshly-created wizard finish entering its first page before the
        # combos are searched (user input excluded -> no reentrancy).
        "slicer.app.processEvents(qt.QEventLoop.ExcludeUserInputEvents)",
        "_mc_combos = []",
        # findChildren(None) silently scans the WHOLE application window --
        # never search when the module widget could not be resolved.
        "if _mc_root is not None:",
        "    for _mc_cls in ('ctkComboBox', 'QComboBox'):",
        "        try:",
        "            for _mc_w in slicer.util.findChildren(_mc_root, className=_mc_cls):",
        "                if _mc_w not in _mc_combos:",
        "                    _mc_combos.append(_mc_w)",
        "        except Exception:",
        "            pass",
        "_mc_missed = []",
    ]
    for pick in picks:
        value = str(pick.get("value", ""))
        options = [str(o) for o in (pick.get("options") or [])]
        anchor = _norm_anchor_text(pick.get("anchor"))
        param = str(pick.get("param") or "")
        if not value:
            continue
        lines.extend([
            f"_mc_target = {value!r}",
            f"_mc_opts = {options!r}",
            f"_mc_anchor = {anchor!r}",
            "_mc_hit = False",
            "for _mc_w in _mc_combos:",
            "    _mc_items = [_mc_w.itemText(_mc_i) for _mc_i in range(_mc_w.count)]",
            "    _mc_static = _mc_opts and all(_mc_o in _mc_items for _mc_o in _mc_opts)",
            # Anchor compare normalized the same way the pipeline normalized it
            # (case, whitespace, trailing colon) so a label tweak cannot desync.
            "    _mc_first = _mc_items[0].strip().rstrip(':').strip().lower() if _mc_items else ''",
            "    _mc_dynamic = (not _mc_opts) and _mc_first == _mc_anchor",
            "    if not (_mc_static or _mc_dynamic):",
            "        continue",
            "    if _mc_target not in _mc_items:",
            "        continue",
            "    try:",
            "        _mc_w.setCurrentText(_mc_target)",
            "        _mc_hit = True",
            "    except Exception:",
            "        pass",
            # Fire the combo's activated handler the way a real click would --
            # PythonQt signals are callable; try the QString overload, then the
            # int one. Fail-soft: combos with no connected handler need neither.
            "    try:",
            "        _mc_w.activated(_mc_target)",
            "    except Exception:",
            "        try:",
            "            _mc_w.activated(_mc_w.currentIndex)",
            "        except Exception:",
            "            pass",
            "    break",
            "if not _mc_hit:",
            f"    _mc_missed.append({param!r})",
        ])
    lines.extend([
        "if _mc_missed:",
        "    raise RuntimeError(",
        f"        \"Could not apply selection(s) %s to the {module_name} module's own \"",
        "        \"controls -- open the module and verify its page is built.\" % _mc_missed",
        "    )",
        f"print({('[' + ctx.ext_name + '] Step ' + repr(ctx.workflow_step) + ': selections applied.')!r})",
        "",
    ])
    return "\n".join(lines)


def _record_multi_choice_and_advance(
    ctx: _WorkflowContext,
    items: List[Dict],
    values: Dict[str, Any],
) -> Dict:
    """Record every selector of a multi-selection step and advance once.

    Each {parameter_name: value} pair lands in the choice mirror under its own key
    (later templates read {param} per selector), the checkpoint keeps the whole
    dict, and the emitted code mirrors every pick onto the extension's live combos
    so its own handlers see the state a manual user would have left.
    """
    ext_choices = _workflow_choices.setdefault(ctx.ext_name, {})
    picks = []
    for item in items:
        param = str(item.get("parameter_name") or "")
        if not param or param not in values:
            continue
        value = values[param]
        ext_choices[param] = value
        picks.append({
            "param": param,
            "value": value,
            "options": [
                str(c.get("label", c.get("value", "")))
                for c in (item.get("choices") or []) if isinstance(c, dict)
            ],
            # For a dynamic (live-items) combo the placeholder row restates the
            # question -- the anchor that identifies the combo among its siblings.
            "anchor": str(item.get("question") or ""),
        })

    ctx.done.add(ctx.workflow_step)
    next_step = _find_next_step_local(ctx.workflow_graph, ctx.done)
    summary = ", ".join(f"{p}={values[p]}" for p in
                        [i.get("parameter_name") for i in items]
                        if p in values)
    result = {
        "tool": ctx.tool_name,
        "type": "choice_made",
        "step_id": ctx.workflow_step,
        "parameter_name": (items[0].get("parameter_name") if items else ""),
        "choice_value": dict(values),
        "message": f"Selected {summary or 'values'}.",
    }
    choice_code = _build_multi_choice_drive_code(ctx, picks) if picks else ""
    if choice_code:
        result["code"] = choice_code
        result["instruction"] = (
            "STOP. Do NOT make any more tool calls. "
            "Your NEXT response must be an ```agent_plan JSON block followed by a ```python block "
            "containing the 'code' field above VERBATIM. "
            "Do NOT call any more tools until this code has been executed."
        )
        if next_step:
            result["next_step"] = next_step
            result["after_execution_instruction"] = _build_next_step_instruction(ctx.tool_name, next_step)
        return result
    result["instruction"] = _build_next_step_instruction(ctx.tool_name, next_step)
    if next_step:
        result["next_step"] = next_step
    return result


def _record_choice_and_advance(
    ctx: _WorkflowContext,
    param_name: str,
    choice_value: Any,
    auto_selected: bool = False,
) -> Dict:
    """Store a choice, initialize repeat state when needed, and advance."""
    # A multi-selection step commits ALL its selectors at once as a
    # {parameter_name: value} dict (the step's choice_info_list names them).
    # Every pair lands in the mirror under its OWN key -- so later templates fill
    # {param} per selector -- and the source wizard combos are driven live. Keyed
    # on the step META (choice_info_list), never on the value shape, so a compound
    # single-choice value (a segment pick) is never mistaken for one.
    multi_items = _multi_choice_items_for_step(ctx)
    if multi_items and isinstance(choice_value, dict):
        return _record_multi_choice_and_advance(ctx, multi_items, choice_value)
    choice_desc = (ctx.target_gen or {}).get("choice_descriptor", {}) or {}
    choices = choice_desc.get("choices") or (ctx.target_step.get("choice_info") or {}).get("choices") or []
    choice_value = _normalize_choice_value(choice_value, choices)
    ext_choices = _workflow_choices.setdefault(ctx.ext_name, {})
    if param_name:
        ext_choices[param_name] = choice_value

    repeat_group = (
        (ctx.target_gen or {}).get("repeat_group")
        or (ctx.target_gen or {}).get("choice_descriptor", {}).get("repeat_group")
        or ctx.target_step.get("repeat_group")
    )
    if repeat_group:
        try:
            target = int(choice_value)
        except (TypeError, ValueError):
            target = 0
        if target > 0:
            group_id = repeat_group.get("group_id") or ctx.workflow_step
            _workflow_repeat_state.setdefault(ctx.ext_name, {})[group_id] = {
                "target": target,
                "completed": 0,
            }

    ctx.done.add(ctx.workflow_step)
    next_step = _find_next_step_local(ctx.workflow_graph, ctx.done)
    result = {
        "tool": ctx.tool_name,
        "type": "choice_made",
        "step_id": ctx.workflow_step,
        "parameter_name": param_name,
        "choice_value": choice_value,
        "message": f"Selected '{choice_value}' for '{param_name}'.",
    }
    if auto_selected:
        result["auto_selected"] = True
        result["message"] = (
            f"Automatically selected '{choice_value}' for '{param_name}' "
            "from the loaded scene."
        )
    choice_code = _build_choice_parameter_update_code(ctx, param_name, choice_value)
    if not choice_code:
        # A numeric RANGE pick ([min, max]) applies to the live Segment Editor
        # effect, NOT a scene node. Checked before the segment-name / node
        # materializers so the list value is never resolved as a node/name.
        choice_code = _build_range_choice_materialization_code(ctx, param_name, choice_value)
    if not choice_code:
        # A SEGMENT pick ({node_id, segment_id}) identifies a segment inside a
        # segmentation, not a scene node. Checked before the node materializer, which
        # would resolve the compound value as a node name and raise.
        choice_code = _build_segment_ref_choice_materialization_code(ctx, param_name, choice_value)
    if not choice_code:
        # A segment-NAME pick (content combobox like the 'Fragment' box) is an
        # in-content item, NOT a scene node: mirror it onto the extension's own
        # combobox (by name) so its connected handler fires. Checked BEFORE the
        # node-materialization fallback, which would otherwise try to resolve the
        # fragment name as a whole scene node and raise.
        choice_code = _build_segment_name_choice_materialization_code(ctx, param_name, choice_value)
    if not choice_code:
        # No scalar parameter-update binding matched. If this is a node choice
        # whose selector the pipeline could not bind (subject-hierarchy combo /
        # parameterNodeWrapper), nothing else applies the picked node — emit code
        # that materializes it into the cross-stage globals downstream templates
        # read, so a later step does not raise "Missing required input".
        choice_code = _build_node_choice_materialization_code(ctx, param_name, choice_value)
    if choice_code:
        result["type"] = "choice_made"
        result["code"] = choice_code
        result["instruction"] = (
            "STOP. Do NOT make any more tool calls. "
            "Your NEXT response must be an ```agent_plan JSON block followed by a ```python block "
            "containing the 'code' field above VERBATIM. "
            "Do NOT call any more tools until this code has been executed."
        )
        if next_step:
            result["next_step"] = next_step
            result["after_execution_instruction"] = _build_next_step_instruction(ctx.tool_name, next_step)
        return result
    result["instruction"] = _build_next_step_instruction(ctx.tool_name, next_step)
    if next_step:
        result["next_step"] = next_step
    return result


def _normalize_choice_value(choice_value: Any, choices: List[Dict]) -> Any:
    """Map labels like 'Yes'/'No' or strings to the declared choice value."""
    if isinstance(choice_value, str):
        raw = choice_value.strip()
        lowered = raw.lower()
    else:
        raw = choice_value
        lowered = str(choice_value).strip().lower()
    for choice in choices or []:
        label = str(choice.get("label", "")).strip().lower()
        value = choice.get("value")
        value_text = str(value).strip().lower()
        if lowered in {label, value_text}:
            return value
    if lowered in ("true", "yes", "right", "right leg", "right side"):
        return True
    if lowered in ("false", "no", "left", "left leg", "left side"):
        return False
    return raw


def _python_bool_text(value: Any) -> str:
    normalized = _normalize_choice_value(value, [])
    if isinstance(normalized, bool):
        return "True" if normalized else "False"
    lowered = str(normalized).strip().lower()
    return "True" if lowered in ("true", "yes", "right", "right leg", "right side", "1") else "False"


def _build_choice_parameter_update_code(
    ctx: _WorkflowContext,
    param_name: str,
    choice_value: Any,
) -> str:
    """Return executable code for user_choice steps bound to parameter updates."""
    sub_ops = (
        (ctx.target_gen or {}).get("sub_operations")
        or ctx.target_step.get("sub_operations")
        or []
    )
    choice_desc = (ctx.target_gen or {}).get("choice_descriptor", {}) or {}
    choices = choice_desc.get("choices") or (ctx.target_step.get("choice_info") or {}).get("choices") or []
    normalized_value = _normalize_choice_value(choice_value, choices)
    matched = None
    for so in sub_ops:
        if (
            so.get("operation_intent") == "extension_parameter_update"
            and so.get("parameter_name") == param_name
        ):
            matched = so
            break
    if not matched:
        return ""

    module_name = ctx.metadata.get("extension_module_name") or ctx.ext_name
    logic_class_name = ctx.metadata.get("logic_class_name") or f"{ctx.ext_name}Logic"
    logic_var = f"_{ctx.ext_name.lower()}_logic"
    value_property = matched.get("value_property", "")
    if value_property == "checked":
        value_text = _python_bool_text(normalized_value)
    else:
        value_text = str(normalized_value)

    return "\n".join([
        f"# --- {ctx.ext_name}: {ctx.workflow_step} choice ---",
        "import slicer",
        f"from {module_name} import {logic_class_name}",
        "",
        "try:",
        f"    logic = {logic_var}",
        "except NameError:",
        f"    logic = {logic_class_name}()",
        f"    {logic_var} = logic",
        "",
        "parameterNode = logic.getParameterNode()",
        f"parameterNode.SetParameter({param_name!r}, {value_text!r})",
        "try:",
        "    parameterNode.Modified()",
        "except Exception:",
        "    pass",
        f"{logic_var} = logic",
        f"print(\"[{ctx.ext_name}] Step '{ctx.workflow_step}' choice applied.\")",
        "",
    ])


def _is_segment_visibility_choice(ctx: _WorkflowContext) -> bool:
    """True for a segments-table step (the user unticks per-segment visibility on a
    qMRMLSegmentsTableView). Its Done carries NO node value -- the visibility is set
    directly on the scene -- so it must never trigger node materialization."""
    for src in ((ctx.target_gen or {}), (ctx.target_step or {})):
        for so in src.get("sub_operations") or []:
            if isinstance(so, dict) and (
                str(so.get("value_kind") or "").strip() == "segment_visibility_selection"
                or str(so.get("widget_class") or "").strip() == "qMRMLSegmentsTableView"
            ):
                return True
    return False


# Mirror of WorkflowRuntime._CHOICE_SELECT_VERBS / _CHOICE_VALUE_STOPWORDS /
# _CHOICE_NODE_FAMILY (kept duplicated, not imported, so the loader never imports
# WorkflowRuntime). See WorkflowRuntime for the full rationale. Keep in sync.
_CHOICE_SELECT_VERBS = frozenset({
    "choose", "select", "pick", "identify", "specify",
})
_CHOICE_VALUE_STOPWORDS = frozenset({
    "number", "count", "many", "amount", "radius", "threshold", "thickness",
    "diameter", "distance", "length", "width", "height", "angle", "degree",
    "degrees", "unit", "units", "mm", "cm", "percent", "percentage", "opacity",
    "enable", "enabled", "disable", "disabled", "visible", "visibility",
    "checkbox", "toggle", "minimum", "maximum", "factor", "ratio", "smoothing",
    "iteration", "iterations", "spacing", "tolerance", "intensity",
    "brightness", "contrast", "true", "false", "yes", "no",
})
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
# Mirror of WorkflowRuntime._NONSPECIFIC_NODE_CLASSES: base classes that say
# nothing about WHICH node to pick, so they must not win over the language
# classifier (the pipeline sometimes emits vtkMRMLNode as a placeholder).
_NONSPECIFIC_NODE_CLASSES = frozenset({
    "vtkMRMLNode", "vtkMRMLStorableNode", "vtkMRMLDisplayableNode",
    "vtkMRMLTransformableNode", "vtkMRMLDisplayableHierarchyNode",
})


def _tokenize_choice_text(text) -> set:
    """Mirror of WorkflowRuntime._tokenize_choice_text: lowercased word-token set
    with camelCase split and every non-alphanumeric run as a separator (token
    membership, not substring)."""
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", str(text or ""))
    return {t for t in re.split(r"[^A-Za-z0-9]+", spaced.lower()) if t}


def _classify_node_choice_language(family_text, broad_text, priority_text="") -> str:
    """Mirror of WorkflowRuntime._classify_node_choice_language: select verb +
    no value stopword (broad text) + a node-family noun (narrow text) -> class.
    ``priority_text`` (the parameter name — authoritative "what is selected") is
    scanned for a family noun first, so "select the source VOLUME for segmentation"
    (param ``sourceVolume``) reads as a volume, not the purpose's segmentation."""
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


def _node_class_from_choice_language(ctx: _WorkflowContext, param_name: str) -> str:
    """Language-only node-class fallback over the loader ctx (mirror of
    WorkflowRuntime._node_class_from_choice_language). Reads the family noun from
    the narrow selection labels of ctx.target_step / ctx.target_gen and the
    verb/stopword gate from the broader description text. Excludes segment-name /
    range / segment-visibility choices first. Returns "" for non-node choices."""
    if _is_segment_visibility_choice(ctx) or _is_segment_name_choice(ctx, param_name) or _is_range_choice(ctx):
        return ""
    family_parts = []
    broad_parts = []
    for src in ((ctx.target_step or {}), (ctx.target_gen or {})):
        if not isinstance(src, dict):
            continue
        guidance = src.get("ui_guidance") if isinstance(src.get("ui_guidance"), dict) else {}
        choice_info = src.get("choice_info") if isinstance(src.get("choice_info"), dict) else {}
        family_parts.extend([
            guidance.get("object_label"), guidance.get("choice_label"),
            guidance.get("input_label"), choice_info.get("question"),
            choice_info.get("parameter_name"),
        ])
        broad_parts.extend([
            src.get("description"), guidance.get("instruction"), guidance.get("title"),
        ])
        for so in src.get("sub_operations") or []:
            if not isinstance(so, dict):
                continue
            family_parts.extend([so.get("question"), so.get("parameter_name")])
            broad_parts.extend([so.get("question"), so.get("parameter_name"), so.get("description")])
    broad_parts = family_parts + broad_parts
    family_text = " ".join(str(p) for p in family_parts if p)
    broad_text = " ".join(str(p) for p in broad_parts if p)
    # The parameter name names WHAT is selected (authoritative), so it is scanned
    # for a family noun before the purpose-laden question/label text.
    priority_parts = [param_name]
    for src in ((ctx.target_step or {}), (ctx.target_gen or {})):
        if not isinstance(src, dict):
            continue
        choice_info = src.get("choice_info") if isinstance(src.get("choice_info"), dict) else {}
        priority_parts.append(choice_info.get("parameter_name"))
        for so in src.get("sub_operations") or []:
            if isinstance(so, dict):
                priority_parts.append(so.get("parameter_name"))
    priority_text = " ".join(str(p) for p in priority_parts if p)
    return _classify_node_choice_language(family_text, broad_text, priority_text)


def _node_class_for_choice(ctx: _WorkflowContext, param_name: str) -> str:
    """Node class for a node-valued choice, read from the step graph itself.

    Mirrors WorkflowRuntime._node_class_from_step_meta: prefers a ``choice_input``
    node role, then a ``value_kind == "node"`` sub-operation. Returns "" for a
    non-node choice (boolean/int/float), or when the role/sub-op is bound to a
    different parameter than ``param_name``.
    """
    # A segments-table step carries a choice_input role of vtkMRMLSegmentationNode
    # (the LLM emits it non-deterministically), but the user's input is per-segment
    # visibility on the scene, not a node pick; its Done value is empty. Never
    # materialize a node from it (an empty choice_value would raise
    # "Could not resolve the selected ... node ''").
    if _is_segment_visibility_choice(ctx):
        return ""
    # A segment-NAME pick carries a choice_input role of vtkMRMLSegmentationNode,
    # but the chosen value is a segment name, not a node — never resolve it as a
    # scene node (that path raises). Its combobox-mirror code runs instead.
    if _is_segment_name_choice(ctx, param_name):
        return ""
    # A numeric RANGE pick is a [min, max] value, never a scene node.
    if _is_range_choice(ctx):
        return ""
    for src in ((ctx.target_gen or {}), (ctx.target_step or {})):
        for role in src.get("node_roles") or []:
            if not isinstance(role, dict) or role.get("role_kind") != "choice_input":
                continue
            rp = role.get("parameter_name")
            if param_name and rp not in (None, "", param_name):
                continue
            nc = str(role.get("node_class") or "").strip()
            if nc and nc not in _NONSPECIFIC_NODE_CLASSES:
                return nc
    for src in ((ctx.target_gen or {}), (ctx.target_step or {})):
        for so in src.get("sub_operations") or []:
            if not isinstance(so, dict) or str(so.get("value_kind") or "").strip() != "node":
                continue
            sp = so.get("parameter_name")
            if param_name and sp not in (None, "", param_name):
                continue
            nc = str(so.get("node_class") or "").strip()
            if nc and nc not in _NONSPECIFIC_NODE_CLASSES:
                return nc
    # Last resort (mirrors WorkflowRuntime._node_class_from_step_meta): no
    # structural class captured — infer from the choice's language so the pick
    # both renders a node tree and drives the extension's live selector.
    return _node_class_from_choice_language(ctx, param_name)


def _choice_selector_widget(ctx: _WorkflowContext, param_name: str) -> str:
    """Name of the extension UI selector widget bound to this node choice, or ''.

    Used to mirror a user's node pick into the extension's own selector so a
    later button-click step (which drives the widget handler) sees it as input.
    """
    for src in ((ctx.target_gen or {}), (ctx.target_step or {})):
        for so in src.get("sub_operations") or []:
            if not isinstance(so, dict):
                continue
            sp = so.get("parameter_name")
            if param_name and sp not in (None, "", param_name):
                continue
            wn = str(so.get("widget_name") or "").strip()
            if wn:
                return wn
    return ""


def _has_real_choices(choices) -> bool:
    """True for genuine literal choices (a static enum), False for an empty list or
    a placeholder ``{"value": None}`` header (mirrors
    WorkflowRuntime._has_real_choices)."""
    for c in (choices or []):
        if isinstance(c, dict):
            if c.get("value") not in (None, ""):
                return True
        elif c not in (None, ""):
            return True
    return False


def _content_combo_has_keyword(widget_name: str) -> bool:
    """Whether a widget name yields a distinctive token (mirrors the stop set in
    WorkflowRuntime._keywords_from_widget_name) -- gates the content-combobox
    segment-name fallback so generically-named combos don't trip it."""
    stop = {
        "segments", "segment", "seg", "table", "view", "selector", "widget",
        "combo", "combobox", "node", "nodes", "mrml", "qmrml", "list", "tree",
        "box", "panel", "frame", "output", "input", "the", "for",
    }
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", str(widget_name or ""))
    for tok in re.split(r"[^A-Za-z0-9]+", spaced):
        t = tok.strip().lower()
        if len(t) >= 3 and t not in stop:
            return True
    return False


def _is_segment_name_choice(ctx: _WorkflowContext, param_name: str) -> bool:
    """True when this choice reproduces a content combobox of a segmentation's
    segment NAMES (e.g. the 'Fragment' box), mirroring
    WorkflowRuntime._is_segment_name_selection over the loader's ctx: an explicit
    ``value_kind == "segment_name_selection"`` OR a plain combobox source widget
    plus a ``choice_input`` role of class ``vtkMRMLSegmentationNode``.
    """
    srcs = ((ctx.target_gen or {}), (ctx.target_step or {}))
    for src in srcs:
        for so in src.get("sub_operations") or []:
            if isinstance(so, dict) and str(so.get("value_kind") or "").strip() == "segment_name_selection":
                return True
    combo = any(
        isinstance(so, dict) and str(so.get("widget_class") or "").strip() in ("QComboBox", "ctkComboBox")
        for src in srcs for so in (src.get("sub_operations") or [])
    )
    if not combo:
        return False
    for src in srcs:
        roles = list(src.get("node_roles") or [])
        for so in src.get("sub_operations") or []:
            if isinstance(so, dict):
                roles.extend(so.get("node_roles") or [])
        for role in roles:
            if (isinstance(role, dict)
                    and role.get("role_kind") == "choice_input"
                    and str(role.get("node_class") or "").strip() == "vtkMRMLSegmentationNode"):
                return True
    # Deterministic fallback (matches WorkflowRuntime._is_segment_name_selection):
    # a named content combobox -- a plain combobox with no static choices whose name
    # yields a distinctive token. Mirroring the pick onto it is fail-soft anyway.
    for src in srcs:
        for so in src.get("sub_operations") or []:
            if (isinstance(so, dict)
                    and str(so.get("widget_class") or "").strip() in ("QComboBox", "ctkComboBox")
                    and not _has_real_choices(so.get("choices"))
                    and _content_combo_has_keyword(so.get("widget_name") or "")):
                return True
    return False


def _build_segment_name_choice_materialization_code(ctx: _WorkflowContext, param_name: str, choice_value) -> str:
    """For a segment-NAME choice, set the extension's own combobox to the picked
    name so its connected handler fires (e.g. ``currentIndexChanged`` ->
    ``onFragmentSelected`` reveals that fragment's interaction handles for the next
    step). CodeValidator-safe (only ``import slicer``, method calls), fail-soft.
    Returns "" when this is not a segment-name choice or no selector is known.
    """
    if not _is_segment_name_choice(ctx, param_name):
        return ""
    module_name = str((ctx.metadata or {}).get("extension_module_name") or "").strip() or ctx.ext_name
    selector = _choice_selector_widget(ctx, param_name)
    if not (module_name and selector.isidentifier()):
        return ""
    log_msg = f"[{ctx.ext_name}] Step '{ctx.workflow_step}': selected fragment {choice_value!r}."
    lines = [
        f"# --- {ctx.ext_name}: {ctx.workflow_step} segment-name selection ---",
        "import slicer",
        f"_seg_name = {choice_value!r}",
        "_choice_widget = None",
        "try:",
        f"    _choice_widget = slicer.util.getModuleWidget({module_name!r})",
        "except Exception:",
        "    _choice_widget = None",
        "if _choice_widget is not None:",
        "    _seg_sel = None",
        "    try:",
        f"        _seg_sel = _choice_widget.ui.{selector}",
        "    except Exception:",
        "        _seg_sel = None",
        "    if _seg_sel is not None:",
        "        try:",
        "            _seg_idx = _seg_sel.findText(_seg_name)",
        "            if _seg_idx >= 0:",
        "                _seg_sel.setCurrentIndex(_seg_idx)",
        "            else:",
        "                _seg_sel.setCurrentText(_seg_name)",
        "        except Exception:",
        "            pass",
        f"print({log_msg!r})",
        "",
    ]
    return "\n".join(lines)


def _is_segment_ref_choice(ctx: _WorkflowContext) -> bool:
    """True when this choice reproduces a selector that picks a SEGMENT inside a
    segmentation, mirroring WorkflowRuntime._segment_ref_meta over the loader's ctx
    (the duplication the two mirrors already mandate for the other families).
    Keyed on the ``selection_granularity`` axis the capture stage reads off the
    extension's own selection-resolution code."""
    for src in ((ctx.target_gen or {}), (ctx.target_step or {})):
        for so in src.get("sub_operations") or []:
            if (isinstance(so, dict)
                    and str(so.get("selection_granularity") or "").strip() == "segment"):
                return True
    return False


def _build_segment_ref_choice_materialization_code(
    ctx: _WorkflowContext,
    param_name: str,
    choice_value: Any,
) -> str:
    """For a SEGMENT pick ``{node_id, segment_id, ...}``, drive the extension's own
    subject-hierarchy selector to the chosen SEGMENT ROW so its connected handler
    stores both the segmentation and the segment id.

    This is what makes the pick usable: such an extension keeps the segment id in its
    own state, and a later button-click step drives that handler, so selecting only
    the segmentation row leaves the id empty and the later step fails. Selecting a
    segment row means matching the segmentID subject-hierarchy attribute on the
    segmentation's children -- a segment row has no data node, so
    ``GetItemByDataNode`` (what the node materializer uses) cannot reach it, and
    segment names are not unique so the row name cannot identify it either.

    Also publishes the chosen segmentation under the cross-stage cached-id global and
    the segment id alongside it, so a grounded template can consume the pair directly.
    CodeValidator-safe (only ``import slicer``/``vtk`` and method calls -- no
    ``getattr``/``globals``), fail-soft. Returns "" when this is not a segment pick.
    """
    if not (param_name and param_name.isidentifier()):
        return ""
    if not _is_segment_ref_choice(ctx):
        return ""
    if not _is_segment_ref_value(choice_value):
        return ""
    node_id = str(choice_value.get("node_id") or "")
    segment_id = str(choice_value.get("segment_id") or "")
    if not (node_id and segment_id):
        return ""
    ext_slug = ctx.ext_name.lower()
    id_global = f"_{ext_slug}_{param_name}_id"
    module_name = str((ctx.metadata or {}).get("extension_module_name") or "").strip()
    selector = _choice_selector_widget(ctx, param_name)
    err_msg = (
        f"Could not resolve the selected segmentation {node_id!r} in the scene "
        f"for '{param_name}'."
    )
    log_prefix = (
        f"[{ctx.ext_name}] Step '{ctx.workflow_step}': selected segment for "
        f"'{param_name}': "
    )
    lines = [
        f"# --- {ctx.ext_name}: {ctx.workflow_step} segment selection ---",
        "import slicer",
        "import vtk",
        f"_seg_node = slicer.mrmlScene.GetNodeByID({node_id!r})",
        "if _seg_node is None:",
        f"    raise RuntimeError({err_msg!r})",
        f"_seg_id = {segment_id!r}",
        f"{param_name} = _seg_id",
        f"{id_global} = _seg_node.GetID()",
        f"_{ext_slug}_{param_name}_segment_id = _seg_id",
    ]
    # Publish the segmentation under every same-class consumer's parameter name, so a
    # later template reading it under the consuming method's role param agrees with
    # this writer (mirrors the node materializer's alias channel).
    _alias_seen = {param_name}
    for _alias_roles in ((ctx.metadata or {}).get("node_roles", {}) or {}).values():
        for _alias_role in (_alias_roles or []):
            if not isinstance(_alias_role, dict):
                continue
            if str(_alias_role.get("node_class") or "").strip() != "vtkMRMLSegmentationNode":
                continue
            _alias = str(_alias_role.get("parameter_name") or "").strip()
            if not _alias or not _alias.isidentifier() or _alias in _alias_seen:
                continue
            _alias_seen.add(_alias)
            lines.append(f"_{ext_slug}_{_alias}_id = _seg_node.GetID()")
    if module_name:
        # Find the segment's own row: the child of the segmentation item whose
        # segmentID attribute matches, then make it current so the handler fires.
        lines.extend([
            "_seg_row = 0",
            "try:",
            "    _seg_shn = slicer.mrmlScene.GetSubjectHierarchyNode()",
            "    _seg_parent = _seg_shn.GetItemByDataNode(_seg_node)",
            "    _seg_kids = vtk.vtkIdList()",
            "    _seg_shn.GetItemChildren(_seg_parent, _seg_kids)",
            "    _seg_attr = slicer.vtkMRMLSegmentationNode.GetSegmentIDAttributeName()",
            "    for _seg_i in range(_seg_kids.GetNumberOfIds()):",
            "        _seg_kid = _seg_kids.GetId(_seg_i)",
            "        if _seg_shn.GetItemAttribute(_seg_kid, _seg_attr) == _seg_id:",
            "            _seg_row = _seg_kid",
            "            break",
            "except Exception:",
            "    _seg_row = 0",
            "_seg_driven = False",
        ])
        if selector.isidentifier():
            lines.extend([
                "_seg_widget = None",
                "try:",
                f"    _seg_widget = slicer.util.getModuleWidget({module_name!r})",
                "except Exception:",
                "    _seg_widget = None",
                "if _seg_widget is not None and _seg_row:",
                "    try:",
                f"        _seg_widget.ui.{selector}.setCurrentItem(_seg_row)",
                "        _seg_driven = True",
                "    except Exception:",
                "        pass",
            ])
        # Fallback for Python-built UIs (no `.ui` entry): drive every SH tree whose
        # nodeTypes filter IsA-matches the segmentation. The filter match keeps an
        # unrelated selector (e.g. a curve tree) out of it.
        lines.extend([
            "if not _seg_driven and _seg_row:",
            "    _seg_root = None",
            "    try:",
            f"        _seg_root = slicer.util.getModule({module_name!r}).widgetRepresentation()",
            "    except Exception:",
            "        _seg_root = None",
            "    try:",
            "        _seg_trees = slicer.util.findChildren(",
            "            _seg_root, className='qMRMLSubjectHierarchyTreeView')",
            "    except Exception:",
            "        _seg_trees = []",
            "    for _seg_t in _seg_trees:",
            "        try:",
            "            _seg_nt = _seg_t.nodeTypes",
            "            _seg_types = list(_seg_nt() if callable(_seg_nt) else _seg_nt)",
            "        except Exception:",
            "            _seg_types = []",
            "        if not _seg_types:",
            "            continue",
            "        if not any(_seg_node.IsA(str(_seg_ty)) for _seg_ty in _seg_types):",
            "            continue",
            "        try:",
            "            _seg_t.setCurrentItem(_seg_row)",
            "        except Exception:",
            "            pass",
        ])
    lines.append(f"print({log_prefix!r} + _seg_node.GetName() + ' / ' + _seg_id)")
    lines.append("")
    return "\n".join(lines)


def _is_range_choice(ctx: _WorkflowContext) -> bool:
    """True when this choice is a numeric RANGE adjustment (double-handled slider),
    mirroring WorkflowRuntime._is_range_selection over the loader's ctx: an explicit
    ``value_kind == "range"`` OR a range widget source class."""
    for src in ((ctx.target_gen or {}), (ctx.target_step or {})):
        for so in src.get("sub_operations") or []:
            if not isinstance(so, dict):
                continue
            if str(so.get("value_kind") or "").strip() == "range":
                return True
            if str(so.get("widget_class") or "").strip() in _RANGE_WIDGET_CLASSES:
                return True
    return False


def _build_range_choice_materialization_code(ctx: _WorkflowContext, param_name: str, choice_value) -> str:
    """For a numeric RANGE choice ``[min, max]``, apply the chosen range to the live
    Segment Editor effect so its state/preview reflects the pick (the downstream
    Apply step reads the stored value via _build_format_kwargs). Drives the active
    effect's own range widget generically (its handler then applies the values),
    falling back to the effect's Minimum/MaximumThreshold parameters. CodeValidator-
    safe (only ``import slicer`` + method calls; no globals()/getattr/eval), fail-
    soft. Returns "" when this is not a range choice or the value is malformed."""
    if not _is_range_choice(ctx):
        return ""
    try:
        v_min = float(choice_value[0])
        v_max = float(choice_value[1])
    except (TypeError, ValueError, IndexError, KeyError):
        return ""
    log_msg = f"[{ctx.ext_name}] Step '{ctx.workflow_step}': set range '{param_name}' to [{v_min}, {v_max}]."
    lines = [
        f"# --- {ctx.ext_name}: {ctx.workflow_step} range selection ---",
        "import slicer",
        f"_range_lo, _range_hi = {v_min!r}, {v_max!r}",
        "_range_effect = None",
        "try:",
        "    _range_effect = slicer.modules.segmenteditor.widgetRepresentation().self().editor.activeEffect()",
        "except Exception:",
        "    _range_effect = None",
        "if _range_effect is not None:",
        "    _range_applied = False",
        "    try:",
        "        _range_frame = _range_effect.optionsFrame()",
        "        _range_widgets = slicer.util.findChildren(_range_frame, className='ctkRangeWidget')",
        "        if _range_widgets:",
        "            _range_widgets[0].setMinimumValue(_range_lo)",
        "            _range_widgets[0].setMaximumValue(_range_hi)",
        "            _range_applied = True",
        "    except Exception:",
        "        _range_applied = False",
        "    if not _range_applied:",
        "        try:",
        "            _range_effect.setParameter('MinimumThreshold', _range_lo)",
        "            _range_effect.setParameter('MaximumThreshold', _range_hi)",
        "        except Exception:",
        "            pass",
        f"print({log_msg!r})",
        "",
    ]
    return "\n".join(lines)


def _choice_has_node_binding(ctx: _WorkflowContext, param_name: str) -> bool:
    """True when the pipeline inferred a node binding for this choice.

    A bound node choice is applied to the parameter node by the prelude's
    ``apply_workflow_metadata``; only UNBOUND node choices need explicit
    materialization. Checks the same binding sources the dispatch handler does.
    """
    binding = (
        ((ctx.target_gen or {}).get("choice_descriptor", {}) or {}).get("binding")
        or ctx.target_step.get("choice_binding")
        or (ctx.metadata.get("choice_bindings", {}) or {}).get(ctx.workflow_step, {})
    )
    if isinstance(binding, dict) and binding.get("node_class"):
        return True
    pb = (ctx.metadata.get("parameter_bindings", {}) or {}).get(param_name, {})
    return bool(isinstance(pb, dict) and pb.get("node_class"))


def _build_node_choice_materialization_code(
    ctx: _WorkflowContext,
    param_name: str,
    choice_value: Any,
) -> str:
    """Materialize an UNBOUND node choice into the globals downstream templates read.

    The pipeline's UI->parameter binding inference only recognizes the classic
    ``qMRMLNodeComboBox`` + ``SetNodeReferenceID(...currentNodeID)`` pattern.
    Selectors using a ``qMRMLSubjectHierarchyComboBox`` or the
    ``parameterNodeWrapper`` / ``connectGui`` style yield no binding, so for those
    node choices nothing applies the picked node: ``apply_workflow_metadata``
    skips it (empty bindings) and no scalar apply code is emitted. A later
    template that resolves the node by its cached id
    (``_<ext_slug>_<param>_id``, see template_generation.py:290/503) then raises
    "Missing required input". Resolve the chosen node by name and set both the
    namespace variable and the cached-id global the cross-stage wiring expects,
    so downstream steps find it. Returns "" when this is not an unbound node
    choice (bound choices are handled by the prelude instead).
    """
    if not param_name or not param_name.isidentifier():
        return ""
    node_class = _node_class_for_choice(ctx, param_name)
    if not node_class:
        return ""
    if _choice_has_node_binding(ctx, param_name):
        return ""
    ext_slug = ctx.ext_name.lower()
    id_global = f"_{ext_slug}_{param_name}_id"
    err_msg = (
        f"Could not resolve the selected {node_class} node "
        f"{choice_value!r} in the scene for '{param_name}'."
    )
    log_prefix = (
        f"[{ctx.ext_name}] Step '{ctx.workflow_step}': "
        f"selected node for '{param_name}': "
    )
    # Resolve by name with only ``slicer`` (no library import) so the emitted code
    # passes CodeValidator and runs in the sandboxed __main__ namespace: exact
    # getNode() first, then a name match within the node class. Sets both the
    # namespace variable and the cross-stage cached-id global the generator's
    # GetNodeByID wiring expects (template_generation.py:290/503).
    lines = [
        f"# --- {ctx.ext_name}: {ctx.workflow_step} node selection (unbound choice) ---",
        "import slicer",
        f"_sel_name = {choice_value!r}",
        f"_sel_class = {node_class!r}",
        "_chosen_node = None",
        "try:",
        "    _cand = slicer.util.getNode(_sel_name)",
        "    if _cand is not None and _cand.IsA(_sel_class):",
        "        _chosen_node = _cand",
        "except Exception:",
        "    _chosen_node = None",
        "if _chosen_node is None:",
        "    _nodes = slicer.mrmlScene.GetNodesByClass(_sel_class)",
        "    for _i in range(_nodes.GetNumberOfItems()):",
        "        _cand = _nodes.GetItemAsObject(_i)",
        "        if _cand is not None and _cand.GetName() == _sel_name:",
        "            _chosen_node = _cand",
        "            break",
        "if _chosen_node is None:",
        f"    raise RuntimeError({err_msg!r})",
        f"{param_name} = _chosen_node",
        f"{id_global} = _chosen_node.GetID()",
        f"print({log_prefix!r} + _chosen_node.GetName())",
    ]
    # Cache the chosen node's id under every consumer's parameter name whose
    # node_class matches. The unbound-choice writer names the cached-id global after
    # THIS choice's param (often the widget name, e.g. `fullBoneSelector`), but a
    # later extension_op template reads it under the consuming method's role param
    # (e.g. `segmentationNode`). Emitting matching-class aliases makes writer and
    # reader agree regardless of which naming convention the reader used. Generic:
    # keyed only on node_class; CodeValidator-safe (only `.GetID()`).
    _alias_seen = {param_name}
    for _alias_roles in ((ctx.metadata or {}).get("node_roles", {}) or {}).values():
        for _alias_role in (_alias_roles or []):
            if not isinstance(_alias_role, dict):
                continue
            if str(_alias_role.get("node_class") or "").strip() != node_class:
                continue
            _alias = str(_alias_role.get("parameter_name") or "").strip()
            if not _alias or not _alias.isidentifier() or _alias in _alias_seen:
                continue
            _alias_seen.add(_alias)
            lines.append(f"_{ext_slug}_{_alias}_id = _chosen_node.GetID()")
    # Also mirror the pick into the extension's own LIVE selector widget, so a
    # later button-click step (which drives the widget handler) reads the chosen
    # node as its input — e.g. onLoadSkull reads segTree.currentItem(), which is
    # empty unless we drive it here (the agent's own panel selection does NOT reach
    # the extension's widget). Fail-soft and additive — the cached-id channel above
    # still serves the low-level cross-stage consumers. module_name is the
    # IMPORTABLE extension module (the getModule key), NOT ctx.ext_name.
    module_name = str((ctx.metadata or {}).get("extension_module_name") or "").strip()
    selector = _choice_selector_widget(ctx, param_name)
    if module_name:
        lines.append("_choice_driven = False")
        # (A) Preferred: the pipeline-captured selector on the module's `.ui`
        # (classic .ui extensions). qMRMLNodeComboBox -> setCurrentNode;
        # qMRMLSubjectHierarchyComboBox -> setCurrentItem.
        if selector.isidentifier():
            lines.extend([
                "_choice_widget = None",
                "try:",
                f"    _choice_widget = slicer.util.getModuleWidget({module_name!r})",
                "except Exception:",
                "    _choice_widget = None",
                "if _choice_widget is not None:",
                "    _choice_sel = None",
                "    try:",
                f"        _choice_sel = _choice_widget.ui.{selector}",
                "    except Exception:",
                "        _choice_sel = None",
                "    if _choice_sel is not None:",
                "        try:",
                "            _choice_sel.setCurrentNode(_chosen_node)",
                "            _choice_driven = True",
                "        except Exception:",
                "            try:",
                "                _choice_shn = slicer.mrmlScene.GetSubjectHierarchyNode()",
                "                _choice_sel.setCurrentItem(_choice_shn.GetItemByDataNode(_chosen_node))",
                "                _choice_driven = True",
                "            except Exception:",
                "                pass",
            ])
        # (B) Fallback for PYTHON-built UIs (no captured widget_name / no `.ui`,
        # like this extension's `self.segTree`): introspect the module's own
        # QWidget for node-selector widgets whose nodeTypes filter IsA-matches the
        # chosen node, and drive them. The filter match disambiguates (a
        # segmentation drives segTree, never curveTree); an empty (catch-all)
        # filter is skipped to avoid over-driving. Read nodeTypes as a Q_PROPERTY
        # (the getter is not a slot on qMRMLSubjectHierarchyTreeView). Traverse
        # getModule(...).widgetRepresentation() (the real QWidget), NOT
        # getModuleWidget(...) (the non-traversable Python self object).
        lines.extend([
            "if not _choice_driven:",
            "    _choice_root = None",
            "    try:",
            f"        _choice_root = slicer.util.getModule({module_name!r}).widgetRepresentation()",
            "    except Exception:",
            "        _choice_root = None",
            # widgetRepresentation() may have CREATED the widget just now; a
            # wizard-style module builds its first page asynchronously (its
            # QStateMachine enters the page on the next event-loop spin), so pump
            # queued events (user input excluded) before searching for selectors.
            "    import qt as _choice_qt",
            "    slicer.app.processEvents(_choice_qt.QEventLoop.ExcludeUserInputEvents)",
            "    for _choice_cls in ('qMRMLSubjectHierarchyTreeView', 'qMRMLNodeComboBox', 'qMRMLSubjectHierarchyComboBox'):",
            "        try:",
            "            _choice_sels = slicer.util.findChildren(_choice_root, className=_choice_cls)",
            "        except Exception:",
            "            _choice_sels = []",
            "        for _choice_w in _choice_sels:",
            "            try:",
            "                _choice_nt = _choice_w.nodeTypes",
            "                _choice_types = list(_choice_nt() if callable(_choice_nt) else _choice_nt)",
            "            except Exception:",
            "                _choice_types = []",
            "            if not _choice_types:",
            "                continue",
            "            if not any(_chosen_node.IsA(str(_choice_t)) for _choice_t in _choice_types):",
            "                continue",
            "            try:",
            "                _choice_w.setCurrentNode(_chosen_node)",
            "            except Exception:",
            "                try:",
            "                    _choice_shn2 = slicer.mrmlScene.GetSubjectHierarchyNode()",
            "                    _choice_w.setCurrentItem(_choice_shn2.GetItemByDataNode(_chosen_node))",
            "                except Exception:",
            "                    pass",
        ])
    lines.append("")
    return "\n".join(lines)


# Automatic node selection was removed: node/option choices are always made
# manually by the user via the selection dropdown in the agent panel.


def _build_choice_prelude(ctx: _WorkflowContext) -> str:
    """Emit a tiny shim that imports and invokes the metadata-application helper.

    The choices/bindings/defaults dicts are passed as Python objects via the
    executor namespace (see _build_prelude_globals); the prelude only needs
    to import the helper and call it. This collapses ~60 lines of inlined
    Python source per dispatch into ~10, and eliminates the json.dumps-vs-Python
    literal class of bugs (booleans like ``false`` are not Python literals).
    """
    # A @parameterNodeWrapper parameter node has no classic Get/SetParameter /
    # Get/SetNodeReferenceID API, so apply_workflow_metadata would crash on it.
    # For these extensions the data flows the extension's own way — choice steps
    # set the real UI selectors (which connectGui syncs into the wrapper) and the
    # button/checkbox handlers read them — so the classic prelude is both useless
    # and harmful. Skip it entirely.
    if ctx.metadata.get("parameter_node_wrapper"):
        return ""
    choices = _workflow_choices.get(ctx.ext_name, {})
    bindings = ctx.metadata.get("parameter_bindings", {}) or {}
    defaults = ctx.metadata.get("parameter_defaults", {}) or {}
    module_name = ctx.metadata.get("extension_module_name", "")
    logic_class_name = ctx.metadata.get("logic_class_name", "")
    if (not choices and not defaults) or not bindings or not module_name or not logic_class_name:
        return ""

    logic_var = f"_{ctx.ext_name.lower()}_logic"
    return (
        "# [Workflow metadata] Apply source-derived defaults and stored user choices\n"
        "import slicer\n"
        f"from {module_name} import {logic_class_name}\n"
        "from SlicerAIAgentLib.workflow_state import apply_workflow_metadata\n"
        "try:\n"
        f"    logic = {logic_var}\n"
        "except NameError:\n"
        f"    logic = {logic_class_name}()\n"
        "parameterNode = logic.getParameterNode()\n"
        "apply_workflow_metadata(parameterNode, _workflow_choices, _workflow_bindings, _workflow_defaults)\n"
        f"{logic_var} = logic\n\n"
    )


def _repeat_index_for_context(ctx: _WorkflowContext) -> int:
    repeat_group = (
        (ctx.target_gen or {}).get("repeat_block")
        or ctx.target_step.get("repeat_block")
        or (ctx.target_gen or {}).get("repeat_group")
        or (ctx.target_gen or {}).get("interaction_descriptor", {}).get("repeat_group")
        or (ctx.target_gen or {}).get("choice_descriptor", {}).get("repeat_group")
        or ctx.target_step.get("repeat_group")
        or {}
    )
    group_id = repeat_group.get("repeat_id") or repeat_group.get("group_id", "")
    if not group_id:
        return 0
    state = _workflow_repeat_state.get(ctx.ext_name, {}).get(group_id, {})
    if state.get("iteration"):
        return int(state["iteration"])
    return int(state.get("completed", 0)) + 1


def _method_name_for_context(ctx: _WorkflowContext) -> str:
    method_name = (ctx.target_gen or {}).get("method_name") or ctx.target_step.get("method_name") or ""
    if method_name:
        return method_name
    for so in (ctx.target_gen or {}).get("sub_operations", []) or ctx.target_step.get("sub_operations", []) or []:
        if so.get("op_type") == "extension_op" and so.get("extension_method_hint"):
            return so.get("extension_method_hint", "")
    return ""


def _build_runtime_prelude(ctx: _WorkflowContext) -> str:
    """Build hidden runtime context and an import shim for precondition checks.

    The validator function itself lives in SlicerAIAgentLib.workflow_state —
    the prelude just imports it and resolves the per-step ``_workflow_logic``
    instance. ``_workflow_required_bindings`` and ``_workflow_method_name``
    are passed as Python objects via the _prelude_globals side channel; the
    injected precondition call before each ``logic.<method>()`` site reads
    them from the executor namespace.
    """
    workflow_id = str(ctx.arguments.get("_workflow_id") or ctx.arguments.get("workflow_id") or "")
    repeat_index = _repeat_index_for_context(ctx)
    step_id = ctx.workflow_step
    method_name = _method_name_for_context(ctx)
    metadata = ctx.metadata or {}
    module_name = metadata.get("extension_module_name", "")
    logic_class_name = metadata.get("logic_class_name", "")
    bindings = metadata.get("parameter_bindings", {}) or {}
    method_deps = (metadata.get("parameter_method_dependencies", {}) or {}).get(method_name, {}) or {}
    role_names = list(method_deps.get("parameter_roles") or []) + list(method_deps.get("node_roles") or [])
    node_requirements = method_deps.get("node_requirements") or {}
    fallback_required_bindings = {
        role: {
            **bindings.get(role, {}),
            "_workflow_requirement": node_requirements.get(
                role,
                {
                    "requirement": "optional_unknown",
                    "conditions": [],
                    "condition_groups": [],
                },
            ),
        }
        for role in role_names
        if isinstance(bindings.get(role), dict)
    }

    lines = [
        "# [Workflow runtime] Hidden generated-CLI workflow context",
        f"_workflow_runtime_extension = {ctx.ext_name!r}",
        f"_workflow_runtime_id = {workflow_id!r}",
        f"_workflow_runtime_step = {step_id!r}",
        f"_workflow_runtime_repeat_index = {repeat_index}",
        "from SlicerAIAgentLib.workflow_state import remember_interaction_node, resolve_interaction_node",
        "",
    ]
    if not (method_name and module_name and logic_class_name):
        return "\n".join(lines) + "\n"

    lines.extend([
        "# [Workflow preconditions] Validate source-derived node references before extension logic calls",
        "from SlicerAIAgentLib.workflow_state import validate_method_preconditions",
        f"try:\n    _workflow_logic = _{ctx.ext_name.lower()}_logic\nexcept NameError:\n    from {module_name} import {logic_class_name}\n    _workflow_logic = {logic_class_name}()",
        f"_{ctx.ext_name.lower()}_logic = _workflow_logic",
        "try:",
        "    _workflow_required_bindings",
        "except NameError:",
        f"    _workflow_required_bindings = {fallback_required_bindings!r}",
        "def _workflow_validate_method_preconditions():",
        "    validate_method_preconditions(_workflow_logic, _workflow_required_bindings)",
        "",
    ])
    return "\n".join(lines) + "\n"


def _has_method_preconditions(ctx: _WorkflowContext) -> bool:
    """True iff this step will emit method-precondition metadata.

    Cheap structural check — only depends on whether the step has a method
    name AND parameter bindings referenced by that method's dependencies.
    Used by _inject_method_precondition_call to avoid rebuilding the entire
    prelude just to test membership.
    """
    method_name = _method_name_for_context(ctx)
    if not method_name:
        return False
    metadata = ctx.metadata or {}
    bindings = metadata.get("parameter_bindings", {}) or {}
    method_deps = (metadata.get("parameter_method_dependencies", {}) or {}).get(method_name, {}) or {}
    role_names = list(method_deps.get("parameter_roles") or []) + list(method_deps.get("node_roles") or [])
    return any(isinstance(bindings.get(role), dict) for role in role_names)


def _inject_method_precondition_call(ctx: _WorkflowContext, code: str) -> str:
    method_name = _method_name_for_context(ctx)
    if not method_name or not _has_method_preconditions(ctx):
        return code
    pattern = re.compile(
        rf"^(?P<indent>[ \t]*)logic\.{re.escape(method_name)}\s*\(",
        re.MULTILINE,
    )
    match = pattern.search(code)
    if not match:
        return code
    insertion = (
        f"{match.group('indent')}"
        "validate_method_preconditions(_workflow_logic, _workflow_required_bindings)\n"
    )
    return code[:match.start()] + insertion + code[match.start():]


def _build_prelude_globals(ctx: _WorkflowContext) -> Dict[str, Any]:
    """Return the Python-object side channel for the prelude.

    The dispatch result attaches this dict under ``_prelude_globals``; the
    executor registers each key as a ``__main__`` global before exec, so the
    prelude can reference choices/bindings/defaults directly without
    serializing them to source text. Always emits all-or-nothing per group
    (choice metadata vs precondition metadata) so the prelude never sees a
    missing global it would otherwise reference.
    """
    globals_dict: Dict[str, Any] = {}
    choices = _workflow_choices.get(ctx.ext_name, {})
    bindings = ctx.metadata.get("parameter_bindings", {}) or {}
    defaults = ctx.metadata.get("parameter_defaults", {}) or {}
    module_name = ctx.metadata.get("extension_module_name", "")
    logic_class_name = ctx.metadata.get("logic_class_name", "")
    # Wrapper extensions skip the classic-plumbing prelude (see
    # _build_choice_prelude), so its globals are unused — don't inject them.
    if (
        not ctx.metadata.get("parameter_node_wrapper")
        and (choices or defaults) and bindings and module_name and logic_class_name
    ):
        globals_dict["_workflow_choices"] = dict(choices)
        globals_dict["_workflow_bindings"] = dict(bindings)
        globals_dict["_workflow_defaults"] = dict(defaults)

    method_name = _method_name_for_context(ctx)
    if method_name:
        method_deps = (ctx.metadata.get("parameter_method_dependencies", {}) or {}).get(method_name, {}) or {}
        role_names = list(method_deps.get("parameter_roles") or []) + list(method_deps.get("node_roles") or [])
        node_requirements = method_deps.get("node_requirements") or {}
        required_bindings = {
            role: {
                **bindings.get(role, {}),
                "_workflow_requirement": node_requirements.get(
                    role, {
                        "requirement": "optional_unknown",
                        "conditions": [],
                        "condition_groups": [],
                    }
                ),
            }
            for role in role_names
            if isinstance(bindings.get(role), dict)
        }
        if required_bindings and module_name and logic_class_name:
            globals_dict["_workflow_required_bindings"] = required_bindings
            globals_dict["_workflow_method_name"] = method_name
    return globals_dict


def _extension_input_roles(ctx: _WorkflowContext) -> List[Dict[str, Any]]:
    """Collect this step's ``extension_input`` node roles (deduped by parameter).

    Reads both the step-level ``node_roles`` and any sub-operation ``node_roles``
    so a handler step's required inputs are found regardless of where the
    analyzer recorded them.
    """
    roles: List[Dict[str, Any]] = []
    seen = set()
    sources = [ctx.target_step.get("node_roles") or []]
    for so in (ctx.target_step.get("sub_operations") or []):
        if isinstance(so, dict):
            sources.append(so.get("node_roles") or [])
    for role_list in sources:
        for role in role_list:
            if not isinstance(role, dict):
                continue
            if role.get("role_kind") != "extension_input":
                continue
            pname = str(role.get("parameter_name") or "").strip()
            nclass = str(role.get("node_class") or "").strip()
            if not pname or not nclass or pname in seen:
                continue
            seen.add(pname)
            roles.append({"parameter_name": pname, "node_class": nclass})
    return roles


def _build_input_guard(ctx: _WorkflowContext) -> str:
    """Ensure a @parameterNodeWrapper extension's required inputs are bound.

    For a ``parameterNodeWrapper`` extension the classic choice->SetNodeReferenceID
    prelude is intentionally skipped (see _build_choice_prelude), so when no
    user_choice step provides an ``extension_input`` node role nothing sets it —
    the extension's handler (e.g. onSegPelvis reading ui.inputSelector) then
    silently no-ops on the empty input and creates nothing, yet raises no
    exception, so the workflow advances with no output. This precondition binds
    each unset input field on the wrapper parameter node — from the workflow's
    recorded choice if any, else the first matching scene node — exactly the way
    the extension's own enter()-time auto-pick does, so connectGui propagates it
    to the real selector the handler reads. If no candidate node exists it raises
    loudly instead of letting the step no-op silently.

    Only emitted for parameterNodeWrapper extensions, and only for roles whose
    parameter_name is a real wrapper field; a runtime ``not set`` guard makes it a
    no-op when the input is already bound (e.g. by the extension's own auto-pick
    or an upstream step), so it is safe to emit on every handler step.
    """
    if not ctx.metadata.get("parameter_node_wrapper"):
        return ""
    wrapper_fields = (ctx.metadata.get("parameter_node_wrapper", {}) or {}).get("fields", {}) or {}
    module_name = str((ctx.metadata or {}).get("extension_module_name") or "").strip()
    if not module_name:
        return ""
    roles = [
        r for r in _extension_input_roles(ctx)
        if r["parameter_name"] in wrapper_fields
        and r["parameter_name"].isidentifier()
    ]
    if not roles:
        return ""
    recorded = _workflow_choices.get(ctx.ext_name, {}) or {}

    blocks = [
        f"# --- {ctx.ext_name}: {ctx.workflow_step} ensure extension inputs ---",
        "import slicer",
        "_ig_widget = None",
        "try:",
        f"    _ig_widget = slicer.util.getModuleWidget({module_name!r})",
        "except Exception:",
        "    _ig_widget = None",
        "_ig_pn = None",
        "if _ig_widget is not None:",
        "    try:",
        "        _ig_pn = _ig_widget._parameterNode",
        "    except Exception:",
        "        _ig_pn = None",
        "    if _ig_pn is None:",
        "        try:",
        "            _ig_pn = _ig_widget.logic.getParameterNode()",
        "        except Exception:",
        "            _ig_pn = None",
    ]
    for role in roles:
        pname = role["parameter_name"]
        nclass = role["node_class"]
        rec_val = str(recorded.get(pname) or "")
        err = (
            f"[GeneratedWorkflowPrecondition] Missing required input {nclass} "
            f"for '{pname}' in {ctx.workflow_step}. Load or select a {nclass} first."
        )
        log = f"[{ctx.ext_name}] {ctx.workflow_step}: bound extension input '{pname}' = "
        blocks += [
            "if _ig_pn is not None:",
            "    _ig_cur = None",
            "    try:",
            f"        _ig_cur = _ig_pn.{pname}",
            "    except Exception:",
            "        _ig_cur = None",
            "    if not _ig_cur:",
            "        _ig_node = None",
            f"        _ig_recorded = {rec_val!r}",
            "        if _ig_recorded:",
            "            try:",
            "                _ig_c = slicer.util.getNode(_ig_recorded)",
            f"                if _ig_c is not None and _ig_c.IsA({nclass!r}):",
            "                    _ig_node = _ig_c",
            "            except Exception:",
            "                _ig_node = None",
            "        if _ig_node is None:",
            f"            _ig_nodes = slicer.mrmlScene.GetNodesByClass({nclass!r})",
            "            for _ig_i in range(_ig_nodes.GetNumberOfItems()):",
            "                _ig_cand = _ig_nodes.GetItemAsObject(_ig_i)",
            "                if _ig_cand is None:",
            "                    continue",
            "                _ig_hidden = False",
            "                try:",
            "                    _ig_hidden = bool(_ig_cand.GetHideFromEditors())",
            "                except Exception:",
            "                    _ig_hidden = False",
            "                if not _ig_hidden:",
            "                    _ig_node = _ig_cand",
            "                    break",
            "        if _ig_node is None:",
            f"            raise RuntimeError({err!r})",
            "        try:",
            f"            _ig_pn.{pname} = _ig_node",
            "        except Exception:",
            "            pass",
            f"        print({log!r} + str(_ig_node.GetName()))",
        ]
    blocks.append("")
    return "\n".join(blocks)


def _prepend_choice_prelude(ctx: _WorkflowContext, code: Optional[str]) -> Optional[str]:
    if not code:
        return code
    runtime_prelude = _build_runtime_prelude(ctx)
    prelude = _build_choice_prelude(ctx)
    input_guard = _build_input_guard(ctx)
    code = _inject_method_precondition_call(ctx, code)
    return (prelude or "") + runtime_prelude + (input_guard or "") + code


def build_assembled_code_for_validation(
    ext_name: str,
    metadata: Dict[str, Any],
    generator: Dict[str, Any],
    template_code: str,
) -> str:
    """Assemble prelude + filled template for offline dry-validation.

    Mirrors what ``dispatch_workflow_step`` produces at runtime, minus the
    actual choice values (which are runtime state). Used by verify_repair to
    validate the *assembled* artifact (template + prelude) at generation
    time, so generator-side prelude bugs surface here instead of at every
    runtime step.

    Args:
        ext_name: Extension name (e.g., "BoneReconstructionPlanner").
        metadata: workflow_metadata.json contents (parameter_bindings, etc.).
        generator: Generator entry from code_generators.json.
        template_code: Template file content with all format-kwargs already
            filled by the caller.

    Returns:
        Assembled code string (prelude + template) ready for ``ast.parse``
        and ``CodeValidator.validate``.
    """
    workflow_step = (
        (generator.get("param_signature") or {}).get("workflow_step")
        or generator.get("workflow_step")
        or "validation_sample_step"
    )
    target_step = {
        "step_id": workflow_step,
        "method_name": generator.get("method_name", ""),
        "sub_operations": generator.get("sub_operations", []),
        "repeat_block": generator.get("repeat_block"),
        "repeat_group": generator.get("repeat_group"),
        "interaction_descriptor": generator.get("interaction_descriptor", {}),
        "choice_descriptor": generator.get("choice_descriptor", {}),
    }
    ctx = _WorkflowContext(
        ext_name=ext_name,
        ext_dir="",
        tool_name=f"{ext_name}_validation",
        workflow_graph={"steps": []},
        target_step=target_step,
        target_gen=generator,
        arguments={"_workflow_id": "validation"},
        user_action="start",
        done=set(),
        metadata=metadata or {},
    )
    assembled = _prepend_choice_prelude(ctx, template_code)
    return assembled if assembled is not None else template_code


def _store_generated_interaction_node_code(
    extension_name: str,
    step_id: str,
    node_expr: str = "node",
) -> str:
    node_var = f"_{extension_name.lower()}_{step_id}_id"
    return "\n".join([
        f"{node_var} = {node_expr}.GetID()",
        (
            "remember_interaction_node("
            f"_workflow_runtime_extension, _workflow_runtime_id, {step_id!r}, "
            f"{node_var}, _workflow_runtime_repeat_index)"
        ),
    ])


def _handle_repeat_after_interaction(ctx: _WorkflowContext) -> Optional[Dict]:
    """Return a repeat-next response when an interaction should loop."""
    if (ctx.target_gen or {}).get("repeat_block") or ctx.target_step.get("repeat_block"):
        # Generic repeat blocks advance only after post-code execution succeeds.
        return None
    repeat_group = (
        (ctx.target_gen or {}).get("repeat_group")
        or (ctx.target_gen or {}).get("interaction_descriptor", {}).get("repeat_group")
        or ctx.target_step.get("repeat_group")
    )
    if not repeat_group:
        return None
    if repeat_group.get("interaction_step") != ctx.workflow_step:
        return None

    group_id = repeat_group.get("group_id") or ctx.workflow_step
    state = _workflow_repeat_state.setdefault(ctx.ext_name, {}).setdefault(
        group_id, {"target": 0, "completed": 0}
    )
    state["completed"] = int(state.get("completed", 0)) + 1
    target = int(state.get("target", 0))
    if target <= 0 or state["completed"] >= target:
        return None

    start_step_id = repeat_group.get("start_step")
    if start_step_id:
        ctx.done.discard(start_step_id)
    ctx.done.discard(ctx.workflow_step)
    next_step = {
        "step_id": start_step_id or ctx.workflow_step,
        "step_type": "automated",
        "description": (
            f"Repeat placement {state['completed'] + 1} of {target}"
        ),
        "is_optional": False,
    }
    return {
        "tool": ctx.tool_name,
        "type": "repeat_next",
        "step_id": ctx.workflow_step,
        "repeat_group": repeat_group,
        "repeat_progress": {
            "group_id": group_id,
            "completed": state["completed"],
            "current": state["completed"] + 1,
            "total": target,
        },
        "ui_guidance": _ui_guidance_for_context(ctx, (ctx.target_gen or {}).get("interaction_descriptor", {})),
        "message": (
            f"Repeat item {state['completed']} of {target} completed. "
            f"Continue with item {state['completed'] + 1}."
        ),
        "next_step": next_step,
        "instruction": _build_next_step_instruction(ctx.tool_name, next_step),
    }
