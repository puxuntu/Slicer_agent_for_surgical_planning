"""The Experiments panel for ZygomaticImplantPlanner: one button, one workbook.

Kept apart from ``zygomatic.py`` so the numerics stay Qt-free and testable
outside Slicer; this half only wires a button to them and reports what happened.
"""

from __future__ import annotations

import logging
import os

import qt
import slicer

from ..app.widget_experiments import register_experiment_panel
from . import zygomatic

logger = logging.getLogger(__name__)


@register_experiment_panel(zygomatic.EXTENSION_NAME)
def build_panel(widget, layout, extension):
    root = _repository_root()
    experiment_dir = os.path.join(root, zygomatic.EXPERIMENT_DIR)

    intro = qt.QLabel(
        "Summarises every run under <code>{runs}</code> against the manually "
        "planned paths in <code>{data}</code>, and writes both tables to one "
        "workbook beside the runs."
        .format(runs=os.path.join(zygomatic.EXPERIMENT_DIR, zygomatic.RUNS_SUBDIR),
                data=os.path.join(zygomatic.EXPERIMENT_DIR, zygomatic.DATASET_SUBDIR))
    )
    intro.setWordWrap(True)
    intro.setTextFormat(qt.Qt.RichText)
    layout.addWidget(intro)

    count = len(zygomatic.discover_cases(experiment_dir))
    # One line, reused for the outcome. The full per-path table goes to the
    # Python console: it is 60+ rows across the two sheets, which is a
    # spreadsheet's job, not a panel's -- and everything it would show is in the
    # workbook this writes.
    found = qt.QLabel(
        "%d case(s) found." % count if count
        else "No cases found -- each run needs a Statistic/scene/ folder.")
    found.setWordWrap(True)
    found.setStyleSheet("color: gray;" if count else "color: #b00;")
    layout.addWidget(found)

    button = qt.QPushButton("Analyse BIC + timing  ->  Excel")
    button.setToolTip(
        "For every case: recompute the bone-implant contact of the four planned "
        "paths and of the four manually planned STLs on the same bone cloud, "
        "pair them by entry point, and write the relative BIC and the run "
        "timing to one .xlsx.")
    button.setEnabled(bool(count))
    layout.addWidget(button)

    def _run():
        # The scan reads several hundred MB of models per case and runs on the
        # Qt main thread, so the UI would otherwise sit frozen with no
        # explanation of what it is doing.
        progress = None
        button.setEnabled(False)
        found.setStyleSheet("color: gray;")
        found.setText("Analysing %d case(s)..." % count)
        try:
            progress = qt.QProgressDialog(slicer.util.mainWindow())
            progress.setWindowTitle("Experiments")
            progress.setLabelText("Analysing %d case(s)..." % count)
            progress.setMinimum(0)
            progress.setMaximum(0)
            progress.setMinimumDuration(0)
            progress.setAutoClose(False)
            progress.setWindowModality(qt.Qt.ApplicationModal)
            try:
                progress.setCancelButton(None)
            except Exception:
                progress.setCancelButtonText("")
            progress.show()
            slicer.app.processEvents()
        except Exception:
            logger.debug("Experiments progress dialog unavailable", exc_info=True)
            progress = None

        try:
            report = zygomatic.run_analysis(root)
        except Exception as exc:
            logger.warning("Zygomatic experiment analysis failed", exc_info=True)
            found.setStyleSheet("color: #b00;")
            found.setText("Analysis failed: %s  (see the Python console)" % exc)
            return
        finally:
            if progress is not None:
                try:
                    progress.close()
                    progress.deleteLater()
                except Exception:
                    logger.debug("Closing the progress dialog failed", exc_info=True)
            button.setEnabled(True)

        # The detail is worth keeping, just not on screen: printed rather than
        # logged so it lands in the Python console as a readable block.
        print(_summarise(report))
        found.setText(_outcome(report, count))

    button.clicked.connect(_run)


def _outcome(report, count):
    """The one line the panel shows: where it went, and whether to trust it."""
    parts = ["Saved %s" % report.get("workbook_relative", "")]
    overall = [c for c in report.get("per_case") or [] if c["case"] == "ALL CASES"]
    if overall:
        parts.append("%d case(s), mean relative BIC %.3f over %d path(s), "
                     "%d above 1"
                     % (count, overall[0]["mean_relative_bic"],
                        overall[0]["paths"], overall[0]["paths_above_1"]))
    # A case whose planner score could not be reproduced is the one result a
    # reader must not take at face value, so it is said here and not only in the
    # console.
    suspect = {r["case"] for r in report.get("bic_rows") or []
               if r.get("reconstruction_ok") is False}
    if suspect:
        parts.append("[!] planner score NOT reproduced for %s -- see the console"
                     % ", ".join(sorted(suspect)))
    parts.append("Full detail in the Python console.")
    return "  |  ".join(parts)


def _repository_root():
    """The extension checkout, so every path below it can stay relative."""
    from ..app.common import SLICER_AI_AGENT_ROOT             # noqa: PLC0415
    return SLICER_AI_AGENT_ROOT


def _summarise(report):
    lines = ["Saved: %s" % report.get("workbook_relative", ""), ""]
    lines.extend(report.get("log") or [])

    rows = [r for r in report.get("bic_rows") or [] if r.get("relative_bic") is not None]
    if rows:
        lines.append("")
        lines.append("Relative BIC (ours / manual, same entry point)")
        lines.append("  %-9s %-11s %-4s %8s %8s %9s"
                     % ("case", "path", "side", "ours", "manual", "relative"))
        for row in rows:
            lines.append("  %-9s %-11s %-4s %8s %8s %9.3f"
                         % (row["case"], row["path"], row["side"] or "?",
                            row["bic_ours"], row["bic_manual"], row["relative_bic"]))
    totals = report.get("side_totals") or []
    if totals:
        lines.append("")
        lines.append("Per-side totals (baseline = one per manual path)")
        for total in totals:
            lines.append("  %-9s side %-2s  %.3f / %d  %s"
                         % (total["case"], total["side"], total["sum_relative_bic"],
                            total["baseline"],
                            "better than manual" if total["beats_manual"] else "below manual"))
    steps = report.get("step_rows") or []
    if steps:
        visits = [r for r in steps if r["kind"] == "step visit"]
        reviews = [r for r in steps if r["kind"] == "replay review"]
        lines.append("")
        lines.append("Per-step timing: %d step visit(s) and %d replay review(s) "
                     "listed across %d case(s)."
                     % (len(visits), len(reviews),
                        len({r["case"] for r in steps})))

    overall = [c for c in report.get("per_case") or [] if c["case"] == "ALL CASES"]
    if overall:
        summary = overall[0]
        lines.append("")
        lines.append("All cases: mean relative BIC %.3f over %d path(s); "
                     "%d above 1."
                     % (summary["mean_relative_bic"], summary["paths"],
                        summary["paths_above_1"]))
    return "\n".join(lines)
