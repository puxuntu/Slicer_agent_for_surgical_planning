"""
CookbookParser - Parse extension cookbook markdown files into structured
step definitions.

Cookbook .md files are user-facing guides (numbered step lists) that serve
as the ground truth for the CLI generation pipeline.  Each numbered step must
include a simple operation annotation, for example ``[op=extension_op]``.
The parser records this broad type only; technical metadata is inferred later
from extension source/UI evidence.

Type definitions:
- extension_op: Calls this extension's own Logic methods (code from local source).
- slicer_op: Uses Slicer core API not in this extension (needs KB search).
- user_interaction: User physically acts in 3D view (draw, position, drag).
- user_choice: Agent cannot determine value, must ask user via chat.
"""

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

VALID_OPERATION_TYPES = {
    "extension_op",
    "slicer_op",
    "user_interaction",
    "user_choice",
    # A user decision that ALSO performs an extension action (e.g. tick a
    # checkbox that enables an optional mode) and BRANCHES the workflow
    # (run the optional body, jump to a step, or stop). Distinct from a
    # choice-only user_choice (which just selects a value/node).
    "branch_op",
    # Present already-generated results (e.g. an output table) for the user to
    # inspect; the only interaction is a Confirm that advances the workflow. No
    # code runs and nothing is selected -- purely a checkpoint for human review.
    "review_op",
}

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SubOperation:
    """A single atomic operation within a cookbook step."""
    op_type: str                    # "extension_op" | "slicer_op" | "user_interaction" | "user_choice"
    description: str                # What the operation does (prose)
    extension_method_hint: Optional[str] = None   # Guessed logic method name
    slicer_api_keywords: List[str] = field(default_factory=list)  # KB search hints
    interaction_type: Optional[str] = None        # "curve", "plane", "line", "fiducial"
    node_class: Optional[str] = None              # VTK MRML node class for interaction
    placement_instructions: Optional[str] = None   # Guidance text for the user
    evidence_type: Optional[str] = None            # logic_method/widget_connection/slicer_core/etc.
    evidence_id: Optional[str] = None              # Method name, widget name, or matched concept
    confidence: Optional[str] = None               # high | medium | low
    interaction_kind: Optional[str] = None         # markup_placement | view_adjustment | none
    slicer_op_category: Optional[str] = None       # layout_slice_view, markups_display, etc.
    # user_choice-specific fields
    question: Optional[str] = None                # Question to ask the user
    choices: List[Dict] = field(default_factory=list)  # [{"label": "...", "value": "..."}]
    parameter_name: Optional[str] = None          # Snake_case identifier for the choice
    default_value: Optional[str] = None           # Optional default value


@dataclass
class CookbookStep:
    """A single numbered step from the cookbook."""
    step_number: int
    title: str
    description: str                        # Full prose of the step
    operation_type: str = ""                # Canonical op from [op=...]
    sub_operations: List[SubOperation] = field(default_factory=list)
    depends_on: List[int] = field(default_factory=list)
    is_mixed: bool = False                  # True if sub_operations span >1 op_type


@dataclass
class CookbookDef:
    """Parsed cookbook for a single extension."""
    extension_name: str
    source_file: str
    steps: List[CookbookStep] = field(default_factory=list)
    raw_content: str = ""

    def get_sub_ops_by_type(self, op_type: str) -> List[tuple]:
        """Return (step_number, SubOperation) pairs for a given op_type."""
        result = []
        for step in self.steps:
            for sub in step.sub_operations:
                if sub.op_type == op_type:
                    result.append((step.step_number, sub))
        return result

    def classify_step_type(self, step: CookbookStep) -> str:
        """Return the canonical operation type for the step."""
        if step.operation_type:
            return step.operation_type
        if step.sub_operations:
            return step.sub_operations[0].op_type
        return "extension_op"


# ---------------------------------------------------------------------------
# CookbookParser
# ---------------------------------------------------------------------------

class CookbookParser:
    """Parse free-form cookbook markdown into structured step definitions.

    Only does regex-based step extraction and operation annotation parsing.
    Source-derived technical metadata is inferred later by the analyzer.
    """

    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(
        self,
        cookbook_path: str,
    ) -> Optional[CookbookDef]:
        """Read a cookbook .md file and parse into numbered steps.

        This only does regex-based step extraction and [op=...] parsing
        (instant, no LLM).

        Args:
            cookbook_path: Absolute path to the .md cookbook file.

        Returns:
            CookbookDef, or None if the file is empty / unparseable.
        """
        if not os.path.isfile(cookbook_path):
            logger.warning("Cookbook not found: %s", cookbook_path)
            return None

        with open(cookbook_path, "r", encoding="utf-8") as f:
            raw = f.read()

        if not raw.strip():
            return None

        # Derive extension name from filename
        basename = os.path.basename(cookbook_path)
        ext_name = basename.replace(".md", "")
        if ext_name.startswith("Slicer"):
            ext_name = ext_name[len("Slicer"):]

        # Parse numbered steps into simple CookbookStep objects
        raw_steps = self._split_numbered_steps(raw)
        if not raw_steps:
            logger.warning("No numbered steps found in cookbook: %s", cookbook_path)
            return None

        steps = []
        for step_num, step_text in raw_steps:
            operation_type, clean_text = self._extract_operation_annotation(
                step_num, step_text, cookbook_path,
            )
            first_line = clean_text.split("\n", 1)[0]
            steps.append(CookbookStep(
                step_number=step_num,
                title=first_line[:120],
                description=clean_text,
                operation_type=operation_type,
                sub_operations=[],  # populated later in _cookbook_build_stage_map
                is_mixed=False,
            ))

        # Resolve dependencies (sequential ordering)
        self._resolve_dependencies(steps)
        return CookbookDef(
            extension_name=ext_name,
            source_file=cookbook_path,
            steps=steps,
            raw_content=raw,
        )

    # ------------------------------------------------------------------
    # Step splitting
    # ------------------------------------------------------------------

    _STEP_RE = re.compile(r"^(\d+)\.\s+(.+)", re.MULTILINE)
    _OP_ANNOTATION_RE = re.compile(
        r"^(\d+\.\s*)\[op\s*=\s*([A-Za-z_]+)\]\s*(.*)$",
        re.DOTALL,
    )
    def _extract_operation_annotation(
        self,
        step_number: int,
        step_text: str,
        cookbook_path: str,
    ) -> tuple:
        """Return (operation_type, cleaned_step_text) from a numbered step."""
        match = self._OP_ANNOTATION_RE.match(step_text.strip())
        if not match:
            raise ValueError(
                f"Cookbook step {step_number} in {cookbook_path} is missing "
                "a required [op=...] annotation. Valid values: "
                + ", ".join(sorted(VALID_OPERATION_TYPES))
            )
        _prefix, op_type, remainder = match.groups()
        op_type = op_type.strip()
        if op_type not in VALID_OPERATION_TYPES:
            raise ValueError(
                f"Cookbook step {step_number} in {cookbook_path} has invalid "
                f"operation type '{op_type}'. Valid values: "
                + ", ".join(sorted(VALID_OPERATION_TYPES))
            )
        cleaned = remainder.strip()
        return op_type, cleaned

    def _split_numbered_steps(self, markdown: str) -> List[tuple]:
        """Split markdown into (step_number, step_text) pairs.

        Each step's text extends from its match to the next match (or EOF).
        """
        matches = list(self._STEP_RE.finditer(markdown))
        if not matches:
            return []

        result = []
        for i, m in enumerate(matches):
            num = int(m.group(1))
            start = m.start()
            # Text runs from after the match to the start of the next match
            end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
            text = markdown[start:end].strip()
            result.append((num, text))

        return result

    # ------------------------------------------------------------------
    # Dependency resolution
    # ------------------------------------------------------------------

    def _resolve_dependencies(self, steps: List[CookbookStep]) -> None:
        """Assign depends_on based on sequential ordering and cross-references."""
        step_by_num = {s.step_number: s for s in steps}

        for i, step in enumerate(steps):
            # Default: depends on the previous step
            if i > 0:
                step.depends_on.append(steps[i - 1].step_number)

            # Check for explicit cross-references in the text
            # e.g. "repeat step 13" or "as in step 5".
            # Only BACKWARD references are dependencies: a DAG edge must point to an
            # earlier step. A forward reference (e.g. "if not, jump to step 10") is a
            # conditional branch target handled by repeat_blocks, not a dependency --
            # adding it would create an unsatisfiable cycle and deadlock the workflow.
            refs = re.findall(r"step\s+(\d+)", step.description, re.IGNORECASE)
            for ref_str in refs:
                ref_num = int(ref_str)
                if ref_num < step.step_number and ref_num in step_by_num:
                    if ref_num not in step.depends_on:
                        step.depends_on.append(ref_num)
