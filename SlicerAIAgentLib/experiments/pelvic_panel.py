"""The Experiments panel for PelvicFracturePlanning: one button, one workbook.

Kept apart from ``pelvic.py`` so the numerics stay Qt-free -- and, here,
Slicer-free as well -- so ``scripts/check_pelvic_analysis.py`` can run the whole
analysis outside Slicer. This half only wires a button to it and reports what
happened.

No confirmation dialog and no scene-close warning, unlike ``orbital_panel``: this
analysis builds nothing in the MRML scene and touches nothing the user has open.

The one control beside the button is the verification checkbox, and it is a real
choice rather than a setting: unticked, the analysis reads only each run's
transforms file and finishes in milliseconds; ticked, it also decompresses two
segmentations per case -- 900 MB of voxels for a whole pelvis -- to prove the
record was written for the files beside it. That is why the run gets a per-case
progress dialog: with verification on, half a minute per case on the Qt main
thread is the difference between "Slicer is busy" and "Slicer has hung".
"""

from __future__ import annotations

import logging
import os

import qt
import slicer

from ..app.widget_experiments import register_experiment_panel
from . import pelvic

logger = logging.getLogger(__name__)


@register_experiment_panel(pelvic.EXTENSION_NAME)
def build_panel(widget, layout, extension):
    root = _repository_root()
    experiment_dir = os.path.join(root, pelvic.EXPERIMENT_DIR)

    intro = qt.QLabel(
        "Scores every run under <code>{runs}</code> from the transform each run "
        "<b>recorded</b> when its ground truth was saved "
        "(<code>Ground truth*.transforms.json</code>). That file holds, per "
        "piece, the rigid transform from where the pipeline put it to where the "
        "surgeon says it belongs — which <i>is</i> the reduction error — so "
        "<b>displacement</b> (mm) and <b>rotation</b> (deg) are read, not "
        "estimated.<br>"
        "The segmentations are still read for the four things the record cannot "
        "say: how large the error is <b>at the bone surface</b> rather than at "
        "one reference point (<code>point_error_max_mm</code>), whether the "
        "record was written for the files beside it "
        "(<code>transform_residual_mm</code>), whether the paired segments are "
        "the same object, and which pieces the reduction moved that nobody "
        "annotated.<br>"
        "Two tabs are written beside the runs: <b>Reduction accuracy</b> and "
        "<b>Timing</b> (t₀ setup, t₁ segment the pelvis, t₂ segment and "
        "separate the fractures, t₃ reduction template, t₄ reduce the "
        "fragments, t₅ plan the screws)."
        .format(runs=os.path.join(pelvic.EXPERIMENT_DIR, pelvic.RUNS_SUBDIR))
    )
    intro.setWordWrap(True)
    intro.setTextFormat(qt.Qt.RichText)
    layout.addWidget(intro)

    cases = pelvic.discover_cases(experiment_dir)
    count = len(cases)
    # A run missing any of the three files cannot be scored. Naming them is worth
    # a line: the alternative is a case count that is quietly short.
    incomplete = [c for c in cases if not pelvic.case_is_scorable(c)]

    found = qt.QLabel(
        ("%d case(s) found.%s"
         % (count, ("  [!] %d without all three files: %s"
                    % (len(incomplete), ", ".join(c["subject"] or c["run"]
                                                  for c in incomplete[:6])))
            if incomplete else ""))
        if count else
        "No cases found — each run needs a Statistic/scene/ folder.")
    found.setWordWrap(True)
    found.setStyleSheet("color: #b00;" if (incomplete or not count) else "color: gray;")
    layout.addWidget(found)

    verify = qt.QCheckBox("Check each record against the saved segmentations")
    verify.setChecked(True)
    verify.setToolTip(
        "On (recommended): apply each recorded transform to the reduction's own "
        "surface and measure how far it lands from the ground truth's. This is "
        "the only check that catches a transforms file written before its "
        "ground truth was last re-saved — the one way a recorded number can be "
        "wrong. It also supplies the surface error, the volumes and the list of "
        "pieces nobody annotated.\n\n"
        "Off: read the transforms files alone. Displacement and rotation are "
        "identical either way, and it takes milliseconds instead of about half "
        "a minute per case.")
    layout.addWidget(verify)

    button = qt.QPushButton("Analyse reduction error + timing  ->  Excel")
    button.setToolTip(
        "For every case: read the recorded per-piece transform, and write its "
        "displacement and rotation, the surface error they imply, and the run "
        "timing to one .xlsx beside the runs.\n\n"
        "Reads only; the current scene is left alone.")
    button.setEnabled(bool(count))
    layout.addWidget(button)

    def _run():
        checking = bool(verify.checked)
        progress = _progress_dialog(count) if checking else None
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
            report = pelvic.run_analysis(root, progress=_tick, verify=checking)
        except Exception as exc:
            logger.warning("Pelvic experiment analysis failed", exc_info=True)
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
        if row["metric"].startswith("displacement") and row.get("mean") is not None:
            parts.append("%d case(s): displacement mean %.2f mm (max %.2f)"
                         % (analysed, row["mean"], row["max"]))
        elif row["metric"].startswith("rotation") and row.get("mean") is not None:
            parts.append("rotation mean %.2f deg (max %.2f)"
                         % (row["mean"], row["max"]))
        elif row["metric"].startswith("point error, max") \
                and row.get("mean") is not None:
            parts.append("worst surface point mean %.2f mm (max %.2f)"
                         % (row["mean"], row["max"]))

    # Four things a reader must not take at face value, so they are said here and
    # not only in the console.
    if not report.get("verified"):
        parts.append("[!] records NOT checked against the segmentations")
    broken = report.get("failed_cases") or []
    if broken:
        # A case that raised produced no row anywhere, so nothing below can see
        # it -- without this the status line would quote the discovered count
        # beside a mean taken over fewer cases and read as a complete sweep.
        parts.append("[!] %d of %d case(s) could NOT be analysed at all: %s"
                     % (len(broken), discovered, ", ".join(broken[:6])))
    rows = report.get("rows") or []
    suspect = [r for r in rows if r.get("record_consistent") is False
               or r.get("transform_verified") is False]
    if suspect:
        parts.append("[!] %d recorded transform(s) failed a verdict: %s"
                     % (len(suspect),
                        ", ".join(sorted({"%s/%s" % (r["case"], r["segment"])
                                          for r in suspect})[:4])))
    unscored = [r for r in rows if r.get("displacement_mm") is None]
    if unscored:
        parts.append("[!] %d recorded piece(s) not scored -- see the status "
                     "column" % len(unscored))
    parts.append("Full detail in the Python console.")
    return "  |  ".join(parts)


def _summarise(report):
    lines = ["Saved: %s" % report.get("workbook_relative", ""), ""]
    lines.extend(report.get("log") or [])

    rows = [r for r in report.get("rows") or []
            if r.get("displacement_mm") is not None]
    if rows:
        lines.append("")
        lines.append("Recorded reduction error, per annotated piece")
        lines.append("  %-8s %-26s %9s %9s %10s %9s %9s %7s"
                     % ("case", "piece", "disp mm", "rot deg", "pt err mm",
                        "HD95 mm", "resid mm", "ok?"))
        for row in rows:
            lines.append("  %-8s %-26s %9.3f %9.3f %10s %9s %9s %7s"
                         % (row["case"], row["segment"][:26],
                            row["displacement_mm"], row["rotation_deg"],
                            _number(row.get("point_error_max_mm")),
                            _number(row.get("surface_hd95_mm")),
                            _number(row.get("transform_residual_mm")),
                            _verdict(row)))

    broken = [r for r in report.get("rows") or [] if r.get("error")]
    for row in broken:
        lines.append("  [!] %s / %s: %s" % (row.get("case"), row.get("segment"),
                                            row["error"]))

    unpaired = report.get("unpaired") or []
    if unpaired:
        lines.append("")
        lines.append("Moved by the reduction, no transform recorded "
                     "(nothing to score)")
        for row in unpaired:
            lines.append("  %-8s %-26s %10.1f mm3"
                         % (row["case"], row["segment"][:26],
                            row.get("volume_mm3") or 0.0))

    phases = report.get("phase_rows") or []
    if phases:
        lines.append("")
        lines.append("Phase timing (s) — t1 segment pelvis, t2 segment/separate "
                     "fractures, t3 template, t4 reduce, t5 screws")
        lines.append("  %-8s %7s %7s %7s %7s %7s %7s %9s"
                     % ("case", "t0", "t1", "t2", "t3", "t4", "t5", "total"))
        for row in phases:
            lines.append("  %-8s %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %9s"
                         % (row["case"],
                            row.get("t0_s") or 0.0, row.get("t1_s") or 0.0,
                            row.get("t2_s") or 0.0, row.get("t3_s") or 0.0,
                            row.get("t4_s") or 0.0, row.get("t5_s") or 0.0,
                            "%.2f" % row["t_total_s"]
                            if row.get("t_total_s") is not None else "--"))

    summary = report.get("summary") or []
    if summary:
        lines.append("")
        lines.append("Across all annotated pieces")
        for row in summary:
            if row.get("mean") is None:
                # A count, not a distribution -- its note IS the statement, so
                # printing empty mean/sd/min/max columns beside it would only
                # invite them to be read as zeros.
                lines.append("  %-32s n=%-4s %s"
                             % (row["metric"], row.get("n"), row.get("note") or ""))
                continue
            lines.append("  %-32s n=%-4s mean=%-9s sd=%-9s [%s .. %s]"
                         % (row["metric"], row.get("n"), row.get("mean"),
                            row.get("sd"), row.get("min"), row.get("max")))
    return "\n".join(lines)


def _number(value):
    return "%.3f" % value if isinstance(value, (int, float)) else "--"


def _verdict(row):
    """'yes' / 'NO' / '--', where '--' means the check did not run.

    A blank and a failure must not print the same: verification off is a choice
    the user made, a failed verdict is a finding.
    """
    if row.get("record_consistent") is False or row.get("transform_verified") is False:
        return "NO"
    if row.get("transform_verified") is None:
        return "--"
    return "yes"
