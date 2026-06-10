from .common import *


class AnalyzerApiProbeMixin:
    @staticmethod
    def _build_var_to_expr_map(code: str) -> Dict[str, str]:
        """Map local variables to the expressions that create them.

        This preserves calls, unlike the old chain extractor.  For example:
            lm = slicer.app.layoutManager()
            lm.setLayout(...)
        is probed as `hasattr(slicer.app.layoutManager(), "setLayout")`.
        """
        import ast as _ast
        var_map: Dict[str, str] = {}
        try:
            tree = _ast.parse(code)
        except (SyntaxError, IndentationError):
            return var_map

        for node in tree.body:
            if not isinstance(node, _ast.Assign):
                continue
            if len(node.targets) != 1 or not isinstance(node.targets[0], _ast.Name):
                continue
            try:
                expr = _ast.unparse(node.value)
            except Exception:
                continue
            var_map[node.targets[0].id] = expr
        return var_map

    @staticmethod
    def _expand_probe_expr(expr: str, var_map: Dict[str, str]) -> str:
        """Inline simple variable assignments inside a receiver expression."""
        import ast as _ast

        class _ReplaceNames(_ast.NodeTransformer):
            def __init__(self):
                self.changed = False

            def visit_Name(self, node):
                if isinstance(node.ctx, _ast.Load) and node.id in var_map:
                    replacement = var_map[node.id]
                    try:
                        repl_node = _ast.parse(f"({replacement})", mode="eval").body
                    except SyntaxError:
                        return node
                    self.changed = True
                    return _ast.copy_location(repl_node, node)
                return node

        expanded = expr
        for _ in range(5):
            try:
                tree = _ast.parse(expanded, mode="eval")
            except SyntaxError:
                return expanded
            replacer = _ReplaceNames()
            tree = replacer.visit(tree)
            _ast.fix_missing_locations(tree)
            if not replacer.changed:
                return expanded
            try:
                new_expanded = _ast.unparse(tree.body)
            except Exception:
                return expanded
            if new_expanded == expanded:
                return expanded
            expanded = new_expanded
        return expanded

    @staticmethod
    def _expr_starts_with_api_root(expr: str) -> bool:
        return bool(_re.match(r'^\s*\(*\s*(slicer|vtk|qt|ctk)\b', expr))

    @staticmethod
    def _make_probe_receiver_safe(expr: str) -> str:
        """Avoid scene mutations while probing receiver objects."""
        import ast as _ast

        class _SafeReceiverCalls(_ast.NodeTransformer):
            def visit_Call(self, node):
                node = self.generic_visit(node)
                if (
                    isinstance(node.func, _ast.Attribute)
                    and node.func.attr == "AddNewNodeByClass"
                    and len(node.args) >= 1
                ):
                    node.func.attr = "CreateNodeByClass"
                    node.args = node.args[:1]
                    node.keywords = []
                return node

        try:
            tree = _ast.parse(expr, mode="eval")
            tree = _SafeReceiverCalls().visit(tree)
            _ast.fix_missing_locations(tree)
            return _ast.unparse(tree.body)
        except Exception:
            return expr

    @staticmethod
    def _extract_api_probe_specs(code: str) -> List[Dict[str, Any]]:
        """Extract receiver-level API probes from template code.

        Pass 1: Extract method call chains (e.g., obj.method()).
        Pass 2: Extract bare attribute accesses (e.g., slicer.vtkMRMLSliceNode.EnumValue).
        """
        import ast as _ast
        try:
            tree = _ast.parse(code)
        except (SyntaxError, IndentationError):
            return []

        var_map = ExtensionCLIAnalyzer._build_var_to_expr_map(code)
        specs: List[Dict[str, Any]] = []
        seen = set()

        # Pass 1: method calls (existing logic)
        for node in _ast.walk(tree):
            if not isinstance(node, _ast.Call) or not isinstance(node.func, _ast.Attribute):
                continue
            attr = node.func.attr
            try:
                receiver_expr = _ast.unparse(node.func.value)
            except Exception:
                continue
            receiver_expr = ExtensionCLIAnalyzer._expand_probe_expr(receiver_expr, var_map)
            receiver_expr = ExtensionCLIAnalyzer._make_probe_receiver_safe(receiver_expr)
            if ".GetDisplayNode()" in receiver_expr:
                continue
            if not ExtensionCLIAnalyzer._expr_starts_with_api_root(receiver_expr):
                continue
            try:
                recv_tree = _ast.parse(receiver_expr, mode="eval")
            except SyntaxError:
                continue
            unresolved = {
                n.id for n in _ast.walk(recv_tree)
                if isinstance(n, _ast.Name) and n.id not in {"slicer", "vtk", "qt", "ctk"}
            }
            if unresolved:
                continue

            chain = f"{receiver_expr}.{attr}"
            key = (receiver_expr, attr)
            if key in seen:
                continue
            seen.add(key)
            specs.append({
                "chain": chain,
                "receiver_expr": receiver_expr,
                "attr": attr,
                "lineno": getattr(node, "lineno", 0),
                "is_attribute": False,
            })

        # Pass 2: bare attribute accesses (e.g., slicer.vtkMRMLSliceNode.SpacingModeMatch2D)
        # These are ast.Attribute nodes that are NOT the func of a Call.
        call_func_ids = set()
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Call) and isinstance(node.func, _ast.Attribute):
                call_func_ids.add(id(node.func))

        for node in _ast.walk(tree):
            if not isinstance(node, _ast.Attribute):
                continue
            if id(node) in call_func_ids:
                continue
            attr = node.attr
            try:
                receiver_expr = _ast.unparse(node.value)
            except Exception:
                continue
            receiver_expr = ExtensionCLIAnalyzer._expand_probe_expr(receiver_expr, var_map)
            if not ExtensionCLIAnalyzer._expr_starts_with_api_root(receiver_expr):
                continue
            # Skip expressions with unresolved locals
            try:
                recv_tree = _ast.parse(receiver_expr, mode="eval")
            except SyntaxError:
                continue
            unresolved = {
                n.id for n in _ast.walk(recv_tree)
                if isinstance(n, _ast.Name) and n.id not in {"slicer", "vtk", "qt", "ctk"}
            }
            if unresolved:
                continue

            chain = f"{receiver_expr}.{attr}"
            key = (receiver_expr, attr)
            if key in seen:
                continue
            seen.add(key)
            specs.append({
                "chain": chain,
                "receiver_expr": receiver_expr,
                "attr": attr,
                "lineno": getattr(node, "lineno", 0),
                "is_attribute": True,
            })

        return specs

    @staticmethod
    def _extract_api_chains(code: str) -> List[str]:
        """Return display names for API calls extracted from template code."""
        return [p["chain"] for p in ExtensionCLIAnalyzer._extract_api_probe_specs(code)]

    def _get_template_purpose(self, tpl_key: str) -> str:
        """Look up a human-readable description for a template from the cookbook."""
        import re as _re
        m = _re.search(r"cb_step_(\d+)", tpl_key)
        if not m:
            return ""
        step_num = int(m.group(1))
        if not self._cookbook_def:
            return ""
        for step in self._cookbook_def.steps:
            if step.step_number == step_num:
                return step.description
        return ""

    @staticmethod
    def _generate_probes(api_specs: List[Dict[str, Any]]) -> List[Dict]:
        """Generate micro-probes that evaluate actual receiver objects.

        For method calls: check hasattr and return available methods.
        For attribute accesses (enums, constants): try to resolve and return
        all public attributes on failure.
        """
        probes = []
        seen = set()
        for spec in api_specs:
            receiver_expr = spec.get("receiver_expr", "")
            attr = spec.get("attr", "")
            is_attr = spec.get("is_attribute", False)
            if not receiver_expr or not attr:
                continue
            key = f"{receiver_expr}.{attr}"
            if key in seen:
                continue
            seen.add(key)

            if is_attr:
                # Attribute access probe: resolve the attribute and catch errors
                probe_code = (
                    f"try:\n"
                    f"    _obj = {receiver_expr}\n"
                    f"    _val = getattr(_obj, '{attr}')\n"
                    f"    __result = {{'exists': True, 'type': type(_val).__name__, 'value_repr': repr(_val)[:80]}}\n"
                    f"except AttributeError as _e:\n"
                    f"    _all = [m for m in dir(_obj) if not m.startswith('_')][:40]\n"
                    f"    __result = {{'exists': False, 'error': str(_e), 'type': type(_obj).__name__, 'available_methods': _all, 'all_attrs': _all}}\n"
                    f"except Exception as _e:\n"
                    f"    __result = {{'error': f'{{type(_e).__name__}}: {{_e}}'}}"
                )
            else:
                # Method call probe: check hasattr and return available methods
                probe_code = (
                    f"try:\n"
                    f"    _obj = {receiver_expr}\n"
                    f"    _exists = _obj is not None and hasattr(_obj, '{attr}')\n"
                    f"    _available = []\n"
                    f"    if not _exists and _obj is not None:\n"
                    f"        _available = [m for m in dir(_obj) if not m.startswith('_')][:40]\n"
                    f"    _all_attrs = [m for m in dir(_obj) if not m.startswith('_')][:80] if _obj else []\n"
                    f"    __result = {{'exists': _exists, 'is_none': _obj is None, 'type': type(_obj).__name__, 'available_methods': _available, 'all_attrs': _all_attrs}}\n"
                    f"except Exception as _e:\n"
                    f"    __result = {{'error': f'{{type(_e).__name__}}: {{_e}}'}}"
                )
            probes.append({
                "chain": key,
                "receiver_expr": receiver_expr,
                "attr": attr,
                "probe_code": probe_code,
                "lineno": spec.get("lineno", 0),
            })

        return probes

    @staticmethod
    def _execute_probe(probe_code: str) -> Any:
        """Execute a probe snippet in Slicer's Python environment.

        Runs in the caller's thread.  Probes may instantiate temporary MRML
        nodes when evaluating receivers such as AddNewNodeByClass(...), so this
        method removes any newly added nodes before returning.
        """
        import slicer as _slicer_mod
        exec_globals = {
            "__builtins__": __builtins__,
            "slicer": _slicer_mod,
            "vtk": globals().get("vtk"),
            "qt": globals().get("qt"),
            "ctk": globals().get("ctk"),
        }

        def _scene_node_ids():
            ids = set()
            try:
                nodes = _slicer_mod.mrmlScene.GetNodes()
                for i in range(nodes.GetNumberOfItems()):
                    node = nodes.GetItemAsObject(i)
                    if node:
                        ids.add(node.GetID())
            except Exception:
                pass
            return ids

        before_ids = _scene_node_ids()
        try:
            exec(probe_code, exec_globals)
            return exec_globals.get("__result", "NO_RESULT")
        except Exception as e:
            return f"EXCEPTION: {e}"
        finally:
            try:
                after_ids = _scene_node_ids()
                for node_id in after_ids - before_ids:
                    node = _slicer_mod.mrmlScene.GetNodeByID(node_id)
                    if node:
                        _slicer_mod.mrmlScene.RemoveNode(node)
            except Exception:
                pass

    def _execute_live_probe(self, probe_code: str) -> Any:
        """Execute a live probe, using the UI-provided main-thread bridge if available."""
        if self._live_probe_executor:
            return self._live_probe_executor(probe_code)
        return self._execute_probe(probe_code)

    def _stage7c_live_api_probe(
        self, templates: Dict[str, str],
    ) -> Dict[str, Any]:
        """Probe generated templates against the live Slicer API.

        For each .py.tpl template, extracts `slicer.*` API calls and
        verifies that the attribute chain exists.  Returns a report of
        failures with available-alternative context for LLM revision.

        Returns:
            {"probed": int, "failures": [...], "revised": int}
        """
        try:
            import slicer as _slicer_mod  # noqa: F401
        except ImportError:
            logger.info(
                "[verify_repair] Slicer not available — skipping live API probe"
            )
            return {"probed": 0, "failures": [], "revised": 0}

        self.on_progress(
            "verify_repair", "Verify And Repair Templates",
            "Verifying template API calls against running Slicer..."
        )

        all_specs_by_template = {}
        syntax_skipped = []
        for key, code in templates.items():
            if not key.endswith(".py.tpl") or not code or not code.strip():
                continue
            sample_code = code.replace(
                "{vol_lookup}",
                "inputVolume = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode')"
            )
            sample_code = self._fill_remaining_placeholders(sample_code)
            try:
                ast.parse(sample_code)
            except SyntaxError as exc:
                syntax_skipped.append({"template": key, "error": str(exc)})
                continue
            specs = self._extract_api_probe_specs(sample_code)
            if specs:
                all_specs_by_template[key] = specs

        if not all_specs_by_template:
            return {
                "probed": 0,
                "failures": [],
                "revised": 0,
                "syntax_skipped": syntax_skipped,
            }

        # Collect all unique receiver probes
        all_specs = []
        seen_specs = set()
        for specs in all_specs_by_template.values():
            for spec in specs:
                key = (spec.get("receiver_expr", ""), spec.get("attr", ""))
                if key not in seen_specs:
                    seen_specs.add(key)
                    all_specs.append(spec)

        probes = self._generate_probes(all_specs)
        logger.info(
            "[verify_repair] Generated %d probes for %d API calls across %d templates",
            len(probes), len(all_specs), len(all_specs_by_template),
        )

        # Execute probes
        probe_results = {}
        for probe in probes:
            chain_key = probe["chain"]
            result = self._execute_live_probe(probe["probe_code"])
            probe_results[chain_key] = result

        # Analyze results — collect failures
        failures = []
        for chain_key, probe_result in probe_results.items():
            if isinstance(probe_result, dict):
                if probe_result.get("error"):
                    failures.append({
                        "chain": chain_key,
                        "error": probe_result["error"],
                    })
                elif not probe_result.get("exists"):
                    failures.append({
                        "chain": chain_key,
                        "receiver_type": probe_result.get("type"),
                        "receiver_is_none": probe_result.get("is_none"),
                        "available_methods": probe_result.get("available_methods", []),
                    })
            elif isinstance(probe_result, str) and probe_result.startswith("EXCEPTION:"):
                failures.append({
                    "chain": chain_key,
                    "error": probe_result,
                })

        if not failures:
            logger.info("[verify_repair] All %d API probes passed", len(probes))
            self.on_progress(
                "verify_repair", "Verify And Repair Templates",
                f"All {len(probes)} API probes passed"
            )
            return {
                "probed": len(probes),
                "failures": [],
                "revised": 0,
                "syntax_skipped": syntax_skipped,
            }

        # Log failures
        logger.warning(
            "[verify_repair] %d/%d API probes failed",
            len(failures), len(all_specs),
        )
        for f in failures:
            logger.warning("[verify_repair] FAILED: %s", f["chain"])

        # Map failures back to affected templates
        affected_templates = {}
        for tpl_key, specs in all_specs_by_template.items():
            for spec in specs:
                chain = spec.get("chain", "")
                for f in failures:
                    if chain == f["chain"] or chain.startswith(f["chain"] + "."):
                        affected_templates.setdefault(tpl_key, []).append(f)
                        break

        # Revise affected templates via LLM
        revised_count = 0
        unresolved_failures = []
        for tpl_key, tpl_failures in affected_templates.items():
            if tpl_key not in templates:
                continue
            original_code = templates[tpl_key]
            # Look up template purpose from stage_map for better LLM context
            purpose = self._get_template_purpose(tpl_key)
            revised = self._revise_template_for_api(
                tpl_key, original_code, tpl_failures,
                template_purpose=purpose,
            )
            if revised and revised != original_code:
                templates[tpl_key] = revised
                revised_count += 1
                logger.info(
                    "[verify_repair] Revised template '%s' for API failures",
                    tpl_key,
                )
            else:
                for failure in tpl_failures:
                    failure_with_template = dict(failure)
                    failure_with_template["template"] = tpl_key
                    unresolved_failures.append(failure_with_template)

        # Re-probe revised templates once without another LLM pass.  This
        # prevents a first repair from introducing a new invalid API that would
        # otherwise be reported as probe-passed because the original failure was
        # revised.
        if revised_count:
            final_specs_by_template = {}
            for key, code in templates.items():
                if not key.endswith(".py.tpl") or not code or not code.strip():
                    continue
                sample_code = self._fill_remaining_placeholders(
                    code.replace(
                        "{vol_lookup}",
                        "inputVolume = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode')",
                    )
                )
                try:
                    ast.parse(sample_code)
                except SyntaxError:
                    continue
                specs = self._extract_api_probe_specs(sample_code)
                if specs:
                    final_specs_by_template[key] = specs
            final_specs = []
            seen_final_specs = set()
            for specs in final_specs_by_template.values():
                for spec in specs:
                    key = (spec.get("receiver_expr", ""), spec.get("attr", ""))
                    if key not in seen_final_specs:
                        seen_final_specs.add(key)
                        final_specs.append(spec)
            final_probe_results = {}
            for probe in self._generate_probes(final_specs):
                final_probe_results[probe["chain"]] = self._execute_live_probe(probe["probe_code"])
            final_failures = []
            for chain_key, probe_result in final_probe_results.items():
                if isinstance(probe_result, dict):
                    if probe_result.get("error"):
                        final_failures.append({"chain": chain_key, "error": probe_result["error"]})
                    elif not probe_result.get("exists"):
                        final_failures.append({
                            "chain": chain_key,
                            "receiver_type": probe_result.get("type"),
                            "receiver_is_none": probe_result.get("is_none"),
                            "available_methods": probe_result.get("available_methods", []),
                        })
                elif isinstance(probe_result, str) and probe_result.startswith("EXCEPTION:"):
                    final_failures.append({"chain": chain_key, "error": probe_result})
            if final_failures:
                unresolved_failures = []
                for tpl_key, specs in final_specs_by_template.items():
                    for spec in specs:
                        chain = spec.get("chain", "")
                        for failure in final_failures:
                            if chain == failure["chain"] or chain.startswith(failure["chain"] + "."):
                                item = dict(failure)
                                item["template"] = tpl_key
                                unresolved_failures.append(item)
                                break

        self.on_progress(
            "verify_repair", "Verify And Repair Templates",
            f"Found {len(failures)} API issues, revised {revised_count} templates"
        )
        return {
            "probed": len(probes),
            "failures": failures,
            "revised": revised_count,
            "unresolved_failures": unresolved_failures,
            "syntax_skipped": syntax_skipped,
        }

    def _revise_template_for_api(
        self, template_key: str, code: str, failures: List[Dict],
        template_purpose: str = "",
    ) -> Optional[str]:
        """Ask the LLM to revise a template to fix API failures."""
        failure_descriptions = []
        for f in failures:
            chain = f.get("chain", "")
            failed_attr = chain.rsplit(".", 1)[-1] if "." in chain else chain
            desc = f"API call `{chain}` does NOT EXIST."
            if f.get("receiver_type"):
                desc += f" Receiver type: {f['receiver_type']}."
            if f.get("receiver_is_none"):
                desc += " Receiver evaluated to None."
            # Include all attributes (not just callables) for better LLM context
            all_attrs = f.get("all_attrs") or f.get("available_methods", [])
            if all_attrs and isinstance(all_attrs, list):
                desc += f"\n  All public attributes on the receiver: {all_attrs}"
                # Add close matches: attributes whose names contain parts of the failed attr
                close = [
                    a for a in all_attrs
                    if any(part in a.lower() for part in failed_attr.lower().split("_") if len(part) > 2)
                ]
                if close:
                    desc += f"\n  Close matches for '{failed_attr}': {close}"
            elif "error" in f:
                desc += f" Error: {f['error']}"
            failure_descriptions.append(desc)

        purpose_section = ""
        if template_purpose:
            purpose_section = f"\nTemplate purpose: {template_purpose}\n"

        prompt = textwrap.dedent(f"""\
            The following Python template for 3D Slicer has API errors detected
            by live probing against the running Slicer instance.

            Template file: {template_key}
            {purpose_section}
            API failures:
            {chr(10).join(f'- {fd}' for fd in failure_descriptions)}

            Current template code:
            ```python
            {code}
            ```

            Fix the template so it uses the correct Slicer API.
            Only fix the broken API calls. Do not change the logic or structure.

            When fixing attribute access errors (e.g., incorrect enum values),
            select from the "Close matches" list above. These are attributes on
            the actual receiver object whose names are similar to the failed attribute.

            IMPORTANT restrictions:
            - Do NOT use `os`, `sys`, `subprocess`, `socket`, `shutil`, `pathlib`.
            - Do NOT use `eval()`, `exec()`, `open()`, `getattr()` on user input.
            - Do NOT use `dir()`, `globals()`, `locals()`.
            - Use `try/except NameError` to check variable existence.
            - Return ONLY raw Python code. Do NOT wrap in markdown fences.
        """)

        try:
            for _attempt in range(2):
                response = self._call_llm(prompt)
                response = self._strip_markdown_fences(response) if response else None
                if not response:
                    break
                import ast as _ast
                try:
                    _ast.parse(response)
                    return response
                except (SyntaxError, IndentationError) as e:
                    if _attempt == 0:
                        prompt += (
                            f"\n\nYour previous output had a syntax error: {e}\n"
                            "Output ONLY the corrected Python code, no explanation."
                        )
                    else:
                        return response
        except Exception:
            logger.debug(
                "[verify_repair] LLM revision failed for %s", template_key,
                exc_info=True,
            )
        return None
