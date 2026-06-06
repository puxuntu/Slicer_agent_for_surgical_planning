from .common import *


class LogicIndexMixin:
    def clearConversation(self):
        if self.conversationStore:
            self.conversationStore.clear()
        if self.llmClient:
            self.llmClient.clearHistory()

    def pauseProcessing(self):
        self._processing = False

    def resumeProcessing(self):
        self._processing = True

    def cleanup(self):
        if self.llmClient:
            self.llmClient.cleanup()
        if self.executor:
            self.executor.cleanup()

    def _start_index_background_check(self):
        """
        Check whether a vector index exists on disk.
        Does NOT auto-build or auto-update — the user must run scripts/build_rag.py manually.
        """
        try:
            from SlicerAIAgentLib.SkillIndexer import IndexBuilder

            # Use the same root directory as SlicerAIAgent.py so that the index
            # path is deterministic regardless of how SkillIndexer.py resolves __file__.
            self._index_dir = os.path.join(
                SLICER_AI_AGENT_ROOT, "Resources", "Code_RAG", "v1"
            )
            self._indexBuilder = IndexBuilder(self.skill_path, index_dir=self._index_dir)
            if self._indexBuilder.index_exists():
                self._index_status = "Ready"
                logger.info(f"Vector index found: {self._index_dir}")
            else:
                self._index_status = "Missing"
                logger.info(f"Vector index not found at {self._index_dir}. Run scripts/build_rag.py to create it.")
        except Exception as e:
            logger.warning(f"Could not check index status: {e}")
            self._index_status = "Error"

    def _start_vector_warmup(self):
        """
        Start a background thread that eagerly loads the tokenizer and ONNX session.
        This prevents the ~4-minute first-prompt delay caused by transformers import.
        """
        import threading
        def _warmup():
            try:
                if not self.toolExecutor:
                    return
                if not self.toolExecutor.has_vector_index():
                    return
                retriever = self.toolExecutor._vector_retriever
                if retriever is None:
                    return
                vector = retriever.vector
                if vector is None:
                    return
                # Trigger tokenizer loading + ONNX session creation
                import time
                t0 = time.time()
                vector._ensure_model_files()
                t1 = time.time()
                vector._load_model()
                t2 = time.time()
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger.warning(f"Background vector warmup failed: {e}")
        thread = threading.Thread(target=_warmup, daemon=True)
        thread.start()
        return thread

    def get_index_status(self) -> str:
        """Return current vector index status for UI display."""
        return getattr(self, '_index_status', 'Unknown')
