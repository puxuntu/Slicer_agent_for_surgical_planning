"""The "User study" subsection of the Experiments panel.

Three selectors -- procedure, arm, participant -- name one folder under
``Experiments/3_User_Study/Results/``; **Compute** scores its runs and writes
``Quanti_Quali_Eva/<folder>.xlsx``, **Compute all** does that for every folder
there. The numerics are ``user_study.py`` (Qt-free), which hands each folder to
the procedure's existing analysis; this half only wires the controls to it.

Nothing runs on its own: the section scans folders when it is built and on
Rescan, and computes only when a button is pressed.

The selectors are filled from what is ON DISK, so a new participant's folders
appear after Rescan with no code change, and a combination that has no folder
says so instead of offering a button that cannot work.
"""

from __future__ import annotations

import logging
import os

import ctk
import qt
import slicer

from . import user_study

logger = logging.getLogger(__name__)


def build_section(widget, layout):
    """Add the subsection to ``layout``; returns its group box."""
    root = _repository_root()
    box = ctk.ctkCollapsibleGroupBox()
    box.title = "User study  ->  Quanti_Quali_Eva"
    box.collapsed = True
    layout.addWidget(box)
    outer = qt.QVBoxLayout(box)

    state = {"study_dir": "", "groups": [], "busy": False}

    intro = qt.QLabel()
    intro.setWordWrap(True)
    intro.setTextFormat(qt.Qt.RichText)
    outer.addWidget(intro)

    form = qt.QFormLayout()
    procedure_combo = qt.QComboBox()
    arm_combo = qt.QComboBox()
    participant_combo = qt.QComboBox()
    for combo in (procedure_combo, arm_combo, participant_combo):
        combo.setMinimumWidth(0)
    form.addRow("Extension:", procedure_combo)
    form.addRow("Arm:", arm_combo)
    form.addRow("Participant:", participant_combo)
    outer.addLayout(form)

    status = qt.QLabel()
    status.setWordWrap(True)
    outer.addWidget(status)

    buttons = qt.QHBoxLayout()
    compute_one = qt.QPushButton("Compute selected  ->  Excel")
    compute_one.setToolTip(
        "Score every run in the selected Results folder with that procedure's "
        "analysis (the same one its Experiments panel above uses) and write "
        "Quanti_Quali_Eva/<folder>.xlsx, replacing an earlier one.")
    compute_all = qt.QPushButton("Compute all")
    compute_all.setToolTip(
        "Do the same for EVERY folder under Results/ -- one workbook per folder. "
        "Fail-soft: a folder that fails is reported and the others still run.")
    rescan = qt.QPushButton("Rescan")
    rescan.setToolTip("Re-read Results/ -- after adding a participant's folders.")
    buttons.addWidget(compute_one, 2)
    buttons.addWidget(compute_all, 2)
    buttons.addWidget(rescan, 1)
    outer.addLayout(buttons)

    outcome = qt.QLabel()
    outcome.setWordWrap(True)
    outcome.setStyleSheet("color: gray;")
    outer.addWidget(outcome)

    # -- selection -------------------------------------------------------------
    def selected_group():
        procedure = _combo_value(procedure_combo)
        arm = _combo_value(arm_combo)
        participant = _combo_value(participant_combo)
        for group in state["groups"]:
            if (group["procedure"], group["arm"], group["participant"]) == (procedure, arm, participant):
                return group
        return None

    def runnable(group):
        return bool(group and group.get("analysis") and group.get("saved_runs"))

    def refresh_status(*_unused):
        group = selected_group()
        compute_one.setEnabled(runnable(group) and not state["busy"])
        if group is None:
            status.setStyleSheet("color: #b00;")
            status.setText("No folder %s%s%s under Results/ for this combination."
                           % (u"【%s】" % _combo_value(arm_combo),
                              _combo_value(procedure_combo),
                              u"【%s】" % _combo_value(participant_combo))
                           if procedure_combo.count else
                           "No Results folders found.")
            return
        parts = ["<b>%s</b>" % _html(group["folder"]),
                 "%d run(s) with a saved scene" % len(group["saved_runs"])]
        warn = False
        if not group.get("analysis"):
            parts.append("[!] no analysis registered for %s"
                         % _html(group["extension"] or "these runs"))
            warn = True
        if not group.get("dataset_dir"):
            parts.append("[!] no Dataset/%s/ folder" % _html(group["procedure"]))
            warn = True
        for problem in group.get("problems") or []:
            parts.append("[!] %s" % _html(problem))
            warn = True
        output = group["output"]
        written = ("written %s" % _mtime(output)) if os.path.isfile(output) else "not written yet"
        parts.append("&rarr; %s/%s (%s)" % (user_study.OUTPUT_SUBDIR,
                                            _html(os.path.basename(output)), written))
        status.setStyleSheet("color: #b00;" if warn else "color: gray;")
        status.setText("<br>".join(parts))

    def fill(combo, values, labels=None):
        previous = _combo_value(combo)
        combo.blockSignals(True)
        try:
            combo.clear()
            for value in values:
                combo.addItem((labels or {}).get(value, value), value)
            index = combo.findData(previous) if previous else -1
            if index >= 0:
                combo.setCurrentIndex(index)
        finally:
            combo.blockSignals(False)

    def scan():
        state["study_dir"] = user_study.resolve_study_dir(root)
        state["groups"] = user_study.discover_groups(state["study_dir"])
        groups = state["groups"]
        procedures, labels = [], {}
        for group in groups:
            if group["procedure"] not in procedures:
                procedures.append(group["procedure"])
                labels[group["procedure"]] = (
                    "%s  (%s)" % (group["procedure"], group["extension"])
                    if group["extension"] else group["procedure"])
        arms = sorted({g["arm"] for g in groups},
                      key=lambda a: (0 if a.lower() == "agent" else 1, a))
        participants = sorted({g["participant"] for g in groups},
                              key=user_study.participant_key)
        fill(procedure_combo, procedures, labels)
        fill(arm_combo, arms)
        fill(participant_combo, participants)

        shown = _relative(state["study_dir"], root)
        intro.setText(
            "Scores every run in one <code>{s}/{r}/&lt;folder&gt;</code> with that "
            "procedure's own analysis &mdash; the same measurement as its panel "
            "above &mdash; using the ground truth in <code>{s}/{d}/&lt;procedure&gt;/</code> "
            "where it needs one, and writes <code>{s}/{o}/&lt;folder&gt;.xlsx</code>: "
            "the procedure's sheets, plus <b>Run set</b> (what was scored) and "
            "<b>Interaction</b> (time, activity states and clicks as the recorder "
            "measured them &mdash; identical in both arms). Runs are listed in the "
            "order they were performed.<br>"
            "Reads the runs and writes only the workbook, with one exception: the "
            "mandible analysis caches each run's predicted ground truth in that "
            "run's <code>Statistic/analysis/</code>."
            .format(s=_html(shown), r=user_study.RESULTS_SUBDIR,
                    d=user_study.DATASET_SUBDIR, o=user_study.OUTPUT_SUBDIR))
        ready = [g for g in groups if runnable(g)]
        compute_all.setText("Compute all %d folder(s)  ->  %d xlsx" % (len(ready), len(ready))
                            if ready else "Compute all")
        compute_all.setEnabled(bool(ready) and not state["busy"])
        refresh_status()

    # -- running ---------------------------------------------------------------
    def run(groups):
        if state["busy"] or not groups:
            return
        if any((g.get("analysis") or {}).get("scene") for g in groups):
            # The orbital analysis meshes in the MRML scene (temporary nodes,
            # dropped again). A guided run owns that scene, so refuse rather
            # than interleave with it.
            runtime = getattr(widget, "_workflowRuntime", None)
            if runtime is not None and getattr(runtime, "session", None) is not None:
                outcome.setStyleSheet("color: #b00;")
                outcome.setText("A guided workflow is open -- press Exit on its panel "
                                "first (the orbital analysis builds temporary nodes "
                                "in the scene).")
                return
        state["busy"] = True
        compute_one.setEnabled(False)
        compute_all.setEnabled(False)
        rescan.setEnabled(False)
        total = sum(len(g["saved_runs"]) for g in groups)
        progress = _progress_dialog(total)
        done = {"cases": 0}
        results = []
        try:
            for position, group in enumerate(groups):
                def _tick(index, count, label, _group=group, _position=position):
                    if progress is None:
                        return
                    progress.setLabelText("Folder %d of %d: %s\nRun %d of %d: %s"
                                          % (_position + 1, len(groups), _group["folder"],
                                             index + 1, count, label))
                    progress.setValue(min(done["cases"] + index, total))
                    slicer.app.processEvents()

                _tick(0, len(group["saved_runs"]), "...")
                try:
                    report = user_study.run_group(root, group, progress=_tick)
                    results.append((group, report, None))
                except Exception as exc:                     # noqa: BLE001
                    logger.warning("User-study analysis failed for %s", group["folder"],
                                   exc_info=True)
                    results.append((group, None, exc))
                done["cases"] += len(group["saved_runs"])
        finally:
            if progress is not None:
                try:
                    progress.close()
                    progress.deleteLater()
                except Exception:                            # noqa: BLE001
                    logger.debug("Closing the progress dialog failed", exc_info=True)
            state["busy"] = False
            rescan.setEnabled(True)
            scan()

        print(_summarise(results))
        written = [r for r in results if r[1] is not None]
        broken = [r for r in results if r[2] is not None]
        partial = [(g, user_study.failures_in(rep)) for g, rep, _ in written
                   if user_study.failures_in(rep)]
        parts = ["Wrote %d of %d workbook(s) to %s"
                 % (len(written), len(results),
                    _relative(os.path.join(state["study_dir"], user_study.OUTPUT_SUBDIR), root))]
        if broken:
            parts.append("[!] FAILED: %s" % "; ".join("%s (%s)" % (g["folder"], exc)
                                                      for g, _, exc in broken))
        if partial:
            parts.append("[!] runs not scored: %s"
                         % "; ".join("%s: %s" % (g["folder"], ", ".join(f[:6]))
                                     for g, f in partial))
        parts.append("Full detail in the Python console.")
        outcome.setStyleSheet("color: #b00;" if (broken or partial) else "color: gray;")
        outcome.setText("  |  ".join(parts))

    procedure_combo.currentIndexChanged.connect(refresh_status)
    arm_combo.currentIndexChanged.connect(refresh_status)
    participant_combo.currentIndexChanged.connect(refresh_status)
    compute_one.clicked.connect(lambda: run([g for g in [selected_group()] if runnable(g)]))
    compute_all.clicked.connect(lambda: run([g for g in state["groups"] if runnable(g)]))
    rescan.clicked.connect(scan)

    scan()
    return box


def _combo_value(combo):
    if combo.currentIndex < 0:
        return ""
    value = combo.itemData(combo.currentIndex)
    return value if isinstance(value, str) and value else combo.currentText


def _progress_dialog(total):
    try:
        progress = qt.QProgressDialog(slicer.util.mainWindow())
        progress.setWindowTitle("User study evaluation")
        progress.setLabelText("Scoring %d run(s)..." % total)
        progress.setMinimum(0)
        progress.setMaximum(max(total, 1))
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
        logger.debug("User-study progress dialog unavailable", exc_info=True)
        return None


def _summarise(results):
    lines = []
    for group, report, error in results:
        lines.append("=" * 78)
        lines.append(group["folder"])
        if error is not None:
            lines.append("  FAILED: %s" % error)
            continue
        lines.append("  Saved: %s  (%d run(s) scored)"
                     % (report.get("workbook_relative", ""), report.get("scored_runs", 0)))
        for line in report.get("log") or []:
            lines.append("  %s" % line)
    return "\n".join(lines)


def _mtime(path):
    try:
        import time                                          # noqa: PLC0415
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(path)))
    except OSError:
        return ""


def _relative(path, root):
    try:
        return os.path.relpath(path, root)
    except ValueError:
        return path


def _html(text):
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _repository_root():
    from ..app.common import SLICER_AI_AGENT_ROOT             # noqa: PLC0415
    return SLICER_AI_AGENT_ROOT
