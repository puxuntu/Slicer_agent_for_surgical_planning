from .common import *
from .phases import PIPELINE_VERSION
from ..cli_artifacts import (
    debug_round_dir,
    next_repair_round_label,
    snapshot_package_version,
)


class AnalyzerLiveRevisionMixin:
    # ── Live-execution validation status values ──
    # A step's template is run for real in Slicer; the outcome is one of:
    LIVE_VALID = "live_valid"                       # executed clean (assertions passed)
    LIVE_FAILED_BUG = "failed_bug"                  # raised — a real template defect
    LIVE_SKIPPED_PRECONDITION = "skipped_precondition"  # needs scene state not present headless
    LIVE_SKIPPED_INTERACTION = "skipped_interaction"    # user_interaction step, cannot run headless
    LIVE_SKIPPED_NO_TEMPLATE = "skipped_no_template"    # step has no executable code template

    @staticmethod
    def _live_required_input_node_classes(gen: Dict) -> List[str]:
        """Node classes a step must read before it can run (generic, role-based).

        Reads the step's declared dataflow roles. A role is an INPUT requirement
        when it consumes an existing scene node — `extension_input` (produced by
        an upstream extension step) or `choice_input` with a concrete node_class
        (a node the user loaded/selected). Pure value choices (no node_class,
        e.g. a boolean toggle) impose no scene precondition. No per-extension
        rules — this is the cookbook dataflow contract.
        """
        required = []
        for role in gen.get("node_roles") or []:
            kind = role.get("role_kind") or ""
            node_class = (role.get("node_class") or "").strip()
            if node_class and kind in ("extension_input", "choice_input"):
                required.append(node_class)
        return sorted(set(required))

    @staticmethod
    def _live_step_order_key(gen: Dict):
        """Sort generators by cookbook step number (cb_step_N), not file glob."""
        step = (gen.get("param_signature") or {}).get("workflow_step", "") or ""
        m = _re.search(r"cb_step_(\d+)", step)
        return (int(m.group(1)) if m else 1_000_000, step)

    def live_validate_templates(
        self,
        cli_dir: str,
        executor,
        on_progress=None,
    ) -> Dict[str, Dict]:
        """Validate generated templates by EXECUTING them in live Slicer, in order.

        Unlike static checks (CodeValidator, hasattr api-probe) this actually runs
        each step's template through SafeExecutor, so runtime-only defects — a
        wrong read-back predicate that raises STATE_NOT_APPLIED, a Qt property
        invoked like a method ('int' object is not callable), an AttributeError —
        surface here instead of in the main agent at use time.

        Sequential best-effort (no per-step rollback): steps run in cookbook order
        on an accumulating scene, so step N sees the nodes and cross-stage
        variables that steps 1..N-1 created (SafeExecutor shares __main__'s
        namespace). One rollback boundary wraps the whole sequence — created nodes
        are removed and layout/module/interaction restored at the end, so the
        user's scene is left untouched.

        Precondition-aware: a step is SKIPPED (not failed) when it cannot run
        headless — a `user_interaction` step, or a step whose required input nodes
        (per its dataflow roles) are absent from the live scene because their
        producer was itself skipped or the user never loaded that data. This keeps
        false positives low while still exercising every precondition-free step.

        MUST be called on the Qt main thread (SafeExecutor needs slicer.mrmlScene).

        Returns:
            Dict mapping template key → {
                "live_valid": bool,        # True only for status == LIVE_VALID
                "status": str,             # one of the LIVE_* constants
                "error": str or None,
                "traceback": str,
                "output": str,
                "execution_time": float,
                "step_id": str,
                "operation_type": str,
            }
        """
        import slicer  # main-thread only; imported lazily so module import is headless-safe

        generators = self._live_load_generators(cli_dir)
        if not generators:
            return {}
        generators = sorted(generators, key=self._live_step_order_key)

        # ── Capture scene state before the whole sequence (single rollback boundary) ──
        _pre_layout = None
        _pre_module = None
        _pre_interaction_node_mode = None
        _node_ids_before = set()
        try:
            lm = slicer.app.layoutManager()
            if lm:
                _pre_layout = lm.layout
        except Exception:
            pass
        try:
            _pre_module = slicer.util.selectedModule()
        except Exception:
            pass
        try:
            interactionNode = slicer.mrmlScene.GetNodeByID(
                "vtkMRMLInteractionNodeSingleton"
            )
            if interactionNode:
                _pre_interaction_node_mode = interactionNode.GetCurrentInteractionMode()
        except Exception:
            pass
        # Full pre-sequence node-state snapshot. Live execution of slicer_op steps
        # mutates VIEW/DISPLAY state (slice visibility, slice intersections, FOV
        # match, view filters) that is NOT a node add/remove and so is NOT covered
        # by the layout/module/interaction restore — that gap was leaving residue
        # in the user's viewport. Copy every node's state into an off-scene twin so
        # the exact prior state is restored, leaving the scene byte-for-byte
        # unchanged. vtkMRMLNode.Copy is metadata-level (it does not deep-copy
        # volume voxels), so this is cheap even for large scenes.
        _node_state_snapshot = {}
        try:
            for i in range(slicer.mrmlScene.GetNumberOfNodes()):
                node = slicer.mrmlScene.GetNthNode(i)
                if not node or not node.GetID():
                    continue
                _node_ids_before.add(node.GetID())
                try:
                    twin = slicer.mrmlScene.CreateNodeByClass(node.GetClassName())
                    if twin:
                        twin.Copy(node)
                        _node_state_snapshot[node.GetID()] = twin
                except Exception:
                    pass
        except Exception:
            pass

        # Suppress rendering for the whole validation so the user never sees the
        # transient layout/view changes; everything is reverted before resume.
        _render_paused = False
        try:
            if hasattr(slicer.app, "pauseRender"):
                slicer.app.pauseRender()
                _render_paused = True
        except Exception:
            _render_paused = False

        results: Dict[str, Dict] = {}
        total = len(generators)
        try:
            for idx, gen in enumerate(generators):
                step_id = (gen.get("param_signature") or {}).get("workflow_step", "") or ""
                op_type = gen.get("operation_type", "") or ""
                tpl_file = gen.get("template_file", "") or ""
                tpl_key = tpl_file or step_id

                record = self._live_validate_one_step(
                    cli_dir, gen, step_id, op_type, tpl_file, executor, slicer
                )
                results[tpl_key] = record
                if on_progress:
                    try:
                        on_progress(idx, total, tpl_key, record)
                    except Exception:
                        pass
        finally:
            # ── Restore scene state after the sequence (order matters) ──
            # 1) Remove nodes created during validation.
            if _node_ids_before:
                try:
                    to_remove = []
                    for i in range(slicer.mrmlScene.GetNumberOfNodes()):
                        node = slicer.mrmlScene.GetNthNode(i)
                        if node and node.GetID() and node.GetID() not in _node_ids_before:
                            to_remove.append(node)
                    for node in to_remove:
                        slicer.mrmlScene.RemoveNode(node)
                except Exception:
                    pass
            # 2) Revert every surviving original node to its snapshotted state
            #    (slice visibility, intersections, FOV match, view filters, …).
            if _node_state_snapshot:
                for node_id, twin in _node_state_snapshot.items():
                    try:
                        node = slicer.mrmlScene.GetNodeByID(node_id)
                        if node and twin:
                            node.Copy(twin)
                    except Exception:
                        pass
            # 3) Restore layout / module / interaction mode (app-global, not node state).
            try:
                if _pre_layout is not None:
                    lm = slicer.app.layoutManager()
                    if lm and lm.layout != _pre_layout:
                        lm.setLayout(_pre_layout)
            except Exception:
                pass
            try:
                if _pre_module:
                    if slicer.util.selectedModule() != _pre_module:
                        slicer.util.selectModule(_pre_module)
            except Exception:
                pass
            try:
                if _pre_interaction_node_mode is not None:
                    interactionNode = slicer.mrmlScene.GetNodeByID(
                        "vtkMRMLInteractionNodeSingleton"
                    )
                    if interactionNode:
                        interactionNode.SetCurrentInteractionMode(
                            _pre_interaction_node_mode
                        )
            except Exception:
                pass
            # 4) Resume rendering — the viewport repaints once, already reverted.
            try:
                if _render_paused and hasattr(slicer.app, "resumeRender"):
                    slicer.app.resumeRender()
            except Exception:
                pass

        return results

    @staticmethod
    def _live_load_generators(cli_dir: str) -> List[Dict]:
        """Load code_generators.json (the per-step template + dataflow record)."""
        gen_path = os.path.join(cli_dir, "code_generators.json")
        if not os.path.isfile(gen_path):
            return []
        try:
            with open(gen_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception:
            logger.debug("live_validate: failed to load code_generators.json", exc_info=True)
            return []

    def _live_validate_one_step(
        self, cli_dir, gen, step_id, op_type, tpl_file, executor, slicer,
    ) -> Dict:
        """Classify and (when runnable) execute one step's template live."""
        base = {
            "live_valid": False,
            "status": self.LIVE_SKIPPED_NO_TEMPLATE,
            "error": None,
            "traceback": "",
            "output": "",
            "execution_time": 0,
            "step_id": step_id,
            "operation_type": op_type,
            "template_key": tpl_file or step_id,
        }

        # user_interaction steps perform human 3D actions — never runnable headless.
        if op_type == "user_interaction":
            base["status"] = self.LIVE_SKIPPED_INTERACTION
            return base

        # Steps with no executable code template (e.g. pure user_choice param sets).
        if not tpl_file:
            base["status"] = self.LIVE_SKIPPED_NO_TEMPLATE
            return base

        tpl_path = os.path.join(cli_dir, tpl_file)
        if not os.path.isfile(tpl_path):
            base["status"] = self.LIVE_SKIPPED_NO_TEMPLATE
            base["error"] = "template file not found"
            return base

        # Precondition gate (generic, dataflow-role driven).
        required = self._live_required_input_node_classes(gen)
        # extension_op steps almost always read parameter-node references to
        # user-loaded data; when none of the required inputs are present (the
        # common case in a clean generation scene) the step is a precondition
        # skip, not a bug. A step with declared inputs runs only once they exist.
        if op_type == "extension_op" and not required:
            base["status"] = self.LIVE_SKIPPED_PRECONDITION
            base["error"] = "extension_op inputs (user-loaded data) not present in scene"
            return base
        missing = [
            nc for nc in required
            if slicer.mrmlScene.GetFirstNodeByClass(nc) is None
        ]
        if missing:
            base["status"] = self.LIVE_SKIPPED_PRECONDITION
            base["error"] = "required input nodes absent: " + ", ".join(missing)
            return base

        try:
            with open(tpl_path, "r", encoding="utf-8") as f:
                raw_code = f.read()
        except Exception as e:
            base["status"] = self.LIVE_SKIPPED_NO_TEMPLATE
            base["error"] = f"failed to read template: {e}"
            return base

        if not raw_code.strip():
            base["status"] = self.LIVE_VALID
            base["live_valid"] = True
            base["output"] = "(empty template)"
            return base

        filled_code = self._live_fill_template(raw_code)

        # Run on the accumulating scene (no per-step rollback on success). A step
        # that RAISES is auto-rolled-back by SafeExecutor (error path), so a
        # failed step does not pollute later steps; only clean steps persist.
        exec_result = executor.execute(filled_code, always_rollback=False)

        if exec_result.get("success"):
            base["status"] = self.LIVE_VALID
            base["live_valid"] = True
            base["output"] = (exec_result.get("output") or "")[:500]
            base["execution_time"] = exec_result.get("execution_time", 0)
            return base

        error = exec_result.get("error") or self._live_error_from_traceback(
            exec_result.get("traceback", "")
        ) or "unknown live execution error"
        tb = exec_result.get("traceback", "") or ""
        base["error"] = error
        base["traceback"] = tb
        base["output"] = (exec_result.get("output") or "")[:500]
        base["execution_time"] = exec_result.get("execution_time", 0)

        # The structural precondition gate only sees dependencies DECLARED in
        # node_roles. When the contract under-declares a step's inputs (e.g. a
        # slicer_op that looks a node up by class with no extension_input role),
        # the step runs and raises its own "needs upstream X" guard. That is a
        # genuinely-unmet precondition, NOT a template defect — classify it as a
        # skip so it neither blocks validation nor triggers a futile repair loop.
        # A read-back assertion (STATE_NOT_APPLIED) or a non-callable invocation
        # is always a real bug and is never reclassified.
        if self._is_runtime_precondition_failure(error, tb):
            base["status"] = self.LIVE_SKIPPED_PRECONDITION
            base["live_valid"] = False
            return base

        base["status"] = self.LIVE_FAILED_BUG
        return base

    def _live_fill_template(self, raw_code: str) -> str:
        """Fill template placeholders with safe defaults for a trial run."""
        # vol_lookup is the one structural placeholder that expands to a lookup
        # statement rather than a literal value (mirrors the generated runtime fill).
        filled = raw_code.replace(
            "{vol_lookup}",
            "inputVolume = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode')",
        )
        return self._fill_remaining_placeholders(filled)

    @staticmethod
    def _live_error_from_traceback(traceback_str: str) -> Optional[str]:
        """Extract the terminal error line from a traceback string."""
        if not traceback_str:
            return None
        for line in reversed(traceback_str.strip().split("\n")):
            line = line.strip()
            if line and not line.startswith("File ") and not line.startswith("Traceback"):
                return line
        return None

    # Runtime signatures that mean "a node/state this step needs was not present"
    # rather than "this template is defective". Keyed on the error SHAPE, not on
    # any extension. A template that raises its own "needs upstream X" guard, or
    # operates on a None returned by a failed node lookup, is a precondition skip.
    _PRECONDITION_ERROR_MARKERS = (
        "nonetype' object has no attribute",   # operated on a failed lookup (None)
        "not found",                            # explicit "<node> not found" guard
        "ensure",                               # "...Ensure cb_step_N completed..."
        "completed successfully",
        "could not find",
        "no such node",
        "does not exist in the scene",
        "is none",
        "no node",
    )

    @classmethod
    def _is_runtime_precondition_failure(cls, error: str, traceback_str: str) -> bool:
        """True when a live failure reflects an unmet input, not a template defect.

        Read-back assertions (STATE_NOT_APPLIED) and unresolved grounding sentinels
        (MISSING_EVIDENCE) are real defects and are never reclassified — they are
        excluded first so a precondition marker elsewhere in the text cannot mask
        them.
        """
        text = ((error or "") + "\n" + (traceback_str or "")).lower()
        if not text.strip():
            return False
        if "state_not_applied" in text or "missing_evidence" in text:
            return False
        return any(marker in text for marker in cls._PRECONDITION_ERROR_MARKERS)

    # ================================================================
    # Live-execution repair (runtime-only defects that pass static checks)
    # ================================================================

    def _live_failure_error_strings(self, live_failures: List[Dict]) -> List[str]:
        """Compose repair error strings from live-execution failure records.

        The 'Live execution failed:' marker makes _classify_validation_issue route
        these as template-class LiveExecutionError (never upstream). Each string
        carries the real error, a traceback tail, generic gotcha guidance, and
        shared live attribute evidence so the repair LLM can fix the exact failing
        call. The guidance is keyed on the error shape, not on any extension.
        """
        try:
            from ..ApiSanityChecker import live_attribute_evidence
        except Exception:
            def live_attribute_evidence(_t):
                return ""

        strings = []
        for rec in live_failures or []:
            if rec.get("status") != self.LIVE_FAILED_BUG:
                continue
            tpl_key = rec.get("template_key") or rec.get("step_id") or ""
            error = rec.get("error") or "unknown error"
            parts = [f"{tpl_key}: Live execution failed: {error}"]

            tb = rec.get("traceback") or ""
            if tb:
                tail = "\n".join(tb.strip().split("\n")[-4:])
                parts.append("Traceback (last lines):\n" + tail)

            lowered = error.lower()
            if "state_not_applied" in lowered:
                parts.append(
                    "STATE_NOT_APPLIED means the read-back assertion raised: the state "
                    "change most likely succeeded, but the verification getter/predicate "
                    "is wrong. Verify the correct getter for this property and the value "
                    "it actually returns, then compare against the right constant/enum — "
                    "do NOT assert a structured/description value against a short human "
                    "label."
                )
            if "object is not callable" in lowered:
                parts.append(
                    "A non-callable was invoked like a method (often a Qt Q_PROPERTY "
                    "exposed as a plain attribute in Python). Access the property WITHOUT "
                    "parentheses, or use the matching MRML getter method instead."
                )
            evidence = live_attribute_evidence(error)
            if evidence:
                parts.append(evidence)
            strings.append("\n".join(parts))
        return strings

    def repair_live_failures(
        self,
        extension_name: str,
        live_failures: List[Dict],
        source_path: Optional[str] = None,
    ) -> Dict:
        """Targeted template repair driven by live-execution failures.

        Each entry in `live_failures` is a record from `live_validate_templates`
        with status == LIVE_FAILED_BUG (carrying template_key, error, traceback,
        step_id). It seeds the SAME grounded verify/repair loop generation uses
        (`_verify_and_repair_templates`) with the real tracebacks: slicer_op crashes
        are re-grounded via KB + extension-source search, others get targeted repair,
        and the loop validates (api-proof + semantic) before returning. The caller
        re-runs live validation to confirm the fix.

        Returns {success, repaired: [changed keys], valid, fix_description}.
        """
        from ..ExtensionCLILoader import get_cli_base_dir, invalidate_cache

        extension_name = _validate_extension_name(extension_name)
        cli_dir = os.path.join(get_cli_base_dir(), extension_name)
        if not os.path.isdir(cli_dir):
            return {"success": False, "error": f"No CLI found for {extension_name}", "repaired": []}

        generators_path = os.path.join(cli_dir, "code_generators.json")
        try:
            with open(generators_path, "r", encoding="utf-8") as f:
                generators = json.load(f)
        except Exception:
            return {"success": False, "error": "code_generators.json unreadable", "repaired": []}

        workflow_metadata_path = os.path.join(cli_dir, "workflow_metadata.json")
        workflow_metadata = {}
        if os.path.isfile(workflow_metadata_path):
            try:
                with open(workflow_metadata_path, "r", encoding="utf-8") as f:
                    workflow_metadata = json.load(f)
            except Exception:
                workflow_metadata = {}
        self._workflow_metadata = workflow_metadata
        # Lets _reground_slicer_template register the extension's source as a
        # searchable `ext:` root even though the Repair path never parses the cookbook.
        self._repair_extension_name = extension_name
        if source_path:
            self._source_path = source_path
        # Isolated debug folder for this repair round (debug/repair_NNN/).
        repair_round = self._begin_repair_round(cli_dir, extension_name)

        manifest = {}
        manifest_path = os.path.join(cli_dir, "manifest.json")
        if os.path.isfile(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except Exception:
                manifest = {}
        workflow_path = os.path.join(
            cli_dir, manifest.get("workflow_graph_file", "workflow.json")
        )
        workflow_data = {"steps": []}
        if os.path.isfile(workflow_path):
            try:
                with open(workflow_path, "r", encoding="utf-8") as f:
                    workflow_data = json.load(f)
            except Exception:
                workflow_data = {"steps": []}

        # Read every template referenced by the generators.
        templates: Dict[str, str] = {}
        for gen in generators:
            for key in ("template_file", "pre_template_file", "post_template_file"):
                tpl_file = gen.get(key)
                if not tpl_file:
                    continue
                tpl_path = os.path.join(cli_dir, tpl_file)
                if os.path.isfile(tpl_path):
                    with open(tpl_path, "r", encoding="utf-8") as f:
                        templates[tpl_file] = f.read()

        error_strings = self._live_failure_error_strings(live_failures)
        if not error_strings:
            return {"success": False, "error": "no live failures to repair", "repaired": []}

        # Reconstruct first-round context and run the SAME grounded verify/repair
        # loop generation uses, seeded with the live failures. Compare against the
        # sanitized baseline so only TRUE repairs count as changed.
        logic_analysis = self._reconstruct_logic_analysis_from_metadata()
        baseline = self._sanitize_templates(dict(templates))
        repaired_templates, validation_result = self._verify_and_repair_templates(
            extension_name,
            templates,
            generators,
            logic_analysis,
            workflow_contract=workflow_data,
            workflow_graph=workflow_data,
            seed_errors=error_strings,
        )

        changed = [
            key for key in repaired_templates
            if repaired_templates.get(key) != baseline.get(key)
        ]
        for key in changed:
            tpl_path = os.path.join(cli_dir, key)
            os.makedirs(os.path.dirname(tpl_path), exist_ok=True)
            with open(tpl_path, "w", encoding="utf-8") as f:
                f.write(repaired_templates[key])

        # Keep template contracts / api evidence in sync with the rewritten code.
        try:
            self._sync_template_contracts(
                repaired_templates, generators, workflow_graph=workflow_data
            )
            with open(generators_path, "w", encoding="utf-8") as f:
                json.dump(generators, f, indent=2)
            with open(workflow_metadata_path, "w", encoding="utf-8") as f:
                json.dump(self._workflow_metadata, f, indent=2)
        except Exception:
            logger.debug("live-repair contract sync failed", exc_info=True)

        # Archive the now-current package as this repair round's version snapshot.
        if changed:
            snapshot_package_version(cli_dir, repair_round)

        invalidate_cache()
        live_repair_result = {
            "success": bool(changed),
            "repaired": changed,
            "valid": bool(validation_result.get("valid")),
            "fix_description": getattr(self, "_last_fix_description", ""),
        }
        self._flush_progress_artifacts(live_repair_result)
        return live_repair_result

    # ================================================================
    # Two-source repair: recorded runtime API errors + user behavior reports
    # ================================================================

    @staticmethod
    def _template_file_by_step(generators: List[Dict]) -> Dict[str, str]:
        """Map step_id -> template_file from the generators."""
        mapping = {}
        for gen in generators or []:
            sid = (gen.get("param_signature") or {}).get("workflow_step", "")
            tpl = gen.get("template_file")
            if sid and tpl:
                mapping[sid] = tpl
        return mapping

    def _function_error_strings(
        self, function_errors: List[str], generators: List[Dict], workflow_data: Dict,
    ) -> List[str]:
        """Map free-form user behavior reports to steps and format repair strings.

        The 'Function behavior error' marker routes these as FunctionBehaviorError.
        """
        descriptions = [d.strip() for d in (function_errors or []) if d and d.strip()]
        if not descriptions:
            return []
        tpl_by_step = self._template_file_by_step(generators)
        steps = workflow_data.get("steps", []) if isinstance(workflow_data, dict) else []
        strings = []
        for desc in descriptions:
            sid = self._map_description_to_step(desc, steps)
            tpl = tpl_by_step.get(sid, "")
            if not tpl:
                logger.info(
                    "Function error could not be mapped to a code template step: %s",
                    desc[:120],
                )
                continue
            step_desc = next(
                (s.get("description", "") for s in steps if s.get("step_id") == sid), ""
            )
            entry = f"{tpl}: Function behavior error (user-reported): {desc}"
            if step_desc:
                entry += f"\nContract step description: {step_desc}"
            strings.append(entry)
        return strings

    def _map_description_to_step(self, desc: str, steps: List[Dict]) -> str:
        """Resolve a user behavior report to a step_id (explicit ref, else LLM)."""
        valid_ids = {s.get("step_id", "") for s in steps if s.get("step_id")}
        m = (
            _re.search(r"cb[_\s]*step[_\s]*(\d+)", desc, _re.IGNORECASE)
            or _re.search(r"\bstep\s*(\d+)\b", desc, _re.IGNORECASE)
        )
        if m:
            sid = f"cb_step_{int(m.group(1))}"
            if sid in valid_ids:
                return sid
        return self._llm_map_description_to_step(desc, steps, valid_ids)

    def _llm_map_description_to_step(
        self, desc: str, steps: List[Dict], valid_ids: set,
    ) -> str:
        """One LLM call mapping a free-form report to the best-matching step_id."""
        if not valid_ids:
            return ""
        candidates = [
            {"step_id": s.get("step_id", ""), "description": s.get("description", "")}
            for s in steps if s.get("step_id")
        ]
        prompt = textwrap.dedent(f"""\
            A user reported that a step in a generated 3D Slicer workflow runs without
            error but behaves incorrectly. Map the report to the single best-matching
            step_id from the workflow.

            USER REPORT:
            {desc}

            WORKFLOW STEPS:
            {json.dumps(candidates, indent=2)}

            Return ONLY JSON: {{"step_id": "<one of the step_ids above>"}}.""")

        def _validate(candidate, raw):
            if isinstance(candidate, dict) and candidate.get("step_id") in valid_ids:
                return candidate, []
            return None, ["step_id must be one of the listed workflow step_ids"]

        try:
            result = self._call_llm_structured(
                prompt=prompt,
                validator=_validate,
                call_class="repair",
                max_attempts=2,
                failure_label="Function-error step mapping",
            )
            return result.get("step_id", "")
        except Exception:
            logger.debug("LLM step mapping failed", exc_info=True)
            return ""


    def _reconstruct_logic_analysis_from_metadata(self) -> Optional[Dict]:
        """Rebuild a minimal logic_analysis from persisted workflow_metadata.

        logic_analysis is not saved to the package, but workflow_metadata keeps the
        proven method inventory (`extension_callable_inventory.logic_methods`) and
        per-method effects (`method_parameter_effects`). This reconstructs real
        PROVEN TARGETS (names + reads/writes) for the repair with zero LLM cost, so
        the grounded loop isn't blind to the extension's actual methods. Returns
        None if no inventory is present.
        """
        meta = self._workflow_metadata if isinstance(self._workflow_metadata, dict) else {}
        method_names = list(
            (meta.get("extension_callable_inventory", {}) or {}).get("logic_methods", [])
            or []
        )
        if not method_names:
            return None
        effects = meta.get("method_parameter_effects", {}) or {}
        methods = []
        for name in method_names:
            eff = effects.get(name, {}) if isinstance(effects, dict) else {}
            methods.append({
                "name": name,
                "parameters": [],
                "state_reads": list((eff or {}).get("reads", []) or []),
                "state_writes": list((eff or {}).get("writes", []) or []),
            })
        return {"methods": methods}

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

    def repair_generated_cli(
        self,
        extension_name: str,
        function_errors: Optional[List[str]] = None,
        source_path: Optional[str] = None,
    ) -> Dict:
        """Repair an existing CLI from user-reported function/behavior errors.

        `function_errors` — free-form user descriptions of steps that run without
        error but behave wrong (FunctionBehaviorError issues, mapped to steps) — are
        fixed by the SAME grounded verify/repair loop that generation uses
        (`_verify_and_repair_templates`). Runtime API errors are NOT handled here:
        the runtime self-correction loop fixes those and writes the corrected code
        straight back into the step's template.

        slicer_op API/behavior issues are re-grounded via KB + extension-source
        search (`_reground_slicer_template` → SlicerOpGenerator); the loop validates
        (api-proof + semantic) before returning. `logic_analysis` is reconstructed
        from persisted metadata so PROVEN TARGETS are real. Writes the rewritten
        templates back and consumes the recorded runtime errors. Safe off the Qt
        main thread (no Slicer scene execution — the api-probe is non-mutating). The
        caller re-runs live validation afterward to confirm no crash was introduced.
        """
        from ..ExtensionCLILoader import get_cli_base_dir, invalidate_cache

        extension_name = _validate_extension_name(extension_name)
        cli_dir = os.path.join(get_cli_base_dir(), extension_name)
        if not os.path.isdir(cli_dir):
            return {"success": False, "error": f"No CLI found for {extension_name}", "repaired": []}

        generators_path = os.path.join(cli_dir, "code_generators.json")
        try:
            with open(generators_path, "r", encoding="utf-8") as f:
                generators = json.load(f)
        except Exception:
            return {"success": False, "error": "code_generators.json unreadable", "repaired": []}

        workflow_metadata_path = os.path.join(cli_dir, "workflow_metadata.json")
        workflow_metadata = {}
        if os.path.isfile(workflow_metadata_path):
            try:
                with open(workflow_metadata_path, "r", encoding="utf-8") as f:
                    workflow_metadata = json.load(f)
            except Exception:
                workflow_metadata = {}
        self._workflow_metadata = workflow_metadata
        # Lets _reground_slicer_template register the extension's source as a
        # searchable `ext:` root even though the Repair path never parses the cookbook.
        self._repair_extension_name = extension_name
        if source_path:
            self._source_path = source_path
        # Isolated debug folder for this repair round (debug/repair_NNN/).
        repair_round = self._begin_repair_round(cli_dir, extension_name)

        manifest = {}
        manifest_path = os.path.join(cli_dir, "manifest.json")
        if os.path.isfile(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
            except Exception:
                manifest = {}
        workflow_path = os.path.join(
            cli_dir, manifest.get("workflow_graph_file", "workflow.json")
        )
        workflow_data = {"steps": []}
        if os.path.isfile(workflow_path):
            try:
                with open(workflow_path, "r", encoding="utf-8") as f:
                    workflow_data = json.load(f)
            except Exception:
                workflow_data = {"steps": []}

        templates: Dict[str, str] = {}
        for gen in generators:
            for key in ("template_file", "pre_template_file", "post_template_file"):
                tpl_file = gen.get(key)
                if not tpl_file:
                    continue
                tpl_path = os.path.join(cli_dir, tpl_file)
                if os.path.isfile(tpl_path):
                    with open(tpl_path, "r", encoding="utf-8") as f:
                        templates[tpl_file] = f.read()

        function_error_strings = self._function_error_strings(
            function_errors, generators, workflow_data
        )
        all_errors = function_error_strings
        if not all_errors:
            return {
                "success": False,
                "error": "No function-error descriptions to repair.",
                "repaired": [],
                "function_error_count": 0,
            }

        # Reconstruct first-round generation context (proven methods + effects) so
        # the grounded loop has real PROVEN TARGETS even though logic_analysis was
        # never persisted.
        logic_analysis = self._reconstruct_logic_analysis_from_metadata()

        # Run the SAME grounded verify/repair loop generation uses, seeded with the
        # recorded API errors + function-error descriptions. Compare against the
        # sanitized baseline (the loop sanitizes its input) so only TRUE repairs
        # count as changed, not cosmetic cleanup.
        baseline = self._sanitize_templates(dict(templates))
        repaired_templates, validation_result = self._verify_and_repair_templates(
            extension_name,
            templates,
            generators,
            logic_analysis,
            workflow_contract=workflow_data,
            workflow_graph=workflow_data,
            seed_errors=all_errors,
        )

        changed = [
            key for key in repaired_templates
            if repaired_templates.get(key) != baseline.get(key)
        ]
        for key in changed:
            tpl_path = os.path.join(cli_dir, key)
            os.makedirs(os.path.dirname(tpl_path), exist_ok=True)
            with open(tpl_path, "w", encoding="utf-8") as f:
                f.write(repaired_templates[key])

        try:
            self._sync_template_contracts(
                repaired_templates, generators, workflow_graph=workflow_data
            )
            with open(generators_path, "w", encoding="utf-8") as f:
                json.dump(generators, f, indent=2)
            with open(workflow_metadata_path, "w", encoding="utf-8") as f:
                json.dump(self._workflow_metadata, f, indent=2)
        except Exception:
            logger.debug("repair_generated_cli contract sync failed", exc_info=True)

        # Archive the now-current package as this repair round's version snapshot.
        if changed:
            snapshot_package_version(cli_dir, repair_round)

        invalidate_cache()
        repair_result = {
            "success": bool(changed),
            "repaired": changed,
            "valid": bool(validation_result.get("valid")),
            "fix_description": getattr(self, "_last_fix_description", ""),
            "function_error_count": len(function_error_strings),
        }
        self._flush_progress_artifacts(repair_result)
        return repair_result

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
                tpl_files = []
                if gen.get("template_file"):
                    tpl_files.append(gen["template_file"])
                if gen.get("pre_template_file"):
                    tpl_files.append(gen["pre_template_file"])
                if gen.get("post_template_file"):
                    tpl_files.append(gen["post_template_file"])
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
