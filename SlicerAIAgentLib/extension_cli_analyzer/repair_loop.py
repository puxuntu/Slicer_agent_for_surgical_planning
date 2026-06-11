from .common import *
import hashlib

from .api_proof import ApiEvidenceAgent, RepairCoordinator

_SEMANTIC_REPAIR_RECIPES = {
    "slice_intersection_visibility": {
        "recipe_id": "slice_intersection_visibility",
        "knowledge_level": "behavioral_contract",
        "behavior_requirements": [
            "The requested slice intersections become visible.",
            "Any requested slice-intersection interaction modes become enabled.",
            "Changed slice-view state is refreshed when the selected API requires it.",
        ],
        "invalid_substitutions": [
            "crosshair-only visibility changes",
            "module switching used as the operation implementation",
        ],
        "retrieval_queries": [
            "SetIntersectingSlicesEnabled",
            "SetSliceIntersectionInteractionEnabled",
            "SetSliceIntersectionInteractionModeFlags",
        ],
        "retrieval_query_provenance": "generic_slicer_search_hint",
        "evidence_policy": "Select any source-backed implementation that satisfies the behavior validator.",
    },
    "layout_activate": {
        "recipe_id": "layout_activate",
        "knowledge_level": "behavioral_contract",
        "behavior_requirements": ["The requested layout becomes the active layout."],
        "invalid_substitutions": ["registering a layout without activating it"],
        "retrieval_queries": ["layoutManager setLayout activate layout"],
        "retrieval_query_provenance": "generic_slicer_search_hint",
        "evidence_policy": "Accept direct Slicer APIs or extension helpers proven to activate the layout.",
    },
    "view_display_scope": {
        "recipe_id": "view_display_scope",
        "knowledge_level": "behavioral_contract",
        "behavior_requirements": [
            "The displayable is visible in every requested target view.",
            "Slice-view targets receive the display-class-specific slice/2D visibility state.",
        ],
        "invalid_substitutions": ["view filtering without enabling required slice visibility"],
        "retrieval_queries": ["view display scope slice visibility"],
        "retrieval_query_provenance": "generic_slicer_search_hint",
        "evidence_policy": "Select APIs appropriate to the discovered display-node class.",
    },
}


class AnalyzerRepairLoopMixin:
    _VERIFY_REPAIR_MAX_ATTEMPTS = 3
    _FORMAT_RETRY_MAX_ATTEMPTS = 2

    @staticmethod
    def _classify_validation_issue(error: str) -> str:
        text = error or ""
        lowered = text.lower()
        if "contractfidelity" in lowered or "workflow contract audit failed" in lowered:
            return "ContractFidelity"
        if "workflowstate" in lowered:
            return "WorkflowStateError"
        if "unproven dynamic api receiver" in lowered:
            return "UnprovenReceiver"
        if "unresolved live api probe failure" in lowered or "api call does not exist" in lowered:
            return "InvalidSlicerAPI"
        if "callablereferencemisuse" in lowered or "without calling it" in lowered:
            return "CallableReferenceMisuse"
        if "badinstructiontext" in lowered or "invalid user-facing instruction" in lowered:
            return "BadInstructionText"
        if "low-confidence" in lowered and "default" in lowered:
            return "LowConfidenceFallback"
        if (
            "slice intersection visibility step" in lowered
            or "slice-intersection behavior" in lowered
            or "layout activation step" in lowered
            or "display step targets a slice view" in lowered
            or "markups display step targets a slice view" in lowered
        ):
            return "SlicerSemanticError"
        if "does not call slicer.util.selectmodule" in lowered:
            return "ModuleEnterPreconditionMissing"
        if "required template is a stub" in lowered or "only pass/comments/prints" in lowered:
            return "StubTemplate"
        if "node class" in lowered and "metadata expects" in lowered:
            return "NodeClassMismatch"
        if "unresolved placeholders" in lowered or "placeholder" in lowered:
            return "UnresolvedPlaceholder"
        if "syntax" in lowered:
            return "SyntaxError"
        if "unknown_op" in lowered or "could not be proven" in lowered:
            return "UnknownOperation"
        if "sub-operation" in lowered and "no code" in lowered:
            return "MissingOperationFootprint"
        if "operation_model" in lowered or "contract" in lowered:
            return "ContractConflict"
        return "ValidationError"

    @staticmethod
    def _issue_class_for_issue(issue_type: str) -> str:
        if issue_type in {"ContractFidelity", "ContractConflict", "UnknownOperation"}:
            return "contract"
        if issue_type in {"WorkflowStateError", "LowConfidenceFallback", "UnresolvedPlaceholder"}:
            return "dataflow"
        if issue_type in {"InvalidSlicerAPI", "UnprovenReceiver"}:
            return "runtime_api"
        if issue_type in {"SlicerSemanticError", "MissingOperationFootprint"}:
            return "grounding"
        if issue_type in {
            "CallableReferenceMisuse", "BadInstructionText",
            "ModuleEnterPreconditionMissing", "SyntaxError", "StubTemplate",
            "NodeClassMismatch",
        }:
            return "template"
        return "template"

    @staticmethod
    def _repair_route_for_issue(issue_class: str, issue_type: str, strategy: str) -> str:
        if issue_class == "contract":
            return "rebuild_contract"
        if issue_class == "dataflow":
            return "rebuild_dataflow"
        if issue_class == "runtime_api":
            if issue_type == "UnprovenReceiver":
                return "gather_receiver_method_behavior_evidence"
            return "resolve_receiver_and_reground"
        if issue_class == "grounding":
            return "reground_api"
        if strategy == "targeted_template_repair":
            return "repair_template"
        return strategy or "repair_template"

    @classmethod
    def _validation_issues_from_result(
        cls,
        validation_result: Dict,
        generators: Optional[List[Dict]] = None,
        workflow_contract: Optional[Dict] = None,
    ) -> List[Dict]:
        template_context = {}
        for gen in generators or []:
            for key in ("template_file", "pre_template_file", "post_template_file"):
                if gen.get(key):
                    template_context[gen[key]] = gen
        contract_steps = {
            step.get("step_id", ""): step
            for step in (workflow_contract or {}).get("steps", [])
            if isinstance(step, dict)
        }
        issues = []
        for structured in validation_result.get("validation_issues", []) or []:
            if not isinstance(structured, dict):
                continue
            if structured.get("severity") == "warning" or structured.get("blocking") is False:
                continue
            issue_type = structured.get("issue_type", "ValidationError")
            if issue_type == "InvalidApiCall":
                classified = "InvalidSlicerAPI"
            elif issue_type == "UnprovenApiCall":
                classified = "UnprovenReceiver"
            else:
                classified = issue_type
            template = structured.get("template", "")
            step_match = _re.search(r"(cb_step_\d+)", template)
            gen = template_context.get(template, {})
            issue_class = cls._issue_class_for_issue(classified)
            strategy = cls._repair_strategy_for_issue(classified, gen)
            issue = {
                **structured,
                "issue_id": structured.get("issue_id") or f"issue_{len(issues) + 1}",
                "issue_type": classified,
                "issue_class": issue_class,
                "template_key": template,
                "step_id": step_match.group(1) if step_match else "",
                "root_cause": structured.get("diagnosis", classified),
                "repair_strategy": strategy,
                "repair_route": cls._repair_route_for_issue(issue_class, classified, strategy),
                "affected_artifacts": [issue_class],
                "message": structured.get("diagnosis", classified),
                "raw": structured,
            }
            issue["evidence_diagnosis"] = ApiEvidenceAgent.diagnose(structured)
            issues.append(issue)
        if validation_result.get("validation_issues"):
            return issues
        for index, error in enumerate(validation_result.get("errors", []) or []):
            if any(marker in str(error) for marker in (
                "UnprovenApiCall:", "InvalidApiCall:", "IncompleteCallInventory:",
            )):
                continue
            template = ""
            message = error
            if isinstance(error, str) and ": " in error:
                prefix, rest = error.split(": ", 1)
                if prefix.endswith((".py.tpl", ".py")) or prefix.startswith("templates/"):
                    template = prefix
                    message = rest
            step_match = _re.search(r"(cb_step_\d+)", template)
            step_id = step_match.group(1) if step_match else ""
            gen = template_context.get(template, {})
            operation_model = gen.get("operation_model") or {}
            operation_intents = list(operation_model.get("operation_intents") or [])
            if not operation_intents:
                for sub_op in gen.get("sub_operations", []) or []:
                    operation_intents.extend(_text_list(sub_op.get("operation_intents", [])))
                    if sub_op.get("operation_intent"):
                        operation_intents.append(sub_op["operation_intent"])
            issue_type = cls._classify_validation_issue(str(error))
            recipe_id = cls._semantic_recipe_for_issue(
                issue_type, operation_intents, str(error)
            )
            strategy = cls._repair_strategy_for_issue(issue_type, gen)
            issue_class = cls._issue_class_for_issue(issue_type)
            repair_route = cls._repair_route_for_issue(issue_class, issue_type, strategy)
            issues.append({
                "issue_id": f"issue_{index + 1}",
                "issue_type": issue_type,
                "issue_class": issue_class,
                "severity": "error",
                "template_key": template,
                "step_id": step_id,
                "operation_type": gen.get("operation_type", ""),
                "operation_intents": sorted(set(operation_intents)),
                "slicer_op_category": next((
                    so.get("slicer_op_category", "")
                    for so in gen.get("sub_operations", []) or []
                    if so.get("op_type") == "slicer_op"
                ), ""),
                "root_cause": issue_type,
                "repair_strategy": strategy,
                "repair_route": repair_route,
                "affected_artifacts": [issue_class],
                "semantic_recipe_id": recipe_id,
                "semantic_recipe": _SEMANTIC_REPAIR_RECIPES.get(recipe_id, {}),
                "evidence_requirements": {
                    "retrieval_queries": _SEMANTIC_REPAIR_RECIPES.get(recipe_id, {}).get(
                        "retrieval_queries", []
                    ),
                    "behavior_requirements": _SEMANTIC_REPAIR_RECIPES.get(recipe_id, {}).get(
                        "behavior_requirements", []
                    ),
                },
                "contract_step": contract_steps.get(step_id, {}),
                "message": message,
                "raw": str(error),
            })
        return issues

    @staticmethod
    def _semantic_recipe_for_issue(
        issue_type: str, operation_intents: List[str], error: str,
    ) -> str:
        intents = set(operation_intents or [])
        lowered = (error or "").lower()
        for recipe_id in _SEMANTIC_REPAIR_RECIPES:
            if recipe_id in intents:
                return recipe_id
        if "slice intersection" in lowered:
            return "slice_intersection_visibility"
        if "layout activation" in lowered:
            return "layout_activate"
        if "slice view" in lowered and "visibility" in lowered:
            return "view_display_scope"
        return ""

    @staticmethod
    def _repair_strategy_for_issue(issue_type: str, gen: Dict) -> str:
        slicer_sub_ops = [
            so for so in gen.get("sub_operations", []) or []
            if so.get("op_type") == "slicer_op"
        ]
        operation_type = gen.get("operation_type") or gen.get("op_type")
        pure_slicer_op = operation_type == "slicer_op" or (
            slicer_sub_ops
            and len(slicer_sub_ops) == len(gen.get("sub_operations", []) or [])
        )
        if issue_type in {"InvalidSlicerAPI", "SlicerSemanticError", "MissingOperationFootprint"}:
            return "reground_slicer_op" if pure_slicer_op else "contract_aware_template_repair"
        if issue_type == "UnprovenReceiver":
            return "gather_api_evidence"
        if issue_type in {
            "CallableReferenceMisuse", "BadInstructionText",
            "ModuleEnterPreconditionMissing", "SyntaxError",
        }:
            return "targeted_template_repair"
        if issue_type in {"LowConfidenceFallback", "UnresolvedPlaceholder"}:
            return "parameter_contract_repair"
        return "contract_aware_template_repair"

    @staticmethod
    def _repair_plan_from_issues(issues: List[Dict]) -> List[Dict]:
        return [
            {
                "issue_id": issue.get("issue_id"),
                "template_key": issue.get("template_key"),
                "step_id": issue.get("step_id"),
                "strategy": issue.get("repair_strategy"),
                "route": issue.get("repair_route"),
                "semantic_recipe_id": issue.get("semantic_recipe_id", ""),
            }
            for issue in issues or []
        ]

    def _repair_templates_in_memory(
        self,
        extension_name: str,
        templates: Dict[str, str],
        generators: List[Dict],
        workflow_contract: Dict,
        issues: List[Dict],
        logic_analysis: Optional[Dict],
    ) -> Optional[Dict[str, str]]:
        """Ask the LLM for targeted template repairs without writing files."""
        if not issues:
            return None

        affected = {
            issue.get("template_key")
            for issue in issues
            if issue.get("template_key")
        }
        if not affected:
            affected = {
                gen.get("template_file") or gen.get("pre_template_file") or gen.get("post_template_file")
                for gen in generators or []
            }
        affected = {key for key in affected if key in templates}
        if not affected:
            return None

        issue_text = json.dumps(issues, indent=2)
        contract_steps = []
        for step in (workflow_contract or {}).get("steps", []):
            sid = step.get("step_id", "")
            if any(sid and sid in key for key in affected):
                contract_steps.append(step)
        templates_text = "\n\n".join(
            f"--- {key} ---\n{templates[key]}"
            for key in sorted(affected)
        )
        logic_methods = []
        if logic_analysis:
            for method in logic_analysis.get("methods", []) or []:
                logic_methods.append({
                    "name": method.get("name", ""),
                    "parameters": method.get("parameters", []),
                    "state_reads": method.get("state_reads", []),
                    "state_writes": method.get("state_writes", []),
                })

        prompt = textwrap.dedent(f"""\
You are repairing generated 3D Slicer workflow templates for extension "{extension_name}".

Fix only the affected templates. Use the workflow contract as the source of truth.
Do not introduce extension-specific assumptions beyond the contract and source facts.

VALIDATION ISSUES:
{issue_text}

WORKFLOW CONTRACT STEPS:
{json.dumps(contract_steps, indent=2)}

LOGIC METHOD FACTS:
{json.dumps(logic_methods[:80], indent=2)}

TEMPLATES:
{templates_text}

Rules:
- Return valid JSON only.
- Gather and report receiver-type, method-existence, and behavior evidence before rewriting code.
- Distinguish invalid code from missing proof; do not claim a call is valid from absence of a probe failure.
- Preserve template placeholders like {{name: default}} and {{vol_lookup}}.
- Do not use blocked modules or functions: os, sys, subprocess, socket, eval, exec, open, getattr, setattr, globals, locals, vars, dir.
- For node class conflicts, the workflow contract and parameter metadata win.
- For API errors, replace only invalid Slicer API calls with APIs supported by the evidence in the issue.
- For CallableReferenceMisuse, call the function explicitly (for example slicer.util.selectedModule()) when reading its value.
- Module-enter lifecycle setup is handled deterministically outside this LLM repair.
- For BadInstructionText, replace empty/None/null instructions with the cookbook step description from the workflow contract.
- For LowConfidenceFallback, do not silently use 0/0.0/False typed fallback values for required logic inputs. Bind from a user/cookbook value, derive a source-backed default, or raise a clear RuntimeError that names the missing input.
- For stubs, implement the required operation or instruction-only setup if the contract explicitly allows it.
- Do not introduce unrelated UI, icon, toolbar, module-switching, or layout behavior.

Return:
{{
  "templates": {{
    "templates/name.py.tpl": "complete repaired template content"
  }},
  "fix_description": "short summary"
}}""")

        for _attempt in range(self._FORMAT_RETRY_MAX_ATTEMPTS):
            response = self._call_llm(prompt)
            fixed = self._parse_json_response(response)
            if isinstance(fixed, dict) and isinstance(fixed.get("templates"), dict):
                repaired = dict(templates)
                for tpl_name, tpl_content in fixed["templates"].items():
                    key = tpl_name if tpl_name.startswith("templates/") else f"templates/{tpl_name}"
                    if key in affected and isinstance(tpl_content, str):
                        repaired[key] = tpl_content
                return self._sanitize_templates(repaired)
            prompt += "\n\nPrevious response was not valid JSON with a templates object. Return only the required JSON."
        return None

    def _reground_slicer_template(
        self,
        issue: Dict,
        templates: Dict[str, str],
        generators: List[Dict],
    ) -> Optional[Tuple[str, str, Dict]]:
        """Re-run the evidence-seeking SlicerOpGenerator for one failed template."""
        template_key = issue.get("template_key", "")
        if not template_key or template_key not in templates:
            return None
        gen = next((
            item for item in generators or []
            if template_key in {
                item.get("template_file"),
                item.get("pre_template_file"),
                item.get("post_template_file"),
            }
        ), None)
        if not gen:
            return None

        slicer_sub_ops = [
            so for so in gen.get("sub_operations", []) or []
            if so.get("op_type") == "slicer_op"
        ]
        if not slicer_sub_ops and gen.get("operation_type") != "slicer_op":
            return None
        source = slicer_sub_ops[0] if slicer_sub_ops else gen

        from ..CookbookParser import SubOperation
        from ..SlicerOpGenerator import SlicerOpGenerator

        description = (
            source.get("description")
            or gen.get("description")
            or (issue.get("contract_step") or {}).get("description")
            or issue.get("message", "")
        )
        recipe = issue.get("semantic_recipe") or {}
        keywords = list(source.get("slicer_api_keywords") or [])
        keywords.extend(recipe.get("retrieval_queries") or [])
        sub_op = SubOperation(
            op_type="slicer_op",
            description=description,
            slicer_api_keywords=sorted(set(k for k in keywords if k)),
            interaction_type=source.get("interaction_type"),
            node_class=source.get("node_class"),
            placement_instructions=source.get("placement_instructions"),
            evidence_type="verify_repair_reground",
            evidence_id=issue.get("issue_id"),
            confidence="high",
            interaction_kind=source.get("interaction_kind"),
            slicer_op_category=(
                source.get("slicer_op_category")
                or issue.get("slicer_op_category")
                or "generic_slicer_api"
            ),
        )
        sub_op.repair_context = {
            "validation_issue": issue.get("message", ""),
            "semantic_recipe": recipe,
            "existing_api_evidence": gen.get("api_evidence") or {},
            "failed_code": templates[template_key],
        }

        skill_path = os.path.join(
            _PROJECT_ROOT, "Resources", "Skills", "slicer-skill-full"
        )
        debug_path = None
        if self._debug_dir:
            debug_path = os.path.join(
                self._debug_dir,
                f"verify_repair_reground_{issue.get('step_id') or 'unknown'}.json",
            )

        def _progress(finished, total, detail):
            self._phase_progress(
                "verify_repair",
                f"Re-grounding {template_key}: {detail}",
                "Verify And Repair Templates",
            )

        generator = SlicerOpGenerator(
            llm_client=self.llm_client,
            skill_path=skill_path,
            on_progress=_progress,
            debug_path=debug_path,
        )
        step_match = _re.search(r"cb_step_(\d+)", issue.get("step_id", "") or template_key)
        step_number = int(step_match.group(1)) if step_match else 0
        generated = generator.generate([(step_number, sub_op)])
        code = next(iter(generated.values()), "")
        if not code or "SLICER_OP_GENERATION_FAILED" in code:
            return None
        records = list(getattr(generator, "last_run_records", []) or [])
        evidence = {
            "source": "verify_repair_reground",
            "issue_id": issue.get("issue_id"),
            "semantic_recipe_id": issue.get("semantic_recipe_id", ""),
            "behavior_requirements": recipe.get("behavior_requirements", []),
            "invalid_substitutions": recipe.get("invalid_substitutions", []),
            "evidence_policy": recipe.get("evidence_policy", ""),
            "generator_records": records,
        }
        return template_key, code, evidence

    def _execute_repair_plan(
        self,
        extension_name: str,
        templates: Dict[str, str],
        generators: List[Dict],
        workflow_contract: Dict,
        issues: List[Dict],
        logic_analysis: Optional[Dict],
    ) -> Tuple[Optional[Dict[str, str]], List[Dict]]:
        """Execute issue-specific repair strategies and return changed templates."""
        repaired = dict(templates)
        strategy_results = []
        remaining = []

        reground_by_template = {}
        for issue in issues or []:
            if issue.get("repair_strategy") == "gather_api_evidence":
                strategy_results.append({
                    "template_key": issue.get("template_key", ""),
                    "strategy": "gather_api_evidence",
                    "changed": False,
                    "evidence_diagnosis": issue.get("evidence_diagnosis", {}),
                })
            elif issue.get("repair_strategy") == "reground_slicer_op":
                key = issue.get("template_key", "")
                existing = reground_by_template.get(key)
                if (
                    existing is None
                    or (
                        issue.get("semantic_recipe_id")
                        and not existing.get("semantic_recipe_id")
                    )
                ):
                    reground_by_template[key] = issue
            elif issue.get("issue_type") == "ModuleEnterPreconditionMissing":
                key = issue.get("template_key", "")
                if key in repaired:
                    updated = self._inject_module_enter_precondition(
                        repaired[key], extension_name
                    )
                    changed = updated != repaired[key]
                    repaired[key] = updated
                    strategy_results.append({
                        "template_key": key,
                        "strategy": "deterministic_module_enter_precondition",
                        "changed": changed,
                    })
            elif issue.get("issue_class") in {"contract", "dataflow"}:
                strategy_results.append({
                    "template_key": issue.get("template_key", ""),
                    "strategy": "requires_upstream_artifact_rebuild",
                    "route": issue.get("repair_route"),
                    "changed": False,
                    "blocked": True,
                })
            else:
                remaining.append(issue)

        for template_key, issue in reground_by_template.items():
            result = self._reground_slicer_template(issue, repaired, generators)
            if not result:
                remaining.append(issue)
                strategy_results.append({
                    "template_key": template_key,
                    "strategy": "reground_slicer_op",
                    "changed": False,
                })
                continue
            key, code, evidence = result
            changed = repaired.get(key) != code
            repaired[key] = code
            strategy_results.append({
                "template_key": key,
                "strategy": "reground_slicer_op",
                "changed": changed,
                "evidence": evidence,
            })
            gen = next((
                item for item in generators or []
                if key in {
                    item.get("template_file"),
                    item.get("pre_template_file"),
                    item.get("post_template_file"),
                }
            ), None)
            if gen is not None:
                recipe = issue.get("semantic_recipe") or {}
                gen["semantic_recipe_id"] = issue.get("semantic_recipe_id", "")
                gen["behavior_requirements"] = recipe.get("behavior_requirements", [])
                gen["invalid_substitutions"] = recipe.get("invalid_substitutions", [])
                gen["repair_evidence"] = evidence
            if isinstance(self._workflow_metadata, dict):
                self._workflow_metadata.setdefault("repair_evidence", {})[key] = evidence

        if remaining:
            llm_repaired = self._repair_templates_in_memory(
                extension_name,
                repaired,
                generators,
                workflow_contract,
                remaining,
                logic_analysis,
            )
            if llm_repaired:
                changed_keys = sorted(
                    key for key in llm_repaired
                    if llm_repaired.get(key) != repaired.get(key)
                )
                repaired = llm_repaired
                strategy_results.append({
                    "strategy": "targeted_or_contract_aware_template_repair",
                    "changed": bool(changed_keys),
                    "changed_templates": changed_keys,
                })

        repaired = self._sanitize_templates(repaired)
        return (repaired if repaired != templates else None), strategy_results

    def _verify_and_repair_templates(
        self,
        extension_name: str,
        templates: Dict[str, str],
        generators: List[Dict],
        logic_analysis: Optional[Dict],
        workflow_contract: Optional[Dict],
        workflow_graph: Optional[Dict],
    ) -> Tuple[Dict[str, str], Dict]:
        """Validate, live-probe, repair, and revalidate templates before packaging."""
        repair_log = []
        repair_coordinator = RepairCoordinator(
            (
                self._workflow_metadata.get("repair_strategy_history", [])
                if isinstance(self._workflow_metadata, dict) else []
            )
        )
        current_templates = self._sanitize_templates(dict(templates or {}))
        current_probe_result = None
        validation_result = {"valid": False, "errors": ["verify_repair did not run"]}

        for attempt in range(self._VERIFY_REPAIR_MAX_ATTEMPTS):
            self._phase_progress(
                "verify_repair",
                f"Validation attempt {attempt + 1}/{self._VERIFY_REPAIR_MAX_ATTEMPTS}",
                "Verify And Repair Templates",
            )
            self._sync_template_contracts(
                current_templates,
                generators,
                workflow_graph=workflow_graph,
            )
            current_probe_result = self._stage7c_live_api_probe(current_templates)
            self._sync_template_contracts(
                current_templates,
                generators,
                workflow_graph=workflow_graph,
            )
            validation_result = self._stage9_validate(
                current_templates,
                generators,
                logic_analysis=logic_analysis,
                api_probe_result=current_probe_result,
                extension_name=extension_name,
            )
            issues = self._validation_issues_from_result(
                validation_result,
                generators=generators,
                workflow_contract=workflow_contract,
            )
            filtered_issues = []
            for issue in issues:
                strategy = issue.get("repair_strategy", "")
                call_id = issue.get("call_id") or issue.get("issue_id", "")
                template_code = current_templates.get(issue.get("template_key", ""), "")
                content_fingerprint = hashlib.sha256(
                    template_code.encode("utf-8")
                ).hexdigest()[:20]
                if repair_coordinator.can_attempt(call_id, strategy, content_fingerprint):
                    filtered_issues.append(issue)
            issues = filtered_issues
            if isinstance(self._workflow_metadata, dict):
                repair_trace = self._workflow_metadata.setdefault("repair_trace", [])
                for issue in issues:
                    repair_trace.append({
                        "attempt": attempt + 1,
                        "issue_class": issue.get("issue_type"),
                        "repair_route": issue.get("repair_route"),
                        "template_file": issue.get("template_key", ""),
                        "message": issue.get("message", ""),
                    })
            repair_plan = self._repair_plan_from_issues(issues)
            repair_log.append({
                "attempt": attempt + 1,
                "valid": bool(validation_result.get("valid")),
                "issue_count": len(issues),
                "issues": issues,
                "repair_plan": repair_plan,
                "api_probe_result": current_probe_result,
            })
            if validation_result.get("valid"):
                break
            repaired, strategy_results = self._execute_repair_plan(
                extension_name,
                current_templates,
                generators,
                workflow_contract or {},
                issues,
                logic_analysis,
            )
            repair_log[-1]["strategy_results"] = strategy_results
            if not repaired or repaired == current_templates:
                for issue in issues:
                    template_code = current_templates.get(issue.get("template_key", ""), "")
                    repair_coordinator.record(
                        issue.get("call_id") or issue.get("issue_id", ""),
                        issue.get("repair_strategy", ""),
                        "failed",
                        hashlib.sha256(template_code.encode("utf-8")).hexdigest()[:20],
                    )
                break
            current_templates = repaired

        if not validation_result.get("valid"):
            final_issues = self._validation_issues_from_result(
                validation_result,
                generators=generators,
                workflow_contract=workflow_contract,
            )
            repaired, strategy_results = self._execute_repair_plan(
                extension_name,
                current_templates,
                generators,
                workflow_contract or {},
                final_issues,
                logic_analysis,
            )
            if repaired and repaired != current_templates:
                self._phase_progress(
                    "verify_repair",
                    "Final consolidated repair validation",
                    "Verify And Repair Templates",
                )
                current_templates = repaired
                self._sync_template_contracts(
                    current_templates,
                    generators,
                    workflow_graph=workflow_graph,
                )
                current_probe_result = self._stage7c_live_api_probe(current_templates)
                self._sync_template_contracts(
                    current_templates,
                    generators,
                    workflow_graph=workflow_graph,
                )
                validation_result = self._stage9_validate(
                    current_templates,
                    generators,
                    logic_analysis=logic_analysis,
                    api_probe_result=current_probe_result,
                    extension_name=extension_name,
                )
                repair_log.append({
                    "attempt": "final",
                    "valid": bool(validation_result.get("valid")),
                    "issue_count": len(self._validation_issues_from_result(
                        validation_result,
                        generators=generators,
                        workflow_contract=workflow_contract,
                    )),
                    "issues": self._validation_issues_from_result(
                        validation_result,
                        generators=generators,
                        workflow_contract=workflow_contract,
                    ),
                    "repair_plan": self._repair_plan_from_issues(final_issues),
                    "strategy_results": strategy_results,
                    "api_probe_result": current_probe_result,
                })

        if isinstance(self._workflow_metadata, dict):
            self._workflow_metadata["repair_strategy_history"] = repair_coordinator.history
            self._workflow_metadata["verify_repair"] = {
                "attempts": repair_log,
                "status": "passed" if validation_result.get("valid") else "failed",
                "used_outer_revision": False,
            }
        validation_result["repair_log"] = repair_log
        validation_result["api_probe_result"] = current_probe_result
        return current_templates, validation_result
