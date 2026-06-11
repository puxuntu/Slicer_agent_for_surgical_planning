from .common import *


_INTENT_TEXT_REQUIREMENTS = {
    "slice_intersection_visibility": {
        "required_any": (r"\bintersection(s)?\b", r"\bintersecting\b"),
        "conflicts": (r"\bslice\s+visibility\s+in\s+3d\b", r"\bslice\s+visible\s+in\s+3d\b"),
        "explanation": "slice-intersection intent requires intersection/intersecting text evidence",
    },
    "layout_activate": {
        "required_any": (r"\blayout\b",),
        "conflicts": (),
        "explanation": "layout activation intent requires layout text evidence",
    },
    "view_display_scope": {
        "required_any": (r"\bview\b", r"\bdisplay\b", r"\bvisible\b", r"\bvisibility\b"),
        "conflicts": (),
        "explanation": "display-scope intent requires view/display/visibility text evidence",
    },
}


class AnalyzerContractAuditMixin:
    """Independent checks that generated contracts are faithful to source facts.

    This mixin deliberately validates the contract against raw step text and
    source-derived metadata instead of using generated operation categories as
    self-confirming evidence.
    """

    @staticmethod
    def _contract_step_text(step: Dict) -> str:
        parts = [_text_or_empty(step.get("description"))]
        for op in step.get("operations", []) or []:
            if isinstance(op, dict):
                parts.append(_text_or_empty(op.get("description")))
        return " ".join(p for p in parts if p)

    @staticmethod
    def _contract_step_intents(step: Dict) -> List[str]:
        intents = []
        model = step.get("operation_model") or {}
        intents.extend(_text_list(model.get("operation_intents", [])))
        for op in step.get("operations", []) or []:
            if isinstance(op, dict) and op.get("intent"):
                intents.append(_text_or_empty(op.get("intent")))
        return sorted(set(intent for intent in intents if intent))

    @staticmethod
    def _text_matches_any(text: str, patterns: Tuple[str, ...]) -> bool:
        return any(_re.search(pattern, text, _re.IGNORECASE) for pattern in patterns)

    def _audit_contract_intent_fidelity(self, step: Dict) -> List[Dict]:
        findings = []
        text = self._contract_step_text(step)
        lowered = text.lower()
        step_id = _text_or_empty(step.get("step_id"))
        for intent in self._contract_step_intents(step):
            requirements = _INTENT_TEXT_REQUIREMENTS.get(intent)
            if not requirements:
                continue
            required_any = requirements.get("required_any", ())
            conflicts = requirements.get("conflicts", ())
            has_support = self._text_matches_any(lowered, required_any)
            has_conflict = bool(conflicts and self._text_matches_any(lowered, conflicts))
            if not has_support or has_conflict:
                findings.append({
                    "step_id": step_id,
                    "verdict": "fail",
                    "issue_class": "intent_mismatch",
                    "affected_artifact": "workflow_contract",
                    "recommended_route": "rebuild_contract",
                    "message": (
                        f"ContractFidelity: {step_id} intent '{intent}' is not "
                        f"supported by cookbook/source step text; "
                        f"{requirements.get('explanation', 'missing required text evidence')}"
                    ),
                    "evidence": [text[:300]],
                })
        return findings

    def _audit_workflow_state_graph(
        self,
        workflow_contract: Dict,
        workflow_graph: Optional[Dict] = None,
    ) -> Dict:
        """Build and validate a lightweight producer/consumer state graph."""
        metadata = self._workflow_metadata if isinstance(self._workflow_metadata, dict) else {}
        dependencies = metadata.get("parameter_method_dependencies", {}) or {}
        method_effects = metadata.get("method_parameter_effects", {}) or {}
        defaults = metadata.get("parameter_defaults", {}) or {}
        choice_bindings = metadata.get("choice_bindings", {}) or {}
        interaction_bindings = metadata.get("interaction_bindings", {}) or {}

        produced_by_role: Dict[str, List[Dict]] = {}
        for step_id, binding in choice_bindings.items():
            if isinstance(binding, dict) and binding.get("parameter_name"):
                produced_by_role.setdefault(binding["parameter_name"], []).append({
                    "step_id": step_id,
                    "source": "choice_binding",
                })
        for step_id, binding in interaction_bindings.items():
            if isinstance(binding, dict) and binding.get("parameter_name"):
                produced_by_role.setdefault(binding["parameter_name"], []).append({
                    "step_id": step_id,
                    "source": "interaction_binding",
                })

        graph = {
            "schema_version": 1,
            "consumers": [],
            "producers": produced_by_role,
            "parameter_consumers": {},
            "parameter_producers": produced_by_role,
            "step_order": {},
            "errors": [],
            "warnings": [],
        }
        step_order = {
            step.get("step_id", ""): index
            for index, step in enumerate((workflow_contract or {}).get("steps", []) or [])
        }
        graph["step_order"] = dict(step_order)

        def _methods_for_step(step: Dict) -> set:
            methods = set()
            if step.get("method_name"):
                methods.add(_text_or_empty(step.get("method_name")))
            for op in step.get("operations", []) or []:
                if isinstance(op, dict) and op.get("extension_method_hint"):
                    methods.add(_text_or_empty(op.get("extension_method_hint")))
            for so in step.get("sub_operations", []) or []:
                if isinstance(so, dict) and so.get("extension_method_hint"):
                    methods.add(_text_or_empty(so.get("extension_method_hint")))
            return {method for method in methods if method}

        steps = (workflow_contract or {}).get("steps", []) or []
        for step in steps:
            step_id = _text_or_empty(step.get("step_id"))
            for method in sorted(_methods_for_step(step)):
                effects = method_effects.get(method, {}) or {}
                for role in effects.get("writes", []) or []:
                    produced_by_role.setdefault(role, []).append({
                        "step_id": step_id,
                        "method": method,
                        "source": "method_parameter_effect",
                    })

        for step in steps:
            step_id = _text_or_empty(step.get("step_id"))
            methods = _methods_for_step(step)
            for method in sorted(methods):
                dep = dependencies.get(method, {}) or {}
                for role in dep.get("parameter_roles", []) or []:
                    effects = method_effects.get(method, {}) or {}
                    if role in (effects.get("writes", []) or []):
                        continue
                    role_producers = produced_by_role.get(role, [])
                    consumer = {
                        "step_id": step_id,
                        "method": method,
                        "role": role,
                        "producers": role_producers,
                        "default": defaults.get(role, {}),
                    }
                    graph["consumers"].append(consumer)
                    graph["parameter_consumers"].setdefault(role, []).append(consumer)
                    default_info = defaults.get(role, {}) or {}
                    producer_steps = [
                        item.get("step_id", "") if isinstance(item, dict) else str(item)
                        for item in role_producers
                    ]
                    has_prior_producer = any(
                        step_order.get(pid, 10**9) < step_order.get(step_id, 10**9)
                        for pid in producer_steps
                    )
                    if has_prior_producer:
                        continue
                    if default_info and default_info.get("confidence") != "low":
                        continue
                    if default_info.get("confidence") == "low":
                        graph["errors"].append(
                            f"WorkflowState: {step_id} consumes '{role}' for logic.{method}() "
                            "using only a low-confidence default; template generation must "
                            "bind it, derive a source-backed value, or raise a required-input error"
                        )
                    elif not default_info:
                        graph["errors"].append(
                            f"WorkflowState: {step_id} consumes '{role}' for logic.{method}() "
                            "without a prior producer or source-derived default"
                        )
        return graph

    def _audit_workflow_contract(
        self,
        workflow_contract: Dict,
        workflow_graph: Optional[Dict] = None,
        logic_analysis: Optional[Dict] = None,
    ) -> Dict:
        findings = []
        warnings = []
        for step in (workflow_contract or {}).get("steps", []) or []:
            findings.extend(self._audit_contract_intent_fidelity(step))

        state_graph = self._audit_workflow_state_graph(workflow_contract, workflow_graph)
        warnings.extend(state_graph.get("warnings", []))
        errors = [finding["message"] for finding in findings if finding.get("verdict") == "fail"]
        errors.extend(state_graph.get("errors", []))
        report = {
            "schema_version": 1,
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
            "findings": findings,
            "workflow_state_graph": state_graph,
        }
        if isinstance(self._workflow_metadata, dict):
            self._workflow_metadata["contract_audit"] = report
            state = self._workflow_metadata.setdefault("validation_state", {})
            state["contract_audit_valid"] = report["valid"]
            state["workflow_state_valid"] = not bool(state_graph.get("errors"))
        return report

    def _enforce_workflow_contract_audit(
        self,
        workflow_contract: Dict,
        workflow_graph: Optional[Dict] = None,
        logic_analysis: Optional[Dict] = None,
    ) -> Dict:
        self._phase_progress(
            "audit_contract",
            "Auditing workflow contract against cookbook/source evidence...",
            "Audit Workflow Contract",
        )
        report = self._audit_workflow_contract(
            workflow_contract,
            workflow_graph=workflow_graph,
            logic_analysis=logic_analysis,
        )
        if report.get("valid"):
            self._phase_progress(
                "audit_contract",
                "PASS",
                "Audit Workflow Contract",
            )
            return report
        self._phase_progress(
            "audit_contract",
            f"FAIL: {report.get('errors', [])}",
            "Audit Workflow Contract",
        )
        raise RuntimeError(
            "Workflow contract audit failed: " + "; ".join(report.get("errors", []))
        )

    def _finalize_package_validation_state(
        self,
        manifest: Dict,
        validation_result: Dict,
    ) -> Dict:
        metadata = self._workflow_metadata if isinstance(self._workflow_metadata, dict) else {}
        state = metadata.setdefault("validation_state", {})
        valid = bool((validation_result or {}).get("valid"))
        coverage = (validation_result or {}).get("api_proof_coverage") or metadata.get(
            "api_proof_coverage", {}
        ) or {}
        proof_valid = bool(
            coverage.get("inventory_complete")
            and not coverage.get("invalid_calls")
            and not coverage.get("blocking_unproven_calls")
        )
        valid = valid and proof_valid
        state["overall_valid"] = valid
        state["api_proof_valid"] = proof_valid
        audit = metadata.get("contract_audit")
        if isinstance(audit, dict):
            state["contract_audit_valid"] = bool(audit.get("valid"))
        repair = metadata.setdefault("verify_repair", {})
        if valid:
            if metadata.get("revision_validation_status") == "passed":
                repair["status"] = "passed_after_revision"
                repair["used_outer_revision"] = True
            elif repair.get("attempts"):
                repair["status"] = "passed_after_repair"
            else:
                repair["status"] = "passed"
            manifest["status"] = (
                "validated_with_warnings"
                if coverage.get("warning_unproven_reads")
                else "validated"
            )
        else:
            repair["status"] = "failed"
            manifest["status"] = "validation_failed"
        manifest["validation_state"] = state
        manifest["api_proof_coverage"] = coverage
        return manifest
