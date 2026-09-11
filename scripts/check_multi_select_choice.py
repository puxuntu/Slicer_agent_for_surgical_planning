"""A control the surgeon answers with SEVERAL options must not be reproduced as a
one-of-N dropdown.

Some extensions ask one question that takes many answers -- PedicleScrewPlanner's
"Instrumented Levels", a ``ctkCheckableComboBox`` where every vertebral level to
instrument is ticked. Nothing about how such a control is filled or read
distinguishes it from an ordinary combo: ``addItems`` puts the options in,
``checkedIndexes()`` takes the answer out, and it is a QComboBox subclass. So the
whole mechanism hangs on ONE fact -- the widget's class -- and every way of losing
that fact is silent:

* the scan not knowing the class: the control vanishes from the page inventory
  entirely, the cookbook's quoted label matches nothing, and the step ships as a
  free-text box ("Enter Choice");
* the label never pairing with the widget: same outcome, because the quoted label
  is what the reconciler matches against -- and the pairing really does fail here,
  since the page lays its fields out by ITERATING a list of ``(label, widget)``
  pairs, so no ``addRow``/grid/sequence call names either one;
* the runtime rendering a dropdown anyway: it works, it commits, and it silently
  instruments ONE level out of however many were ticked;
* the drive missing the extension's own control: the panel shows the right answer
  and ``doStepProcessing`` reads the factory default off an untouched widget.

Every section below is one of those. Runs entirely outside Slicer: the scans are
pure AST, and the emitted drive code is executed against fake Qt widgets -- which
is the only way to prove the ticking, since there is no ctk to test against here.

Section 6 holds the other half of the same form: a selector's DEFAULT. A GUI
control answers its own question before anyone touches it -- the ROI page opens on
"L&R" and "Posterior", and ``doStepProcessing`` writes ``currentText`` on exit
whether or not the surgeon ever opened either dropdown -- so a reproduced panel
that opens on "-- Select --" demands a decision the original never demanded. The
opposite mistake is worse, and is why this is not simply "pre-select item 0": the
Measurements page opens on a PROMPT ("Choose the puncture site"), and pre-selecting
there would commit a site nobody picked, to a handler that deletes and rebuilds the
screw line. Which shape a selector has is decided from the scanned control.

    python scripts/check_multi_select_choice.py
"""

import ast
import io
import os
import sys
import types

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYZER = os.path.join(REPO, "SlicerAIAgentLib", "extension_cli_analyzer")
LOADER = os.path.join(REPO, "SlicerAIAgentLib", "extension_cli_loader")
EXT_ROOT = os.path.join(os.path.dirname(REPO), "External_extensions")

_failures = []
_checks = [0]


def check(name, cond, detail=""):
    _checks[0] += 1
    if cond:
        print("  ok   %s" % name)
    else:
        print("  FAIL %s   %s" % (name, detail))
        _failures.append(name)


# --------------------------------------------------------------------------
# Loading the analyzer's pure-AST halves without Slicer
# --------------------------------------------------------------------------
def _load_analyzer():
    ns = {"__name__": "check_multi_select",
          "__file__": os.path.join(ANALYZER, "common.py")}
    with io.open(os.path.join(ANALYZER, "common.py"), encoding="utf-8") as f:
        exec(compile(f.read(), "common.py", "exec"), ns)
    for module in ("scan.py", "stage4_decomposition.py"):
        with io.open(os.path.join(ANALYZER, module), encoding="utf-8") as f:
            src = f.read().replace("from .common import *", "", 1)
        exec(compile(src, module, "exec"), ns)
    # Several static helpers recurse through the composed class name.
    ns["ExtensionCLIAnalyzer"] = ns["AnalyzerScanMixin"]
    return ns


def _scan(ns, path):
    inst = ns["AnalyzerScanMixin"]()
    inst.on_progress = lambda *a, **k: None
    return inst._stage1_scan(path)


def _extension_dirs():
    """Every cookbook extension module folder under External_extensions."""
    found = {}
    if not os.path.isdir(EXT_ROOT):
        return found
    for entry in sorted(os.listdir(EXT_ROOT)):
        path = os.path.join(EXT_ROOT, entry)
        if not os.path.isdir(path):
            continue
        if os.path.exists(os.path.join(path, entry + ".py")):
            found[entry] = path
            continue
        for sub in sorted(os.listdir(path)):
            sub_path = os.path.join(path, sub)
            if os.path.isdir(sub_path) and os.path.exists(
                    os.path.join(sub_path, sub + ".py")):
                found[sub] = sub_path
    return found


# --------------------------------------------------------------------------
# 1. The scan sees the control at all, and pairs it with its on-screen label
# --------------------------------------------------------------------------
def section_scan(ns):
    print("[1] the page scan: a checkable combo, and the label it was written beside")
    extensions = _extension_dirs()
    if not extensions:
        check("External_extensions is available", False, EXT_ROOT)
        return {}

    scans = {}
    multi_pages = 0
    for name, path in sorted(extensions.items()):
        try:
            scans[name] = _scan(ns, path)
        except Exception as exc:                                # pragma: no cover
            check("scanning %s" % name, False, repr(exc))
            continue
        for page in (scans[name].get("wizard_pages") or {}).values():
            for combo in page.get("combos") or []:
                if combo.get("multi_select"):
                    multi_pages += 1
    check("every cookbook extension still scans", len(scans) == len(extensions))
    check("at least one multi-select control exists to test against", multi_pages > 0,
          "no ctkCheckableComboBox found in any extension")

    # The reference case: PedicleScrewPlanner's ROI page.
    roi = None
    for name in ("PedicleScrewPlanner", "PedicleScrewSimulator"):
        pages = (scans.get(name) or {}).get("wizard_pages") or {}
        if "DefineROIStep" in pages:
            roi = pages["DefineROIStep"]
            break
    if roi is None:
        check("PedicleScrewPlanner's DefineROIStep page was scanned", False)
        return scans

    by_attr = {c.get("attr"): c for c in roi.get("combos") or []}
    check("the checkable combo is in the inventory", "lSelector" in by_attr,
          sorted(by_attr))
    levels = by_attr.get("lSelector") or {}
    check("it is recorded as multi-select", bool(levels.get("multi_select")))
    check("its Qt class is carried", levels.get("widget_class") == "ctkCheckableComboBox",
          levels.get("widget_class"))
    check("its options are the control's own", "T3" in (levels.get("items") or [])
          and "C1" in (levels.get("items") or []))
    # The label is what the cookbook's quote is matched against, and this page
    # lays out `for column, (label, widget) in enumerate(fields)` -- no layout
    # call names either object, so only the pair literal can recover it.
    check("the pair-literal rule recovered its label",
          levels.get("label") == "Instrumented Levels:", levels.get("label"))
    check("and its siblings' labels too",
          (by_attr.get("sSelector") or {}).get("label") == "# Sides:"
          and (by_attr.get("aSelector") or {}).get("label") == "Approach Direction:")

    # A label is only ever RECOVERED, never invented: every non-empty label must
    # be a QLabel string that really appears in that page's source.
    invented = []
    for name, scan in sorted(scans.items()):
        for page_class, page in (scan.get("wizard_pages") or {}).items():
            source = _page_source(scan, page_class)
            for combo in page.get("combos") or []:
                label = str(combo.get("label") or "")
                if label and source is not None and label not in source:
                    invented.append("%s/%s/%s=%r"
                                    % (name, page_class, combo.get("attr"), label))
    check("no label is invented -- each appears verbatim in its page's source",
          not invented, invented[:4])
    return scans


def _page_source(scan, page_class):
    path = ((scan.get("wizard") or {}).get("page_files") or {}).get(page_class)
    if not path or not os.path.exists(path):
        return None
    with io.open(path, encoding="utf-8", errors="ignore") as f:
        return f.read()


# --------------------------------------------------------------------------
# 2. Stage 4 turns the scanned control into a multi-select choice item
# --------------------------------------------------------------------------
def section_stage4(ns, scans):
    print("[2] stage 4: the reconciler marks it, and a LONE one is enough")
    mixin = ns["AnalyzerStage4DecompositionMixin"]

    def reconcile(pages, description, sub_ops=None):
        inst = mixin()
        inst._wizard = {"present": True}
        inst._wizard_pages = pages
        return inst._reconcile_multi_choice(
            sub_ops or [{"op_type": "user_choice", "question": description,
                         "choices": [], "parameter_name": "choice_step_4",
                         "value_kind": ""}],
            description)

    pages = {}
    for name in ("PedicleScrewPlanner", "PedicleScrewSimulator"):
        found = (scans.get(name) or {}).get("wizard_pages") or {}
        if "DefineROIStep" in found:
            pages = found
            break
    if not pages:
        check("the reference wizard pages are available", False)
        return

    # The real cookbook sentence for the step this was written for.
    description = ('Choose the "Instrumented Levels:". Choose the "# Sides:". '
                   'Choose the "Approach Direction:".')
    rebuilt = reconcile(pages, description)
    check("the 3-selector step rebuilds into 3 items", len(rebuilt) == 3,
          len(rebuilt))
    by_param = {so.get("parameter_name"): so for so in rebuilt}
    levels = by_param.get("instrumented_levels")
    check("the levels selector is named from its own label", levels is not None,
          sorted(by_param))
    if levels is not None:
        check("it is marked multi_select", bool(levels.get("multi_select")))
        check("its value_kind says so too", levels.get("value_kind") == "multi_select")
        check("it carries the source class",
              levels.get("widget_class") == "ctkCheckableComboBox")
        check("its choices are the control's own options",
              [c["value"] for c in levels["choices"]][:3] == ["C1", "C2", "C3"])
    sides = by_param.get("sides")
    check("an ordinary sibling stays single-pick",
          sides is not None and not sides.get("multi_select")
          and sides.get("value_kind") == "")

    # A LONE quoted multi-select control is enough evidence to rebuild -- the
    # alternative is not "some other control" but "this control, as a dropdown".
    lone = reconcile(pages, 'Choose the "Instrumented Levels:".')
    check("a lone multi-select match rebuilds the step", len(lone) == 1
          and bool(lone[0].get("multi_select")), lone)

    # ...and a lone PLAIN match still does not: one quote is not evidence that the
    # LLM's sub-op is about that combo, and rebuilding would replace whatever
    # renderer the step legitimately had.
    plain = reconcile(pages, 'Choose the "# Sides:".')
    check("a lone single-pick match is left alone",
          len(plain) == 1 and plain[0].get("parameter_name") == "choice_step_4",
          plain)

    # A step that asks several questions but whose OTHER controls were not found
    # must not be rebuilt around the one that was: the result would answer one
    # question and never ask the rest, which looks right on screen. The unmatched
    # quote here names no control on any page.
    partial = reconcile(pages, 'Choose the "Instrumented Levels:". Then press "Compute the plan".')
    check("a partial match is refused, not silently narrowed",
          len(partial) == 1 and partial[0].get("parameter_name") == "choice_step_4",
          partial)

    # A classic (non-wizard) extension is untouched whatever its text quotes.
    inst = mixin()
    inst._wizard = {"present": False}
    inst._wizard_pages = {}
    original = [{"op_type": "user_choice", "question": "q", "choices": [],
                 "parameter_name": "p"}]
    check("classic extensions pass through byte-identical",
          inst._reconcile_multi_choice(original, 'the "A" and the "B"') is original)


# --------------------------------------------------------------------------
# 3. The two mirrors agree on what "multi-select" means
# --------------------------------------------------------------------------
def _load_choice_helpers():
    import json as _json
    import logging as _logging
    import re as _re
    from typing import Any, Dict, List, Optional
    ns = {"__name__": "check_multi_select_helpers", "re": _re, "json": _json,
          "os": os, "logging": _logging, "List": List, "Dict": Dict, "Any": Any,
          "Optional": Optional,
          "_workflow_choices": {}, "_workflow_repeat_state": {},
          "_find_next_step_local": lambda *a, **k: None,
          "logger": types.SimpleNamespace(debug=lambda *a, **k: None,
                                          info=lambda *a, **k: None,
                                          warning=lambda *a, **k: None)}
    with io.open(os.path.join(LOADER, "choice_helpers.py"), encoding="utf-8") as f:
        src = f.read()
    for line in ("from .cache import *",
                 "from .templates import _workflow_choices, _workflow_repeat_state",
                 "from .workflow_state import _find_next_step_local"):
        src = src.replace(line, "")
    exec(compile(src, "choice_helpers.py", "exec"), ns)
    return ns


def _runtime_multi_select_classes():
    """``WorkflowRuntime._MULTI_SELECT_WIDGET_CLASSES``, read from the source.

    The module imports slicer, so it is read as AST rather than imported -- the
    same reason the other Slicer-free checkers exist.
    """
    path = os.path.join(REPO, "SlicerAIAgentLib", "WorkflowRuntime.py")
    with io.open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "_MULTI_SELECT_WIDGET_CLASSES":
                return tuple(_const(el) for el in node.value.elts)
    return None


def _const(node):
    if isinstance(node, ast.Str):                 # dev interpreter is 3.7
        return node.s
    return getattr(node, "value", None)


def section_mirrors(helpers):
    print("[3] the runtime and loader mirrors agree")
    runtime_classes = _runtime_multi_select_classes()
    check("WorkflowRuntime declares the class list", bool(runtime_classes),
          runtime_classes)
    check("the loader's mirror matches it exactly",
          tuple(helpers["_MULTI_SELECT_WIDGET_CLASSES"]) == runtime_classes,
          (helpers["_MULTI_SELECT_WIDGET_CLASSES"], runtime_classes))
    # findChildren matches className() EXACTLY, so a QComboBox subclass is not
    # found under "QComboBox" -- the search list must name it.
    for cls in runtime_classes or ():
        check("the live search looks for %s" % cls,
              cls in helpers["_COMBO_SEARCH_CLASSES"],
              helpers["_COMBO_SEARCH_CLASSES"])

    is_multi = helpers["_item_is_multi_select"]
    check("the recorded flag is enough", is_multi({"multi_select": True}))
    check("the source class alone is enough (a classic .ui yields no flag)",
          is_multi({"widget_class": "ctkCheckableComboBox"}))
    check("an ordinary combo is not multi-select", not is_multi({"widget_class": "QComboBox"}))
    check("an empty item is not multi-select", not is_multi({}) and not is_multi(None))

    items_for = helpers["_multi_choice_items_for_step"]

    class Ctx(object):
        def __init__(self, step):
            self.target_step = step
            self.ext_name = "Ext"
            self.workflow_step = "cb_step_4"
            self.metadata = {"extension_module_name": "Ext"}
            self.tool_name = "tool"

    lone = {"choice_info": {"parameter_name": "p", "widget_class": "ctkCheckableComboBox"}}
    check("a lone tick list reaches the multi-selection commit path",
          len(items_for(Ctx(lone))) == 1)
    plain = {"choice_info": {"parameter_name": "p", "widget_class": "QComboBox"}}
    check("a lone ordinary selector does not", items_for(Ctx(plain)) == [])
    pair = {"choice_info_list": [{"parameter_name": "a"}, {"parameter_name": "b"}]}
    check("two ordinary selectors still do", len(items_for(Ctx(pair))) == 2)


# --------------------------------------------------------------------------
# 4. The emitted drive code really ticks the extension's own control
# --------------------------------------------------------------------------
class _Qt(object):
    Checked = 2
    Unchecked = 0
    CheckStateRole = 10


class _EventLoop(object):
    ExcludeUserInputEvents = 1


class _Model(object):
    def __init__(self, combo):
        self.combo = combo

    def index(self, row, col):
        return row

    def data(self, index, role=None):
        return self.combo.items[index]

    def setData(self, index, value, role=None):
        self.combo.states[index] = value
        return True


class _Combo(object):
    """A plain one-of-N combo: setCheckState/checkedIndexes do not exist on it."""

    def __init__(self, items, cls="QComboBox"):
        self.items = list(items)
        self.states = [_Qt.Unchecked] * len(self.items)
        self._cls = cls
        self.current = ""
        self.activated_with = []

    def className(self):
        return self._cls

    @property
    def count(self):
        return len(self.items)

    def itemText(self, i):
        return self.items[i]

    def model(self):
        return _Model(self)

    def setCurrentText(self, text):
        self.current = text

    @property
    def currentIndex(self):
        return self.items.index(self.current) if self.current in self.items else -1

    def activated(self, arg):
        self.activated_with.append(arg)

    def setCheckState(self, index, state):
        raise AttributeError("not checkable")

    def checkedIndexes(self):
        raise AttributeError("not checkable")


class _CheckableCombo(_Combo):
    def __init__(self, items):
        _Combo.__init__(self, items, cls="ctkCheckableComboBox")

    def setCheckState(self, index, state):
        self.states[index] = state

    def checkedIndexes(self):
        return [i for i, st in enumerate(self.states) if st == _Qt.Checked]

    def ticked(self):
        return [self.items[i] for i in self.checkedIndexes()]


def _env(widgets):
    qt_mod = types.ModuleType("qt")
    qt_mod.Qt = _Qt
    qt_mod.QEventLoop = _EventLoop
    slicer_mod = types.ModuleType("slicer")

    class _Util(object):
        def getModule(self, name):
            return self

        def widgetRepresentation(self):
            return "ROOT"

        def findChildren(self, root, className=""):
            return [w for w in widgets if w.className() == className]

    class _App(object):
        @staticmethod
        def processEvents(*a, **k):
            return None

    slicer_mod.util = _Util()
    slicer_mod.app = _App()
    sys.modules["qt"] = qt_mod
    sys.modules["slicer"] = slicer_mod
    return {"__name__": "__main__", "qt": qt_mod, "slicer": slicer_mod}


LEVELS = ["C1", "C2", "C3", "T1", "T2", "T3", "T4", "L1"]
SIDES = ["L&R", "Left", "Right", "--"]


def section_drive(helpers):
    print("[4] the emitted drive code, executed against fake controls")
    build = helpers["_build_multi_choice_drive_code"]

    class Ctx(object):
        target_step = {}
        ext_name = "Ext"
        workflow_step = "cb_step_4"
        metadata = {"extension_module_name": "Ext"}
        tool_name = "tool"

    levels_pick = {"param": "c_levels", "value": ["T2", "T4"], "options": LEVELS,
                   "anchor": "instrumented levels", "multi_select": True,
                   "widget_class": "ctkCheckableComboBox"}
    sides_pick = {"param": "c_sides", "value": "Left", "options": SIDES,
                  "anchor": "# sides", "multi_select": False,
                  "widget_class": "QComboBox"}

    code = build(Ctx(), [levels_pick, sides_pick])
    try:
        compile(code, "<drive>", "exec")
        compiled = True
    except SyntaxError as exc:                                  # pragma: no cover
        compiled = False
        print(code)
        print(exc)
    check("the emitted code compiles", compiled)
    if not compiled:
        return

    levels, sides = _CheckableCombo(LEVELS), _Combo(SIDES)
    exec(compile(code, "<drive>", "exec"), _env([levels, sides]))
    check("exactly the chosen options are ticked", levels.ticked() == ["T2", "T4"],
          levels.ticked())
    check("the single-pick sibling is unaffected by the new branch",
          sides.current == "Left" and sides.activated_with)

    # A second pass must SET the state, not add to it: a replay or a corrected
    # answer that only ever added would keep every level ever ticked.
    exec(compile(build(Ctx(), [dict(levels_pick, value=["C2"])]), "<again>", "exec"),
         _env([levels, sides]))
    check("re-driving replaces rather than accumulates", levels.ticked() == ["C2"],
          levels.ticked())

    # The class filter: a plain combo listing the same options must never be the
    # one that gets ticked (both would pass the item-set match).
    decoy, real = _Combo(LEVELS), _CheckableCombo(LEVELS)
    exec(compile(build(Ctx(), [dict(levels_pick, value=["T3"])]), "<pick>", "exec"),
         _env([decoy, real]))
    check("a same-options decoy is not ticked",
          real.ticked() == ["T3"] and decoy.states == [_Qt.Unchecked] * len(LEVELS))

    # No control found at all -- must raise, because the panel would otherwise
    # show the answer while the extension reads its factory default.
    raised = ""
    try:
        exec(compile(build(Ctx(), [dict(levels_pick, value=["T3"])]), "<miss>", "exec"),
             _env([_Combo(LEVELS)]))
    except RuntimeError as exc:
        raised = str(exc)
    check("a miss raises, naming the selector", "c_levels" in raised, raised)

    # A control that accepts setCheckState and reports nothing ticked is the same
    # failure wearing a disguise: only the read-back catches it.
    class _Liar(_CheckableCombo):
        def setCheckState(self, index, state):
            return None

    raised = ""
    try:
        exec(compile(build(Ctx(), [dict(levels_pick, value=["T3"])]), "<liar>", "exec"),
             _env([_Liar(LEVELS)]))
    except RuntimeError as exc:
        raised = str(exc)
    check("a control that silently ignores the write is caught by the read-back",
          "c_levels" in raised, raised)


# --------------------------------------------------------------------------
# 5. The panel renders a tick list, and only commits a ticked one
# --------------------------------------------------------------------------
def section_panel():
    print("[5] the panel: the render branch and the commit rule")
    path = os.path.join(REPO, "SlicerAIAgentLib", "app", "widget_workflow.py")
    with io.open(path, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}

    for name in ("_buildMultiSelectControl", "_multiSelectCheckedTexts",
                 "_setMultiSelectChecked"):
        check("the panel defines %s" % name, name in funcs)

    render = funcs.get("_renderWorkflowMultiChoiceForm")
    check("the form renderer exists", render is not None)
    if render is not None:
        src = ast.dump(render)
        check("it branches on the item's multi_select fact", "multi_select" in src)
        # The form is the ONLY renderer that can show a tick list, so it must not
        # turn a one-item step away -- that item would fall through to the
        # single-choice renderers and become a dropdown.
        check("it does not require two selectors",
              "len(items) < 2" not in ast.dump(render))

    confirm = funcs.get("_onWorkflowMultiChoiceConfirmed")
    check("the confirm handler reads the tick list",
          confirm is not None and "_multiSelectCheckedTexts" in ast.dump(confirm))

    # A tick list with nothing ticked contributes no value, so the existing
    # "every selector answered" gate refuses the commit -- the same rule the
    # source extension applies in its own validate().
    fallback = ast.dump(funcs["_buildMultiSelectControl"]) if "_buildMultiSelectControl" in funcs else ""
    check("there is a fallback for a build without the ctk class",
          "QListWidget" in fallback)


# --------------------------------------------------------------------------
# 6. A selector starts where its SOURCE control starts
# --------------------------------------------------------------------------
_PAGE_TEMPLATE = """
from __main__ import qt, ctk, slicer


class SyntheticStep(object):
    def createUserInterface(self):
        aText = qt.QLabel("Approach:")
        self.aSelector = qt.QComboBox()
        self.aSelector.addItems(['Posterior', 'Anterior', 'Left', 'Right'])
%(setup)s
        self.__layout.addRow(aText, self.aSelector)
"""


def _synthetic_default(ns, tmpdir, setup):
    """Scan a one-combo page whose setup line is ``setup``; return the recorded combo."""
    path = os.path.join(tmpdir, "SyntheticStep.py")
    with io.open(path, "w", encoding="utf-8") as handle:
        handle.write(_PAGE_TEMPLATE % {"setup": setup})
    pages = ns["AnalyzerScanMixin"]._scan_wizard_pages(
        {"present": True, "page_files": {"SyntheticStep": path}})
    combos = {c.get("attr"): c
              for c in (pages.get("SyntheticStep") or {}).get("combos", [])}
    return combos.get("aSelector") or {}


def section_defaults(ns, scans):
    print("[6] the selector's own default: carried when it is real, withheld when it is a prompt")
    pages = {}
    for name in ("PedicleScrewPlanner", "PedicleScrewSimulator"):
        found = (scans.get(name) or {}).get("wizard_pages") or {}
        if "DefineROIStep" in found:
            pages = found
            break
    if not pages:
        check("the reference wizard pages are available", False)
        return

    mixin = ns["AnalyzerStage4DecompositionMixin"]

    def reconcile(description):
        inst = mixin()
        inst._wizard = {"present": True}
        inst._wizard_pages = pages
        return inst._reconcile_multi_choice(
            [{"op_type": "user_choice", "question": description, "choices": [],
              "parameter_name": "choice_step", "value_kind": ""}], description)

    # (a) The ROI page: two ordinary combos that really do open on an option, and
    #     one checkable combo that opens on nothing ticked.
    roi = {so.get("parameter_name"): so for so in reconcile(
        'Choose the "Instrumented Levels:". Choose the "# Sides:". '
        'Choose the "Approach Direction:".')}
    check("the sides selector carries the option the page opens on",
          (roi.get("sides") or {}).get("default_value") == "L&R",
          (roi.get("sides") or {}).get("default_value"))
    check("so does the approach selector",
          (roi.get("approach_direction") or {}).get("default_value") == "Posterior",
          (roi.get("approach_direction") or {}).get("default_value"))
    # A tick list starts EMPTY -- "the first level" is not an answer the extension
    # gives, and pre-ticking one would instrument a level nobody chose.
    check("a checkable selector carries no default",
          (roi.get("instrumented_levels") or {}).get("default_value") is None,
          (roi.get("instrumented_levels") or {}).get("default_value"))

    # (b) The Measurements page: both selectors open on a PROMPT, and the prompt
    #     is dropped from the options -- so there is no default to carry and the
    #     panel keeps its placeholder. This is the case that must NOT regress: the
    #     diameter handler deletes and rebuilds the screw line at a default
    #     position, so a pre-selected value would silently move a screw the
    #     surgeon already fixed on an earlier pass of the loop.
    meas = {so.get("parameter_name"): so for so in reconcile(
        'Choose the "Choose the puncture site". Choose the "Select screw diametermm".')}
    check("a prompt-led selector is left unanswered",
          bool(meas) and all(so.get("default_value") is None for so in meas.values()),
          dict((k, v.get("default_value")) for k, v in meas.items()))
    # ...and it is the PROMPT that withholds it, not a lack of items: that combo
    # has eight real options behind its prompt row.
    diameter = meas.get("select_screw_diametermm") or {}
    check("even though that selector has real options behind the prompt",
          len(diameter.get("choices") or []) >= 4,
          len(diameter.get("choices") or []))

    # (c) Every shipped extension: a recovered default must be one of the options
    #     the same item offers. A default outside its own list is the one shape
    #     the panel cannot render -- it would fall back to the placeholder without
    #     saying so.
    stray = []
    for name, scan in sorted(scans.items()):
        for page_class, page in (scan.get("wizard_pages") or {}).items():
            for combo in page.get("combos") or []:
                items = [str(i) for i in (combo.get("items") or [])]
                if not items:
                    continue
                value = mixin._combo_default_option(combo, items)
                if value is not None and value not in items:
                    stray.append("%s/%s/%s=%r"
                                 % (name, page_class, combo.get("attr"), value))
    check("no recovered default is outside its own option list", not stray, stray[:4])

    # (d) The spellings of "what this control opens on", on synthetic pages: no
    #     explicit call (Qt selects item 0), the setter, PythonQt's property form
    #     -- and the two that must NOT be taken: a non-literal argument is not a
    #     fact about the startup state, and a handler re-pointing the combo later
    #     is a fact about a run.
    tmpdir = os.path.join(REPO, "logs", "_check_multi_select_tmp")
    try:
        if not os.path.isdir(tmpdir):
            os.makedirs(tmpdir)
        opts = ["Posterior", "Anterior", "Left", "Right"]
        implicit = _synthetic_default(ns, tmpdir, "")
        check("no explicit call -> item 0, which is what Qt itself selects",
              mixin._combo_default_option(implicit, opts) == "Posterior", implicit)
        setter = _synthetic_default(ns, tmpdir, "        self.aSelector.setCurrentIndex(2)")
        check("setCurrentIndex(2) is read",
              setter.get("default_index") == 2
              and mixin._combo_default_option(setter, opts) == "Left", setter)
        text = _synthetic_default(ns, tmpdir,
                                  "        self.aSelector.setCurrentText('Right')")
        check("setCurrentText is read",
              mixin._combo_default_option(text, opts) == "Right", text)
        prop = _synthetic_default(ns, tmpdir, "        self.aSelector.currentIndex = 1")
        check("PythonQt's property spelling is read too",
              mixin._combo_default_option(prop, opts) == "Anterior", prop)
        dynamic = _synthetic_default(
            ns, tmpdir, "        self.aSelector.setCurrentIndex(self.lastUsed)")
        check("a non-literal index is ignored, not guessed",
              dynamic.get("default_index") is None
              and mixin._combo_default_option(dynamic, opts) == "Posterior", dynamic)
        rebound = _synthetic_default(
            ns, tmpdir,
            "        self.aSelector.setCurrentIndex(3)\n"
            "\n    def onSomethingElse(self):\n"
            "        self.aSelector.setCurrentIndex(1)")
        check("a later handler does not overwrite the startup selection",
              rebound.get("default_index") == 3, rebound)
    finally:
        for name in (os.listdir(tmpdir) if os.path.isdir(tmpdir) else []):
            try:
                os.remove(os.path.join(tmpdir, name))
            except OSError:
                pass
        try:
            os.rmdir(tmpdir)
        except OSError:
            pass

    # (e) The panel: the placeholder row is CONDITIONAL on the default, and the
    #     voice half agrees about what "answered" means. A voice check reading
    #     `currentIndex <= 0` would call a defaulted selector unanswered forever --
    #     the form would never confirm and nothing would say why.
    path = os.path.join(REPO, "SlicerAIAgentLib", "app", "widget_workflow.py")
    with io.open(path, encoding="utf-8") as handle:
        tree = ast.parse(handle.read())
    funcs = dict((n.name, n) for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
    render = (ast.dump(funcs["_renderWorkflowMultiChoiceForm"])
              if "_renderWorkflowMultiChoiceForm" in funcs else "")
    check("the form reads the item's default_value", "default_value" in render)
    check("and the placeholder row is conditional on it",
          "_MULTI_CHOICE_PLACEHOLDER" in render and "default" in render)

    vpath = os.path.join(REPO, "SlicerAIAgentLib", "app", "widget_voice.py")
    with io.open(vpath, encoding="utf-8") as handle:
        vtree = ast.parse(handle.read())
    vfuncs = dict((n.name, n) for n in ast.walk(vtree) if isinstance(n, ast.FunctionDef))
    apply_multi = (ast.dump(vfuncs["_voiceApplyMulti"])
                   if "_voiceApplyMulti" in vfuncs else "")
    check("voice decides 'answered' by the value, not by the index",
          "_MULTI_CHOICE_PLACEHOLDER" in apply_multi
          and "currentIndex" not in apply_multi,
          "reads currentIndex" if "currentIndex" in apply_multi else "no placeholder read")


def main():
    print(__doc__.strip().splitlines()[0])
    print("")
    ns = _load_analyzer()
    scans = section_scan(ns)
    print("")
    section_stage4(ns, scans)
    print("")
    helpers = _load_choice_helpers()
    section_mirrors(helpers)
    print("")
    section_drive(helpers)
    print("")
    section_panel()
    print("")
    section_defaults(ns, scans)

    print("")
    print("checks run: %d" % _checks[0])
    if _failures:
        print("FAILED: %s" % ", ".join(_failures))
        return 1
    print("all multi-select choice checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
