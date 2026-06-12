from __future__ import annotations

from .cache import *


def dispatch_extension_cli_tool(tool_name: str, arguments: Dict) -> Optional[Dict]:
    """
    Dispatch a tool call to the appropriate extension CLI code generator.

    Returns a result dict with 'tool', 'code', 'instruction', 'explanation' keys,
    or None if the tool_name is not found in any extension CLI.
    """
    _ensure_cache()

    for ext_name, ext_data in _cli_cache.items():
        for schema in ext_data["schemas"]:
            func_info = schema.get("function", {})
            if func_info.get("name") != tool_name:
                continue

            # Found the matching tool — generate code from template
            result = _generate_from_template(
                ext_name, ext_data, tool_name, arguments
            )
            if result and ext_data.get("partial"):
                step_id = (arguments or {}).get("workflow_step", "")
                step_state = (
                    ext_data.get("manifest", {}).get("step_validation") or {}
                ).get(step_id)
                if step_state and not step_state.get("valid", True):
                    issues = "; ".join(step_state.get("issues", [])[:3])
                    warning = (
                        f"WARNING: step '{step_id}' did NOT pass validation "
                        f"({issues or 'unproven behavior'}). Ask the user to "
                        "confirm before executing this step's code, and tell "
                        "them what could not be proven.\n\n"
                    )
                    result["instruction"] = warning + (result.get("instruction") or "")
                    result["requires_confirmation"] = True
            return result

    return None
