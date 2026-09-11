"""Check the LongBoneFractureReduction analysis outside Slicer.

``longbone.py`` imports neither ``slicer`` nor ``vtk``, so this runs the WHOLE
analysis -- the ITK/HDF5 transform reader, the ``scene.mrml`` chain walk, the
frame resolution, the ground-truth choice and the residual statistics -- against
the real saved runs.

The module reduces two different kinds of case to one residual ``E = G . P^-1``,
and every way that can go wrong yields a plausible table of millimetres rather
than an error:

1. **The transform reader.** ``P`` is pulled out of an 8 KB HDF5 file by locating
   twelve doubles that form a proper rotation -- no ``h5py`` in Slicer's Python
   and no HDF5 parser here. Section 1 requires that reader to reproduce, on all
   seven annotated runs, the ``pose_before_annotation_ras`` those runs recorded
   independently. That agreement is the whole licence for using it on the other
   57, where nothing else states the pose.
2. **The composition order.** ``Reduction Base`` is the identity on every run
   saved so far, so composing the chain backwards is invisible today and wrong
   the day a run has a real one. Section 2 requires the order to come from
   ``scene.mrml`` -- it builds a scene whose chain is reversed and a non-identity
   pair, and requires the two orders to disagree and the scene's to win.
3. **Which fragment the run moved.** The simulation displaced ONE of the two
   fragments, so the ground truth is ``D^-1`` or ``D``. Section 3 requires the
   decision to come out right on every simulated run, and section 4 requires the
   abutment verdict to REFUSE the other matrix rather than merely report it --
   a check that only means something if it can fail.
4. **The frame.** These meshes are written in LPS; un-mirrored they are the same
   bone on the far side of the origin, which still produces distances. Section 5
   requires the resolver to pick the mirrored frame on real data and to REFUSE
   when neither frame fits.
5. **The residual itself.** Section 6 requires the recomputed rotation and shift
   to equal the ones the annotation recorded, and checks the arithmetic against
   a synthetic case whose answer is known in closed form.
6. **The phase map.** Section 7 checks ``PHASE_STEPS`` against the installed
   ``workflow.json``: a regenerated package that renumbers its steps would
   otherwise make t0..t6 silently shrink while still summing to something
   plausible.
7. **The whole sweep.** Section 8 runs ``build_report`` over every saved run and
   requires every case to be scored and every verdict to pass.
8. **Damage.** Section 9 requires the module's source to carry no write and no
   delete at all: the panel promises the saved runs and the open scene are left
   alone, and the safest form of that promise is that the code cannot break it.
9. **Reachability.** Section 10 requires the panel to actually appear. A second
   module once registered a builder for this procedure too, the registry held
   ONE builder per extension, and the later import silently replaced this
   analysis -- the section showed only the other tool. Nothing raised, and which
   panel survived depended on the order of a tuple. That module is gone, so the
   registry's tolerance of two claims is now pinned with SYNTHETIC builders:
   an invariant nothing exercises is the one that rots.

    python scripts/check_longbone_analysis.py
"""

import io
import json
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

for _name in ("slicer", "qt", "vtk", "ctk"):
    sys.modules.setdefault(_name, types.ModuleType(_name))
sys.modules["slicer"].util = types.ModuleType("slicer.util")

import numpy as np                                            # noqa: E402

from SlicerAIAgentLib.experiments import longbone             # noqa: E402

FAILURES = []

EXPERIMENT_ROOT = os.path.join(ROOT, longbone.EXPERIMENT_DIR)
SCRATCH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "_check_longbone_tmp")


def check(label, condition):
    print(("PASS  " if condition else "FAIL  ") + label)
    if not condition:
        FAILURES.append(label)


def section(title):
    print("")
    print("=== " + title)


def _scratch(name):
    if not os.path.isdir(SCRATCH):
        os.makedirs(SCRATCH)
    return os.path.join(SCRATCH, name)


def rigid(degrees, axis, translation):
    """A 4x4 rigid transform, built the long way so it is independent of the
    module's own axis-angle code."""
    axis = np.asarray(axis, dtype=np.float64)
    axis = axis / np.linalg.norm(axis)
    theta = np.radians(degrees)
    cross = np.array([[0, -axis[2], axis[1]],
                      [axis[2], 0, -axis[0]],
                      [-axis[1], axis[0], 0]], dtype=np.float64)
    rotation = (np.eye(3) + np.sin(theta) * cross
                + (1 - np.cos(theta)) * (cross @ cross))
    matrix = np.eye(4)
    matrix[:3, :3] = rotation
    matrix[:3, 3] = np.asarray(translation, dtype=np.float64)
    return matrix


def annotated_cases():
    cases = longbone.discover_cases(EXPERIMENT_ROOT)
    return [case for case in cases
            if os.path.isfile(os.path.join(case["scene_dir"],
                                           longbone.ANNOTATION_NAME))]


def simulated_cases():
    cases = longbone.discover_cases(EXPERIMENT_ROOT)
    return [case for case in cases
            if not os.path.isfile(os.path.join(case["scene_dir"],
                                               longbone.ANNOTATION_NAME))]


# ---------------------------------------------------------------------------
# 1. The transform reader, against an independent record of the same pose
# ---------------------------------------------------------------------------

def check_transform_reader():
    section("1. the ITK/HDF5 reader vs the pose the annotation recorded")
    cases = annotated_cases()
    check("there are annotated runs to check the reader against", bool(cases))
    worst = 0.0
    for case in cases:
        record = longbone.read_annotation(
            os.path.join(case["scene_dir"], longbone.ANNOTATION_NAME))
        pose, chain = longbone.pose_from_scene(case["scene_dir"])
        gap = float(np.abs(pose - record["pose_before_annotation_ras"]).max())
        worst = max(worst, gap)
        check("%s: the pose composed from %s equals the recorded one (%.2g)"
              % (case["subject"], " o ".join(chain), gap),
              gap <= longbone.POSE_RESIDUAL_LIMIT_MM)
    print("      worst disagreement over %d run(s): %.3g" % (len(cases), worst))

    # A file that is not an affine transform must be refused, not mined for
    # twelve doubles that happen to look orthonormal.
    path = _scratch("not-a-transform.h5")
    with open(path, "wb") as handle:
        handle.write(b"\x89HDF\r\n\x1a\n" + np.eye(3).tobytes() * 40)
    try:
        longbone.read_itk_affine(path)
        check("a file with no AffineTransform_double_3_3 is refused", False)
    except ValueError:
        check("a file with no AffineTransform_double_3_3 is refused", True)


# ---------------------------------------------------------------------------
# 2. The composition order comes from the scene, not from the file names
# ---------------------------------------------------------------------------

_SCENE_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<MRML version="Slicer4.11.0" userTags="">
 <Model id="vtkMRMLModelNode5" name="Moving_Segment" \
references="storage:vtkMRMLModelStorageNode2;transform:{first}" ></Model>
 <LinearTransform id="vtkMRMLLinearTransformNodeA" name="Outer" \
references="storage:vtkMRMLTransformStorageNodeA;{outer_parent}" ></LinearTransform>
 <LinearTransform id="vtkMRMLLinearTransformNodeB" name="Inner" \
references="storage:vtkMRMLTransformStorageNodeB;{inner_parent}" ></LinearTransform>
 <TransformStorage id="vtkMRMLTransformStorageNodeA" \
fileName="A%20transform.h5" ></TransformStorage>
 <TransformStorage id="vtkMRMLTransformStorageNodeB" \
fileName="B%20transform.h5" ></TransformStorage>
</MRML>
"""


def check_composition_order():
    section("2. the transform chain is read out of scene.mrml")
    # A o B and B o A, with two transforms that do NOT commute -- otherwise the
    # order could be wrong and the test would still pass.
    forward = os.path.join(SCRATCH, "chain-forward")
    backward = os.path.join(SCRATCH, "chain-backward")
    for folder in (forward, backward):
        if not os.path.isdir(folder):
            os.makedirs(folder)

    # A: model -> B -> A, so world = A o B.  B: model -> A -> B, world = B o A.
    io.open(os.path.join(forward, "scene.mrml"), "w", encoding="utf-8").write(
        _SCENE_TEMPLATE.format(first="vtkMRMLLinearTransformNodeB",
                               inner_parent="transform:"
                                            "vtkMRMLLinearTransformNodeA",
                               outer_parent=""))
    io.open(os.path.join(backward, "scene.mrml"), "w", encoding="utf-8").write(
        _SCENE_TEMPLATE.format(first="vtkMRMLLinearTransformNodeA",
                               inner_parent="",
                               outer_parent="transform:"
                                            "vtkMRMLLinearTransformNodeB"))

    matrices = {"A transform.h5": rigid(30, (0, 0, 1), (10, 0, 0)),
                "B transform.h5": rigid(40, (1, 0, 0), (0, 20, 0))}
    check("the two test transforms do not commute",
          np.abs(matrices["A transform.h5"] @ matrices["B transform.h5"]
                 - matrices["B transform.h5"] @ matrices["A transform.h5"]
                 ).max() > 1.0)

    # Patch the reader for this section only: writing a real ITK HDF5 file is not
    # what is under test here, the ORDER is.
    original = longbone.read_itk_affine
    longbone.read_itk_affine = lambda path: matrices[os.path.basename(path)]
    try:
        for folder in (forward, backward):
            for name in matrices:
                open(os.path.join(folder, name), "wb").close()
        chain_forward = longbone.transform_chain(
            os.path.join(forward, "scene.mrml"))
        chain_backward = longbone.transform_chain(
            os.path.join(backward, "scene.mrml"))
        check("the chain is read nearest-parent first (%s)"
              % " o ".join(chain_forward),
              chain_forward == ["B transform.h5", "A transform.h5"])
        check("the reversed scene yields the reversed chain",
              chain_backward == ["A transform.h5", "B transform.h5"])

        pose_forward, _unused = longbone.pose_from_scene(forward)
        pose_backward, _unused = longbone.pose_from_scene(backward)
        check("model -> B -> A composes as A o B",
              np.abs(pose_forward - matrices["A transform.h5"]
                     @ matrices["B transform.h5"]).max() < 1e-12)
        check("model -> A -> B composes as B o A",
              np.abs(pose_backward - matrices["B transform.h5"]
                     @ matrices["A transform.h5"]).max() < 1e-12)
        check("and the two orders really are different poses",
              np.abs(pose_forward - pose_backward).max() > 1.0)
    finally:
        longbone.read_itk_affine = original

    # A model under no transform recorded no reduction, and must be refused
    # rather than scored against the identity -- which would report the whole
    # displacement as the residual and look like a total failure of the run.
    bare = os.path.join(SCRATCH, "chain-none")
    if not os.path.isdir(bare):
        os.makedirs(bare)
    io.open(os.path.join(bare, "scene.mrml"), "w", encoding="utf-8").write(
        '<MRML><Model id="m" name="Moving_Segment" references="storage:s;" >'
        '</Model></MRML>')
    try:
        longbone.transform_chain(os.path.join(bare, "scene.mrml"))
        check("a model under no transform is refused", False)
    except ValueError:
        check("a model under no transform is refused", True)


# ---------------------------------------------------------------------------
# 3-4. Which fragment the run moved, and the verdict that can refuse the other
# ---------------------------------------------------------------------------

def check_fragment_role():
    section("3. which simulated fragment each run moved")
    cases = simulated_cases()
    check("there are simulated runs to decide", bool(cases))
    roles = {"moved": 0, "fixed": 0}
    worst_margin, worst_cost = 1e9, 0.0
    for case in cases:
        files = longbone.find_case_files(case, EXPERIMENT_ROOT)
        if files["error"]:
            check("%s: files complete" % case["subject"], False)
            continue
        moving = longbone.read_vtk_points(files["moving"])
        reference = longbone.read_vtk_points(files["reference"])
        truth = longbone._simulated_truth(files, moving, reference)
        roles[truth["role"]] += 1
        margin = truth["columns"]["role_margin_mm"]
        cost = truth["columns"]["role_cost_mm"]
        worst_margin = min(worst_margin, margin)
        worst_cost = max(worst_cost, cost)
    print("      roles: %d moved, %d fixed" % (roles["moved"], roles["fixed"]))
    print("      smallest margin %.1f mm, largest winning cost %.1f mm"
          % (worst_margin, worst_cost))
    check("both roles actually occur, so the choice is not a constant",
          roles["moved"] > 0 and roles["fixed"] > 0)
    check("the winning assignment always beats the other by more than it "
          "itself costs", worst_margin > worst_cost)


def check_wrong_truth_is_refused():
    section("4. the abutment verdict refuses the OTHER ground truth")
    cases = simulated_cases()
    right, wrong = [], []
    for case in cases:
        files = longbone.find_case_files(case, EXPERIMENT_ROOT)
        if files["error"]:
            continue
        moving = longbone.read_vtk_points(files["moving"])
        reference = longbone.read_vtk_points(files["reference"])
        truth = longbone._simulated_truth(files, moving, reference)
        record = truth["record"]
        other = longbone.ground_truth_for_role(
            record, "fixed" if truth["role"] == "moved" else "moved")
        frame = truth["frame"]
        moving_surface = longbone.in_frame(
            longbone.read_vtk_points(files["moving_surface"]), frame)
        reference_surface = longbone.in_frame(
            longbone.read_vtk_points(files["reference_surface"]), frame)
        right.append(longbone.median_distance(
            longbone.apply_transform(truth["matrix"], moving_surface),
            reference_surface))
        wrong.append(longbone.median_distance(
            longbone.apply_transform(other, moving_surface), reference_surface))
    check("there were runs to test", bool(right))
    print("      chosen  ground truth: %.2f .. %.2f mm" % (min(right), max(right)))
    print("      rejected ground truth: %.2f .. %.2f mm" % (min(wrong), max(wrong)))
    check("every chosen ground truth passes the %.0f mm limit"
          % longbone.TRUTH_FIT_LIMIT_MM,
          max(right) <= longbone.TRUTH_FIT_LIMIT_MM)
    check("every rejected one FAILS it -- the verdict can refuse, so passing "
          "it means something", min(wrong) > longbone.TRUTH_FIT_LIMIT_MM)


# ---------------------------------------------------------------------------
# 5. The frame is resolved, and an impossible one is refused
# ---------------------------------------------------------------------------

def check_frame_resolution():
    section("5. LPS vs RAS is measured, not assumed")
    cases = longbone.discover_cases(EXPERIMENT_ROOT)
    frames = set()
    for case in cases[:8]:
        files = longbone.find_case_files(case, EXPERIMENT_ROOT)
        if files["error"]:
            continue
        moving = longbone.read_vtk_points(files["moving"])
        if files["annotation"]:
            pose, _unused = longbone.pose_from_scene(case["scene_dir"])
            truth = longbone._annotated_truth(files, moving, pose)
        else:
            truth = longbone._simulated_truth(
                files, moving, longbone.read_vtk_points(files["reference"]))
        frames.add(truth["frame"])
    check("the saved models resolve to one frame, and it is the mirrored one "
          "(%s)" % ", ".join(sorted(frames)), frames == {longbone.FRAME_MIRRORED})

    # A witness that fits NEITHER frame must raise rather than silently pick the
    # less-bad one: the whole point is that a mirrored bone still yields numbers.
    try:
        longbone.resolve_points_frame(np.zeros((10, 3)),
                                      lambda points, frame: 1e6)
        check("a cloud that fits neither frame is refused", False)
    except ValueError:
        check("a cloud that fits neither frame is refused", True)
    points, frame, distance = longbone.resolve_points_frame(
        np.array([[1.0, 2.0, 3.0]]),
        lambda pts, label: 0.0 if label == longbone.FRAME_MIRRORED else 100.0)
    check("the witness's own answer decides which frame is returned",
          frame == longbone.FRAME_MIRRORED and distance == 0.0
          and np.allclose(points, [[-1.0, -2.0, 3.0]]))


# ---------------------------------------------------------------------------
# 6. The residual arithmetic
# ---------------------------------------------------------------------------

def check_residual_arithmetic():
    section("6. the residual reproduces what the annotation recorded")
    for case in annotated_cases():
        files = longbone.find_case_files(case, EXPERIMENT_ROOT)
        if files["error"]:
            check("%s: files complete" % case["subject"], False)
            continue
        result = longbone.analyse_case(case, EXPERIMENT_ROOT)
        row = result["row"]
        rotation_gap = abs(row["rotation_deg"] - row["recorded_rotation_deg"])
        shift_gap = abs(row["translation_mm"] - row["recorded_shift_mm"])
        check("%s: rotation %.4f deg matches the recorded %.4f (%.2g)"
              % (case["subject"], row["rotation_deg"],
                 row["recorded_rotation_deg"], rotation_gap),
              rotation_gap <= longbone.RECORD_TOLERANCE_DEG)
        check("%s: shift %.4f mm matches the recorded %.4f (%.2g)"
              % (case["subject"], row["translation_mm"],
                 row["recorded_shift_mm"], shift_gap),
              shift_gap <= longbone.RECORD_SHIFT_TOLERANCE_MM)
        check("%s: the ground truth carries the mesh onto the shape the "
              "annotation saved (%.2g mm)"
              % (case["subject"], row["truth_shape_residual_mm"]),
              row["truth_shape_residual_mm"] < 1e-3)

    section("6b. the same arithmetic on a case whose answer is known")
    # A pure 10 deg rotation about z through the origin, applied to a ring of
    # radius 50 in the z = 0 plane: every point travels 2 * 50 * sin(5 deg).
    angle = np.radians(np.arange(0, 360, 1.0))
    ring = np.stack([50 * np.cos(angle), 50 * np.sin(angle),
                     np.zeros_like(angle)], axis=1)
    residual = rigid(10.0, (0, 0, 1), (0, 0, 0))
    expected = 2 * 50 * np.sin(np.radians(5.0))
    stats = longbone.point_displacement_stats(ring, residual)
    check("every point of a ring travels 2 R sin(theta/2) = %.4f mm (%.4f)"
          % (expected, stats["mean"]), abs(stats["mean"] - expected) < 1e-6)
    degrees, axis = longbone.rotation_angle_axis(residual[:3, :3])
    check("its angle reads back as 10 deg about +z",
          abs(degrees - 10.0) < 1e-9 and np.allclose(axis, [0, 0, 1]))

    # The clinical split: a rotation purely about the shaft is all malrotation
    # and no angulation, and a shift purely along it is all shortening.
    shaft = np.array([0.0, 0.0, 1.0])
    points = ring + np.array([0.0, 0.0, 100.0])
    site = np.zeros(3)
    torsion = longbone.axis_decomposition(rigid(6.0, shaft, (0, 0, 0)),
                                          points, shaft, site)
    check("a rotation about the shaft is all malrotation",
          abs(torsion["axial_rotation_deg"] - 6.0) < 1e-9
          and torsion["angulation_deg"] < 1e-9)
    tilt = longbone.axis_decomposition(rigid(6.0, (1, 0, 0), (0, 0, 0)),
                                       points, shaft, site)
    check("a rotation across it is all angulation",
          tilt["axial_rotation_deg"] < 1e-9
          and abs(tilt["angulation_deg"] - 6.0) < 1e-9)
    shortened = longbone.axis_decomposition(
        rigid(0.0, shaft, (0, 0, 4.0)), points, shaft, site)
    check("a shift along it, away from the fracture, is +4 mm of overlap",
          abs(shortened["axial_error_mm"] - 4.0) < 1e-9
          and shortened["transverse_error_mm"] < 1e-9)
    # The sign is against an axis pointed AWAY from the fracture site, so the
    # same shift on a fragment sitting on the other side must read as -4.
    mirrored = longbone.axis_decomposition(
        rigid(0.0, shaft, (0, 0, 4.0)), points - np.array([0.0, 0.0, 200.0]),
        shaft, site)
    check("and reads -4 mm on a fragment on the other side of the fracture",
          abs(mirrored["axial_error_mm"] + 4.0) < 1e-9)


# ---------------------------------------------------------------------------
# 7. The phase map against the installed workflow
# ---------------------------------------------------------------------------

def check_phase_map():
    section("7. PHASE_STEPS against the installed workflow.json")
    path = os.path.join(ROOT, "Resources", "extension_CLI",
                        longbone.EXTENSION_NAME, "workflow.json")
    if not os.path.isfile(path):
        print("      no workflow.json installed -- skipped")
        return
    document = json.load(io.open(path, encoding="utf-8"))
    steps = document.get("steps") if isinstance(document, dict) else document
    ids = [longbone.canonical_step_id(str(step.get("step_id", "")))
           for step in steps or []]
    ids = [step_id for step_id in ids if step_id]
    mapped = set(longbone._PHASE_OF_STEP)
    missing = [step_id for step_id in ids if step_id not in mapped]
    extra = sorted(mapped - set(ids))
    check("every workflow step lands in a phase (%d step(s))" % len(ids),
          not missing)
    if missing:
        print("      unplaced: " + ", ".join(missing))
    check("no phase names a step the workflow does not have", not extra)
    if extra:
        print("      unknown: " + ", ".join(extra))
    check("the phases do not overlap",
          sum(len(steps) for steps in longbone.PHASE_STEPS.values())
          == len(mapped))


# ---------------------------------------------------------------------------
# 8. The whole sweep
# ---------------------------------------------------------------------------

def check_full_sweep():
    section("8. every saved run, end to end")
    report = longbone.build_report(EXPERIMENT_ROOT)
    rows = report["rows"]
    check("every discovered run produced a row (%d of %d)"
          % (report["analysed"], report["cases"]),
          report["analysed"] == report["cases"] and not report["failed_cases"])
    check("every row is scored",
          all(row.get("status") == "scored" for row in rows))
    check("every ground truth passed the abutment verdict",
          all(row.get("truth_verified") for row in rows))
    check("every annotation agreed with itself and with its run",
          all(row.get("record_consistent") is not False for row in rows))
    check("both kinds of ground truth are represented",
          {row.get("truth_source") for row in rows} == {"annotation",
                                                        "simulation"})
    # The residual must be a real improvement on doing nothing, or the pipeline
    # would not be worth measuring -- and a residual LARGER than the initial
    # displacement means the sign of something is inverted.
    fractions = [row.get("residual_fraction") for row in rows
                 if isinstance(row.get("residual_fraction"), float)]
    check("every run left less error than it started with (worst %.2f)"
          % max(fractions), max(fractions) < 1.0)
    # The decomposition exists exactly where an axis is recorded, and nowhere
    # else: a blank there is a refusal this analysis makes deliberately.
    decomposed = [row for row in rows
                  if row.get("axial_rotation_deg") is not None]
    check("the clinical split is present on the simulated cases and absent on "
          "the annotated ones",
          all(row.get("truth_source") == "simulation" for row in decomposed)
          and len(decomposed) == sum(1 for row in rows
                                     if row.get("truth_source") == "simulation"))
    for population in ("annotated (6 hospitals)", "simulated (TotalSegmentor)"):
        check("the summary reports the %s population" % population,
              any(row["population"] == population for row in report["summary"]))
    pooled = [row for row in report["summary"]
              if row["population"] == "all cases"]
    check("the pooled block omits the metrics only one population carries",
          all("malrotation" not in row["metric"] for row in pooled))
    print("      %d case(s), point error mean %.2f mm"
          % (len(rows), float(np.mean([row["point_error_mean_mm"]
                                       for row in rows]))))


# ---------------------------------------------------------------------------
# 9. The analysis cannot damage a run
# ---------------------------------------------------------------------------

def check_read_only():
    section("9. the analysis only reads")
    # The panel promises the current scene and the saved runs are left alone,
    # and the safest guarantee is that the module CANNOT touch them: it opens
    # nothing for writing and removes nothing. The one file this feature writes
    # is the workbook, and that is written by workbook.py from run_analysis --
    # which is why the ban is checked against the analysis module's source and
    # not against the package.
    source = io.open(os.path.join(ROOT, "SlicerAIAgentLib", "experiments",
                                  "longbone.py"), encoding="utf-8").read()
    banned = [token for token in
              ('rmtree', 'os.remove', 'os.rename', 'os.makedirs', 'saveNode',
               'saveScene', '"w"', "'w'", '"wb"', "'wb'", '"a"', "'a'")
              if token in source]
    check("longbone.py writes and deletes nothing (%s)"
          % (", ".join(banned) if banned else "no write tokens"), not banned)
    check("and it imports neither slicer nor vtk, so this whole file ran "
          "outside Slicer",
          "\nimport slicer" not in source and "\nimport vtk" not in source)


# ---------------------------------------------------------------------------
# 10. The panel is actually reachable
# ---------------------------------------------------------------------------

def check_panel_registration():
    section("10. the panel is reachable, and is the only one on this procedure")
    # This is the failure that made the whole analysis invisible: a second
    # module (the DICOM dataset tool, since removed) registered a builder for
    # this procedure too, the registry was a dict of ONE builder, and that
    # module was imported last -- so it silently replaced the analysis panel and
    # the section showed the dataset tool as if that were all there was. Nothing
    # raised: an overwrite is a legal assignment.
    #
    # The registry must still tolerate two claims, or the next procedure to
    # attract a second panel loses one of them the same silent way. Nothing
    # shipped claims two any more, so this is proved against the shipped
    # registry code driven with SYNTHETIC builders -- an invariant no live code
    # exercises is precisely the one that rots.
    import ast                                                # noqa: PLC0415

    panel_dir = os.path.join(ROOT, "SlicerAIAgentLib", "experiments")
    app_dir = os.path.join(ROOT, "SlicerAIAgentLib", "app")
    widget = io.open(os.path.join(app_dir, "widget_experiments.py"),
                     encoding="utf-8").read()

    listed = ast.literal_eval(
        widget.split("_PANEL_MODULES = ", 1)[1].split("\n\n", 1)[0].strip())
    check("longbone_panel is in _PANEL_MODULES", "longbone_panel" in listed)
    check("every listed panel module exists (%s)" % ", ".join(listed),
          all(os.path.isfile(os.path.join(panel_dir, "%s.py" % name))
              for name in listed))

    # Run the registry exactly as shipped, with two builders from two modules.
    head = widget[widget.index("EXPERIMENT_PANELS = {}"):
                  widget.index("class WidgetExperimentsMixin:")]
    namespace = {"qt": types.SimpleNamespace(QFrame=object)}
    exec(compile(head, "widget_experiments", "exec"), namespace)   # noqa: S102
    register = namespace["register_experiment_panel"]
    panels = namespace["EXPERIMENT_PANELS"]

    def builder(module, name):
        scope = {"__name__": module}
        exec("def %s(widget, layout, extension):\n    pass\n" % name, scope)
        return scope[name]

    register(longbone.EXTENSION_NAME)(builder("longbone_panel", "build_panel"))
    register(longbone.EXTENSION_NAME)(builder("second_panel", "_build"))
    registered = panels[longbone.EXTENSION_NAME]
    check("both builders survive registration (%s)"
          % ", ".join(fn.__module__ for fn in registered),
          [fn.__module__ for fn in registered] == ["longbone_panel",
                                                   "second_panel"])
    reloaded = builder("longbone_panel", "build_panel")
    register(longbone.EXTENSION_NAME)(reloaded)
    check("re-importing a panel module replaces its builder instead of "
          "stacking a second copy",
          len(panels[longbone.EXTENSION_NAME]) == 2
          and panels[longbone.EXTENSION_NAME][0] is reloaded)

    # And the section must build every one of them, not just the first.
    body = widget[widget.index("def _onExperimentExtensionChanged"):]
    body = body[:body.index("\n    def ", 1)]
    check("the section iterates the builders rather than taking one",
          "for position, builder in enumerate(builders)" in body)
    check("and a failing builder does not clear its neighbours' widgets",
          "_clearExperimentContent()" not in body.split("except Exception")[1])

    # And nothing else may claim this procedure. The DICOM dataset panel that
    # once did is gone; a new second claimant would have to be a deliberate
    # choice, not something that arrives by importing a module.
    claimants = [name for name in listed
                 if longbone.EXTENSION_NAME in io.open(
                     os.path.join(panel_dir, "%s.py" % name),
                     encoding="utf-8").read()]
    check("exactly one shipped panel module claims %s (%s)"
          % (longbone.EXTENSION_NAME, ", ".join(claimants) or "none"),
          claimants == ["longbone_panel"])


def _cleanup():
    import shutil                                             # noqa: PLC0415
    if os.path.isdir(SCRATCH):
        shutil.rmtree(SCRATCH, ignore_errors=True)


def main():
    try:
        check_transform_reader()
        check_composition_order()
        check_fragment_role()
        check_wrong_truth_is_refused()
        check_frame_resolution()
        check_residual_arithmetic()
        check_phase_map()
        check_full_sweep()
        check_read_only()
        check_panel_registration()
    finally:
        _cleanup()

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
