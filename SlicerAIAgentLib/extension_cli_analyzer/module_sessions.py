"""Generic core-module SESSION framework for the CLI generation pipeline.

Cookbook ``slicer_op`` steps phrased "In the 'X' module, ..." form coherent
multi-step SESSIONS inside a Slicer module — e.g. the Segment Editor:
``create segmentation -> add segment -> activate effect -> apply``. The pipeline
grounds each step in isolation (see ``slicer_op_manifest.py`` /
``slicer_op_generator``), so the steps lose the module's shared, stateful
workflow AND the LLM frequently grounds the STANDARD operations incorrectly
(e.g. cb_step_3 emitted an unfilled ``"{segmentation_name}"`` placeholder inside
a string literal, then self-correction thrashed on ``AddEmptySegment`` and each
failed attempt left an orphan segment named ``Segment_1``). Wrapping that code
cannot help — it fails before an appended block runs, and corrections are fresh
code with no wrap.

This module provides a GENERIC framework: a registry of per-module "session
drivers". A driver OVERRIDES the known standard operations of its module with
correct, deterministic, IDEMPOTENT code (reuse-or-create by the cookbook name,
correct API), and WRAPS the remaining operations (binding + shared-state
preamble). Shared state is threaded through MRML node ATTRIBUTES (persisted in
the scene) — never a cross-module Python import — so emitted templates stay
self-contained and pass CodeValidator (a ``SlicerAIAgentLib`` import inside a
template would be rejected as a non-allowed module).

Generic and safe: keyed on the module + the step's Slicer API surface, never on
the extension or a specific step; idempotent + marker-guarded; an unknown module
gets no driver -> no change (identical to prior behavior). The Segment Editor is
the first (reference) driver; adding Markups / another core module is a new
``ModuleSessionDriver`` subclass in the registry — the framework does not change.
"""

import re

# "In the 'Segment Editor' module ..." — capture the module label generically.
_MODULE_CONTEXT_RE = re.compile(
    r"\bin\s+the\s+[\"']?([A-Za-z0-9 _\-/]+?)[\"']?\s+module\b",
    re.IGNORECASE,
)


def extract_module(text):
    """Return the target module named in a cookbook step's text
    ("In the 'X' module, ..."), normalized to lowercase single-spaced, or "" if
    none. Generic for any module name; used to document/scope sessions."""
    if not text:
        return ""
    match = _MODULE_CONTEXT_RE.search(str(text))
    if not match:
        return ""
    return re.sub(r"\s+", " ", match.group(1).strip()).lower()


def _safe_name(name, default):
    """A MRML-safe display name: keep word chars / space / dash, drop quotes and
    anything that could break the emitted string literal. Falls back to default."""
    cleaned = re.sub(r"[^\w \-]", "", str(name or "")).strip()
    return cleaned or default


class ModuleSessionDriver:
    """Base class: a per-module session driver rewrites a slicer_op step's
    template so the module's stateful workflow is coherent + its standard
    operations are correct. Subclasses set ``module_names`` and override
    ``wrap``. ``wrap`` MUST be idempotent (guard on a marker) and emit only
    CodeValidator-safe code (no ``globals``/``getattr``/``eval``/``open``, no
    cross-module imports, no destructive ops)."""

    module_names = ()

    def claims(self, module):
        return bool(module) and module in self.module_names

    def wrap(self, code, description="", active_effect=None):
        return code

    # --- hooks consumed by the interaction classifier / template threading ---
    def effect_activated_by(self, step):
        """If ``step`` activates a named tool/effect in this module (e.g. clicks
        the 'Islands' button), return that tool's name; else None. Used to thread
        the active tool across a module session. Default: no tool model."""
        return None

    def activates_view_owning_tool(self, step):
        """True when ``step`` puts this module into a state where an active tool
        consumes direct view interaction (clicks/drags in a slice/3D view) itself
        — so a following 'click in the view' user_interaction is an in-tool
        interaction, not a Markups placement. Default: this module has no such
        tool concept."""
        return False

    def interaction_preamble(self):
        """CodeValidator-safe, CREATION-FREE code that re-asserts this module's
        active tool is bound to the right target just before the user interacts
        with it (no node creation, no place mode). Empty for modules with no
        interactive tool concept."""
        return ""


# --- Segment Editor session driver -----------------------------------------
# MRML attributes that thread the session across steps (stored on the session
# segmentation node, persisted in the scene). Namespaced so they never collide.
_SEG_SESSION_ATTR = "SlicerAIAgent.SegmentEditorSession"
_SEG_TARGET_ATTR = "SlicerAIAgent.SegmentEditorTargetSegmentID"
_SEG_SESSION_MARK = "[Segment Editor session]"
# Structural button/label words that are NOT effect names — used to tell an
# effect-activation step ("click the 'Islands' button") from a segment/structural
# op ("click the 'Add' button"). Generic across effects; not an effect enumeration.
_SEG_STRUCTURAL_LABELS = frozenset({
    "add", "apply", "remove", "delete", "create", "new", "ok", "cancel",
    "done", "close", "show", "hide", "show 3d", "toggle", "undo", "redo",
})

# Effect/tool drivers on qMRMLSegmentEditorWidget that need a bound segmentation +
# source volume + a valid selected segment before they are safe/correct to call.
_SEGMENT_EDITOR_EFFECT_DRIVERS = (
    "setActiveEffectByName",
    "setActiveEffect(",
    "activeEffect(",
    "effectByName(",
    "setCurrentSegmentID(",
)


class SegmentEditorSessionDriver(ModuleSessionDriver):
    """Reference driver. OVERRIDES the Segment Editor's standard create/add ops
    with deterministic idempotent code, and WRAPS effect-drive ops with a
    binding + target-selection preamble.

    - create-segmentation  -> deterministic reuse-or-create by the cookbook name;
      marks it the session segmentation. No placeholder, no duplicate on re-run.
    - add-segment          -> deterministic + IDEMPOTENT: reuse a segment already
      named ``<name>`` (kills the orphan-on-retry that produced ``Segment_1``),
      else ``AddEmptySegment(id, name)`` with the correct arg order. Marks it the
      session TARGET segment.
    - effect activate/apply -> preamble binds the shared editor + session
      segmentation + source volume and SELECTS the target segment on both the
      editor node and the widget, so Threshold ``onApply`` writes into the target.
    """

    module_names = ("segment editor", "segmenteditor")

    # ---- detection --------------------------------------------------------
    @staticmethod
    def _creates_segmentation(code):
        return "AddNewNodeByClass" in code and "vtkMRMLSegmentationNode" in code

    @staticmethod
    def _adds_segment(code):
        return "AddEmptySegment" in code

    @classmethod
    def _drives_effect(cls, code):
        low = code.lower()
        grabs_editor = (
            ("segmenteditor" in low and ".editor" in low)
            or "qmrmlsegmenteditorwidget" in low
        )
        if not grabs_editor:
            return False
        return any(driver in code for driver in _SEGMENT_EDITOR_EFFECT_DRIVERS)

    # ---- name extraction (from grounded code, else the step description) ---
    @staticmethod
    def _first_group(patterns, code, group=1):
        for pat in patterns:
            m = re.search(pat, code)
            if m and m.group(group):
                return m.group(group)
        return ""

    @classmethod
    def _extract_segmentation_name(cls, code, description):
        # Prefer the COOKBOOK name from the step description — it is authoritative and
        # SHARED with the add step and the downstream node selection. The LLM's
        # grounded-code name is per-roll variance (e.g. it grounded
        # "ReferenceBone_segmentation" for a cookbook that says "Reference_Segmentation"),
        # so trusting the code diverges the create step from every other step that
        # references the cookbook name -> a second, empty segmentation + a
        # self-correction cascade. Fall back to the grounded code only when the
        # description declares no name.
        m = re.search(r"segmentation\b[^.]*?\b(?:as|to|named|called)\s+[\"']?([\w \-]+?)[\"']?\s*[.,;)]?\s*$",
                      str(description or ""), re.IGNORECASE)
        name = m.group(1) if m else ""
        if not name:
            name = cls._first_group([
                r"AddNewNodeByClass\(\s*[\"']vtkMRMLSegmentationNode[\"']\s*,\s*[\"']([^\"']+)[\"']",
                r"\.SetName\(\s*[\"']([^\"']+)[\"']",
            ], code)
        return _safe_name(name, "Segmentation")

    @classmethod
    def _extract_segment_name(cls, code, description):
        # Prefer the COOKBOOK name from the description (authoritative + shared with
        # downstream), see _extract_segmentation_name. ``segment\b`` matches the
        # standalone word, never "segmentation".
        m = re.search(r"segment\b[^.]*?\b(?:as|to|named|called)\s+[\"']?([\w \-]+?)[\"']?\s*[.,;)]?\s*$",
                      str(description or ""), re.IGNORECASE)
        name = m.group(1) if m else ""
        if not name:
            name = cls._first_group([
                r"AddEmptySegment\(\s*segmentName\s*=\s*[\"']([^\"']+)[\"']",
                r"GetName\(\)\s*(?:!=|==)\s*[\"']([^\"']+)[\"']",
                r"GetSegmentIdBySegmentName\(\s*[\"']([^\"']+)[\"']",
            ], code)
        if not name:
            # AddEmptySegment("id", "name") -> take the 2nd literal as the name.
            m2 = re.search(r"AddEmptySegment\(\s*[\"']([^\"']+)[\"']\s*,\s*[\"']([^\"']+)[\"']", code)
            if m2:
                name = m2.group(2)
        return _safe_name(name, "Segment")

    @staticmethod
    def _effect_name(code):
        m = re.search(r"setActiveEffectByName\(\s*[\"']([^\"']+)[\"']", code)
        return m.group(1) if m else "Threshold"

    @staticmethod
    def _is_apply(code, description):
        low = code.lower()
        if "onapply" in low or re.search(r"\.apply\s*\(", code):
            return True
        return "apply" in str(description or "").lower()

    @staticmethod
    def _step_kind_from_description(description):
        """Classify a Segment Editor step from its cookbook DESCRIPTION, which is
        authoritative over the frequently-miswritten grounded code (the LLM often
        grounds "add the segment" as create-segmentation and vice versa). Returns
        'apply' | 'add' | 'create' | ''. Word-level tokens so 'segment' (a segment)
        is never confused with 'segmentation' (the node)."""
        words = set(re.findall(r"[a-z]+", str(description or "").lower()))
        if "apply" in words:
            return "apply"
        if ("add" in words or "rename" in words) and "segment" in words:
            return "add"
        if "create" in words and "segmentation" in words:
            return "create"
        return ""

    # ---- effect / option model (generic; no per-effect enumeration) --------
    @staticmethod
    def _quoted_label_before(description, nouns):
        """Return the quoted 'X' label in a phrase like "... the 'X' <noun> ..."
        where <noun> is one of ``nouns`` (e.g. button/effect/tool or
        option/mode/operation), else "". Generic — reads the cookbook's own quoted
        UI label, never a hard-coded effect/option list."""
        text = str(description or "")
        noun_alt = "|".join(re.escape(n) for n in nouns)
        m = re.search(
            r"[\"']([^\"']+)[\"']\s+(?:" + noun_alt + r")\b",
            text, re.IGNORECASE,
        )
        return m.group(1).strip() if m else ""

    @classmethod
    def _effect_button_label(cls, description, code=""):
        """The effect a step ACTIVATES, from "click/activate the 'X' button/effect/
        tool" (X not a structural label) or a ``setActiveEffectByName("X")`` in the
        grounded code; else ""."""
        label = cls._quoted_label_before(description, ("button", "effect", "tool"))
        if label and label.strip().lower() not in _SEG_STRUCTURAL_LABELS:
            return label
        m = re.search(r"setActiveEffectByName\(\s*[\"']([^\"']+)[\"']", code or "")
        if m:
            return m.group(1)
        return ""

    @classmethod
    def _option_label(cls, description):
        """The option/mode a step SELECTS within the active effect, from
        "select/choose/set the 'Y' option/mode/operation/method"; else ""."""
        return cls._quoted_label_before(
            description, ("option", "mode", "operation", "method", "setting"),
        )

    @classmethod
    def _is_select_option_step(cls, description):
        low = str(description or "").lower()
        if not re.search(r"\b(select|choose|set|pick|enable|use|switch to)\b", low):
            return False
        return bool(cls._option_label(description))

    def effect_activated_by(self, step):
        """Return the effect name a Segment Editor step activates, else None.
        A structural (create/add/apply) or option-select step activates nothing."""
        if not isinstance(step, dict):
            return None
        desc = step.get("description", "") or ""
        if self._step_kind_from_description(desc) in ("create", "add", "apply"):
            return None
        if self._is_select_option_step(desc):
            return None
        code = self._step_grounded_code(step)
        label = self._effect_button_label(desc, code)
        return label or None

    def activates_view_owning_tool(self, step):
        """In the Segment Editor an ACTIVE effect owns slice-view interaction, so
        activating any effect means a following 'click in the view' step is an
        in-effect interaction. Keyed on effect activation, not on which effect."""
        return self.effect_activated_by(step) is not None

    @staticmethod
    def _step_grounded_code(step):
        """Concatenate a step's grounded sub-op code / slicer_api_keywords so the
        effect detectors can read a ``setActiveEffectByName`` the LLM emitted."""
        if not isinstance(step, dict):
            return ""
        parts = []
        for so in step.get("sub_operations", []) or []:
            if not isinstance(so, dict):
                continue
            for key in ("generated_code", "code", "implementation"):
                val = so.get(key)
                if isinstance(val, str):
                    parts.append(val)
            for kw in so.get("slicer_api_keywords", []) or []:
                if isinstance(kw, str):
                    parts.append(kw)
        return "\n".join(parts)

    # ---- dispatch ---------------------------------------------------------
    def wrap(self, code, description="", active_effect=None):
        if not isinstance(code, str) or not code or _SEG_SESSION_MARK in code:
            return code
        # An OPTION/MODE selection within an already-active effect ("select the
        # 'Keep selected island' option") sets the effect's sub-mode via the
        # effect's OWN option widget, keeping the effect active. It has no
        # create/add/apply word, so it must be routed before those branches, and
        # it must NOT re-activate a defaulted "Threshold" effect (which dropped
        # the mode entirely). Generic across effects: drives the option widget
        # whose visible label matches the cookbook's quoted option.
        option_label = self._option_label(description)
        if option_label and self._is_select_option_step(description):
            return self._select_option_block(active_effect, option_label)
        kind = self._step_kind_from_description(description)
        drives = self._drives_effect(code)
        creates = self._creates_segmentation(code)
        adds = self._adds_segment(code)
        is_apply = kind == "apply" or self._is_apply(code, description)
        # An EFFECT step (activate / apply) takes priority over create/add
        # detection: its grounded code often ALSO (wrongly) re-creates the
        # segmentation + re-adds a segment (stateless-grounding garbage — that is
        # how the bogus "segmentation_name Segmentation" node and the extra
        # "Segment" appeared). If so, OVERRIDE it with a CLEAN effect op that uses
        # the session segmentation + tracked target segment (no garbage). A clean
        # effect step (no stray create/add) just gets the binding preamble.
        #
        # An APPLY step is recognized by its DESCRIPTION ("...Apply..."), not only
        # by an on-widget effect drive: the LLM frequently grounds "Apply threshold
        # to create segment" as a LABELMAP-based segment creation
        # (AddEmptySegment / AddSegmentFromBinaryLabelmap, NO setActiveEffectByName)
        # so ``drives`` is False and ``adds`` is True — which would misroute it to
        # the add-segment override (a bogus extra "Segment" AND the Threshold never
        # applied -> the target segment stays empty -> onLoadSkull exports an empty
        # labelmap and crashes). Route any effect/apply step to the clean effect op.
        if drives or is_apply:
            # ALL effect steps (activate AND apply) emit the effect operation
            # DETERMINISTICALLY: bind the session segmentation + source volume +
            # tracked target, then setActiveEffectByName([+ set threshold range +
            # onApply for an apply]). Do NOT append the grounded code: the LLM
            # sometimes wraps the activation in an uncalled
            # ``def activateThresholdEffect(): ...`` (or re-creates the
            # segmentation/segment statelessly), so trusting it leaves the effect
            # NEVER activated — no live Threshold preview at the range step and the
            # apply is a no-op. _effect_operation_block prefers the THREADED active
            # effect (from a prior activate step) over the grounded code's own
            # setActiveEffectByName, so an effect step whose isolated grounding
            # omitted the effect no longer defaults to "Threshold" (which for an
            # Islands/Paint/… session would switch effects and re-threshold).
            return self._effect_operation_block(code, description, active_effect)
        # Create-vs-add: the DESCRIPTION is authoritative (the LLM frequently
        # grounds "add the segment" as create-segmentation -> a bogus extra
        # "Segmentation" node, and the target segment is never added). So a step
        # the cookbook calls an ADD emits the add-segment block even if its
        # grounded code (wrongly) created a segmentation, and vice versa.
        if kind == "add":
            return self._add_segment_block(self._extract_segment_name(code, description))
        if kind == "create":
            return self._create_segmentation_block(self._extract_segmentation_name(code, description))
        # No decisive description -> fall back to what the grounded code does.
        if creates or adds:
            blocks = []
            if creates:
                blocks.append(self._create_segmentation_block(
                    self._extract_segmentation_name(code, description)))
            if adds:
                blocks.append(self._add_segment_block(
                    self._extract_segment_name(code, description)))
            return "\n".join(blocks)
        return code

    # ---- emitted code blocks (CodeValidator-safe, real Slicer API) --------
    @staticmethod
    def _create_segmentation_block(name):
        return (
            "# --- {mark} create or reuse the segmentation ---\n".format(mark=_SEG_SESSION_MARK)
            + "# Deterministic + idempotent: reuse an existing segmentation of this name\n"
            "# (a re-run / correction never duplicates it), else create it, and mark it the\n"
            "# session segmentation for the add / apply steps.\n"
            "import slicer\n"
            "_ses_seg = None\n"
            "_ses_segs = slicer.mrmlScene.GetNodesByClass(\"vtkMRMLSegmentationNode\")\n"
            "for _ses_i in range(_ses_segs.GetNumberOfItems()):\n"
            "    _ses_c = _ses_segs.GetItemAsObject(_ses_i)\n"
            "    if _ses_c is not None and _ses_c.GetName() == \"{name}\":\n".format(name=name)
            + "        _ses_seg = _ses_c\n"
            "        break\n"
            "if _ses_seg is None:\n"
            "    _ses_seg = slicer.mrmlScene.AddNewNodeByClass(\"vtkMRMLSegmentationNode\", \"{name}\")\n".format(name=name)
            + "_ses_seg.CreateDefaultDisplayNodes()\n"
            # A cookbook with MORE THAN ONE segmentation (e.g. Reference then Moving,
            # each with its own Threshold->Islands cycle) forms consecutive sessions.
            # The session flag must mark ONLY the current segmentation — clear it on
            # every other one first, else the first-match resolver
            # (_resolve_session_segmentation_lines) keeps binding the effects + the
            # interaction to the FIRST-created segmentation and the later cycle
            # writes into the wrong segment. Clear-all-then-set is idempotent.
            "_ses_all = slicer.mrmlScene.GetNodesByClass(\"vtkMRMLSegmentationNode\")\n"
            "for _ses_k in range(_ses_all.GetNumberOfItems()):\n"
            "    _ses_o = _ses_all.GetItemAsObject(_ses_k)\n"
            "    if _ses_o is not None:\n"
            "        _ses_o.SetAttribute(\"{attr}\", \"0\")\n".format(attr=_SEG_SESSION_ATTR)
            + "_ses_seg.SetAttribute(\"{attr}\", \"1\")\n".format(attr=_SEG_SESSION_ATTR)
            + "segmentationNode = _ses_seg\n"
            "if _ses_seg.GetName() != \"{name}\":\n".format(name=name)
            + "    raise RuntimeError(\"STATE_NOT_APPLIED: segmentation name\")\n"
            "print(\"[SegmentEditor] Segmentation '{name}' ready.\")\n".format(name=name)
            + "# --- [end Segment Editor session] ---\n"
        )

    @staticmethod
    def _resolve_session_segmentation_lines(indent=""):
        """Emit lines that set ``_ses_seg`` to the session segmentation (the one
        marked by the create step, else the most-recently-added in the scene)."""
        return (
            "{i}_ses_seg = None\n"
            "{i}_ses_segs = slicer.mrmlScene.GetNodesByClass(\"vtkMRMLSegmentationNode\")\n"
            "{i}for _ses_i in range(_ses_segs.GetNumberOfItems()):\n"
            "{i}    _ses_c = _ses_segs.GetItemAsObject(_ses_i)\n"
            "{i}    if _ses_c is not None and _ses_c.GetAttribute(\"{attr}\") == \"1\":\n"
            "{i}        _ses_seg = _ses_c\n"
            "{i}        break\n"
            "{i}if _ses_seg is None:\n"
            "{i}    for _ses_i in range(_ses_segs.GetNumberOfItems() - 1, -1, -1):\n"
            "{i}        _ses_c = _ses_segs.GetItemAsObject(_ses_i)\n"
            "{i}        if _ses_c is not None:\n"
            "{i}            _ses_seg = _ses_c\n"
            "{i}            break\n"
        ).format(i=indent, attr=_SEG_SESSION_ATTR)

    @classmethod
    def _add_segment_block(cls, name):
        return (
            "# --- {mark} add or reuse the target segment ---\n".format(mark=_SEG_SESSION_MARK)
            + "# Deterministic + IDEMPOTENT: reuse a segment already named '{name}' (so a\n".format(name=name)
            + "# re-run / correction never creates a duplicate orphan), else\n"
            "# AddEmptySegment(id, name) with the correct arg order (a one-arg\n"
            "# AddEmptySegment auto-names the segment 'Segment_1'). Marks it the session\n"
            "# TARGET segment so the effect Apply writes into it.\n"
            "import slicer\n"
            + cls._resolve_session_segmentation_lines()
            + "if _ses_seg is None:\n"
            "    raise RuntimeError(\"STATE_NOT_APPLIED: no segmentation found for add-segment\")\n"
            "_ses_segmentation = _ses_seg.GetSegmentation()\n"
            "_ses_sid = _ses_segmentation.GetSegmentIdBySegmentName(\"{name}\")\n".format(name=name)
            + "if not _ses_sid:\n"
            "    _ses_sid = _ses_segmentation.AddEmptySegment(\"{name}\", \"{name}\")\n".format(name=name)
            + "if not _ses_sid:\n"
            "    raise RuntimeError(\"STATE_NOT_APPLIED: AddEmptySegment returned empty id\")\n"
            "_ses_seg.SetAttribute(\"{attr}\", _ses_sid)\n".format(attr=_SEG_TARGET_ATTR)
            + "segmentId = _ses_sid\n"
            "print(\"[SegmentEditor] Segment '{name}' ready.\")\n".format(name=name)
            + "# --- [end Segment Editor session] ---\n"
        )

    @classmethod
    def _bind_and_select_body(cls, create_editor_node=True):
        """Bind the shared editor + SESSION segmentation + source volume + the
        editor node, and select the tracked TARGET segment on the editor node (the
        effect reads GetSelectedSegmentID from it) and the widget. No markers.

        ``create_editor_node`` False emits a CREATION-FREE variant (reuse the
        existing segment-editor node if present, never AddNewNodeByClass) so it can
        be embedded in a user_interaction pre-template whose descriptor declares
        creates_node=false (the interaction contract validator rejects any
        AddNewNodeByClass there). By that point a prior effect step has already
        created the editor node, so reuse is sufficient."""
        if create_editor_node:
            editor_lines = (
                "_ses_editor_node = slicer.mrmlScene.GetFirstNodeByClass(\"vtkMRMLSegmentEditorNode\")\n"
                "if _ses_editor_node is None:\n"
                "    _ses_editor_node = slicer.mrmlScene.AddNewNodeByClass(\"vtkMRMLSegmentEditorNode\")\n"
                "_ses_widget.setMRMLSegmentEditorNode(_ses_editor_node)\n"
            )
        else:
            editor_lines = (
                "_ses_editor_node = slicer.mrmlScene.GetFirstNodeByClass(\"vtkMRMLSegmentEditorNode\")\n"
                "if _ses_editor_node is not None:\n"
                "    _ses_widget.setMRMLSegmentEditorNode(_ses_editor_node)\n"
            )
        return (
            "import slicer\n"
            "_ses_widget = slicer.modules.segmenteditor.widgetRepresentation().self().editor\n"
            "_ses_widget.setMRMLScene(slicer.mrmlScene)\n"
            + editor_lines
            + cls._resolve_session_segmentation_lines()
            + "if _ses_seg is not None:\n"
            "    _ses_widget.setSegmentationNode(_ses_seg)\n"
            "_ses_vol = None\n"
            "_ses_vols = slicer.mrmlScene.GetNodesByClass(\"vtkMRMLScalarVolumeNode\")\n"
            "for _ses_j in range(_ses_vols.GetNumberOfItems() - 1, -1, -1):\n"
            "    _ses_vc = _ses_vols.GetItemAsObject(_ses_j)\n"
            "    if _ses_vc is not None and not _ses_vc.IsA(\"vtkMRMLLabelMapVolumeNode\"):\n"
            "        _ses_vol = _ses_vc\n"
            "        break\n"
            "if _ses_vol is not None:\n"
            "    _ses_widget.setSourceVolumeNode(_ses_vol)\n"
            "if _ses_seg is not None and _ses_editor_node is not None:\n"
            "    _ses_segmentation = _ses_seg.GetSegmentation()\n"
            "    _ses_target = _ses_seg.GetAttribute(\"{attr}\")\n".format(attr=_SEG_TARGET_ATTR)
            + "    if not _ses_target or _ses_segmentation.GetSegment(_ses_target) is None:\n"
            "        _ses_target = _ses_segmentation.GetNthSegmentID(0) if _ses_segmentation.GetNumberOfSegments() > 0 else \"\"\n"
            "    if _ses_target:\n"
            "        _ses_editor_node.SetSelectedSegmentID(_ses_target)\n"
            "        _ses_widget.setCurrentSegmentID(_ses_target)\n"
            # Show the target segment MASK in the 2D slice views. An interactive
            # effect that acts on a slice-view click (Islands 'Keep selected island',
            # Paint, Draw, ...) needs the mask visible so the user can SEE the islands
            # to click, and it CANCELS the click on a hidden segment
            # (confirmCurrentSegmentVisible). Turn on the segmentation display's 2D
            # fill + outline + overall visibility + the segment's own visibility —
            # binding the segmentation on the editor programmatically does NOT do this
            # (that happens on Segment Editor module-enter, which the agent bypasses).
            # SafeDownCast typed so the api-proof pass keeps it (an untyped
            # GetDisplayNode() gets stripped). Idempotent.
            "        _ses_disp = slicer.vtkMRMLSegmentationDisplayNode.SafeDownCast(_ses_seg.GetDisplayNode())\n"
            "        if _ses_disp is not None:\n"
            "            _ses_disp.SetVisibility(True)\n"
            "            _ses_disp.SetVisibility2DFill(True)\n"
            "            _ses_disp.SetVisibility2DOutline(True)\n"
            "            _ses_disp.SetSegmentVisibility(_ses_target, True)\n"
        )

    def interaction_preamble(self):
        """Creation-free bind for a module_tool_interaction pre-template: re-assert
        the segment editor is bound to the SESSION segmentation + target segment +
        source volume so the ACTIVE effect (already set by the prior activate/option
        steps) consumes the user's slice-view clicks. No node creation, no place
        mode — so the interaction contract (creates_node=false / requires_place_mode
        =false) holds."""
        return (
            "# --- {mark} prepare the active effect for in-view interaction ---\n".format(mark=_SEG_SESSION_MARK)
            + "# The prior steps activated the effect and set its mode; re-bind the\n"
            "# session segmentation + target so the effect's own slice-view clicks work.\n"
            + self._bind_and_select_body(create_editor_node=False)
            # Put the source volume in the slice backgrounds and fit the view so the
            # user sees the anatomy + the segment mask overlay and can aim the click.
            + "if _ses_vol is not None:\n"
            "    try:\n"
            "        slicer.util.setSliceViewerLayers(background=_ses_vol, fit=True)\n"
            "    except Exception:\n"
            "        pass\n"
            + "# --- [end Segment Editor session] ---\n"
        )

    @classmethod
    def _operate_preamble(cls):
        return (
            "# --- {mark} bind editor + select the target segment ---\n".format(mark=_SEG_SESSION_MARK)
            + "# Effect activation on the shared qMRMLSegmentEditorWidget needs a bound\n"
            "# segmentation + source volume (else a native crash) AND a valid selected\n"
            "# segment (else onApply's modifySegmentByLabelmap gets an empty id and\n"
            "# materializes a new 'Segment_1'). Bind the SESSION segmentation + volume +\n"
            "# a single editor node and select the tracked target segment.\n"
            + cls._bind_and_select_body()
            + "# --- [end Segment Editor session] ---\n"
        )

    @classmethod
    def _effect_operation_block(cls, code, description="", active_effect=None):
        """OVERRIDE for an effect step whose grounded code (wrongly) re-creates the
        segmentation / re-adds a segment statelessly. Bind the SESSION segmentation
        + tracked target, activate the effect, and — for an APPLY step — commit it.

        The effect name is the THREADED ``active_effect`` (from a prior activate
        step) when available, else parsed from the grounded code, else "Threshold".
        This stops an effect/apply step whose isolated grounding omitted
        ``setActiveEffectByName`` from silently switching to Threshold (which for an
        Islands/Paint/… session would change effects and re-threshold the segment).

        Apply is effect-aware: the Threshold range placeholders
        (``{threshold_min}``/``{threshold_max}``, filled from the range user_choice
        by _build_format_kwargs) are emitted ONLY for the Threshold effect — for any
        other effect the apply is just the effect's own onApply (a safe no-op for the
        interactive island/paint modes, which commit on the slice-view click)."""
        effect = _safe_name(active_effect or cls._effect_name(code), "Threshold")
        out = (
            "# --- {mark} run the effect on the target segment ---\n".format(mark=_SEG_SESSION_MARK)
            + "# The grounded effect code re-created the segmentation/segment statelessly;\n"
            "# operate on the SESSION segmentation + tracked target instead (no duplicates).\n"
            + cls._bind_and_select_body()
            + "_ses_widget.setActiveEffectByName(\"{effect}\")\n".format(effect=effect)
        )
        if cls._is_apply(code, description):
            if effect == "Threshold":
                out += (
                    "_ses_eff = _ses_widget.activeEffect()\n"
                    "if _ses_eff is not None:\n"
                    "    _ses_eff.setParameter(\"MinimumThreshold\", {threshold_min: 150.0})\n"
                    "    _ses_eff.setParameter(\"MaximumThreshold\", {threshold_max: 3000.0})\n"
                    "    try:\n"
                    "        _ses_eff.self().onApply()\n"
                    "    except Exception:\n"
                    "        pass\n"
                )
            else:
                out += (
                    "_ses_eff = _ses_widget.activeEffect()\n"
                    "if _ses_eff is not None:\n"
                    "    try:\n"
                    "        _ses_eff.self().onApply()\n"
                    "    except Exception:\n"
                    "        pass\n"
                )
        out += "# --- [end Segment Editor session] ---\n"
        return out

    @classmethod
    def _select_option_block(cls, active_effect, option_label):
        """OVERRIDE for an option/mode selection within the active effect ("select
        the 'Keep selected island' option"). Bind + select target, ensure the
        effect is active (the LIVE active effect from the prior activate step, else
        re-activate the threaded ``active_effect``), then drive the effect's OWN
        option widget whose visible label matches ``option_label`` — a radio button
        / push button / checkbox (``.click()`` fires the effect's handler which sets
        the parameter) or a combo box (``findText``/``setCurrentIndex``). Generic
        across effects and options: it reproduces the exact GUI action the cookbook
        describes, so it needs no per-effect parameter/enum table."""
        label = _safe_name(option_label, "")
        reactivate = ""
        eff = _safe_name(active_effect, "")
        if eff:
            reactivate = (
                "if _ses_widget.activeEffect() is None:\n"
                "    _ses_widget.setActiveEffectByName(\"{effect}\")\n".format(effect=eff)
            )
        return (
            "# --- {mark} select an option/mode of the active effect ---\n".format(mark=_SEG_SESSION_MARK)
            + "# Keep the current effect active (do NOT switch to a default) and set its\n"
            "# mode by driving the effect's own option widget matching the cookbook label,\n"
            "# so the effect's handler applies the parameter exactly as a click would.\n"
            + cls._bind_and_select_body()
            + reactivate
            + "_opt_label = \"{label}\"\n".format(label=label)
            + "_opt_hit = False\n"
            # slicer.util.findChildren walks .children() manually — the native
            # PythonQt QWidget.findChildren is unreliable — and returns ALL
            # descendants (no className filter, which would be an EXACT match and
            # miss QRadioButton under 'QAbstractButton'). Match any child whose
            # visible text equals the option label (case-insensitive, mnemonic-
            # stripped) and click it: for a radio/checkbox/push button that fires
            # the effect's own toggled/clicked handler, which sets the parameter.
            "import slicer\n"
            "for _opt_w in slicer.util.findChildren(_ses_widget):\n"
            "    try:\n"
            "        _opt_t = _opt_w.text\n"
            "    except Exception:\n"
            "        _opt_t = None\n"
            "    if isinstance(_opt_t, str) and _opt_t.replace(\"&\", \"\").strip().lower() == _opt_label.strip().lower():\n"
            "        try:\n"
            "            _opt_w.click()\n"
            "            _opt_hit = True\n"
            "            break\n"
            "        except Exception:\n"
            "            pass\n"
            "if not _opt_hit:\n"
            "    for _opt_cb in slicer.util.findChildren(_ses_widget, className=\"QComboBox\"):\n"
            "        _opt_idx = _opt_cb.findText(_opt_label)\n"
            "        if _opt_idx >= 0:\n"
            "            _opt_cb.setCurrentIndex(_opt_idx)\n"
            "            _opt_hit = True\n"
            "            break\n"
            + (
                "if _opt_hit:\n"
                "    print(\"[SegmentEditor] Option '{label}' selected.\")\n"
                "else:\n"
                "    print(\"[SegmentEditor] Option '{label}' not found (effect options may not be shown).\")\n"
            ).format(label=label)
            + "# --- [end Segment Editor session] ---\n"
        )


# Registry — extension point. Add a new core module by appending its driver.
_DRIVERS = [
    SegmentEditorSessionDriver(),
]


def all_drivers():
    """All registered module session drivers."""
    return list(_DRIVERS)


def driver_for_module(module):
    """The session driver claiming ``module`` (lowercased label), or None."""
    for driver in _DRIVERS:
        if driver.claims(module):
            return driver
    return None
