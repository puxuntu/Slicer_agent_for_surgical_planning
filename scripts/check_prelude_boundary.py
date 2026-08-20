"""A runtime self-correction must be able to find where the prelude ends.

Every dispatched step is prefixed with a hidden prelude carrying
``_workflow_runtime_id``, which names ONE run. When self-correction fixes a step,
persisting that fix back into the .tpl means cutting the prelude off first -- and
if the boundary cannot be found the write-back refuses, so the step self-corrects,
advances, throws the fix away, and does it all again on the next run.

That is what happened to PelvicFracturePlanning's cb_step_3: the boundary was
found by scanning for the template's own ``import slicer`` line, and that template
opens with ``import math`` and never imports slicer (it relies on ``slicer``
already being bound in ``__main__``). The fix is an explicit end marker emitted by
the prelude itself. This holds the two halves of that contract together --
``choice_helpers._prepend_choice_prelude`` emits it, ``workflow_state
.strip_runtime_prelude`` parses it -- and checks the property that actually
matters: for every shipped template, prelude + template round-trips back to the
template.

Runs OUTSIDE Slicer::

    python scripts/check_prelude_boundary.py
"""
import importlib.util
import io
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Loaded by path: workflow_state is itself Qt- and Slicer-free, but the package
# __init__ imports SafeExecutor, which imports slicer.
_spec = importlib.util.spec_from_file_location(
    "_workflow_state", os.path.join(REPO, "SlicerAIAgentLib", "workflow_state.py")
)
_workflow_state = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_workflow_state)
PRELUDE_END_MARKER = _workflow_state.PRELUDE_END_MARKER
strip_runtime_prelude = _workflow_state.strip_runtime_prelude

CLI_ROOT = os.path.join(REPO, "Resources", "extension_CLI")

# The prelude's own shape, reproduced from choice_helpers._build_runtime_prelude.
# Deliberately NOT imported: that module needs the loader's _WorkflowContext and a
# live package. What must not drift is the MARKER, and that is imported.
RUNTIME_PRELUDE = "\n".join([
    "# [Workflow runtime] Hidden generated-CLI workflow context",
    "_workflow_runtime_extension = 'PelvicFracturePlanning'",
    "_workflow_runtime_id = 'PelvicFracturePlanning_1787000000000'",
    "_workflow_runtime_step = 'cb_step_3'",
    "_workflow_runtime_repeat_index = 0",
    "from SlicerAIAgentLib.workflow_state import remember_interaction_node, resolve_interaction_node",
    "",
]) + "\n"

PRECONDITION_PRELUDE = "\n".join([
    "# [Workflow preconditions] Validate source-derived node references before extension logic calls",
    "from SlicerAIAgentLib.workflow_state import validate_method_preconditions",
    "try:\n    _workflow_logic = _pelvicfractureplanning_logic\nexcept NameError:",
    "    from PelvicFracturePlanning import PelvicFracturePlanningLogic",
    "    _workflow_logic = PelvicFracturePlanningLogic()",
    "",
]) + "\n"


def _dispatch(template_body, with_preconditions=False):
    """What _prepend_choice_prelude produces: prelude, marker, then the body."""
    prelude = RUNTIME_PRELUDE + (PRECONDITION_PRELUDE if with_preconditions else "")
    return prelude + PRELUDE_END_MARKER + "\n" + template_body


def main():
    fails = []

    # 1. The emitter and the parser agree on the marker. Checked by reading the
    #    emitter's source rather than importing it (it needs a live _WorkflowContext).
    emitter = os.path.join(
        REPO, "SlicerAIAgentLib", "extension_cli_loader", "choice_helpers.py"
    )
    with io.open(emitter, encoding="utf-8") as handle:
        emitter_source = handle.read()
    if "PRELUDE_END_MARKER" not in emitter_source:
        fails.append("choice_helpers no longer emits PRELUDE_END_MARKER")
    if not re.search(r"def _prepend_choice_prelude\b[\s\S]{0,2000}?PRELUDE_END_MARKER",
                     emitter_source):
        fails.append("PRELUDE_END_MARKER is not emitted by _prepend_choice_prelude "
                     "(the single funnel every dispatch path goes through)")

    # 2. The regression case: a template with NO `import slicer` line. This is the
    #    exact shape that used to defeat the boundary scan and is why the marker
    #    exists, so it is named rather than left implicit.
    no_slicer_import = (
        "# Center the 3D view(s) on the scene\n"
        "import math\n"
        "\n"
        "layoutManager = slicer.app.layoutManager()\n"
        "for viewIndex in range(layoutManager.threeDViewCount):\n"
        "    layoutManager.threeDWidget(viewIndex).threeDView().resetFocalPoint()\n"
    )
    recovered = strip_runtime_prelude(_dispatch(no_slicer_import))
    if recovered != no_slicer_import:
        fails.append("template without an `import slicer` line did not round-trip "
                     "(got %r)" % (recovered if recovered is None else recovered[:60],))

    # 3. Still exact with the conditional precondition block in between -- the
    #    reason the marker is emitted by the funnel and not by one builder.
    if strip_runtime_prelude(_dispatch(no_slicer_import, True)) != no_slicer_import:
        fails.append("boundary lost when the precondition prelude is present")

    # 4. Prelude-free code is returned untouched (a correction often drops it).
    if strip_runtime_prelude(no_slicer_import) != no_slicer_import:
        fails.append("prelude-free code was modified")

    # 5. The safety property survives: a prelude present with NO boundary at all
    #    must still refuse, or a run id gets baked into a shipped template.
    if strip_runtime_prelude(RUNTIME_PRELUDE + no_slicer_import) is not None:
        fails.append("a prelude with no resolvable boundary was accepted -- this "
                     "bakes _workflow_runtime_id into the package")

    # 6. The legacy fallback still works for corrections made before the marker.
    legacy = "import slicer\nslicer.util.selectModule('X')\n"
    if strip_runtime_prelude(RUNTIME_PRELUDE + legacy) != legacy:
        fails.append("the `import slicer` fallback regressed")

    # 7. LAST marker wins: a correction that quotes the failing code back inside a
    #    comment would otherwise cut at the quote and keep the real prelude.
    quoted = ("# previous attempt:\n"
              "# " + PRELUDE_END_MARKER + "\n"
              + RUNTIME_PRELUDE + PRELUDE_END_MARKER + "\n" + no_slicer_import)
    if strip_runtime_prelude(quoted) != no_slicer_import:
        fails.append("an earlier quoted marker won over the real one")

    # 8. The property that matters, over every shipped template: dispatch then
    #    strip returns the template unchanged.
    checked = 0
    for ext in sorted(os.listdir(CLI_ROOT)) if os.path.isdir(CLI_ROOT) else []:
        templates = os.path.join(CLI_ROOT, ext, "templates")
        if not os.path.isdir(templates):
            continue
        for name in sorted(os.listdir(templates)):
            if not name.endswith(".tpl"):
                continue
            with io.open(os.path.join(templates, name), encoding="utf-8") as handle:
                body = handle.read()
            checked += 1
            if strip_runtime_prelude(_dispatch(body)) != body:
                fails.append("%s/%s did not round-trip through the prelude boundary"
                             % (ext, name))

    if fails:
        print("\n".join("FAIL: " + item for item in fails))
        return 1
    print("OK: the prelude boundary is recoverable for all %d shipped templates "
          "(and refuses when it genuinely cannot be found)" % checked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
