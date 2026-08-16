"""Microphone capture and audio playback for the voice front-end.

WHY THIS FILE IS SHAPED THE WAY IT IS
-------------------------------------

This is the only module in the repository that touches hardware, and it is the
only one whose dependency (PortAudio, via ``sounddevice``) is *not* installed by
CMake. A surgeon's Slicer install may have no microphone, no PortAudio, a
locked-down pip, or an OS that refuses microphone permission -- and none of those
may take the module down with it. So the whole file obeys three rules:

1. **Importable with no audio backend at all.** ``sounddevice`` and ``numpy`` are
   imported lazily inside functions, never at module scope, and every failure is
   recorded as a *string* (:func:`audio_backend_error`) rather than raised at
   import. A voice feature that cannot start must leave the typed-text panel
   working, not break ``import SlicerAIAgentLib``.
2. **Qt-free and Slicer-free.** ``import slicer`` appears once, inside the
   installer, wrapped in try/except -- so this file can be unit-tested in a
   plain CPython interpreter (the dev interpreter here is 3.7).
3. **Every failure carries its remedy.** :class:`AudioUnavailable` messages name
   the pip command or the OS package, because the person hitting them is a
   clinician, not the developer who wrote the stack.

Two design decisions worth defending, because both are easy to "simplify" into
bugs:

*Capture runs on a blocking-read worker thread, not in a PortAudio callback.*
The callback runs on PortAudio's real-time thread; anything slow in it (a
``queue`` contention, a log line, a Qt signal) drops audio, and inside a Qt
application it produces stalls that are close to undebuggable. ``stream.read()``
on our own daemon thread costs one extra buffer of latency and makes the failure
mode "a late utterance" instead of "a corrupted one".

*The user callback is dispatched on a third thread with a bounded queue.*
Transcription is an HTTP round trip; if it ran on the capture thread the
microphone would be deaf for its duration. The queue is bounded at
:data:`_MAX_PENDING_UTTERANCES` and drops the **oldest** entry: in a surgical
workflow a command replayed a minute late is worse than a command lost, because
the scene it was spoken about no longer exists.

Nothing here persists audio. :data:`_DUMP_ENV_VAR` opts into writing captured
WAVs for debugging, off by default, and even then it goes through the fail-soft
``RunLog`` writers so a full disk cannot abort a capture.
"""

from __future__ import annotations

import array
import io
import logging
import math
import os
import struct
import subprocess
import sys
import tempfile
import threading
import time
import wave
from typing import Any, Callable, Dict, List, Optional, Tuple

try:  # queue is stdlib everywhere, but keep the import defensive for symmetry.
    import queue
except Exception:  # pragma: no cover - cannot realistically happen
    queue = None  # type: ignore

# ``deque`` is a C-level builtin type and cannot be absent the way an optional
# wheel can, so it is imported unconditionally. It was previously guarded like
# ``queue`` below, falling back to a plain ``list`` -- but a list has no
# ``maxlen``, so the pre-roll ring would have grown without bound on an
# always-on idle microphone (~2 KB/s, forever). A fallback that leaks is worse
# than an import that cannot fail.
from collections import deque

# ``audioop`` was removed in Python 3.13. It is only ever a fast path here; the
# struct/array fallback below is the contract.
try:
    import audioop as _audioop  # type: ignore
except Exception:
    _audioop = None  # type: ignore

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Audio format constants
# ---------------------------------------------------------------------------

#: 16 kHz mono is what qwen3-asr-flash is happiest with, and it is a third of
#: the bytes of a 48 kHz capture -- which matters because every utterance is
#: uploaded over HTTP while the surgeon waits.
DEFAULT_SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2  # int16
CHANNELS = 1

#: pip distribution that provides the PortAudio bindings *and* bundles the
#: native library in its wheels, so no OS package is needed on Windows/macOS.
_PIP_PACKAGE = "sounddevice"

#: Utterances allowed to queue up in front of a slow ``on_utterance``. Beyond
#: this the OLDEST is dropped -- see the module docstring.
_MAX_PENDING_UTTERANCES = 3

#: Blocks of trailing silence kept in an emitted utterance. A little tail helps
#: the recogniser decide the word ended; the rest is dead weight on the upload.
_TAIL_PAD_BLOCKS = 4

#: Smoothing for the idle ambient-floor tracker (per block, ~30 ms).
_FLOOR_EMA_ALPHA = 0.05

#: Absolute ceiling on the tracked ambient floor. Without it, a long stretch of
#: sub-threshold speech-shaped noise would ratchet the floor up until the
#: microphone is permanently deaf.
_MAX_TRACKED_FLOOR = 0.20

#: A measured noise floor at or below this is not a quiet room -- it is an input
#: device that has not started delivering audio yet. PortAudio commonly returns
#: zero-filled blocks for the first fraction of a second after a stream opens,
#: and calibrating on those yields a floor of 0.
_MIN_VALID_FLOOR = 1e-4

#: Extra calibration rounds to wait for a device that is still warming up,
#: before giving up and using an absolute threshold.
_MAX_CALIBRATION_ROUNDS = 4

#: Threshold used when calibration never produced a usable floor. Deliberately
#: well ABOVE a typical room: a threshold derived from a zero floor collapses to
#: ``min_threshold``, and if that sits below the ambient level then every block
#: is "speech", the detector never returns to idle, and each utterance runs to
#: the maximum length and is cut mid-sentence. Silence is recoverable; a
#: permanently-triggered microphone is not.
_FALLBACK_THRESHOLD = 0.03

#: A forced cut whose speech ran essentially the whole window is proof that the
#: threshold is below the room, not that somebody talked for fifteen seconds.
_SATURATED_SPEECH_RATIO = 0.9

#: Once speech has started, this fraction of the threshold keeps it going.
#: Standard VAD hysteresis. 0.5 is deliberately generous: the cost of holding on
#: through a pause is a slightly longer clip, and the cost of letting go is a
#: severed sentence that transcribes to nothing at all.
_SPEECH_EXIT_RATIO = 0.5

#: Peak amplitude (0..1) a captured clip is lifted towards before it is sent.
#: Recognisers are trained on speech at a healthy level; a laptop microphone at
#: arm's length routinely delivers a tenth of that.
_TARGET_PEAK = 0.60

#: Ceiling on that lift, so a clip containing only room tone is not amplified
#: into something that sounds like speech to the detector's downstream.
_MAX_GAIN = 8.0

#: Set this environment variable to a directory to persist captured WAVs for
#: debugging. Off by default: raw audio is patient-adjacent data.
_DUMP_ENV_VAR = "SLICER_AGENT_VOICE_DUMP"


class AudioUnavailable(RuntimeError):
    """Raised when capture or playback cannot start.

    The message is always remedy-bearing (a pip command, an OS package, or
    "plug in a microphone"), because it is shown to a clinician.
    """


# ---------------------------------------------------------------------------
# Backend acquisition
# ---------------------------------------------------------------------------

_backend_lock = threading.RLock()
_sd = None                 # the sounddevice module once imported
_numpy_mod = None          # numpy once imported
_numpy_tried = False
_backend_error_text = ""
_install_attempted = False


def _numpy():
    """Return numpy, or None. Cached; numpy is an accelerator here, never a
    requirement -- ``pcm_rms`` and the WAV path both work without it."""
    global _numpy_mod, _numpy_tried
    if _numpy_mod is not None or _numpy_tried:
        return _numpy_mod
    _numpy_tried = True
    try:
        import numpy  # type: ignore
        _numpy_mod = numpy
    except Exception:
        logger.debug("numpy unavailable; using stdlib audio math", exc_info=True)
        _numpy_mod = None
    return _numpy_mod


def _install_message(detail: str = "") -> str:
    """Build the one message a user can act on when there is no backend.

    Double quotes around the package name throughout, including inside the
    exception text CPython authored (which uses single quotes). The message is
    displayed as selectable text so the install line can be copied straight into
    Slicer's Python console, and a line that copies out in the same quoting
    style as the rest of this project is one less thing to retype.
    """
    lines = [
        'Microphone support needs the "sounddevice" package (PortAudio), which '
        'is not available in this Python environment.',
        "Install it into Slicer's own Python from the Python console:",
        '    slicer.util.pip_install("sounddevice")',
        "then restart Slicer. Voice stays off until then; the panel still works "
        "with typed text.",
    ]
    low = (detail or "").lower()
    if "portaudio" in low:
        lines.insert(
            2,
            "On Linux the wheel needs the system library too: "
            "sudo apt install libportaudio2",
        )
    if detail:
        lines.append("Details: %s" % detail)
    # Only the package name is re-quoted, so nothing else in an exception
    # message can be altered by this.
    return "\n".join(lines).replace("'%s'" % _PIP_PACKAGE, '"%s"' % _PIP_PACKAGE)


def _try_import_sounddevice() -> Tuple[Any, str]:
    """Import sounddevice. Returns (module, "") or (None, reason)."""
    try:
        import sounddevice  # type: ignore
        return sounddevice, ""
    except Exception as exc:
        # OSError here is the classic "PortAudio library not found" on Linux;
        # ImportError is "wheel not installed". Both are reported verbatim so
        # the remedy hint above can key on the text.
        return None, "%s: %s" % (type(exc).__name__, exc)


def _pip_install(package: str) -> bool:
    """Install ``package``, preferring Slicer's own interpreter.

    Shaped after ``SkillToolExecutor._install_rg``: try ``slicer.util.pip_install``
    first so the wheel lands in Slicer's Python rather than a developer shell,
    then fall back to ``sys.executable -m pip``. Never raises, never shows a
    modal -- a failed install degrades voice, it does not break the module.
    """
    try:
        import slicer  # noqa: F401  (Slicer-only; absent in the test interpreter)
        pip_install = getattr(getattr(slicer, "util", None), "pip_install", None)
        if callable(pip_install):
            pip_install(package)
            return True
    except Exception as exc:
        logger.warning("slicer.util.pip_install('%s') failed: %s", package, exc)

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            timeout=180,
        )
        if result.returncode != 0:
            stderr = b""
            try:
                stderr = result.stderr or b""
            except Exception:
                stderr = b""
            logger.warning(
                "pip install %s failed: %s",
                package,
                stderr.decode("utf-8", errors="ignore")[:1000],
            )
            return False
        return True
    except Exception as exc:
        logger.warning("pip install %s raised %s", package, exc)
        return False


def ensure_audio_backend(auto_install: bool = True) -> bool:
    """Make the audio backend importable, installing it once if permitted.

    Returns True when :mod:`sounddevice` is usable. On False,
    :func:`audio_backend_error` holds a remedy-bearing explanation. This never
    raises: callers that need a hard failure raise :class:`AudioUnavailable`
    themselves with that text.

    ``auto_install=False`` is for read-only probes (device listing, capability
    checks) which must not trigger a network install as a side effect of
    drawing a settings dialog.

    **The lock is NOT held across the install.** ``_pip_install`` runs a
    subprocess with a 180 s timeout, and ``_backend_lock`` is also taken by
    :func:`audio_backend_error` and (via :func:`_list_devices`) by both device
    listers -- all of which the Qt main thread calls to draw a settings dialog
    or a status label. Holding the lock over the subprocess therefore froze the
    whole application for up to three minutes behind a *background* install.
    Claiming ``_install_attempted`` under the lock and releasing it for the
    duration keeps the once-per-session guarantee (the claim is what is
    exclusive, not the work) while leaving every reader responsive; a
    concurrent caller simply sees "no backend yet", which is true.
    """
    global _sd, _backend_error_text, _install_attempted
    with _backend_lock:
        if _sd is not None:
            return True

        module, reason = _try_import_sounddevice()
        if module is not None:
            _sd = module
            _backend_error_text = ""
            return True

        _backend_error_text = _install_message(reason)
        if not auto_install:
            return False

        if _install_attempted:
            # One attempt per session. Retrying a failing pip on every click
            # would freeze the UI for 180 s at a time.
            return False
        _install_attempted = True

    logger.info("sounddevice missing (%s); attempting install", reason)
    _pip_install(_PIP_PACKAGE)

    # Verify by RE-IMPORTING rather than trusting pip's exit code: a wheel
    # can install cleanly and still fail to load its native library.
    module, reason2 = _try_import_sounddevice()
    with _backend_lock:
        if _sd is not None:      # another thread won the race while pip ran
            return True
        if module is not None:
            _sd = module
            _backend_error_text = ""
            logger.info("sounddevice installed and importable")
            return True

        _backend_error_text = _install_message(reason2 or reason)
        logger.warning("sounddevice still unavailable after install: %s", reason2)
        return False


def audio_backend_error() -> str:
    """The last backend failure reason, or "" when the backend is fine."""
    with _backend_lock:
        if _sd is not None:
            return ""
        return _backend_error_text or _install_message()


# ---------------------------------------------------------------------------
# Device enumeration
# ---------------------------------------------------------------------------

def _default_device_indices() -> Tuple[Optional[int], Optional[int]]:
    """(default input index, default output index); (None, None) if unknown."""
    try:
        default = _sd.default.device
    except Exception:
        return (None, None)
    try:
        if isinstance(default, (list, tuple)):
            din = default[0] if len(default) > 0 else None
            dout = default[1] if len(default) > 1 else None
        else:
            din = dout = default
        din = int(din) if din is not None and int(din) >= 0 else None
        dout = int(dout) if dout is not None and int(dout) >= 0 else None
        return (din, dout)
    except Exception:
        return (None, None)


def _list_devices(kind: str) -> List[Dict[str, Any]]:
    """Shared body of the two public listers. Never raises: an empty list means
    "cannot enumerate", which every caller must already handle (a machine with
    no microphone returns an empty list too)."""
    if not ensure_audio_backend(auto_install=False):
        return []
    key = "max_input_channels" if kind == "input" else "max_output_channels"
    try:
        devices = _sd.query_devices()
    except Exception:
        logger.debug("query_devices() failed", exc_info=True)
        return []

    din, dout = _default_device_indices()
    default_index = din if kind == "input" else dout

    out: List[Dict[str, Any]] = []
    try:
        for index, info in enumerate(devices):
            try:
                channels = int(info.get(key, 0) or 0)
            except Exception:
                channels = 0
            if channels <= 0:
                continue
            out.append({
                "index": index,
                "name": str(info.get("name", "device %d" % index)),
                "channels": channels,
                "default": (default_index is not None and index == default_index),
            })
    except Exception:
        logger.debug("Could not walk the device list", exc_info=True)
        return out
    return out


def list_input_devices() -> List[Dict[str, Any]]:
    """Input devices as ``[{"index", "name", "channels", "default"}, ...]``.

    Returns ``[]`` -- never raises -- when there is no backend or no microphone.
    """
    return _list_devices("input")


def list_output_devices() -> List[Dict[str, Any]]:
    """Output devices, same shape as :func:`list_input_devices`."""
    return _list_devices("output")


# ---------------------------------------------------------------------------
# WAV helpers
# ---------------------------------------------------------------------------

def encode_wav(pcm: bytes,
               sample_rate: int = DEFAULT_SAMPLE_RATE,
               channels: int = CHANNELS,
               sample_width: int = SAMPLE_WIDTH) -> bytes:
    """Wrap raw little-endian PCM in a RIFF/WAVE container.

    WAV rather than a compressed container on purpose: it is the one format the
    stdlib can both write and read, so the capture -> upload -> playback path
    needs no codec wheel and cannot fail on a machine without ffmpeg.
    """
    buffer = io.BytesIO()
    try:
        handle = wave.open(buffer, "wb")
        try:
            handle.setnchannels(int(channels))
            handle.setsampwidth(int(sample_width))
            handle.setframerate(int(sample_rate))
            handle.writeframes(pcm or b"")
        finally:
            handle.close()
    except Exception as exc:
        raise RuntimeError(
            "Could not encode captured audio as WAV (%s). This is a bug, not a "
            "configuration problem -- please report it." % exc
        )
    return buffer.getvalue()


def decode_wav(data: bytes) -> Tuple[bytes, int, int, int]:
    """Return ``(pcm, sample_rate, channels, sample_width)`` from WAV bytes."""
    try:
        handle = wave.open(io.BytesIO(data), "rb")
        try:
            channels = handle.getnchannels()
            width = handle.getsampwidth()
            rate = handle.getframerate()
            frames = handle.readframes(handle.getnframes())
        finally:
            handle.close()
    except Exception as exc:
        raise RuntimeError(
            "Could not decode WAV audio (%s). The data may be truncated or may "
            "not be a WAV file." % exc
        )
    return (frames, int(rate), int(channels), int(width))


def pcm_rms(pcm: bytes) -> float:
    """RMS of little-endian int16 PCM, normalised to 0..1.

    numpy when present; then ``audioop`` (gone in Python 3.13, hence the guard
    at import); then a pure ``array``/``struct`` loop so this keeps working on a
    future Slicer that ships a newer interpreter.
    """
    if not pcm:
        return 0.0
    usable = (len(pcm) // SAMPLE_WIDTH) * SAMPLE_WIDTH
    if usable <= 0:
        return 0.0
    data = pcm[:usable]

    np = _numpy()
    if np is not None:
        try:
            samples = np.frombuffer(data, dtype="<i2").astype("float32")
            if samples.size == 0:
                return 0.0
            value = float(np.sqrt(float(np.mean(samples * samples)))) / 32768.0
            return value if value < 1.0 else 1.0
        except Exception:
            logger.debug("numpy RMS failed; falling back", exc_info=True)

    if _audioop is not None:
        try:
            return min(1.0, float(_audioop.rms(data, SAMPLE_WIDTH)) / 32768.0)
        except Exception:
            logger.debug("audioop RMS failed; falling back", exc_info=True)

    try:
        samples_arr = array.array("h")
        samples_arr.frombytes(data)
        if sys.byteorder == "big":
            samples_arr.byteswap()
    except Exception:
        try:
            count = usable // SAMPLE_WIDTH
            samples_arr = struct.unpack("<%dh" % count, data)  # type: ignore
        except Exception:
            return 0.0
    total = 0
    count = 0
    for sample in samples_arr:
        total += sample * sample
        count += 1
    if count == 0:
        return 0.0
    return min(1.0, math.sqrt(float(total) / count) / 32768.0)


def pcm_peak(pcm: bytes) -> float:
    """Largest absolute sample of little-endian int16 PCM, normalised to 0..1."""
    if not pcm:
        return 0.0
    usable = (len(pcm) // SAMPLE_WIDTH) * SAMPLE_WIDTH
    if usable <= 0:
        return 0.0
    data = pcm[:usable]

    np = _numpy()
    if np is not None:
        try:
            samples = np.frombuffer(data, dtype="<i2")
            if samples.size == 0:
                return 0.0
            return min(1.0, float(np.max(np.abs(samples.astype("int32")))) / 32768.0)
        except Exception:
            logger.debug("numpy peak failed; falling back", exc_info=True)

    if _audioop is not None:
        try:
            return min(1.0, float(_audioop.max(data, SAMPLE_WIDTH)) / 32768.0)
        except Exception:
            logger.debug("audioop peak failed; falling back", exc_info=True)

    try:
        samples_arr = array.array("h")
        samples_arr.frombytes(data)
        if sys.byteorder == "big":
            samples_arr.byteswap()
    except Exception:
        return 0.0
    highest = 0
    for sample in samples_arr:
        magnitude = -sample if sample < 0 else sample
        if magnitude > highest:
            highest = magnitude
    return min(1.0, float(highest) / 32768.0)


def normalize_gain(pcm: bytes, target_peak: float = _TARGET_PEAK,
                   max_gain: float = _MAX_GAIN) -> Tuple[bytes, float]:
    """Lift a quiet clip towards ``target_peak``. Returns (pcm, gain applied).

    Recognisers are trained on speech at a healthy level. A laptop microphone at
    arm's length routinely delivers a peak around 0.05 -- roughly a tenth of
    that -- and a quiet clip is one of the ways an otherwise valid request comes
    back with an empty transcript.

    Only ever amplifies, never attenuates, and never beyond ``max_gain``, so a
    clip that is already loud is returned untouched and one containing only room
    tone is not inflated into something that merely sounds like speech. Clipping
    is impossible by construction: the gain is derived from the measured peak.
    """
    if not pcm:
        return pcm, 1.0
    peak = pcm_peak(pcm)
    if peak <= 0.0:
        return pcm, 1.0
    gain = target_peak / peak
    if gain <= 1.01:
        return pcm, 1.0
    gain = min(gain, max_gain)

    np = _numpy()
    if np is not None:
        try:
            samples = np.frombuffer(pcm, dtype="<i2").astype("float32") * gain
            samples = np.clip(samples, -32768.0, 32767.0).astype("<i2")
            return samples.tobytes(), gain
        except Exception:
            logger.debug("numpy gain failed; falling back", exc_info=True)

    try:
        samples_arr = array.array("h")
        samples_arr.frombytes(pcm[:(len(pcm) // SAMPLE_WIDTH) * SAMPLE_WIDTH])
        if sys.byteorder == "big":
            samples_arr.byteswap()
        for index in range(len(samples_arr)):
            scaled = int(samples_arr[index] * gain)
            if scaled > 32767:
                scaled = 32767
            elif scaled < -32768:
                scaled = -32768
            samples_arr[index] = scaled
        if sys.byteorder == "big":
            samples_arr.byteswap()
        return samples_arr.tobytes(), gain
    except Exception:
        logger.debug("Gain normalisation failed; sending the clip as captured",
                     exc_info=True)
        return pcm, 1.0


def _pcm_to_int16(pcm: bytes, sample_width: int) -> bytes:
    """Widen/narrow PCM of an arbitrary sample width to int16 little-endian.

    Only WAV files coming back from a TTS service reach this, and they are short,
    so the 24-bit branch is allowed to be a Python loop.
    """
    if sample_width == SAMPLE_WIDTH:
        return pcm
    if sample_width == 1:
        # WAV 8-bit is UNSIGNED; the offset is not optional.
        return b"".join(
            struct.pack("<h", (byte - 128) * 256) for byte in bytearray(pcm)
        )
    if sample_width == 3:
        out = bytearray()
        for offset in range(0, len(pcm) - 2, 3):
            # Keep the two most significant bytes; sign comes along with them.
            out += pcm[offset + 1:offset + 3]
        return bytes(out)
    if sample_width == 4:
        count = len(pcm) // 4
        if count == 0:
            return b""
        values = struct.unpack("<%di" % count, pcm[:count * 4])
        return struct.pack("<%dh" % count, *[value >> 16 for value in values])
    raise RuntimeError(
        "Unsupported WAV sample width: %s bytes. Expected 1, 2, 3 or 4."
        % sample_width
    )


# ---------------------------------------------------------------------------
# Microphone capture
# ---------------------------------------------------------------------------

class MicListener:
    """Always-on capture that segments continuous audio into utterances by
    energy VAD.

    Threading: three threads are involved and the split is deliberate.

    * the **capture thread** does nothing but ``stream.read()`` + RMS + state
      machine, so it can never fall behind PortAudio;
    * the **dispatch thread** calls ``on_utterance`` (typically an HTTP
      transcription) off a queue bounded at 3, dropping the oldest;
    * the **caller's thread** only ever touches :meth:`start`, :meth:`stop`,
      :meth:`mute`, :meth:`unmute` and the two read-only properties.

    ``on_utterance(wav_bytes, seconds)`` and ``on_state(state, detail)`` are both
    invoked on worker threads. **A Qt consumer must marshal to the main thread**
    (this repo's convention is the ``queue.Queue`` + ``QTimer`` pump in
    ``WidgetStreamingMixin``); touching a widget or the MRML scene from here is
    a crash, not a race.

    States passed to ``on_state``: ``"calibrating"``, ``"idle"``, ``"speech"``,
    ``"captured"``, plus ``"muted"`` / ``"unmuted"`` / ``"error"`` / ``"stopped"``
    for UI feedback. Unknown states must be ignored, not asserted on.

    SHARED MUTABLE STATE -- what guards what
    ----------------------------------------

    * ``_thread`` / ``_dispatch_thread`` / ``_stream`` / ``_dispatch_queue`` /
      ``_epoch``: written only under ``_lock``, by :meth:`start` and
      :meth:`stop`. Workers never write them; they receive what they need as
      **call arguments** instead, so a worker can never observe a half-swapped
      session.
    * ``_epoch`` fences work already in flight, on the model of
      ``_guidedSessionEpoch`` in the widget layer. :meth:`start` and
      :meth:`stop` each bump it, and both loops carry the value they were
      started with and exit when it no longer matches. This is what makes
      stop/start correct rather than merely usually-correct: ``stop()`` joins
      with a 2 s timeout, and ``on_utterance`` is an HTTP round trip that
      routinely exceeds it, so a worker from the previous session outliving its
      ``stop()`` is the NORMAL case, not a corner. Without the epoch such a
      worker resumed the moment ``start()`` cleared ``_stop_event`` -- two
      dispatchers on one queue, and the ``stop()`` sentinel it never consumed
      still sitting there to kill the *next* session's dispatch thread on its
      first ``get()``, leaving the microphone permanently deaf with no error
      anywhere. The per-session queue closes the same hole from the other side:
      a stale sentinel now belongs to a queue nobody reads.
    * ``_level`` / ``_threshold`` / ``_floor`` / ``_state``: written by the
      capture thread, read by the properties from any thread. Unguarded **by
      design** -- they are independent floats/strings for a UI meter, a single
      ``STORE_FAST``-to-attribute is atomic under the GIL, and a torn read costs
      one stale meter frame. Do not add a field here that must agree with
      another one; that would need the lock.
    * ``_recalibrate_requested`` / ``_drain_requested``: single-writer
      request flags (caller sets, capture thread clears). Atomic under the GIL;
      a lost race costs one block of latency, never correctness.
    * ``_mute_event`` / ``_stop_event``: :class:`threading.Event`, internally
      locked.
    * The utterance queue is bounded twice over: ``maxsize`` is structural, and
      :meth:`_enqueue_utterance` drops the OLDEST under ``_dispatch_lock`` to
      keep the newest command. See the module docstring for why oldest.
    """

    def __init__(self,
                 on_utterance: Callable[[bytes, float], None],
                 on_state: Optional[Callable[[str, Dict[str, Any]], None]] = None,
                 sample_rate: int = DEFAULT_SAMPLE_RATE,
                 device: Optional[Any] = None,
                 block_ms: int = 30,
                 silence_ms: int = 900,
                 min_speech_ms: int = 350,
                 max_utterance_ms: int = 15000,
                 preroll_ms: int = 300,
                 calibration_ms: int = 800,
                 threshold_multiplier: float = 3.0,
                 min_threshold: float = 0.015,
                 push_to_talk: bool = False) -> None:
        #: When True the energy detector is bypassed entirely: capture runs
        #: between :meth:`begin_talk` and :meth:`end_talk` and nothing else.
        #: The stream stays OPEN either way -- opening a device takes long
        #: enough to swallow the first word, so the key gates accumulation, not
        #: the stream.
        self.push_to_talk = bool(push_to_talk)
        self._on_utterance = on_utterance
        self._on_state = on_state
        self.sample_rate = int(sample_rate)
        self.device = device
        self.block_ms = max(10, int(block_ms))
        self.silence_ms = max(self.block_ms, int(silence_ms))
        self.min_speech_ms = max(0, int(min_speech_ms))
        self.max_utterance_ms = max(self.block_ms, int(max_utterance_ms))
        self.preroll_ms = max(0, int(preroll_ms))
        self.calibration_ms = max(0, int(calibration_ms))
        self.threshold_multiplier = float(threshold_multiplier)
        self.min_threshold = float(min_threshold)

        self._blocksize = max(1, int(self.sample_rate * self.block_ms / 1000.0))
        self._preroll_blocks = max(1, int(round(self.preroll_ms / float(self.block_ms))))
        self._silence_blocks = max(1, int(round(self.silence_ms / float(self.block_ms))))
        self._max_blocks = max(1, int(round(self.max_utterance_ms / float(self.block_ms))))
        self._calibration_blocks = int(round(self.calibration_ms / float(self.block_ms)))

        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._mute_event = threading.Event()
        #: Held down = capturing. An Event because it is set from the Qt main
        #: thread (a key event) and read from the capture thread.
        self._talk_event = threading.Event()
        self._stream = None
        self._thread: Optional[threading.Thread] = None
        self._dispatch_thread: Optional[threading.Thread] = None
        # Created per session in start(), not once per instance: a queue that
        # outlives its session carries that session's stop() sentinel into the
        # next one, where the fresh dispatch thread consumes it and returns
        # immediately -- see the class docstring. None until the first start().
        self._dispatch_queue = None
        self._dispatch_lock = threading.Lock()
        #: Bumped by start() and stop(); workers exit when theirs goes stale.
        self._epoch = 0
        #: Streams whose capture thread would not join in time. Held so CPython
        #: cannot close them from __del__ at an arbitrary later moment, which is
        #: the very "close under a blocking read()" crash stop() avoids.
        self._orphaned_streams: List[Any] = []

        self._recalibrate_requested = False
        self._drain_requested = False

        # VAD state, owned by the capture thread; read (only) by the properties.
        self._level = 0.0
        self._threshold = max(self.min_threshold, 0.0)
        self._floor = 0.0
        self._floor_ceiling = _MAX_TRACKED_FLOOR
        self._state = "stopped"

    # -- lifecycle ---------------------------------------------------------

    def start(self) -> None:
        """Open the input stream and begin capturing.

        Raises :class:`AudioUnavailable` -- with a message naming the fix --
        when there is no backend, no device, or the OS denies the microphone.
        """
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            if queue is None:
                raise AudioUnavailable(
                    "The Python 'queue' module is missing, so audio capture "
                    "cannot be dispatched. This interpreter is broken."
                )
            if not ensure_audio_backend():
                raise AudioUnavailable(audio_backend_error())

            try:
                stream = _sd.RawInputStream(
                    samplerate=self.sample_rate,
                    blocksize=self._blocksize,
                    device=self.device,
                    dtype="int16",
                    channels=CHANNELS,
                )
                stream.start()
            except Exception as exc:
                raise AudioUnavailable(
                    "Could not open the microphone (%s).\n"
                    "Check that a microphone is connected, that it is not in "
                    "use by another application, and that this application is "
                    "allowed to record (Windows: Settings > Privacy > "
                    "Microphone; macOS: System Settings > Privacy & Security > "
                    "Microphone). Voice input stays off until then." % exc
                )

            # A new session: bump the epoch so any worker still running from a
            # previous one retires instead of resuming when _stop_event clears,
            # and give this session its own queue so no stale sentinel reaches
            # it. maxsize is a STRUCTURAL bound on top of the drop-oldest policy
            # in _enqueue_utterance; +1 is the sentinel's own slot, so stop()
            # can always post it even with the queue full of utterances.
            self._epoch += 1
            epoch = self._epoch
            dispatch_queue = queue.Queue(maxsize=_MAX_PENDING_UTTERANCES + 1)
            self._dispatch_queue = dispatch_queue

            self._stream = stream
            self._stop_event.clear()
            self._recalibrate_requested = False
            self._drain_requested = False
            self._level = 0.0
            self._floor = 0.0
            self._threshold = self.min_threshold

            self._dispatch_thread = threading.Thread(
                target=self._dispatch_loop,
                args=(epoch, dispatch_queue),
                name="MicListener-dispatch",
                daemon=True,
            )
            self._dispatch_thread.start()

            self._thread = threading.Thread(
                target=self._capture_loop,
                args=(epoch, stream, dispatch_queue),
                name="MicListener",
                daemon=True,
            )
            self._thread.start()

    def stop(self) -> None:
        """Stop capture. Idempotent, safe from any thread, never raises.

        Also safe on an interpreter-shutdown path, which is why every step is
        individually guarded: by then ``threading`` internals and even the
        logger may already be half torn down.
        """
        try:
            self._stop_event.set()
            with self._lock:
                # Retire this session: a worker that outlives the join below
                # compares its own epoch against this and exits rather than
                # coming back to life when the next start() clears _stop_event.
                self._epoch += 1
                thread = self._thread
                dispatch = self._dispatch_thread
                stream = self._stream
                dispatch_queue = self._dispatch_queue
                self._thread = None
                self._dispatch_thread = None
                self._stream = None
                self._dispatch_queue = None

            # Sentinel ONLY when a dispatch thread was actually running. stop()
            # is idempotent and gets called on every voice toggle and again from
            # onSceneEndClose; posting a sentinel unconditionally left one dead
            # entry per call in a queue nobody drains any more. It is now merely
            # an optimisation -- it wakes the dispatch thread instantly instead
            # of at its next poll -- and it can no longer poison a later session
            # because the queue it lands in is retired with this one.
            if dispatch is not None and dispatch_queue is not None:
                try:
                    dispatch_queue.put_nowait(None)  # sentinel
                except Exception:
                    # Full, or 'queue' itself is missing so queue.Full is not
                    # even nameable. Either way the dispatch thread also polls
                    # _stop_event and its epoch, so this costs promptness, not
                    # termination.
                    pass

            # Join the capture thread BEFORE closing the stream: closing a
            # stream out from under a blocking read() is a native-level crash
            # in some PortAudio host APIs. The read blocks at most one block
            # (~30 ms), so this returns promptly.
            current = None
            try:
                current = threading.current_thread()
            except Exception:
                current = None

            capture_settled = True
            if thread is not None and thread is not current:
                try:
                    thread.join(timeout=2.0)
                    capture_settled = not thread.is_alive()
                except Exception:
                    capture_settled = False

            if stream is not None:
                if capture_settled:
                    for method in ("abort", "close"):
                        try:
                            func = getattr(stream, method, None)
                            if callable(func):
                                func()
                        except Exception:
                            pass
                else:
                    # The join TIMED OUT, so the capture thread may still be
                    # inside stream.read(). Closing now is exactly the crash the
                    # join exists to prevent, and simply dropping the reference
                    # is no better -- CPython would then close it from __del__ at
                    # an arbitrary later moment. Park it instead: a leaked device
                    # handle is recoverable, a native crash mid-procedure is not.
                    try:
                        self._orphaned_streams.append(stream)
                    except Exception:
                        pass
                    try:
                        logger.warning(
                            "Voice: the capture thread did not stop within 2 s; "
                            "leaving the input stream open rather than closing "
                            "it under a blocking read. The microphone stays "
                            "claimed until Slicer restarts."
                        )
                    except Exception:
                        pass

            if dispatch is not None and dispatch is not current:
                try:
                    dispatch.join(timeout=2.0)
                except Exception:
                    pass

            self._emit_state("stopped", {})
        except Exception:
            try:
                logger.debug("MicListener.stop() failed", exc_info=True)
            except Exception:
                pass

    def is_running(self) -> bool:
        thread = self._thread
        return bool(
            thread is not None and thread.is_alive() and not self._stop_event.is_set()
        )

    # -- muting ------------------------------------------------------------

    def mute(self) -> None:
        """Keep the stream open but discard everything it delivers.

        Muting exists because the application speaks: with an always-on
        microphone, hearing our own text-to-speech through the speakers is the
        normal case, not an edge case. Keeping the stream open (rather than
        stopping it) avoids a device re-open per spoken sentence, which on
        Windows costs hundreds of milliseconds and sometimes fails.
        """
        if not self._mute_event.is_set():
            self._mute_event.set()
            self._emit_state("muted", {})

    def unmute(self) -> None:
        """Resume. Drops whatever the driver buffered while muted.

        Without the drain and the pre-roll reset, the tail of our own spoken
        guidance -- captured into the ring buffer microseconds before unmuting --
        would be prepended to the user's next utterance and transcribed as if
        they had said it.
        """
        if self._mute_event.is_set():
            self._mute_event.clear()
            self._drain_requested = True
            self._emit_state("unmuted", {})

    def is_muted(self) -> bool:
        return self._mute_event.is_set()

    # -- push-to-talk ------------------------------------------------------

    def begin_talk(self) -> None:
        """Key down: start accumulating. Safe from the Qt thread, idempotent.

        A no-op unless the listener was built with ``push_to_talk``, so a stray
        key event can never start a capture the energy detector is also driving.
        """
        if self.push_to_talk:
            self._talk_event.set()

    def end_talk(self) -> None:
        """Key up: cut the utterance and send it. Idempotent."""
        self._talk_event.clear()

    def is_talking(self) -> bool:
        return self._talk_event.is_set()

    def recalibrate(self) -> None:
        """Re-measure the ambient floor from scratch on the capture thread."""
        self._recalibrate_requested = True

    # -- observation -------------------------------------------------------

    @property
    def level(self) -> float:
        """Most recent block RMS, 0..1 -- drive a UI meter from this."""
        return self._level

    @property
    def threshold(self) -> float:
        """Current speech threshold, 0..1 (ambient floor x multiplier)."""
        return self._threshold

    @property
    def state(self) -> str:
        """The last state passed to ``on_state``.

        Exposed so a consumer that missed a callback (or attached late) can read
        the current state instead of tracking one of its own; ``_state`` was
        being written on every transition and read by nobody.
        """
        return self._state

    # -- internals ---------------------------------------------------------

    def _emit_state(self, state: str, detail: Optional[Dict[str, Any]] = None) -> None:
        self._state = state
        callback = self._on_state
        if callback is None:
            return
        try:
            callback(state, detail or {})
        except Exception:
            # A raising UI callback must not take the capture thread down with
            # it -- the microphone outliving one bad repaint is the whole point.
            logger.debug("MicListener on_state callback raised", exc_info=True)

    def _enqueue_utterance(self, dispatch_queue: Any,
                           wav_bytes: bytes, seconds: float) -> None:
        """Queue an utterance for the dispatch thread, dropping the oldest.

        Takes the queue as an argument rather than reading ``_dispatch_queue``
        so the capture thread of session N always feeds session N's queue, even
        if stop() has already swapped the attribute out from under it.
        """
        if dispatch_queue is None:
            return
        # Nothing will ever consume this once stop() has run, and the tuple
        # holds a whole utterance's WAV bytes, so enqueueing after the stop
        # flag is set is pure retention of patient-adjacent audio.
        if self._stop_event.is_set():
            return
        with self._dispatch_lock:
            while dispatch_queue.qsize() >= _MAX_PENDING_UTTERANCES:
                try:
                    dropped = dispatch_queue.get_nowait()
                except Exception:
                    break
                if dropped is None:
                    # Never eat the stop sentinel.
                    try:
                        dispatch_queue.put_nowait(None)
                    except Exception:
                        pass
                    break
                dropped_seconds = dropped[1] if isinstance(dropped, tuple) else -1.0
                logger.warning(
                    "Voice: dropping the oldest queued utterance (%.1f s) -- "
                    "transcription is falling behind capture. A stale spoken "
                    "command is worse than a lost one.", dropped_seconds)
                # Through the STATE channel as well, because that is the one
                # that reaches the console trace and the panel. Reported only
                # via logger, this is invisible: the recogniser silently
                # swallows every repeat of a command while the user watches a
                # microphone that looks perfectly healthy, and concludes the
                # feature is unreliable rather than that it is behind.
                self._emit_state("dropped", {
                    "seconds": dropped_seconds,
                    "reason": "transcription is behind capture",
                })
            try:
                dispatch_queue.put_nowait((wav_bytes, seconds))
            except Exception:
                logger.warning(
                    "Voice: could not queue a %.1f s utterance; it is lost. "
                    "Transcription is falling behind capture.", seconds,
                    exc_info=True,
                )
                self._emit_state("dropped", {
                    "seconds": seconds,
                    "reason": "the queue would not accept it",
                })

    def _dispatch_loop(self, epoch: int, dispatch_queue: Any) -> None:
        empty_exc = getattr(queue, "Empty", Exception) if queue is not None else Exception
        while not self._stop_event.is_set() and epoch == self._epoch:
            try:
                # Timed, not blocking: the sentinel is the fast path, but it can
                # be lost to a full queue, and a thread parked forever on get()
                # would then leak one per stop().
                item = dispatch_queue.get(timeout=0.25)
            except empty_exc:
                continue  # Empty -> re-test the stop flag and the epoch
            except Exception:
                # Not "nothing to do" but a broken queue: spinning at 4 Hz on it
                # forever would hide a real fault, so retire this dispatcher.
                logger.warning(
                    "Voice: utterance queue failed; transcription dispatch is "
                    "stopping. Toggle voice off and on to recover.",
                    exc_info=True,
                )
                return
            if item is None:
                return
            if self._stop_event.is_set() or epoch != self._epoch:
                continue
            wav_bytes, seconds = item
            try:
                self._on_utterance(wav_bytes, seconds)
            except Exception as exc:
                # Swallowing this at debug level made a failed transcription
                # indistinguishable from silence: the surgeon speaks, the panel
                # does nothing, and the only trace is a log nobody has open. The
                # utterance is genuinely gone (re-running it would replay a stale
                # command), so the honest response is to say so.
                logger.warning(
                    "Voice: handling a %.1f s utterance raised %s: %s",
                    seconds, type(exc).__name__, exc, exc_info=True,
                )
                self._emit_state("error", {
                    "error": str(exc),
                    "stage": "on_utterance",
                    "seconds": seconds,
                    "remedy": "That utterance could not be processed. Please say "
                              "it again, or type the request instead.",
                })

    def _drain_stream(self, stream: Any) -> None:
        if stream is None:
            return
        try:
            available = int(getattr(stream, "read_available", 0) or 0)
            if available > 0:
                stream.read(available)
        except Exception:
            logger.debug("Could not drain buffered input", exc_info=True)

    def _apply_threshold(self) -> None:
        self._threshold = max(self.min_threshold, self._floor * self.threshold_multiplier)

    def _capture_loop(self, epoch: int, stream: Any, dispatch_queue: Any) -> None:
        preroll = deque(maxlen=self._preroll_blocks)
        calibration_samples: List[float] = []
        calibration_rounds = 0
        # Push-to-talk needs no room measurement -- the key decides what is
        # speech. Skipping it also means the microphone is usable the instant it
        # is armed, instead of a second (or four, if the device is slow to wake)
        # later, which matters when the user's next move is to hold the key.
        calibrating = not self.push_to_talk
        in_speech = False
        frames: List[bytes] = []
        preroll_len = 0
        speech_blocks = 0
        silence_run = 0
        last_voiced_offset = 0
        unreadable_blocks = 0

        self._emit_state("calibrating", {"ms": self.calibration_ms})

        # The stream and the queue arrive as arguments, so this loop cannot be
        # made to read a *later* session's objects by a concurrent start().
        while not self._stop_event.is_set() and epoch == self._epoch:
            if self._drain_requested:
                self._drain_requested = False
                self._drain_stream(stream)
                preroll.clear()
                in_speech = False
                frames = []
                silence_run = 0

            if self._recalibrate_requested:
                self._recalibrate_requested = False
                calibrating = True
                calibration_samples = []
                in_speech = False
                frames = []
                self._emit_state("calibrating", {"ms": self.calibration_ms})

            if stream is None:
                break
            try:
                data, overflowed = stream.read(self._blocksize)
            except Exception as exc:
                if self._stop_event.is_set():
                    break
                logger.warning("Microphone read failed: %s", exc)
                self._emit_state("error", {
                    "error": str(exc),
                    "remedy": "The microphone stopped responding. Unplugging a "
                              "USB device does this. Toggle voice off and on to "
                              "reopen it.",
                })
                # Tear the stream down rather than spinning on a dead device.
                try:
                    self.stop()
                except Exception:
                    pass
                return
            if overflowed:
                logger.debug("Microphone input overflow (a block was dropped)")

            try:
                block = bytes(data)
                unreadable_blocks = 0
            except Exception as exc:
                # A bare `continue` here spun this loop forever, silently, if the
                # backend ever handed back something unconvertible -- a dead
                # microphone that still looks alive. Say so once, then treat a
                # sustained run of them as a device failure like a read error.
                unreadable_blocks += 1
                if unreadable_blocks == 1:
                    logger.warning(
                        "Voice: microphone delivered an unusable block (%s: %s)",
                        type(exc).__name__, exc, exc_info=True,
                    )
                if unreadable_blocks >= self._silence_blocks:
                    self._emit_state("error", {
                        "error": str(exc),
                        "remedy": "The microphone is delivering unreadable "
                                  "audio. Toggle voice off and on to reopen it.",
                    })
                    try:
                        self.stop()
                    except Exception:
                        pass
                    return
                continue
            rms = pcm_rms(block)

            if self._mute_event.is_set():
                # Report silence, not what we hear: while muted the mic is deaf
                # by policy, and the level drives a UI meter. Leaving the real
                # RMS here made the meter dance to our OWN text-to-speech coming
                # back through the speakers, which reads as "it is listening".
                self._level = 0.0
                # Read and throw away; reset the VAD so speech straddling a
                # mute boundary is never stitched into one utterance.
                if in_speech:
                    in_speech = False
                    frames = []
                    self._emit_state("idle", {"reason": "muted"})
                preroll.clear()
                continue

            self._level = rms

            if self.push_to_talk:
                # PUSH-TO-TALK. The key IS the detector: everything between
                # press and release is the utterance, no threshold involved.
                # That removes the whole class of failure the energy detector
                # has on a quiet microphone -- a sentence chopped at a pause,
                # or never triggered at all -- because the user has said, with a
                # key, exactly where their sentence begins and ends.
                talking = self._talk_event.is_set()
                if talking:
                    if not in_speech:
                        in_speech = True
                        # Keep the pre-roll: a person starts speaking a moment
                        # before, or as, the key goes down, and the first
                        # phoneme is the one a recogniser can least afford.
                        frames = list(preroll)
                        preroll_len = len(frames)
                        speech_blocks = 0
                        self._emit_state("speech", {"level": rms, "ptt": True})
                    frames.append(block)
                    speech_blocks += 1
                    last_voiced_offset = speech_blocks
                    if speech_blocks >= self._max_blocks:
                        self._finish_utterance(dispatch_queue, frames, preroll_len,
                                               last_voiced_offset, forced=True)
                        in_speech = False
                        frames = []
                        preroll.clear()
                elif in_speech:
                    self._finish_utterance(dispatch_queue, frames, preroll_len,
                                           last_voiced_offset, forced=False)
                    in_speech = False
                    frames = []
                    preroll.clear()
                else:
                    preroll.append(block)
                continue

            if calibrating:
                calibration_samples.append(rms)
                if len(calibration_samples) >= max(1, self._calibration_blocks):
                    ordered = sorted(calibration_samples)
                    # Median, not mean: one cough during calibration would
                    # otherwise set a threshold nothing can cross.
                    measured = ordered[len(ordered) // 2]

                    # A floor of (near) zero does not mean a silent room. It
                    # means the device has not produced a sample yet -- and
                    # accepting it is worse than useless, because the derived
                    # threshold collapses to min_threshold, which may sit BELOW
                    # the real ambient level. The detector then reports speech
                    # forever and every utterance is a forced 15-second cut.
                    if measured <= _MIN_VALID_FLOOR and calibration_rounds < _MAX_CALIBRATION_ROUNDS:
                        calibration_rounds += 1
                        del calibration_samples[:]
                        self._emit_state("calibrating", {
                            "round": calibration_rounds,
                            "reason": "no signal from the device yet",
                        })
                        continue

                    if measured <= _MIN_VALID_FLOOR:
                        self._floor = 0.0
                        self._threshold = max(self.min_threshold, _FALLBACK_THRESHOLD)
                        logger.warning(
                            "Voice: the input device produced no signal during "
                            "%d calibration rounds; using an absolute threshold "
                            "of %.4f. If speech is not detected, check that the "
                            "selected microphone is the one you are speaking "
                            "into and that the OS is not muting it.",
                            calibration_rounds + 1, self._threshold)
                    else:
                        self._floor = measured
                        self._apply_threshold()
                    self._floor_ceiling = min(
                        _MAX_TRACKED_FLOOR, max(self.min_threshold, self._floor * 4.0)
                    )
                    calibrating = False
                    self._emit_state("idle", {
                        "floor": self._floor,
                        "threshold": self._threshold,
                        "rounds": calibration_rounds + 1,
                    })
                continue

            # HYSTERESIS. A block has to beat the full threshold to START
            # speech, but only a fraction of it to CONTINUE. Using one level for
            # both is the defect that chops a sentence into fragments: real
            # speech is 1.2-2x the threshold on a quiet microphone, and its
            # natural dips -- the gap between words, an unvoiced consonant, the
            # tail of a vowel -- fall under it constantly. The silence timer
            # then fires mid-phrase, and each fragment reaches the recogniser
            # too partial to be recognised, which reads as "the microphone works
            # but nothing is ever transcribed".
            voiced = rms > (self._threshold * _SPEECH_EXIT_RATIO
                            if in_speech else self._threshold)

            if not in_speech:
                if voiced:
                    in_speech = True
                    frames = list(preroll)
                    preroll_len = len(frames)
                    frames.append(block)
                    speech_blocks = 1
                    last_voiced_offset = 1
                    silence_run = 0
                    self._emit_state("speech", {"level": rms})
                else:
                    preroll.append(block)
                    # Adaptive floor: track the ambient level only while idle and
                    # only from sub-threshold blocks, and clamp it, so a fan
                    # starting up re-tunes the threshold while a long monologue
                    # cannot ratchet the microphone deaf.
                    self._floor = (
                        (1.0 - _FLOOR_EMA_ALPHA) * self._floor + _FLOOR_EMA_ALPHA * rms
                    )
                    if self._floor > self._floor_ceiling:
                        self._floor = self._floor_ceiling
                    if self._floor < 0.0:
                        self._floor = 0.0
                    self._apply_threshold()
                continue

            # --- in speech ---
            frames.append(block)
            speech_blocks += 1
            if voiced:
                silence_run = 0
                last_voiced_offset = speech_blocks
            else:
                silence_run += 1

            forced = speech_blocks >= self._max_blocks
            if silence_run >= self._silence_blocks or forced:
                speech_ms = self._finish_utterance(
                    dispatch_queue, frames, preroll_len, last_voiced_offset, forced)
                in_speech = False
                frames = []
                silence_run = 0
                preroll.clear()

                # A forced cut in which speech never once dropped out is not a
                # long sentence -- it is a threshold sitting under the room. The
                # adaptive floor cannot fix it, because it only tracks ambient
                # while IDLE and this state never returns to idle. Re-measure.
                if forced and speech_ms >= self.max_utterance_ms * _SATURATED_SPEECH_RATIO:
                    logger.warning(
                        "Voice: the detector never went quiet during a %.1f s "
                        "capture (threshold %.4f). Re-measuring the room.",
                        speech_ms / 1000.0, self._threshold)
                    calibrating = True
                    calibration_rounds = 0
                    del calibration_samples[:]
                    self._emit_state("calibrating", {
                        "reason": "threshold below the room noise",
                    })
                    continue

                self._emit_state("idle", {"threshold": self._threshold})

        # Falling out of the loop means stop() is in progress; it owns teardown.

    def _finish_utterance(self, dispatch_queue: Any, frames: List[bytes],
                          preroll_len: int, last_voiced_offset: int,
                          forced: bool) -> float:
        """Trim, level, encode and queue one utterance. Returns its speech ms.

        Shared by both capture modes. In push-to-talk ``last_voiced_offset`` is
        simply every block held, so the trim keeps the whole clip; in the
        energy-detector mode it is the last block that was above threshold, so
        the trailing silence that ended the utterance is cut off (plus a short
        pad, because a recogniser wants the final consonant).
        """
        keep = min(len(frames), preroll_len + last_voiced_offset + _TAIL_PAD_BLOCKS)
        payload = b"".join(frames[:keep])
        speech_ms = last_voiced_offset * self.block_ms

        if speech_ms < self.min_speech_ms:
            # A click, a cough, a chair -- or a key tapped rather than held.
            # Discarded silently: surfacing it would make the panel flicker all
            # day in a busy theatre.
            self._emit_state("idle", {"discarded": True, "speech_ms": speech_ms})
            return speech_ms

        seconds = len(payload) / float(self.sample_rate * SAMPLE_WIDTH * CHANNELS)
        raw_peak = pcm_peak(payload)
        raw_rms = pcm_rms(payload)
        payload, gain = normalize_gain(payload)
        try:
            wav_bytes = encode_wav(payload, self.sample_rate, CHANNELS, SAMPLE_WIDTH)
        except Exception:
            logger.debug("Could not encode utterance", exc_info=True)
            self._emit_state("idle", {"discarded": True, "reason": "encode_failed"})
            return speech_ms

        self._emit_state("captured", {
            "seconds": seconds,
            "speech_ms": speech_ms,
            "forced": forced,
            # Level of the clip AS CAPTURED. An empty transcript with a peak of
            # 0.04 is a microphone problem; the same transcript with a peak of
            # 0.6 is not, and the two need opposite remedies.
            "peak": raw_peak,
            "rms": raw_rms,
            "gain": gain,
            "ptt": bool(self.push_to_talk),
        })
        self._dump_utterance(wav_bytes, seconds)
        self._enqueue_utterance(dispatch_queue, wav_bytes, seconds)
        return speech_ms

    def _dump_utterance(self, wav_bytes: bytes, seconds: float) -> None:
        """Opt-in debug persistence of a captured utterance.

        Off unless ``SLICER_AGENT_VOICE_DUMP`` names a directory: audio of a
        surgeon in theatre is patient-adjacent data and is never written by
        default. Fail-soft throughout -- a logging failure must never abort the
        capture it is logging.

        This is the one thing on the capture thread that is not read+RMS+state,
        and it is deliberate: with the variable unset (every clinical install)
        the cost is a single ``os.environ.get``, so the real-time contract in
        the class docstring holds in production. Turning the dump ON knowingly
        trades capture latency for evidence, which is what a debugging switch is
        for; do not promote it to a default.

        ``RunLog`` is imported lazily, inside the function, for two reasons: it
        keeps this module importable on its own (rule 1 in the module
        docstring), and it keeps the dependency off the default path entirely,
        since the import cannot even be attempted unless the switch is set. Its
        writers are fail-soft by contract and every call here is additionally
        wrapped, so neither a missing RunLog nor a full disk can propagate.
        """
        target = os.environ.get(_DUMP_ENV_VAR, "")
        if not target:
            return
        try:
            from SlicerAIAgentLib import RunLog  # lazy: keeps this module standalone
        except Exception:
            logger.debug("RunLog unavailable; skipping utterance dump", exc_info=True)
            return
        try:
            directory = RunLog.ensure_dir(target)
            stamp = time.strftime("%Y%m%d_%H%M%S") + "_%03d" % int((time.time() % 1) * 1000)
            wav_path = os.path.join(directory, "utterance_%s.wav" % stamp)
            with open(wav_path, "wb") as handle:
                handle.write(wav_bytes)
            RunLog.write_json(
                os.path.join(directory, "utterance_%s.json" % stamp),
                {
                    "seconds": round(seconds, 3),
                    "sample_rate": self.sample_rate,
                    "channels": CHANNELS,
                    "sample_width": SAMPLE_WIDTH,
                    "threshold": round(self._threshold, 5),
                    "floor": round(self._floor, 5),
                    "bytes": len(wav_bytes),
                },
            )
        except Exception:
            logger.debug("Could not dump utterance", exc_info=True)


# ---------------------------------------------------------------------------
# Playback
# ---------------------------------------------------------------------------

#: Decoders we will USE if already installed, in preference order. We never
#: install any of them: pulling a media stack (and, for pydub, ffmpeg) onto a
#: hospital workstation behind the user's back is not a reasonable price for
#: spoken guidance that the panel also shows as text.
_OPTIONAL_DECODERS = ("soundfile", "miniaudio", "pydub")

_decoder_lock = threading.Lock()
_decoder_name: Optional[str] = None
_decoder_probed = False
_logged_reasons = set()


def _log_once(key: str, message: str, *args: Any) -> None:
    """Log a degradation reason once per session rather than per utterance.

    ``_logged_reasons`` is touched from the playback thread and the caller's
    thread with no lock, and that is fine but not accidental: ``set.add`` is
    atomic under the GIL, so the set cannot corrupt, and the check-then-add race
    costs at most one duplicate log line. A lock here would be a lock taken on
    every degraded playback to protect a cosmetic property.
    """
    if key in _logged_reasons:
        return
    _logged_reasons.add(key)
    logger.warning(message, *args)


def _find_decoder() -> Optional[str]:
    """Name of the first importable optional decoder, or None. Cached."""
    global _decoder_name, _decoder_probed
    with _decoder_lock:
        if _decoder_probed:
            return _decoder_name
        _decoder_probed = True
        for name in _OPTIONAL_DECODERS:
            try:
                __import__(name)
                _decoder_name = name
                break
            except Exception:
                continue
        return _decoder_name


def _normalize_format(audio_format: str) -> str:
    fmt = (audio_format or "").strip().lower()
    if not fmt:
        return ""
    if "/" in fmt:  # a MIME type
        fmt = fmt.split("/")[-1]
    fmt = fmt.lstrip(".")
    aliases = {
        "mpeg": "mp3",
        "mpga": "mp3",
        "x-wav": "wav",
        "wave": "wav",
        "vnd.wave": "wav",
        "x-m4a": "m4a",
        "mp4": "m4a",
        "vorbis": "ogg",
    }
    return aliases.get(fmt, fmt)


def _sniff_format(data: bytes, audio_format: str = "") -> str:
    """Magic bytes first, the caller's hint second.

    The hint comes from an HTTP ``Content-Type`` or a config string, and TTS
    services have been known to label an MP3 as ``audio/wav``. The bytes have
    not been known to lie.
    """
    head = data[:16] if data else b""
    if len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return "wav"
    if head[:4] == b"OggS":
        return "ogg"
    if head[:4] == b"fLaC":
        return "flac"
    if head[:3] == b"ID3":
        return "mp3"
    if len(head) >= 2 and head[0] == 0xFF and (head[1] & 0xE0) == 0xE0:
        return "mp3"
    if len(head) >= 8 and head[4:8] == b"ftyp":
        return "m4a"
    return _normalize_format(audio_format)


class AudioPlayer:
    """Plays synthesized speech.

    Format support is deliberately narrow. **WAV always works** when the audio
    backend is present: it is decoded with the stdlib :mod:`wave` module and
    written to PortAudio as int16, so the spoken-guidance path needs no codec
    wheel and cannot break on a machine without ffmpeg. Anything else (mp3, ogg,
    m4a) plays only if ``soundfile``, ``miniaudio`` or ``pydub`` *happens to be*
    installed; we will not install one. When it is not, :meth:`play` returns
    False and sets :attr:`last_error`, and the caller degrades to "the panel
    still shows the text" -- which is the correct outcome, since the text was
    always the primary channel and the speech is an affordance.

    ``on_finished(ok)`` runs on the playback thread. **A Qt caller must marshal
    it to the main thread.** It is not called at all after :meth:`stop`.
    """

    def __init__(self, device: Optional[Any] = None) -> None:
        self._device = device
        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._stream = None
        self._temp_path: Optional[str] = None
        self._winsound_active = False
        #: Human-readable reason the last :meth:`play` returned False; "" when fine.
        self.last_error = ""

    # -- capability --------------------------------------------------------

    @staticmethod
    def can_play(audio_format: str) -> bool:
        """Whether this process can decode ``audio_format``.

        Best effort: for the optional decoders it reports that *a* decoder is
        importable, not that it handles this particular codec (pydub, for one,
        still needs ffmpeg on the PATH for mp3). WAV is the only guarantee.
        """
        fmt = _normalize_format(audio_format)
        if not fmt or fmt == "wav":
            return True
        return _find_decoder() is not None

    @staticmethod
    def supported_formats() -> List[str]:
        """Formats :meth:`play` will attempt, most-certain first."""
        formats = ["wav"]
        if _find_decoder() is not None:
            formats.extend(["mp3", "ogg", "flac", "m4a", "aac", "opus"])
        return formats

    # -- playback ----------------------------------------------------------

    def play(self,
             data: bytes,
             audio_format: str = "",
             blocking: bool = False,
             on_finished: Optional[Callable[[bool], None]] = None) -> bool:
        """Play ``data``. Returns False (with :attr:`last_error` set) rather
        than raising when the format or the backend is unavailable.

        Any playback already in flight is cut first: a new step opening must be
        able to interrupt the previous step's spoken guidance (barge-in).
        """
        self.last_error = ""
        if not data:
            self.last_error = "No audio data to play."
            return False

        self.stop()

        fmt = _sniff_format(data, audio_format)
        try:
            pcm, rate, channels = self._decode(data, fmt)
        except AudioUnavailable as exc:
            self.last_error = str(exc)
            _log_once("decode_%s" % fmt, "Voice playback unavailable: %s", exc)
            return False
        except Exception as exc:
            text = str(exc)
            # decode_wav already produces a full sentence; do not wrap it again.
            self.last_error = text if text.startswith("Could not decode") else (
                "Could not decode %s audio: %s" % (fmt or "unknown", text))
            _log_once("decode_err_%s" % fmt, "Voice playback: %s", self.last_error)
            return False

        if not pcm:
            self.last_error = "Decoded audio was empty."
            return False

        if ensure_audio_backend(auto_install=False):
            return self._play_stream(pcm, rate, channels, blocking, on_finished)

        # No PortAudio. On Windows the stdlib can still play a WAV *file*, which
        # keeps spoken guidance working on the most common install. We already
        # hold decoded PCM, so re-wrapping it as WAV makes even an mp3 (decoded
        # by an optional package) reachable through this path.
        encode_error = ""
        try:
            wav_bytes = encode_wav(pcm, rate, channels, SAMPLE_WIDTH)
        except Exception as exc:
            # Keep the real reason. Falling through to audio_backend_error()
            # would have told the user to pip-install sounddevice when what
            # actually failed was wrapping PCM we already hold -- sending them
            # after the wrong remedy for a bug on our side.
            wav_bytes = b""
            encode_error = str(exc)
            logger.warning("Voice: could not re-wrap decoded audio as WAV: %s", exc)
        if wav_bytes and self._play_winsound(
                wav_bytes, pcm, rate, channels, blocking, on_finished):
            return True

        if encode_error:
            self.last_error = encode_error
            _log_once("wav_rewrap_failed", "Voice playback: %s", encode_error)
            return False

        self.last_error = audio_backend_error()
        _log_once("no_backend_playback", "Voice playback unavailable: %s", self.last_error)
        return False

    def stop(self) -> None:
        """Cut playback immediately and suppress ``on_finished``.

        Used for barge-in, so it must not wait for the current buffer to drain:
        ``abort()`` discards what PortAudio has already queued, where ``stop()``
        would play it out.
        """
        try:
            self._stop_event.set()
            with self._lock:
                thread = self._thread
                self._thread = None
                self._winsound_active = False

            # Deliberately NOT abort()/close() here. The playback thread may be
            # sitting inside a blocking stream.write(), and closing a PortAudio
            # stream out from under a blocking call is a native-level crash on
            # some host APIs -- the same hazard MicListener.stop() joins the
            # capture thread to avoid. The write loop checks _stop_event every
            # ~100 ms chunk, and _stream_run's own finally aborts and closes the
            # stream on the thread that owns it. All this has to do is ask.
            self._stop_winsound()

            current = None
            try:
                current = threading.current_thread()
            except Exception:
                current = None
            if thread is not None and thread is not current:
                try:
                    thread.join(timeout=2.0)
                except Exception:
                    pass

            self._cleanup_temp()
        except Exception:
            try:
                logger.debug("AudioPlayer.stop() failed", exc_info=True)
            except Exception:
                pass

    def is_playing(self) -> bool:
        thread = self._thread
        if thread is not None and thread.is_alive():
            return True
        return bool(self._winsound_active)

    # -- decoding ----------------------------------------------------------

    def _decode(self, data: bytes, fmt: str) -> Tuple[bytes, int, int]:
        """Return ``(int16 pcm, sample_rate, channels)``."""
        if fmt == "wav" or (not fmt and data[:4] == b"RIFF"):
            pcm, rate, channels, width = decode_wav(data)
            return (_pcm_to_int16(pcm, width), rate, channels)

        decoder = _find_decoder()
        if decoder is None:
            raise AudioUnavailable(
                "This audio is '%s', and no decoder for it is installed. WAV "
                "plays with no extra package; for other formats install one of "
                "%s into Slicer's Python, or configure the speech service to "
                "return WAV. The guidance text is still shown in the panel."
                % (fmt or "unknown", ", ".join(_OPTIONAL_DECODERS))
            )
        if decoder == "soundfile":
            return self._decode_soundfile(data)
        if decoder == "miniaudio":
            return self._decode_miniaudio(data)
        return self._decode_pydub(data, fmt)

    def _decode_soundfile(self, data: bytes) -> Tuple[bytes, int, int]:
        import soundfile  # type: ignore
        samples, rate = soundfile.read(io.BytesIO(data), dtype="int16", always_2d=True)
        channels = int(samples.shape[1]) if samples.ndim > 1 else 1
        return (samples.tobytes(), int(rate), channels)

    def _decode_miniaudio(self, data: bytes) -> Tuple[bytes, int, int]:
        import miniaudio  # type: ignore
        decoded = miniaudio.decode(data)
        pcm = decoded.samples.tobytes()
        return (pcm, int(decoded.sample_rate), int(decoded.nchannels))

    def _decode_pydub(self, data: bytes, fmt: str) -> Tuple[bytes, int, int]:
        from pydub import AudioSegment  # type: ignore
        segment = AudioSegment.from_file(io.BytesIO(data), format=fmt or None)
        segment = segment.set_sample_width(SAMPLE_WIDTH)
        return (segment.raw_data, int(segment.frame_rate), int(segment.channels))

    # -- transports --------------------------------------------------------

    def _play_stream(self,
                     pcm: bytes,
                     rate: int,
                     channels: int,
                     blocking: bool,
                     on_finished: Optional[Callable[[bool], None]]) -> bool:
        frame_bytes = max(1, channels * SAMPLE_WIDTH)
        usable = (len(pcm) // frame_bytes) * frame_bytes
        payload = pcm[:usable]
        if not payload:
            self.last_error = "Decoded audio contained no complete frames."
            return False

        self._stop_event.clear()

        if blocking:
            # Register the CALLING thread as the playback thread. Without this
            # a blocking play is invisible to stop(), which then has nothing to
            # join and no way to know whether the writer has settled -- and the
            # next play() would clear _stop_event while the previous writer was
            # still in its loop.
            try:
                own = threading.current_thread()
            except Exception:
                own = None
            with self._lock:
                self._thread = own
            try:
                return self._stream_run(payload, rate, channels, frame_bytes, on_finished)
            finally:
                with self._lock:
                    if self._thread is own:
                        self._thread = None

        thread = threading.Thread(
            target=self._stream_run,
            args=(payload, rate, channels, frame_bytes, on_finished),
            name="AudioPlayer",
            daemon=True,
        )
        with self._lock:
            self._thread = thread
        thread.start()
        return True

    def _stream_run(self,
                    payload: bytes,
                    rate: int,
                    channels: int,
                    frame_bytes: int,
                    on_finished: Optional[Callable[[bool], None]]) -> bool:
        ok = False
        stream = None
        try:
            stream = _sd.RawOutputStream(
                samplerate=int(rate),
                channels=int(channels),
                dtype="int16",
                device=self._device,
            )
            stream.start()
            with self._lock:
                self._stream = stream
            # ~100 ms per write: small enough that stop() cuts within a
            # perceptual instant, large enough not to thrash the GIL.
            chunk = max(frame_bytes, int(rate * 0.1) * frame_bytes)
            offset = 0
            total = len(payload)
            while offset < total:
                if self._stop_event.is_set():
                    return False
                stream.write(payload[offset:offset + chunk])
                offset += chunk
            ok = not self._stop_event.is_set()
        except Exception as exc:
            self.last_error = "Playback failed: %s" % exc
            _log_once("playback_failed", "Voice playback failed: %s", exc)
            ok = False
        finally:
            if stream is not None:
                try:
                    if self._stop_event.is_set():
                        stream.abort()
                    else:
                        stream.stop()
                except Exception:
                    pass
                try:
                    stream.close()
                except Exception:
                    pass
            with self._lock:
                if self._stream is stream:
                    self._stream = None

        if on_finished is not None and not self._stop_event.is_set():
            try:
                on_finished(ok)
            except Exception:
                logger.debug("AudioPlayer on_finished callback raised", exc_info=True)
        return ok

    def _play_winsound(self,
                       wav_bytes: bytes,
                       pcm: bytes,
                       rate: int,
                       channels: int,
                       blocking: bool,
                       on_finished: Optional[Callable[[bool], None]]) -> bool:
        """Windows-only stdlib fallback when PortAudio is missing."""
        try:
            import winsound  # type: ignore  (Windows only)
        except Exception:
            return False

        try:
            handle, path = tempfile.mkstemp(prefix="slicer_voice_", suffix=".wav")
            try:
                os.write(handle, wav_bytes)
            finally:
                os.close(handle)
        except Exception as exc:
            self.last_error = "Could not stage audio for playback: %s" % exc
            return False

        self._stop_event.clear()
        with self._lock:
            self._temp_path = path
            self._winsound_active = True

        flags = winsound.SND_FILENAME
        if not blocking:
            flags |= winsound.SND_ASYNC
        try:
            winsound.PlaySound(path, flags)
        except Exception as exc:
            self.last_error = "Windows playback failed: %s" % exc
            self._winsound_active = False
            self._cleanup_temp()
            return False

        duration = len(pcm) / float(max(1, rate) * SAMPLE_WIDTH * max(1, channels))
        if blocking:
            self._winsound_active = False
            self._cleanup_temp()
            if on_finished is not None and not self._stop_event.is_set():
                try:
                    on_finished(True)
                except Exception:
                    logger.debug("AudioPlayer on_finished callback raised", exc_info=True)
            return True

        # winsound gives no completion signal, so time it: the duration is known
        # exactly from the PCM length, and stop() short-circuits the wait.
        def _await_end() -> None:
            interrupted = True
            try:
                interrupted = self._stop_event.wait(timeout=duration + 0.05)
            finally:
                # The temp file holds decoded speech audio, so it is removed on
                # EVERY exit from this thread, not just the happy one. Anything
                # escaping the wait would otherwise leave it on disk until the
                # OS cleaned /tmp -- audio outliving the session that made it.
                with self._lock:
                    self._winsound_active = False
                self._cleanup_temp()
            if on_finished is not None and not interrupted:
                try:
                    on_finished(True)
                except Exception:
                    logger.debug("AudioPlayer on_finished callback raised", exc_info=True)

        thread = threading.Thread(target=_await_end, name="AudioPlayer-winsound", daemon=True)
        with self._lock:
            self._thread = thread
        thread.start()
        return True

    def _stop_winsound(self) -> None:
        try:
            import winsound  # type: ignore
        except Exception:
            return
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass

    def _cleanup_temp(self) -> None:
        with self._lock:
            path = self._temp_path
            self._temp_path = None
        if not path:
            return
        try:
            os.remove(path)
        except Exception:
            logger.debug("Could not remove temp audio file %s", path, exc_info=True)
