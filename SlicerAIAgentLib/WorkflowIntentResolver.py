"""Validated LLM resolver for natural-language generated-workflow turns."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

from .TurnRouter import (
    ROUTE_TRADITIONAL,
    ROUTE_WORKFLOW_CONFLICT,
    ROUTE_WORKFLOW_CONTROL,
    ROUTE_WORKFLOW_UNRESOLVED,
    TurnRoute,
)

logger = logging.getLogger(__name__)


class WorkflowIntentResolver:
    """Resolve active-workflow chat turns without wording-specific rules."""

    def __init__(self, llm_client, confidence_threshold: float = 0.80):
        self.llm_client = llm_client
        self.confidence_threshold = confidence_threshold

    def resolve(
        self,
        prompt: str,
        workflow_state: Optional[Dict[str, Any]] = None,
        step_info: Optional[Dict[str, Any]] = None,
    ) -> TurnRoute:
        state = workflow_state or {}
        if not state.get("active"):
            return TurnRoute(ROUTE_TRADITIONAL, reason="no_active_workflow")
        if not self.llm_client or not getattr(self.llm_client, "api_key", None):
            return TurnRoute(
                ROUTE_WORKFLOW_UNRESOLVED,
                reason="workflow intent resolver is unavailable",
            )

        status = state.get("status", "")
        if status == "waiting_for_user":
            allowed_actions = ["proceed", "cancel"]
            if (step_info or {}).get("is_optional") or (step_info or {}).get("can_skip"):
                allowed_actions.append("skip")
        elif status == "waiting_for_choice":
            allowed_actions = ["choice_made", "cancel"]
        else:
            allowed_actions = ["start", "cancel"]
        current_step = state.get("current_step")
        choices = (step_info or {}).get("choices") or []
        payload = {
            "user_prompt": str(prompt or ""),
            "workflow_state": state,
            "current_step_info": step_info or {},
            "allowed_routes": [ROUTE_WORKFLOW_CONTROL, ROUTE_WORKFLOW_CONFLICT],
            "allowed_actions": allowed_actions,
            "allowed_step_id": current_step,
            "allowed_choices": choices,
        }
        messages = [
            {
                "role": "system",
                "content": (
                    "Resolve one natural-language turn while a generated workflow is active. "
                    "Return strict JSON only. Never invent an action, step, or closed-form "
                    "choice. Use workflow_conflict when the request is a separate task."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Return exactly: {\"route_type\":\"workflow_control|workflow_conflict\","
                    "\"action\":null,\"step_id\":null,\"choice_value\":null,"
                    "\"confidence\":0.0,\"reason\":\"\"}. "
                    "For workflow_control, select only an allowed action and the allowed "
                    "step_id. For closed-form choices, return the supplied choice value. "
                    "When uncertain, use confidence below 0.8.\n\n"
                    f"Input:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
                ),
            },
        ]
        try:
            decision = self._extract_json(self._call_llm(messages))
        except Exception as exc:
            logger.warning("Workflow intent LLM resolver failed: %s", exc)
            return TurnRoute(ROUTE_WORKFLOW_UNRESOLVED, reason=f"resolver failed: {exc}")

        confidence = self._coerce_confidence(decision.get("confidence"))
        if confidence < self.confidence_threshold:
            return TurnRoute(
                ROUTE_WORKFLOW_UNRESOLVED,
                confidence=confidence,
                reason=decision.get("reason", "resolver confidence below threshold"),
            )
        route_type = decision.get("route_type")
        if route_type == ROUTE_WORKFLOW_CONFLICT:
            return TurnRoute(
                ROUTE_WORKFLOW_CONFLICT,
                confidence=confidence,
                reason=decision.get("reason", ""),
            )
        if route_type != ROUTE_WORKFLOW_CONTROL:
            return TurnRoute(ROUTE_WORKFLOW_UNRESOLVED, reason="invalid workflow route")

        action = decision.get("action")
        step_id = decision.get("step_id")
        if action not in allowed_actions or step_id != current_step:
            return TurnRoute(
                ROUTE_WORKFLOW_UNRESOLVED,
                confidence=confidence,
                reason="LLM selected an action or step outside the allowed workflow state",
            )
        choice_value = decision.get("choice_value")
        if action == "choice_made" and choice_value is None:
            return TurnRoute(
                ROUTE_WORKFLOW_UNRESOLVED,
                confidence=confidence,
                reason="LLM did not provide a choice value",
            )
        if action == "choice_made" and choices:
            allowed_values = [choice.get("value", choice.get("label")) for choice in choices]
            if choice_value not in allowed_values:
                return TurnRoute(
                    ROUTE_WORKFLOW_UNRESOLVED,
                    confidence=confidence,
                    reason="LLM selected a choice outside the allowed choices",
                )
        return TurnRoute(
            ROUTE_WORKFLOW_CONTROL,
            action=action,
            step_id=step_id,
            choice_value=choice_value,
            confidence=confidence,
            reason=decision.get("reason", ""),
        )

    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        payload = self.llm_client._buildPayload(
            messages, stream=False, tools=None, thinking=False, reasoning_effort="low"
        )
        request = self.llm_client._buildRequest(self.llm_client._getChatUrl(), payload)
        data = self.llm_client._fetchWithDiagnostics(request)
        if self.llm_client._isClaude():
            data = self.llm_client._normalizeClaudeResponse(data)
        return self.llm_client._coerceText(data["choices"][0]["message"].get("content", ""))

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        match = re.search(r"\{.*\}", str(text or ""), re.DOTALL)
        data = json.loads(match.group(0) if match else str(text or ""))
        if not isinstance(data, dict):
            raise ValueError("resolver response is not a JSON object")
        return data

    @staticmethod
    def _coerce_confidence(value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0
