from .common import *

_SEMANTIC_REPAIR_RECIPES = {
    "slice_intersection_visibility": {
        "recipe_id": "slice_intersection_visibility",
        "required_api_patterns": [
            "slicer.app.applicationLogic().SetIntersectingSlicesEnabled(...)",
            "vtkMRMLSliceNode.Modified() after per-slice interaction changes",
        ],
        "forbidden_api_patterns": [
            "crosshair-only visibility APIs",
            "module switching used as the operation implementation",
        ],
        "search_terms": [
            "SetIntersectingSlicesEnabled",
            "SetSliceIntersectionInteractionEnabled",
            "SetSliceIntersectionInteractionModeFlags",
        ],
    },
    "layout_activate": {
        "recipe_id": "layout_activate",
        "required_api_patterns": ["layoutManager().setLayout(...)"],
        "forbidden_api_patterns": ["AddLayoutDescription without activating the layout"],
        "search_terms": ["layoutManager setLayout"],
    },
    "view_display_scope": {
        "recipe_id": "view_display_scope",
        "required_api_patterns": [
            "view-node filtering plus display-node 2D/slice visibility for slice targets",
        ],
        "forbidden_api_patterns": ["view-node filtering without enabling slice visibility"],
        "search_terms": ["AddViewNodeID SetVisibility2D SetSliceProjection"],
    },
}


class AnalyzerRepairLoopMixin:
    _VERIFY_REPAIR_MAX_ATTEMPTS = 3
    _FORMAT_RETRY_MAX_ATTEMPTS = 2

    @staticmethod
    def _classify_validation_issue(error: str) -> str:
        text = error or ""
        lowered = text.lower()
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
        for index, error in enumerate(validation_result.get("errors", []) or []):
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
            issues.append({
                "issue_id": f"issue_{index + 1}",
                "issue_type": issue_type,
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
                "semantic_recipe_id": recipe_id,
                "semantic_recipe": _SEMANTIC_REPAIR_RECIPES.get(recipe_id, {}),
                "evidence_requirements": {
                    "search_terms": _SEMANTIC_REPAIR_RECIPES.get(recipe_id, {}).get(
                        "search_terms", []
                    ),
                    "required_api_patterns": _SEMANTIC_REPAIR_RECIPES.get(recipe_id, {}).get(
                        "required_api_patterns", []
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
- Preserve template placeholders like {{name: default}} and {{vol_lookup}}.
- Do not use blocked modules or functions: os, sys, subprocess, socket, eval, exec, open, getattr, setattr, globals, locals, vars, dir.
- For node class conflicts, the workflow contract and parameter metadata win.
- For API errors, replace only invalid Slicer API calls with APIs supported by the evidence in the issue.
- For CallableReferenceMisuse, call the function explicitly (for example slicer.util.selectedModule()) when reading its value.
- For ModuleEnterPreconditionMissing, add the standard module-enter precondition after imports and before extension logic use:
  # precondition:begin
  # Ensure the extension module is active so module.enter() has run.
  _active_module = slicer.app.moduleManager().activeModule()
  if _active_module is None or _active_module.name != "{extension_name}":
      try:
          slicer.util.selectModule("{extension_name}")
      except Exception as _module_enter_error:
          print(f"Warning: could not activate module '{extension_name}': {{_module_enter_error}}")
  # precondition:end
- For BadInstructionText, replace empty/None/null instructions with the cookbook step description from the workflow contract.
- For LowConfidenceFallback, do not silently use 0/0.0/False typed fallback values for required logic inputs. Bind from a user/cookbook value, derive a source-backed default, or raise a clear RuntimeError that names the missing input.
- For stubs, implement the required operation or instruction-only setup if the contract explicitly allows it.

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
        keywords.extend(recipe.get("search_terms") or [])
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
            "required_api_patterns": recipe.get("required_api_patterns", []),
            "forbidden_api_patterns": recipe.get("forbidden_api_patterns", []),
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
            if issue.get("repair_strategy") == "reground_slicer_op":
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
                gen["required_api_patterns"] = recipe.get("required_api_patterns", [])
                gen["forbidden_api_patterns"] = recipe.get("forbidden_api_patterns", [])
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
            self._workflow_metadata["verify_repair"] = {
                "attempts": repair_log,
                "status": "passed" if validation_result.get("valid") else "failed",
                "used_outer_revision": False,
            }
        validation_result["repair_log"] = repair_log
        validation_result["api_probe_result"] = current_probe_result
        return current_templates, validation_result
