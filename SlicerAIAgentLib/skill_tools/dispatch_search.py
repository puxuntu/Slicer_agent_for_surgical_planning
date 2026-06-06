from .common import *


class SkillToolDispatchSearchMixin:
    def execute(self, tool_name: str, arguments: Dict) -> Dict:
        """
        Execute a tool call.

        Args:
            tool_name: Name of the tool (SearchSymbol, Grep, ReadFile, VectorSearch)
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        import time
        start = time.time()

        if tool_name == "SearchSymbol":
            result = self._search_symbol(
                arguments.get("pattern", ""),
                arguments.get("path", ""),
                arguments.get("type", "all")
            )
        elif tool_name == "Grep":
            result = self._grep(arguments.get("pattern", ""), arguments.get("path", ""))
        elif tool_name == "ReadFile":
            result = self._readfile(
                arguments.get("path", ""),
                arguments.get("query")
            )
        elif tool_name == "VectorSearch":
            result = self._vector_search(
                arguments.get("query", ""),
                arguments.get("top_k", 10)
            )
        else:
            result = dispatch_extension_cli_tool(tool_name, arguments)
            if result is None:
                return {"error": f"Unknown tool: {tool_name}"}

        elapsed = time.time() - start
        if isinstance(result, dict):
            result["_tool_timing"] = f"{elapsed:.3f}s"

        # Normalize absolute paths in the result back to relative forward-slash paths
        if isinstance(result, dict):
            if "path" in result:
                result["path"] = self._relativize(result["path"])
            # Legacy line-by-line results (SearchSymbol / old Grep)
            if "results" in result and isinstance(result["results"], list):
                for item in result["results"]:
                    if isinstance(item, dict) and "file" in item:
                        item["file"] = self._relativize(item["file"])
            # Aggregated Grep results
            if "files" in result and isinstance(result["files"], list):
                for item in result["files"]:
                    if isinstance(item, dict) and "file" in item:
                        item["file"] = self._relativize(item["file"])
            if "representative_matches" in result and isinstance(result["representative_matches"], list):
                for item in result["representative_matches"]:
                    if isinstance(item, dict) and "file" in item:
                        item["file"] = self._relativize(item["file"])
            if "file" in result:
                result["file"] = self._relativize(result["file"])
        return result

    def _vector_search(self, query: str, top_k: int = 10) -> Dict:
        """Execute dense vector search against the pre-built index."""
        if not self._vector_retriever:
            return {
                "tool": "VectorSearch",
                "query": query,
                "error": "Vector index not available. Please build index first."
            }
        try:
            results = self._vector_retriever.search(query, top_k)
            # Filter out chunks from files already included as full files in Phase 2
            excluded = self._vector_retriever.full_file_paths
            if excluded:
                results = [rc for rc in results if rc.chunk.file_path not in excluded]
            formatted = self._vector_retriever.format_for_prompt(results)
            # Serialize results for JSON compatibility
            serializable = []
            for rc in results:
                c = rc.chunk
                serializable.append({
                    "chunk_id": c.chunk_id,
                    "file_path": c.file_path,
                    "start_line": c.start_line,
                    "end_line": c.end_line,
                    "chunk_type": c.chunk_type,
                    "source_type": c.source_type,
                    "vector_score": round(rc.vector_score, 4),
                    "final_score": round(rc.final_score, 4),
                })
            return {
                "tool": "VectorSearch",
                "query": query,
                "results": serializable,
                "formatted_context": formatted,
            }
        except Exception as e:
            logger.warning(f"Vector search failed: {e}")
            return {
                "tool": "VectorSearch",
                "query": query,
                "error": str(e),
            }

    @staticmethod
    def _is_executable_file(path: str) -> bool:
        return bool(path and os.path.isfile(path) and os.access(path, os.X_OK))

    @staticmethod
    def _run_rg_version(path: str) -> bool:
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                timeout=2,
            )
            return result.returncode == 0
        except Exception:
            return False

    def _candidate_rg_paths(self) -> List[str]:
        """Return candidate rg executable paths visible to Slicer's Python."""
        candidates = []

        for env_name in ("SLICER_AGENT_RG", "SLICER_AGENT_RG_PATH", "RIPGREP_PATH"):
            env_path = os.environ.get(env_name)
            if env_path:
                candidates.append(env_path)

        # Bundled binaries, if present.
        candidates.extend([_RG_UNIX_PATH, _RG_EXE_PATH])

        # PATH lookup from the current Slicer process environment.
        which_rg = shutil.which("rg")
        if which_rg:
            candidates.append(which_rg)

        # pip-installed console scripts may not be added to PATH inside Slicer,
        # so check Python's script directories explicitly.
        script_dirs = []
        try:
            script_dirs.append(sysconfig.get_path("scripts"))
        except Exception:
            pass
        try:
            import site
            script_dirs.append(os.path.join(site.getuserbase(), "bin"))
            script_dirs.append(os.path.join(site.getuserbase(), "Scripts"))
        except Exception:
            pass
        script_dirs.append(os.path.dirname(sys.executable))

        for script_dir in script_dirs:
            if not script_dir:
                continue
            candidates.append(os.path.join(script_dir, "rg"))
            candidates.append(os.path.join(script_dir, "rg.exe"))

        # Preserve order while removing duplicates.
        seen = set()
        unique = []
        for candidate in candidates:
            if not candidate:
                continue
            norm = os.path.normpath(candidate)
            if norm not in seen:
                unique.append(norm)
                seen.add(norm)
        return unique

    def _find_rg(self) -> Optional[str]:
        for candidate in self._candidate_rg_paths():
            if candidate == "rg":
                if self._run_rg_version(candidate):
                    return candidate
                continue
            if os.path.isfile(candidate) and not os.access(candidate, os.X_OK):
                try:
                    os.chmod(candidate, os.stat(candidate).st_mode | 0o111)
                except Exception:
                    pass
            if self._is_executable_file(candidate) and self._run_rg_version(candidate):
                return candidate
        return None

    def _install_rg(self) -> bool:
        """Install ripgrep into Slicer's Python environment when rg is missing."""
        logger.info("ripgrep executable not found; attempting to install '%s'", _RG_PIP_PACKAGE)

        # Prefer Slicer's pip_install so the package lands in Slicer's own
        # Python environment, not the system or developer shell environment.
        try:
            import slicer
            pip_install = getattr(getattr(slicer, "util", None), "pip_install", None)
            if callable(pip_install):
                pip_install(_RG_PIP_PACKAGE)
                if self._find_rg():
                    return True
        except Exception as exc:
            logger.warning("slicer.util.pip_install('%s') failed: %s", _RG_PIP_PACKAGE, exc)

        # Fallback for tests or non-Slicer runs.
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", _RG_PIP_PACKAGE],
                capture_output=True,
                timeout=180,
            )
            if result.returncode != 0:
                stderr = result.stderr.decode("utf-8", errors="ignore")[:1000]
                logger.warning("pip install %s failed: %s", _RG_PIP_PACKAGE, stderr)
                return False
            return self._find_rg() is not None
        except Exception as exc:
            logger.warning("pip install %s raised %s", _RG_PIP_PACKAGE, exc)
            return False

    def _ensure_rg(self) -> Optional[str]:
        """Find rg, install it if missing, and return the executable path."""
        rg_path = self._find_rg()
        if rg_path:
            logger.info("ripgrep available: %s", rg_path)
            return rg_path

        if self._install_rg():
            rg_path = self._find_rg()
            if rg_path:
                logger.info("ripgrep installed and available: %s", rg_path)
                return rg_path

        logger.warning(
            "ripgrep is unavailable. Grep tool calls will fail until rg is installed "
            "or SLICER_AGENT_RG points to an rg executable."
        )
        return None

    def _grep_rg_aggregate(self, pattern: str, path: str) -> Dict:
        """Aggregate ripgrep: returns per-file summary instead of line-by-line matches."""
        rg_exe = self._rg_path_cache
        if not rg_exe:
            return {"error": "ripgrep not found"}

        # Step 1: Count matches per file
        count_cmd = [
            rg_exe, "-i", "--count-matches", "--no-heading",
            pattern, path,
        ]
        try:
            count_result = subprocess.run(count_cmd, capture_output=True, timeout=15)
        except Exception as e:
            return {"error": f"ripgrep count failed: {e}"}

        file_hits = {}
        total_hits = 0
        if count_result.returncode in (0, 1):
            stdout = count_result.stdout.decode('utf-8', errors='ignore')
            for line in stdout.strip().split('\n'):
                if not line:
                    continue
                if ':' in line:
                    file_path, count_str = line.rsplit(':', 1)
                    try:
                        count = int(count_str)
                        if count > 0:
                            rel_path = self._relativize(file_path)
                            file_hits[rel_path] = count
                            total_hits += count
                    except ValueError:
                        pass
                elif os.path.isfile(path):
                    # rg --count-matches --no-heading on a single file outputs just the number
                    try:
                        count = int(line)
                        if count > 0:
                            rel_path = self._relativize(path)
                            file_hits[rel_path] = count
                            total_hits += count
                    except ValueError:
                        pass
        # Step 2: Get representative matches from top files
        sorted_files = sorted(file_hits.items(), key=lambda x: x[1], reverse=True)
        representative = []

        for file_path, _ in sorted_files[:5]:
            abs_path = self._resolve_path(file_path)
            sample_cmd = [
                rg_exe, "-H", "-n", "-i", "-B", "5", "-A", "5", "-m", "3",
                "--max-columns", "500",
                "--color", "never",
                pattern, abs_path,
            ]
            try:
                sample_result = subprocess.run(sample_cmd, capture_output=True, timeout=10)
                if sample_result.returncode in (0, 1):
                    stdout = sample_result.stdout.decode('utf-8', errors='ignore').strip()
                    if not stdout:
                        continue
                    # rg -B/-A output separates match blocks with '--'
                    blocks = []
                    current_block = []
                    for line in stdout.split('\n'):
                        if line == '--':
                            if current_block:
                                blocks.append(current_block)
                                current_block = []
                        else:
                            current_block.append(line)
                    if current_block:
                        blocks.append(current_block)

                    for block in blocks:
                        matched_line = None
                        for raw_line in block:
                            m = re.match(r'^(.+?):(\d+):(.*)$', raw_line)
                            if m:
                                line_content = m.group(3)
                                if pattern.lower() in line_content.lower():
                                    matched_line = m
                                    break
                        if not matched_line and block:
                            for raw_line in block:
                                m = re.match(r'^(.+?):(\d+):(.*)$', raw_line)
                                if m:
                                    matched_line = m
                                    break

                        if matched_line:
                            context_lines = []
                            for raw_line in block:
                                m = re.match(r'^(.+?):(\d+):(.*)$', raw_line)
                                if m:
                                    context_lines.append(m.group(3))
                                else:
                                    context_lines.append(raw_line)
                            representative.append({
                                "file": self._relativize(matched_line.group(1)),
                                "line": int(matched_line.group(2)),
                                "content": matched_line.group(3).strip(),
                                "context": '\n'.join(context_lines),
                            })
            except Exception:
                pass

        files_summary = [
            {
                "file": f,
                "hits": h,
                "source_type": self._infer_source_type(f),
            }
            for f, h in sorted_files[:20]
        ]

        return {
            "total_hits": total_hits,
            "total_files": len(file_hits),
            "files": files_summary,
            "representative_matches": representative[:10],
        }

    def _grep(self, pattern: str, path: str) -> Dict:
        """
        Search for pattern in files using ripgrep.
        Returns aggregated summary (per-file hit counts + representative matches).
        """
        path = self._resolve_path(path)

        if not os.path.exists(path):
            return {"error": f"Path not found: {path}"}

        if not self._rg_path_cache:
            return {
                "error": (
                    "ripgrep (rg) is not installed. "
                    "Please install ripgrep and ensure it is in your PATH. "
                    "Download: https://github.com/BurntSushi/ripgrep#installation"
                )
            }

        result = self._grep_rg_aggregate(pattern, path)
        if "error" in result:
            return result

        return {
            "tool": "Grep",
            "pattern": pattern,
            "path": self._relativize(path),
            **result,
        }
