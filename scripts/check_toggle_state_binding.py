"""A control the extension reads as a COMPARISON is still a bound control.

An extension states the same fact about a checkbox in two spellings. Most write
the attribute truth test::

    if self.ui.showOriginalMandibleCheckBox.checked:
        parameterNode.SetParameter("showOriginalMandible", "True")

and some write a comparison, because the control's state is not a bool::

    if self.ui.generateFibula...Button.checkState == qt.Qt.Checked:
        parameterNode.SetParameter("updateOnMandiblePlanesMovement", "True")

``_extract_ui_parameter_bindings`` read only the first form, so the second-form
control was ABSENT from the binding table -- and everything downstream of that is
silent. The step gets no ``ui_parameter_binding``, so the deterministic toggle
emitter never fires, so the step falls through to free-form generation, which is
free to guess. On BoneReconstructionPlanner it guessed ``'true'``; the extension
compares ``GetParameter(role) == "True"`` against an exact string, so the
parameter was set, the read was False forever, and the observer it gates
(``onPlaneModifiedTimer`` -> regenerate the fibula) never ran. Nothing raised.
The symptom landed two steps later and looked like a different feature: dragging
a mandibular cut plane no longer updated the fibula bone pieces.

Two halves, and BOTH must hold, because each one alone still fails silently:

* the parameter's ON/OFF string is READ from the source, never assumed -- an
  extension's spelling is its own (``"True"`` here, but nothing forbids ``"1"``);
* the CONTROL is driven on the property the source uses. ``checkState`` is a
  tri-state enum, and on a ``ctkCheckablePushButton`` -- a QPushButton subclass
  whose indicator is separate from the button's own checked state -- writing
  ``checked = True`` raises nothing and ticks nothing. An unticked control is not
  cosmetic: every sibling control wired on ``stateChanged`` re-runs
  ``updateParameterNodeFromGUI``, which reads this control and ratchets the
  parameter back to "False".

Runs OUTSIDE Slicer (these scans are pure AST) over all nine cookbook
extensions, so "the mechanism is generic" is checkable rather than asserted::

    python scripts/check_toggle_state_binding.py
"""
import ast
import importlib
import importlib.util
import os
import sys
import types

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXT_ROOT = os.path.normpath(os.path.join(REPO, "..", "External_extensions"))

# ---------------------------------------------------------------------------
# The dev machine's python is 3.7, whose parser still emits ast.Str / ast.Num /
# ast.NameConstant. The code under test runs inside Slicer (3.9+), where every
# literal is an ast.Constant -- and an `isinstance(x, ast.Constant)` check does
# not error on 3.7, it silently matches nothing. Normalising the tree at parse
# time tests the code as Slicer runs it; weakening the code to suit 3.7 would
# not. On 3.8+ this is a no-op.
# ---------------------------------------------------------------------------
_LEGACY_LITERALS = tuple(
    getattr(ast, name) for name in ("Str", "Bytes", "Num", "NameConstant", "Ellipsis")
    if hasattr(ast, name)
)


def _as_constant(node):
    if isinstance(node, (getattr(ast, "Str", ()), getattr(ast, "Bytes", ()))):
        value = node.s
    elif isinstance(node, getattr(ast, "Num", ())):
        value = node.n
    elif isinstance(node, getattr(ast, "NameConstant", ())):
        value = node.value
    elif isinstance(node, getattr(ast, "Ellipsis", ())):
        value = Ellipsis
    else:
        return node
    return ast.copy_location(ast.Constant(value=value, kind=None), node)


def _install_constant_normalizer():
    if sys.version_info >= (3, 8):
        return
    original = ast.parse

    def parse(*args, **kwargs):
        tree = original(*args, **kwargs)
        for node in ast.walk(tree):
            for field, old in ast.iter_fields(node):
                if isinstance(old, list):
                    setattr(node, field, [
                        _as_constant(item) if isinstance(item, _LEGACY_LITERALS) else item
                        for item in old
                    ])
                elif isinstance(old, _LEGACY_LITERALS):
                    setattr(node, field, _as_constant(old))
        return tree

    ast.parse = parse


_install_constant_normalizer()

# The analyzer submodules imported WITHOUT running SlicerAIAgentLib/__init__.py
# (which reaches Qt) or the package __init__ (which pulls the whole LLM
# pipeline). The scans themselves are Slicer-free, so a stub package with
# __path__ set resolves their relative imports against the real files -- this
# script exercises the PRODUCTION scan and the PRODUCTION emitter; a copy of
# either rule here would answer confidently about code the pipeline no longer
# runs.
_pkg = types.ModuleType("_eca")
_pkg.__path__ = [os.path.join(REPO, "SlicerAIAgentLib", "extension_cli_analyzer")]
sys.modules["_eca"] = _pkg
_common = importlib.import_module("_eca.common")
_scan = importlib.import_module("_eca.scan")
_node_lifecycle = importlib.import_module("_eca.node_lifecycle")
_cookbook_mapping = importlib.import_module("_eca.cookbook_mapping")
_parameter_metadata = importlib.import_module("_eca.parameter_metadata")
_template_helpers = importlib.import_module("_eca.template_helpers")
_stage4 = importlib.import_module("_eca.stage4_decomposition")
_workflow_templates = importlib.import_module("_eca.workflow_templates")
_validation_semantics = importlib.import_module("_eca.validation_semantics")

_cv_spec = importlib.util.spec_from_file_location(
    "_code_validator", os.path.join(REPO, "SlicerAIAgentLib", "CodeValidator.py")
)
_cv = importlib.util.module_from_spec(_cv_spec)
_cv_spec.loader.exec_module(_cv)


class _Analyzer(
    _scan.AnalyzerScanMixin,
    _node_lifecycle.AnalyzerNodeLifecycleMixin,
    _cookbook_mapping.AnalyzerCookbookMappingMixin,
    _parameter_metadata.AnalyzerParameterMetadataMixin,
    _template_helpers.AnalyzerTemplateHelpersMixin,
    _stage4.AnalyzerStage4DecompositionMixin,
    _workflow_templates.AnalyzerWorkflowTemplatesMixin,
    _validation_semantics.AnalyzerValidationSemanticsMixin,
):
    """The production mixins, composed the way analyzer.py composes them."""


def _new_analyzer():
    analyzer = _Analyzer()
    analyzer._parameter_appliers = {}
    analyzer._parameter_node_wrapper = {}
    analyzer._widget_parameter_bindings = {}
    analyzer._workflow_metadata = {}
    return analyzer


def _entry_module_and_ui(ext_dir):
    """The module's widget source and its .ui files, the way discover finds them."""
    entry, longest = None, -1
    ui_files = []
    for root, _dirs, names in os.walk(ext_dir):
        for name in names:
            path = os.path.join(root, name)
            if name.endswith(".ui"):
                ui_files.append(path)
            elif name.endswith(".py"):
                try:
                    text = open(path, encoding="utf-8", errors="replace").read()
                except Exception:
                    continue
                if "ScriptedLoadableModuleWidget" in text and len(text) > longest:
                    entry, longest = path, len(text)
    return entry, ui_files


failures = []
notes = []
checked = 0


def check(condition, message):
    global checked
    checked += 1
    if not condition:
        failures.append(message)


# ── 1. Polarity, over every spelling a source can use ────────────────────────
# The comparison form has an operand order and a negation, and reading either
# backwards inverts the step: "tick this box" would untick it, which is the one
# way this mechanism can be worse than not existing.
_POLARITY_CASES = [
    ("self.ui.box.checked", ("box", "checked", True)),
    ("not self.ui.box.checked", ("box", "checked", False)),
    ("self.ui.box.checkState == qt.Qt.Checked", ("box", "checkState", True)),
    ("qt.Qt.Checked == self.ui.box.checkState", ("box", "checkState", True)),
    ("self.ui.box.checkState != qt.Qt.Checked", ("box", "checkState", False)),
    ("self.ui.box.checkState == qt.Qt.Unchecked", ("box", "checkState", False)),
    ("self.ui.box.checkState != qt.Qt.Unchecked", ("box", "checkState", True)),
    ("self.ui.box.checkState == 2", ("box", "checkState", True)),
    ("self.ui.box.checkState == 0", ("box", "checkState", False)),
    ("not (self.ui.box.checkState == 2)", ("box", "checkState", False)),
    ("self.ui.box.checked is True", ("box", "checked", True)),
    ("self.ui.box.checked is not True", ("box", "checked", False)),
    ("self.ui.box.enabled == True", ("box", "enabled", True)),
    # Undecidable or out of scope: record NOTHING rather than guess a polarity
    # that cannot be recovered. A wrong guess here ships an inverted step.
    ("self.ui.box.checkState == qt.Qt.PartiallyChecked", ("", "", None)),
    ("self.ui.box.checkState == someLocalState", ("", "", None)),
    ("self.ui.combo.currentIndex == 0", ("", "", None)),
    ("self.ui.spin.value > 3", ("", "", None)),
    ("self.ui.box.checked and self.ui.other.checked", ("", "", None)),
]

_analyzer = _new_analyzer()
for expression, expected in _POLARITY_CASES:
    tree = ast.parse(expression, mode="eval")
    widget, prop, polarity = _analyzer._widget_state_test(tree.body)
    if expected[0] == "":
        check(widget == "", "%r must yield no binding, got (%r, %r, %r)"
                            % (expression, widget, prop, polarity))
    else:
        check((widget, prop, polarity) == expected,
              "%r read as (%r, %r, %r), expected %r"
              % (expression, widget, prop, polarity, expected))

# ── 2. The real source: the control that was invisible must be bound ─────────
BRP_DIR = os.path.join(EXT_ROOT, "SlicerBoneReconstructionPlanner")
if not os.path.isdir(BRP_DIR):
    print("SKIP: %s not present; nothing to check against." % BRP_DIR)
    sys.exit(0)

brp_entry, brp_ui = _entry_module_and_ui(BRP_DIR)
check(brp_entry is not None, "no widget source found under %s" % BRP_DIR)
brp_source = open(brp_entry, encoding="utf-8", errors="replace").read()
brp_bindings = _new_analyzer()._extract_ui_parameter_bindings(brp_source, brp_ui, [])

COMPARISON_CONTROLS = {
    # widget object name -> (role, property, on string, off string)
    "generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton":
        ("updateOnMandiblePlanesMovement", "checkState", "True", "False"),
    "updateFibulaDentalImplantCylindersButton":
        ("updateOnDentalImplantPlanesMovement", "checkState", "True", "False"),
}
for widget_name, (role, prop, on_text, off_text) in COMPARISON_CONTROLS.items():
    binding = brp_bindings.get(widget_name)
    check(binding is not None,
          "%s is not bound: a control read as a comparison is still a bound control."
          % widget_name)
    if not binding:
        continue
    entry = None
    for candidate in binding.get("roles") or []:
        if candidate.get("parameter_name") == role:
            entry = candidate
            break
    check(entry is not None, "%s has no role for %s" % (widget_name, role))
    if not entry:
        continue
    check(entry.get("value_property") == prop,
          "%s: property is %r, source reads %r"
          % (widget_name, entry.get("value_property"), prop))
    # Both spellings on ONE role entry: downstream reads roles[0], so an
    # else-branch appended as a second dict is an off value nobody ever sees.
    check(entry.get("true_value") == on_text and entry.get("false_value") == off_text,
          "%s: on/off strings are %r/%r, source writes %r/%r"
          % (widget_name, entry.get("true_value"), entry.get("false_value"),
             on_text, off_text))
    form = entry.get("write_form") or {}
    check(form.get("on") == "2" and form.get("off") == "0",
          "%s: write form is %r, the extension writes checkState = 2 / 0"
          % (widget_name, form))

# ── 3. The emitted step: the two halves of the fix ───────────────────────────
STEP_28 = ('Tick the "Update fibula planes over fibula line; update fibula bone '
           'pieces and transform them to mandible" checkbox.')


def _emit(analyzer, step_id, description, extension_name="BoneReconstructionPlanner",
          logic_class="BoneReconstructionPlannerLogic", module_name="BoneReconstructionPlanner"):
    """Cookbook line -> the template the pipeline would ship, or None."""
    candidates = analyzer._match_ui_parameter_bindings(description)
    if not candidates:
        return None, None
    top = candidates[0]
    final_state = _common._infer_final_state_intent(description)
    if not analyzer._should_apply_ui_parameter_candidate(top, final_state, description):
        return None, top
    role = top.get("role") or {}
    sub_op = {
        "op_type": "extension_op",
        "operation_intent": analyzer._ui_binding_operation_intent(top),
        "parameter_name": role.get("parameter_name", ""),
        "value_property": role.get("value_property", ""),
        "target_value": final_state.get("state"),
        "target_value_mode": final_state.get("mode"),
        "ui_parameter_binding": top,
    }
    step = {"step_id": step_id, "description": description, "sub_operations": [sub_op]}
    return analyzer._generate_parameter_update_template(
        extension_name, step, logic_class, module_name), top


brp_analyzer = _new_analyzer()
brp_analyzer._ui_parameter_bindings = brp_bindings
code_28, candidate_28 = _emit(brp_analyzer, "cb_step_28", STEP_28)

check(candidate_28 is not None and candidate_28.get("widget_name")
      == "generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton",
      "step 28 matches %r, not the control its own words quote"
      % (candidate_28 or {}).get("widget_name"))
check(code_28 is not None,
      "step 28 produced no deterministic template; it would fall through to "
      "free-form generation, which is where 'true' came from.")

if code_28:
    check("parameterNode.SetParameter('updateOnMandiblePlanesMovement', 'True')" in code_28,
          "step 28 does not write the source's own ON string.")
    check("'true'" not in code_28,
          "step 28 writes a lowercase 'true'; the extension compares == \"True\".")
    check("_sync_ctrl.checkState = 2" in code_28,
          "step 28 does not tick the control on the property the source uses.")
    check("_sync_ctrl.checked" not in code_28,
          "step 28 writes .checked on a ctkCheckablePushButton, which ticks nothing.")
    check("parameterNode.Modified()" in code_28,
          "step 28 never fires the parameter observer that repaints the GUI.")

# Step 27 clicks the SAME control to run the action once. It states no final
# state, so it must NOT be captured as a parameter update -- that would replace
# a one-shot reconstruction with a checkbox tick.
STEP_27 = ('Click "Update fibula planes over fibula line; update fibula bone pieces '
           'and transform them to mandible" to generate the reconstruction and create '
           'the fibula cut planes.')
code_27, _candidate_27 = _emit(brp_analyzer, "cb_step_27", STEP_27)
check(code_27 is None,
      "step 27 ('Click ...') was captured as a parameter update; it has no final "
      "state and must stay an action.")

# ── 4. No regression: the attribute-test controls emit exactly what they did ──
ATTRIBUTE_STEPS = [
    ("cb_step_23", 'Tick the "Automatic mandibular planes positioning for maximum '
                   'bones contact area" checkbox.',
     "mandiblePlanesPositioningForMaximumBoneContactCheckBox",
     "mandiblePlanesPositioningForMaximumBoneContact", "_sync_ctrl.checked = True", "'True'"),
    ("cb_step_24", 'Tick the "Make all mandible planes rotate together" checkbox.',
     "makeAllMandiblePlanesRotateTogetherCheckBox",
     "makeAllMandiblePlanesRotateTogether", "_sync_ctrl.checked = True", "'True'"),
    ("cb_step_33", 'Clear the "Show original mandible model" checkbox.',
     "showOriginalMandibleCheckBox",
     "showOriginalMandible", "_sync_ctrl.checked = False", "'False'"),
]
for step_id, description, widget_name, role, sync_line, state_text in ATTRIBUTE_STEPS:
    code, candidate = _emit(brp_analyzer, step_id, description)
    check(candidate is not None and candidate.get("widget_name") == widget_name,
          "%s now matches %r instead of %s"
          % (step_id, (candidate or {}).get("widget_name"), widget_name))
    check(code is not None and sync_line in code,
          "%s no longer drives its control with %r" % (step_id, sync_line))
    check(code is not None
          and ("parameterNode.SetParameter(%r, %s)" % (role, state_text)) in code,
          "%s no longer writes %s for %s" % (step_id, state_text, role))

# ── 5. Every emitted template is executable and passes the executor's gate ───
validator = _cv.CodeValidator()
for label, code in (("cb_step_28", code_28),):
    if not code:
        continue
    try:
        compile(code, label, "exec")
    except SyntaxError as exc:
        failures.append("%s does not compile: %s" % (label, exc))
    checked += 1
    verdict = validator.validate(code)
    check(verdict.get("valid"),
          "%s is refused by CodeValidator: %s" % (label, verdict.get("reason")))

# ── 6. The ON string is READ, not assumed ────────────────────────────────────
# BoneReconstructionPlanner happens to spell it "True". Nothing makes that a
# rule, and an extension spelling it "1" must get "1" -- the same defect this
# whole file is about, entering through the emitter instead of the model.
_SYNTHETIC_SOURCE = '''
class Widget(ScriptedLoadableModuleWidget):
    def updateParameterNodeFromGUI(self, caller=None, event=None):
        if self.ui.autoRefreshButton.checkState == qt.Qt.Checked:
            self._parameterNode.SetParameter("autoRefresh", "1")
        else:
            self._parameterNode.SetParameter("autoRefresh", "0")

    def updateGUIFromParameterNode(self, caller=None, event=None):
        if self._parameterNode.GetParameter("autoRefresh") == "1":
            self.ui.autoRefreshButton.checkState = qt.Qt.Checked
        else:
            self.ui.autoRefreshButton.checkState = qt.Qt.Unchecked
'''
synthetic = _new_analyzer()
synthetic_bindings = synthetic._extract_ui_parameter_bindings(_SYNTHETIC_SOURCE, [], [])
entry = (synthetic_bindings.get("autoRefreshButton") or {}).get("roles") or [{}]
check(entry[0].get("true_value") == "1" and entry[0].get("false_value") == "0",
      "a source spelling its states '1'/'0' was read as %r/%r"
      % (entry[0].get("true_value"), entry[0].get("false_value")))
check((entry[0].get("write_form") or {}).get("on") == "qt.Qt.Checked",
      "the extension's own dotted write form was not carried: %r"
      % (entry[0].get("write_form"),))

synthetic._ui_parameter_bindings = synthetic_bindings
synthetic_code, _ = _emit(
    synthetic, "cb_step_1", "Tick the auto refresh button checkbox.",
    extension_name="Synthetic", logic_class="SyntheticLogic", module_name="Synthetic")
check(synthetic_code is not None, "the synthetic control produced no template")
if synthetic_code:
    check("parameterNode.SetParameter('autoRefresh', '1')" in synthetic_code,
          "the emitter assumed 'True' where the source writes '1'")
    check("_sync_ctrl.checkState = qt.Qt.Checked" in synthetic_code,
          "the emitter did not reproduce the source's own dotted write form")
    # A dotted Qt constant is only usable if the template imports qt.
    check("import qt" in synthetic_code,
          "the template writes qt.Qt.Checked without importing qt")
    try:
        compile(synthetic_code, "synthetic", "exec")
    except SyntaxError as exc:
        failures.append("the synthetic template does not compile: %s" % exc)
    checked += 1

# ── 7. A one-sided write form is not a write form ────────────────────────────
# "How to turn it on" without "how to turn it off" would ship a step that can
# only move one way; the Qt fallback for the property is the safer answer.
_ONE_SIDED = '''
class Widget(ScriptedLoadableModuleWidget):
    def updateGUIFromParameterNode(self, caller=None, event=None):
        if self._parameterNode.GetParameter("halfWay") == "True":
            self.ui.halfWayButton.checkState = qt.Qt.Checked
'''
one_sided = _new_analyzer()._extract_ui_parameter_bindings(_ONE_SIDED, [], [])
roles = (one_sided.get("halfWayButton") or {}).get("roles") or []
check(not any(r.get("write_form") for r in roles),
      "a one-sided control write was recorded as a complete write form")

# ── 8. Generic across the shipped set: nothing lost anywhere ─────────────────
# Only BoneReconstructionPlanner drives this scan today (the rest bind their
# GUI another way), so the point of sweeping all nine is the blast radius: the
# scan must still run, and must still recover every attribute-test control.
scanned = 0
for name in sorted(os.listdir(EXT_ROOT)) if os.path.isdir(EXT_ROOT) else []:
    ext_dir = os.path.join(EXT_ROOT, name)
    if not os.path.isdir(ext_dir):
        continue
    entry_module, ui_files = _entry_module_and_ui(ext_dir)
    if not entry_module:
        continue
    source = open(entry_module, encoding="utf-8", errors="replace").read()
    try:
        bindings = _new_analyzer()._extract_ui_parameter_bindings(source, ui_files, [])
    except Exception as exc:
        failures.append("%s: the binding scan raised %r" % (name, exc))
        continue
    scanned += 1
    checked += 1
    for widget_name, binding in bindings.items():
        for role_entry in binding.get("roles") or []:
            # One entry per (role, access, property): a duplicate means the
            # merge broke and roles[0] is carrying half the evidence again.
            same = [
                other for other in binding["roles"]
                if (other.get("parameter_name"), other.get("access"),
                    other.get("value_property"))
                == (role_entry.get("parameter_name"), role_entry.get("access"),
                    role_entry.get("value_property"))
            ]
            if len(same) > 1:
                failures.append(
                    "%s/%s: %d role entries for one (role, access, property)"
                    % (name, widget_name, len(same)))
                break
notes.append("binding scan run over %d extensions under %s" % (scanned, EXT_ROOT))
notes.append("BoneReconstructionPlanner: %d bound controls, %d of them read as a "
             "comparison" % (len(brp_bindings), len(COMPARISON_CONTROLS)))

# -- 9. The second gate: the shipped artifacts, judged by the real validator --
# A deterministic emitter fixes what the emitter writes. Free-form generation,
# self-correction and the runtime Revise all write templates too, so the
# spelling rule is enforced a second time where every producer's output passes:
# validation. Run it over the templates this repo actually ships -- all of them
# must pass -- and then over a copy of one with the bug put back, which must be
# refused by name. Pinning the assertion to the RULE and not to the broken
# artifact matters: the artifact was regenerated the day after it was found, and
# an artifact-pinned check would have started passing for the wrong reason.
_gate = _new_analyzer()
_gate._workflow_metadata = {"ui_parameter_bindings": brp_bindings}
_BRP_TEMPLATES = os.path.join(REPO, "Resources", "extension_CLI",
                              "BoneReconstructionPlanner", "templates")
if os.path.isdir(_BRP_TEMPLATES):
    refused, accepted = {}, []
    step_28_text = ""
    for name in sorted(os.listdir(_BRP_TEMPLATES)):
        if not name.endswith(".tpl"):
            continue
        template = open(os.path.join(_BRP_TEMPLATES, name),
                        encoding="utf-8", errors="replace").read()
        if name == "cb_step_28.py.tpl":
            step_28_text = template
        verdict = _gate._validate_parameter_state_spelling(template)
        if verdict.get("errors"):
            refused[name] = verdict["errors"]
        else:
            accepted.append(name)
    for name in sorted(refused):
        check(False, "%s is refused by the spelling gate: %s"
                     % (name, refused[name]))
    check(not refused,
          "%d shipped BoneReconstructionPlanner template(s) fail the spelling gate"
          % len(refused))
    notes.append("spelling gate over %d shipped BoneReconstructionPlanner "
                 "templates: %d refused" % (len(accepted) + len(refused), len(refused)))

    # The bug as it actually shipped, reintroduced into the real template: the
    # extension compares == "True", so 'true' sets the parameter and changes
    # nothing, and every other gate accepts it.
    check("SetParameter('updateOnMandiblePlanesMovement', 'True')" in step_28_text,
          "cb_step_28 no longer writes the source's ON string; this check can no "
          "longer reintroduce the defect it is testing for.")
    regressed = step_28_text.replace(
        "SetParameter('updateOnMandiblePlanesMovement', 'True')",
        "SetParameter('updateOnMandiblePlanesMovement', 'true')")
    errors = _gate._validate_parameter_state_spelling(regressed).get("errors", [])
    check(any("updateOnMandiblePlanesMovement" in message for message in errors),
          "the spelling gate accepts a lowercase 'true' written to a role the "
          "extension compares against \"True\": %s" % errors)

    # And the template the fixed pipeline emits for that same step must pass.
    if code_28:
        check(not _gate._validate_parameter_state_spelling(code_28).get("errors"),
              "the newly emitted step 28 is refused by the spelling gate")

# A role whose two spellings were not BOTH recovered cannot be judged, and a
# non-literal value is not decidable at all: neither may be refused.
_undecidable = _new_analyzer()
_undecidable._workflow_metadata = {"ui_parameter_bindings": brp_bindings}
for snippet in (
    "parameterNode.SetParameter('updateOnMandiblePlanesMovement', _state)",
    "parameterNode.SetParameter('colorIndex', '3')",
    "parameterNode.SetParameter(roleName, 'true')",
):
    check(not _undecidable._validate_parameter_state_spelling(snippet).get("errors"),
          "the spelling gate refused an undecidable write: %s" % snippet)

for note in notes:
    print("note: " + note)
print("")
if failures:
    print("FAILED (%d checks):" % checked)
    for failure in failures:
        print("  - " + failure)
    sys.exit(1)
print("OK: %d checks passed." % checked)
