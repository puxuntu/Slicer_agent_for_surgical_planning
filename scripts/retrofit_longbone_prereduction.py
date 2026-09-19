# -*- coding: utf-8 -*-
"""Give every saved LongBoneFractureReduction run the pre-reduction bone it lacks.

A saved run shows the reference bone and the moving bone in its REDUCED pose, and
the displaced position the operation started from is nowhere in the scene: the
moving fragment is one node, moved by the ``Reduction Base`` / ``Reduction
Transform`` chain. So the one thing a reader wants from the scene -- what was
corrected -- cannot be seen in it.

The extension now keeps that copy itself (``Logic.savePreReductionModel``, called
from ``onReduce``), so any future run has it. This script puts the same node into
the 64 runs already on disk, so they need not be re-run.

**The copy is the moving model's own file, unmoved.**
``reconstructModelFromSegment`` bakes the segmentation's parent transform into the
polydata and leaves the model unparented, so ``Moving_Segment.vtk`` already holds
the fragment where the scan found it; everything after detection moves it by
parenting, which never touches the points. The retrofit is therefore a byte copy
of that file plus three XML elements -- not a computation, and nothing here can
produce a geometry a re-run would not.

**The three elements are copied from the moving model's own**, with only id, name,
references, colour, opacity and visibility changed. Writing them from scratch would
mean reproducing this Slicer version's display-node schema from memory; deriving
them from the element beside it cannot drift.

Safety: ``scene.mrml`` is backed up to ``scene.mrml.orig`` once (an existing backup
is never overwritten -- it is the pre-edit scene, and taking a second copy later
would preserve an edit instead), the edit is idempotent (a scene that already has
the node is skipped), and ``--dry-run`` reports without writing.

    python scripts/retrofit_longbone_prereduction.py --dry-run
    python scripts/retrofit_longbone_prereduction.py
"""

from __future__ import annotations

import argparse
import io
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Must match the extension's constants, or a retrofitted scene and a re-run scene
#: would disagree about what the node is called and how it is marked.
MOVING_MODEL = "Moving_Segment"
SUFFIX = "_before_reduction"
ROLE_ATTR = "LongBoneFractureReduction.Role"
ROLE_VALUE = "movingBeforeReduction"
COLOR_SCALE = 0.55
OPACITY = 1.0

RUNS = os.path.join(ROOT, "Experiments", "LongBoneFractureReduction",
                    "Overall_Performance")


def _element(text, tag, attribute, value):
    """The whole ``<tag ...></tag>`` element whose ``attribute`` equals ``value``."""
    pattern = re.compile(r"[ \t]*<%s\b[^>]*></%s>\n" % (tag, tag))
    for match in pattern.finditer(text):
        if re.search(r'\b%s="%s"' % (attribute, re.escape(value)), match.group(0)):
            return match
    return None


def _attr(element, name, default=""):
    found = re.search(r'\b%s="([^"]*)"' % name, element)
    return found.group(1) if found else default


def _set_attr(element, name, value):
    """Replace one attribute's value, leaving every other byte of the element."""
    return re.sub(r'(\b%s=")[^"]*(")' % name, lambda m: m.group(1) + value + m.group(2),
                  element, count=1)


def _next_id(text, klass):
    """The id Slicer itself would hand the next node of this class."""
    numbers = [int(n) for n in re.findall(r'id="vtkMRML%s(\d+)"' % klass, text)]
    return "vtkMRML%s%d" % (klass, (max(numbers) + 1) if numbers else 1)


def _next_name(text, stem):
    """``ModelDisplay_7`` style: the next free index for an auto-named helper node."""
    numbers = [int(n) for n in re.findall(r'name="%s_(\d+)"' % stem, text)]
    if not re.search(r'name="%s"' % stem, text) and not numbers:
        return stem
    return "%s_%d" % (stem, (max(numbers) + 1) if numbers else 1)


def _darken(color):
    try:
        parts = [float(v) for v in color.split()]
    except ValueError:
        return color
    return " ".join(("%g" % (v * COLOR_SCALE)) for v in parts)


def _refresh(scene_path, text, new_name, dry_run):
    """Bring an already-retrofitted scene's copy up to the constants above.

    The alternative -- skipping any scene that already has the node -- means a
    change to how the copy looks reaches new runs and silently never reaches the
    64 on disk, which is how two halves of one cohort come to differ. Only the
    display properties are rewritten; the node, its file and its ids are left
    exactly as they are.
    """
    model = _element(text, "Model", "name", new_name)
    if model is None:
        return "error", "the role attribute is present but the model is not"
    display_id = re.search(r"display:([^;]+);", _attr(model.group(0), "references"))
    if not display_id:
        return "error", "the pre-reduction model has no display reference"
    display = _element(text, "ModelDisplay", "id", display_id.group(1))
    if display is None:
        return "error", "the pre-reduction display node is missing"

    updated_display = _set_attr(display.group(0), "opacity", "%g" % OPACITY)
    updated_display = _set_attr(updated_display, "visibility", "false")
    updated_model = _set_attr(model.group(0), "attributes",
                              "%s:%s" % (ROLE_ATTR, ROLE_VALUE))
    if updated_display == display.group(0) and updated_model == model.group(0):
        return "skipped", "already current"
    if dry_run:
        return "updated", "opacity -> %g, attribute separator" % OPACITY
    # Model first or the display span, which sits after it, would shift.
    updated = text[:display.start()] + updated_display + text[display.end():]
    model_again = _element(updated, "Model", "name", new_name)
    updated = (updated[:model_again.start()] + updated_model
               + updated[model_again.end():])
    with io.open(scene_path, "w", encoding="utf-8", newline="") as handle:
        handle.write(updated)
    return "updated", "opacity -> %g" % OPACITY


def retrofit(scene_dir, dry_run=False):
    """Returns (status, detail). Status is added / updated / skipped / error."""
    scene_path = os.path.join(scene_dir, "scene.mrml")
    if not os.path.isfile(scene_path):
        return "error", "no scene.mrml"
    source_vtk = os.path.join(scene_dir, MOVING_MODEL + ".vtk")
    if not os.path.isfile(source_vtk):
        return "error", "no %s.vtk" % MOVING_MODEL

    text = io.open(scene_path, encoding="utf-8").read()
    new_name = MOVING_MODEL + SUFFIX
    if ROLE_VALUE in text or ('name="%s"' % new_name) in text:
        return _refresh(scene_path, text, new_name, dry_run)

    model = _element(text, "Model", "name", MOVING_MODEL)
    if model is None:
        return "error", "no <Model name=\"%s\">" % MOVING_MODEL
    model_xml = model.group(0)
    references = _attr(model_xml, "references")
    display_id = re.search(r"display:([^;]+);", references)
    storage_id = re.search(r"storage:([^;]+);", references)
    if not display_id or not storage_id:
        return "error", "the moving model has no display/storage reference"

    display = _element(text, "ModelDisplay", "id", display_id.group(1))
    storage = _element(text, "ModelStorage", "id", storage_id.group(1))
    if display is None or storage is None:
        return "error", "the moving model's display/storage element is missing"

    new_model_id = _next_id(text, "ModelNode")
    new_display_id = _next_id(text, "ModelDisplayNode")
    new_storage_id = _next_id(text, "ModelStorageNode")

    new_display = display.group(0)
    new_display = _set_attr(new_display, "id", new_display_id)
    new_display = _set_attr(new_display, "name", _next_name(text, "ModelDisplay"))
    new_display = _set_attr(new_display, "color", _darken(_attr(new_display, "color")))
    new_display = _set_attr(new_display, "opacity", "%g" % OPACITY)
    new_display = _set_attr(new_display, "scalarVisibility", "false")
    # The master switch, which is what the extension's SetVisibility(False) writes;
    # visibility3D stays true so ticking the node on in the Data module shows it.
    new_display = _set_attr(new_display, "visibility", "false")

    new_storage = storage.group(0)
    new_storage = _set_attr(new_storage, "id", new_storage_id)
    new_storage = _set_attr(new_storage, "name", _next_name(text, "ModelStorage"))
    new_storage = _set_attr(new_storage, "fileName", new_name + ".vtk")

    new_model = model_xml
    new_model = _set_attr(new_model, "id", new_model_id)
    new_model = _set_attr(new_model, "name", new_name)
    # Its own marker only. The segment-source and terminology attributes belong to a
    # model exported from a segment, which this is not. No trailing separator:
    # vtkMRMLNode::WriteXML joins attributes with ';' and ends without one, and
    # ReadXML's getline would turn a trailing ';' into an extra nameless attribute.
    new_model = _set_attr(new_model, "attributes", "%s:%s" % (ROLE_ATTR, ROLE_VALUE))
    # No transform reference: not following the reduction is the whole point.
    new_model = _set_attr(new_model, "references", "display:%s;storage:%s;"
                          % (new_display_id, new_storage_id))

    if dry_run:
        return "added", "%s (%s, %s, %s)" % (new_name, new_model_id, new_display_id,
                                             new_storage_id)

    backup = scene_path + ".orig"
    if not os.path.exists(backup):
        shutil.copy2(scene_path, backup)
    shutil.copy2(source_vtk, os.path.join(scene_dir, new_name + ".vtk"))

    # Model and display beside the pair they were copied from; storage with the other
    # storage nodes -- the layout this file already uses.
    updated = text[:model.end()] + new_model + text[model.end():]
    display_again = _element(updated, "ModelDisplay", "id", display_id.group(1))
    updated = (updated[:display_again.end()] + new_display
               + updated[display_again.end():])
    last_storage = None
    for match in re.finditer(r"[ \t]*<ModelStorage\b[^>]*></ModelStorage>\n", updated):
        last_storage = match
    updated = updated[:last_storage.end()] + new_storage + updated[last_storage.end():]

    with io.open(scene_path, "w", encoding="utf-8", newline="") as handle:
        handle.write(updated)
    return "added", "%s (%s)" % (new_name, new_model_id)


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
            print("%-10s %-52s %s" % (status, name[:52], detail))
    print("\n%s: %d added, %d updated, %d already current, %d errors"
          % ("would do" if args.dry_run else "done", counts["added"],
             counts["updated"], counts["skipped"], counts["error"]))
    return 1 if counts["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
