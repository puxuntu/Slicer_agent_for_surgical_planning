"""Turning a transcribed sentence into one action against the step on screen.

This resolver is built to **decline**. An utterance resolves only against the
closed vocabulary the current step actually offers, and anything below the
acceptance floor becomes ``ACTION_NONE`` rather than a guess. Answering the
wrong orbit is not a worse version of doing nothing; it is a different kind of
event entirely.

That discipline was designed for an always-on microphone, which saw every
sentence spoken in the room. Capture is now normally gated by a push-to-talk
key, so most of that traffic never arrives here -- but the always-on mode is
still available behind a setting, and the discipline earns its place either way.
A held key says *when* somebody is addressing the application, not *what* they
said, and a recogniser working from a quiet theatre microphone still hands this
module sentences nobody uttered.

Two tiers, in this order:

1. **Deterministic.** Fixed verbs (done / skip / repeat / explain / exit), the
   step's own option labels, live node and segment names, ordinals, and numbers.
   No network, no model, fully auditable, and it answers the overwhelming
   majority of utterances -- 27 of the 49 decision points in the shipped
   packages have a finite label list, and every one of the 26 interaction steps
   is answered by the single word "done".
2. **LLM fallback**, only when tier 1 is *uncertain* -- not when it is empty.
   A sentence that matched nothing at all is more likely to be a mis-recognition
   or an aside than a paraphrase, so sending it to a model mostly buys a
   confident-sounding wrong answer. The fallback is offered the step's options
   as the *only* candidates and is required to return an index, so it can rename
   an option but never invent one.

Free text is the one family where a bare utterance is never accepted: it needs
an explicit "set" / "enter" lead-in, because a free-text step would otherwise
record whatever the recogniser produced as the parameter value.
"""

from __future__ import annotations

import difflib
import json
import logging
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from . import grammar as _grammar
from .grammar import StepGrammar

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Actions. These map 1:1 onto a panel control (see widget_voice.py's dispatch
# table); nothing else is reachable by voice, by construction.
# ---------------------------------------------------------------------------
ACTION_NONE = "none"
ACTION_START_WORKFLOW = "start_workflow"
ACTION_PROCEED = "proceed"
ACTION_SKIP = "skip"
ACTION_CHOICE = "choice"
ACTION_NODE = "node"
ACTION_SEGMENT_NAME = "segment_name"
ACTION_SEGMENT_VISIBILITY = "segment_visibility"
ACTION_SCALAR = "scalar"
ACTION_RANGE = "range"
ACTION_TEXT = "text"
ACTION_MULTI = "multi"
ACTION_REPEAT = "repeat"
ACTION_DETAILS = "details"
ACTION_OPTIONS = "options"
ACTION_STATUS = "status"
ACTION_BACK = "back"
ACTION_FORWARD = "forward"
ACTION_EXIT = "exit"
ACTION_CONFIRM = "confirm"
ACTION_ABORT = "abort"
ACTION_STOP_LISTENING = "stop_listening"

#: Actions that change the scene or the run. These are the ones the optional
#: "confirm before acting" setting arms rather than executes.
COMMITTING_ACTIONS = frozenset({
    ACTION_PROCEED, ACTION_SKIP, ACTION_CHOICE, ACTION_NODE,
    ACTION_SEGMENT_NAME, ACTION_SEGMENT_VISIBILITY, ACTION_SCALAR,
    ACTION_RANGE, ACTION_TEXT, ACTION_MULTI, ACTION_BACK, ACTION_FORWARD,
    ACTION_EXIT, ACTION_START_WORKFLOW,
})

#: Below this, tier 1 has not matched. Above ``STRONG`` it is treated as certain
#: and the LLM is never consulted, even when it is enabled.
ACCEPT_SCORE = 0.62
STRONG_SCORE = 0.86
#: Two candidates this close together are a tie, not a winner.
AMBIGUITY_MARGIN = 0.07

SOURCE_DETERMINISTIC = "deterministic"
SOURCE_LLM = "llm"
SOURCE_NONE = "none"

VOICE_COMMAND_PROMPT = "voice_command_prompt.md"

_FALLBACK_PROMPT = (
    "Map the surgeon's spoken sentence onto exactly one option of the control "
    "on screen, or onto no action. Reply with JSON only: "
    '{"action": "...", "index": <int or null>, "value": <string or null>, '
    '"confidence": <0..1>, "reason": "..."}'
)


# ---------------------------------------------------------------------------
# Fixed verbs. Matched as whole phrases against the normalised utterance, longest
# phrase first, so "step back" cannot be eaten by "back".
# ---------------------------------------------------------------------------
_VERBS = (
    (ACTION_STOP_LISTENING, (
        "stop listening", "stop the microphone", "stop the mic", "microphone off",
        "mic off", "turn off the microphone", "turn the microphone off",
        "mute the microphone", "stop voice control", "voice off",
    )),
    (ACTION_EXIT, (
        "exit the workflow", "exit workflow", "exit the procedure",
        "exit procedure", "stop the workflow", "stop the procedure",
        "quit the workflow", "quit the procedure", "abort the procedure",
        "abandon the procedure", "close the workflow", "end the procedure",
    )),
    (ACTION_DETAILS, (
        "explain that", "explain this", "explain the step", "explain",
        "more detail", "more details", "tell me more", "why am i doing this",
        "why", "in detail", "read the details",
    )),
    (ACTION_OPTIONS, (
        "what are my options", "what are the options", "list the options",
        "what can i say", "what can i choose", "options",
    )),
    (ACTION_STATUS, (
        "where am i", "what step is this", "which step", "how far along",
        "status",
    )),
    (ACTION_REPEAT, (
        "say that again", "say it again", "repeat that", "repeat the step",
        "repeat", "come again", "what do i do", "what should i do",
        "what was that", "again please",
    )),
    (ACTION_BACK, (
        "step back", "go back", "previous step", "go to the previous step",
        "back a step", "one step back",
    )),
    (ACTION_FORWARD, (
        "step forward", "go forward", "forward a step", "one step forward",
        "next in the timeline",
    )),
    (ACTION_SKIP, (
        "skip this step", "skip the step", "skip this", "skip it", "skip",
    )),
    # "ready" and "go ahead" are deliberately NOT here. With a hot microphone
    # they are among the most common things said in a theatre to somebody other
    # than the computer, and advancing a user_interaction step early ends a
    # markup placement mid-way. The phrases kept are the ones a person says to a
    # machine; the residual risk of the bare ones ("next", "done") is inherent
    # to a no-wake-word design and is what "confirm before acting" answers.
    (ACTION_PROCEED, (
        "i am done", "i'm done", "im done", "that's done", "thats done",
        "all done", "done with this", "finished", "i have finished",
        "next step", "go to the next step", "move on", "carry on",
        "continue", "proceed", "keep going", "next", "done",
        "ok next", "okay next",
    )),
)

# Confirm-mode vocabulary. "right", "ok" and "okay" are DELIBERATELY absent:
# they are ordinary conversational filler, and "right" is also the semantic value
# of an option on the orbital step -- a surgeon saying "right" to mean the right
# orbit would have confirmed a pending "Blue box" instead of correcting it. Every
# phrase kept here is unambiguous as an assent.
_AFFIRMATIVE = ("yes", "yeah", "yep", "yup", "correct", "confirm", "confirmed",
                "do it", "go ahead", "that's right", "thats right", "affirmative")
_NEGATIVE = ("no", "nope", "cancel", "cancel that", "never mind", "nevermind",
             "stop", "wrong", "not that", "forget it", "abort", "undo that")

#: What to accept for an option whose label is punctuation only (see
#: _aliases_for_choice). Deliberately a small, unambiguous set: these words must
#: not collide with a real label on the same step, and "none"/"neither" are what
#: a surgeon says for an empty selector.
_UNSPEAKABLE_ALIASES = ("none", "neither", "not applicable", "no side", "blank")

# Free text is the only family where the utterance itself becomes the value, so
# the lead-in has to be a verb aimed at the application. Bare "use" and "make
# it" were removed: they open ordinary theatre sentences ("use the 2.5 driver")
# and would have recorded them as the parameter.
_TEXT_LEAD_INS = ("set it to", "set the value to", "set value to", "set to",
                  "set", "enter", "type", "use the value", "value is",
                  "call it", "name it")

# True ordinals only. A bare cardinal is deliberately NOT an ordinal here: "the
# blue one" and "the red one" are the natural way to name an option by colour,
# and reading the trailing "one" as an index silently selects option 1 for BOTH
# -- which on the orbital step is the wrong side of the head, in a run that then
# completes and reports success. Cardinals are accepted only after an explicit
# anchor noun ("option two"), via _CARDINALS below.
_ORDINALS = {
    "first": 0, "1st": 0,
    "second": 1, "2nd": 1,
    "third": 2, "3rd": 2,
    "fourth": 3, "4th": 3,
    "fifth": 4, "5th": 4,
    "sixth": 5, "6th": 5,
    "seventh": 6, "7th": 6,
    "eighth": 7, "8th": 7,
    "ninth": 8, "9th": 8,
    "tenth": 9, "10th": 9,
}
_CARDINALS = {
    "one": 0, "two": 1, "three": 2, "four": 3, "five": 4,
    "six": 5, "seven": 6, "eight": 7, "nine": 8, "ten": 9,
}
_ORDINAL_ANCHORS = ("option", "choice", "number", "item", "answer")

# Words that carry no identity in a spoken command. Stripped before scoring so
# "the red one please" still reaches the "Red box" label -- without this the
# filler dilutes the token overlap below the acceptance floor and the utterance
# falls through to a much weaker heuristic.
_FILLER = frozenset((
    "the", "a", "an", "please", "just", "now", "then", "ok", "okay", "yeah",
    "select", "selects", "selected", "pick", "picks", "choose", "chose", "use",
    "using", "set", "go", "with", "for", "of", "it", "its", "that", "this",
    "these", "those", "one", "ones", "thing", "i", "id", "ill", "im", "we",
    "want", "wanna", "would", "like", "to", "lets", "let", "do", "does",
    "make", "take", "give", "me", "my", "is", "was", "be", "and",
))

_UNITS = {
    "zero": 0, "oh": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fourty": 40, "fifty": 50,
         "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
_SCALES = {"hundred": 100, "thousand": 1000, "million": 1000000}
_RANGE_CONNECTORS = ("to", "through", "thru", "until", "till", "and", "dash",
                     "minus", "-", "–", "—")

_WORD_RE = re.compile(r"[a-z0-9.+-]+")
_NUMBER_RE = re.compile(r"^[+-]?\d+(?:\.\d+)?$")


class VoiceCommand(object):
    """One resolved intent, plus everything needed to explain or refuse it."""

    __slots__ = ("action", "value", "label", "confidence", "source",
                 "rationale", "transcript", "options", "extra")

    def __init__(self, action=ACTION_NONE, value=None, label="", confidence=0.0,
                 source=SOURCE_NONE, rationale="", transcript="",
                 options=None, extra=None):
        self.action = action
        self.value = value
        self.label = label
        self.confidence = float(confidence)
        self.source = source
        self.rationale = rationale
        self.transcript = transcript
        self.options = options or []
        self.extra = extra or {}

    def __bool__(self):
        return self.action != ACTION_NONE

    __nonzero__ = __bool__

    def is_committing(self) -> bool:
        return self.action in COMMITTING_ACTIONS

    def describe(self) -> str:
        """One short sentence, safe to speak back as an acknowledgement."""
        if self.action == ACTION_CHOICE:
            return "Selecting %s." % (self.label or self.value)
        if self.action == ACTION_NODE:
            return "Selecting %s." % (self.label or self.value)
        if self.action == ACTION_SEGMENT_NAME:
            return "Selecting segment %s." % (self.label or self.value)
        if self.action == ACTION_SEGMENT_VISIBILITY:
            shown = "Showing" if self.extra.get("visible") else "Hiding"
            return "%s %s." % (shown, self.label)
        if self.action == ACTION_SCALAR:
            return "Setting %s to %s." % (self.label or "the value", _fmt(self.value))
        if self.action == ACTION_RANGE:
            pair = self.value or [0, 0]
            return "Setting %s from %s to %s." % (
                self.label or "the range", _fmt(pair[0]), _fmt(pair[1]))
        if self.action == ACTION_TEXT:
            return "Entering %s." % self.value
        if self.action == ACTION_MULTI:
            return "Setting " + ", ".join(
                "%s to %s" % (k, v) for k, v in sorted((self.value or {}).items()))
        if self.action == ACTION_PROCEED:
            return "Continuing."
        if self.action == ACTION_SKIP:
            return "Skipping this step."
        if self.action == ACTION_BACK:
            return "Stepping back."
        if self.action == ACTION_FORWARD:
            return "Stepping forward."
        if self.action == ACTION_EXIT:
            return "Exiting the workflow."
        if self.action == ACTION_START_WORKFLOW:
            return "Starting the procedure."
        return ""

    def to_log(self, include_transcript: bool = False) -> Dict[str, Any]:
        """A role-trace record. The transcript is withheld by default.

        ``role_trace.json`` is written into the run folder, so including the raw
        utterance would put theatre conversation there by another door -- the
        same reason the ASR client does not persist it. What was DECIDED is
        always recorded; what was overheard is opt-in.
        """
        record = {
            "action": self.action,
            "label": self.label,
            "value": self.value if _jsonable(self.value) else str(self.value),
            "confidence": round(self.confidence, 3),
            "source": self.source,
            "rationale": self.rationale,
            "transcript_chars": len(self.transcript or ""),
            "options": list(self.options),
        }
        if include_transcript:
            record["transcript"] = self.transcript
        return record


def _jsonable(value) -> bool:
    return isinstance(value, (str, int, float, bool, type(None), list, dict))


def _fmt(value) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return ("%.3f" % number).rstrip("0").rstrip(".")


# ---------------------------------------------------------------------------
# Normalisation and scoring
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    """Lower-case, strip punctuation, collapse whitespace.

    Hyphens and dots survive only inside a token that still looks numeric, so
    "3.5" and "T-12" keep their shape while "Yes, adjust more" loses its comma.
    """
    lowered = str(text or "").lower().replace("’", "'")
    lowered = re.sub(r"[^a-z0-9.+\-\s]", " ", lowered)
    tokens = []
    for token in lowered.split():
        token = token.strip(".-+")
        if token:
            tokens.append(token)
    return " ".join(tokens)


def _tokens(text: str) -> List[str]:
    return normalize(text).split()


def _aliases_for_choice(choice: Dict[str, Any]) -> List[str]:
    """Every phrasing that should select this option.

    Real shipped labels carry clauses nobody says out loud -- "No (go to step
    12)", "Yes, adjust more", "Yes (check box)". The first clause is therefore an
    alias in its own right. The VALUE word is included too so "right" reaches the
    "Red box" option on the orbital step, but only as an alias: the label stays
    the primary match, because the panel deliberately asks the colour question
    the surgeon is looking at.
    """
    out = []
    for key in ("label", "raw_label"):
        label = str(choice.get(key) or "").strip()
        if not label:
            continue
        out.append(label)
        head = re.split(r"[(,;/]| - ", label)[0].strip()
        if head and head.lower() != label.lower():
            out.append(head)
    value = choice.get("value")
    if isinstance(value, str) and value.strip():
        out.append(value.strip())
        out.append(value.strip().replace("_", " "))
    elif value is True:
        out.extend(("yes", "yeah", "yep", "affirmative", "correct"))
    elif value is False:
        out.extend(("no", "nope", "negative"))
    seen, unique = set(), []
    for alias in out:
        key = normalize(alias)
        if key and key not in seen:
            seen.add(key)
            unique.append(alias)
    if not unique:
        # A label made only of punctuation has no pronounceable form and would
        # be unreachable by voice. PedicleScrewPlanner's "# Sides" selector ships
        # exactly this: its fourth option is "--", the extension's own way of
        # writing "neither side". Give such an option the words a person would
        # actually use, rather than leaving one choice of a real step
        # unspeakable.
        unique = list(_UNSPEAKABLE_ALIASES)
    return unique


def _strip_filler(normalized: str) -> str:
    """Drop carrier words, but never everything -- an all-filler phrase stands."""
    kept = [t for t in normalized.split() if t not in _FILLER]
    return " ".join(kept) if kept else normalized


_WORD_FOR_DIGIT = {v: k for k, v in _UNITS.items() if k != "oh"}


def _spell_digits(normalized: str) -> str:
    """"fragment 1" -> "fragment one"."""
    out = []
    for token in normalized.split():
        if token.isdigit() and int(token) in _WORD_FOR_DIGIT:
            out.append(_WORD_FOR_DIGIT[int(token)])
        else:
            out.append(token)
    return " ".join(out)


def _digitise_words(normalized: str) -> str:
    """"fragment one" -> "fragment 1"."""
    out = []
    for token in normalized.split():
        if token in _UNITS and token != "oh":
            out.append(str(_UNITS[token]))
        else:
            out.append(token)
    return " ".join(out)


def _variants(normalized: str, strip_filler: bool) -> List[str]:
    """The few spellings of one phrase that must compare as equal.

    Slicer names nodes and segments with trailing numerals ("Fragment 1"), and a
    person says "fragment one". Without a numeral variant those two score no
    better than "Fragment 2" does, and a step with two numbered fragments
    resolves to an ambiguity -- or, worse, to whichever one difflib happens to
    like. Generated here rather than baked into ``normalize`` so the raw form is
    still what an exact match is measured against.
    """
    seen, out = set(), []
    candidates = [normalized]
    if strip_filler:
        candidates.append(_strip_filler(normalized))
    for base in list(candidates):
        candidates.append(_spell_digits(base))
        candidates.append(_digitise_words(base))
    for candidate in candidates:
        if candidate and candidate not in seen:
            seen.add(candidate)
            out.append(candidate)
    return out


def match_score(utterance: str, candidate: str) -> float:
    """0..1 similarity, tuned for short spoken phrases against short labels.

    Scored over a small cross product of spellings -- verbatim, carrier words
    removed, numerals spelled out, number words digitised -- taking the best.
    "Blue box" said as "the blue one please" only reaches the label once the
    filler is gone, and "Fragment 1" only beats "Fragment 2" for the utterance
    "fragment one" once the numeral forms line up.
    """
    utterance_n = normalize(utterance)
    candidate_n = normalize(candidate)
    best = 0.0
    for u in _variants(utterance_n, strip_filler=True):
        for c in _variants(candidate_n, strip_filler=False):
            score = _match_score_one(u, c)
            if score > best:
                best = score
                if best >= 1.0:
                    return 1.0
    return best


def _match_score_one(utterance_n: str, candidate_n: str) -> float:
    if not utterance_n or not candidate_n:
        return 0.0
    if utterance_n == candidate_n:
        return 1.0

    u_tokens = utterance_n.split()
    c_tokens = candidate_n.split()
    u_set, c_set = set(u_tokens), set(c_tokens)

    # Every heuristic is scored and the BEST one wins. Returning from the first
    # one that fires looks equivalent and is not: token overlap is the weakest
    # signal and fires most often, so an early return there hides a much
    # stronger character-level match. "case 01 ct cropped" against
    # "Case01_CT_cropped" scores 0.59 on overlap (below the floor, so refused)
    # and 0.85 on the character ratio.
    scores = [0.0]

    # The whole label appears inside what was said ("select the red box").
    if _contains_sequence(u_tokens, c_tokens):
        scores.append(0.94)
    # What was said is the head of the label ("red" -> "Red box"). A one-word
    # utterance scores lower: it may merely share a prefix with the label.
    if len(c_tokens) > len(u_tokens) and _contains_sequence(c_tokens, u_tokens):
        scores.append(0.88 if len(u_tokens) > 1 else 0.80)

    overlap = len(u_set & c_set)
    if overlap:
        coverage = float(overlap) / float(len(c_set))
        precision = float(overlap) / float(len(u_set))
        f1 = 2 * coverage * precision / (coverage + precision)
        if f1 >= 0.5:
            scores.append(0.55 + 0.30 * min(1.0, (f1 - 0.5) / 0.5))

    ratio = difflib.SequenceMatcher(None, utterance_n, candidate_n).ratio()
    if ratio >= 0.82:
        scores.append(0.60 + 0.30 * (ratio - 0.82) / 0.18)
    return max(scores)


def _contains_sequence(haystack: List[str], needle: List[str]) -> bool:
    if not needle or len(needle) > len(haystack):
        return False
    for start in range(len(haystack) - len(needle) + 1):
        if haystack[start:start + len(needle)] == needle:
            return True
    return False


def _best_match(utterance: str, entries: List[Tuple[Any, List[str]]]
                ) -> Tuple[Optional[Any], float, List[Any]]:
    """Score every entry by its best alias; return (winner, score, ties)."""
    scored = []
    for payload, aliases in entries:
        best = 0.0
        for alias in aliases:
            score = match_score(utterance, alias)
            if score > best:
                best = score
        scored.append((best, payload))
    if not scored:
        return None, 0.0, []
    scored.sort(key=lambda item: item[0], reverse=True)
    top_score, top_payload = scored[0]
    if top_score < ACCEPT_SCORE:
        return None, top_score, []
    ties = [payload for score, payload in scored[1:]
            if top_score - score <= AMBIGUITY_MARGIN and score >= ACCEPT_SCORE]
    if ties:
        return None, top_score, [top_payload] + ties
    return top_payload, top_score, []


# ---------------------------------------------------------------------------
# Numbers
# ---------------------------------------------------------------------------

def _trim_token(raw: str) -> str:
    """Strip decoration from a token WITHOUT eating a leading minus sign.

    ``"-10".strip(".-+")`` is ``"10"``, so a threshold of minus one thousand
    twenty four -- the bottom of a CT window, and the single most common negative
    number in this application -- silently became positive. Trailing punctuation
    is always dropped; a leading sign survives only when what follows is a
    number.
    """
    token = raw.rstrip(".-+")
    if not token:
        return ""
    if _NUMBER_RE.match(token):
        return token
    return token.strip(".-+")


def extract_numbers(text: str) -> List[float]:
    """Every number in an utterance, digits or words, in spoken order.

    ``enable_itn`` normally makes the ASR emit digits, but it is documented for
    Chinese and English only and can be switched off, so the word forms are
    parsed here too rather than assumed away.
    """
    tokens = [t for t in (_trim_token(raw) for raw
                          in _WORD_RE.findall(str(text or "").lower())) if t]
    numbers = []
    run = []
    negative = False

    def flush():
        """Emit the pending word-run; True when it produced a number."""
        sign = negative
        emitted = False
        if run:
            value = _words_to_number(run)
            if value is not None:
                numbers.append(-value if sign else value)
                emitted = True
            del run[:]
        return emitted

    position = 0
    while position < len(tokens):
        token = tokens[position]
        position += 1
        if token in ("minus", "negative"):
            if flush():
                negative = False
            negative = True
            continue
        if _NUMBER_RE.match(token):
            if flush():
                # The sign was consumed by the run that just closed.
                negative = False
            value = float(token)
            numbers.append(-value if negative else value)
            negative = False
            continue
        if token in _UNITS or token in _TENS or token in _SCALES or token == "point":
            run.append(token)
            continue
        if token == "and" and _and_continues_number(run, tokens, position):
            # "one hundred and twenty" is one number; "between two hundred and
            # three thousand" is two. The difference is whether what follows the
            # "and" is a bare tens/units word or the start of a larger magnitude,
            # which is exactly the lookahead below.
            continue
        flush()
        del run[:]
        negative = False
    flush()
    return numbers


def _and_continues_number(run: List[str], tokens: List[str], position: int) -> bool:
    """True when "and" joins a scale to its remainder rather than separating."""
    if not run or run[-1] not in _SCALES:
        return False
    if position >= len(tokens):
        return False
    following = tokens[position]
    if following not in _UNITS and following not in _TENS:
        return False
    after = tokens[position + 1] if position + 1 < len(tokens) else ""
    return after not in _SCALES


def _words_to_number(words: List[str]) -> Optional[float]:
    """"three thousand two hundred and fifty" -> 3250.0; "one point five" -> 1.5."""
    if "point" in words:
        head = words[:words.index("point")]
        tail = words[words.index("point") + 1:]
        whole = _words_to_number(head) if head else 0.0
        digits = "".join(str(_UNITS[w]) for w in tail if w in _UNITS)
        if whole is None or not digits:
            return whole
        return float("%d.%s" % (int(whole), digits))
    total, current, seen = 0.0, 0.0, False
    for word in words:
        if word in _UNITS:
            current += _UNITS[word]
            seen = True
        elif word in _TENS:
            current += _TENS[word]
            seen = True
        elif word in _SCALES:
            scale = _SCALES[word]
            seen = True
            if scale == 100:
                current = (current or 1) * 100
            else:
                total += (current or 1) * scale
                current = 0.0
        else:
            return None
    return (total + current) if seen else None


def _looks_like_range(text: str) -> bool:
    tokens = _tokens(text)
    return any(token in _RANGE_CONNECTORS for token in tokens) or "between" in tokens


def _build_positional_phrases() -> Dict[str, int]:
    """Whole-utterance phrases that mean "the Nth option", and nothing else.

    Positional selection is matched as an EXACT phrase, never by finding an
    ordinal somewhere in a sentence. That is not fussiness: with a hot
    microphone the ordinal path is reached precisely when label matching has
    failed, which is the state ordinary conversation is in, and "just a second"
    then selects option two. On the orbital step option two is the other side of
    the head, in a run that completes and reports success.

    No amount of token filtering rescues the loose form -- "just a second" and
    "that was the last one" both survive a stopword filter, and both contain a
    perfectly good ordinal. So the phrase has to be the whole thing the person
    said. Nothing is really lost: every option's label is read aloud in the
    prompt, so saying the label is always available and is always safer.
    """
    ordinals = ["first", "second", "third", "fourth", "fifth",
                "sixth", "seventh", "eighth", "ninth", "tenth"]
    cardinals = ["one", "two", "three", "four", "five",
                 "six", "seven", "eight", "nine", "ten"]
    phrases = {}

    def add(phrase, index):
        key = normalize(phrase)
        if key and key not in phrases:
            phrases[key] = index

    for index in range(len(ordinals)):
        word = ordinals[index]
        number = str(index + 1)
        cardinal = cardinals[index]
        add(word, index)
        add("the " + word, index)
        add(word + " one", index)
        add("the " + word + " one", index)
        for anchor in _ORDINAL_ANCHORS:
            for tail in (number, cardinal, word):
                add("%s %s" % (anchor, tail), index)
                add("the %s %s" % (anchor, tail), index)
    return phrases


_POSITIONAL_PHRASES = _build_positional_phrases()
_LAST_PHRASES = frozenset(normalize(p) for p in
                          ("last", "the last", "last one", "the last one",
                           "the last option", "bottom one", "the bottom one"))
_ONLY_PHRASES = frozenset(normalize(p) for p in
                          ("only one", "the only one", "the only option",
                           "the only candidate"))


def _ordinal_index(text: str, count: int) -> Optional[int]:
    """"the third one" / "option 2" / "the last one" -> a 0-based index.

    Whole-utterance only -- see ``_build_positional_phrases``.
    """
    if count <= 0:
        return None
    normalized = normalize(text)
    if not normalized:
        return None
    # Only the polite wrapper is tolerated, matching _match_verb.
    normalized = re.sub(r"^(ok|okay|alright|now|please)\s+", "", normalized)
    normalized = re.sub(r"\s+(please|thanks|thank you)$", "", normalized).strip()
    if normalized in _LAST_PHRASES:
        return count - 1
    if normalized in _ONLY_PHRASES:
        return 0 if count == 1 else None
    index = _POSITIONAL_PHRASES.get(normalized)
    if index is not None and 0 <= index < count:
        return index
    return None


def _strip_lead_in(text: str) -> Optional[str]:
    """Remove a free-text lead-in verb; None when there is none.

    Requiring the lead-in is what stops a free-text step from recording whatever
    was said in the room as the parameter value.
    """
    normalized = normalize(text)
    for lead in _TEXT_LEAD_INS:
        if normalized == lead:
            return ""
        if normalized.startswith(lead + " "):
            return normalized[len(lead) + 1:].strip()
    return None


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------

def resolve(transcript: str,
            step: Optional[StepGrammar],
            allow_llm: bool = True,
            llm_call: Optional[Callable[[str, str], str]] = None,
            confirmation_pending: bool = False) -> VoiceCommand:
    """Map ``transcript`` to one action against ``step``.

    ``llm_call(system_prompt, user_prompt) -> raw_reply`` is injected rather than
    imported so this module stays Qt-free and testable, and so the caller keeps
    ownership of which client, which budget and which log folder the fallback
    call belongs to.
    """
    text = str(transcript or "").strip()
    if not text:
        return VoiceCommand(transcript=text)

    normalized = normalize(text)
    if not normalized:
        return VoiceCommand(transcript=text)

    # A pending confirmation owns yes/no outright. Without this precedence a
    # "yes" meant to confirm a resolved command would instead be re-matched as
    # the Yes option of the branch step underneath it.
    if confirmation_pending:
        if _matches_any(normalized, _AFFIRMATIVE_N):
            return VoiceCommand(ACTION_CONFIRM, confidence=1.0,
                                source=SOURCE_DETERMINISTIC, transcript=text)
        if _matches_any(normalized, _NEGATIVE_N):
            return VoiceCommand(ACTION_ABORT, confidence=1.0,
                                source=SOURCE_DETERMINISTIC, transcript=text)

    verb = _match_verb(normalized)

    if step is None or not step.workflow_active:
        # Nothing is running. Only the microphone verbs are meaningful; anything
        # else is a request, and the router decides whether it names a procedure.
        if verb in (ACTION_STOP_LISTENING, ACTION_REPEAT, ACTION_STATUS):
            return VoiceCommand(verb, confidence=1.0,
                                source=SOURCE_DETERMINISTIC, transcript=text)
        return VoiceCommand(ACTION_START_WORKFLOW, value=text, confidence=0.5,
                            source=SOURCE_DETERMINISTIC, transcript=text,
                            rationale="no workflow active; routed as a request")

    if verb is not None:
        gated = _gate_verb(verb, step)
        if gated is not None:
            return VoiceCommand(gated[0], confidence=1.0,
                                source=SOURCE_DETERMINISTIC, transcript=text,
                                rationale=gated[1])

    command = _resolve_value(text, normalized, step)
    if command is not None:
        return command

    if allow_llm and llm_call is not None and step.expects_value():
        fallback = _resolve_with_llm(text, step, llm_call)
        if fallback is not None:
            return fallback

    return VoiceCommand(transcript=text, rationale="no confident match")


def _normalized_set(phrases) -> frozenset:
    """Phrase tables are authored readably and compared normalised.

    Without this, "i'm done" never matches: the utterance has already been
    through ``normalize`` (which drops the apostrophe) while the table entry
    still carries it.
    """
    return frozenset(normalize(p) for p in phrases if normalize(p))


_AFFIRMATIVE_N = _normalized_set(_AFFIRMATIVE)
_NEGATIVE_N = _normalized_set(_NEGATIVE)

#: normalised phrase -> action. Built in _VERBS order so the first table that
#: claims a phrase keeps it (the tables are ordered by priority).
_VERB_LOOKUP = {}
for _action, _phrases in _VERBS:
    for _phrase in _phrases:
        _key = normalize(_phrase)
        if _key and _key not in _VERB_LOOKUP:
            _VERB_LOOKUP[_key] = _action
del _action, _phrases, _phrase, _key


def explain(transcript: str, step: Optional[StepGrammar],
            limit: int = 5) -> List[Tuple[str, float]]:
    """Score every candidate the step offers, best first, for a debug trace.

    "It did not match" is the least useful thing this module can say. The score
    against each option answers the actual question -- whether the utterance was
    close and lost to the acceptance floor, close to TWO options and refused as
    ambiguous, or nowhere near any of them (which usually means the recogniser
    heard something other than what was said).
    """
    if step is None:
        return []
    entries = []
    if step.family == _grammar.FAMILY_CHOICES:
        entries = [(c.get("label", ""), _aliases_for_choice(c)) for c in step.choices]
    elif step.family == _grammar.FAMILY_NODE:
        entries = [(n.get("name", ""), [n.get("name", "")]) for n in step.nodes]
    elif step.family in (_grammar.FAMILY_SEGMENT_NAME, _grammar.FAMILY_SEGMENT_REF):
        entries = [(n, [n]) for n in step.segment_names]
    elif step.family == _grammar.FAMILY_SEGMENTS_TABLE:
        entries = [(s.get("name", ""), [s.get("name", "")]) for s in step.segments]
    elif step.family == _grammar.FAMILY_MULTI:
        for item in step.multi_items:
            for option in (item.get("options") or []):
                entries.append((str(option), [str(option)]))
    scored = []
    for label, aliases in entries:
        best = 0.0
        for alias in aliases:
            score = match_score(transcript, alias)
            if score > best:
                best = score
        scored.append((label, round(best, 3)))
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return scored[:limit]


def resolve_llm(transcript: str, step: Optional[StepGrammar],
                llm_call: Optional[Callable[[str, str], str]]) -> Optional[VoiceCommand]:
    """The second tier on its own, for callers that must run it off-thread.

    ``resolve`` can chain both tiers, which is convenient in a test but wrong in
    the application: tier 1 is pure computation and belongs on the Qt main
    thread beside the panel it reads, while tier 2 is an HTTP round trip that
    would freeze Slicer there. Splitting them lets the caller run tier 1
    synchronously and hand only the leftovers to a worker.
    """
    if step is None or llm_call is None or not step.expects_value():
        return None
    text = str(transcript or "").strip()
    if not text:
        return None
    return _resolve_with_llm(text, step, llm_call)


def _matches_any(normalized: str, phrases) -> bool:
    return normalized in phrases


def _match_verb(normalized: str) -> Optional[str]:
    """Fixed-verb match against the WHOLE utterance.

    Whole-utterance only, deliberately. Substring matching would make every
    sentence containing the word "done" advance the workflow, which with an
    always-on microphone is a scene change caused by a conversation.
    """
    action = _VERB_LOOKUP.get(normalized)
    if action is not None:
        return action
    # One tolerated form: a polite wrapper ("ok, next step please").
    stripped = re.sub(r"^(ok|okay|alright|alrighty|now|please|slicer|hey slicer)\s+",
                      "", normalized)
    stripped = re.sub(r"\s+(please|now|thanks|thank you)$", "", stripped).strip()
    if stripped and stripped != normalized:
        return _VERB_LOOKUP.get(stripped)
    return None


def _gate_verb(verb: str, step: StepGrammar) -> Optional[Tuple[str, str]]:
    """Refuse a verb the step cannot honour, instead of dispatching it blindly.

    The panel handlers do not re-check visibility -- ``_onWorkflowDoneClicked``
    dispatches ``proceed`` whenever a step id is set, even where the button is
    hidden -- so the check has to happen here.
    """
    if verb == ACTION_PROCEED:
        # No Done button on this step. Returning None lets the utterance fall
        # through to value matching, which is what makes "yes"/"no" still work
        # on a branch step where "next" would have been meaningless.
        return (ACTION_PROCEED, "") if step.can_done else None
    if verb == ACTION_SKIP:
        return (ACTION_SKIP, "") if step.can_skip else None
    if verb == ACTION_BACK:
        return (ACTION_BACK, "") if step.can_back else None
    if verb == ACTION_FORWARD:
        return (ACTION_FORWARD, "") if step.can_forward else None
    return (verb, "")


def _resolve_value(text: str, normalized: str, step: StepGrammar
                   ) -> Optional[VoiceCommand]:
    family = step.family

    if family == _grammar.FAMILY_CHOICES:
        entries = [(choice, _aliases_for_choice(choice)) for choice in step.choices]
        winner, score, ties = _best_match(text, entries)
        if winner is not None:
            return VoiceCommand(ACTION_CHOICE, value=winner.get("value"),
                                label=winner.get("label"), confidence=score,
                                source=SOURCE_DETERMINISTIC, transcript=text)
        if ties:
            return VoiceCommand(transcript=text, confidence=score,
                                options=[t.get("label") for t in ties],
                                rationale="ambiguous between several options")
        index = _ordinal_index(text, len(step.choices))
        if index is not None:
            choice = step.choices[index]
            return VoiceCommand(ACTION_CHOICE, value=choice.get("value"),
                                label=choice.get("label"), confidence=0.75,
                                source=SOURCE_DETERMINISTIC, transcript=text,
                                rationale="matched by position")
        return None

    if family == _grammar.FAMILY_NODE:
        entries = [(node, [node.get("name", "")]) for node in step.nodes]
        winner, score, ties = _best_match(text, entries)
        if winner is not None:
            return VoiceCommand(ACTION_NODE, value=winner.get("name"),
                                label=winner.get("name"), confidence=score,
                                source=SOURCE_DETERMINISTIC, transcript=text,
                                extra={"node_id": winner.get("id")})
        if ties:
            return VoiceCommand(transcript=text, confidence=score,
                                options=[t.get("name") for t in ties],
                                rationale="ambiguous between several nodes")
        index = _ordinal_index(text, len(step.nodes))
        if index is not None:
            node = step.nodes[index]
            return VoiceCommand(ACTION_NODE, value=node.get("name"),
                                label=node.get("name"), confidence=0.75,
                                source=SOURCE_DETERMINISTIC, transcript=text,
                                extra={"node_id": node.get("id")},
                                rationale="matched by position")
        return None

    if family in (_grammar.FAMILY_SEGMENT_NAME, _grammar.FAMILY_SEGMENT_REF):
        entries = [(name, [name]) for name in step.segment_names]
        winner, score, ties = _best_match(text, entries)
        if winner is not None:
            return VoiceCommand(ACTION_SEGMENT_NAME, value=winner, label=winner,
                                confidence=score, source=SOURCE_DETERMINISTIC,
                                transcript=text)
        if ties:
            return VoiceCommand(transcript=text, confidence=score, options=ties,
                                rationale="ambiguous between several segments")
        index = _ordinal_index(text, len(step.segment_names))
        if index is not None:
            name = step.segment_names[index]
            return VoiceCommand(ACTION_SEGMENT_NAME, value=name, label=name,
                                confidence=0.75, source=SOURCE_DETERMINISTIC,
                                transcript=text, rationale="matched by position")
        return None

    if family == _grammar.FAMILY_SEGMENTS_TABLE:
        visible = None
        remainder = normalized
        for verb, flag in (("show", True), ("unhide", True), ("reveal", True),
                           ("hide", False), ("remove", False), ("untick", False),
                           ("uncheck", False), ("turn off", False), ("turn on", True)):
            if remainder.startswith(verb + " "):
                visible = flag
                remainder = remainder[len(verb) + 1:].strip()
                break
        if visible is None:
            return None
        entries = [(seg, [seg.get("name", "")]) for seg in step.segments]
        winner, score, ties = _best_match(remainder, entries)
        if winner is not None:
            return VoiceCommand(ACTION_SEGMENT_VISIBILITY, value=winner.get("id"),
                                label=winner.get("name"), confidence=score,
                                source=SOURCE_DETERMINISTIC, transcript=text,
                                extra={"visible": visible})
        if ties:
            return VoiceCommand(transcript=text, confidence=score,
                                options=[t.get("name") for t in ties],
                                rationale="ambiguous between several segments")
        return None

    if family == _grammar.FAMILY_SCALAR:
        numbers = extract_numbers(text)
        if len(numbers) == 1:
            return _scalar_command(numbers[0], step, text)
        if len(numbers) > 1:
            return VoiceCommand(transcript=text,
                                rationale="heard several numbers for one value")
        return None

    if family == _grammar.FAMILY_RANGE:
        numbers = extract_numbers(text)
        if len(numbers) >= 2 and _looks_like_range(text):
            low, high = sorted(numbers[:2])
            return _range_command(low, high, step, text)
        if len(numbers) >= 2:
            low, high = sorted(numbers[:2])
            return _range_command(low, high, step, text, confidence=0.70)
        return None

    if family == _grammar.FAMILY_MULTI:
        assignments = {}
        matched_labels = []
        for item in step.multi_items:
            options = [str(o) for o in (item.get("options") or [])]
            entries = [(option, [option]) for option in options]
            winner, score, _ties = _best_match(text, entries)
            if winner is not None and score >= ACCEPT_SCORE:
                assignments[item.get("param")] = winner
                matched_labels.append("%s = %s" % (item.get("label")
                                                   or item.get("param"), winner))
        if assignments:
            return VoiceCommand(ACTION_MULTI, value=assignments,
                                label="; ".join(matched_labels), confidence=0.80,
                                source=SOURCE_DETERMINISTIC, transcript=text)
        return None

    if family == _grammar.FAMILY_TEXT:
        payload = _strip_lead_in(text)
        if payload:
            return VoiceCommand(ACTION_TEXT, value=payload, label=payload,
                                confidence=0.85, source=SOURCE_DETERMINISTIC,
                                transcript=text)
        numbers = extract_numbers(text)
        if payload is None and len(numbers) == 1 and len(_tokens(text)) <= 3:
            # A bare number on a free-text step is unambiguous enough to take:
            # the shipped free-text steps are all numeric parameters.
            return VoiceCommand(ACTION_TEXT, value=_fmt(numbers[0]),
                                label=_fmt(numbers[0]), confidence=0.70,
                                source=SOURCE_DETERMINISTIC, transcript=text)
        return None

    return None


def _scalar_command(value: float, step: StepGrammar, text: str,
                    confidence: float = 0.85) -> VoiceCommand:
    low, high = step.scalar.get("min"), step.scalar.get("max")
    label = step.choice_label or step.parameter_name or "the value"
    if low is not None and high is not None and not (low <= value <= high):
        return VoiceCommand(transcript=text, confidence=confidence,
                            rationale="%s is outside the allowed %s to %s"
                                      % (_fmt(value), _fmt(low), _fmt(high)))
    return VoiceCommand(ACTION_SCALAR, value=float(value), label=label,
                        confidence=confidence, source=SOURCE_DETERMINISTIC,
                        transcript=text)


def _range_command(low: float, high: float, step: StepGrammar, text: str,
                   confidence: float = 0.85) -> VoiceCommand:
    bound_low, bound_high = step.range.get("min"), step.range.get("max")
    label = step.choice_label or step.parameter_name or "the range"
    if bound_low is not None and bound_high is not None:
        if low < bound_low - 1e-6 or high > bound_high + 1e-6:
            return VoiceCommand(transcript=text, confidence=confidence,
                                rationale="%s to %s is outside the allowed %s to %s"
                                          % (_fmt(low), _fmt(high),
                                             _fmt(bound_low), _fmt(bound_high)))
    return VoiceCommand(ACTION_RANGE, value=[float(low), float(high)], label=label,
                        confidence=confidence, source=SOURCE_DETERMINISTIC,
                        transcript=text)


# ---------------------------------------------------------------------------
# LLM fallback
# ---------------------------------------------------------------------------

def build_fallback_prompts(transcript: str, step: StepGrammar) -> Tuple[str, str]:
    """(system, user) for the constrained fallback call.

    The system half lives in ``Resources/Prompts/voice_command_prompt.md`` --
    prompts are experimental variables of this system and never Python literals.
    """
    try:
        from SlicerAIAgentLib import PromptLibrary
        system = PromptLibrary.load(VOICE_COMMAND_PROMPT, fallback=_FALLBACK_PROMPT)
    except Exception:
        logger.debug("Voice fallback prompt load failed", exc_info=True)
        system = _FALLBACK_PROMPT
    payload = {
        "heard": transcript,
        "step": step.to_dict(),
        "allowed_actions": _allowed_actions(step),
    }
    user = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    return system, user


def _allowed_actions(step: StepGrammar) -> List[str]:
    """The closed action list the fallback may choose from.

    Derived from the live panel state, not from a fixed table, so the model can
    never be talked into an action the step does not offer -- the same shape of
    guard ``WorkflowIntentResolver`` applies to free-typed text.
    """
    allowed = [ACTION_NONE]
    if step.can_done:
        allowed.append(ACTION_PROCEED)
    if step.can_skip:
        allowed.append(ACTION_SKIP)
    family = step.family
    if family == _grammar.FAMILY_CHOICES:
        allowed.append(ACTION_CHOICE)
    elif family == _grammar.FAMILY_NODE:
        allowed.append(ACTION_NODE)
    elif family in (_grammar.FAMILY_SEGMENT_NAME, _grammar.FAMILY_SEGMENT_REF):
        allowed.append(ACTION_SEGMENT_NAME)
    elif family == _grammar.FAMILY_SEGMENTS_TABLE:
        allowed.append(ACTION_SEGMENT_VISIBILITY)
    elif family == _grammar.FAMILY_SCALAR:
        allowed.append(ACTION_SCALAR)
    elif family == _grammar.FAMILY_RANGE:
        allowed.append(ACTION_RANGE)
    elif family == _grammar.FAMILY_MULTI:
        allowed.append(ACTION_MULTI)
    elif family == _grammar.FAMILY_TEXT:
        allowed.append(ACTION_TEXT)
    return allowed


def _resolve_with_llm(transcript: str, step: StepGrammar,
                      llm_call: Callable[[str, str], str]) -> Optional[VoiceCommand]:
    system, user = build_fallback_prompts(transcript, step)
    try:
        reply = llm_call(system, user)
    except Exception:
        logger.debug("Voice fallback call failed", exc_info=True)
        return None
    parsed = _parse_json_reply(reply)
    if not parsed:
        return None
    return command_from_fallback(parsed, step, transcript)


def command_from_fallback(parsed: Dict[str, Any], step: StepGrammar,
                          transcript: str) -> Optional[VoiceCommand]:
    """Validate a fallback reply back into the step's own vocabulary.

    An index is required for every option-bearing family: the model may rename an
    option in its ``value`` field, but the value that reaches the runtime is
    always read out of the grammar by index. That is what makes it impossible for
    the fallback to send a ``choice_value`` the step never offered -- the failure
    mode that would otherwise surface deep inside emitted code rather than here.
    """
    action = str(parsed.get("action") or ACTION_NONE)
    if action not in _allowed_actions(step):
        logger.info("Voice fallback proposed a disallowed action: %s", action)
        return None
    try:
        confidence = float(parsed.get("confidence") or 0.0)
    except (TypeError, ValueError):
        confidence = 0.0
    if confidence < ACCEPT_SCORE:
        return None
    reason = str(parsed.get("reason") or "")
    index = parsed.get("index")
    index = int(index) if isinstance(index, (int, float)) else None

    if action == ACTION_CHOICE:
        if index is None or not (0 <= index < len(step.choices)):
            return None
        choice = step.choices[index]
        return VoiceCommand(ACTION_CHOICE, value=choice.get("value"),
                            label=choice.get("label"), confidence=confidence,
                            source=SOURCE_LLM, transcript=transcript, rationale=reason)
    if action == ACTION_NODE:
        if index is None or not (0 <= index < len(step.nodes)):
            return None
        node = step.nodes[index]
        return VoiceCommand(ACTION_NODE, value=node.get("name"),
                            label=node.get("name"), confidence=confidence,
                            source=SOURCE_LLM, transcript=transcript,
                            extra={"node_id": node.get("id")}, rationale=reason)
    if action == ACTION_SEGMENT_NAME:
        if index is None or not (0 <= index < len(step.segment_names)):
            return None
        name = step.segment_names[index]
        return VoiceCommand(ACTION_SEGMENT_NAME, value=name, label=name,
                            confidence=confidence, source=SOURCE_LLM,
                            transcript=transcript, rationale=reason)
    if action == ACTION_SEGMENT_VISIBILITY:
        if index is None or not (0 <= index < len(step.segments)):
            return None
        segment = step.segments[index]
        return VoiceCommand(ACTION_SEGMENT_VISIBILITY, value=segment.get("id"),
                            label=segment.get("name"), confidence=confidence,
                            source=SOURCE_LLM, transcript=transcript,
                            extra={"visible": bool(parsed.get("visible", True))},
                            rationale=reason)
    if action == ACTION_SCALAR:
        numbers = extract_numbers(str(parsed.get("value")))
        if not numbers:
            return None
        return _scalar_command(numbers[0], step, transcript, confidence)
    if action == ACTION_RANGE:
        value = parsed.get("value")
        numbers = ([float(v) for v in value] if isinstance(value, list) and len(value) >= 2
                   else extract_numbers(str(value)))
        if len(numbers) < 2:
            return None
        low, high = sorted(numbers[:2])
        return _range_command(low, high, step, transcript, confidence)
    if action == ACTION_MULTI:
        value = parsed.get("value")
        if not isinstance(value, dict) or not value:
            return None
        known = {item.get("param"): [str(o) for o in (item.get("options") or [])]
                 for item in step.multi_items}
        cleaned = {}
        for param, chosen in value.items():
            options = known.get(param)
            if options and str(chosen) in options:
                cleaned[param] = str(chosen)
        if not cleaned:
            return None
        return VoiceCommand(ACTION_MULTI, value=cleaned,
                            label="; ".join("%s = %s" % kv for kv in sorted(cleaned.items())),
                            confidence=confidence, source=SOURCE_LLM,
                            transcript=transcript, rationale=reason)
    if action == ACTION_TEXT:
        payload = str(parsed.get("value") or "").strip()
        if not payload:
            return None
        return VoiceCommand(ACTION_TEXT, value=payload, label=payload,
                            confidence=confidence, source=SOURCE_LLM,
                            transcript=transcript, rationale=reason)
    if action in (ACTION_PROCEED, ACTION_SKIP):
        return VoiceCommand(action, confidence=confidence, source=SOURCE_LLM,
                            transcript=transcript, rationale=reason)
    return None


def _parse_json_reply(reply: str) -> Optional[Dict[str, Any]]:
    text = str(reply or "").strip()
    if not text:
        return None
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fenced:
        text = fenced.group(1)
    else:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            return None
        text = text[start:end + 1]
    try:
        parsed = json.loads(text)
    except ValueError:
        logger.debug("Voice fallback reply was not JSON: %r", reply[:200])
        return None
    return parsed if isinstance(parsed, dict) else None
