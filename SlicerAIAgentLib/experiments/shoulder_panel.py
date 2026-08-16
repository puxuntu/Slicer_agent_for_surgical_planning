"""The Experiments panel for ReverseShoulderArthroplasty: one button, one workbook.

Kept apart from ``shoulder.py`` so the numerics stay Qt-free -- and, here, Slicer-free
as well -- so ``scripts/check_rsa_analysis.py`` can run the whole analysis outside
Slicer. This half only wires a button to it and reports what happened.

No confirmation dialog and no scene-close warning, unlike ``orbital_panel``: this
analysis builds nothing in the MRML scene and touches nothing the user has open.
It does read one full CT per case and sweep ~25,000 candidate trajectories
through it on the Qt main thread, so it gets orbital's per-case progress dialog
rather than zygomatic's indeterminate one -- with 60+ subjects the difference is
between "Slicer is busy" and "Slicer has hung".
"""

from __future__ import annotations

import logging
import os

import qt
import slicer

from ..app.widget_experiments import register_experiment_panel
from . import shoulder

logger = logging.getLogger(__name__)


@register_experiment_panel(shoulder.EXTENSION_NAME)
def build_panel(widget, layout, extension):
    root = _repository_root()
    experiment_dir = os.path.join(root, shoulder.EXPERIMENT_DIR)

    intro = qt.QLabel(
        "Scores every run under <code>{runs}</code> against the four measures of "
        "Li et al., <i>IJCARS</i> 2022;17:1017-1027 — the angles "
        "<b>θ₁</b>, <b>θ₂</b> (each long screw against the middle peg) and "
        "<b>θ₃</b> (the two long screws against each other), and <b>δ</b>, the "
        "chosen path's bone-density integral divided by the largest integral "
        "anywhere in its cone once the screw-exposure constraint is dropped.<br>"
        "Both plans are scored: the pipeline's <code>Path_Screw*</code> and the "
        "surgeon's hand-planned <code>Manual_Screw_Model_*</code>. They leave "
        "the <b>same</b> baseplate hole, so one cone and one denominator serve "
        "both and <code>delta_gain</code> is a paired difference.<br>"
        "Everything is <b>recomputed from the saved scene</b>: the extension "
        "stores no score, and it never scores the paths it rejects — which is "
        "exactly what δ divides by. The evidence that it is the same arithmetic "
        "is the <code>score_reproduced</code> column, which compares the "
        "recomputed integral against the <i>Stability score</i> the run printed "
        "while planning.<br>"
        "Two tabs are written beside the runs: <b>Metrics</b> and <b>Timing</b> "
        "(t₁ bone reconstruction, t₂ reference point and baseplate pose, "
        "t₃ automatic planning, and the total)."
        .format(runs=os.path.join(shoulder.EXPERIMENT_DIR, shoulder.RUNS_SUBDIR))
    )
    intro.setWordWrap(True)
    intro.setTextFormat(qt.Qt.RichText)
    layout.addWidget(intro)

    cases = shoulder.discover_cases(experiment_dir)
    count = len(cases)
    # A run that was exited without saving has no scene to score. Naming them is
    # worth a line: the alternative is a case count that is quietly short.
    incomplete = [c for c in cases
                  if not os.path.isfile(os.path.join(c["scene_dir"],
                                                     shoulder.MIDDLE_PATH_FILE))]

    found = qt.QLabel(
        ("%d case(s) found.%s"
         % (count, ("  [!] %d without a planned prosthesis: %s"
                    % (len(incomplete), ", ".join(c["subject"] or c["run"]
                                                  for c in incomplete[:6])))
            if incomplete else ""))
        if count else
        "No cases found — each run needs a Statistic/scene/ folder.")
    found.setWordWrap(True)
    found.setStyleSheet("color: #b00;" if (incomplete or not count) else "color: gray;")
    layout.addWidget(found)

    button = qt.QPushButton("Analyse θ₁ θ₂ θ₃ δ + timing  ->  Excel")
    button.setToolTip(
        "For every case: recover the two screw paths and the middle peg from the "
        "saved scene, measure the three angles between them, re-run the "
        "bone-density path integral over the whole cone on that case's own CT, "
        "and write the ratios and the run timing to one .xlsx.\n\n"
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
            report = shoulder.run_analysis(root, progress=_tick)
        except Exception as exc:
            logger.warning("RSA experiment analysis failed", exc_info=True)
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
    for row in report.get("summary") or []:
        # The PLANNED population only. The best-effort screws have their own
        # summary row because they were chosen by depth rather than density, and
        # a headline that pooled them would not be the paper's delta.
        if row["metric"] == "delta — pipeline (planned)" and row.get("mean") is not None:
            parts.append("%d case(s) analysed, mean δ %.3f over %d planned screw(s)"
                         % (analysed, row["mean"], row["n"]))

    # The headline the workbook exists for, and it is split by selection: a
    # best-effort screw was aimed by depth, so losing to the hand plan there says
    # nothing about the search. Pooling the two would hide exactly that.
    comparison = report.get("comparison_rows") or []
    graded = [r for r in comparison if r.get("selection") != "best effort"]
    if graded:
        won = sum(1 for r in graded if r.get("pipeline_denser"))
        parts.append("denser than the hand plan on %d of %d planned screw(s)"
                     % (won, len(graded)))
    effort = [r for r in comparison if r.get("selection") == "best effort"]
    if effort:
        won = sum(1 for r in effort if r.get("pipeline_denser"))
        parts.append("%d of %d BEST EFFORT screw(s) (aimed by depth, not density)"
                     % (won, len(effort)))

    # Four things a reader must not take at face value, so they are said here
    # and not only in the console.
    broken = report.get("failed_cases") or []
    if broken:
        # A case that raised produced no row anywhere, so nothing below can see
        # it -- without this the status line would quote the discovered count
        # beside a mean taken over fewer cases and read as a complete sweep.
        parts.append("[!] %d of %d case(s) could NOT be analysed at all: %s"
                     % (len(broken), discovered, ", ".join(broken[:6])))
    metrics = report.get("metric_rows") or []
    unproven = [r for r in metrics
                if r.get("score_reproduced") is False
                or r.get("safe_points_reproduced") is False]
    if unproven:
        parts.append("[!] the recomputation does NOT match what the run logged "
                     "for %s -- see the console"
                     % ", ".join(sorted({r["case"] for r in unproven})))
    failed = sorted({r["case"] for r in metrics if r.get("error")})
    if failed:
        parts.append("[!] %d case(s) with a problem: %s"
                     % (len(failed), ", ".join(failed[:6])))
    parts.append("Full detail in the Python console.")
    return "  |  ".join(parts)


def _summarise(report):
    lines = ["Saved: %s" % report.get("workbook_relative", ""), ""]
    lines.extend(report.get("log") or [])

    comparison = report.get("comparison_rows") or []
    if comparison:
        lines.append("")
        lines.append("PIPELINE vs the surgeon's HAND PLAN "
                     "(same entry, same cone, same denominator)")
        lines.append("  %-9s %5s %9s %9s %9s %6s %9s  %s"
                     % ("case", "screw", "delta_pl", "delta_man", "gain",
                        "wins?", "apart_deg", "selection"))
        for row in comparison:
            lines.append("  %-9s %5d %9.3f %9.3f %+9.3f %6s %9s  %s"
                         % (row["case"], row["screw"], row["delta_pipeline"],
                            row["delta_manual"], row["delta_gain"],
                            "yes" if row["pipeline_denser"] else "NO",
                            "%.2f" % row["plans_apart_deg"]
                            if row.get("plans_apart_deg") is not None else "--",
                            row.get("selection") or "?"))

    angles = [r for r in report.get("angle_rows") or []
              if r.get("theta3_deg") is not None]
    if angles:
        lines.append("")
        lines.append("Screw / peg angles (deg)")
        lines.append("  %-9s %-9s %8s %8s %8s %10s"
                     % ("case", "plan", "theta1", "theta2", "theta3", "cone half"))
        for row in angles:
            lines.append("  %-9s %-9s %8.3f %8.3f %8.3f %10.2f"
                         % (row["case"], row.get("plan") or "?",
                            row["theta1_deg"], row["theta2_deg"],
                            row["theta3_deg"], row.get("cone_half_angle_deg") or 0.0))

    metrics = [r for r in report.get("metric_rows") or [] if r.get("delta") is not None]
    if metrics:
        lines.append("")
        lines.append("Bone-density ratio (integral / cone-space maximum)")
        lines.append("  %-9s %5s %-9s %9s %9s %8s %9s %6s  %s"
                     % ("case", "screw", "plan", "chosen", "max", "delta",
                        "searched", "repro", "selection"))
        for row in metrics:
            lines.append("  %-9s %5d %-9s %9d %9d %8.3f %9s %6s  %s"
                         % (row["case"], row["screw"], row.get("plan") or "?",
                            row["integral_chosen"],
                            row["integral_max_cone"], row["delta"],
                            "%.3f" % row["delta_searched"]
                            if row.get("delta_searched") is not None else "--",
                            "yes" if row.get("score_reproduced") else
                            ("NO" if row.get("score_reproduced") is False else "--"),
                            row.get("selection") or "?"))

    broken = [r for r in report.get("metric_rows") or [] if r.get("error")]
    for row in broken:
        lines.append("  [!] %s screw %s: %s"
                     % (row.get("case"), row.get("screw"), row["error"]))

    phases = report.get("phase_rows") or []
    if phases:
        lines.append("")
        lines.append("Phase timing (s) — t1 bone model, t2 reference frame, "
                     "t3 automatic planning")
        lines.append("  %-9s %8s %8s %8s %8s %9s %9s"
                     % ("case", "t0", "t1", "t2", "t3", "t_refine", "total"))
        for row in phases:
            lines.append("  %-9s %8.2f %8.2f %8.2f %8.2f %9.2f %9s"
                         % (row["case"], row.get("t0_s") or 0.0,
                            row.get("t1_s") or 0.0, row.get("t2_s") or 0.0,
                            row.get("t3_s") or 0.0, row.get("t_refine_s") or 0.0,
                            "%.2f" % row["t_total_s"]
                            if row.get("t_total_s") is not None else "--"))
        lines.append("  (t3 is the cone search alone; the surgeon's own time sits "
                     "in t2 and t_refine)")

    summary = report.get("summary") or []
    if summary:
        lines.append("")
        lines.append("Across all cases")
        for row in summary:
            if row.get("mean") is None:
                # A count, not a distribution -- its note IS the statement, so
                # printing empty mean/sd/min/max columns beside it would only
                # invite them to be read as zeros.
                lines.append("  %-42s %s" % (row["metric"], row.get("note") or ""))
                continue
            lines.append("  %-42s n=%-3s mean=%-10s sd=%-10s [%s .. %s]"
                         % (row["metric"], row.get("n"), row.get("mean"),
                            row.get("sd"), row.get("min"), row.get("max")))
    return "\n".join(lines)
