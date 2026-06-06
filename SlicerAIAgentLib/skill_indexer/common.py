"""
SkillIndexer - Dense vector retrieval index for Slicer skill knowledge base.

Implements pure dense vector (FAISS) retrieval with source-type weighting.
Indexes and model caches are stored under the project's Code_RAG/ directory.

Components:
- Chunker: splits knowledge-base files into semantic chunks
- VectorIndex: dense semantic retrieval via ONNX Runtime + FAISS
- VectorRetriever: similarity search + source_type weighting
- IndexBuilder: orchestrates incremental index building
"""

import hashlib
import json
import logging
import os
import ast
import re
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


def _get_project_root() -> str:
    """Return the repository root directory (parent of SlicerAIAgentLib/)."""
    root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    return root


def _get_index_dir() -> str:
    """Return the project-local index directory: <repo>/Resources/Code_RAG/v1/."""
    d = os.path.join(_get_project_root(), "Resources", "Code_RAG", "v1")
    return d


def _get_model_cache_dir() -> str:
    """Return the project-local model cache directory: <repo>/Resources/Code_RAG/models/."""
    d = os.path.join(_get_project_root(), "Resources", "Code_RAG", "models")
    return d


def _get_ui_analysis_docs_dir() -> str:
    """Return generated Slicer UI pre-analysis docs directory."""
    return os.path.join(
        _get_project_root(), "Resources", "Slicer_UI_PreAnalysis", "v1", "docs"
    )


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class CodeChunk:
    """A single semantic chunk from a knowledge-base file."""
    chunk_id: str           # "{rel_path}#{start_line}-{end_line}"
    file_path: str          # relative to skill root
    start_line: int
    end_line: int
    content: str            # raw text
    embedding_text: str     # text fed to the embedding model
    chunk_type: str         # function | class | heading | code_block | whole_file
    source_type: str        # doc_example | python_api | effect_implementation | ...
    language: str           # python | cpp | markdown | other


@dataclass
class RetrievedChunk:
    """A chunk returned by the dense vector retriever."""
    chunk: CodeChunk
    vector_score: float = 0.0
    final_score: float = 0.0


# ---------------------------------------------------------------------------
# Dependency helpers (mirrors SkillTools._ensure_tree_sitter pattern)
# ---------------------------------------------------------------------------

def _ensure_packages(packages: List[str]) -> bool:
    """Ensure Python packages are importable, installing if necessary."""
    missing = []
    for pkg in packages:
        try:
            __import__(pkg.replace('-', '_').split('[')[0])
        except ImportError:
            missing.append(pkg)
    if not missing:
        return True

    # Try Slicer's pip_install first
    try:
        import slicer
        for pkg in missing:
            logger.info(f"Installing {pkg} via slicer.util.pip_install...")
            slicer.util.pip_install(pkg)
        return True
    except ImportError:
        pass

    # Fallback to subprocess pip
    import subprocess
    import sys
    for pkg in missing:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg],
                check=True, capture_output=True
            )
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to install {pkg}: {e}")
            return False
    return True


def _get_faiss() -> Any:
    """Lazy import faiss with auto-install."""
    try:
        import faiss
        return faiss
    except ImportError:
        if _ensure_packages(["faiss-cpu"]):
            import faiss
            return faiss
        raise ImportError("faiss-cpu is required but could not be installed.")


def _get_onnxruntime() -> Any:
    """Lazy import onnxruntime with auto-install."""
    try:
        import onnxruntime as ort
        return ort
    except ImportError:
        if _ensure_packages(["onnxruntime"]):
            import onnxruntime as ort
            return ort
        raise ImportError("onnxruntime is required but could not be installed.")


def _get_numpy() -> Any:
    try:
        import numpy as np
        return np
    except ImportError:
        if _ensure_packages(["numpy>=1.21.0"]):
            import numpy as np
            return np
        raise


# ---------------------------------------------------------------------------
# API description extraction (for embedding text enrichment)
# ---------------------------------------------------------------------------


def _extract_api_description(content: str) -> str:
    """Extract function signature + docstring from a Python code chunk."""
    import ast
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                sig_line = content.split('\n')[0].strip()
                doc = ast.get_docstring(node)
                parts = []
                if sig_line:
                    parts.append(f"API: {sig_line}")
                if doc:
                    parts.append(f"Description: {doc}")
                return "\n".join(parts) if parts else ""
    except Exception:
        pass
    return ""


# ---------------------------------------------------------------------------
# Chunker
# ---------------------------------------------------------------------------


__all__ = [name for name in list(globals()) if not name.startswith('__')]
