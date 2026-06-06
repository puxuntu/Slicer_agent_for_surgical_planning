from .common import *

class VectorIndex:
    """Dense semantic retrieval via ONNX Runtime + FAISS."""

    MODEL_NAME = "jinaai/jina-embeddings-v2-base-code"
    ONNX_SUBPATH = "onnx/model.onnx"
    DIMENSION = 768
    MAX_SEQ_LENGTH = 1024

    def __init__(self, index_path: str):
        self.index_path = index_path
        self.session = None      # onnxruntime InferenceSession
        self.tokenizer = None    # tokenizers Tokenizer
        self.faiss_index = None
        self.chunk_ids: List[str] = []

    @staticmethod
    def _find_tokenizer_json(cache_dir: str) -> Optional[str]:
        """Find tokenizer.json in the HF Hub cache under cache_dir."""
        # Prefer the exact model repo cache
        model_cache = os.path.join(cache_dir, "models--jinaai--jina-embeddings-v2-base-code")
        if os.path.isdir(model_cache):
            for root, _, files in os.walk(model_cache):
                if "tokenizer.json" in files:
                    return os.path.join(root, "tokenizer.json")
        # Fallback: search entire cache_dir
        for root, _, files in os.walk(cache_dir):
            if "tokenizer.json" in files:
                return os.path.join(root, "tokenizer.json")
        return None

    def _ensure_model_files(self):
        """Download ONNX model and load lightweight tokenizer if not cached locally."""
        import time
        t0 = time.time()
        cache_dir = _get_model_cache_dir()
        os.makedirs(cache_dir, exist_ok=True)

        # Ensure tokenizer is available
        if self.tokenizer is None:
            t1 = time.time()
            try:
                from tokenizers import Tokenizer
            except ImportError:
                _ensure_packages(["tokenizers"])
                from tokenizers import Tokenizer

            tokenizer_json = self._find_tokenizer_json(cache_dir)
            if tokenizer_json is None:
                raise RuntimeError(
                    f"tokenizer.json not found under {cache_dir}. "
                    "Please ensure the model tokenizer files are downloaded."
                )
            t_tok0 = time.time()
            self.tokenizer = Tokenizer.from_file(tokenizer_json)
            self.tokenizer.enable_truncation(max_length=self.MAX_SEQ_LENGTH)
            pad_id = self.tokenizer.token_to_id("<pad>")
            if pad_id is None:
                pad_id = 0
            self.tokenizer.enable_padding(
                length=self.MAX_SEQ_LENGTH,
                pad_id=pad_id,
                pad_token="<pad>",
            )
        # Ensure ONNX model is available
        onnx_path = os.path.join(cache_dir, "model.onnx")
        onnx_exists = os.path.exists(onnx_path)
        onnx_size = os.path.getsize(onnx_path) if onnx_exists else 0
        if not onnx_exists:
            self._download_onnx_model(onnx_path)

    def _download_onnx_model(self, onnx_path: str):
        """Download ONNX model from HuggingFace Hub with progress logging."""
        import urllib.request
        import time
        url = f"https://huggingface.co/{self.MODEL_NAME}/resolve/main/{self.ONNX_SUBPATH}"
        logger.info(f"Downloading ONNX model from {url} ...")
        logger.info(f"Target: {onnx_path} (this is a one-time ~640 MB download)")

        def _report(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                pct = min(100, downloaded * 100 / total_size)
                if block_num % 50 == 0 or pct >= 100:
                    logger.info(f"  Download progress: {pct:.1f}% "
                               f"({downloaded // 1024 // 1024}MB / {total_size // 1024 // 1024}MB)")

        t0 = time.time()
        try:
            urllib.request.urlretrieve(url, onnx_path, reporthook=_report)
            elapsed = time.time() - t0
            final_size = os.path.getsize(onnx_path) if os.path.exists(onnx_path) else 0
            logger.info(f"ONNX model downloaded successfully: {onnx_path}")
        except Exception as e:
            elapsed = time.time() - t0
            logger.error(f"Failed to download ONNX model: {e}")
            raise

    def _load_model(self):
        import time
        if self.session is None:
            t0 = time.time()
            _get_onnxruntime()
            self._ensure_model_files()

            cache_dir = _get_model_cache_dir()
            onnx_path = os.path.join(cache_dir, "model.onnx")

            import onnxruntime as ort
            logger.info(f"Loading ONNX model from {onnx_path} ...")

            # Auto-detect GPU providers; fallback to CPU
            available = ort.get_available_providers()
            preferred = []
            if 'CUDAExecutionProvider' in available:
                preferred.append('CUDAExecutionProvider')
            if 'DmlExecutionProvider' in available:
                preferred.append('DmlExecutionProvider')
            if 'ROCMExecutionProvider' in available:
                preferred.append('ROCMExecutionProvider')
            if 'CoreMLExecutionProvider' in available:
                preferred.append('CoreMLExecutionProvider')
            preferred.append('CPUExecutionProvider')

            if preferred[0] != 'CPUExecutionProvider':
                logger.info(f"GPU provider available: {preferred[0]}")
            else:
                logger.info("No GPU provider found; using CPU.")

            sess_options = ort.SessionOptions()
            sess_options.intra_op_num_threads = 0  # use all CPU cores
            sess_options.inter_op_num_threads = 0

            t_sess0 = time.time()
            self.session = ort.InferenceSession(
                onnx_path,
                sess_options=sess_options,
                providers=preferred,
            )
            t_sess = time.time() - t_sess0
            total = time.time() - t0
            provider = self.session.get_providers()[0]
            logger.info(f"ONNX model loaded successfully on provider: {provider}")
        return self.session

    @staticmethod
    def _mean_pooling(last_hidden_state: Any, attention_mask: Any) -> Any:
        """Mean pooling over token embeddings, masking padding tokens."""
        np = _get_numpy()
        mask = np.expand_dims(attention_mask.astype(np.float32), -1)  # [batch, seq_len, 1]
        sum_embeddings = np.sum(last_hidden_state * mask, axis=1)      # [batch, hidden_dim]
        sum_mask = np.clip(np.sum(mask, axis=1), a_min=1e-9, a_max=None)
        return sum_embeddings / sum_mask

    @staticmethod
    def _l2_normalize(vectors: Any) -> Any:
        """L2 normalize embeddings."""
        np = _get_numpy()
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.clip(norms, a_min=1e-12, a_max=None)

    def _encode(self, texts: List[str], batch_size: int = 8) -> Any:
        """Encode texts into embeddings using ONNX Runtime."""
        import time
        t0 = time.time()
        np = _get_numpy()
        t_load0 = time.time()
        session = self._load_model()
        t_load = time.time() - t_load0
        tokenizer = self.tokenizer

        all_embeddings = []
        total = len(texts)
        start = time.time()
        n_batches = (total + batch_size - 1) // batch_size
        last_logged_done = 0

        def _format_eta(seconds: float) -> str:
            if seconds < 60:
                return f"{seconds:.0f}s"
            elif seconds < 3600:
                return f"{seconds/60:.0f}m {seconds%60:.0f}s"
            else:
                return f"{seconds/3600:.0f}h {(seconds%3600)/60:.0f}m"

        for batch_idx, i in enumerate(range(0, total, batch_size)):
            batch = texts[i:i + batch_size]
            t_batch0 = time.time()

            # Use lightweight tokenizers library (Rust-based, no transformers import)
            encodings = tokenizer.encode_batch(batch)
            input_ids_list = [enc.ids for enc in encodings]
            attention_mask_list = [enc.attention_mask for enc in encodings]
            type_ids_list = [enc.type_ids for enc in encodings]

            inputs = {
                "input_ids": np.array(input_ids_list, dtype=np.int64),
                "attention_mask": np.array(attention_mask_list, dtype=np.int64),
            }
            # Only include token_type_ids if the tokenizer produced them
            has_type_ids = any(len(tids) > 0 and any(tids) for tids in type_ids_list)
            if has_type_ids:
                inputs["token_type_ids"] = np.array(type_ids_list, dtype=np.int64)

            t_tok = time.time() - t_batch0

            # Build ONNX inputs dynamically based on model's expected inputs
            ort_inputs = {}
            for inp in session.get_inputs():
                name = inp.name
                if name == "input_ids":
                    ort_inputs[name] = inputs["input_ids"]
                elif name == "attention_mask":
                    ort_inputs[name] = inputs["attention_mask"]
                elif name == "token_type_ids":
                    if "token_type_ids" in inputs:
                        ort_inputs[name] = inputs["token_type_ids"]
                    else:
                        ort_inputs[name] = np.zeros_like(inputs["input_ids"], dtype=np.int64)

            t_inf0 = time.time()
            outputs = session.run(None, ort_inputs)
            t_inf = time.time() - t_inf0
            last_hidden_state = outputs[0]

            # Handle both pooled and hidden-state outputs
            if last_hidden_state.ndim == 2:
                embeddings = last_hidden_state
            else:
                embeddings = self._mean_pooling(last_hidden_state, inputs["attention_mask"])

            embeddings = self._l2_normalize(embeddings)
            all_embeddings.append(embeddings)
            t_batch = time.time() - t_batch0

            done = min(i + batch_size, total)
            # Log every time at least 5 more chunks have been processed since last log
            if done - last_logged_done >= 5 or done == total:
                elapsed = time.time() - start
                pct = done * 100.0 / total
                rate = done / elapsed if elapsed > 0 else 0
                remaining = (total - done) / rate if rate > 0 else 0
                logger.info(
                    f"[PROGRESS] {done:>5}/{total} ({pct:5.1f}%) | "
                    f"{rate:.1f} chunks/s | ETA: {_format_eta(remaining)}"
                )
                last_logged_done = done

        elapsed = time.time() - start
        rate = total / elapsed if elapsed > 0 else 0
        logger.info(f"[PROGRESS] {total:>5}/{total} (100.0%) | {rate:.1f} chunks/s total | Done in {_format_eta(elapsed)}")
        total_t = time.time() - t0

        return np.concatenate(all_embeddings, axis=0)

    def build(self, chunks: List[CodeChunk], batch_size: int = 16):
        """Build FAISS index from chunks."""
        import time
        np = _get_numpy()

        texts = [c.embedding_text for c in chunks]
        session = self._load_model()
        provider = session.get_providers()[0] if session else "CPUExecutionProvider"
        logger.info(f"[EMBED] Encoding {len(texts)} chunks with {self.MODEL_NAME} (provider: {provider}) ...")
        logger.info(f"[EMBED] Max sequence length: {self.MAX_SEQ_LENGTH} tokens. Batch size: {batch_size}")

        start = time.time()
        embeddings = self._encode(texts, batch_size=batch_size)
        elapsed = time.time() - start
        speed = len(texts) / elapsed if elapsed > 0 else 0
        logger.info(f"[EMBED] Done: {len(texts)} chunks in {elapsed:.1f}s ({speed:.1f} chunks/s)")

        self.chunk_ids = [c.chunk_id for c in chunks]
        faiss = _get_faiss()
        self.faiss_index = faiss.IndexFlatIP(self.DIMENSION)
        self.faiss_index.add(np.array(embeddings, dtype=np.float32))
        self.save()

    def search(self, query: str, top_k: int = 50) -> List[Tuple[str, float]]:
        """Return (chunk_id, cosine_similarity) sorted descending."""
        import time
        t0 = time.time()
        if self.faiss_index is None:
            return []
        np = _get_numpy()
        t_enc0 = time.time()
        query_embedding = self._encode([query], batch_size=1)
        t_enc = time.time() - t_enc0
        t_faiss0 = time.time()
        scores, indices = self.faiss_index.search(
            np.array(query_embedding, dtype=np.float32), top_k
        )
        t_faiss = time.time() - t_faiss0
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.chunk_ids):
                continue
            results.append((self.chunk_ids[int(idx)], float(score)))
        total = time.time() - t0
        return results

    def save(self):
        if self.faiss_index is None:
            return
        faiss = _get_faiss()
        faiss.write_index(self.faiss_index, self.index_path)
        meta_path = self.index_path + ".meta.json"
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump({'chunk_ids': self.chunk_ids}, f)

    def load(self) -> bool:
        if not os.path.exists(self.index_path):
            return False
        try:
            faiss = _get_faiss()
            self.faiss_index = faiss.read_index(self.index_path)
            meta_path = self.index_path + ".meta.json"
            with open(meta_path, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            self.chunk_ids = meta['chunk_ids']
            return True
        except Exception as e:
            logger.warning(f"Failed to load vector index: {e}")
            return False


# ---------------------------------------------------------------------------
# VectorRetriever
# ---------------------------------------------------------------------------

_SOURCE_TYPE_WEIGHTS = {
    'doc_example': 1.3,
    'python_api': 1.2,
    'ui_analysis': 1.15,
    'effect_implementation': 1.1,
    'scripted_module': 1.1,
    'test_example': 1.05,
    'source': 1.0,
}
