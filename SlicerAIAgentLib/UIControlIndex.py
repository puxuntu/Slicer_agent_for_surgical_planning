"""Deterministic lookup over the Slicer core UI pre-analysis artifacts.

`scripts/build_ui_analysis.py` produces `Resources/Slicer_UI_PreAnalysis/v1/`
(ui_controls.jsonl + docs/*.md): a bridge from user-facing Slicer core UI
labels/actions to nearby implementation evidence (slots, API footprints,
confidence levels). Those artifacts were previously reachable only through
LLM-driven retrieval (VectorSearch/Grep over the indexed docs), which makes
which evidence gets seen depend on tool-call ordering — an observed source of
run-to-run grounding variance.

This module provides a pure, LLM-free, deterministic token index over
ui_controls.jsonl so pipeline stages can fetch the relevant evidence directly:
- SlicerOpGenerator injects matching control records into grounding prompts.
- The repair loop's broadened re-ground rung widens retrieval with matching
  API footprints.
- The evidence-first proven-API block cites core-UI evidenced method names.

Everything degrades gracefully: when the artifacts are absent or corrupt,
`get_index()` returns None and callers behave exactly as before.
"""

from __future__ import annotations

import json
import logging
import os
import re
import threading
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)

_LIB_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_LIB_DIR)
PREANALYSIS_DIR = os.path.join(
    _PROJECT_ROOT, "Resources", "Slicer_UI_PreAnalysis", "v1"
)

_CONFIDENCE_RANK = {
    "linked_to_api": 3,
    "linked_to_slot": 2,
    "linked_to_code": 1,
    "ui_only": 0,
}
_DEFAULT_MIN_CONFIDENCE = {"linked_to_slot", "linked_to_api"}

_STOPWORDS = {
    "the", "and", "for", "with", "from", "into", "this", "that", "use",
    "set", "get", "all", "any", "are", "you", "your", "its", "can",
    "widget", "button", "qslicer", "slicer",
}

_CAMEL_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])")
_NON_ALNUM_RE = re.compile(r"[^A-Za-z0-9]+")

_lock = threading.Lock()
_cached_index = None
_cached_key = None


def _safe_name(rel_path: str) -> str:
    """Must replicate scripts/build_ui_analysis.py:_safe_name exactly."""
    return re.sub(r"[^A-Za-z0-9_.-]+", "__", rel_path).replace("/", "__")


def tokenize(text: str) -> List[str]:
    """Lowercase tokens split on non-alphanumerics and camelCase boundaries."""
    if not text:
        return []
    tokens: List[str] = []
    for raw in _NON_ALNUM_RE.split(str(text)):
        if not raw:
            continue
        for part in _CAMEL_RE.split(raw):
            part = part.lower()
            if len(part) >= 3 and part not in _STOPWORDS:
                tokens.append(part)
    return tokens


class UIControlIndex:
    """Inverted token index over ui_controls.jsonl records."""

    def __init__(self, records: List[Dict]):
        self.records = records
        self.token_postings: Dict[str, Set[int]] = {}
        for idx, record in enumerate(records):
            for token in set(self._record_tokens(record)):
                self.token_postings.setdefault(token, set()).add(idx)

    @staticmethod
    def _record_tokens(record: Dict) -> List[str]:
        ui_file = record.get("ui_file", "")
        stem = os.path.splitext(os.path.basename(ui_file))[0]
        tokens: List[str] = []
        for field in ("object_name", "text", "tool_tip", "widget_class", "owner_class"):
            tokens.extend(tokenize(record.get(field, "")))
        tokens.extend(tokenize(stem))
        return tokens

    def match(
        self,
        query,
        top_k: int = 5,
        min_confidence: Optional[Set[str]] = None,
        min_matched_tokens: int = 2,
    ) -> List[Dict]:
        """Deterministic top-k control match for a query string or token list.

        Score: sum over matched tokens of 1/df(token) (rarer tokens weigh
        more). Ties broken by (confidence rank desc, ui_file, object_name) so
        ordering is invariant across runs and load order.
        """
        if min_confidence is None:
            min_confidence = _DEFAULT_MIN_CONFIDENCE
        query_tokens = sorted(set(
            query if isinstance(query, (list, tuple, set)) else tokenize(query)
        ))
        if not query_tokens:
            return []

        scores: Dict[int, float] = {}
        matched: Dict[int, List[str]] = {}
        for token in query_tokens:
            postings = self.token_postings.get(token)
            if not postings:
                continue
            weight = 1.0 / len(postings)
            for idx in postings:
                scores[idx] = scores.get(idx, 0.0) + weight
                matched.setdefault(idx, []).append(token)

        candidates = []
        for idx, score in scores.items():
            record = self.records[idx]
            if record.get("confidence", "ui_only") not in min_confidence:
                continue
            if len(matched[idx]) < min_matched_tokens:
                continue
            candidates.append((
                -score,
                -_CONFIDENCE_RANK.get(record.get("confidence", "ui_only"), 0),
                record.get("ui_file", ""),
                record.get("object_name", ""),
                idx,
            ))
        candidates.sort()

        results = []
        for _, _, _, _, idx in candidates[:top_k]:
            record = self.records[idx]
            results.append({
                "record": record,
                "score": scores[idx],
                "matched_tokens": sorted(matched[idx]),
                "doc_path": "slicer-ui-analysis/" + _safe_name(record.get("ui_file", "")) + ".md",
            })
        return results


def get_index() -> Optional[UIControlIndex]:
    """Process-level singleton; rebuilt when the jsonl file changes.

    Returns None (never raises) when artifacts are absent or unreadable.
    """
    global _cached_index, _cached_key
    path = os.path.join(PREANALYSIS_DIR, "ui_controls.jsonl")
    try:
        stat = os.stat(path)
        key = (path, stat.st_mtime, stat.st_size)
    except OSError:
        return None
    with _lock:
        if _cached_index is not None and _cached_key == key:
            return _cached_index
        try:
            records = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    if isinstance(record, dict) and record.get("object_name"):
                        records.append(record)
            if not records:
                return None
            _cached_index = UIControlIndex(records)
            _cached_key = key
            logger.info("UIControlIndex loaded: %d controls", len(records))
            return _cached_index
        except Exception:
            logger.debug("UIControlIndex load failed", exc_info=True)
            return None


def format_evidence_lines(
    matches: List[Dict],
    max_total_chars: int = 1200,
    max_footprints: int = 10,
) -> List[str]:
    """Compact one-line-per-control evidence for prompt injection."""
    lines: List[str] = []
    total = 0
    for match in matches:
        record = match.get("record", {})
        impl = record.get("implementation_files", []) or []
        slots = record.get("slots", []) or []
        footprints = (record.get("api_footprints", []) or [])[:max_footprints]
        bits = [
            f"- [{record.get('confidence', '?')}] {record.get('kind', 'widget')} "
            f"{record.get('object_name', '?')}"
        ]
        if record.get("text"):
            bits.append(f"\"{record['text']}\"")
        loc = []
        if record.get("ui_file"):
            loc.append(f"ui {os.path.basename(record['ui_file'])}")
        if impl:
            loc.append(f"impl {os.path.basename(impl[0])}")
        if loc:
            bits.append("(" + ", ".join(loc) + ")")
        if slots:
            bits.append("slots: " + ", ".join(slots[:4]))
        if footprints:
            bits.append("api: " + ", ".join(footprints))
        bits.append("doc: " + match.get("doc_path", ""))
        line = " ".join(bits)
        if total + len(line) > max_total_chars:
            break
        lines.append(line)
        total += len(line)
    return lines


def preanalysis_status() -> Dict:
    """Integrity check on the pre-analysis artifacts.

    Validates only relative existence and counts — never the absolute
    `source_root`/`docs_path` recorded inside manifest.json (artifacts may
    have been generated on another machine).
    """
    manifest_path = os.path.join(PREANALYSIS_DIR, "manifest.json")
    jsonl_path = os.path.join(PREANALYSIS_DIR, "ui_controls.jsonl")
    docs_dir = os.path.join(PREANALYSIS_DIR, "docs")
    status = {
        "ok": False,
        "reason": "",
        "control_count": 0,
        "confidence_counts": {},
        "manifest_path": manifest_path,
    }
    if not os.path.isfile(manifest_path):
        status["reason"] = "manifest.json missing"
        return status
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except Exception:
        status["reason"] = "manifest.json unreadable"
        return status
    status["control_count"] = int(manifest.get("control_count", 0) or 0)
    status["confidence_counts"] = manifest.get("confidence_counts", {}) or {}
    if status["control_count"] <= 0:
        status["reason"] = "manifest reports zero controls"
        return status
    if not (os.path.isfile(jsonl_path) and os.path.getsize(jsonl_path) > 0):
        status["reason"] = "ui_controls.jsonl missing or empty"
        return status
    try:
        has_docs = any(name.endswith(".md") for name in os.listdir(docs_dir))
    except OSError:
        has_docs = False
    if not has_docs:
        status["reason"] = "docs/ missing or empty"
        return status
    status["ok"] = True
    return status


def preanalysis_fingerprint() -> str:
    """Content fingerprint for checkpoint keys; 'absent' when unavailable."""
    jsonl_path = os.path.join(PREANALYSIS_DIR, "ui_controls.jsonl")
    try:
        stat = os.stat(jsonl_path)
    except OSError:
        return "absent"
    count = preanalysis_status().get("control_count", 0)
    return f"{count}:{int(stat.st_mtime)}:{stat.st_size}"
