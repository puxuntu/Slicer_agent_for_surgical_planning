"""Fast first-turn router: which guided planning workflow does this request mean?

Once a generated-CLI workflow is running, every step is dispatched, rendered and
executed by :mod:`SlicerAIAgentLib.WorkflowRuntime` -- the LLM is not in the
loop. So the *only* thing the model has to decide on the opening turn is **which
workflow to enter**. The full agent turn that used to make that decision carried
the whole coding manual, the dense-retrieval snippets and every extension's CLI
prompt fragment: ~140,000 characters of system prompt to emit a single tool call.

This router replaces that with one small, tool-free, temperature-0 call:

* system = ``Resources/Prompts/workflow_router_prompt.md`` + a compact catalog
  built from the workflow graphs (name, step count, seven step descriptions
  spread across the procedure -- the head names the inputs, the tail names the
  goal, which is what actually discriminates between nine similar procedures).
* user = the request, verbatim.
* out = ``{"extension": ..., "confidence": ..., "reason": ...}``.

Below the confidence threshold, or on any failure, the caller falls through to
the unchanged full agent turn -- so a request this router cannot place is still
answered exactly as before. The router only ever *skips* work; it never becomes
the only path to an answer.
"""

from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from . import PromptLibrary

logger = logging.getLogger(__name__)

#: Below this the request goes to the full coding agent instead. Chosen so a
#: genuinely ambiguous request pays the cost of the big turn rather than
#: silently entering the wrong 33-step procedure, which is far more expensive
#: for the user to unwind.
DEFAULT_CONFIDENCE_THRESHOLD = 0.6

#: Master switch for the fast first-turn path. Set False to send every opening
#: turn through the full agent again (the behaviour before this router existed),
#: e.g. to measure the routing turn's own cost against the baseline it replaced.
#: Under ``GUIDED_ONLY_MODE`` there is no full agent turn to fall back to, so
#: False there means every request is refused -- which the refusal dialog says
#: in those words rather than blaming the request.
ROUTER_ENABLED = True

#: The runtime supports the guided generated-CLI pipeline and nothing else.
#:
#: A request the router cannot place used to fall through to the full agent turn
#: (dense retrieval -> tool loop -> free-form code generation). That turn is the
#: opposite of what this system claims: its whole thesis is that a validated,
#: offline-analysed procedure is what drives the scene, so a silent fallback to
#: improvised code is both an unmeasured escape hatch in every evaluation and an
#: unreviewed code path in a surgical-planning context. With this True the router
#: decision is FINAL: a match enters the workflow, anything else is refused in a
#: dialog that says why, and no code is generated.
#:
#: Set False to restore the fall-through (the behaviour before this existed) --
#: a one-line revert, in the style of ``ROUTER_ENABLED`` above. Every guard reads
#: this flag at call time, so flipping it needs no other change.
#:
#: Deliberately NOT a ban on all generation: self-correction still repairs a
#: failing guided step, and the comparison baselines still run their own
#: producers. Both are scoped to a step of a workflow that already started.
GUIDED_ONLY_MODE = True

#: Check the scene for the procedure's required INPUT data before entering it.
#:
#: A guided workflow that starts without its inputs does not degrade gracefully:
#: the pick step opens with an empty picker, falls back to a free-text box, and
#: the name is then resolved against the scene and raises "Could not resolve the
#: selected <class> node". This moves that late failure to a dialog before any
#: session, run folder or manifest exists, and tells the surgeon what to load.
#:
#: What is required is derived from the generated package alone
#: (``SlicerAIAgentLib.WorkflowInputs``): a class a pick step demands is an INPUT
#: only when no earlier step creates one. Set False to enter every matched
#: workflow regardless of scene contents -- for evaluation runs that deliberately
#: start empty, and as the one-line revert if the derivation is ever wrong for an
#: installed extension. Read at call time.
PRECHECK_WORKFLOW_INPUTS = True

#: How many step descriptions per extension go into the catalog, and how much of
#: each. Seven at 90 characters keeps the whole catalog around 4.5 KB for nine
#: extensions -- roughly a tenth of the CLI prompt fragments it replaces.
CATALOG_STEP_SAMPLES = 7
CATALOG_STEP_CHARS = 90

_FALLBACK_ROUTER_PROMPT = (
    "Decide which guided 3D Slicer surgical-planning workflow the user's request "
    "means, from the list below. Return strict JSON only: "
    '{"extension": "<exact name or null>", "confidence": 0.0, "reason": "<clause>"}. '
    "Return null when the request is a general Slicer operation or is not covered.\n\n"
    "{{EXTENSION_CATALOG}}"
)


@dataclass(frozen=True)
class RouterDecision:
    """Outcome of one routing call."""

    extension: Optional[str] = None
    confidence: float = 0.0
    reason: str = ""
    seconds: float = 0.0
    tokens: int = 0
    #: USD for this routing call, priced by the LLM client's own table. Carried
    #: on the decision because under GUIDED_ONLY_MODE this is the ONLY model call
    #: a clean run makes, so it is the run's entire model cost.
    cost: float = 0.0
    prompt_chars: int = 0
    error: str = ""
    #: The workflow the router named but that was NOT entered -- because the
    #: name was unknown, or the confidence fell short. Under GUIDED_ONLY_MODE a
    #: near miss is the difference between "nothing here does this" and "say it
    #: the way the procedure says it", so the refusal dialog reports it instead
    #: of discarding it with the rest of the rejected decision.
    rejected_extension: str = ""

    @property
    def matched(self) -> bool:
        return bool(self.extension)


def _spread(items: List[str], count: int) -> List[str]:
    """Evenly-spaced sample of ``items``, always including the first and last.

    Sampling across the procedure rather than taking the head matters: several
    cookbooks open with the same Segment Editor thresholding boilerplate and are
    only told apart by what they build at the end.
    """
    if count <= 0 or not items:
        return []
    if len(items) <= count:
        return list(items)
    last = len(items) - 1
    positions = sorted({int(round(i * last / (count - 1))) for i in range(count)})
    return [items[i] for i in positions]


def build_extension_catalog() -> str:
    """Compact one-line-per-extension catalog of every validated generated CLI."""
    try:
        from SlicerAIAgentLib.ExtensionCLILoader import (
            get_validated_extensions,
            get_workflow_graph,
        )
    except Exception:
        logger.debug("Extension CLI loader unavailable for routing", exc_info=True)
        return ""

    lines = []
    for ext_name in sorted(get_validated_extensions().keys()):
        try:
            graph = get_workflow_graph(ext_name) or {}
        except Exception:
            logger.debug("Workflow graph unreadable for %s", ext_name, exc_info=True)
            continue
        steps = graph.get("steps") or []
        descriptions = [
            " ".join(str(step.get("description") or "").split())
            for step in steps
            if isinstance(step, dict)
        ]
        descriptions = [text for text in descriptions if text]
        if not descriptions:
            lines.append(f"- **{ext_name}**")
            continue
        sample = " | ".join(
            text[:CATALOG_STEP_CHARS] for text in _spread(descriptions, CATALOG_STEP_SAMPLES)
        )
        lines.append(
            f"- **{ext_name}** — {graph.get('step_count') or len(steps)} steps: {sample}"
        )
    return "\n".join(lines)


def available_extension_names() -> List[str]:
    try:
        from SlicerAIAgentLib.ExtensionCLILoader import get_validated_extensions
        return sorted(get_validated_extensions().keys())
    except Exception:
        return []


def display_name(extension_name: str) -> str:
    """``BoneReconstructionPlanner`` -> ``Bone Reconstruction Planner``.

    Shares the runtime's own spelling so a workflow is named identically in the
    refusal dialog and in the panel header the user sees once it starts.
    """
    try:
        from SlicerAIAgentLib.WorkflowRuntime import WorkflowRuntime
        return WorkflowRuntime._display_name(extension_name)
    except Exception:
        return str(extension_name or "Workflow")


def describe_available_workflows() -> List[str]:
    """One human-readable line per installed workflow, for the refusal dialog.

    Under ``GUIDED_ONLY_MODE`` a refusal is the end of the request, so the user
    has to be able to see what the runtime *can* do without leaving the dialog.
    """
    lines = []
    for name in available_extension_names():
        try:
            from SlicerAIAgentLib.ExtensionCLILoader import get_workflow_graph
            graph = get_workflow_graph(name) or {}
            count = graph.get("step_count") or len(graph.get("steps") or [])
        except Exception:
            count = 0
        label = display_name(name)
        lines.append(f"• {label} ({count} steps)" if count else f"• {label}")
    return lines


class WorkflowRouter:
    """One tool-free LLM call that picks a generated CLI workflow, or none."""

    def __init__(self, llm_client, confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD):
        self.llm_client = llm_client
        self.confidence_threshold = float(confidence_threshold)
        # The last call, kept so the caller can flush it to disk AFTER the run
        # folder exists -- the folder is named after the decision, so it cannot
        # exist while the decision is being made.
        self.last_messages: List[Dict[str, str]] = []
        self.last_reply: str = ""
        self.last_error: str = ""

    def is_available(self) -> bool:
        """True when routing is possible at all (client, key, and workflows)."""
        return not self.unavailable_reason()

    def unavailable_reason(self) -> str:
        """Why routing is impossible, or "" when it is possible.

        Two very different failures used to collapse into one False: an install
        with no API key, and an install with no generated CLIs. When the router
        was only an optimisation that did not matter -- the full turn answered
        either way. Under ``GUIDED_ONLY_MODE`` it is the whole product, and the
        two need opposite remedies (configure a key / generate a CLI), so the
        cause is reported rather than inferred.
        """
        if not self.llm_client:
            return "no_client"
        if not getattr(self.llm_client, "api_key", None):
            return "no_api_key"
        if not available_extension_names():
            return "no_workflows"
        return ""

    def build_messages(self, prompt: str) -> List[Dict[str, str]]:
        catalog = build_extension_catalog()
        system = PromptLibrary.render(
            PromptLibrary.WORKFLOW_ROUTER_PROMPT,
            fallback=_FALLBACK_ROUTER_PROMPT,
            extension_catalog=catalog,
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": str(prompt or "").strip()},
        ]

    def resolve(self, prompt: str, log_dir: str = "") -> RouterDecision:
        """Route ``prompt``; never raises.

        ``log_dir`` (optional) receives a ``00_router/`` folder holding the exact
        messages sent and the raw reply. This is the ONLY model call a guided
        run makes -- the steps after it are deterministic template dispatch --
        so without it the run's single piece of model evidence is unrecorded.
        """
        unavailable = self.unavailable_reason()
        if unavailable:
            return RouterDecision(error=f"router unavailable: {unavailable}")

        started = time.time()
        messages = self.build_messages(prompt)
        self.last_messages, self.last_reply, self.last_error = messages, "", ""
        prompt_chars = sum(len(message.get("content", "")) for message in messages)
        try:
            text, tokens, cost = self._call(messages)
            self.last_reply = text
            self.write_artifacts(log_dir)
            decision = self._extract_json(text)
        except Exception as exc:
            logger.warning("Workflow router call failed: %s", exc)
            self.last_error = str(exc)
            self.write_artifacts(log_dir)
            return RouterDecision(
                seconds=round(time.time() - started, 3),
                prompt_chars=prompt_chars,
                error=str(exc),
            )

        confidence = self._coerce_confidence(decision.get("confidence"))
        reason = str(decision.get("reason") or "")
        elapsed = round(time.time() - started, 3)

        name = decision.get("extension")
        name = "" if name is None else str(name).strip()
        # Reject anything that is not verbatim one of the loaded extensions:
        # a hallucinated name must fall through to the full agent, not raise
        # deep inside start_for_extension.
        if name.lower() in ("", "null", "none"):
            return RouterDecision(
                confidence=confidence, reason=reason, seconds=elapsed,
                tokens=tokens, cost=cost, prompt_chars=prompt_chars,
            )
        if name not in available_extension_names():
            return RouterDecision(
                confidence=confidence, seconds=elapsed, tokens=tokens,
                cost=cost, prompt_chars=prompt_chars, rejected_extension=name,
                reason=f"router named an unknown workflow '{name}'",
            )
        if confidence < self.confidence_threshold:
            return RouterDecision(
                confidence=confidence, seconds=elapsed, tokens=tokens,
                cost=cost, prompt_chars=prompt_chars, rejected_extension=name,
                reason=reason or "router confidence below threshold",
            )
        return RouterDecision(
            extension=name, confidence=confidence, reason=reason,
            seconds=elapsed, tokens=tokens, cost=cost, prompt_chars=prompt_chars,
        )

    def write_artifacts(self, log_dir: str) -> None:
        """Persist the last routing call into ``<run>/00_router/``. Never raises.

        Callable after the fact, because the run folder is named after the
        decision and so cannot exist while the decision is being made.
        """
        if not log_dir or not self.last_messages:
            return
        messages, reply, error = self.last_messages, self.last_reply, self.last_error
        try:
            import os
            from . import RunLog
            out = RunLog.ensure_dir(os.path.join(log_dir, "00_router"))
            body = []
            for i, message in enumerate(messages or []):
                body.append("=" * 60)
                body.append(f"MESSAGE {i + 1} | role: {message.get('role', 'unknown')}")
                body.append("=" * 60)
                body.append(f"{message.get('content', '')}\n")
            RunLog.write_text(os.path.join(out, "messages_sent.txt"), "\n".join(body))
            RunLog.write_text(os.path.join(out, "reply.txt"), reply or error or "")
            RunLog.write_json(os.path.join(out, "call.json"), {
                "thinking": False,
                "reasoning_effort": "low",
                "temperature": 0.0,
                "tools": None,
                # Recorded so "why is there no thinking.txt for this run?" is
                # answerable from the artifacts alone: the routing call is a
                # 9-way classification against a fixed JSON schema, and thinking
                # would add seconds to the one turn this path exists to speed up.
                "note": (
                    "Routing is a deliberate non-thinking call, so it produces no "
                    "reasoning content. The workflow steps after it are "
                    "deterministic template dispatch and call no model at all."
                ),
                "prompt_chars": sum(
                    len(m.get("content", "") or "") for m in (messages or [])
                ),
                "error": error or None,
            })
        except Exception:
            logger.debug("Router artifact write failed", exc_info=True)

    # ------------------------------------------------------------------ internals
    def _call(self, messages: List[Dict[str, str]]):
        """One non-streaming, tool-free, thinking-off completion.

        Uses the same low-level request path as WorkflowIntentResolver so the
        router inherits provider handling (Anthropic-native conversion, retries,
        diagnostics) without going through chat()/chatWithTools() -- those write
        conversation_history and bump turn_number, which a routing call must not.
        """
        client = self.llm_client
        payload = client._buildPayload(
            messages,
            stream=False,
            tools=None,
            thinking=False,
            reasoning_effort="low",
            options={"temperature": 0.0},
        )
        request = client._buildRequest(client._getChatUrl(), payload)
        data = client._fetchWithDiagnostics(request)
        if client._isClaude():
            data = client._normalizeClaudeResponse(data)
        usage = data.get("usage") or {}
        tokens = int(usage.get("total_tokens") or 0)
        # Price it with the CLIENT's own pricing table rather than a local copy,
        # so the routing call is costed exactly like every other call to the same
        # model. Without this the router reported tokens but never a price, and
        # since a clean guided run makes no other model call, the run's total
        # cost was structurally $0.0000 -- understating precisely the number this
        # path exists to demonstrate.
        try:
            cost = float(client._calculateCost(usage))
        except Exception:
            logger.debug("Router cost calculation failed", exc_info=True)
            cost = 0.0
        text = client._coerceText(data["choices"][0]["message"].get("content", ""))
        return text, tokens, cost

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        match = re.search(r"\{.*\}", str(text or ""), re.DOTALL)
        data = json.loads(match.group(0) if match else str(text or ""))
        if not isinstance(data, dict):
            raise ValueError("router response is not a JSON object")
        return data

    @staticmethod
    def _coerce_confidence(value: Any) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0
