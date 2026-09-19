# -*- coding: utf-8 -*-
"""What the person did, and where their time went -- measured the same way in
both arms of the user study.

The guided runtime already answers "how long did step 7 take" (``RunLog``'s
three clocks: wall, exec, wait). It cannot answer the question a learning curve
is made of, which is what the *person* was doing inside that wall clock: a
``user_interaction`` step's ``wait`` is one number covering reading the
instruction, deciding, dragging a plane, and the pause before pressing Done.
And the comparison arm -- the extension's own GUI, driven by hand -- has no
steps at all, so it produces no clock of any kind.

So this module measures the session from **Slicer's own input events**, which
both arms have in common, and derives a partition of the wall clock into states
a reader can act on:

    away      Slicer is not the active window (the participant is in a browser)
    compute   the Qt main thread was blocked, i.e. an algorithm was running
    view_3d   inside a burst of input landing in a 3D view
    view_2d   inside a burst of input landing in a slice view
    panel     inside a burst of input landing in the module panel
    other     inside a burst of input landing elsewhere in Slicer
    idle      none of the above: reading, deciding, waiting

They are DISJOINT and sum to the session's wall clock, which is what makes the
split checkable rather than a set of overlapping estimates. Beside them,
counters: clicks by button and by target, double-clicks, drags and pointer
travel, wheel notches, key presses.

Two design facts carry most of the correctness:

- **Span reconstruction is a pure function of the recorded event list.** The
  filter does nothing but append ``(kind, time, target)`` tuples; every rule
  below -- burst merging, precedence, padding -- runs in ``snapshot()`` over
  that list. So the whole derivation is testable outside Slicer, which
  ``scripts/check_planning_recorder.py`` does, and a rule can be changed after
  the fact against recorded sessions instead of only against new ones.
- **The module imports cleanly with no Slicer and no Qt.** ``qt`` and ``slicer``
  are imported inside the functions that need them. That is what lets
  ``RunLog`` render the interaction report (it is Qt-free by contract), and what
  lets the check script run the arithmetic on a developer machine.

**This file is VENDORED.** The canonical copy is
``SlicerAIAgentLib/PlanningRecorder.py``; byte-identical copies sit beside each
of the four study extensions (OrbitalFractureReconstruction, PedicleScrewPlanner,
BoneReconstructionPlanner, PelvicFracturePlanning), because the comparison arm
must keep recording on a machine where the agent is not installed -- an
instrument that stops working when the thing it is measuring against is absent
is not an instrument. ``scripts/check_planning_recorder.py`` asserts the copies
are identical, since a copy that drifted would produce two arms whose numbers
are not comparable and nothing would say so.
"""

from __future__ import annotations

import bisect
import json
import logging
import math
import os
import re
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

SCHEMA = "slicer_planning_recorder.interaction/1"

# ---------------------------------------------------------------------------
# The rules, as constants, because every one of them is a judgement call that a
# reader of the numbers is entitled to see and to change.
# ---------------------------------------------------------------------------

#: How often the main-thread heartbeat fires. Small enough that a half-second
#: block is several missed ticks, large enough to be free (the guided runtime
#: already polls its stream queue at 50 ms).
HEARTBEAT_MS = 100

#: A gap between heartbeats longer than this means the Qt main thread was busy
#: -- an algorithm was running -- and the gap is charged to ``compute``.
#:
#: Deliberately generous. A shorter threshold would reclassify *stuttery
#: interaction* as computation: dragging a mandibular cut plane re-clips the
#: fibula on a 50 ms coalescing timer, so the main thread is repeatedly busy for
#: a few hundred milliseconds while the person is plainly still dragging. Half a
#: second is past anything that reads as interface latency and short enough to
#: catch every real algorithm in the nine procedures.
BLOCK_THRESHOLD_S = 0.5

#: Input events closer together than this belong to one continuous piece of
#: work. Two seconds is about the pause a person leaves between two clicks that
#: are part of the same intention, and well under the pause that means they have
#: stopped to look at the result.
IDLE_GAP_S = 2.0

#: A burst is widened by this much at each end. Without it an isolated click --
#: one event, zero duration -- would contribute no active time at all, and a
#: step answered with a single button press would read as pure idle. Half a
#: second per isolated click is about what reaching, aiming and clicking costs.
BURST_PAD_S = 0.25

#: Pointer motion is sampled at most this often while a button is held. Motion
#: has to enter the event list (a slow five-second drag with no other input
#: would otherwise split into two bursts around a five-second "gap"), but at the
#: rate Qt delivers it, it would be the only thing in the list.
DRAG_SAMPLE_MS = 50

#: A single physical mouse event can reach an application-wide event filter
#: MORE THAN ONCE -- Slicer's VTK views forward Qt mouse events on to another
#: object, and every forward is a fresh delivery. Two deliveries of one event
#: share a Qt `timestamp()`, which is the exact test; without one, an identical
#: (type, button, screen position) inside this window is the same press, since
#: no hand can click the same pixel twice that fast.
DUPLICATE_WINDOW_S = 0.05

#: Motion with no button held is NOT recorded. Hovering the pointer over the 3D
#: view while thinking about the plan is thinking, not operating, and recording
#: it would make ``idle`` unreachable for anyone who does not park their hand.
#:
#: (Stated as a constant so the choice is visible; the code has no other branch.)
RECORD_HOVER = False

#: Where an event landed, in the vocabulary the report uses.
TARGET_VIEW_3D = "view_3d"
TARGET_VIEW_2D = "view_2d"
TARGET_PANEL = "panel"
TARGET_OTHER = "other"
TARGET_KINDS = (TARGET_VIEW_3D, TARGET_VIEW_2D, TARGET_PANEL, TARGET_OTHER)

#: The non-activity states, in the order they win.
STATE_AWAY = "away"
STATE_COMPUTE = "compute"
STATE_IDLE = "idle"

#: Every bucket, in report order. ``away`` first and ``idle`` last because that
#: is how a reader scans them: what was not the session, then what was.
ALL_STATES = (STATE_AWAY, STATE_COMPUTE) + TARGET_KINDS + (STATE_IDLE,)

#: Qt class-name fragments that identify a view. Matched as substrings of
#: ``className()`` walking up the parent chain, never against an exact list:
#: Slicer wraps its views in several layers (``qMRMLSliceWidget`` holds a
#: ``qMRMLSliceView`` holds the VTK render window widget) and the receiver of a
#: mouse event is whichever of them has focus.
_VIEW_3D_MARKERS = ("ThreeDView", "ThreeDWidget")
_VIEW_2D_MARKERS = ("SliceView", "SliceWidget")
#: Only a FALLBACK, for a recorder given no panel of its own. Every scripted
#: module's frame carries these, so matching on them alone counts another
#: module's controls as this extension's panel -- which is why the real test is
#: ancestry under the owning widget.
_PANEL_MARKERS = ("qSlicerModulePanel", "ModulePanel", "qSlicerWidget")

#: The condition token for the comparison arm. Must match
#: ``RunLog.CONDITION_MANUAL`` -- the two are separate because this file has to
#: work with no ``SlicerAIAgentLib`` on the path, and a token mismatch would put
#: the two arms in folders that no analysis pairs up.
CONDITION_MANUAL = "manual"
CONDITION_MANUAL_LABEL = (
    "Comparison arm: the extension's own GUI and its published tutorial, unaided"
)

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


# ---------------------------------------------------------------------------
# Interval arithmetic. Pure, and the whole partition rests on it.
# ---------------------------------------------------------------------------

def _merge(intervals: Sequence[Tuple[float, float]]) -> List[List[float]]:
    """Sort and coalesce, dropping empties. Returns a list of ``[a, b]``."""
    items = sorted([float(a), float(b)] for a, b in intervals if float(b) > float(a))
    out: List[List[float]] = []
    for span in items:
        if out and span[0] <= out[-1][1]:
            out[-1][1] = max(out[-1][1], span[1])
        else:
            out.append([span[0], span[1]])
    return out


def _intersect(base: Sequence[Sequence[float]],
               other: Sequence[Sequence[float]]) -> List[List[float]]:
    """Every part of ``base`` that is also in ``other``."""
    out: List[List[float]] = []
    i = j = 0
    base = _merge([(a, b) for a, b in base])
    other = _merge([(a, b) for a, b in other])
    while i < len(base) and j < len(other):
        lo = max(base[i][0], other[j][0])
        hi = min(base[i][1], other[j][1])
        if hi > lo:
            out.append([lo, hi])
        if base[i][1] < other[j][1]:
            i += 1
        else:
            j += 1
    return out


def _subtract(base: Sequence[Sequence[float]],
              cuts: Sequence[Sequence[float]]) -> List[List[float]]:
    """Every part of ``base`` that is not in ``cuts``."""
    cuts = _merge([(a, b) for a, b in cuts])
    out: List[List[float]] = []
    for a, b in _merge([(x, y) for x, y in base]):
        cursor = a
        for ca, cb in cuts:
            if cb <= cursor or ca >= b:
                continue
            if ca > cursor:
                out.append([cursor, min(ca, b)])
            cursor = max(cursor, cb)
            if cursor >= b:
                break
        if cursor < b:
            out.append([cursor, b])
    return [span for span in out if span[1] > span[0]]


def _total(intervals: Sequence[Sequence[float]]) -> float:
    return round(sum(float(b) - float(a) for a, b in intervals), 3)


# ---------------------------------------------------------------------------
# Span reconstruction: the event list -> the partition
# ---------------------------------------------------------------------------

def _bursts_from_events(events: Sequence[Sequence[Any]]) -> List[List[Any]]:
    """Group input events into ``[start, end, target_kind]`` bursts.

    A burst ends when the gap to the next event exceeds ``IDLE_GAP_S`` **or the
    target changes**. Ending on a target change rather than labelling a mixed
    burst by majority is what keeps "clicked Apply, then dragged in 3D" from
    being reported entirely as panel work or entirely as 3D work; the two are
    separate answers to separate questions and the burst boundary is free.

    Padding is applied at both ends and then clipped so bursts never overlap --
    an overlap would double-count time and break the partition.
    """
    inputs = [e for e in events if e[0] in _INPUT_KINDS]
    inputs.sort(key=lambda e: e[1])
    groups: List[List[Any]] = []
    for kind, stamp, target in ((e[0], float(e[1]), e[2]) for e in inputs):
        if (groups and groups[-1][2] == target
                and stamp - groups[-1][1] <= IDLE_GAP_S):
            groups[-1][1] = stamp
            continue
        groups.append([stamp, stamp, target])

    padded: List[List[Any]] = []
    for start, end, target in groups:
        padded.append([start - BURST_PAD_S, end + BURST_PAD_S, target])
    # Clip forward: a burst may not start before the previous one ended, and may
    # not end after the next one starts. Walking once in each direction is
    # enough because the groups are already sorted and non-overlapping before
    # padding.
    for index in range(1, len(padded)):
        if padded[index][0] < padded[index - 1][1]:
            middle = (padded[index][0] + padded[index - 1][1]) / 2.0
            padded[index - 1][1] = middle
            padded[index][0] = middle
    return [span for span in padded if span[1] > span[0]]


def _alive_spans(events: Sequence[Sequence[Any]]) -> List[List[Any]]:
    """The stretches the Qt main thread was responsive, as ``[start, end, busy]``.

    TWO input forms, which is deliberate and is checked rather than assumed.

    The recorder emits ``alive`` entries directly: one per stretch of continuous
    responsiveness at one busy state, extended in place on every heartbeat. That
    is what keeps the event list proportional to what HAPPENED rather than to
    how long the session ran -- a quiet hour is one entry, not 36,000.

    A ``tick`` entry is one heartbeat as a point, which is how the rules below
    are most readably specified and how ``scripts/check_planning_recorder.py``
    writes its cases. Consecutive ticks no further apart than the threshold are
    folded into the same span here, so the two forms describe the same session
    and the check script proves they yield the same partition.
    """
    spans: List[List[Any]] = [list(e[2]) for e in events
                              if e[0] == "alive" and isinstance(e[2], (list, tuple))]
    ticks = sorted((float(e[1]), bool(e[2])) for e in events if e[0] == "tick")
    current: Optional[List[Any]] = None
    for stamp, busy in ticks:
        if (current is not None and current[2] == busy
                and stamp - current[1] <= BLOCK_THRESHOLD_S):
            current[1] = stamp
            continue
        if current is not None and stamp - current[1] <= BLOCK_THRESHOLD_S:
            # A busy CHANGE, not a gap: the new span begins where the old one
            # ended, so the boundary is not mistaken for a block.
            current = [current[1], stamp, busy]
        else:
            current = [stamp, stamp, busy]
        spans.append(current)
    spans.sort(key=lambda span: span[0])
    return spans


def _blocked_from_ticks(events: Sequence[Sequence[Any]]) -> List[List[float]]:
    """The ``compute`` intervals: the main thread was busy running something.

    Two producers, and the second is not redundant. (a) A gap between two alive
    spans longer than ``BLOCK_THRESHOLD_S`` means the main thread did not get
    back to the event loop, which is what a synchronous algorithm looks like
    from outside. (b) A span recorded *while an override cursor was set* means
    an algorithm is running but is pumping the event loop -- several of the
    study extensions drive a progress dialog, which keeps timers alive, so
    without this their compute time would land in ``idle`` and read as the
    participant sitting and thinking.

    Only the override cursor is used for (b), never "a modal window is up": a
    progress dialog and a confirmation dialog are both modal, and the second one
    is a person deciding, which is the opposite of compute.

    A gap is CUT at every input delivery -- see ``_unattended_stretches``. The
    busy-cursor intervals are NOT cut that way: there the extension has said
    outright that it is working, and a surgeon clicking at a busy application is
    not operating it.
    """
    spans = _alive_spans(events)
    out: List[List[float]] = [[span[0], span[1]] for span in spans if span[2]]
    stamps = sorted(float(e[1]) for e in events if e[0] in _INPUT_KINDS)
    for previous, span in zip(spans, spans[1:]):
        out.extend(_unattended_stretches(previous[1], span[0], stamps))
    return _merge([(a, b) for a, b in out])


def _unattended_stretches(low: float, high: float,
                          stamps: Sequence[float]) -> List[List[float]]:
    """The parts of a heartbeat gap in which NOTHING was delivered.

    Delivering an event IS the main thread turning over, so the thread was alive
    at every timestamp inside the gap and can only have been blocked between
    them. Cutting the gap at each delivery and keeping the stretches that are
    still longer than ``BLOCK_THRESHOLD_S`` therefore answers both cases with
    one rule: a click that starts a four-second computation leaves one
    four-second stretch, and a drag whose render blocks in bursts leaves only
    stretches under the threshold and contributes no compute at all.

    Judging the gap as a WHOLE is what this replaces, and it failed in the
    direction that mattered. A gap runs from the last tick before the block to
    the first tick after it, so its trailing edge is up to one heartbeat later
    than the block; on Windows the timer message is delivered only once the
    queue is otherwise empty, so everything queued during the block flushes into
    that sliver. One click before and one release after was enough to hand a
    whole four-second computation back to the person -- which is why one real
    unaided run reported 0.0 s of algorithm time for a procedure the guided arm
    measured at 24.8 s.

    Both edges are open: the click that STARTS a computation sits on the leading
    edge and the queued release on the trailing one, and neither is evidence
    that the thread was alive in between.
    """
    low, high = float(low), float(high)
    if high - low <= BLOCK_THRESHOLD_S:
        return []
    cuts = [low]
    index = bisect.bisect_right(stamps, low)
    while index < len(stamps) and stamps[index] < high:
        cuts.append(float(stamps[index]))
        index += 1
    cuts.append(high)
    return [[a, b] for a, b in zip(cuts, cuts[1:]) if b - a > BLOCK_THRESHOLD_S]


def _away_from_events(events: Sequence[Sequence[Any]],
                      start: float, stop: float) -> List[List[float]]:
    """Focus transitions -> the intervals where Slicer was not the active window.

    An unterminated "away" runs to the end of the session: the participant may
    still have been elsewhere when recording stopped, and assuming they came
    back would silently credit that time to the session.
    """
    marks = sorted(((float(e[1]), bool(e[2])) for e in events if e[0] == "focus"),
                   key=lambda item: item[0])
    out: List[List[float]] = []
    opened: Optional[float] = None
    for stamp, active in marks:
        if not active and opened is None:
            opened = stamp
        elif active and opened is not None:
            out.append([opened, stamp])
            opened = None
    if opened is not None:
        out.append([opened, stop])
    return _intersect(_merge([(a, b) for a, b in out]), [[start, stop]])


def partition(events: Sequence[Sequence[Any]], start: float,
              stop: float) -> Dict[str, List[List[float]]]:
    """The seven disjoint state intervals, in precedence order.

    ``away`` beats everything: nothing that happened while the window was
    inactive is part of this session's work.

    ``compute`` beats activity. A click that starts a three-second computation
    produces one input event and a three-second block, and the three seconds are
    the algorithm's, not the person's. The generous ``BLOCK_THRESHOLD_S`` is
    what makes this safe -- see its comment: the case it must not steal is a
    drag that keeps the main thread intermittently busy, and those gaps are
    individually far shorter than the threshold.
    """
    session = [[float(start), float(stop)]]
    away = _intersect(session, _away_from_events(events, start, stop))
    taken = list(away)
    compute = _subtract(_intersect(session, _blocked_from_ticks(events)), taken)
    taken = _merge([(a, b) for a, b in taken + compute])

    out: Dict[str, List[List[float]]] = {STATE_AWAY: away, STATE_COMPUTE: compute}
    bursts = _bursts_from_events(events)
    for kind in TARGET_KINDS:
        spans = [[a, b] for a, b, target in bursts if target == kind]
        resolved = _subtract(_intersect(session, spans), taken)
        out[kind] = resolved
        taken = _merge([(a, b) for a, b in taken + resolved])
    out[STATE_IDLE] = _subtract(session, taken)
    return out


def _INPUT_KINDS_default() -> Tuple[str, ...]:
    return ("click", "release", "double", "drag", "wheel", "key")


#: Event kinds that count as the person operating Slicer. ``tick`` and ``focus``
#: are bookkeeping and are excluded, which is what keeps a session with no input
#: at all reading as 100% idle rather than 100% active.
_INPUT_KINDS = _INPUT_KINDS_default()

#: The kinds carried out of a session individually, so a reader can attribute
#: them to any window it likes rather than to the label windows the recorder
#: happened to use. Deliberately NOT ``drag`` or ``release``: pointer motion is
#: the bulk of the event list and nothing per-window needs it, while these four
#: are a few hundred entries in a long session.
_REPORTED_INPUT_KINDS = ("click", "double", "wheel", "key")


# ---------------------------------------------------------------------------
# The recorder
# ---------------------------------------------------------------------------

class InputRecorder:
    """Records Slicer's input events and the main thread's availability.

    Nothing here interprets anything: ``eventFilter`` appends tuples and the
    heartbeat appends tuples. ``snapshot()`` is where the rules live.

    Every click is gated on the Slicer main window being the ACTIVE window. The
    filter is installed on our own ``QApplication`` so another application's
    clicks could never reach it anyway; the gate is for the case the study
    actually produces -- a participant who alt-tabs to a browser and whose
    window manager still routes a stray event here -- and it is the same fact
    the ``away`` bucket records for time.
    """

    #: Sent to ourselves at install time to prove the filter is really being
    #: called. PythonQt's dispatch of a C++ virtual to a Python override is not
    #: guaranteed, and a filter that is silently never invoked would present as
    #: "recording produced nothing", discovered only when the study is over.
    #: F35 is chosen because no keyboard has one.
    PROBE_KEY_NAME = "Key_F35"

    def __init__(self):
        self._events: List[List[Any]] = []
        self._started: Optional[float] = None
        self._stopped: Optional[float] = None
        self._label = ""
        #: label -> [event index range start]; a label's events are the slice
        #: from where it was set to where the next one was.
        self._label_marks: List[List[Any]] = []
        self._filter = None
        self._timer = None
        self._app = None
        self._hook = "none"
        self._probe_seen = False
        #: The live button mask, READ from each event rather than counted.
        #: A counter drifts the moment deliveries are not one-to-one, and a
        #: stuck non-zero value turns every hover into a recorded drag.
        self._button_down = 0
        self._last_event_key = None
        self._last_event_time = 0.0
        #: What the counted delivery of the current event said, and where its
        #: entry sits in `_events` -- so a later delivery that knows better can
        #: correct both rather than being thrown away.
        self._last_target = TARGET_OTHER
        self._last_target_index = None
        #: The widget of the extension being recorded. Without it `panel` means
        #: any module panel, and clicks spent in OTHER modules -- which is what
        #: a novice does, and what a learning curve should show falling -- are
        #: booked as operating this procedure's own panel.
        self.panel_root = None
        self._last_drag_sample = 0.0
        self._last_pos = None
        self._drag_pixels = 0.0
        self._drag_moves = 0
        self._counts: Dict[str, float] = {}
        #: The alive span currently being extended, mutated in place on every
        #: heartbeat -- see `_alive_spans`. It is the SAME list object that sits
        #: in `_events`, which is what makes extending it free.
        self._alive: Optional[List[Any]] = None
        self._was_active = True

    # -- lifecycle ------------------------------------------------------
    @property
    def running(self) -> bool:
        return self._started is not None and self._stopped is None

    @property
    def hook(self) -> str:
        """``event_filter`` once proved, ``unverified`` when the probe failed."""
        return self._hook

    def start(self, label: str = "", panel_root=None) -> bool:
        """Install the filter and the heartbeat. Idempotent; never raises.

        ``panel_root`` is the owning extension's widget -- see ``panel_root``.
        """
        if self.running:
            return True
        self.panel_root = panel_root
        import qt  # noqa: F401  (Slicer-only; see the module docstring)

        self._events = []
        self._counts = {}
        self._label_marks = []
        self._started = time.time()
        self._stopped = None
        self._alive = None
        self._was_active = self._main_window_active()
        self.mark(label)
        try:
            self._install_filter()
        except Exception:
            logger.warning("Input recorder: the event filter could not be "
                           "installed", exc_info=True)
            self._hook = "unavailable"
        try:
            self._start_heartbeat()
        except Exception:
            logger.warning("Input recorder: the heartbeat could not be started",
                           exc_info=True)
        # The session opens with a focus event whatever the state, so
        # `_away_from_events` never has to guess where it began.
        self._append("focus", self._was_active)
        return True

    def stop(self) -> None:
        """Remove the filter and the heartbeat. Keeps every recorded event."""
        if self._started is None or self._stopped is not None:
            return
        self._stopped = time.time()
        try:
            if self._filter is not None and self._app is not None:
                self._app.removeEventFilter(self._filter)
        except Exception:
            logger.debug("Removing the input event filter failed", exc_info=True)
        self._filter = None
        try:
            if self._timer is not None:
                self._timer.stop()
        except Exception:
            logger.debug("Stopping the heartbeat failed", exc_info=True)
        self._timer = None

    def mark(self, label: str) -> None:
        """Name what is happening from now on (the guided arm passes the step id).

        The label partitions the event list by index rather than by time, so a
        step re-visited after a rewind accumulates into the same label -- which
        is what ``steps[]`` in the run manifest does, and therefore what the
        per-step numbers in ``interaction.json`` can be compared against.
        """
        label = str(label or "")
        if self._label_marks and self._label_marks[-1][0] == label:
            return
        self._label_marks.append([label, len(self._events), time.time()])
        self._label = label

    # -- Qt plumbing ----------------------------------------------------
    def _install_filter(self) -> None:
        import qt

        recorder = self

        class _Filter(qt.QObject):
            def eventFilter(self, obj, event):
                try:
                    recorder._handle(obj, event)
                except Exception:
                    # A filter runs for every event in the application; letting
                    # one raise would be a storm, and a study session that dies
                    # because its instrument raised has lost the data it was
                    # recording.
                    pass
                # NEVER consume. This is an observer: swallowing an event would
                # change the behaviour of the software under measurement, which
                # is the one thing an instrument may not do.
                return False

        self._app = qt.QApplication.instance()
        if self._app is None:
            import slicer
            self._app = slicer.app          # Slicer's app IS the QApplication
        self._filter = _Filter()
        self._app.installEventFilter(self._filter)
        self._hook = "event_filter" if self._probe_filter() else "unverified"

    def _probe_filter(self) -> bool:
        """One synthetic key event, and a check that the filter saw it."""
        import qt

        key = getattr(qt.Qt, self.PROBE_KEY_NAME, None)
        if key is None:
            return False
        try:
            # The main window when there is one, the application otherwise --
            # the same target the voice push-to-talk probe uses, which is the
            # spelling proven to work under PythonQt.
            window = self._main_window() or qt.QApplication.instance()
            if window is None:
                return False
            self._probe_seen = False
            event = qt.QKeyEvent(qt.QEvent.KeyPress, key, qt.Qt.NoModifier)
            qt.QApplication.sendEvent(window, event)
            return bool(self._probe_seen)
        except Exception:
            logger.debug("Input recorder: the filter probe failed", exc_info=True)
            return False

    def _start_heartbeat(self) -> None:
        import qt

        recorder = self
        self._timer = qt.QTimer()
        self._timer.setInterval(HEARTBEAT_MS)

        def _tick():
            try:
                recorder._on_tick()
            except Exception:
                pass

        self._timer.connect("timeout()", _tick)
        self._timer.start()

    @staticmethod
    def _main_window():
        try:
            import slicer
            return slicer.util.mainWindow()
        except Exception:
            return None

    def _main_window_active(self) -> bool:
        window = self._main_window()
        if window is None:
            return True          # fail open: unknown focus is not "away"
        try:
            return bool(window.isActiveWindow())
        except Exception:
            return True

    @staticmethod
    def _override_cursor_set() -> bool:
        try:
            import qt
            return qt.QApplication.overrideCursor() is not None
        except Exception:
            return False

    # -- the two producers ----------------------------------------------
    def _append(self, kind: str, target: Any) -> None:
        self._events.append([kind, round(time.time(), 4), target])

    def _bump(self, name: str, amount: float = 1) -> None:
        self._counts[name] = self._counts.get(name, 0) + amount

    def _on_tick(self) -> None:
        """Heartbeat: the main thread is alive, and here is whether it was busy.

        Also where focus transitions are noticed. Qt delivers
        ``WindowActivate`` / ``WindowDeactivate`` to the window, and those do
        reach an application filter -- but only while the application is getting
        events at all, which is exactly what is in question. Polling the flag on
        a timer that is itself a liveness proof is the reading that cannot be
        missed.

        The heartbeat itself is recorded as a SPAN that is extended in place,
        never as one event per tick: at 10 Hz the points alone would be 36,000
        entries an hour, which is a list that grows with the clock rather than
        with anything the participant did.
        """
        if not self.running:
            return
        now = time.time()
        busy = self._override_cursor_set()
        current = self._alive
        if current is not None and current[2] == busy and now - current[1] <= BLOCK_THRESHOLD_S:
            # The common case, and the reason this is a span and not a point:
            # a responsive minute costs one in-place write, not 600 appends.
            current[1] = now
        else:
            if current is not None and now - current[1] <= BLOCK_THRESHOLD_S:
                # A busy CHANGE with no gap: start where the last span ended so
                # the boundary is never read as a block.
                self._alive = [current[1], now, busy]
            else:
                self._alive = [now, now, busy]
            self._events.append(["alive", self._alive[0], self._alive])
        active = self._main_window_active()
        if active != self._was_active:
            self._was_active = active
            self._append("focus", active)

    def _handle(self, obj, event) -> None:
        import qt

        if not self.running:
            return
        kind = event.type()
        if kind == qt.QEvent.KeyPress:
            probe = getattr(qt.Qt, self.PROBE_KEY_NAME, None)
            try:
                if probe is not None and event.key() == probe:
                    self._probe_seen = True
                    return
            except Exception:
                pass

        if kind in (qt.QEvent.MouseButtonPress, qt.QEvent.MouseButtonDblClick,
                    qt.QEvent.MouseButtonRelease, qt.QEvent.MouseMove,
                    qt.QEvent.Wheel):
            if not self._was_active:
                return
            target = self._resolve_target(obj, event)
            if kind == qt.QEvent.MouseMove:
                self._on_move(event, target)
                return
            if kind == qt.QEvent.Wheel:
                if self._is_duplicate_delivery(event, kind):
                    self._upgrade_target(target)
                    return
                self._last_target = target
                self._last_target_index = len(self._events)
                self._append("wheel", target)
                self._bump("wheel_notches")
                self._bump("wheel_" + target)
                return
            self._on_button(event, kind, target)
            return

        if kind == qt.QEvent.KeyPress:
            if not self._was_active:
                return
            try:
                if event.isAutoRepeat():
                    return
            except Exception:
                pass
            self._append("key", self._resolve_target(obj, event))
            self._bump("keys")

    def _resolve_target(self, obj, event) -> str:
        """Where did this land: a 3D view, a slice view, the panel, or elsewhere?

        The object that received the delivery first, and the widget under the
        POINTER second. Qt delivers a mouse event to the `QWidgetWindow` before
        the widget, and a QWindow's parents are windows -- so asking only the
        receiver answers `other` for every click in a view, which is what made
        the 3D / slice / panel split sit at zero while the total rose.

        `widgetAt` is a hit test and is only reached when the chain gave
        nothing, so the common case still costs one walk.
        """
        target = classify_widget(obj, self.panel_root)
        if target != TARGET_OTHER:
            return target
        try:
            import qt
            widget = qt.QApplication.widgetAt(event.globalX(), event.globalY())
        except Exception:
            return TARGET_OTHER
        return (classify_widget(widget, self.panel_root)
                if widget is not None else TARGET_OTHER)

    def _upgrade_target(self, target: str) -> None:
        """A repeat delivery knew where the click landed; the counted one did not.

        Rewrites the recorded EVENT as well as the counter: the event's target
        is what `_bursts_from_events` attributes time by, and the time is the
        larger of the two numbers.
        """
        if target == TARGET_OTHER or self._last_target != TARGET_OTHER:
            return
        index = self._last_target_index
        if index is None or not (0 <= index < len(self._events)):
            return
        self._events[index][2] = target
        for prefix in ("clicks_", "wheel_"):
            stale = prefix + TARGET_OTHER
            if self._counts.get(stale):
                self._counts[stale] -= 1
                if not self._counts[stale]:
                    self._counts.pop(stale, None)
                self._bump(prefix + target)
        self._last_target = target

    def _is_duplicate_delivery(self, event, kind) -> bool:
        """Has this exact physical event already been counted?

        The filter sits on the QApplication, so it runs once per DELIVERY, and
        Slicer's VTK views re-dispatch a mouse event to a second object --
        which is why one press-and-drag in a 3D view counted as several clicks.

        Qt stamps every input event with the time the window system produced
        it, so two deliveries of one event are identical in `timestamp()` while
        two real clicks never are (they are hundreds of milliseconds apart and
        the stamp is in milliseconds). Where PythonQt does not expose it, the
        fallback is an identical (type, button, screen position) inside
        `DUPLICATE_WINDOW_S` -- which no hand can produce twice, and which a
        double click does not trip either, since its two presses are far apart
        and its `MouseButtonDblClick` is a different type.
        """
        try:
            button = int(event.button())
        except Exception:
            button = 0
        try:
            position = (event.globalX(), event.globalY())
        except Exception:
            position = None
        try:
            stamp = int(event.timestamp())
        except Exception:
            stamp = None
        key = (int(kind), button, position, stamp)
        now = time.time()
        if key == self._last_event_key and (
                stamp is not None or now - self._last_event_time < DUPLICATE_WINDOW_S):
            self._bump("clicks_duplicate_suppressed")
            return True
        self._last_event_key = key
        self._last_event_time = now
        return False

    def _read_button_mask(self, event) -> None:
        """Take the held-button set from the event itself.

        `buttons()` is the mask AFTER the event -- it includes the button on a
        press and excludes it on a release -- so reading it is exact however
        many times the event is delivered. The previous code incremented on
        press and decremented on release, which drifts upward the moment one
        press is delivered twice, and a stuck non-zero value makes `_on_move`
        record every hover as a drag for the rest of the session.
        """
        try:
            self._button_down = int(event.buttons())
        except Exception:
            pass          # keep the last known mask rather than guessing zero

    def _on_button(self, event, kind, target: str) -> None:
        import qt

        if self._is_duplicate_delivery(event, kind):
            # Not counted again -- but this delivery may know where the click
            # landed when the one that was counted did not.
            self._upgrade_target(target)
            return
        self._read_button_mask(event)
        self._last_target = target
        self._last_target_index = len(self._events)

        if kind == qt.QEvent.MouseButtonRelease:
            self._append("release", target)
            if self._drag_moves >= 3:
                self._bump("drags")
                self._bump("drag_pixels", round(self._drag_pixels, 1))
                self._bump("drags_" + target)
            self._drag_moves = 0
            self._drag_pixels = 0.0
            self._last_pos = None
            return

        self._last_pos = None
        self._drag_moves = 0
        self._drag_pixels = 0.0
        if kind == qt.QEvent.MouseButtonDblClick:
            # Qt sends Press, Release, DblClick, Release for a double click, so
            # the two presses are already counted. Counting the DblClick as a
            # third would inflate every double click by 50%.
            self._append("double", target)
            self._bump("double_clicks")
            return
        self._append("click", target)
        self._bump("clicks_total")
        self._bump("clicks_" + target)
        try:
            button = int(event.button())
            self._bump({int(qt.Qt.LeftButton): "clicks_left",
                        int(qt.Qt.RightButton): "clicks_right",
                        int(qt.Qt.MiddleButton): "clicks_middle"}.get(
                            button, "clicks_other_button"))
        except Exception:
            pass

    def _on_move(self, event, target: str) -> None:
        # The mask on the event itself, not a remembered one: this is the gate
        # that decides drag from hover, and a stale "a button is down" turns the
        # whole session's idle time into recorded 3D-view interaction.
        self._read_button_mask(event)
        if not self._button_down and not RECORD_HOVER:
            return
        now = time.time()
        try:
            position = (event.globalX(), event.globalY())
        except Exception:
            position = None
        if position is not None and self._last_pos is not None:
            self._drag_pixels += math.hypot(position[0] - self._last_pos[0],
                                            position[1] - self._last_pos[1])
        if position is not None:
            self._last_pos = position
        if (now - self._last_drag_sample) * 1000.0 < DRAG_SAMPLE_MS:
            return
        self._last_drag_sample = now
        self._drag_moves += 1
        self._append("drag", target)

    # -- the reading ----------------------------------------------------
    def snapshot(self, now: Optional[float] = None) -> Dict[str, Any]:
        """The partition, the counters and the per-label breakdown.

        Safe to call while running -- the session is closed at ``now`` for the
        purpose of the arithmetic and the recorder keeps going -- which is what
        lets the panel show a live figure and what lets a killed session still
        have a readable last write.
        """
        if self._started is None:
            return {"schema": SCHEMA, "recorded": False}
        stop = float(self._stopped if self._stopped is not None
                     else (now if now is not None else time.time()))
        start = float(self._started)
        spans = partition(self._events, start, stop)
        payload: Dict[str, Any] = {
            "schema": SCHEMA,
            "recorded": True,
            "hook": self._hook,
            "started_epoch": round(start, 3),
            "stopped_epoch": round(stop, 3),
            "running": self.running,
            "wall_seconds": round(stop - start, 3),
            "settings": {
                "heartbeat_ms": HEARTBEAT_MS,
                "block_threshold_s": BLOCK_THRESHOLD_S,
                "idle_gap_s": IDLE_GAP_S,
                "burst_pad_s": BURST_PAD_S,
                "drag_sample_ms": DRAG_SAMPLE_MS,
                "record_hover": RECORD_HOVER,
            },
            "totals": {state: _total(spans[state]) for state in ALL_STATES},
            "counts": {key: (round(value, 1) if isinstance(value, float) else value)
                       for key, value in sorted(self._counts.items())},
            "events_recorded": len(self._events),
            "spans": [[round(a, 3), round(b, 3), state]
                      for state in ALL_STATES for a, b in spans[state]
                      if state != STATE_IDLE],
        }
        payload["spans"].sort(key=lambda row: row[0])
        # Each counted click, with when and where. The per-step tables in the
        # guided report attribute these to the STEP'S OWN window, which is not
        # the window `by_label` uses -- see `_by_label`.
        payload["input_events"] = [
            [event[0], round(float(event[1]), 3), str(event[2])]
            for event in self._events
            if event[0] in _REPORTED_INPUT_KINDS and start <= float(event[1]) <= stop
        ]
        payload["by_label"] = self._by_label(start, stop)
        return payload

    def live_summary(self) -> Dict[str, Any]:
        """Elapsed seconds and the running counters. O(1).

        The panel's status line refreshes once a second, and ``snapshot()``
        re-derives the whole partition -- a sort plus interval arithmetic over
        every event recorded so far. An hour into a session that is hundreds of
        milliseconds of main-thread work every second, which would perturb the
        very measurement it is displaying: the recorder would be charging the
        participant compute time for the act of watching the clock.
        """
        if self._started is None:
            return {"recorded": False, "seconds": 0.0, "counts": {}}
        stop = self._stopped if self._stopped is not None else time.time()
        return {
            "recorded": True,
            "running": self.running,
            "seconds": round(float(stop) - float(self._started), 3),
            "counts": dict(self._counts),
        }

    def _by_label(self, start: float, stop: float) -> Dict[str, Any]:
        """Per-label totals, from the event-index ranges ``mark()`` recorded.

        NOTE the window: a label runs from the moment it was set to the moment
        the NEXT was, so the labels TILE the whole recording -- the gaps between
        steps and the wait at the end included. That is the right shape for the
        unaided arm, whose phases are whatever the operator marked, and the
        wrong one for a guided step, whose wall clock excludes those gaps. The
        guided report therefore does not read this: it intersects ``spans`` and
        ``input_events`` with the step's own visit windows.

        A label's window runs from the moment it was set to the moment the next
        was, so the windows tile the session and their totals sum to it. A label
        set more than once (a re-visited step) accumulates, which is what makes
        these comparable with the run manifest's per-step aggregate.
        """
        if not self._label_marks:
            return {}
        windows: List[Tuple[str, float, float]] = []
        for index, (label, _start_index, stamp) in enumerate(self._label_marks):
            end = (self._label_marks[index + 1][2]
                   if index + 1 < len(self._label_marks) else stop)
            windows.append((label, float(stamp), float(end)))
        out: Dict[str, Any] = {}
        for label, window_start, window_end in windows:
            if window_end <= window_start:
                continue
            entry = out.setdefault(label, {"seconds": 0.0, "visits": 0,
                                           "totals": {s: 0.0 for s in ALL_STATES},
                                           "counts": {}})
            entry["visits"] += 1
            entry["seconds"] = round(entry["seconds"] + window_end - window_start, 3)
            sliced = self.slice_totals(window_start, window_end, start, stop)
            for state, value in sliced["totals"].items():
                entry["totals"][state] = round(entry["totals"][state] + value, 3)
            for key, value in sliced["counts"].items():
                entry["counts"][key] = entry["counts"].get(key, 0) + value
        return out

    def slice_totals(self, window_start: float, window_end: float,
                     start: Optional[float] = None,
                     stop: Optional[float] = None) -> Dict[str, Any]:
        """The partition and the click counts restricted to one time window."""
        start = float(self._started if start is None else start)
        stop = float(stop if stop is not None else
                     (self._stopped if self._stopped is not None else time.time()))
        spans = partition(self._events, start, stop)
        window = [[max(window_start, start), min(window_end, stop)]]
        totals = {state: _total(_intersect(spans[state], window))
                  for state in ALL_STATES}
        counts: Dict[str, int] = {}
        for kind, stamp, target in ((e[0], float(e[1]), e[2]) for e in self._events):
            if kind not in _INPUT_KINDS or not (window[0][0] <= stamp < window[0][1]):
                continue
            if kind == "click":
                counts["clicks_total"] = counts.get("clicks_total", 0) + 1
                counts["clicks_" + str(target)] = counts.get("clicks_" + str(target), 0) + 1
            elif kind == "double":
                counts["double_clicks"] = counts.get("double_clicks", 0) + 1
            elif kind == "wheel":
                counts["wheel_notches"] = counts.get("wheel_notches", 0) + 1
            elif kind == "key":
                counts["keys"] = counts.get("keys", 0) + 1
        return {"totals": totals, "counts": counts}


def _widget_is_inside(root, widget) -> bool:
    """Is ``widget`` the panel ``root`` or somewhere inside it?

    ``isAncestorOf`` is asked first because it is Qt's own answer and needs no
    identity comparison -- PythonQt can hand out a fresh wrapper for the same
    C++ object, so ``a is b`` is not reliable between two lookups. It returns
    False for the root itself, though, so the chain walk below covers that,
    comparing with ``==`` (which PythonQt maps onto the underlying pointer) and
    treating any failure as "no" rather than guessing.
    """
    if root is None or widget is None:
        return False
    try:
        if root.isAncestorOf(widget):
            return True
    except Exception:
        pass
    node = widget
    for _ in range(24):
        try:
            if node == root:
                return True
        except Exception:
            pass
        try:
            node = node.parent()
        except Exception:
            break
        if node is None:
            break
    return False


def totals_in_windows(spans: Sequence[Sequence[Any]],
                      windows: Sequence[Sequence[float]]) -> Dict[str, float]:
    """Seconds per state inside ``windows``, with ``idle`` as the remainder.

    ``spans`` carries every state except ``idle`` -- idle is what is left when
    the others are taken out, which is also what makes the result sum to the
    windows exactly rather than approximately. A caller can therefore hand this
    any window it likes (a step's visits, a phase, a whole run) and get a
    partition of that window rather than of the recorder's own labelling.
    """
    merged = _merge([(float(a), float(b)) for a, b in windows])
    span_total = _total(merged)
    out = {state: 0.0 for state in ALL_STATES}
    grouped: Dict[str, List[List[float]]] = {}
    for row in spans or []:
        grouped.setdefault(str(row[2]), []).append([float(row[0]), float(row[1])])
    named = 0.0
    for state, intervals in grouped.items():
        if state not in out or state == STATE_IDLE:
            continue
        seconds = _total(_intersect(intervals, merged))
        out[state] = seconds
        named += seconds
    out[STATE_IDLE] = round(max(0.0, span_total - named), 3)
    return out


def counts_in_windows(input_events: Sequence[Sequence[Any]],
                      windows: Sequence[Sequence[float]]) -> Dict[str, int]:
    """Clicks, double clicks, wheel notches and keys inside ``windows``.

    Same key names as ``snapshot()["counts"]``, so a caller reads one vocabulary
    whichever window it asked about. Drags are absent for the reason they are
    absent from ``input_events``: a drag is a GESTURE closed at its release, and
    attributing one to a window it straddles would be a decision, not a count.
    """
    merged = _merge([(float(a), float(b)) for a, b in windows])
    out: Dict[str, int] = {}

    def bump(key):
        out[key] = out.get(key, 0) + 1

    for event in input_events or []:
        kind, stamp, target = event[0], float(event[1]), str(event[2])
        if not any(low <= stamp <= high for low, high in merged):
            continue
        if kind == "click":
            bump("clicks_total")
            bump("clicks_" + target)
        elif kind == "double":
            bump("double_clicks")
        elif kind == "wheel":
            bump("wheel_notches")
        elif kind == "key":
            bump("keys")
    return out


def classify_widget(obj, panel_root=None) -> str:
    """Where an event landed: a 3D view, a slice view, THIS panel, or elsewhere.

    ``panel_root`` is the widget of the extension being recorded, and without it
    ``panel`` would mean any module panel at all -- so a participant who opened
    Volumes or Segment Editor would have those clicks counted as operating the
    procedure's own panel. Everything inside Slicer that is not this panel and
    not a view is ``other``: other modules, other extensions, the toolbars, the
    menus, the data probe, the Python console.

    Walks the parent chain and matches ``className()`` by SUBSTRING, never
    against an exact list. Slicer nests its views several layers deep
    (``qMRMLSliceWidget`` -> ``qMRMLSliceView`` -> the VTK render widget) and the
    receiver of a mouse event is whichever of them holds focus, so an exact list
    would have to enumerate implementation detail and would go quietly wrong on
    the next Slicer release -- as "every click is 'other'", which looks like a
    participant who never touched a view.

    The views are tested before the panel because a view can legitimately be
    parented inside a panel (a module that embeds its own view), and the view is
    the more specific answer.
    """
    try:
        node = obj
        for _ in range(24):          # bounded: a cycle here would hang Slicer
            if node is None:
                break
            name = ""
            for read in (lambda: node.className(),
                         lambda: node.metaObject().className(),
                         lambda: type(node).__name__):
                # Three ways, because a wrapper that exposes none of the first
                # two would make EVERY object `other` -- and that reads as a
                # participant who never touched a view rather than as a fault.
                try:
                    name = str(read() or "")
                except Exception:
                    continue
                if name:
                    break
            if any(marker in name for marker in _VIEW_3D_MARKERS):
                return TARGET_VIEW_3D
            if any(marker in name for marker in _VIEW_2D_MARKERS):
                return TARGET_VIEW_2D
            # Only when nobody said which panel is ours -- otherwise this
            # would claim every module's frame.
            if panel_root is None and any(marker in name for marker in _PANEL_MARKERS):
                return TARGET_PANEL
            try:
                node = node.parent()
            except Exception:
                break
        # Views win over the panel, so this is asked only once the walk found
        # none: a view embedded in a panel is still a view.
        if panel_root is not None and _widget_is_inside(panel_root, obj):
            return TARGET_PANEL
    except Exception:
        logger.debug("Classifying an input target failed", exc_info=True)
    return TARGET_OTHER


# ---------------------------------------------------------------------------
# The report, shared by both arms
# ---------------------------------------------------------------------------

_STATE_LABELS = (
    (TARGET_VIEW_3D, "operating a 3D view"),
    (TARGET_VIEW_2D, "operating a slice view"),
    (TARGET_PANEL, "operating this extension's own panel"),
    (TARGET_OTHER, "elsewhere in Slicer (other modules, toolbars, menus)"),
    (STATE_COMPUTE, "algorithm running (main thread blocked)"),
    (STATE_IDLE, "idle -- reading, deciding, waiting"),
    (STATE_AWAY, "away -- Slicer was not the active window"),
)


def _fmt(seconds: Optional[float]) -> str:
    if seconds is None:
        return "unknown"
    seconds = float(seconds)
    if seconds < 60:
        return f"{seconds:.1f} s"
    minutes, rest = divmod(seconds, 60)
    if minutes < 60:
        return f"{seconds:.1f} s  ({int(minutes)} min {rest:04.1f} s)"
    hours, minutes = divmod(int(minutes), 60)
    return f"{seconds:.1f} s  ({hours} h {minutes} min {rest:04.1f} s)"


def render_interaction_sections(interaction: Optional[Dict[str, Any]]) -> List[str]:
    """The two interaction blocks, as report lines. Shared by both arms.

    Written here rather than in ``RunLog`` so the comparison arm renders the
    identical text with no ``SlicerAIAgentLib`` present: two arms whose reports
    are worded differently invite a reader to compare two things that are not
    the same measurement.
    """
    out: List[str] = []
    if not interaction or not interaction.get("recorded"):
        out.append(" INTERACTION: not recorded for this run.")
        out.append("")
        return out
    totals = interaction.get("totals") or {}
    counts = interaction.get("counts") or {}
    wall = interaction.get("wall_seconds")
    out.append(" What the person was doing (these seven sum to the recorded wall clock):")
    for state, label in _STATE_LABELS:
        out.append(f"   {label:<42}: {_fmt(totals.get(state))}")
    measured = sum(float(totals.get(state) or 0.0) for state in ALL_STATES)
    if wall is not None and abs(measured - float(wall)) > 1.0:
        # The partition is disjoint and total by construction, so a residual is
        # evidence of a bug rather than of rounding -- printed, never hidden.
        out.append(f"   [!] the seven sum to {measured:.1f} s, "
                   f"not the {float(wall):.1f} s recorded")
    out.append("")
    out.append(" Input, counted only while Slicer was the active window:")
    out.append(f"   mouse clicks                              : "
               f"{int(counts.get('clicks_total', 0))}"
               f"   (left {int(counts.get('clicks_left', 0))},"
               f" right {int(counts.get('clicks_right', 0))},"
               f" middle {int(counts.get('clicks_middle', 0))})")
    for kind, label in ((TARGET_VIEW_3D, "in a 3D view"),
                        (TARGET_VIEW_2D, "in a slice view"),
                        (TARGET_PANEL, "on this extension's own panel"),
                        (TARGET_OTHER, "elsewhere in Slicer (other modules etc.)")):
        out.append(f"     {label:<40}: {int(counts.get('clicks_' + kind, 0))}")
    out.append(f"   double clicks                             : "
               f"{int(counts.get('double_clicks', 0))}")
    out.append(f"   drags                                     : "
               f"{int(counts.get('drags', 0))}"
               f"   ({float(counts.get('drag_pixels', 0)) / 1000.0:.1f} k pixels of travel)")
    out.append(f"   wheel notches                             : "
               f"{int(counts.get('wheel_notches', 0))}")
    out.append(f"   key presses                               : "
               f"{int(counts.get('keys', 0))}")
    suppressed = int(counts.get("clicks_duplicate_suppressed", 0))
    if suppressed:
        # Reported, not hidden: a filter on the QApplication sees one physical
        # event once per delivery, and Slicer's VTK views re-dispatch. This is
        # how many repeats were dropped, so a rule that dropped too much would
        # show up here rather than as a quietly low count.
        out.append(f"   (repeat deliveries of one event, not counted : "
                   f"{suppressed})")
    hook = interaction.get("hook")
    if hook and hook != "event_filter":
        out.append(f"   [!] input hook was '{hook}': the counts above may be "
                   f"incomplete")
    out.append("")
    return out


def render_label_table(interaction: Optional[Dict[str, Any]],
                       title: str = "BY PHASE") -> List[str]:
    """One row per recorded label. Used by the comparison arm's report."""
    out: List[str] = []
    by_label = (interaction or {}).get("by_label") or {}
    rows = [(label, entry) for label, entry in by_label.items() if label]
    if not rows:
        return out
    thin = "-" * 78
    out.append(thin)
    out.append(f" {title}")
    out.append(thin)
    header = (f" {'phase':<22} {'wall':>9} {'active':>9} {'compute':>9} "
              f"{'idle':>9} {'clicks':>7}")
    out.append(header)
    out.append(" " + "-" * (len(header) - 1))
    for label, entry in rows:
        totals = entry.get("totals") or {}
        active = sum(float(totals.get(kind) or 0.0) for kind in TARGET_KINDS)
        out.append(
            f" {str(label)[:22]:<22} {float(entry.get('seconds') or 0):>8.1f}s "
            f"{active:>8.1f}s {float(totals.get(STATE_COMPUTE) or 0):>8.1f}s "
            f"{float(totals.get(STATE_IDLE) or 0):>8.1f}s "
            f"{int((entry.get('counts') or {}).get('clicks_total', 0)):>7}"
        )
    out.append("")
    return out


# ---------------------------------------------------------------------------
# Run folders: the same layout as the guided arm, so one analysis reads both
# ---------------------------------------------------------------------------

STATISTIC_DIRNAME = "Statistic"
RUNTIME_DIRNAME = "runtime"
SCENE_FILE_NAME = "scene.mrml"
INTERACTION_FILE_NAME = "interaction.json"
MANIFEST_FILE_NAME = "run_manifest.json"


def slug(text: Any, max_len: int = 48) -> str:
    cleaned = _UNSAFE.sub("-", str(text or "")).strip("-._")
    return cleaned[:max_len]


def timestamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def run_dir_name(procedure: str, subject: str = "",
                 condition: str = CONDITION_MANUAL, stamp: str = "") -> str:
    """``<Procedure>_<subject>_<condition>_<stamp>``.

    The same grammar as ``RunLog.run_dir_name`` -- procedure first, timestamp
    last -- so the two arms interleave in one ``logs/`` listing and sort by
    procedure and subject, which is the unit a learning curve is read in.
    """
    parts = [slug(procedure) or "task"]
    if subject:
        parts.append(slug(subject))
    parts.append(slug(condition) or CONDITION_MANUAL)
    parts.append(stamp or timestamp())
    return "_".join(part for part in parts if part)


def ensure_dir(path: str) -> str:
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        logger.warning("Could not create %s", path, exc_info=True)
    return path


def write_json(path: str, payload: Any) -> str:
    try:
        ensure_dir(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False, default=str)
        return path
    except Exception:
        logger.warning("Could not write %s", path, exc_info=True)
        return ""


def write_text(path: str, text: str) -> str:
    try:
        ensure_dir(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text or "")
        return path
    except Exception:
        logger.warning("Could not write %s", path, exc_info=True)
        return ""


# ---------------------------------------------------------------------------
# Saving the scene flat -- the ONE implementation, shared by both arms
# ---------------------------------------------------------------------------

def safe_file_name(name: Any) -> str:
    """Slicer's own filename rule (``qSlicerCoreIOManager::fileNameRegularExpression``)."""
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                  "0123456789 -_.()$!~#'%^{}")
    cleaned = "".join(ch for ch in str(name or "") if ch in allowed).strip()
    return cleaned[:255] or "node"


def save_scene_flat(directory: str, scene_file_name: str = SCENE_FILE_NAME,
                    progress=None) -> Tuple[int, str]:
    """Save the scene as ONE flat folder: ``scene.mrml`` beside every node's file.

    This is what File > Save Data produces with every row pointed at one
    directory. ``slicer.util.saveScene(<dir>)`` cannot give it: a directory path
    routes to ``qSlicerSceneWriter::writeToDirectory`` ->
    ``SaveSceneToSlicerDataBundleDirectory``, which builds ``Data/`` and
    ``private/`` subfolders.

    Mirrors ``qSlicerSaveDataDialogPrivate`` exactly: skip nodes that are not
    storable, are hidden from editors, or are not ``SaveWithScene``; give each
    remaining node a default storage node and skip it if it does not need one
    (it is stored inside the scene); name its file ``<sanitised node
    name>.<default write extension>``; and save the nodes FIRST, the scene last,
    so the ``.mrml`` records the paths the nodes were just written to.

    Every mutation it makes to the live scene -- storage-node file names, the
    scene URL and root directory, and the storable-modified flags that writing
    clears -- is undone afterwards, so the surgeon's own File > Save Data still
    offers their chosen directory and still shows their work as unsaved.
    Returns ``(files_written, note)``.

    ``progress(done, total, name)`` is called once per candidate node -- on the
    FULL storable list, including the ones filtered out below, so the bar
    advances monotonically instead of stalling through a run of skipped nodes.
    Optional and never allowed to fail the save.
    """
    import slicer

    scene = slicer.mrmlScene
    original_url = scene.GetURL()
    original_root = scene.GetRootDirectory()
    restore: Dict[str, Any] = {}
    used_names = set()
    written, skipped, failed = 0, 0, []
    try:
        # The root directory FIRST, before a single node is written. Every path
        # a storage node records while writing is relativised against
        # scene->GetRootDirectory() AS IT STANDS AT THAT MOMENT, not against the
        # .mrml written afterwards. Leave the user's own root in place and a
        # volume's fileListMember paths end up relative to THEIR folder while
        # the scene resolves them from this one -- so the saved scene does not
        # reload.
        scene.SetRootDirectory(str(directory).replace("\\", "/"))
        nodes = scene.GetNodesByClass("vtkMRMLStorableNode")
        nodes.UnRegister(None)
        candidates = nodes.GetNumberOfItems()
        for index in range(candidates):
            node = nodes.GetItemAsObject(index)
            if progress is not None:
                try:
                    progress(index, candidates,
                             (node.GetName() if node is not None else "") or "")
                except Exception:
                    logger.debug("Scene-save progress callback failed", exc_info=True)
            if node is None or node.GetHideFromEditors() or not node.GetSaveWithScene():
                skipped += 1
                continue
            storage = node.GetStorageNode()
            if storage is None:
                if not node.AddDefaultStorageNode():
                    skipped += 1
                    continue
                storage = node.GetStorageNode()
            if storage is None:
                skipped += 1      # no storage node needed: lives in the scene
                continue
            try:
                if slicer.app.coreIOManager().fileWriterFileType(node) == "NoFile":
                    skipped += 1
                    continue
            except Exception:
                logger.debug("fileWriterFileType probe failed", exc_info=True)
            name = safe_file_name(node.GetName() or node.GetID() or "node")
            extension = storage.GetDefaultWriteFileExtension() or ""
            if extension and not extension.startswith("."):
                extension = "." + extension
            candidate = f"{name}{extension}"
            suffix = 1
            while candidate.lower() in used_names:
                suffix += 1
                candidate = f"{name}_{suffix}{extension}"
            used_names.add(candidate.lower())
            key = storage.GetID()
            if key not in restore:
                restore[key] = (
                    storage,
                    storage.GetFileName(),
                    [storage.GetNthFileName(i)
                     for i in range(storage.GetNumberOfFileNames())],
                    storage.GetURI(),
                    (storage.GetCropToMinimumExtent()
                     if hasattr(storage, "GetCropToMinimumExtent") else None),
                )
            path = os.path.join(directory, candidate)
            try:
                if slicer.util.saveNode(node, path):
                    written += 1
                else:
                    failed.append(candidate)
            except Exception as exc:
                logger.debug("Saving node %s failed: %s", candidate, exc, exc_info=True)
                failed.append(candidate)
        scene_path = os.path.join(directory, scene_file_name)
        if progress is not None:
            try:
                progress(candidates, candidates, scene_file_name)
            except Exception:
                logger.debug("Scene-save progress callback failed", exc_info=True)
        if not slicer.util.saveScene(scene_path):
            failed.append(scene_file_name)
    finally:
        for storage, name, name_list, uri, crop in restore.values():
            try:
                storage.ResetFileNameList()
                storage.SetFileName(name)
                for extra in name_list:
                    if extra is not None:
                        storage.AddFileName(extra)
                storage.SetURI(uri)
                if crop is not None:
                    storage.SetCropToMinimumExtent(crop)
            except Exception:
                logger.debug("Restoring a storage node's save state failed",
                             exc_info=True)
        try:
            scene.SetURL(original_url)
            scene.SetRootDirectory(original_root)
            # Writing every node stamps its StoredTime, which clears
            # GetModifiedSinceRead() scene-wide -- the participant's own work
            # would then show as "Not Modified" in File > Save Data and Slicer
            # would not warn about it on quit, while the only copy on disk sat
            # in logs/.
            scene.SetStorableNodesModifiedSinceRead()
        except Exception:
            logger.debug("Restoring scene save state failed", exc_info=True)

    note = f"{written} node file(s) + {scene_file_name}"
    if skipped:
        note += f", {skipped} node(s) stored inside the scene"
    if failed:
        note += f". FAILED: {', '.join(failed[:6])}"
    return written, note


def scene_subject_name(extra_excluded: Sequence[str] = ()) -> Tuple[str, str]:
    """``(subject, folder)`` the scene's data was loaded from, or ``("", "")``.

    The same derivation the guided arm uses, so the two arms name the same
    patient the same way and the analysis can pair them. Read off the storage
    nodes rather than typed by the participant: a subject typed twice is a
    subject spelled two ways.

    The MOST COMMON parent folder wins, with two filters that each alone would
    be enough. Only the user's data votes (``HideFromEditors`` / not
    ``SaveWithScene`` is what File > Save Data would offer, and every colour node
    Slicer loads sets ``HideFromEditors``), and application-owned directories are
    excluded -- ~20 colour tables out of ``<slicerHome>/share`` otherwise
    outvote a case folder holding one volume and one markup, which produced a
    run folder named after Slicer's ``ColorFiles`` directory.
    """
    import slicer

    excluded = [str(path) for path in extra_excluded if path]
    for getter in (lambda: slicer.app.temporaryPath,
                   lambda: slicer.dicomDatabase.databaseDirectory,
                   lambda: slicer.app.slicerHome,
                   lambda: slicer.app.extensionsInstallPath):
        try:
            path = getter()
        except Exception:
            continue
        if path:
            excluded.append(path)
    excluded = [os.path.normcase(os.path.abspath(p)) for p in excluded if p]

    counts: Dict[str, int] = {}
    order: List[Tuple[str, str]] = []
    try:
        nodes = slicer.mrmlScene.GetNodesByClass("vtkMRMLStorableNode")
        nodes.UnRegister(None)
        for index in range(nodes.GetNumberOfItems()):
            node = nodes.GetItemAsObject(index)
            if node is None:
                continue
            try:
                if node.GetHideFromEditors() or not node.GetSaveWithScene():
                    continue
            except Exception:
                pass          # fail open: a node we cannot read still votes
            storage = node.GetStorageNode()
            filename = storage.GetFileName() if storage is not None else ""
            if not filename:
                continue
            folder = os.path.dirname(os.path.abspath(filename))
            normalised = os.path.normcase(folder)
            # Compared as a path, not as a string: a bare startswith would also
            # exclude a sibling whose name merely begins with one.
            if any(normalised == bad or normalised.startswith(bad + os.sep)
                   for bad in excluded):
                continue
            name = os.path.basename(folder)
            if not name:
                continue
            if name not in counts:
                order.append((name, folder))
            counts[name] = counts.get(name, 0) + 1
    except Exception:
        logger.debug("Subject detection failed", exc_info=True)
        return "", ""
    if not order:
        return "", ""
    return max(order, key=lambda item: counts[item[0]])


#: The file that identifies the agent's own directory. ``SLICER_AI_AGENT_ROOT``
#: in ``app/common.py`` is the folder holding it, and the guided arm writes
#: ``<that folder>/logs``. Naming the file rather than the folder is what makes
#: the search below independent of what the checkout happens to be called.
AGENT_MODULE_FILE = "SlicerAIAgent.py"

#: Where a vendored copy sits relative to the agent's directory. Tried before
#: the directory walk because they are exact and free; each is still CONFIRMED
#: by finding ``SlicerAIAgent.py`` there, so a wrong guess is never accepted.
_AGENT_ROOT_ROUTES = (
    os.pardir,                                                  # <agent>/SlicerAIAgentLib/
    os.path.join(os.pardir, os.pardir, "Slicer_agent"),          # External_extensions/<Ext>/
    os.path.join(os.pardir, os.pardir, os.pardir, "Slicer_agent"),  # .../<Ext>/<Sub>/
)


def agent_checkout_root(start: str = "") -> str:
    """The directory holding ``SlicerAIAgent.py``, found from THIS file, or ``""``.

    Two searches, and the second exists because the first names a folder. The
    named routes cover the five places this file is vendored and cost nothing;
    the walk then tries each ancestor and its immediate children, so a checkout
    renamed from ``Slicer_agent`` still resolves. Every candidate is confirmed
    by the presence of the module file, so neither search can return a directory
    that merely sits in the right place.
    """
    here = start or os.path.dirname(os.path.abspath(__file__))
    for relative in _AGENT_ROOT_ROUTES:
        candidate = os.path.normpath(os.path.join(here, relative))
        if os.path.isfile(os.path.join(candidate, AGENT_MODULE_FILE)):
            return candidate
    node = here
    for _ in range(6):
        if os.path.isfile(os.path.join(node, AGENT_MODULE_FILE)):
            return node
        try:
            for entry in sorted(os.listdir(node)):
                child = os.path.join(node, entry)
                if os.path.isfile(os.path.join(child, AGENT_MODULE_FILE)):
                    return child
        except OSError:
            pass
        parent = os.path.dirname(node)
        if parent == node:
            break
        node = parent
    return ""


def resolve_logs_root() -> Tuple[str, str]:
    """``(directory, where it came from)``.

    Both arms of the study must land in ONE ``logs/``, or the comparison has two
    directories that no script reads together and nothing says so -- the run
    completes, the report is written, and the halves are simply somewhere else.
    So every source below resolves to the AGENT's own ``logs/``; only the last
    is a different place, and it exists for a machine that has no agent at all.

    1. the ``SlicerAIAgent/studyLogRoot`` setting, which an organiser can pin;
    2. the **installed** SlicerAIAgent module's directory, via ``slicer.modules``
       -- definitionally the folder the pipeline writes to, since that is how
       ``SLICER_AI_AGENT_ROOT`` is derived;
    3. this file's own checkout (``agent_checkout_root``), which is what makes
       the comparison arm work with the agent module not loaded;
    4. ``<default scene path>/PlanningStudyLogs``, the only fallback that is a
       different directory, for a machine carrying the extension alone.

    The source is returned, not just the path, because the panel prints both: a
    study whose organiser cannot see where the data is going finds out at the end.
    """
    try:
        import qt
        value = qt.QSettings().value("SlicerAIAgent/studyLogRoot")
        if value:
            return str(value), "the studyLogRoot setting"
    except Exception:
        logger.debug("Reading the study log root setting failed", exc_info=True)
    try:
        import slicer
        module = getattr(slicer.modules, "slicerairagent", None)
        path = getattr(module, "path", "") if module is not None else ""
        if path:
            return os.path.join(os.path.dirname(path), "logs"), "the installed agent"
    except Exception:
        logger.debug("Locating the agent module failed", exc_info=True)
    root = agent_checkout_root()
    if root:
        return os.path.join(root, "logs"), "this checkout"
    try:
        import slicer
        return (os.path.join(slicer.app.defaultScenePath, "PlanningStudyLogs"),
                "NO AGENT FOUND -- fallback")
    except Exception:
        return (os.path.join(os.path.expanduser("~"), "PlanningStudyLogs"),
                "NO AGENT FOUND -- fallback")


def default_logs_root() -> str:
    """Just the directory. See ``resolve_logs_root`` for how it is found."""
    return resolve_logs_root()[0]


class PlanningRunRecord:
    """One comparison-arm run: its folder, its manifest, its report.

    Deliberately the same two children as a guided run -- ``runtime/`` and
    ``Statistic/`` -- holding the same file names, so ``scripts/collect_runs.py``
    and the per-procedure analyses read both arms without a special case. What
    is absent is absent for a reason a reader can see: there are no step folders
    because an unaided run has no steps, and that is the thing being compared.
    """

    SCHEMA = "slicer_planning_recorder.run_manifest/1"

    def __init__(self, procedure: str, logs_root: str = "",
                 condition: str = CONDITION_MANUAL, participant: str = "",
                 notes: str = "", panel_root=None):
        self.procedure = str(procedure or "")
        self.condition = str(condition or CONDITION_MANUAL)
        self.logs_root = logs_root or default_logs_root()
        self.participant = str(participant or "")
        self.notes = str(notes or "")
        self.recorder = InputRecorder()
        #: The owning extension's widget, so `panel` means THIS panel.
        self.panel_root = panel_root
        self.run_root = ""
        self.runtime_dir = ""
        self.subject = ""
        self.subject_source = ""
        self.started_epoch: Optional[float] = None
        self.stopped_epoch: Optional[float] = None
        self.saved_scene_dir = ""
        self.scene_note = ""
        #: Has any of this run reached disk? Nothing does until Save, so this
        #: is what the panel's NOT SAVED warning is driven from.
        self.saved = False

    # -- lifecycle ------------------------------------------------------
    def begin(self) -> str:
        """Start measuring. Creates NOTHING on disk -- see ``write_all``.

        The folder is only NAMED here, from the subject the scene shows at the
        start (which is the input data set, and is the one moment it can be read
        from) and the clock at the start (so the stamp says when the trial
        began, not when it was saved). Nothing is created until Save, so an
        abandoned or mis-started trial leaves no folder to find and delete.
        """
        try:
            self.subject, self.subject_source = scene_subject_name(
                extra_excluded=[self.logs_root])
        except Exception:
            self.subject, self.subject_source = "", ""
        name = run_dir_name(self.procedure, self.subject, self.condition)
        self.run_root = os.path.join(self.logs_root, name)     # planned, not made
        self.runtime_dir = os.path.join(self.run_root, RUNTIME_DIRNAME)
        self.started_epoch = time.time()
        self.stopped_epoch = None
        self.saved = False
        self.recorder.start(label="", panel_root=self.panel_root)
        return self.run_root

    def end(self) -> None:
        """Stop measuring. Still writes nothing.

        Everything the run produced is held in memory until ``write_all``. The
        cost is real and is why the panel says NOT SAVED in those words: a trial
        whose Save is forgotten, or whose Slicer is closed first, is lost
        entirely rather than losing only its scene.
        """
        if self.started_epoch is None:
            return
        self.recorder.stop()
        self.stopped_epoch = time.time()

    @property
    def unsaved(self) -> bool:
        """A run exists and nothing of it is on disk."""
        return self.started_epoch is not None and not self.saved

    def write_all(self, progress=None) -> bool:
        """Create the run folder and write all of it. This is the Save button.

        The scene is written FIRST so the manifest and the report can name what
        landed, and its failure is not fatal: a scene that cannot be written
        still leaves the measurement, with the reason recorded in the report
        rather than only in a log nobody reads.

        Returns whether the SCENE landed. ``saved`` is set whenever the record
        did, which is the weaker claim the panel needs to stop saying NOT SAVED.
        """
        if self.started_epoch is None or not self.runtime_dir:
            return False
        scene_ok = self.save_scene(progress=progress)
        interaction = self.recorder.snapshot()
        write_json(os.path.join(self.runtime_dir, INTERACTION_FILE_NAME), interaction)
        manifest = self.write_manifest(interaction)
        report = write_text(os.path.join(self.statistic_dir(), "timing.txt"),
                            self.build_report(interaction))
        self.saved = bool(manifest) or bool(report)
        return scene_ok

    # -- artifacts ------------------------------------------------------
    def statistic_dir(self) -> str:
        return ensure_dir(os.path.join(self.run_root, STATISTIC_DIRNAME))

    def manifest_data(self, interaction: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        interaction = interaction if interaction is not None else self.recorder.snapshot()
        totals = (interaction or {}).get("totals") or {}
        counts = (interaction or {}).get("counts") or {}
        payload = {
            "schema": self.SCHEMA,
            "condition": self.condition,
            "condition_label": (CONDITION_MANUAL_LABEL
                                if self.condition == CONDITION_MANUAL
                                else self.condition),
            "folder": os.path.basename(self.run_root),
            "extension": self.procedure,
            "subject": self.subject or None,
            "subject_source": self.subject_source or None,
            "participant": self.participant or None,
            "notes": self.notes or None,
            "started": (time.strftime("%Y-%m-%dT%H:%M:%S",
                                      time.localtime(self.started_epoch))
                        if self.started_epoch else None),
            "started_epoch": round(self.started_epoch, 3) if self.started_epoch else None,
            "stopped_epoch": round(self.stopped_epoch, 3) if self.stopped_epoch else None,
            "status": ("completed" if self.stopped_epoch else "running"),
            # Named `steps` and left empty ON PURPOSE, so a reader of the two
            # arms side by side sees that this arm has no step structure rather
            # than wondering whether the field failed to write.
            "steps": [],
            "interaction": {"totals": totals, "counts": counts,
                            "hook": (interaction or {}).get("hook")},
            "scene": {"directory": self.saved_scene_dir or None,
                      "note": self.scene_note or None},
        }
        return {key: value for key, value in payload.items() if value is not None}

    def write_manifest(self, interaction: Optional[Dict[str, Any]] = None) -> str:
        return write_json(os.path.join(self.runtime_dir, MANIFEST_FILE_NAME),
                          self.manifest_data(interaction))

    def save_scene(self, progress=None) -> bool:
        """Write ``Statistic/scene/``. Returns True only if a scene landed.

        A POSITIVE check -- the ``.mrml`` exists and at least one node was
        written -- rather than the absence of an exception: nothing in the save
        path raises, so "no exception" would report success for a save that
        wrote nothing.
        """
        try:
            scene_dir = ensure_dir(os.path.join(self.statistic_dir(), "scene"))
            written, note = save_scene_flat(scene_dir, progress=progress)
            self.saved_scene_dir = scene_dir
            self.scene_note = note
            return bool(written) and os.path.isfile(
                os.path.join(scene_dir, SCENE_FILE_NAME))
        except Exception as exc:
            logger.warning("Saving the scene failed: %s", exc, exc_info=True)
            self.scene_note = f"Scene save raised: {exc}"
            return False

    def build_report(self, interaction: Optional[Dict[str, Any]] = None) -> str:
        interaction = interaction if interaction is not None else self.recorder.snapshot()
        rule = "=" * 78
        out: List[str] = [rule,
                          " Slicer planning session - unaided extension run",
                          rule]
        out.append(f" Run folder    : {os.path.basename(self.run_root)}")
        out.append(f" Procedure     : {self.procedure or '(none)'}")
        if self.subject:
            out.append(f" Subject       : {self.subject}"
                       + (f"   ({self.subject_source})" if self.subject_source else ""))
        out.append(f" Condition     : {self.condition}")
        if self.participant:
            out.append(f" Participant   : {self.participant}")
        if self.notes:
            out.append(f" Notes         : {' '.join(self.notes.split())[:200]}")
        out.append("")
        out.append(f" Recording started : {_clock(self.started_epoch)}")
        out.append(f" Recording stopped : {_clock(self.stopped_epoch)}")
        out.append(f" TOTAL RUN TIME    : "
                   f"{_fmt((interaction or {}).get('wall_seconds'))}")
        out.append("")
        out.append(" This arm has no step structure: the participant drove the")
        out.append(" extension's own GUI, so there is nothing to tabulate per step.")
        out.append(" The split below is measured from Slicer's input events and is")
        out.append(" the SAME measurement the guided arm records, so the two are")
        out.append(" directly comparable.")
        out.append("")
        out.extend(render_interaction_sections(interaction))
        out.extend(render_label_table(interaction))
        out.append("-" * 78)
        out.append(" SCENE SNAPSHOT")
        out.append("-" * 78)
        if self.saved_scene_dir:
            out.append(f" Saved to: {self.saved_scene_dir}")
            out.append(f" {self.scene_note}")
        else:
            out.append(" Not saved. Press 'Save run' in the Session recording")
            out.append(" section to write the scene beside this report.")
        out.append("")
        out.append(rule)
        return "\n".join(out) + "\n"


def _clock(epoch: Optional[float]) -> str:
    if not epoch:
        return "not recorded"
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(epoch)))
    except (TypeError, ValueError):
        return "not recorded"


# ---------------------------------------------------------------------------
# The panel the four study extensions get
# ---------------------------------------------------------------------------

def _slicer_window():
    """Slicer's main window, or None -- so a dialog can be parented or skipped."""
    try:
        import slicer
        return slicer.util.mainWindow()
    except Exception:
        return None


def addRecorderPanel(widget, procedure: str, collapsed: bool = False):
    """Add the "Session recording (user study)" section to a module widget.

    Three lines in the host extension: import, this call anywhere in
    ``setup()``, and ``stopRecorderPanel(self)`` in ``cleanup()``. Everything
    else lives here, so the four extensions carry an identical, reviewable diff
    and cannot drift into measuring four different things.

    The section inserts itself at the **top** of the panel and starts expanded.
    Top, because a study instrument the operator has to scroll for is one they
    will find un-started at the end of a session -- and two of the four study
    extensions fill the panel's whole height before this is reached. Inserting
    rather than appending is also what makes the call position-independent: a
    host that adds it halfway through ``setup()`` gets the same panel as one
    that adds it last, so the four diffs stay identical.
    """
    try:
        panel = _RecorderPanel(widget, procedure, collapsed=collapsed)
        widget._planningRecorderPanel = panel
        return panel
    except Exception:
        # Never take the host extension down with us. A module that fails to
        # load because its instrument raised has destroyed the session it was
        # there to measure.
        logger.warning("The session recorder panel could not be added",
                       exc_info=True)
        return None


def stopRecorderPanel(widget) -> None:
    """Tear the panel's recording down. Safe to call when there is none."""
    panel = getattr(widget, "_planningRecorderPanel", None)
    if panel is None:
        return
    try:
        panel.shutdown()
    except Exception:
        logger.debug("Recorder panel shutdown failed", exc_info=True)


class _RecorderPanel:
    """Start / Stop / Save, a live status line, and where the data is going."""

    TITLE = "Session recording (user study)"

    def __init__(self, widget, procedure: str, collapsed: bool = False):
        import ctk
        import qt

        self._procedure = str(procedure or "")
        # The host module's own frame. `widget` is the ScriptedLoadableModuleWidget
        # and `widget.parent` is the QWidget every one of its controls sits in,
        # which is what makes `panel` mean THIS extension rather than any module.
        self._panelRoot = getattr(widget, "parent", None)
        self._record: Optional[PlanningRunRecord] = None
        self._tick = None

        section = ctk.ctkCollapsibleButton()
        section.text = self.TITLE
        section.collapsed = bool(collapsed)
        # insertWidget(0), never addWidget: the section belongs at the top of
        # the panel whatever the host does afterwards. Index 0 puts it above
        # Slicer's own Reload & Test section too, which is correct -- that one
        # only exists in developer mode and is not what the operator is here for.
        widget.layout.insertWidget(0, section)
        layout = qt.QVBoxLayout(section)
        self._section = section

        form = qt.QFormLayout()
        self._participantEdit = qt.QLineEdit()
        self._participantEdit.setPlaceholderText("e.g. P07  (optional)")
        self._participantEdit.toolTip = (
            "Written into the run manifest so a folder can be matched to a "
            "participant without a separate spreadsheet.")
        form.addRow("Participant / trial:", self._participantEdit)
        layout.addLayout(form)

        row = qt.QHBoxLayout()
        self._startButton = qt.QPushButton("Start recording")
        self._startButton.toolTip = (
            "Open a run folder and begin measuring. Clicks are counted only "
            "while Slicer is the active window.")
        self._stopButton = qt.QPushButton("Stop")
        self._stopButton.toolTip = (
            "Stop measuring. Nothing is written yet -- press 'Save run' to "
            "keep this trial.")
        self._saveButton = qt.QPushButton("Save run")
        self._saveButton.toolTip = (
            "Write the whole trial: the scene, the manifest, interaction.json "
            "and timing.txt. NOTHING reaches logs/ until this is pressed.")
        for button in (self._startButton, self._stopButton, self._saveButton):
            row.addWidget(button)
        layout.addLayout(row)

        self._statusLabel = qt.QLabel("Not recording.")
        self._statusLabel.setWordWrap(True)
        layout.addWidget(self._statusLabel)

        self._pathLabel = qt.QLabel("")
        self._pathLabel.setWordWrap(True)
        self._pathLabel.setStyleSheet("color: gray;")
        layout.addWidget(self._pathLabel)

        self._startButton.connect("clicked(bool)", self.onStart)
        self._stopButton.connect("clicked(bool)", self.onStop)
        self._saveButton.connect("clicked(bool)", self.onSave)

        self._tick = qt.QTimer()
        self._tick.setInterval(1000)
        self._tick.connect("timeout()", self._refresh)
        self._tick.start()

        # Closing the scene ends the case, so it ends the trial. Removed again
        # in shutdown(): a VTK observer holding a bound method keeps this panel
        # alive and would fire into a torn-down one after a module reload.
        self._sceneObserverTag = None
        try:
            import slicer
            self._sceneObserverTag = slicer.mrmlScene.AddObserver(
                slicer.mrmlScene.EndCloseEvent, self.onSceneClosed)
        except Exception:
            logger.debug("Could not observe the scene close", exc_info=True)

        self._refresh()

    # -- actions --------------------------------------------------------
    def onStart(self, _checked=False):
        import qt

        if self._record is not None and self._record.recorder.running:
            return
        # Nothing is on disk until Save, so starting over on top of a finished
        # unsaved trial destroys it silently. One question is cheap; losing a
        # participant's attempt is not.
        if self._record is not None and self._record.unsaved:
            answer = qt.QMessageBox.question(
                _slicer_window(),
                "Discard the unsaved run?",
                "The previous run was never saved, so nothing of it is on disk.\n"
                "Starting a new one discards it.\n\nDiscard and start?",
                qt.QMessageBox.Yes | qt.QMessageBox.No, qt.QMessageBox.No)
            if answer != qt.QMessageBox.Yes:
                return
        try:
            self._record = PlanningRunRecord(
                self._procedure, participant=self._participantEdit.text.strip(),
                panel_root=self._panelRoot)
            folder = self._record.begin()
            logger.info("[Study] recording into %s", folder)
        except Exception as exc:
            self._record = None
            self._statusLabel.setText(f"Could not start recording: {exc}")
            logger.warning("Starting the study recording failed", exc_info=True)
        self._refresh()

    def onStop(self, _checked=False):
        if self._record is None:
            return
        try:
            self._record.end()
        except Exception:
            logger.warning("Stopping the study recording failed", exc_info=True)
        self._refresh()

    def onSave(self, _checked=False):
        import qt

        if self._record is None:
            self._statusLabel.setText("Nothing to save: no run has been started.")
            return
        # Stop first if still running, so the saved scene and the reported
        # duration describe the same moment.
        if self._record.recorder.running:
            self._record.end()
        cursor_set = False
        try:
            qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)
            cursor_set = True
            scene_ok = self._record.write_all()
        except Exception as exc:
            logger.warning("Saving the study run failed", exc_info=True)
            self._statusLabel.setText(f"Save failed, NOTHING written: {exc}")
            return
        finally:
            if cursor_set:
                try:
                    qt.QApplication.restoreOverrideCursor()
                except Exception:
                    pass
        if scene_ok:
            self._statusLabel.setText(f"Saved. {self._record.scene_note}")
        elif self._record.saved:
            self._statusLabel.setText(
                f"Measurement saved, but NO scene landed on disk. "
                f"{self._record.scene_note}")
        else:
            self._statusLabel.setText("Save FAILED: nothing reached logs/.")
        self._refresh(keep_status=True)

    def onSceneClosed(self, caller=None, event=None):
        """The scene is gone, so the trial it measured is over.

        STOPS, and deliberately does not zero. Nothing is written before Save,
        so zeroing here would destroy a trial that exists only in memory -- and
        it would do it at the one moment an operator is least likely to be
        watching the panel. The counters the operator wants back at zero are
        reset by the next Start, which builds a fresh record.

        A run that was already stopped is left exactly as it is, so closing the
        scene after Stop and before Save cannot lose the trial either.
        """
        try:
            if self._record is None or not self._record.recorder.running:
                return
            self._record.end()
            self._statusLabel.setText(
                "Scene closed, so the trial ended and recording STOPPED. "
                "Press 'Save run' to keep it, or 'Start recording' to begin "
                "the next one.")
            self._refresh(keep_status=True)
        except Exception:
            logger.warning("Handling the scene close failed", exc_info=True)

    def shutdown(self):
        try:
            if self._tick is not None:
                self._tick.stop()
        except Exception:
            pass
        self._tick = None
        tag = getattr(self, "_sceneObserverTag", None)
        if tag is not None:
            try:
                import slicer
                slicer.mrmlScene.RemoveObserver(tag)
            except Exception:
                logger.debug("Removing the scene observer failed", exc_info=True)
            self._sceneObserverTag = None
        if self._record is not None and self._record.recorder.running:
            try:
                # Stop the hooks. Deliberately does NOT write: nothing is saved
                # without Save, and a teardown is not somebody pressing it.
                self._record.end()
            except Exception:
                logger.debug("Recorder shutdown stop failed", exc_info=True)
        if self._record is not None and self._record.unsaved:
            logger.warning("[Study] the module closed with an UNSAVED run "
                           "(%s); nothing was written",
                           os.path.basename(self._record.run_root))

    # -- status ---------------------------------------------------------
    def _refresh(self, keep_status: bool = False):
        try:
            running = self._record is not None and self._record.recorder.running
            started = self._record is not None and self._record.started_epoch
            self._startButton.setEnabled(not running)
            self._stopButton.setEnabled(bool(running))
            self._saveButton.setEnabled(bool(started))
            if self._record is None:
                # The SOURCE as well as the path: the two arms must share one
                # logs/, and "NO AGENT FOUND" is the one answer that means they
                # will not -- which is invisible in the path alone.
                root, source = resolve_logs_root()
                self._pathLabel.setText(f"Runs will be written under: {root}"
                                        f"   [{source}]")
            elif self._record.saved:
                self._pathLabel.setText(f"Saved to: {self._record.run_root}")
            else:
                # The folder does not exist yet. Saying so, and naming where it
                # WOULD go, is the difference between a trial the operator knows
                # is unsaved and one they assume is safe.
                self._pathLabel.setText(
                    f"Nothing written yet. Save run would create: "
                    f"{self._record.run_root}")
            if keep_status:
                return
            if self._record is None:
                self._statusLabel.setText("Not recording.")
                return
            # live_summary, not snapshot: this runs once a second for the
            # whole session, and snapshot() re-derives the entire partition.
            summary = self._record.recorder.live_summary()
            counts = summary.get("counts") or {}
            seconds = float(summary.get("seconds") or 0.0)
            state = ("Recording" if running
                     else ("Stopped - NOT SAVED" if self._record.unsaved
                           else "Saved"))
            self._statusLabel.setText(
                f"{state}  -  {int(seconds // 60):02d}:{int(seconds % 60):02d}  -  "
                f"{int(counts.get('clicks_total', 0))} clicks "
                f"({int(counts.get('clicks_' + TARGET_VIEW_3D, 0))} in 3D, "
                f"{int(counts.get('clicks_' + TARGET_VIEW_2D, 0))} in slices, "
                f"{int(counts.get('clicks_' + TARGET_PANEL, 0))} on the panel, "
                # Shown so that "everything is landing in `other`" says so on
                # screen, rather than looking like nothing was clicked at all.
                f"{int(counts.get('clicks_' + TARGET_OTHER, 0))} elsewhere)")
        except Exception:
            logger.debug("Recorder panel refresh failed", exc_info=True)
