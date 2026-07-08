from .common import *


class AnalyzerApiProbeMixin:
    @staticmethod
    def _enrich_resolved_probe_specs(
        specs: List[Dict[str, Any]],
        probe_results: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Attach successful live receiver evidence to resolved probe specs."""
        enriched = []
        for spec in specs or []:
            item = dict(spec)
            result = probe_results.get(spec.get("chain", ""))
            if isinstance(result, dict) and result.get("exists") and not result.get("error"):
                item["method_exists"] = True
                item["live_receiver_type"] = result.get("type", "")
                if not item.get("receiver_type"):
                    item["receiver_type"] = result.get("type", "")
                item["evidence_source"] = "live_probe_success"
            enriched.append(item)
        return enriched

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
    def _slicer_class_from_expr(node) -> str:
        """Return a Slicer class name proven by an expression, if any."""
        import ast as _ast

        if not isinstance(node, _ast.Call):
            return ""

        func = node.func
        if (
            isinstance(func, _ast.Attribute)
            and func.attr == "SafeDownCast"
            and isinstance(func.value, _ast.Attribute)
            and isinstance(func.value.value, _ast.Name)
            and func.value.value.id == "slicer"
            and func.value.attr.startswith("vtkMRML")
        ):
            return func.value.attr

        if isinstance(func, _ast.Attribute) and node.args:
            class_arg = node.args[0]
            if isinstance(class_arg, _ast.Constant) and isinstance(class_arg.value, str):
                class_name = class_arg.value
                if class_name.startswith("vtkMRML") and func.attr in {
                    "CreateNodeByClass",
                    "AddNewNodeByClass",
                    "GetFirstNodeByClass",
                }:
                    return class_name

        if isinstance(func, _ast.Attribute):
            if func.attr == "mrmlSliceNode":
                return "vtkMRMLSliceNode"
            if func.attr == "mrmlViewNode":
                return "vtkMRMLViewNode"
            if func.attr == "GetDisplayNode":
                return "vtkMRMLDisplayNode"
        if isinstance(func, _ast.Name) and func.id == "resolve_interaction_node":
            for keyword in node.keywords:
                if (
                    keyword.arg == "expected_class"
                    and isinstance(keyword.value, _ast.Constant)
                    and isinstance(keyword.value.value, str)
                ):
                    return keyword.value.value

        return ""

    @staticmethod
    def _infer_probe_receiver_types(code: str) -> Dict[str, str]:
        """Infer local receiver variable classes from source-backed Slicer idioms.

        Covers single-node constructors/casts (``_slicer_class_from_expr``) plus
        the generic node-collection iteration idiom — ``for node in
        scene.GetNodesByClass('vtkMRML...')`` (directly or via an intermediate
        collection variable) — and simple ``x = y`` aliases that re-bind such a
        receiver. Keyed on the API shape, not on any specific extension/class.
        """
        import ast as _ast
        try:
            tree = _ast.parse(code)
        except (SyntaxError, IndentationError):
            return {}

        def _collection_element_class(call) -> str:
            if (
                isinstance(call, _ast.Call)
                and isinstance(call.func, _ast.Attribute)
                and call.func.attr in {
                    "getNodesByClass", "GetNodesByClass", "GetNodesByClassByName",
                }
                and call.args
                and isinstance(call.args[0], _ast.Constant)
                and isinstance(call.args[0].value, str)
                and call.args[0].value.startswith("vtkMRML")
            ):
                return call.args[0].value
            return ""

        inferred: Dict[str, str] = {}
        collections: Dict[str, str] = {}
        for node in _ast.walk(tree):
            if (
                isinstance(node, _ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], _ast.Name)
            ):
                target = node.targets[0].id
                class_name = ExtensionCLIAnalyzer._slicer_class_from_expr(node.value)
                if class_name:
                    inferred[target] = class_name
                else:
                    coll_cls = _collection_element_class(node.value)
                    if coll_cls:
                        collections[target] = coll_cls
            elif isinstance(node, _ast.For) and isinstance(node.target, _ast.Name):
                coll_cls = _collection_element_class(node.iter)
                if not coll_cls and isinstance(node.iter, _ast.Name):
                    coll_cls = collections.get(node.iter.id, "")
                if coll_cls:
                    inferred[node.target.id] = coll_cls

        # Propagate simple Name aliases (e.g. `sliceNode = node`) to a fixpoint.
        for _ in range(4):
            changed = False
            for node in _ast.walk(tree):
                if (
                    isinstance(node, _ast.Assign)
                    and len(node.targets) == 1
                    and isinstance(node.targets[0], _ast.Name)
                    and isinstance(node.value, _ast.Name)
                    and node.value.id in inferred
                    and inferred.get(node.targets[0].id) != inferred[node.value.id]
                ):
                    inferred[node.targets[0].id] = inferred[node.value.id]
                    changed = True
            if not changed:
                break
        return inferred

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
        receiver_types = ExtensionCLIAnalyzer._infer_probe_receiver_types(code)
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
            original_receiver_expr = receiver_expr
            if (
                isinstance(node.func.value, _ast.Name)
                and node.func.value.id in receiver_types
            ):
                class_name = receiver_types[node.func.value.id]
                class_receiver = f"slicer.{class_name}"
                chain = f"{receiver_expr}.{attr}"
                key = (chain, attr)
                if key not in seen:
                    seen.add(key)
                    specs.append({
                        "chain": chain,
                        "receiver_expr": class_receiver,
                        "original_receiver_expr": original_receiver_expr,
                        "expanded_receiver_expr": class_receiver,
                        "receiver_type": class_name,
                        "proof_kind": "class_type",
                        "attr": attr,
                        "lineno": getattr(node, "lineno", 0),
                        "is_attribute": False,
                    })
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
                "original_receiver_expr": original_receiver_expr,
                "expanded_receiver_expr": receiver_expr,
                "proof_kind": "live_instance",
                "attr": attr,
                "lineno": getattr(node, "lineno", 0),
                "is_attribute": False,
            })

        # Pass 2: bare attribute accesses (e.g., slicer.vtkMRMLSliceNode.SpacingModeMatch2D)
        # These are ast.Attribute nodes that are NOT the func of a Call.
        call_func_ids = set()
        attribute_value_ids = set()
        for node in _ast.walk(tree):
            if isinstance(node, _ast.Call) and isinstance(node.func, _ast.Attribute):
                call_func_ids.add(id(node.func))
            if isinstance(node, _ast.Attribute) and isinstance(node.value, _ast.Attribute):
                attribute_value_ids.add(id(node.value))

        for node in _ast.walk(tree):
            if not isinstance(node, _ast.Attribute):
                continue
            if id(node) in call_func_ids or id(node) in attribute_value_ids:
                continue
            attr = node.attr
            try:
                original_receiver_expr = _ast.unparse(node.value)
            except Exception:
                continue
            receiver_expr = ExtensionCLIAnalyzer._expand_probe_expr(
                original_receiver_expr, var_map
            )
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
                # Keep the literal call-site receiver so live evidence can be
                # aliased back to what the proof validator actually looks up.
                "original_receiver_expr": original_receiver_expr,
                "expanded_receiver_expr": receiver_expr,
                "proof_kind": "live_instance",
                "attr": attr,
                "lineno": getattr(node, "lineno", 0),
                "is_attribute": True,
            })

        return specs

    @staticmethod
    def _extract_unresolved_api_probe_specs(code: str) -> List[Dict[str, Any]]:
        """Return likely Slicer receiver calls that static probing cannot resolve."""
        import ast as _ast
        try:
            tree = _ast.parse(code)
        except (SyntaxError, IndentationError):
            return []

        var_map = ExtensionCLIAnalyzer._build_var_to_expr_map(code)
        receiver_types = ExtensionCLIAnalyzer._infer_probe_receiver_types(code)
        resolved_specs = ExtensionCLIAnalyzer._extract_api_probe_specs(code)
        resolved_keys = set()
        for spec in resolved_specs:
            attr = spec.get("attr", "")
            for key_name in ("receiver_expr", "original_receiver_expr", "expanded_receiver_expr"):
                receiver = spec.get(key_name, "")
                if receiver:
                    resolved_keys.add((receiver, attr))
        unresolved = []
        seen = set()
        receiver_name_re = _re.compile(
            r"(slice_?node|slice_?display|display_?node|view_?node|layout_?node)",
            _re.IGNORECASE,
        )
        method_re = _re.compile(
            r"^(Set|Get|Add|Remove|Update|Modified|Visibility|.*Visibility.*|.*Layout.*)",
        )
        for node in _ast.walk(tree):
            if not isinstance(node, _ast.Call) or not isinstance(node.func, _ast.Attribute):
                continue
            attr = node.func.attr
            try:
                receiver_expr = _ast.unparse(node.func.value)
            except Exception:
                continue
            if isinstance(node.func.value, _ast.Name) and node.func.value.id in receiver_types:
                continue
            expanded_receiver = ExtensionCLIAnalyzer._expand_probe_expr(receiver_expr, var_map)
            expanded_receiver = ExtensionCLIAnalyzer._make_probe_receiver_safe(expanded_receiver)
            if (expanded_receiver, attr) in resolved_keys or (receiver_expr, attr) in resolved_keys:
                continue
            if ExtensionCLIAnalyzer._expr_starts_with_api_root(expanded_receiver):
                try:
                    recv_tree = _ast.parse(expanded_receiver, mode="eval")
                except SyntaxError:
                    recv_tree = None
                if recv_tree is not None:
                    unresolved_names = {
                        n.id for n in _ast.walk(recv_tree)
                        if isinstance(n, _ast.Name)
                        and n.id not in {"slicer", "vtk", "qt", "ctk"}
                    }
                    if not unresolved_names:
                        continue
            elif ExtensionCLIAnalyzer._expr_starts_with_api_root(receiver_expr):
                continue
            if not method_re.match(attr):
                continue
            receiver_compact = receiver_expr.replace(".", "_")
            if not receiver_name_re.search(receiver_compact):
                continue
            chain = f"{receiver_expr}.{attr}"
            if chain in seen:
                continue
            seen.add(chain)
            unresolved.append({
                "chain": chain,
                "receiver_expr": receiver_expr,
                "expanded_receiver_expr": expanded_receiver,
                "attr": attr,
                "proof_kind": "unproven_receiver",
                "lineno": getattr(node, "lineno", 0),
                "unresolved_reason": "receiver expression is dynamic and could not be live-probed",
            })
        return unresolved

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
            key = spec.get("chain") or f"{receiver_expr}.{attr}"
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
                # Method call probe: check hasattr AND callability — Qt
                # wrappers expose Q_PROPERTYs as plain attributes, so an
                # existing-but-not-callable attribute at a CALL site is the
                # "'int' object is not callable" class of runtime failure.
                probe_code = (
                    f"try:\n"
                    f"    _obj = {receiver_expr}\n"
                    f"    _exists = _obj is not None and hasattr(_obj, '{attr}')\n"
                    f"    _callable = bool(_exists and callable(getattr(_obj, '{attr}')))\n"
                    f"    _available = []\n"
                    f"    if not _exists and _obj is not None:\n"
                    f"        _available = [m for m in dir(_obj) if not m.startswith('_')][:40]\n"
                    f"    _all_attrs = [m for m in dir(_obj) if not m.startswith('_')][:80] if _obj else []\n"
                    f"    __result = {{'exists': _exists, 'callable': _callable, 'is_none': _obj is None, 'type': type(_obj).__name__, 'available_methods': _available, 'all_attrs': _all_attrs}}\n"
                    f"except Exception as _e:\n"
                    f"    __result = {{'error': f'{{type(_e).__name__}}: {{_e}}'}}"
                )
            probes.append({
                "chain": key,
                "receiver_expr": receiver_expr,
                "original_receiver_expr": spec.get("original_receiver_expr", receiver_expr),
                "expanded_receiver_expr": spec.get("expanded_receiver_expr", receiver_expr),
                "receiver_type": spec.get("receiver_type", ""),
                "proof_kind": spec.get("proof_kind", "live_instance"),
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

    def _introspect_type_method(self, class_name: str, attr: str) -> Dict[str, Any]:
        """Ask the running Slicer whether instances of ``class_name`` expose ``attr``.

        This is the universal, source-agnostic method-existence oracle.  Given a
        receiver type that the proof layer already named (e.g.
        ``vtkMRMLScriptedModuleNode``) and a method name, it resolves the class
        from ``slicer``/``vtk``/``qt`` by name, constructs (or, failing that,
        queries) a transient instance, and reports ``hasattr``.  There are no
        per-class rules: any class the type graph can name can be checked.

        Returns a dict that always carries ``resolved``.  Only when
        ``resolved`` is True is ``method_exists`` meaningful — callers must NOT
        treat an unresolved class or a probe error as method-absent evidence.

        Results are memoised for the lifetime of the verify/repair run via
        ``self._introspection_cache`` (keyed by ``(class_name, attr)``).
        """
        if not class_name or not attr or class_name.startswith("live_instance"):
            return {"resolved": False, "reason": "missing_class_or_attr"}
        cache = getattr(self, "_introspection_cache", None)
        if cache is None:
            cache = {}
            self._introspection_cache = cache
        cache_key = (class_name, attr)
        if cache_key in cache:
            return cache[cache_key]

        # vtk/qt are not imported at module scope in this file, so the probe
        # imports them itself rather than relying on injected globals.
        probe_code = (
            "try:\n"
            "    import slicer as _slicer\n"
            "    try:\n"
            "        import vtk as _vtk\n"
            "    except Exception:\n"
            "        _vtk = None\n"
            "    try:\n"
            "        import qt as _qt\n"
            "    except Exception:\n"
            "        _qt = None\n"
            f"    _cls = getattr(_slicer, {class_name!r}, None)\n"
            f"    if _cls is None and _vtk is not None:\n"
            f"        _cls = getattr(_vtk, {class_name!r}, None)\n"
            f"    if _cls is None and _qt is not None:\n"
            f"        _cls = getattr(_qt, {class_name!r}, None)\n"
            "    if _cls is None:\n"
            "        __result = {'resolved': False, 'reason': 'class_not_found'}\n"
            "    else:\n"
            "        _inst = None\n"
            f"        if {class_name!r}.startswith('vtkMRML'):\n"
            "            try:\n"
            f"                _inst = _slicer.mrmlScene.CreateNodeByClass({class_name!r})\n"
            "            except Exception:\n"
            "                _inst = None\n"
            "        if _inst is None:\n"
            "            try:\n"
            "                _inst = _cls()\n"
            "            except Exception:\n"
            "                _inst = None\n"
            "        _target = _inst if _inst is not None else _cls\n"
            "        _all = [m for m in dir(_target) if not m.startswith('_')][:80]\n"
            "        __result = {\n"
            "            'resolved': True,\n"
            "            'instance': _inst is not None,\n"
            f"            'method_exists': hasattr(_target, {attr!r}),\n"
            "            'type': (type(_inst).__name__ if _inst is not None"
            " else getattr(_cls, '__name__', '')),\n"
            "            'all_attrs': _all,\n"
            "        }\n"
            "except Exception as _e:\n"
            "    __result = {'resolved': False, 'error': f'{type(_e).__name__}: {_e}'}"
        )
        result = self._execute_live_probe(probe_code)
        if not isinstance(result, dict):
            result = {"resolved": False, "error": str(result)}
        cache[cache_key] = result
        return result

    def _introspect_expr_method(self, receiver_expr: str, attr: str) -> Dict[str, Any]:
        """Ground-truth oracle for a runtime-root receiver EXPRESSION.

        The type graph names some receivers not by a class but by an opaque
        runtime-root chain string (e.g. ``slicer.mrmlScene``, ``slicer.app``,
        ``slicer.util``, ``slicer.modules.<x>``) — Slicer singletons whose
        concrete class is only knowable at runtime, so class-name introspection
        (``_introspect_type_method``) cannot resolve them.  This resolves the
        receiver EXPRESSION live and reports its real type and ``hasattr(attr)``:
        the same running-Slicer oracle, applied to an expression instead of a
        class name.

        Safe + generic: only a *pure attribute chain* rooted at
        ``slicer``/``vtk``/``qt``/``ctk`` is accepted (no calls, subscripts, or
        other side-effecting nodes), so evaluating the receiver mutates nothing
        and there are no per-singleton rules.  Returns a dict that always carries
        ``resolved``; ``method_exists`` is meaningful only when ``resolved`` is
        True — an unresolved receiver or probe error is NOT method-absent
        evidence.  Memoised via ``self._introspection_cache``.
        """
        import ast as _ast
        if not receiver_expr or not attr:
            return {"resolved": False, "reason": "missing_expr_or_attr"}
        try:
            node = _ast.parse(receiver_expr, mode="eval").body
        except SyntaxError:
            return {"resolved": False, "reason": "unparseable"}
        # Pure attribute chain only: nested Attribute* down to a Name root, with
        # no Call/Subscript/Starred anywhere (so the receiver has no side effect).
        for sub in _ast.walk(node):
            if isinstance(sub, (_ast.Call, _ast.Subscript, _ast.Starred)):
                return {"resolved": False, "reason": "not_pure_chain"}
        root = node
        while isinstance(root, _ast.Attribute):
            root = root.value
        if not (isinstance(root, _ast.Name) and root.id in {"slicer", "vtk", "qt", "ctk"}):
            return {"resolved": False, "reason": "not_runtime_root_chain"}

        cache = getattr(self, "_introspection_cache", None)
        if cache is None:
            cache = {}
            self._introspection_cache = cache
        cache_key = ("__expr__", receiver_expr, attr)
        if cache_key in cache:
            return cache[cache_key]

        probe_code = (
            "try:\n"
            "    import slicer\n"
            "    try:\n"
            "        import vtk\n"
            "    except Exception:\n"
            "        vtk = None\n"
            "    try:\n"
            "        import qt\n"
            "    except Exception:\n"
            "        qt = None\n"
            "    try:\n"
            "        import ctk\n"
            "    except Exception:\n"
            "        ctk = None\n"
            f"    _recv = {receiver_expr}\n"
            "    if _recv is None:\n"
            "        __result = {'resolved': False, 'reason': 'receiver_none'}\n"
            "    else:\n"
            "        __result = {'resolved': True, 'method_exists': hasattr(_recv, "
            f"{attr!r}), 'type': type(_recv).__name__}}\n"
            "except Exception as _e:\n"
            "    __result = {'resolved': False, 'error': f'{type(_e).__name__}: {_e}'}"
        )
        result = self._execute_live_probe(probe_code)
        if not isinstance(result, dict):
            result = {"resolved": False, "error": str(result)}
        cache[cache_key] = result
        return result

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
            return {
                "probed": 0,
                "failures": [],
                "revised": 0,
                "api_probe_coverage": {
                    "resolved": [],
                    "unresolved": [],
                    "skipped": [{"reason": "slicer_not_available"}],
                },
            }

        self.on_progress(
            "verify_repair", "Verify And Repair Templates",
            "Verifying template API calls against running Slicer..."
        )

        from .module_sessions import _SEG_SESSION_MARK
        all_specs_by_template = {}
        unresolved_dynamic_by_template = {}
        syntax_skipped = []
        for key, code in templates.items():
            if not key.endswith(".py.tpl") or not code or not code.strip():
                continue
            # Do NOT probe the DETERMINISTIC module-session templates
            # (`[Segment Editor session]`): their Slicer API is hand-verified, and
            # probing them against the EMPTY probe scene both WASTES TIME
            # (instantiates the Segment Editor widget and executes guarded receiver
            # chains on the main thread — a big part of the "Not Responding" freeze)
            # and yields FALSE "does not exist" failures on None receivers
            # (activeEffect() returns None) that the repair LLM then "fixes" by
            # stripping the required `.self()`. Skipping them avoids both.
            if isinstance(code, str) and _SEG_SESSION_MARK in code:
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
            unresolved_specs = self._extract_unresolved_api_probe_specs(sample_code)
            if unresolved_specs:
                unresolved_dynamic_by_template[key] = unresolved_specs

        if not all_specs_by_template and not unresolved_dynamic_by_template:
            return {
                "probed": 0,
                "failures": [],
                "revised": 0,
                "syntax_skipped": syntax_skipped,
                "unresolved_failures": [],
                "api_probe_coverage": {
                    "resolved": [],
                    "unresolved": [],
                    "skipped": syntax_skipped,
                },
            }

        # Collect all unique receiver probes
        all_specs = []
        seen_specs = set()
        for specs in all_specs_by_template.values():
            for spec in specs:
                # Keep the call-site receiver spelling in the key: two templates
                # may reach the same expanded chain via different spellings
                # (e.g. `layoutManager` vs `slicer.app.layoutManager()`), and the
                # validator looks evidence up by the literal call-site receiver,
                # so each spelling must survive to produce its own alias.
                key = (
                    spec.get("receiver_expr", ""),
                    spec.get("attr", ""),
                    spec.get("original_receiver_expr", ""),
                )
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
        probe_metadata = {}
        for probe in probes:
            chain_key = probe["chain"]
            probe_metadata[chain_key] = probe
            result = self._execute_live_probe(probe["probe_code"])
            probe_results[chain_key] = result
        resolved_specs = self._enrich_resolved_probe_specs(all_specs, probe_results)

        # Analyze results — collect failures
        failures = []
        for chain_key, probe_result in probe_results.items():
            probe_meta = probe_metadata.get(chain_key, {})
            if isinstance(probe_result, dict):
                if probe_result.get("error"):
                    failures.append({
                        "chain": chain_key,
                        "error": probe_result["error"],
                        "receiver_expr": probe_meta.get("receiver_expr", ""),
                        "original_receiver_expr": probe_meta.get("original_receiver_expr", ""),
                        "expanded_receiver_expr": probe_meta.get("expanded_receiver_expr", ""),
                        "attr": probe_meta.get("attr", ""),
                        "receiver_type": probe_meta.get("receiver_type", ""),
                        "proof_kind": probe_meta.get("proof_kind", ""),
                    })
                elif not probe_result.get("exists") and not probe_result.get("is_none"):
                    # NOTE: a chain whose receiver merely evaluated to ``None`` in
                    # the empty probe scene is NOT a real failure — it is absence of
                    # evidence, not evidence of absence. It is exactly the runtime-
                    # guarded ``if x is not None:`` case (e.g.
                    # ``_ses_eff = ...activeEffect(); if _ses_eff is not None:
                    # _ses_eff.self().onApply()`` — ``activeEffect()`` returns None
                    # with no active effect / empty scene, GetDisplayNode() before
                    # display nodes exist, GetNodeReference() before the ref is set).
                    # Flagging it makes the repair LLM "fix" a perfectly valid call
                    # (it stripped the required ``.self()`` off the Threshold effect
                    # apply). Only flag a genuinely-missing attribute on a REAL
                    # receiver; mirror the static prover's non-blocking treatment of
                    # an unproven receiver.
                    failures.append({
                        "chain": chain_key,
                        "receiver_type": probe_result.get("type"),
                        "expected_receiver_type": probe_meta.get("receiver_type", ""),
                        "receiver_expr": probe_meta.get("receiver_expr", ""),
                        "original_receiver_expr": probe_meta.get("original_receiver_expr", ""),
                        "expanded_receiver_expr": probe_meta.get("expanded_receiver_expr", ""),
                        "attr": probe_meta.get("attr", ""),
                        "proof_kind": probe_meta.get("proof_kind", ""),
                        "receiver_is_none": probe_result.get("is_none"),
                        "available_methods": probe_result.get("available_methods", []),
                    })
                elif "callable" in probe_result and not probe_result.get("callable"):
                    # The attribute exists but is NOT callable at a CALL site —
                    # a Qt property accessed as a method ('int' object is not
                    # callable at runtime). Loud at generation time instead.
                    failures.append({
                        "chain": chain_key,
                        "error": (
                            f"QtPropertyCalledAsMethod: '{chain_key}' resolves to a "
                            f"non-callable {probe_result.get('type', 'value')} — it is a "
                            "property; read it without parentheses or use the "
                            "equivalent MRML-node getter"
                        ),
                        "receiver_expr": probe_meta.get("receiver_expr", ""),
                        "original_receiver_expr": probe_meta.get("original_receiver_expr", ""),
                        "expanded_receiver_expr": probe_meta.get("expanded_receiver_expr", ""),
                        "attr": probe_meta.get("attr", ""),
                        "receiver_type": probe_result.get("type", ""),
                        "proof_kind": probe_meta.get("proof_kind", ""),
                    })
            elif isinstance(probe_result, str) and probe_result.startswith("EXCEPTION:"):
                failures.append({
                    "chain": chain_key,
                    "error": probe_result,
                    "receiver_expr": probe_meta.get("receiver_expr", ""),
                    "original_receiver_expr": probe_meta.get("original_receiver_expr", ""),
                    "expanded_receiver_expr": probe_meta.get("expanded_receiver_expr", ""),
                    "attr": probe_meta.get("attr", ""),
                    "receiver_type": probe_meta.get("receiver_type", ""),
                    "proof_kind": probe_meta.get("proof_kind", ""),
                })

        unresolved_failures = []
        for tpl_key, unresolved_specs in unresolved_dynamic_by_template.items():
            for spec in unresolved_specs:
                unresolved_failures.append({
                    "template": tpl_key,
                    "chain": spec.get("chain", "unknown API"),
                    "error": spec.get("unresolved_reason", "API receiver could not be resolved"),
                    "proof_kind": "unproven_receiver",
                    "receiver_expr": spec.get("receiver_expr", ""),
                    "expanded_receiver_expr": spec.get("expanded_receiver_expr", ""),
                    "lineno": spec.get("lineno", 0),
                })

        if not failures and not unresolved_failures:
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
                "api_probe_coverage": {
                    "resolved": resolved_specs,
                    "unresolved": [
                        {**spec, "template": tpl_key}
                        for tpl_key, specs in unresolved_dynamic_by_template.items()
                        for spec in specs
                    ],
                    "skipped": syntax_skipped,
                },
            }
        if not failures and unresolved_failures:
            logger.warning(
                "[verify_repair] %d dynamic API receivers could not be resolved",
                len(unresolved_failures),
            )
            self.on_progress(
                "verify_repair", "Verify And Repair Templates",
                f"Found {len(unresolved_failures)} unresolved dynamic API receiver(s)"
            )

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
        from .module_sessions import _SEG_SESSION_MARK
        for tpl_key, tpl_failures in affected_templates.items():
            if tpl_key not in templates:
                continue
            original_code = templates[tpl_key]
            # NEVER let the probe-repair LLM rewrite the DETERMINISTIC module-session
            # templates (marked `[Segment Editor session]`): their Slicer API is
            # hand-verified and correct, but the probe runs against an EMPTY scene
            # where runtime-guarded receivers like `activeEffect()` return None, so it
            # keeps reporting valid guarded calls (`activeEffect().self().onApply`,
            # `...widgetRepresentation().self().editor`) as "does not exist" and the
            # LLM strips the REQUIRED `.self()` → the Threshold effect apply silently
            # fails (empty Cranial_Segment → step-8 onLoadSkull crashes) on every
            # regen. The None-receiver guard above prevents most of this, but exempt
            # these deterministic templates outright so a probe never mangles them.
            if isinstance(original_code, str) and _SEG_SESSION_MARK in original_code:
                logger.info(
                    "[verify_repair] skip revise of deterministic session template %s",
                    tpl_key,
                )
                continue
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
                # Same exemption as the initial pass: never probe the deterministic
                # [Segment Editor session] templates.
                if isinstance(code, str) and _SEG_SESSION_MARK in code:
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
                    key = (
                        spec.get("receiver_expr", ""),
                        spec.get("attr", ""),
                        spec.get("original_receiver_expr", ""),
                    )
                    if key not in seen_final_specs:
                        seen_final_specs.add(key)
                        final_specs.append(spec)
            final_probe_results = {}
            final_probe_metadata = {}
            for probe in self._generate_probes(final_specs):
                final_probe_metadata[probe["chain"]] = probe
                final_probe_results[probe["chain"]] = self._execute_live_probe(probe["probe_code"])
            resolved_specs = self._enrich_resolved_probe_specs(
                final_specs, final_probe_results
            )
            final_failures = []
            for chain_key, probe_result in final_probe_results.items():
                probe_meta = final_probe_metadata.get(chain_key, {})
                if isinstance(probe_result, dict):
                    if probe_result.get("error"):
                        final_failures.append({
                            "chain": chain_key,
                            "error": probe_result["error"],
                            "receiver_expr": probe_meta.get("receiver_expr", ""),
                            "original_receiver_expr": probe_meta.get("original_receiver_expr", ""),
                            "expanded_receiver_expr": probe_meta.get("expanded_receiver_expr", ""),
                            "attr": probe_meta.get("attr", ""),
                            "receiver_type": probe_meta.get("receiver_type", ""),
                            "proof_kind": probe_meta.get("proof_kind", ""),
                        })
                    elif not probe_result.get("exists"):
                        final_failures.append({
                            "chain": chain_key,
                            "receiver_type": probe_result.get("type"),
                            "expected_receiver_type": probe_meta.get("receiver_type", ""),
                            "receiver_expr": probe_meta.get("receiver_expr", ""),
                            "original_receiver_expr": probe_meta.get("original_receiver_expr", ""),
                            "expanded_receiver_expr": probe_meta.get("expanded_receiver_expr", ""),
                            "attr": probe_meta.get("attr", ""),
                            "proof_kind": probe_meta.get("proof_kind", ""),
                            "receiver_is_none": probe_result.get("is_none"),
                            "available_methods": probe_result.get("available_methods", []),
                        })
                elif isinstance(probe_result, str) and probe_result.startswith("EXCEPTION:"):
                    final_failures.append({
                        "chain": chain_key,
                        "error": probe_result,
                        "receiver_expr": probe_meta.get("receiver_expr", ""),
                        "original_receiver_expr": probe_meta.get("original_receiver_expr", ""),
                        "expanded_receiver_expr": probe_meta.get("expanded_receiver_expr", ""),
                        "attr": probe_meta.get("attr", ""),
                        "receiver_type": probe_meta.get("receiver_type", ""),
                        "proof_kind": probe_meta.get("proof_kind", ""),
                    })
            if final_failures:
                unresolved_failures = []
                for tpl_key, specs in final_specs_by_template.items():
                    for spec in specs:
                        chain = spec.get("chain", "")
                        for failure in final_failures:
                            if chain == failure["chain"] or chain.startswith(failure["chain"] + "."):
                                item = dict(failure)
                                item["template"] = tpl_key
                                item["receiver_expr"] = spec.get("receiver_expr", "")
                                item["original_receiver_expr"] = spec.get(
                                    "original_receiver_expr", ""
                                )
                                item["expanded_receiver_expr"] = spec.get(
                                    "expanded_receiver_expr", ""
                                )
                                item["attr"] = spec.get("attr", item.get("attr", ""))
                                item["proof_kind"] = spec.get("proof_kind", "")
                                unresolved_failures.append(item)
                                break
            failures = final_failures

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
            "api_probe_coverage": {
                "resolved": resolved_specs,
                "unresolved": [
                    {**spec, "template": tpl_key}
                    for tpl_key, specs in unresolved_dynamic_by_template.items()
                    for spec in specs
                ],
                "skipped": syntax_skipped,
            },
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
                response = self._call_llm(prompt, call_class="grounding", attempt=_attempt)
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
