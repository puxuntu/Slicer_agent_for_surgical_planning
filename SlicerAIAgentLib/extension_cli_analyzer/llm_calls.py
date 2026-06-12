from .common import *

# Per-call-class sampling configuration.
#
# Fact-extraction classes (analysis/contract/critic) run at low temperature so
# repeated pipeline runs derive the same facts from the same source. Code- and
# repair-producing classes keep moderate temperature so a re-ask after a
# rejected response can escape a bad sample instead of reproducing it.
#
# These are sampling *requests*: the LLM client applies them only where the
# provider supports them (see LLMClient._applySamplingOptions).
_CALL_CLASS_CONFIG = {
    "analysis": {"temperature": 0.1},
    "contract": {"temperature": 0.0},
    "critic": {"temperature": 0.0},
    "grounding": {"temperature": 0.2},
    "generation": {"temperature": 0.4},
    "repair": {"temperature": 0.4},
}


class AnalyzerLLMCallsMixin:
    """Single funnel for structured (JSON-validated) LLM calls.

    Every pipeline stage that expects machine-readable LLM output should go
    through _call_llm_structured rather than calling _call_llm and parsing by
    hand. The wrapper owns: sampling options per call class, JSON parsing,
    validation, bounded re-ask with error feedback, and debug logging of every
    attempt. This generalizes the retry-with-feedback loops that previously
    lived inline in stage 4 decomposition and cross-stage mapping.
    """

    _STRUCTURED_CALL_MAX_ATTEMPTS = 3

    @staticmethod
    def _llm_sampling_options(call_class: Optional[str]) -> Optional[Dict]:
        if not call_class:
            return None
        return dict(_CALL_CLASS_CONFIG.get(call_class, {})) or None

    def _call_llm_structured(
        self,
        prompt,
        validator: Optional[Callable] = None,
        call_class: str = "analysis",
        max_attempts: Optional[int] = None,
        expect_json: bool = True,
        failure_label: str = "",
    ):
        """Call the LLM and return validated output, re-asking on rejection.

        Args:
            prompt: Either the prompt string, or a builder
                ``callable(prior_result, errors) -> str`` invoked each attempt
                with the previous (possibly invalid) result and the validation
                errors it produced. Use a builder when the stage already has
                its own feedback formatting; plain strings get generic
                error-feedback appended automatically on re-asks.
            validator: ``callable(candidate, raw_text) -> (result, errors)``.
                ``candidate`` is the parsed JSON when expect_json, else the raw
                text. Empty/None ``errors`` accepts ``result`` as the return
                value. None accepts any parsed/raw response.
            call_class: Sampling class (see _CALL_CLASS_CONFIG).
            max_attempts: Bounded re-asks; defaults to
                _STRUCTURED_CALL_MAX_ATTEMPTS.
            expect_json: Parse the response as JSON before validation.
            failure_label: Human-readable stage label for the terminal error.

        Raises:
            RuntimeError: when no attempt produces a validated result.
        """
        attempts = max_attempts or self._STRUCTURED_CALL_MAX_ATTEMPTS
        errors: List[str] = []
        prior_result = None
        prior_raw = ""

        for attempt in range(attempts):
            if callable(prompt):
                attempt_prompt = prompt(prior_result, errors)
            else:
                attempt_prompt = prompt
                if errors:
                    attempt_prompt = (
                        prompt
                        + "\n\nYour previous response was rejected. Validation errors:\n"
                        + "\n".join(f"- {e}" for e in errors[:20])
                        + "\n\nPrevious response (for reference):\n"
                        + prior_raw[:8000]
                        + "\n\nReturn a corrected response that fixes every error above."
                    )

            raw = self._call_llm(
                attempt_prompt,
                call_class=call_class,
                attempt=attempt,
                validation_errors=errors,
            )

            candidate = raw
            if expect_json:
                try:
                    candidate = self._parse_json_response(raw)
                except Exception as exc:
                    candidate = None
                    errors = [f"Response was not valid JSON: {exc}"]
                if candidate is None:
                    errors = errors or ["Response did not contain a valid JSON value"]
                    prior_result, prior_raw = None, raw
                    self._log_structured_rejection(call_class, failure_label, attempt, errors)
                    continue

            if validator is None:
                return candidate

            try:
                result, errors = validator(candidate, raw)
                errors = list(errors or [])
            except Exception as exc:
                result, errors = None, [f"Validator raised: {exc}"]
            if not errors:
                return result

            # Feed the validator's normalized result (when available) back to
            # prompt builders so re-asks can reference it; fall back to the
            # parsed candidate.
            prior_result = result if result is not None else candidate
            prior_raw = raw
            self._log_structured_rejection(call_class, failure_label, attempt, errors)

        raise RuntimeError(
            f"Structured LLM call ({failure_label or call_class}) failed after "
            f"{attempts} attempts: " + "; ".join(errors[:20])
        )

    @staticmethod
    def _log_structured_rejection(call_class, failure_label, attempt, errors):
        logger.warning(
            "[%s] structured LLM call attempt %d rejected: %s",
            failure_label or call_class,
            attempt + 1,
            "; ".join(errors[:10]),
        )
