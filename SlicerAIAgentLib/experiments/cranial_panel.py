"""The Experiments panel for CranialImplantPlanning: one button.

Kept apart from ``cranial.py`` the same way ``orbital_panel.py`` is kept apart
from ``orbital.py``: this half only wires a button to the analysis and reports
what happened.

It warns before running, for orbital's reason: the colour error maps are built in
the main MRML scene -- the only way to write a scene file Slicer is certain to be
able to reopen -- so the analysis CLOSES whatever the user has open.
"""

from __future__ import annotations

import logging
import os

import qt
import slicer

from ..app.widget_experiments import register_experiment_panel
from . import cranial

logger = logging.getLogger(__name__)


@register_experiment_panel(cranial.EXTENSION_NAME)
def build_panel(widget, layout, extension):
    root = _repository_root()
    experiment_dir = os.path.join(root, cranial.EXPERIMENT_DIR)

    intro = qt.QLabel(
        "Scores every run under <code>{runs}</code> against the surgeon's "
        "<code>Ground Truth.seg.nrrd</code>, which each run saved beside its own "
        "result, and writes one workbook there.<br>"
        "The three metrics are the AutoImplant 2021 challenge's: <b>DSC</b>, "
        "<b>HD95</b> (mm) and <b>bDSC</b> — Dice restricted to the part of each "
        "implant within {t:.0f} voxels of the <i>defective</i> skull, which is "
        "where the fit is decided.<br>"
        "It also writes a <b>colour map on the predicted implant</b> into each "
        "case's <code>Statistic/scene/</code> (0–{mm:.0f} mm, green→red, the same "
        "scale on every case): open <code>ErrorMaps.mrml</code> for just that, or "
        "the run's own <code>scene.mrml</code>, which it is added to."
        .format(runs=os.path.join(cranial.EXPERIMENT_DIR, cranial.RUNS_SUBDIR),
                t=cranial.BORDER_DISTANCE_VOXELS, mm=cranial.COLOR_MAX_MM)
    )
    intro.setWordWrap(True)
    intro.setTextFormat(qt.Qt.RichText)
    layout.addWidget(intro)

    cases = cranial.discover_cases(experiment_dir)
    count = len(cases)
    missing = [c for c in cases if not cranial.case_is_scorable(c)]

    found = qt.QLabel(
        "%d case(s) found.%s" % (count, ("  [!] %d without both segmentations: %s"
                                         % (len(missing),
                                            ", ".join(c["subject"] or c["run"]
                                                      for c in missing[:6])))
         if missing else "")
        if count else
        "No cases found — each run needs a Statistic/scene/ folder.")
    found.setWordWrap(True)
    found.setStyleSheet("color: #b00;" if (missing or not count) else "color: gray;")
    layout.addWidget(found)

    button = qt.QPushButton("Analyse DSC / HD95 / bDSC + timing  ->  Excel + colour maps")
    button.setToolTip(
        "For every case: read the ground-truth implant and the predicted implant "
        "from the run's own scene folder, compute DSC, HD95 and border DSC, write "
        "them and the run timing to one .xlsx, and save a colour error map per "
        "case.\n\n"
        "This CLOSES the current scene.")
    button.setEnabled(bool(count))
    layout.addWidget(button)

    def _run():
        # A guided run owns the scene and this analysis clears it. The teardown a
        # scene close triggers is correct but silent, so a half-finished
        # procedure would simply vanish; refusing is the only outcome that
        # cannot surprise anyone.
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
            report = cranial.run_analysis(root, progress=_tick)
        except Exception as exc:
            logger.warning("Cranial experiment analysis failed", exc_info=True)
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
        box.setWindowTitle("Analyse cranial implant accuracy")
        box.setText("Analyse %d case(s)?" % count)
        box.setInformativeText(
            "This CLOSES the current scene — each case's colour map is built in "
            "it. Anything open and unsaved is lost.\n\n"
            "It writes ErrorMaps.mrml, two .vtp models and a colour table into "
            "every case's Statistic/scene/, and adds the error map to that run's "
            "own scene.mrml (backing the original up as scene.mrml.orig the first "
            "time). Re-running replaces them rather than adding more.\n\n"
            "Roughly 3 seconds per case.")
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
        if row["metric"] == "DSC" and row.get("cases"):
            parts.append("DSC mean %.4f / median %.4f over %d case(s)"
                         % (row["mean"], row["median"], row["cases"]))
        elif row["metric"].startswith("HD95") and row.get("cases"):
            parts.append("HD95 median %.2f mm" % row["median"])
    failed = sorted({r["case"] for r in report.get("rows") or [] if r.get("error")})
    if failed:
        parts.append("[!] %d case(s) with a problem: %s"
                     % (len(failed), ", ".join(failed[:6])))
    parts.append("Full detail in the Python console.")
    return "  |  ".join(parts)


def _summarise(report):
    lines = ["Saved: %s" % report.get("workbook_relative", ""), ""]
    lines.extend(report.get("log") or [])

    rows = [r for r in report.get("rows") or [] if r.get("dsc") is not None]
    if rows:
        lines.append("")
        lines.append("Implant accuracy against the ground truth")
        lines.append("  %-9s %8s %8s %9s %9s" % ("case", "DSC", "bDSC", "HD95 mm",
                                                 "ASSD mm"))
        for row in rows:
            lines.append("  %-9s %8.4f %8.4f %9.3f %9.3f"
                         % (row["case"], row["dsc"], row.get("bdsc") or float("nan"),
                            row.get("hd95_mm") or float("nan"),
                            row.get("assd_mm") or float("nan")))

    summary = report.get("summary") or []
    if summary:
        lines.append("")
        lines.append("Across all %d scored case(s)" % report.get("scored", 0))
        lines.append("  %-24s %8s %8s %8s %8s %8s"
                     % ("metric", "mean", "median", "std", "min", "max"))
        for row in summary:
            if not row.get("cases"):
                continue
            lines.append("  %-24s %8s %8s %8s %8s %8s"
                         % (row["metric"], row["mean"], row["median"],
                            row["std"], row["min"], row["max"]))
    return "\n".join(lines)
