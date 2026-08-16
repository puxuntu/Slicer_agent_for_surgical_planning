"""Check the ReverseShoulderArthroplasty analysis outside Slicer.

``shoulder.py`` and ``volume_io.py`` import neither ``slicer`` nor ``vtk``, so
unlike the orbital check this one can run the WHOLE analysis -- the angles, the
bone-density integral and both of its cone-space denominators -- against the real
saved runs. That is deliberate and it is the point of keeping the module
Slicer-free.

The reason it has to be provable here is that the module's worst failure mode
does not raise and does not look wrong. Slicer writes model files in LPS; the
plan is scored against a CT indexed from RAS. Forgetting the flip is invisible in
the angles -- the mirror is orthogonal, so every dot product, and therefore
theta1/theta2/theta3, is EXACTLY unchanged -- while the mirrored path leaves the
CT array entirely, every sample returns the out-of-bounds sentinel, and delta
comes out at ~1.000: a flawless score for a plan that is not in the patient.
Sections 5, 6 and 8 below exist for that one bug.

    python scripts/check_rsa_analysis.py
"""

import ast
import glob
import io
import os
import shutil
import sys
import tempfile
import types
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

for _name in ("slicer", "qt", "vtk", "ctk"):
    sys.modules.setdefault(_name, types.ModuleType(_name))
sys.modules["slicer"].util = types.ModuleType("slicer.util")

import numpy as np                                            # noqa: E402

from SlicerAIAgentLib.experiments import shoulder             # noqa: E402
from SlicerAIAgentLib.experiments import volume_io            # noqa: E402

FAILURES = []

EXPERIMENT_ROOT = os.path.join(ROOT, shoulder.EXPERIMENT_DIR)


def check(label, condition):
    print(("PASS  " if condition else "FAIL  ") + label)
    if not condition:
        FAILURES.append(label)


def close(a, b, tol=1e-6):
    return a is not None and abs(a - b) <= tol


def _cases():
    return shoulder.discover_cases(EXPERIMENT_ROOT)


def _case(subject):
    for case in _cases():
        if case["subject"] == subject:
            return case
    return None


# ---------------------------------------------------------------------------
# 1. The NRRD reader, against files whose answer is known by construction
# ---------------------------------------------------------------------------

def _write_nrrd(path, array, directions, origin, space, encoding, dtype_name,
                truncate=0, extra=()):
    """A minimal but real NRRD, written the way Slicer writes one."""
    header = ["NRRD0004", "type: %s" % dtype_name, "dimension: 3",
              "space: %s" % space,
              "sizes: %d %d %d" % (array.shape[2], array.shape[1], array.shape[0]),
              "space directions: (%g,%g,%g) (%g,%g,%g) (%g,%g,%g)"
              % tuple(list(directions[0]) + list(directions[1]) + list(directions[2])),
              "kinds: domain domain domain",
              "encoding: %s" % encoding,
              "space origin: (%g,%g,%g)" % tuple(origin)]
    if array.dtype.itemsize > 1:
        header.append("endian: %s" % ("little" if array.dtype.byteorder in "<=|"
                                      else "big"))
    header.extend(extra)
    body = array.tobytes()
    if encoding == "gzip":
        compressor = zlib.compressobj(6, zlib.DEFLATED, 16 + zlib.MAX_WBITS)
        body = compressor.compress(body) + compressor.flush()
    if truncate:
        body = body[:-truncate]
    with open(path, "wb") as handle:
        handle.write(("\n".join(header) + "\n\n").encode("ascii"))
        handle.write(body)


def check_nrrd_reader():
    work = tempfile.mkdtemp(prefix="rsa_nrrd_")
    try:
        array = (np.arange(2 * 3 * 4, dtype="<i2") - 5).reshape(4, 3, 2)
        directions = [(-0.5, 0, 0), (0, -0.5, 0), (0, 0, 2.0)]
        origin = (10.0, 20.0, 30.0)

        for encoding in ("raw", "gzip"):
            path = os.path.join(work, "lps_%s.nrrd" % encoding)
            _write_nrrd(path, array, directions, origin,
                        "left-posterior-superior", encoding, "short")
            read, ijk_to_ras, _header = volume_io.read_nrrd(path)
            check("%s encoding round-trips every voxel" % encoding,
                  np.array_equal(read, array))
            # LPS -> RAS negates the first two rows of BOTH the directions and
            # the origin. Getting only one of the two is the classic half-fix.
            check("%s: LPS is flipped to RAS in directions AND origin" % encoding,
                  close(ijk_to_ras[0, 0], 0.5) and close(ijk_to_ras[1, 1], 0.5)
                  and close(ijk_to_ras[2, 2], 2.0)
                  and close(ijk_to_ras[0, 3], -10.0) and close(ijk_to_ras[1, 3], -20.0)
                  and close(ijk_to_ras[2, 3], 30.0))

        path = os.path.join(work, "ras.nrrd")
        _write_nrrd(path, array, [(0.5, 0, 0), (0, 0.5, 0), (0, 0, 2.0)], origin,
                    "right-anterior-superior", "raw", "short")
        _read, ras_matrix, _header = volume_io.read_nrrd(path)
        check("a RAS file is NOT flipped",
              close(ras_matrix[0, 3], 10.0) and close(ras_matrix[1, 3], 20.0))

        path = os.path.join(work, "meta.nrrd")
        _write_nrrd(path, array.astype(np.uint8), directions, origin,
                    "left-posterior-superior", "gzip", "unsigned char",
                    extra=["Segment0_Name:=Bone", "sizes:=not a real field"])
        read, _matrix, _header = volume_io.read_nrrd(path)
        # `key:=value` is NRRD metadata. A parser that treats it as a field lets
        # `sizes:=...` shadow the real `sizes:` -- which a .seg.nrrd is full of.
        check("key:=value metadata cannot shadow a real field", read.shape == (4, 3, 2))

        path = os.path.join(work, "short.nrrd")
        _write_nrrd(path, array, directions, origin, "left-posterior-superior",
                    "raw", "short", truncate=8)
        raised = False
        try:
            volume_io.read_nrrd(path)
        except ValueError:
            raised = True
        check("a truncated payload raises rather than short-reading", raised)

        path = os.path.join(work, "odd.nrrd")
        _write_nrrd(path, array, directions, origin, "anterior-superior-left",
                    "raw", "short")
        raised = False
        try:
            volume_io.read_nrrd(path)
        except ValueError:
            raised = True
        check("an unhandled anatomical space raises rather than being assumed",
              raised)
    finally:
        shutil.rmtree(work, ignore_errors=True)


# ---------------------------------------------------------------------------
# 2. The sampler: nearest neighbour, banker's rounding, and the sentinel
# ---------------------------------------------------------------------------

def check_sampler():
    array = np.arange(8, dtype=np.int16).reshape(2, 2, 2)      # [k, j, i]
    identity = np.eye(4)

    values, inside = volume_io.sample_nearest(
        array, identity, np.array([[0., 0., 0.], [1., 1., 1.]]), -2000.0)
    check("a sample is indexed [k, j, i], matching arrayFromVolume",
          close(values[0], 0.0) and close(values[1], 7.0) and inside.all())

    # 0.5 and 1.5 are exact ties. np.rint is half-to-EVEN, like Python's round
    # and therefore like the int(round(...)) being reproduced; int(x + 0.5)
    # would give 1 and 2, and astype(int) would give 0 and 1.
    ties, _inside = volume_io.sample_nearest(
        array, identity, np.array([[0.5, 0., 0.], [1.5, 0., 0.]]), -2000.0)
    check("index rounding is half-to-even, not half-up and not truncation",
          close(ties[0], 0.0) and close(ties[1], -2000.0))

    values, inside = volume_io.sample_nearest(
        array, identity, np.array([[-5., 0., 0.], [99., 0., 0.]]), -2000.0)
    check("out of bounds takes the sentinel, not a clamped edge value",
          close(values[0], -2000.0) and close(values[1], -2000.0) and not inside.any())

    # The whole point of the sentinel: it must be SUBTRACTED from the integral,
    # so a path aimed out of the volume scores negative rather than zero.
    apex = np.array([0.0, 0.0, 0.0])
    away = np.array([[0.0, 0.0, -1.0]])
    total, _safe, in_bounds = shoulder.path_integrals(
        apex, away, 50.0, array, identity, -1024.0, 1528.0)
    check("a path outside the volume scores NEGATIVE, not zero",
          total[0] < 0 and in_bounds[0] == 0)


# ---------------------------------------------------------------------------
# 3. Tube-axis recovery
# ---------------------------------------------------------------------------

def _tube(entry, direction, length, radius, sides):
    direction = np.asarray(direction, float)
    direction = direction / np.linalg.norm(direction)
    helper = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(helper, direction)) > 0.9:
        helper = np.array([0.0, 1.0, 0.0])
    u = np.cross(direction, helper)
    u = u / np.linalg.norm(u)
    v = np.cross(direction, u)
    points = []
    for centre in (np.asarray(entry, float),
                   np.asarray(entry, float) + direction * length):
        for k in range(sides):
            angle = 2 * np.pi * k / sides
            points.append(centre + radius * (u * np.cos(angle) + v * np.sin(angle)))
    return np.asarray(points)


def check_tube_axis():
    entry, direction = np.array([1.0, 2.0, 3.0]), np.array([0.2, -0.4, 0.9])
    for sides, length in ((8, 38.97), (12, 14.72)):
        points = _tube(entry, direction, length, 1.0, sides)
        recovered, tip, radius = shoulder.tube_axis(points)
        check("a %d-sided tube gives back its axis and its %.2f mm length"
              % (sides, length),
              np.allclose(recovered, entry, atol=1e-9)
              and close(float(np.linalg.norm(tip - recovered)), length, 1e-9)
              and close(radius, 1.0, 1e-9))

    # The middle peg has TWELVE sides. Reading its 24 points as three rings of
    # eight yields a 7.4 mm "length" and a wrong direction -- which corrupts
    # theta1, theta2 and the cone axis at once. Rebuilt here as a genuine
    # three-ring tube so the ring check has something real to reject.
    three_rings = np.vstack([
        _tube(entry, direction, 14.72, 1.0, 8)[:8],
        _tube(entry + direction * 7.36, direction, 0.0, 1.0, 8)[:8],
        _tube(entry + direction * 14.72, direction, 0.0, 1.0, 8)[:8]])
    raised = False
    try:
        shoulder.tube_axis(three_rings)
    except ValueError:
        raised = True
    check("a mis-split that mixes the two ends is rejected, not averaged", raised)


# ---------------------------------------------------------------------------
# 4. The real cases: the angles
# ---------------------------------------------------------------------------

#: Measured from the two saved runs. Regenerating those runs changes them; that
#: is the point of pinning them.
EXPECTED_ANGLES = {
    "10250_L": (13.116, 22.500, 35.607),
    "10250_R": (10.272, 7.375, 14.315),
}


def _angle_row(result, plan="pipeline"):
    for row in result.get("angle_rows") or []:
        if row.get("plan") == plan:
            return row
    return None


def check_angles(results):
    if not results:
        print("SKIP  no saved runs under %s" % EXPERIMENT_ROOT)
        return
    for subject, (theta1, theta2, theta3) in EXPECTED_ANGLES.items():
        row = _angle_row(results.get(subject, {}))
        if row is None:
            print("SKIP  %s is not among the saved runs" % subject)
            continue
        check("%s: theta1/theta2/theta3 = %.3f / %.3f / %.3f"
              % (subject, theta1, theta2, theta3),
              close(row["theta1_deg"], theta1, 1e-3)
              and close(row["theta2_deg"], theta2, 1e-3)
              and close(row["theta3_deg"], theta3, 1e-3))

    for subject, result in results.items():
        row = _angle_row(result)
        # Spherical triangle inequality: the two screws cannot be further apart
        # than the sum of their angulations from the shared axis.
        check("%s: theta3 <= theta1 + theta2 (both are measured from one axis)"
              % subject,
              row["theta3_deg"] <= row["theta1_deg"] + row["theta2_deg"] + 1e-6)
        check("%s: the cone's own axis agrees with the middle peg" % subject,
              close(row.get("cone_axis_agreement_deg"), 0.0,
                    shoulder.AXIS_AGREEMENT_DEG))
        check("%s: the saved cone is the extension's %.1f deg half-angle"
              % (subject, shoulder.CONE_HALF_ANGLE_DEG),
              close(row.get("cone_half_angle_deg"), shoulder.CONE_HALF_ANGLE_DEG, 1e-2))
        check("%s: theta1 and theta2 are inside that cone" % subject,
              row.get("theta1_within_cone") and row.get("theta2_within_cone"))


# ---------------------------------------------------------------------------
# 5. The frame: proved against an independently written RAS record
# ---------------------------------------------------------------------------

def check_frame(results):
    if not results:
        print("SKIP  no saved runs")
        return
    for subject, result in results.items():
        row = _angle_row(result)
        check("%s: the drawn paths reproduce RSA_PlanResults.tsv, which is "
              "written in RAS (max gap %s mm)" % (subject, row.get("tsv_max_gap_mm")),
              row.get("frame_proof") == "plan table (RAS)"
              and row.get("tsv_max_gap_mm") is not None
              and row["tsv_max_gap_mm"] <= shoulder.TSV_TOLERANCE_MM)

    # And the discriminating half: the UNconverted (mirrored) geometry must fall
    # outside the CT array. Without this, "we applied the flip" is unfalsifiable
    # -- the angles are identical either way.
    for subject, result in results.items():
        case = result["case"]
        array, ijk_to_ras, _header = volume_io.read_nrrd(shoulder.ct_volume_path(case))
        try:
            ras_to_ijk = np.linalg.inv(ijk_to_ras)
            correct = shoulder.read_path_points(
                os.path.join(case["scene_dir"], shoulder.SCREW_PATH_FILES[0]))
            mirrored = correct.copy()
            mirrored[:, 0] *= -1.0
            mirrored[:, 1] *= -1.0
            _v, inside_ok = volume_io.sample_nearest(array, ras_to_ijk, correct, -2000.0)
            _v, inside_bad = volume_io.sample_nearest(array, ras_to_ijk, mirrored, -2000.0)
            check("%s: the mirrored path leaves the CT array, so the missing "
                  "LPS->RAS flip is detectable at all" % subject,
                  inside_ok.all() and not inside_bad.any())
        finally:
            del array


# ---------------------------------------------------------------------------
# 6. The integral reproduces the planner's own logged score
# ---------------------------------------------------------------------------

def check_integral(results):
    if not results:
        print("SKIP  no saved runs")
        return
    witnessed = 0
    for subject, result in results.items():
        for row in result["metric_rows"]:
            if row.get("score_logged") is None:
                continue
            witnessed += 1
            # Compared against the number parsed out of the run's own stdout,
            # not against a constant, so the check stays honest if the runs are
            # regenerated on different data.
            check("%s screw %d: the recomputed integral reproduces the planner's "
                  "logged Stability score bit-exactly (%d)"
                  % (subject, row["screw"], row["score_logged"]),
                  row.get("score_reproduced") is True)
            # The independent witness. The integral is a sum, which two
            # different sample sets could reach by cancellation; this is a
            # count over the same samples, so agreeing on both is what shows
            # the sampler sits on the same voxels.
            #
            # Checked only when it is PRESENT: the two lines are several lines
            # apart in the planner's stdout, and the 10 KB truncation lands
            # between them on at least one saved run (11084_L screw 2), which
            # leaves a score with no tally. That is a missing witness, not a
            # disagreement.
            if row.get("safe_points_logged") is not None:
                check("%s screw %d: and its threshold tally too (%s)"
                      % (subject, row["screw"], row["safe_points_logged"]),
                      row.get("safe_points_reproduced") is True)
    check("at least one run still carries a logged score to compare against",
          witnessed > 0)
    # The planner's stdout is truncated near 10 KB, so screw 2 normally has no
    # witness. Say so rather than letting a reader read the gap as a failure.
    print("      %d of %d screw row(s) had a logged score to compare against "
          "(the rest were cut off by the 10 KB stdout limit)"
          % (witnessed, sum(len(r["metric_rows"]) for r in results.values())))


# ---------------------------------------------------------------------------
# 7. The cone, and delta
# ---------------------------------------------------------------------------

#: (subject, screw) -> (chosen, max over the planner's half-cone, max over the full cone)
EXPECTED_DELTA = {
    ("10250_L", 1): (5098, 6259, 6259),
    ("10250_L", 2): (5131, 6472, 6507),
    ("10250_R", 1): (4855, 6373, 6373),
    ("10250_R", 2): (4843, 6958, 6958),
}


def check_delta(results):
    if not results:
        print("SKIP  no saved runs")
        return
    for (subject, screw), (chosen, searched, full) in EXPECTED_DELTA.items():
        rows = [r for r in results.get(subject, {}).get("metric_rows", [])
                if r["screw"] == screw and r.get("plan") == "pipeline"]
        if not rows:
            print("SKIP  %s screw %d is not among the saved runs" % (subject, screw))
            continue
        row = rows[0]
        check("%s screw %d: chosen %d, half-cone max %d, full-cone max %d"
              % (subject, screw, chosen, searched, full),
              row["integral_chosen"] == chosen
              and row["integral_max_searched"] == searched
              and row["integral_max_cone"] == full)
        check("%s screw %d: delta = %.4f, delta_searched = %.4f"
              % (subject, screw, chosen / float(full), chosen / float(searched)),
              close(row["delta"], round(chosen / float(full), 4), 1e-4)
              and close(row["delta_searched"], round(chosen / float(searched), 4), 1e-4))

    for subject, result in results.items():
        for row in result["metric_rows"]:
            if row.get("delta") is None:
                continue
            # The half-cone is a SUBSET of the full cone, so its maximum can
            # never be the larger. If it is, the rebuilt cone is not the one the
            # planner searched -- a wrong axis, or the paper's alpha written in
            # place of the extension's half-angle.
            plan = row.get("plan")
            label = "%s screw %d (%s)" % (subject, row["screw"], plan)
            # The half-cone is a SUBSET of the full cone, so its maximum can
            # never be the larger. If it is, the rebuilt cone is not the one the
            # planner searched -- a wrong axis, or the paper's alpha written in
            # place of the extension's half-angle.
            check("%s: the full cone's maximum is >= the half-cone's" % label,
                  row["integral_max_cone"] >= row["integral_max_searched"])
            check("%s: delta <= 1 -- the trajectory does not beat its own cone"
                  % label, row["delta"] <= 1.0)
            if plan == "pipeline":
                check("%s: the drawn path IS a candidate the planner searched "
                      "(not hand-aimed)" % label,
                      close(row.get("on_search_grid_deg"), 0.0, 1e-3))
            else:
                # A surgeon aiming by hand has no reason to land on the search
                # grid, and does not on any saved case. If a manual trajectory
                # ever sat exactly on it, the two plans would be the same plan
                # and the comparison would be vacuous.
                check("%s: the hand plan is NOT on the search grid, so the two "
                      "plans are genuinely different (%.2f deg off)"
                      % (label, row.get("on_search_grid_deg") or 0.0),
                      (row.get("on_search_grid_deg") or 0.0) > 1e-3)
            check("%s: the denominator is not a grid artefact (%.3f%% at %dx "
                  "resolution)"
                  % (label, row["denominator_sensitivity_pct"],
                     shoulder.DENOMINATOR_REFINE),
                  abs(row["denominator_sensitivity_pct"]) < 2.0)
            check("%s: every sample is inside the CT" % label,
                  row["samples_in_bounds"] == shoulder.INTEGRATION_STATIONS)

    # The rebuilt full cone must actually be a cone of the right shape, and it
    # must contain the axis itself as its centre candidate.
    apex, axis = np.array([1.0, 2.0, 3.0]), np.array([0.0, 0.0, -1.0])
    directions = shoulder.full_cone_directions(apex, axis, 38.97, 22.5, 144, 16)
    check("the rebuilt cone has Ra*Rl + 1 directions", directions.shape[0] == 144 * 16 + 1)
    angles = np.degrees(np.arccos(np.clip(directions @ axis, -1, 1)))
    check("no rebuilt direction leaves the cone half-angle", angles.max() <= 22.5 + 1e-6)
    check("the cone axis itself is among the candidates", angles.min() <= 1e-9)


# ---------------------------------------------------------------------------
# 7b. The pipeline-vs-manual pairing
# ---------------------------------------------------------------------------

def check_comparison(results):
    """The comparison is only meaningful if both plans share one denominator."""
    if not results:
        print("SKIP  no saved runs")
        return
    paired = 0
    for subject, result in results.items():
        rows = {(r["screw"], r.get("plan")): r for r in result["metric_rows"]}
        for row in result.get("comparison_rows") or []:
            paired += 1
            screw = row["screw"]
            pipeline = rows.get((screw, "pipeline")) or {}
            manual = rows.get((screw, "manual")) or {}
            label = "%s screw %d" % (subject, screw)

            # THE load-bearing invariant. Two deltas are only subtractable if
            # they divide by the same number; if the manual screw were scored
            # against its own cone, delta_gain would be the difference of two
            # differently-normalised quantities and would mean nothing.
            check("%s: both plans divide by the SAME cone maximum (%s)"
                  % (label, pipeline.get("integral_max_cone")),
                  pipeline.get("integral_max_cone") is not None
                  and pipeline["integral_max_cone"] == manual.get("integral_max_cone"))
            check("%s: and they leave the same entry point (%.6f mm apart)"
                  % (label, row.get("entry_gap_mm") or 0.0),
                  (row.get("entry_gap_mm") or 0.0) <= shoulder.ENTRY_PAIR_TOLERANCE_MM)
            check("%s: delta_gain is exactly delta_pipeline - delta_manual"
                  % label,
                  close(row["delta_gain"],
                        round(row["delta_pipeline"] - row["delta_manual"], 4), 1e-9))
            check("%s: pipeline_denser agrees with the sign of delta_gain" % label,
                  bool(row["pipeline_denser"]) == (row["delta_gain"] > 0))
            # Both trajectories are the same screw, so a length difference would
            # mean one of them is not 38.97 mm of bone and the integrals are
            # over different spans.
            check("%s: both trajectories are the same length (%.3f / %.3f mm)"
                  % (label, pipeline.get("length_mm") or 0.0,
                     manual.get("length_mm") or 0.0),
                  abs((pipeline.get("length_mm") or 0.0)
                      - (manual.get("length_mm") or 0.0)) <= 0.05)
            check("%s: the manual mesh corroborates its own table row (%.3f deg)"
                  % (label, manual.get("mesh_agreement_deg") or 0.0),
                  (manual.get("mesh_agreement_deg") or 0.0)
                  <= shoulder.MANUAL_MESH_TOLERANCE_DEG)
    check("every case produced two paired screws", paired == 2 * len(results))


# ---------------------------------------------------------------------------
# 8. delta refuses to be computed on geometry that is not in the volume
# ---------------------------------------------------------------------------

def check_out_of_frame_refusal(results):
    if not results:
        print("SKIP  no saved runs")
        return
    subject, result = sorted(results.items())[0]
    case = result["case"]
    array, ijk_to_ras, _header = volume_io.read_nrrd(shoulder.ct_volume_path(case))
    try:
        ras_to_ijk = np.linalg.inv(ijk_to_ras)
        smin, smax = float(array.min()), float(array.max())
        screw = shoulder.path_axis(case["scene_dir"], shoulder.SCREW_PATH_FILES[0])
        mirrored_entry = screw["entry"] * np.array([-1.0, -1.0, 1.0])
        mirrored_dir = screw["direction"] * np.array([-1.0, -1.0, 1.0])

        chosen, _safe, inside = shoulder.path_integrals(
            mirrored_entry, mirrored_dir[None, :], screw["length"],
            array, ras_to_ijk, smin, smax)
        cone = shoulder.full_cone_directions(mirrored_entry,
                                             screw["direction"] * np.array([-1., -1., 1.]),
                                             screw["length"], 22.5, 144, 16)
        totals, _s, _i = shoulder.path_integrals(mirrored_entry, cone, screw["length"],
                                                 array, ras_to_ijk, smin, smax)
        ratio = float(chosen[0]) / float(totals.max())
        # This is the failure the guard exists for, demonstrated rather than
        # asserted: a mirrored plan produces a delta indistinguishable from a
        # perfect one, because numerator and denominator are the same sentinel.
        check("%s: a mirrored plan yields a PLAUSIBLE delta (%.3f) -- which is "
              "why samples_in_bounds is the guard, not the ratio"
              % (subject, ratio),
              int(inside[0]) == 0 and 0.9 <= ratio <= 1.1)
        check("%s: and the guard would have caught it (0 of %d samples in bounds "
              "< %d)" % (subject, shoulder.INTEGRATION_STATIONS,
                         shoulder.MIN_SAMPLES_IN_BOUNDS),
              int(inside[0]) < shoulder.MIN_SAMPLES_IN_BOUNDS)
    finally:
        del array


# ---------------------------------------------------------------------------
# 9. The timing phase split
# ---------------------------------------------------------------------------

EXPECTED_PHASES = {
    "10250_L": {"t0_s": 0.89, "t1_s": 24.55, "t2_s": 40.43, "t3_s": 32.13,
                "t_refine_s": 8.31, "t_total_s": 113.7},
    "10250_R": {"t0_s": 0.87, "t1_s": 22.55, "t2_s": 31.10, "t3_s": 31.17,
                "t_refine_s": 3.50, "t_total_s": 97.1},
}


def check_phases(report):
    rows = {row["case"]: row for row in report.get("phase_rows") or []}
    if not rows:
        print("SKIP  no saved runs")
        return
    for subject, expected in EXPECTED_PHASES.items():
        row = rows.get(subject)
        if row is None:
            print("SKIP  %s is not among the saved runs" % subject)
            continue
        for name, value in expected.items():
            check("%s: %s = %.2f s" % (subject, name, value),
                  close(row.get(name), value, 0.02))
        check("%s: every step landed in a phase" % subject,
              not row.get("steps_unassigned"))
        check("%s: the phases sum to the report's own inside_steps_s (residual "
              "%s s)" % (subject, row.get("phase_residual_s")),
              abs(row.get("phase_residual_s") or 0.0) < 0.5)
        check("%s: the planning step ran exactly once" % subject,
              row.get("t3_visits") == 1)

    # A regenerated workflow that renumbers its steps must be LOUD, not short.
    # Without the unassigned bucket the phases would simply shrink.
    saved = dict(shoulder.PHASE_STEPS)
    saved_map = dict(shoulder._PHASE_OF_STEP)
    try:
        shoulder._PHASE_OF_STEP.pop("cb_step_20", None)
        case = _case(sorted(EXPECTED_PHASES)[0])
        if case is not None:
            from SlicerAIAgentLib.experiments.run_timing import collect_timing
            log = []
            timing_rows, step_rows = collect_timing([case], log)
            row = shoulder.phase_row(case, timing_rows[0] if timing_rows else {},
                                     step_rows, log)
            check("dropping a step from PHASE_STEPS surfaces it as unassigned "
                  "instead of silently shrinking t3",
                  "cb_step_20" in (row.get("steps_unassigned") or "")
                  and row["t3_s"] == 0.0
                  and any("no timing phase" in line for line in log))
    finally:
        shoulder.PHASE_STEPS = saved
        shoulder._PHASE_OF_STEP.clear()
        shoulder._PHASE_OF_STEP.update(saved_map)

    check("cb_step_07 and cb_step_7 are the same step",
          shoulder.canonical_step_id("cb_step_07") == "cb_step_7"
          and shoulder.canonical_step_id("cb_step_7") == "cb_step_7")


# ---------------------------------------------------------------------------
# 10. Discovery, and the shape of the workbook
# ---------------------------------------------------------------------------

def check_discovery_and_sheets(report):
    cases = _cases()
    if not cases:
        print("SKIP  no saved runs under %s" % EXPERIMENT_ROOT)
        return
    # RSA subjects carry an underscore (10250_L), which is exactly what
    # subject_from_run's basename.split("_")[1] fallback would truncate to
    # "10250" -- and Dataset/<subject> would then not exist.
    check("every case's subject survived discovery intact (%s)"
          % ", ".join(c["subject"] for c in cases),
          all("_" in (c["subject"] or "") for c in cases))
    check("each case's dataset folder was resolved",
          all(c["dataset_dir"] and os.path.basename(c["dataset_dir"]) == c["subject"]
              for c in cases))

    sheets = report.get("sheets") or []
    check("the workbook has exactly two tabs", len(sheets) == 2)
    check("they are Metrics and Timing",
          [title for title, _blocks in sheets] == ["Metrics", "Timing"])
    for title, blocks in sheets:
        check("the %s tab's blocks all declare their columns" % title,
              all(len(block) == 3 and block[1] for block in blocks))

    # A row is written through `row.get(name)` for each declared column, so a key
    # with no column is silently dropped -- which is how a computed metric gets
    # into the report and never into the spreadsheet. Checked only on the blocks
    # THIS module builds: the three that `run_timing.timing_sheet` contributes
    # are shared by every procedure and are not ours to constrain. (For the
    # record, its per-run block does drop one key, `subject`, deliberately --
    # `case` is derived from it and already carries it.)
    owned = [("angles", shoulder.ANGLE_COLUMNS, report.get("angle_rows")),
             ("density", shoulder.METRIC_COLUMNS, report.get("metric_rows")),
             ("comparison", shoulder.COMPARISON_COLUMNS, report.get("comparison_rows")),
             ("summary", shoulder.SUMMARY_COLUMNS, report.get("summary")),
             ("phases", shoulder.PHASE_COLUMNS, report.get("phase_rows"))]
    for name, columns, rows in owned:
        unknown = sorted({key for row in rows or [] for key in row
                          if key not in columns})
        check("every value of the %s block reaches a column (%s)"
              % (name, "stray: " + ", ".join(unknown) if unknown else "none stray"),
              not unknown)

    # The paper's delta is over the screws the planner optimised FOR DENSITY. A
    # best-effort screw was chosen by depth, so pooling the two produces a
    # headline number that answers neither question and whose meaning drifts
    # with the proportion of best-effort screws in the cohort.
    metrics = [name for name in
               (row["metric"] for row in report.get("summary") or [])]
    check("the summary reports delta for the PLANNED screws separately",
          "delta — pipeline (planned)" in metrics)
    check("no summary row pools the two populations under a bare 'delta'",
          "delta" not in metrics and "delta_searched" not in metrics)
    if any(r.get("selection") == "best effort" for r in report.get("metric_rows") or []):
        check("and the best-effort screws get their own row rather than "
              "vanishing into it", "delta — pipeline (BEST EFFORT)" in metrics)
    # The pipeline's and the surgeon's deltas answer the same question but are
    # two different plans; one pooled row would average a method against itself.
    check("the surgeon's hand plan gets its own summary row",
          "delta — manual" in metrics)
    check("and the paired difference is summarised too",
          "delta_gain (pipeline - manual)" in metrics)
    check("theta is summarised per plan, not pooled across the two",
          "theta1 (deg) — pipeline" in metrics and "theta1 (deg) — manual" in metrics)

    # `analysed` counts CASES; angle_rows carries one row per plan per case, so
    # the two differ by exactly the number of plans.
    check("the report distinguishes cases discovered from cases analysed",
          report.get("analysed") == len({row["case"] for row
                                         in report.get("angle_rows") or []})
          and isinstance(report.get("failed_cases"), list))
    check("every analysed case contributed one angle row per plan",
          len(report.get("angle_rows") or [])
          == report.get("analysed", 0) * len(shoulder.PLANS))


# ---------------------------------------------------------------------------
# 11. Static invariants
# ---------------------------------------------------------------------------

def check_no_slicer_imports():
    """The numerics halves must import neither Slicer nor VTK at module level.

    That is what lets this script exercise the real delta. A module-level
    ``import vtk`` added later would not fail in Slicer, so nothing but this
    check would notice that the whole analysis had become unverifiable.
    """
    for name in ("SlicerAIAgentLib/experiments/shoulder.py",
                 "SlicerAIAgentLib/experiments/volume_io.py"):
        path = os.path.join(ROOT, name)
        tree = ast.parse(io.open(path, encoding="utf-8").read(), filename=path)
        offenders = []
        for node in tree.body:                      # module level only
            if isinstance(node, ast.Import):
                offenders += [a.name for a in node.names
                              if a.name.split(".")[0] in ("slicer", "vtk", "qt", "ctk")]
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".")[0] in ("slicer", "vtk", "qt", "ctk"):
                    offenders.append(node.module)
        check("%s imports no Slicer/VTK/Qt at module level" % os.path.basename(name),
              not offenders)


def check_panel_registration():
    path = os.path.join(ROOT, "SlicerAIAgentLib", "app", "widget_experiments.py")
    source = io.open(path, encoding="utf-8").read()
    check("shoulder_panel is listed in _PANEL_MODULES",
          "shoulder_panel" in source)
    panel = io.open(os.path.join(ROOT, "SlicerAIAgentLib", "experiments",
                                 "shoulder_panel.py"), encoding="utf-8").read()
    check("the panel registers under the extension's own name",
          "@register_experiment_panel(shoulder.EXTENSION_NAME)" in panel)
    cli = os.path.join(ROOT, "Resources", "extension_CLI",
                       shoulder.EXTENSION_NAME, "manifest.json")
    # The Experiments selector is populated from the installed CLI packages, so
    # a name that does not match one there means the panel never appears --
    # and _loadExperimentPanels swallows the import error, so the symptom is
    # "No analysis defined for ..." rather than a traceback.
    check("that name matches an installed CLI package", os.path.isfile(cli))


def check_analysis_reads_only():
    """Nothing in this analysis may write to a run folder.

    ``orbital.py`` edits a run's saved ``scene.mrml`` in place, and does so
    carefully. This module has no reason to write anything but the workbook, so
    the safest guarantee is that it cannot: no open-for-write, no rmtree, no
    saveNode anywhere in it.
    """
    source = io.open(os.path.join(ROOT, "SlicerAIAgentLib", "experiments",
                                  "shoulder.py"), encoding="utf-8").read()
    banned = [token for token in ("rmtree", "os.remove", "os.rename", "saveNode",
                                  "saveScene", 'open(', "makedirs")
              if token in source.replace("io.open(", "").replace("_write", "")]
    # `open(` survives only via geometry_io/volume_io, which this module calls
    # rather than contains.
    check("shoulder.py writes nothing except through workbook.write_workbook",
          not banned)


def main():
    print("=" * 74)
    print(" 1. NRRD reader")
    print("=" * 74)
    check_nrrd_reader()
    print()
    print("=" * 74)
    print(" 2. CT sampler: nearest neighbour, rounding, the out-of-bounds sentinel")
    print("=" * 74)
    check_sampler()
    print()
    print("=" * 74)
    print(" 3. Tube-axis recovery")
    print("=" * 74)
    check_tube_axis()
    print()

    cases = _cases()
    results = {}
    report = {}
    if cases:
        print("=" * 74)
        print(" Analysing %d saved run(s)" % len(cases))
        print("=" * 74)
        for case in cases:
            try:
                results[case["subject"] or case["run"]] = dict(
                    analyse_result(case), case=case)
            except Exception as exc:                # noqa: BLE001
                check("%s could be analysed at all (%s)"
                      % (case["subject"] or case["run"], exc), False)
        report = shoulder.build_report(EXPERIMENT_ROOT)
        for line in report["log"]:
            print("      " + line)
        print()

    for title, function in ((" 4. The angles, on the real cases", check_angles),
                            (" 5. The coordinate frame", check_frame),
                            (" 6. The integral vs the planner's own log", check_integral),
                            (" 7. The cone and delta", check_delta),
                            (" 7b. Pipeline vs the surgeon's hand plan",
                             check_comparison),
                            (" 8. Refusing to score geometry outside the volume",
                             check_out_of_frame_refusal)):
        print("=" * 74)
        print(title)
        print("=" * 74)
        function(results)
        print()

    print("=" * 74)
    print(" 9. The timing phase split")
    print("=" * 74)
    check_phases(report)
    print()
    print("=" * 74)
    print(" 10. Discovery and the workbook's shape")
    print("=" * 74)
    check_discovery_and_sheets(report)
    print()
    print("=" * 74)
    print(" 11. Static invariants")
    print("=" * 74)
    check_no_slicer_imports()
    check_panel_registration()
    check_analysis_reads_only()
    print()

    if FAILURES:
        print("FAILED (%d):" % len(FAILURES))
        for failure in FAILURES:
            print("  - " + failure)
        return 1
    print("All ReverseShoulderArthroplasty-analysis checks passed.")
    return 0


def analyse_result(case):
    return shoulder.analyse_case(case)


if __name__ == "__main__":
    sys.exit(main())
