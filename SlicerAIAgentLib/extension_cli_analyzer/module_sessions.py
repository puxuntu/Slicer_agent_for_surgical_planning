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

    def wrap(self, code, description=""):
        return code


# --- Segment Editor session driver -----------------------------------------
# MRML attributes that thread the session across steps (stored on the session
# segmentation node, persisted in the scene). Namespaced so they never collide.
_SEG_SESSION_ATTR = "SlicerAIAgent.SegmentEditorSession"
_SEG_TARGET_ATTR = "SlicerAIAgent.SegmentEditorTargetSegmentID"
_SEG_SESSION_MARK = "[Segment Editor session]"

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
        name = cls._first_group([
            r"AddNewNodeByClass\(\s*[\"']vtkMRMLSegmentationNode[\"']\s*,\s*[\"']([^\"']+)[\"']",
            r"\.SetName\(\s*[\"']([^\"']+)[\"']",
        ], code)
        if not name:
            m = re.search(r"segmentation\b[^.]*?\b(?:as|to|named|called)\s+[\"']?([\w \-]+?)[\"']?\s*[.,;)]?\s*$",
                          str(description or ""), re.IGNORECASE)
            if m:
                name = m.group(1)
        return _safe_name(name, "Segmentation")

    @classmethod
    def _extract_segment_name(cls, code, description):
        name = cls._first_group([
            r"AddEmptySegment\(\s*segmentName\s*=\s*[\"']([^\"']+)[\"']",
            r"GetName\(\)\s*(?:!=|==)\s*[\"']([^\"']+)[\"']",
            r"GetSegmentIdBySegmentName\(\s*[\"']([^\"']+)[\"']",
        ], code)
        if not name:
            # AddEmptySegment("id", "name") -> take the 2nd literal as the name.
            m = re.search(r"AddEmptySegment\(\s*[\"']([^\"']+)[\"']\s*,\s*[\"']([^\"']+)[\"']", code)
            if m:
                name = m.group(2)
        if not name:
            m = re.search(r"segment\b[^.]*?\b(?:as|to|named|called)\s+[\"']?([\w \-]+?)[\"']?\s*[.,;)]?\s*$",
                          str(description or ""), re.IGNORECASE)
            if m:
                name = m.group(1)
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

    # ---- dispatch ---------------------------------------------------------
    def wrap(self, code, description=""):
        if not isinstance(code, str) or not code or _SEG_SESSION_MARK in code:
            return code
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
            # apply is a no-op. _effect_operation_block reads the effect name from
            # the grounded code (default "Threshold") and emits real top-level API.
            return self._effect_operation_block(code, description)
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
            "_ses_seg.SetAttribute(\"{attr}\", \"1\")\n".format(attr=_SEG_SESSION_ATTR)
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
    def _bind_and_select_body(cls):
        """Bind the shared editor + SESSION segmentation + source volume + a single
        editor node, and select the tracked TARGET segment on the editor node (the
        effect reads GetSelectedSegmentID from it) and the widget. No markers."""
        return (
            "import slicer\n"
            "_ses_widget = slicer.modules.segmenteditor.widgetRepresentation().self().editor\n"
            "_ses_widget.setMRMLScene(slicer.mrmlScene)\n"
            "_ses_editor_node = slicer.mrmlScene.GetFirstNodeByClass(\"vtkMRMLSegmentEditorNode\")\n"
            "if _ses_editor_node is None:\n"
            "    _ses_editor_node = slicer.mrmlScene.AddNewNodeByClass(\"vtkMRMLSegmentEditorNode\")\n"
            "_ses_widget.setMRMLSegmentEditorNode(_ses_editor_node)\n"
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
            "if _ses_seg is not None:\n"
            "    _ses_segmentation = _ses_seg.GetSegmentation()\n"
            "    _ses_target = _ses_seg.GetAttribute(\"{attr}\")\n".format(attr=_SEG_TARGET_ATTR)
            + "    if not _ses_target or _ses_segmentation.GetSegment(_ses_target) is None:\n"
            "        _ses_target = _ses_segmentation.GetNthSegmentID(0) if _ses_segmentation.GetNumberOfSegments() > 0 else \"\"\n"
            "    if _ses_target:\n"
            "        _ses_editor_node.SetSelectedSegmentID(_ses_target)\n"
            "        _ses_widget.setCurrentSegmentID(_ses_target)\n"
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
    def _effect_operation_block(cls, code, description=""):
        """OVERRIDE for an effect step whose grounded code (wrongly) re-creates the
        segmentation / re-adds a segment statelessly. Bind the SESSION segmentation
        + tracked target, activate the effect, and — for an APPLY step — set the
        Threshold range from the user's choice and commit onApply, WITHOUT creating
        any garbage segmentation/segment. ``{threshold_min}``/``{threshold_max}``
        are runtime placeholders filled from the range user_choice (see
        _build_format_kwargs); they stay literal here (not inside a string)."""
        effect = _safe_name(cls._effect_name(code), "Threshold")
        out = (
            "# --- {mark} run the effect on the target segment ---\n".format(mark=_SEG_SESSION_MARK)
            + "# The grounded effect code re-created the segmentation/segment statelessly;\n"
            "# operate on the SESSION segmentation + tracked target instead (no duplicates).\n"
            + cls._bind_and_select_body()
            + "_ses_widget.setActiveEffectByName(\"{effect}\")\n".format(effect=effect)
        )
        if cls._is_apply(code, description):
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
        out += "# --- [end Segment Editor session] ---\n"
        return out


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
