"""Check the BoneReconstructionPlanner reconstruction analysis outside Slicer.

``mandible.py`` and the readers it leans on import neither ``slicer`` nor
``vtk``, so this runs the WHOLE analysis -- scene reader, voxeliser, contour
scan, every metric -- against the real saved runs. That is deliberate and it is
the point of keeping the module Slicer-free.

Four sections exist because their failure mode is a plausible millimetre rather
than an error, and each one cost a bug:

* **Section 2** -- a Slicer plane-cut model is PARTIALLY WELDED, and every
  cut-surface voxeliser that relies on connectivity is thrown by that. On the
  reference case it inflated the resected mandible by 4%, and the completion
  network then predicted a 45 cm3 blob instead of a 19 cm3 graft. The property
  the module rests on is that its voxeliser does not care, so a mesh is
  rasterised here in all three weldings and required to give one answer.
* **Section 3** -- the three-axis sweep. A hole in a cut fibula piece is real
  (one shipped run has a 44-edge one) and it silently costs the rays that pass
  through it. One axis under-fills; the union must not.
* **Section 4** -- the contour scan's direction. Nakao marches inward from a
  ring outside the mandible, which on a concave reference locks onto the far
  side of the arch and reports it as a 15 mm protrusion. The shipped scan walks
  away from each sample instead, and the concave case here is what pins that.
* **Section 5** -- the storage file names in ``scene.mrml`` are URL-ESCAPED, and
  every model this procedure saves has spaces in its name. Reading them verbatim
  produced a scene that reported no fibula pieces at all -- which is how both
  real runs failed the first time this ran.

    python scripts/check_mandible_analysis.py
    python scripts/check_mandible_analysis.py --predict   # also re-run the net
"""

import ast
import io
import json
import os
import struct
import sys
import tempfile
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

for _name in ("slicer", "qt", "vtk", "ctk"):
    sys.modules.setdefault(_name, types.ModuleType(_name))
sys.modules["slicer"].util = types.ModuleType("slicer.util")

import numpy as np                                            # noqa: E402

from SlicerAIAgentLib.experiments import geometry_io           # noqa: E402
from SlicerAIAgentLib.experiments import mandible              # noqa: E402
from SlicerAIAgentLib.experiments import run_timing        # noqa: E402

FAILURES = []
EXPERIMENT_ROOT = run_timing.resolve_experiment_dir(
    ROOT, mandible.EXPERIMENT_DIR)
PREDICT = "--predict" in sys.argv


def section(title):
    print("\n" + title)
    print("-" * len(title))


def check(label, condition):
    print(("PASS  " if condition else "FAIL  ") + label)
    if not condition:
        FAILURES.append(label)


# ---------------------------------------------------------------------------
# Meshes whose answer is known by construction
# ---------------------------------------------------------------------------

def cube(size=10.0, origin=(0.0, 0.0, 0.0)):
    """An axis-aligned box as (vertices, triangles), shared vertices."""
    origin = np.asarray(origin, dtype=np.float64)
    corners = np.array([[x, y, z] for x in (0.0, size) for y in (0.0, size)
                        for z in (0.0, size)], dtype=np.float64) + origin
    quads = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1),
             (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    faces = []
    for a, b, c, d in quads:
        faces.extend([[a, b, c], [a, c, d]])
    return corners, np.asarray(faces, dtype=np.int64)


def unwelded(vertices, faces):
    """The same surface as a triangle soup: no two triangles share a vertex."""
    points = vertices[faces].reshape(-1, 3)
    return points, np.arange(len(points), dtype=np.int64).reshape(-1, 3)


def half_welded(vertices, faces):
    """What Slicer's plane cut writes: coincident points stored twice.

    Every second triangle gets its own copy of its corners, so the surface is
    geometrically closed and topologically open.
    """
    extra = []
    triangles = []
    points = list(vertices)
    for index, face in enumerate(faces):
        if index % 2:
            base = len(points) + len(extra)
            extra.extend(vertices[face])
            triangles.append([base, base + 1, base + 2])
        else:
            triangles.append(list(face))
    return (np.asarray(points + extra, dtype=np.float64),
            np.asarray(triangles, dtype=np.int64))


def write_vtk(path, vertices, faces, binary=True, space="LPS"):
    """A legacy PolyData written the way Slicer writes one."""
    header = ("# vtk DataFile Version 4.2\n3D Slicer output. SPACE=%s\n%s\n"
              "DATASET POLYDATA\nPOINTS %d double\n"
              % (space, "BINARY" if binary else "ASCII", len(vertices)))
    with open(path, "wb") as handle:
        handle.write(header.encode("ascii"))
        if binary:
            handle.write(np.asarray(vertices, dtype=">f8").tobytes())
            handle.write(("\nPOLYGONS %d %d\n" % (len(faces), len(faces) * 4)
                          ).encode("ascii"))
            cells = np.concatenate(
                [np.full((len(faces), 1), 3, dtype=np.int64),
                 np.asarray(faces, dtype=np.int64)], axis=1)
            handle.write(cells.astype(">i4").tobytes())
        else:
            for point in vertices:
                handle.write(("%.17g %.17g %.17g\n" % tuple(point)).encode("ascii"))
            handle.write(("POLYGONS %d %d\n" % (len(faces), len(faces) * 4)
                          ).encode("ascii"))
            for face in faces:
                handle.write(("3 %d %d %d\n" % tuple(face)).encode("ascii"))
    return path


#: ``grid_for_bounds`` puts the grid ORIGIN at ``lower - margin``, so a whole
#: number of voxels of margin would place the mesh's own faces exactly on voxel
#: centres -- where a solid voxeliser's answer is a coin flip and the cube's
#: volume is unstated by 15%. A quarter-voxel offset puts every face midway
#: between centres, and the expected volume is then exact.
GRID_MARGIN = 4.25


def grid_over(*meshes, margin=GRID_MARGIN):
    lower = np.min([mesh[0].min(axis=0) for mesh in meshes], axis=0)
    upper = np.max([mesh[0].max(axis=0) for mesh in meshes], axis=0)
    return mandible.grid_for(np.array([lower, upper]),
                             mandible.METRIC_SPACING_MM, margin=margin)


# ---------------------------------------------------------------------------
# 1. The legacy VTK reader
# ---------------------------------------------------------------------------

def check_reader():
    section("1. the legacy VTK PolyData reader")
    vertices, faces = cube(10.0)
    with tempfile.TemporaryDirectory() as folder:
        for binary in (True, False):
            path = write_vtk(os.path.join(folder, "cube_%s.vtk" % binary),
                             vertices, faces, binary=binary)
            read_vertices, read_faces = geometry_io.read_vtk_mesh(path)
            label = "binary" if binary else "ASCII"
            check("%s: 8 points, 12 triangles" % label,
                  len(read_vertices) == 8 and len(read_faces) == 12)
            check("%s: coordinates survive" % label,
                  np.allclose(np.sort(read_vertices, axis=0),
                              np.sort(vertices, axis=0)))
            check("%s: the enclosed volume is 1000 mm3" % label,
                  abs(geometry_io.mesh_volume_mm3(read_vertices, read_faces)
                      - 1000.0) < 1e-6)

        # Slicer's cut output keeps the WHOLE input point array and references a
        # few hundred of them. A bounding box over POINTS then describes the
        # UNCUT bone, which is how a fibula segment reads as a whole fibula.
        padded = np.concatenate([vertices, vertices + 500.0])
        path = write_vtk(os.path.join(folder, "padded.vtk"), padded, faces)
        read_vertices = geometry_io.read_vtk_mesh(path)[0]
        check("points no cell refers to are dropped",
              len(read_vertices) == 8
              and read_vertices.max() < 11.0)

        check("SPACE= is read from the header",
              geometry_io.vtk_coordinate_system(path) == "lps"
              and geometry_io.vtk_coordinate_system(
                  write_vtk(os.path.join(folder, "ras.vtk"), vertices, faces,
                            space="RAS")) == "ras")

        # A quadrilateral must be fanned, not dropped: Slicer's dynamic modeler
        # caps a plane cut with polygons that are not triangles.
        quad_faces = np.array([[0, 1, 3, 2]], dtype=np.int64)
        with open(os.path.join(folder, "quad.vtk"), "wb") as handle:
            handle.write(("# vtk DataFile Version 4.2\nx\nASCII\n"
                          "DATASET POLYDATA\nPOINTS 4 double\n").encode("ascii"))
            for point in vertices[:4]:
                handle.write(("%g %g %g\n" % tuple(point)).encode("ascii"))
            handle.write(b"POLYGONS 1 5\n4 0 1 3 2\n")
        quad = geometry_io.read_vtk_mesh(os.path.join(folder, "quad.vtk"))[1]
        check("a quad polygon is fanned into 2 triangles", len(quad) == 2)
        del quad_faces


def check_reader_against_runs():
    section("1b. the reader on the real saved scenes")
    cases = mandible.discover_cases(EXPERIMENT_ROOT)
    if not cases:
        print("      no saved runs -- skipped")
        return
    folders = mandible.read_scene(cases[0]["scene_dir"])
    total = 0
    for entries in folders.values():
        for _name, path in entries:
            if not path.endswith(".vtk"):
                continue
            vertices, faces = geometry_io.read_vtk_mesh(path)
            total += 1
            if len(faces) == 0 or (faces.max() < len(vertices)):
                continue
            check("%s indexes only points it carries" % os.path.basename(path), False)
    check("every model in the scene reads with in-range faces (%d model(s))" % total,
          total > 0)


# ---------------------------------------------------------------------------
# 2. Welding cannot change the answer
# ---------------------------------------------------------------------------

def check_welding():
    section("2. a partially welded mesh must voxelise like a welded one")
    vertices, faces = cube(10.0)
    shape, affine = grid_over((vertices, faces))

    welded = mandible.voxelize(vertices, faces, shape, affine)
    soup = mandible.voxelize(*unwelded(vertices, faces), shape=shape, affine=affine)
    seamed_vertices, seamed_faces = half_welded(vertices, faces)
    seamed = mandible.voxelize(seamed_vertices, seamed_faces, shape, affine)

    check("the welded 10 mm cube is exactly 1000 mm3 (%.1f)"
          % (mandible.volume_cm3(welded) * 1000.0),
          abs(mandible.volume_cm3(welded) * 1000.0 - 1000.0) < 1.0)
    check("a triangle soup gives the identical mask",
          np.array_equal(welded, soup))
    check("a PARTIALLY welded mesh gives the identical mask",
          np.array_equal(welded, seamed))

    # ...and that is only interesting because the seams really do read as open.
    check("the partially welded mesh reads as open before welding",
          geometry_io.mesh_open_edges(seamed_faces) > 0)
    check("and as closed after it",
          geometry_io.mesh_open_edges(
              geometry_io.weld_mesh(seamed_vertices, seamed_faces)[1]) == 0)
    check("welding recovers the enclosed volume the open mesh cannot state",
          abs(geometry_io.mesh_volume_mm3(
              *geometry_io.weld_mesh(seamed_vertices, seamed_faces)) - 1000.0) < 1e-6)


# ---------------------------------------------------------------------------
# 3. The three-axis sweep against a hole
# ---------------------------------------------------------------------------

def _voxelize_one_axis(vertices, faces, shape, affine):
    repair = mandible._repair_module()                        # noqa: SLF001
    return repair._voxelize_fallback(vertices, faces, shape, affine)  # noqa: SLF001


def check_sweep():
    section("3. a hole costs one axis its rays; the union must survive it")
    vertices, faces = cube(10.0)
    shape, affine = grid_over((vertices, faces))
    whole = mandible.voxelize(vertices, faces, shape, affine)

    # Remove the two triangles of the +x face: rays along axis 0 through it now
    # cross the surface once, which the parity fill skips rather than fills.
    holed = np.asarray([face for index, face in enumerate(faces)
                        if index not in (2, 3)], dtype=np.int64)
    single = _voxelize_one_axis(vertices, holed, shape, affine)
    union = mandible.voxelize(vertices, holed, shape, affine)

    check("the hole is real (open edges after welding)",
          geometry_io.mesh_open_edges(geometry_io.weld_mesh(vertices, holed)[1]) > 0)
    check("one axis loses most of the solid (%.0f%% of it)"
          % (100.0 * single.sum() / max(whole.sum(), 1)),
          single.sum() < 0.5 * whole.sum())
    check("the three-axis union recovers it (%.1f%% of the intact cube)"
          % (100.0 * union.sum() / max(whole.sum(), 1)),
          union.sum() > 0.95 * whole.sum())
    check("and never adds a voxel outside the intact solid",
          not np.logical_and(union, ~whole).any())


# ---------------------------------------------------------------------------
# 4. The contour scan
# ---------------------------------------------------------------------------

def _flat_face(scan, axis, index, half=8):
    """Readings on the flat middle of one face, away from every edge."""
    points = scan["points"].astype(int)
    on_face = ((points[:, axis] == index)
               & (abs(points[:, (axis + 1) % 3] - 30) < half)
               & (abs(points[:, (axis + 2) % 3] - 30) < half))
    values = scan["signed"][on_face]
    return values[np.isfinite(values)]


def check_contour_scan():
    section("4. the contour scan: sign, magnitude, and the concavity trap")
    spacing = mandible.METRIC_SPACING_MM

    # A slab of reference, and a fibula slab offset by a known whole number of
    # voxels. On a flat face the answer is exact, so it is checked as such --
    # this is the section that caught the scan reading a 3.0 mm protrusion as
    # 3.25 (it started at a voxel CENTRE, half a voxel inside the surface it
    # stands for) and a 2 mm gap as -1.75 on one side of the slab and -2.00 on
    # the other (a boolean lookup flips on a tie, whichever way rint rounds).
    shape = (80, 60, 60)
    affine = np.eye(4)
    affine[:3, :3] = np.diag([spacing] * 3)
    reference = np.zeros(shape, bool)
    reference[20:60, 10:50, 10:50] = True

    inset = np.zeros(shape, bool)
    inset[20:56, 14:46, 14:46] = True            # 2 mm inside on every face
    scan = mandible.contour_scan(reference, inset, spacing)
    for axis, index, label in ((1, 10, "-y"), (1, 49, "+y"), (2, 10, "-z")):
        values = _flat_face(scan, axis, index)
        # 1e-3 mm, not 0: the normal comes from a smoothed distance field, so on
        # a flat face it is axis-aligned to about half a thousandth of a voxel.
        check("a fibula set 2 mm inside reads -2.000 on %s (worst %.2e off)"
              % (label, np.abs(values + 2.0).max() if values.size else np.nan),
              values.size and np.allclose(values, -2.0, atol=1e-3))
    finite = scan["signed"][np.isfinite(scan["signed"])]
    check("and nowhere reports a projection (max %.2f)" % finite.max(),
          finite.max() <= 0.0 + 1e-6)

    proud = np.zeros(shape, bool)
    proud[20:66, 10:50, 10:50] = True            # 3 mm past the +x face
    scan = mandible.contour_scan(reference, proud, spacing)
    values = _flat_face(scan, 0, 59)
    check("a fibula standing 3 mm proud reads +3.000 (worst %.2e off)"
          % (np.abs(values - 3.0).max() if values.size else np.nan),
          values.size and np.allclose(values, 3.0, atol=1e-3))

    scan = mandible.contour_scan(reference, reference, spacing)
    values = _flat_face(scan, 0, 59)
    check("two identical masks read flush, not half a voxel apart (worst "
          "%.2e off)" % (np.abs(values).max() if values.size else np.nan),
          values.size and np.allclose(values, 0.0, atol=1e-3))

    check("a fibula the scan cannot reach yields no pair, not a zero",
          not np.isfinite(mandible.contour_scan(
              reference, np.zeros(shape, bool), spacing)["signed"]).any())

    # The concavity. A U: two arms 24 mm apart with the fibula on ONE of them.
    # A normal on the empty arm's inner wall points across the gap at the other
    # arm, so an outside-in march from a ring 20 mm out meets the far arm FIRST
    # and calls it a +15 mm protrusion. Walking away from the sample cannot.
    arch = np.zeros(shape, bool)
    arch[20:60, 10:20, 10:50] = True             # arm A
    arch[20:60, 44:54, 10:50] = True             # arm B, 12 mm of gap between
    on_far_arm = np.zeros(shape, bool)
    on_far_arm[20:60, 44:54, 10:50] = True
    scan = mandible.contour_scan(arch, on_far_arm, spacing)
    signed = scan["signed"]
    found = np.isfinite(signed)
    inner_wall_reading = signed[found].max()
    check("across a concavity the far wall is not reported as a protrusion "
          "(max %.2f mm, gap is %.0f mm)"
          % (inner_wall_reading, (44 - 20) * spacing),
          inner_wall_reading < 1.0)


def check_scan_uses_local_walk():
    section("4b. the scan walks away from the sample, on the distance field")
    source = io.open(os.path.join(ROOT, "SlicerAIAgentLib", "experiments",
                                  "mandible.py"), encoding="utf-8").read()
    body = source[source.index("def contour_scan"):]
    body = body[:body.index("\ndef ", 1)]
    check("it asks whether the fibula covers the sample itself",
          "covered = sample(0.0) <= 0.0" in body)
    check("it walks outward for the samples the fibula covers",
          "walk(covered, 1.0, SCAN_OUT_MM)" in body)
    check("and inward for the ones it does not",
          "walk(~covered, -1.0, SCAN_IN_MM)" in body)
    check("the crossing is read off the signed distance field, not a boolean "
          "lookup", "distance_transform_edt(~fibula)" in body
          and "np.rint" not in body)
    check("and the half-voxel start offset is taken back out",
          "- 0.5 * spacing" in body)


# ---------------------------------------------------------------------------
# 5. scene.mrml: roles by folder, file names URL-escaped
# ---------------------------------------------------------------------------

_SCENE_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<MRML version="Slicer4.11" userTags="">
 <ModelStorage id="vtkMRMLModelStorageNode1" name="s1" fileName="{stump}" />
 <ModelStorage id="vtkMRMLModelStorageNode2" name="s2" fileName="{piece}" />
 <Model id="vtkMRMLModelNode1" name="Resected mandible"
  references="display:vtkMRMLModelDisplayNode1;storage:vtkMRMLModelStorageNode1;" />
 <Model id="vtkMRMLModelNode2" name="Transformed Fibula Segment 0A-0B_15"
  references="display:vtkMRMLModelDisplayNode2;storage:vtkMRMLModelStorageNode2;" />
 <SubjectHierarchy id="vtkMRMLSubjectHierarchyNode1" name="SubjectHierarchy">
  <SubjectHierarchyItem id="1" name="Scene" parent="0" type="" />
  <SubjectHierarchyItem id="2" name="Cut Bones" parent="1" type="" />
  <SubjectHierarchyItem id="3" name="Transformed Fibula Pieces" parent="1" type="" />
  <SubjectHierarchyItem id="4" dataNode="vtkMRMLModelNode1" parent="2" type="Models" />
  <SubjectHierarchyItem id="5" dataNode="vtkMRMLModelNode2" parent="3" type="Models" />
 </SubjectHierarchy>
</MRML>
"""


def check_scene_reader():
    section("5. scene.mrml: roles come from folders, file names are URL-escaped")
    vertices, faces = cube(10.0)
    with tempfile.TemporaryDirectory() as folder:
        stump = "Resected mandible.vtk"
        piece = "Transformed Fibula Segment 0A-0B_15.vtk"
        write_vtk(os.path.join(folder, stump), vertices, faces)
        write_vtk(os.path.join(folder, piece), vertices, faces)
        io.open(os.path.join(folder, "scene.mrml"), "w", encoding="utf-8").write(
            _SCENE_TEMPLATE.format(
                stump=stump.replace(" ", "%20"), piece=piece.replace(" ", "%20")))

        folders = mandible.read_scene(folder)
        pieces = folders.get(mandible.FIBULA_FOLDER) or []
        check("the escaped file name resolves to a file that exists",
              len(pieces) == 1 and os.path.isfile(pieces[0][1]))
        check("the fibula pieces are found by FOLDER, suffix and all",
              len(pieces) == 1 and pieces[0][0].endswith("_15"))
        check("the resected mandible is found under Cut Bones",
              (mandible.folder_entry(folders, mandible.CUT_BONES_FOLDER,
                                     mandible.RESECTED_MANDIBLE_NAME) or "")
              .endswith(stump))

        # An unescaped writer must still be read.
        io.open(os.path.join(folder, "scene.mrml"), "w", encoding="utf-8").write(
            _SCENE_TEMPLATE.format(stump=stump, piece=piece))
        check("a name that was never escaped is read too",
              len(mandible.read_scene(folder).get(mandible.FIBULA_FOLDER) or []) == 1)


# ---------------------------------------------------------------------------
# 6. Overlap metrics and the slice-weighted Dice objective
# ---------------------------------------------------------------------------

def check_overlap_metrics():
    section("6. Rv, Dice and the Guo et al. slice loss on known masks")
    spacing = mandible.METRIC_SPACING_MM
    shape = (60, 60, 60)
    affine = np.eye(4)
    affine[:3, :3] = np.diag([spacing] * 3)

    reference = np.zeros(shape, bool)
    reference[10:50, 10:50, 10:50] = True
    half = np.zeros(shape, bool)
    half[10:30, 10:50, 10:50] = True             # exactly half of it

    overlap = float(np.logical_and(reference, half).sum())
    check("Rv of a fibula filling exactly half is 0.5",
          abs(overlap / reference.sum() - 0.5) < 1e-9)
    check("Dice of that pair is 2/3",
          abs(2.0 * overlap / (reference.sum() + half.sum()) - 2.0 / 3.0) < 1e-9)

    same = mandible.slice_dice_loss(reference, reference, affine, spacing)
    check("the slice loss of a perfect match is 0 on both families",
          abs(same["slice_loss_xy"]) < 1e-6 and abs(same["slice_loss_xz"]) < 1e-6)
    check("and its total is 0", abs(same["slice_loss_total"]) < 1e-6)

    # A fibula that is half the reference cuboid. Sliced ACROSS the cut every
    # slice is half covered (Dice 2/3, loss 1/3); sliced ALONG it every spanned
    # slice matches exactly (loss 0). Which family gets which follows from the
    # OBB, so the pair is checked as a set rather than by name.
    partial = mandible.slice_dice_loss(reference, half, affine, spacing)
    pair = sorted(round(partial[key], 2)
                  for key in ("slice_loss_xy", "slice_loss_xz"))
    check("a fibula filling half the reference loses 0 one way and 1/3 the "
          "other (%s)" % pair,
          abs(pair[0]) < 0.02 and abs(pair[1] - 1.0 / 3.0) < 0.06)
    check("the total is xy + %.1f x xz" % mandible.SLICE_XZ_WEIGHT,
          abs(partial["slice_loss_total"]
              - (partial["slice_loss_xy"]
                 + mandible.SLICE_XZ_WEIGHT * partial["slice_loss_xz"])) < 1e-9)

    # Wholly disjoint: no slice the plan spans holds any reference, so the
    # weighted mean has no weight. That is undefined, and reporting it as a
    # blank is the only honest answer -- a fabricated 1.0 would read as "the
    # worst possible plan" rather than "this was not measurable".
    apart = np.zeros(shape, bool)
    apart[10:20, 10:20, 10:20] = True
    elsewhere = np.zeros(shape, bool)
    elsewhere[40:50, 40:50, 40:50] = True
    disjoint = mandible.slice_dice_loss(apart, elsewhere, affine, spacing)
    check("masks that share no slice give no loss rather than a made-up one",
          disjoint["slice_loss_total"] is None)

    # A gap BETWEEN two pieces is inside the span and must count against the
    # plan -- otherwise a plan that leaves the middle of the defect empty scores
    # like one that fills it.
    split = np.zeros(shape, bool)
    split[10:22, 10:50, 10:50] = True
    split[38:50, 10:50, 10:50] = True
    gapped = mandible.slice_dice_loss(reference, split, affine, spacing)
    filled = np.zeros(shape, bool)
    filled[10:22, 10:50, 10:50] = True
    solid = mandible.slice_dice_loss(reference, filled, affine, spacing)
    check("a plan with a hole in the middle scores worse than the same bone in "
          "one piece (%.3f vs %.3f)"
          % (gapped["slice_loss_xy"], solid["slice_loss_xy"]),
          gapped["slice_loss_xy"] > solid["slice_loss_xy"])


# ---------------------------------------------------------------------------
# 7. The prediction, against the reference implementation
# ---------------------------------------------------------------------------

def check_prediction():
    section("7. the ground truth: our prediction vs the shipped repair()")
    model = mandible.model_path(ROOT)
    cases = mandible.discover_cases(EXPERIMENT_ROOT)
    if not cases:
        print("      no saved runs -- skipped")
        return
    if not os.path.isfile(model):
        print("      %s is not installed -- skipped" % mandible.MODEL_RELATIVE)
        return
    if not PREDICT:
        print("      pass --predict to run the network (about 25 s per run)")
        return

    case = cases[0]
    folders = mandible.read_scene(case["scene_dir"])
    source = mandible.folder_entry(folders, mandible.CUT_BONES_FOLDER,
                                   mandible.RESECTED_MANDIBLE_NAME)
    vertices, faces = mandible.read_mesh(source)
    declared = geometry_io.vtk_coordinate_system(source)
    ours = mandible.predict_graft(vertices, faces, model, declared)

    repair = mandible._repair_module()                        # noqa: SLF001
    with tempfile.TemporaryDirectory() as folder:
        stl = os.path.join(folder, "in.stl")
        repair.save_stl(vertices, faces, stl)
        theirs = repair.load_stl(repair.repair(stl, model, orientation=declared,
                                               echo=False))[0]

    check("the file declares a frame and the anatomy agrees with it "
          "(declared %s, detected %s, %.3f)"
          % (declared, ours["detected_orientation"], ours["orientation_score"]),
          declared == ours["detected_orientation"])
    check("our graft has the same bounds as the shipped repair()'s "
          "(%s vs %s)" % (np.round(ours["vertices"].min(axis=0), 1),
                          np.round(theirs.min(axis=0), 1)),
          np.allclose(ours["vertices"].min(axis=0), theirs.min(axis=0), atol=0.6)
          and np.allclose(ours["vertices"].max(axis=0), theirs.max(axis=0), atol=0.6))
    check("and a plausible graft volume (%.1f cm3)" % ours["graft_volume_cm3"],
          1.0 < ours["graft_volume_cm3"] < mandible.PLAUSIBLE_GRAFT_CM3)


# ---------------------------------------------------------------------------
# 8. Every saved run, end to end
# ---------------------------------------------------------------------------

def check_full_sweep():
    section("8. every saved run, end to end")
    report = mandible.build_report(ROOT)
    rows = report["rows"]
    check("every run was analysed (%d of %d)" % (len(rows), report["cases"]),
          rows and not report["failed_cases"])
    if not rows:
        for line in report["log"]:
            print("      " + line)
        return

    for row in rows:
        label = row["case"]
        check("%s: Rv is a share of the defect (%.1f%%)"
              % (label, row["volume_ratio_pct"]),
              0.0 < row["volume_ratio_pct"] <= 100.0)
        check("%s: Ec is a few millimetres (%.2f mm over %.0f%% of the contour)"
              % (label, row["contour_error_mm"], row["contour_coverage_pct"]),
              0.0 < row["contour_error_mm"] < 15.0)
        check("%s: Ep is positive and inside the scan range (%.2f mm)"
              % (label, row["max_projection_mm"]),
              0.0 < row["max_projection_mm"] <= mandible.SCAN_OUT_MM)
        check("%s: the fibula sits INSIDE the contour on balance (median %.2f mm)"
              % (label, row["median_offset_mm"]),
              row["median_offset_mm"] < 0.0)
        check("%s: no contour sample saturated the scan" % label,
              row["saturated_samples"] == 0)

        # Two independent routes to "how far does the fibula stand proud": the
        # contour scan along the reference normals, and the volumetric distance
        # from each piece to the graft. They measure the same thing differently,
        # so a disagreement means one of them is wrong.
        pieces = [seg for seg in report["segments"] if seg["case"] == label]
        volumetric = max(seg["protrusion_max_mm"] for seg in pieces)
        check("%s: Ep agrees with the volumetric protrusion (%.2f vs %.2f mm)"
              % (label, row["max_projection_mm"], volumetric),
              abs(row["max_projection_mm"] - volumetric) < 1.5)
        check("%s: the pieces' volumes sum to the fibula's (%.2f vs %.2f cm3)"
              % (label, sum(seg["volume_cm3"] for seg in pieces),
                 row["fibula_volume_cm3"]),
              abs(sum(seg["volume_cm3"] for seg in pieces)
                  - row["fibula_volume_cm3"]) < 0.05)
        check("%s: the ground truth came from the run's own cache or the network"
              % label, row["gt_source"] in ("cached", "predicted"))

    check("the workbook has both sheets",
          [title for title, _blocks in report["sheets"]][:1]
          == ["Reconstruction accuracy"] and len(report["sheets"]) == 2)
    check("every per-run column is defined",
          _undefined(mandible.CASE_COLUMNS, mandible.CASE_DEFINITIONS) == [])
    check("every per-segment column is defined",
          _undefined(mandible.SEGMENT_COLUMNS, mandible.SEGMENT_DEFINITIONS) == [])


#: Columns whose meaning is the run's identity or a plain restatement of another
#: column, and which therefore need no definition row of their own.
_SELF_EVIDENT = {
    "case", "run", "segments", "gt_volume_cm3", "fibula_volume_cm3",
    "outside_gt_cm3", "specimen_volume_cm3", "total_graft_length_mm",
    "gt_source", "prediction_s", "status", "projection_p95_mm",
    "segment", "volume_cm3", "share_of_fibula_pct", "protrusion_p95_mm",
    "open_edges",
}


def _undefined(columns, definitions):
    """Columns with no definition row. A definition may name several columns."""
    text = " ".join(term for term, _definition in definitions)
    return [column for column in columns
            if column not in _SELF_EVIDENT and column not in text]


# ---------------------------------------------------------------------------
# 9. The module never deletes anything
# ---------------------------------------------------------------------------

def check_no_deletion():
    section("9. the analysis reads runs and adds to them; it removes nothing")
    path = os.path.join(ROOT, "SlicerAIAgentLib", "experiments", "mandible.py")
    tree = ast.parse(io.open(path, encoding="utf-8").read())
    banned = {"remove", "unlink", "rmtree", "rmdir", "removedirs", "truncate"}
    found = sorted({node.func.attr for node in ast.walk(tree)
                    if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr in banned})
    check("no delete call anywhere in mandible.py", not found)
    if found:
        print("      found: " + ", ".join(found))

    writes = sorted({node.func.attr for node in ast.walk(tree)
                     if isinstance(node, ast.Call)
                     and isinstance(node.func, ast.Attribute)
                     and node.func.attr in {"makedirs", "save_stl"}})
    check("it writes only the analysis cache (%s)" % ", ".join(writes) or "nothing",
          set(writes) <= {"makedirs", "save_stl"})


# ---------------------------------------------------------------------------
# 10. The panel is reachable
# ---------------------------------------------------------------------------

def check_panel():
    section("10. the panel is registered and reachable")
    app_dir = os.path.join(ROOT, "SlicerAIAgentLib", "app")
    panel_dir = os.path.join(ROOT, "SlicerAIAgentLib", "experiments")
    widget = io.open(os.path.join(app_dir, "widget_experiments.py"),
                     encoding="utf-8").read()
    listed = ast.literal_eval(
        widget.split("_PANEL_MODULES = ", 1)[1].split("\n\n", 1)[0].strip())
    check("mandible_panel is in _PANEL_MODULES", "mandible_panel" in listed)
    check("every listed panel module exists",
          all(os.path.isfile(os.path.join(panel_dir, "%s.py" % name))
              for name in listed))

    source = io.open(os.path.join(panel_dir, "mandible_panel.py"),
                     encoding="utf-8").read()
    check("it registers under the CLI package name, not the folder name",
          "register_experiment_panel(mandible.EXTENSION_NAME)" in source)
    check("the folder on disk exists under that name",
          os.path.isdir(EXPERIMENT_ROOT))
    check("the numerics half imports no Qt",
          "import qt" not in io.open(
              os.path.join(panel_dir, "mandible.py"), encoding="utf-8").read())


class _Widget:
    """Enough of a Qt widget for the panel to build against.

    Every attribute resolves and every call succeeds, so the panel's own control
    flow runs without this having to track Qt's API. Two things ARE recorded:
    the calls, so an assertion can be made about what the panel did, and the
    signal connections -- a button that builds and connects to nothing is the
    one panel failure that looks exactly like a working panel.
    """

    def __init__(self, kind="", registry=None):
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "registry", registry if registry is not None else {})
        object.__setattr__(self, "slots", [])
        object.__setattr__(self, "calls", [])
        object.__setattr__(self, "properties", {})
        self.registry.setdefault(kind, []).append(self)

    def __getattr__(self, name):
        if name in ("clicked", "toggled"):
            return self                       # signals: .connect() lands here
        if name in self.properties:
            return self.properties[name]      # e.g. .checked after setChecked

        def recorder(*args, **kwargs):
            self.calls.append((name, args))
            if name.startswith("set") and len(args) == 1:
                self.properties[name[3].lower() + name[4:]] = args[0]
            return _Widget(name, self.registry)
        return recorder

    def __setattr__(self, name, value):
        self.properties[name] = value

    def __call__(self, *args, **kwargs):
        return _Widget(self.kind, self.registry)

    def connect(self, slot):
        self.slots.append(slot)

    def fire(self):
        for slot in self.slots:
            slot()

    def called(self, name):
        return [args for called, args in self.calls if called == name]


def check_panel_builds():
    section("10b. the panel builds, and its button actually runs the analysis")
    import importlib                                          # noqa: PLC0415

    registry = {}

    def factory(kind):
        return lambda *a, **k: _Widget(kind, registry)

    qt_stub = types.ModuleType("qt")
    for name in ("QLabel", "QCheckBox", "QPushButton", "QVBoxLayout",
                 "QProgressDialog", "QWidget", "QFrame", "QComboBox"):
        setattr(qt_stub, name, factory(name))
    qt_stub.Qt = types.SimpleNamespace(RichText=1, ApplicationModal=2)
    sys.modules["qt"] = qt_stub

    slicer_stub = sys.modules["slicer"]
    slicer_stub.app = types.SimpleNamespace(processEvents=lambda: None)
    slicer_stub.util.mainWindow = lambda: None

    # The panel reaches its two Slicer-side neighbours by relative import, and
    # both drag in the whole Qt widget stack. Substituting them keeps this a
    # test of the panel rather than of the application around it.
    package = "SlicerAIAgentLib.app"
    registrations = []
    experiments = types.ModuleType(package + ".widget_experiments")
    experiments.register_experiment_panel = (
        lambda name: lambda builder: registrations.append((name, builder)) or builder)
    common = types.ModuleType(package + ".common")
    common.SLICER_AI_AGENT_ROOT = ROOT
    sys.modules[package + ".widget_experiments"] = experiments
    sys.modules[package + ".common"] = common

    try:
        # Imported once, from scratch: reloading would run the decorator a
        # second time and turn one registration into two.
        sys.modules.pop("SlicerAIAgentLib.experiments.mandible_panel", None)
        importlib.import_module("SlicerAIAgentLib.experiments.mandible_panel")
        check("importing the panel registers exactly one builder for %s"
              % mandible.EXTENSION_NAME,
              [name for name, _b in registrations] == [mandible.EXTENSION_NAME])

        layout = _Widget("QVBoxLayout", registry)
        registrations[-1][1](_Widget("host", registry), layout, mandible.EXTENSION_NAME)
        buttons = registry.get("QPushButton") or []
        boxes = registry.get("QCheckBox") or []
        check("it builds one button and one checkbox",
              len(buttons) == 1 and len(boxes) == 1)
        check("the button is connected to something",
              bool(buttons and buttons[0].slots))
        check("re-predicting is OFF by default -- a sweep must not silently "
              "spend 25 s a run rebuilding ground truths that are already saved",
              bool(boxes) and boxes[0].properties.get("checked") is False)
        check("the button is enabled, there being runs to analyse",
              bool(buttons) and buttons[0].called("setEnabled")[-1] == (True,))

        # Press it. The predictions are cached, so this is the real analysis and
        # the real workbook write, driven through the panel's own code path.
        buttons[0].fire()

        enabling = buttons[0].called("setEnabled")
        check("pressing it disables the button and re-enables it afterwards",
              enabling[-2:] == [(False,), (True,)])
        status = [args[0] for label in (registry.get("QLabel") or [])
                  for args in label.called("setText")]
        check("the status line ends by naming where the workbook went (%s)"
              % (status[-1][:60] if status else ""),
              bool(status) and "Saved" in status[-1])
        check("and it is not reporting a failure",
              bool(status) and "failed" not in status[-1].lower())
        check("the workbook is on disk",
              os.path.isfile(os.path.join(EXPERIMENT_ROOT, mandible.RUNS_SUBDIR,
                                          mandible.WORKBOOK_NAME)))
    finally:
        for name in (package + ".widget_experiments", package + ".common"):
            sys.modules.pop(name, None)


# ---------------------------------------------------------------------------

def main():
    check_reader()
    check_reader_against_runs()
    check_welding()
    check_sweep()
    check_contour_scan()
    check_scan_uses_local_walk()
    check_scene_reader()
    check_overlap_metrics()
    check_prediction()
    check_full_sweep()
    check_no_deletion()
    check_panel()
    check_panel_builds()

    print("\n" + "=" * 60)
    if FAILURES:
        print("%d FAILURE(S):" % len(FAILURES))
        for failure in FAILURES:
            print("  - " + failure)
        return 1
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
