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
            return _generate_from_template(
                ext_name, ext_data, tool_name, arguments
            )

    return None
