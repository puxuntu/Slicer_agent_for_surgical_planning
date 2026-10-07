"""The Experiments panel for LongBoneFractureReduction: one button, one workbook.

Kept apart from ``longbone.py`` so the numerics stay Qt-free -- and, here,
Slicer-free as well -- so ``scripts/check_longbone_analysis.py`` can run the
whole analysis outside Slicer. This half only wires a button to it and reports
what happened.

No confirmation dialog and no scene-close warning, unlike ``orbital_panel``: this
analysis builds nothing in the MRML scene and touches nothing the user has open.

It does get a per-case progress dialog, which ``pelvic_panel`` only shows when
its expensive option is on. Here there is no option to make it conditional on:
every case reads two meshes of up to 12 MB and builds a KD-tree over them, which
is about a second apiece on the Qt main thread -- and a minute of frozen
application with no dialog is indistinguishable from a hang.
"""

from __future__ import annotations

import logging
import os

import qt
import slicer

from ..app.widget_experiments import register_experiment_panel
from . import longbone, run_timing

logger = logging.getLogger(__name__)


@register_experiment_panel(longbone.EXTENSION_NAME)
def build_panel(widget, layout, extension):
    root = _repository_root()
    # Resolved, never joined: the folder may sit under a tier
    # (Experiments/1_Quanti_Eva/<Ext>/) whose name belongs to the
    # study and has already changed once.
    experiment_dir = run_timing.resolve_experiment_dir(
        root, longbone.EXPERIMENT_DIR)
    # What the prose below should NAME -- the resolved location,
    # so "no cases found" never sends a reader to the wrong folder.
    shown_dir = run_timing.experiment_dir_label(
        root, longbone.EXPERIMENT_DIR)

    intro = qt.QLabel(
        "Scores every run under <code>{runs}</code> from one rigid residual, "
        "<b>E = G · P⁻¹</b>: the transform still needed to carry the pipeline's "
        "reduced fragment onto the ground truth. <b>P</b> is the pose the run "
        "computed, read from its own <code>Reduction Transform.h5</code> / "
        "<code>Reduction Base.h5</code> composed in the order "
        "<code>scene.mrml</code> declares.<br>"
        "<b>G</b> arrives two ways. A run the surgeon annotated carries "
        "<code>Moving_Segment_groundtruth.json</code>, which states G outright. "
        "A run from the fracture simulator has none — so G is taken from the "
        "simulation's own <code>*_fracture.json</code>, and since that record "
        "displaced only <i>one</i> of the two fragments, G is its inverse or "
        "the matrix itself depending on <b>which fragment this run chose to "
        "move</b>. That is decided by centroid and then <b>checked</b>: a "
        "correct G closes the fracture, so <code>truth_fit_mm</code> is under "
        "2 mm with the right matrix and never under 14 mm with the wrong one."
        "<br>"
        "Two tabs are written beside the runs: <b>Reduction accuracy</b> and "
        "<b>Timing</b> (t₀ input, t₁/t₂ segment the two fragments, t₃ 3D "
        "reconstruction, t₄ detect + initialise, t₅ hand pre-alignment, t₆ the "
        "reduction itself)."
        .format(runs=os.path.join(shown_dir,
                                  longbone.RUNS_SUBDIR))
    )
    intro.setWordWrap(True)
    intro.setTextFormat(qt.Qt.RichText)
    layout.addWidget(intro)

    cases = longbone.discover_cases(experiment_dir)
    count = len(cases)
    # A run missing any of its files cannot be scored. Naming them is worth a
    # line: the alternative is a case count that is quietly short.
    incomplete = [case for case in cases
                  if not longbone.case_is_scorable(case, experiment_dir)]

    found = qt.QLabel(
        ("%d case(s) found.%s"
         % (count, ("  [!] %d not scorable: %s"
                    % (len(incomplete),
                       ", ".join(case["subject"] or case["run"]
                                 for case in incomplete[:6])))
            if incomplete else ""))
        if count else
        "No cases found — each run needs a Statistic/scene/ folder.")
    found.setWordWrap(True)
    found.setStyleSheet("color: #b00;" if (incomplete or not count) else "color: gray;")
    layout.addWidget(found)

    button = qt.QPushButton("Analyse reduction error + timing  ->  Excel")
    button.setToolTip(
        "For every run: compose its reduction pose, resolve its ground truth, "
        "and write the residual rotation, the residual translation, the error "
        "over the fragment's own surface, the clinical split where a shaft axis "
        "is recorded, and the run timing to one .xlsx beside the runs.\n\n"
        "Reads only; the current scene is left alone.")
    button.setEnabled(bool(count))
    layout.addWidget(button)

    def _run():
        progress = _progress_dialog(count)
        button.setEnabled(False)
        found.setStyleSheet("color: gray;")
        found.setText("Analysing %d case(s)..." % count)

        def _tick(index, total, label):
            if progress is None:
                return
            progress.setLabelText("Case %d of %d: %s" % (index + 1, total, label))
            progress.setValue(index)
            slicer.app.processEvents()

        try:
            report = longbone.run_analysis(root, progress=_tick)
        except Exception as exc:
            logger.warning("Long-bone experiment analysis failed", exc_info=True)
            found.setStyleSheet("color: #b00;")
            found.setText("Analysis failed: %s  (see the Python console)" % exc)
            return
        finally:
            if progress is not None:
                try:
                    progress.close()
                    progress.deleteLater()
                except Exception:
                    logger.debug("Closing the progress dialog failed",
                                 exc_info=True)
            button.setEnabled(True)

        # The detail is worth keeping, just not on screen: printed rather than
        # logged so it lands in the Python console as a readable block.
        print(_summarise(report))
        found.setStyleSheet("color: gray;")
        found.setText(_outcome(report))

    button.clicked.connect(_run)


def _progress_dialog(count):
    try:
        progress = qt.QProgressDialog(slicer.util.mainWindow())
        progress.setWindowTitle("Experiments")
        progress.setLabelText("Analysing %d case(s)..." % count)
        progress.setMinimum(0)
        progress.setMaximum(count)
        progress.setMinimumDuration(0)
        progress.setAutoClose(False)
        progress.setWindowModality(qt.Qt.ApplicationModal)
        try:
            progress.setCancelButton(None)
        except Exception:
            progress.setCancelButtonText("")
        progress.show()
        slicer.app.processEvents()
        return progress
    except Exception:
        logger.debug("Experiments progress dialog unavailable", exc_info=True)
        return None


def _repository_root():
    from ..app.common import SLICER_AI_AGENT_ROOT             # noqa: PLC0415
    return SLICER_AI_AGENT_ROOT


def _outcome(report):
    """The one line the panel shows: where it went, and whether to trust it."""
    parts = ["Saved %s" % report.get("workbook_relative", "")]
    discovered, analysed = report.get("cases", 0), report.get("analysed", 0)

    # One population's numbers, not several: the summary carries a block per
    # population plus a pooled one, and a status line quoting all of them would
    # be three means with nothing saying which is which. The pooled block is
    # taken when it exists, and it exists exactly when there is more than one.
    summary = report.get("summary") or []
    populations = [row["population"] for row in summary]
    headline = "all cases" if "all cases" in populations else (
        populations[0] if populations else "")
    for row in summary:
        if row["population"] != headline:
            continue
        if row["metric"].startswith("point error, mean") \
                and row.get("mean") is not None:
            parts.append("%d case(s): point error mean %.2f mm (median %.2f, "
                         "max %.2f)" % (analysed, row["mean"], row["median"],
                                        row["max"]))
        elif row["metric"].startswith("residual rotation") \
                and row.get("mean") is not None:
            parts.append("rotation mean %.2f deg (median %.2f, max %.2f)"
                         % (row["mean"], row["median"], row["max"]))
        elif row["metric"].startswith("what fraction") \
                and row.get("mean") is not None:
            parts.append("%.0f%% of the displacement left, on average"
                         % (100.0 * row["mean"]))

    # Three things a reader must not take at face value, so they are said here
    # and not only in the console.
    broken = report.get("failed_cases") or []
    if broken:
        # A case that raised produced no row anywhere, so nothing below can see
        # it -- without this the status line would quote the discovered count
        # beside a mean taken over fewer cases and read as a complete sweep.
        parts.append("[!] %d of %d case(s) could NOT be analysed at all: %s"
                     % (len(broken), discovered, ", ".join(broken[:6])))
    rows = report.get("rows") or []
    suspect = [row for row in rows if row.get("truth_verified") is False
               or row.get("record_consistent") is False]
    if suspect:
        parts.append("[!] %d case(s) failed a verdict, so their millimetres are "
                     "about an unproven ground truth: %s"
                     % (len(suspect),
                        ", ".join(sorted(row["case"] for row in suspect)[:4])))
    unchecked = [row for row in rows if row.get("truth_verified") is None]
    if unchecked:
        parts.append("[!] %d case(s) could not be checked at all (no fracture "
                     "surfaces to compare)" % len(unchecked))
    parts.append("Full detail in the Python console.")
    return "  |  ".join(parts)


def _summarise(report):
    lines = ["Saved: %s" % report.get("workbook_relative", ""), ""]
    lines.extend(report.get("log") or [])

    rows = [row for row in report.get("rows") or []
            if row.get("rotation_deg") is not None]
    if rows:
        lines.append("")
        lines.append("Residual after the reduction, per case")
        lines.append("  %-22s %-11s %-6s %8s %8s %9s %9s %8s %7s"
                     % ("case", "truth", "role", "rot deg", "shift mm",
                        "pt mean", "pt p95", "fit mm", "ok?"))
        for row in rows:
            lines.append("  %-22s %-11s %-6s %8.3f %8.3f %9.3f %9.3f %8s %7s"
                         % (row["case"][:22], (row.get("truth_source") or "")[:11],
                            (row.get("fragment_role") or "-")[:6],
                            row["rotation_deg"], row["translation_mm"],
                            row["point_error_mean_mm"], row["point_error_p95_mm"],
                            _number(row.get("truth_fit_mm")), _verdict(row)))

    broken = [row for row in report.get("rows") or []
              if row.get("rotation_deg") is None]
    for row in broken:
        lines.append("  [!] %s: %s" % (row.get("case"), row.get("error")))

    phases = report.get("phase_rows") or []
    if phases:
        lines.append("")
        lines.append("Phase timing (s) — t0 input, t1/t2 segment the two "
                     "fragments, t3 3D reconstruction, t4 detect + initialise, "
                     "t5 hand pre-alignment, t6 reduce")
        lines.append("  %-22s %7s %7s %7s %7s %7s %7s %7s %9s"
                     % (("case",) + longbone.PHASE_ORDER + ("total",)))
        for row in phases:
            lines.append("  %-22s %7.1f %7.1f %7.1f %7.1f %7.1f %7.1f %7.1f %9s"
                         % ((row["case"][:22],)
                            + tuple(row.get("%s_s" % phase) or 0.0
                                    for phase in longbone.PHASE_ORDER)
                            + ("%.1f" % row["t_total_s"]
                               if row.get("t_total_s") is not None else "--",)))

    summary = report.get("summary") or []
    if summary:
        lines.append("")
        lines.append("Across the cases that passed every verdict")
        for row in summary:
            if row.get("mean") is None:
                # A count, not a distribution -- its note IS the statement, so
                # printing empty mean/sd/min/max columns beside it would only
                # invite them to be read as zeros.
                lines.append("  %-28s %-52s n=%-4s %s"
                             % (row["population"], row["metric"], row.get("n"),
                                row.get("note") or ""))
                continue
            lines.append("  %-28s %-52s n=%-4s mean=%-9s sd=%-9s median=%-9s "
                         "[%s .. %s]"
                         % (row["population"], row["metric"], row.get("n"),
                            row.get("mean"), row.get("sd"), row.get("median"),
                            row.get("min"), row.get("max")))
    return "\n".join(lines)


def _number(value):
    return "%.3f" % value if isinstance(value, (int, float)) else "--"


def _verdict(row):
    """'yes' / 'NO' / '--', where '--' means the check could not run.

    A blank and a failure must not print the same: a ground truth that could not
    be checked is unproven, while one that failed is wrong.
    """
    if row.get("truth_verified") is False or row.get("record_consistent") is False:
        return "NO"
    if row.get("truth_verified") is None:
        return "--"
    return "yes"
