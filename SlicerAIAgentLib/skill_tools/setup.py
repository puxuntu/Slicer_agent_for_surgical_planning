from .common import *


class SkillToolSetupMixin:
    def __init__(self, skill_path: str):
        self.skill_path = skill_path
        self.extra_roots: Dict[str, str] = {}  # {prefix: abs_path} for extension source dirs
        # {prefix: [abs dirs]} -- sibling packages an extension's source imports
        # (e.g. a shared wizard-step package in a multi-module repo). Searched as
        # fallback roots after the extension's own directory.
        self.extra_sibling_roots: Dict[str, List[str]] = {}
        self.platform = platform.system().lower()  # 'windows', 'linux', 'darwin'
        self._tree_sitter_available = self._ensure_tree_sitter()
        self._tree_sitter_parsers = {}  # ext -> parser cache
        self._read_history = {}  # path -> {"query": str, "strategy": str}
        self._vector_retriever = self._init_vector_retriever()
        self._rg_path_cache = self._ensure_rg()  # cache once at init

    def _ensure_tree_sitter(self) -> bool:
        """
        Check if tree-sitter and language parsers are available.
        If not, attempt to install them automatically.
        Returns True if available (either already installed or successfully installed).
        """
        try:
            import tree_sitter
            import tree_sitter_python
            import tree_sitter_cpp
            return True
        except ImportError:
            pass

        packages = ["tree-sitter", "tree-sitter-python", "tree-sitter-cpp"]

        # Try Slicer's built-in pip_install first (if running inside Slicer)
        try:
            import slicer
            logger.info("Attempting to install tree-sitter via slicer.util.pip_install...")
            for pkg in packages:
                slicer.util.pip_install(pkg)
        except ImportError:
            # Not in Slicer; use subprocess pip
            logger.info("Attempting to install tree-sitter via pip subprocess...")
            import sys
            for pkg in packages:
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", pkg],
                        check=True,
                        capture_output=True
                    )
                except subprocess.CalledProcessError as e:
                    logger.warning(f"Failed to install {pkg}: {e}")
                    return False
        except Exception as e:
            logger.warning(f"Failed to install tree-sitter: {e}")
            return False

        # Verify installation
        try:
            import tree_sitter
            import tree_sitter_python
            import tree_sitter_cpp
            logger.info("tree-sitter successfully installed and available.")
            return True
        except ImportError:
            logger.warning("tree-sitter installation verification failed.")
            return False

    def _get_tree_sitter_parser(self, ext: str):
        """Get a tree-sitter parser for the given file extension (cached)."""
        if ext in self._tree_sitter_parsers:
            return self._tree_sitter_parsers[ext]
        try:
            from tree_sitter_languages import get_parser
            if ext == '.py':
                parser = get_parser('python')
            elif ext in ('.cxx', '.cpp', '.h', '.hxx', '.c'):
                parser = get_parser('cpp')
            else:
                return None
            self._tree_sitter_parsers[ext] = parser
            return parser
        except Exception:
            return None

    def _extract_symbols_from_ast(self, node, filepath: str, pattern_lower: str, symbol_type: str, results: List[Dict], lines: List[str]):
        """Recursively walk AST to find function/class definitions."""
        node_type = node.type

        # Python
        if node_type == 'function_definition':
            name_node = None
            for child in node.children:
                if child.type == 'identifier':
                    name_node = child
                    break
            if name_node and (symbol_type in ("all", "function")):
                name = name_node.text.decode('utf8')
                if pattern_lower in name.lower():
                    line_num = node.start_point[0] + 1
                    sig = lines[line_num - 1].strip()[:120] if line_num <= len(lines) else ""
                    results.append({
                        "name": name,
                        "type": "function",
                        "file": filepath,
                        "line": line_num,
                        "signature": sig,
                        "source_type": self._infer_source_type(filepath),
                    })

        elif node_type == 'class_definition':
            name_node = None
            for child in node.children:
                if child.type == 'identifier':
                    name_node = child
                    break
            if name_node and (symbol_type in ("all", "class")):
                name = name_node.text.decode('utf8')
                if pattern_lower in name.lower():
                    line_num = node.start_point[0] + 1
                    sig = lines[line_num - 1].strip()[:120] if line_num <= len(lines) else ""
                    results.append({
                        "name": name,
                        "type": "class",
                        "file": filepath,
                        "line": line_num,
                        "signature": sig,
                        "source_type": self._infer_source_type(filepath),
                    })

        # C/C++
        elif node_type in ('function_definition', 'declaration'):
            # For C++, we need to find the declarator to get the name
            # function_definition in C++ grammar may have nested structure
            # We'll do a simpler approach: look for function_declarator or identifier
            def _find_name_in_node(n):
                if n.type in ('identifier', 'field_identifier'):
                    return n.text.decode('utf8')
                for c in n.children:
                    found = _find_name_in_node(c)
                    if found:
                        return found
                return None

            # Only process if it looks like a function definition/declaration
            has_body = any(c.type == 'compound_statement' for c in node.children)
            is_declaration = node_type == 'declaration'

            if (has_body or is_declaration) and (symbol_type in ("all", "function")):
                name = _find_name_in_node(node)
                if name and pattern_lower in name.lower():
                    line_num = node.start_point[0] + 1
                    sig = lines[line_num - 1].strip()[:120] if line_num <= len(lines) else ""
                    results.append({
                        "name": name,
                        "type": "function",
                        "file": filepath,
                        "line": line_num,
                        "signature": sig,
                        "source_type": self._infer_source_type(filepath),
                    })

        elif node_type in ('class_specifier', 'struct_specifier'):
            name_node = None
            for child in node.children:
                if child.type == 'type_identifier':
                    name_node = child
                    break
            if name_node and (symbol_type in ("all", "class")):
                name = name_node.text.decode('utf8')
                if pattern_lower in name.lower():
                    line_num = node.start_point[0] + 1
                    sig = lines[line_num - 1].strip()[:120] if line_num <= len(lines) else ""
                    results.append({
                        "name": name,
                        "type": "class",
                        "file": filepath,
                        "line": line_num,
                        "signature": sig,
                        "source_type": self._infer_source_type(filepath),
                    })

        # Recurse into children
        for child in node.children:
            self._extract_symbols_from_ast(child, filepath, pattern_lower, symbol_type, results, lines)

    def _infer_source_type(self, file_path: str) -> str:
        """Infer the role of a file based on its path within the Slicer codebase."""
        path_lower = file_path.lower().replace('\\', '/')
        if path_lower.startswith('slicer-ui-analysis/') or '/slicer_ui_preanalysis/' in path_lower:
            return 'ui_analysis'
        if '/testing/python/' in path_lower:
            return 'test_example'
        if '/docs/developer_guide/script_repository/' in path_lower:
            return 'doc_example'
        if '/editoreffects/' in path_lower or '/editor_effects/' in path_lower:
            return 'effect_implementation'
        if '/widgets/' in path_lower:
            return 'ui_implementation'
        if '/modules/cli/' in path_lower:
            return 'cli_module'
        if '/modules/scripted/' in path_lower:
            return 'scripted_module'
        if '/modules/loadable/' in path_lower:
            return 'loadable_module'
        if '/base/python/slicer/' in path_lower:
            return 'python_api'
        if '/libs/mrml/core/' in path_lower:
            return 'mrml_definition'
        return 'source'

    def _relativize(self, path: str) -> str:
        """Convert an absolute path back to a relative forward-slash path."""
        # If already relative, normalize separators only
        if not os.path.isabs(path):
            return path.replace(os.sep, '/')

        ui_docs_dir = _get_ui_analysis_docs_dir()
        try:
            ui_rel = os.path.relpath(path, ui_docs_dir)
            if not ui_rel.startswith('..'):
                return f"slicer-ui-analysis/{ui_rel.replace(os.sep, '/')}"
        except ValueError:
            pass

        try:
            rel = os.path.relpath(path, self.skill_path)
        except ValueError:
            # On Windows, relpath can fail if paths are on different drives
            rel = path

        # If relpath escapes skill_path (starts with ..), the path is not under skill_path
        # or path resolution produced an anomaly. Try manual suffix extraction.
        if rel.startswith('..'):
            norm_path = os.path.normpath(path).replace(os.sep, '/').lower()
            norm_skill = os.path.normpath(self.skill_path).replace(os.sep, '/').lower()
            if norm_path.startswith(norm_skill):
                suffix = norm_path[len(norm_skill):].lstrip('/')
                return suffix
            # Try extra roots (extension source directories)
            for prefix, root in self.extra_roots.items():
                try:
                    ext_rel = os.path.relpath(path, root)
                except ValueError:
                    continue
                if not ext_rel.startswith('..'):
                    return f"ext:{prefix}/{ext_rel.replace(os.sep, '/')}"
            # Path genuinely outside skill_path — return basename to avoid leaking
            # system directory structure to the LLM (which may reuse it in next round)
            base = os.path.basename(path.rstrip(os.sep))
            return base if base else path

        return rel.replace(os.sep, '/')

    def _resolve_path(self, path: str) -> str:
        """Resolve a tool path argument to an absolute filesystem path.

        - Absolute path: used as-is
        - slicer-ui-analysis/...: UI-analysis docs dir
        - ext:<prefix>/...: resolved against extra_roots (the INSTALLED extension)
        - slicer-extensions/<Ext>/...: when <Ext> is an installed extension (in
          extra_roots), redirected to its INSTALLED copy so the agent reads the
          same version it runs — avoids the knowledge-base-vs-installed version
          skew. Non-installed extensions stay in the knowledge base.
        - Relative path: resolved against skill_path (knowledge base)
        """
        if os.path.isabs(path):
            return path
        if path == "slicer-ui-analysis" or path.startswith("slicer-ui-analysis/"):
            sub = path[len("slicer-ui-analysis"):].lstrip("/\\")
            return os.path.join(_get_ui_analysis_docs_dir(), sub)
        if path.startswith("ext:"):
            rest = path[4:]
            slash = rest.find('/')
            if slash >= 0:
                prefix, sub = rest[:slash], rest[slash + 1:]
                if prefix in self.extra_roots:
                    return self._resolve_in_extension_root(
                        self.extra_roots[prefix], sub,
                        self.extra_sibling_roots.get(prefix, ()),
                    )
            return path
        # Redirect an installed extension's knowledge-base path to its installed
        # source (the version the runtime imports). Path form:
        # "slicer-extensions/<Ext>/<sub>".
        marker = "slicer-extensions/"
        norm = path.replace("\\", "/")
        if norm.startswith(marker):
            rest = norm[len(marker):]
            slash = rest.find('/')
            ext_name = rest[:slash] if slash >= 0 else rest
            sub = rest[slash + 1:] if slash >= 0 else ""
            if ext_name in self.extra_roots:
                return self._resolve_in_extension_root(
                    self.extra_roots[ext_name], sub,
                    self.extra_sibling_roots.get(ext_name, ()),
                )
        return os.path.join(self.skill_path, path)

    def _resolve_in_extension_root(self, root: str, sub: str, siblings=()) -> str:
        """Resolve ``sub`` under an installed extension root, with basename fallback.

        Installed extensions place their modules under a build-specific subtree
        (e.g. ``lib/Slicer-X.Y/qt-scripted-modules/``) that differs from the
        knowledge-base layout, so an exact relative path often does not exist.
        Fall back to the first file with the same basename anywhere under the
        installed root, then under the extension's sibling source roots (shared
        packages a multi-module repo keeps outside the module folder).
        """
        if not sub:
            return root
        direct = os.path.join(root, sub)
        if os.path.exists(direct):
            return direct
        base = os.path.basename(sub.replace("\\", "/"))
        if base:
            for search_root in (root,) + tuple(siblings or ()):
                try:
                    for dirpath, _dirs, files in os.walk(search_root):
                        if base in files:
                            return os.path.join(dirpath, base)
                except Exception:
                    pass
        return direct

    def _init_vector_retriever(self) -> Any:
        """
        Attempt to load an existing vector index.
        Returns VectorRetriever if available, else None.
        """
        import time
        t0 = time.time()
        try:
            from ..SkillIndexer import IndexBuilder, _get_model_cache_dir, _get_index_dir
            builder = IndexBuilder(self.skill_path)
            retriever = builder.load_retriever()
            t1 = time.time()
            if retriever and retriever.is_ready():
                logger.info("Vector retriever loaded successfully.")
                return retriever
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.warning(f"Vector retriever initialization failed: {e}")
        return None

    def has_vector_index(self) -> bool:
        """Return True if a dense vector index is loaded and ready."""
        result = self._vector_retriever is not None and self._vector_retriever.is_ready()
        return result
