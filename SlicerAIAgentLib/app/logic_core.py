from .common import *


class LogicCoreMixin:
    def __init__(self):
        ScriptedLoadableModuleLogic.__init__(self)
        self.apiKey = None
        self.model = "kimi-k2.5"
        self.baseUrl = ""
        self.llmClient = None
        self.skill_path = None
        self.skill_mode = "unknown"
        self.codeValidator = None
        self.executor = None
        self.conversationStore = None
        self._processing = False
        self._lastInteractiveStep = None
        self._lastWorkflowStep = None
        self._initializeComponents()

    def _initializeComponents(self):
        try:
            from SlicerAIAgentLib import LLMClient, CodeValidator, SafeExecutor, ConversationStore, SkillTools, SceneTools

            self.conversationStore = ConversationStore()
            self.llmClient = LLMClient()

            # Resolve skill path relative to this module
            self.skill_path = os.path.normpath(os.path.join(
                SLICER_AI_AGENT_ROOT,
                'Resources', 'Skills', 'slicer-skill-full'
            ))
            self.skill_mode = self._detectSkillMode()

            # Initialize tool executor for skill searching
            self.toolExecutor = SkillTools.SkillToolExecutor(self.skill_path)

            # Register extension source directories as searchable roots
            from SlicerAIAgentLib.ExtensionCLILoader import get_validated_extensions
            for ext_name, ext_data in get_validated_extensions().items():
                source_path = ext_data["manifest"].get("source_path", "")
                if source_path and os.path.isdir(source_path):
                    self.toolExecutor.extra_roots[ext_name] = source_path

            # Publish this executor so other consumers (extension CLI
            # generation) reuse it instead of loading a second ONNX
            # session + vector index.
            try:
                SkillTools.register_shared_executor(self.toolExecutor)
            except Exception:
                logger.debug("Shared executor registration failed", exc_info=True)

            self.skillTools = SkillTools.get_skill_tools() + SceneTools.get_scene_tools()
            self.codeValidator = CodeValidator()
            self.executor = SafeExecutor()

            # Vector index background check
            self._indexBuilder = None
            self._index_status = "Unknown"
            self._start_index_background_check()

            # Background pre-load: import transformers and create ONNX session
            # so the first prompt doesn't block on the 4-minute import
            self._warmup_thread = self._start_vector_warmup()

            logger.info("SlicerAIAgent logic components initialized")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            logger.error(f"Failed to initialize components: {e}\n{tb}")
            # Store the error so the UI can surface it to the user
            self._initError = str(e)

    def _detectSkillMode(self):
        """Detect skill mode from .setup-stamp.json."""
        stamp_path = os.path.join(self.skill_path, ".setup-stamp.json")
        if os.path.exists(stamp_path):
            try:
                with open(stamp_path, 'r', encoding='utf-8') as f:
                    stamp = json.load(f)
                return stamp.get("mode", "unknown")
            except Exception as e:
                logger.warning(f"Failed to read setup stamp: {e}")
        return "unknown"

    def setApiKey(self, apiKey):
        self.apiKey = apiKey
        if self.llmClient:
            self.llmClient.setApiKey(apiKey)

    def setModel(self, model):
        self.model = model
        if self.llmClient:
            self.llmClient.setModel(model)

    def setBaseUrl(self, baseUrl):
        self.baseUrl = baseUrl
        if self.llmClient:
            self.llmClient.setBaseUrl(baseUrl)

    def setProvider(self, provider):
        if self.llmClient:
            self.llmClient.setProvider(provider)

    def hasApiKey(self):
        return bool(self.apiKey)

    def _getVectorRetriever(self):
        """Get the cached vector retriever if available."""
        if self.toolExecutor and self.toolExecutor.has_vector_index():
            return self.toolExecutor._vector_retriever
        if self._indexBuilder and self._indexBuilder.index_exists():
            return self._indexBuilder.load_retriever()
        return None

    def _buildRetrievalContext(self, prompt: str, timing: Optional[Dict] = None) -> str:
        """
        Perform dense vector pre-retrieval with query decomposition.
        Breaks the request into sub-task queries, runs a separate semantic
        search for each, then merges and formats the results.
        """
        import time
        t_total0 = time.time()

        # Deterministic core-UI evidence (sub-millisecond, no LLM): controls
        # whose labels match the request contribute slots/API footprints.
        # Quiet no-op when the pre-analysis artifacts are absent or nothing
        # matches confidently.
        ui_block = ""
        try:
            from SlicerAIAgentLib.UIControlIndex import format_evidence_lines, get_index
            ui_index = get_index()
            if ui_index is not None:
                ui_lines = format_evidence_lines(
                    ui_index.match(prompt, top_k=3), max_total_chars=700,
                )
                if ui_lines:
                    ui_block = (
                        "\n\n## CORE-UI EVIDENCE (deterministic, from Slicer core "
                        "UI pre-analysis)\n"
                        "These Slicer core controls match the request; prefer their "
                        "evidenced slots/API method names over remembered APIs:\n"
                        + "\n".join(ui_lines)
                    )
                if timing is not None:
                    timing['ui_evidence_count'] = len(ui_lines)
        except Exception:
            logger.debug("Core-UI evidence lookup failed", exc_info=True)

        try:
            t_get0 = time.time()
            retriever = self._getVectorRetriever()
            t_get = time.time() - t_get0
            if not retriever or not retriever.is_ready():
                return ui_block

            from concurrent.futures import ThreadPoolExecutor

            def _timed_search(query):
                q_start = time.time()
                try:
                    results = retriever.search(query, top_k=10)
                except Exception as exc:
                    logger.warning(f"Pre-retrieval search failed for '{query}': {exc}")
                    results = []
                return results, round(time.time() - q_start, 3)

            # Steps 1+2 overlapped: the raw-prompt search runs DURING the
            # decompose LLM call, and sub-query searches run in parallel.
            # Result ordering and per-query timing entries are identical to
            # the previous sequential implementation.
            all_results = []
            per_query = []
            raw_prefetch_reused = False
            with ThreadPoolExecutor(max_workers=4) as pool:
                raw_future = pool.submit(_timed_search, prompt)

                t0 = time.time()
                sub_queries = self.llmClient.decomposeQuery(prompt)
                t1 = time.time()

                futures = []
                for sq in sub_queries:
                    if sq == prompt:
                        futures.append(raw_future)
                        raw_prefetch_reused = True
                    else:
                        futures.append(pool.submit(_timed_search, sq))
                for sq, future in zip(sub_queries, futures):
                    results, q_time = future.result()
                    all_results.append(results)
                    per_query.append({
                        'query': sq,
                        'count': len(results),
                        'time': q_time,
                    })

            # Step 3: Concatenate all per-query results and format
            t_merge0 = time.time()
            concatenated: List[Any] = []
            for res in all_results:
                concatenated.extend(res)

            # ---- Full-file inclusion for heavily-referenced .md files ----
            # Count chunks per file path
            from collections import Counter
            file_counts = Counter(rc.chunk.file_path for rc in concatenated)
            # Identify .md files with >= 3 chunks
            full_md_files = [
                fp for fp, cnt in file_counts.items()
                if cnt >= 3 and fp.lower().endswith('.md')
            ]
            if full_md_files and self.toolExecutor:
                from SlicerAIAgentLib.SkillIndexer import CodeChunk, RetrievedChunk
                skill_root = self.toolExecutor.skill_path
                for fp in full_md_files:
                    abs_path = os.path.join(skill_root, fp)
                    if not os.path.exists(abs_path):
                        continue
                    try:
                        with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                            full_content = f.read()
                        total_lines = full_content.count('\n') + 1
                        # Determine dominant source_type from existing chunks
                        source_types = [rc.chunk.source_type for rc in concatenated if rc.chunk.file_path == fp]
                        dominant_source = Counter(source_types).most_common(1)[0][0] if source_types else 'doc_example'
                        # Remove all individual chunks from this file
                        concatenated = [rc for rc in concatenated if rc.chunk.file_path != fp]
                        # Create synthetic whole-file chunk
                        synthetic_chunk = CodeChunk(
                            chunk_id=f"{fp}#full",
                            file_path=fp,
                            start_line=1,
                            end_line=total_lines,
                            content=full_content,
                            embedding_text="",
                            chunk_type="whole_file",
                            source_type=dominant_source,
                            language="markdown",
                        )
                        synthetic_rc = RetrievedChunk(
                            chunk=synthetic_chunk,
                            vector_score=1.0,
                            final_score=1.5,
                        )
                        concatenated.append(synthetic_rc)
                        retriever.full_file_paths.add(fp)
                    except Exception as e:
                        logger.warning(f"Failed to include full file {fp}: {e}")
                # Re-sort by final_score descending so full files appear near top
                concatenated.sort(key=lambda rc: rc.final_score, reverse=True)

            t_merge = time.time() - t_merge0
            formatted = retriever.format_for_prompt(concatenated)
            # Prepend the sub-queries so the LLM knows what topics were already searched
            if sub_queries:
                search_note = (
                    "## Pre-retrieval search coverage\n"
                    "The following topics were already searched automatically. "
                    "You do NOT need to call VectorSearch for these same topics again. "
                    "Only use tools for gaps not covered below.\n"
                    + '\n'.join(f"- {sq}" for sq in sub_queries)
                    + "\n\n"
                )
                formatted = search_note + formatted
            total_t = time.time() - t_total0

            if timing is not None:
                timing['decompose_time'] = round(t1 - t0, 3)
                timing['decompose_thinking'] = False
                timing['sub_queries'] = sub_queries
                timing['retrieval_count'] = len(sub_queries)
                timing['retrieval_per_query'] = per_query
                timing['concatenated_count'] = len(concatenated)
                timing['retrieval_parallel'] = True
                timing['retrieval_wall_time'] = round(total_t, 3)
                timing['raw_prompt_prefetch_reused'] = raw_prefetch_reused

            return formatted + ui_block
        except Exception as e:
            import traceback
            traceback.print_exc()
            logger.warning(f"Dense pre-retrieval failed: {e}")
            return ui_block

    @staticmethod
    def _isWorkflowControlTurn(prompt: str, context: Optional[Dict] = None) -> bool:
        """Return True for active-workflow turns that should not pre-retrieve.

        Generated extension CLI workflows already carry validated templates and
        metadata.  For simple control turns, dense pre-retrieval adds latency
        without improving the next action.  Tool access remains enabled later in
        the turn for correction or unexpected error handling.
        """
        if not context or not context.get("workflow_state"):
            return False
        from SlicerAIAgentLib.TurnRouter import is_workflow_control_turn
        workflow_state = {
            "active": True,
            "current_step": None,
            "status": "running",
        }
        match = re.search(r"Current step:\s*(cb_step_\d+)", str(context.get("workflow_state", "")))
        if match:
            workflow_state["current_step"] = match.group(1)
        return is_workflow_control_turn(prompt, workflow_state)

    def generateResponse(self, prompt):
        """
        Generate AI response (non-streaming).

        Args:
            prompt: User's natural language request

        Returns:
            dict with keys: message, reasoning_content, code, tokens, cost
        """
        if not self.llmClient:
            raise RuntimeError("LLM client not initialized")
        if not self.apiKey:
            raise RuntimeError("API key not configured")

        context = {"scene": self._buildSceneContext()}
        retrieval_timing = {}
        retrieval = self._buildRetrievalContext(prompt, retrieval_timing)
        if retrieval:
            context["retrieval_results"] = retrieval
        response = self.llmClient.chat(prompt, context=context)
        response['retrieval_timing'] = retrieval_timing
        self.conversationStore.addExchange(prompt, response)
        return response

    def generateResponseStream(self, prompt, context=None, on_delta=None, use_tools=True, on_status=None, on_reasoning=None, on_reasoning_delta=None):
        """
        Generate AI response using streaming with optional tool calling.

        This runs the actual HTTP request (blocking I/O).  Callers should
        invoke this from a background thread.

        Args:
            prompt: User's natural language request
            context: Pre-built skill context (or None to build here)
            on_delta: Callback for incremental updates
            use_tools: Whether to use tool calling for skill search
            on_status: Callback for status updates (str) — 'Retrieving...', 'Thinking...', etc.

        Returns:
            dict with keys: message, reasoning_content, code, tokens, cost
        """
        if not self.llmClient:
            raise RuntimeError("LLM client not initialized")
        if not self.apiKey:
            raise RuntimeError("API key not configured")

        if context is None:
            context = {"scene": self._buildSceneContext()}

        # Inject dense vector retrieval results if not already present
        retrieval_timing = {}
        if (
            "retrieval_results" not in context
            and not self._isWorkflowControlTurn(prompt, context)
        ):
            if on_status:
                on_status("Retrieving...")
            retrieval = self._buildRetrievalContext(prompt, retrieval_timing)
            if retrieval:
                context["retrieval_results"] = retrieval
        elif "retrieval_results" not in context:
            retrieval_timing["skipped"] = True
            retrieval_timing["skip_reason"] = "active_workflow_control_turn"
        retrieval_timing["used_tool_loop"] = bool(use_tools and self.toolExecutor and self.skillTools)

        if use_tools and self.toolExecutor and self.skillTools:
            # Use tool calling for skill search
            try:
                if on_status:
                    on_status("Thinking...")
                # Progress callback to show tool execution in real-time
                def _on_progress(progress):
                    if on_delta:
                        on_delta(progress)

                response = self.llmClient.chatWithTools(
                    prompt,
                    tools=self.skillTools,
                    tool_executor=self._executeTool,
                    context=context,
                    on_progress=_on_progress,
                    on_status=on_status,
                    on_reasoning=on_reasoning,
                    on_reasoning_delta=on_reasoning_delta,
                )

                # Tool calling returns complete response (no streaming during tool rounds).
                # Final code generation is non-streaming; the UI displays the complete result.
            except Exception as e:
                logger.warning(f"Tool calling failed, falling back to regular chat: {e}")
                response = self.llmClient.chatStream(prompt, context=context, on_delta=on_delta, on_status=on_status)
        else:
            # Fallback to regular streaming
            response = self.llmClient.chatStream(prompt, context=context, on_delta=on_delta, on_status=on_status)

        response['retrieval_timing'] = retrieval_timing
        self.conversationStore.addExchange(prompt, response)
        return response

    def addExecutionFeedback(self, feedback_text):
        """
        Append code execution feedback to the LLM conversation history.
        Only keeps the most recent 2 feedback messages to prevent context bloat.
        """
        if not self.llmClient:
            return

        history = self.llmClient.conversation_history
        MAX_FEEDBACK = 2

        # Find indices of existing execution feedback messages
        feedback_indices = [
            i for i, msg in enumerate(history)
            if msg.get('role') == 'system'
            and msg.get('content', '').startswith('Code execution result:')
        ]

        # Remove oldest ones, keeping at most (MAX_FEEDBACK - 1) recent ones
        # We delete from back to front so indices don't shift underneath us
        to_remove = feedback_indices[:-(MAX_FEEDBACK - 1)] if len(feedback_indices) >= MAX_FEEDBACK else []
        for idx in reversed(to_remove):
            history.pop(idx)

        history.append({
            "role": "system",
            "content": feedback_text,
        })

    def _executeTool(self, tool_name, tool_args):
        """
        Execute a tool call.

        Args:
            tool_name: Name of the tool (Grep, ReadFile, VectorSearch, GetNodeProperties)
            tool_args: Tool arguments dict

        Returns:
            Tool execution result dict
        """
        # Scene introspection tools (do not require skill executor)
        if tool_name == "GetNodeProperties":
            try:
                from SlicerAIAgentLib import SceneTools
                ids = tool_args.get("ids", [])
                if isinstance(ids, str):
                    ids = [ids]
                if not ids:
                    return {
                        "error": (
                            "GetNodeProperties was called with an empty ids list. "
                            "Do NOT call this tool unless you have specific node IDs from the scene summary. "
                            "If the scene summary is missing, proceed with the information you have."
                        )
                    }
                results = {}
                for node_id in ids:
                    results[node_id] = SceneTools.getNodeProperties(node_id)
                return {
                    "tool": "GetNodeProperties",
                    "results": results,
                    "count": len(results),
                }
            except Exception as e:
                logger.error(f"GetNodeProperties failed: {e}")
                return {"error": str(e)}

        if not self.toolExecutor:
            return {"error": "Tool executor not initialized"}

        try:
            result = self.toolExecutor.execute(tool_name, tool_args)
            # Log tool execution for debugging
            logger.info(f"Tool {tool_name} executed: {tool_args.get('pattern', tool_args.get('path', tool_args.get('ids', 'N/A')))}")

            # Track interactive/mixed/user_choice workflow dispatch results for the Widget
            if isinstance(result, dict) and result.get("type") in ("interactive", "mixed", "user_choice"):
                self._lastInteractiveStep = result
            # Track all workflow step dispatches (including automated) for auto-advance
            if isinstance(result, dict) and result.get("step_id") and result.get("tool"):
                self._lastWorkflowStep = result

            return result
        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name} - {e}")
            return {"error": str(e)}
