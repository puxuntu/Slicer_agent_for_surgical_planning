"""A self-correction must be persistable, and a placeholder must be reachable.

Two halves of one failure, both silent, both observed on
BoneReconstructionPlanner's cb_step_12.

**The step could never work.** Its template searched every node name for
``"{curve_name_keyword: mandible}"`` -- a placeholder written INSIDE a string
literal. The loader masks string literals before it substitutes (deliberately: a
template's prose must survive filling), so that placeholder is never filled, and
the dispatched code searches for the brace text itself. It raised MISSING_NODE on
every run of the procedure. CranialImplantPlanning ships the same shape:
``AddNewNodeByClass(cls, "{curve_name: CuttingCurve}")`` names its node
``{curve_name: CuttingCurve}`` and raises nothing at all. The blanket
unresolved-placeholder rule cannot catch either, because both carry a DEFAULT --
and a default is exactly what makes a placeholder safe at dispatch, everywhere
except inside a string, where it is never read.

**The fix could never persist.** ``_persistGeneratedTemplateRepair`` refuses to
write a self-correction back into a template that carries placeholders, because
the corrected code is the FILLED code and freezing this run's ``{side}`` into the
package would make every later run reconstruct whichever side this one picked.
It decided that with a raw brace scan -- which also matches every f-string
interpolation, and the precondition block every generated step carries ends with
``print(f"...: {_module_enter_error}")``. So the guard fired on 45 of the 181
shipped templates that have nothing fillable in them at all, and the write-back
was dead for most of the cookbook: the step self-corrected, advanced, threw the
fix away, and did it again on the next run, forever.

Both are measured with the LOADER'S OWN filler, never with a second regex.

Runs OUTSIDE Slicer::

    python scripts/check_template_write_back.py
"""
import importlib
import importlib.util
import io
import os
import re
import sys
import types

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI_ROOT = os.path.join(REPO, "Resources", "extension_CLI")

# TemplateReviser is Qt-free, but SlicerAIAgentLib/__init__.py imports slicer.
# Register a stub package pointing at the real directory so the module -- and the
# `from .extension_cli_loader.templates import _fill_template` inside it, and the
# `from SlicerAIAgentLib.TemplateReviser import ...` the analyzer's validator
# does -- all resolve to the production files without running that __init__.
_lib = types.ModuleType("SlicerAIAgentLib")
_lib.__path__ = [os.path.join(REPO, "SlicerAIAgentLib")]
sys.modules.setdefault("SlicerAIAgentLib", _lib)
_reviser = importlib.import_module("SlicerAIAgentLib.TemplateReviser")

_eca = types.ModuleType("_eca")
_eca.__path__ = [os.path.join(REPO, "SlicerAIAgentLib", "extension_cli_analyzer")]
sys.modules["_eca"] = _eca
_validation_semantics = importlib.import_module("_eca.validation_semantics")
_reachability = _validation_semantics.AnalyzerValidationSemanticsMixin._validate_placeholder_reachability

_ecl = importlib.import_module("SlicerAIAgentLib.extension_cli_loader.templates")

#: The write-back's old rule, kept here as the thing being ruled out.
RAW_BRACE_SCAN = re.compile(r"(?<!\{)\{([A-Za-z_][A-Za-z0-9_]*)(?::[^{}]*)?\}(?!\})")

failures = []
notes = []
checked = 0


def check(condition, message):
    global checked
    checked += 1
    if not condition:
        failures.append(message)


def shipped_templates():
    for name in sorted(os.listdir(CLI_ROOT)):
        tdir = os.path.join(CLI_ROOT, name, "templates")
        if not os.path.isdir(tdir):
            continue
        for fname in sorted(os.listdir(tdir)):
            if not fname.endswith(".tpl"):
                continue
            path = os.path.join(tdir, fname)
            yield name, fname, io.open(path, encoding="utf-8", errors="replace").read()


# ── 1. The guard measures what the filler LOOKS UP ───────────────────────────
raw_blocked = fillable_blocked = unblocked = 0
for pkg, fname, text in shipped_templates():
    raw = set(RAW_BRACE_SCAN.findall(text)) - {"vol_lookup"}
    fillable = set(_reviser.fillable_placeholder_names(text)) - {"vol_lookup"}
    # The relaxation may only ever go one way: everything the filler looks up is
    # still blocked. A name in `fillable` that the raw scan missed would mean the
    # new rule is not a subset and something run-specific could now be frozen.
    check(fillable <= raw,
          "%s/%s: fillable %s is not a subset of the raw scan %s"
          % (pkg, fname, sorted(fillable), sorted(raw)))
    if raw:
        raw_blocked += 1
    if fillable:
        fillable_blocked += 1
    elif raw:
        unblocked += 1
notes.append("%d templates blocked by the old raw scan, %d by the filler-backed "
             "rule: %d self-corrections can now be persisted"
             % (raw_blocked, fillable_blocked, unblocked))
check(unblocked > 0,
      "the filler-backed rule blocks exactly what the raw scan blocked; the "
      "write-back is still dead for every template carrying an f-string.")

# The precondition block is why: it is in most generated templates and its only
# brace span is an f-string interpolation of a local exception variable.
PRECONDITION_FSTRING = (
    'print(f"Warning: could not activate module \'X\': {_module_enter_error}")')
check("_module_enter_error" in RAW_BRACE_SCAN.findall(PRECONDITION_FSTRING),
      "the raw scan no longer matches the precondition f-string; this check is "
      "no longer testing the regression it was written for.")
check(not _reviser.fillable_placeholder_names(PRECONDITION_FSTRING),
      "an f-string interpolation is still counted as a fillable placeholder.")

# ── 2. ...and still refuses a genuinely run-specific value ───────────────────
# Each of these is filled at dispatch from something the run supplies, so
# persisting a filled copy would freeze one run's answer into the package.
MUST_STAY_BLOCKED = [
    ("OrbitalFractureReconstruction", "cb_step_14.py.tpl", "side"),
    ("BoneReconstructionPlanner", "cb_step_25.py.tpl", "initial_space"),
    ("BoneReconstructionPlanner", "cb_step_2.py.tpl",
     "mandibular_segmentation_node_name"),
    ("CranialImplantPlanning", "cb_step_6_slicer.py.tpl", "threshold_min"),
]
for pkg, fname, name in MUST_STAY_BLOCKED:
    path = os.path.join(CLI_ROOT, pkg, "templates", fname)
    if not os.path.isfile(path):
        notes.append("skipped %s/%s (not shipped in this checkout)" % (pkg, fname))
        continue
    text = io.open(path, encoding="utf-8", errors="replace").read()
    check(name in _reviser.fillable_placeholder_names(text),
          "%s/%s no longer counts {%s} as fillable; a run's own value could be "
          "frozen into the package." % (pkg, fname, name))

# ── 3. The write-back really routes through it ────────────────────────────────
# The rule is only worth checking if the write-back asks it. Read the source,
# because the mixin it lives on imports Qt and cannot be loaded here.
_flow = io.open(os.path.join(REPO, "SlicerAIAgentLib", "app",
                             "widget_execution_flow.py"),
                encoding="utf-8", errors="replace").read()
check("fillable_placeholder_names" in _flow,
      "widget_execution_flow no longer consults fillable_placeholder_names; the "
      "write-back guard is back to a raw brace scan.")
_guard = _flow.split("def _templatePlaceholderNames", 1)[-1].split("def ", 1)[0]
check(_guard.index("fillable_placeholder_names") < _guard.index("re.findall")
      if "re.findall" in _guard else True,
      "the raw brace scan is consulted before the filler-backed rule.")

# ── 4. Persisting is lossless: escape, refill, byte-identical ────────────────
# The write-back escapes every brace and saves the result as the template. If
# that round trip were not exact, persisting an f-string would corrupt it into a
# literal `{name}` and the step would print braces instead of the error.
ROUND_TRIP_BODIES = [
    'try:\n    pass\nexcept Exception as e:\n    print(f"boom: {e}")\n',
    'd = {"a": 1}\ns = "{curve_name: X}"\n',
    'print(f"{a}{b}")\nnode.SetName("Result")\n',
]
for body in ROUND_TRIP_BODIES:
    escaped = body.replace("{", "{{").replace("}", "}}")
    check(_ecl._fill_template(escaped, {}) == body,
          "escaping braces and refilling does not reproduce %r" % body[:40])

# Over the real corrected code the reported run produced, too, when it is there.
_run_root = os.path.join(REPO, "logs")
_corrected = None
if os.path.isdir(_run_root):
    for run in sorted(os.listdir(_run_root)):
        candidate = os.path.join(_run_root, run, "runtime", "cb_step_12",
                                 "correction_2", "code.py")
        if os.path.isfile(candidate):
            _corrected = io.open(candidate, encoding="utf-8", errors="replace").read()
            break
if _corrected:
    body = _corrected.split(
        "# [Workflow runtime] end of injected prelude", 1)[-1]
    body = body.split("\n", 1)[1] if "\n" in body else body
    escaped = body.replace("{", "{{").replace("}", "}}")
    check(_ecl._fill_template(escaped, {}) == body,
          "the recorded cb_step_12 correction does not survive the escape/refill "
          "round trip.")
    notes.append("round trip also checked against a recorded cb_step_12 correction")

# ── 5. A placeholder inside a plain string is inert, and is reported ─────────
INERT_CASES = [
    # (source, inert names, why)
    ('node = scene.AddNewNodeByClass(cls, "{curve_name: CuttingCurve}")\n',
     ["curve_name"], "a placeholder in a plain string is never substituted"),
    ('if "{keyword: mandible}" in name.lower():\n    pass\n',
     ["keyword"], "the same, as a search keyword"),
    ('try:\n    pass\nexcept Exception as e:\n    print(f"failed: {e}")\n',
     [], "an f-string interpolation is Python's, not the filler's"),
    ('print(f"step {step_id} of {total}")\n',
     [], "several interpolations in one f-string"),
    ('logic.reconstruct({side})\n',
     [], "a placeholder in code is filled normally"),
    ('logic.reconstruct({side: left})\n',
     [], "...and so is a defaulted one"),
]
for source, expected, why in INERT_CASES:
    got = _reviser.inert_placeholders(source)
    check(got == expected,
          "inert_placeholders(%r) = %s, expected %s (%s)"
          % (source[:44], got, expected, why))

# ── 6. Over the shipped set: exactly the two known defects, nothing else ─────
inert_found = []
for pkg, fname, text in shipped_templates():
    for name in _reviser.inert_placeholders(text):
        inert_found.append((pkg, fname, name))
EXPECTED_INERT = {
    ("BoneReconstructionPlanner", "cb_step_12_slicer.py.tpl", "curve_name_keyword"),
    ("CranialImplantPlanning", "cb_step_16_slicer.py.tpl", "curve_name"),
}
present = {row for row in EXPECTED_INERT
           if os.path.isfile(os.path.join(CLI_ROOT, row[0], "templates", row[1]))}
check(set(inert_found) == present,
      "inert placeholders across the shipped set are %s, expected %s. A NEW one "
      "means a package shipped a placeholder that can never fill; a MISSING one "
      "means the package was regenerated (update this list) or the detector "
      "stopped working." % (sorted(inert_found), sorted(present)))
notes.append("inert placeholders across %d shipped templates: %d"
             % (sum(1 for _ in shipped_templates()), len(inert_found)))

# ── 7. The generation gate names them, and passes everything else ────────────
for pkg, fname, name in inert_found:
    text = io.open(os.path.join(CLI_ROOT, pkg, "templates", fname),
                   encoding="utf-8", errors="replace").read()
    errors = _reachability(text).get("errors", [])
    check(any(name in message for message in errors),
          "the reachability gate does not report {%s} in %s/%s: %s"
          % (name, pkg, fname, errors))
clean_checked = 0
for pkg, fname, text in shipped_templates():
    if (pkg, fname) in {(p, f) for p, f, _ in inert_found}:
        continue
    errors = _reachability(text).get("errors", [])
    if errors:
        failures.append("%s/%s is refused by the reachability gate: %s"
                        % (pkg, fname, errors))
    clean_checked += 1
checked += 1
notes.append("reachability gate run over every shipped template (%d clean)"
             % clean_checked)

# ── 8. The reported step, end to end ─────────────────────────────────────────
_step12 = os.path.join(CLI_ROOT, "BoneReconstructionPlanner", "templates",
                       "cb_step_12_slicer.py.tpl")
if os.path.isfile(_step12):
    text = io.open(_step12, encoding="utf-8", errors="replace").read()
    check(not (set(_reviser.fillable_placeholder_names(text)) - {"vol_lookup"}),
          "cb_step_12 still looks parameterised to the write-back guard, so its "
          "self-correction is still discarded on every run.")
    check(_reviser.inert_placeholders(text) == ["curve_name_keyword"],
          "cb_step_12's unfillable placeholder is no longer detected.")

for note in notes:
    print("note: " + note)
print("")
if failures:
    print("FAILED (%d checks):" % checked)
    for failure in failures:
        print("  - " + failure)
    sys.exit(1)
print("OK: %d checks passed." % checked)
