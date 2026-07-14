"""
ExtensionCLIAnalyzer - named-phase v2 pipeline for analyzing Slicer extensions
and generating operation CLIs (tool schemas + code templates).

The pipeline is cookbook-driven: a markdown cookbook describing the extension's
step-by-step workflow is REQUIRED.  Without it the pipeline aborts.

Uses the same LLM provider as the main agent to analyze extension source code,
identify operations, and generate validated code templates that integrate with
the SlicerAIAgent tool system.
"""

import ast
import json
import logging
import os
import re as _re
import textwrap
import traceback
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

# Path to the analyzer system prompt
_ANALYZER_PROMPT_PATH = os.path.join(
    _PROJECT_ROOT,
    "Resources", "Prompts", "extension_cli_analyzer_prompt.md",
)

# Maximum source file size to send to LLM (chars)
_MAX_SOURCE_FOR_LLM = 300_000

# Maximum revision attempts for failed validation
_MAX_REVISION_ATTEMPTS = 3

# Regex to strip JavaScript-style // comments from LLM JSON output.
# Matches // comments that appear after JSON structural chars (, : [ ] { })
# or whitespace — avoids breaking URLs inside string values.
_JS_COMMENT_RE = _re.compile(r'(?<=[,\[\]{}:\s])\s*//[^\n]*')

# Derive interaction_type from node_class.  interaction_type is kept as a
# convenience label for display / logging but is NEVER used as a gate — the
# presence of a `user_interaction` sub-operation in `sub_operations` is the
# authoritative signal that a step requires user interaction.
_NODE_CLASS_TO_INTERACTION_TYPE = {
    "vtkMRMLMarkupsCurveNode": "curve",
    "vtkMRMLMarkupsClosedCurveNode": "closed_curve",
    "vtkMRMLMarkupsPlaneNode": "plane",
    "vtkMRMLMarkupsLineNode": "line",
    "vtkMRMLMarkupsAngleNode": "angle",
    "vtkMRMLMarkupsFiducialNode": "fiducial",
    "vtkMRMLMarkupsROINode": "roi",
}

CANONICAL_OPERATION_TYPES = {
    "extension_op",
    "slicer_op",
    "user_interaction",
    "user_choice",
    # Decision + on-accept extension action + branch (jump/stop/run body).
    "branch_op",
}


def _operation_type_for_step(step: Dict[str, Any]) -> str:
    """Return the canonical operation type, with legacy fallback."""
    if not isinstance(step, dict):
        return ""
    for key in ("operation_type", "op_type"):
        value = _text_or_empty(step.get(key))
        if value:
            return value

    sub_op_types = {
        _text_or_empty(so.get("op_type"))
        for so in (step.get("sub_operations") or [])
        if isinstance(so, dict) and _text_or_empty(so.get("op_type")) in CANONICAL_OPERATION_TYPES
    }
    if len(sub_op_types) == 1:
        return next(iter(sub_op_types))

    legacy_step_type = _text_or_empty(step.get("step_type"))
    if legacy_step_type == "automated":
        if any(
            isinstance(so, dict) and so.get("op_type") == "slicer_op"
            for so in (step.get("sub_operations") or [])
        ):
            return "slicer_op"
        return "extension_op"
    if legacy_step_type == "interactive":
        return "user_interaction"
    if legacy_step_type == "user_choice":
        return "user_choice"
    return legacy_step_type


def _legacy_step_type_for_operation(operation_type: str) -> str:
    """Map canonical operation type to the old execution category."""
    if operation_type in ("extension_op", "slicer_op"):
        return "automated"
    if operation_type == "user_interaction":
        return "interactive"
    if operation_type in ("user_choice", "branch_op"):
        # branch_op is presented/recorded like a user_choice decision; its
        # on-accept action is generated separately as a per-step template.
        return "user_choice"
    return operation_type or "automated"


def _is_automated_operation(operation_type: str) -> bool:
    return operation_type in ("extension_op", "slicer_op")


def _derive_interaction_type(node_class, fallback="generic"):
    """Derive a human-readable interaction type from a node class string."""
    return _NODE_CLASS_TO_INTERACTION_TYPE.get(node_class or "", fallback)


def _infer_final_state_intent(text: str) -> Dict[str, Any]:
    """Infer whether an operation asks to set a final state or invert state."""
    raw = text or ""
    normalized = _re.sub(r"[^a-z0-9]+", " ", raw.lower()).strip()
    action_text = _re.sub(r"^\d+\s+", "", normalized).strip()
    padded = f" {normalized} "
    invert_patterns = (
        " invert current state ",
        " invert the current state ",
        " toggle current state ",
        " toggle the current state ",
        " flip current state ",
        " flip the current state ",
        " switch to opposite ",
        " switch to the opposite ",
    )
    true_patterns = (
        " toggle on ",
        " turn on ",
        " switch on ",
        " set on ",
        " enable ",
        " enabled ",
        " show ",
        " visible ",
        " visibility on ",
        " select ",
        " selected ",
        " checked ",
        " tick ",
        " activate ",
        " activated ",
    )
    false_patterns = (
        " toggle off ",
        " turn off ",
        " switch off ",
        " set off ",
        " disable ",
        " disabled ",
        " hide ",
        " hidden ",
        " invisible ",
        " visibility off ",
        " unselect ",
        " deselect ",
        " unchecked ",
        " uncheck ",
        " untick ",
        " clear ",
        " deactivate ",
        " deactivated ",
    )
    if any(pattern in padded for pattern in invert_patterns):
        return {"mode": "invert", "state": None, "confidence": "high"}
    leading_false_patterns = (
        "toggle off ",
        "turn off ",
        "switch off ",
        "set off ",
        "disable ",
        "hide ",
        "unselect ",
        "deselect ",
        "uncheck ",
        "clear ",
        "untick ",
        "deactivate ",
    )
    leading_true_patterns = (
        "toggle on ",
        "turn on ",
        "switch on ",
        "set on ",
        "enable ",
        "show ",
        "select ",
        "check ",
        "tick ",
        "activate ",
    )
    if any(action_text.startswith(pattern) for pattern in leading_false_patterns):
        return {"mode": "set", "state": False, "confidence": "high"}
    if any(action_text.startswith(pattern) for pattern in leading_true_patterns):
        return {"mode": "set", "state": True, "confidence": "high"}
    true_hit = any(pattern in padded for pattern in true_patterns)
    false_hit = any(pattern in padded for pattern in false_patterns)
    if true_hit and not false_hit:
        return {"mode": "set", "state": True, "confidence": "high"}
    if false_hit and not true_hit:
        return {"mode": "set", "state": False, "confidence": "high"}
    if true_hit and false_hit:
        return {"mode": "ambiguous", "state": None, "confidence": "low"}
    return {"mode": "unspecified", "state": None, "confidence": "none"}


def _collect_attr_chain(node) -> List[str]:
    """Recursively collect attribute chain from an AST node.

    Turns `slicer.app.layoutManager().setLayout` into
    ["slicer", "app", "layoutManager", "setLayout"].
    """
    import ast as _ast
    parts = []
    current = node
    while True:
        if isinstance(current, _ast.Attribute):
            parts.append(current.attr)
            current = current.value
        elif isinstance(current, _ast.Call):
            current = current.func
        elif isinstance(current, _ast.Name):
            parts.append(current.id)
            break
        elif isinstance(current, _ast.Subscript):
            current = current.value
        else:
            break
    parts.reverse()
    return parts


def _validate_extension_name(name: str) -> str:
    """Validate and sanitize an extension name to prevent path traversal.

    Returns the sanitized name.  Raises ValueError if the name is invalid.
    """
    if not name or not name.strip():
        raise ValueError("Extension name must not be empty.")
    # Reject path separators and traversal patterns
    if any(ch in name for ch in ("/", "\\", "\x00")):
        raise ValueError(
            f"Invalid extension name '{name}': contains path separators."
        )
    if ".." in name:
        raise ValueError(
            f"Invalid extension name '{name}': contains '..' traversal."
        )
    return name.strip()


def _tokenize_name(name: str) -> set:
    """Split a CamelCase/underscore name into lowercase tokens."""
    import re
    name = _text_or_empty(name)
    parts = re.split(r'(?<=[a-z])(?=[A-Z])|_|(?<=[A-Z])(?=[A-Z][a-z])', name)
    return {p.lower() for p in parts if p}


def _text_or_empty(value: Any) -> str:
    """Return a safe text value for fields that may come from LLM JSON."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _optional_text(value: Any) -> Optional[str]:
    """Return a stripped string for meaningful text fields, otherwise None."""
    if value is None or isinstance(value, bool):
        return None
    text = _text_or_empty(value).strip()
    return text or None


def _text_list(value: Any) -> List[str]:
    """Coerce a possibly malformed LLM field into a list of text values."""
    if value is None:
        return []
    if isinstance(value, list):
        return [_text_or_empty(v) for v in value if v is not None]
    return [_text_or_empty(value)]


def _int_or_none(value: Any) -> Optional[int]:
    """Coerce simple integer-like values without treating booleans as numbers."""
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _name_similarity(name_a: str, name_b: str) -> float:
    """Jaccard similarity between tokens of two names."""
    ta = _tokenize_name(name_a)
    tb = _tokenize_name(name_b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _parse_default_value(default_str: str):
    """Parse a default value string from AST into a Python value."""
    if default_str == "True":
        return True
    if default_str == "False":
        return False
    if default_str == "None":
        return None
    try:
        return int(default_str)
    except (ValueError, TypeError):
        pass
    try:
        return float(default_str)
    except (ValueError, TypeError):
        pass
    return default_str


class _AddNodeVisitor(ast.NodeVisitor):
    """AST visitor that detects AddNode/AddNewNodeByClass calls on method parameters."""

    def __init__(self, param_names: set):
        self.param_names = param_names
        self.params_added_to_scene = set()   # params passed to AddNode()
        self.has_addnewnodebyclass = False    # method calls AddNewNodeByClass anywhere
        self._added_node_args = []            # raw args to AddNode calls

    def visit_Call(self, node):
        func_name = self._get_qualified_name(node.func)
        # slicer.mrmlScene.AddNode(param)
        if func_name and func_name.endswith("AddNode"):
            for arg in node.args:
                if isinstance(arg, ast.Name) and arg.id in self.param_names:
                    self.params_added_to_scene.add(arg.id)
                elif isinstance(arg, ast.Name):
                    self._added_node_args.append(arg.id)
            # Don't recurse into the call's args
            return
        # slicer.mrmlScene.AddNewNodeByClass(...)
        if func_name and func_name.endswith("AddNewNodeByClass"):
            self.has_addnewnodebyclass = True
            return
        self.generic_visit(node)

    @staticmethod
    def _get_qualified_name(node):
        parts = []
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
        return ".".join(reversed(parts)) if parts else None



__all__ = [name for name in list(globals()) if not name.startswith('__')]
