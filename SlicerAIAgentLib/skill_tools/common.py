"""
SkillTools - Tool implementations for searching the Slicer skill.

Provides cross-platform search functionality:
- All platforms: Uses ripgrep (rg) for fast aggregated search.
  Windows falls back to a bundled rg.exe; Linux/macOS require system rg in PATH.
"""

import os
import re
import json
import time
import subprocess
import platform
import logging
import shutil
import sys
import sysconfig
from typing import List, Dict, Optional, Any
from pathlib import Path
from ..ExtensionCLILoader import get_dynamic_extension_tools, dispatch_extension_cli_tool

logger = logging.getLogger(__name__)

# Paths to bundled ripgrep binaries. Windows builds historically shipped rg.exe;
# Linux/macOS may ship an executable named rg in the same folder.
_LIB_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BIN_DIR = os.path.join(_LIB_DIR, "bin")
_RG_EXE_PATH = os.path.join(_BIN_DIR, "rg.exe")
_RG_UNIX_PATH = os.path.join(_BIN_DIR, "rg")
_RG_PIP_PACKAGE = "ripgrep"


def _get_project_root() -> str:
    return os.path.dirname(_LIB_DIR)


def _get_ui_analysis_docs_dir() -> str:
    return os.path.join(
        _get_project_root(), "Resources", "Slicer_UI_PreAnalysis", "v1", "docs"
    )



__all__ = [name for name in list(globals()) if not name.startswith('__')]
