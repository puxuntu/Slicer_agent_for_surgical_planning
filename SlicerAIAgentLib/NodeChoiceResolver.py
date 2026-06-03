"""Lightweight LLM resolver for ambiguous generated-CLI node choices."""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class NodeChoiceResolver:
    """Resolve scene-node choices with a narrow JSON-only LLM call."""

    def __init__(
        self,
        llm_client,
        confidence_threshold: float = 0.80,
        max_candidates: int = 20,
    ):
        self.llm_client = llm_client
        self.confidence_threshold = confidence_threshold
        self.max_candidates = max_candidates

    def should_resolve(self, step_info: Dict[str, Any], candidates: List[Dict[str, str]]) -> bool:
        """Return True when this is an open-ended scene-node choice."""
        if not self.llm_client or not getattr(self.llm_client, "api_key", None):
            return False
        if not isinstance(step_info, dict):
            return False
        if step_info.get("type") != "user_choice":
            return False
        if step_info.get("choices"):
            return False
        if not step_info.get("node_class"):
            return False
        return 1 < len(candidates) <= self.max_candidates

    def resolve(self, step_info: Dict[str, Any], candidates: List[Dict[str, str]]) -> Dict[str, Any]:
        """Return a validated LLM node-choice decision.

        The result is always safe to inspect.  ``selected`` is true only when
        the model selected an existing candidate with enough confidence.
        """
        if not self.should_resolve(step_info, candidates):
            return {"selected": False, "reason": "resolver_not_applicable"}

        candidate_by_id = {c["id"]: c for c in candidates if c.get("id")}
        candidate_by_name = {c["name"]: c for c in candidates if c.get("name")}
        payload = {
            "task": "Select the best existing Slicer scene node for a generated workflow parameter.",
            "question": step_info.get("question", ""),
            "workflow_step": step_info.get("step_id", ""),
            "parameter_name": step_info.get("parameter_name", ""),
            "node_class": step_info.get("node_class", ""),
            "binding": {
                "parameter_name": (step_info.get("binding") or {}).get("parameter_name", ""),
                "role": (step_info.get("binding") or {}).get("role", ""),
                "keywords": (step_info.get("binding") or {}).get("keywords", []),
            },
            "candidates": candidates,
        }
        messages = [
            {
                "role": "system",
                "content": (
                    "You resolve ambiguous 3D Slicer scene-node choices. "
                    "Select only from the provided candidates. "
                    "Return strict JSON only, with no markdown."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Choose the best candidate if the name clearly matches the requested role. "
                    "If no candidate is clearly best, set selected_node_id and selected_node_name to null "
                    "and confidence below 0.8.\n\n"
                    "Return JSON exactly with keys: selected_node_id, selected_node_name, "
                    "confidence, reason.\n\n"
                    f"Input:\n{json.dumps(payload, ensure_ascii=False, indent=2)}"
                ),
            },
        ]

        try:
            response = self._call_llm(messages)
            decision = self._extract_json(response)
        except Exception as exc:
            logger.warning("Node choice LLM resolver failed: %s", exc)
            return {"selected": False, "reason": f"resolver_failed: {exc}"}

        selected_id = decision.get("selected_node_id")
        selected_name = decision.get("selected_node_name")
        confidence = self._coerce_confidence(decision.get("confidence"))

        candidate = None
        if selected_id in candidate_by_id:
            candidate = candidate_by_id[selected_id]
        elif selected_name in candidate_by_name:
            candidate = candidate_by_name[selected_name]

        if not candidate:
            return {
                "selected": False,
                "confidence": confidence,
                "reason": "LLM selected a node outside the candidate list",
                "raw_decision": decision,
            }
        if confidence < self.confidence_threshold:
            return {
                "selected": False,
                "confidence": confidence,
                "reason": decision.get("reason", "LLM confidence below threshold"),
                "raw_decision": decision,
            }

        return {
            "selected": True,
            "choice_value": candidate["name"],
            "selected_node_id": candidate["id"],
            "selected_node_name": candidate["name"],
            "confidence": confidence,
            "reason": decision.get("reason", ""),
            "raw_decision": decision,
        }

    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """Run one direct non-tool, non-history-mutating LLM call."""
        payload = self.llm_client._buildPayload(
            messages,
            stream=False,
            tools=None,
            thinking=False,
            reasoning_effort="low",
        )
        request = self.llm_client._buildRequest(self.llm_client._getChatUrl(), payload)
        data = self.llm_client._fetchWithDiagnostics(request)
        if self.llm_client._isClaude():
            data = self.llm_client._normalizeClaudeResponse(data)
        message = data["choices"][0]["message"]
        return self.llm_client._coerceText(message.get("content", ""))

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        text = str(text or "").strip()
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if fenced:
            text = fenced.group(1)
        else:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                text = match.group(0)
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("resolver response is not a JSON object")
        return data

    @staticmethod
    def _coerce_confidence(value: Any) -> float:
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, confidence))
