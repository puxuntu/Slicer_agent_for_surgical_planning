"""The Experiments panel for BoneReconstructionPlanner: one button, one workbook.

Kept apart from ``mandible.py`` so the numerics stay Qt-free -- and, here,
Slicer-free as well -- so ``scripts/check_mandible_analysis.py`` can run the
whole analysis outside Slicer. This half only wires a button to it and reports
what happened.

No confirmation dialog and no scene-close warning, unlike ``orbital_panel``: the
analysis builds nothing in the MRML scene and touches nothing the user has open.
It does need a per-case progress dialog, and for a reason the others do not
have: the first pass over a run RUNS A NETWORK (about 25 s on CPU) to predict
that patient's premorbid mandible, on the Qt main thread. Without a dialog that
is the difference between "Slicer is busy" and "Slicer has hung".

The one control beside the button is the re-predict checkbox, and it is a real
choice rather than a setting. Every prediction is cached inside the run it
belongs to, so the second sweep costs seconds and -- more importantly -- scores
against exactly the ground truth a reader can open. Ticking the box throws that
away and predicts again, which is what a new model or a changed input calls for
and nothing else does.
"""

from __future__ import annotations

import logging
import os

import qt
import slicer

from ..app.widget_experiments import register_experiment_panel
from . import mandible, run_timing

logger = logging.getLogger(__name__)


@register_experiment_panel(mandible.EXTENSION_NAME)
def build_panel(widget, layout, extension):
    root = _repository_root()
    # Resolved, never joined: the folder may sit under a tier
    # (Experiments/1_Quanti_Eva/<Ext>/) whose name belongs to the
    # study and has already changed once.
    experiment_dir = run_timing.resolve_experiment_dir(
        root, mandible.EXPERIMENT_DIR)
    # What the prose below should NAME -- the resolved location,
    # so "no cases found" never sends a reader to the wrong folder.
    shown_dir = run_timing.experiment_dir_label(
        root, mandible.EXPERIMENT_DIR)

    intro = qt.QLabel(
        "Scores the fibula reconstruction in every run under "
        "<code>{runs}</code> against the <b>healthy mandible segment that used "
        "to fill the defect</b>.<br>"
        "That segment is not in the scan — it was removed with the tumour — so "
        "it is predicted from <i>Cut Bones / Resected mandible</i> by the "
        "shape-completion network in <code>{model}</code>, and cached inside "
        "each run as <code>Statistic/analysis/{stl}</code>. The bone the "
        "surgeon actually took out is diseased, so it is reported for context "
        "and is never the reference.<br>"
        "<b>Headline metrics</b> — <b>Rv</b> volume ratio, <b>Ec</b> contour "
        "error and <b>Ep</b> maximum projection: the three Guo et al. "
        "(<i>Med. Image Anal.</i> 102, 2025, §4.2) take from Nakao et al. "
        "(<i>IEEE TBME</i> 64(8):1772, 2017), measured here the same way and "
        "against the same kind of predicted reference they used. Beside them: "
        "Dice, symmetric surface distance and HD95, the two 2 mm coverage "
        "shares, and Guo's own slice-weighted Dice objective (eqs. 4–5).<br>"
        "Nakao's mirror-symmetric distance <b>Er</b> is <i>not</i> computed — "
        "it needs the contralateral mandible and a located midline, neither of "
        "which the graft and the fibula can supply. The workbook says so rather "
        "than approximating it.<br>"
        "Two tabs are written beside the runs: <b>Reconstruction accuracy</b> "
        "and <b>Timing</b>."
        .format(runs=os.path.join(shown_dir, mandible.RUNS_SUBDIR),
                model=mandible.MODEL_RELATIVE, stl=mandible.GT_STL_NAME)
    )
    intro.setWordWrap(True)
    intro.setTextFormat(qt.Qt.RichText)
    layout.addWidget(intro)

    cases = mandible.discover_cases(experiment_dir)
    count = len(cases)
    unusable = [case for case in cases if not mandible.case_is_scorable(case)]
    model_present = os.path.isfile(mandible.model_path(root))

    found = qt.QLabel(_found_text(count, unusable, model_present))
    found.setWordWrap(True)
    found.setStyleSheet("color: #b00;" if (unusable or not count or not model_present)
                        else "color: gray;")
    layout.addWidget(found)

    recompute = qt.QCheckBox("Re-predict the ground truth (discard the cached one)")
    recompute.setChecked(False)
    recompute.setToolTip(
        "Off (recommended): reuse each run's cached "
        "Statistic/analysis/%s. It is the file the numbers were taken on, so "
        "the workbook and the mesh a reader opens beside the plan cannot drift "
        "apart, and the sweep costs seconds instead of ~25 s per run.\n\n"
        "On: predict again from the resected mandible and overwrite the cache. "
        "Needed after the model changes, and not otherwise."
        % mandible.GT_STL_NAME)
    layout.addWidget(recompute)

    button = qt.QPushButton("Analyse reconstruction accuracy + timing  ->  Excel")
    button.setToolTip(
        "For every run: how much of the resected volume the fibula restores, "
        "how far its surface sits from the mandible contour it should "
        "reproduce, how far it stands proud of it, and which of its segments "
        "carries the error. Written to one .xlsx beside the runs.\n\n"
        "Reads the runs and writes the workbook plus each run's cached ground "
        "truth; the current scene is left alone.\n\n"
        "The first run may install onnxruntime and scikit-image into Slicer's "
        "Python — they are what the shape-completion network needs, and only "
        "predicting a ground truth uses them.")
    button.setEnabled(bool(count))
    layout.addWidget(button)

    def _run():
        again = bool(recompute.checked)
        progress = _progress_dialog(count, again)
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
            report = mandible.run_analysis(root, progress=_tick, recompute=again)
        except Exception as exc:                             # noqa: BLE001
            logger.warning("Mandible experiment analysis failed", exc_info=True)
            found.setStyleSheet("color: #b00;")
            found.setText("Analysis failed: %s  (see the Python console)" % exc)
            return
        finally:
            if progress is not None:
                try:
                    progress.close()
                    progress.deleteLater()
                except Exception:                            # noqa: BLE001
                    logger.debug("Closing the progress dialog failed", exc_info=True)
            button.setEnabled(True)

        # The detail is worth keeping, just not on screen: printed rather than
        # logged so it lands in the Python console as a readable block.
        print(_summarise(report))
        found.setStyleSheet("color: gray;")
        found.setText(_outcome(report))

    button.clicked.connect(_run)


def _found_text(count, unusable, model_present):
    if not count:
        return ("No runs found — each needs a Statistic/scene/ folder, i.e. a "
                "run exited with \"save\".")
    parts = ["%d run(s) found." % count]
    if unusable:
        parts.append("[!] %d without both a resected mandible and transformed "
                     "fibula pieces: %s"
                     % (len(unusable), ", ".join(case["subject"] or case["run"]
                                                 for case in unusable[:6])))
    if not model_present:
        parts.append("[!] the shape-completion model is missing (%s), so a run "
                     "with no cached ground truth cannot be scored."
                     % mandible.MODEL_RELATIVE)
    return "  ".join(parts)


def _progress_dialog(count, recompute):
    try:
        progress = qt.QProgressDialog(slicer.util.mainWindow())
        progress.setWindowTitle("Experiments")
        progress.setLabelText(
            "Analysing %d run(s)%s..."
            % (count, " — predicting each ground truth, ~25 s per run"
               if recompute else ""))
        progress.setMinimum(0)
        progress.setMaximum(count)
        progress.setMinimumDuration(0)
        progress.setAutoClose(False)
        progress.setWindowModality(qt.Qt.ApplicationModal)
        try:
            progress.setCancelButton(None)
        except Exception:                                    # noqa: BLE001
            progress.setCancelButtonText("")
        progress.show()
        slicer.app.processEvents()
        return progress
    except Exception:                                        # noqa: BLE001
        logger.debug("Experiments progress dialog unavailable", exc_info=True)
        return None


def _repository_root():
    from ..app.common import SLICER_AI_AGENT_ROOT             # noqa: PLC0415
    return SLICER_AI_AGENT_ROOT


def _outcome(report):
    """The one line the panel shows: where it went, and whether to trust it."""
    parts = ["Saved %s" % report.get("workbook_relative", "")]
    rows = report.get("rows") or []
    if rows:
        parts.append("%d run(s): Rv %s, Ec %s mm, Ep %s mm (mean)"
                     % (len(rows), _mean(rows, "volume_ratio_pct", 1, "%%"),
                        _mean(rows, "contour_error_mm", 2),
                        _mean(rows, "max_projection_mm", 2)))
        parts.append("Ec is over %s%% of the outer contour on average — a "
                     "fibula cannot reach the alveolar crest"
                     % _mean(rows, "contour_coverage_pct", 0))

    # Four things a reader must not take at face value, so they are said here
    # and not only in the console.
    broken = report.get("failed_cases") or []
    if broken:
        parts.append("[!] %d of %d run(s) could NOT be analysed at all: %s"
                     % (len(broken), report.get("cases", 0), ", ".join(broken[:6])))
    if not report.get("model_present"):
        parts.append("[!] the shape-completion model was missing; only cached "
                     "ground truths were used")
    leaking = [row for row in rows if row.get("open_edges")]
    if leaking:
        parts.append("[!] %d run(s) have a fibula piece with a hole in it — its "
                     "volume is the enclosed part only" % len(leaking))
    saturated = [row for row in rows if row.get("saturated_samples")]
    if saturated:
        parts.append("[!] %d run(s) have contour samples the fibula covers "
                     "beyond the scan range; their Ep is a lower bound"
                     % len(saturated))
    parts.append("Full detail in the Python console.")
    return "  |  ".join(parts)


def _mean(rows, column, digits, suffix=""):
    values = [row[column] for row in rows
              if isinstance(row.get(column), (int, float))]
    if not values:
        return "--"
    return ("%%.%df%%s" % digits) % (sum(values) / len(values), suffix)


def _summarise(report):
    lines = ["Saved: %s" % report.get("workbook_relative", ""), ""]
    lines.extend(report.get("log") or [])

    rows = report.get("rows") or []
    if rows:
        lines.append("")
        lines.append("Per run, against that patient's predicted healthy segment")
        lines.append("  %-20s %4s %7s %7s %7s %7s %6s %7s %7s"
                     % ("case", "seg", "Rv%", "Ec mm", "Ep mm", "cover%", "dice",
                        "surf mm", "hd95"))
        for row in rows:
            lines.append("  %-20s %4s %7s %7s %7s %7s %6s %7s %7s"
                         % (row["case"][:20], row.get("segments"),
                            _number(row.get("volume_ratio_pct"), 1),
                            _number(row.get("contour_error_mm"), 2),
                            _number(row.get("max_projection_mm"), 2),
                            _number(row.get("contour_coverage_pct"), 1),
                            _number(row.get("dice"), 3),
                            _number(row.get("surface_mean_mm"), 2),
                            _number(row.get("hd95_mm"), 1)))

    segments = report.get("segments") or []
    if segments:
        lines.append("")
        lines.append("Per fibula segment")
        lines.append("  %-20s %-34s %8s %8s %9s %9s"
                     % ("case", "segment", "len mm", "vol cm3", "in GT %",
                        "proud mm"))
        for row in segments:
            lines.append("  %-20s %-34s %8s %8s %9s %9s"
                         % (row["case"][:20], (row.get("segment") or "")[:34],
                            _number(row.get("length_mm"), 1),
                            _number(row.get("volume_cm3"), 2),
                            _number(row.get("inside_gt_pct"), 1),
                            _number(row.get("protrusion_max_mm"), 2)))

    summary = report.get("summary") or []
    if summary:
        lines.append("")
        lines.append("Across every scored run")
        for row in summary:
            lines.append("  %-22s n=%-3s %9s +- %-9s [%s .. %s]  %s"
                         % (row["metric"], row.get("n"), row.get("mean"),
                            row.get("sd"), row.get("min"), row.get("max"),
                            row.get("note") or ""))
    return "\n".join(lines)


def _number(value, digits):
    return ("%%.%df" % digits) % value if isinstance(value, (int, float)) else "--"
