# -*- coding: utf-8 -*-
"""Give every saved PedicleScrewPlanner run the per-screw slice views it lacks.

Picking a screw in "Choose the puncture site" reformats the Red and Yellow views
onto it (``PlanningMeasurementsStep.sSelector_chosen`` -> ``Helper.UpdateSlicePlane``).
A scene has ONE Red slice node, so each screw overwrites the last, and a saved
scene carries only the screw that happened to be selected at save time. Reopened,
the plan shows four screws and one screw's view; the rest have to be re-aimed by
hand, at an angle nothing on screen states.

The extension now writes each screw's two matrices onto its own ``Isthmus-<n>``
markup as node attributes (``PedicleScrewPlanner.saveScrewView``), so future runs
keep all of them. This script puts the same attributes into the runs already on
disk, so they need not be re-run. Afterwards, in a reopened scene:

    import PedicleScrewPlanner as P
    P.screwViews()            # [(0, 'T11_L', True), (1, 'T11_R', True), ...]
    P.applyScrewView('T11_L') # the Red view is that screw's again

**The matrices are recomputed, not estimated**, by replaying the extension's own
arithmetic on the landmarks the run saved: ``Helper.UpdateSlicePlane``'s plane
construction followed by ``vtkMRMLSliceNode::SetSliceToRASByNTP`` (case 0), which
re-orthogonalises T against N before writing the columns [T, C, N]. That
replication is checked against the scene on every run: the LAST screw's computed
Red matrix must equal the Red slice node the run actually saved, since that is
the screw whose view was on screen. On the 55 runs here it agrees to 5e-7 on the
direction cosines and 4e-4 mm on the origin -- the precision the .mrml prints.

Safety: ``scene.mrml`` is backed up to ``scene.mrml.orig`` once, an existing
backup is never overwritten, the edit is idempotent, and ``--dry-run`` reports
without writing. A run whose last-screw check fails is refused, not guessed at.

    python scripts/retrofit_pedicle_screwviews.py --dry-run
    python scripts/retrofit_pedicle_screwviews.py
"""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Must match PedicleScrewPlanner.py, or a retrofitted scene and a re-run scene
#: would disagree about where the views live and how they are written.
RED_ATTR = "PedicleScrewPlanner.RedSliceToRAS"
YELLOW_ATTR = "PedicleScrewPlanner.YellowSliceToRAS"
NODE_FORMAT = "Isthmus-%d"
NUMBER_FORMAT = "%.9g"

#: The landmark node the screw pairs come from: three points per vertebra
#: (anterior, left entry, right entry), which ``Helper.Pdata3`` turns into two
#: screws per vertebra.
LANDMARKS = "T.mrk.json"

#: How far the last screw's recomputed Red matrix may sit from the one the run
#: saved. The .mrml prints six significant digits, so the floor is ~1e-6 on a
#: direction cosine and ~1e-4 mm on an origin; anything above this is not a
#: rounding difference and means the replay is wrong for that run.
AXIS_TOLERANCE = 1e-4
ORIGIN_TOLERANCE = 1e-2

RUNS = os.path.join(ROOT, "Experiments", "PedicleScrewPlanner",
                    "Overall_Performance")


def _read_landmarks(path):
    """The T landmarks as an (n, 3) RAS array. Markups JSON is written in LPS."""
    markup = json.load(io.open(path, encoding="utf-8"))["markups"][0]
    points = np.array([p["position"] for p in markup["controlPoints"]],
                      dtype=float)
    if str(markup.get("coordinateSystem", "LPS")).upper().startswith("L"):
        points = points * np.array([-1.0, -1.0, 1.0])
    return points


def _slice_to_ras(normal, transverse, position):
    """``vtkMRMLSliceNode::SetSliceToRASByNTP`` with Orientation 0, exactly.

    The order matters and is easy to get wrong: C = N x T, then T = C x N, and
    only then are all three normalised. Skipping the re-orthogonalisation of T
    leaves the matrix up to 0.06 degrees off on these runs -- small enough to
    look like rounding and large enough not to be.
    """
    n = np.asarray(normal, dtype=float)
    t = np.asarray(transverse, dtype=float)
    c = np.cross(n, t)
    t = np.cross(c, n)
    n = n / np.linalg.norm(n)
    t = t / np.linalg.norm(t)
    c = c / np.linalg.norm(c)
    matrix = np.eye(4)
    matrix[:3, 0] = t
    matrix[:3, 1] = c
    matrix[:3, 2] = n
    matrix[:3, 3] = np.asarray(position, dtype=float)
    return matrix


def _plane(points, first, second):
    """``Helper.UpdateSlicePlane``: a plane through three points, as a matrix."""
    stacked = np.array(points, dtype=float).T           # columns are the points
    normal = np.cross(stacked[:, 1] - stacked[:, 0], stacked[:, 2] - stacked[:, 0])
    transverse = stacked[:, first] - stacked[:, second]
    return _slice_to_ras(normal, transverse, stacked.mean(axis=1))


def screw_views(landmarks):
    """``[(index, red, yellow), ...]`` for every screw the landmarks define.

    Mirrors the two lines in ``sSelector_chosen``: for screw ``index`` of
    vertebra ``index // 2``, Pa is that vertebra's anterior landmark and Pz its
    left or right entry, and the third point of each plane is built the way the
    step builds it -- Pz's R with Pa's A and S for Red, Pa shifted 10 mm inferior
    for Yellow.
    """
    views = []
    for index in range(2 * (len(landmarks) // 3)):
        vertebra, side = index // 2, index % 2
        pa = landmarks[3 * vertebra]
        pz = landmarks[3 * vertebra + 1 + side]
        red = _plane([pz, pa, [pz[0], pa[1], pa[2]]], 1, 2)
        yellow = _plane([pz, pa, [pa[0], pa[1], pa[2] - 10.0]], 2, 1)
        views.append((index, red, yellow))
    return views


def _format(matrix):
    return " ".join(NUMBER_FORMAT % v for v in np.asarray(matrix).reshape(16))


def _element(text, tag, attribute, value):
    pattern = re.compile(r"[ \t]*<%s\b[^>]*></%s>\n" % (tag, tag))
    for match in pattern.finditer(text):
        if re.search(r'\b%s="%s"' % (attribute, re.escape(value)), match.group(0)):
            return match
    return None


def _saved_red(text):
    """The Red slice matrix the run saved, or None."""
    match = re.search(r'<Slice\b[^>]*layoutName="Red"[^>]*></Slice>', text)
    if not match:
        return None
    found = re.search(r'sliceToRAS="([^"]*)"', match.group(0))
    if not found:
        return None
    return np.array([float(v) for v in found.group(1).split()]).reshape(4, 4)


def _with_attributes(element, pairs):
    """The element carrying exactly these node attributes.

    Slicer joins them with ';' and writes NO trailing separator (see
    vtkMRMLNode::WriteXML), in std::map order -- alphabetical by key. A trailing
    ';' would parse back as one extra nameless attribute, so it is not cosmetic.
    Written between 'selected' and 'references', which is where WriteXML puts the
    block.
    """
    encoded = ";".join("%s:%s" % (key, value)
                       for key, value in sorted(pairs.items()))
    if re.search(r'\battributes="', element):
        return re.sub(r'\battributes="[^"]*"', 'attributes="%s"' % encoded,
                      element, count=1)
    if " references=" in element:
        return element.replace(" references=", ' attributes="%s" references='
                               % encoded, 1)
    return element.replace(" >", ' attributes="%s" >' % encoded, 1)


def retrofit(scene_dir, dry_run=False):
    """Returns ``(status, detail)``: added / updated / skipped / error."""
    scene_path = os.path.join(scene_dir, "scene.mrml")
    landmarks_path = os.path.join(scene_dir, LANDMARKS)
    if not os.path.isfile(scene_path):
        return "error", "no scene.mrml"
    if not os.path.isfile(landmarks_path):
        return "error", "no %s" % LANDMARKS

    text = io.open(scene_path, encoding="utf-8").read()
    landmarks = _read_landmarks(landmarks_path)
    if len(landmarks) < 3 or len(landmarks) % 3:
        return "error", "%d landmarks in %s is not whole vertebrae" % (
            len(landmarks), LANDMARKS)
    views = screw_views(landmarks)

    # The run's own Red view is the last screw's, so it is the witness that this
    # replay reproduces what the extension did. Without it the other screws'
    # matrices would be an unchecked computation.
    saved = _saved_red(text)
    if saved is None:
        return "error", "no Red slice node to check the replay against"
    computed = views[-1][1]
    axis = float(np.abs(computed[:3, :3] - saved[:3, :3]).max())
    origin = float(np.abs(computed[:3, 3] - saved[:3, 3]).max())
    if axis > AXIS_TOLERANCE or origin > ORIGIN_TOLERANCE:
        return "error", ("the last screw's replayed view does not match the "
                         "saved Red slice (axis %.2e, origin %.2e mm)"
                         % (axis, origin))

    changed, missing = 0, []
    for index, red, yellow in views:
        element = _element(text, "MarkupsFiducial", "name", NODE_FORMAT % index)
        if element is None:
            missing.append(NODE_FORMAT % index)
            continue
        updated = _with_attributes(element.group(0),
                                   {RED_ATTR: _format(red),
                                    YELLOW_ATTR: _format(yellow)})
        if updated != element.group(0):
            text = text[:element.start()] + updated + text[element.end():]
            changed += 1
    if missing:
        return "error", "no markup named %s" % ", ".join(missing)
    if not changed:
        return "skipped", "%d screws already current" % len(views)

    if dry_run:
        return "added", "%d screws (replay matches to %.1e / %.1e mm)" % (
            len(views), axis, origin)

    backup = scene_path + ".orig"
    if not os.path.exists(backup):
        shutil.copy2(scene_path, backup)
    with io.open(scene_path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    return "added", "%d screws" % len(views)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", default=RUNS)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not os.path.isdir(args.runs):
        print("no run folder: %s" % args.runs)
        return 1

    counts = {"added": 0, "updated": 0, "skipped": 0, "error": 0}
    for name in sorted(os.listdir(args.runs)):
        scene_dir = os.path.join(args.runs, name, "Statistic", "scene")
        if not os.path.isdir(scene_dir):
            continue
        status, detail = retrofit(scene_dir, dry_run=args.dry_run)
        counts[status] += 1
        if status == "error" or counts[status] <= 3:
            print("%-8s %-52s %s" % (status, name[:52], detail))
    print("\n%s: %d written, %d already current, %d errors"
          % ("would write" if args.dry_run else "done",
             counts["added"] + counts["updated"], counts["skipped"],
             counts["error"]))
    return 1 if counts["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
