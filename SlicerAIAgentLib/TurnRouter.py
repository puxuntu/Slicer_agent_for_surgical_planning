"""Turn routing helpers for traditional and generated-CLI workflows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


ROUTE_TRADITIONAL = "traditional"
ROUTE_CLI_START = "cli_start"
ROUTE_WORKFLOW_CONTROL = "workflow_control"
ROUTE_WORKFLOW_CONFLICT = "workflow_conflict"
ROUTE_WORKFLOW_REPAIR = "workflow_repair"
ROUTE_WORKFLOW_UNRESOLVED = "workflow_unresolved"


@dataclass(frozen=True)
class TurnRoute:
    """Classification result for one user turn."""

    route_type: str
    action: Optional[str] = None
    step_id: Optional[str] = None
    choice_value: Any = None
    confidence: float = 0.0
    reason: str = ""

    @property
    def is_direct_workflow(self) -> bool:
        return self.route_type == ROUTE_WORKFLOW_CONTROL


class TurnRouter:
    """Compatibility router for callers that do not have an LLM resolver."""

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
        if not active:
            return TurnRoute(ROUTE_TRADITIONAL, reason="no_active_workflow")
        return TurnRoute(
            ROUTE_WORKFLOW_UNRESOLVED,
            reason="active workflow turns require WorkflowIntentResolver",
        )


def is_workflow_control_turn(prompt: str, workflow_state: Optional[Dict[str, Any]]) -> bool:
    """Compatibility helper for dense retrieval gating."""
    return TurnRouter.classify(prompt, workflow_state).is_direct_workflow
