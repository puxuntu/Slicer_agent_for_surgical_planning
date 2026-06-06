import json
import os
import queue
import re
import threading
import unittest
import logging
from typing import Dict, List, Optional
import vtk
import qt
import ctk
import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SLICER_AI_AGENT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
SLICER_AI_AGENT_MODULE_FILE = os.path.join(SLICER_AI_AGENT_ROOT, "SlicerAIAgent.py")

__all__ = [name for name in list(globals()) if not name.startswith('__')]
