"""Spoken output for guided workflows, via Alibaba Cloud Model Studio (DashScope).

WHY THIS EXISTS
---------------
A surgeon driving a guided workflow is looking at the 3D view and holding a
mouse, not reading a panel. Speaking a step's guidance is the only channel that
does not require their eyes. This is the *only* speech-output path in the
feature -- the user chose cloud Qwen TTS deliberately -- so when it cannot
speak, it must say why in words that name a remedy. Every failure here is a
degradation of a convenience, never of the procedure: the caller is expected to
carry on silently, so this module raises ``RuntimeError`` with a human-readable
message and never takes the application down with it.

WHY urllib AND NOT httpx
------------------------
Same reason as ``SlicerAIAgentLib/llm_client/transport.py``: ``httpx`` is listed
in requirements.txt but imported by no project code and unproven inside
Slicer's Python. The transport shape here (build request -> open with timeout ->
retry ladder) is deliberately a copy of that module's, so there is one HTTP
idiom in the repo rather than two.

WHAT THE API ACTUALLY RETURNS (verified 2026-08, docs read in full)
-------------------------------------------------------------------
Endpoint family (same native multimodal-generation endpoint as ASR)::

    POST <region>/api/v1/services/aigc/multimodal-generation/generation
    {"model": "qwen3-tts-flash",
     "input": {"text": "...", "voice": "Cherry", "language_type": "English"}}

Reference: https://www.alibabacloud.com/help/en/model-studio/qwen-tts-api
Guide:     https://www.alibabacloud.com/help/en/model-studio/qwen-tts
Voices:    https://www.alibabacloud.com/help/en/model-studio/qwen-tts-voice-list

Two findings that shaped this file:

1. **The audio comes back as a URL, not inline.** In non-streaming mode the
   documented response is ``{"output": {"audio": {"data": "", "url": "http://
   dashscope-result-...oss-...aliyuncs.com/...", "id": "...", "expires_at":
   ...}}}`` -- ``data`` is an *empty string* and the bytes must be fetched with a
   second, plain, unauthenticated GET. That URL is time-limited (the guide says
   the file is valid for 24 hours), so it is fetched immediately and never
   stored. Streaming mode does return inline base64, so both shapes are handled:
   non-empty ``data`` wins, otherwise the URL is fetched.

2. **There is NO documented way to request a container or sample rate.** The API
   reference lists exactly five keys under ``input`` -- ``text``, ``voice``,
   ``language_type``, ``instructions``, ``optimize_instructions`` -- and no
   ``format`` / ``sample_rate`` anywhere, in ``input`` or ``parameters``; the
   response's ``audio`` object carries no ``content_type``, ``sample_rate``,
   ``channels`` or ``duration`` either. (Other DashScope TTS families --
   CosyVoice, the realtime WebSocket API -- *do* take ``format``/``sample_rate``
   under ``input``, which is where the third-party claims that they work here
   come from. They are not documented for this model.) The documented response
   example points at a ``.wav`` file, and the streaming guide describes PCM at
   24 kHz, so WAV is the expectation -- but an undocumented parameter sent to
   this endpoint would be a guess that fails as an opaque 400. So we send none
   and **sniff the returned bytes instead**, reporting the container in
   ``SpeechResult.audio_format``. Callers that can only decode WAV (the stdlib
   ``wave`` module, which is the whole reason WAV matters -- MP3 would need a
   codec wheel) must check that field rather than assume. If Alibaba later
   documents a format parameter, add it here and default it to ``"wav"``.

Qt-free and Slicer-free at import time: this module is plain stdlib so it can be
exercised in a bare CPython 3.7 interpreter outside Slicer.
"""

from __future__ import annotations

import base64
import collections
import json
import logging
import os
import socket
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Service constants
# ---------------------------------------------------------------------------

#: The same three regional hosts the ASR path uses. A DashScope API key is
#: issued *per region*, so a key that works against one host returns 401 on
#: another -- which is why the endpoint is a first-class setting and why the 401
#: message below names the region rather than only blaming the key.
ENDPOINTS = {
    "intl": "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
    "cn": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
    "us": "https://dashscope-us.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
}

DEFAULT_ENDPOINT = "https://dashscope-us.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
DEFAULT_MODEL = "qwen3-tts-flash"

#: Deliberately SHORT. The API reference documents exactly one voice by example
#: -- "Cherry" -- and the separate voice-list page enumerates roughly fifty,
#: including dialect voices whose identifiers contain spaces and hyphens
#: ("Beijing - Dylan"). Shipping a long transcribed list would be asserting
#: something this file cannot verify, and a wrong identifier is a 400 at the
#: moment the surgeon expects speech. So: the confirmed one first, a few
#: well-known siblings after it, and the UI combo must be **editable** so any
#: other documented voice can simply be typed in.
VOICES: List[str] = [
    "Cherry",   # the only voice in the API reference's own request example
    "Serena",
    "Ethan",
    "Chelsie",
]

#: Verbatim from the API reference. "Auto" is the documented default and is the
#: right choice for this feature: guidance text is English but node names,
#: segment names and the surgeon's own wording may not be.
LANGUAGE_TYPES: List[str] = [
    "Auto",
    "Chinese",
    "English",
    "German",
    "Italian",
    "Portuguese",
    "Spanish",
    "Japanese",
    "Korean",
    "French",
    "Russian",
]

#: ``input.text`` is documented as capped at ~512 tokens. Tokens are not
#: characters and the ratio differs per language, so the cap enforced here is
#: characters and is deliberately generous-but-safe: a step's guidance paragraph
#: fits, a pasted transcript does not. Exceeding the server's limit costs a
#: round trip and returns an error at the moment speech was wanted, which is
#: strictly worse than speaking a sentence less.
MAX_TEXT_CHARS = 2000

#: Sentence terminators, longest-meaningful-unit first. Truncating mid-word
#: makes synthesised speech sound broken in a way that reads as a malfunction;
#: truncating after a full stop just sounds shorter.
_SENTENCE_ENDINGS = ("\n", "。", "！", "？", "；", ".", "!", "?", ";")

#: Only what ``sniff_audio_format`` can return. Anything else maps to "" rather
#: than to a plausible-but-guessed type -- a wrong MIME sends the player down a
#: decoder that cannot work and reports the failure as a corrupt file.
_MIME_BY_FORMAT = {
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "ogg": "audio/ogg",
    "flac": "audio/flac",
    "m4a": "audio/mp4",
}


# ---------------------------------------------------------------------------
# Container sniffing
# ---------------------------------------------------------------------------

def sniff_audio_format(data: bytes) -> str:
    """Identify an audio container from its magic bytes.

    Returns ``"wav"``, ``"mp3"``, ``"ogg"``, ``"flac"``, ``"m4a"`` or ``""``.

    This exists because the service documents no way to *ask* for a container
    (see the module docstring), so the only honest answer about what came back
    is the one read off the bytes. The player in this feature can only decode
    WAV with the stdlib, so the caller must be able to tell the difference
    rather than assume.

    This is the second magic-byte reader in the package -- ``audio.py``'s
    ``_sniff_format`` is the one the player actually decodes with -- so the two
    must recognise the same set. They did not: this one lacked the ``ftyp``
    (m4a) case, which ``AudioPlayer.supported_formats()`` lists. The result was
    a file the player can decode being reported here as an unrecognised
    container, with an empty ``mime`` and a warning telling the user their
    audio was probably broken. Anything added to one sniffer belongs in both.
    """
    if not data or len(data) < 4:
        return ""
    head = bytes(data[:16])
    if len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return "wav"
    if head[:4] == b"OggS":
        return "ogg"
    if head[:4] == b"fLaC":
        return "flac"
    if head[:3] == b"ID3":
        return "mp3"
    if len(head) >= 8 and head[4:8] == b"ftyp":
        return "m4a"
    # Bare MPEG frame sync: 11 set bits, i.e. 0xFF followed by 0xEx/0xFx.
    if len(head) >= 2 and head[0] == 0xFF and (head[1] & 0xE0) == 0xE0:
        return "mp3"
    return ""


def _truncate_on_sentence(text: str, limit: int) -> Tuple[str, bool]:
    """Cut ``text`` to ``limit`` characters at the latest sentence boundary.

    Falls back to a word boundary, then to a hard cut. Returns
    ``(text, was_truncated)``.
    """
    if len(text) <= limit:
        return text, False
    head = text[:limit]
    floor = int(limit * 0.4)  # never throw away more than ~60% chasing a period
    cut = -1
    for marker in _SENTENCE_ENDINGS:
        position = head.rfind(marker)
        if position > cut:
            cut = position
    if cut >= floor:
        return head[:cut + 1].rstrip(), True
    space = max(head.rfind(" "), head.rfind("\t"))
    if space >= floor:
        return head[:space].rstrip(), True
    return head.rstrip(), True


# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------

class SpeechResult:
    """One synthesis outcome. Falsy when there is no audio.

    Deliberately not a dataclass: ``__repr__`` must never print the audio, and
    an empty instance (``SpeechResult()``) is a first-class value -- it is what
    ``synthesize("")`` returns, and what a caller gets to test with ``if not
    result:`` instead of catching an exception for the ordinary case of having
    nothing to say.
    """

    def __init__(
        self,
        audio: bytes = b"",
        audio_format: str = "",
        mime: str = "",
        seconds: float = 0.0,
        text: str = "",
        request_id: str = "",
        raw: Optional[Dict[str, Any]] = None,
        truncated: bool = False,
        from_cache: bool = False,
    ) -> None:
        self.audio = audio or b""
        self.audio_format = audio_format or ""
        self.mime = mime or ""
        #: WALL-CLOCK LATENCY of the round trip, in seconds -- **not** the
        #: duration of the speech. The two are easy to confuse and the mistake
        #: is silent: a caller timing a barge-in window off this value would cut
        #: the audio off after however long the network took, and on a cache hit
        #: this is ~0.0 while the clip is still seconds long. The service
        #: returns no duration (see the module docstring), so the only honest
        #: source for one is decoding the bytes -- ``audio.decode_wav``.
        self.seconds = float(seconds or 0.0)
        #: The text ACTUALLY sent -- post-truncation. A caller that shows a
        #: transcript alongside the speech must show this, not its own input.
        self.text = text or ""
        self.request_id = request_id or ""
        #: Response METADATA only. The audio payload (inline base64 and the
        #: signed download URL) is stripped by ``_sanitize_raw`` before it gets
        #: here -- see that method for why.
        self.raw = raw if raw is not None else {}
        self.truncated = bool(truncated)
        self.from_cache = bool(from_cache)

    def __bool__(self) -> bool:
        return bool(self.audio)

    # Python 2 name kept off deliberately; this repo is 3.7+.

    def __len__(self) -> int:
        return len(self.audio)

    def __repr__(self) -> str:
        return (
            "SpeechResult(bytes={0}, format={1!r}, seconds={2:.2f}, "
            "chars={3}, truncated={4}, cached={5}, request_id={6!r})".format(
                len(self.audio), self.audio_format, self.seconds,
                len(self.text), self.truncated, self.from_cache, self.request_id,
            )
        )


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class QwenTTSClient:
    """Text-to-speech against DashScope's ``qwen3-tts-flash``.

    Stateless apart from configuration and the response cache, so one instance
    can be shared by the whole session and driven from any thread that is not
    the Qt main thread (which is where it belongs: a synthesis round trip is
    ~1 s and blocking the main thread would freeze the 3D view).

    THREADING CONTRACT (the same one :class:`QwenASRClient` keeps, for the same
    reasons -- this class makes the identical promise of being shared between
    the Qt main thread, which owns the settings widgets and calls the ``set*``
    methods, and a background worker calling :meth:`synthesize`). Three pieces
    of state are guarded by ``_lock``, and none of the three is optional:

    * **Configuration is read exactly once per call** (:meth:`_snapshot`).
      Individual attribute assignment is atomic under the GIL, so nothing here
      can corrupt -- but ``model``/``voice``/``language_type`` are *paired*:
      they are the payload AND the cache key. Reading them separately let a
      settings change land between the two reads, filing a clip synthesised
      with voice A under a cache key naming voice B, after which every later
      request for that text got the wrong voice out of memory and never
      contacted the service to find out. A snapshot also stops a retry ladder
      changing endpoint mid-ladder.
    * **The cache is guarded.** ``_cache`` and ``_cache_bytes`` are a
      read-modify-write pair; unguarded, the byte accounting drifts from the
      dict and the budget stops bounding anything. Worse, ``setModel`` calls
      ``clear_cache`` -- a settings change during an eviction sweep could
      empty the OrderedDict mid-``popitem`` and raise out of the caller's
      synthesis.
    * **``_call_index`` is incremented under the lock.** It is the whole of the
      artifact filename's uniqueness beyond a one-second timestamp, so a lost
      increment silently overwrites one call's record with another's.

    :meth:`synthesize` holds no lock across the HTTP round trip, so concurrent
    synthesis is supported and merely competes for the network.
    """

    DEFAULT_TIMEOUT = 30
    #: Two attempts, not five. Speech is guidance for the step the surgeon is on
    #: *now*; a prompt that arrives after they have moved on is worse than
    #: silence, because it describes the wrong step. The LLM path can afford
    #: five retries because its answer is still correct when it is late.
    MAX_RETRIES = 2

    #: Cache bounds. 24 entries covers a workflow's whole guidance set (the
    #: longest cookbook procedure is 33 steps and only some speak), and 8 MB
    #: bounds the damage if a caller speaks long paragraphs -- roughly 3 minutes
    #: of 24 kHz mono 16-bit WAV.
    CACHE_MAX_ENTRIES = 24
    CACHE_MAX_BYTES = 8 * 1024 * 1024

    #: The audio URL is served by OSS and must be fetched without an auth
    #: header (sending one makes OSS reject the request). Kept short: the file
    #: already exists by the time we are told about it, so a slow fetch is a
    #: network problem and waiting the full synthesis timeout for it only
    #: delays the caller's fallback to silence.
    AUDIO_FETCH_TIMEOUT = 20

    #: Populated by ``_run_log`` on the by-path fallback only. Class-level so
    #: the dev harness pays the file read once, not once per artifact.
    _run_log_module = None  # type: Any

    def __init__(
        self,
        api_key: str = "",
        endpoint: str = DEFAULT_ENDPOINT,
        model: str = DEFAULT_MODEL,
        voice: str = "Cherry",
        language_type: str = "Auto",
        timeout: Optional[int] = None,
        debug_output_dir: Optional[str] = None,
    ) -> None:
        self.api_key = (api_key or "").strip()
        self.endpoint = (endpoint or DEFAULT_ENDPOINT).strip()
        self.model = (model or DEFAULT_MODEL).strip()
        self.voice = (voice or "Cherry").strip()
        self.language_type = self._normalize_language(language_type)
        self.timeout = self.DEFAULT_TIMEOUT if timeout is None else int(timeout)
        self.debug_output_dir = debug_output_dir

        # Guards the configuration fields against the settings UI mutating them
        # under an in-flight request, and guards the cache and _call_index. See
        # the class docstring.
        self._lock = threading.RLock()
        # Instance-level, never global: two clients (a live one and a test one
        # in the settings dialog) must not hand each other results, and a module
        # global would keep audio alive for the life of the Slicer process.
        self._cache = collections.OrderedDict()  # type: collections.OrderedDict
        self._cache_bytes = 0
        self._call_index = 0

    # -- configuration ----------------------------------------------------

    def _snapshot(self) -> Dict[str, Any]:
        """The configuration for ONE call, read atomically.

        Everything downstream takes this dict rather than re-reading ``self``,
        so a request, its cache key and its artifact record cannot be assembled
        from three different configurations. See the class docstring for the
        wrong-voice-from-cache bug that motivated it.
        """
        with self._lock:
            return {
                "api_key": self.api_key,
                "endpoint": self.endpoint,
                "model": self.model,
                "voice": self.voice,
                "language_type": self.language_type,
                "timeout": self.timeout,
            }

    def setApiKey(self, api_key: str) -> None:
        """Set the DashScope API key. Never logged, never written to disk."""
        with self._lock:
            self.api_key = (api_key or "").strip()

    def setEndpoint(self, endpoint: str) -> None:
        """Set the regional endpoint (see ``ENDPOINTS``)."""
        with self._lock:
            self.endpoint = (endpoint or DEFAULT_ENDPOINT).strip()

    def setModel(self, model: str) -> None:
        with self._lock:
            self.model = (model or DEFAULT_MODEL).strip()
        self.clear_cache()

    def setVoice(self, voice: str) -> None:
        with self._lock:
            self.voice = (voice or "Cherry").strip()

    def setLanguageType(self, language_type: str) -> None:
        # Normalised outside the lock: it only logs and compares constants, and
        # holding the lock across a logging call invites a needless stall.
        normalized = self._normalize_language(language_type)
        with self._lock:
            self.language_type = normalized

    def setDebugOutputDir(self, path: Optional[str]) -> None:
        """Point per-call artifacts at a run folder, or ``None`` to stop writing."""
        with self._lock:
            self.debug_output_dir = path

    @staticmethod
    def _normalize_language(language_type: str) -> str:
        """Repair casing against the documented list; pass anything else through.

        Passing an unknown value through rather than silently rewriting it to
        "Auto" is intentional: if Alibaba adds a language, a caller that sets it
        should reach the service and get a real answer, not be quietly
        overridden by a stale constant in this file.
        """
        value = (language_type or "").strip()
        if not value:
            return "Auto"
        for known in LANGUAGE_TYPES:
            if known.lower() == value.lower():
                return known
        logger.warning(
            "Qwen TTS: language_type %r is not one of the documented values (%s); "
            "sending it unchanged.", value, ", ".join(LANGUAGE_TYPES))
        return value

    def is_configured(self) -> bool:
        """True when a call could be attempted at all."""
        return not self.unavailable_reason()

    def unavailable_reason(self) -> str:
        """Why speech is off, phrased as something the user can act on.

        Empty string when nothing is wrong. This is what the UI shows in place
        of a speaker icon, so it must name the setting to change -- "TTS
        unavailable" tells a surgeon nothing.
        """
        return self._unavailable_reason(self._snapshot())

    @staticmethod
    def _unavailable_reason(cfg: Dict[str, Any]) -> str:
        """The reason for one already-taken configuration snapshot."""
        if not cfg.get("api_key"):
            return (
                "Spoken guidance is off: no Alibaba Cloud Model Studio (DashScope) "
                "API key is set. Paste one into the agent's Settings to enable it."
            )
        if not cfg.get("endpoint"):
            return (
                "Spoken guidance is off: no TTS endpoint is set. Choose a region in "
                "Settings (International / China / US) or restore the default."
            )
        if not cfg.get("model"):
            return (
                "Spoken guidance is off: no TTS model is set. Restore the default "
                "'{0}' in Settings.".format(DEFAULT_MODEL)
            )
        return ""

    # -- cache ------------------------------------------------------------

    def clear_cache(self) -> None:
        """Drop every cached clip (and its memory)."""
        with self._lock:
            self._cache.clear()
            self._cache_bytes = 0

    @staticmethod
    def _cache_key(cfg: Dict[str, Any], text: str) -> Tuple[str, str, str, str]:
        """Keyed off the SNAPSHOT, never off ``self``.

        The key must name the configuration the audio was actually synthesised
        with; deriving it from live attributes is what let a settings change
        mid-call file a clip under another voice's name.
        """
        return (cfg["model"], cfg["voice"], cfg["language_type"], text)

    def _cache_get(self, key: Tuple[str, str, str, str]) -> Optional[SpeechResult]:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            self._cache.move_to_end(key)  # LRU: a hit is a recent use
            return entry

    def _cache_put(self, key: Tuple[str, str, str, str], result: SpeechResult) -> None:
        size = len(result.audio)
        if not size or size > self.CACHE_MAX_BYTES:
            return  # a single clip larger than the whole budget is not cacheable
        with self._lock:
            existing = self._cache.pop(key, None)
            if existing is not None:
                self._cache_bytes -= len(existing.audio)
            self._cache[key] = result
            self._cache_bytes += size
            while self._cache and (
                    len(self._cache) > self.CACHE_MAX_ENTRIES
                    or self._cache_bytes > self.CACHE_MAX_BYTES):
                _, evicted = self._cache.popitem(last=False)
                self._cache_bytes -= len(evicted.audio)
            if self._cache_bytes < 0:  # defensive; accounting must never go negative
                self._cache_bytes = sum(len(r.audio) for r in self._cache.values())

    # -- transport (shape copied from llm_client/transport.py) -------------

    @staticmethod
    def _open_request(request: urllib.request.Request, timeout: Optional[int]):
        if timeout is None:
            return urllib.request.urlopen(request)
        return urllib.request.urlopen(request, timeout=timeout)

    @staticmethod
    def _build_request(
        url: str,
        payload: Optional[Dict[str, Any]] = None,
        method: str = "POST",
        api_key: str = "",
    ) -> urllib.request.Request:
        """Build one request. ``api_key`` empty means send no ``Authorization``.

        The key is a parameter rather than read from ``self`` so the audio
        download -- which must NOT be authenticated, being an OSS link already
        signed in its query string -- cannot accidentally acquire a header from
        a later settings change.
        """
        data = None
        headers = {}  # type: Dict[str, str]
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if api_key:
            headers["Authorization"] = "Bearer " + api_key
        return urllib.request.Request(url, data=data, headers=headers, method=method)

    @staticmethod
    def _timeout_message(timeout: Optional[int]) -> str:
        return (
            "Qwen TTS timed out after {0} seconds. Spoken guidance was skipped for "
            "this step; check the network connection or pick a nearer region in "
            "Settings.".format(timeout)
        )

    @classmethod
    def _backoff(cls, attempt: int, seconds: Optional[float] = None) -> bool:
        """Sleep before the next attempt -- and only if there IS a next attempt.

        Every retry branch used to sleep unconditionally and then fall out of
        the loop, so the *last* failure paid a full backoff before raising: 3
        wasted seconds on a 429/5xx ladder, on a feature whose retry budget was
        cut to two attempts precisely because late speech describes the wrong
        step. Returns True when the caller should ``continue``.
        """
        if attempt >= cls.MAX_RETRIES - 1:
            return False
        time.sleep(2 ** attempt if seconds is None else seconds)
        return True

    @staticmethod
    def _parse_json(body: bytes) -> Dict[str, Any]:
        """Decode one response body. Raises RuntimeError, never retries.

        This is deliberately OUTSIDE the retry ladder's ``try``. It used to be
        inside it -- ``json.loads`` on the same line as ``response.read()`` --
        which meant a malformed reply was caught by the ladder's catch-all,
        slept on, re-requested, and finally reported as "Failed after 2
        attempts. Last error: Expecting value: line 1 column 1", burying both
        the fact that the server answered and what it said. A reply that is not
        JSON is not a transient fault.
        """
        text = (body or b"").decode("utf-8", errors="replace")
        try:
            parsed = json.loads(text)
        except ValueError as e:
            raise RuntimeError(
                "Qwen TTS returned a reply that is not JSON ({0}). First bytes: "
                "{1!r}".format(e, text[:200]))
        if not isinstance(parsed, dict):
            raise RuntimeError(
                "Qwen TTS returned an unexpected response (a {0}, not a JSON "
                "object).".format(type(parsed).__name__))
        return parsed

    def _post_json(self, cfg: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST the synthesis request, with the project's standard retry ladder.

        Only the HTTP round trip lives inside the loop -- see
        :meth:`_parse_json` for why parsing must not.
        """
        url = cfg["endpoint"]
        timeout = cfg["timeout"]
        last_error = None  # type: Any
        for attempt in range(self.MAX_RETRIES):
            try:
                request = self._build_request(url, payload, api_key=cfg["api_key"])
                with self._open_request(request, timeout) as response:
                    body = response.read()

            except urllib.error.HTTPError as e:
                last_error = e
                # errors='replace': the LLM client omits it and can raise
                # UnicodeDecodeError from inside the handler, which masks the
                # real failure with an unrelated traceback.
                try:
                    error_body = e.read().decode("utf-8", errors="replace")
                except Exception:
                    error_body = str(e)
                logger.warning("Qwen TTS HTTP error on attempt %d: %s - %s",
                               attempt + 1, e.code, error_body[:500])
                if e.code == 401:
                    raise RuntimeError(
                        "Invalid API key for Qwen TTS. Check the DashScope key in "
                        "Settings, and that it was issued for this region ({0}).".format(
                            urllib.parse.urlparse(url).hostname or url)
                    )
                if e.code == 403:
                    raise RuntimeError(
                        "Qwen TTS refused the request (403). The API key is valid but "
                        "not authorised for model '{0}' -- enable it in the Model "
                        "Studio console.".format(cfg["model"])
                    )
                if e.code == 404:
                    raise RuntimeError(
                        # cfg, not self: the message must name the model that was
                        # actually sent. Re-reading self here is how the sibling
                        # ASR client once reported a 404 against a model the user
                        # had already switched away from.
                        "Qwen TTS endpoint or model not found (404). Model '{0}' at "
                        "{1}. Check the model name and the region in Settings.".format(
                            cfg["model"], url)
                    )
                if e.code == 429 or e.code >= 500:
                    if self._backoff(attempt):
                        continue
                    break
                raise RuntimeError(
                    "Qwen TTS request failed: {0} - {1}".format(e.code, error_body[:500]))

            except urllib.error.URLError as e:
                last_error = e
                if isinstance(e.reason, socket.timeout):
                    raise RuntimeError(self._timeout_message(timeout))
                logger.warning("Qwen TTS URL error on attempt %d: %s", attempt + 1, e)
                if self._backoff(attempt, 1):
                    continue
                break

            except socket.timeout:
                raise RuntimeError(self._timeout_message(timeout))

            except RuntimeError:
                # Ours, and already carrying a remedy. Retrying it would spend
                # the ladder re-deriving a message we have, then replace it with
                # "Failed after 2 attempts".
                raise

            except Exception as e:
                # Genuinely unexpected -- a bug here, or a transport failure no
                # branch above names. Retried once (it may be transient) but the
                # TYPE is kept in the message, because "Last error: 'NoneType'
                # object is not subscriptable" reported as a network problem is
                # how a programming error hides for a release.
                last_error = e
                logger.warning("Qwen TTS unexpected %s on attempt %d: %s",
                               type(e).__name__, attempt + 1, e, exc_info=True)
                if self._backoff(attempt):
                    continue
                break

            else:
                return self._parse_json(body)

        raise RuntimeError(
            "Qwen TTS failed after {0} attempts. Last error: {1}".format(
                self.MAX_RETRIES,
                "{0}: {1}".format(type(last_error).__name__, last_error)
                if last_error is not None else "unknown"))

    def _fetch_audio_url(self, url: str) -> bytes:
        """GET the synthesised file. No auth header -- this is OSS, not DashScope.

        Sending ``Authorization`` here makes OSS reject a request that is
        already signed in its query string. The link is short-lived
        (``expires_at`` in the response; the guide says 24 hours), so it is
        fetched once, immediately, and never persisted.
        """
        last_error = None  # type: Any
        for attempt in range(self.MAX_RETRIES):
            try:
                # api_key deliberately omitted: OSS rejects a request that is
                # both header-authenticated and query-signed.
                request = self._build_request(url, method="GET")
                with self._open_request(request, self.AUDIO_FETCH_TIMEOUT) as response:
                    return response.read() or b""
            except urllib.error.HTTPError as e:
                last_error = e
                try:
                    body = e.read().decode("utf-8", errors="replace")
                except Exception:
                    body = str(e)
                if e.code in (403, 404):
                    raise RuntimeError(
                        "Qwen TTS produced audio but the download link was rejected "
                        "({0}). The link is time-limited; retry the step. Details: "
                        "{1}".format(e.code, body[:300])
                    )
                if e.code == 429 or e.code >= 500:
                    if self._backoff(attempt):
                        continue
                    break
                raise RuntimeError(
                    "Could not download the synthesised audio: {0} - {1}".format(
                        e.code, body[:300]))
            except urllib.error.URLError as e:
                last_error = e
                if isinstance(e.reason, socket.timeout):
                    raise RuntimeError(
                        "Timed out downloading the synthesised audio after {0} "
                        "seconds.".format(self.AUDIO_FETCH_TIMEOUT))
                if self._backoff(attempt, 1):
                    continue
                break
            except socket.timeout:
                raise RuntimeError(
                    "Timed out downloading the synthesised audio after {0} "
                    "seconds.".format(self.AUDIO_FETCH_TIMEOUT))
            except RuntimeError:
                raise
            except Exception as e:
                last_error = e
                logger.warning("Qwen TTS unexpected %s downloading audio on attempt "
                               "%d: %s", type(e).__name__, attempt + 1, e, exc_info=True)
                if self._backoff(attempt):
                    continue
                break
        raise RuntimeError(
            "Could not download the synthesised audio after {0} attempts. Last "
            "error: {1}".format(
                self.MAX_RETRIES,
                "{0}: {1}".format(type(last_error).__name__, last_error)
                if last_error is not None else "unknown"))

    # -- response handling -------------------------------------------------

    def _extract_audio(self, data: Dict[str, Any]) -> bytes:
        """Pull the audio bytes out of a 200 response, inline or by URL.

        DashScope can answer 200 with an error envelope (``code``/``message``
        populated, ``output`` empty), so a successful HTTP status is not a
        successful synthesis and both shapes have to be checked here.
        """
        if not isinstance(data, dict):
            raise RuntimeError("Qwen TTS returned an unexpected response (not a JSON object).")

        code = str(data.get("code") or "").strip()
        if code:
            message = str(data.get("message") or "").strip()
            raise RuntimeError(
                "Qwen TTS rejected the request: {0}{1}".format(
                    code, " - " + message if message else ""))

        output = data.get("output") or {}
        if not isinstance(output, dict):
            # The final message below already allowed for this, but the .get()
            # two lines down would have raised AttributeError first -- escaping
            # this module as something no caller catches, since the contract is
            # that every failure here is a RuntimeError carrying a remedy.
            raise RuntimeError(
                "Qwen TTS returned an 'output' that is not an object (a {0}).".format(
                    type(output).__name__))

        audio = output.get("audio") or {}
        if not isinstance(audio, dict):
            raise RuntimeError("Qwen TTS returned no audio object in its response.")

        inline = audio.get("data") or ""
        if inline:
            try:
                decoded = base64.b64decode(inline)
            except Exception as e:
                raise RuntimeError(
                    "Qwen TTS returned inline audio that is not valid base64: {0}".format(e))
            if decoded:
                return decoded

        url = str(audio.get("url") or "").strip()
        if url:
            return self._fetch_audio_url(url)

        raise RuntimeError(
            "Qwen TTS returned neither inline audio nor a download URL. "
            "Response keys: {0}".format(sorted(output.keys())))

    @staticmethod
    def _sanitize_raw(data: Dict[str, Any]) -> Dict[str, Any]:
        """The response with its audio payload removed, for ``SpeechResult.raw``.

        Three reasons, none cosmetic:

        1. ``output.audio.data`` is the inline base64 clip in streaming mode --
           a second copy of the audio, ~1.33x its size. Keeping it made the
           cache's byte budget a fiction: ``_cache_put`` charges an entry
           ``len(result.audio)`` while the entry actually retains the audio
           *and* its base64, so an 8 MB cap held nearer 19 MB.
        2. ``output.audio.url`` is an OSS link signed in its query string -- a
           short-lived credential. ``raw`` is exactly the field a caller dumps
           into a debug log, and the module docstring promises the URL is
           fetched immediately and never stored. It was being stored.
        3. The bytes are already on ``SpeechResult.audio``; nothing needs them
           twice.

        Everything else (``request_id``, ``usage``, ``output.finish_reason``, an
        error envelope) is kept -- that is what ``raw`` is for.
        """
        if not isinstance(data, dict):
            return {}
        cleaned = dict(data)
        output = cleaned.get("output")
        if isinstance(output, dict):
            output = dict(output)
            audio = output.get("audio")
            if isinstance(audio, dict):
                audio = dict(audio)
                for key in ("data", "url"):
                    if audio.get(key):
                        audio[key] = "<omitted>"
                output["audio"] = audio
            cleaned["output"] = output
        return cleaned

    # -- artifacts (fail-soft) --------------------------------------------

    @staticmethod
    def _run_log():
        """RunLog, imported lazily -- and by path when the package cannot load.

        ``SlicerAIAgentLib/__init__.py`` imports modules that need ``slicer``,
        so ``from SlicerAIAgentLib import RunLog`` raises outside Slicer even
        though RunLog itself is deliberately Qt-free and Slicer-free. Without
        the by-path fallback, running this client from the dev harness would
        write no artifact at all and say nothing about why -- the exact silent
        nothing that fail-soft logging is supposed to avoid. Inside Slicer the
        first branch is the one that runs.
        """
        try:
            from SlicerAIAgentLib import RunLog  # type: ignore
            return RunLog
        except Exception:
            logger.debug("Package import of RunLog failed; loading it by path",
                         exc_info=True)

        # Memoised: without this the fallback re-executes RunLog.py on every
        # artifact write, building a fresh module object per call.
        cached = QwenTTSClient._run_log_module
        if cached is not None:
            return cached

        import importlib.util

        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "RunLog.py")
        spec = importlib.util.spec_from_file_location("_voice_run_log", path)
        # spec_from_file_location returns None for a missing file, and a spec
        # with loader None for some path shapes; unguarded, both surface as
        # "'NoneType' object has no attribute ...", which is a confusing thing
        # to find in a debug log that was supposed to explain a missing artifact.
        if spec is None or spec.loader is None:
            raise RuntimeError("RunLog.py not importable at {0}".format(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        QwenTTSClient._run_log_module = module
        return module

    def _write_call_artifact(self, record: Dict[str, Any]) -> None:
        """One JSON per call under ``debug_output_dir``. Never the audio itself.

        Wrapped whole so a logging failure can never abort the call it was
        logging -- the same contract RunLog itself keeps.
        """
        with self._lock:
            directory = self.debug_output_dir
        if not directory:
            return
        try:
            run_log = self._run_log()
            # Under the lock: the index is the whole of this filename's
            # uniqueness beyond a one-second timestamp, so a lost increment from
            # an unguarded read-modify-write silently overwrites one call's
            # record with the next one's.
            with self._lock:
                self._call_index += 1
                index = self._call_index
            name = "voice_tts_{0}_{1}.json".format(time.strftime("%H%M%S"), index)
            run_log.ensure_dir(directory)
            run_log.write_json(os.path.join(directory, name), record)
        except Exception:
            logger.debug("Could not write TTS call artifact", exc_info=True)

    # -- synthesis ---------------------------------------------------------

    def synthesize(self, text: str) -> SpeechResult:
        """Speak ``text``. Returns an empty, falsy result for empty input.

        Raises ``RuntimeError`` with a remedy-bearing message on any failure the
        caller should surface; callers are expected to catch it and continue
        silently rather than let it reach the user as a traceback.
        """
        return self._synthesize(text, use_cache=True)

    def _synthesize(self, text: str, use_cache: bool = True) -> SpeechResult:
        start = time.time()
        prepared, truncated = _truncate_on_sentence((text or "").strip(), MAX_TEXT_CHARS)
        if not prepared:
            # Nothing to say is not an error and must not cost a request: the
            # caller speaks whatever guidance a step carries, and some steps
            # carry none.
            return SpeechResult()
        if truncated:
            logger.warning(
                "Qwen TTS: text of %d characters exceeds the %d-character cap; "
                "truncated to %d at a sentence boundary.",
                len(text or ""), MAX_TEXT_CHARS, len(prepared))

        # ONE read of the configuration for the whole call: the payload, the
        # cache key and the artifact record must describe the same request even
        # if the settings UI changes something mid-flight. See the class
        # docstring.
        cfg = self._snapshot()
        reason = self._unavailable_reason(cfg)
        if reason:
            raise RuntimeError(reason)

        record = {
            "model": cfg["model"],
            "voice": cfg["voice"],
            "language_type": cfg["language_type"],
            "endpoint": cfg["endpoint"],
            "text_chars": len(prepared),
            "truncated": truncated,
            "cached": False,
        }
        # The api_key is deliberately absent from `record`, and must stay
        # absent: this dict is written to disk verbatim.

        key = self._cache_key(cfg, prepared)
        if use_cache:
            hit = self._cache_get(key)
            if hit is not None:
                # A step's guidance is re-spoken on every replay Back/Forward.
                # Re-synthesising it would cost a second of silence and a
                # request for bytes we already hold.
                cached = SpeechResult(
                    audio=hit.audio, audio_format=hit.audio_format, mime=hit.mime,
                    seconds=round(time.time() - start, 3), text=hit.text,
                    # dict(): the cached entry's `raw` must not be handed out by
                    # reference, or one caller mutating it corrupts what every
                    # later hit sees. `audio` is bytes and immutable, so it can
                    # be shared -- which is the point of the cache.
                    request_id=hit.request_id, raw=dict(hit.raw),
                    truncated=hit.truncated, from_cache=True,
                )
                # Logged like any other call, flagged `cached`. A run whose
                # artifacts show only the misses would misreport how often the
                # feature spoke, which is the number this logging is for.
                record.update({
                    "cached": True,
                    "audio_format": cached.audio_format,
                    "audio_bytes": len(cached.audio),
                    "seconds": cached.seconds,
                    "request_id": cached.request_id,
                    "error": "",
                })
                self._write_call_artifact(record)
                return cached

        payload = {
            "model": cfg["model"],
            "input": {
                "text": prepared,
                "voice": cfg["voice"],
                "language_type": cfg["language_type"],
            },
        }

        try:
            data = self._post_json(cfg, payload)
            audio = self._extract_audio(data)
        except Exception as e:
            record.update({
                "audio_format": "",
                "audio_bytes": 0,
                "seconds": round(time.time() - start, 3),
                "request_id": "",
                "error": str(e),
            })
            self._write_call_artifact(record)
            raise

        audio_format = sniff_audio_format(audio)
        if not audio_format:
            # Not fatal -- the bytes may still be playable by something -- but
            # the caller's stdlib WAV path cannot use them, so say so once.
            logger.warning(
                "Qwen TTS returned %d bytes in an unrecognised container "
                "(first bytes: %r). The player may not be able to decode it.",
                len(audio), bytes(audio[:8]))

        result = SpeechResult(
            audio=audio,
            audio_format=audio_format,
            mime=_MIME_BY_FORMAT.get(audio_format, ""),
            seconds=round(time.time() - start, 3),
            text=prepared,
            request_id=str(data.get("request_id") or ""),
            raw=self._sanitize_raw(data),
            truncated=truncated,
            from_cache=False,
        )
        if use_cache:
            self._cache_put(key, result)

        record.update({
            "audio_format": result.audio_format,
            "audio_bytes": len(result.audio),
            "seconds": result.seconds,
            "request_id": result.request_id,
            "error": "",
        })
        self._write_call_artifact(record)
        return result

    def test_connection(self) -> Dict[str, Any]:
        """Synthesise one short phrase and report what happened.

        Never raises: this backs a "Test" button in Settings, where an
        exception dialog is a worse answer than a sentence saying which setting
        is wrong. The cache is bypassed deliberately -- a test that a previous
        test satisfied from memory would report success with the network
        unplugged.
        """
        start = time.time()
        reason = self.unavailable_reason()
        if reason:
            return {"success": False, "error": reason, "bytes": 0,
                    "audio_format": "", "seconds": 0.0}
        try:
            result = self._synthesize("Slicer AI Agent voice check.", use_cache=False)
        except Exception as e:
            return {"success": False, "error": str(e), "bytes": 0,
                    "audio_format": "", "seconds": round(time.time() - start, 3)}
        return {
            "success": bool(result),
            "error": "" if result else "The service returned no audio.",
            "bytes": len(result.audio),
            "audio_format": result.audio_format,
            "seconds": result.seconds,
        }
