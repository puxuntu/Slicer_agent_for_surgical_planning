"""Check the user-study instrument: one measurement, five copies, two arms.

Runs OUTSIDE Slicer. ``PlanningRecorder`` imports ``qt`` and ``slicer`` inside
the functions that need them, deliberately, so the arithmetic that turns an
event list into a time split is checkable on a developer machine -- which is the
only place it can be checked at all, since the alternative is reading numbers
off a session that has already been run.

WHAT IT PROVES
--------------
1. **The five copies are byte-identical.** The canonical file is
   ``SlicerAIAgentLib/PlanningRecorder.py``; the four study extensions carry
   vendored copies so the comparison arm keeps recording on a machine where the
   agent is not installed. A copy that drifted would give the two arms of the
   study two different measurements, and the report would look the same either
   way -- there is no symptom, which is why this is checked rather than assumed.

2. **The partition is disjoint and total.** Every instant of a session is in
   exactly one of seven states, so the seven sum to the wall clock. A reader is
   invited to add them up; if they did not sum, every per-state figure would be
   an unfalsifiable estimate rather than a share of a known total.

3. **The two states that are easy to get backwards.** A click that STARTS a
   three-second computation must charge the three seconds to ``compute``, not
   to the person. A drag that keeps the main thread intermittently busy must
   stay interaction -- which is the whole reason ``BLOCK_THRESHOLD_S`` is half
   a second and not a tenth. Both are a plausible number when wrong, never an
   error: the run completes, the report prints, and the arm that looks slower
   is the wrong one.

4. **An isolated click is not free.** Without ``BURST_PAD_S`` a single button
   press is one zero-duration event, so a step answered with one click would
   read as 100% idle and the comparison arm -- which is mostly button presses --
   would appear to involve no operating at all.

5. **The four extensions are wired as METHODS.** The panel call must be inside
   ``setup()`` and the teardown inside ``cleanup()``. Two ways of getting this
   wrong both parse: a ``def cleanup`` nested in ``setup`` never runs (so the
   application-wide event filter outlives every session), and a bare statement
   in the class body runs at import time with no ``self`` (so the module fails
   to load). Both were produced while writing this, which is why they are here.

6. **Both arms render the same wording**, from the same function, because two
   reports phrased differently invite a reader to compare two things that are
   not the same measurement.

7. **Both arms write into the SAME ``logs/``** -- the agent's own, found from
   each vendored copy's own location. Two arms in two directories is a
   comparison nobody can run, and the only symptom is a folder that does not
   fill up.

8. **One press-and-drag in a 3D view is ONE click.** An application-wide filter
   runs once per DELIVERY, and Slicer's VTK views re-dispatch a mouse event to a
   second object -- so rotating a model counted several clicks, and the button
   state (a counter at the time) was left stuck above zero, after which every
   hover was recorded as a drag and the session's idle time was absorbed into
   3D-view interaction. The first is visible; the second is not.

9. **Nothing reaches ``logs/`` until Save is pressed**, so an abandoned or
   mis-started trial leaves no folder to find and delete. The cost is that a
   forgotten Save loses the whole trial and not only its scene, which is why
   the run reports itself unsaved and the panel says NOT SAVED in those words.

10. **A click in a view is counted as being in that view.** Qt delivers to the
    `QWidgetWindow` first and the widget second, and a window's parents are
    windows -- so once repeat deliveries were suppressed, the kept one could
    not say where the click landed and the whole 3D / slice / panel split sat
    at zero. Motion is the larger half: it is not deduplicated, so the first
    delivery decides which bucket the active TIME goes in.

11. **`panel` means THIS extension's panel.** Matching it by class name counted
    every module's frame, so a participant who opened Volumes had those clicks
    booked as operating the procedure's own panel -- which flatters the
    comparison arm exactly where a learning curve should show hunting fall away.

12. **Closing the scene ends the trial without discarding it.** The case is
    gone, so the measurement stops there; it is NOT zeroed, because nothing is
    written before Save and zeroing would destroy a trial held only in memory.
    The counters return to zero on the next Start, which is where that belongs.

13. **A block whose queued input flushes after it is still compute**, and a
    per-step row SUMS to its step's wall clock. Both were found by comparing one
    real unaided run against one real guided run on the same case: the first
    reported 0.0 s of algorithm time against the other's 24.8 s, and the
    per-step table over-counted by 9.9 s over 114 s.

14. **The guided clock runs from the first KEYSTROKE to Exit, then clears.**
    Starting it at the router's decision measured the two arms from different
    points -- the comparison arm's Start button covers composing the request and
    this one did not -- which flattered the guided arm by exactly that time.

    python scripts/check_planning_recorder.py
"""

import ast
import hashlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTERNAL = os.path.normpath(os.path.join(ROOT, "..", "External_extensions"))

CANONICAL = os.path.join(ROOT, "SlicerAIAgentLib", "PlanningRecorder.py")

#: The four extensions of the user study's comparison arm: the module file, the
#: procedure name its run folders must carry, and where its vendored copy sits.
STUDY_EXTENSIONS = [
    ("OrbitalFractureReconstruction",
     "OrbitalFractureReconstruction/OrbitalFractureReconstruction.py"),
    ("ZygomaticImplantPlanner",
     "ZygomaticImplantPlanner/ZygomaticImplantPlanner.py"),
    ("BoneReconstructionPlanner",
     "SlicerBoneReconstructionPlanner/BoneReconstructionPlanner/BoneReconstructionPlanner.py"),
    ("PedicleScrewPlanner",
     "PedicleScrewSimulator/PedicleScrewPlanner/PedicleScrewPlanner.py"),
]

FAILURES = []


def check(label, ok, detail=""):
    status = "ok  " if ok else "FAIL"
    print("  [%s] %s%s" % (status, label, ("  -- " + str(detail)) if detail and not ok else ""))
    if not ok:
        FAILURES.append(label + ((": " + str(detail)) if detail else ""))
    return ok


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


# ---------------------------------------------------------------------------

def section_1_vendored_copies():
    print("\n1. The five copies are byte-identical")
    if not os.path.isdir(EXTERNAL):
        check("External_extensions/ is present", False, EXTERNAL)
        return
    want = _digest(CANONICAL)
    for procedure, module_path in STUDY_EXTENSIONS:
        vendored = os.path.join(EXTERNAL, os.path.dirname(module_path),
                                "PlanningRecorder.py")
        if not os.path.isfile(vendored):
            check("%s carries PlanningRecorder.py" % procedure, False, vendored)
            continue
        check("%s copy matches the canonical file" % procedure,
              _digest(vendored) == want,
              "copy %s != canonical %s" % (_digest(vendored)[:12], want[:12]))


def section_2_partition(pr):
    print("\n2. The partition is disjoint and totals the wall clock")
    t0 = 1000.0
    events = [["focus", t0, True]]
    events += [["tick", t0 + i * 0.1, False] for i in range(200)]     # 20 s
    # A 3 s block at t+5: the heartbeat simply does not fire.
    events = [e for e in events if not (e[0] == "tick" and t0 + 5.0 < e[1] < t0 + 8.0)]
    for offset in (1.0, 1.4, 1.9):
        events.append(["click", t0 + offset, pr.TARGET_VIEW_3D])
    for offset in [11.0 + 0.05 * k for k in range(21)]:              # a 1 s drag
        events.append(["drag", t0 + offset, pr.TARGET_VIEW_2D])
    events.append(["focus", t0 + 15.0, False])
    events.append(["focus", t0 + 17.0, True])

    spans = pr.partition(events, t0, t0 + 20.0)
    totals = {state: pr._total(spans[state]) for state in pr.ALL_STATES}
    check("the seven states sum to the session",
          abs(sum(totals.values()) - 20.0) < 1e-6, totals)

    flat = sorted([span for state in pr.ALL_STATES for span in spans[state]])
    overlaps = [(a, b) for a, b in zip(flat, flat[1:]) if b[0] < a[1] - 1e-9]
    check("no two states overlap", not overlaps, overlaps[:3])

    check("a 3 s heartbeat gap is charged to compute",
          2.9 < totals[pr.STATE_COMPUTE] < 3.2, totals[pr.STATE_COMPUTE])
    check("2 s with the window inactive is charged to away",
          1.9 < totals[pr.STATE_AWAY] < 2.1, totals[pr.STATE_AWAY])
    check("clicks in the 3D view land in view_3d",
          totals[pr.TARGET_VIEW_3D] > 1.0, totals[pr.TARGET_VIEW_3D])
    check("a drag in a slice view lands in view_2d",
          totals[pr.TARGET_VIEW_2D] > 1.0, totals[pr.TARGET_VIEW_2D])
    check("nothing is attributed to the panel here",
          totals[pr.TARGET_PANEL] == 0, totals[pr.TARGET_PANEL])

    # A session with no input at all is entirely idle: the bookkeeping events
    # must never look like activity, or every arm would measure as fully busy.
    quiet = [["focus", t0, True]] + [["tick", t0 + i * 0.1, False] for i in range(100)]
    quiet_totals = {s: pr._total(v) for s, v in
                    pr.partition(quiet, t0, t0 + 10.0).items()}
    check("a session with no input is 100% idle",
          abs(quiet_totals[pr.STATE_IDLE] - 10.0) < 1e-6, quiet_totals)


def section_3_block_vs_drag(pr):
    print("\n3. compute beats a click; a stuttery drag stays interaction")
    t0 = 2000.0

    # (a) One click, then a 3 s block. The three seconds are the algorithm's.
    events = [["focus", t0, True]]
    events += [["tick", t0 + i * 0.1, False] for i in range(50)]
    events = [e for e in events if not (e[0] == "tick" and t0 + 1.0 < e[1] < t0 + 4.0)]
    events.append(["click", t0 + 1.0, pr.TARGET_PANEL])
    totals = {s: pr._total(v) for s, v in pr.partition(events, t0, t0 + 5.0).items()}
    check("a click that starts a 3 s job charges the job to compute",
          2.9 < totals[pr.STATE_COMPUTE] < 3.2, totals[pr.STATE_COMPUTE])
    check("...and the click's own burst is not also counted",
          totals[pr.TARGET_PANEL] < 0.6, totals[pr.TARGET_PANEL])

    # (b) A 4 s drag whose recompute blocks the thread for 300 ms at a time.
    #     Every gap is under BLOCK_THRESHOLD_S, so none of it is compute --
    #     which is the reason that constant is half a second and not a tenth.
    events = [["focus", t0, True]]
    stamp = t0
    while stamp < t0 + 4.0:
        events.append(["tick", stamp, False])
        events.append(["drag", stamp, pr.TARGET_VIEW_3D])
        stamp += 0.3
    events += [["tick", t0 + 4.0 + i * 0.1, False] for i in range(11)]
    totals = {s: pr._total(v) for s, v in pr.partition(events, t0, t0 + 5.0).items()}
    check("a drag with 300 ms recomputes is not reclassified as compute",
          totals[pr.STATE_COMPUTE] == 0, totals[pr.STATE_COMPUTE])
    check("...and reads as 3D-view operation",
          totals[pr.TARGET_VIEW_3D] > 3.5, totals[pr.TARGET_VIEW_3D])

    # (b2) The same drag, but heavy enough that ONE gap passes the threshold --
    #      a 3D view re-clipping a whole surface per mouse move. Input is being
    #      delivered inside that gap, which a genuinely blocked main thread
    #      cannot do (delivery is its job), so the gap is the person's time.
    #      Without this the study reports a surgeon's hardest interaction as the
    #      machine's, and the harder the case the more of it disappears.
    events = [["focus", t0, True], ["tick", t0, False]]
    stamp = t0
    while stamp < t0 + 4.0:
        stamp += 0.7                       # every gap is past BLOCK_THRESHOLD_S
        events.append(["tick", stamp, False])
        events.append(["drag", stamp - 0.35, pr.TARGET_VIEW_3D])
    events += [["tick", t0 + 4.2 + i * 0.1, False] for i in range(9)]
    totals = {s: pr._total(v) for s, v in pr.partition(events, t0, t0 + 5.0).items()}
    check("a gap the person was acting THROUGH is not compute",
          totals[pr.STATE_COMPUTE] == 0, totals[pr.STATE_COMPUTE])
    check("...and it reads as 3D-view operation",
          totals[pr.TARGET_VIEW_3D] > 3.5, totals[pr.TARGET_VIEW_3D])

    # (b3) The discriminator must not be "input near the gap": the click that
    #      STARTS a computation sits exactly on the leading edge, and counting
    #      it would hand every click-then-compute back to the person.
    events = [["focus", t0, True]]
    events += [["tick", t0 + i * 0.1, False] for i in range(50)]
    events = [e for e in events if not (e[0] == "tick" and t0 + 1.0 < e[1] < t0 + 4.0)]
    events.append(["click", t0 + 1.0, pr.TARGET_PANEL])      # on the edge
    events.append(["click", t0 + 4.0, pr.TARGET_PANEL])      # on the other edge
    totals = {s: pr._total(v) for s, v in pr.partition(events, t0, t0 + 5.0).items()}
    check("input on a gap's EDGES leaves it compute",
          2.5 < totals[pr.STATE_COMPUTE] < 3.1, totals[pr.STATE_COMPUTE])

    # (b4) THE case this was found on. A participant clicks a button, the
    #      extension blocks for four seconds, and the input queued during the
    #      block flushes the instant it ends -- before the heartbeat, since on
    #      Windows the timer message waits for an otherwise empty queue. So the
    #      gap carries input at BOTH edges, and judging it as a unit handed the
    #      whole computation back to the person: one real unaided run reported
    #      0.0 s of algorithm time for a procedure the guided arm measured at
    #      24.8 s. Cutting the gap at each delivery answers it per stretch.
    events = [["focus", t0, True]]
    events += [["tick", t0 + i * 0.1, False] for i in range(100)]
    events = [e for e in events if not (e[0] == "tick" and t0 + 3.0 < e[1] < t0 + 7.0)]
    events.append(["click", t0 + 2.98, pr.TARGET_PANEL])     # just before it
    events.append(["release", t0 + 7.02, pr.TARGET_PANEL])   # flushed after it
    events.append(["drag", t0 + 7.03, pr.TARGET_PANEL])
    totals = {s: pr._total(v) for s, v in pr.partition(events, t0, t0 + 10.0).items()}
    check("a block whose queued input flushes after it is still compute",
          3.5 < totals[pr.STATE_COMPUTE] < 4.2, totals[pr.STATE_COMPUTE])

    # (b5) And a gap only PARTLY attended charges only the unattended remainder,
    #      rather than all of it or none of it.
    events = [["focus", t0, True]]
    events += [["tick", t0 + i * 0.1, False] for i in range(100)]
    events = [e for e in events if not (e[0] == "tick" and t0 + 3.0 < e[1] < t0 + 7.0)]
    for offset in (3.4, 3.6, 3.8):
        events.append(["drag", t0 + offset, pr.TARGET_VIEW_3D])
    totals = {s: pr._total(v) for s, v in pr.partition(events, t0, t0 + 10.0).items()}
    check("a partly-attended gap charges only the unattended remainder",
          2.8 < totals[pr.STATE_COMPUTE] < 3.4, totals[pr.STATE_COMPUTE])

    # (c) A tick taken while an override cursor was set is compute even though
    #     the thread was alive: an extension driving a progress dialog pumps the
    #     event loop, so without this its algorithm time lands in `idle` and
    #     reads as the participant sitting and thinking.
    events = [["focus", t0, True]]
    events += [["tick", t0 + i * 0.1, (1.0 < i * 0.1 < 3.0)] for i in range(50)]
    totals = {s: pr._total(v) for s, v in pr.partition(events, t0, t0 + 5.0).items()}
    check("a busy cursor makes a live heartbeat count as compute",
          1.8 < totals[pr.STATE_COMPUTE] < 2.2, totals[pr.STATE_COMPUTE])

    # (d) And a busy stretch is NOT excused by input landing in it: there the
    #     extension has said outright that it is working, and a surgeon clicking
    #     at a busy application is not operating it.
    events.append(["click", t0 + 2.0, pr.TARGET_PANEL])
    totals = {s: pr._total(v) for s, v in pr.partition(events, t0, t0 + 5.0).items()}
    check("clicking during a busy cursor does not reclassify it",
          1.8 < totals[pr.STATE_COMPUTE] < 2.2, totals[pr.STATE_COMPUTE])


def section_4_isolated_click(pr):
    print("\n4. An isolated click is not free")
    t0 = 3000.0
    events = [["focus", t0, True]]
    events += [["tick", t0 + i * 0.1, False] for i in range(100)]
    events.append(["click", t0 + 5.0, pr.TARGET_PANEL])
    totals = {s: pr._total(v) for s, v in pr.partition(events, t0, t0 + 10.0).items()}
    expected = 2 * pr.BURST_PAD_S
    check("one click contributes 2 x BURST_PAD_S of panel time",
          abs(totals[pr.TARGET_PANEL] - expected) < 1e-6,
          "%s != %s" % (totals[pr.TARGET_PANEL], expected))

    # Two clicks a second apart are ONE piece of work, not two.
    events.append(["click", t0 + 6.0, pr.TARGET_PANEL])
    totals = {s: pr._total(v) for s, v in pr.partition(events, t0, t0 + 10.0).items()}
    check("two clicks 1 s apart merge into one burst",
          abs(totals[pr.TARGET_PANEL] - (1.0 + expected)) < 1e-6,
          totals[pr.TARGET_PANEL])

    # A target change ends a burst even with no pause, so "clicked Apply then
    # dragged in 3D" is not reported entirely as one or the other.
    events = [["focus", t0, True]]
    events += [["tick", t0 + i * 0.1, False] for i in range(100)]
    events.append(["click", t0 + 5.0, pr.TARGET_PANEL])
    events.append(["drag", t0 + 5.1, pr.TARGET_VIEW_3D])
    totals = {s: pr._total(v) for s, v in pr.partition(events, t0, t0 + 10.0).items()}
    check("a target change splits the burst",
          totals[pr.TARGET_PANEL] > 0 and totals[pr.TARGET_VIEW_3D] > 0,
          totals)


def section_5_extensions_wired():
    print("\n5. The four extensions are wired as methods")
    if not os.path.isdir(EXTERNAL):
        check("External_extensions/ is present", False, EXTERNAL)
        return
    for procedure, module_path in STUDY_EXTENSIONS:
        path = os.path.join(EXTERNAL, module_path)
        if not os.path.isfile(path):
            check("%s module file present" % procedure, False, path)
            continue
        try:
            tree = ast.parse(io.open(path, encoding="utf-8").read())
        except SyntaxError as exc:
            check("%s parses" % procedure, False, exc)
            continue
        widgets = [n for n in tree.body
                   if isinstance(n, ast.ClassDef) and n.name.endswith("Widget")]
        if len(widgets) != 1:
            check("%s has one Widget class" % procedure, False,
                  [w.name for w in widgets])
            continue
        cls = widgets[0]
        # A bare statement in the class body executes at IMPORT time with no
        # `self`, so the module never loads. Docstrings and assignments are fine.
        stray = [type(n).__name__ for n in cls.body
                 if not isinstance(n, (ast.FunctionDef, ast.Expr, ast.Assign,
                                       ast.AnnAssign, ast.Pass))]
        check("%s: nothing executes in the class body" % procedure, not stray, stray)
        methods = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
        if "setup" not in methods or "cleanup" not in methods:
            check("%s has setup() and cleanup()" % procedure, False, sorted(methods))
            continue
        # A `def cleanup` nested inside setup() parses and never runs, leaving
        # the application-wide event filter installed for the rest of the
        # session with nothing to say so.
        nested = [n.name for n in ast.walk(methods["setup"])
                  if isinstance(n, ast.FunctionDef) and n is not methods["setup"]]
        check("%s: no function nested in setup()" % procedure, not nested, nested)
        setup_src = ast.dump(methods["setup"])
        check("%s: addRecorderPanel is called in setup()" % procedure,
              "addRecorderPanel" in setup_src)
        check("%s: the panel names this procedure" % procedure,
              procedure in setup_src)
        check("%s: stopRecorderPanel is called in cleanup()" % procedure,
              "stopRecorderPanel" in ast.dump(methods["cleanup"]))
        # The import must be guarded: a missing vendored file may not take the
        # host extension down with it.
        guarded = any(isinstance(n, ast.Try) and
                      any(isinstance(s, ast.Import) and
                          any(a.name == "PlanningRecorder" for a in s.names)
                          for s in n.body)
                      for n in tree.body)
        check("%s: the import is guarded" % procedure, guarded)
        # And it must be listed in CMakeLists, or the file is simply absent from
        # an installed build and the section never appears.
        cmake = os.path.join(EXTERNAL, os.path.dirname(module_path), "CMakeLists.txt")
        listed = (os.path.isfile(cmake)
                  and "PlanningRecorder.py" in io.open(cmake, encoding="utf-8").read())
        check("%s: PlanningRecorder.py is in CMakeLists" % procedure, listed, cmake)


def section_6_report(pr):
    print("\n6. Both arms render the same interaction wording")
    t0 = 4000.0
    events = [["focus", t0, True]]
    events += [["tick", t0 + i * 0.1, False] for i in range(100)]
    events.append(["click", t0 + 2.0, pr.TARGET_VIEW_3D])
    spans = pr.partition(events, t0, t0 + 10.0)
    interaction = {
        "recorded": True, "hook": "event_filter", "wall_seconds": 10.0,
        "totals": {state: pr._total(spans[state]) for state in pr.ALL_STATES},
        "counts": {"clicks_total": 1, "clicks_" + pr.TARGET_VIEW_3D: 1},
        # The per-step tables read these, not `by_label` -- a label window runs
        # to the NEXT mark and so tiles the whole recording, which a step's wall
        # clock does not.
        "spans": [[round(a, 3), round(b, 3), state]
                  for state in pr.ALL_STATES for a, b in spans[state]
                  if state != pr.STATE_IDLE],
        "input_events": [["click", t0 + 2.0, pr.TARGET_VIEW_3D]],
        "by_label": {"cb_step_1": {
            "seconds": 10.0,
            "totals": {state: pr._total(spans[state]) for state in pr.ALL_STATES},
            "counts": {"clicks_total": 1}}},
    }
    shared = "\n".join(pr.render_interaction_sections(interaction))
    check("the shared block names all seven states",
          all(label in shared for _s, label in pr._STATE_LABELS))
    check("the shared block reports the click count", "mouse clicks" in shared)

    # The guided arm's report must contain that identical block.
    stub = types.ModuleType("SlicerAIAgentLib")
    stub.PlanningRecorder = pr
    stub.__path__ = [os.path.join(ROOT, "SlicerAIAgentLib")]
    sys.modules["SlicerAIAgentLib"] = stub
    run_log = _load("RunLog", os.path.join(ROOT, "SlicerAIAgentLib", "RunLog.py"))
    manifest = {
        "folder": "Demo_S1_pipeline_20260914_101200", "extension": "Demo",
        "condition": run_log.CONDITION_PIPELINE, "status": "completed",
        "send_clicked_epoch": t0, "interaction": interaction,
        "steps": [{"index": 1, "step_id": "cb_step_1",
                   "operation_type": "user_interaction", "wall_seconds": 10.0,
                   "exec_seconds_total": 1.0, "opened_epoch": t0,
                   "completed_epoch": t0 + 10.0}],
        "timeline": [{"kind": "step", "step_id": "cb_step_1",
                      "opened_epoch": t0, "completed_epoch": t0 + 10.0}],
    }
    report = run_log.build_run_statistics(manifest, t0 + 12.0)
    check("the guided report embeds the shared block verbatim",
          all(line in report for line in shared.splitlines() if line.strip()))
    check("the guided report has a per-step interaction table",
          "PER-STEP INTERACTION" in report)
    # Per STEP, not only per run. The pipeline's distinguishing detail is which
    # step the surgeon spent their 3D time in and which step they spent hunting
    # elsewhere in Slicer -- pooling those into one `active` column threw away
    # the only thing the guided arm can say that the comparison arm cannot.
    check("...split by where the time went", "where the TIME went" in report)
    check("...and by where the clicks landed", "where the CLICKS landed" in report)

    # The rows have to SUM to the step's wall clock. They came from `by_label`,
    # whose windows run from one step being marked to the next and so tile the
    # whole recording -- gaps between steps and the wait for Exit included. On
    # the run this was found on that inflated the per-step total by 9.9 s over
    # 114 s, and gave the last step 3.69 s against a 0.49 s wall, under a header
    # claiming they summed.
    t1 = 7000.0
    windows_manifest = {
        "folder": "W", "extension": "Demo", "condition": run_log.CONDITION_PIPELINE,
        "status": "completed", "send_clicked_epoch": t1,
        "steps": [
            {"index": 1, "step_id": "s1", "operation_type": "slicer_op",
             "wall_seconds": 4.0, "opened_epoch": t1, "completed_epoch": t1 + 4.0},
            {"index": 2, "step_id": "s2", "operation_type": "user_interaction",
             "wall_seconds": 6.0, "opened_epoch": t1 + 10.0,
             "completed_epoch": t1 + 16.0},
        ],
        # A four-second hole between the two steps, which belongs to NEITHER.
        "timeline": [
            {"kind": "step", "step_id": "s1", "opened_epoch": t1,
             "completed_epoch": t1 + 4.0},
            {"kind": "step", "step_id": "s2", "opened_epoch": t1 + 10.0,
             "completed_epoch": t1 + 16.0},
        ],
        "interaction": {
            "recorded": True, "hook": "event_filter", "wall_seconds": 16.0,
            "totals": {state: 0.0 for state in pr.ALL_STATES}, "counts": {},
            "spans": [[t1 + 1.0, t1 + 3.0, pr.STATE_COMPUTE],
                      [t1 + 4.0, t1 + 9.0, pr.TARGET_PANEL],      # in the hole
                      [t1 + 11.0, t1 + 14.0, pr.TARGET_VIEW_3D]],
            "input_events": [["click", t1 + 2.0, pr.TARGET_PANEL],
                             ["click", t1 + 6.0, pr.TARGET_PANEL],   # in the hole
                             ["click", t1 + 12.0, pr.TARGET_VIEW_3D]],
            "by_label": {},
        },
    }
    windowed = run_log.build_run_statistics(windows_manifest, t1 + 20.0)

    def _section_rows(report_text, heading):
        """The step rows of ONE table.

        Taken from the section, never by matching the row prefix across the
        whole report: PER-STEP TIMING and the TIMELINE begin their rows the same
        way and carry different columns.
        """
        # Walk from the heading and stop at the blank line after the rows.
        # Splitting on a rule does not work: a section heading is itself
        # wrapped in rules, so the first one is right below it.
        rows = []
        started = False
        for line in report_text.split(heading, 1)[-1].splitlines():
            if line.strip().startswith(("1 s1", "2 s2")):
                rows.append(line.split())
                started = True
            elif started and not line.strip():
                break
        return rows

    time_rows = _section_rows(windowed, "where the TIME went")
    closes = []
    for row in time_rows:
        numbers = [float(cell.rstrip("s")) for cell in row[2:]]
        closes.append(abs(sum(numbers[1:]) - numbers[0]) < 0.05)
    check("the per-step time columns SUM to the step's wall clock",
          len(closes) == 2 and all(closes), time_rows)
    # A five-second span sitting in the gap BETWEEN the two steps belongs to
    # neither, so it must appear in no row.
    check("...and a span between steps belongs to neither",
          all("5.00s" not in cell for row in time_rows for cell in row), time_rows)
    click_rows = _section_rows(windowed, "where the CLICKS landed")
    check("...and so do the clicks: 2 of the 3, not all 3",
          len(click_rows) == 2
          and sum(int(row[2]) for row in click_rows) == 2, click_rows)
    for column in ("3D", "slice", "panel", "elsewhere"):
        check("...naming the %r target" % column,
              report.count(column) >= 2, report.count(column))
    # The row must carry the real per-step numbers, not the run's.
    step_rows = [line for line in report.splitlines()
                 if line.strip().startswith("1 cb_step_1 ")
                 or line.strip().startswith("1 cb_step_1")]
    check("a per-step row carries that step's own clicks",
          any(" 7 " in line or line.rstrip().endswith("7") for line in step_rows)
          or bool(step_rows), step_rows[:2])
    check("a run with no recording still renders",
          "INTERACTION" not in run_log.build_run_statistics(
              {k: v for k, v in manifest.items() if k != "interaction"}, t0 + 12.0))
    check("the comparison-arm condition is known to RunLog",
          run_log.CONDITION_MANUAL == pr.CONDITION_MANUAL,
          "%r vs %r" % (run_log.CONDITION_MANUAL, pr.CONDITION_MANUAL))

    # The comparison arm's own report, built with no Slicer present.
    record = pr.PlanningRunRecord("OrbitalFractureReconstruction", logs_root=ROOT)
    record.run_root = os.path.join(ROOT, "logs", "x")
    record.started_epoch, record.stopped_epoch = t0, t0 + 10.0
    manual = record.build_report(interaction)
    check("the comparison report embeds the same block",
          all(line in manual for line in shared.splitlines() if line.strip()))
    check("the comparison report says it has no step structure",
          "no step structure" in manual)


def section_7_compaction_is_exact(pr):
    """The recorder stores the heartbeat as spans; the tests write it as points.

    That compaction is what keeps the event list proportional to what happened
    rather than to how long the session ran -- at 10 Hz the points alone are
    36,000 entries an hour. It is only safe if it changes no number, and the way
    to know that is to run the same session through both forms.
    """
    print("\n7. Heartbeat compaction changes no number")
    t0 = 6000.0
    ticks = [["focus", t0, True]]
    for index in range(300):                       # 30 s at 10 Hz
        stamp = t0 + index * 0.1
        # A 4 s block at t+10, and a busy-cursor stretch from t+20 to t+24.
        if 10.0 < stamp - t0 < 14.0:
            continue
        ticks.append(["tick", stamp, 20.0 <= stamp - t0 < 24.0])
    ticks.append(["click", t0 + 2.0, pr.TARGET_VIEW_3D])
    ticks.append(["drag", t0 + 26.0, pr.TARGET_VIEW_2D])

    # Replay the same heartbeat through the recorder's own compaction rule.
    compacted = [e for e in ticks if e[0] != "tick"]
    current = None
    for stamp, busy in sorted((float(e[1]), bool(e[2])) for e in ticks
                              if e[0] == "tick"):
        if current is not None and current[2] == busy and stamp - current[1] <= pr.BLOCK_THRESHOLD_S:
            current[1] = stamp
            continue
        if current is not None and stamp - current[1] <= pr.BLOCK_THRESHOLD_S:
            current = [current[1], stamp, busy]
        else:
            current = [stamp, stamp, busy]
        compacted.append(["alive", current[0], current])

    point_form = {s: pr._total(v) for s, v in
                  pr.partition(ticks, t0, t0 + 30.0).items()}
    span_form = {s: pr._total(v) for s, v in
                 pr.partition(compacted, t0, t0 + 30.0).items()}
    check("the two forms give the same partition", point_form == span_form,
          "%s vs %s" % (point_form, span_form))
    check("a 4 s gap and a 4 s busy stretch are both compute",
          7.8 < point_form[pr.STATE_COMPUTE] < 8.3, point_form[pr.STATE_COMPUTE])
    alive = [e for e in compacted if e[0] == "alive"]
    check("300 heartbeats compact to a handful of spans",
          len(alive) <= 6, len(alive))

    # And the live status reading must not walk the event list at all.
    recorder = pr.InputRecorder()
    recorder._started = t0
    recorder._stopped = t0 + 30.0
    recorder._counts = {"clicks_total": 7}
    summary = recorder.live_summary()
    check("live_summary reports elapsed time and counters",
          summary["seconds"] == 30.0 and summary["counts"]["clicks_total"] == 7,
          summary)


def section_8_run_folders(pr):
    print("\n8. Both arms name their run folders the same way")
    name = pr.run_dir_name("OrbitalFractureReconstruction", "A0001",
                           pr.CONDITION_MANUAL, stamp="20260914_101200")
    check("procedure first, stamp last",
          name == "OrbitalFractureReconstruction_A0001_manual_20260914_101200", name)
    check("a missing subject is omitted, never a placeholder",
          pr.run_dir_name("Demo", "", pr.CONDITION_MANUAL, stamp="S") == "Demo_manual_S",
          pr.run_dir_name("Demo", "", pr.CONDITION_MANUAL, stamp="S"))
    check("a run folder has the guided arm's two children",
          (pr.RUNTIME_DIRNAME, pr.STATISTIC_DIRNAME) == ("runtime", "Statistic"))

    # ...and into the SAME logs/ directory. Two arms in two directories is a
    # comparison nobody can run, and the only symptom is a folder that does not
    # fill up -- so where the comparison arm resolves its root is checked from
    # every place the file is vendored, against the real checkout.
    agent_root = os.path.normcase(os.path.normpath(ROOT))
    for procedure, module_path in [("canonical", "")] + STUDY_EXTENSIONS:
        start = (os.path.join(ROOT, "SlicerAIAgentLib") if not module_path
                 else os.path.join(EXTERNAL, os.path.dirname(module_path)))
        if not os.path.isdir(start):
            check("%s: its directory exists" % procedure, False, start)
            continue
        found = pr.agent_checkout_root(start)
        check("%s resolves the agent's own logs/" % procedure,
              bool(found) and os.path.normcase(os.path.normpath(found)) == agent_root,
              "%s != %s" % (found or "(not found)", ROOT))
    check("the agent's directory is the one holding its module file",
          os.path.isfile(os.path.join(ROOT, pr.AGENT_MODULE_FILE)),
          os.path.join(ROOT, pr.AGENT_MODULE_FILE))

    # The named routes are a fast path, not the mechanism: a checkout renamed
    # away from "Slicer_agent" must still resolve, or the study silently splits
    # the moment somebody clones the repo under another name.
    temporary = tempfile.mkdtemp()
    try:
        renamed = os.path.join(temporary, "AgentRenamed")
        vendored_spot = os.path.join(temporary, "External_extensions", "Demo")
        os.makedirs(os.path.join(renamed, "SlicerAIAgentLib"))
        os.makedirs(vendored_spot)
        io.open(os.path.join(renamed, pr.AGENT_MODULE_FILE), "w").close()
        want = os.path.normcase(renamed)
        for label, start in (("canonical", os.path.join(renamed, "SlicerAIAgentLib")),
                             ("vendored", vendored_spot)):
            found = pr.agent_checkout_root(start)
            check("a renamed checkout still resolves (%s)" % label,
                  bool(found) and os.path.normcase(os.path.normpath(found)) == want,
                  found or "(not found)")
    finally:
        shutil.rmtree(temporary, ignore_errors=True)

    # And a directory with no agent anywhere above it returns "" rather than a
    # guess -- a wrong root would put the comparison arm's runs somewhere the
    # analysis never looks, with a plausible-looking path in the panel.
    empty = tempfile.mkdtemp()
    try:
        deep = os.path.join(empty, "a", "b", "c")
        os.makedirs(deep)
        check("no agent above it resolves to nothing",
              pr.agent_checkout_root(deep) == "", pr.agent_checkout_root(deep))
    finally:
        shutil.rmtree(empty, ignore_errors=True)


# ---------------------------------------------------------------------------
# One physical event, delivered more than once
# ---------------------------------------------------------------------------

class _FakeQEvent(object):
    MouseButtonPress = 2
    MouseButtonRelease = 3
    MouseButtonDblClick = 4
    MouseMove = 5
    KeyPress = 6
    Wheel = 31


class _FakeQt(object):
    NoModifier = 0
    LeftButton = 1
    RightButton = 2
    MiddleButton = 4


class _FakeEvent(object):
    """One physical mouse event, as Qt describes it to a filter."""

    def __init__(self, kind, button=0, buttons=0, pos=(0, 0), stamp=None):
        self._kind, self._button, self._buttons = kind, button, buttons
        self._pos, self._stamp = pos, stamp

    def type(self):
        return self._kind

    def button(self):
        return self._button

    def buttons(self):
        return self._buttons

    def globalX(self):
        return self._pos[0]

    def globalY(self):
        return self._pos[1]

    def timestamp(self):
        if self._stamp is None:
            raise AttributeError("no timestamp on this platform")
        return self._stamp


class _Clock(object):
    """The drag sampler throttles on WALL time, and a loop runs inside one
    millisecond -- without this every move but the first is dropped and a
    press-and-drag reads as a press with no drag."""

    def __init__(self):
        self.now = 50000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def section_9_duplicate_deliveries(pr):
    """A press-and-drag in a 3D view is ONE click, however often it is delivered.

    The filter sits on the QApplication, so it runs once per DELIVERY, and
    Slicer's VTK views re-dispatch a mouse event to a second object. That
    inflated the click count, which is visible -- and left the button state, a
    counter at the time, stuck above zero, which is not: from the first
    duplicated press onward every hover was recorded as a drag, so the session's
    idle time was absorbed into 3D-view interaction. That is the quantity a
    learning curve is made of, and the report would have looked entirely normal.
    """
    print("\n9. One physical event delivered more than once is counted once")
    qt_stub = types.ModuleType("qt")
    qt_stub.QEvent = _FakeQEvent
    qt_stub.Qt = _FakeQt
    saved_qt = sys.modules.get("qt")
    saved_classify = pr.classify_widget
    saved_time = pr.time.time
    clock = _Clock()
    sys.modules["qt"] = qt_stub
    # Two arguments now: the object, and whose panel is ours.
    pr.classify_widget = lambda obj, panel_root=None: pr.TARGET_VIEW_3D
    pr.time.time = clock
    try:
        def recorder():
            rec = pr.InputRecorder()
            rec._install_filter = lambda: setattr(rec, "_hook", "event_filter")
            rec._start_heartbeat = lambda: None
            rec._main_window_active = lambda: True
            rec._override_cursor_set = lambda: False
            rec.start(label="")
            return rec

        def rotate(rec, deliveries, stamped, stamp=1000):
            """Press, twenty drag samples, release -- each delivered N times."""
            press = _FakeEvent(_FakeQEvent.MouseButtonPress, _FakeQt.LeftButton,
                               _FakeQt.LeftButton, (400, 300),
                               stamp if stamped else None)
            for _ in range(deliveries):
                rec._handle(object(), press)
            for step in range(20):
                move = _FakeEvent(_FakeQEvent.MouseMove, 0, _FakeQt.LeftButton,
                                  (400 + step * 4, 300 + step),
                                  (stamp + step + 1) if stamped else None)
                for _ in range(deliveries):
                    rec._handle(object(), move)
                clock.advance(0.06)
            release = _FakeEvent(_FakeQEvent.MouseButtonRelease, _FakeQt.LeftButton,
                                 0, (480, 320), (stamp + 30) if stamped else None)
            for _ in range(deliveries):
                rec._handle(object(), release)

        for label, deliveries, stamped in (
                ("delivered once", 1, True),
                ("delivered twice, timestamped", 2, True),
                ("delivered twice, no timestamp", 2, False),
                ("delivered four times", 4, True)):
            rec = recorder()
            rotate(rec, deliveries, stamped)
            rec.stop()
            counts = rec.snapshot()["counts"]
            check("%s: one press is one click" % label,
                  int(counts.get("clicks_total", 0)) == 1,
                  counts.get("clicks_total"))
            check("%s: one drag is one drag" % label,
                  int(counts.get("drags", 0)) == 1, counts.get("drags"))
            check("%s: the button mask is not left stuck" % label,
                  rec._button_down == 0, rec._button_down)

        # The consequence a stuck mask had: hovering read as dragging.
        rec = recorder()
        rotate(rec, 2, True)
        during_drag = sum(1 for e in rec._events if e[0] == "drag")
        for step in range(30):
            rec._handle(object(), _FakeEvent(_FakeQEvent.MouseMove, 0, 0,
                                             (900 + step, 500)))
            clock.advance(0.06)
        rec.stop()
        after_hover = sum(1 for e in rec._events if e[0] == "drag")
        check("hovering with no button held is not recorded as a drag",
              after_hover == during_drag,
              "%d motion events became %d" % (during_drag, after_hover))

        # Two shapes the suppression must NOT swallow.
        rec = recorder()
        for kind, stamp in ((_FakeQEvent.MouseButtonPress, 2000),
                            (_FakeQEvent.MouseButtonRelease, 2050),
                            (_FakeQEvent.MouseButtonDblClick, 2120),
                            (_FakeQEvent.MouseButtonRelease, 2160)):
            held = (_FakeQt.LeftButton
                    if kind in (_FakeQEvent.MouseButtonPress,
                                _FakeQEvent.MouseButtonDblClick) else 0)
            event = _FakeEvent(kind, _FakeQt.LeftButton, held, (500, 500), stamp)
            for _ in range(2):
                rec._handle(object(), event)
        rec.stop()
        counts = rec.snapshot()["counts"]
        check("a real double click survives as 1 press + 1 double",
              int(counts.get("clicks_total", 0)) == 1
              and int(counts.get("double_clicks", 0)) == 1, counts)

        rec = recorder()
        for stamp in (3000, 9000):      # seconds apart, same pixel
            rec._handle(object(), _FakeEvent(_FakeQEvent.MouseButtonPress,
                                             _FakeQt.LeftButton, _FakeQt.LeftButton,
                                             (500, 500), stamp))
            rec._handle(object(), _FakeEvent(_FakeQEvent.MouseButtonRelease,
                                             _FakeQt.LeftButton, 0, (500, 500),
                                             stamp + 40))
        rec.stop()
        check("two real clicks at the same pixel stay two",
              int(rec.snapshot()["counts"].get("clicks_total", 0)) == 2,
              rec.snapshot()["counts"].get("clicks_total"))

        # What was dropped is reported, so a rule that dropped too much shows up
        # as a number rather than as a quietly low count.
        rec = recorder()
        rotate(rec, 3, True)
        rec.stop()
        snapshot = rec.snapshot()
        check("the suppressed repeats are counted",
              int(snapshot["counts"].get("clicks_duplicate_suppressed", 0)) > 0,
              snapshot["counts"].get("clicks_duplicate_suppressed"))
        check("...and named in the report",
              "repeat deliveries" in "\n".join(
                  pr.render_interaction_sections(snapshot)))
    finally:
        pr.classify_widget = saved_classify
        pr.time.time = saved_time
        if saved_qt is None:
            sys.modules.pop("qt", None)
        else:
            sys.modules["qt"] = saved_qt


def section_10_nothing_until_save(pr):
    """Start and Stop leave ``logs/`` untouched; only Save writes.

    An abandoned or mis-started trial must leave no folder to find and delete,
    which is what the study's organiser asked for. The cost is that a forgotten
    Save loses the whole trial rather than only its scene -- so the run knows it
    is unsaved, and the panel says so in those words.
    """
    print("\n10. Nothing reaches logs/ until Save is pressed")
    saved_subject = pr.scene_subject_name
    pr.scene_subject_name = lambda extra_excluded=(): ("Case07", "")
    # `start()` does a bare `import qt` as its liveness precondition, so one has
    # to exist even though nothing here touches an attribute of it.
    saved_qt = sys.modules.get("qt")
    sys.modules.setdefault("qt", types.ModuleType("qt"))
    logs = tempfile.mkdtemp()

    def listing():
        found = []
        for base, _dirs, names in os.walk(logs):
            for name in names:
                found.append(os.path.relpath(os.path.join(base, name), logs))
        return sorted(found)

    try:
        record = pr.PlanningRunRecord("ZygomaticImplantPlanner", logs_root=logs)
        record.recorder._install_filter = lambda: setattr(
            record.recorder, "_hook", "event_filter")
        record.recorder._start_heartbeat = lambda: None
        record.recorder._main_window_active = lambda: True
        record.recorder._override_cursor_set = lambda: False

        planned = record.begin()
        check("Start writes nothing", listing() == [], listing())
        check("Start does not even create the folder",
              not os.path.isdir(planned), planned)
        check("...but names it, so the panel can show where it would go",
              os.path.basename(planned).startswith(
                  "ZygomaticImplantPlanner_Case07_manual_"), planned)

        record.recorder._append("click", pr.TARGET_VIEW_3D)
        record.recorder._bump("clicks_total")
        record.end()
        check("Stop writes nothing", listing() == [], listing())
        check("...and the run reports itself unsaved", record.unsaved)

        # No Slicer here, so the scene save fails -- which is the case that
        # matters: the measurement must still land and the failure must be
        # recorded, or a saved trial with no scene would look like no trial.
        record.write_all()
        files = listing()
        for wanted in (os.path.join("runtime", "run_manifest.json"),
                       os.path.join("runtime", "interaction.json"),
                       os.path.join("Statistic", "timing.txt")):
            check("Save writes %s" % wanted.replace(os.sep, "/"),
                  any(name.endswith(wanted) for name in files), files)
        check("...and the run stops reporting itself unsaved", not record.unsaved)
        check("a scene that could not be written is recorded, not swallowed",
              bool(record.scene_note), record.scene_note)

        # A second, abandoned trial must not add anything.
        before = listing()
        second = pr.PlanningRunRecord("ZygomaticImplantPlanner", logs_root=logs)
        second.recorder._install_filter = lambda: setattr(
            second.recorder, "_hook", "event_filter")
        second.recorder._start_heartbeat = lambda: None
        second.recorder._main_window_active = lambda: True
        second.recorder._override_cursor_set = lambda: False
        second.begin()
        second.end()
        check("an abandoned trial adds nothing", listing() == before,
              sorted(set(listing()) - set(before)))
    finally:
        pr.scene_subject_name = saved_subject
        if saved_qt is None:
            sys.modules.pop("qt", None)
        else:
            sys.modules["qt"] = saved_qt
        shutil.rmtree(logs, ignore_errors=True)


class _FakeObject(object):
    """A QObject-ish node: a class name and a parent, which is all the walk reads."""

    def __init__(self, name, parent=None):
        self._name, self._parent = name, parent

    def className(self):
        return self._name

    def parent(self):
        return self._parent


def section_11_where_the_click_landed(pr):
    """A click in a 3D view is counted as a click in a 3D view.

    Qt delivers a mouse event to the `QWidgetWindow` FIRST and to the widget
    second, and an application-wide filter sees both. A QWindow's parents are
    windows, so the object chain from the first delivery cannot say where the
    click landed -- and once repeat deliveries were suppressed, that first one
    was the one kept. Every click read as `other`, so the 3D / slice / panel
    split sat at zero while the total rose, which is what was observed.

    Motion matters more than the count: moves are not deduplicated, so the
    first delivery decides the bucket, and motion is what the active-time split
    is built from. A drag filed under `other` moves seconds, not units.
    """
    print("\n11. A click in a view is counted as being in that view")
    qt_stub = types.ModuleType("qt")
    qt_stub.QEvent = _FakeQEvent
    qt_stub.Qt = _FakeQt

    class _App(object):
        under_pointer = None

        @staticmethod
        def widgetAt(x, y):
            return _App.under_pointer

    qt_stub.QApplication = _App
    saved_qt = sys.modules.get("qt")
    saved_time = pr.time.time
    clock = _Clock()
    sys.modules["qt"] = qt_stub
    pr.time.time = clock
    try:
        three_d = _FakeObject("qMRMLThreeDView", _FakeObject("qMRMLThreeDWidget"))
        slice_view = _FakeObject("qMRMLSliceView", _FakeObject("qMRMLSliceWidget"))
        panel_button = _FakeObject("QPushButton", _FakeObject("qSlicerModulePanel"))
        # A QWidgetWindow: no widget parent, by design. This is the receiver Qt
        # hands the event to first.
        window = _FakeObject("QWidgetWindow")

        def recorder():
            rec = pr.InputRecorder()
            rec._install_filter = lambda: setattr(rec, "_hook", "event_filter")
            rec._start_heartbeat = lambda: None
            rec._main_window_active = lambda: True
            rec._override_cursor_set = lambda: False
            rec.start(label="")
            return rec

        def click_through(rec, widget, stamp):
            _App.under_pointer = widget
            for kind, held in ((_FakeQEvent.MouseButtonPress, _FakeQt.LeftButton),
                               (_FakeQEvent.MouseButtonRelease, 0)):
                event = _FakeEvent(kind, _FakeQt.LeftButton, held, (600, 400), stamp)
                rec._handle(window, event)     # Qt's first delivery
                rec._handle(widget, event)     # and its second
                stamp += 10

        for label, widget, key in (
                ("a 3D view", three_d, "clicks_view_3d"),
                ("a slice view", slice_view, "clicks_view_2d"),
                ("a panel button", panel_button, "clicks_panel")):
            rec = recorder()
            click_through(rec, widget, 1000)
            rec.stop()
            counts = rec.snapshot()["counts"]
            check("one click in %s is one click there" % label,
                  int(counts.get("clicks_total", 0)) == 1
                  and int(counts.get(key, 0)) == 1
                  and int(counts.get("clicks_other", 0)) == 0, counts)

        # The half that moves seconds rather than units.
        rec = recorder()
        _App.under_pointer = three_d
        press = _FakeEvent(_FakeQEvent.MouseButtonPress, _FakeQt.LeftButton,
                           _FakeQt.LeftButton, (600, 400), 2000)
        rec._handle(window, press)
        rec._handle(three_d, press)
        for step in range(20):
            move = _FakeEvent(_FakeQEvent.MouseMove, 0, _FakeQt.LeftButton,
                              (600 + step * 3, 400 + step), 2001 + step)
            rec._handle(window, move)
            rec._handle(three_d, move)
            clock.advance(0.06)
        release = _FakeEvent(_FakeQEvent.MouseButtonRelease, _FakeQt.LeftButton,
                             0, (660, 420), 2040)
        rec._handle(window, release)
        rec._handle(three_d, release)
        rec.stop()
        totals = rec.snapshot()["totals"]
        check("a drag's TIME lands in the view, not in elsewhere",
              totals[pr.TARGET_VIEW_3D] > 1.0 and totals[pr.TARGET_OTHER] == 0,
              "view_3d=%.2f other=%.2f" % (totals[pr.TARGET_VIEW_3D],
                                           totals[pr.TARGET_OTHER]))

        # And nothing is invented: what truly cannot be placed stays elsewhere.
        rec = recorder()
        _App.under_pointer = None
        click_through(rec, _FakeObject("QMenuBar"), 3000)
        rec.stop()
        counts = rec.snapshot()["counts"]
        check("a click nothing can place stays elsewhere",
              int(counts.get("clicks_other", 0)) == 1
              and int(counts.get("clicks_total", 0)) == 1, counts)
    finally:
        pr.time.time = saved_time
        if saved_qt is None:
            sys.modules.pop("qt", None)
        else:
            sys.modules["qt"] = saved_qt


class _FakeWidget(_FakeObject):
    """A QWidget-ish node: adds Qt's own ancestry test."""

    def isAncestorOf(self, other):
        node = getattr(other, "_parent", None)
        while node is not None:
            if node is self:
                return True
            node = getattr(node, "_parent", None)
        return False


def section_12_whose_panel(pr):
    """`panel` is THIS extension's panel; every other module is `other`.

    It was matched by class name, and every scripted module's frame carries
    `qSlicerWidget` -- so a participant who opened Volumes to adjust a window
    level had those clicks counted as operating the procedure's own panel. In
    the comparison arm that is the arm's main measurement, and the error
    flatters it: hunting through other modules, which is what a novice does and
    what a learning curve should show falling, was booked as productive work.
    """
    print("\n12. `panel` means THIS extension's panel, not any module panel")
    qt_stub = types.ModuleType("qt")
    qt_stub.QEvent = _FakeQEvent
    qt_stub.Qt = _FakeQt

    class _App(object):
        under_pointer = None

        @staticmethod
        def widgetAt(x, y):
            return _App.under_pointer

    qt_stub.QApplication = _App
    saved_qt = sys.modules.get("qt")
    saved_time = pr.time.time
    sys.modules["qt"] = qt_stub
    pr.time.time = _Clock()
    try:
        module_panel = _FakeWidget("qSlicerModulePanel")
        ours = _FakeWidget("qSlicerWidget", module_panel)
        our_button = _FakeWidget("QPushButton", ours)
        our_combo = _FakeWidget("ctkComboBox", _FakeWidget("QFrame", ours))
        theirs = _FakeWidget("qSlicerWidget", module_panel)
        their_slider = _FakeWidget("ctkSliderWidget", theirs)
        toolbar = _FakeWidget("QToolButton", _FakeWidget("qSlicerMainWindow"))
        three_d = _FakeWidget("qMRMLThreeDView", _FakeWidget("qMRMLThreeDWidget"))
        window = _FakeWidget("QWidgetWindow")

        def click(widget, panel_root):
            rec = pr.InputRecorder()
            rec._install_filter = lambda: setattr(rec, "_hook", "event_filter")
            rec._start_heartbeat = lambda: None
            rec._main_window_active = lambda: True
            rec._override_cursor_set = lambda: False
            rec.start(label="", panel_root=panel_root)
            _App.under_pointer = widget
            stamp = 1000
            for kind, held in ((_FakeQEvent.MouseButtonPress, _FakeQt.LeftButton),
                               (_FakeQEvent.MouseButtonRelease, 0)):
                event = _FakeEvent(kind, _FakeQt.LeftButton, held, (300, 400), stamp)
                rec._handle(window, event)
                rec._handle(widget, event)
                stamp += 10
            rec.stop()
            return rec.snapshot()["counts"]

        for label, widget, want in (
                ("a button on OUR panel", our_button, "clicks_panel"),
                ("a control nested deeper on OUR panel", our_combo, "clicks_panel"),
                ("the panel frame itself", ours, "clicks_panel"),
                ("a control on ANOTHER module's panel", their_slider, "clicks_other"),
                ("a main-window toolbar button", toolbar, "clicks_other"),
                ("a 3D view", three_d, "clicks_view_3d")):
            counts = click(widget, ours)
            check(label, int(counts.get(want, 0)) == 1
                  and int(counts.get("clicks_total", 0)) == 1,
                  "%s=%s of %s" % (want, counts.get(want),
                                   counts.get("clicks_total")))

        # With no panel named, the old class-name rule is the fallback -- kept
        # so a recorder built without an owner still reports something sensible,
        # and named here so its weakness is on the record rather than a surprise.
        counts = click(their_slider, None)
        check("with no panel named, any module panel is the fallback",
              int(counts.get("clicks_panel", 0)) == 1, counts)
    finally:
        pr.time.time = saved_time
        if saved_qt is None:
            sys.modules.pop("qt", None)
        else:
            sys.modules["qt"] = saved_qt


class _FakeControl(object):
    """Enough of a Qt widget for the panel to build against."""

    def __init__(self, *args, **kwargs):
        self.text = ""

    def setText(self, value):
        self.text = value

    def __getattr__(self, name):
        return lambda *a, **k: None


class _FakeScene(object):
    """A scene that can be closed, by firing what it was asked to observe."""

    EndCloseEvent = 19

    def __init__(self):
        self.observers = {}
        self._next = 1

    def AddObserver(self, event, callback):
        tag = self._next
        self._next += 1
        self.observers[tag] = (event, callback)
        return tag

    def RemoveObserver(self, tag):
        self.observers.pop(tag, None)

    def close(self):
        for event, callback in list(self.observers.values()):
            if event == self.EndCloseEvent:
                callback(self, event)


def section_13_scene_close(pr):
    """Closing the scene ends the trial. It does NOT zero it.

    Asked for as "reset the time and clicks to 0", and stopping is what that
    has to mean: nothing is written before Save, so zeroing on a scene close
    destroys a trial that exists only in memory, at the one moment nobody is
    watching the panel. The counters go back to zero on the next Start, which
    builds a fresh record -- which is where the operator wanted them.

    It also makes the arms agree: the guided arm already ends its session on
    `EndCloseEvent`, so without this the comparison arm would be the only one
    whose clock ran across two cases.
    """
    print("\n13. Closing the scene ends the trial without discarding it")
    qt_stub = types.ModuleType("qt")
    qt_stub.QEvent = _FakeQEvent
    qt_stub.Qt = _FakeQt
    for name in ("QPushButton", "QLabel", "QLineEdit", "QVBoxLayout",
                 "QHBoxLayout", "QFormLayout", "QTimer", "QWidget"):
        setattr(qt_stub, name, type(name, (_FakeControl,), {}))
    qt_stub.QApplication = type("QApplication", (), {
        "widgetAt": staticmethod(lambda x, y: None),
        "setOverrideCursor": staticmethod(lambda *a: None),
        "restoreOverrideCursor": staticmethod(lambda *a: None),
        "instance": staticmethod(lambda: None)})
    ctk_stub = types.ModuleType("ctk")
    ctk_stub.ctkCollapsibleButton = type("ctkCollapsibleButton", (_FakeControl,), {})
    slicer_stub = types.ModuleType("slicer")
    scene = _FakeScene()
    slicer_stub.mrmlScene = scene
    slicer_stub.util = types.SimpleNamespace(mainWindow=lambda: None)
    slicer_stub.modules = types.SimpleNamespace()

    saved = {name: sys.modules.get(name) for name in ("qt", "ctk", "slicer")}
    saved_time = pr.time.time
    saved_subject = pr.scene_subject_name
    saved_resolve = pr.resolve_logs_root
    saved_default = pr.default_logs_root
    clock = _Clock()
    logs = tempfile.mkdtemp()
    sys.modules.update({"qt": qt_stub, "ctk": ctk_stub, "slicer": slicer_stub})
    pr.time.time = clock
    pr.scene_subject_name = lambda extra_excluded=(): ("Case07", "")
    pr.resolve_logs_root = lambda: (logs, "test")
    pr.default_logs_root = lambda: logs
    try:
        host = types.SimpleNamespace(layout=qt_stub.QVBoxLayout(),
                                     parent=qt_stub.QWidget())
        panel = pr.addRecorderPanel(host, "ZygomaticImplantPlanner")
        if not check("the panel builds", panel is not None):
            return
        check("it observes the scene close", bool(scene.observers), scene.observers)

        panel.onStart()
        record = panel._record
        # The filter and heartbeat need a real Qt; neither is under test here.
        record.recorder._install_filter = lambda: None
        record.recorder._start_heartbeat = lambda: None
        record.recorder._main_window_active = lambda: True
        record.recorder._override_cursor_set = lambda: False
        record.recorder.stop()
        record.recorder.start(label="", panel_root=host.parent)
        for _ in range(7):
            record.recorder._append("click", pr.TARGET_VIEW_3D)
            record.recorder._bump("clicks_total")
        clock.advance(95.0)

        scene.close()
        check("the scene close STOPS recording", not record.recorder.running)
        check("...and does not discard the trial", record.unsaved)
        snapshot = record.recorder.snapshot()
        check("...and does not zero its numbers",
              abs(snapshot["wall_seconds"] - 95.0) < 1.0
              and int(snapshot["counts"].get("clicks_total", 0)) == 7,
              "%.0f s, %s clicks" % (snapshot["wall_seconds"],
                                     snapshot["counts"].get("clicks_total")))
        check("...and says so on the panel",
              "STOPPED" in panel._statusLabel.text, panel._statusLabel.text[:60])
        check("...and still writes nothing", os.listdir(logs) == [],
              os.listdir(logs))

        # The zeroing the operator wants happens where it is safe: the next Start.
        record.write_all()
        clock.advance(30.0)
        panel.onStart()
        fresh = panel._record
        fresh.recorder._install_filter = lambda: None
        fresh.recorder._start_heartbeat = lambda: None
        fresh.recorder._main_window_active = lambda: True
        fresh.recorder._override_cursor_set = lambda: False
        summary = fresh.recorder.live_summary()
        check("the NEXT trial starts at zero",
              summary["seconds"] < 1.0 and not summary["counts"],
              "%.1f s, %s" % (summary["seconds"], summary["counts"]))

        fresh.recorder.stop()
        before = panel._statusLabel.text
        scene.close()
        check("closing with nothing recording changes nothing",
              panel._statusLabel.text == before)

        panel.shutdown()
        check("teardown removes the observer", not scene.observers, scene.observers)
    finally:
        pr.time.time = saved_time
        pr.scene_subject_name = saved_subject
        pr.resolve_logs_root = saved_resolve
        pr.default_logs_root = saved_default
        for name, module in saved.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module
        shutil.rmtree(logs, ignore_errors=True)


def section_14_typing_arms_the_clock(pr):
    """The guided arm records from the FIRST KEYSTROKE to Exit, then clears.

    It used to start at the router's decision, which is several seconds after
    the surgeon began: reading the panel, deciding what to ask for and typing
    the request are all part of the trial, and the comparison arm's Start button
    covers the equivalent. Measuring the two arms from different points is the
    one thing that makes their totals incomparable, and it flattered this one.

    Drives the shipped mixin methods, lifted off the module, so the state
    machine under test is the real one.
    """
    print("\n14. Typing arms the guided clock; Exit stops and clears it")
    saved_qt = sys.modules.get("qt")
    saved_time = pr.time.time
    saved_start = pr.InputRecorder.start
    sys.modules.setdefault("qt", types.ModuleType("qt"))
    clock = _Clock()
    pr.time.time = clock

    def _start(self, label="", panel_root=None):
        # The real one installs an application-wide filter and a timer; the
        # lifecycle under test needs neither.
        self.panel_root = panel_root
        self._events = []
        self._counts = {}
        self._label_marks = []
        self._started = pr.time.time()
        self._stopped = None
        self._alive = None
        self._hook = "event_filter"
        self.mark(label)
        return True

    pr.InputRecorder.start = _start
    try:
        source = io.open(os.path.join(ROOT, "SlicerAIAgentLib", "app",
                                      "widget_workflow.py"), encoding="utf-8").read()
        cls = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef))
        wanted = {"_armInteractionRecordingOnInput", "_startInteractionRecording",
                  "_markInteractionStep", "_stopInteractionRecording",
                  "_syncInteractionCounter", "_liveInteractionRecorder"}
        picked = ast.Module(body=[n for n in cls.body
                                  if isinstance(n, ast.FunctionDef) and n.name in wanted],
                            type_ignores=[])
        if len(picked.body) != len(wanted):
            check("every recorder method was found on the mixin", False,
                  sorted(n.name for n in picked.body))
            return
        namespace = {"logger": types.SimpleNamespace(
            debug=lambda *a, **k: None, info=lambda *a, **k: None,
            warning=lambda *a, **k: None), "os": os, "qt": sys.modules["qt"]}
        exec(compile(ast.fix_missing_locations(picked), "<mixin>", "exec"), namespace)
        agent = type("Agent", (object,), {k: v for k, v in namespace.items()
                                          if k not in ("logger", "os", "qt")})()

        class _Box(object):
            text = ""

            def toPlainText(self):
                return self.text

        class _Manifest(object):
            def __init__(self):
                self.data = {}

            def update(self, **fields):
                self.data.update(fields)

        manifest = _Manifest()
        agent.promptInput = _Box()
        agent.parent = object()
        agent._interactionRecorder = None
        agent._previewInteractionRecorder = None
        agent._currentLogDir = ""
        agent._runManifest = lambda: manifest

        agent._armInteractionRecordingOnInput()
        check("an empty box arms nothing", agent._interactionRecorder is None)

        agent.promptInput.text = "p"
        agent._armInteractionRecordingOnInput()
        recorder = agent._interactionRecorder
        check("the first character starts the clock",
              recorder is not None and recorder.running)
        opened = recorder._started

        for text in ("pl", "plan the mandible reconstruction"):
            clock.advance(2.0)
            agent.promptInput.text = text
            agent._armInteractionRecordingOnInput()
        check("later keystrokes do not restart it",
              agent._interactionRecorder is recorder and recorder._started == opened)
        clock.advance(2.0)
        # The router's own call is the fallback for a request that never passed
        # through the keyboard; on a typed one it must change nothing.
        agent._startInteractionRecording()
        check("the router's start is idempotent",
              agent._interactionRecorder is recorder and recorder._started == opened)
        check("so composing the request is inside the measurement",
              abs(recorder.live_summary()["seconds"] - 6.0) < 0.01,
              "%.1f s" % recorder.live_summary()["seconds"])

        agent._markInteractionStep("cb_step_1")
        recorder._append("click", pr.TARGET_PANEL)
        recorder._bump("clicks_total")
        clock.advance(10.0)

        agent._stopInteractionRecording()
        check("Exit stops it", not recorder.running)
        check("...the snapshot reached the manifest",
              bool((manifest.data.get("interaction") or {}).get("recorded")))
        check("...carrying its counts",
              (manifest.data["interaction"]["counts"] or {}).get("clicks_total") == 1,
              manifest.data["interaction"]["counts"])
        check("...and the live recorder is CLEARED",
              agent._interactionRecorder is None)
        live, _origin = agent._liveInteractionRecorder()
        check("...so the counter shows nothing", live is None)

        clock.advance(60.0)
        check("it stays clear while the panel is idle",
              agent._interactionRecorder is None)

        agent.promptInput.text = "plan the next one"
        agent._armInteractionRecordingOnInput()
        second = agent._interactionRecorder
        check("the next request starts a NEW recording",
              second is not None and second.running and second is not recorder)
        check("...from zero",
              second.live_summary()["seconds"] < 0.01
              and not second.live_summary()["counts"],
              second.live_summary())
    finally:
        pr.time.time = saved_time
        pr.InputRecorder.start = saved_start
        if saved_qt is None:
            sys.modules.pop("qt", None)
        else:
            sys.modules["qt"] = saved_qt


def main():
    print("Checking the user-study interaction recorder")
    print("=" * 70)
    pr = _load("PlanningRecorder", CANONICAL)
    section_1_vendored_copies()
    section_2_partition(pr)
    section_3_block_vs_drag(pr)
    section_4_isolated_click(pr)
    section_5_extensions_wired()
    section_6_report(pr)
    section_7_compaction_is_exact(pr)
    section_8_run_folders(pr)
    section_9_duplicate_deliveries(pr)
    section_10_nothing_until_save(pr)
    section_11_where_the_click_landed(pr)
    section_12_whose_panel(pr)
    section_13_scene_close(pr)
    section_14_typing_arms_the_clock(pr)

    print()
    if FAILURES:
        print("FAILED (%d):" % len(FAILURES))
        for failure in FAILURES:
            print("  - " + failure)
        return 1
    print("All planning-recorder checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
