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
    # Global cycle cap. Wasted same-strategy retries are prevented by the
    # per-lineage escalation ladder (RepairCoordinator), so a higher cap buys
    # real strategy diversity instead of repetition.
    _VERIFY_REPAIR_MAX_ATTEMPTS = 5
    _FORMAT_RETRY_MAX_ATTEMPTS = 2

    @staticmethod
    def _classify_validation_issue(error: str) -> str:
        text = error or ""
        lowered = text.lower()
        # Live-execution failures: a generated template raised when actually run
        # in Slicer (a runtime defect static checks miss). These are concrete,
        # traceback-backed template bugs — always repaired at template level, never
        # routed upstream. Checked first so the marker wins over substring overlaps
        # (e.g. an AttributeError traceback also matching api-existence patterns).
        if "live execution failed" in lowered:
            return "LiveExecutionError"
        # User-reported behavior error: the step runs without raising but does the
        # wrong thing. No traceback — the evidence is the user's description.
        if "function behavior error" in lowered or "user-reported behavior" in lowered:
            return "FunctionBehaviorError"
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
        if "inventedparameterrole" in lowered:
            return "InventedParameterRole"
        if "parametereffectnotapplied" in lowered:
            return "ParameterEffectNotApplied"
        if "interactionscopeexceeded" in lowered:
            return "InteractionScopeExceeded"
        if "pairedstepmechanismmismatch" in lowered:
            return "PairedStepMechanismMismatch"
        if "positionalviewresolution" in lowered:
            return "PositionalViewResolution"
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
        if issue_type in {
            "SlicerSemanticError", "MissingOperationFootprint",
            "PairedStepMechanismMismatch", "PositionalViewResolution",
        }:
            return "grounding"
        if issue_type in {
            "CallableReferenceMisuse", "BadInstructionText",
            "ModuleEnterPreconditionMissing", "SyntaxError", "StubTemplate",
            "NodeClassMismatch", "InventedParameterRole",
            "ParameterEffectNotApplied", "InteractionScopeExceeded",
            "LiveExecutionError", "FunctionBehaviorError",
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
            strategy = cls._repair_strategy_for_issue(classified, gen, structured)
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
            # Recipe synthesized from the contract step + validator message
            # (general mechanism). The static table is a deprecated fallback:
            # its retrieval hints are merged in when one still matches, and
            # the match is logged so the table can be retired after a release
            # of trace comparisons.
            recipe = cls._synthesize_semantic_recipe(
                issue_type, operation_intents,
                contract_steps.get(step_id, {}), str(error),
            )
            static_recipe = _SEMANTIC_REPAIR_RECIPES.get(recipe_id, {})
            if static_recipe:
                logger.info(
                    "[deprecated] static semantic recipe '%s' merged as fallback "
                    "alongside synthesized recipe", recipe_id,
                )
                recipe["retrieval_queries"] = list(dict.fromkeys(
                    list(recipe.get("retrieval_queries", []))
                    + list(static_recipe.get("retrieval_queries", []))
                ))
                recipe["behavior_requirements"] = list(dict.fromkeys(
                    list(static_recipe.get("behavior_requirements", []))
                    + list(recipe.get("behavior_requirements", []))
                ))
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
                "semantic_recipe_id": recipe.get("recipe_id", recipe_id),
                "semantic_recipe": recipe,
                "evidence_requirements": {
                    "retrieval_queries": recipe.get("retrieval_queries", []),
                    "behavior_requirements": recipe.get("behavior_requirements", []),
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
    def _synthesize_semantic_recipe(
        issue_type: str,
        operation_intents: List[str],
        contract_step: Dict,
        error: str,
    ) -> Dict:
        """Synthesize a repair recipe from generic inputs at repair time.

        Replaces the fixed _SEMANTIC_REPAIR_RECIPES table with a recipe built
        from what is actually known about the failing step: the contract step
        description, its operation intents, and the validator's stated
        requirement. Works for any extension and any operation — no
        per-operation rules.
        """
        step_desc = _text_or_empty((contract_step or {}).get("description"))
        behavior_requirements = []
        if step_desc:
            behavior_requirements.append(
                f"The step's contracted behavior is achieved: {step_desc}"
            )
        if error:
            behavior_requirements.append(
                f"The validator's stated requirement is satisfied: {error}"
            )

        # Retrieval queries from intents, contract-step terms, and API-shaped
        # tokens in the validator message (CamelCase or dotted chains).
        queries: List[str] = [intent for intent in (operation_intents or []) if intent]
        text = " ".join(filter(None, [step_desc, error]))
        api_tokens = [
            token for token in _re.findall(r"[A-Za-z_][A-Za-z0-9_.]{3,}", text)
            if "." in token or _re.search(r"[a-z][A-Z]", token)
        ]
        plain_terms = [
            token.lower()
            for token in _re.findall(r"[A-Za-z]{4,}", step_desc)
        ]
        queries.extend(sorted(set(api_tokens))[:12])
        queries.append(" ".join(dict.fromkeys(plain_terms))[:120])

        return {
            "recipe_id": f"synthesized:{issue_type or 'semantic'}",
            "knowledge_level": "behavioral_contract",
            "behavior_requirements": behavior_requirements,
            "invalid_substitutions": [
                "an implementation that does not produce the contracted behavior",
                "removing or skipping the required behavior instead of implementing it",
                "an unrelated operation (e.g. module switching) used as the implementation",
            ],
            "retrieval_queries": [q for q in queries if q and q.strip()],
            "retrieval_query_provenance": "synthesized_from_contract_and_validator",
            "evidence_policy": (
                "Select any source-backed implementation that satisfies the "
                "behavior validator."
            ),
        }

    @staticmethod
    def _repair_strategy_for_issue(issue_type: str, gen: Dict, structured: Optional[Dict] = None) -> str:
        slicer_sub_ops = [
            so for so in gen.get("sub_operations", []) or []
            if so.get("op_type") == "slicer_op"
        ]
        operation_type = gen.get("operation_type") or gen.get("op_type")
        pure_slicer_op = operation_type == "slicer_op" or (
            slicer_sub_ops
            and len(slicer_sub_ops) == len(gen.get("sub_operations", []) or [])
        )
        if issue_type in {
            "InvalidSlicerAPI", "SlicerSemanticError", "MissingOperationFootprint",
            "PairedStepMechanismMismatch", "PositionalViewResolution",
            # On a slicer_op step, both a user-reported behavior error and a runtime
            # crash are best fixed by re-grounding (KB + extension-source search),
            # not a blind rewrite. (LiveExecutionError only arises from runtime/live
            # errors fed into the Repair flow, so this never affects generation.)
            "FunctionBehaviorError", "LiveExecutionError",
        }:
            return "reground_slicer_op" if pure_slicer_op else "contract_aware_template_repair"
        if issue_type == "UnprovenReceiver":
            # A state-changing call whose method cannot be proven on a KNOWN
            # receiver type ("method_unproven") will never be resolved by more
            # probing — the method simply is not on that type. Escalate it to the
            # LLM rewrite path so the template can be repaired (remove the dead
            # call, replace with a proven method, or restructure). Receiver-type-
            # unknown and read-only cases keep the cheap evidence-gathering path.
            info = structured or {}
            diagnosis = info.get("diagnosis")
            if (
                diagnosis == "method_unproven"
                and info.get("effect") != "read_only"
                and info.get("blocking", True)
            ):
                return "contract_aware_template_repair"
            # A hallucinated attribute member (e.g. `logic.parameterNode`) cannot be
            # resolved by probing — the member simply does not exist on the receiver.
            # It is read-only but must still be rewritten to a proven member, so
            # escalate it too.
            if diagnosis == "member_unproven" and info.get("blocking", True):
                return "contract_aware_template_repair"
            return "gather_api_evidence"
        if issue_type in {
            "CallableReferenceMisuse", "BadInstructionText",
            "ModuleEnterPreconditionMissing", "SyntaxError",
            "InventedParameterRole", "ParameterEffectNotApplied",
            "InteractionScopeExceeded",
        }:
            return "targeted_template_repair"
        if issue_type in {"LowConfidenceFallback", "UnresolvedPlaceholder"}:
            return "parameter_contract_repair"
        return "contract_aware_template_repair"

    @staticmethod
    def _upstream_requests_from_issues(
        issues: List[Dict],
        escalated_lineages: Optional[set] = None,
    ) -> List[Dict]:
        """Convert contract/dataflow-rooted issues into structured re-entry requests.

        These issues cannot be fixed at template level; the pipeline engine
        re-runs the owning upstream phase with this feedback injected instead
        of blocking and asking the user to rerun manually. Issues whose
        escalation ladder ended at "upstream_request" (any class) are included
        via escalated_lineages.
        """
        escalated_lineages = escalated_lineages or set()
        requests = []
        for issue in issues or []:
            escalated = (
                issue.get("escalated_to_upstream")
                or RepairCoordinator.lineage_key(issue) in escalated_lineages
            )
            if issue.get("issue_class") not in {"contract", "dataflow"} and not escalated:
                continue
            requests.append({
                "phase": "contract",
                "issue_type": issue.get("issue_type", ""),
                "issue_class": issue.get("issue_class", ""),
                "step_ids": [issue["step_id"]] if issue.get("step_id") else [],
                "template_key": issue.get("template_key", ""),
                "message": issue.get("message", ""),
                "contract_step": issue.get("contract_step", {}),
                "repair_route": issue.get("repair_route", ""),
            })
        return requests

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

        # Wizard-grounded templates are DETERMINISTIC -- an LLM rewrite would lose
        # the [wizard drive] marker (their only footprint acceptance) and strand
        # the step permanently. Re-derive them from the recorded wizard evidence
        # instead, and keep them away from the LLM.
        wizard_repaired: Dict[str, str] = {}
        module_name = str(
            (workflow_contract or {}).get("extension_module_name")
            or (getattr(self, "_workflow_metadata", {}) or {}).get("extension_module_name")
            or extension_name
        )
        for gen in generators or []:
            key = gen.get("template_file") or ""
            if key not in affected:
                continue
            sub_ops = gen.get("sub_operations") or []
            if not any(isinstance(so, dict) and (so.get("wizard_nav")
                                                 or so.get("wizard_button")
                                                 or so.get("wizard_place_button"))
                       for so in sub_ops):
                continue
            step_id = (gen.get("param_signature") or {}).get("workflow_step", "")
            regenerated = self._maybe_generate_wizard_template(
                extension_name,
                {"step_id": step_id, "description": gen.get("description", ""),
                 "sub_operations": sub_ops},
                module_name,
            )
            if regenerated:
                wizard_repaired[key] = regenerated
                affected.discard(key)
        if wizard_repaired and not affected:
            # Every affected template was wizard-grounded -- no LLM round needed.
            merged = dict(templates)
            merged.update(wizard_repaired)
            self._last_fix_description = "Re-derived wizard drive template(s) deterministically"
            return self._sanitize_templates(merged)

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
        if not logic_methods and isinstance(self._workflow_metadata, dict):
            # Fallback when logic_analysis isn't in memory (e.g. the Repair-button
            # path loads from disk): use the proven method names persisted in the
            # package's callable inventory so PROVEN TARGETS isn't wrongly empty.
            logic_methods = [
                {"name": n}
                for n in (
                    self._workflow_metadata.get("extension_callable_inventory", {})
                    .get("logic_methods", []) or []
                )
            ]
        logic_attributes = []
        if isinstance(self._workflow_metadata, dict):
            logic_attributes = list(
                self._workflow_metadata.get("extension_callable_inventory", {})
                .get("logic_attributes", []) or []
            )
        memory_examples = self._repair_memory_examples(issues)

        # User-reported behavior errors execute WITHOUT raising — there is no
        # traceback, only the user's description of the wrong behavior. Surface
        # them explicitly so the LLM rewrites for correct behavior (not for a
        # crash that never happened).
        behavior_issues = [
            i for i in issues if i.get("issue_type") == "FunctionBehaviorError"
        ]
        behavior_section = ""
        if behavior_issues:
            lines = []
            for i in behavior_issues:
                lines.append(
                    f"- {i.get('template_key', '?')} (step {i.get('step_id', '?')}): "
                    f"{i.get('message', '')}"
                )
            behavior_section = (
                "\nUSER-REPORTED BEHAVIOR ERRORS (these steps run with NO exception "
                "but do the WRONG thing — rewrite the template so the step achieves "
                "the described correct behavior, grounded ONLY in the workflow "
                "contract and extension/Slicer source evidence; do not invent APIs; "
                "if the correct API cannot be found in evidence, emit "
                "`raise RuntimeError(\"MISSING_EVIDENCE: <what>\")`):\n"
                + "\n".join(lines) + "\n"
            )

        prompt = textwrap.dedent(f"""\
You are repairing generated 3D Slicer workflow templates for extension "{extension_name}".

Fix only the affected templates. Use the workflow contract as the source of truth.
Do not introduce extension-specific assumptions beyond the contract and source facts.

VALIDATION ISSUES:
{issue_text}
{behavior_section}

WORKFLOW CONTRACT STEPS:
{json.dumps(contract_steps, indent=2)}

PROVEN TARGETS (the ONLY methods known to exist on the extension logic receiver `logic`):
{json.dumps(logic_methods[:80], indent=2)}

PROVEN MEMBERS (the ONLY attributes/members known on `logic`; `getParameterNode` returns the parameter node):
{json.dumps(logic_attributes[:120], indent=2)}

TEMPLATES:
{templates_text}
{memory_examples}
Rules:
- Return valid JSON only.
- You may call a method on the `logic` receiver ONLY if its name appears in PROVEN TARGETS. Never call or assume a method that is not listed (it does not exist on the logic class — it may belong to the Widget class or not exist at all).
- A "method_unproven" issue with a known receiver type means the named method does NOT exist on that receiver. To repair it you MUST do exactly ONE of: (a) REMOVE the call if it sits in a defensive guard/fallback (e.g. `if hasattr(...)`, `try/except AttributeError`) and is not required by the contract step; (b) REPLACE it with a PROVEN TARGET method that achieves the contract step's stated effect; (c) RESTRUCTURE so the unprovable call is both unreachable and unnecessary.
- A "member_unproven" issue means an ATTRIBUTE access `logic.<name>` references a member that does NOT exist on the logic class. Replace it with a PROVEN MEMBER/TARGET that yields the intended object — most often the access should be the method call `logic.getParameterNode()` (e.g. rewrite `logic.parameterNode.GetNodeReference(...)` to `logic.getParameterNode().GetNodeReference(...)`). Never access an attribute that is not in PROVEN MEMBERS.
- Do NOT satisfy a "method_unproven" issue by wrapping a REQUIRED call in a new `hasattr`/`try` guard — guarding a required step does not implement it.
- Gather and report receiver-type, method-existence, and behavior evidence before rewriting code.
- Distinguish invalid code from missing proof; do not claim a call is valid from absence of a probe failure.
- Preserve template placeholders like {{name: default}} and {{vol_lookup}}.
- Do not use blocked modules or functions: os, sys, subprocess, socket, eval, exec, open, getattr, setattr, globals, locals, vars, dir.
- For node class conflicts, the workflow contract and parameter metadata win.
- For API errors, replace only invalid Slicer API calls with APIs supported by the evidence in the issue.
- A MISSING_EVIDENCE sentinel marks an extension-defined artifact (custom layout ID/XML, a `slicer.<Const>` the extension registers, a magic constant) that could not be found in source evidence. NEVER replace it with a guessed value, a name string passed where an ID is expected, or an invented constant. Resolve it ONLY from real evidence (the extension's source under `ext:<extension>/`, or an extension helper function that performs the operation). If no evidence is available, KEEP the sentinel — a loud failure is correct; a fabricated value is not.
- For CallableReferenceMisuse, call the function explicitly (for example slicer.util.selectedModule()) when reading its value.
- Never invent parameter/reference role names: only roles present in the supplied parameter metadata exist. For InventedParameterRole issues, REMOVE the invented SetParameter/SetNodeReferenceID block entirely — do not rename it to another role; the called method manages that state internally.
- For ParameterEffectNotApplied, keep the SetParameter call and ADD a call to the listed evidence-backed applier method with the explicit final state; do not rely on GUI observers to apply parameter changes.
- For InteractionScopeExceeded, remove the interaction/handle/interactive-mode calls that the step description does not request; keep only the contracted visibility/state change.
- For PairedStepMechanismMismatch, both steps of the pair must change state through the SAME API — the one with the stronger evidence (core-UI control evidence or extension source); rewrite the weaker-evidenced step to use that mechanism with the opposite state value, never leave the pair split across different APIs.
- For PositionalViewResolution, resolve the named view NODE by identity from layout evidence (GetSingletonNode with the evidenced singleton tag, or GetFirstNodeByName with the evidenced node name) — never by positional widget index; positional accessors change meaning with the active layout.
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

        def _validate(candidate, raw):
            if isinstance(candidate, dict) and isinstance(candidate.get("templates"), dict):
                return candidate, []
            return None, ["Response must be a JSON object with a 'templates' object"]

        try:
            fixed = self._call_llm_structured(
                prompt=prompt,
                validator=_validate,
                call_class="repair",
                max_attempts=self._FORMAT_RETRY_MAX_ATTEMPTS,
                failure_label="Targeted template repair",
            )
        except RuntimeError:
            if wizard_repaired:
                # The LLM round failed but the wizard templates were still
                # re-derived deterministically -- keep them.
                merged = dict(templates)
                merged.update(wizard_repaired)
                return self._sanitize_templates(merged)
            return None
        self._last_fix_description = _text_or_empty(fixed.get("fix_description"))
        repaired = dict(templates)
        for tpl_name, tpl_content in fixed["templates"].items():
            key = tpl_name if tpl_name.startswith("templates/") else f"templates/{tpl_name}"
            if key in affected and isinstance(tpl_content, str):
                repaired[key] = tpl_content
        # The deterministically re-derived wizard templates win over anything the
        # LLM may have emitted for those keys.
        repaired.update(wizard_repaired)
        return self._sanitize_templates(repaired)

    @staticmethod
    def _broadened_keywords(step_text: str) -> List[str]:
        """Widened retrieval terms for an escalated re-ground rung.

        Generic synthesis from the failing step's text (tokenization) plus the
        Slicer core-UI pre-analysis index: controls whose labels match the
        step text contribute their observed API footprints. No rule tables;
        no-op when the pre-analysis artifacts are absent.
        """
        added = sorted({
            token for token in _re.findall(r"[A-Za-z][A-Za-z0-9_]{3,}", step_text)
        })[:24]
        try:
            from ..UIControlIndex import get_index
            index = get_index()
            if index is not None:
                ui_terms = []
                for match in index.match(step_text, top_k=4):
                    record = match.get("record", {})
                    ui_terms.extend((record.get("api_footprints") or [])[:6])
                    if record.get("object_name"):
                        ui_terms.append(record["object_name"])
                added.extend(sorted(set(ui_terms))[:12])
        except Exception:
            logger.debug("UI-evidence keyword broadening failed", exc_info=True)
        return added

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
        if issue.get("broadened_retrieval"):
            step_text = " ".join(filter(None, [
                _text_or_empty((issue.get("contract_step") or {}).get("description")),
                _text_or_empty(source.get("description")),
                _text_or_empty(issue.get("message")),
            ]))
            keywords.extend(self._broadened_keywords(step_text))
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

        # During generation the name comes from the parsed cookbook; the Repair
        # path never parses the cookbook, so fall back to the repair-set name —
        # otherwise the extension's own source would not be registered as a
        # searchable `ext:` root and re-grounding couldn't find extension evidence.
        _ext_name = (
            (self._cookbook_def.extension_name
             if getattr(self, "_cookbook_def", None) else "")
            or getattr(self, "_repair_extension_name", "")
        )
        generator = SlicerOpGenerator(
            llm_client=self.llm_client,
            skill_path=skill_path,
            on_progress=_progress,
            debug_path=debug_path,
            extension_name=_ext_name,
            extension_source_path=getattr(self, "_source_path", ""),
        )
        step_match = _re.search(r"cb_step_(\d+)", issue.get("step_id", "") or template_key)
        step_number = int(step_match.group(1)) if step_match else 0
        generated = generator.generate([(step_number, sub_op)])
        code = next(iter(generated.values()), "")
        if not code or "SLICER_OP_GENERATION_FAILED" in code:
            return None
        # Re-grounding regenerates the slicer_op code from scratch, dropping any
        # binding preamble that generation injected. Re-apply the Segment Editor
        # crash-preventer so a re-grounded effect-drive template stays bound.
        code = self._ensure_segment_editor_bindings(code)
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
            elif issue.get("issue_class") in {"contract", "dataflow"} and issue.get(
                "repair_strategy", ""
            ) in {"", "rebuild_contract", "rebuild_dataflow", "upstream_request"}:
                # No template-level rung assigned — this issue is owned by the
                # pipeline engine's upstream re-entry (see upstream_requests).
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
        seed_errors: Optional[List[str]] = None,
    ) -> Tuple[Dict[str, str], Dict]:
        """Validate, live-probe, repair, and revalidate templates before packaging.

        seed_errors (optional): externally-reported failures — recorded runtime API
        errors and user function-error descriptions — injected as first-iteration
        issues so they are repaired WITH grounded re-search/validation alongside any
        static issue, even when static validation alone would pass. Used by the
        Repair button to give it the same capability as generation.
        """
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
        applied_last_cycle: Dict[str, str] = {}
        last_cycle_issues: List[Dict] = []
        escalated_upstream_lineages: set = set()

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
            # First-iteration seed injection: turn externally-reported failures into
            # issues (same path → each gets a synthesized semantic_recipe with
            # retrieval_queries that drives grounded re-search) and append them to
            # the static issues. Force invalid so the loop repairs them even if
            # static validation passed.
            if attempt == 0 and seed_errors:
                seed_issues = self._validation_issues_from_result(
                    {"errors": list(seed_errors)},
                    generators=generators,
                    workflow_contract=workflow_contract,
                )
                seen = {
                    (i.get("template_key"), i.get("issue_type")) for i in issues
                }
                for si in seed_issues:
                    if (si.get("template_key"), si.get("issue_type")) not in seen:
                        issues.append(si)
                if seed_issues:
                    validation_result["valid"] = False
            # Escalation ladder: a lineage that survived the strategy applied
            # in the previous cycle exhausts that rung — the next rung of its
            # issue-class ladder becomes mandatory. Lineages whose ladder ends
            # in "upstream_request" are routed to the pipeline engine for
            # upstream phase re-entry instead of more template-level retries.
            surviving_lineages = set()
            for issue in issues:
                lineage = RepairCoordinator.lineage_key(issue)
                prior_rung = applied_last_cycle.get(lineage)
                if prior_rung:
                    repair_coordinator.record_lineage(lineage, prior_rung, "survived")
                    surviving_lineages.add(lineage)
                    self._repair_memory_record(issue, prior_rung, "failed")
            # Lineages repaired last cycle that no longer appear were fixed —
            # record the successful strategy as cross-run experience.
            for prev_issue in last_cycle_issues:
                lineage = RepairCoordinator.lineage_key(prev_issue)
                rung = applied_last_cycle.get(lineage)
                if rung and lineage not in surviving_lineages:
                    self._repair_memory_record(
                        prev_issue, rung, "succeeded",
                        getattr(self, "_last_fix_description", ""),
                    )
            applied_last_cycle = {}
            filtered_issues = []
            for issue in issues:
                lineage = RepairCoordinator.lineage_key(issue)
                rung = repair_coordinator.next_strategy(issue)
                if rung == "upstream_request":
                    issue["escalated_to_upstream"] = True
                    escalated_upstream_lineages.add(lineage)
                    repair_coordinator.record_lineage(lineage, rung, "requested")
                    continue
                if rung is None:
                    repair_coordinator.record_lineage(lineage, "", "exhausted")
                    continue
                issue["ladder_rung"] = rung
                if rung == "reground_broadened":
                    issue["repair_strategy"] = "reground_slicer_op"
                    issue["broadened_retrieval"] = True
                else:
                    issue["repair_strategy"] = rung
                filtered_issues.append(issue)
            issues = filtered_issues

            # Detailed attempt report for the UI/debug log: issue breakdown
            # and the ladder rung chosen per lineage.
            if not validation_result.get("valid"):
                type_counts: Dict[str, int] = {}
                for issue in issues:
                    key = issue.get("issue_type", "?")
                    type_counts[key] = type_counts.get(key, 0) + 1
                breakdown = ", ".join(
                    f"{itype}x{count}" for itype, count in sorted(type_counts.items())
                ) or "none repairable"
                self._phase_progress(
                    "verify_repair",
                    f"Attempt {attempt + 1} found {len(issues)} repairable issue(s) "
                    f"[{breakdown}]"
                    + (f"; {len(escalated_upstream_lineages)} lineage(s) escalated "
                       "to upstream re-entry" if escalated_upstream_lineages else ""),
                    "Verify And Repair Templates",
                )
                ladder_notes = [
                    f"{issue.get('step_id') or issue.get('template_key', '?')}:"
                    f"{issue.get('issue_type', '?')} -> "
                    f"{issue.get('ladder_rung', issue.get('repair_strategy', '?'))}"
                    for issue in issues[:6]
                ]
                if ladder_notes:
                    self._phase_progress(
                        "verify_repair",
                        "Repair ladder: " + "; ".join(ladder_notes)
                        + (" ..." if len(issues) > 6 else ""),
                        "Verify And Repair Templates",
                    )
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
            changed_results = [r for r in strategy_results or [] if r.get("changed")]
            if changed_results:
                self._phase_progress(
                    "verify_repair",
                    f"Repairs applied: {len(changed_results)} change(s) via "
                    + ", ".join(sorted({
                        str(r.get("strategy", "?")) for r in changed_results
                    })),
                    "Verify And Repair Templates",
                )
            elif strategy_results:
                self._phase_progress(
                    "verify_repair",
                    "No template changes produced by repair strategies this attempt",
                    "Verify And Repair Templates",
                )
            # Lineages repaired this cycle: if they reappear next cycle the
            # applied rung is recorded as survived (exhausted).
            applied_last_cycle = {
                RepairCoordinator.lineage_key(issue): issue.get(
                    "ladder_rung", issue.get("repair_strategy", "")
                )
                for issue in issues
            }
            last_cycle_issues = list(issues)
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

        if not validation_result.get("valid"):
            remaining_issues = self._validation_issues_from_result(
                validation_result,
                generators=generators,
                workflow_contract=workflow_contract,
            )
            upstream_requests = self._upstream_requests_from_issues(
                remaining_issues,
                escalated_lineages=escalated_upstream_lineages,
            )
            if upstream_requests:
                validation_result["upstream_requests"] = upstream_requests

        if isinstance(self._workflow_metadata, dict):
            self._workflow_metadata["repair_strategy_history"] = repair_coordinator.history
            self._workflow_metadata["verify_repair"] = {
                "attempts": repair_log,
                "status": "passed" if validation_result.get("valid") else "failed",
                "used_outer_revision": False,
            }
        validation_result["repair_log"] = repair_log
        validation_result["api_probe_result"] = current_probe_result
        upstream_count = len(validation_result.get("upstream_requests") or [])
        self._phase_progress(
            "verify_repair",
            f"verify_repair finished: {'PASS' if validation_result.get('valid') else 'FAIL'} "
            f"after {len(repair_log)} validation attempt(s)"
            + (f"; {upstream_count} upstream re-entry request(s) raised"
               if upstream_count else ""),
            "Verify And Repair Templates",
        )
        return current_templates, validation_result
