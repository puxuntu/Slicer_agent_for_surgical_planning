from .common import *


class SkillToolReadFileMixin:
    def _readfile(self, path: str, query: Optional[str] = None) -> Dict:
        """Read file content with smart slicing for large files."""
        # Normalize path
        path = self._resolve_path(path)

        if not os.path.exists(path):
            return {"error": f"File not found: {path}"}

        if not os.path.isfile(path):
            return {"error": f"Path is not a file: {path}"}

        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            total_lines = len(lines)
            is_markdown = path.lower().endswith('.md')

            # Duplicate read detection
            note = None
            rel_path = self._relativize(path)
            if rel_path in self._read_history:
                prev = self._read_history[rel_path]
                note = (
                    f"[Note: This file was previously read with query='{prev['query']}' "
                    f"(strategy={prev['strategy']}). "
                    f"If the current content is insufficient, consider searching a different file.]"
                )

            if total_lines < 500:
                content = ''.join(lines)
                strategy = "full"
            else:
                if query:
                    if is_markdown:
                        content = self._slice_markdown_by_query(lines, query)
                        strategy = "markdown_heading"
                    else:
                        # For test files, prefer test-method slicing over class-level AST
                        is_test_file = '/Testing/Python/' in path.replace('\\', '/')
                        if is_test_file:
                            test_slice = self._slice_test_method(lines, query)
                            if test_slice:
                                content = test_slice
                                strategy = "test_method"
                            else:
                                ext = os.path.splitext(path)[1].lower()
                                ast_slice = self._slice_by_ast_boundary(lines, query, ext)
                                if ast_slice:
                                    content = ast_slice
                                    strategy = "ast_boundary"
                                else:
                                    content = self._slice_by_grep_context(lines, query)
                                    strategy = "grep_context"
                        else:
                            # Try AST-based boundary slice first (exact function/class boundaries)
                            ext = os.path.splitext(path)[1].lower()
                            ast_slice = self._slice_by_ast_boundary(lines, query, ext)
                            if ast_slice:
                                content = ast_slice
                                strategy = "ast_boundary"
                            else:
                                content = self._slice_by_grep_context(lines, query)
                                strategy = "grep_context"
                else:
                    content = ''.join(lines[:500]) + "\n... [file truncated: provide query to locate specific section] ..."
                    strategy = "truncated"

            # Record this read for duplicate detection
            self._read_history[rel_path] = {"query": query or "(none)", "strategy": strategy}

            result = {
                "tool": "ReadFile",
                "path": path,
                "query": query,
                "content": content,
                "total_lines": total_lines,
                "strategy": strategy,
                "source_type": self._infer_source_type(path),
            }
            notes = []
            if note:
                notes.append(note)

            # Gist-link dead-end detection
            gist_links = re.findall(r'https?://gist\.github\.com/\S+', content)
            has_local_code = bool(re.search(r'```python\s*\n', content))
            if len(gist_links) > 2 and not has_local_code:
                notes.append(
                    "[Note: This section contains mainly external gist links with no local executable examples. "
                    "Search for specific function names in test files instead.]"
                )

            if notes:
                result["_note"] = "\n".join(notes)

            # For markdown files, list all available headings so the LLM can decide if further reads are needed
            if is_markdown:
                headings = []
                for line in lines:
                    m = re.match(r'^(#{1,6})\s+(.+)$', line)
                    if m:
                        level = len(m.group(1))
                        title = m.group(2).strip()
                        headings.append(f"{'  ' * (level - 1)}{title}")
                if headings:
                    MAX_HEADINGS = 30
                    if len(headings) > MAX_HEADINGS:
                        result["available_sections"] = headings[:MAX_HEADINGS] + [f"... {len(headings) - MAX_HEADINGS} more headings omitted ..."]
                    else:
                        result["available_sections"] = headings
            return result
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}

    def _slice_markdown_by_query(self, lines: List[str], query: str) -> str:
        """Slice markdown by heading boundaries, keeping sections that match query."""
        query_lower = query.lower()
        sections = []
        current_section = []
        current_heading = ""

        for line in lines:
            if re.match(r'^#{1,6}\s+', line):
                if current_section:
                    section_text = ''.join(current_section)
                    if query_lower in section_text.lower():
                        sections.append(section_text)
                current_heading = line
                current_section = [line]
            else:
                current_section.append(line)

        if current_section:
            section_text = ''.join(current_section)
            if query_lower in section_text.lower():
                sections.append(section_text)

        if sections:
            return '\n\n... [other sections omitted] ...\n\n'.join(sections)
        else:
            return ''.join(lines[:300]) + "\n... [no matching section found, truncated] ..."

    def _slice_by_grep_context(self, lines: List[str], query: str) -> str:
        """Find query in lines and extract ±100 line context blocks."""
        query_lower = query.lower()
        match_lines = []
        for i, line in enumerate(lines):
            if query_lower in line.lower():
                match_lines.append(i)

        if not match_lines:
            return ''.join(lines[:300]) + "\n... [query not found, truncated] ..."

        CONTEXT = 100
        blocks = []
        for line_no in match_lines:
            start = max(0, line_no - CONTEXT)
            end = min(len(lines), line_no + CONTEXT + 1)
            blocks.append((start, end))

        merged = []
        for start, end in sorted(blocks):
            if merged and start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))

        parts = []
        for i, (start, end) in enumerate(merged):
            if i > 0:
                skipped = merged[i][0] - merged[i-1][1]
                parts.append(f"\n... [{skipped} lines skipped] ...\n")
            parts.append(''.join(lines[start:end]))

        return ''.join(parts)

    def _slice_test_method(self, lines: List[str], query: str) -> Optional[str]:
        """
        Slice Python test files by test method boundaries.
        Returns complete test method / TestSection bodies that match the query.
        More precise than class-level AST slicing for test files.
        """
        query_lower = query.lower()
        matches = []
        i = 0
        while i < len(lines):
            line = lines[i]
            # Match test methods: def test_xxx(...) or def TestSection_xxx(...)
            match = re.match(r'^(\s*)def\s+(test_\w+|TestSection_\w+)\s*\(', line)
            if match:
                indent = match.group(1)
                method_name = match.group(2)
                start = i
                i += 1
                # Capture until next method/class at same or less indentation
                while i < len(lines):
                    next_line = lines[i]
                    # Check if next line is a new def/class at same or less indent
                    if re.match(rf'^{re.escape(indent)}(?:def\s+|class\s+)', next_line):
                        break
                    i += 1
                end = i
                body = ''.join(lines[start:end])
                if query_lower in body.lower():
                    matches.append((method_name, start, end))
                continue
            i += 1

        if not matches:
            return None

        MAX_MATCHES = 3
        parts = []
        for i, (method_name, start, end) in enumerate(matches[:MAX_MATCHES]):
            parts.append(f"=== test method: {method_name} (lines {start+1}-{end}) ===\n")
            parts.append(''.join(lines[start:end]))

        if len(matches) > MAX_MATCHES:
            parts.append(f"\n... [{len(matches) - MAX_MATCHES} more test methods omitted, use more specific query] ...")

        return ''.join(parts)

    def _slice_by_ast_boundary(self, lines: List[str], query: str, ext: str) -> Optional[str]:
        """
        Slice code by AST boundaries: return complete function/class bodies that match query.
        Ensures function bodies are never truncated mid-definition.
        Falls back to None if tree-sitter unavailable or parse fails.
        """
        if not self._tree_sitter_available:
            return None

        parser = self._get_tree_sitter_parser(ext)
        if not parser:
            return None

        source = ''.join(lines)
        try:
            tree = parser.parse(bytes(source, 'utf8'))
        except Exception:
            return None

        query_lower = query.lower()
        matches = []

        def _extract_node_name(node):
            """Extract identifier name from function/class AST node."""
            target_types = {
                'function_definition': ('identifier', 'field_identifier'),
                'class_definition': ('identifier',),
                'class_specifier': ('type_identifier',),
                'struct_specifier': ('type_identifier',),
            }
            expected = target_types.get(node.type, ('identifier', 'type_identifier', 'field_identifier'))

            def _find(n):
                if n.type in expected:
                    return n.text.decode('utf8')
                for c in n.children:
                    found = _find(c)
                    if found:
                        return found
                return None

            return _find(node)

        def _walk(node):
            if node.type in ('function_definition', 'class_definition', 'class_specifier', 'struct_specifier'):
                name = _extract_node_name(node)

                # Strategy 1: name contains query
                if name and query_lower in name.lower():
                    matches.append((name, node))
                    return  # Don't recurse into children to avoid nested duplicates

                # Strategy 2: body contains query (but node has a name)
                if name:
                    body = node.text.decode('utf8').lower()
                    if query_lower in body:
                        matches.append((name, node))
                        return

            for child in node.children:
                _walk(child)

        _walk(tree.root_node)

        if not matches:
            return None

        # Deduplicate by line range
        seen = set()
        unique = []
        for name, node in matches:
            key = (node.start_point[0], node.end_point[0])
            if key not in seen:
                seen.add(key)
                unique.append((name, node))

        MAX_MATCHES = 3
        parts = []
        for i, (name, node) in enumerate(unique[:MAX_MATCHES]):
            start_line = node.start_point[0]
            end_line = node.end_point[0]
            node_type = node.type.replace('_', ' ')
            parts.append(f"=== {node_type}: {name} (lines {start_line+1}-{end_line+1}) ===\n")
            parts.append(''.join(lines[start_line:end_line+1]))

        if len(unique) > MAX_MATCHES:
            parts.append(f"\n... [{len(unique) - MAX_MATCHES} more AST matches omitted, use more specific query] ...")

        return ''.join(parts)
