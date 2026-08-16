#!/usr/bin/env python3
"""Check the voice matcher against every choice-bearing step actually shipped.

    python scripts/check_voice_commands.py            # fixed cases + every package
    python scripts/check_voice_commands.py --verbose  # print each resolution

Runs OUTSIDE Slicer, deliberately. The whole point of keeping
``SlicerAIAgentLib/voice/{grammar,commands}.py`` Qt-free and Slicer-free is that
the part of voice control that decides *what a spoken sentence does to the
scene* can be exercised without launching an application, and can therefore be
run on every change rather than when someone remembers. It imports the two
modules by path, because ``SlicerAIAgentLib/__init__.py`` imports ``slicer``.

Two halves:

* **Fixed cases** -- the behaviours that must hold whatever the packages say:
  conversation is refused, "the blue one" picks the BLUE option (a bare cardinal
  is not an ordinal), a Yes/No label leaves as a real boolean, an out-of-range
  number is refused, free text needs a lead-in verb.
* **A sweep of every ``Resources/extension_CLI/*/workflow.json``** -- for each
  step that offers a finite option list, every option's own label must resolve
  back to that option's value, and no option may be ambiguous against another on
  the same step. That is what catches a regenerated package whose new labels
  collide ("Yes" vs "Yes, adjust more") before a surgeon says one of them.

Exit code 0 when everything passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICE_DIR = os.path.join(ROOT, "SlicerAIAgentLib", "voice")


def _load_voice_modules():
    """Import grammar+commands as a synthetic package, without SlicerAIAgentLib."""
    package = types.ModuleType("_voice")
    package.__path__ = [VOICE_DIR]
    sys.modules["_voice"] = package

    def load(name):
        path = os.path.join(VOICE_DIR, name + ".py")
        spec = importlib.util.spec_from_file_location("_voice." + name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["_voice." + name] = module
        spec.loader.exec_module(module)
        setattr(package, name, module)
        return module

    return load("grammar"), load("commands")


G, C = _load_voice_modules()

FAILURES = []
CHECKS = [0]


def fail(message):
    FAILURES.append(message)


def _state(**kwargs):
    state = {"active": True, "current_step": "cb_step_1",
             "current_index": 1, "total_steps": 10}
    state.update(kwargs)
    return state


def expect(step, utterance, action, value=None, check_value=True, note=""):
    CHECKS[0] += 1
    command = C.resolve(utterance, step)
    ok = command.action == action
    if ok and check_value and value is not None:
        ok = command.value == value
    if not ok:
        fail("%-40r expected %s/%r, got %s/%r%s"
             % (utterance, action, value, command.action, command.value,
                (" [" + note + "]") if note else ""))
    return command


# ---------------------------------------------------------------------------
# Fixed cases
# ---------------------------------------------------------------------------

def check_fixed(verbose=False):
    colours = G.build_step_grammar(_state(
        description="Fractured side (pick the colored box over the fractured orbit)",
        choices=[{"label": "Red box", "value": "right"},
                 {"label": "Blue box", "value": "left"}]))
    expect(colours, "red box", C.ACTION_CHOICE, "right")
    expect(colours, "the blue one", C.ACTION_CHOICE, "left",
           note="a bare cardinal must not be read as an ordinal")
    expect(colours, "the red one please", C.ACTION_CHOICE, "right")
    expect(colours, "option two", C.ACTION_CHOICE, "left")
    for chatter in ("how is the patient doing today",
                    "can you pass me the retractor",
                    "we are done with the previous patient",
                    "the blood pressure is fine"):
        expect(colours, chatter, C.ACTION_NONE, note="room conversation must be refused")

    booleans = G.build_step_grammar(_state(
        description="Further adjustments required?",
        choices=[{"label": "Yes", "value": "true"},
                 {"label": "No", "value": "false"}]))
    CHECKS[0] += 1
    if booleans.choices[0]["value"] is not True or booleans.choices[1]["value"] is not False:
        fail("Yes/No labels must coerce to real booleans, got %r"
             % [c["value"] for c in booleans.choices])
    expect(booleans, "yes", C.ACTION_CHOICE, True)
    expect(booleans, "nope", C.ACTION_CHOICE, False)

    scalar = G.build_step_grammar(_state(
        description="Adjust the crop radius", scalar_selection=True,
        parameter_name="cropRadius", choice_label="Crop radius",
        scalar_min=10.0, scalar_max=120.0))
    expect(scalar, "set it to 45", C.ACTION_SCALAR, 45.0)
    expect(scalar, "one hundred and twenty", C.ACTION_SCALAR, 120.0)
    expect(scalar, "500", C.ACTION_NONE, note="out of range must be refused")

    band = G.build_step_grammar(
        _state(description="Set the threshold range", range_selection=True,
               parameter_name="thresholdRange"),
        range_live={"min": -1024.0, "max": 3071.0})
    expect(band, "two hundred to three thousand", C.ACTION_RANGE, [200.0, 3000.0])
    expect(band, "between 250 and 1500", C.ACTION_RANGE, [250.0, 1500.0])
    expect(band, "5000 to 9000", C.ACTION_NONE, note="above the live ceiling")

    text = G.build_step_grammar(_state(description="Name the plan",
                                       needs_choice_input=True,
                                       input_label="plan name"))
    expect(text, "call it left maxilla plan", C.ACTION_TEXT, "left maxilla plan")
    expect(text, "the anaesthetist is asking about the next case", C.ACTION_NONE,
           note="free text must not swallow the room")

    wait = G.build_step_grammar(_state(description="Place the ROI", can_done=True))
    for phrase in ("done", "i'm done", "next", "continue", "proceed", "ok next"):
        expect(wait, phrase, C.ACTION_PROCEED)
    expect(wait, "skip", C.ACTION_NONE, note="can_skip is false")
    expect(wait, "exit the workflow", C.ACTION_EXIT)

    nodes = G.build_step_grammar(
        _state(description="Select the CT volume", node_class="vtkMRMLScalarVolumeNode",
               needs_choice_input=True),
        nodes=[{"id": "n1", "name": "Case01_CT"},
               {"id": "n2", "name": "Case01_CT_cropped"},
               {"id": "n3", "name": "Cranial_Segmentation"}])
    expect(nodes, "cranial segmentation", C.ACTION_NODE, "Cranial_Segmentation")
    expect(nodes, "case 01 ct cropped", C.ACTION_NODE, "Case01_CT_cropped")
    expect(nodes, "case01 ct", C.ACTION_NODE, "Case01_CT",
           note="an exact full name beats its prefix-sharing sibling")
    expect(nodes, "case", C.ACTION_NONE, note="a fragment fitting both must be refused")
    expect(nodes, "scalpel please", C.ACTION_NONE)

    segments = G.build_step_grammar(
        _state(description="Hide the fragments you do not want", segment_selection=True),
        segments=[{"id": "Segment_1", "name": "Fragment 1", "visible": True},
                  {"id": "Segment_2", "name": "Fragment 2", "visible": True}])
    expect(segments, "hide fragment 2", C.ACTION_SEGMENT_VISIBILITY, "Segment_2")
    expect(segments, "show fragment 1", C.ACTION_SEGMENT_VISIBILITY, "Segment_1")
    expect(segments, "fragment 2", C.ACTION_NONE,
           note="needs an explicit show/hide verb")

    multi = G.build_step_grammar(
        _state(description="Configure the instrumented levels", multi_choice=True),
        multi_items=[{"param": "level", "label": "1st Instrumented Level",
                      "options": ["C1", "C2", "T11", "T12", "L1", "L5", "S1"]},
                     {"param": "sides", "label": "# Sides",
                      "options": ["L&R", "Left", "Right", "--"]}])
    command = expect(multi, "t12", C.ACTION_MULTI, check_value=False)
    CHECKS[0] += 1
    if command.action == C.ACTION_MULTI and (command.value or {}).get("level") != "T12":
        fail("multi-selector: 't12' set %r" % (command.value,))

    # --- regressions from the adversarial safety review ---------------------
    # A positional pick must BE the utterance, not merely occur in it. The
    # ordinal path runs after label matching fails, which is exactly the state
    # ordinary conversation is in.
    for chatter in ("just a second",
                    "give me a second",
                    "hang on a second",
                    "second thing we need more suction",
                    "can you pass me the second retractor",
                    "first let me check the airway",
                    "that was the last one",
                    "this is the last case today",
                    "last night i read the ct again"):
        expect(colours, chatter, C.ACTION_NONE,
               note="an ordinal inside a sentence must not select an option")
    # The deliberate positional forms still work.
    expect(colours, "the first one", C.ACTION_CHOICE, "right")
    expect(colours, "option two", C.ACTION_CHOICE, "left")
    expect(colours, "the last one", C.ACTION_CHOICE, "left")
    expect(colours, "second", C.ACTION_CHOICE, "left")

    # Confirm mode must not let an ordinary word confirm. "right" is also the
    # VALUE of an option here, so accepting it as assent would let a surgeon
    # correcting the side confirm the wrong one.
    for word in ("right", "ok", "okay"):
        CHECKS[0] += 1
        if C.resolve(word, colours, confirmation_pending=True).action == C.ACTION_CONFIRM:
            fail("%r must not count as confirmation" % word)

    # A numbered name must not collide with its sibling.
    fragments = G.build_step_grammar(
        _state(description="Pick the fragment", node_class="vtkMRMLModelNode",
               needs_choice_input=True),
        nodes=[{"id": "f1", "name": "Fragment 1"}, {"id": "f2", "name": "Fragment 2"}])
    expect(fragments, "fragment one", C.ACTION_NODE, "Fragment 1")
    expect(fragments, "fragment two", C.ACTION_NODE, "Fragment 2")
    expect(fragments, "fragment 2", C.ACTION_NODE, "Fragment 2")

    # A leading minus must survive tokenisation: minus one thousand twenty four
    # is the bottom of a CT window and the commonest negative here.
    CHECKS[0] += 1
    if C.extract_numbers("-1024 to 3071") != [-1024.0, 3071.0]:
        fail("negative digits lost their sign: %r" % C.extract_numbers("-1024 to 3071"))
    CHECKS[0] += 1
    if C.extract_numbers("minus one thousand and twenty four") != [-1024.0]:
        fail("word-form negative wrong: %r"
             % C.extract_numbers("minus one thousand and twenty four"))

    # Free text needs a verb aimed at the application, not a sentence opener.
    expect(text, "use the two point five driver", C.ACTION_NONE,
           note="'use' is not a free-text lead-in")

    # Advance verbs that are ordinary theatre speech were removed.
    expect(wait, "ready", C.ACTION_NONE)
    expect(wait, "go ahead", C.ACTION_NONE)

    idle = G.build_step_grammar({"active": False})
    expect(idle, "plan the orbital fracture reconstruction", C.ACTION_START_WORKFLOW)
    expect(idle, "stop listening", C.ACTION_STOP_LISTENING)

    CHECKS[0] += 1
    if C.resolve("yes", colours, confirmation_pending=True).action != C.ACTION_CONFIRM:
        fail("a pending confirmation must claim 'yes' before the step's own options do")

    CHECKS[0] += 1
    long_list = G.build_step_grammar(_state(
        description="1st Instrumented Level",
        choices=[{"label": n, "value": n} for n in
                 ["C%d" % i for i in range(1, 8)] + ["T%d" % i for i in range(1, 13)]]))
    if "more" not in G.spoken_prompt(long_list):
        fail("a truncated spoken option list must say that it was truncated")

    if verbose:
        print("fixed cases: %d checks" % CHECKS[0])


# ---------------------------------------------------------------------------
# Sweep of the shipped packages
# ---------------------------------------------------------------------------

def _steps_with_choices(package_dir):
    path = os.path.join(package_dir, "workflow.json")
    try:
        with io.open(path, encoding="utf-8") as handle:
            graph = json.load(handle)
    except Exception as error:
        fail("%s: unreadable workflow.json (%s)" % (os.path.basename(package_dir), error))
        return []
    out = []
    for step in graph.get("steps") or []:
        info = step.get("choice_info") or {}
        if info.get("choices"):
            out.append((step, info))
        for extra in step.get("choice_info_list") or []:
            if extra.get("choices") and extra is not info:
                out.append((step, extra))
    return out


def check_packages(verbose=False):
    root = os.path.join(ROOT, "Resources", "extension_CLI")
    if not os.path.isdir(root):
        print("No Resources/extension_CLI on disk; package sweep skipped.")
        return
    packages = sorted(name for name in os.listdir(root)
                      if os.path.isfile(os.path.join(root, name, "workflow.json")))
    total_steps = 0
    for name in packages:
        for step, info in _steps_with_choices(os.path.join(root, name)):
            total_steps += 1
            choices = []
            for choice in info["choices"]:
                if isinstance(choice, dict):
                    choices.append({"label": choice.get("label"),
                                    "value": choice.get("value", choice.get("label"))})
                else:
                    choices.append({"label": str(choice), "value": str(choice)})
            grammar = G.build_step_grammar(_state(
                current_step=step.get("step_id"),
                description=info.get("question"),
                choices=choices))
            for index, entry in enumerate(grammar.choices):
                CHECKS[0] += 1
                # A label made only of punctuation ("--") cannot be said aloud;
                # the matcher gives such an option a standard spoken alias, and
                # that is what has to resolve.
                spoken = entry["label"]
                if not C.normalize(spoken):
                    spoken = C._UNSPEAKABLE_ALIASES[0]
                command = C.resolve(spoken, grammar)
                where = "%s/%s option %d (%r said as %r)" % (
                    name, step.get("step_id"), index, entry["label"], spoken)
                if command.action != C.ACTION_CHOICE:
                    fail("%s: its own label does not resolve (%s, %s)"
                         % (where, command.action, command.rationale))
                elif command.value != entry["value"]:
                    fail("%s: resolved to %r, expected %r"
                         % (where, command.value, entry["value"]))
                elif verbose:
                    print("  ok %s -> %r" % (where, command.value))
    print("package sweep: %d packages, %d choice-bearing steps" % (len(packages), total_steps))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    check_fixed(args.verbose)
    check_packages(args.verbose)

    print("checks run: %d" % CHECKS[0])
    if FAILURES:
        print("\nFAILURES (%d):" % len(FAILURES))
        for line in FAILURES:
            print("  " + line)
        return 1
    print("all voice matcher checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
