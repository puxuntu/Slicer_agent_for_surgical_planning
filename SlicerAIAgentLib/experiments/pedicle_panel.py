"""The Experiments panel for PedicleScrewPlanner: one button, one workbook.

Kept apart from ``pedicle.py`` so the numerics stay Qt-free -- and, here,
Slicer-free as well -- so ``scripts/check_pedicle_analysis.py`` can run the whole
analysis outside Slicer. This half only wires a button to it and reports what
happened.

No confirmation dialog and no scene-close warning, unlike ``orbital_panel``: the
analysis builds nothing in the MRML scene and touches nothing the user has open.
It does need a per-case progress dialog, because a case decompresses a
segmentation and a CT and runs three distance transforms -- about ten seconds on
the Qt main thread, which without a dialog is the difference between "Slicer is
busy" and "Slicer has hung".

The one control beside the button is the density checkbox, and it is a real
choice rather than a setting: unticked, the case's CT is never read, which saves
decompressing 250-450 MB per case and leaves only the HU columns blank. Every
positional measure -- breach, grade, clearance, containment, fill, depth -- is
taken against the segmentation and is identical either way.
"""

from __future__ import annotations

import logging
import os

import qt
import slicer

from ..app.widget_experiments import register_experiment_panel
from . import pedicle, run_timing

logger = logging.getLogger(__name__)


@register_experiment_panel(pedicle.EXTENSION_NAME)
def build_panel(widget, layout, extension):
    root = _repository_root()
    # Resolved, never joined: the folder may sit under a tier
    # (Experiments/1_Quanti_Eva/<Ext>/) whose name belongs to the
    # study and has already changed once.
    experiment_dir = run_timing.resolve_experiment_dir(
        root, pedicle.EXPERIMENT_DIR)
    # What the prose below should NAME -- the resolved location,
    # so "no cases found" never sends a reader to the wrong folder.
    shown_dir = run_timing.experiment_dir_label(
        root, pedicle.EXPERIMENT_DIR)

    intro = qt.QLabel(
        "Scores every planned screw in every run under <code>{runs}</code> "
        "against the per-vertebra ground truth in "
        "<code>Dataset/&lt;case&gt;/segmentation.seg.nrrd</code>.<br>"
        "<b>Safety</b> — Gertzbein–Robbins grade and the millimetres behind it, "
        "which wall the screw crosses, the clearance to each wall, and whether "
        "the tip perforates the anterior cortex. <b>Fit</b> — containment, the "
        "pedicle width at the isthmus and the fill ratio against it, and the "
        "screw's length as a share of the depth available. <b>Bone</b> — the "
        "median HU <i>inside</i> the volume the screw occupies (not merely on "
        "its surface), the contact area in each density band, and the "
        "vertebral trabecular HU with the cortex eroded away.<br>"
        "Each screw is matched to its vertebra by the surgeon's own "
        "<b>isthmus landmark</b>, never by name — the plan's <code>_L</code>/"
        "<code>_R</code> suffix follows the order the landmarks were placed and "
        "its level follows what was picked in the wizard, so neither is "
        "evidence. Where the two names disagree the workbook says so and scores "
        "against the landmark.<br>"
        "Two tabs are written beside the runs: <b>Screw accuracy</b> and "
        "<b>Timing</b> (t₀ load, t₁ ROI and levels, t₂ landmarks, t₃ plan the "
        "screws, t₄ grade)."
        .format(runs=os.path.join(shown_dir, pedicle.RUNS_SUBDIR))
    )
    intro.setWordWrap(True)
    intro.setTextFormat(qt.Qt.RichText)
    layout.addWidget(intro)

    cases = pedicle.discover_cases(experiment_dir)
    count = len(cases)
    # A run whose data set is missing cannot be scored at all. Naming those is
    # worth a line: the alternative is a case count that is quietly short.
    incomplete = [c for c in cases if not pedicle.case_is_scorable(c)]

    found = qt.QLabel(
        ("%d run(s) found.%s"
         % (count, ("  [!] %d without a ground truth: %s"
                    % (len(incomplete), ", ".join(c["subject"] or c["run"]
                                                  for c in incomplete[:6])))
            if incomplete else ""))
        if count else
        "No runs found — each needs a Statistic/scene/ folder, and a "
        "Dataset/<subject>/ beside it holding segmentation.seg.nrrd.")
    found.setWordWrap(True)
    found.setStyleSheet("color: #b00;" if (incomplete or not count) else "color: gray;")
    layout.addWidget(found)

    density = qt.QCheckBox("Also read the CT (bone density columns)")
    density.setChecked(True)
    density.setToolTip(
        "On (recommended): read each case's CT and report the path HU inside "
        "the screw's own volume, the contact area in each density band, the "
        "surface HU percentiles and the vertebral trabecular HU.\n\n"
        "Off: skip it. That saves decompressing 250-450 MB per case and leaves "
        "only those columns blank — every positional measure is taken against "
        "the segmentation and is identical either way.")
    layout.addWidget(density)

    button = qt.QPushButton("Analyse screw accuracy + timing  ->  Excel")
    button.setToolTip(
        "For every planned screw: its Gertzbein-Robbins grade against the "
        "ground-truth vertebra, its clearance to each pedicle wall, how much of "
        "it is in bone, how well it fills the pedicle, and the bone it is "
        "gripping. Written to one .xlsx beside the runs.\n\n"
        "Reads only; the current scene is left alone.")
    button.setEnabled(bool(count))
    layout.addWidget(button)

    def _run():
        with_density = bool(density.checked)
        progress = _progress_dialog(count)
        button.setEnabled(False)
        found.setStyleSheet("color: gray;")
        found.setText("Analysing %d run(s)..." % count)

        def _tick(index, total, label):
            if progress is None:
                return
            progress.setLabelText("Case %d of %d: %s" % (index + 1, total, label))
            progress.setValue(index)
            slicer.app.processEvents()

        try:
            report = pedicle.run_analysis(root, progress=_tick,
                                          with_density=with_density)
        except Exception as exc:
            logger.warning("Pedicle experiment analysis failed", exc_info=True)
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
        progress.setLabelText("Analysing %d run(s)..." % count)
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
    rows = [r for r in report.get("rows") or [] if r.get("grade")]

    if rows:
        acceptable = sum(1 for r in rows
                         if r["grade"] in pedicle.ACCEPTABLE_GRADES)
        worst = max((r["breach_mm"] for r in rows
                     if r.get("breach_mm") is not None), default=None)
        parts.append("%d run(s), %d screw(s): %d at grade A/B, worst breach "
                     "%.2f mm" % (analysed, len(rows), acceptable, worst or 0.0))
        gated = [r for r in rows if r.get("gate_pass") is not None]
        if gated:
            parts.append("%d of %d pass the safety gate"
                         % (sum(1 for r in gated if r["gate_pass"]), len(gated)))

    # Four things a reader must not take at face value, so they are said here
    # and not only in the console.
    if not report.get("with_density"):
        parts.append("[!] the CT was NOT read; density columns are blank")
    broken = report.get("failed_cases") or []
    if broken:
        # A run that raised produced no row anywhere, so nothing above can see
        # it -- without this the status line would quote the discovered count
        # beside figures taken over fewer runs and read as a complete sweep.
        parts.append("[!] %d of %d run(s) could NOT be analysed at all: %s"
                     % (len(broken), discovered, ", ".join(broken[:6])))
    unscored = [r for r in report.get("rows") or [] if not r.get("grade")]
    if unscored:
        parts.append("[!] %d screw(s) not scored -- see the status column"
                     % len(unscored))
    mislabelled = [r for r in report.get("rows") or []
                   if r.get("name_agrees") is False]
    if mislabelled:
        parts.append("[!] %d screw(s) name a different level from the one their "
                     "landmark is in" % len(mislabelled))
    parts.append("Full detail in the Python console.")
    return "  |  ".join(parts)


def _summarise(report):
    lines = ["Saved: %s" % report.get("workbook_relative", ""), ""]
    lines.extend(report.get("log") or [])

    rows = [r for r in report.get("rows") or [] if r.get("grade")]
    if rows:
        lines.append("")
        lines.append("Per screw, against the vertebra its isthmus landmark is in")
        lines.append("  %-8s %-8s %-14s %-6s %5s %5s %5s %-2s %-9s %8s %8s %7s %6s"
                     % ("case", "site", "level", "side", "dia", "len", "breach",
                        "GR", "wall", "medial", "contain", "fill", "gate"))
        for row in rows:
            lines.append("  %-8s %-8s %-14s %-6s %5s %5s %5s %-2s %-9s %8s %7s%% %6s%% %6s"
                         % (row["case"], (row.get("site") or "")[:8],
                            (row.get("level") or "")[:14], row.get("side") or "",
                            _number(row.get("diameter_mm"), 1),
                            _number(row.get("length_mm"), 0),
                            _number(row.get("breach_mm"), 2), row.get("grade"),
                            row.get("breach_direction") or "",
                            _number(row.get("medial_clearance_mm"), 2),
                            _number(row.get("containment_pct"), 1),
                            _number(row.get("fill_ratio_pct"), 0),
                            _verdict(row.get("gate_pass"))))

    broken = [r for r in report.get("rows") or [] if r.get("status")]
    for row in broken:
        lines.append("  [!] %s / %s: %s" % (row.get("case"), row.get("screw"),
                                            row["status"]))

    levels = report.get("levels") or []
    if levels:
        lines.append("")
        lines.append("Per level")
        lines.append("  %-8s %-14s %6s %8s %10s %12s"
                     % ("case", "level", "screws", "worst", "symmetry",
                        "trabecular"))
        for row in levels:
            lines.append("  %-8s %-14s %6d %5s %-2s %8s deg %9s HU"
                         % (row["case"], row["level"][:14], row["screws"],
                            _number(row.get("worst_breach_mm"), 2),
                            row.get("worst_grade") or "",
                            _number(row.get("symmetry_deg"), 1),
                            _number(row.get("trabecular_hu"), 0)))

    grades = report.get("grades") or []
    if grades:
        lines.append("")
        lines.append("Gertzbein-Robbins distribution")
        for row in grades:
            lines.append("  %-3s %3d screw(s)  %5s%%   %s"
                         % (row["grade"], row["screws"],
                            _number(row.get("share_pct"), 1), row["meaning"]))

    phases = report.get("phase_rows") or []
    if phases:
        lines.append("")
        lines.append("Phase timing (s) — t0 load, t1 ROI/levels, t2 landmarks, "
                     "t3 plan the screws, t4 grade")
        lines.append("  %-8s %8s %8s %8s %8s %8s %9s %9s"
                     % ("case", "t0", "t1", "t2", "t3", "t4", "unphased",
                        "total"))
        for row in phases:
            lines.append("  %-8s %8s %8s %8s %8s %8s %9s %9s"
                         % (row["case"],
                            _number(row.get("t0_s"), 2), _number(row.get("t1_s"), 2),
                            _number(row.get("t2_s"), 2), _number(row.get("t3_s"), 2),
                            _number(row.get("t4_s"), 2),
                            _number(row.get("unphased_s"), 2),
                            _number(row.get("t_total_s"), 2)))

    summary = report.get("summary") or []
    if summary:
        lines.append("")
        lines.append("Across every scored screw")
        for row in summary:
            if row.get("sd") is None:
                # A share or a count, not a distribution -- its note IS the
                # statement, and printing empty sd/min/max beside it would only
                # invite them to be read as zeros.
                lines.append("  %-34s n=%-4s %-9s %s"
                             % (row["metric"], row.get("n"),
                                _number(row.get("mean"), 1)
                                if row.get("mean") is not None else "",
                                row.get("note") or ""))
                continue
            lines.append("  %-34s n=%-4s mean=%-9s sd=%-9s [%s .. %s]"
                         % (row["metric"], row.get("n"), row.get("mean"),
                            row.get("sd"), row.get("min"), row.get("max")))
    return "\n".join(lines)


def _number(value, digits=3):
    return ("%.*f" % (digits, value)) if isinstance(value, (int, float)) else "--"


def _verdict(value):
    """'yes' / 'NO' / '--', where '--' means the verdict could not be reached.

    A blank and a failure must not print the same: an unscored screw has no
    verdict, while a scored one that failed is a finding.
    """
    if value is None:
        return "--"
    return "yes" if value else "NO"
