"""Check that a second guided run starts where the first one did.

Runs OUTSIDE Slicer. ``SafeExecutor`` imports ``slicer``/``qt``/``vtk`` at
module level, so they are stubbed here -- none of the behaviour under test
touches them, because the thing under test is the Python namespace itself.

WHAT IT PROVES
--------------
Generated workflow templates reach their extension through

    try:    logic = _<ext>_logic
    except NameError: logic = <Ext>Logic()

and hand node IDs forward the same way (``_<ext>_<step>_id``). That is the
intended channel from step N to step N+1. But the namespace it lives in is
``__main__``, whose lifetime is the PROCESS, so it was also an unintended
channel from run 1 to run 2: a freshly launched Slicer takes the
``except NameError`` branch and a second run in the same session did not,
reusing the previous run's logic object -- with its stale node attributes --
against a scene those nodes had been removed from. The observed symptom was a
step revealing geometry from four steps later, because the extension's
"has this stage run?" guard is an attribute on that object.

``SafeExecutor.clearIntroducedGlobals`` unbinds exactly the names our own
``exec`` calls introduced, and ``_prepareCleanRuntime`` calls it when a
workflow starts. Test 2 below is that bug and its fix, in miniature.

    python scripts/check_runtime_reset.py
"""

import sys
import types
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

for _name in ("slicer", "qt", "vtk", "ctk"):
    sys.modules.setdefault(_name, types.ModuleType(_name))
sys.modules["slicer"].util = types.ModuleType("slicer.util")
sys.modules["slicer"].app = types.SimpleNamespace(processEvents=lambda: None)

from SlicerAIAgentLib.SafeExecutor import SafeExecutor  # noqa: E402

FAILURES = []


def check(label, condition):
    print(("PASS  " if condition else "FAIL  ") + label)
    if not condition:
        FAILURES.append(label)


def main():
    # Everything runs inside a function on purpose: this script's own locals
    # would otherwise land in the very __main__ dict it is measuring.
    main_ns = sys.modules["__main__"].__dict__
    pre_existing = set(main_ns)
    executor = SafeExecutor()

    check("the executor writes into __main__", executor._globals_dict is main_ns)

    # -- 1. A step's bindings are tracked, then unbound on demand. ------------
    before = set(executor._globals_dict)
    exec("_ofr_logic = object()\n_ofr_cb_step_3_id = 'vtkMRMLMarkupsROINode1'\n",
         executor._globals_dict)
    executor._trackIntroducedGlobals(before, executor._globals_dict)
    check("both generated names are tracked",
          set(executor._introduced_globals) == {"_ofr_logic", "_ofr_cb_step_3_id"})

    removed = executor.clearIntroducedGlobals()
    check("clearing reports both", sorted(removed) == ["_ofr_cb_step_3_id", "_ofr_logic"])
    check("clearing unbinds both",
          "_ofr_logic" not in main_ns and "_ofr_cb_step_3_id" not in main_ns)
    check("the ledger is emptied", executor._introduced_globals == [])

    # -- 2. THE BUG: run 2 must take the `except NameError` branch. -----------
    template = (
        "try:\n"
        "    logic = _ofr_logic\n"
        "except NameError:\n"
        "    logic = 'FRESH'\n"
        "    _ofr_logic = logic\n"
    )
    before = set(executor._globals_dict)
    exec(template, executor._globals_dict)
    executor._trackIntroducedGlobals(before, executor._globals_dict)
    check("run 1 constructs a fresh logic object", main_ns["logic"] == "FRESH")

    # Stand in for a run-1 object carrying stale node attributes.
    main_ns["_ofr_logic"] = "STALE-FROM-RUN-1"
    exec(template, executor._globals_dict)
    check("without the reset, run 2 reuses the stale object (the bug)",
          main_ns["logic"] == "STALE-FROM-RUN-1")

    executor.clearIntroducedGlobals()
    check("the reset unbinds the cached logic", "_ofr_logic" not in main_ns)
    exec(template, executor._globals_dict)
    check("after the reset, run 2 behaves like a fresh launch (the fix)",
          main_ns["logic"] == "FRESH")

    # -- 3. Nothing that is not ours is ever removed. -------------------------
    main_ns["a_variable_the_user_typed"] = 42
    before = set(executor._globals_dict)
    exec("_ses_seg = 1\n", executor._globals_dict)
    executor._trackIntroducedGlobals(before, executor._globals_dict)
    executor.clearIntroducedGlobals()
    check("a name the user typed in the console survives",
          main_ns.get("a_variable_the_user_typed") == 42)
    check("names that predate our first exec survive",
          pre_existing.issubset(set(main_ns)))

    main_ns["preexisting_name"] = "original"
    before = set(executor._globals_dict)
    exec("preexisting_name = 'rebound by a step'\n", executor._globals_dict)
    executor._trackIntroducedGlobals(before, executor._globals_dict)
    executor.clearIntroducedGlobals()
    check("a pre-existing name a step REBOUND is left alone",
          main_ns.get("preexisting_name") == "rebound by a step")

    # -- 4. One namespace per process => one ledger per process. --------------
    # More than one executor exists per session (the runtime's own, and the CLI
    # generation api-probe's) and they all write to the same __main__.
    other = SafeExecutor()
    before = set(other._globals_dict)
    exec("_live_validation_leftover = 1\n", other._globals_dict)
    other._trackIntroducedGlobals(before, other._globals_dict)
    check("a second executor's residue is visible to the first",
          "_live_validation_leftover" in executor._introduced_globals)
    executor.clearIntroducedGlobals()
    check("the first executor clears the second's residue",
          "_live_validation_leftover" not in main_ns)
    check("clearing never shadows the class-level ledger",
          executor._introduced_globals
          is other._introduced_globals
          is SafeExecutor._introduced_globals)

    # -- 5. The prelude keys (addGlobal/removeGlobal). ------------------------
    executor.addGlobal("_workflow_choices", {"side": "left"})
    check("addGlobal is tracked", "_workflow_choices" in executor._introduced_globals)
    executor.removeGlobal("_workflow_choices")
    check("removeGlobal untracks", "_workflow_choices" not in executor._introduced_globals)
    check("removeGlobal unbinds", "_workflow_choices" not in main_ns)
    executor.removeGlobal("_a_name_never_added")  # must not raise

    print()
    if FAILURES:
        print("FAILED (%d):" % len(FAILURES))
        for failure in FAILURES:
            print("  - " + failure)
        return 1
    print("All runtime-reset checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
