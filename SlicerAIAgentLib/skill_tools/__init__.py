from .executor import *
from .schemas import *

import os as _os
import threading as _threading

# Process-wide shared executor: the main agent registers its instance so
# other consumers (extension CLI generation) reuse it instead of loading a
# second ONNX embedding session + vector index (~700MB, seconds of cold load).
_shared_executor = None
_shared_lock = _threading.Lock()


def register_shared_executor(executor) -> None:
    """Publish an executor instance for reuse by other consumers."""
    global _shared_executor
    with _shared_lock:
        _shared_executor = executor


def get_shared_executor(skill_path):
    """Return the shared executor when it serves the same skill path, else None."""
    with _shared_lock:
        executor = _shared_executor
    if executor is None or not skill_path:
        return None
    try:
        wanted = _os.path.normcase(_os.path.abspath(str(skill_path)))
        actual = _os.path.normcase(_os.path.abspath(str(executor.skill_path)))
    except Exception:
        return None
    return executor if wanted == actual else None


__all__ = [
    'SkillToolExecutor', 'get_skill_tools',
    'register_shared_executor', 'get_shared_executor',
]
