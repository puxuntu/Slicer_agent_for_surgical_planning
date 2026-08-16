"""Voice control for the guided runtime.

Five modules, split along the one line that matters in this codebase: what may
touch Qt and the MRML scene, and what may not.

============  =============================================================
module        role
============  =============================================================
``audio``     microphone capture (always-on, energy-segmented) and playback.
              Owns the only third-party binary dependency in the feature
              (``sounddevice``), installed at runtime and degrading to a
              named reason rather than an ImportError.
``asr_client`` speech -> text, qwen3-asr-flash over DashScope.
``tts_client`` text -> speech, qwen3-tts-flash over DashScope.
``grammar``   the step on screen, reduced to the closed set of utterances it
              will accept. A mirror of the panel's own render branch.
``commands``  one transcript -> one action, deterministic first and a small
              constrained model call only when that is uncertain.
============  =============================================================

Every module here is **Qt-free and Slicer-free at import time**, so the whole
matcher can be exercised outside Slicer (see the matcher checks). The Qt half
lives in ``SlicerAIAgentLib/app/widget_voice.py``, which is the only place that
touches the workflow panel, the MRML scene or the stream queue.

The threading contract, which is not optional: capture runs on its own thread
and the ASR round trip on the listener's dispatch thread. Neither may touch
MRML or a Qt widget. Results cross to the Qt main thread through the existing
``_streamQueue`` + 50 ms poll timer, exactly like every other background
producer in this extension.
"""

from .grammar import (  # noqa: F401
    StepGrammar,
    build_step_grammar,
    spoken_prompt,
)
from .commands import (  # noqa: F401
    VoiceCommand,
    resolve,
    resolve_llm,
)

__all__ = [
    "StepGrammar",
    "build_step_grammar",
    "spoken_prompt",
    "VoiceCommand",
    "resolve",
    "resolve_llm",
]
