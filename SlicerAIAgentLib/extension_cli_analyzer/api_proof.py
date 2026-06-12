"""Typed call inventory and evidence-complete API proof validation."""

from __future__ import annotations

import ast
import builtins
import hashlib
import re
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from .common import _text_or_empty


_READ_PREFIXES = ("Get", "Is", "Has", "Can", "Find", "Lookup", "Compute", "Count")
_WRITE_PREFIXES = (
    "Set", "Add", "Remove", "Delete", "Clear", "Create", "Update", "Modified",
    "Invoke", "Start", "Stop", "Enable", "Disable", "Select", "Switch", "Apply",
    "Remember", "Store", "Cache",
)
_READ_ONLY_BUILTINS = {
    "all", "any", "bool", "dict", "enumerate", "float", "int", "isinstance",
    "len", "list", "max", "min", "next", "print", "range", "reversed", "set",
    "sorted", "str", "sum", "tuple", "type", "zip",
}
_PYTHON_METHOD_EFFECTS = {
    "add": "state_change",
    "append": "state_change",
    "clear": "state_change",
    "copy": "read_only",
    "endswith": "read_only",
    "extend": "state_change",
    "format": "read_only",
    "get": "read_only",
    "items": "read_only",
    "join": "read_only",
    "keys": "read_only",
    "lower": "read_only",
    "pop": "state_change",
    "remove": "state_change",
    "replace": "read_only",
    "setdefault": "state_change",
    "split": "read_only",
    "startswith": "read_only",
    "strip": "read_only",
    "update": "state_change",
    "upper": "read_only",
    "values": "read_only",
}


def _unparse(node: Optional[ast.AST]) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except Exception:
        return ""


def _confidence_rank(value: str) -> int:
    return {"none": 0, "low": 1, "medium": 2, "high": 3}.get(value, 0)


class TemplateApiAnalyzer:
    """Create one stable inventory entry for every executable call."""

    def analyze(self, template: str, code: str, enclosing_operation: str = "") -> Dict:
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            return {
                "template": template,
                "complete": False,
                "calls": [],
                "error": str(exc),
            }

        parents: Dict[int, ast.AST] = {}
        for parent in ast.walk(tree):
            for child in ast.iter_child_nodes(parent):
                parents[id(child)] = parent

        calls = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            receiver = node.func.value if isinstance(node.func, ast.Attribute) else None
            method = node.func.attr if isinstance(node.func, ast.Attribute) else _unparse(node.func)
            span = {
                "lineno": getattr(node, "lineno", 0),
                "col_offset": getattr(node, "col_offset", 0),
                "end_lineno": getattr(node, "end_lineno", getattr(node, "lineno", 0)),
                "end_col_offset": getattr(node, "end_col_offset", 0),
            }
            fingerprint = "|".join([
                template,
                str(span["lineno"]),
                str(span["col_offset"]),
                str(span["end_lineno"]),
                str(span["end_col_offset"]),
                _unparse(node.func),
            ])
            parent = parents.get(id(node))
            result_usage = "discarded"
            if isinstance(parent, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                result_usage = "assigned"
            elif not isinstance(parent, ast.Expr):
                result_usage = "consumed"
            calls.append({
                "call_id": hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:20],
                "template": template,
                "source_span": span,
                "call_expression": _unparse(node),
                "receiver_expression": _unparse(receiver),
                "method": method,
                "arguments": [_unparse(arg) for arg in node.args],
                "keyword_arguments": {
                    kw.arg or "**": _unparse(kw.value) for kw in node.keywords
                },
                "result_usage": result_usage,
                "enclosing_operation": enclosing_operation,
            })

        # Attribute-access obligations: a bare ``logic.<attr>`` member access on the
        # extension Logic receiver is invisible to the call inventory above, yet a
        # hallucinated member (e.g. ``logic.parameterNode`` instead of
        # ``logic.getParameterNode()``) raises AttributeError at runtime.  Emit a
        # proof obligation for each such access so the validator can deny unknown
        # members.  Restricted to the simple ``logic.<attr>`` receiver (the strict,
        # low-false-positive start); skip attributes that are the method being
        # called (handled as a call above).
        for node in ast.walk(tree):
            if not isinstance(node, ast.Attribute):
                continue
            if not (isinstance(node.value, ast.Name) and node.value.id == "logic"):
                continue
            parent = parents.get(id(node))
            if isinstance(parent, ast.Call) and parent.func is node:
                continue
            span = {
                "lineno": getattr(node, "lineno", 0),
                "col_offset": getattr(node, "col_offset", 0),
                "end_lineno": getattr(node, "end_lineno", getattr(node, "lineno", 0)),
                "end_col_offset": getattr(node, "end_col_offset", 0),
            }
            fingerprint = "|".join([
                template,
                str(span["lineno"]),
                str(span["col_offset"]),
                str(span["end_lineno"]),
                str(span["end_col_offset"]),
                "attr:" + _unparse(node),
            ])
            calls.append({
                "call_id": hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:20],
                "template": template,
                "source_span": span,
                "call_expression": _unparse(node),
                "receiver_expression": _unparse(node.value),
                "method": node.attr,
                "arguments": [],
                "keyword_arguments": {},
                "result_usage": "consumed",
                "enclosing_operation": enclosing_operation,
                "access_kind": "attribute",
            })

        calls.sort(key=lambda item: (
            item["source_span"]["lineno"],
            item["source_span"]["col_offset"],
            item["call_id"],
        ))
        return {"template": template, "complete": True, "calls": calls, "error": ""}


class TypeProvenanceGraph:
    """Infer receiver types through generic AST dataflow with provenance."""

    def __init__(
        self,
        code: str,
        workflow_roles: Optional[Dict[str, Dict]] = None,
        return_contracts: Optional[Dict[str, Any]] = None,
        logic_class_name: str = "",
    ):
        self.code = code
        self.workflow_roles = workflow_roles or {}
        self.return_contracts = return_contracts or {}
        self.logic_class_name = logic_class_name
        self.variables: Dict[str, List[Dict]] = {}
        self.collections: Dict[str, List[Dict]] = {}
        self.function_returns: Dict[str, List[Dict]] = {}
        self.function_effects: Dict[str, str] = {}
        self.imported_functions: Set[str] = set()
        self.imported_symbols: Set[str] = set()
        try:
            self.tree = ast.parse(code)
        except SyntaxError:
            self.tree = None
        if self.tree is not None:
            self._build()

    @staticmethod
    def _evidence(type_name: str, confidence: str, provenance: str) -> Dict:
        return {
            "type": type_name,
            "confidence": confidence,
            "provenance": provenance,
        }

    @staticmethod
    def _dedupe(items: Iterable[Dict]) -> List[Dict]:
        best: Dict[Tuple[str, str], Dict] = {}
        for item in items:
            key = (_text_or_empty(item.get("type")), _text_or_empty(item.get("provenance")))
            if not key[0]:
                continue
            if key not in best or _confidence_rank(item.get("confidence", "")) > _confidence_rank(
                best[key].get("confidence", "")
            ):
                best[key] = item
        return sorted(best.values(), key=lambda item: (
            -_confidence_rank(item.get("confidence", "")),
            item.get("type", ""),
            item.get("provenance", ""),
        ))

    def _assign(self, name: str, candidates: Iterable[Dict]) -> None:
        merged = list(self.variables.get(name, [])) + list(candidates)
        self.variables[name] = self._dedupe(merged)

    @staticmethod
    def _annotation_element_type(annotation: ast.AST) -> str:
        if not isinstance(annotation, ast.Subscript):
            return ""
        base = _unparse(annotation.value).split(".")[-1]
        if base not in {"List", "Sequence", "Iterable", "Collection", "Set", "Tuple"}:
            return ""
        slice_node = annotation.slice
        if isinstance(slice_node, ast.Tuple) and slice_node.elts:
            slice_node = slice_node.elts[0]
        return _unparse(slice_node)

    def _contract_return_types(self, receiver_types: List[Dict], method: str) -> List[Dict]:
        found = []
        for receiver in receiver_types:
            contract = self.return_contracts.get(receiver.get("type", ""), {}) or {}
            methods = contract.get("methods", contract) if isinstance(contract, dict) else {}
            method_contract = methods.get(method, {}) if isinstance(methods, dict) else {}
            return_type = (
                method_contract.get("return_type")
                if isinstance(method_contract, dict)
                else ""
            )
            if return_type:
                found.append(self._evidence(
                    return_type,
                    method_contract.get("confidence", "high"),
                    method_contract.get("source", "api_return_contract"),
                ))
        return found

    def infer_expr(self, node: Optional[ast.AST]) -> List[Dict]:
        if node is None:
            return []
        if isinstance(node, ast.Name):
            if node.id in self.variables:
                return self.variables[node.id]
            if node.id in {"slicer", "vtk", "qt", "ctk"}:
                return [self._evidence(node.id, "high", "runtime_module")]
            return []
        if isinstance(node, ast.Constant):
            return [self._evidence(type(node.value).__name__, "high", "python_literal")]
        if isinstance(node, ast.Dict):
            return [self._evidence("dict", "high", "python_literal")]
        if isinstance(node, ast.IfExp):
            return self._dedupe(self.infer_expr(node.body) + self.infer_expr(node.orelse))
        if isinstance(node, ast.Subscript):
            base = _unparse(node.value)
            if isinstance(node.value, ast.Name):
                return self.collections.get(node.value.id, [])
            return self.collections.get(base, [])
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            return [self._evidence(
                type(node).__name__.lower(), "high", "python_literal"
            )]
        if isinstance(node, ast.Attribute):
            chain = _unparse(node)
            if chain.startswith("slicer.vtk") or chain.startswith("vtk.vtk"):
                return [self._evidence(node.attr, "high", "wrapper_class_attribute")]
            if chain.startswith("slicer."):
                return [self._evidence(chain, "high", "slicer_runtime_root")]
            return []
        if not isinstance(node, ast.Call):
            return []

        func = node.func
        if isinstance(func, ast.Name):
            if func.id == "cast" and node.args:
                cast_type = _unparse(node.args[0])
                if cast_type:
                    return [self._evidence(cast_type, "medium", "typed_cast")]
            if hasattr(builtins, func.id):
                value = getattr(builtins, func.id)
                if isinstance(value, type):
                    return [self._evidence(func.id, "high", "python_builtin_type")]
            if func.id in self.imported_symbols and func.id[:1].isupper():
                return [self._evidence(func.id, "high", "imported_constructor")]
            if func.id == "resolve_interaction_node":
                for keyword in node.keywords:
                    if (
                        keyword.arg == "expected_class"
                        and isinstance(keyword.value, ast.Constant)
                        and isinstance(keyword.value.value, str)
                        and keyword.value.value
                    ):
                        return [self._evidence(
                            keyword.value.value, "high", "runtime_helper_contract"
                        )]
            return self.function_returns.get(func.id, [])
        if isinstance(func, ast.Attribute):
            if func.attr == "cast" and node.args:
                cast_type = _unparse(node.args[0])
                if cast_type:
                    return [self._evidence(cast_type, "medium", "typed_cast")]
            if (
                func.attr == "SafeDownCast"
                and isinstance(func.value, ast.Attribute)
                and isinstance(func.value.value, ast.Name)
                and func.value.value.id in {"slicer", "vtk"}
            ):
                return [self._evidence(func.value.attr, "high", "typed_safe_downcast")]
            if (
                isinstance(func.value, ast.Name)
                and func.value.id in {"slicer", "vtk", "qt", "ctk"}
                and (
                    func.attr[:1].isupper()
                    or func.attr.startswith(("vtk", "qSlicer", "qMRML"))
                )
            ):
                return [self._evidence(func.attr, "high", "direct_constructor")]
            if (
                isinstance(func.value, ast.Name)
                and func.value.id in self.imported_symbols
                and func.attr[:1].isupper()
            ):
                return [self._evidence(func.attr, "high", "imported_constructor")]
            if func.attr in {"CreateNodeByClass", "AddNewNodeByClass", "GetFirstNodeByClass"}:
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(
                    node.args[0].value, str
                ):
                    return [self._evidence(
                        node.args[0].value, "high", f"{func.attr}_class_argument"
                    )]
            if func.attr in {"GetSingletonNode", "GetNthNodeByClass"} and len(node.args) >= 2:
                class_arg = node.args[1]
                if isinstance(class_arg, ast.Constant) and isinstance(class_arg.value, str):
                    return [self._evidence(
                        class_arg.value, "high", f"{func.attr}_class_argument"
                    )]
            if func.attr == "getParameterNode":
                return [self._evidence(
                    "vtkMRMLScriptedModuleNode", "high", "extension_logic_contract"
                )]
            if (
                func.attr == "logic"
                and self.logic_class_name
                and _unparse(func.value).startswith("slicer.modules.")
            ):
                return [self._evidence(
                    self.logic_class_name, "high", "extension_module_logic_contract"
                )]
            if func.attr in {"GetNodeReference", "GetNodeReferenceID"} and node.args:
                role_arg = node.args[0]
                if isinstance(role_arg, ast.Constant) and isinstance(role_arg.value, str):
                    role = self.workflow_roles.get(role_arg.value, {}) or {}
                    node_class = role.get("node_class", "")
                    if node_class:
                        return [self._evidence(
                            node_class, role.get("confidence", "high"),
                            role.get("source", "workflow_role"),
                        )]
            if func.attr == "resolve_interaction_node":
                for keyword in node.keywords:
                    if (
                        keyword.arg == "expected_class"
                        and isinstance(keyword.value, ast.Constant)
                        and isinstance(keyword.value.value, str)
                        and keyword.value.value
                    ):
                        return [self._evidence(
                            keyword.value.value, "high", "runtime_helper_contract"
                        )]
            if func.attr == "GetDisplayNode":
                return [self._evidence(
                    "vtkMRMLDisplayNode", "medium", "slicer_return_contract"
                )]
            receiver_types = self.infer_expr(func.value)
            return self._dedupe(self._contract_return_types(receiver_types, func.attr))
        return []

    def _build(self) -> None:
        # Repeated passes propagate aliases and chained return contracts.
        for _ in range(4):
            before = repr(self.variables)
            for node in ast.walk(self.tree):
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        local_name = alias.asname or alias.name
                        self.imported_functions.add(local_name)
                        self.imported_symbols.add(local_name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imported_symbols.add(alias.asname or alias.name.split(".")[0])
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    returns = []
                    annotation = _unparse(node.returns)
                    if annotation:
                        returns.append(self._evidence(
                            annotation, "medium", "function_return_annotation"
                        ))
                    for child in ast.walk(node):
                        if isinstance(child, ast.Return):
                            returns.extend(self.infer_expr(child.value))
                    self.function_returns[node.name] = self._dedupe(returns)
                    called_methods = [
                        child.func.attr
                        for child in ast.walk(node)
                        if isinstance(child, ast.Call)
                        and isinstance(child.func, ast.Attribute)
                    ]
                    self.function_effects[node.name] = (
                        "state_change"
                        if any(method.startswith(_WRITE_PREFIXES) for method in called_methods)
                        else "read_only"
                    )
                if isinstance(node, ast.Assign):
                    candidates = self.infer_expr(node.value)
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self._assign(target.id, candidates)
                            if isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
                                self.collections[target.id] = self._dedupe(
                                    candidate
                                    for element in node.value.elts
                                    for candidate in self.infer_expr(element)
                                )
                            elif (
                                isinstance(node.value, ast.Call)
                                and isinstance(node.value.func, ast.Attribute)
                                and node.value.func.attr == "getNodesByClass"
                                and node.value.args
                                and isinstance(node.value.args[0], ast.Constant)
                                and isinstance(node.value.args[0].value, str)
                            ):
                                self.collections[target.id] = [self._evidence(
                                    node.value.args[0].value,
                                    "high",
                                    "typed_collection_api_contract",
                                )]
                elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                    annotation = _unparse(node.annotation)
                    candidates = self.infer_expr(node.value)
                    element_type = self._annotation_element_type(node.annotation)
                    if element_type:
                        self.collections[node.target.id] = [self._evidence(
                            element_type, "medium", "typed_collection_annotation"
                        )]
                    if annotation:
                        candidates.append(self._evidence(
                            annotation, "medium", "type_annotation"
                        ))
                    self._assign(node.target.id, candidates)
                elif isinstance(node, ast.For) and isinstance(node.target, ast.Name):
                    candidates = []
                    if isinstance(node.iter, ast.Name):
                        candidates = self.collections.get(node.iter.id, [])
                    else:
                        candidates = self.infer_expr(node.iter)
                    self._assign(node.target.id, candidates)
            if repr(self.variables) == before:
                break

    def receiver_candidates(self, expression: str) -> List[Dict]:
        try:
            node = ast.parse(expression, mode="eval").body
        except SyntaxError:
            return []
        return self._dedupe(self.infer_expr(node))


class ApiProofValidator:
    """Evaluate receiver, method-existence, and behavior proof obligations."""

    # Members inherited from ScriptedLoadableModuleLogic / VTKObservationMixin that
    # an extension Logic instance exposes but that are not visible in a subclass AST
    # scan.  Base-class-generic (not tied to any specific extension).
    _KNOWN_LOGIC_BASE_MEMBERS = frozenset({
        "getParameterNode", "getParameterNodeWrapper", "parent", "moduleName",
        "resourcePath", "cliRunSync", "delayDisplay",
        "addObserver", "removeObserver", "removeObservers", "hasObserver",
    })

    def __init__(
        self,
        type_contracts: Optional[Dict[str, Any]] = None,
        live_evidence: Optional[Dict[str, Dict]] = None,
        extension_methods: Optional[Set[str]] = None,
        extension_functions: Optional[Set[str]] = None,
        extension_attributes: Optional[Set[str]] = None,
        logic_class_name: str = "",
    ):
        self.type_contracts = type_contracts or {}
        self.live_evidence = live_evidence or {}
        self.extension_methods = extension_methods or set()
        self.extension_functions = extension_functions or set()
        self.extension_attributes = extension_attributes or set()
        self.logic_class_name = logic_class_name

    @staticmethod
    def effect_for_method(method: str, contract: Optional[Dict] = None) -> str:
        if isinstance(contract, dict) and contract.get("effect") in {
            "state_change", "read_only", "unknown"
        }:
            return contract["effect"]
        lowered = method.lower()
        if lowered.startswith(tuple(prefix.lower() for prefix in _READ_PREFIXES) + ("resolve",)):
            return "read_only"
        if lowered.startswith(tuple(prefix.lower() for prefix in _WRITE_PREFIXES)):
            return "state_change"
        tokens = {
            token.lower()
            for token in re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", method)
        }
        if tokens & {
            "set", "add", "remove", "delete", "clear", "create", "update",
            "modified", "invoke", "start", "stop", "enable", "disable",
            "select", "switch", "apply", "remember", "store", "cache",
            "make", "run", "process", "force", "write", "save",
        }:
            return "state_change"
        if method[:1].islower():
            return "read_only"
        return "unknown"

    def _method_contract(self, receiver_type: str, method: str) -> Optional[Dict]:
        contract = self.type_contracts.get(receiver_type, {}) or {}
        methods = contract.get("methods", contract) if isinstance(contract, dict) else {}
        value = methods.get(method) if isinstance(methods, dict) else None
        if value is True:
            return {"exists": True, "effect": "unknown", "source": "api_type_contract"}
        if value is False:
            return {"exists": False, "effect": "unknown", "source": "api_type_contract"}
        return value if isinstance(value, dict) else None

    def _validate_attribute_access(
        self,
        obligation: Dict,
        graph: TypeProvenanceGraph,
        attr: str,
        receiver_expr: str,
    ) -> Tuple[Dict, Optional[Dict]]:
        """Prove a bare attribute access (e.g. ``logic.parameterNode``) on a known
        extension Logic receiver.  An unknown member is itself the bug, so it blocks
        regardless of how the resulting value is later consumed (a downstream
        read-only call must not downgrade it)."""
        obligation["effect"] = "read_only"

        # Confidence gate: only judge attributes on a confidently-known extension
        # Logic receiver.  Anything else is left unproven-but-silent (out of scope).
        candidates = graph.receiver_candidates(receiver_expr) if receiver_expr else []
        high_types = {
            item.get("type") for item in candidates
            if _confidence_rank(item.get("confidence", "")) >= _confidence_rank("medium")
        }
        is_known_logic_receiver = (
            receiver_expr == "logic"
            or (self.logic_class_name and self.logic_class_name in high_types)
            or "extension_logic" in high_types
        )
        if not is_known_logic_receiver:
            obligation["proof_status"] = "proven"
            return obligation, None

        known_members = (
            set(self.extension_methods)
            | set(self.extension_attributes)
            | self._KNOWN_LOGIC_BASE_MEMBERS
        )
        if attr in known_members:
            obligation["proof_status"] = "proven"
            obligation["evidence"].append({
                "kind": "extension_source",
                "receiver_type": self.logic_class_name or "extension_logic",
                "method_exists": True,
                "effect": "read_only",
                "source": "extension_callable_inventory",
            })
            return obligation, None

        # Unknown member on a known extension Logic receiver → blocking.  Emitted as
        # an UnprovenApiCall with a dedicated `member_unproven` diagnosis so it flows
        # through the existing repair escalation (rewrite to a proven member).
        issue = {
            "issue_id": "api_proof_" + obligation["call_id"],
            "issue_type": "UnprovenApiCall",
            "severity": "error",
            "blocking": True,
            "template": obligation["template"],
            "call_id": obligation["call_id"],
            "source_span": obligation["source_span"],
            "diagnosis": "member_unproven",
            "receiver_expression": receiver_expr,
            "receiver_type": self.logic_class_name or "extension_logic",
            "method": attr,
            "method_exists": False,
            "effect": "read_only",
            "evidence_sources": ["extension_callable_inventory"],
            "minimal_repair": None,
        }
        return obligation, issue

    def validate_call(self, call: Dict, graph: TypeProvenanceGraph) -> Tuple[Dict, Optional[Dict]]:
        obligation = {
            **call,
            "receiver_type_candidates": [],
            "effect": "unknown",
            "proof_status": "unproven",
            "evidence": [],
            "repair_history": [],
        }
        method = call.get("method", "")
        receiver_expr = call.get("receiver_expression", "")

        if call.get("access_kind") == "attribute":
            return self._validate_attribute_access(obligation, graph, method, receiver_expr)

        if not receiver_expr and method in _READ_ONLY_BUILTINS:
            obligation["effect"] = "read_only"
            obligation["proof_status"] = "proven"
            obligation["evidence"].append({
                "kind": "python_builtin",
                "source": "python_runtime_contract",
                "method_exists": True,
                "effect": "read_only",
            })
            return obligation, None
        if not receiver_expr and hasattr(builtins, method):
            obligation["effect"] = "read_only"
            obligation["proof_status"] = "proven"
            obligation["evidence"].append({
                "kind": "python_builtin",
                "source": "python_runtime_contract",
                "method_exists": True,
                "effect": "read_only",
            })
            return obligation, None
        if not receiver_expr and method in graph.imported_functions:
            obligation["effect"] = self.effect_for_method(method)
            obligation["evidence"].append({
                "kind": "imported_callable",
                "source": "template_import",
                "method_exists": True,
                "effect": obligation["effect"],
            })
            if obligation["effect"] != "unknown":
                obligation["proof_status"] = "proven"
                return obligation, None
        if not receiver_expr and method in graph.function_effects:
            obligation["effect"] = graph.function_effects[method]
            obligation["proof_status"] = "proven"
            obligation["evidence"].append({
                "kind": "local_function",
                "source": "template_ast",
                "method_exists": True,
                "effect": obligation["effect"],
            })
            return obligation, None
        if (
            not receiver_expr
            and method in graph.imported_symbols
            and method[:1].isupper()
        ):
            obligation["effect"] = "read_only"
            obligation["proof_status"] = "proven"
            obligation["evidence"].append({
                "kind": "imported_constructor",
                "source": "template_import",
                "method_exists": True,
                "effect": "read_only",
            })
            return obligation, None

        candidates = graph.receiver_candidates(receiver_expr) if receiver_expr else []
        obligation["receiver_type_candidates"] = candidates
        if (
            method[:1].isupper()
            and receiver_expr in graph.imported_symbols
        ):
            obligation["effect"] = "read_only"
            obligation["proof_status"] = "proven"
            obligation["evidence"].extend(candidates)
            obligation["evidence"].append({
                "kind": "imported_constructor",
                "source": "template_import",
                "method_exists": True,
                "effect": "read_only",
            })
            return obligation, None
        if method in _PYTHON_METHOD_EFFECTS and not receiver_expr.startswith(
            ("slicer.", "vtk.", "qt.", "ctk.")
        ):
            obligation["effect"] = _PYTHON_METHOD_EFFECTS[method]
            obligation["proof_status"] = "proven"
            obligation["evidence"].extend(candidates)
            obligation["evidence"].append({
                "kind": "python_method",
                "source": "python_runtime_contract",
                "method_exists": True,
                "effect": obligation["effect"],
            })
            return obligation, None
        if (
            receiver_expr in {"slicer", "vtk", "qt", "ctk"}
            and (
                method[:1].isupper()
                or method.startswith(("vtk", "qSlicer", "qMRML"))
            )
        ):
            obligation["effect"] = "read_only"
            obligation["proof_status"] = "proven"
            obligation["evidence"].extend(candidates)
            obligation["evidence"].append({
                "kind": "wrapper_constructor",
                "source": "wrapper_class_attribute",
                "method_exists": True,
                "effect": "read_only",
            })
            return obligation, None
        high_types = {
            item.get("type") for item in candidates
            if _confidence_rank(item.get("confidence", "")) >= _confidence_rank("medium")
        }
        method_evidence = []
        invalid_evidence = []
        effects = set()
        for receiver_type in sorted(t for t in high_types if t):
            contract = self._method_contract(receiver_type, method)
            if contract:
                item = {
                    "kind": "type_contract",
                    "receiver_type": receiver_type,
                    "method_exists": contract.get("exists", True),
                    "effect": self.effect_for_method(method, contract),
                    "source": contract.get("source", "api_type_contract"),
                }
                (method_evidence if item["method_exists"] else invalid_evidence).append(item)
                effects.add(item["effect"])

        live = self.live_evidence.get(call.get("call_expression", "")) or self.live_evidence.get(
            f"{receiver_expr}.{method}", ""
        )
        if isinstance(live, dict):
            live_receiver_type = live.get("receiver_type", "")
            high_types.add(
                live_receiver_type or f"live_instance:{receiver_expr or method}"
            )
            item = {
                "kind": "live_probe",
                "receiver_type": live_receiver_type or "live_instance",
                "method_exists": bool(live.get("method_exists")),
                "effect": live.get("effect", self.effect_for_method(method)),
                "source": live.get("source", "live_probe"),
            }
            (method_evidence if item["method_exists"] else invalid_evidence).append(item)
            effects.add(item["effect"])

        if (
            method in self.extension_methods
            and (
                receiver_expr == "logic"
                or self.logic_class_name in high_types
            )
        ):
            method_evidence.append({
                "kind": "extension_source",
                "receiver_type": "extension_logic",
                "method_exists": True,
                "effect": "state_change",
                "source": "extension_callable_inventory",
            })
            high_types.add("extension_logic")
            effects.add("state_change")
        if not receiver_expr and method in self.extension_functions:
            method_evidence.append({
                "kind": "extension_source",
                "receiver_type": "extension_module",
                "method_exists": True,
                "effect": "state_change",
                "source": "extension_callable_inventory",
            })
            high_types.add("extension_module")
            effects.add("state_change")

        obligation["evidence"].extend(candidates)
        obligation["evidence"].extend(invalid_evidence + method_evidence)
        obligation["effect"] = (
            next(iter(effects)) if len(effects) == 1 else self.effect_for_method(method)
        )

        diagnosis = ""
        if invalid_evidence and not method_evidence:
            obligation["proof_status"] = "invalid"
            diagnosis = "method_unproven"
        elif not high_types:
            diagnosis = "receiver_type_unproven"
        elif not method_evidence:
            diagnosis = "method_unproven"
        elif obligation["effect"] == "unknown":
            diagnosis = "behavior_unproven"
        else:
            obligation["proof_status"] = "proven"

        if obligation["proof_status"] == "proven":
            return obligation, None

        blocking = obligation["proof_status"] == "invalid" or obligation["effect"] != "read_only"
        # `behavior_unproven` is only reachable once the receiver type AND method
        # existence are both proven (see the diagnosis chain above) — the method
        # is a real, resolved API and only its read/write effect could not be
        # name-classified.  That is a bookkeeping gap, not a proof or safety
        # failure (destructive-op safety lives in CodeValidator), so it must not
        # block.  Down-grade it to a non-blocking warning.
        #
        # `receiver_type_unproven` means NO receiver type could be resolved at all
        # (common for chained MRML/VTK accessors like
        # `node.GetMarkupsDisplayNode()` or `scene.GetNodesByClass(...)` whose
        # return types are not contracted, and which the live probe cannot resolve
        # against an empty scene).  Without a resolved type we have NO positive
        # evidence the method is invalid — it is a proof gap, not a proven error,
        # so it must not block either.  Calls that ARE provably wrong stay blocking:
        # `method_unproven`/`member_unproven` (receiver type known, member absent)
        # and `InvalidApiCall` (a live probe proved the method missing).
        if diagnosis in ("behavior_unproven", "receiver_type_unproven"):
            blocking = False
        issue = {
            "issue_id": "api_proof_" + obligation["call_id"],
            "issue_type": (
                "InvalidApiCall" if obligation["proof_status"] == "invalid"
                else "UnprovenApiCall"
            ),
            "severity": "error" if blocking else "warning",
            "blocking": blocking,
            "template": obligation["template"],
            "call_id": obligation["call_id"],
            "source_span": obligation["source_span"],
            "diagnosis": diagnosis,
            "receiver_expression": receiver_expr,
            "receiver_type": sorted(high_types)[0] if len(high_types) == 1 else "",
            "method": method,
            "method_exists": False if obligation["proof_status"] == "invalid" else None,
            "effect": obligation["effect"],
            "evidence_sources": sorted({
                _text_or_empty(item.get("source") or item.get("provenance"))
                for item in obligation["evidence"]
                if _text_or_empty(item.get("source") or item.get("provenance"))
            }),
            "minimal_repair": None,
        }
        return obligation, issue

    def validate_inventory(
        self,
        inventory: Dict,
        graph: TypeProvenanceGraph,
    ) -> Dict:
        obligations = []
        issues = []
        for call in inventory.get("calls", []):
            obligation, issue = self.validate_call(call, graph)
            obligations.append(obligation)
            if issue:
                issues.append(issue)
        return {"obligations": obligations, "issues": issues}


class ApiEvidenceAgent:
    """Return structured deterministic evidence before any repair is attempted."""

    @staticmethod
    def diagnose(issue: Dict) -> Dict:
        return {
            "diagnosis": issue.get("diagnosis", "behavior_unproven"),
            "receiver_type": issue.get("receiver_type", ""),
            "method_exists": issue.get("method_exists"),
            "effect": issue.get("effect", "unknown"),
            "evidence_sources": list(issue.get("evidence_sources", []) or []),
            "minimal_repair": None,
        }


class RepairCoordinator:
    """Track issue lineages and escalate strategies instead of retrying them.

    A *lineage* identifies the same semantic issue across validation cycles
    — (issue_type, step_id, normalized subject) — independent of message text
    or template content. When a lineage survives a validation cycle after a
    strategy was applied, that strategy is exhausted for the lineage and the
    next rung of its issue-class ladder becomes mandatory. This replaces the
    old exact-content-fingerprint dedup, which let the same strategy be
    retried indefinitely because every LLM rewrite changed the fingerprint.
    """

    # Generic per-issue-class escalation ladders (data, not per-error rules).
    # The final rung "upstream_request" hands the issue to the pipeline
    # engine for upstream phase re-entry.
    STRATEGY_LADDERS = {
        "template": [
            "targeted_template_repair",
            "contract_aware_template_repair",
            "upstream_request",
        ],
        "grounding": [
            "reground_slicer_op",
            "reground_broadened",
            "upstream_request",
        ],
        "runtime_api": [
            "gather_api_evidence",
            "contract_aware_template_repair",
            "upstream_request",
        ],
        "contract": ["upstream_request"],
        "dataflow": ["upstream_request"],
    }

    def __init__(self, history: Optional[List[Dict]] = None):
        self.history = list(history or [])

    @staticmethod
    def lineage_key(issue: Dict) -> str:
        """Semantic identity of an issue: type + step + offending subject."""
        subject = (
            issue.get("call_id")
            or ".".join(filter(None, [
                _text_or_empty(issue.get("receiver_expression")),
                _text_or_empty(issue.get("method")),
            ]))
            or issue.get("template_key", "")
        )
        return "|".join([
            _text_or_empty(issue.get("issue_type")),
            _text_or_empty(issue.get("step_id")),
            _text_or_empty(subject),
        ])

    def exhausted_rungs(self, lineage: str) -> set:
        return {
            item.get("strategy", "")
            for item in self.history
            if item.get("lineage") == lineage
            and item.get("outcome") in {"failed", "survived", "exhausted"}
        }

    def next_strategy(self, issue: Dict) -> Optional[str]:
        """Return the next untried ladder rung for this issue's lineage.

        The issue's classifier-chosen strategy anchors the starting rung:
        earlier rungs the classifier deliberately skipped are not revisited.
        Returns None when the ladder is exhausted (terminal diagnosis).
        """
        lineage = self.lineage_key(issue)
        ladder = list(self.STRATEGY_LADDERS.get(issue.get("issue_class", ""), []))
        default = issue.get("repair_strategy") or ""
        if default:
            if default in ladder:
                ladder = ladder[ladder.index(default):]
            else:
                ladder.insert(0, default)
        if not ladder:
            ladder = [default] if default else []
        tried = self.exhausted_rungs(lineage)
        for rung in ladder:
            if rung and rung not in tried:
                return rung
        return None

    def record_lineage(self, lineage: str, strategy: str, outcome: str) -> Dict:
        entry = {"lineage": lineage, "strategy": strategy, "outcome": outcome}
        self.history.append(entry)
        return entry

    @staticmethod
    def fingerprint(call_id: str, strategy: str, content_fingerprint: str = "") -> str:
        raw = "|".join([call_id, strategy, content_fingerprint])
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]

    def can_attempt(self, call_id: str, strategy: str, content_fingerprint: str = "") -> bool:
        fingerprint = self.fingerprint(call_id, strategy, content_fingerprint)
        return not any(
            item.get("fingerprint") == fingerprint and item.get("outcome") == "failed"
            for item in self.history
        )

    def record(
        self,
        call_id: str,
        strategy: str,
        outcome: str,
        content_fingerprint: str = "",
    ) -> Dict:
        entry = {
            "call_id": call_id,
            "strategy": strategy,
            "outcome": outcome,
            "fingerprint": self.fingerprint(call_id, strategy, content_fingerprint),
        }
        self.history.append(entry)
        return entry


class AnalyzerApiProofMixin:
    """Analyzer integration for inventory, proof validation, and coverage."""

    @staticmethod
    def _render_api_proof_issue(issue: Dict) -> str:
        span = issue.get("source_span", {}) or {}
        location = f"line {span.get('lineno', 0)}"
        return (
            f"{issue.get('issue_type')}: {issue.get('diagnosis')} for "
            f"'{issue.get('receiver_expression') + '.' if issue.get('receiver_expression') else ''}"
            f"{issue.get('method', '')}' ({location}, effect={issue.get('effect', 'unknown')})"
        )

    def _api_live_evidence(self, api_probe_result: Optional[Dict]) -> Dict[str, Dict]:
        result = {}
        probe = api_probe_result or {}
        failures = list(probe.get("failures", []) or []) + list(
            probe.get("unresolved_failures", []) or []
        )
        for failure in failures:
            chain = failure.get("chain", "")
            if failure.get("proof_kind") == "unproven_receiver":
                continue
            # A probe that could not evaluate its receiver (NameError on a local,
            # or a receiver that resolved to None) is NOT evidence that the method
            # is absent — only a resolved receiver object lacking the attribute is.
            # Treating un-runnable receivers as method-absent would falsely reject
            # valid APIs, so they are skipped here and stay "unproven" instead.
            if failure.get("error"):
                continue
            if failure.get("receiver_is_none"):
                continue
            method = failure.get("attr") or (chain.rsplit(".", 1)[-1] if chain else "")
            receiver_type = failure.get("receiver_type", "")
            if not receiver_type or receiver_type == "NoneType":
                receiver_type = failure.get("expected_receiver_type", "")
            evidence = {
                "method_exists": False,
                "receiver_type": receiver_type,
                "source": "live_probe_failure",
            }
            aliases = {
                chain,
                f"{failure.get('receiver_expr', '')}.{method}",
                f"{failure.get('original_receiver_expr', '')}.{method}",
                f"{failure.get('expanded_receiver_expr', '')}.{method}",
            }
            for alias in aliases:
                if alias and not alias.startswith("."):
                    result[alias] = evidence
        if probe.get("probed", 0):
            for spec in (probe.get("api_probe_coverage", {}) or {}).get("resolved", []) or []:
                chain = spec.get("chain", "")
                attr = spec.get("attr", "")
                evidence = {
                    "method_exists": spec.get("method_exists", True),
                    "receiver_type": (
                        spec.get("live_receiver_type")
                        or spec.get("receiver_type", "")
                    ),
                    "effect": ApiProofValidator.effect_for_method(attr),
                    "source": spec.get("evidence_source", "live_probe_success"),
                }
                aliases = {
                    chain,
                    f"{spec.get('receiver_expr', '')}.{attr}",
                    f"{spec.get('original_receiver_expr', '')}.{attr}",
                    f"{spec.get('expanded_receiver_expr', '')}.{attr}",
                }
                for alias in aliases:
                    if alias and not alias.startswith(".") and alias not in result:
                        result[alias] = evidence
        return result

    def _enrich_contracts_via_introspection(
        self,
        obligations: List[Dict],
        issues: List[Dict],
        type_contracts: Dict[str, Any],
    ) -> bool:
        """Prove method existence for type-known calls via live introspection.

        For each ``method_unproven`` issue whose receiver type was resolved with
        >= medium confidence, query the running Slicer for whether that type has
        the method and record the answer as a high-confidence ``type_contract``.
        Mutates ``type_contracts`` in place; returns True if anything was added.

        Invariants:
        - Only a class that actually resolves can mint evidence.  ``class_not_found``
          or a probe error writes NO contract, so the call stays unproven (still
          blocking) rather than being falsely accepted or falsely rejected.
        - A resolved class whose ``hasattr`` is False is written ``exists: False``,
          which the validator routes to a blocking ``InvalidApiCall``.
        """
        if not hasattr(self, "_introspect_type_method"):
            return False
        obligation_by_call = {
            obligation.get("call_id"): obligation for obligation in obligations
        }
        targets = set()
        for issue in issues:
            if issue.get("issue_type") != "UnprovenApiCall":
                continue
            if issue.get("diagnosis") != "method_unproven":
                continue
            method = _text_or_empty(issue.get("method"))
            if not method:
                continue
            candidate_types = []
            obligation = obligation_by_call.get(issue.get("call_id"))
            if obligation:
                for item in obligation.get("receiver_type_candidates", []) or []:
                    if _confidence_rank(item.get("confidence", "")) >= _confidence_rank("medium"):
                        receiver_type = _text_or_empty(item.get("type"))
                        if receiver_type and not receiver_type.startswith("live_instance"):
                            candidate_types.append(receiver_type)
            if not candidate_types and _text_or_empty(issue.get("receiver_type")):
                candidate_types.append(_text_or_empty(issue.get("receiver_type")))
            for receiver_type in candidate_types:
                targets.add((receiver_type, method))

        added = False
        for receiver_type, method in sorted(targets):
            existing = (type_contracts.get(receiver_type, {}) or {}).get("methods", {})
            if method in existing:
                continue
            result = self._introspect_type_method(receiver_type, method)
            if not isinstance(result, dict) or not result.get("resolved"):
                continue
            receiver_contract = type_contracts.setdefault(receiver_type, {})
            methods = receiver_contract.setdefault("methods", {})
            methods[method] = {
                "exists": bool(result.get("method_exists")),
                "effect": ApiProofValidator.effect_for_method(method),
                "source": "live_introspection",
                "confidence": "high",
            }
            added = True
        return added

    def _build_api_proof_report(
        self,
        templates: Dict[str, str],
        generators: Optional[List[Dict]] = None,
        api_probe_result: Optional[Dict] = None,
    ) -> Dict:
        metadata = self._workflow_metadata if isinstance(self._workflow_metadata, dict) else {}
        roles = metadata.get("parameter_bindings", {}) or {}
        type_contracts = dict(metadata.get("api_type_contracts", {}) or {})
        probe = api_probe_result or {}
        if probe.get("probed", 0):
            for spec in (probe.get("api_probe_coverage", {}) or {}).get("resolved", []) or []:
                receiver_type = _text_or_empty(spec.get("receiver_type"))
                method = _text_or_empty(spec.get("attr"))
                if not receiver_type or receiver_type == "NoneType" or not method:
                    continue
                receiver_contract = type_contracts.setdefault(receiver_type, {})
                methods = receiver_contract.setdefault("methods", {})
                methods[method] = {
                    "exists": True,
                    "effect": ApiProofValidator.effect_for_method(method),
                    "source": "live_probe_success",
                    "confidence": "high",
                }
            for failure in probe.get("failures", []) or []:
                # Only a resolved receiver that lacks the attribute is evidence of
                # an absent method; an un-runnable receiver or a None receiver is not.
                if failure.get("error") or failure.get("receiver_is_none"):
                    continue
                receiver_type = _text_or_empty(
                    failure.get("expected_receiver_type") or failure.get("receiver_type")
                )
                chain = _text_or_empty(failure.get("chain"))
                method = chain.rsplit(".", 1)[-1] if chain else ""
                if not receiver_type or receiver_type == "NoneType" or not method:
                    continue
                receiver_contract = type_contracts.setdefault(receiver_type, {})
                methods = receiver_contract.setdefault("methods", {})
                methods[method] = {
                    "exists": False,
                    "effect": ApiProofValidator.effect_for_method(method),
                    "source": "live_probe_failure",
                    "confidence": "high",
                }
        if isinstance(self._workflow_metadata, dict):
            self._workflow_metadata["api_type_contracts"] = type_contracts
        inventory_analyzer = TemplateApiAnalyzer()
        live_evidence = self._api_live_evidence(api_probe_result)
        callable_inventory = metadata.get("extension_callable_inventory", {}) or {}
        extension_methods = set(callable_inventory.get("logic_methods", []) or [])
        extension_attributes = set(callable_inventory.get("logic_attributes", []) or [])
        extension_functions = (
            set(callable_inventory.get("module_functions", []) or [])
            | {_text_or_empty(metadata.get("logic_class_name"))}
        ) - {""}
        logic_class_name = _text_or_empty(metadata.get("logic_class_name"))

        generator_by_template = {}
        for gen in generators or []:
            for key in ("template_file", "pre_template_file", "post_template_file"):
                if gen.get(key):
                    generator_by_template[gen[key]] = gen

        # Build the call inventory once; templates with an incomplete inventory
        # are reported up front and excluded from proof passes.
        inventories = {}
        prepared = []  # (template, code, inventory)
        inventory_issues = []
        coverage_complete = True
        for template, raw_code in templates.items():
            if not template.endswith((".py.tpl", ".py")):
                continue
            code = self._fill_remaining_placeholders(raw_code.replace(
                "{vol_lookup}",
                "inputVolume = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode')",
            ))
            gen = generator_by_template.get(template, {})
            operation = (
                (gen.get("param_signature") or {}).get("workflow_step")
                or gen.get("operation_type")
                or ""
            )
            inventory = inventory_analyzer.analyze(template, code, operation)
            inventories[template] = inventory
            if not inventory.get("complete"):
                coverage_complete = False
                inventory_issues.append({
                    "issue_id": "api_inventory_" + hashlib.sha256(
                        template.encode("utf-8")
                    ).hexdigest()[:20],
                    "issue_type": "IncompleteCallInventory",
                    "severity": "error",
                    "blocking": True,
                    "template": template,
                    "diagnosis": "inventory_incomplete",
                    "effect": "unknown",
                    "evidence_sources": [],
                    "minimal_repair": None,
                })
                continue
            prepared.append((template, code, inventory))

        def _run_proof_pass(contracts):
            validator = ApiProofValidator(
                type_contracts=contracts,
                live_evidence=live_evidence,
                extension_methods=extension_methods,
                extension_functions=extension_functions,
                extension_attributes=extension_attributes,
                logic_class_name=logic_class_name,
            )
            pass_obligations = []
            pass_issues = []
            for template, code, inventory in prepared:
                graph = TypeProvenanceGraph(
                    code,
                    workflow_roles=roles,
                    return_contracts=contracts,
                    logic_class_name=logic_class_name,
                )
                proof = validator.validate_inventory(inventory, graph)
                pass_obligations.extend(proof["obligations"])
                pass_issues.extend(proof["issues"])
            return pass_obligations, pass_issues

        obligations, issues = _run_proof_pass(type_contracts)

        # Universal live-introspection enrichment: for every method that the
        # static layer could not prove but whose receiver TYPE is already known,
        # ask the running Slicer directly whether the type exposes the method.
        # This replaces partial keyword/idiom evidence with a single ground-truth
        # oracle and is applied uniformly to every template.
        if self._enrich_contracts_via_introspection(obligations, issues, type_contracts):
            if isinstance(self._workflow_metadata, dict):
                self._workflow_metadata["api_type_contracts"] = type_contracts
            obligations, issues = _run_proof_pass(type_contracts)

        issues = inventory_issues + issues

        state_changing = [
            item for item in obligations if item.get("effect") in {"state_change", "unknown"}
        ]
        coverage = {
            "total_calls": len(obligations),
            "state_changing_calls": len(state_changing),
            "proven_calls": sum(item.get("proof_status") == "proven" for item in obligations),
            "invalid_calls": sum(item.get("proof_status") == "invalid" for item in obligations),
            "blocking_unproven_calls": sum(
                issue.get("blocking") and issue.get("issue_type") == "UnprovenApiCall"
                for issue in issues
            ),
            "warning_unproven_reads": sum(
                not issue.get("blocking") and issue.get("issue_type") == "UnprovenApiCall"
                for issue in issues
            ),
            "inventory_complete": coverage_complete,
        }
        report = {
            "schema_version": 1,
            "inventories": inventories,
            "obligations": obligations,
            "issues": issues,
            "api_proof_coverage": coverage,
            "valid": coverage_complete and not any(issue.get("blocking") for issue in issues),
            "has_warnings": any(not issue.get("blocking") for issue in issues),
        }
        if isinstance(self._workflow_metadata, dict):
            self._workflow_metadata["api_call_inventory"] = inventories
            self._workflow_metadata["api_proof_obligations"] = obligations
            self._workflow_metadata["api_proof_issues"] = issues
            self._workflow_metadata["api_proof_coverage"] = coverage
        return report
