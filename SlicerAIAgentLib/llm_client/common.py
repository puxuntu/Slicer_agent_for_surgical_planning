"""
LLMClient - HTTP client for LLM API communication.

Supports streaming responses, conversation history, token tracking, and tool calling.
System prompt is loaded from external markdown file.

Compatible with OpenAI-compatible APIs including Kimi, OpenAI, and others.
"""

import concurrent.futures
import json
import logging
import os
import re
import socket
import time
import urllib.error
import urllib.request
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)



__all__ = [name for name in list(globals()) if not name.startswith('__')]
