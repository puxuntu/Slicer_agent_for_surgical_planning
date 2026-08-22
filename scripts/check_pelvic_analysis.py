"""Check the PelvicFracturePlanning analysis outside Slicer.

``pelvic.py`` and ``segmentation_io.py`` import neither ``slicer`` nor ``vtk``,
so this runs the WHOLE analysis -- the transforms-file reader, the layered
``.seg.nrrd`` reader, the surface extraction and the timing phase split --
against the real saved runs.

The analysis READS the reduction error out of each run's
``Ground truth*.transforms.json`` rather than estimating it, so what has to be
proved here is different from what an estimator would need. Five failure modes,
none of which raises and none of which looks wrong:

* **A record that does not describe the files beside it.** This is the one real
  hazard of reading a number instead of measuring it: a recorded transform
  measures whatever was on disk *when it was written*, and a ground truth
  re-annotated afterwards leaves it silently stale. (It happened during
  development: an earlier ground truth gave 5.83 deg where the record says
  2.25.) Section 4 checks that applying the record to the saved reduction lands
  on the saved ground truth, and section 5 requires that check to actually
  REFUSE a record from another case rather than merely reporting it.
* **A record that does not agree with itself.** Section 3 corrupts one field at
  a time -- a reflection instead of a rotation, a wrong angle, a wrong axis,
  centroids the matrix does not connect -- and requires each to be caught.
* **The layer axis.** A ``.seg.nrrd`` with overlapping segments is 4-D, and its
  LAYER axis is the first of ``sizes:`` and therefore the LAST array index.
  Indexing ``array[layer]`` is in bounds, is the right dtype, and quietly
  returns a slab of the volume instead of a layer of it. Section 1 builds a file
  whose two layers carry the SAME label value over different boxes, so the wrong
  indexing cannot come out right by accident.
* **The slab halo.** The surface is extracted in slabs to bound memory, and a
  missing one-plane halo turns every slab boundary into a false surface --
  a denser cloud and a plausible, slightly worse residual. Section 2 requires
  the identical surface at four slab sizes.
* **A renumbered workflow.** ``PHASE_STEPS`` maps cookbook steps to the
  extension's five stages. If the CLI package is regenerated with different step
  ids, the phases silently shrink while still summing to something plausible.
  Section 7 checks the map against the installed ``workflow.json`` itself.

    python scripts/check_pelvic_analysis.py
"""

import ast
import copy
import io
import json
import os
import sys
import types
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

for _name in ("slicer", "qt", "vtk", "ctk"):
    sys.modules.setdefault(_name, types.ModuleType(_name))
sys.modules["slicer"].util = types.ModuleType("slicer.util")

import numpy as np                                            # noqa: E402

from SlicerAIAgentLib.experiments import pelvic               # noqa: E402
from SlicerAIAgentLib.experiments import segmentation_io      # noqa: E402

FAILURES = []

EXPERIMENT_ROOT = os.path.join(ROOT, pelvic.EXPERIMENT_DIR)
SCRATCH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "_check_pelvic_tmp")


def check(label, condition):
    print(("PASS  " if condition else "FAIL  ") + label)
    if not condition:
        FAILURES.append(label)


def close(a, b, tol=1e-6):
    return a is not None and abs(float(a) - float(b)) <= tol


def _scratch(name):
    if not os.path.isdir(SCRATCH):
        os.makedirs(SCRATCH)
    return os.path.join(SCRATCH, name)


def _raises(function):
    try:
        function()
    except Exception:                                  # noqa: BLE001
        return True
    return False


def _rotation(axis, degrees):
    axis = np.asarray(axis, dtype=np.float64)
    axis = axis / np.linalg.norm(axis)
    angle = np.radians(degrees)
    cross = np.array([[0.0, -axis[2], axis[1]],
                      [axis[2], 0.0, -axis[0]],
                      [-axis[1], axis[0], 0.0]])
    return np.eye(3) + np.sin(angle) * cross + (1 - np.cos(angle)) * (cross @ cross)


# ---------------------------------------------------------------------------
# Writing files whose answer is known by construction
# ---------------------------------------------------------------------------

def _write_seg(path, array, segments, spacing=1.0, origin=(0.0, 0.0, 0.0),
               space="left-posterior-superior", encoding="gzip", truncate=0,
               kinds=None):
    """A real .seg.nrrd. ``array`` is ``(nk, nj, ni)`` or ``(nk, nj, ni, layers)``.

    ``segments`` is a list of ``(name, layer, label)``.
    """
    dimension = array.ndim
    if dimension == 4:
        sizes = [array.shape[3], array.shape[2], array.shape[1], array.shape[0]]
        default_kinds = "list domain domain domain"
        directions = ("none (%g,0,0) (0,%g,0) (0,0,%g)"
                      % (spacing, spacing, spacing))
    else:
        sizes = [array.shape[2], array.shape[1], array.shape[0]]
        default_kinds = "domain domain domain"
        directions = "(%g,0,0) (0,%g,0) (0,0,%g)" % (spacing, spacing, spacing)

    header = ["NRRD0004", "type: unsigned char",
              "dimension: %d" % dimension,
              "space: %s" % space,
              "sizes: " + " ".join(str(n) for n in sizes),
              "space directions: " + directions,
              "kinds: " + (kinds or default_kinds),
              "encoding: " + encoding,
              "space origin: (%g,%g,%g)" % tuple(origin)]
    for index, (name, layer, label) in enumerate(segments):
        header.append("Segment%d_Name:=%s" % (index, name))
        header.append("Segment%d_Layer:=%d" % (index, layer))
        header.append("Segment%d_LabelValue:=%d" % (index, label))
    blob = np.ascontiguousarray(array, dtype=np.uint8).tobytes()
    if encoding == "gzip":
        engine = zlib.compressobj(6, zlib.DEFLATED, 16 + zlib.MAX_WBITS)
        blob = engine.compress(blob) + engine.flush()
    if truncate:
        blob = blob[:-truncate]
    with open(path, "wb") as handle:
        handle.write(("\n".join(header) + "\n\n").encode("utf-8"))
        handle.write(blob)
    return path


def _piece(name, rotation, translation, centroid):
    """One ``pieces`` entry, internally consistent by construction."""
    matrix = np.eye(4)
    matrix[:3, :3] = rotation
    matrix[:3, 3] = translation
    annotated = rotation @ np.asarray(centroid, float) + np.asarray(translation, float)
    degrees, axis = pelvic.rotation_angle_axis(rotation)
    moved = annotated - np.asarray(centroid, float)
    return {
        "name": name,
        "translation_mm": [round(float(v), 4) for v in moved],
        "translation_magnitude_mm": round(float(np.linalg.norm(moved)), 4),
        "centroid_reduced_mm": [round(float(v), 4) for v in centroid],
        "centroid_annotated_mm": [round(float(v), 4) for v in annotated],
        "matrix": [[round(float(v), 9) for v in row] for row in matrix],
        "rotation_angle_deg": round(degrees, 4),
        "rotation_axis": [round(float(v), 6) for v in axis],
        "rotation_euler_deg": [0.0, 0.0, 0.0],
    }


def _write_record(path, pieces, segmentation="Ground truth.seg.nrrd",
                  reduction="Fragment Reduction"):
    document = {"segmentation": segmentation, "reduction": reduction,
                "convention": "RAS millimetres.", "pieces": pieces}
    with io.open(path, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(document, indent=2))
    return path


def _lumpy_blob(shape=(64, 60, 56)):
    """A bumpy, asymmetric solid -- the union of spheres of different radii.

    A bone-like shape rather than a box or an ellipsoid, so a transform applied
    to it and then checked against it cannot be satisfied by the shape sliding
    on itself.
    """
    nk, nj, ni = shape
    k, j, i = np.mgrid[0:nk, 0:nj, 0:ni].astype(float)
    solid = np.zeros(shape, dtype=bool)
    for ci, cj, ck, radius in ((28, 30, 32, 14), (18, 22, 20, 9), (38, 40, 44, 10),
                               (20, 40, 42, 7), (40, 20, 18, 8), (30, 18, 46, 6),
                               (14, 34, 40, 5)):
        solid |= ((i - ci) ** 2 + (j - cj) ** 2 + (k - ck) ** 2) <= radius * radius
    return solid.astype(np.uint8)


# ---------------------------------------------------------------------------
# 1. The .seg.nrrd reader: layers, frames, encodings
# ---------------------------------------------------------------------------

def check_reader():
    # Two layers, the SAME label value in both, over DIFFERENT boxes. Indexing
    # the layer as the first array axis would still return an array of the right
    # dtype and would mix the two boxes together.
    array = np.zeros((20, 18, 16, 2), dtype=np.uint8)
    array[2:6, 2:6, 2:6, 0] = 1                        # layer 0: 4x4x4 = 64
    array[10:16, 8:14, 6:10, 1] = 1                    # layer 1: 6x6x4 = 144
    path = _write_seg(_scratch("two_layers.seg.nrrd"), array,
                      [("Alpha", 0, 1), ("Beta", 1, 1)])

    with segmentation_io.Segmentation(path) as seg:
        check("a 4-D segmentation reports its layer count", seg.layers == 2)
        check("its segments are read by name",
              sorted(seg.names()) == ["Alpha", "Beta"])
        table = seg.by_name()
        alpha = segmentation_io.measure_segment(seg, table["alpha"])
        beta = segmentation_io.measure_segment(seg, table["beta"])
        check("layer 0's segment holds only its own voxels (64)",
              alpha["voxels"] == 64)
        check("layer 1's segment holds only its own voxels (144) despite sharing "
              "the label value", beta["voxels"] == 144)
        # LPS: i and j are negated, k is not. The box spans i=2..5, so its
        # centroid index is 3.5 and its RAS r is -3.5.
        check("LPS->RAS negates i and j and leaves k",
              np.allclose(alpha["centroid"], [-3.5, -3.5, 3.5]))

    # The same content, uncompressed, must read identically -- and the raw path
    # maps the file itself rather than owning a temp copy.
    raw = _write_seg(_scratch("two_layers_raw.seg.nrrd"), array,
                     [("Alpha", 0, 1), ("Beta", 1, 1)], encoding="raw")
    with segmentation_io.Segmentation(raw) as seg:
        again = segmentation_io.measure_segment(seg, seg.by_name()["beta"])
    check("an uncompressed file reads the same as a gzipped one",
          again["voxels"] == 144)

    # A 3-D segmentation is the single-layer case and must work unchanged.
    flat = np.zeros((12, 12, 12), dtype=np.uint8)
    flat[3:9, 3:9, 3:9] = 2
    path3 = _write_seg(_scratch("flat.seg.nrrd"), flat, [("Solo", 0, 2)])
    with segmentation_io.Segmentation(path3) as seg:
        solo = segmentation_io.measure_segment(seg, seg.by_name()["solo"])
    check("a 3-D (single-layer) segmentation reads", solo["voxels"] == 216)

    # RAS in the header means no flip at all.
    ras = _write_seg(_scratch("ras.seg.nrrd"), flat, [("Solo", 0, 2)],
                     space="right-anterior-superior")
    with segmentation_io.Segmentation(ras) as seg:
        centroid = segmentation_io.measure_segment(
            seg, seg.by_name()["solo"])["centroid"]
    check("a RAS file is not flipped", np.allclose(centroid, [5.5, 5.5, 5.5]))

    # The memmap path: force it, and require the temp file to be gone on close.
    limit = segmentation_io.INLINE_LIMIT_BYTES
    segmentation_io.INLINE_LIMIT_BYTES = 1
    try:
        seg = segmentation_io.Segmentation(path)
        mapped = segmentation_io.measure_segment(seg, seg.by_name()["beta"])
        temp = seg._temp_path                          # noqa: SLF001
        existed = bool(temp) and os.path.isfile(temp)
        seg.close()
        check("the memmap path gives the same voxel count as the inline one",
              mapped["voxels"] == 144)
        check("it decompresses to a temp file", existed)
        check("and close() removes it", existed and not os.path.isfile(temp))
    finally:
        segmentation_io.INLINE_LIMIT_BYTES = limit

    # What must raise, rather than be read as something plausible.
    bad_kinds = _write_seg(_scratch("bad_kinds.seg.nrrd"), array,
                           [("Alpha", 0, 1)],
                           kinds="domain domain domain list")
    check("a 4-D file whose layer axis is not first is REFUSED",
          _raises(lambda: segmentation_io.Segmentation(bad_kinds)))

    short = _write_seg(_scratch("short.seg.nrrd"), array, [("Alpha", 0, 1)],
                       truncate=64)
    check("a truncated payload is REFUSED",
          _raises(lambda: _measure_first(short)))

    unknown = _write_seg(_scratch("unknown_space.seg.nrrd"), flat,
                         [("Solo", 0, 2)], space="scanner-xyz")
    check("an unhandled anatomical space is REFUSED",
          _raises(lambda: segmentation_io.Segmentation(unknown)))


def _measure_first(path):
    with segmentation_io.Segmentation(path) as seg:
        return segmentation_io.measure_segment(seg, seg.segments[0])


# ---------------------------------------------------------------------------
# 2. Surface extraction, and the slab halo
# ---------------------------------------------------------------------------

def check_surface():
    size, span = 24, 10
    array = np.zeros((size, size, size), dtype=np.uint8)
    array[5:5 + span, 5:5 + span, 5:5 + span] = 1
    path = _write_seg(_scratch("cube.seg.nrrd"), array, [("Cube", 0, 1)])

    expected = span ** 3 - (span - 2) ** 3             # the shell of the cube
    reference = None
    consistent = True
    for slab in (1 << 20, 4096, 512, 64):
        with segmentation_io.Segmentation(path) as seg:
            measured = segmentation_io.measure_segment(seg, seg.segments[0],
                                                       slab_bytes=slab)
        points = measured["surface"]
        order = np.lexsort((points[:, 2], points[:, 1], points[:, 0]))
        points = points[order]
        if reference is None:
            reference = points
            check("a solid cube's surface is exactly its shell (%d voxels)"
                  % expected, len(points) == expected)
            check("its volume is the cube (%d voxels)" % span ** 3,
                  measured["voxels"] == span ** 3)
        elif points.shape != reference.shape or not np.allclose(points, reference):
            consistent = False
    check("the surface is identical at every slab size (the one-plane halo)",
          consistent)

    # with_surface=False is the cheap path for an unannotated segment: same size,
    # no shape.
    with segmentation_io.Segmentation(path) as seg:
        cheap = segmentation_io.measure_segment(seg, seg.segments[0],
                                                with_surface=False)
    check("with_surface=False keeps the volume and drops the surface",
          cheap["voxels"] == span ** 3 and len(cheap["surface"]) == 0)


# ---------------------------------------------------------------------------
# 3. The record, judged against ITSELF
# ---------------------------------------------------------------------------

def check_record_consistency():
    rotation = _rotation([0.2, 0.9, -0.35], 6.0)
    translation = np.array([2.0, -1.25, 3.5])
    centroid = np.array([30.0, -12.0, 44.0])
    good = _piece("Blob", rotation, translation, centroid)

    check("a well-formed record has no problems", not pelvic.record_problems(
        _parsed(good)))

    degrees, axis = pelvic.rotation_angle_axis(rotation)
    check("the rotation this module reads out of a matrix is the one put in",
          close(degrees, 6.0, 1e-9))
    check("and so is its axis",
          np.allclose(axis, np.array([0.2, 0.9, -0.35])
                      / np.linalg.norm([0.2, 0.9, -0.35])))
    check("the identity is 0 deg with no axis",
          close(pelvic.rotation_angle_axis(np.eye(3))[0], 0.0, 1e-9))

    # One corrupted field at a time. Each of these leaves a record that still
    # parses, still has a 4x4 matrix, and still reports a plausible displacement.
    def corrupted(mutate, label):
        broken = copy.deepcopy(good)
        mutate(broken)
        problems = pelvic.record_problems(_parsed(broken))
        check(label, bool(problems))
        return problems

    corrupted(lambda p: p.update(rotation_angle_deg=3.0),
              "a rotation_angle_deg the matrix does not encode is caught")
    corrupted(lambda p: p.update(rotation_axis=[1.0, 0.0, 0.0]),
              "a rotation_axis the matrix does not encode is caught")
    corrupted(lambda p: p.update(centroid_annotated_mm=[0.0, 0.0, 0.0]),
              "centroids the matrix does not connect are caught")
    corrupted(lambda p: p.update(translation_magnitude_mm=9.9),
              "a translation_magnitude_mm that is not |translation_mm| is caught")
    corrupted(lambda p: p.update(translation_mm=[0.0, 0.0, 0.0]),
              "a translation_mm that is not the centroid displacement is caught")

    # A reflection: the one corruption that would still map points onto points,
    # and out of which rotation_angle_axis would still read an angle.
    def mirror(piece):
        matrix = np.asarray(piece["matrix"], float)
        matrix[:3, :3] = matrix[:3, :3] @ np.diag([1.0, 1.0, -1.0])
        piece["matrix"] = matrix.tolist()
    problems = corrupted(mirror, "a reflection in the matrix is caught")
    check("and it is named as a reflection, not as a rounding error",
          any("reflection" in text or "orthonormal" in text for text in problems))

    corrupted(lambda p: p.update(translation_magnitude_mm=250.0,
                                 translation_mm=[250.0, 0.0, 0.0],
                                 centroid_annotated_mm=[280.0, -12.0, 44.0]),
              "an implausibly large displacement is caught")

    # And what must RAISE rather than be scored.
    empty = _write_record(_scratch("empty.transforms.json"), [])
    check("a record naming no pieces is REFUSED",
          _raises(lambda: pelvic.read_transform_record(empty)))
    nameless = _write_record(_scratch("nameless.transforms.json"),
                             [{"matrix": np.eye(4).tolist()}])
    check("a piece with no name is REFUSED",
          _raises(lambda: pelvic.read_transform_record(nameless)))
    shapeless = _write_record(_scratch("shapeless.transforms.json"),
                              [{"name": "Blob", "matrix": [[1, 0], [0, 1]]}])
    check("a piece whose matrix is not 4x4 is REFUSED",
          _raises(lambda: pelvic.read_transform_record(shapeless)))

    # A round trip through the reader must preserve the numbers exactly -- this
    # module's whole claim is that it reads rather than derives.
    path = _write_record(_scratch("good.transforms.json"), [good])
    piece = pelvic.read_transform_record(path)["pieces"][0]
    row = pelvic._transform_row("case", "run", piece)          # noqa: SLF001
    check("displacement_mm is the record's own translation_magnitude_mm",
          close(row["displacement_mm"], good["translation_magnitude_mm"], 0.0))
    check("rotation_deg is the record's own rotation_angle_deg",
          close(row["rotation_deg"], good["rotation_angle_deg"], 0.0))
    check("the RAS components are the record's own translation_mm",
          [row["disp_r_mm"], row["disp_a_mm"], row["disp_s_mm"]]
          == [round(v, 4) for v in good["translation_mm"]])


def _parsed(piece):
    """One raw piece dict, given the parsed fields read_transform_record adds."""
    matrix = np.asarray(piece["matrix"], dtype=np.float64)
    return dict(piece, matrix=matrix, rotation=matrix[:3, :3],
                translation=matrix[:3, 3])


# ---------------------------------------------------------------------------
# 4. The record, judged against the FILES -- on a case built to order
# ---------------------------------------------------------------------------

def _synthetic_case(folder, rotation, translation, record_rotation=None,
                    record_translation=None):
    """A scene folder holding a reduction, a ground truth, and a record.

    The ground truth is the reduction actually moved by ``rotation``/
    ``translation`` (resampled onto its own grid), while the RECORD claims
    ``record_rotation``/``record_translation``. Passing different ones is how a
    stale record is simulated -- the only failure this design has that an
    estimator did not.
    """
    if not os.path.isdir(folder):
        os.makedirs(folder)
    solid = _lumpy_blob()
    reduction = _write_seg(os.path.join(folder, "Fragment Reduction.seg.nrrd"),
                           solid, [("Blob", 0, 1)],
                           space="right-anterior-superior")

    # Rasterise the moved solid by asking, for every voxel of the target grid,
    # where it came from -- nearest neighbour, so no mask is interpolated.
    nk, nj, ni = solid.shape
    k, j, i = np.mgrid[0:nk, 0:nj, 0:ni]
    points = np.stack([i.ravel(), j.ravel(), k.ravel()], axis=1).astype(float)
    inverse = np.linalg.inv(rotation)
    source = (points - np.asarray(translation, float)) @ inverse.T
    index = np.rint(source).astype(np.int64)
    inside = ((index >= 0).all(axis=1)
              & (index[:, 0] < ni) & (index[:, 1] < nj) & (index[:, 2] < nk))
    moved = np.zeros(points.shape[0], dtype=np.uint8)
    chosen = index[inside]
    moved[inside] = solid[chosen[:, 2], chosen[:, 1], chosen[:, 0]]
    truth = _write_seg(os.path.join(folder, "Ground truth.seg.nrrd"),
                       moved.reshape(solid.shape), [("Blob", 0, 1)],
                       space="right-anterior-superior")

    with segmentation_io.Segmentation(reduction) as seg:
        centroid = segmentation_io.measure_segment(
            seg, seg.segments[0], with_surface=False)["centroid"]
    _write_record(os.path.join(folder, "Ground truth.transforms.json"),
                  [_piece("Blob",
                          rotation if record_rotation is None else record_rotation,
                          translation if record_translation is None
                          else record_translation, centroid)])
    return {"subject": os.path.basename(folder), "run": os.path.basename(folder),
            "scene_dir": folder, "run_dir": folder, "timing": "",
            "dataset_dir": ""}, truth


def check_verification():
    rotation = _rotation([0.2, 0.9, -0.35], 6.0)
    translation = np.array([2.0, -1.25, 3.5])

    honest, _unused = _synthetic_case(_scratch("case_ok"), rotation, translation)
    result = pelvic.analyse_case(honest)
    row = result["rows"][0]
    check("a record that matches its files is verified",
          row["transform_verified"] and row["record_consistent"])
    check("and its residual is a fraction of a voxel",
          row["transform_residual_mm"] is not None
          and row["transform_residual_mm"] < 0.6)
    check("the displacement it reports is the record's own",
          close(row["displacement_mm"],
                np.linalg.norm(rotation @ np.zeros(3) + translation), 5.0))
    check("point_error_max is at least the displacement",
          row["point_error_max_mm"] >= row["displacement_mm"])
    check("the two volumes agree",
          abs(row["volume_ratio"] - 1.0) < pelvic.VOLUME_TOLERANCE)

    # The stale record: the ground truth was moved one way and the record says
    # another. Everything about the record is internally perfect.
    stale, _unused = _synthetic_case(
        _scratch("case_stale"), rotation, translation,
        record_rotation=_rotation([0.2, 0.9, -0.35], 2.0),
        record_translation=np.array([2.0, -1.25, 3.5]))
    row = pelvic.analyse_case(stale)["rows"][0]
    check("a STALE record is still internally consistent (nothing else catches it)",
          row["record_consistent"])
    check("but it is REFUSED against the files", row["transform_verified"] is False)
    check("and the row says so", row["status"] == "unreliable"
          and "recorded before" in (row.get("error") or ""))
    check("its residual is millimetres, not a fraction of a voxel",
          row["transform_residual_mm"] > pelvic.TRANSFORM_RESIDUAL_LIMIT_MM)

    # verify=False must report the same displacement and rotation and no verdict
    # -- a blank, which must not read as a pass.
    quick = pelvic.analyse_case(stale, verify=False)["rows"][0]
    check("verify=False reports the identical displacement and rotation",
          quick["displacement_mm"] == row["displacement_mm"]
          and quick["rotation_deg"] == row["rotation_deg"])
    check("and leaves the against-the-files verdict blank, not True",
          quick.get("transform_verified") is None)
    check("so a blank verdict is excluded from neither the table nor the mean",
          len(pelvic._trusted([quick])) == 1)                  # noqa: SLF001
    check("while a failed one IS excluded", not pelvic._trusted([row])) # noqa: SLF001


# ---------------------------------------------------------------------------
# 5. The real runs
# ---------------------------------------------------------------------------

def check_real_cases(report):
    rows = [row for row in report.get("rows") or []
            if row.get("displacement_mm") is not None]
    check("every saved run produced at least one annotated piece",
          bool(rows) and len(report.get("failed_cases") or []) == 0)
    if not rows:
        return

    check("every record is internally consistent",
          all(row.get("record_consistent") for row in rows))
    check("every record is verified against the segmentations beside it",
          all(row.get("transform_verified") for row in rows))
    check("the residual is below a voxel everywhere",
          all(row["transform_residual_mm"] < 0.5 for row in rows))
    check("the paired volumes agree to within 1% (one object on two grids)",
          all(abs(row["volume_ratio"] - 1.0) < 0.01 for row in rows))
    # point_error is the transform applied at the surface, surface_* is the gap
    # left with no transform applied, so neither ordering below can be an
    # accident of the data.
    check("point error is never smaller than the displacement",
          all(row["point_error_max_mm"] >= row["displacement_mm"]
              for row in rows))
    check("point error is never smaller than the surface distance",
          all(row["point_error_mean_mm"] >= row["surface_mean_mm"]
              for row in rows))

    for row in rows:
        print("      %-8s %-24s disp %6.3f mm  rot %6.3f deg  pt err %6.3f mm  "
              "resid %.3f mm"
              % (row["case"], row["segment"][:24], row["displacement_mm"],
                 row["rotation_deg"], row["point_error_max_mm"],
                 row["transform_residual_mm"]))


def check_real_records(cases):
    """The recorded matrix, applied to the real reductions, in both directions.

    A rigid transform and its inverse are equally well-formed, and reading the
    convention backwards would report the same displacement and the same
    rotation ANGLE -- only the residual notices. So the inverse is measured
    beside it and required to be worse.
    """
    checked = 0
    for case in cases:
        files = pelvic.find_case_files(case["scene_dir"])
        if files["error"]:
            continue
        record = pelvic.read_transform_record(files["transforms"])
        planned = segmentation_io.Segmentation(files["reduction"])
        truth = segmentation_io.Segmentation(files["truth"])
        try:
            planned_by_name = planned.by_name()
            truth_by_name = truth.by_name()
            for piece in record["pieces"]:
                key = segmentation_io.normalise_name(piece["name"])
                if key not in planned_by_name or key not in truth_by_name:
                    continue
                source = segmentation_io.subsample(
                    segmentation_io.measure_segment(
                        planned, planned_by_name[key])["surface"],
                    pelvic.SURFACE_MAX_POINTS)
                target = segmentation_io.subsample(
                    segmentation_io.measure_segment(
                        truth, truth_by_name[key])["surface"],
                    pelvic.SURFACE_MAX_POINTS)
                rotation = np.asarray(piece["rotation"])
                translation = np.asarray(piece["translation"])
                forward = pelvic.transform_residual_mm(source, target, rotation,
                                                       translation)
                identity = pelvic.transform_residual_mm(source, target, np.eye(3),
                                                        np.zeros(3))
                inverse = np.linalg.inv(rotation)
                backward = pelvic.transform_residual_mm(source, target, inverse,
                                                        -inverse @ translation)
                checked += 1
                label = "%s / %s" % (case["subject"] or case["run"], piece["name"])
                check("%s: the record closes the gap (%.3f mm -> %.3f mm)"
                      % (label, identity, forward), forward < identity)
                check("%s: and its INVERSE does not (%.3f mm)" % (label, backward),
                      backward > forward)
        finally:
            planned.close()
            truth.close()
    check("at least one real record was applied to real geometry", checked > 0)


# ---------------------------------------------------------------------------
# 6. The timing phase split
# ---------------------------------------------------------------------------

def check_phases(report):
    rows = report.get("phase_rows") or []
    check("every case has a phase row", bool(rows))
    for row in rows:
        label = row["case"]
        check("%s: no step landed outside t0..t5" % label,
              not row.get("steps_unassigned"))
        if isinstance(row.get("inside_steps_s"), float):
            check("%s: the phases sum to the time inside the steps" % label,
                  close(row["phase_sum_s"], row["inside_steps_s"], 0.06))
        for phase in pelvic.PHASE_ORDER:
            wall = row.get("%s_s" % phase) or 0.0
            spent = (row.get("%s_exec_s" % phase) or 0.0) \
                + (row.get("%s_wait_s" % phase) or 0.0)
            check("%s / %s: exec + wait = wall" % (label, phase),
                  close(wall, spent, 0.02))

    # The map against the workflow it describes. A regenerated package that
    # renumbers its steps would otherwise make the phases shrink silently.
    path = os.path.join(ROOT, "Resources", "extension_CLI", pelvic.EXTENSION_NAME,
                        "workflow.json")
    if not os.path.isfile(path):
        check("the installed CLI package has a workflow.json", False)
        return
    steps = json.load(io.open(path, encoding="utf-8")).get("steps") or []
    declared = [pelvic.canonical_step_id(step.get("step_id", "")) for step in steps]
    mapped = set(pelvic._PHASE_OF_STEP)                        # noqa: SLF001
    missing = [step for step in declared if step not in mapped]
    extra = [step for step in sorted(mapped) if step not in declared]
    check("PHASE_STEPS covers every step of the installed workflow (%d)"
          % len(declared), not missing)
    if missing:
        print("      unmapped: " + ", ".join(missing))
    check("PHASE_STEPS names no step the workflow does not have", not extra)
    if extra:
        print("      stale: " + ", ".join(extra))
    check("no step is in two phases at once",
          sum(len(group) for group in pelvic.PHASE_STEPS.values()) == len(mapped))


# ---------------------------------------------------------------------------
# 7. Discovery, the workbook's shape, and the file-pairing rules
# ---------------------------------------------------------------------------

#: Fields the shared ``run_timing`` parser puts on its rows that its own
#: TIMING_COLUMNS does not show. ``subject`` is the only one, and it is not lost:
#: the sheet's ``case`` column IS the subject. Named here rather than added to
#: the shared column list, which every procedure's workbook would then grow a
#: duplicate column for.
_TIMING_BY_PRODUCTS = ("subject",)


def check_discovery_and_sheets(report):
    cases = pelvic.discover_cases(EXPERIMENT_ROOT)
    check("runs are discovered under %s" % pelvic.RUNS_SUBDIR, bool(cases))
    check("each has a subject", all(case["subject"] for case in cases))
    check("each is scorable", all(pelvic.case_is_scorable(case) for case in cases))

    sheets = report.get("sheets") or []
    check("two sheets are written", len(sheets) == 2)
    titles = [title for title, _blocks in sheets]
    check("named Reduction accuracy and Timing",
          titles == ["Reduction accuracy", "Timing"])
    for title, blocks in sheets:
        for caption, columns, rows in blocks:
            unknown = sorted({key for row in rows for key in row
                              if key not in columns
                              and key not in _TIMING_BY_PRODUCTS})
            check("%s / %s: every field of every row has a column"
                  % (title, (caption or "")[:34]), not unknown)
            if unknown:
                print("      not shown: " + ", ".join(unknown))

    # An ambiguous scene folder must be refused, not resolved by guessing, and
    # all THREE files are required now -- a run with segmentations but no record
    # can no longer be scored at all.
    folder = _scratch("ambiguous")
    if not os.path.isdir(folder):
        os.makedirs(folder)
    array = np.zeros((6, 6, 6), dtype=np.uint8)
    array[1:5, 1:5, 1:5] = 1
    for name in ("Fragment Reduction.seg.nrrd", "Fragment Reduction_1.seg.nrrd",
                 "Ground truth.seg.nrrd"):
        _write_seg(os.path.join(folder, name), array, [("Bone", 0, 1)])
    _write_record(os.path.join(folder, "Ground truth.transforms.json"),
                  [_piece("Bone", np.eye(3), np.zeros(3), np.zeros(3))])
    found = pelvic.find_case_files(folder)
    check("two 'Fragment Reduction*' files are an ERROR, not a guess",
          bool(found["error"]) and "which one" in found["error"])
    os.remove(os.path.join(folder, "Fragment Reduction_1.seg.nrrd"))
    check("one of each pairs cleanly", not pelvic.find_case_files(folder)["error"])
    os.remove(os.path.join(folder, "Ground truth.transforms.json"))
    missing = pelvic.find_case_files(folder)
    check("a missing transforms file is an ERROR",
          bool(missing["error"]) and "transforms.json" in missing["error"])
    os.remove(os.path.join(folder, "Ground truth.seg.nrrd"))
    check("a missing ground truth is an ERROR",
          bool(pelvic.find_case_files(folder)["error"]))


# ---------------------------------------------------------------------------
# 8. Static invariants
# ---------------------------------------------------------------------------

def check_no_slicer_imports():
    """The numerics halves must import neither Slicer nor VTK at module level.

    That is what lets this script exercise the real analysis. A module-level
    ``import vtk`` added later would not fail in Slicer, so nothing but this
    check would notice that the whole analysis had become unverifiable.
    """
    for name in ("SlicerAIAgentLib/experiments/pelvic.py",
                 "SlicerAIAgentLib/experiments/segmentation_io.py"):
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


def check_no_registration():
    """The analysis must not have grown an estimator back.

    The module's claim is that the reduction error is READ. A fitting step added
    later would not fail anything -- it would agree with the record to a
    hundredth of a degree, as the ICP version did -- so nothing but this would
    notice that the claim had stopped being true.
    """
    source = io.open(os.path.join(ROOT, "SlicerAIAgentLib", "experiments",
                                  "pelvic.py"), encoding="utf-8").read()
    tree = ast.parse(source)
    defined = {node.name for node in ast.walk(tree)
               if isinstance(node, ast.FunctionDef)}
    check("pelvic.py defines no registration routine",
          not ({"kabsch", "rigid_register", "icp"} & defined))
    check("and calls no SVD", "np.linalg.svd" not in source)


def check_panel_registration():
    path = os.path.join(ROOT, "SlicerAIAgentLib", "app", "widget_experiments.py")
    source = io.open(path, encoding="utf-8").read()
    check("pelvic_panel is listed in _PANEL_MODULES", "pelvic_panel" in source)
    panel = io.open(os.path.join(ROOT, "SlicerAIAgentLib", "experiments",
                                 "pelvic_panel.py"), encoding="utf-8").read()
    check("the panel registers under the extension's own name",
          "@register_experiment_panel(pelvic.EXTENSION_NAME)" in panel)
    cli = os.path.join(ROOT, "Resources", "extension_CLI",
                       pelvic.EXTENSION_NAME, "manifest.json")
    # The Experiments selector is populated from the installed CLI packages, so a
    # name that does not match one there means the panel never appears -- and
    # _loadExperimentPanels swallows the import error, so the symptom is "No
    # analysis defined for ..." rather than a traceback.
    check("that name matches an installed CLI package", os.path.isfile(cli))


def check_analysis_reads_only():
    """Nothing in this analysis may write to a run folder.

    ``orbital.py`` edits a run's saved ``scene.mrml`` in place, and does so
    carefully. This module has no reason to write anything but the workbook, so
    the safest guarantee is that it cannot: no open-for-write, no rmtree, no
    saveNode anywhere in it.
    """
    source = io.open(os.path.join(ROOT, "SlicerAIAgentLib", "experiments",
                                  "pelvic.py"), encoding="utf-8").read()
    # io.open( is the transforms record being READ; it is stripped before the
    # scan so the bare `open(` below still means an unguarded write.
    stripped = source.replace("io.open(", "")
    banned = [token for token in ("rmtree", "os.remove", "os.rename", "saveNode",
                                  "saveScene", "open(", "makedirs")
              if token in stripped]
    check("pelvic.py writes nothing except through workbook.write_workbook",
          not banned)
    check("and it opens the transforms record read-only",
          'io.open(path, encoding="utf-8")' in source)


def _cleanup():
    import shutil                                             # noqa: PLC0415
    if os.path.isdir(SCRATCH):
        shutil.rmtree(SCRATCH, ignore_errors=True)


def main():
    try:
        print("=" * 74)
        print(" 1. The .seg.nrrd reader: layers, frames, encodings")
        print("=" * 74)
        check_reader()
        print()
        print("=" * 74)
        print(" 2. Surface extraction and the slab halo")
        print("=" * 74)
        check_surface()
        print()
        print("=" * 74)
        print(" 3. The recorded transform, judged against itself")
        print("=" * 74)
        check_record_consistency()
        print()
        print("=" * 74)
        print(" 4. The recorded transform vs the files -- including a STALE one")
        print("=" * 74)
        check_verification()
        print()

        cases = pelvic.discover_cases(EXPERIMENT_ROOT)
        print("=" * 74)
        print(" 5. The %d saved run(s)" % len(cases))
        print("=" * 74)
        report = pelvic.build_report(EXPERIMENT_ROOT)
        for line in report["log"]:
            print("      " + line)
        check_real_cases(report)
        print()
        print("=" * 74)
        print(" 5b. The real records applied to the real geometry")
        print("=" * 74)
        check_real_records(cases)
        print()
        print("=" * 74)
        print(" 6. The timing phase split")
        print("=" * 74)
        check_phases(report)
        print()
        print("=" * 74)
        print(" 7. Discovery, the workbook's shape, and file pairing")
        print("=" * 74)
        check_discovery_and_sheets(report)
        print()
        print("=" * 74)
        print(" 8. Static invariants")
        print("=" * 74)
        check_no_slicer_imports()
        check_no_registration()
        check_panel_registration()
        check_analysis_reads_only()
        print()
    finally:
        _cleanup()

    if FAILURES:
        print("FAILED (%d):" % len(FAILURES))
        for failure in FAILURES:
            print("  - " + failure)
        return 1
    print("All PelvicFracturePlanning-analysis checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
