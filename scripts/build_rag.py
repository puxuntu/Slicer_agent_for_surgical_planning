"""
Standalone script to build the dense vector retrieval index.
Run this to create/update the FAISS vector index under Resources/Code_RAG/v1/.
Uses ONNX Runtime for embedding (no PyTorch/CUDA required).
"""
import os
import sys
import logging
import time
import importlib.util

# Project root is one level up from this script
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
sys.path.insert(0, _PROJECT_ROOT)

_spec = importlib.util.spec_from_file_location(
    "SkillIndexer",
    os.path.join(_PROJECT_ROOT, "SlicerAIAgentLib", "SkillIndexer.py")
)
SkillIndexer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SkillIndexer)
IndexBuilder = SkillIndexer.IndexBuilder

SKILL_PATH = os.path.join(_PROJECT_ROOT, "Resources", "Skills", "slicer-skill-full")
SLICER_SOURCE_ROOT = os.path.join(SKILL_PATH, "slicer-source")
UI_ANALYSIS_OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "Resources", "Slicer_UI_PreAnalysis", "v1")


def _build_ui_analysis_if_possible() -> None:
    """Build generated UI-analysis docs before indexing, if Slicer source exists."""
    script_path = os.path.join(_PROJECT_ROOT, "scripts", "build_ui_analysis.py")
    if not os.path.isdir(SLICER_SOURCE_ROOT) or not os.path.isfile(script_path):
        logger.info("UI pre-analysis skipped: Slicer source or builder script not found.")
        return
    spec = importlib.util.spec_from_file_location("build_ui_analysis", script_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    logger.info("[STAGE 0/4] Building Slicer UI pre-analysis...")
    manifest = module.build_ui_analysis(
        module.Path(SLICER_SOURCE_ROOT),
        module.Path(UI_ANALYSIS_OUTPUT_DIR),
        clean=True,
    )
    logger.info(
        "UI pre-analysis ready: %d UI files, %d controls.",
        manifest.get("ui_file_count", 0),
        manifest.get("control_count", 0),
    )

if __name__ == "__main__":
    if not os.path.isdir(SKILL_PATH):
        logger.error(f"Skill directory not found: {SKILL_PATH}")
        sys.exit(1)

    total_start = time.time()
    logger.info(f"Skill path: {SKILL_PATH}")
    _build_ui_analysis_if_possible()
    builder = IndexBuilder(SKILL_PATH)

    if builder.index_exists():
        logger.info("Existing index found, checking for incremental updates...")
    else:
        logger.info("No existing index found, starting fresh build...")

    logger.info("[STAGE 1/4] Scanning and chunking files...")
    success = builder.build_or_update()
    total_elapsed = time.time() - total_start
    logger.info(f"[DONE] Total elapsed time: {total_elapsed:.1f}s ({total_elapsed/60:.1f} min)")

    if success:
        logger.info("[STAGE 4/4] Loading retriever and running sanity check...")
        retriever = builder.load_retriever()
        if retriever and retriever.is_ready():
            logger.info("Retriever loaded and ready.")
            try:
                results = retriever.search("load a volume and display it", top_k=5)
                logger.info(f"Sanity search returned {len(results)} results.")
                for i, r in enumerate(results, 1):
                    logger.info(f"  [{i}] {r.chunk.file_path} ({r.chunk.start_line}-{r.chunk.end_line}) score={r.final_score:.3f}")
            except Exception as e:
                logger.warning(f"Sanity search failed: {e}")
        logger.info("Index build/update completed successfully.")
    else:
        logger.error("Index build/update failed.")
        sys.exit(1)
