from .common import *

_MEMORY_FILENAME = "_repair_memory.json"
_MAX_ENTRIES = 200


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
        self._path = os.path.join(base_dir, _MEMORY_FILENAME) if base_dir else ""
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
