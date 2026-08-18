from .common import *
from .phases import PIPELINE_VERSION
from ..cli_artifacts import (
    debug_round_dir,
    next_repair_round_label,
    snapshot_package_version,
)


class AnalyzerLiveRevisionMixin:
    """Whole-package revision: rewrite templates that failed static validation.

    Reached from ONE place -- `_autoReviseCli`, when a generation run finishes
    with an invalid validation_result. It is the generation pipeline's own
    last-chance repair, and it is the only revision that may rewrite the whole
    package and re-stamp ``manifest["status"]``.

    Two things that used to live here are gone. The live-execution gate
    (`live_validate_templates` / `repair_live_failures`) executed every step of
    a package against the real MRML scene from the CLI panel; and
    `repair_generated_cli` took free-form "step 12 behaves wrongly" sentences,
    guessed which step each meant with an LLM call, and repaired blind. Both
    were reachable only from the deleted "Repair Generated CLI" button. A step
    that runs without raising but does the wrong thing is now revised where it
    is SEEN -- the ✍ button beside Send, on the step in front of the user, with
    that step's template, that run's execution output and the live scene in the
    prompt (SlicerAIAgentLib/TemplateReviser.py, app/widget_revise.py).
    """

    def _begin_repair_round(self, cli_dir: str, extension_name: str = "") -> str:
        """Set up an isolated debug folder for one repair round; return its label.

        Each repair round gets debug/repair_NNN/ with its own LLM-call files and a
        fresh ui_output.log, so it never clobbers the first generation's debug or a
        prior round's. The returned label is reused for the version snapshot so the
        debug and versions folders line up.
        """
        import time as _time
        round_label = next_repair_round_label(cli_dir)
        self._debug_dir = debug_round_dir(cli_dir, round_label)
        self._llm_call_counter = 0
        self._progress_events = []
        self._phase_durations = {}
        self._phase_start_times = {}
        self._pipeline_start = _time.time()
        self._progress_log_name = "ui_output.log"
        self._progress_json_name = "progress_events.json"
        ext_name = extension_name or getattr(self, "_repair_extension_name", "") or os.path.basename(cli_dir)
        try:
            self._begin_ui_output_round(round_label, ext_name, "", "repair")
        except Exception:
            logger.debug("repair-round ui_output header failed", exc_info=True)
        return round_label

    # ================================================================
    # Revision System
    # ================================================================

    _MAX_SOURCE_CONTEXT_CHARS = 400_000

    def _build_revision_source_context(
        self,
        source_path: Optional[str],
        manifest: Dict,
        generators: List[Dict],
    ) -> str:
        """Build source code context for the revision prompt.

        Extracts the logic class method sources and UI file content from
        the extension's source directory.  Method sources are extracted via
        AST so only the relevant class body is included (not the full file).

        Returns a formatted string for the revision prompt, or empty string
        if source_path is not available.
        """
        if not source_path or not os.path.isdir(source_path):
            return ""

        logic_class_name = manifest.get("logic_class_name", "")
        module_name = manifest.get("extension_module_name", "")

        # Find .py and .ui files in the extension source tree
        py_files = []
        ui_files = []
        for root, dirs, files in os.walk(source_path):
            dirs[:] = [d for d in dirs if not d.startswith((".", "__")) and d != "build"]
            for f in files:
                if f.endswith(".py"):
                    py_files.append(os.path.join(root, f))
                elif f.endswith(".ui"):
                    ui_files.append(os.path.join(root, f))

        # Extract logic class method sources
        parts = []
        for py_file in py_files:
            try:
                with open(py_file, "r", encoding="utf-8", errors="ignore") as f:
                    source = f.read()
                tree = ast.parse(source)
            except Exception:
                continue

            lines = source.split("\n")
            for node in ast.iter_child_nodes(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                # Match the logic class
                if node.name != logic_class_name and not (
                    logic_class_name and node.name.endswith("Logic")
                ):
                    continue

                method_sources = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        start = item.lineno - 1
                        end = (
                            item.end_lineno
                            if hasattr(item, "end_lineno") and item.end_lineno
                            else start + 60
                        )
                        method_src = "\n".join(lines[start:end])
                        method_sources.append(
                            f"  def {item.name}(...):\n"
                            + "\n".join("    " + l for l in method_src.split("\n")[1:])
                        )

                if method_sources:
                    parts.append(
                        f"--- {os.path.basename(py_file)}: class {node.name} ---\n"
                        + "\n\n".join(method_sources)
                    )
                break

        # Include UI file (has parameter node property names, widget names)
        for ui_file in ui_files:
            try:
                with open(ui_file, "r", encoding="utf-8", errors="ignore") as f:
                    ui_content = f.read()
                # Trim UI to just property names and node references (remove layout boilerplate)
                if len(ui_content) > 5000:
                    # Extract lines with objectName, property, node references
                    import re
                    key_lines = []
                    for line in ui_content.split("\n"):
                        stripped = line.strip()
                        if any(kw in stripped for kw in (
                            "objectName", "property", "nodeReference",
                            "MRMLNode", "parameterName", "SetNodeReferenceID",
                            "<property", "<string>", "ctkMRMLNodeComboBox",
                        )):
                            key_lines.append(stripped)
                    if key_lines:
                        ui_content = (
                            "<!-- UI key properties (truncated) -->\n"
                            + "\n".join(key_lines[:200])
                        )
                    else:
                        ui_content = "<!-- UI file present but no key properties found -->"
                parts.append(f"--- {os.path.basename(ui_file)} (UI) ---\n{ui_content}")
            except Exception:
                pass

        combined = "\n\n".join(parts)

        # Truncate if too large
        if len(combined) > self._MAX_SOURCE_CONTEXT_CHARS:
            combined = combined[:self._MAX_SOURCE_CONTEXT_CHARS] + "\n# ... [truncated]"

        return combined

    def _build_revision_prompt_fragment(
        self,
        extension_name: str,
        tool_schemas: List[Dict],
        generators: List[Dict],
    ) -> str:
        """Build a deterministic prompt fragment after successful revision."""
        tool_names = []
        for schema in tool_schemas or []:
            fn = schema.get("function", {}) if isinstance(schema, dict) else {}
            if fn.get("name"):
                tool_names.append(fn["name"])
        if not tool_names:
            tool_names = [extension_name]

        step_lines = []
        for gen in generators or []:
            step = gen.get("param_signature", {}).get("workflow_step", "")
            desc = gen.get("description", "")
            step_type = gen.get("step_type", "automated")
            if step:
                step_lines.append(f"- `{step}` [{step_type}]: {desc}")

        return (
            f"### {extension_name}\n\n"
            f"Generated CLI package status: validated.\n\n"
            f"Available tool: `{tool_names[0]}`.\n\n"
            "Execute cookbook workflow steps in order. For automated steps, run "
            "the returned code. For interactive or mixed steps, run the pre-code, "
            "wait for the user to finish the requested interaction, then run the "
            "post-code.\n\n"
            "Workflow steps:\n"
            + "\n".join(step_lines)
            + "\n"
        )

    def revise(
        self,
        extension_name: str,
        errors: List[str],
        max_attempts: int = _MAX_REVISION_ATTEMPTS,
        source_path: Optional[str] = None,
        logic_analysis: Optional[Dict] = None,
        api_probe_result: Optional[Dict] = None,
    ) -> Dict:
        """Revise failed templates; always flushes progress artifacts to debug/."""
        result: Dict = {}
        try:
            result = self._revise_impl(
                extension_name, errors,
                max_attempts=max_attempts,
                source_path=source_path,
                logic_analysis=logic_analysis,
                api_probe_result=api_probe_result,
            )
            return result
        finally:
            try:
                self._flush_progress_artifacts(result if isinstance(result, dict) else {})
            except Exception:
                logger.debug("Revision progress flush failed", exc_info=True)

    def _revise_impl(
        self,
        extension_name: str,
        errors: List[str],
        max_attempts: int = _MAX_REVISION_ATTEMPTS,
        source_path: Optional[str] = None,
        logic_analysis: Optional[Dict] = None,
        api_probe_result: Optional[Dict] = None,
    ) -> Dict:
        """
        Revise failed templates using LLM feedback.

        Args:
            extension_name: Name of the CLI to revise.
            errors: List of error messages from validation or testing.
            source_path: Path to the extension's source directory. If provided,
                the logic class source code and UI file are included in the
                revision prompt so the LLM can verify API calls against actual
                method signatures.
            logic_analysis: Optional in-memory logic analysis from the failed
                generation run. When present, semantic validation remains active
                during revision.
            api_probe_result: Optional live API probe result from the failed
                generation run. When present, unresolved live API failures remain
                blocking during revision.

        Returns:
            Dict with 'success', 'validation_result', 'attempts' keys.
        """
        extension_name = _validate_extension_name(extension_name)
        from ..ExtensionCLILoader import get_cli_base_dir

        cli_dir = os.path.join(get_cli_base_dir(), extension_name)
        if not os.path.isdir(cli_dir):
            return {"success": False, "error": f"No CLI found for {extension_name}"}

        # Each revision is its own repair round (debug/repair_NNN/) with its own
        # LLM-call artifacts and ui_output.log, so it never clobbers the first
        # generation's debug or a prior round's.
        import time as _time
        if source_path:
            self._source_path = source_path
        repair_round = self._begin_repair_round(cli_dir, extension_name)
        self.on_progress(
            "verify_repair", "Verify And Repair Templates",
            f"Revision started for '{extension_name}' with {len(errors or [])} "
            f"reported error(s)",
        )

        # Load existing CLI data
        manifest_path = os.path.join(cli_dir, "manifest.json")
        generators_path = os.path.join(cli_dir, "code_generators.json")
        tool_schemas_path = os.path.join(cli_dir, "tool_schemas.json")
        workflow_metadata_path = os.path.join(cli_dir, "workflow_metadata.json")

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        with open(generators_path, "r", encoding="utf-8") as f:
            generators = json.load(f)

        workflow_metadata = {}
        if os.path.isfile(workflow_metadata_path):
            try:
                with open(workflow_metadata_path, "r", encoding="utf-8") as f:
                    workflow_metadata = json.load(f)
            except Exception:
                workflow_metadata = {}
        self._workflow_metadata = workflow_metadata

        # Load workflow.json to provide semantic context for revision
        workflow_path = os.path.join(cli_dir, manifest.get("workflow_graph_file", "workflow.json"))
        workflow_steps = {}
        workflow_data = None
        if os.path.isfile(workflow_path):
            try:
                with open(workflow_path, "r", encoding="utf-8") as f:
                    workflow_data = json.load(f)
                for ws in workflow_data.get("steps", []):
                    workflow_steps[ws.get("step_id", "")] = ws
            except Exception:
                pass

        tool_schemas = []
        if os.path.isfile(tool_schemas_path):
            with open(tool_schemas_path, "r", encoding="utf-8") as f:
                tool_schemas = json.load(f)

        # Collect source code context (logic class methods + UI file)
        source_context = self._build_revision_source_context(
            source_path, manifest, generators
        )

        # Repair deterministic workflow contracts before template-only LLM
        # revision.  This lets revision fix stale graph/generator metadata from
        # older failed packages without extension-specific rules.
        if source_path and workflow_data and logic_analysis:
            try:
                scan_result = self._stage1_scan(source_path)
                self._placement_starter_methods = self._classify_placement_starter_methods(
                    logic_analysis
                )
                self._normalize_workflow_contracts(
                    workflow_data, self._workflow_metadata, scan_result, logic_analysis
                )
                self._synthesize_workflow_ui_guidance(
                    workflow_data, self._workflow_metadata, scan_result, logic_analysis
                )
                _, generators = self._build_workflow_manifest_and_generators(
                    extension_name, scan_result, workflow_data
                )
                with open(workflow_path, "w", encoding="utf-8") as f:
                    json.dump(workflow_data, f, indent=2)
                with open(generators_path, "w", encoding="utf-8") as f:
                    json.dump(generators, f, indent=2)
                with open(workflow_metadata_path, "w", encoding="utf-8") as f:
                    json.dump(self._workflow_metadata, f, indent=2)
                workflow_steps = {
                    ws.get("step_id", ""): ws
                    for ws in workflow_data.get("steps", [])
                }
            except Exception:
                logger.debug("Revision workflow normalization failed", exc_info=True)

        result = {
            "success": False,
            "validation_result": None,
            "attempts": 0,
            "error": None,
        }

        initial_issues = self._validation_issues_from_result(
            {"errors": errors or []},
            generators=generators,
            workflow_contract=workflow_data or {"steps": []},
        )
        upstream_issues = [
            issue for issue in initial_issues
            if issue.get("issue_class") in {"contract", "dataflow"}
        ]
        if upstream_issues:
            repair_trace = self._workflow_metadata.setdefault("repair_trace", [])
            for issue in upstream_issues:
                repair_trace.append({
                    "issue_class": issue.get("issue_type"),
                    "repair_route": issue.get("repair_route"),
                    "template_file": issue.get("template_key", ""),
                    "message": issue.get("message", ""),
                })
            validation_result = {
                "valid": False,
                "errors": [
                    (
                        f"{issue.get('template_key') or 'workflow_contract'}: "
                        f"{issue.get('issue_type')} requires {issue.get('repair_route')} "
                        "before template revision"
                    )
                    for issue in upstream_issues
                ],
            }
            result["validation_result"] = validation_result
            upstream_requests = self._upstream_requests_from_issues(upstream_issues)
            result["upstream_requests"] = upstream_requests
            result["requires_regeneration"] = True
            # Persist the diagnosis so the next regeneration starts the
            # contract phase with this failure as structured feedback
            # (cross-run closed loop) instead of resampling blindly.
            self._save_pending_upstream_feedback(extension_name, upstream_requests)
            result["error"] = (
                "Upstream contract/dataflow issue detected; template-level revision "
                "cannot fix it. Re-run generation: the pipeline will re-derive the "
                "workflow contract using this failure as feedback."
            )
            self._finalize_package_validation_state(manifest, validation_result)
            try:
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, indent=2)
                with open(workflow_metadata_path, "w", encoding="utf-8") as f:
                    json.dump(self._workflow_metadata, f, indent=2)
            except Exception:
                logger.debug("Failed to persist upstream revision block", exc_info=True)
            return result

        for attempt in range(max_attempts):
            result["attempts"] = attempt + 1
            self.on_progress(
                "verify_repair", "Verify And Repair Templates",
                f"Revision attempt {attempt + 1}/{max_attempts}..."
            )

            # Read all templates
            templates = {}
            for gen in generators:
                # Collect all template file references from this generator
                tpl_files = [gen[key] for key in TEMPLATE_FILE_FIELDS if gen.get(key)]
                for tpl_file in tpl_files:
                    tpl_path = os.path.join(cli_dir, tpl_file)
                    if os.path.isfile(tpl_path):
                        with open(tpl_path, "r") as f:
                            templates[tpl_file] = f.read()

            # Re-evaluate current templates with fresh deterministic/live
            # evidence before asking the LLM to rewrite anything. Stale proof
            # failures from a previous validator version must not trigger a
            # broad template regeneration.
            self._sync_template_contracts(
                templates,
                generators,
                workflow_graph=workflow_data,
            )
            # Re-apply the core-module session drivers (module_sessions) so the
            # deterministic standard-op templates + shared-state binding survive
            # the revise path — the generation pass' _apply_module_session_drivers
            # does not run here, and an LLM rewrite may have dropped them.
            self._apply_module_session_drivers(
                templates,
                (workflow_data or {}).get("steps") if isinstance(workflow_data, dict) else None,
            )
            fresh_probe_result = self._stage7c_live_api_probe(templates)
            for tpl_file, tpl_code in templates.items():
                tpl_path = os.path.join(cli_dir, tpl_file)
                os.makedirs(os.path.dirname(tpl_path), exist_ok=True)
                with open(tpl_path, "w", encoding="utf-8") as f:
                    f.write(tpl_code)
            current_validation = self._stage9_validate(
                templates,
                generators,
                logic_analysis=logic_analysis,
                api_probe_result=fresh_probe_result,
                extension_name=extension_name,
            )
            if current_validation.get("valid"):
                manifest["manifest_version"] = 3
                manifest["pipeline_version"] = PIPELINE_VERSION
                self._workflow_metadata["revision_validation_status"] = "passed"
                self._finalize_package_validation_state(
                    manifest, current_validation,
                    templates=templates, generators=generators,
                )
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, indent=2)
                with open(workflow_metadata_path, "w", encoding="utf-8") as f:
                    json.dump(self._workflow_metadata, f, indent=2)
                # Archive this revision round's validated package snapshot.
                snapshot_package_version(cli_dir, repair_round)
                result["success"] = True
                result["validation_result"] = current_validation
                return result

            current_issues = self._validation_issues_from_result(
                current_validation,
                generators=generators,
                workflow_contract=workflow_data or {"steps": []},
            )
            rewrite_issues = [
                issue for issue in current_issues
                if issue.get("repair_strategy") != "gather_api_evidence"
            ]
            if current_issues and not rewrite_issues:
                result["validation_result"] = current_validation
                result["error"] = (
                    "Revision stopped because validation requires additional "
                    "receiver, method, or behavior evidence; templates were not rewritten."
                )
                self._finalize_package_validation_state(
                    manifest, current_validation,
                    templates=templates, generators=generators,
                )
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, indent=2)
                with open(workflow_metadata_path, "w", encoding="utf-8") as f:
                    json.dump(self._workflow_metadata, f, indent=2)
                return result

            errors = current_validation.get("errors", [])
            affected_templates = {
                issue.get("template_key")
                for issue in rewrite_issues
                if issue.get("template_key") in templates
            }
            # Build revision prompt
            templates_text = "\n\n".join(
                f"--- {name} ---\n{content}"
                for name, content in templates.items()
                if not affected_templates or name in affected_templates
            )

            source_section = ""
            if source_context:
                source_section = f"\nEXTENSION SOURCE CODE (use to verify correct API calls):\n{source_context}\n"

            # Build semantic context from workflow.json so the LLM knows what
            # each template is SUPPOSED to do (not just what the stub looks like).
            semantic_section = ""
            if workflow_steps:
                semantic_lines = []
                for tpl_file, tpl_code in templates.items():
                    # Find matching workflow step(s) by template file reference
                    step_id = None
                    # Extract the generated step ID from the template filename.
                    import re as _re_for_tpl
                    m = _re_for_tpl.search(r"(cb_step_\d+)", tpl_file)
                    if m:
                        step_id = m.group(1)
                    ws = workflow_steps.get(step_id) if step_id else None
                    if ws:
                        desc = ws.get("description", "")
                        sub_ops = ws.get("sub_operations", [])
                        sub_ops_text = "\n".join(
                            f"    - [{so.get('op_type')}] {so.get('description')}"
                            for so in sub_ops
                        )
                        semantic_lines.append(
                            f"Template '{tpl_file}' (step {step_id}):\n"
                            f"  Cookbook description: {desc}\n"
                            f"  Required sub-operations:\n{sub_ops_text}"
                        )
                if semantic_lines:
                    semantic_section = (
                        "\nSEMANTIC CONTEXT (what each template should implement):\n"
                        + "\n".join(semantic_lines) + "\n"
                    )

            # Structured per-call diagnosis so the LLM knows exactly which
            # receiver/method could not be proven and why (the stringified ERRORS
            # alone do not carry receiver_type/effect/diagnosis fields).
            diagnosis_section = ""
            diag_entries = []
            for issue in rewrite_issues:
                if issue.get("issue_type") != "UnprovenReceiver":
                    continue
                diag_entries.append({
                    "template": issue.get("template_key", ""),
                    "receiver_expression": issue.get("receiver_expression", ""),
                    "receiver_type": issue.get("receiver_type", ""),
                    "method": issue.get("method", ""),
                    "diagnosis": issue.get("diagnosis", ""),
                    "effect": issue.get("effect", ""),
                })
            if diag_entries:
                diagnosis_section = (
                    "\nUNPROVEN CALL DIAGNOSIS (each entry names a call that could not "
                    "be proven; 'method_unproven' with a known receiver_type means the "
                    "method does NOT exist on that receiver type):\n"
                    + json.dumps(diag_entries, indent=2) + "\n"
                )

            # Proven-method inventory: the only methods known to exist on the
            # extension logic receiver. Same source the api-proof validator trusts,
            # enriched with signatures from logic_analysis when available.
            proven_targets_section = ""
            try:
                proven_names = list(
                    (self._workflow_metadata or {})
                    .get("extension_callable_inventory", {})
                    .get("logic_methods", [])
                ) or []
            except Exception:
                proven_names = []
            proven_methods = []
            if logic_analysis:
                for method in logic_analysis.get("methods", []) or []:
                    proven_methods.append({
                        "name": method.get("name", ""),
                        "parameters": method.get("parameters", []),
                        "state_reads": method.get("state_reads", []),
                        "state_writes": method.get("state_writes", []),
                    })
            if proven_methods or proven_names:
                proven_targets_section = (
                    "\nPROVEN TARGETS (the ONLY methods known to exist on the extension "
                    "logic receiver `logic`; never call or assume a method not listed):\n"
                    + json.dumps(proven_methods[:80] if proven_methods else proven_names, indent=2)
                    + "\n"
                )

            # Proven attribute/members on `logic` (for member_unproven diagnoses).
            proven_members_section = ""
            try:
                proven_members = list(
                    (self._workflow_metadata or {})
                    .get("extension_callable_inventory", {})
                    .get("logic_attributes", [])
                ) or []
            except Exception:
                proven_members = []
            if proven_members:
                proven_members_section = (
                    "\nPROVEN MEMBERS (the ONLY attributes/members known on `logic`; "
                    "`getParameterNode` returns the parameter node):\n"
                    + json.dumps(proven_members[:120], indent=2) + "\n"
                )

            prompt = textwrap.dedent(f"""\
The following code templates for the "{extension_name}" extension failed validation.
Please fix ALL errors while maintaining the template format (use {{placeholder}} for dynamic values, {{{{ }}}} for literal braces).

ERRORS:
{chr(10).join(f'- {e}' for e in errors)}
{source_section}
{diagnosis_section}
{proven_targets_section}
{proven_members_section}
{semantic_section}
REPAIR RULES FOR UNPROVEN CALLS:
- You may call a method on the `logic` receiver ONLY if its name appears in PROVEN TARGETS. A method not listed does not exist on the logic class (it may belong to the Widget class or not exist at all).
- To repair a "method_unproven" call you MUST do exactly ONE of: (a) REMOVE the call if it sits in a defensive guard/fallback (e.g. `if hasattr(...)`, `try/except AttributeError`) and is not required by the step's semantic context; (b) REPLACE it with a PROVEN TARGET method that achieves the step's stated effect; (c) RESTRUCTURE so the unprovable call is both unreachable and unnecessary.
- A "member_unproven" issue means an ATTRIBUTE access `logic.<name>` references a member that does NOT exist on the logic class. Replace it with a PROVEN MEMBER/TARGET that yields the intended object — most often the access should be the method call `logic.getParameterNode()` (e.g. rewrite `logic.parameterNode.GetNodeReference(...)` to `logic.getParameterNode().GetNodeReference(...)`). Never access an attribute that is not in PROVEN MEMBERS.
- Do NOT satisfy a "method_unproven" issue by wrapping a REQUIRED call in a new `hasattr`/`try` guard — guarding a required step does not implement it.

CONSTRAINTS (CodeValidator):
- BLOCKED: os, subprocess, sys, socket, urllib, http, pickle, ctypes, mmap
- BLOCKED: eval, exec, compile, __import__, open, file, input, getattr, setattr, delattr
- BLOCKED: globals, locals, vars, dir
- ALLOWED: slicer, vtk, qt, ctk, numpy, SimpleITK, math, json, re, copy

TEMPLATES TO FIX:
{templates_text}

Return a JSON object with this structure:
{{
  "templates": {{
    "template_file_name.py.tpl": "fixed template content",
    ...
  }},
  "fix_description": "what was changed and why"
}}

Return ONLY the JSON, no markdown fences.""")

            response = self._call_llm(prompt, call_class="repair")
            fixed = self._parse_json_response(response)

            if not fixed or "templates" not in fixed:
                self.on_error(f"Revision attempt {attempt + 1}: LLM returned invalid response")
                continue

            # Save fixed templates — ensure .py.tpl files go into templates/ subdir
            for tpl_name, tpl_content in fixed["templates"].items():
                if tpl_name.endswith(".py.tpl") and not tpl_name.startswith("templates/"):
                    tpl_name = f"templates/{tpl_name}"
                if affected_templates and tpl_name not in affected_templates:
                    continue
                tpl_path = os.path.join(cli_dir, tpl_name)
                os.makedirs(os.path.dirname(tpl_path), exist_ok=True)
                templates[tpl_name] = tpl_content

            templates = self._sanitize_templates(templates)
            for tpl_name, tpl_content in templates.items():
                if not tpl_name.endswith(".py.tpl"):
                    continue
                tpl_path = os.path.join(cli_dir, tpl_name)
                os.makedirs(os.path.dirname(tpl_path), exist_ok=True)
                with open(tpl_path, "w", encoding="utf-8") as f:
                    f.write(tpl_content)

            # Re-validate
            if not self.code_validator:
                from ..CodeValidator import CodeValidator
                self.code_validator = CodeValidator()

            self._sync_template_contracts(
                templates,
                generators,
                workflow_graph=workflow_data,
            )
            with open(generators_path, "w", encoding="utf-8") as f:
                json.dump(generators, f, indent=2)
            if workflow_data is not None:
                with open(workflow_path, "w", encoding="utf-8") as f:
                    json.dump(workflow_data, f, indent=2)
            with open(workflow_metadata_path, "w", encoding="utf-8") as f:
                json.dump(self._workflow_metadata, f, indent=2)

            # Re-apply the core-module session drivers (see the other revise path).
            self._apply_module_session_drivers(
                templates,
                (workflow_data or {}).get("steps") if isinstance(workflow_data, dict) else None,
            )
            fresh_probe_result = self._stage7c_live_api_probe(templates)
            for tpl_name, tpl_content in templates.items():
                tpl_path = os.path.join(cli_dir, tpl_name)
                if tpl_name.endswith(".py.tpl") and os.path.isfile(tpl_path):
                    with open(tpl_path, "w", encoding="utf-8") as f:
                        f.write(tpl_content)

            self._sync_template_contracts(
                templates,
                generators,
                workflow_graph=workflow_data,
            )
            with open(generators_path, "w", encoding="utf-8") as f:
                json.dump(generators, f, indent=2)
            if workflow_data is not None:
                with open(workflow_path, "w", encoding="utf-8") as f:
                    json.dump(workflow_data, f, indent=2)
            with open(workflow_metadata_path, "w", encoding="utf-8") as f:
                json.dump(self._workflow_metadata, f, indent=2)

            validation_result = self._stage9_validate(
                templates, generators,
                logic_analysis=logic_analysis,
                api_probe_result=fresh_probe_result,
                extension_name=extension_name,
            )

            if validation_result.get("valid"):
                if isinstance(self._workflow_metadata, dict):
                    resolved_syntax_issues = self._workflow_metadata.pop(
                        "generate_syntax_issues", None
                    )
                    if resolved_syntax_issues:
                        self._workflow_metadata["resolved_generate_syntax_issues"] = (
                            resolved_syntax_issues
                        )
                    self._workflow_metadata["revision_validation_status"] = "passed"
                    self._workflow_metadata.setdefault("verify_repair", {})[
                        "used_outer_revision"
                    ] = True

                manifest["manifest_version"] = 3
                manifest["pipeline_version"] = PIPELINE_VERSION
                self._finalize_package_validation_state(
                    manifest, validation_result,
                    templates=templates, generators=generators,
                )
                with open(manifest_path, "w", encoding="utf-8") as f:
                    json.dump(manifest, f, indent=2)
                if os.path.isfile(workflow_metadata_path):
                    with open(workflow_metadata_path, "w", encoding="utf-8") as f:
                        json.dump(self._workflow_metadata, f, indent=2)

                prompt_fragment = self._build_revision_prompt_fragment(
                    extension_name, tool_schemas, generators
                )
                with open(
                    os.path.join(cli_dir, "prompt_fragment.md"),
                    "w",
                    encoding="utf-8",
                ) as f:
                    f.write(prompt_fragment)

                # Append to generation log
                log_path = os.path.join(cli_dir, "generation_log.json")
                log_entries = []
                if os.path.isfile(log_path):
                    with open(log_path, "r", encoding="utf-8") as f:
                        log_entries = json.load(f)
                log_entries.append({
                    "attempt": len(log_entries) + 1,
                    "timestamp": datetime.now().isoformat(),
                    "phase": "verify_repair",
                    "trigger": "validation_failure",
                    "error": "; ".join(errors),
                    "fix": fixed.get("fix_description", ""),
                    "api_probe_result": fresh_probe_result,
                    "validation_result": validation_result,
                })
                with open(log_path, "w", encoding="utf-8") as f:
                    json.dump(log_entries, f, indent=2)

                from ..ExtensionCLILoader import invalidate_cache
                invalidate_cache()

                result["success"] = True
                result["validation_result"] = validation_result
                return result

            self._finalize_package_validation_state(
                manifest, validation_result,
                templates=templates, generators=generators,
            )
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)
            if os.path.isfile(workflow_metadata_path):
                with open(workflow_metadata_path, "w", encoding="utf-8") as f:
                    json.dump(self._workflow_metadata, f, indent=2)
            log_path = os.path.join(cli_dir, "generation_log.json")
            log_entries = []
            if os.path.isfile(log_path):
                try:
                    with open(log_path, "r", encoding="utf-8") as f:
                        log_entries = json.load(f)
                except Exception:
                    log_entries = []
            log_entries.append({
                "attempt": len(log_entries) + 1,
                "timestamp": datetime.now().isoformat(),
                "phase": "verify_repair",
                "trigger": "validation_failure",
                "status": "validation_failed",
                "error": "; ".join(errors),
                "fix": fixed.get("fix_description", ""),
                "api_probe_result": fresh_probe_result,
                "validation_result": validation_result,
            })
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(log_entries, f, indent=2)
            errors = validation_result.get("errors", [])

        self._finalize_package_validation_state(manifest, {"valid": False})
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
        with open(
            os.path.join(cli_dir, "prompt_fragment.md"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(
                f"### {extension_name}\n\n"
                "Revision failed validation. This CLI package is saved only "
                "for debugging and is not loaded as a runtime tool.\n"
            )

        result["error"] = f"Revision failed after {max_attempts} attempts"
        return result

    # ================================================================
