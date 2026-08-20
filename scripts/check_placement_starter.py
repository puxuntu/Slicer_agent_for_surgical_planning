"""A placement armed by the extension must not be re-armed by the runtime.

When a cookbook step says "click Manually separate" and the next says "click a
point and adjust the plane", the handler behind the button has ALREADY created the
markup, pointed the active list at it, entered place mode, and observed
PointPositionDefinedEvent -- the click is what makes the extension build the
cutting plane. If the generated interaction step creates its own markup node and
re-points the active list, the click lands in the runtime's node instead, the
observer never fires, and the plane never appears. Nothing raises. The step simply
does nothing, which is the hardest kind of defect to find in a generated package.

`_find_recent_placement_starter_for_interaction` exists to prevent exactly that,
and on PelvicFracturePlanning it could not fire, for three compounding reasons:
the starter scan read only the LOGIC class (the handler is on the WIDGET, which is
where Slicer's module template puts GUI actions); the step that drives it carries
only `widget_name`, which `_step_placement_starter` did not resolve; and the
binding required the interaction step's node_class to match, while the LLM had
read "adjust the cutting plane" as a plane and the click actually places a
fiducial.

Runs OUTSIDE Slicer::

    python scripts/check_placement_starter.py
"""
import ast
import importlib.util
import json
import os
import re
import sys
import types

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(REPO, "SlicerAIAgentLib", "extension_cli_analyzer")
EXT_ROOT = os.path.join(os.path.dirname(REPO), "External_extensions")
CLI_ROOT = os.path.join(REPO, "Resources", "extension_CLI")

CASE_EXT = "PelvicFracturePlanning"
CASE_WIDGET = "PelvicFracturePlanningWidget"
CASE_STARTER = "onManualSplit"
CASE_ARMED = "vtkMRMLMarkupsFiducialNode"
CASE_DECLARED = "vtkMRMLMarkupsPlaneNode"
CASE_BUTTON_STEP = "cb_step_7"
CASE_INTERACTION_STEP = "cb_step_8"

for _name in ("slicer", "vtk", "qt", "ctk"):
    sys.modules.setdefault(_name, types.ModuleType(_name))

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


_load("common")
scan = _load("scan")
slicer_op_manifest = _load("slicer_op_manifest")
cross_stage = _load("cross_stage")
template_helpers = _load("template_helpers")
workflow_contracts = _load("workflow_contracts")


class _Probe(
    cross_stage.AnalyzerCrossStageMixin,
    workflow_contracts.AnalyzerWorkflowContractsMixin,
    template_helpers.AnalyzerTemplateHelpersMixin,
    slicer_op_manifest.AnalyzerSlicerOpManifestMixin,
    scan.AnalyzerScanMixin,
):
    """The analyzer reduced to the mixins this chain touches."""

    def __init__(self):
        self._widget_class_info = {}
        self._placement_starter_methods = {}
        self._widget_connections = []
        self.llm_client = None

    def on_progress(self, *args, **kwargs):
        pass


def _widget_connections(probe, source_path, source_text, class_name):
    """The scanned button -> handler connections, with a dev-interpreter fallback.

    `scan.py` matches a connect()'s signal argument as `ast.Constant`, which is
    Python 3.8+; on a 3.7 interpreter a string literal is `ast.Str`, so the real
    scanner returns nothing OUTSIDE Slicer. Slicer ships 3.9+, and the generated
    `[source drive]` templates naming these handlers are the evidence it works
    there. Re-derive them textually so the rest of this check exercises the code
    under test instead of the interpreter.
    """
    connections = probe._extract_widget_connections(
        probe._extract_class_source(source_path, class_name) or ""
    )
    if connections:
        return connections, False
    return [
        {"button_widget_name": widget, "signal": signal, "handler_method": handler}
        for widget, signal, handler in re.findall(
            r"self\.ui\.(\w+)\.connect\(\s*'([^']+)'\s*,\s*self\.(\w+)\s*\)", source_text
        )
    ], True


def _widget_classes(root):
    """Every *Widget class under an extension source tree, as (file, class_name)."""
    found = []
    for directory, _dirs, files in os.walk(root):
        for name in files:
            if not name.endswith(".py"):
                continue
            path = os.path.join(directory, name)
            try:
                with open(path, encoding="utf-8", errors="ignore") as handle:
                    tree = ast.parse(handle.read())
            except Exception:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name.endswith("Widget"):
                    found.append((path, node.name))
    return found


def main():
    fails = []
    case_source = os.path.join(EXT_ROOT, CASE_EXT, CASE_EXT + ".py")
    if not os.path.isfile(case_source):
        print("SKIP: %s source not found at %s" % (CASE_EXT, case_source))
        return 0
    with open(case_source, encoding="utf-8") as handle:
        source_text = handle.read()

    probe = _Probe()
    probe._widget_class_info = {"file": case_source, "class_name": CASE_WIDGET}
    probe._widget_connections, fallback = _widget_connections(
        probe, case_source, source_text, CASE_WIDGET
    )
    if fallback:
        print("(dev interpreter: %d connections re-derived textually)"
              % len(probe._widget_connections))

    # 0. Each method's source is bounded by its own block, not by the end of the
    #    file. `end_lineno` is 3.8+, and a "rest of the file" fallback makes every
    #    method contain every marker -- i.e. classifies the whole class as a starter.
    sources = probe._widget_method_sources()
    if CASE_STARTER not in sources:
        fails.append("widget method sources missing %s" % CASE_STARTER)
    elif "def onConfirmSplit" in sources[CASE_STARTER]:
        fails.append("method source bleeds into the next method (unbounded extraction)")

    # 1. The widget handler is seen as a placement starter, arming its own class.
    starters = probe._classify_placement_starter_methods(
        {"_logic_file": case_source, "methods": []}
    )
    probe._placement_starter_methods = starters
    info = starters.get(CASE_STARTER)
    if not info:
        fails.append("%s not detected as a placement starter" % CASE_STARTER)
    else:
        if info.get("node_classes") != [CASE_ARMED]:
            fails.append("%s arms %r, expected [%r]"
                         % (CASE_STARTER, info.get("node_classes"), CASE_ARMED))
        if not info.get("has_placement_observer"):
            fails.append("%s placement observer not seen" % CASE_STARTER)
        if info.get("receiver") != "widget":
            fails.append("%s receiver %r, expected 'widget'" % (CASE_STARTER, info.get("receiver")))

    # 2. A widget-side starter must not reach the template that emits logic.<m>().
    if probe._is_logic_placement_starter(CASE_STARTER):
        fails.append("%s would be called on the logic object" % CASE_STARTER)

    workflow = os.path.join(CLI_ROOT, CASE_EXT, "workflow.json")
    if not os.path.isfile(workflow):
        print("\n".join("FAIL: " + item for item in fails) if fails
              else "OK (workflow.json absent; contract half not checked)")
        return 1 if fails else 0
    with open(workflow, encoding="utf-8") as handle:
        steps = json.load(handle)["steps"]
    by_id = {step["step_id"]: step for step in steps}

    # 3. The button step resolves to its starter through widget_name alone: it
    #    carries no method_name and no extension_method_hint.
    button_step = by_id.get(CASE_BUTTON_STEP, {})
    resolved = probe._step_placement_starter(button_step)
    if resolved != CASE_STARTER:
        fails.append("%s resolves to %r, expected %r"
                     % (CASE_BUTTON_STEP, resolved, CASE_STARTER))

    # 4. The interaction step binds to it and adopts the class actually armed.
    index = next(
        (i for i, s in enumerate(steps) if s["step_id"] == CASE_INTERACTION_STEP), None
    )
    if index is None:
        fails.append("%s missing from workflow.json" % CASE_INTERACTION_STEP)
    else:
        step = by_id[CASE_INTERACTION_STEP]
        declared_before = step.get("node_class")
        binding = probe._find_recent_placement_starter_for_interaction(steps, index)
        if binding.get("method") != CASE_STARTER:
            fails.append("%s did not bind to %s (binding=%r)"
                         % (CASE_INTERACTION_STEP, CASE_STARTER, binding))
        if declared_before == CASE_DECLARED and binding.get("node_class") != CASE_ARMED:
            fails.append("binding node_class %r, expected the armed %r"
                         % (binding.get("node_class"), CASE_ARMED))
        if binding.get("adopt_node_class"):
            probe._adopt_placement_starter_node_class(step, binding)
        if step.get("node_class") != CASE_ARMED:
            fails.append("%s node_class not adopted (%r)"
                         % (CASE_INTERACTION_STEP, step.get("node_class")))
        if step.get("creates_node") is not False:
            fails.append("%s still claims to create the node it reuses" % CASE_INTERACTION_STEP)
        for sub in step.get("sub_operations") or []:
            if sub.get("op_type") != "user_interaction":
                continue
            if sub.get("node_class") != CASE_ARMED or sub.get("creates_node") is not False:
                fails.append("%s sub-operation not adopted: %r / %r"
                             % (CASE_INTERACTION_STEP, sub.get("node_class"),
                                sub.get("creates_node")))

        # 5. And the resulting policy leaves the extension holding the placement.
        step["interaction_owner"] = "previous_extension_method"
        policy = probe._placement_mode_policy(step, starters.get(CASE_STARTER))
        if policy.get("should_set_active_list") or policy.get("should_enter_placement_mode"):
            fails.append("policy would re-arm placement over the extension: %r" % policy)

    # 6. Blast radius: scanning widget classes must not invent starters elsewhere.
    gained = {}
    for ext in sorted(os.listdir(EXT_ROOT)) if os.path.isdir(EXT_ROOT) else []:
        root = os.path.join(EXT_ROOT, ext)
        if not os.path.isdir(root):
            continue
        names = set()
        for path, class_name in _widget_classes(root):
            sweep = _Probe()
            sweep._widget_class_info = {"file": path, "class_name": class_name}
            names |= set(sweep._classify_placement_starter_methods(
                {"_logic_file": path, "methods": []}
            ))
        if names:
            gained[ext] = sorted(names)
    print("widget-side starters across the cookbook extensions: %s"
          % (json.dumps(gained) if gained else "none"))
    if set(gained) - {CASE_EXT}:
        # Not a failure -- a real starter elsewhere is exactly what this scan is
        # for -- but it changes those packages on regeneration, so say so loudly.
        print("NOTE: extensions beyond %s now have widget-side starters; their "
              "interaction steps will bind differently on regeneration." % CASE_EXT)

    if fails:
        print("\n".join("FAIL: " + item for item in fails))
        return 1
    print("OK: the extension's own placement arming is detected, bound, and left alone")
    return 0


if __name__ == "__main__":
    sys.exit(main())
