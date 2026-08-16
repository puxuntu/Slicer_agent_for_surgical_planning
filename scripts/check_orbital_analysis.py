"""Check the OrbitalFractureReconstruction analysis outside Slicer.

``orbital.py`` imports ``slicer``/``vtk`` lazily, inside the functions that mesh
and render, so everything else -- the statistics, the improvement pairing, case
discovery, and the MRML splicer -- is importable and checkable here. That split
is deliberate: the splicer edits a run's saved ``scene.mrml`` in place, which is
the one operation in this feature that can damage existing data, so it is the one
that must be provable without a running Slicer.

    python scripts/check_orbital_analysis.py
"""

import os
import shutil
import sys
import tempfile
import types
import xml.etree.ElementTree as ElementTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

for _name in ("slicer", "qt", "vtk", "ctk"):
    sys.modules.setdefault(_name, types.ModuleType(_name))
sys.modules["slicer"].util = types.ModuleType("slicer.util")

import numpy as np                                            # noqa: E402

from SlicerAIAgentLib.experiments import orbital              # noqa: E402

FAILURES = []


def check(label, condition):
    print(("PASS  " if condition else "FAIL  ") + label)
    if not condition:
        FAILURES.append(label)


def close(a, b, tol=1e-6):
    return a is not None and abs(a - b) <= tol


# ---------------------------------------------------------------------------
# 1. distance_statistics, on values whose answer is known by hand
# ---------------------------------------------------------------------------

def check_statistics():
    gt_to_other = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    other_to_gt = np.array([1.0, 1.0])
    stats = orbital.distance_statistics(gt_to_other, other_to_gt)

    # pooled = [0,1,2,3,4,1,1] -> mean 12/7
    check("assd pools BOTH directions", close(stats["assd_mm"], round(12 / 7.0, 4), 1e-4))
    check("rms is over the pooled set",
          close(stats["rms_mm"], round(float(np.sqrt(32 / 7.0)), 4), 1e-4))
    check("median is over the pooled set", close(stats["median_mm"], 1.0))
    check("hd_max is the pooled maximum", close(stats["hd_max_mm"], 4.0))
    check("one-way means are kept separate",
          close(stats["mean_gt_to_other_mm"], 2.0) and close(stats["mean_other_to_gt_mm"], 1.0))
    check("within_1mm is measured on the GROUND TRUTH surface only",
          close(stats["within_1mm_pct"], 40.0))       # 0 and 1 of five GT values
    check("within_2mm likewise", close(stats["within_2mm_pct"], 60.0))
    check("point counts are reported",
          stats["gt_points"] == 5 and stats["other_points"] == 2)

    # hd95 must not follow a single stray vertex, which is why it is quoted.
    clean = np.zeros(1000)
    strayed = np.concatenate([np.zeros(999), [50.0]])
    a = orbital.distance_statistics(clean, clean)
    b = orbital.distance_statistics(strayed, strayed)
    check("hd_max IS moved by one stray vertex", b["hd_max_mm"] == 50.0)
    check("hd95 is NOT moved by one stray vertex",
          close(b["hd95_mm"], a["hd95_mm"], 1e-9))

    check("empty input yields no row, not a crash",
          orbital.distance_statistics(np.zeros(0), np.zeros(0)) == {})
    one_sided = orbital.distance_statistics(np.array([2.0, 4.0]), np.zeros(0))
    check("a one-sided comparison still summarises", close(one_sided["assd_mm"], 3.0))


# ---------------------------------------------------------------------------
# 2. improvement pairing
# ---------------------------------------------------------------------------

def check_improvement():
    rows = [
        {"case": "051", "comparison": "fractured", "assd_mm": 2.0, "hd95_mm": 5.0,
         "within_1mm_pct": 20.0, "run": "r1"},
        {"case": "051", "comparison": "reconstructed", "assd_mm": 0.5, "hd95_mm": 1.5,
         "within_1mm_pct": 80.0, "run": "r1"},
        {"case": "052", "comparison": "fractured", "assd_mm": 1.0, "hd95_mm": 2.0,
         "within_1mm_pct": 50.0, "run": "r2"},
        {"case": "052", "comparison": "reconstructed", "assd_mm": 1.4, "hd95_mm": 3.0,
         "within_1mm_pct": 40.0, "run": "r2"},
        # Only one side scored: must be dropped rather than half-reported.
        {"case": "053", "comparison": "reconstructed", "assd_mm": 0.9, "run": "r3"},
    ]
    out = orbital.improvement_rows(rows)
    check("one row per case with BOTH comparisons", [r["case"] for r in out] == ["051", "052"])
    check("improvement is before - after", close(out[0]["assd_improvement_mm"], 1.5))
    check("improvement percentage", close(out[0]["assd_improvement_pct"], 75.0))
    check("a case that got WORSE is flagged, not hidden",
          out[1]["improved"] is False and close(out[1]["assd_improvement_mm"], -0.4))

    summary = orbital._aggregate(rows, out)
    reconstructed = [s for s in summary if s["comparison"] == "Reconstructed"][0]
    check("aggregate averages the reconstruction rows",
          close(reconstructed["mean_assd_mm"], round((0.5 + 1.4 + 0.9) / 3, 4), 1e-4))
    improvement = [s for s in summary if s["comparison"].startswith("IMPROVEMENT")][0]
    check("aggregate counts how many cases improved", improvement["cases_improved"] == 1)


# ---------------------------------------------------------------------------
# 3. The MRML splicer -- the part that edits existing data
# ---------------------------------------------------------------------------

RUN_SCENE = """<?xml version="1.0" encoding="UTF-8"?>
<MRML version="Slicer 5.10.0" userTags="">
 <Model id="vtkMRMLModelNode1" name="OFR_FullBone" references="display:vtkMRMLModelDisplayNode1;storage:vtkMRMLModelStorageNode1;"></Model>
 <ModelDisplay id="vtkMRMLModelDisplayNode1" name="ModelDisplay" color="0.9 0.85 0.75"></ModelDisplay>
 <ModelStorage id="vtkMRMLModelStorageNode1" name="ModelStorage" fileName="OFR_FullBone.vtk"></ModelStorage>
 <View id="vtkMRMLViewNode1" name="View1"></View>
</MRML>
"""

# Deliberately numbered so a naive textual rewrite would corrupt it:
# vtkMRMLModelNode1 is a prefix of vtkMRMLModelNode10.
ERROR_SCENE = """<?xml version="1.0" encoding="UTF-8"?>
<MRML version="Slicer 5.10.0" userTags="">
 <Model id="vtkMRMLModelNode1" name="ErrorMap_Reconstructed_vs_GT" references="display:vtkMRMLModelDisplayNode1;storage:vtkMRMLModelStorageNode1;"></Model>
 <Model id="vtkMRMLModelNode10" name="ErrorMap_Fractured_vs_GT" references="display:vtkMRMLModelDisplayNode10;storage:vtkMRMLModelStorageNode10;"></Model>
 <Model id="vtkMRMLModelNode2" name="GroundTruth_051" references="display:vtkMRMLModelDisplayNode2;storage:vtkMRMLModelStorageNode2;"></Model>
 <ModelDisplay id="vtkMRMLModelDisplayNode1" name="D1" references="colorNodeRef:vtkMRMLColorTableNode1;" viewNodeRef="vtkMRMLViewNode1"></ModelDisplay>
 <ModelDisplay id="vtkMRMLModelDisplayNode10" name="D10" references="colorNodeRef:vtkMRMLColorTableNode1;"></ModelDisplay>
 <ModelDisplay id="vtkMRMLModelDisplayNode2" name="D2"></ModelDisplay>
 <ModelStorage id="vtkMRMLModelStorageNode1" name="S1" fileName="ErrorMap_Reconstructed_vs_GT.vtp"></ModelStorage>
 <ModelStorage id="vtkMRMLModelStorageNode10" name="S10" fileName="ErrorMap_Fractured_vs_GT.vtp"></ModelStorage>
 <ModelStorage id="vtkMRMLModelStorageNode2" name="S2" fileName="GroundTruth_051.vtp"></ModelStorage>
 <ColorTable id="vtkMRMLColorTableNode1" name="OFR_SurfaceError_0_3mm" references="storage:vtkMRMLColorTableStorageNode1;"></ColorTable>
 <ColorTableStorage id="vtkMRMLColorTableStorageNode1" name="CS1" fileName="OFR_SurfaceError_0_3mm.ctbl"></ColorTableStorage>
 <View id="vtkMRMLViewNode1" name="View1"></View>
</MRML>
"""


def check_splicer():
    check("renamed ids cannot collide with Slicer's",
          orbital._renamed_id("vtkMRMLModelNode1", "0") == "vtkMRMLModelNodeOFRErr_0")

    workdir = tempfile.mkdtemp(prefix="ofr_splice_")
    try:
        scene = os.path.join(workdir, "scene.mrml")
        errors = os.path.join(workdir, "ErrorMaps.mrml")
        open(scene, "w", encoding="utf-8").write(RUN_SCENE)
        open(errors, "w", encoding="utf-8").write(ERROR_SCENE)
        original = open(scene, encoding="utf-8").read()

        names = ["ErrorMap_Reconstructed_vs_GT", "ErrorMap_Fractured_vs_GT"]
        notes = []
        ok = orbital._splice_into_scene(scene, errors, names, notes)
        check("splice reports success", ok and not notes)

        backup = os.path.join(workdir, orbital.SCENE_BACKUP)
        check("the original scene is backed up", os.path.isfile(backup))
        check("the backup is byte-identical to the original",
              open(backup, encoding="utf-8").read() == original)

        root = ElementTree.parse(scene).getroot()
        spliced = [el for el in root if orbital.ID_MARKER in (el.get("id") or "")]
        by_name = {el.get("name"): el for el in spliced}
        check("both error maps are in the run scene",
              set(names).issubset(set(by_name)))
        check("the ground-truth model is NOT spliced in (it is the same surface)",
              "GroundTruth_051" not in by_name)
        check("the colour table came along",
              any(el.tag == "ColorTable" for el in spliced))
        check("its storage node came along",
              any(el.tag == "ColorTableStorage" for el in spliced))
        check("the View node did NOT come along",
              not any(el.tag == "View" for el in spliced))

        # The run's own nodes must be untouched, ids included.
        kept = {el.get("id") for el in root if orbital.ID_MARKER not in (el.get("id") or "")}
        check("the run's own nodes survive unchanged",
              {"vtkMRMLModelNode1", "vtkMRMLModelDisplayNode1",
               "vtkMRMLModelStorageNode1", "vtkMRMLViewNode1"} <= kept)
        check("no id is duplicated after splicing",
              len([el.get("id") for el in root]) == len({el.get("id") for el in root}))

        # The prefix trap: Node1 must not have been rewritten inside Node10.
        recon = by_name["ErrorMap_Reconstructed_vs_GT"]
        frac = by_name["ErrorMap_Fractured_vs_GT"]
        check("references were remapped, not left dangling",
              orbital.ID_MARKER in recon.get("references"))
        check("Node1 and Node10 did not collapse onto one another",
              recon.get("references") != frac.get("references"))
        display_ids = {el.get("id") for el in spliced if el.tag == "ModelDisplay"}
        for model in (recon, frac):
            for ref in model.get("references").split(";"):
                if ref.startswith("display:"):
                    check("%s points at a display node that exists"
                          % model.get("name"), ref.split(":", 1)[1] in display_ids)
        check("file names still point at the .vtp files",
              {el.get("fileName") for el in spliced if el.tag == "ModelStorage"}
              == {"ErrorMap_Reconstructed_vs_GT.vtp", "ErrorMap_Fractured_vs_GT.vtp"})

        # Idempotency: running twice must replace, not accumulate.
        after_first = len(list(root))
        orbital._splice_into_scene(scene, errors, names, [])
        orbital._splice_into_scene(scene, errors, names, [])
        root2 = ElementTree.parse(scene).getroot()
        check("re-running replaces rather than stacks copies",
              len(list(root2)) == after_first)
        check("the backup is still the ORIGINAL after re-runs",
              open(backup, encoding="utf-8").read() == original)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# 4. Case discovery against the real tree (skipped if it is not present)
# ---------------------------------------------------------------------------

def check_discovery():
    experiment_root = os.path.join(ROOT, orbital.EXPERIMENT_DIR)
    if not os.path.isdir(os.path.join(experiment_root, orbital.RUNS_SUBDIR)):
        print("SKIP  no Experiments tree here -- discovery not checked")
        return
    cases = orbital.discover_cases(experiment_root)
    check("cases are discovered", len(cases) > 0)
    with_gt = [c for c in cases if os.path.isfile(orbital.ground_truth_path(c))]
    print("      %d case(s), %d with a ground-truth label" % (len(cases), len(with_gt)))
    check("every case resolves a subject", all(c["subject"] for c in cases))
    check("every case has both segmentation files",
          all(os.path.isfile(os.path.join(c["scene_dir"], f))
              for c in cases for f in (orbital.RECONSTRUCTED_FILE, orbital.FRACTURED_FILE)))
    check("every case has a ground truth", len(with_gt) == len(cases))


# ---------------------------------------------------------------------------
# 5. The write gate.
#
# Regression for a real defect: slicer.util.saveScene("....mrml") writes ONLY
# the scene XML -- qSlicerSceneWriter::writeToMRML is SetURL + Commit(), and
# Commit() never asks a storage node to write its data. The first version
# assumed it did, so every case's scene.mrml was edited to reference .vtp files
# that did not exist, and the damage only surfaced when a run's scene was
# opened. _write_error_scene must therefore report success on the FILES, never
# on the return value of the save call.
# ---------------------------------------------------------------------------

class _FakeNode:
    def __init__(self, name, path):
        self._name, self._storage = name, _FakeStorage(path)

    def GetName(self):
        return self._name

    def GetStorageNode(self):
        return self._storage


class _FakeStorage:
    def __init__(self, path):
        self._path = path

    def GetFileName(self):
        return self._path


def check_write_gate():
    workdir = tempfile.mkdtemp(prefix="ofr_write_")
    try:
        good = os.path.join(workdir, "ErrorMap_Reconstructed_vs_GT.vtp")
        bad = os.path.join(workdir, "ErrorMap_Fractured_vs_GT.vtp")
        ours = [_FakeNode("ErrorMap_Reconstructed_vs_GT", good),
                _FakeNode("ErrorMap_Fractured_vs_GT", bad)]

        util = sys.modules["slicer"].util
        util.saveScene = lambda path: open(path, "w").write("<MRML/>") or True

        # Slicer keeps ~20 built-in colour tables as singletons; some point INTO
        # THE APPLICATION'S OWN INSTALL. Writing to one would corrupt Slicer, and
        # asking the scene "which colour tables are there?" returned all of them.
        # Nothing here may reach a node the caller did not hand in.
        installed = os.path.join(workdir, "SlicerInstall_Labels.txt")
        open(installed, "w").write("SLICER'S OWN COLOUR TABLE")
        builtin = _FakeNode("Labels", installed)
        util.getNodesByClass = lambda cls: ours + [builtin]

        saved = []

        def _record(node, path):
            saved.append(node.GetName())
            open(path, "w").write("x")
            return True

        util.saveNode = _record
        notes = []
        check("writes exactly the nodes it was handed",
              orbital._write_error_scene(workdir, ours, notes) is True)
        check("and NOTHING that merely lives in the scene",
              sorted(saved) == ["ErrorMap_Fractured_vs_GT",
                                "ErrorMap_Reconstructed_vs_GT"])
        check("Slicer's own installed colour file is untouched",
              open(installed).read() == "SLICER'S OWN COLOUR TABLE")
        check("and it is quiet on success", notes == [])
        os.remove(good)
        os.remove(bad)

        # The original defect: every save reports success, and no file appears.
        util.saveNode = lambda node, path: True
        notes = []
        check("a save that writes NOTHING is not reported as success",
              orbital._write_error_scene(workdir, ours, notes) is False)
        check("and it says which node", any("ErrorMap_Reconstructed_vs_GT" in n
                                            for n in notes))

        # One file appears, the other does not -> still a failure.
        def _half(node, path):
            if path == good:
                open(path, "w").write("x")
            return True
        util.saveNode = _half
        notes = []
        check("one missing file out of two is still a failure",
              orbital._write_error_scene(workdir, ours, notes) is False)
        check("and it names the MISSING one, not the written one",
              any("ErrorMap_Fractured_vs_GT" in n for n in notes)
              and not any("ErrorMap_Reconstructed_vs_GT" in n for n in notes))

        # A save that raises must be caught and reported, not propagated.
        def _raises(node, path):
            raise RuntimeError("disk full")
        util.saveNode = _raises
        os.remove(good)
        notes = []
        check("a raising save is caught",
              orbital._write_error_scene(workdir, ours, notes) is False)
        check("and the reason is kept", any("disk full" in n for n in notes))

        check("an empty node list is a failure, not a silent success",
              orbital._write_error_scene(workdir, [], []) is False)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# 6. numpy -> VTK handover.
#
# Regression for a crash that took Slicer down three times: numpy_to_vtk
# defaults to deep=0, which makes the VTK array a VIEW on the numpy buffer. Ours
# was handed a temporary, so CPython freed it on return and the vtkFloatArray
# was left pointing at freed memory -- a use-after-free that reads correctly
# until the allocator reuses the block, and then faults inside vtkCommon during
# an unrelated case minutes later (0xc0000005, vtkCommon-9.5.dll).
#
# There is no vtk here to test against, so this is checked at the source level:
# it is a footgun with a single correct spelling, and the cost of getting it
# wrong is a hard crash with no Python traceback.
# ---------------------------------------------------------------------------

def check_numpy_to_vtk_is_deep():
    import ast
    import glob

    def literal(node):
        """The value of a literal AST node, across Python versions.

        3.8+ parses ``deep=1`` to ``ast.Constant(value=1)``; 3.7 -- which is what
        this repository's development interpreter is -- parses it to
        ``ast.Num(n=1)``. Reading only ``.value`` made this check report the
        correct code as broken, which is the worst kind of check.
        """
        for attribute in ("value", "n"):
            if hasattr(node, attribute):
                return getattr(node, attribute)
        return None

    offenders = []
    checked = 0
    roots = [os.path.join(ROOT, "SlicerAIAgentLib"), os.path.join(ROOT, "scripts")]
    files = []
    for root in roots:
        files.extend(glob.glob(os.path.join(root, "**", "*.py"), recursive=True))
    for path in files:
        try:
            tree = ast.parse(open(path, encoding="utf-8").read())
        except Exception:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "attr", None) or getattr(node.func, "id", None)
            if name not in ("numpy_to_vtk", "numpy_to_vtkIdTypeArray"):
                continue
            checked += 1
            deep = [k for k in node.keywords if k.arg == "deep"]
            ok = bool(deep) and literal(deep[0].value) in (1, True)
            # deep may also be passed positionally: numpy_to_vtk(a, 1)
            if not ok and len(node.args) >= 2:
                ok = literal(node.args[1]) in (1, True)
            if not ok:
                offenders.append("%s:%d" % (os.path.relpath(path, ROOT), node.lineno))
    print("      %d numpy_to_vtk call(s) found" % checked)
    check("every numpy_to_vtk copies (deep=1); a view onto a temporary is a "
          "use-after-free%s" % (" -- " + ", ".join(offenders) if offenders else ""),
          not offenders)

    # arrayFromVolume returns a VIEW on VTK-owned memory, and updateVolumeFromArray
    # reallocates exactly that buffer (AllocateScalars). Holding the view across
    # it dangles. The rule is enforced structurally: one wrapper copies, and
    # nothing else in the module may call the raw API.
    source = open(os.path.join(ROOT, "SlicerAIAgentLib", "experiments",
                               "orbital.py"), encoding="utf-8").read()
    tree = ast.parse(source)
    callers = []
    for func in ast.walk(tree):
        if not isinstance(func, ast.FunctionDef):
            continue
        for node in ast.walk(func):
            if isinstance(node, ast.Call) and \
                    getattr(node.func, "attr", None) == "arrayFromVolume":
                callers.append(func.name)
    check("arrayFromVolume is only reached through the copying wrapper "
          "(callers: %s)" % (", ".join(sorted(set(callers))) or "none"),
          sorted(set(callers)) in ([], ["_volume_array_copy"]))

    # RemoveNode must be reached only through _drop_node, which holds a live
    # reference and checks IsNodePresent. Resolving ids from a snapshot and
    # removing them in a loop is what crashed the batch: removing a segmentation
    # cascades to its display and storage nodes, so a precomputed id can name a
    # node that is already gone -- and RemoveNode's own guard against that is
    # compiled out of release builds, leaving an access violation.
    removers = []
    for func in ast.walk(tree):
        if not isinstance(func, ast.FunctionDef):
            continue
        for node in ast.walk(func):
            if isinstance(node, ast.Call) and \
                    getattr(node.func, "attr", None) in ("RemoveNode", "GetNodeByID"):
                removers.append("%s -> %s" % (func.name, node.func.attr))
    check("nodes are removed only through _drop_node, never by resolving an id "
          "(%s)" % (", ".join(sorted(set(removers))) or "none"),
          removers and all(r.startswith("_drop_node ") for r in removers))

    # Every module-private helper that is CALLED must also be DEFINED. A bulk
    # edit that deletes one function can silently take its neighbour with it,
    # and nothing else here would notice: the file still parses, and the AST
    # checks above match patterns rather than resolve names. The failure would
    # be a NameError on the first case, after the user has restarted Slicer.
    # Nested functions count (``_values`` lives inside ``_surface_distances``),
    # and so do import aliases (``discover_cases as _discover_cases``).
    defined = {n.name for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            defined.update((alias.asname or alias.name) for alias in node.names)
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id.startswith("_"):
            called.add(node.func.id)
    # Locals and parameters are never named like module helpers here, so a bare
    # _name(...) call is a module-level function or a mistake.
    undefined = sorted(called - defined - {"_"})
    check("every _helper() called is defined in the module%s"
          % (" -- MISSING: " + ", ".join(undefined) if undefined else ""),
          not undefined)

    # A filter's output is owned by its executive and references its producer,
    # so it must never escape the scope its filter lives in nor be wired into a
    # second filter. Three separate instances of this were crashing Slicer.
    # Legal uses: inside _detached_output (which copies), or read straight into
    # numpy by _values (which copies). Anything else is the defect.
    escapes = []
    for func in ast.walk(tree):
        if not isinstance(func, ast.FunctionDef) or func.name == "_detached_output":
            continue
        for node in ast.walk(func):
            if not isinstance(node, ast.Call):
                continue
            if getattr(node.func, "attr", "") not in ("GetOutput",
                                                      "GetSecondDistanceOutput"):
                continue
            # Allowed only as the direct argument of _values(...).
            parent_ok = False
            for outer in ast.walk(func):
                if isinstance(outer, ast.Call) and \
                        getattr(outer.func, "id", None) == "_values" and \
                        any(a is node for a in outer.args):
                    parent_ok = True
            if not parent_ok:
                escapes.append("%s:%d" % (func.name, node.lineno))
    check("a filter's output never escapes its filter (use _detached_output)%s"
          % (" -- " + ", ".join(escapes) if escapes else ""),
          not escapes)


# ---------------------------------------------------------------------------
# 7. Cropping the ground truth before it is meshed.
#
# The label arrives on the full CT grid; only ~1/66th of it produces any
# surface. Meshing all of it wasted every case and killed the batch on the one
# case large enough (068: 110 M voxels). Cropping is exact -- but the origin
# shift that goes with it is the kind of mistake that does not raise: it moves
# the ground truth in world space and quietly returns wrong distances. So the
# invariant checked here is world-position invariance, not the box itself.
# ---------------------------------------------------------------------------

def check_crop():
    # A deliberately awkward IJK->RAS: anisotropic, flipped, and rotated, so a
    # crop that "works" only for axis-aligned identity spacing fails here.
    matrix = [[0.0, -0.43, 0.0, 12.5],
              [0.6, 0.0, 0.0, -30.25],
              [0.0, 0.0, -1.7, 700.0],
              [0.0, 0.0, 0.0, 1.0]]

    def to_world(m, ijk):
        i, j, k = ijk
        return tuple(m[a][0] * i + m[a][1] * j + m[a][2] * k + m[a][3]
                     for a in range(3))

    volume = np.zeros((40, 50, 60), dtype=np.uint8)          # k, j, i
    volume[12:19, 21:27, 33:41] = 1
    bounds = orbital.crop_bounds(volume.shape, np.nonzero(volume), margin=2)
    (k0, k1), (j0, j1), (i0, i1) = bounds
    check("the box covers the label with the margin",
          (k0, k1, j0, j1, i0, i1) == (10, 21, 19, 29, 31, 43))
    check("the crop keeps every labelled voxel",
          int(volume[k0:k1, j0:j1, i0:i1].sum()) == int(volume.sum()))

    shifted = orbital.cropped_ijk_to_ras(matrix, (i0, j0, k0))
    check("the rotation/scale block is untouched",
          all(shifted[r][c] == matrix[r][c] for r in range(3) for c in range(3)))

    # The invariant that matters: a voxel keeps its world position.
    worst = 0.0
    for kk in range(k0, k1, 3):
        for jj in range(j0, j1, 3):
            for ii in range(i0, i1, 3):
                before = to_world(matrix, (ii, jj, kk))
                after = to_world(shifted, (ii - i0, jj - j0, kk - k0))
                worst = max(worst, max(abs(a - b) for a, b in zip(before, after)))
    check("every voxel keeps its world position after cropping (worst %.2e mm)"
          % worst, worst < 1e-9)

    # Clamping at the edges, and the empty case.
    edge = np.zeros((5, 5, 5), dtype=np.uint8)
    edge[0, 0, 0] = 1
    edge[4, 4, 4] = 1
    check("the box is clamped to the array",
          orbital.crop_bounds(edge.shape, np.nonzero(edge), margin=2)
          == ((0, 5), (0, 5), (0, 5)))
    check("an empty label yields no box rather than a degenerate one",
          orbital.crop_bounds((4, 4, 4), np.nonzero(np.zeros((4, 4, 4))), 2) is None)

    # And the real payoff, on the case that crashed.
    gt = os.path.join(ROOT, orbital.EXPERIMENT_DIR, orbital.DATASET_SUBDIR,
                      "068", "068_Label.nii.gz")
    if os.path.isfile(gt):
        import gzip
        import struct
        raw = gzip.open(gt, "rb").read()
        dims = struct.unpack("<8h", raw[40:56])
        offset, = struct.unpack("<f", raw[108:112])
        data = np.frombuffer(raw, dtype=np.uint16,
                             offset=int(offset))[:dims[1] * dims[2] * dims[3]]
        data = data.reshape(dims[3], dims[2], dims[1])
        box = orbital.crop_bounds(data.shape, np.nonzero(data))
        kept = (box[0][1] - box[0][0]) * (box[1][1] - box[1][0]) * (box[2][1] - box[2][0])
        print("      case 068: %d -> %d voxels (%.0fx less to mesh)"
              % (data.size, kept, data.size / float(kept)))
        check("case 068 is cropped to well under a typical case's full volume",
              kept < 25_000_000 / 4)


def main():
    check_statistics()
    print()
    check_improvement()
    print()
    check_splicer()
    print()
    check_write_gate()
    print()
    check_numpy_to_vtk_is_deep()
    print()
    check_crop()
    print()
    check_discovery()
    print()
    if FAILURES:
        print("FAILED (%d):" % len(FAILURES))
        for failure in FAILURES:
            print("  - " + failure)
        return 1
    print("All orbital-analysis checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
