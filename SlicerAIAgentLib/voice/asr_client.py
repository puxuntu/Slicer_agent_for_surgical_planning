"""
Speech-to-text against Alibaba Cloud Model Studio (DashScope), qwen3-asr-flash.

WHY THIS IS NOT AN OpenAI-COMPATIBLE CALL. Every other model call in this
project goes through ``LLMClient`` and the ``/compatible-mode/v1`` base URL, and
the obvious thing to do here was to reuse it. It does not work: DashScope
exposes ASR through ``compatible-mode`` only in some regions, and **not in the
US (Virginia) region this project targets by default** (see
``app/widget_settings.py`` — the Qwen chat provider already points at
``dashscope-us``). Sending the audio through the compatible endpoint therefore
fails for exactly the deployment we ship. So this client speaks the DashScope
**native** multimodal-generation protocol instead, which is why it has its own
payload/response shapes rather than reusing ``LLMClient``'s.

WHY urllib AND NOT httpx. ``httpx`` appears in requirements.txt but is imported
by no project code and is unproven inside Slicer's Python. The whole networking
surface of this repo is ``urllib.request``; this module copies the shape of
``llm_client/transport.py`` and the retry ladder of ``llm_client/chat.py`` so
there is one failure mode to understand, not two.

WHY ``enable_itn`` DEFAULTS TO TRUE. Inverse text normalization turns spoken
numbers into digits. Voice here drives workflow steps that carry numeric
arguments ("threshold two hundred to three thousand"), and a transcript reading
"two hundred" instead of "200" is a transcript the downstream parser cannot use.
The cost is that ITN also normalizes dates and units, which is harmless for this
vocabulary.

WHY THE AUDIO IS NEVER PERSISTED. This runs in a room where a microphone hears
the patient and the surgical team. Run folders under ``logs/`` are copied,
shared and attached to papers. The debug artifact therefore records the *shape*
of the request (byte counts, duration, model, latency) and the transcript, and
deliberately never the audio bytes. The API key is never logged either.

WHY THE TIMEOUT IS SHORTER THAN LLMClient's. 60 s, not 120 s: a chat turn that
takes two minutes is annoying, but an utterance that takes a minute to transcribe
has already been overtaken by the user speaking again, so failing fast and
letting them repeat themselves is the better outcome.

Qt-free and Slicer-free: this module imports in a plain CPython 3.7 interpreter
with only the standard library, so the client can be exercised outside Slicer.
"""

from __future__ import annotations

import base64
import io
import json
import logging
import os
import re
import socket
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import wave
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# Anything that could be a credential, stripped out of server- and
# exception-derived text before it reaches a log line or a run folder. See
# _redact_secrets().
_SECRET_PATTERNS = (
    re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{8,}"),
    re.compile(r"\bsk-[A-Za-z0-9._\-]{8,}"),
)
_REDACTED = "***redacted***"


# --------------------------------------------------------------------------
# Regions
#
# The model id is region-specific, not just the host: the US region serves
# `qwen3-asr-flash-us` and rejects the bare `qwen3-asr-flash` name. Pairing the
# two here keeps a settings UI from offering a combination that cannot work.
# --------------------------------------------------------------------------

REGIONS: Dict[str, Dict[str, Any]] = {
    "us": {
        "label": "US (Virginia)",
        "endpoint": "https://dashscope-us.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
        "models": [
            "qwen3-asr-flash-us",
            "qwen3-asr-flash-2025-09-08-us",
        ],
        "default_model": "qwen3-asr-flash-us",
    },
    "intl": {
        "label": "International (Singapore)",
        "endpoint": "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
        "models": [
            "qwen3-asr-flash",
            "qwen3-asr-flash-2026-02-10",
            "qwen3-asr-flash-2025-09-08",
        ],
        "default_model": "qwen3-asr-flash",
    },
    "cn": {
        "label": "China (Beijing)",
        "endpoint": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
        "models": [
            "qwen3-asr-flash",
            "qwen3-asr-flash-2026-02-10",
        ],
        "default_model": "qwen3-asr-flash",
    },
}

DEFAULT_REGION = "us"
DEFAULT_MODEL = "qwen3-asr-flash-us"
DEFAULT_ENDPOINT = "https://dashscope-us.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

# ("", "Auto-detect") first, because omitting the language key entirely is a
# supported and often better choice than guessing wrong: a forced language is
# applied even when the speaker used another one.
LANGUAGES: List[Tuple[str, str]] = [
    ("", "Auto-detect"),
    ("en", "English"),
    ("zh", "Chinese (Mandarin)"),
    ("yue", "Chinese (Cantonese)"),
    ("ja", "Japanese"),
    ("ko", "Korean"),
    ("de", "German"),
    ("fr", "French"),
    ("es", "Spanish"),
    ("it", "Italian"),
    ("pt", "Portuguese"),
    ("ru", "Russian"),
    ("ar", "Arabic"),
    ("hi", "Hindi"),
    ("id", "Indonesian"),
    ("th", "Thai"),
    ("tr", "Turkish"),
    ("uk", "Ukrainian"),
    ("vi", "Vietnamese"),
    ("cs", "Czech"),
    ("da", "Danish"),
    ("fil", "Filipino"),
    ("fi", "Finnish"),
    ("is", "Icelandic"),
    ("ms", "Malay"),
    ("no", "Norwegian"),
    ("pl", "Polish"),
    ("sv", "Swedish"),
]

_LANGUAGE_CODES = set(code for code, _label in LANGUAGES if code)

# Documented service limits. Both are enforced client-side, before a request is
# spent, because the server-side rejection arrives as a generic 400 that reads
# like a bug in this client rather than "your clip is too long".
MAX_AUDIO_SECONDS = 300              # 5 minutes
MAX_ENCODED_BYTES = 10 * 1024 * 1024  # 10 MB *after* base64 (~7.5 MB of raw WAV)

# Aliases callers reasonably produce that the API does not name that way.
_MIME_ALIASES = {
    "audio/x-wav": "audio/wav",
    "audio/wave": "audio/wav",
    "audio/vnd.wave": "audio/wav",
    "audio/mp3": "audio/mpeg",
    "audio/x-mpeg": "audio/mpeg",
    "audio/x-flac": "audio/flac",
}

_DEFAULT_MIME = "audio/wav"

# Test-connection probe: long enough that the service accepts it as audio,
# short enough to cost nothing. 0.4 s of 16 kHz mono silence is ~12.8 KB.
_PROBE_SECONDS = 0.4
_PROBE_SAMPLE_RATE = 16000


def region_for_endpoint(endpoint: str) -> str:
    """Return the REGIONS key serving ``endpoint``, or "" when unrecognized.

    "" rather than a default, deliberately: a custom or mistyped endpoint
    labelled "us" would silently offer the US model list, and picking a model
    from the wrong region is the failure this pairing exists to prevent.
    """
    candidate = (endpoint or "").strip().rstrip("/").lower()
    if not candidate:
        return ""
    for key, info in REGIONS.items():
        if candidate == str(info["endpoint"]).rstrip("/").lower():
            return key
    # Fall back to host comparison so a path variant still resolves.
    try:
        host = urllib.parse.urlparse(candidate).hostname or ""
    except Exception:
        host = ""
    if host:
        for key, info in REGIONS.items():
            try:
                known = urllib.parse.urlparse(str(info["endpoint"])).hostname or ""
            except Exception:
                known = ""
            if known and host == known:
                return key
    return ""


def endpoint_for_region(region: str) -> str:
    """Return the native ASR endpoint for ``region`` (DEFAULT_REGION if unknown)."""
    info = REGIONS.get((region or "").strip().lower()) or REGIONS[DEFAULT_REGION]
    return str(info["endpoint"])


def models_for_region(region: str) -> List[str]:
    """Return the model ids valid in ``region`` (DEFAULT_REGION's if unknown)."""
    info = REGIONS.get((region or "").strip().lower()) or REGIONS[DEFAULT_REGION]
    return list(info["models"])


class TranscriptionResult:
    """One transcription. Falsy when the model produced no text.

    Silence is a *normal* outcome for an always-on microphone, so an empty
    transcript is a successful call carrying ``text == ""`` — never an
    exception and never None. ``bool(result)`` is the "did anyone say
    anything?" test callers actually want.
    """

    def __init__(self, text: str = "", language: str = "", emotion: str = "",
                 seconds: float = 0.0, audio_seconds: float = 0.0,
                 request_id: str = "", raw: Optional[Dict[str, Any]] = None) -> None:
        self.text: str = text or ""
        self.language: str = language or ""
        self.emotion: str = emotion or ""
        self.seconds: float = float(seconds or 0.0)          # wall clock of the HTTP call
        self.audio_seconds: float = float(audio_seconds or 0.0)
        self.request_id: str = request_id or ""
        self.raw: Dict[str, Any] = raw if isinstance(raw, dict) else {}

    def __bool__(self) -> bool:
        return bool(self.text.strip())

    def to_dict(self) -> Dict[str, Any]:
        """Serializable view. ``raw`` is included; it never holds the audio."""
        return {
            "text": self.text,
            "language": self.language,
            "emotion": self.emotion,
            "seconds": round(self.seconds, 3),
            "audio_seconds": round(self.audio_seconds, 3),
            "request_id": self.request_id,
        }

    def __repr__(self) -> str:
        preview = self.text if len(self.text) <= 60 else self.text[:57] + "..."
        return "TranscriptionResult(text=%r, language=%r, seconds=%.2f)" % (
            preview, self.language, self.seconds)


class QwenASRClient:
    """Synchronous speech-to-text over the DashScope native ASR endpoint.

    THREADING CONTRACT. One instance is shared between the Qt main thread
    (which owns the settings widgets and calls the ``set*`` methods) and a
    background worker (which calls :meth:`transcribe`). Two properties make
    that safe, and neither is free:

    * **Every setter takes ``_lock``, and a call reads its configuration
      exactly once, up front** (:meth:`_snapshot`). Attribute assignment is
      individually atomic under the GIL, so nothing here can corrupt — but the
      endpoint and the model are *paired* (a region serves only its own model
      ids, see REGIONS), and re-reading them field by field, per retry
      attempt, let a region change land between the two reads. The request
      then carried region A's URL with region B's model and came back as a
      404 whose message named a model the user had just stopped using. The
      snapshot also means a retry ladder cannot change endpoint mid-ladder.
    * **``_artifact_index`` is incremented under the same lock.** It exists
      only because two transcriptions can land in the same second, so it is
      the whole of the artifact filename's uniqueness; a lost increment from
      an unguarded read-modify-write silently overwrites the previous call's
      record with the next one's.

    :meth:`transcribe` is otherwise re-entrant: it holds no lock across the
    HTTP call, so a second thread transcribing concurrently is supported and
    merely competes for the network.
    """

    # 60, not LLMClient's 120 — see the module docstring.
    DEFAULT_TIMEOUT = 60
    MAX_RETRIES = 3

    def __init__(self, api_key: str = "", endpoint: str = DEFAULT_ENDPOINT,
                 model: str = DEFAULT_MODEL, language: str = "",
                 enable_itn: bool = True, timeout: Optional[int] = None,
                 debug_output_dir: Optional[str] = None,
                 log_transcripts: bool = False) -> None:
        #: Whether the recognised TEXT is written into the run folder.
        #: Off by default, and that is a privacy decision rather than a
        #: performance one: this microphone is always on in an operating
        #: theatre, so most of what it transcribes is conversation about a
        #: patient, and run folders are copied, shared and attached to papers.
        #: A researcher who needs the transcripts for an evaluation turns it on
        #: deliberately; the byte counts, durations and detected language are
        #: always kept, so the artifact still evidences that the call happened.
        self.log_transcripts: bool = bool(log_transcripts)
        self.api_key: str = api_key or ""
        self.endpoint: str = (endpoint or DEFAULT_ENDPOINT).strip()
        self.model: str = (model or DEFAULT_MODEL).strip()
        self.language: str = (language or "").strip()
        self.enable_itn: bool = bool(enable_itn)
        # timeout<=0 means "no timeout", matching LLMClient's None semantics.
        if timeout is None:
            self.timeout: Optional[int] = self.DEFAULT_TIMEOUT
        elif timeout <= 0:
            self.timeout = None
        else:
            self.timeout = int(timeout)
        self.debug_output_dir: Optional[str] = debug_output_dir
        # Guards the configuration fields against the settings UI mutating them
        # under an in-flight request, and guards _artifact_index. See the class
        # docstring.
        self._lock = threading.RLock()
        # Two transcriptions can land in the same second, so the timestamp alone
        # is not a unique artifact name.
        self._artifact_index: int = 0

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def _snapshot(self) -> Dict[str, Any]:
        """The configuration for ONE call, read atomically.

        Everything downstream takes this dict rather than reading ``self``, so
        a request cannot be assembled from two different configurations — see
        the class docstring for the 404 that motivated it.
        """
        with self._lock:
            return {
                "api_key": self.api_key,
                "endpoint": self.endpoint,
                "model": self.model,
                "language": self.language,
                "enable_itn": bool(self.enable_itn),
                "timeout": self.timeout,
                "log_transcripts": bool(self.log_transcripts),
            }

    def setApiKey(self, api_key: str) -> None:
        """Set or update the API key. It is never logged or persisted."""
        with self._lock:
            self.api_key = api_key or ""

    def setEndpoint(self, endpoint: str) -> None:
        """Set the native ASR endpoint (see REGIONS / endpoint_for_region)."""
        with self._lock:
            self.endpoint = (endpoint or "").strip()

    def setModel(self, model: str) -> None:
        """Set the model id. Must be one this endpoint's region serves."""
        with self._lock:
            self.model = (model or "").strip()

    def setLanguage(self, language: str) -> None:
        """Set the ASR language; "" means auto-detect (the key is then omitted).

        An unknown code is passed through with a warning rather than rejected:
        the service adds languages faster than this table is updated, and
        refusing one here would be a hard failure for a value that works.
        """
        code = (language or "").strip()
        if code and code not in _LANGUAGE_CODES:
            logger.warning("Unrecognized ASR language code %r; sending it anyway", code)
        with self._lock:
            self.language = code

    def setEnableItn(self, enabled: bool) -> None:
        """Toggle inverse text normalization (spoken numbers -> digits)."""
        with self._lock:
            self.enable_itn = bool(enabled)

    def setDebugOutputDir(self, path: Optional[str]) -> None:
        """Set the directory for per-call debug artifacts (None disables them)."""
        with self._lock:
            self.debug_output_dir = path

    def is_configured(self) -> bool:
        """True when a call could be attempted at all."""
        cfg = self._snapshot()
        return bool(cfg["api_key"] and cfg["endpoint"] and cfg["model"])

    def unavailable_reason(self) -> str:
        """"" when configured, else one sentence naming the missing piece and the fix."""
        return self._unavailableReason(self._snapshot())

    def _unavailableReason(self, cfg: Dict[str, Any]) -> str:
        """As :meth:`unavailable_reason`, against an already-taken snapshot."""
        if not cfg["api_key"]:
            return ("Voice input needs a DashScope (Alibaba Cloud Model Studio) API key. "
                    "Set it in the extension's Settings section.")
        if not cfg["endpoint"]:
            return ("No speech-to-text endpoint is configured. Choose a region in Settings "
                    "(US Virginia is the default: %s)." % DEFAULT_ENDPOINT)
        if not cfg["model"]:
            region = region_for_endpoint(cfg["endpoint"]) or DEFAULT_REGION
            return ("No speech-to-text model is configured. For this endpoint choose one of: %s."
                    % ", ".join(models_for_region(region)))
        return ""

    # ------------------------------------------------------------------
    # Transport (shape copied from llm_client/transport.py)
    # ------------------------------------------------------------------

    def _buildHeaders(self, cfg: Dict[str, Any]) -> Dict[str, str]:
        if not cfg["api_key"]:
            raise RuntimeError(self._unavailableReason(cfg))
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % cfg["api_key"],
        }

    def _buildRequest(self, payload: Dict[str, Any],
                      cfg: Dict[str, Any]) -> urllib.request.Request:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return urllib.request.Request(
            cfg["endpoint"],
            data=data,
            headers=self._buildHeaders(cfg),
            method="POST",
        )

    def _openRequest(self, request: urllib.request.Request, cfg: Dict[str, Any]):
        if cfg["timeout"] is None:
            return urllib.request.urlopen(request)
        return urllib.request.urlopen(request, timeout=cfg["timeout"])

    def _timeoutErrorMessage(self, cfg: Dict[str, Any]) -> str:
        if cfg["timeout"] is None:
            return ("Speech-to-text request timed out. Check your network connection "
                    "and try speaking again.")
        return ("Speech-to-text request timed out after %d seconds. Check your network "
                "connection and try speaking again." % cfg["timeout"])

    def _httpErrorMessage(self, code: int, body: str, cfg: Dict[str, Any]) -> str:
        """Turn a DashScope HTTP failure into something a user can act on.

        ``body`` is server text and is redacted before it is quoted: some
        gateways echo the offending credential back in an auth failure, and
        this string reaches both the log and the run folder.
        """
        body = _redact_secrets(body, cfg.get("api_key", ""))
        detail = _dashscope_error_detail(body)
        region = region_for_endpoint(cfg["endpoint"])
        models = ", ".join(models_for_region(region or DEFAULT_REGION))
        lowered = (detail or body or "").lower()

        if code == 403:
            return ("Speech-to-text access denied (403)%s. The API key may not be enabled for "
                    "Model Studio in this region, or the model is not activated on this account."
                    % _suffix(detail))
        if code == 404 or (code == 400 and "model" in lowered):
            return ("Speech-to-text model '%s' was not found at %s%s. Model ids are "
                    "region-specific — this endpoint serves: %s."
                    % (cfg["model"], cfg["endpoint"], _suffix(detail), models))
        if code == 413:
            return ("The audio clip was rejected as too large (413)%s. Keep recordings under "
                    "%d seconds and about 7.5 MB of raw WAV." % (_suffix(detail), MAX_AUDIO_SECONDS))
        if code == 429:
            return ("Speech-to-text is rate limited (429)%s. The service is throttling this "
                    "account — wait a moment and speak again." % _suffix(detail))
        if code >= 500:
            return ("The speech-to-text service is temporarily unavailable (%d)%s. This is a "
                    "server-side fault; try again shortly." % (code, _suffix(detail)))
        return ("Speech-to-text request failed: %d%s" % (code, _suffix(detail or body)))

    def _post(self, payload: Dict[str, Any], cfg: Dict[str, Any]) -> Dict[str, Any]:
        """POST with the project's retry ladder (llm_client/chat.py lines 57-107).

        A 401 is never retried: a bad key is bad on every attempt, and retrying
        it just makes the user wait for the same answer three times. Likewise a
        timeout — the clip is already stale by then (see the module docstring).

        Three deliberate departures from chat.py's copy of this ladder:

        * **The backoff is skipped on the final attempt.** ``sleep(2**attempt)``
          before falling out of the loop bought nothing and added four seconds
          to every exhausted 5xx before the user saw the error.
        * **A RuntimeError raised inside the try is re-raised immediately.**
          Those are this module's own remedy-bearing messages; retrying one
          three times and then re-wrapping it as "Failed after 3 attempts.
          Last error: Voice input needs an API key" buries the remedy in
          boilerplate and spends seven seconds doing it.
        * **The final message describes the last failure**, rather than
          ``str(HTTPError)`` — an exhausted 429 ladder said "HTTP Error 429:
          Too Many Requests", which does not tell a clinician to wait.
        """
        last_error: Any = None
        last_message: str = ""
        for attempt in range(self.MAX_RETRIES):
            final_attempt = (attempt == self.MAX_RETRIES - 1)
            try:
                request = self._buildRequest(payload, cfg)
                with self._openRequest(request, cfg) as response:
                    body = response.read().decode("utf-8", errors="replace")
                return json.loads(body)

            except urllib.error.HTTPError as e:
                last_error = e
                # errors='replace': chat.py decodes strictly here, and a
                # non-UTF-8 error body then raises UnicodeDecodeError *inside*
                # the handler, masking the real HTTP failure.
                try:
                    error_body = e.read().decode("utf-8", errors="replace")
                except Exception:
                    error_body = ""
                finally:
                    # HTTPError is an open response object; without this the
                    # socket is only reclaimed when the GC gets to it, and a
                    # retry ladder opens three of them.
                    try:
                        e.close()
                    except Exception:
                        pass
                error_body = _redact_secrets(error_body, cfg.get("api_key", ""))
                logger.warning("ASR HTTP error on attempt %d: %s - %s",
                               attempt + 1, e.code, error_body)
                if e.code == 401:
                    raise RuntimeError(
                        "Invalid API key. Check the DashScope (Alibaba Cloud Model Studio) "
                        "API key in Settings; it must be a Model Studio key for the selected region.")
                last_message = self._httpErrorMessage(e.code, error_body, cfg)
                if e.code == 429 or e.code >= 500:
                    if not final_attempt:
                        time.sleep(2 ** attempt)
                    continue
                raise RuntimeError(last_message)

            except urllib.error.URLError as e:
                last_error = e
                if isinstance(e.reason, socket.timeout):
                    raise RuntimeError(self._timeoutErrorMessage(cfg))
                logger.warning("ASR URL error on attempt %d: %s", attempt + 1, e)
                last_message = (
                    "Could not reach the speech-to-text service at %s (%s). Check the network "
                    "connection and the endpoint in Settings." % (cfg["endpoint"], e.reason))
                if not final_attempt:
                    time.sleep(1)
                continue

            except socket.timeout:
                raise RuntimeError(self._timeoutErrorMessage(cfg))

            except RuntimeError:
                # Ours, already phrased for the user. Not a transport failure.
                raise

            except Exception as e:
                last_error = e
                logger.warning("ASR error on attempt %d: %s", attempt + 1, e)
                last_message = "Speech-to-text failed unexpectedly: %s: %s" % (
                    type(e).__name__, _redact_secrets(str(e), cfg.get("api_key", "")))
                if not final_attempt:
                    time.sleep(2 ** attempt)

        if last_message:
            raise RuntimeError("%s (failed after %d attempts)" % (last_message, self.MAX_RETRIES))
        raise RuntimeError("Speech-to-text failed after %d attempts. Last error: %s"
                           % (self.MAX_RETRIES,
                              _redact_secrets(str(last_error), cfg.get("api_key", ""))))

    # ------------------------------------------------------------------
    # Transcription
    # ------------------------------------------------------------------

    def _buildPayload(self, data_uri: str, cfg: Dict[str, Any]) -> Dict[str, Any]:
        asr_options: Dict[str, Any] = {"enable_itn": bool(cfg["enable_itn"])}
        # The key is OMITTED for auto-detect. Sending language:"" is not the
        # same request and the service does not read it as "decide for me".
        if cfg["language"]:
            asr_options["language"] = cfg["language"]
        return {
            "model": cfg["model"],
            "input": {"messages": [{"role": "user", "content": [{"audio": data_uri}]}]},
            "parameters": {"asr_options": asr_options},
        }

    def transcribe(self, audio_bytes: bytes, mime: str = "audio/wav",
                   audio_seconds: float = 0.0,
                   context: str = "") -> TranscriptionResult:
        """Transcribe one clip. Returns a result whose ``text`` may be "".

        ``audio_seconds`` is the caller's known duration; pass 0.0 and a WAV
        clip and it is read out of the header instead, so the 5-minute guard
        still applies.

        ``context`` is accepted, recorded in the debug artifact, and **not
        sent**: qwen3-asr-flash documents only ``language`` and ``enable_itn``
        under ``asr_options``, and inventing a biasing field would either be
        ignored or 400 the whole request. It is kept in the signature as the
        hook for a documented biasing field when one exists, so callers that
        already have the context (the active workflow step, the scene's node
        names) do not have to be rewritten then — and so the argument is not
        silently discarded today.
        """
        # One read of the configuration for the whole call, retries included.
        cfg = self._snapshot()
        reason = self._unavailableReason(cfg)
        if reason:
            raise RuntimeError(reason)

        if not audio_bytes:
            raise RuntimeError("No audio was captured. Check that the microphone is "
                               "connected and not muted, then record again.")

        mime = _normalize_mime(mime)
        duration = float(audio_seconds or 0.0)
        if duration <= 0.0 and mime == "audio/wav":
            duration = _probe_wav_seconds(audio_bytes)

        if duration > MAX_AUDIO_SECONDS:
            raise RuntimeError(
                "The recording is %.1f seconds long; the speech-to-text service accepts at most "
                "%d seconds (5 minutes). Record a shorter clip."
                % (duration, MAX_AUDIO_SECONDS))

        encoded = base64.b64encode(audio_bytes).decode("ascii")
        encoded_bytes = len(encoded)
        if encoded_bytes > MAX_ENCODED_BYTES:
            raise RuntimeError(
                "The recording is %.1f MB, which exceeds the %d MB limit once base64-encoded "
                "(about 7.5 MB of raw WAV). Record a shorter clip or use a lower sample rate."
                % (len(audio_bytes) / (1024.0 * 1024.0), MAX_ENCODED_BYTES // (1024 * 1024)))

        data_uri = "data:%s;base64,%s" % (mime, encoded)
        payload = self._buildPayload(data_uri, cfg)

        started = time.time()
        elapsed = 0.0
        error_text = ""
        result: Optional[TranscriptionResult] = None
        try:
            data = self._post(payload, cfg)
            elapsed = time.time() - started
            result = _parse_response(data, seconds=elapsed, audio_seconds=duration)
            return result
        except Exception as exc:
            elapsed = time.time() - started
            # Redacted again at the boundary: this string is written into the
            # run folder, and an exception raised below _post (or by a future
            # caller of it) has not been through _httpErrorMessage.
            error_text = _redact_secrets(str(exc), cfg.get("api_key", ""))
            raise
        finally:
            self._writeArtifact(
                cfg=cfg,
                mime=mime,
                audio_byte_count=len(audio_bytes),
                encoded_bytes=encoded_bytes,
                audio_seconds=duration,
                seconds=elapsed,
                context=context,
                result=result,
                error=error_text,
            )

    def test_connection(self) -> Dict[str, Any]:
        """Verify credentials, endpoint and model without needing a microphone.

        Sends ~0.4 s of synthesized silence. A call that succeeds and
        transcribes to "" is a SUCCESS — it proves the key, the region and the
        model id line up, which is the only thing this can prove without a
        speaker in the room.
        """
        reason = self.unavailable_reason()
        if reason:
            return {"success": False, "error": reason, "text": "", "seconds": 0.0}

        started = time.time()
        try:
            silence = _build_silence_wav(_PROBE_SECONDS, _PROBE_SAMPLE_RATE)
        except Exception as exc:
            logger.debug("Could not synthesize the ASR probe clip", exc_info=True)
            return {"success": False,
                    "error": "Could not build the test audio clip: %s" % exc,
                    "text": "", "seconds": 0.0}

        try:
            result = self.transcribe(silence, mime="audio/wav",
                                     audio_seconds=_PROBE_SECONDS)
        except Exception as exc:
            return {"success": False, "error": str(exc), "text": "",
                    "seconds": round(time.time() - started, 3)}

        return {"success": True, "error": "", "text": result.text,
                "seconds": round(result.seconds, 3)}

    # ------------------------------------------------------------------
    # Debug artifact (fail-soft: logging must never abort the call it logs)
    # ------------------------------------------------------------------

    def _writeArtifact(self, cfg: Dict[str, Any], mime: str, audio_byte_count: int,
                       encoded_bytes: int, audio_seconds: float, seconds: float,
                       context: str, result: Optional[TranscriptionResult],
                       error: str) -> str:
        # Read once: the settings UI may repoint this while a call is in flight,
        # and a half-written record in the previous folder helps nobody.
        target = self.debug_output_dir
        if not target:
            return ""
        try:
            from SlicerAIAgentLib import RunLog

            # The index is the whole of the filename's uniqueness within a
            # second, so a lost increment overwrites a record. See the class
            # docstring.
            with self._lock:
                self._artifact_index += 1
                index = self._artifact_index
            name = "voice_asr_%s_%03d.json" % (time.strftime("%H%M%S"), index)
            RunLog.ensure_dir(target)
            record: Dict[str, Any] = {
                "endpoint": cfg.get("endpoint", ""),
                "model": cfg.get("model", ""),
                "language": cfg.get("language", "") or "(auto-detect)",
                "enable_itn": bool(cfg.get("enable_itn", True)),
                "mime": mime,
                "audio_seconds": round(float(audio_seconds), 3),
                "audio_bytes": int(audio_byte_count),
                "encoded_bytes": int(encoded_bytes),
                "seconds": round(float(seconds), 3),
                "request_id": result.request_id if result is not None else "",
                "text_chars": len(result.text) if result is not None else 0,
                "detected_language": result.language if result is not None else "",
                "emotion": result.emotion if result is not None else "",
                "error": _redact_secrets(error or "", cfg.get("api_key", "")),
                # Recorded, not sent — see transcribe().
                "context": context or "",
                "log_transcripts": bool(cfg.get("log_transcripts")),
                "note": ("Neither the audio NOR the transcript is persisted by default. "
                         "This microphone is always on in an operating theatre, so most "
                         "of what it hears is conversation about a patient, and run folders "
                         "are copied, shared and attached to papers -- the byte counts, the "
                         "duration and the detected language evidence that the call happened "
                         "without carrying its content. Set log_transcripts=True to keep the "
                         "text for an evaluation. The API key is never recorded, and any "
                         "credential echoed back by the service is redacted out of 'error'."),
            }
            if cfg.get("log_transcripts"):
                record["text"] = result.text if result is not None else ""
            return RunLog.write_json(os.path.join(target, name), record)
        except Exception:
            logger.debug("Could not write the ASR debug artifact", exc_info=True)
            return ""


# --------------------------------------------------------------------------
# Module-level helpers
# --------------------------------------------------------------------------

def _redact_secrets(text: str, api_key: str = "") -> str:
    """Strip anything that could be a credential out of externally-authored text.

    Error bodies and exception strings are both logged AND written into the run
    folder, and this project's threat model says run folders are copied, shared
    and attached to papers (see the module docstring). This module never writes
    the key itself — but the *service* can: an auth failure that echoes the
    offending credential back ("invalid api key: sk-...") arrives as text this
    module did not author, and would then be persisted verbatim.

    Redacting where such text ENTERS a log or an artifact is the only placement
    that scales: the alternative is auditing every current and future producer
    of an error string, and missing one is silent.
    """
    value = text or ""
    if not value:
        return ""
    key = (api_key or "").strip()
    # The length floor keeps a stray one-character "key" from blanking the text.
    if len(key) >= 8 and key in value:
        value = value.replace(key, _REDACTED)
    for pattern in _SECRET_PATTERNS:
        value = pattern.sub(_REDACTED, value)
    return value


def _suffix(detail: str) -> str:
    detail = (detail or "").strip()
    if not detail:
        return ""
    if len(detail) > 400:
        detail = detail[:400] + "..."
    return " - %s" % detail


def _dashscope_error_detail(body: str) -> str:
    """Pull the human-readable message out of a DashScope error body."""
    if not body:
        return ""
    try:
        data = json.loads(body)
    except Exception:
        return body.strip()
    if not isinstance(data, dict):
        return body.strip()
    message = data.get("message")
    if isinstance(message, str) and message.strip():
        code = data.get("code")
        if isinstance(code, str) and code.strip():
            return "%s: %s" % (code.strip(), message.strip())
        return message.strip()
    error = data.get("error")
    if isinstance(error, dict):
        inner = error.get("message")
        if isinstance(inner, str) and inner.strip():
            return inner.strip()
    return body.strip()


def _normalize_mime(mime: str) -> str:
    value = (mime or "").strip().lower()
    if not value:
        return _DEFAULT_MIME
    # Strip any parameters a caller copied from a Content-Type header.
    value = value.split(";")[0].strip()
    return _MIME_ALIASES.get(value, value)


def _probe_wav_seconds(audio_bytes: bytes) -> float:
    """Duration of a WAV clip from its header; 0.0 when it cannot be read.

    Fail-soft on purpose: an unreadable header is the server's problem to
    report, not a reason to refuse to send audio that may be perfectly fine.
    """
    try:
        with wave.open(io.BytesIO(audio_bytes), "rb") as handle:
            rate = handle.getframerate()
            frames = handle.getnframes()
        if rate > 0:
            return float(frames) / float(rate)
    except Exception:
        logger.debug("Could not read WAV duration from the clip header", exc_info=True)
    return 0.0


def _build_silence_wav(seconds: float = _PROBE_SECONDS,
                       sample_rate: int = _PROBE_SAMPLE_RATE) -> bytes:
    """Synthesize mono 16-bit PCM silence wrapped in a real WAV header.

    Built with the stdlib ``wave`` module into a BytesIO rather than by hand:
    a hand-written 44-byte header is exactly the kind of thing that is wrong in
    one field and turns a working connection test into a mystery 400.
    """
    # round(), not int(): seconds is a float, so int() truncates. 0.4 s at
    # 16 kHz is 6400.000000000001 samples today and could as easily be
    # 6399.999999999999 for another pair, which truncates to one sample short.
    # A frame is 2 bytes here (16-bit mono), so frame_count*2 is the payload.
    frame_count = max(1, int(round(sample_rate * max(seconds, 0.0))))
    buffer = io.BytesIO()
    handle = wave.open(buffer, "wb")
    try:
        handle.setnchannels(1)
        handle.setsampwidth(2)  # 16-bit PCM
        handle.setframerate(int(sample_rate))
        handle.writeframes(b"\x00\x00" * frame_count)
    finally:
        handle.close()
    return buffer.getvalue()


def _extract_text(message: Dict[str, Any]) -> str:
    """Join the non-empty ``text`` values of a DashScope content list.

    Defensive because the shape varies: ``content`` is documented as a list of
    dicts, but a plain string and a list of strings both occur in the wild, and
    an empty transcript must come back as "" rather than as a parse error.
    """
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    parts: List[str] = []
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    parts.append(text.strip())
            elif isinstance(item, str) and item.strip():
                parts.append(item.strip())
    return " ".join(parts)


def _extract_audio_info(message: Dict[str, Any]) -> Tuple[str, str]:
    """Return (language, emotion) from the ``audio_info`` annotation, if present."""
    annotations = message.get("annotations")
    if not isinstance(annotations, list):
        return "", ""
    for item in annotations:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "audio_info":
            language = item.get("language")
            emotion = item.get("emotion")
            return (language if isinstance(language, str) else "",
                    emotion if isinstance(emotion, str) else "")
    return "", ""


def _parse_response(data: Dict[str, Any], seconds: float,
                    audio_seconds: float) -> TranscriptionResult:
    """Normalize a DashScope native ASR response into a TranscriptionResult."""
    if not isinstance(data, dict):
        raise RuntimeError("Speech-to-text returned an unexpected response type: %s"
                           % type(data).__name__)

    output = data.get("output")
    if not isinstance(output, dict):
        # A 200 that carries an error object instead of output.
        detail = _dashscope_error_detail(json.dumps(data, ensure_ascii=False))
        raise RuntimeError("Speech-to-text returned no transcription output%s" % _suffix(detail))

    choices = output.get("choices")
    message: Dict[str, Any] = {}
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            candidate = first.get("message")
            if isinstance(candidate, dict):
                message = candidate

    text = _extract_text(message)
    language, emotion = _extract_audio_info(message)

    # usage.seconds is the billed audio length; it is the better number when
    # the caller did not know the duration and the clip was not a readable WAV.
    resolved_audio_seconds = float(audio_seconds or 0.0)
    if resolved_audio_seconds <= 0.0:
        usage = data.get("usage")
        if isinstance(usage, dict):
            try:
                resolved_audio_seconds = float(usage.get("seconds") or 0.0)
            except (TypeError, ValueError):
                resolved_audio_seconds = 0.0

    request_id = data.get("request_id")
    return TranscriptionResult(
        text=text,
        language=language,
        emotion=emotion,
        seconds=seconds,
        audio_seconds=resolved_audio_seconds,
        request_id=request_id if isinstance(request_id, str) else "",
        raw=data,
    )
