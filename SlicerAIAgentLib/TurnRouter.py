"""Turn routing helpers for traditional and generated-CLI workflows."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Optional


ROUTE_TRADITIONAL = "traditional"
ROUTE_CLI_START = "cli_start"
ROUTE_WORKFLOW_CONTROL = "workflow_control"
ROUTE_WORKFLOW_CONFLICT = "workflow_conflict"
ROUTE_WORKFLOW_REPAIR = "workflow_repair"


@dataclass(frozen=True)
class TurnRoute:
    """Classification result for one user turn."""

    route_type: str
    action: Optional[str] = None
    step_id: Optional[str] = None
    reason: str = ""

    @property
    def is_direct_workflow(self) -> bool:
        return self.route_type == ROUTE_WORKFLOW_CONTROL


class TurnRouter:
    """Classify whether a prompt needs the traditional LLM loop or CLI runtime."""

    _STEP_RE = re.compile(
        r"(?:proceed|start|run|execute|continue(?:\s+with)?)"
        r"(?:\s+workflow)?\s+step\s+['\"]?(cb_step_\d+)['\"]?",
        re.IGNORECASE,
    )

    _CONTROL_ACTIONS = {
        "done": "proceed",
        "finished": "proceed",
        "complete": "proceed",
        "completed": "proceed",
        "proceed": "proceed",
        "continue": "proceed",
        "next": "proceed",
        "skip": "skip",
        "cancel": "cancel",
    }

    @classmethod
    def classify(
        cls,
        prompt: str,
        workflow_state: Optional[Dict[str, Any]] = None,
    ) -> TurnRoute:
        """Return the route for a user prompt.

        ``workflow_state`` is intentionally small and generic.  The router only
        needs to know whether a generated CLI workflow is active, the current
        wait status, and the current step id.
        """
        state = workflow_state or {}
        active = bool(state.get("active"))
        normalized = str(prompt or "").strip()
        lowered = normalized.lower()

        if not active:
            # Initial selection still belongs to the traditional agent/tool loop.
            return TurnRoute(ROUTE_TRADITIONAL, reason="no_active_workflow")

        step_match = cls._STEP_RE.fullmatch(normalized)
        if step_match:
            return TurnRoute(
                ROUTE_WORKFLOW_CONTROL,
                action="start",
                step_id=step_match.group(1),
                reason="explicit_workflow_step",
            )

        if lowered in cls._CONTROL_ACTIONS:
            action = cls._CONTROL_ACTIONS[lowered]
            return TurnRoute(
                ROUTE_WORKFLOW_CONTROL,
                action=action,
                step_id=state.get("current_step"),
                reason="simple_workflow_control",
            )

        if state.get("status") == "waiting_for_choice":
            return TurnRoute(
                ROUTE_WORKFLOW_CONTROL,
                action="choice_made",
                step_id=state.get("current_step"),
                reason="choice_response",
            )

        return TurnRoute(
            ROUTE_WORKFLOW_CONFLICT,
            reason="active_workflow_non_control_prompt",
        )


def is_workflow_control_turn(prompt: str, workflow_state: Optional[Dict[str, Any]]) -> bool:
    """Compatibility helper for dense retrieval gating."""
    return TurnRouter.classify(prompt, workflow_state).is_direct_workflow
