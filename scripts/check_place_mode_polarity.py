"""The "Place a control point" button is a TOGGLE, and the generated step must
click it the way the cookbook clicks it.

A wizard extension arms point placement from one button and ends it from the same
one: PedicleScrewPlanner's landmarks page says "click it to activate", the surgeon
places the landmarks for that level, and then "click it again to inactivate".
Emitting ``setPlaceModeEnabled(True)`` for both -- which the generator did -- is
the worst shape a defect can take here, because **nothing raises**: re-enabling an
already-enabled place widget succeeds, the step reports success, and the run
carries on with the views still owned by the markup tool.

The symptom therefore lands on a LATER step and looks like a different bug. That
loop's next iteration opens on "rotate the red slice for a clear view", and every
attempt to rotate it drops another control point instead. The person at the screen
sees a view that will not move; the log shows a step that succeeded.

Two independent things have to hold, and this file holds both:

* the **generator** must read the polarity -- from the recorded ``target_value``,
  and from the step's own text when the decomposition left none;
* a **view-adjustment step must give the views back to the mouse when it OPENS**,
  not only when it is done. The post-template already switched to view-transform
  mode, which is the same fix applied one step too late to help the person doing
  the adjusting -- and it is the only reason this defect could hide as long as it
  did, since the run ends up looking correct afterwards.

The deference reconciler is checked too (section 5): a placement step defers to
the extension's own widget only when the button before it ARMED that widget. After
a disable, deferring would leave the step with no way to place anything at all.

Runs OUTSIDE Slicer -- the generator is pure string assembly and the polarity
reader is pure text::

    python scripts/check_place_mode_polarity.py
"""

import ast
import importlib.util
import io
import json
import os
import sys
import types

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYZER = os.path.join(REPO, "SlicerAIAgentLib", "extension_cli_analyzer")
CLI_ROOT = os.path.join(REPO, "Resources", "extension_CLI")

_failures = []
_notes = []
_checks = [0]


def check(name, cond, detail=""):
    _checks[0] += 1
    if cond:
        print("  ok   %s" % name)
    else:
        print("  FAIL %s   %s" % (name, detail))
        _failures.append(name)


def _load_analyzer():
    """The analyzer halves this chain touches, without Slicer."""
    ns = {"__name__": "check_place_mode",
          "__file__": os.path.join(ANALYZER, "common.py")}
    for module in ("common.py", "template_helpers.py", "workflow_templates.py",
                   "scan.py", "stage4_decomposition.py"):
        with io.open(os.path.join(ANALYZER, module), encoding="utf-8") as handle:
            src = handle.read().replace("from .common import *", "", 1)
        exec(compile(src, module, "exec"), ns)
    return ns


def _code_validator():
    spec = importlib.util.spec_from_file_location(
        "check_place_mode_cv", os.path.join(REPO, "SlicerAIAgentLib", "CodeValidator.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CodeValidator()


# --------------------------------------------------------------------------
# 1. The polarity reader
# --------------------------------------------------------------------------
def section_reader(ns):
    print("[1] the polarity reader: what the step text says about the final state")
    infer = ns["_infer_final_state_intent"]

    def state(text):
        return infer(text).get("state")

    check("'to activate the point placement' is ON",
          state('Click the "Place a control point" button to activate the point placement.')
          is True)
    # The cookbook's own word for the second click. It is not a prefixed spelling
    # of "activate": every true pattern is space-anchored, and "inactivate" gives
    # the 'a' no leading space -- which is exactly why it read as ON before, by
    # matching nothing at all and falling through to the True default.
    check("'to inactivate the point placement' is OFF",
          state('Click the "Place a control point" button to inactivate the point placement.')
          is False)
    check("'deactivate' still is too",
          state("Deactivate control point placement after adding the fiducials.") is False)
    check("and 'activate' is not dragged down with them",
          state("Activate control point placement for placing landmark fiducials.") is True)
    # The vocabulary this shares with every other toggle in the pipeline.
    check("tick/untick are unaffected",
          state('Untick the "Edit Screw trajectories" checkbox') is False
          and state('Tick the "Show 3D" checkbox') is True)
    check("a step with no polarity word states none",
          state('Click the "Next" button in the "Grading Step" page.') is None)


# --------------------------------------------------------------------------
# 2. The emitted template
# --------------------------------------------------------------------------
def _templates_mixin(ns):
    inst = ns["AnalyzerWorkflowTemplatesMixin"]()
    inst._wizard = {
        "present": True, "workflow_attr": "workflow",
        "steps": [{"class_name": "PlanningLandmarksStep", "attr": "landmarksStep"}],
    }
    return inst


def _place_step(step_id, description, target_value, sub_description=""):
    return {
        "step_id": step_id,
        "description": description,
        "sub_operations": [{
            "op_type": "extension_op",
            "description": sub_description,
            "target_value": target_value,
            "wizard_place_button": {"step_attr": "landmarksStep",
                                    "place_attr": "startMeasurements"},
        }],
    }


ACTIVATE = 'Click the "Place a control point" button to activate the point placement.'
INACTIVATE = 'Click the "Place a control point" button to inactivate the point placement.'


def section_template(ns):
    print("[2] the emitted template drives the toggle both ways")
    inst = _templates_mixin(ns)
    validator = _code_validator()

    def emit(step):
        return inst._maybe_generate_wizard_template(
            "PedicleScrewPlanner", step, "PedicleScrewPlanner") or ""

    on = emit(_place_step("cb_step_8", ACTIVATE, True, "Activate control point placement."))
    off = emit(_place_step("cb_step_10", INACTIVATE, False, "Deactivate control point placement."))

    check("the arming step enables place mode",
          "setPlaceModeEnabled(True)" in on and "setPlaceModeEnabled(False)" not in on)
    check("the ending step disables it",
          "setPlaceModeEnabled(False)" in off and "setPlaceModeEnabled(True)" not in off)
    # Both routes to the widget carry the same polarity: the direct call on the
    # step object, and the whole-representation search it falls back to. A fix
    # applied to only one of them is a fix that works until the attribute moves.
    check("both the direct call and the fallback search agree",
          off.count("setPlaceModeEnabled(False)") == 2
          and on.count("setPlaceModeEnabled(True)") == 2,
          (on.count("setPlaceModeEnabled(True)"), off.count("setPlaceModeEnabled(False)")))
    # Belt and braces on the way out only: if the place widget could not be
    # reached, the surgeon is left unable to use the views at all.
    check("the ending step also releases the interaction node",
          "SwitchToViewTransformMode()" in off)
    check("the arming step does NOT release it",
          "SwitchToViewTransformMode()" not in on)
    check("the two steps really differ", on != off)

    for name, code in (("arming", on), ("ending", off)):
        try:
            compile(code, "<tpl>", "exec")
            parses = True
        except SyntaxError as exc:                              # pragma: no cover
            parses = False
            print(code)
            print(exc)
        check("the %s template parses" % name, parses)
        verdict = validator.validate(code)
        check("the %s template passes CodeValidator" % name, verdict.get("valid"),
              verdict.get("reason"))
        check("the %s template keeps its [wizard drive] marker" % name,
              "[wizard drive]" in code)

    # The second layer: a decomposition that recorded no polarity must not default
    # to ON. The step's own sentence is the evidence, and it is the same sentence
    # the surgeon reads in the panel.
    fallback_off = emit(_place_step("cb_step_10", INACTIVATE, None))
    fallback_on = emit(_place_step("cb_step_8", ACTIVATE, None))
    check("with no recorded target_value the step text decides (off)",
          "setPlaceModeEnabled(False)" in fallback_off)
    check("...and (on)", "setPlaceModeEnabled(True)" in fallback_on)
    # Neither layer says anything -> arm it. A place-button step with no polarity
    # at all is far likelier to be the "start placing" one, and arming is the
    # recoverable mistake: the surgeon sees placement they did not ask for, rather
    # than a step that silently does nothing.
    silent = emit(_place_step("cb_step_8", 'Use the "Place a control point" button.', None))
    check("with no evidence at all the step still arms",
          "setPlaceModeEnabled(True)" in silent)


# --------------------------------------------------------------------------
# 3. Navigation and page-button steps are untouched
# --------------------------------------------------------------------------
def section_blast_radius(ns):
    print("[3] the other wizard step shapes are unchanged")
    inst = _templates_mixin(ns)

    nav = inst._maybe_generate_wizard_template("PedicleScrewPlanner", {
        "step_id": "cb_step_5", "description": 'Click the "Next" button.',
        "sub_operations": [{"op_type": "extension_op", "wizard_nav": "forward"}],
    }, "PedicleScrewPlanner") or ""
    check("navigation still goes through the workflow object",
          "goForward()" in nav and "setPlaceModeEnabled" not in nav)

    # A page button whose text happens to carry a polarity word must not acquire
    # place-mode behaviour from it: the branches are exclusive and the button
    # branch is reached first.
    button = inst._maybe_generate_wizard_template("PedicleScrewPlanner", {
        "step_id": "cb_step_16", "description": 'Click the "Update" button.',
        "sub_operations": [{"op_type": "extension_op", "target_value": False,
                            "wizard_button": {"text": "Update", "handler": "manualUp",
                                              "step_attr": "measurementsStep",
                                              "button_attr": "updateButton"}}],
    }, "PedicleScrewPlanner") or ""
    check("a page button is still a handler call",
          "manualUp()" in button and "setPlaceModeEnabled" not in button)

    check("a step with no wizard grounding still yields nothing",
          inst._maybe_generate_wizard_template("PedicleScrewPlanner", {
              "step_id": "cb_step_1", "description": "Select the CT volume.",
              "sub_operations": [{"op_type": "user_choice"}],
          }, "PedicleScrewPlanner") is None)


# --------------------------------------------------------------------------
# 4. A view adjustment gets the mouse back when it OPENS
# --------------------------------------------------------------------------
def section_view_adjustment(ns):
    print("[4] a view-adjustment step releases the views on entry, not only on Done")
    inst = ns["AnalyzerTemplateHelpersMixin"]()
    step = {"step_id": "cb_step_7",
            "description": "Manually adjust the rotation angle of the red slice.",
            "placement_instructions": "Rotate the red slice for a clear view."}

    pre = inst._generate_view_adjustment_pre_template("PedicleScrewPlanner", step)
    post = inst._generate_view_adjustment_post_template("PedicleScrewPlanner", step)
    check("the pre-template switches to view-transform mode",
          "SwitchToViewTransformMode()" in pre)
    check("the post-template still does too (a hand-armed mode must also be released)",
          "SwitchToViewTransformMode()" in post)
    check("the pre-template still creates no markup node",
          "AddNewNodeByClass" not in pre and "SwitchToSinglePlaceMode" not in pre)
    validator = _code_validator()
    check("the pre-template passes CodeValidator",
          validator.validate(pre).get("valid"), validator.validate(pre).get("reason"))

    # The one interaction shape that must NOT release it: there the extension's
    # own tool is holding the clicks on purpose, and releasing would take the
    # placement away from the widget the previous step just armed.
    tool = inst._generate_module_tool_interaction_pre_template("PedicleScrewPlanner", {
        "step_id": "cb_step_9",
        "description": "Click in the 2D views to add fiducial points.",
        "placement_instructions": "Click in the 2D views to add fiducial points.",
    })
    check("an in-tool interaction leaves the active tool alone",
          "SwitchToViewTransformMode()" not in tool)


# --------------------------------------------------------------------------
# 5. Deference is to an ARMED widget, never to one just turned off
# --------------------------------------------------------------------------
def section_deference(ns):
    print("[5] a placement step defers only to a place button that ARMED the widget")
    inst = ns["AnalyzerStage4DecompositionMixin"]()
    inst._wizard = {"present": True}

    def placement_sub():
        return {"op_type": "user_interaction", "interaction_kind": "markup_placement",
                "creates_node": True, "requires_place_mode": True}

    def place_stage(target_value, description):
        return {"sub_operations": [{
            "op_type": "extension_op", "description": description,
            "target_value": target_value,
            "wizard_place_button": {"step_attr": "landmarksStep",
                                    "place_attr": "startMeasurements"}}]}

    after_on = placement_sub()
    inst._reconcile_wizard_placement(after_on, [place_stage(True, ACTIVATE)])
    check("after an arming click the step defers to the extension's widget",
          after_on.get("interaction_kind") == "module_tool_interaction"
          and after_on.get("creates_node") is False
          and after_on.get("native_placement") is True, after_on)

    after_off = placement_sub()
    inst._reconcile_wizard_placement(after_off, [place_stage(False, INACTIVATE)])
    check("after an ending click it keeps its own markup contract",
          after_off.get("interaction_kind") == "markup_placement"
          and after_off.get("creates_node") is True, after_off)

    # Same rule when the polarity was never recorded: the step text decides.
    after_text = placement_sub()
    inst._reconcile_wizard_placement(after_text, [place_stage(None, INACTIVATE)])
    check("and the text alone is enough to refuse the deference",
          after_text.get("interaction_kind") == "markup_placement", after_text)

    # A page boundary still stops the backward search before any place button.
    across = placement_sub()
    inst._reconcile_wizard_placement(across, [
        place_stage(True, ACTIVATE),
        {"sub_operations": [{"op_type": "extension_op", "wizard_nav": "forward"}]},
    ])
    check("a page navigation in between still blocks it",
          across.get("interaction_kind") == "markup_placement", across)

    # Classic (non-wizard) extensions never enter this path at all.
    classic = ns["AnalyzerStage4DecompositionMixin"]()
    classic._wizard = {"present": False}
    untouched = placement_sub()
    classic._reconcile_wizard_placement(untouched, [place_stage(True, ACTIVATE)])
    check("a classic extension is untouched",
          untouched.get("interaction_kind") == "markup_placement")


# --------------------------------------------------------------------------
# 6. What is on disk right now
# --------------------------------------------------------------------------
def section_shipped():
    print("[6] the shipped packages, as they stand on disk")
    if not os.path.isdir(CLI_ROOT):
        check("Resources/extension_CLI is available", False, CLI_ROOT)
        return
    stale = []
    seen = 0
    for name in sorted(os.listdir(CLI_ROOT)):
        graph = os.path.join(CLI_ROOT, name, "workflow.json")
        if not os.path.isfile(graph):
            continue
        try:
            with io.open(graph, encoding="utf-8") as handle:
                steps = json.load(handle).get("steps") or []
        except Exception:
            continue
        for step in steps:
            sub = next((so for so in (step.get("sub_operations") or [])
                        if isinstance(so, dict) and so.get("wizard_place_button")), None)
            if sub is None:
                continue
            seen += 1
            template = step.get("code_template")
            if not template:
                continue
            path = os.path.join(CLI_ROOT, name, template.replace("/", os.sep))
            if not os.path.isfile(path):
                continue
            with io.open(path, encoding="utf-8") as handle:
                code = handle.read()
            wants_on = sub.get("target_value") is not False
            has_on = "setPlaceModeEnabled(True)" in code
            if wants_on != has_on:
                stale.append("%s/%s (step says %s, template does %s)"
                             % (name, step.get("step_id"),
                                "arm" if wants_on else "release",
                                "arm" if has_on else "release"))
    print("  place-button steps across the shipped packages: %d" % seen)
    if stale:
        # NOT a failure: a package is a build artifact, and one built before this
        # fix is expected to disagree with the generator until it is rebuilt. It
        # is said loudly because the disagreement is invisible at run time -- the
        # step succeeds either way.
        _notes.append("REGENERATE: %s" % ", ".join(stale))
        print("  NOTE: shipped template(s) predate the polarity fix:")
        for item in stale:
            print("        - %s" % item)
    else:
        check("every shipped place-button template matches its step's polarity", True)


def main():
    print(__doc__.strip().splitlines()[0])
    print("")
    ns = _load_analyzer()
    section_reader(ns)
    print("")
    section_template(ns)
    print("")
    section_blast_radius(ns)
    print("")
    section_view_adjustment(ns)
    print("")
    section_deference(ns)
    print("")
    section_shipped()

    print("")
    print("checks run: %d" % _checks[0])
    for note in _notes:
        print(note)
    if _failures:
        print("FAILED: %s" % ", ".join(_failures))
        return 1
    print("all place-mode polarity checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
