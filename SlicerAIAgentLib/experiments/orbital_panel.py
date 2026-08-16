"""The Experiments panel for OrbitalFractureReconstruction: one button.

Kept apart from ``orbital.py`` for the same reason ``zygomatic_panel.py`` is:
this half only wires a button to the analysis and reports what happened.

Unlike the zygomatic one it must warn first. The analysis builds each case's
error maps in the main MRML scene -- the only way to write a scene file Slicer is
certain to be able to reopen -- so it CLOSES whatever the user has open. That is
cheap to say and expensive to discover.
"""

from __future__ import annotations

import logging
import os

import qt
import slicer

from ..app.widget_experiments import register_experiment_panel
from . import orbital

logger = logging.getLogger(__name__)


@register_experiment_panel(orbital.EXTENSION_NAME)
def build_panel(widget, layout, extension):
    root = _repository_root()
    experiment_dir = os.path.join(root, orbital.EXPERIMENT_DIR)

    intro = qt.QLabel(
        "Scores every run under <code>{runs}</code> against the surgeon's ground "
        "truth in <code>{data}/&lt;subject&gt;/&lt;subject&gt;_Label.nii.gz</code>, "
        "and writes the tables to one workbook beside the runs.<br>"
        "Two comparisons per case, both symmetric surface distance in mm: the "
        "pipeline's <code>OFR_Reconstructed_Seg</code>, and the "
        "<code>OFR_Fractured_Seg</code> it started from — the second is what "
        "makes the first mean anything.<br>"
        "It also writes <b>two colour maps on the ground-truth surface</b> into "
        "each case's <code>Statistic/scene/</code> (0–{mm:.0f} mm, green→red, the "
        "same scale on every case): open <code>ErrorMaps.mrml</code> for just "
        "those, or the run's own <code>scene.mrml</code>, which they are added to."
        .format(runs=os.path.join(orbital.EXPERIMENT_DIR, orbital.RUNS_SUBDIR),
                data=os.path.join(orbital.EXPERIMENT_DIR, orbital.DATASET_SUBDIR),
                mm=orbital.COLOR_MAX_MM)
    )
    intro.setWordWrap(True)
    intro.setTextFormat(qt.Qt.RichText)
    layout.addWidget(intro)

    cases = orbital.discover_cases(experiment_dir)
    count = len(cases)
    missing = [c for c in cases if not os.path.isfile(orbital.ground_truth_path(c))]

    found = qt.QLabel(
        "%d case(s) found.%s" % (count, ("  [!] %d without a ground-truth label: %s"
                                         % (len(missing),
                                            ", ".join(c["subject"] or c["run"]
                                                      for c in missing[:6])))
         if missing else "")
        if count else
        "No cases found — each run needs a Statistic/scene/ folder.")
    found.setWordWrap(True)
    found.setStyleSheet("color: #b00;" if (missing or not count) else "color: gray;")
    layout.addWidget(found)

    button = qt.QPushButton("Analyse surface error + timing  ->  Excel + colour maps")
    button.setToolTip(
        "For every case: mesh the ground truth, the reconstruction and the "
        "fractured orbit through one pipeline, measure the symmetric surface "
        "distance of each against the ground truth, write the numbers and the "
        "run timing to one .xlsx, and save two colour maps per case.\n\n"
        "This CLOSES the current scene.")
    button.setEnabled(bool(count))
    layout.addWidget(button)

    def _run():
        # A guided run owns the scene, and this analysis clears it. The teardown
        # that a scene close triggers is correct but silent, so a procedure
        # half-finished behind the Experiments section would simply vanish;
        # refusing is the only outcome that cannot surprise anyone.
        runtime = getattr(widget, "_workflowRuntime", None)
        if runtime is not None and getattr(runtime, "session", None) is not None:
            found.setStyleSheet("color: #b00;")
            found.setText("A guided workflow is open — press Exit on its panel "
                          "before running the analysis (this closes the scene).")
            return
        if not _confirm(count):
            return
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
            report = orbital.run_analysis(root, progress=_tick)
        except Exception as exc:
            logger.warning("Orbital experiment analysis failed", exc_info=True)
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

        print(_summarise(report))
        found.setText(_outcome(report))

    button.clicked.connect(_run)


def _confirm(count):
    """Say the one thing that is not obvious before doing it."""
    try:
        box = qt.QMessageBox(slicer.util.mainWindow())
        box.setIcon(qt.QMessageBox.Question)
        box.setWindowTitle("Analyse orbital surface error")
        box.setText("Analyse %d case(s)?" % count)
        box.setInformativeText(
            "This CLOSES the current scene — each case's colour maps are built "
            "in it. Anything open and unsaved is lost.\n\n"
            "It writes ErrorMaps.mrml, three .vtp models and a colour table into "
            "every case's Statistic/scene/, and adds the two error maps to that "
            "run's own scene.mrml (backing the original up as scene.mrml.orig "
            "the first time). Re-running replaces them rather than adding more.")
        analyse = box.addButton("Close the scene and analyse", qt.QMessageBox.AcceptRole)
        cancel = box.addButton("Cancel", qt.QMessageBox.RejectRole)
        box.setDefaultButton(cancel)
        box.setEscapeButton(cancel)
        box.deleteLater()
        box.exec_()
        # By role, not identity: PythonQt can hand back a fresh wrapper for the
        # same button (the same reason _askExitChoice reads roles).
        return box.buttonRole(box.clickedButton()) == qt.QMessageBox.AcceptRole
    except Exception:
        logger.debug("Confirmation dialog failed", exc_info=True)
        # Cancel, not proceed: the dialog exists to authorise closing the scene,
        # so a dialog nobody saw cannot have authorised it.
        return False


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
    parts = ["Saved %s" % report.get("workbook_relative", "")]
    for row in report.get("summary") or []:
        if row["comparison"] == "Reconstructed":
            parts.append("reconstruction ASSD %.2f mm over %d case(s)"
                         % (row["mean_assd_mm"], row["cases"]))
        elif row["comparison"].startswith("IMPROVEMENT"):
            parts.append("improved in %d/%d case(s)"
                         % (row.get("cases_improved", 0), row["cases"]))
    failed = sorted({r["case"] for r in report.get("rows") or [] if r.get("error")})
    if failed:
        parts.append("[!] %d case(s) with a problem: %s"
                     % (len(failed), ", ".join(failed[:6])))
    parts.append("Full detail in the Python console.")
    return "  |  ".join(parts)


def _summarise(report):
    lines = ["Saved: %s" % report.get("workbook_relative", ""), ""]
    lines.extend(report.get("log") or [])

    rows = [r for r in report.get("rows") or [] if r.get("assd_mm") is not None]
    if rows:
        lines.append("")
        lines.append("Surface distance to the ground truth (mm)")
        lines.append("  %-9s %-14s %8s %8s %8s %10s"
                     % ("case", "comparison", "assd", "rms", "hd95", "<=1mm %"))
        for row in rows:
            lines.append("  %-9s %-14s %8.3f %8.3f %8.3f %10.1f"
                         % (row["case"], row["comparison"], row["assd_mm"],
                            row["rms_mm"], row["hd95_mm"], row["within_1mm_pct"]))

    improvements = report.get("improvements") or []
    if improvements:
        lines.append("")
        lines.append("Improvement (fractured -> reconstructed)")
        lines.append("  %-9s %10s %10s %10s %9s"
                     % ("case", "before", "after", "delta", "better?"))
        for row in improvements:
            lines.append("  %-9s %10.3f %10.3f %10.3f %9s"
                         % (row["case"], row["fractured_assd_mm"],
                            row["reconstructed_assd_mm"], row["assd_improvement_mm"],
                            "yes" if row["improved"] else "NO"))

    for row in report.get("summary") or []:
        lines.append("")
        lines.append("%s: %d case(s), mean ASSD %s mm, mean HD95 %s mm"
                     % (row["comparison"], row["cases"],
                        row["mean_assd_mm"], row["mean_hd95_mm"]))
    return "\n".join(lines)
