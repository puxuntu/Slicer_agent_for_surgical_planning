"""A range the user chose must reach the step that consumes it.

A ``user_choice`` step with ``value_kind == "range"`` records ``[lo, hi]`` under
whatever ``parameter_name`` the decomposition invented. A LATER step then consumes
it through a placeholder -- and the two names are chosen independently: the
Segment Editor session driver builds its Threshold-apply block from the EFFECT
alone (``module_sessions._effect_operation_block``), so it can only write the
generic ``{threshold_min: 150.0}`` / ``{threshold_max: 3000.0}``. Bridging the two
is the runtime's job, in ``choice_helpers._build_format_kwargs``.

When that bridge misses, NOTHING RAISES. The placeholder carries a default, so the
Apply runs with a hard-coded range the user never chose and overwrites the segment
the range step just committed -- the mask visibly changes between the step that
chose it and the next step that shows it, several steps later, with no error
anywhere. That is what LongBoneFractureReduction did: its range steps are named
``threshold_range_reference`` / ``threshold_range_moving``, the marker word sits in
the MIDDLE, and the old alias rule stripped it only off the END, so no alias was
emitted at all and both Apply steps thresholded at 150-3000.

So this checks the property the symptom points at, over every shipped package: for
every ``*_min`` / ``*_max`` placeholder in a step's templates, the NEAREST PRECEDING
range choice must fill it, and must fill it with ITS value and not a later one --
proven by filling the real template with the real loader and looking for the value
in the emitted code, not by re-deriving the naming rule here.

Runs OUTSIDE Slicer (the loader's cache module guards ``import slicer``)::

    python scripts/check_range_choice_fill.py
"""
import importlib
import io
import json
import os
import re
import sys
import types

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_ROOT = os.path.join(REPO, "Resources", "extension_CLI")

# The loader package imported WITHOUT running SlicerAIAgentLib/__init__.py (which
# reaches Qt) or the package __init__ (which reaches SafeExecutor -> slicer). The
# submodules themselves are Slicer-free, so a stub package with __path__ set
# resolves their relative imports against the real files. The point is that this
# script exercises the PRODUCTION bridge; a copy of the naming rule here would
# answer confidently about a rule the runtime no longer uses.
_pkg = types.ModuleType("_ecl")
_pkg.__path__ = [os.path.join(REPO, "SlicerAIAgentLib", "extension_cli_loader")]
sys.modules["_ecl"] = _pkg
choice_helpers = importlib.import_module("_ecl.choice_helpers")
loader_templates = importlib.import_module("_ecl.templates")

_spec = importlib.util.spec_from_file_location(
    "_template_reviser", os.path.join(REPO, "SlicerAIAgentLib", "TemplateReviser.py")
)
_reviser = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_reviser)
fillable_placeholder_names = _reviser.fillable_placeholder_names

# Placeholders a min/max-consuming template asks for. Matched on the NAME the
# loader looks up, never on a raw brace scan (an f-string interpolation is two
# braces and an identifier like any other).
_MINMAX_RE = re.compile(r"_(min|max)$")

# Where a step keeps the templates it owns. Same set TemplateReviser resolves.
_TEMPLATE_KEYS = ("code_template", "pre_template", "post_template", "branch_action_template")

failures = []
notes = []
checked = 0


def _range_parameter_name(step):
    """The parameter_name of a step that records a RANGE, else None."""
    for sub in step.get("sub_operations") or []:
        if (sub.get("value_kind") or "") == "range":
            name = sub.get("parameter_name") or (step.get("choice_info") or {}).get("parameter_name")
            return name or None
    return None


def _templates_of(step, pkg_dir):
    out = []
    for key in _TEMPLATE_KEYS:
        rel = step.get(key)
        if not rel:
            continue
        path = os.path.join(pkg_dir, *str(rel).split("/"))
        if os.path.isfile(path):
            out.append((rel, path))
    return out


def _sentinel(index):
    """A value unique to the range step at ``index``, so the filled code says WHICH
    choice landed -- 'a value landed' is not the property under test; the previous
    behaviour also landed a value."""
    return [1000.0 + index, 9000.0 + index]


for ext_name in sorted(os.listdir(CLI_ROOT)):
    pkg_dir = os.path.join(CLI_ROOT, ext_name)
    wf_path = os.path.join(pkg_dir, "workflow.json")
    if not os.path.isfile(wf_path):
        continue
    try:
        steps = json.load(io.open(wf_path, encoding="utf-8")).get("steps") or []
    except Exception as exc:
        failures.append("%s: workflow.json unreadable (%s)" % (ext_name, exc))
        continue

    # Range choices in workflow order, so "the nearest preceding one" is answerable.
    range_steps = []  # [(step_index, parameter_name)]
    for i, step in enumerate(steps):
        name = _range_parameter_name(step)
        if name:
            range_steps.append((i, name))

    for i, step in enumerate(steps):
        step_id = step.get("step_id", "?")
        for rel, path in _templates_of(step, pkg_dir):
            text = io.open(path, encoding="utf-8").read()
            wanted = sorted(n for n in fillable_placeholder_names(text) if _MINMAX_RE.search(n))
            if not wanted:
                continue
            prior = [(j, n) for (j, n) in range_steps if j < i]
            if not prior:
                notes.append(
                    "%s %s (%s): asks for %s with no range choice before it -- the "
                    "placeholder default is the only source." % (ext_name, step_id, rel, ", ".join(wanted))
                )
                continue

            # Record exactly the choices a run would hold when this step dispatches.
            nearest_index, nearest_name = prior[-1]
            choice_helpers._workflow_choices[ext_name] = dict(
                (name, _sentinel(j)) for (j, name) in prior
            )
            kwargs = choice_helpers._build_format_kwargs({}, ext_name)
            expect_lo, expect_hi = _sentinel(nearest_index)

            for name in wanted:
                checked += 1
                if name not in kwargs:
                    failures.append(
                        "%s %s (%s): {%s} is not filled by any recorded range choice "
                        "(nearest is %r at %s) -- the step would silently run at the "
                        "placeholder default."
                        % (ext_name, step_id, rel, name, nearest_name, steps[nearest_index].get("step_id"))
                    )
                    continue
                expect = expect_hi if name.endswith("_max") else expect_lo
                got = kwargs[name]
                if got != repr(expect):
                    failures.append(
                        "%s %s (%s): {%s} filled with %s, expected %r from the nearest "
                        "preceding range choice %r (%s)."
                        % (ext_name, step_id, rel, name, got, expect, nearest_name,
                           steps[nearest_index].get("step_id"))
                    )

            # The claim is about the CODE that executes, so fill the real template
            # with the real filler and look for the value there.
            try:
                filled = loader_templates._fill_template(text, kwargs)
            except Exception as exc:
                failures.append("%s %s (%s): filling raised %s" % (ext_name, step_id, rel, exc))
                continue
            for value in (expect_lo, expect_hi):
                if repr(value) not in filled and str(value) not in filled:
                    failures.append(
                        "%s %s (%s): the chosen value %r does not appear in the filled "
                        "code." % (ext_name, step_id, rel, value)
                    )

# Unit cases for the naming rule itself: the spellings a decomposition produces for
# one concept must all reach the driver's generic placeholder, and an UNRELATED
# concept must not (a bridge that fills everything is not a bridge).
NAME_CASES = [
    ("thresholdRange", True),               # marker last, one concept word
    ("threshold_range", True),
    ("ThresholdRanges", True),
    ("referenceThresholdRange", True),      # qualifier first, marker last
    ("threshold_range_reference", True),    # marker in the MIDDLE -- the reported bug
    ("threshold_range_moving", True),
    ("range_threshold", True),              # marker first
    ("intensityRange", False),              # a different concept
    ("opacity_range", False),
]
for name, should_fill in NAME_CASES:
    checked += 1
    choice_helpers._workflow_choices["__unit__"] = {name: [11.0, 22.0]}
    kw = choice_helpers._build_format_kwargs({}, "__unit__")
    filled = "threshold_min" in kw and "threshold_max" in kw
    if filled != should_fill:
        failures.append(
            "naming rule: %r %s fill {threshold_min}/{threshold_max}, but it %s."
            % (name, "must" if should_fill else "must NOT", "does" if filled else "does not")
        )

# Most-recently-recorded wins, so consecutive threshold cycles in one workflow each
# get their own range (and a replay truncation puts the earlier one back).
choice_helpers._workflow_choices["__unit__"] = {"threshold_range_reference": [1.0, 2.0]}
if choice_helpers._build_format_kwargs({}, "__unit__").get("threshold_min") != repr(1.0):
    failures.append("cycle 1: the reference range does not reach {threshold_min}.")
choice_helpers._workflow_choices["__unit__"]["threshold_range_moving"] = [3.0, 4.0]
if choice_helpers._build_format_kwargs({}, "__unit__").get("threshold_min") != repr(3.0):
    failures.append("cycle 2: the moving range does not displace the reference one.")
del choice_helpers._workflow_choices["__unit__"]["threshold_range_moving"]
if choice_helpers._build_format_kwargs({}, "__unit__").get("threshold_min") != repr(1.0):
    failures.append("replay: truncating the moving choice does not restore the reference one.")
checked += 3

# An explicit tool argument is the caller's own value and must outrank a merged choice.
choice_helpers._workflow_choices["__unit__"] = {"thresholdRange": [1.0, 2.0]}
if choice_helpers._build_format_kwargs({"threshold_min": 7}, "__unit__").get("threshold_min") != repr(7):
    failures.append("an explicit tool argument no longer outranks a merged range choice.")
checked += 1

for note in notes:
    print("note: " + note)
print("")
if failures:
    print("FAILED (%d checks):" % checked)
    for f in failures:
        print("  - " + f)
    sys.exit(1)
print("OK: %d checks passed across %d shipped packages."
      % (checked, len([d for d in os.listdir(CLI_ROOT)
                       if os.path.isfile(os.path.join(CLI_ROOT, d, "workflow.json"))])))
