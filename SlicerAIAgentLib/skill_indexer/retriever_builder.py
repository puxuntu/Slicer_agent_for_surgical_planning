from .common import *
from .chunker import Chunker
from .vector_index import VectorIndex, _SOURCE_TYPE_WEIGHTS

class VectorRetriever:
    """Pure dense vector retrieval with source_type weighting."""

    def __init__(self, vector_index: VectorIndex,
                 chunks_metadata: Dict[str, CodeChunk]):
        self.vector = vector_index
        self.chunks = chunks_metadata
        self.full_file_paths: Set[str] = set()

    def is_ready(self) -> bool:
        return self.vector.faiss_index is not None

    def search(self, query: str, top_k: int = 15) -> List[RetrievedChunk]:
        """Run pure vector search and return ranked chunks."""
        if not self.is_ready():
            return []

        vec_results = self.vector.search(query, top_k=top_k)

        # Apply source_type weighting
        results: List[RetrievedChunk] = []
        for cid, sim in vec_results:
            chunk = self.chunks.get(cid)
            if not chunk:
                continue
            weight = _SOURCE_TYPE_WEIGHTS.get(chunk.source_type, 1.0)
            final = sim * weight
            results.append(RetrievedChunk(
                chunk=chunk,
                vector_score=sim,
                final_score=final,
            ))
            if len(results) >= top_k:
                break

        return results

    def format_for_prompt(self, results: List[RetrievedChunk]) -> str:
        """Format retrieval results for injection into system prompt."""
        if not results:
            return ""
        lines = ["## Relevant code snippets from knowledge base:\n"]
        for i, rc in enumerate(results, 1):
            c = rc.chunk
            if c.chunk_type == "whole_file":
                lines.append(
                    f"[{i}] {c.file_path} (lines {c.start_line}-{c.end_line}) "
                    f"[{c.source_type}] [Full file included — no need to ReadFile or VectorSearch this file]\n"
                    f"```{c.language if c.language != 'other' else ''}\n"
                    f"{c.content}\n"
                    f"```\n"
                )
            else:
                lines.append(
                    f"[{i}] {c.file_path} (lines {c.start_line}-{c.end_line}) "
                    f"[{c.source_type}] similarity:{rc.vector_score:.3f} boosted:{rc.final_score:.3f}\n"
                    f"```{c.language if c.language != 'other' else ''}\n"
                    f"{c.content}\n"
                    f"```\n"
                )
        return '\n'.join(lines)


# ---------------------------------------------------------------------------
# IndexBuilder
# ---------------------------------------------------------------------------

class IndexBuilder:
    """Orchestrate incremental index building / updating."""

    INDEX_VERSION = "1.0"
    INDEX_SUBDIR = "v1"

    def __init__(self, skill_path: str, index_dir: Optional[str] = None):
        self.skill_path = skill_path
        # Allow caller to explicitly specify index_dir so that __file__
        # resolution inside _get_index_dir() is not the only source of truth.
        if index_dir is not None:
            self.index_dir = index_dir
        else:
            self.index_dir = _get_index_dir()
        os.makedirs(self.index_dir, exist_ok=True)
        self._manifest_path = os.path.join(self.index_dir, "manifest.json")
        self._metadata_path = os.path.join(self.index_dir, "chunks_metadata.jsonl")

    def index_exists(self) -> bool:
        return (
            os.path.exists(os.path.join(self.index_dir, "vector_index.faiss")) and
            os.path.exists(self._manifest_path)
        )

    def _file_fingerprint(self, filepath: str) -> str:
        """Return mtime + size as a quick fingerprint."""
        try:
            stat = os.stat(filepath)
            return f"{stat.st_mtime:.6f}:{stat.st_size}"
        except Exception:
            return ""

    def _load_manifest(self) -> Dict[str, Any]:
        if os.path.exists(self._manifest_path):
            try:
                with open(self._manifest_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "version": self.INDEX_VERSION,
            "model": VectorIndex.MODEL_NAME,
            "dimension": VectorIndex.DIMENSION,
            "skill_path": self.skill_path,
            "file_fingerprints": {},
            "total_chunks": 0,
            "build_time": "",
        }

    def _save_manifest(self, manifest: Dict[str, Any]):
        with open(self._manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

    def _load_existing_chunks(self) -> Dict[str, CodeChunk]:
        """Load previously indexed chunks from metadata jsonl."""
        chunks: Dict[str, CodeChunk] = {}
        if not os.path.exists(self._metadata_path):
            return chunks
        try:
            with open(self._metadata_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    obj = json.loads(line)
                    chunk = CodeChunk(**obj)
                    chunks[chunk.chunk_id] = chunk
        except Exception as e:
            logger.warning(f"Could not load existing chunk metadata: {e}")
        return chunks

    def _scan_files(self) -> List[Tuple[str, str]]:
        """Return list of (abs_path, rel_path) for files to index."""
        chunker = Chunker()
        files = []
        for root, _, filenames in os.walk(self.skill_path):
            for filename in filenames:
                abs_path = os.path.join(root, filename)
                rel_path = os.path.relpath(abs_path, self.skill_path).replace('\\', '/')
                if chunker.should_index_file(rel_path):
                    files.append((abs_path, rel_path))
        ui_docs_dir = _get_ui_analysis_docs_dir()
        if os.path.isdir(ui_docs_dir):
            for root, _, filenames in os.walk(ui_docs_dir):
                for filename in filenames:
                    abs_path = os.path.join(root, filename)
                    rel_sub = os.path.relpath(abs_path, ui_docs_dir).replace('\\', '/')
                    rel_path = f"slicer-ui-analysis/{rel_sub}"
                    if chunker.should_index_file(rel_path):
                        files.append((abs_path, rel_path))
        return files

    def build_or_update(self) -> bool:
        """
        Build a fresh index or incrementally update an existing one.
        Returns True on success.
        """
        import time
        t0 = time.time()
        manifest = self._load_manifest()
        old_fingerprints = manifest.get("file_fingerprints", {})
        existing_chunks = self._load_existing_chunks()

        files = self._scan_files()
        new_fingerprints: Dict[str, str] = {}

        # Determine which files changed
        changed_files = []
        unchanged_chunk_ids = set()
        for abs_path, rel_path in files:
            fp = self._file_fingerprint(abs_path)
            new_fingerprints[rel_path] = fp
            if old_fingerprints.get(rel_path) == fp and existing_chunks:
                # File unchanged — keep its chunks
                for cid, chunk in existing_chunks.items():
                    if chunk.file_path == rel_path:
                        unchanged_chunk_ids.add(cid)
            else:
                changed_files.append((abs_path, rel_path))

        # Detect deleted files
        current_rel_paths = {rp for _, rp in files}
        for cid in list(existing_chunks.keys()):
            if existing_chunks[cid].file_path not in current_rel_paths:
                # File was deleted — mark its chunks for removal
                pass

        if not changed_files and existing_chunks:
            logger.info("Index is up-to-date (no file changes detected).")
            return True

        logger.info(
            f"Index update: {len(changed_files)} changed/new files, "
            f"{len(unchanged_chunk_ids)} unchanged chunks."
        )

        # Re-chunk changed files
        t1 = time.time()
        chunker = Chunker()
        new_chunks_list: List[CodeChunk] = []
        for abs_path, rel_path in changed_files:
            chunks = chunker.chunk_file(abs_path, rel_path)
            new_chunks_list.extend(chunks)
        logger.info(f"[CHUNK] {len(changed_files)} files chunked in {time.time()-t1:.1f}s")

        # Assemble final chunk list: unchanged + new
        final_chunks = []
        kept = 0
        for cid, chunk in existing_chunks.items():
            if cid in unchanged_chunk_ids:
                final_chunks.append(chunk)
                kept += 1
        final_chunks.extend(new_chunks_list)

        logger.info(f"Total chunks after update: {len(final_chunks)} (kept {kept}, new {len(new_chunks_list)})")

        if not final_chunks:
            logger.warning("No chunks to index. Check skill_path and P0/P1 filters.")
            return False

        # Build metadata jsonl
        logger.info("[STAGE 2/4] Saving chunk metadata...")
        t2 = time.time()
        with open(self._metadata_path, 'w', encoding='utf-8') as f:
            for chunk in final_chunks:
                f.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")
        logger.info(f"[META] Metadata saved in {time.time()-t2:.1f}s")

        # Build Vector
        logger.info("[STAGE 3/4] Encoding chunks and building FAISS index (this may take a few minutes)...")
        t4 = time.time()
        vector_path = os.path.join(self.index_dir, "vector_index.faiss")
        vector = VectorIndex(vector_path)
        vector.build(final_chunks)
        logger.info(f"[FAISS] Index saved in {time.time()-t4:.1f}s")

        logger.info(f"[TOTAL] Index build completed in {time.time()-t0:.1f}s")

        # Save manifest
        manifest.update({
            "version": self.INDEX_VERSION,
            "model": VectorIndex.MODEL_NAME,
            "dimension": VectorIndex.DIMENSION,
            "skill_path": self.skill_path,
            "file_fingerprints": new_fingerprints,
            "total_chunks": len(final_chunks),
            "build_time": time.strftime("%Y-%m-%dT%H:%M:%S"),
        })
        self._save_manifest(manifest)
        logger.info("Index build/update completed successfully.")
        return True

    def load_retriever(self) -> Optional[VectorRetriever]:
        """Load vector index from disk and return a ready VectorRetriever."""
        if not self.index_exists():
            return None

        vector_path = os.path.join(self.index_dir, "vector_index.faiss")

        vector = VectorIndex(vector_path)
        if not vector.load():
            return None

        # Load metadata
        chunks: Dict[str, CodeChunk] = {}
        if os.path.exists(self._metadata_path):
            try:
                with open(self._metadata_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        obj = json.loads(line)
                        chunk = CodeChunk(**obj)
                        chunks[chunk.chunk_id] = chunk
            except Exception as e:
                logger.warning(f"Failed to load chunk metadata: {e}")
                return None

        if not chunks:
            return None

        return VectorRetriever(vector, chunks)
