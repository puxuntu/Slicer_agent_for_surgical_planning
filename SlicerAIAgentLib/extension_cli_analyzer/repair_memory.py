from .common import *

_MEMORY_FILENAME = "repair_memory.json"
_LEGACY_FILENAME = "_repair_memory.json"
_MAX_ENTRIES = 200


def _memory_dir_for(base_dir: str) -> str:
    """Cross-extension store lives OUTSIDE extension_CLI so that directory
    contains only one folder per extension. Located at
    <project>/Resources/agent_cache/ (gitignored)."""
    # base_dir is .../Resources/extension_CLI — derive the sibling cache dir.
    resources_dir = os.path.dirname(os.path.normpath(base_dir))
    return os.path.join(resources_dir, "agent_cache")


def _tokens(text: str) -> set:
    return {t.lower() for t in _re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", text or "")}


class RepairMemory:
    """Cross-run store of issue→strategy outcomes (generic experience memory).

    Entries describe *issue shapes* (issue type/class + subject tokens), the
    strategy applied, the outcome, and a short fix summary. They are retrieved
    as few-shot examples for future repair prompts — learned guidance, never
    rules. Keys are matched by token similarity, so entries generalize across
    extensions; usefulness counters drive LRU eviction.
    """

    def __init__(self, base_dir: str):
        if base_dir:
            memory_dir = _memory_dir_for(base_dir)
            self._path = os.path.join(memory_dir, _MEMORY_FILENAME)
            # One-time migration from the legacy in-extension_CLI location.
            legacy = os.path.join(base_dir, _LEGACY_FILENAME)
            if not os.path.isfile(self._path) and os.path.isfile(legacy):
                try:
                    os.makedirs(memory_dir, exist_ok=True)
                    os.replace(legacy, self._path)
                    logger.info("Repair memory migrated to %s", self._path)
                except Exception:
                    logger.debug("Repair memory migration failed", exc_info=True)
        else:
            self._path = ""
        self._entries: List[Dict] = []
        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        if not self._path or not os.path.isfile(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self._entries = data
        except Exception:
            logger.debug("Repair memory load failed", exc_info=True)

    def _save(self) -> None:
        if not self._path:
            return
        try:
            os.makedirs(os.path.dirname(self._path), exist_ok=True)
            if len(self._entries) > _MAX_ENTRIES:
                # Evict least-useful first, then oldest
                self._entries.sort(
                    key=lambda e: (e.get("useful_count", 0), e.get("recorded_at", ""))
                )
                self._entries = self._entries[-_MAX_ENTRIES:]
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._entries, f, indent=2)
        except Exception:
            logger.debug("Repair memory save failed", exc_info=True)

    def record(
        self,
        issue_type: str,
        issue_class: str,
        subject: str,
        strategy: str,
        outcome: str,
        fix_summary: str = "",
    ) -> None:
        self._load()
        self._entries.append({
            "issue_type": issue_type,
            "issue_class": issue_class,
            "subject": subject,
            "strategy": strategy,
            "outcome": outcome,
            "fix_summary": fix_summary[:400],
            "useful_count": 0,
            "recorded_at": datetime.now().isoformat(),
        })
        self._save()

    def retrieve(
        self, issue_type: str, issue_class: str, subject: str, k: int = 3,
    ) -> List[Dict]:
        """Top-k successful entries for this issue shape, by token similarity."""
        self._load()
        query = _tokens(subject)
        scored = []
        for entry in self._entries:
            if entry.get("outcome") != "succeeded":
                continue
            score = 0.0
            if entry.get("issue_type") == issue_type:
                score += 2.0
            if entry.get("issue_class") == issue_class:
                score += 1.0
            overlap = query & _tokens(entry.get("subject", ""))
            if query:
                score += len(overlap) / max(len(query), 1)
            if score > 1.0:
                scored.append((score, entry))
        scored.sort(key=lambda item: item[0], reverse=True)
        top = [entry for _, entry in scored[:k]]
        if top:
            for entry in top:
                entry["useful_count"] = entry.get("useful_count", 0) + 1
            self._save()
        return top


class AnalyzerRepairMemoryMixin:
    # ── pending upstream feedback (cross-run closed loop) ──
    # When a revision of an existing CLI hits an upstream contract/dataflow
    # root cause, the structured failure is persisted so the next full
    # regeneration starts with it as contract-phase feedback instead of
    # resampling blindly. Stored inside the extension's own CLI folder.

    def _pending_feedback_path(self, extension_name: str) -> Optional[str]:
        if not self.output_base_dir or not extension_name:
            return None
        return os.path.join(
            self.output_base_dir, extension_name, "pending_upstream_feedback.json"
        )

    def _save_pending_upstream_feedback(self, extension_name: str, requests: List[Dict]) -> None:
        path = self._pending_feedback_path(extension_name)
        if not path or not requests:
            return
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(requests, f, indent=2)
        except Exception:
            logger.debug("Failed to persist pending upstream feedback", exc_info=True)

    def _take_pending_upstream_feedback(self, extension_name: str) -> List[Dict]:
        """Load and consume (delete) persisted upstream feedback, if any."""
        path = self._pending_feedback_path(extension_name)
        if not path or not os.path.isfile(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                requests = json.load(f)
            os.remove(path)
            if isinstance(requests, list) and requests:
                logger.info(
                    "Seeding contract phase with %d persisted upstream "
                    "failure(s) from a prior run", len(requests),
                )
                return requests
        except Exception:
            logger.debug("Failed to load pending upstream feedback", exc_info=True)
        return []

    def _repair_memory(self) -> RepairMemory:
        memory = getattr(self, "_repair_memory_instance", None)
        if memory is None:
            memory = RepairMemory(self.output_base_dir or "")
            self._repair_memory_instance = memory
        return memory

    def _repair_memory_examples(self, issues: List[Dict]) -> str:
        """Few-shot prompt section from previously successful similar repairs."""
        try:
            memory = self._repair_memory()
            examples = []
            seen = set()
            for issue in (issues or [])[:5]:
                subject = (
                    issue.get("call_id")
                    or issue.get("template_key", "")
                    or issue.get("message", "")
                )
                for entry in memory.retrieve(
                    issue.get("issue_type", ""), issue.get("issue_class", ""), subject,
                ):
                    key = (entry.get("issue_type"), entry.get("fix_summary"))
                    if key in seen:
                        continue
                    seen.add(key)
                    examples.append(
                        f"- issue {entry.get('issue_type')} on '{entry.get('subject')}' "
                        f"was fixed via {entry.get('strategy')}: {entry.get('fix_summary')}"
                    )
            if not examples:
                return ""
            return (
                "\nPREVIOUSLY SUCCESSFUL REPAIRS OF SIMILAR ISSUE SHAPES "
                "(guidance from past runs, possibly other extensions — adapt, "
                "do not copy blindly):\n" + "\n".join(examples[:6]) + "\n"
            )
        except Exception:
            logger.debug("Repair memory retrieval failed", exc_info=True)
            return ""

    def _repair_memory_record(self, issue: Dict, strategy: str, outcome: str, fix_summary: str = "") -> None:
        try:
            subject = (
                issue.get("call_id")
                or issue.get("template_key", "")
                or issue.get("message", "")
            )
            self._repair_memory().record(
                issue.get("issue_type", ""),
                issue.get("issue_class", ""),
                str(subject),
                strategy,
                outcome,
                fix_summary,
            )
        except Exception:
            logger.debug("Repair memory record failed", exc_info=True)
