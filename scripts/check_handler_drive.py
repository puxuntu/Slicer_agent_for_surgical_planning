"""The button/checkbox handler-drive emitter must agree with the api proof.

``workflow_templates._maybe_generate_button_handler_template`` writes the call that
drives an extension's own connected handler, and ``api_proof`` checks every call in
that file against the handler's scanned arity. The two read the SAME source of
truth (``handler_required_args``), so an emitted call the gate rejects is not a bad
package -- it is the generator contradicting its own validator, and no repair rung
can resolve it, because the offending call is code the generator just wrote.

That is what happened on PelvicFracturePlanning: the emitter appended an
``except TypeError: handler()`` fallback beside ``handler(True)`` even when the
arity HAD been read from source. The prover does not skip except-handler bodies, so
it reported ``handler_arity_mismatch`` on the dead fallback; the issue routed to the
evidence-gathering rung, which changes no template, so verify_repair broke out of
its own retry loop on attempt 1 of 5 and auto-revision had nothing to rewrite.

Runs OUTSIDE Slicer (the generator is Slicer-free), so it is checkable on every
change::

    python scripts/check_handler_drive.py
"""
import ast
import importlib.util
import os
import sys
import types

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(REPO, "SlicerAIAgentLib", "extension_cli_analyzer")

for _name in ("slicer", "vtk", "qt", "ctk"):
    sys.modules.setdefault(_name, types.ModuleType(_name))

# Load the generator modules standalone: the real package __init__ imports slicer.
_pkg = types.ModuleType("eca")
_pkg.__path__ = [PKG]
sys.modules["eca"] = _pkg


def _load(mod):
    spec = importlib.util.spec_from_file_location(
        "eca." + mod, os.path.join(PKG, mod + ".py")
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["eca." + mod] = module
    spec.loader.exec_module(module)
    return module


common = _load("common")
scan = _load("scan")
workflow_templates = _load("workflow_templates")
repair_loop = _load("repair_loop")


class _Emitter(workflow_templates.AnalyzerWorkflowTemplatesMixin):
    """The emitter with only the collaborators it actually calls."""

    def __init__(self, connections):
        self._widget_connections = connections
        self._parameter_node_wrapper = None

    def _template_header_lines(self, extension_name, step, _unused):
        return ["# --- %s: %s ---" % (extension_name, step.get("description", ""))]

    def _emit_module_enter_precondition(self, module_name):
        return ["# precondition:begin", "# precondition:end"]


STEP = {
    "step_id": "cb_step_10",
    "description": 'tick the "Manually adjust a template" checkbox.',
    "widget_name": "chkAdjustTemplate",
    "target_value": True,
    "sub_operations": [{"widget_name": "chkAdjustTemplate", "target_value": True}],
}
HANDLER = "onAdjustTemplateToggled"


def _connection(required):
    conn = {
        "signal": "toggled(bool)",
        "button_widget_name": "chkAdjustTemplate",
        "handler_method": HANDLER,
        "shares_widget_state": True,
    }
    if required is not None:
        conn["handler_required_args"] = required
    return conn


def _emit(required):
    emitter = _Emitter([_connection(required)])
    return emitter._maybe_generate_button_handler_template(
        "PelvicFracturePlanning",
        STEP,
        "PelvicFracturePlanningLogic",
        "PelvicFracturePlanning",
    )


def _arg_counts(code, handler, receiver="_widget"):
    """Every call to `handler` in the template, as argument counts.

    Walks the whole tree the way the api proof's call inventory does -- an
    ``except`` handler's body included, which is the point.
    """
    counts = []
    for node in ast.walk(ast.parse(code)):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if node.func.attr != handler:
            continue
        value = node.func.value
        if receiver and not (isinstance(value, ast.Name) and value.id == receiver):
            continue
        counts.append(len(node.args))
    return counts


def _method_arities(source_dir):
    """Every method name in an extension's source -> its required positional count."""
    arities = {}
    for root, _dirs, files in os.walk(source_dir):
        for name in files:
            if not name.endswith(".py"):
                continue
            try:
                with open(os.path.join(root, name), encoding="utf-8") as handle:
                    tree = ast.parse(handle.read())
            except Exception:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        arities[item.name] = scan.AnalyzerScanMixin._required_arg_count(
                            item
                        )
    return arities


def main():
    fails = []

    # 1. Arity known and satisfiable -> exactly one call, carrying the state. No
    #    fallback: a 0-arg call to a 1-arg handler is what the gate blocks.
    code = _emit(1)
    if _arg_counts(code, HANDLER) != [1]:
        fails.append(
            "arity-known emitted %r, expected exactly one 1-arg call"
            % (_arg_counts(code, HANDLER),)
        )
    if "except TypeError" in code:
        fails.append("arity-known still emits the 0-arg TypeError fallback")

    # 2. Arity unknown -> the fallback survives. That is exactly the case in which
    #    the gate is silent, because `handler_required_args` has no entry either.
    if sorted(_arg_counts(_emit(None), HANDLER)) != [0, 1]:
        fails.append("arity-unknown lost its TypeError fallback")

    # 3. The two sides agree over the whole domain. Gate condition, verbatim from
    #    api_proof: `isinstance(required, int) and supplied < required`.
    for required in (None, 0, 1, 2, 3):
        emitted = _emit(required)
        if emitted is None:
            # Declining is correct for a handler the drive cannot satisfy (it can
            # pass at most the control's own state); the caller then falls back to
            # its normal generation path.
            if not (isinstance(required, int) and required >= 2):
                fails.append("required=%r: emitter declined a drivable handler" % (required,))
            continue
        for supplied in _arg_counts(emitted, HANDLER):
            if isinstance(required, int) and supplied < required:
                fails.append(
                    "required=%r: emitted a %d-arg call the api proof blocks"
                    % (required, supplied)
                )

    # 4. A blocked arity mismatch must not route to a rung that changes nothing.
    #    `gather_api_evidence` is evidence-only by construction, so sending a fully
    #    diagnosed arity error there deadlocks the repair ladder.
    strategy = repair_loop.AnalyzerRepairLoopMixin._repair_strategy_for_issue(
        "UnprovenReceiver",
        {},
        {"diagnosis": "handler_arity_mismatch", "effect": "read_only", "blocking": True},
    )
    if strategy == "gather_api_evidence":
        fails.append(
            "handler_arity_mismatch routes to gather_api_evidence, which never "
            "edits a template"
        )

    # 5. Every SHIPPED source-drive template agrees with the gate.
    cli_dir = os.path.join(REPO, "Resources", "extension_CLI")
    ext_root = os.path.join(os.path.dirname(REPO), "External_extensions")
    checked = 0
    for ext in sorted(os.listdir(cli_dir)) if os.path.isdir(cli_dir) else []:
        templates = os.path.join(cli_dir, ext, "templates")
        source = os.path.join(ext_root, ext)
        if not (os.path.isdir(templates) and os.path.isdir(source)):
            continue
        arities = _method_arities(source)
        for name in sorted(os.listdir(templates)):
            with open(os.path.join(templates, name), encoding="utf-8") as handle:
                code = handle.read()
            if common.SOURCE_DRIVE_MARKER not in code:
                continue
            try:
                tree = ast.parse(code)
            except SyntaxError:
                continue  # unfilled placeholders; not this check's business
            checked += 1
            for node in ast.walk(tree):
                if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
                    continue
                value = node.func.value
                if not (isinstance(value, ast.Name) and value.id == "_widget"):
                    continue
                required = arities.get(node.func.attr)
                if isinstance(required, int) and len(node.args) < required:
                    fails.append(
                        "%s/%s: %s called with %d arg(s), widget requires %d"
                        % (ext, name, node.func.attr, len(node.args), required)
                    )

    if fails:
        print("\n".join("FAIL: " + item for item in fails))
        return 1
    print(
        "OK: emitter and api-proof arity gate agree "
        "(%d shipped source-drive template(s) cross-checked)" % checked
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
