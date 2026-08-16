"""Experiments panel: prepare a DICOM case dataset into compressed NRRD.

One builder, registered once per entry in ``dicom_dataset.DATASETS`` -- the
panel is identical for every such dataset, so a copy per extension would only
create two places for the same bug to be fixed in one of.

The sweep runs on a WORKER THREAD, several cases at a time, because the fast
path (SimpleITK/GDCM) never touches MRML. That is the whole reason it is fast:
the earlier Slicer-based path had to run on the Qt main thread one case at a
time, since MRML is main-thread only, so Slicer was frozen for the duration and
three of four cores sat idle.

The only things that touch Qt here are the progress updates, and those are
marshalled back through a queue drained by a QTimer on the main thread -- the
same pattern the agent's streaming loop uses.

If SimpleITK is missing, ``process_all`` falls back to the Slicer path by
itself; that path IS main-thread-only, which is why the fallback is single-file
and slow rather than merely slower.
"""

from __future__ import annotations

import logging
import os
import queue
import threading

import qt

from ..app.widget_experiments import register_experiment_panel
from . import dicom_dataset

logger = logging.getLogger(__name__)


def _build(widget, layout, extension):
    dataset = dicom_dataset.DATASETS[extension]
    workspace = _workspace_root()
    original = dataset.original(workspace)
    processed_abs = dataset.processed(workspace)
    processed_rel = os.path.join(dataset.data_dir, dicom_dataset.PROCESSED_SUBDIR)

    intro = qt.QLabel(
        "Reads every case under <code>{orig}</code> (post-operative "
        "<code>*{skip}</code> folders ignored), keeps the thin-slice "
        "reconstruction of each -- both copies when the scanner produced a "
        "near-identical pair -- and writes them to <code>{proc}</code> as "
        "compressed .nrrd named after the case folder."
        .format(orig=os.path.join(dataset.data_dir, dicom_dataset.ORIGINAL_SUBDIR),
                skip=dataset.skip_suffix, proc=processed_rel))
    intro.setWordWrap(True)
    intro.setTextFormat(qt.Qt.RichText)
    layout.addWidget(intro)

    # Recomputed on every click, not captured here: files can appear between
    # the panel being built and the button being pressed (a previous run, a
    # manual delete), and the button must act on what is on disk NOW.
    cases, already = dicom_dataset.pending_cases(original, processed_abs)
    status = qt.QLabel(
        _found_text(cases, already) if (cases or already)
        else "No cases found at %s" % original)
    status.setWordWrap(True)
    status.setStyleSheet("color: gray;" if cases else "color: #b00;")
    layout.addWidget(status)

    progress = qt.QProgressBar()
    progress.setMinimum(0)
    progress.setMaximum(max(1, len(cases)))
    progress.setValue(0)
    progress.setVisible(False)
    layout.addWidget(progress)

    button = qt.QPushButton(_button_text(cases, already))
    button.setToolTip(
        "Scan each case's DICOM headers, keep the series with the most slices "
        "at the finest slice spacing, and export it as a compressed .nrrd. "
        "Cases that already have an output file are skipped, so re-clicking "
        "continues where the last run stopped -- delete a case's .nrrd to have "
        "it done again.")
    button.setEnabled(bool(cases))
    layout.addWidget(button)

    state = {"running": False, "stop": False, "messages": queue.Queue(),
             "outcome": {}, "timer": None, "done": 0, "written": 0, "empty": 0}

    def _log(message):
        """Called from the WORKER threads -- must not touch Qt."""
        state["messages"].put(message)

    def _drain():
        """Main thread: move whatever the workers said onto the screen."""
        printed = 0
        while printed < 200:                    # bounded, so the UI stays live
            try:
                message = state["messages"].get_nowait()
            except queue.Empty:
                break
            printed += 1
            print(message)
            if message.startswith("[") and " -- " in message:
                state["done"] += 1
                progress.setValue(state["done"])
                if "NO OUTPUT" in message:
                    state["empty"] += 1
                else:
                    state["written"] += 1
                status.setText(
                    "[%d/%d]  %d case(s) written, %d with NO output%s"
                    % (state["done"], progress.maximum,
                       state["written"], state["empty"],
                       "  -- see the console for why" if state["empty"] else ""))
        if not state["running"]:
            _finish()

    def _finish():
        timer = state.pop("timer", None)
        if timer is not None:
            timer.stop()
        progress.setVisible(False)
        remaining, finished = dicom_dataset.pending_cases(original, processed_abs)
        button.setText(_button_text(remaining, finished))
        button.setEnabled(bool(remaining))
        report = state.get("outcome") or {}
        aborted = report.get("aborted")
        failed = report.get("failed") or []
        status.setStyleSheet("color: #b00;" if (failed or aborted) else "color: gray;")
        if aborted:
            status.setText("Stopped before starting: %s  (see the console)" % aborted)
            return
        text = "Wrote %d volume(s); %d case(s) left." % (
            report.get("written", 0), len(remaining))
        reasons = report.get("reasons") or {}
        if failed:
            # The REASON on screen, not only the case number: "needs a look at
            # 57, 61, 65, 68" cannot be acted on without opening the console,
            # and the four usually need four different things.
            text += "  Needs a look:  " + "   ".join(
                "%s (%s)" % (case, _short(reasons.get(case, "")))
                for case in failed[:4])
            if len(failed) > 4:
                text += "  ... and %d more -- see the console." % (len(failed) - 4)
        status.setText(text)

    def _work():
        try:
            state["outcome"] = dicom_dataset.process_all(
                workspace, dataset, log=_log,
                should_stop=lambda: state["stop"],
                workers=dicom_dataset.CASE_WORKERS)
        except Exception as exc:
            logger.warning("%s dataset processing failed", extension, exc_info=True)
            state["messages"].put("FAILED: %s" % exc)
            state["outcome"] = {"written": 0, "failed": [], "aborted": str(exc)}
        finally:
            state["running"] = False

    def _run():
        if state["running"]:
            # A second click STOPS: running cases finish (so none is left half
            # written) and nothing new starts.
            state["stop"] = True
            button.setText("Stopping -- letting running cases finish...")
            return
        del cases[:]
        pending, finished = dicom_dataset.pending_cases(original, processed_abs)
        cases.extend(pending)
        if not cases:
            status.setStyleSheet("color: gray;")
            status.setText("Nothing to do -- all %d case(s) already written."
                           % len(finished))
            return
        state.update(running=True, stop=False, outcome={}, done=0,
                     written=0, empty=0)
        button.setText("Stop")
        progress.setMaximum(len(cases))
        progress.setValue(0)
        progress.setVisible(True)
        status.setStyleSheet("color: gray;")
        if finished:
            print("Resuming: %d already written, %d to go."
                  % (len(finished), len(cases)))

        threading.Thread(target=_work, daemon=True).start()
        # Poll for what the workers have to say. 200 ms is plenty for a sweep
        # whose units of work are whole cases.
        timer = qt.QTimer()
        timer.setInterval(200)
        timer.timeout.connect(_drain)
        timer.start()
        state["timer"] = timer

    button.clicked.connect(_run)


# One panel per dataset. Registering in a loop rather than writing a decorated
# function each time is what keeps them from drifting apart.
for _name in dicom_dataset.DATASETS:
    register_experiment_panel(_name)(_build)


def _short(reason, limit=64):
    """One clause of a failure reason, for a label that must stay one line."""
    text = " ".join(str(reason or "").split())
    if not text:
        return "no output"
    text = text.split(";")[0]
    return text if len(text) <= limit else text[:limit - 3] + "..."


def _button_text(pending, done):
    """Say whether a click starts or RESUMES, and how much is left."""
    if not pending:
        return "Original dataset processing  (all done)"
    if done:
        return "Resume dataset processing  (%d left)" % len(pending)
    return "Original dataset processing"


def _found_text(pending, done):
    if not pending:
        return "All %d case(s) already processed." % len(done)
    if done:
        return ("%d case(s) already processed, %d to go -- re-clicking resumes."
                % (len(done), len(pending)))
    return "%d case(s) found." % len(pending)


def _workspace_root():
    """The SlicerAgent workspace: the repo's PARENT, where Test_data lives."""
    from ..app.common import SLICER_AI_AGENT_ROOT              # noqa: PLC0415
    return os.path.dirname(SLICER_AI_AGENT_ROOT)
