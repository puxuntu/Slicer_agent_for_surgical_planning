"""Live-oracle pre-execution API sanity check for generated code.

The main agent runs inside Slicer, so the running Python process is the
authoritative oracle for which APIs exist — including attributes registered
at runtime by loaded extensions. Before executing generated code, this module
extracts module-rooted attribute chains (slicer.*, vtk.*, qt.*, ctk.*) and
resolves them live via getattr-walks. A confirmed-missing chain is caught
BEFORE execution, with close-match suggestions, and routed into the existing
self-correction path — skipping a doomed execute/rollback cycle and giving
the correction LLM precise evidence instead of a raw AttributeError.

Safety constraints:
- Attribute reads only: chains never cross a call boundary, so resolution
  performs exactly the attribute lookups execution itself would perform —
  no constructors, no method invocations.
- Submodule imports are attempted only for children of the four known roots
  (lazy-submodule false-positive guard, e.g. ``vtk.util``).
- Only a RESOLVED parent lacking the attribute counts as missing; any other
  failure (raising __getattr__, unresolvable parent) is skipped, not flagged
  (the doctrine api_proof.py uses for live probes).
- Bounded work (MAX_CHAINS, TIME_BUDGET_S) and a whole-body try/except:
  every failure mode degrades to "proceed with execution as today".

This module must stay importable without Slicer: roots are looked up in
sys.modules at check time, so outside Slicer every chain is simply skipped.
"""

from __future__ import annotations

import ast
import difflib
import importlib
import logging
import re
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

ROOTS = ("slicer", "vtk", "qt", "ctk")
MAX_CHAINS = 200
TIME_BUDGET_S = 0.25
_CLOSE_MATCH_LIMIT = 5


def _collect_shadowed_names(tree: ast.AST) -> set:
    """Names assigned or imported in the code — these shadow the real roots."""
    shadowed = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                for sub in ast.walk(target):
                    if isinstance(sub, ast.Name):
                        shadowed.add(sub.id)
        elif isinstance(node, (ast.AugAssign, ast.AnnAssign, ast.For)):
            target = getattr(node, "target", None)
            if target is not None:
                for sub in ast.walk(target):
                    if isinstance(sub, ast.Name):
                        shadowed.add(sub.id)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                shadowed.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for arg in list(node.args.args) + list(node.args.kwonlyargs):
                shadowed.add(arg.arg)
        elif isinstance(node, ast.withitem) and node.optional_vars is not None:
            for sub in ast.walk(node.optional_vars):
                if isinstance(sub, ast.Name):
                    shadowed.add(sub.id)
    # `import slicer` / `import vtk` aliases the real module — do not treat
    # those as shadowing.
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                base = alias.name.split(".")[0]
                if base in ROOTS and (alias.asname or base) == base:
                    shadowed.discard(base)
    return shadowed


def extract_chains(code: str) -> List[Dict]:
    """Extract module-rooted pure attribute chains from code.

    A chain descends only Name/Attribute links (stops at any Call boundary,
    subscript, etc.). ``is_called`` marks chains whose final attribute is
    invoked, so the resolved object must additionally be callable.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    shadowed = _collect_shadowed_names(tree)

    # Attribute nodes that are an inner segment of a longer chain we already
    # capture from the outermost node.
    inner_attrs = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Attribute):
            inner_attrs.add(id(node.value))

    called_funcs = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            called_funcs.add(id(node.func))

    chains: Dict[str, Dict] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute) or id(node) in inner_attrs:
            continue
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            continue
        parts = []
        cur: Any = node
        while isinstance(cur, ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if not isinstance(cur, ast.Name):
            continue  # chain interrupted by a call/subscript — not checkable
        root = cur.id
        if root not in ROOTS or root in shadowed:
            continue
        chain = ".".join([root] + list(reversed(parts)))
        entry = chains.setdefault(
            chain, {"chain": chain, "is_called": False, "lineno": node.lineno}
        )
        if id(node) in called_funcs:
            entry["is_called"] = True
        if len(chains) >= MAX_CHAINS:
            break
    return list(chains.values())


def resolve_chain(chain: str, is_called: bool = False) -> Dict:
    """Resolve a dotted chain live. Never invokes anything.

    Returns {"status": "resolved" | "missing" | "skipped", ...}. Missing is
    claimed ONLY when a successfully resolved parent provably lacks the
    attribute; every other failure is "skipped" (fail-open).
    """
    parts = chain.split(".")
    root = sys.modules.get(parts[0])
    if root is None:
        return {"status": "skipped", "chain": chain, "reason": "root not loaded"}

    obj = root
    parent_chain = parts[0]
    for attr in parts[1:]:
        try:
            obj = getattr(obj, attr)
        except AttributeError:
            # Lazy-submodule guard: a missing attribute on a module may be an
            # unimported child module.
            if hasattr(obj, "__name__") and getattr(obj, "__spec__", None) is not None:
                try:
                    obj = importlib.import_module(f"{obj.__name__}.{attr}")
                    parent_chain = f"{parent_chain}.{attr}"
                    continue
                except Exception:
                    pass
            try:
                candidates = dir(obj)
            except Exception:
                candidates = []
            return {
                "status": "missing",
                "kind": "missing_attribute",
                "chain": chain,
                "parent_chain": parent_chain,
                "missing_attr": attr,
                "close_matches": difflib.get_close_matches(
                    attr, candidates, n=_CLOSE_MATCH_LIMIT, cutoff=0.6
                ),
            }
        except Exception:
            # Raising __getattr__, lazy proxies, etc. — not evidence of absence.
            return {"status": "skipped", "chain": chain, "reason": "unresolvable parent"}
        parent_chain = f"{parent_chain}.{attr}"

    if is_called and not callable(obj):
        return {
            "status": "missing",
            "kind": "not_callable",
            "chain": chain,
            "parent_chain": ".".join(parts[:-1]),
            "missing_attr": parts[-1],
            "close_matches": [],
        }
    return {"status": "resolved", "chain": chain}


def check_code(code: str) -> Dict:
    """Check all module-rooted chains in code against the live runtime.

    Always safe to call: any internal failure or exceeded time budget
    returns ok=True (fail-open).
    """
    started = time.time()
    result = {"ok": True, "missing": [], "checked": 0, "skipped": 0, "elapsed": 0.0}
    try:
        for entry in extract_chains(code):
            if time.time() - started > TIME_BUDGET_S:
                result["skipped_reason"] = "time budget exceeded"
                result["missing"] = []
                result["ok"] = True
                break
            outcome = resolve_chain(entry["chain"], entry.get("is_called", False))
            if outcome["status"] == "missing":
                outcome["lineno"] = entry.get("lineno")
                result["missing"].append(outcome)
            elif outcome["status"] == "skipped":
                result["skipped"] += 1
            result["checked"] += 1
        else:
            result["ok"] = not result["missing"]
    except Exception:
        logger.debug("ApiSanityChecker failed open", exc_info=True)
        result = {"ok": True, "missing": [], "checked": 0, "skipped": 0,
                  "skipped_reason": "checker error"}
    result["elapsed"] = round(time.time() - started, 4)
    return result


def format_failures(missing: List[Dict]) -> str:
    """Human/LLM-readable evidence for confirmed-missing chains."""
    lines = ["[ApiSanityCheck] Pre-execution live check against this running Slicer:"]
    for item in missing[:8]:
        if item.get("kind") == "not_callable":
            lines.append(
                f"- '{item['chain']}' exists but is NOT callable "
                f"(line {item.get('lineno', '?')}); it must not be called."
            )
            continue
        line = (
            f"- '{item['chain']}' does not exist in this Slicer runtime "
            f"(line {item.get('lineno', '?')}; verified by introspection: "
            f"'{item['parent_chain']}' has no attribute '{item['missing_attr']}')."
        )
        if item.get("close_matches"):
            line += (
                f" Closest existing attributes on {item['parent_chain']}: "
                + ", ".join(item["close_matches"])
            )
        lines.append(line)
    lines.append(
        "Do NOT retry the missing names. Use an existing attribute (see the "
        "closest matches) or a different evidence-backed API path."
    )
    return "\n".join(lines)


_ERROR_PATTERNS = (
    # module 'slicer.util' has no attribute 'getNodez'
    re.compile(r"module '([\w.]+)' has no attribute '(\w+)'"),
    # 'vtkMRMLScalarVolumeNode' object has no attribute 'GetFoo'
    re.compile(r"'(\w+)' object has no attribute '(\w+)'"),
    # name 'slicerx' is not defined
    re.compile(r"name '(\w+)' is not defined"),
)


def live_attribute_evidence(error_text: str) -> str:
    """Close-match evidence for a runtime AttributeError/NameError, or ''.

    Returns '' for [ApiSanityCheck]-prefixed errors (they already embed
    evidence) and on any resolution failure.
    """
    try:
        if not error_text or error_text.lstrip().startswith("[ApiSanityCheck]"):
            return ""
        lines: List[str] = []

        match = _ERROR_PATTERNS[0].search(error_text)
        if match:
            module_name, attr = match.groups()
            module = sys.modules.get(module_name)
            if module is None and module_name.split(".")[0] in ROOTS:
                try:
                    module = importlib.import_module(module_name)
                except Exception:
                    module = None
            if module is not None:
                close = difflib.get_close_matches(
                    attr, dir(module), n=_CLOSE_MATCH_LIMIT, cutoff=0.5
                )
                if close:
                    lines.append(
                        f"- Verified live: module '{module_name}' has no attribute "
                        f"'{attr}'. Closest existing attributes: " + ", ".join(close)
                    )

        match = _ERROR_PATTERNS[1].search(error_text)
        if match:
            type_name, attr = match.groups()
            # Try to locate the type on the known roots (e.g. slicer.vtkMRMLX,
            # vtk.vtkX) — read-only class attribute introspection.
            for root_name in ROOTS:
                root = sys.modules.get(root_name)
                if root is None:
                    continue
                cls = getattr(root, type_name, None)
                if cls is None:
                    continue
                try:
                    close = difflib.get_close_matches(
                        attr, dir(cls), n=_CLOSE_MATCH_LIMIT, cutoff=0.5
                    )
                except Exception:
                    close = []
                if close:
                    lines.append(
                        f"- Verified live: {root_name}.{type_name} has no attribute "
                        f"'{attr}'. Closest existing attributes: " + ", ".join(close)
                    )
                break

        match = _ERROR_PATTERNS[2].search(error_text)
        if match:
            name = match.group(1)
            close = difflib.get_close_matches(
                name, list(ROOTS), n=2, cutoff=0.5
            )
            if close:
                lines.append(
                    f"- Name '{name}' is not defined; did you mean the module "
                    f"{' or '.join(close)}? Variables must be defined before use."
                )

        return "\n".join(lines)
    except Exception:
        logger.debug("live_attribute_evidence failed", exc_info=True)
        return ""
