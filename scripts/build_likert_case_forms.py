# -*- coding: utf-8 -*-
"""One data-collection sheet per procedure, in the layout of Zygomatic.xlsx.

The reference workbook (``build_likert_forms.py``) puts one case on one tab.
These are the sheets a panel actually fills in: **questions down, cases across**,
so a rater scores one question over the whole cohort without paging, and one
column is one case's complete verdict. The layout, the wording and the question
set are taken from ``Experiments/0_QualitativeEvaluation/Zygomatic.xlsx``, which
was authored by hand -- this script reproduces it for the other seven procedures.

Two things that template decided, and this script therefore follows:

- **Two core questions, not three.** G2 (executability) is not on it, so it is
  not on these. ``likert.NOT_COLLECTED`` records that, and the pairwise question,
  as omissions rather than deleting them -- see the note there for what each one
  cost.
- **Case columns are bare numbers**, which is what blinding requires. The number
  is therefore meaningless without a key mapping column N to a run folder; keep
  one beside these files or the ratings cannot be joined to the quantitative
  results later.

An existing file is never overwritten without ``--force``: the first of these
files is the hand-authored template, and regenerating over somebody's manual
edits is not something a build script should do quietly.

    python scripts/build_likert_case_forms.py
    python scripts/build_likert_case_forms.py --cases 32     # same count for all
    python scripts/build_likert_case_forms.py --force        # rewrite everything
"""

from __future__ import annotations

import argparse
import math
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

for _name in ("slicer", "qt", "vtk", "ctk"):
    sys.modules.setdefault(_name, types.ModuleType(_name))
sys.modules["slicer"].util = types.ModuleType("slicer.util")

from SlicerAIAgentLib.experiments import likert               # noqa: E402

OUT_DIR = os.path.join(ROOT, "Experiments", "0_QualitativeEvaluation")

#: Verbatim from the template, including the space that opens the second line.
SCALE_LINE = ("5 = strongly agree, 4 = agree, 3 = unsure, 2 = disagree, "
              "1 = strongly disagree.\n 5＝完全同意，4＝同意，3＝不确定，2＝不同意，"
              "1＝完全不同意")

FONT_NAME = "Times New Roman"
FIRST_CASE_COLUMN = 7                                         # G
QUESTION_LAST_COLUMN = 6                                      # B..F merged

#: Effective width of the merged question cell, in characters. Used only to
#: estimate how many lines a question wraps to, because a merged cell is the one
#: thing Excel will not auto-fit: an unset row height clips the text instead.
QUESTION_WIDTH = 65.75
LINE_HEIGHT = 16.0


def _display_width(text: str) -> float:
    """CJK glyphs occupy two character cells; the questions are half Chinese, so
    measuring in code points would under-count every second line."""
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in text)


def _row_height(text: str) -> float:
    lines = 0
    for segment in text.split("\n"):
        lines += max(1, int(math.ceil(_display_width(segment) / QUESTION_WIDTH)))
    return max(20.0, round(lines * LINE_HEIGHT, 1))


def _question_text(item) -> str:
    """The template strips the sentence-final punctuation from both languages;
    a table cell is not a sentence."""
    english = item["question_en"].strip().rstrip(".")
    chinese = item["question_zh"].strip().rstrip("。")
    return "%s\n%s" % (english, chinese)


def _existing_case_count(path: str):
    """How many case columns the file already has, or None.

    A rebuild must not silently change a cohort size somebody chose: the first of
    these forms was authored by hand with 32 columns while 29 runs are on disk,
    and the difference is a fact about the study, not a mistake to correct.
    """
    if not os.path.exists(path):
        return None
    try:
        import openpyxl
        sheet = openpyxl.load_workbook(path).active
        count = 0
        for column in range(FIRST_CASE_COLUMN, sheet.max_column + 1):
            if sheet.cell(row=4, column=column).value is None:
                break
            count += 1
        return count or None
    except Exception:                                         # noqa: BLE001
        return None


def _build(task, cases: int, path: str) -> None:
    import openpyxl
    from openpyxl.styles import Alignment, Border, Font, Side
    from openpyxl.utils import get_column_letter

    items = likert.case_form_items(task)
    last_case_column = FIRST_CASE_COLUMN + cases - 1

    book = openpyxl.Workbook()
    sheet = book.active
    sheet.title = "Sheet1"

    medium = Side(style="medium")
    box = Border(left=medium, right=medium, top=medium, bottom=medium)
    centre = Alignment(horizontal="center", vertical="center")
    centre_wrap = Alignment(horizontal="center", vertical="center",
                            wrap_text=True)

    def put(row, column, value, bold=False, size=11, wrap=False):
        cell = sheet.cell(row=row, column=column, value=value)
        cell.font = Font(name=FONT_NAME, bold=bold, size=size)
        cell.alignment = centre_wrap if wrap else centre
        cell.border = box
        return cell

    sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=7)
    put(1, 1, "%s / %s" % (task["title_en"], task["title_zh"]), bold=True,
        size=12)

    sheet.merge_cells(start_row=2, start_column=1, end_row=2, end_column=7)
    put(2, 1, SCALE_LINE, bold=True, wrap=True)

    sheet.merge_cells(start_row=3, start_column=1, end_row=4, end_column=1)
    put(3, 1, "No.", bold=True)

    sheet.merge_cells(start_row=3, start_column=2, end_row=4,
                      end_column=QUESTION_LAST_COLUMN)
    put(3, 2, "Question/问题", bold=True)

    sheet.merge_cells(start_row=3, start_column=FIRST_CASE_COLUMN, end_row=3,
                      end_column=last_case_column)
    put(3, FIRST_CASE_COLUMN, "Score for each case/每个结果的评分", bold=True)

    for offset in range(cases):
        put(4, FIRST_CASE_COLUMN + offset, offset + 1, bold=True)

    # Every cell of a merged range carries the border, so Excel draws a box
    # around the range rather than around its first cell.
    for row in (1, 2, 3):
        for column in range(1, last_case_column + 1):
            cell = sheet.cell(row=row, column=column)
            cell.border = box
    for column in range(2, QUESTION_LAST_COLUMN + 1):
        sheet.cell(row=4, column=column).border = box

    for number, item in enumerate(items, start=1):
        row = 4 + number
        put(row, 1, number)
        sheet.merge_cells(start_row=row, start_column=2, end_row=row,
                          end_column=QUESTION_LAST_COLUMN)
        text = _question_text(item)
        put(row, 2, text, wrap=True)
        for column in range(3, last_case_column + 1):
            cell = sheet.cell(row=row, column=column)
            cell.font = Font(name=FONT_NAME, size=11)
            cell.alignment = centre
            cell.border = box
        sheet.row_dimensions[row].height = _row_height(text)

    for height, row in ((16.2, 1), (29.4, 2), (15.0, 3), (14.4, 4)):
        sheet.row_dimensions[row].height = height

    for column in range(1, QUESTION_LAST_COLUMN + 1):
        sheet.column_dimensions[get_column_letter(column)].width = 8.88671875
    sheet.column_dimensions[get_column_letter(QUESTION_LAST_COLUMN)].width = \
        31.109375
    for column in range(FIRST_CASE_COLUMN, last_case_column + 1):
        sheet.column_dimensions[get_column_letter(column)].width = 8.88671875

    # The header is worth keeping on screen once the sheet is 100 cases wide and
    # the rater is 40 columns from the question they are answering.
    sheet.freeze_panes = sheet.cell(row=5, column=FIRST_CASE_COLUMN).coordinate

    book.save(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default=OUT_DIR)
    parser.add_argument("--cases", type=int, default=None,
                        help="case columns for every file; default is each "
                             "procedure's own run count")
    parser.add_argument("--force", action="store_true",
                        help="overwrite files that already exist")
    args = parser.parse_args()

    if not os.path.isdir(args.out_dir):
        os.makedirs(args.out_dir)

    print("%-10s %-7s %-10s %s" % ("file", "cases", "questions", "status"))
    for task in likert.TASKS:
        name = task["sheet"].split("_", 1)[1]
        path = os.path.join(args.out_dir, "%s.xlsx" % name)
        questions = len(likert.case_form_items(task))
        existing = _existing_case_count(path)
        cases = args.cases or existing or task["runs_available"]
        if os.path.exists(path) and not args.force:
            print("%-10s %-7d %-10d skipped, exists" % (name, cases, questions))
            continue
        _build(task, cases, path)
        note = "written" if existing is None else "rebuilt, kept %d cases" % cases
        print("%-10s %-7d %-10d %s" % (name, cases, questions, note))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
