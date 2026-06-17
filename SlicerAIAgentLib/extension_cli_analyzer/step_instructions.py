"""Generate clinically-informed, dual-version per-step user instructions.

Each workflow step gets a friendly action ``title``, a ``simple`` one-line
instruction (what to do now), and a ``detailed`` instruction explaining the
clinical purpose (why / what / target) and how. The LLM's clinical knowledge is
combined with the step's cookbook-derived description and operation context. The
output is written to ``step_instructions.json`` and is manually editable; steps
the user has edited (``edited: true``) are preserved across regeneration.
"""

from __future__ import annotations

import json
import logging
import textwrap
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_TITLE_MAX = 80
_SIMPLE_MAX = 200
_DETAILED_MAX = 600


class AnalyzerStepInstructionsMixin:
    """Mixed into ExtensionCLIAnalyzer; reuses its LLM + guidance-context helpers."""

    def generate_step_instructions(
        self,
        workflow_graph: Dict,
        metadata: Dict,
        scan_result: Dict,
        logic_analysis: Dict,
        cookbook_def: Optional[Any] = None,
        existing: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Return {"version":1, "steps": {step_id: {title, simple, detailed, edited}}}.

        ``existing`` is a previously-saved step_instructions.json; steps flagged
        ``edited`` there are kept verbatim and not regenerated.
        """
        steps = (workflow_graph or {}).get("steps", []) or []
        if not steps:
            return {"version": 1, "steps": {}}
        existing_steps = {}
        if isinstance(existing, dict):
            existing_steps = existing.get("steps", {}) or {}

        to_generate = [
            step for step in steps
            if step.get("step_id")
            and not existing_steps.get(step.get("step_id", ""), {}).get("edited")
        ]
        llm = self._llm_step_instructions(
            to_generate, metadata, scan_result, logic_analysis, cookbook_def
        )

        out: Dict[str, Dict] = {}
        for step in steps:
            step_id = step.get("step_id", "")
            if not step_id:
                continue
            prior = existing_steps.get(step_id, {}) or {}
            if prior.get("edited"):
                out[step_id] = {
                    "title": str(prior.get("title", "") or ""),
                    "simple": str(prior.get("simple", "") or ""),
                    "detailed": str(prior.get("detailed", "") or ""),
                    "edited": True,
                }
                continue
            candidate = llm.get(step_id) if isinstance(llm, dict) else None
            out[step_id] = self._validate_step_instruction(
                candidate, self._fallback_step_instruction(step)
            )
        return {"version": 1, "steps": out}

    @staticmethod
    def _load_existing_step_instructions(extension_name: str) -> Dict:
        """Load a previously-saved step_instructions.json (for edit preservation)."""
        try:
            import os
            from ..ExtensionCLILoader import get_cli_base_dir
            path = os.path.join(get_cli_base_dir(), extension_name, "step_instructions.json")
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            logger.debug("Loading existing step_instructions.json failed", exc_info=True)
        return {}

    # ------------------------------------------------------------------ internals

    def _fallback_step_instruction(self, step: Dict) -> Dict[str, str]:
        guidance = step.get("ui_guidance", {}) or {}
        description = str(step.get("description", "") or "").strip()
        title = str(guidance.get("title", "") or "").strip()
        if not title:
            try:
                title = self._clean_guidance_title(description) or "Workflow step"
            except Exception:
                title = description[:_TITLE_MAX] or "Workflow step"
        return {
            "title": title,
            "simple": str(guidance.get("instruction", "") or "").strip() or description,
            "detailed": description,
        }

    def _validate_step_instruction(self, candidate: Optional[Dict], fallback: Dict[str, str]) -> Dict:
        cand = candidate if isinstance(candidate, dict) else {}
        title = str(cand.get("title", "") or "").strip()[:_TITLE_MAX] or fallback["title"][:_TITLE_MAX]
        simple = str(cand.get("simple", "") or "").strip()[:_SIMPLE_MAX] or fallback["simple"][:_SIMPLE_MAX]
        detailed = str(cand.get("detailed", "") or "").strip()[:_DETAILED_MAX] or fallback["detailed"][:_DETAILED_MAX]
        return {"title": title, "simple": simple, "detailed": detailed, "edited": False}

    def _llm_step_instructions(
        self,
        steps: List[Dict],
        metadata: Dict,
        scan_result: Dict,
        logic_analysis: Dict,
        cookbook_def: Optional[Any],
    ) -> Dict[str, Dict]:
        """One batched LLM call producing {step_id: {title, simple, detailed}}. {} on failure."""
        if not getattr(self, "llm_client", None) or not steps:
            return {}
        contexts = [
            self._build_guidance_context(step, metadata, step.get("ui_guidance", {}) or {})
            for step in steps
        ]
        extension_name = (
            scan_result.get("module_name")
            or scan_result.get("extension_name")
            or scan_result.get("logic_class", {}).get("class_name", "")
            or logic_analysis.get("class_name", "")
            or "the extension"
        )
        domain_hint = ""
        if cookbook_def is not None:
            domain_hint = (
                str(getattr(cookbook_def, "title", "") or "")
                or str(getattr(cookbook_def, "intro", "") or "")
            )[:400]
        prompt = textwrap.dedent(f"""\
            You are a clinical expert writing user instructions for a 3D Slicer
            surgical-planning workflow, for a clinician operating the tool.

            Extension: {extension_name}
            Clinical context: {domain_hint or "(infer the clinical domain from the step descriptions and extension name)"}

            For EACH step, write three fields:
            - "title": a short, friendly action label (the clinical goal of this step).
            - "simple": ONE concise sentence telling the user what to do now.
            - "detailed": 1-3 sentences explaining the CLINICAL PURPOSE — why this
              step matters, what anatomical/surgical target it concerns, and how it
              affects later steps — then how to do it. Use correct clinical terms but
              stay understandable.

            Rules: do not mention code, methods, or node names. Do not tell the user
            to type "done" (the UI has a Done button). For repeated placement steps,
            describe exactly one item per Done click.

            Return ONLY JSON:
            {{
              "steps": [
                {{"step_id": "cb_step_1", "title": "...", "simple": "...", "detailed": "..."}}
              ]
            }}

            Step contexts:
            {json.dumps(contexts, indent=2)}
            """)
        try:
            response = self._call_llm(prompt, call_class="contract")
            parsed = self._parse_json_response(response)
        except Exception:
            logger.debug("Step instruction synthesis failed", exc_info=True)
            return {}
        if not isinstance(parsed, dict):
            return {}
        result: Dict[str, Dict] = {}
        for item in parsed.get("steps", []) or []:
            if not isinstance(item, dict):
                continue
            step_id = item.get("step_id", "")
            if step_id:
                result[step_id] = {
                    "title": item.get("title", ""),
                    "simple": item.get("simple", ""),
                    "detailed": item.get("detailed", ""),
                }
        return result
