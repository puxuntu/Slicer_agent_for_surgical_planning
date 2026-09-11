# -*- coding: utf-8 -*-
"""Build the expert rating workbook and the developer document from one source.

The instrument lives in ``SlicerAIAgentLib/experiments/likert.py`` as data; this
script only renders it, into the two things its two audiences need:

Both land in ``Experiments/0_QualitativeEvaluation/`` -- the study is one thing,
so the form and the document that explains it live in one folder:

- ``Likert_rating_forms.xlsx`` -- one tab per procedure, bilingual, short. What a
  surgeon fills in.
- ``qualitative_evaluation.md`` -- design, protocol, analysis plan, and the
  rationale behind every question. What a developer or a reviewer reads.

Rendering both from one module is the point: a form and a document that explain
the same questions will otherwise drift, and the one that drifts is always the
document.

Runs outside Slicer (the module is Qt- and Slicer-free, and
``workbook.write_workbook`` falls back to one CSV per sheet when openpyxl is
absent), so the instrument can be regenerated on any machine.

    python scripts/build_likert_forms.py
    python scripts/build_likert_forms.py --out some/where/forms.xlsx
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# SlicerAIAgentLib/__init__.py pulls in SafeExecutor, which imports slicer at
# module scope. Stubbed the same way the check_* scripts stub it: neither module
# imported below touches any of these names.
for _name in ("slicer", "qt", "vtk", "ctk"):
    sys.modules.setdefault(_name, types.ModuleType(_name))
sys.modules["slicer"].util = types.ModuleType("slicer.util")

from SlicerAIAgentLib.experiments import likert               # noqa: E402
from SlicerAIAgentLib.experiments import workbook             # noqa: E402

#: Leading "0_" so the study sorts above the eight procedure folders it is about,
#: rather than into the middle of them under Q.
OUT_DIR = os.path.join(ROOT, "Experiments", "0_QualitativeEvaluation")
DEFAULT_OUT = os.path.join(OUT_DIR, "Likert_rating_forms.xlsx")
DEFAULT_DOC = os.path.join(OUT_DIR, "qualitative_evaluation.md")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=DEFAULT_OUT,
                        help="rating workbook (default: %s)"
                             % os.path.relpath(DEFAULT_OUT, ROOT))
    parser.add_argument("--doc", default=DEFAULT_DOC,
                        help="developer document (default: %s)"
                             % os.path.relpath(DEFAULT_DOC, ROOT))
    args = parser.parse_args()

    written, notes = workbook.write_workbook(args.out, likert.build_sheets())
    print("wrote %s" % written)
    for note in notes:
        print("  note: %s" % note)

    directory = os.path.dirname(args.doc)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with io.open(args.doc, "w", encoding="utf-8") as handle:
        handle.write(likert.build_markdown())
    print("wrote %s" % args.doc)

    print("\n%-5s %-46s %-9s %s" % ("task", "procedure", "questions", "minutes"))
    for task in likert.TASKS:
        items = likert.case_form_items(task)
        print("%-5s %-46s %-9d %d  (%d cases + %d repeat)" % (
            task["task_id"], task["title_en"], len(items),
            likert.minutes_per_rater(task), likert.sample_size(task),
            likert.duplicates(task)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
