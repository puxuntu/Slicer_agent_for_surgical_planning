from .common import *

class Chunker:
    """Split knowledge-base files into semantic chunks."""

    # P0 + P1 directories that we actually index
    INDEXED_PREFIXES = (
        # ── Cookbook examples (highest value for code gen) ──
        "slicer-source/Docs/developer_guide/script_repository",

        # ── Core Python API ──
        "slicer-source/Base/Python/slicer/util.py",
        "slicer-source/Base/Python/slicer/",

        # ── Scripted module reference implementations ──
        "slicer-source/Modules/Scripted/",

        # ── Segment Editor Python effects ──
        "slicer-source/Modules/Loadable/Segmentations/EditorEffects/Python/",

        # ── Loadable module Python tests (programmatic control APIs) ──
        "slicer-source/Modules/Loadable/Colors/Testing/Python/",
        "slicer-source/Modules/Loadable/CropVolume/Testing/Python/",
        "slicer-source/Modules/Loadable/Markups/Testing/Python/",
        "slicer-source/Modules/Loadable/Markups/Widgets/Testing/Python/",
        "slicer-source/Modules/Loadable/Plots/Testing/Python/",
        "slicer-source/Modules/Loadable/SceneViews/Testing/Python/",
        "slicer-source/Modules/Loadable/Segmentations/Testing/Python/",
        "slicer-source/Modules/Loadable/Sequences/Testing/Python/",
        "slicer-source/Modules/Loadable/SubjectHierarchy/Testing/Python/",
        "slicer-source/Modules/Loadable/SubjectHierarchy/Widgets/Python/",
        "slicer-source/Modules/Loadable/Tables/Testing/Python/",
        "slicer-source/Modules/Loadable/VolumeRendering/Testing/Python/",
        "slicer-source/Modules/Loadable/Volumes/Testing/Python/",

        # ── MRML node definitions (maps to Python MRML API) ──
        "slicer-source/Libs/MRML/Core/",

        # ── Generated Slicer core UI-to-implementation analysis ──
        "slicer-ui-analysis/",
    )

    # Extensions we know how to chunk
    CHUNKABLE_EXTS = {'.py', '.cxx', '.cpp', '.h', '.hxx', '.c', '.md'}

    def __init__(self, tree_sitter_available: bool = True):
        self._tree_sitter_available = tree_sitter_available

    def should_index_file(self, rel_path: str) -> bool:
        """Only index files under P0/P1 prefixes with known extensions."""
        rel_unix = rel_path.replace('\\', '/')
        # Must match a prefix
        if not any(rel_unix.startswith(p) for p in self.INDEXED_PREFIXES):
            return False
        ext = os.path.splitext(rel_path)[1].lower()
        if ext not in self.CHUNKABLE_EXTS:
            return False
        return True

    def chunk_file(self, filepath: str, rel_path: str) -> List[CodeChunk]:
        """Dispatch to the appropriate chunking strategy."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            logger.warning(f"Cannot read {filepath}: {e}")
            return []

        if not lines:
            return []

        ext = os.path.splitext(filepath)[1].lower()
        source_type = self._infer_source_type(rel_path)

        if ext == '.py':
            chunks = self._chunk_python_ast(filepath, lines, rel_path, source_type)
        elif ext in ('.cxx', '.cpp', '.h', '.hxx', '.c'):
            chunks = self._chunk_cpp_ast(filepath, lines, rel_path, source_type)
        elif ext == '.md':
            chunks = self._chunk_markdown(filepath, lines, rel_path, source_type)
        else:
            chunks = []

        if not chunks:
            # Fallback: whole-file chunk
            content = ''.join(lines)
            chunks = [CodeChunk(
                chunk_id=f"{rel_path}#1-{len(lines)}",
                file_path=rel_path,
                start_line=1,
                end_line=len(lines),
                content=content,
                embedding_text=self._enhance_code_embedding_text(
                    rel_path, content, "whole_file", source_type
                ),
                chunk_type="whole_file",
                source_type=source_type,
                language="other",
            )]

        return chunks

    def _infer_source_type(self, rel_path: str) -> str:
        """Mirror of SkillTools._infer_source_type."""
        path_lower = rel_path.lower().replace('\\', '/')
        if path_lower.startswith('slicer-ui-analysis/'):
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

    def _get_tree_sitter_parser(self, ext: str):
        """Get a tree-sitter parser (same logic as SkillTools)."""
        if not self._tree_sitter_available:
            return None
        try:
            from tree_sitter_languages import get_parser
            if ext == '.py':
                return get_parser('python')
            elif ext in ('.cxx', '.cpp', '.h', '.hxx', '.c'):
                return get_parser('cpp')
            else:
                return None
        except Exception:
            return None

    def _chunk_python_ast(self, filepath: str, lines: List[str],
                          rel_path: str, source_type: str) -> List[CodeChunk]:
        parser = self._get_tree_sitter_parser('.py')
        if not parser:
            return []

        source = ''.join(lines)
        try:
            tree = parser.parse(bytes(source, 'utf8'))
        except Exception:
            return []

        chunks = []

        def _walk(node):
            if node.type in ('function_definition', 'class_definition'):
                name = None
                for child in node.children:
                    if child.type == 'identifier':
                        name = child.text.decode('utf8')
                        break
                if name:
                    start_line = node.start_point[0] + 1
                    end_line = node.end_point[0] + 1
                    content = ''.join(lines[node.start_point[0]:node.end_point[0] + 1])
                    ctype = 'function' if node.type == 'function_definition' else 'class'
                    chunks.append(CodeChunk(
                        chunk_id=f"{rel_path}#{start_line}-{end_line}",
                        file_path=rel_path,
                        start_line=start_line,
                        end_line=end_line,
                        content=content,
                        embedding_text=self._enhance_code_embedding_text(
                            name, content, ctype, source_type
                        ),
                        chunk_type=ctype,
                        source_type=source_type,
                        language='python',
                    ))
                # Recurse into class bodies for nested methods
                if node.type == 'class_definition':
                    for child in node.children:
                        _walk(child)
            else:
                for child in node.children:
                    _walk(child)

        _walk(tree.root_node)
        return chunks

    def _chunk_cpp_ast(self, filepath: str, lines: List[str],
                       rel_path: str, source_type: str) -> List[CodeChunk]:
        parser = self._get_tree_sitter_parser(os.path.splitext(filepath)[1])
        if not parser:
            return []

        source = ''.join(lines)
        try:
            tree = parser.parse(bytes(source, 'utf8'))
        except Exception:
            return []

        chunks = []

        def _find_name(node):
            if node.type in ('identifier', 'field_identifier', 'type_identifier'):
                return node.text.decode('utf8')
            for c in node.children:
                found = _find_name(c)
                if found:
                    return found
            return None

        def _walk(node):
            if node.type in ('function_definition', 'declaration'):
                name = _find_name(node)
                if name:
                    start_line = node.start_point[0] + 1
                    end_line = node.end_point[0] + 1
                    content = ''.join(lines[node.start_point[0]:node.end_point[0] + 1])
                    chunks.append(CodeChunk(
                        chunk_id=f"{rel_path}#{start_line}-{end_line}",
                        file_path=rel_path,
                        start_line=start_line,
                        end_line=end_line,
                        content=content,
                        embedding_text=self._enhance_code_embedding_text(
                            name, content, 'function', source_type
                        ),
                        chunk_type='function',
                        source_type=source_type,
                        language='cpp',
                    ))
            elif node.type in ('class_specifier', 'struct_specifier'):
                name = _find_name(node)
                if name:
                    start_line = node.start_point[0] + 1
                    end_line = node.end_point[0] + 1
                    content = ''.join(lines[node.start_point[0]:node.end_point[0] + 1])
                    chunks.append(CodeChunk(
                        chunk_id=f"{rel_path}#{start_line}-{end_line}",
                        file_path=rel_path,
                        start_line=start_line,
                        end_line=end_line,
                        content=content,
                        embedding_text=self._enhance_code_embedding_text(
                            name, content, 'class', source_type
                        ),
                        chunk_type='class',
                        source_type=source_type,
                        language='cpp',
                    ))
            else:
                for child in node.children:
                    _walk(child)

        _walk(tree.root_node)
        return chunks

    def _chunk_markdown(self, filepath: str, lines: List[str],
                        rel_path: str, source_type: str) -> List[CodeChunk]:
        """Chunk markdown by headings; code blocks under a heading stay with it."""
        chunks = []
        current_heading = None
        current_lines: List[str] = []
        current_start = 1

        def _flush():
            nonlocal current_heading, current_lines, current_start
            if current_lines:
                content = ''.join(current_lines).strip()
                if content:
                    start = current_start
                    end = current_start + len(current_lines) - 1
                    title = current_heading or "(untitled)"
                    chunks.append(CodeChunk(
                        chunk_id=f"{rel_path}#{start}-{end}",
                        file_path=rel_path,
                        start_line=start,
                        end_line=end,
                        content=content,
                        embedding_text=f"heading {title}\n{content}",
                        chunk_type='heading',
                        source_type=source_type,
                        language='markdown',
                    ))
            current_lines = []
            current_heading = None

        for i, line in enumerate(lines):
            m = re.match(r'^(#{1,6})\s+(.+)$', line)
            if m:
                _flush()
                current_heading = m.group(2).strip()
                current_start = i + 1
                current_lines.append(line)
            else:
                current_lines.append(line)

        _flush()
        return chunks

    def _enhance_code_embedding_text(self, name: str, content: str,
                                     chunk_type: str, source_type: str) -> str:
        """Prefix code chunks with type hints and API descriptions for better embedding quality."""
        if chunk_type == 'function':
            prefix = f"function {name}: "
        elif chunk_type == 'class':
            prefix = f"class {name}: "
        else:
            prefix = ""
        # Include source_type context
        ctx = f"[{source_type}] "
        # NEW: extract signature + docstring for Python chunks
        api_desc = _extract_api_description(content)
        if api_desc:
            prefix = api_desc + "\n" + prefix
        return ctx + prefix + content


# ---------------------------------------------------------------------------
# VectorIndex
# ---------------------------------------------------------------------------
