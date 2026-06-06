from __future__ import annotations

from .cache import *


def _fill_template(template_str: str, kwargs: Dict[str, str]) -> str:
    """Fill a template supporting both {name} and {name: default_value} syntax.

    - {name}: replaced with kwargs[name], KeyError if missing
    - {name: default}: replaced with kwargs[name] if present, else default
    - {{ and }} are preserved as literal braces
    - Brace pairs inside Python string/f-string literals are left untouched

    Uses a character-by-character scanner with brace-depth tracking to
    correctly handle nested braces in default values (e.g.
    ``{param: {"key": "val"}}``).
    """
    import re

    # Phase 1: Mask out Python string literals so braces inside them are
    # left untouched.  Handles single/double/triple-quoted strings with
    # optional f/r/b prefixes.
    string_ranges = []
    for m in re.finditer(
        r'(?:[fFrRbBuU]{0,2})("""|\'\'\'|"|\')(.*?)\1',
        template_str, re.DOTALL,
    ):
        string_ranges.append((m.start(), m.end()))

    def _in_string(pos):
        return any(s <= pos < e for s, e in string_ranges)

    # Phase 2: Protect escaped double-braces by replacing them with sentinels.
    sentinel_l = "\x00LBRACE\x00"
    sentinel_r = "\x00RBRACE\x00"
    buf = template_str.replace("{{", sentinel_l).replace("}}", sentinel_r)

    # Phase 3: Walk the buffer character-by-character.  When we find a
    # ``{`` that is NOT inside a string literal, scan forward tracking brace
    # depth until we find the matching ``}``.  Then try to parse the content
    # as a placeholder and replace it.
    result_parts = []
    i = 0
    n = len(buf)

    while i < n:
        ch = buf[i]

        # Skip masked string literals entirely
        if _in_string(i):
            # Find the end of this string range and emit it verbatim
            in_any = False
            for s, e in string_ranges:
                if s <= i < e:
                    result_parts.append(buf[i:e])
                    i = e
                    in_any = True
                    break
            if in_any:
                continue

        if ch != '{':
            result_parts.append(ch)
            i += 1
            continue

        # We have a '{'.  Scan forward to find the matching '}' using
        # brace-depth tracking so nested braces in defaults are handled.
        depth = 0
        j = i
        found = False
        while j < n:
            c = buf[j]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    found = True
                    break
            j += 1

        if not found:
            # No matching '}' — emit the '{' literally and move on.
            result_parts.append(ch)
            i += 1
            continue

        # Extract the content between the outermost braces.
        inner = buf[i + 1 : j]

        # Try to parse as a placeholder:  name  or  name: default
        colon_pos = inner.find(":")
        if colon_pos >= 0 and inner[:colon_pos].strip().isidentifier():
            name = inner[:colon_pos].strip()
            default = inner[colon_pos + 1:]  # everything after ":"
            # Strip one leading space from default for readability: {n: val} → val
            if default.startswith(" "):
                default = default[1:]
        elif inner.strip().isidentifier():
            name = inner.strip()
            default = None
        else:
            # Not a valid placeholder — emit the original text literally.
            result_parts.append(buf[i : j + 1])
            i = j + 1
            continue

        # Perform replacement
        if name in kwargs:
            result_parts.append(kwargs[name])
        elif default is not None:
            result_parts.append(default)
        else:
            raise KeyError(name)

        i = j + 1

    # Phase 4: Restore escaped braces
    out = "".join(result_parts)
    out = out.replace(sentinel_l, "{").replace(sentinel_r, "}")
    return out


def _generate_from_template(
    ext_name: str,
    ext_data: Dict,
    tool_name: str,
    arguments: Dict,
) -> Dict:
    """
    Fill a code template with the provided arguments and return the result dict.
    Always delegates to dispatch_workflow_step for cookbook-driven workflows.
    """
    return dispatch_workflow_step(ext_name, ext_data, tool_name, arguments)


# Track completed/skipped steps per workflow so the skip handler can compute
# the next step without needing a reference to the WorkflowOrchestrator.
_workflow_completed_steps: Dict[str, set] = {}

# Store user_choice selections keyed by (extension_name, parameter_name)
_workflow_choices: Dict[str, Dict[str, Any]] = {}

# Store repeat progress keyed by extension_name then repeat group id.
_workflow_repeat_state: Dict[str, Dict[str, Dict[str, int]]] = {}
