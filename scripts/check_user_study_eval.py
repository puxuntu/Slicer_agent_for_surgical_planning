"""Check the user-study evaluation (``experiments/user_study.py``) outside Slicer.

Run from the repository root::

    python scripts/check_user_study_eval.py

Everything here runs against a SYNTHETIC Results/Dataset tree in a temporary
folder with a stub analysis, so it touches no real run, computes no real metric
and writes nothing under Experiments/. What it pins:

  1. folder names parse into (arm, procedure, participant); P2 sorts before P10
  2. discovery: one group per folder, whatever the count; the procedure comes
     from the RUN folder names; unsaved runs and runs filed under the wrong arm
     are reported; Dataset/<procedure> is paired; the output is
     Quanti_Quali_Eva/<folder>.xlsx
  3. a folder's runs are listed in the order they were PERFORMED, and a missing
     Dataset folder never turns into a relative path
  4. run_group hands the procedure's build_report the explicit cases= run set,
     the right first argument and the panel defaults, and wraps its sheets in
     Run set + Interaction, whose numbers are the recorder's own
  5. every registered analysis is a module whose EXTENSION_NAME matches its key
     and whose build_report accepts ``cases`` and ``progress``
  6. the study folder is found when its tier is renamed
  7. the panel is wired into the Experiments group, above-content ordering kept
"""

import ast
import io
import json
import os
import shutil
import sys
import tempfile
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

for _name in ("slicer", "qt", "vtk", "ctk"):
    sys.modules.setdefault(_name, types.ModuleType(_name))

from SlicerAIAgentLib.experiments import user_study          # noqa: E402
from SlicerAIAgentLib.experiments import workbook             # noqa: E402

FAILURES = []
EXPERIMENTS = os.path.join(ROOT, "SlicerAIAgentLib", "experiments")
AGENT, EXT = u"【Agent】", u"【Extension】"


def check(label, condition):
    print(("PASS  " if condition else "FAIL  ") + label)
    if not condition:
        FAILURES.append(label)


def section(title):
    print("")
    print("=== " + title)


def folder(arm, procedure, participant):
    return u"%s%s【%s】" % (arm, procedure, participant)


def make_run(parent, name, subject, saved=True, wall=None, totals=None, counts=None):
    run = os.path.join(parent, name)
    os.makedirs(os.path.join(run, "runtime"))
    if saved:
        os.makedirs(os.path.join(run, "Statistic", "scene"))
    with io.open(os.path.join(run, "runtime", "run_manifest.json"), "w", encoding="utf-8") as h:
        h.write(json.dumps({"subject": subject}))
    if wall is not None:
        with io.open(os.path.join(run, "runtime", "interaction.json"), "w", encoding="utf-8") as h:
            h.write(json.dumps({"wall_seconds": wall, "elapsed_seconds": wall,
                                "paused_seconds": 0, "pause_count": 0,
                                "totals": totals or {}, "counts": counts or {}}))
    return run


def build_tree(base):
    study = os.path.join(base, "Experiments", "3_User_Study")
    results = os.path.join(study, "Results")
    psp = "Pedicle Screw Planning"
    a1 = os.path.join(results, folder(AGENT, psp, "P1"))
    e1 = os.path.join(results, folder(EXT, psp, "P1"))
    a10 = os.path.join(results, folder(AGENT, psp, "P10"))
    a2 = os.path.join(results, folder(AGENT, psp, "P2"))
    odd = os.path.join(results, folder(AGENT, "Unknown Thing", "P2"))
    for path in (a1, e1, a10, a2, odd, os.path.join(results, "Not a study folder")):
        os.makedirs(path)
    totals = {"view_3d": 10, "view_2d": 20, "panel": 5, "other": 1, "compute": 4,
              "idle": 60, "away": 0}
    counts = {"clicks_total": 30, "clicks_view_3d": 10, "clicks_view_2d": 12,
              "clicks_panel": 6, "clicks_other": 2, "drags": 4, "drag_pixels": 1234.5,
              "wheel_notches": 7, "keys": 3, "double_clicks": 1}
    # named so that NAME order and PERFORMED order disagree
    make_run(a1, "PedicleScrewPlanner_3_pipeline_20260101_100000", "3", wall=100.0,
             totals=totals, counts=counts)
    make_run(a1, "PedicleScrewPlanner_1_304_pipeline_20260101_090000", "1_304", wall=120.0,
             totals=dict(totals, idle=80), counts=counts)
    make_run(a1, "PedicleScrewPlanner_19_pipeline_20260101_110000", "19", saved=False)
    make_run(e1, "PedicleScrewPlanner_3_manual_20251231_100000", "3", wall=300.0,
             totals=totals, counts=counts)
    make_run(e1, "PedicleScrewPlanner_1_304_pipeline_20251231_090000", "1_304")  # wrong arm
    make_run(a10, "PedicleScrewPlanner_3_pipeline_20260105_100000", "3")
    make_run(a2, "PedicleScrewPlanner_3_pipeline_20260103_100000", "3")
    make_run(odd, "FooPlanner_1_pipeline_20260102_100000", "1")
    for subject in ("3", "1_304"):
        os.makedirs(os.path.join(study, "Dataset", psp, subject))
    return study


# ---------------------------------------------------------------------------

def check_names():
    section("1. Results folder names")
    parsed = user_study.parse_folder(folder(AGENT, "Mandible Reconstruction", "P1"))
    check("arm / procedure / participant parsed",
          parsed == {"arm": "Agent", "procedure": "Mandible Reconstruction",
                     "participant": "P1"})
    check("an extension-arm folder parses",
          (user_study.parse_folder(folder(EXT, "Orbital Fracture Reconstruction", "P12"))
           or {}).get("participant") == "P12")
    for bad in ("Mandible Reconstruction", u"【Agent】Mandible", "", "Pedicle_P1"):
        check("not a study folder: %r" % bad, user_study.parse_folder(bad) is None)
    order = sorted(["P10", "P2", "P1"], key=user_study.participant_key)
    check("participants sort by number (P1, P2, P10): %s" % order, order == ["P1", "P2", "P10"])


def check_discovery(study):
    section("2. Discovery")
    groups = user_study.discover_groups(study)
    names = [g["folder"] for g in groups]
    check("one group per study folder, the stray folder ignored (%d)" % len(groups),
          len(groups) == 5 and "Not a study folder" not in names)
    psp = [g for g in groups if g["procedure"] == "Pedicle Screw Planning"]
    check("sorted by procedure, then participant (P1, P2, P10), Agent before Extension",
          [(g["participant"], g["arm"]) for g in psp]
          == [("P1", "Agent"), ("P1", "Extension"), ("P2", "Agent"), ("P10", "Agent")])
    a1 = psp[0]
    check("the procedure is read from the RUN names", a1["extension"] == "PedicleScrewPlanner")
    check("...and mapped to its analysis", (a1["analysis"] or {}).get("module") == "pedicle")
    check("only runs with a saved scene are scorable (2 of 3)",
          len(a1["runs"]) == 3 and len(a1["saved_runs"]) == 2)
    check("the unsaved run is reported by name",
          any("PedicleScrewPlanner_19_pipeline" in p for p in a1["problems"]))
    e1 = psp[1]
    check("a pipeline run inside the Extension folder is reported",
          any("pipeline run in the Extension folder" in p for p in e1["problems"]))
    check("Dataset/<procedure> is paired",
          a1["dataset_dir"] == os.path.join(study, "Dataset", "Pedicle Screw Planning"))
    check("the output is Quanti_Quali_Eva/<folder>.xlsx",
          a1["output"] == os.path.join(study, "Quanti_Quali_Eva", a1["folder"] + ".xlsx"))
    odd = [g for g in groups if g["procedure"] == "Unknown Thing"][0]
    check("an unregistered procedure is listed with no analysis",
          odd["extension"] == "FooPlanner" and odd["analysis"] is None)
    check("...and no dataset folder", odd["dataset_dir"] == "")
    return groups


def check_cases(groups):
    section("3. A folder's run set")
    a1 = groups[0]
    cases = user_study.group_cases(a1)
    check("runs listed in PERFORMED order, not name order: %s" % [c["subject"] for c in cases],
          [c["subject"] for c in cases] == ["1_304", "3"])
    check("each carries its order", [c["order"] for c in cases] == [1, 2])
    check("each is paired with Dataset/<procedure>/<subject>",
          cases[0]["dataset_dir"].endswith(os.path.join("Pedicle Screw Planning", "1_304")))
    odd = [g for g in groups if g["procedure"] == "Unknown Thing"][0]
    check("no Dataset folder -> an empty dataset_dir, never a relative path",
          all(c["dataset_dir"] == "" for c in user_study.group_cases(odd)))


def check_run_group(study, groups):
    section("4. run_group drives the procedure's own build_report")
    calls = {}

    def fake_build_report(first, progress=None, cases=None, **options):
        calls["first"], calls["cases"], calls["options"] = first, cases, options
        if progress:
            progress(0, len(cases), cases[0]["subject"])
        return {"sheets": [("Screw accuracy", [("x", ["case"], [{"case": "3"}])])],
                "log": ["9_9: FAILED -- boom"], "failed_cases": []}

    fake = types.ModuleType("SlicerAIAgentLib.experiments._check_fake_analysis")
    fake.build_report = fake_build_report
    sys.modules[fake.__name__] = fake
    written = {}

    def fake_write(path, sheets):
        written["path"], written["sheets"] = path, sheets
        return path, []

    saved_spec = dict(user_study.ANALYSES["PedicleScrewPlanner"])
    saved_write = workbook.write_workbook
    user_study.ANALYSES["PedicleScrewPlanner"] = {
        "module": "_check_fake_analysis", "first": "runs",
        "options": {"with_density": True}, "scene": False}
    workbook.write_workbook = fake_write
    try:
        group = dict(groups[0], analysis=user_study.ANALYSES["PedicleScrewPlanner"])
        ticks = []
        report = user_study.run_group(ROOT, group, progress=lambda *a: ticks.append(a))
        check("build_report got the explicit run set (cases=)",
              [c["run"] for c in calls["cases"]]
              == [c["run"] for c in user_study.group_cases(group)])
        check("...the folder as its first argument for a 'runs' analysis",
              calls["first"] == group["runs_dir"])
        check("...and the panel's defaults", calls["options"] == {"with_density": True})
        check("the progress callback reached the caller", bool(ticks))
        titles = [title for title, _ in written["sheets"]]
        check("sheets: Run set, the procedure's own, Interaction (%s)" % titles,
              titles == ["Run set", "Screw accuracy", "Interaction"])
        check("written to the group's output", written["path"] == group["output"])
        rows = written["sheets"][-1][1][0][2]
        first = rows[0]
        check("Interaction rows are the recorder's numbers, in performed order",
              [r["case"] for r in rows] == ["1_304", "3"] and first["wall_s"] == 120.0)
        check("hands_on_s is the four operating states (10+20+5+1)", first["hands_on_s"] == 36.0)
        check("clicks and drag travel are carried through",
              first["clicks_total"] == 30 and first["drag_pixels"] == 1234.5)
        summary = written["sheets"][-1][1][1][2]
        mean = [r for r in summary if r["case"] == "mean"][0]
        check("a mean row over the runs (wall 110)", mean["wall_s"] == 110.0)
        check("a failure in the procedure's log is surfaced",
              user_study.failures_in(report) == ["9_9"])
        check("the unsaved run is named in the workbook's log",
              any("PedicleScrewPlanner_19" in line for line in report["log"]))

        user_study.ANALYSES["PedicleScrewPlanner"] = dict(
            user_study.ANALYSES["PedicleScrewPlanner"], first="repository")
        group = dict(groups[0], analysis=user_study.ANALYSES["PedicleScrewPlanner"])
        user_study.run_group(ROOT, group)
        check("a 'repository' analysis gets the checkout as its first argument",
              calls["first"] == ROOT)
    finally:
        user_study.ANALYSES["PedicleScrewPlanner"] = saved_spec
        workbook.write_workbook = saved_write
        sys.modules.pop(fake.__name__, None)


def _function_args(tree, name):
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return [a.arg for a in node.args.args] + [a.arg for a in node.args.kwonlyargs]
    return None


def _assigned_string(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == name for t in node.targets):
            value = node.value
            return getattr(value, "s", getattr(value, "value", None))
    return None


def check_registered_analyses():
    section("5. Every registered analysis can take a run set")
    for extension, spec in sorted(user_study.ANALYSES.items()):
        path = os.path.join(EXPERIMENTS, spec["module"] + ".py")
        if not os.path.isfile(path):
            check("%s: %s.py exists" % (extension, spec["module"]), False)
            continue
        tree = ast.parse(io.open(path, encoding="utf-8").read())
        check("%s: %s.EXTENSION_NAME matches" % (extension, spec["module"]),
              _assigned_string(tree, "EXTENSION_NAME") == extension)
        args = _function_args(tree, "build_report") or []
        check("%s: build_report accepts cases= and progress=" % extension,
              "cases" in args and "progress" in args)
        unknown = [k for k in spec.get("options") or {} if k not in args]
        check("%s: every default option is a build_report parameter" % extension, not unknown)


def check_study_resolution(base):
    section("6. Locating the study folder")
    check("the declared Experiments/3_User_Study wins",
          user_study.resolve_study_dir(base)
          == os.path.join(base, "Experiments", "3_User_Study"))
    renamed = os.path.join(base, "Experiments", "9_Renamed_Study")
    os.rename(os.path.join(base, "Experiments", "3_User_Study"), renamed)
    try:
        check("a renamed tier is found by its Results folders",
              user_study.resolve_study_dir(base) == renamed)
    finally:
        os.rename(renamed, os.path.join(base, "Experiments", "3_User_Study"))
    empty = tempfile.mkdtemp(prefix="userstudy_empty_")
    try:
        check("nothing there -> the declared path, so messages name a real place",
              user_study.resolve_study_dir(empty)
              == os.path.join(empty, "Experiments", "3_User_Study"))
    finally:
        shutil.rmtree(empty, ignore_errors=True)


def check_wiring():
    section("7. Panel wiring")
    widget = io.open(os.path.join(ROOT, "SlicerAIAgentLib", "app", "widget_experiments.py"),
                     encoding="utf-8").read()
    check("_setupExperiments builds the user-study section",
          "self._setupUserStudySection()" in widget and "user_study_panel" in widget)
    check("new per-extension content is inserted ABOVE the section",
          "insertWidget(index, content)" in widget and "_userStudyGroup" in widget)
    panel = io.open(os.path.join(EXPERIMENTS, "user_study_panel.py"), encoding="utf-8").read()
    check("the panel computes only from its buttons (no run_group outside run())",
          panel.count("user_study.run_group(") == 1)


def main():
    base = tempfile.mkdtemp(prefix="userstudy_check_")
    try:
        study = build_tree(base)
        check_names()
        groups = check_discovery(study)
        check_cases(groups)
        check_run_group(study, groups)
        check_registered_analyses()
        check_study_resolution(base)
        check_wiring()
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print("")
    if FAILURES:
        print("%d CHECK(S) FAILED:" % len(FAILURES))
        for label in FAILURES:
            print("  - " + label)
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
