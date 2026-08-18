#!/usr/bin/env python3
"""Check the CranialImplantPlanning DSC / HD95 / bDSC analysis, outside Slicer.

    python scripts/check_cranial_analysis.py              # fixtures + 3 real cases
    python scripts/check_cranial_analysis.py --cases 10   # more real cases
    python scripts/check_cranial_analysis.py --verbose

`SlicerAIAgentLib/experiments/cranial.py` keeps every number in pure numpy/scipy
and imports Slicer only inside the functions that draw the colour map, so the
part that decides what goes in the paper can be exercised without launching an
application. That matters more here than usual, because all three metrics fail
*quietly*: a wrong segment, a wrong skull or an inverted spacing matrix each
produce a plausible number rather than an error.

Five groups:

* **Fixtures** -- DSC/Jaccard against hand-computable answers, and the geometry
  helpers (spacing from an IJK->RAS matrix, the metric window, the border band).
* **The crop is exact** -- the cropped metric window must reproduce the numbers a
  full-volume computation gives, bit for bit, on real data. It is a 5x speed-up
  that would otherwise be a silent approximation.
* **Segment resolution** -- the shipped .seg.nrrd files must resolve
  `Ground Truth`, `Skull` and `Implant` by NAME. Reading the result as non-zero
  instead of `== Implant` is the single most likely coding error here and it
  looks like a pipeline failure, not a bug.
* **The defective skull** -- the skull bDSC bands against must be the one with the
  hole: its intersection with the ground-truth implant has to be 0.
* **Real cases** -- the metrics land in the range the AutoImplant 2021 paper
  reports, and bDSC >= DSC on most cases as the paper observes.

Exit code 0 when everything passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import glob
import importlib
import os
import sys
import types

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAILURES = []
CHECKS = [0]


def fail(message):
    FAILURES.append(message)


def check(condition, message):
    CHECKS[0] += 1
    if not condition:
        fail(message)
    return bool(condition)


def close(a, b, tol=1e-9):
    return a is not None and b is not None and abs(float(a) - float(b)) <= tol


def _load():
    """Import the module with slicer/qt/vtk/ctk stubbed, as the RSA check does."""
    for name in ("slicer", "qt", "vtk", "ctk"):
        sys.modules.setdefault(name, types.ModuleType(name))
    sys.modules["slicer"].util = types.ModuleType("slicer.util")
    sys.path.insert(0, ROOT)
    return importlib.import_module("SlicerAIAgentLib.experiments.cranial")


# ---------------------------------------------------------------------------
# 1. Fixtures
# ---------------------------------------------------------------------------

def check_fixtures(cranial, verbose):
    a = np.zeros((6, 6, 6), dtype=bool)
    b = np.zeros((6, 6, 6), dtype=bool)
    a[1:4, 1:4, 1:4] = True          # 27 voxels
    b[2:5, 2:5, 2:5] = True          # 27 voxels, 8 shared

    check(close(cranial.dice(a, b), 2.0 * 8 / 54),
          "dice of two offset 3x3x3 cubes must be 2*8/54, got %r" % cranial.dice(a, b))
    check(close(cranial.jaccard(a, b), 8.0 / 46),
          "jaccard must be 8/46, got %r" % cranial.jaccard(a, b))
    check(close(cranial.dice(a, a), 1.0), "dice of a mask with itself must be 1")
    check(cranial.dice(np.zeros((2, 2, 2), bool), np.zeros((2, 2, 2), bool)) is None,
          "dice of two empty masks must be None, not 0 or a ZeroDivisionError")

    # Spacing comes from the COLUMN NORMS of IJK->RAS. Inverting it instead gives
    # voxels-per-mm, which scales every distance and leaves DSC untouched.
    matrix = [[-0.5, 0, 0, 10.0], [0, -0.5, 0, 20.0], [0, 0, 0.75, -5.0], [0, 0, 0, 1]]
    spacing = cranial.spacing_mm(matrix)
    check(np.allclose(spacing, [0.75, 0.5, 0.5]),
          "spacing_mm must be (k,j,i) = (0.75, 0.5, 0.5), got %s" % spacing)
    check(close(cranial.voxel_volume_mm3(matrix), 0.75 * 0.5 * 0.5),
          "voxel volume must be the product of the spacings")

    mask = np.zeros((20, 20, 20), dtype=bool)
    mask[8:12, 8:12, 8:12] = True
    window = cranial.metric_window(mask, margin=3)
    check(all(w.start == 5 and w.stop == 15 for w in window),
          "metric_window must be the bbox grown by the margin, got %s" % (window,))
    check(cranial.metric_window(np.zeros((4, 4, 4), bool))[0] == slice(0, 4),
          "an empty mask must give the whole array, not an error")

    # The border band: within t of the skull, measured on the skull's complement.
    skull = np.zeros((1, 1, 20), dtype=bool)
    skull[0, 0, 0] = True
    band = cranial.border_mask(skull, 3.0)
    check(bool(band[0, 0, 3]) and not bool(band[0, 0, 4]),
          "a t=3 band must include voxel 3 and exclude voxel 4")
    band_mm = cranial.border_mask(skull, 3.0, spacing=(1.0, 1.0, 0.5))
    check(bool(band_mm[0, 0, 6]) and not bool(band_mm[0, 0, 7]),
          "with 0.5 mm voxels a 3 mm band must reach voxel 6, not 7")

    check(cranial._round(float("nan")) is None, "_round must turn NaN into None")
    if verbose:
        print("  fixtures exercised")
    print("fixtures: exercised")


# ---------------------------------------------------------------------------
# 2-5. Real data
# ---------------------------------------------------------------------------

def _case_dirs(limit):
    pattern = os.path.join(ROOT, "Experiments", "CranialImplantPlanning",
                           "Overall_Performance", "*", "Statistic", "scene")
    return sorted(glob.glob(pattern))[:limit]


def _full_volume_metrics(cranial, gt, implant, skull, matrix):
    """The same three numbers WITHOUT the crop, for the exactness comparison."""
    from scipy import ndimage

    spacing = cranial.spacing_mm(matrix)
    band = ndimage.distance_transform_edt(
        np.logical_not(skull)) <= cranial.BORDER_DISTANCE_VOXELS
    bdsc = cranial.dice(np.logical_and(gt, band), np.logical_and(implant, band))
    to_gt, to_implant = cranial.surface_distances_mm(gt, implant, spacing)
    both = np.concatenate([to_gt, to_implant])
    return (cranial.dice(gt, implant), bdsc, float(np.percentile(both, 95)))


def check_real_cases(cranial, limit, verbose):
    scenes = _case_dirs(limit)
    if not check(scenes, "no CranialImplantPlanning cases found under Experiments/"):
        return

    dsc_values, bdsc_values, hd95_values = [], [], []
    for scene in scenes:
        subject = os.path.basename(os.path.dirname(os.path.dirname(scene)))
        subject = subject.split("_")[1] if "_" in subject else subject
        gt_file = os.path.join(scene, cranial.GROUND_TRUTH_FILE)
        result_file = os.path.join(scene, cranial.RESULT_FILE)
        if not check(os.path.isfile(gt_file) and os.path.isfile(result_file),
                     "%s: missing a segmentation file" % subject):
            continue

        # --- segments resolve BY NAME -----------------------------------
        gt_labels = cranial.segment_label_values(gt_file)
        result_labels = cranial.segment_label_values(result_file)
        check(cranial.GROUND_TRUTH_SEGMENT in gt_labels,
              "%s: the ground truth has no segment named %r (has: %s)"
              % (subject, cranial.GROUND_TRUTH_SEGMENT, sorted(gt_labels)))
        check(cranial.IMPLANT_SEGMENT in result_labels
              and cranial.SKULL_SEGMENT in result_labels,
              "%s: the result must hold BOTH %r and %r (has: %s)"
              % (subject, cranial.SKULL_SEGMENT, cranial.IMPLANT_SEGMENT,
                 sorted(result_labels)))
        if cranial.IMPLANT_SEGMENT not in result_labels:
            continue

        gt, gt_matrix = cranial._read_mask(gt_file, cranial.GROUND_TRUTH_SEGMENT, 1)
        implant, matrix = cranial._read_mask(result_file, cranial.IMPLANT_SEGMENT)
        skull, _ = cranial._read_mask(result_file, cranial.SKULL_SEGMENT)

        check(gt.shape == implant.shape and np.allclose(gt_matrix, matrix, atol=1e-6),
              "%s: the ground truth and the result must share a grid" % subject)

        # --- the skull really is the DEFECTIVE one ----------------------
        overlap = int(np.logical_and(gt, skull).sum())
        check(overlap == 0,
              "%s: the %r segment overlaps the ground-truth implant by %d voxels "
              "-- it is not the defective skull, so bDSC would band the wrong "
              "region" % (subject, cranial.SKULL_SEGMENT, overlap))

        # --- reading the result as non-zero must be visibly WRONG -------
        naive = cranial.dice(gt, implant | skull)
        proper = cranial.dice(gt, implant)
        check(proper > naive,
              "%s: DSC against the implant (%.4f) must beat DSC against every "
              "non-zero voxel (%.4f) -- if not, the segment selection is moot"
              % (subject, proper, naive))

        row = cranial.case_metrics(gt, implant, skull, matrix)
        dsc_values.append(row["dsc"])
        bdsc_values.append(row["bdsc"])
        hd95_values.append(row["hd95_mm"])

        # --- the crop is exact, not an approximation --------------------
        full_dsc, full_bdsc, full_hd95 = _full_volume_metrics(
            cranial, gt, implant, skull, matrix)
        # Compared against the ROUNDED reference: case_metrics rounds every value
        # it reports, so an unrounded comparison would fail on the rounding and
        # say nothing about the crop.
        check(close(row["dsc"], round(full_dsc, 4), 1e-9),
              "%s: cropped DSC %r != full-volume %r" % (subject, row["dsc"], full_dsc))
        check(close(row["bdsc"], round(full_bdsc, 4), 1e-9),
              "%s: cropped bDSC %r != full-volume %r -- the crop margin is "
              "smaller than the border distance" % (subject, row["bdsc"], full_bdsc))
        check(close(row["hd95_mm"], round(full_hd95, 3), 1e-9),
              "%s: cropped HD95 %r != full-volume %r -- a surface fell outside "
              "the window" % (subject, row["hd95_mm"], full_hd95))

        check(row["gt_in_skull_voxels"] == 0,
              "%s: gt_in_skull_voxels must be 0" % subject)

        # The two one-directional shares are what distinguish "the implant is
        # too small" from "the implant is in the wrong place" -- HD95 pools both
        # directions and cannot. They must be present, be percentages, and be
        # consistent with the means they summarise.
        covered = row.get(cranial.GT_COVERED_COLUMN)
        on_gt = row.get(cranial.IMPLANT_ON_GT_COLUMN)
        check(covered is not None and 0.0 <= covered <= 100.0,
              "%s: %s must be a percentage, got %r"
              % (subject, cranial.GT_COVERED_COLUMN, covered))
        check(on_gt is not None and 0.0 <= on_gt <= 100.0,
              "%s: %s must be a percentage, got %r"
              % (subject, cranial.IMPLANT_ON_GT_COLUMN, on_gt))
        # Whichever direction has the larger mean distance must have the smaller
        # share within tolerance; if not, one of the two pairs is transposed.
        if not close(row["mean_gt_to_implant_mm"], row["mean_implant_to_gt_mm"], 1e-6):
            gt_worse = row["mean_gt_to_implant_mm"] > row["mean_implant_to_gt_mm"]
            check(gt_worse == (covered < on_gt),
                  "%s: the directional means and the directional shares "
                  "disagree (gt->implant %.3f mm / %.2f%%, implant->gt %.3f mm / "
                  "%.2f%%) -- one pair is transposed"
                  % (subject, row["mean_gt_to_implant_mm"], covered,
                     row["mean_implant_to_gt_mm"], on_gt))
        check(row["voxel_volume_mm3"] and row["voxel_volume_mm3"] > 0,
              "%s: voxel volume must be read from the file, not assumed" % subject)
        if verbose:
            print("  %-7s DSC=%.4f bDSC=%.4f HD95=%.3f mm ASSD=%.3f mm"
                  % (subject, row["dsc"], row["bdsc"], row["hd95_mm"], row["assd_mm"]))

    if not dsc_values:
        return

    # --- the cohort lands where the paper says ---------------------------
    check(all(0.0 <= value <= 1.0 for value in dsc_values),
          "every DSC must be in [0, 1]")
    check(all(0.0 <= value <= 1.0 for value in bdsc_values),
          "every bDSC must be in [0, 1]")
    check(max(hd95_values) < 25.0,
          "HD95 of %.2f mm is far outside the AutoImplant range (1.3-7.4 mm) -- "
          "the usual cause is spacing taken from the INVERSE of the IJK->RAS "
          "matrix, which scales every distance" % max(hd95_values))
    higher = sum(1 for d, b in zip(dsc_values, bdsc_values) if b >= d)
    check(higher >= len(dsc_values) / 2.0,
          "the paper reports 'generally bDSC are higher than DSC'; here only "
          "%d of %d cases" % (higher, len(dsc_values)))
    print("real cases: %d scored, DSC %.4f-%.4f, HD95 %.2f-%.2f mm, bDSC>=DSC in %d"
          % (len(dsc_values), min(dsc_values), max(dsc_values),
             min(hd95_values), max(hd95_values), higher))


def check_summary(cranial, verbose):
    rows = [{"dsc": 0.9, "bdsc": 0.95, "hd95_mm": 2.0},
            {"dsc": 0.7, "bdsc": 0.75, "hd95_mm": 4.0},
            {"dsc": None, "error": "boom"}]
    summary = {row["metric"]: row for row in cranial.summary_rows(rows)}
    dsc = summary["DSC"]
    check(dsc["cases"] == 2, "a row with no dsc must not be counted, got %r" % dsc["cases"])
    check(close(dsc["mean"], 0.8) and close(dsc["median"], 0.8),
          "mean/median of 0.9 and 0.7 must be 0.8, got %r/%r" % (dsc["mean"], dsc["median"]))
    check(close(dsc["min"], 0.7) and close(dsc["max"], 0.9), "min/max wrong")
    empty = cranial.summary_rows([{"dsc": None}])
    check(empty[0]["cases"] == 0, "an all-empty cohort must report 0 cases, not crash")
    if verbose:
        print("  summary exercised")
    print("summary: exercised")


def check_wiring(cranial, verbose):
    panel = os.path.join(ROOT, "SlicerAIAgentLib", "experiments", "cranial_panel.py")
    check(os.path.isfile(panel), "cranial_panel.py is missing")
    registry = os.path.join(ROOT, "SlicerAIAgentLib", "app", "widget_experiments.py")
    with open(registry, encoding="utf-8") as fh:
        text = fh.read()
    check("cranial_panel" in text,
          "cranial_panel is not listed in _PANEL_MODULES, so the button never "
          "appears in the Experiments section")
    check(cranial.METRIC_MARGIN_VOXELS >= cranial.BORDER_DISTANCE_VOXELS,
          "the metric window's margin (%s) must be at least the border distance "
          "(%s) or the cropped bDSC stops being exact"
          % (cranial.METRIC_MARGIN_VOXELS, cranial.BORDER_DISTANCE_VOXELS))

    # THE regression guard. orbital._load_segmentation_surface meshes
    # GetNthSegmentID(0) -- the FIRST segment -- and segment 0 of
    # "Cranial Implant Result.seg.nrrd" is Skull, not Implant. Using it here
    # produced a colour map of the 2.1-million-voxel skull: the wrong surface,
    # and by far the slowest step in the batch. The map must be built from the
    # arrays that _read_mask already resolved BY NAME.
    source = os.path.join(ROOT, "SlicerAIAgentLib", "experiments", "cranial.py")
    with open(source, encoding="utf-8") as fh:
        text = fh.read()
    # By AST, not by substring: the docstring of _surface_from_mask names the
    # function precisely to say why it is not used, and a substring test would
    # fire on that explanation.
    import ast
    called = {
        node.func.attr
        for node in ast.walk(ast.parse(text))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    check("_load_segmentation_surface" not in called,
          "cranial.py must not CALL orbital._load_segmentation_surface: it meshes "
          "segment 0, which is Skull in the result file, not Implant")
    check("_load_label_surface" not in called,
          "cranial.py must not call orbital._load_label_surface either -- the "
          "ground truth here is a .seg.nrrd, not a label volume")
    check("_surface_from_mask" in text,
          "the error map must be built from the named-segment arrays via "
          "_surface_from_mask")
    print("wiring: exercised")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=int, default=3)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    cranial = _load()
    check_fixtures(cranial, args.verbose)
    check_summary(cranial, args.verbose)
    check_wiring(cranial, args.verbose)
    check_real_cases(cranial, args.cases, args.verbose)

    print("checks run: %d" % CHECKS[0])
    if FAILURES:
        print("\nFAILURES (%d):" % len(FAILURES))
        for line in FAILURES:
            print("  " + line)
        return 1
    print("all cranial-analysis checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
