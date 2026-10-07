"""Check the PedicleScrewPlanner analysis outside Slicer.

``pedicle.py`` imports neither ``slicer`` nor ``vtk``, so this runs the WHOLE
analysis -- the scene reader, the frame bridge, the distance field, the breach
and clearance measures, the pedicle width and the timing phase split -- against
the two real saved runs.

That matters more here than usual, because every way this can go wrong produces a
plausible millimetre rather than an error. Nine of them, one section each:

1. **The frame bridge.** The run loads its CT centred and the dataset keeps the
   scanner's origin, so plan geometry has to cross between the two THROUGH the
   voxel index. Section 1 proves the bridge on synthetic volumes, proves it is
   NECESSARY (without it the surgeon's own landmarks fall outside every
   vertebra), and proves ``scene_volume_matching`` picks the volume on the
   ground truth's grid rather than the resampled ``baselineROI`` beside it.
2. **The LPS mirror.** Markups and models are written LPS. Skipping the mirror
   puts the plan on the other side of the patient, where it still intersects
   bone. Section 2 requires the un-mirrored plan to be refused.
3. **The zero level set.** The signed distance is ``EDT(outside) - EDT(inside)``,
   and it is the PAIR that puts the boundary on the voxel face. Section 3
   measures a synthetic box at known offsets, on an anisotropic grid, and
   requires the crop to change nothing.
4. **The graded span.** The planner puts the entry ON the cortex, so the wall
   around it is half outside by construction. Section 4 builds a screw whose
   ONLY protrusion is that entry funnel and requires grade A, then moves the
   protrusion into the pedicle and requires the exact millimetres back.
5. **Medial is not the name.** The plan's ``_L``/``_R`` suffix is the order the
   landmarks were placed, and on both real runs every screw named ``_L`` is on
   the patient's RIGHT. Section 5 requires the side to be derived from the
   vertebra's own centroid, and checks the medial direction against the ground
   truth's own spinal cord.
6. **The level comes from the landmark.** Section 6 requires a landmark one
   voxel outside the label to still resolve (a real screw does exactly that),
   requires a landmark between two vertebrae to be refused as ambiguous, and
   requires a deliberately mislabelled plan to be scored against the landmark
   and reported.
7. **The real runs, end to end**, with their reference values.
8. **The phase map** against the installed ``workflow.json``: a regenerated CLI
   package with different step ids would make the phases silently shrink while
   still summing to something plausible.
9. **Read-only.** The module must contain no write and no delete: it reads saved
   runs and a data set, and an analysis that edits its own evidence is not one.

    python scripts/check_pedicle_analysis.py
"""

import ast
import io
import json
import os
import shutil
import sys
import types
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

for _name in ("slicer", "qt", "vtk", "ctk"):
    sys.modules.setdefault(_name, types.ModuleType(_name))
sys.modules["slicer"].util = types.ModuleType("slicer.util")

import numpy as np                                            # noqa: E402

from SlicerAIAgentLib.experiments import pedicle              # noqa: E402
from SlicerAIAgentLib.experiments import run_timing        # noqa: E402
from SlicerAIAgentLib.experiments import geometry_io          # noqa: E402
from SlicerAIAgentLib.experiments import segmentation_io      # noqa: E402

FAILURES = []

EXPERIMENT_ROOT = run_timing.resolve_experiment_dir(
    ROOT, pedicle.EXPERIMENT_DIR)
SCRATCH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "_check_pedicle_tmp")


def check(label, condition):
    print(("PASS  " if condition else "FAIL  ") + label)
    if not condition:
        FAILURES.append(label)


def close(a, b, tol=1e-6):
    return a is not None and abs(float(a) - float(b)) <= tol


def section(title):
    print("")
    print("=" * 78)
    print(title)
    print("=" * 78)


# ---------------------------------------------------------------------------
# Synthetic NRRD writers
# ---------------------------------------------------------------------------

def _scratch(name):
    if not os.path.isdir(SCRATCH):
        os.makedirs(SCRATCH)
    return os.path.join(SCRATCH, name)


def write_nrrd(path, array, spacing, origin_lps, segments=None):
    """A gzip LPS NRRD, optionally carrying a segment table.

    ``array`` is ``[k, j, i]`` -- the order the readers hand back -- so the
    header's ``sizes`` is its reverse.
    """
    array = np.ascontiguousarray(array)
    nk, nj, ni = array.shape
    kind = {np.dtype("uint8"): "unsigned char",
            np.dtype("int16"): "short",
            np.dtype("int32"): "int"}[array.dtype]
    lines = ["NRRD0004", "type: %s" % kind, "dimension: 3",
             "space: left-posterior-superior",
             "sizes: %d %d %d" % (ni, nj, nk),
             "space directions: (%r,0,0) (0,%r,0) (0,0,%r)" % tuple(spacing),
             "kinds: domain domain domain",
             "encoding: gzip",
             "space origin: (%r,%r,%r)" % tuple(origin_lps)]
    if array.dtype.itemsize > 1:
        lines.append("endian: little")
    for index, (name, label) in enumerate(segments or []):
        lines.append("Segment%d_Name:=%s" % (index, name))
        lines.append("Segment%d_LabelValue:=%d" % (index, label))
        lines.append("Segment%d_Layer:=0" % index)
    header = ("\n".join(lines) + "\n\n").encode("ascii")
    engine = zlib.compressobj(6, zlib.DEFLATED, 16 + zlib.MAX_WBITS)
    payload = engine.compress(array.tobytes()) + engine.flush()
    with open(path, "wb") as handle:
        handle.write(header + payload)
    return path


def box_field(spacing=(0.5, 0.5, 1.0), size=(60, 60, 40), box=None,
              label=1, name="T11 vertebra", hu=None):
    """A :class:`VertebraField` over a synthetic box, plus its ijk_to_ras."""
    nk, nj, ni = size[2], size[1], size[0]
    volume = np.zeros((nk, nj, ni), dtype=np.uint8)
    if box is None:
        box = (20, 40, 20, 40, 12, 28)                       # i0,i1,j0,j1,k0,k1
    i0, i1, j0, j1, k0, k1 = box
    volume[k0:k1, j0:j1, i0:i1] = label
    matrix = np.eye(4)
    matrix[0, 0], matrix[1, 1], matrix[2, 2] = spacing
    field = pedicle.build_field(volume, label, name, matrix, hu)
    return volume, matrix, field


# ---------------------------------------------------------------------------
# 1. The frame bridge
# ---------------------------------------------------------------------------

def check_bridge():
    section("1. The frame bridge: scene RAS -> ground-truth RAS, through IJK")

    spacing = (0.49, 0.49, 1.0)
    sizes = (24, 24, 16)
    truth = np.zeros(sizes[::-1], dtype=np.uint8)
    truth[4:12, 6:18, 6:18] = 33
    truth_path = write_nrrd(_scratch("truth.seg.nrrd"), truth, spacing,
                            (-11.0, -20.0, 300.0),
                            segments=[("T11 vertebra", 33)])
    # The run's own copy: identical grid, CENTRED origin.
    centred = (-sizes[0] * spacing[0] / 2.0, -sizes[1] * spacing[1] / 2.0,
               -sizes[2] * spacing[2] / 2.0)
    scene_ct = write_nrrd(_scratch("scene/case.nrrd"),
                          np.zeros(sizes[::-1], dtype=np.int16), spacing, centred) \
        if os.path.isdir(_scratch("scene")) else None
    if scene_ct is None:
        os.makedirs(_scratch("scene"))
        scene_ct = write_nrrd(_scratch("scene/case.nrrd"),
                              np.zeros(sizes[::-1], dtype=np.int16), spacing,
                              centred)
    # ...and a decoy on a DIFFERENT grid, exactly as baselineROI.nrrd is.
    write_nrrd(_scratch("scene/baselineROI.nrrd"),
               np.zeros((8, 9, 10), dtype=np.int16), (0.245, 0.245, 0.245),
               (5.0, 5.0, -9.0))

    segmentation = segmentation_io.Segmentation(truth_path)
    try:
        picked, notes = pedicle.scene_volume_matching(
            _scratch("scene"), segmentation._sizes, segmentation.ijk_to_ras)
        check("the scene volume on the ground truth's grid is the one picked",
              picked is not None and os.path.basename(picked) == "case.nrrd")
        check("the resampled baselineROI beside it is NOT picked",
              picked is not None and "baselineROI" not in picked)

        _sizes, scene_matrix = pedicle._grid_of(scene_ct)
        bridge = pedicle.frame_bridge(scene_matrix, segmentation.ijk_to_ras)
        # Voxel (i,j,k) is the same measurement in both files, so the bridge must
        # carry one file's world position of it onto the other's -- for EVERY
        # voxel, which is what makes it a fact rather than a fit.
        worst = 0.0
        for index in ((0, 0, 0), (23, 23, 15), (7, 11, 4), (12, 3, 9)):
            homogeneous = np.array(list(index) + [1.0])
            scene_point = (homogeneous @ scene_matrix.T)[:3]
            truth_point = (homogeneous @ segmentation.ijk_to_ras.T)[:3]
            moved = pedicle.apply_transform(bridge, scene_point)[0]
            worst = max(worst, float(np.linalg.norm(moved - truth_point)))
        check("the bridge carries every voxel's scene position onto its ground-"
              "truth position (worst %.2e mm)" % worst, worst < 1e-9)
        check("and it is a pure translation, the grids being identical",
              np.allclose(bridge[:3, :3], np.eye(3), atol=1e-12))

        # A grid mismatch must be refused, not approximated.
        picked_none, _notes = pedicle.scene_volume_matching(
            _scratch("scene"), [1, 2, 3], segmentation.ijk_to_ras)
        check("a run with no volume on the ground truth's grid is refused",
              picked_none is None)
    finally:
        segmentation.close()

    # ...and the bridge must be NECESSARY. On the real runs, the surgeon's own
    # landmarks must fall inside a vertebra WITH it and outside every vertebra
    # WITHOUT it -- otherwise nothing here is being tested.
    for case in pedicle.discover_cases(EXPERIMENT_ROOT):
        found = pedicle.find_case_files(case)
        if not found["truth"]:
            continue
        label = case["subject"] or case["run"]
        segmentation = segmentation_io.Segmentation(found["truth"])
        try:
            volume = segmentation.layer_volume(0)
            matrix = segmentation.ijk_to_ras
            labels = pedicle.vertebra_labels(segmentation)
            scene_ct, _notes = pedicle.scene_volume_matching(
                case["scene_dir"], segmentation._sizes, matrix)
            _sizes, scene_matrix = pedicle._grid_of(scene_ct)
            bridge = pedicle.frame_bridge(scene_matrix, matrix)
            landmarks = pedicle.read_landmarks(case["scene_dir"])
            bridged, raw = 0, 0
            for point, _site in landmarks["isthmus"].values():
                moved = pedicle.apply_transform(bridge, point)[0]
                if pedicle.assign_level(volume, matrix, labels,
                                        moved)["label"] is not None:
                    bridged += 1
                if pedicle.assign_level(volume, matrix, labels,
                                        point)["label"] is not None:
                    raw += 1
            total = len(landmarks["isthmus"])
            check("%s: every isthmus landmark lands in a vertebra WITH the "
                  "bridge (%d/%d)" % (label, bridged, total), bridged == total)
            check("%s: and NONE of them does without it (%d/%d) -- so the "
                  "bridge is doing the work" % (label, raw, total), raw == 0)
        finally:
            segmentation.close()


# ---------------------------------------------------------------------------
# 2. The LPS mirror
# ---------------------------------------------------------------------------

def check_mirror():
    section("2. The LPS mirror: an un-mirrored plan must be refused")

    for case in pedicle.discover_cases(EXPERIMENT_ROOT):
        found = pedicle.find_case_files(case)
        if not found["truth"]:
            continue
        label = case["subject"] or case["run"]
        plan = pedicle.read_plan(case["scene_dir"])
        segmentation = segmentation_io.Segmentation(found["truth"])
        try:
            volume = segmentation.layer_volume(0)
            matrix = segmentation.ijk_to_ras
            labels = pedicle.vertebra_labels(segmentation)
            scene_ct, _n = pedicle.scene_volume_matching(
                case["scene_dir"], segmentation._sizes, matrix)
            _s, scene_matrix = pedicle._grid_of(scene_ct)
            bridge = pedicle.frame_bridge(scene_matrix, matrix)
            landmarks = pedicle.read_landmarks(case["scene_dir"])

            proper, forward, backward = [], [], []
            for index in sorted(plan["lines"]):
                entry, tip = pedicle.line_endpoints(plan["lines"][index]["file"])
                isthmus = landmarks["isthmus"][index][0]
                vote = pedicle.assign_level(
                    volume, matrix, labels,
                    pedicle.apply_transform(bridge, isthmus)[0])
                field = pedicle.build_field(volume, vote["label"], vote["name"],
                                            matrix, None)
                proper.append(abs(float(field.distance(
                    pedicle.apply_transform(bridge, entry))[0])))
                axis = tip - entry
                axis /= np.linalg.norm(axis)
                forward.append(float(axis[1]))
                # As if `lps_to_ras` had been skipped: the file's own numbers.
                wrong = geometry_io.lps_to_ras(np.vstack([entry, tip]))
                other = wrong[1] - wrong[0]
                other /= np.linalg.norm(other)
                backward.append(float(other[1]))
            check("%s: every entry lands on the vertebra surface, mirrored "
                  "(worst %.2f mm, limit %.0f)"
                  % (label, max(proper), pedicle.ENTRY_SURFACE_LIMIT_MM),
                  max(proper) <= pedicle.ENTRY_SURFACE_LIMIT_MM)
            # The mirror is NOT detectable from the entry alone -- a spine is
            # nearly symmetric about the sagittal plane, so a mirrored screw
            # lands on the contralateral pedicle and still sits on bone (0.1 mm
            # from the surface, on one of these very screws). What is not
            # symmetric is anterior/posterior: the mirror negates A as well as
            # R, so an un-mirrored plan drives every screw out through the back
            # of the patient. That is the property worth checking.
            check("%s: every trajectory runs entry -> tip anteriorly (worst A "
                  "component %+.2f)" % (label, min(forward)),
                  min(forward) > 0.3)
            check("%s: and un-mirrored every one runs posteriorly (worst "
                  "%+.2f) -- backwards through the patient"
                  % (label, max(backward)), max(backward) < -0.3)
        finally:
            segmentation.close()


# ---------------------------------------------------------------------------
# 3. The signed distance field
# ---------------------------------------------------------------------------

def check_distance_field():
    section("3. The zero level set sits on the voxel FACE, not at its centre")

    spacing = (0.5, 0.5, 1.0)                      # deliberately anisotropic
    _volume, matrix, field = box_field(spacing=spacing)
    # The box is i in [20, 40), j in [20, 40), k in [12, 28). A voxel centre is
    # at index*spacing, so the label's own face in +i is at (39 + 0.5) * 0.5.
    face_r = (39.5) * spacing[0]
    centre = np.array([30 * spacing[0], 30 * spacing[1], 20 * spacing[2]])

    probe = np.array([[face_r, centre[1], centre[2]]])
    check("the boundary is at the voxel face (|sdf| = %.3f mm there)"
          % abs(float(field.distance(probe)[0])),
          abs(float(field.distance(probe)[0])) < 0.06)

    # The magnitudes, which is what the half-voxel debias is for. Uncorrected
    # these read 2.25 / 2.25 / 3.25 -- a bias that inflates a breach and, more
    # dangerously, inflates a clearance measured against a 1 mm threshold.
    inside = np.array([[face_r - 2.0, centre[1], centre[2]]])
    outside = np.array([[face_r + 2.0, centre[1], centre[2]]])
    check("2 mm inside reads -2 mm (%.3f)" % field.distance(inside)[0],
          close(field.distance(inside)[0], -2.0, 0.2))
    check("2 mm outside reads +2 mm (%.3f)" % field.distance(outside)[0],
          close(field.distance(outside)[0], 2.0, 0.2))

    # The K axis has twice the spacing. If `sampling` were passed in the wrong
    # order the distances there would be scaled, and only there.
    face_s = (27.5) * spacing[2]
    above = np.array([[centre[0], centre[1], face_s + 3.0]])
    check("3 mm above the box reads +3 mm on the 1.0 mm axis (%.3f)"
          % field.distance(above)[0], close(field.distance(above)[0], 3.0, 0.25))

    # Half a millimetre out is inside the one-voxel transition band, and it is
    # where a clearance flag is decided -- so the band has to stay linear rather
    # than be flattened to zero by the debias.
    near = np.array([[face_r + d, centre[1], centre[2]]
                     for d in (0.25, 0.5, 0.75)])
    read = field.distance(near)
    check("the sub-voxel band stays monotone and roughly true (%s)"
          % ", ".join("%.2f" % v for v in read),
          bool(np.all(np.diff(read) > 0)) and abs(read[1] - 0.5) < 0.25)

    # Cropping must not change an answer. A wider margin is a different crop and
    # therefore a different EDT; the values inside must be identical.
    original = pedicle.SDF_MARGIN_MM
    try:
        pedicle.SDF_MARGIN_MM = 8.0
        _v2, _m2, tight = box_field(spacing=spacing)
        points = np.array([[face_r + d, centre[1], centre[2]]
                           for d in (-4.0, -1.0, 0.0, 1.0, 4.0)])
        gap = float(np.abs(tight.distance(points)
                           - field.distance(points)).max())
        check("a 8 mm crop and a %.0f mm crop agree exactly (%.2e mm)"
              % (original, gap), gap < 1e-9)
    finally:
        pedicle.SDF_MARGIN_MM = original


# ---------------------------------------------------------------------------
# 4. The graded span
# ---------------------------------------------------------------------------

def check_graded_span():
    section("4. The entry funnel is not a breach; a pedicle protrusion is")

    # A slab of "bone" whose surface is oblique to the screw, so the entry disk
    # necessarily pokes out of it -- the real geometry, in miniature.
    spacing = (0.25, 0.25, 0.25)
    size = (240, 240, 160)
    nk, nj, ni = size[2], size[1], size[0]
    ii, jj, kk = np.meshgrid(np.arange(ni), np.arange(nj), np.arange(nk),
                             indexing="ij")
    x = ii * spacing[0]
    y = jj * spacing[1]
    z = kk * spacing[2]
    # Bone occupies y >= the plane through (x=30, y=10) inclined at 40 degrees,
    # and stops at y = 46 (the "anterior cortex").
    plane = 10.0 + np.tan(np.radians(40.0)) * (x - 30.0)
    solid = (y >= plane) & (y <= 46.0) & (x > 12.0) & (x < 48.0) \
        & (z > 8.0) & (z < 32.0)
    volume = np.transpose(solid, (2, 1, 0)).astype(np.uint8)   # -> [k, j, i]

    matrix = np.eye(4)
    matrix[0, 0], matrix[1, 1], matrix[2, 2] = spacing
    field = pedicle.build_field(volume, 1, "T11 vertebra", matrix, None)

    diameter = 5.0
    direction = np.array([0.0, 1.0, 0.0])
    # The entry sits exactly on the inclined surface, as Helper.probeVolume puts
    # it, so the wall around it is half outside by construction.
    entry = np.array([30.0, 10.0, 20.0])
    tip = entry + 30.0 * direction
    isthmus = entry + 15.0 * direction

    row = pedicle.screw_metrics(field, entry, tip, diameter, isthmus,
                               with_density=False)
    check("a screw whose ONLY protrusion is the entry funnel grades A "
          "(breach %.2f mm at %.1f mm, funnel %.2f mm)"
          % (row["breach_mm"], row["breach_offset_mm"],
             row["breach_with_entry_mm"]),
          row["grade"] == "A")
    check("...and the funnel it excluded is reported, not hidden "
          "(breach_proximal_mm %.2f mm)" % (row["breach_proximal_mm"] or 0.0),
          row["breach_proximal_mm"] is not None and row["breach_proximal_mm"] > 0.5)
    check("...and the unrestricted figure keeps it too (%.2f mm)"
          % row["breach_with_entry_mm"], row["breach_with_entry_mm"] > 0.5)

    # Now cut a notch into the lateral wall at the isthmus, 1.6 mm deep. The
    # screw wall is at x = 30 + 2.5 = 32.5, so bone is removed from x >= 30.9.
    notched = solid.copy()
    notch = (x >= 32.5 - 1.6) & (np.abs(y - (entry[1] + 15.0)) <= 2.0)
    notched[notch] = False
    volume2 = np.transpose(notched, (2, 1, 0)).astype(np.uint8)
    field2 = pedicle.build_field(volume2, 1, "T11 vertebra", matrix, None)
    row2 = pedicle.screw_metrics(field2, entry, tip, diameter, isthmus,
                                with_density=False)
    check("a 1.6 mm notch at the isthmus is measured as 1.6 mm (%.2f) and "
          "graded B" % row2["breach_mm"],
          row2["grade"] == "B" and abs(row2["breach_mm"] - 1.6) < 0.35)
    check("...at the isthmus, not at the entry (offset %.1f mm)"
          % row2["breach_offset_mm"], abs(row2["breach_offset_mm"] - 15.0) < 2.5)
    check("...and breach_isthmus_mm sees the same notch (%.2f mm)"
          % (row2["breach_isthmus_mm"] or 0.0),
          row2["breach_isthmus_mm"] is not None
          and abs(row2["breach_isthmus_mm"] - 1.6) < 0.35)
    check("...and the intact screw beside it is still A",
          row["grade"] == "A")

    # The tip cap is graded: a screw driven out the front must not read A.
    long_tip = entry + 40.0 * direction                       # past y = 46
    row3 = pedicle.screw_metrics(field, entry, long_tip, diameter, isthmus,
                                with_density=False)
    check("a screw out the anterior cortex is named an ANTERIOR breach "
          "(%.2f mm, %s) -- its wall and its tip cap protrude by the same "
          "amount there, so only the field's own gradient can say which way"
          % (row3["breach_mm"], row3["breach_direction"]),
          row3["breach_mm"] > 3.0 and row3["breach_direction"] == "anterior")
    check("...and its tip_to_cortex_mm is negative (%.2f mm)"
          % (row3["tip_to_cortex_mm"] or 0.0),
          row3["tip_to_cortex_mm"] is not None and row3["tip_to_cortex_mm"] < 0)


# ---------------------------------------------------------------------------
# 5. Medial is derived, never named
# ---------------------------------------------------------------------------

def check_side_and_medial():
    section("5. The side comes from the anatomy; the plan's _L/_R does not")

    right = pedicle.anatomic_directions(True)
    left = pedicle.anatomic_directions(False)
    check("medial points toward -R for a right-side screw",
          np.allclose(right["medial"], [-1, 0, 0]))
    check("medial points toward +R for a left-side screw",
          np.allclose(left["medial"], [1, 0, 0]))
    check("medial and lateral are opposite in both",
          np.allclose(right["medial"], -right["lateral"])
          and np.allclose(left["medial"], -left["lateral"]))

    for case in pedicle.discover_cases(EXPERIMENT_ROOT):
        found = pedicle.find_case_files(case)
        if not found["truth"]:
            continue
        label = case["subject"] or case["run"]
        segmentation = segmentation_io.Segmentation(found["truth"])
        try:
            volume = segmentation.layer_volume(0)
            matrix = segmentation.ijk_to_ras
            labels = pedicle.vertebra_labels(segmentation)
            cords = [s for s in segmentation.segments if s.name == "spinal cord"]
            if not cords:
                check("%s: the ground truth names a spinal cord to check "
                      "medial against" % label, False)
                continue
            cord = segmentation_io.measure_segment(segmentation, cords[0],
                                                   with_surface=False)
            scene_ct, _n = pedicle.scene_volume_matching(
                case["scene_dir"], segmentation._sizes, matrix)
            _s, scene_matrix = pedicle._grid_of(scene_ct)
            bridge = pedicle.frame_bridge(scene_matrix, matrix)
            plan = pedicle.read_plan(case["scene_dir"])
            landmarks = pedicle.read_landmarks(case["scene_dir"])

            toward_cord = []
            inverted_names = 0
            for index in sorted(plan["lines"]):
                entry, tip = pedicle.line_endpoints(plan["lines"][index]["file"])
                entry = pedicle.apply_transform(bridge, entry)[0]
                isthmus_scene, site = landmarks["isthmus"][index]
                isthmus = pedicle.apply_transform(bridge, isthmus_scene)[0]
                vote = pedicle.assign_level(volume, matrix, labels, isthmus)
                field = pedicle.build_field(volume, vote["label"], vote["name"],
                                            matrix, None)
                is_right = bool(entry[0] > field.centroid[0])
                medial = pedicle.anatomic_directions(is_right)["medial"]
                to_cord = cord["centroid"] - isthmus
                to_cord /= np.linalg.norm(to_cord)
                toward_cord.append(float(medial @ to_cord))
                if site.endswith("_L") and is_right:
                    inverted_names += 1
                if site.endswith("_R") and not is_right:
                    inverted_names += 1
            check("%s: 'medial' points toward the ground truth's own spinal "
                  "cord for every screw (worst dot %.2f)"
                  % (label, min(toward_cord)), min(toward_cord) > 0.0)
            check("%s: and the plan's _L/_R suffix disagrees with the anatomy "
                  "on %d of %d screws -- which is why it is never used"
                  % (label, inverted_names, len(plan["lines"])),
                  inverted_names == len(plan["lines"]))
        finally:
            segmentation.close()


# ---------------------------------------------------------------------------
# 6. The level comes from the landmark
# ---------------------------------------------------------------------------

def check_level_assignment():
    section("6. The vertebra is chosen by the landmark, never by the name")

    spacing = (0.5, 0.5, 1.0)
    size = (64, 64, 48)
    volume = np.zeros((size[2], size[1], size[0]), dtype=np.uint8)
    volume[6:20, 20:44, 20:44] = 33                          # "T11", lower k
    volume[22:40, 20:44, 20:44] = 31                         # "L1", upper k
    matrix = np.eye(4)
    matrix[0, 0], matrix[1, 1], matrix[2, 2] = spacing
    labels = {33: "T11 vertebra", 31: "L1 vertebra"}

    def at(i, j, k):
        return (np.array([i, j, k, 1.0]) @ matrix.T)[:3]

    inside = pedicle.assign_level(volume, matrix, labels, at(32, 32, 12))
    check("a landmark inside T11 resolves to T11",
          inside["name"] == "T11 vertebra" and inside["margin"] == 1.0)

    # The real failure: an isthmus landmark one voxel OUTSIDE the label. A point
    # probe reports no vertebra at all; one real screw of run 1_304 is here.
    just_out = pedicle.assign_level(volume, matrix, labels, at(19, 32, 12))
    check("a landmark one voxel outside the label still resolves (support "
          "%.2f, margin %.2f)" % (just_out["support"], just_out["margin"]),
          just_out["name"] == "T11 vertebra")
    check("...and the ball is what does it: the voxel under the point is "
          "background", int(volume[12, 32, 19]) == 0)

    # Between the two vertebrae the vote must be refused rather than split.
    between = pedicle.assign_level(volume, matrix, labels, at(32, 32, 21))
    check("a landmark between two vertebrae is flagged ambiguous, on the "
          "MARGIN and not on a voxel count (%s)" % (between["note"] or "no note"),
          bool(between["note"])
          and between["voxels"] >= pedicle.LANDMARK_MIN_VOXELS
          and between["margin"] < pedicle.LANDMARK_MIN_MARGIN)

    away = pedicle.assign_level(volume, matrix, labels, at(2, 2, 2))
    check("a landmark nowhere near the spine resolves to nothing",
          away["label"] is None)

    # And the name must never decide. `_levels_match` REPORTS the disagreement.
    check("a plan naming T12 for a landmark in T11 is reported as a mismatch",
          pedicle._levels_match("T12_L", "T11 vertebra") is False)
    check("...and the matching case is reported as agreement",
          pedicle._levels_match("T11_L", "T11 vertebra") is True)
    check("...and a site with no level in it yields no verdict, not a False",
          pedicle._levels_match("", "T11 vertebra") is None)


# ---------------------------------------------------------------------------
# 7. The real runs
# ---------------------------------------------------------------------------

#: What the two saved runs measure, as of the reference sweep. Ranges rather
#: than exact values: a parameter here is a stated choice and may be retuned,
#: but the ORDER of these numbers is a fact about the plans and must not move.
REFERENCE = {
    ("1_304", "T11_L"): {"level": "T11 vertebra", "side": "right", "grade": "B"},
    ("1_304", "T11_R"): {"level": "T11 vertebra", "side": "left", "grade": "A"},
    ("1_304", "L1_L"): {"level": "L1 vertebra", "side": "right", "grade": "B"},
    ("1_304", "L1_R"): {"level": "L1 vertebra", "side": "left", "grade": "B"},
    ("3", "T11_L"): {"level": "T11 vertebra", "side": "right", "grade": "A"},
    ("3", "T11_R"): {"level": "T11 vertebra", "side": "left", "grade": "B"},
    ("3", "L1_L"): {"level": "L1 vertebra", "side": "right", "grade": "B"},
    ("3", "L1_R"): {"level": "L1 vertebra", "side": "left", "grade": "A"},
}


def check_real_runs():
    section("7. The two saved runs, end to end")

    report = pedicle.build_report(EXPERIMENT_ROOT)
    for line in report["log"]:
        print("      " + line)
    rows = report["rows"]
    check("both runs were analysed", report["analysed"] == 2
          and not report["failed_cases"])
    check("eight screws, all scored", len(rows) == 8
          and all(row.get("grade") for row in rows))

    for row in rows:
        key = (row["case"], row["site"])
        want = REFERENCE.get(key)
        if want is None:
            check("%s/%s is a screw the reference knows about" % key, False)
            continue
        check("%s/%s -> %s, %s side, grade %s (breach %.2f mm %s at %.1f mm)"
              % (key[0], key[1], row["level"], row["side"], row["grade"],
                 row["breach_mm"], row["breach_direction"],
                 row["breach_offset_mm"]),
              row["level"] == want["level"] and row["side"] == want["side"]
              and row["grade"] == want["grade"])

    # Invariants that must hold for every screw whatever the parameters are.
    for row in rows:
        tag = "%s/%s" % (row["case"], row["site"])
        check("%s: the entry lands on the cortex (%.2f mm) -- the bridge witness"
              % (tag, row["entry_on_surface_mm"]),
              row["entry_on_surface_mm"] <= 2.0)
        check("%s: its trajectory line and its screw cylinder are the same "
              "object (%.4f mm apart)" % (tag, row["model_axis_gap_mm"]),
              row["model_axis_gap_mm"] < 1e-3)
        check("%s: the landmark names one vertebra outright (margin %.0f%%)"
              % (tag, row["level_margin_pct"]), row["level_margin_pct"] == 100.0)
        check("%s: the level's anterior landmark agrees" % tag,
              row.get("level_confirmed") is True)
        check("%s: the graded span starts inside the screw and past the entry "
              "(%.1f of %.0f mm)" % (tag, row["graded_from_mm"],
                                     row["length_mm"]),
              row["diameter_mm"] / 2.0 <= row["graded_from_mm"]
              < row["length_mm"])
        check("%s: min_clearance is the breach with its sign flipped" % tag,
              close(row["min_clearance_mm"], -row["breach_mm"], 1e-9))
        check("%s: the isthmus breach cannot exceed the graded one "
              "(%.2f <= %.2f)" % (tag, row["breach_isthmus_mm"],
                                  row["breach_mm"]),
              row["breach_isthmus_mm"] <= row["breach_mm"] + 1e-9)
        check("%s: the unrestricted breach is the largest of the three "
              "(%.2f)" % (tag, row["breach_with_entry_mm"]),
              row["breach_with_entry_mm"] >= row["breach_mm"] - 1e-9)
        check("%s: the tip clears the anterior cortex by %.1f mm and the screw "
              "covers %.0f%% of the depth"
              % (tag, row["tip_to_cortex_mm"], row["length_of_depth_pct"]),
              row["tip_to_cortex_mm"] > 0
              and 40.0 < row["length_of_depth_pct"] < 100.0)
        check("%s: the two width measures agree within 4 mm (%.2f caliper, "
              "%.2f chord)" % (tag, row["pedicle_width_mm"],
                               row["channel_width_mm"]),
              abs(row["pedicle_width_mm"] - row["channel_width_mm"]) < 4.0)
        check("%s: containment is between 80%% and 100%% (%.1f)"
              % (tag, row["containment_pct"]),
              80.0 <= row["containment_pct"] <= 100.0)
        check("%s: path HU is read from the CT, in bone (%s)"
              % (tag, row["path_hu"]),
              isinstance(row["path_hu"], float) and 0.0 < row["path_hu"] < 600.0)
        check("%s: contact area is a share of the lateral surface "
              "(%.0f of %.0f mm2)" % (tag, row["contact_mm2_ge250"],
                                      row["surface_mm2"]),
              0.0 <= row["contact_mm2_ge250"] <= row["surface_mm2"] + 1e-6)

    # The finding this analysis exists to surface, on real data.
    oversized = [r for r in rows if (r.get("fill_ratio_pct") or 0) > 100.0]
    check("the one screw wider than the pedicle it is in is found (%s) and it "
          "is also the worst breach"
          % ", ".join("%s/%s %.0f%%" % (r["case"], r["site"],
                                        r["fill_ratio_pct"])
                      for r in oversized),
          len(oversized) == 1
          and oversized[0]["breach_mm"] == max(r["breach_mm"] for r in rows))

    levels = report["levels"]
    check("four instrumented levels, two per run, each with two screws",
          len(levels) == 4 and all(lv["screws"] == 2 for lv in levels))
    check("every level has a left/right symmetry angle",
          all(lv.get("symmetry_deg") is not None for lv in levels))
    check("every level has a trabecular HU from a non-empty body ROI",
          all(lv.get("trabecular_hu") is not None
              and lv.get("trabecular_voxels", 0) > 1000 for lv in levels))

    # Density off must change ONLY the density columns.
    plain = pedicle.build_report(EXPERIMENT_ROOT, with_density=False)
    positional = ("breach_mm", "grade", "containment_pct", "pedicle_width_mm",
                  "fill_ratio_pct", "tip_to_cortex_mm", "medial_clearance_mm",
                  "side", "level")
    same = all(a.get(key) == b.get(key)
               for a, b in zip(rows, plain["rows"]) for key in positional)
    check("with the CT unread, every positional measure is identical", same)
    check("...and the density columns are then blank",
          all(row.get("path_hu") is None for row in plain["rows"]))

    # The workbook itself.
    sheets = dict((title, blocks) for title, blocks in report["sheets"])
    check("the workbook has a Screw accuracy sheet and a Timing sheet",
          "Screw accuracy" in sheets and len(report["sheets"]) == 2)
    columns = set()
    for _caption, names, _rows in sheets["Screw accuracy"]:
        columns.update(names)
    missing = [key for row in rows for key in row
               if key not in columns and key != "level_note"]
    check("every measured column reaches the sheet (%s)"
          % (", ".join(sorted(set(missing))[:6]) or "none"), not missing)

    defined = set()
    for caption, names, block in sheets["Screw accuracy"]:
        if names == pedicle.DEFINITION_COLUMNS:
            defined.update(row["term"] for row in block)
    described = " ".join(defined)
    undocumented = [name for name in pedicle.SCREW_COLUMNS
                    if name not in described and name not in
                    ("case", "run", "screw", "site")]
    check("every per-screw column is named in a definition (%s)"
          % (", ".join(undocumented[:6]) or "none"), not undocumented)
    return report


# ---------------------------------------------------------------------------
# 8. The phase map
# ---------------------------------------------------------------------------

def check_phase_map(report):
    section("8. The timing phases against the installed workflow.json")

    path = os.path.join(ROOT, "Resources", "extension_CLI", "PedicleScrewPlanner",
                        "workflow.json")
    if not os.path.isfile(path):
        check("the installed CLI package has a workflow.json", False)
        return
    graph = json.load(io.open(path, encoding="utf-8"))
    steps = graph.get("steps") if isinstance(graph, dict) else graph
    ids = [pedicle.canonical_step_id(str(step.get("step_id")))
           for step in steps if step.get("step_id")]
    mapped = set(pedicle._PHASE_OF_STEP)
    missing = [step for step in ids if step not in mapped]
    extra = [step for step in mapped if step not in ids]
    check("every step of the installed workflow is in a phase (%s)"
          % (", ".join(missing[:6]) or "none"), not missing)
    check("and every phased step still exists in it (%s)"
          % (", ".join(sorted(extra)[:6]) or "none"), not extra)
    check("the phases are disjoint",
          sum(len(v) for v in pedicle.PHASE_STEPS.values()) == len(mapped))

    for row in report["phase_rows"]:
        check("%s: no step fell outside the phases (%.2f s unphased)"
              % (row["case"], row.get("unphased_s") or 0.0),
              (row.get("unphased_s") or 0.0) == 0.0)
        residual = row.get("phase_residual_s")
        check("%s: the phases sum to the time inside the steps (residual "
              "%.2f s)" % (row["case"], residual or 0.0),
              residual is not None and abs(residual) < 0.5)
        check("%s: t3 -- planning the screws -- is the largest phase (%.1f s)"
              % (row["case"], row.get("t3_s") or 0.0),
              (row.get("t3_s") or 0.0) == max(row.get("%s_s" % p) or 0.0
                                              for p in pedicle.PHASE_ORDER))


# ---------------------------------------------------------------------------
# 9. Read-only
# ---------------------------------------------------------------------------

_WRITERS = {"remove", "unlink", "rmtree", "rename", "replace", "rmdir",
            "makedirs", "mkdir", "write_text", "write_bytes", "truncate",
            "save", "saveNode", "saveScene", "copyfile", "copytree"}


def check_read_only():
    section("9. The analysis writes nothing but its workbook")

    path = os.path.join(ROOT, "SlicerAIAgentLib", "experiments", "pedicle.py")
    tree = ast.parse(io.open(path, encoding="utf-8").read())
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = ""
            if isinstance(node.func, ast.Attribute):
                name = node.func.attr
            elif isinstance(node.func, ast.Name):
                name = node.func.id
            if name in _WRITERS or (name == "open" and len(node.args) > 1):
                offenders.append("%s (line %d)" % (name, node.lineno))
    check("no write, delete, move or save anywhere in pedicle.py (%s)"
          % (", ".join(offenders[:6]) or "none"), not offenders)

    # The one thing that DOES write is the workbook, and it is written by
    # workbook.write_workbook from run_analysis -- not by any measurement.
    source = io.open(path, encoding="utf-8").read()
    check("the only writer is workbook.write_workbook, reached from "
          "run_analysis", source.count("write_workbook") == 2
          and "def run_analysis" in source)


# ---------------------------------------------------------------------------

def main():
    if os.path.isdir(SCRATCH):
        shutil.rmtree(SCRATCH)
    try:
        check_bridge()
        check_mirror()
        check_distance_field()
        check_graded_span()
        check_side_and_medial()
        check_level_assignment()
        report = check_real_runs()
        check_phase_map(report)
        check_read_only()
    finally:
        if os.path.isdir(SCRATCH):
            shutil.rmtree(SCRATCH, ignore_errors=True)

    print("")
    print("=" * 78)
    if FAILURES:
        print("%d CHECK(S) FAILED" % len(FAILURES))
        for item in FAILURES:
            print("  - " + item)
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
