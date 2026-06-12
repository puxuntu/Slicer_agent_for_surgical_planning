from .common import *
import hashlib
import pickle

# Bump when checkpoint artifact semantics change incompatibly.
_CHECKPOINT_FORMAT_VERSION = 1


class AnalyzerCheckpointsMixin:
    """Content-keyed per-phase artifact checkpoints.

    A phase whose inputs (source, cookbook, prompts, upstream artifacts,
    feedback nonce) hash to the same key as a previous run reloads its saved
    artifact instead of re-deriving it. This makes reruns converge
    incrementally instead of resampling every LLM stage, and makes upstream
    re-entry affordable (only invalidated phases re-run).

    Checkpoints are stored under <output_base_dir>/_checkpoints/<extension>/
    — outside the CLI package dir, so delete/regenerate cycles keep them.
    Artifacts are pickled (they may contain non-JSON-safe keys); a JSON
    sidecar records the key and metadata for inspection.
    """

    checkpoints_enabled = True

    def _checkpoint_dir(self, extension_name: str) -> Optional[str]:
        if not self.output_base_dir:
            return None
        return os.path.join(self.output_base_dir, "_checkpoints", extension_name)

    @staticmethod
    def _checkpoint_fingerprint(*parts) -> str:
        """Stable content hash over arbitrary JSON-representable inputs."""
        try:
            blob = json.dumps(parts, sort_keys=True, default=str).encode("utf-8")
        except Exception:
            blob = repr(parts).encode("utf-8")
        return hashlib.sha256(blob).hexdigest()

    def _checkpoint_load(self, extension_name: str, phase: str, key: str):
        """Return the saved artifact for (phase, key), or None on miss."""
        if not self.checkpoints_enabled:
            return None
        ckpt_dir = self._checkpoint_dir(extension_name)
        if not ckpt_dir:
            return None
        meta_path = os.path.join(ckpt_dir, f"{phase}.json")
        data_path = os.path.join(ckpt_dir, f"{phase}.pkl")
        try:
            if not (os.path.isfile(meta_path) and os.path.isfile(data_path)):
                return None
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            if meta.get("key") != key or meta.get("format") != _CHECKPOINT_FORMAT_VERSION:
                return None
            with open(data_path, "rb") as f:
                artifact = pickle.load(f)
            logger.info("[checkpoint] reusing '%s' artifact (key match)", phase)
            self.on_progress(
                phase, "Checkpoint",
                f"Reusing cached {phase} artifact (inputs unchanged)",
            )
            return artifact
        except Exception:
            logger.debug("Checkpoint load failed for %s", phase, exc_info=True)
            return None

    def _checkpoint_save(self, extension_name: str, phase: str, key: str, artifact) -> None:
        if not self.checkpoints_enabled:
            return
        ckpt_dir = self._checkpoint_dir(extension_name)
        if not ckpt_dir:
            return
        try:
            os.makedirs(ckpt_dir, exist_ok=True)
            with open(os.path.join(ckpt_dir, f"{phase}.pkl"), "wb") as f:
                pickle.dump(artifact, f)
            with open(os.path.join(ckpt_dir, f"{phase}.json"), "w", encoding="utf-8") as f:
                json.dump({
                    "key": key,
                    "format": _CHECKPOINT_FORMAT_VERSION,
                    "phase": phase,
                    "saved_at": datetime.now().isoformat(),
                }, f, indent=2)
        except Exception:
            logger.debug("Checkpoint save failed for %s", phase, exc_info=True)

    # ── pending upstream feedback (cross-run closed loop) ──
    # When a revision of an existing CLI hits an upstream contract/dataflow
    # root cause, the structured failure is persisted here so the next full
    # regeneration starts with it as contract-phase feedback instead of
    # resampling blindly.

    def _save_pending_upstream_feedback(self, extension_name: str, requests: List[Dict]) -> None:
        ckpt_dir = self._checkpoint_dir(extension_name)
        if not ckpt_dir or not requests:
            return
        try:
            os.makedirs(ckpt_dir, exist_ok=True)
            with open(
                os.path.join(ckpt_dir, "pending_upstream_feedback.json"),
                "w", encoding="utf-8",
            ) as f:
                json.dump(requests, f, indent=2)
        except Exception:
            logger.debug("Failed to persist pending upstream feedback", exc_info=True)

    def _take_pending_upstream_feedback(self, extension_name: str) -> List[Dict]:
        """Load and consume (delete) persisted upstream feedback, if any."""
        ckpt_dir = self._checkpoint_dir(extension_name)
        if not ckpt_dir:
            return []
        path = os.path.join(ckpt_dir, "pending_upstream_feedback.json")
        if not os.path.isfile(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                requests = json.load(f)
            os.remove(path)
            if isinstance(requests, list) and requests:
                logger.info(
                    "[checkpoint] seeding contract phase with %d persisted "
                    "upstream failure(s) from a prior run", len(requests),
                )
                return requests
        except Exception:
            logger.debug("Failed to load pending upstream feedback", exc_info=True)
        return []

    @staticmethod
    def _file_content_hash(path: str) -> str:
        try:
            with open(path, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
