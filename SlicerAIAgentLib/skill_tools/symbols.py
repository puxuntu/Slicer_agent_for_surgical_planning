from .common import *


class SkillToolSymbolsMixin:
    def _rg_find_symbol_candidates(self, pattern: str, path: str) -> List[str]:
        """Use ripgrep to quickly find files that may contain the symbol name.

        This avoids slow AST parsing on files that don't contain the pattern at all.
        Returns up to 50 candidate file paths, sorted by modification time (newest first).
        """
        rg_exe = self._rg_path_cache
        if not rg_exe:
            return []

        # Use ripgrep to find files containing the pattern (case-insensitive)
        cmd = [rg_exe, "-l", "-i", "--max-count", "1", pattern, path]
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=15)
            if result.returncode not in (0, 1):  # 1 = no matches
                return []
            files = result.stdout.decode('utf-8', errors='ignore').strip().split('\n')
            files = [f.strip() for f in files if f.strip()]
            # Filter to supported extensions
            valid_exts = {'.py', '.cxx', '.cpp', '.h', '.hxx', '.c', '.md'}
            files = [f for f in files if os.path.splitext(f)[1].lower() in valid_exts]
            # Prioritize newer files (more likely to be relevant in MRML/Core context)
            files.sort(key=lambda f: os.path.getmtime(f) if os.path.isfile(f) else 0, reverse=True)
            return files[:50]
        except Exception:
            return []

    def _search_symbol(self, pattern: str, path: str, symbol_type: str = "all") -> Dict:
        """
        Search for symbol definitions (functions, classes, headings).
        Only matches definitions, not call sites or comments.
        """
        path = self._resolve_path(path)

        if not os.path.exists(path):
            return {"error": f"Path not found: {path}"}

        results = []
        pattern_lower = pattern.lower()

        def _scan_file(filepath: str):
            ext = os.path.splitext(filepath)[1].lower()
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            except Exception:
                return

            # Use AST-based parsing for Python/C++ if tree-sitter is available
            use_ast = self._tree_sitter_available and ext in ('.py', '.cxx', '.cpp', '.h', '.hxx', '.c')

            if use_ast:
                parser = self._get_tree_sitter_parser(ext)
                if parser:
                    try:
                        source = ''.join(lines)
                        tree = parser.parse(bytes(source, 'utf8'))
                        self._extract_symbols_from_ast(
                            tree.root_node, filepath, pattern_lower, symbol_type, results, lines
                        )
                        return  # AST handled everything for this file
                    except Exception:
                        # AST parse failed, fall through to regex
                        pass

            if ext == '.py':
                # Python: def / class definitions
                for i, line in enumerate(lines, 1):
                    match = re.match(r'^(\s*)(def|class)\s+([A-Za-z_][A-Za-z0-9_]*)', line)
                    if match:
                        name = match.group(3)
                        sym_type = "function" if match.group(2) == "def" else "class"
                        if symbol_type in ("all", sym_type) and pattern_lower in name.lower():
                            results.append({
                                "name": name,
                                "type": sym_type,
                                "file": filepath,
                                "line": i,
                                "signature": line.strip()[:120]
                            })

            elif ext in ('.cxx', '.cpp', '.h', '.hxx', '.c'):
                # C/C++: function/class/struct definitions (simplified regex)
                for i, line in enumerate(lines, 1):
                    # Match: return_type name(...) {  or  class/struct Name {
                    match = re.match(
                        r'^[\s\w:*&<>~]+\s+(\w+)\s*\([^)]*\)\s*\{'
                        r'|^(?:class|struct)\s+(\w+)'
                        r'|^\s*(\w+)\s*\([^)]*\)\s*;',
                        line
                    )
                    if match:
                        name = match.group(1) or match.group(2) or match.group(3)
                        if name:
                            if 'class' in line or 'struct' in line:
                                sym_type = "class"
                            else:
                                sym_type = "function"
                            if symbol_type in ("all", sym_type) and pattern_lower in name.lower():
                                results.append({
                                    "name": name,
                                    "type": sym_type,
                                    "file": filepath,
                                    "line": i,
                                    "signature": line.strip()[:120],
                                    "source_type": self._infer_source_type(filepath),
                                })

            elif ext == '.md':
                # Markdown: headings as symbols
                for i, line in enumerate(lines, 1):
                    match = re.match(r'^(#{1,6})\s+(.+)$', line)
                    if match:
                        name = match.group(2).strip()
                        level = len(match.group(1))
                        if symbol_type in ("all", "heading") and pattern_lower in name.lower():
                            results.append({
                                "name": name,
                                "type": f"heading_h{level}",
                                "file": filepath,
                                "line": i,
                                "signature": line.strip()[:120],
                                "source_type": self._infer_source_type(filepath),
                            })

        scan_start = time.time()
        if os.path.isfile(path):
            _scan_file(path)
        else:
            # Fast path: use ripgrep to find candidate files before doing AST scanning
            candidate_files = self._rg_find_symbol_candidates(pattern, path) if self._rg_path_cache else None
            if candidate_files:
                for filepath in candidate_files:
                    _scan_file(filepath)
                    if len(results) >= 20:
                        break
            else:
                for root, _, filenames in os.walk(path):
                    for filename in filenames:
                        ext = os.path.splitext(filename)[1].lower()
                        if ext in ('.py', '.cxx', '.cpp', '.h', '.hxx', '.c', '.md'):
                            _scan_file(os.path.join(root, filename))
                            if len(results) >= 20:
                                break
                    if len(results) >= 20:
                        break

        return {
            "tool": "SearchSymbol",
            "pattern": pattern,
            "type": symbol_type,
            "path": path,
            "results": results,
            "count": len(results),
            "_tool_timing": f"{time.time() - scan_start:.3f}s",
        }


# Tool definitions for AI
