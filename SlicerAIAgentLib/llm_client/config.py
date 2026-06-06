from .common import *


class LLMClientConfigMixin:
    """
    Client configuration and prompt construction helpers.

    - Streaming response handling
    - Multi-turn conversation support
    - Token usage tracking
    - Retry logic with exponential backoff
    - Compatible with Kimi, OpenAI, and other OpenAI-compatible APIs
    """

    # API Configuration
    # Compatible with OpenAI API format
    DEFAULT_BASE_URL = "https://api.moonshot.cn/v1"
    DEFAULT_MODEL = "kimi-k2.5"
    DEFAULT_TIMEOUT = 120  # seconds; abort hung API calls instead of waiting forever
    MAX_RETRIES = 5  # Retry up to 5 times for transient errors
    LEGACY_MODEL_ALIASES = {
        "kimi-latest": DEFAULT_MODEL,
        "kimi-k2-16k": DEFAULT_MODEL,
        "kimi-2.5": DEFAULT_MODEL,
    }

    # Pricing per 1K tokens (approximate, update as needed)
    # See: https://platform.moonshot.cn/docs/pricing and https://www.anthropic.com/pricing
    MODEL_PRICING = {
        # Kimi / Moonshot models
        "kimi-k2.6": {"input": 0.0006, "output": 0.0028},
        "kimi-k2.5": {"input": 0.002, "output": 0.006},
        "kimi-k2-thinking": {"input": 0.002, "output": 0.006},
        "kimi-k2-turbo-preview": {"input": 0.001, "output": 0.003},
        "kimi-k2-0905-preview": {"input": 0.002, "output": 0.006},
        "moonshot-v1-8k": {"input": 0.001, "output": 0.002},
        "moonshot-v1-32k": {"input": 0.002, "output": 0.004},
        "moonshot-v1-128k": {"input": 0.006, "output": 0.012},
        # Claude / Anthropic models (4.6 family)
        "claude-opus-4-6": {"input": 0.015, "output": 0.075},
        "claude-opus-4-6-high": {"input": 0.015, "output": 0.075},
        "claude-opus-4-6-low": {"input": 0.015, "output": 0.075},
        "claude-opus-4-6-max": {"input": 0.015, "output": 0.075},
        "claude-opus-4-6-medium": {"input": 0.015, "output": 0.075},
        "claude-opus-4-6-thinking": {"input": 0.015, "output": 0.075},
        "claude-sonnet-4-6": {"input": 0.003, "output": 0.015},
        "claude-sonnet-4-6-high": {"input": 0.003, "output": 0.015},
        "claude-sonnet-4-6-low": {"input": 0.003, "output": 0.015},
        "claude-sonnet-4-6-max": {"input": 0.003, "output": 0.015},
        "claude-sonnet-4-6-medium": {"input": 0.003, "output": 0.015},
        "claude-sonnet-4-6-thinking": {"input": 0.003, "output": 0.015},
        "claude-haiku-4-5-20251001": {"input": 0.0008, "output": 0.004},
        "claude-haiku-4-5-20251001-thinking": {"input": 0.0008, "output": 0.004},
        # DeepSeek models
        "deepseek-v4-pro": {"input": 0.00174, "output": 0.00348},
        "deepseek-v4-flash": {"input": 0.00014, "output": 0.00028},
        # Qwen / DashScope models (Qwen3.6 / Qwen3.5 / Qwen3 series)
        # Qwen3.6 series
        "qwen3.6-max-preview": {"input": 0.003, "output": 0.012},
        "qwen3.6-plus-2026-04-02": {"input": 0.0015, "output": 0.006},
        "qwen3.6-plus": {"input": 0.0015, "output": 0.006},
        "qwen3.6-flash-2026-04-16": {"input": 0.0003, "output": 0.001},
        "qwen3.6-flash": {"input": 0.0003, "output": 0.001},
        "qwen3.6-35b-a3b": {"input": 0.0003, "output": 0.001},
        # Qwen3.5 series
        "qwen3.5-plus": {"input": 0.001, "output": 0.004},
        "qwen3.5-flash": {"input": 0.0002, "output": 0.0008},
        "qwen3.5-flash-2026-02-23": {"input": 0.0002, "output": 0.0008},
        "qwen3.5-122b-a10b": {"input": 0.001, "output": 0.004},
        "qwen3.5-397b-a17b": {"input": 0.001, "output": 0.004},
        "qwen3.5-35b-a3b": {"input": 0.0002, "output": 0.0008},
        "qwen3.5-27b": {"input": 0.0002, "output": 0.0008},
        # Qwen3 series
        "qwen3-max-2026-01-23": {"input": 0.003, "output": 0.012},
        "qwen3-max-preview": {"input": 0.003, "output": 0.012},
        "qwen3-coder-plus": {"input": 0.001, "output": 0.004},
        "qwen3-coder-flash": {"input": 0.0002, "output": 0.0008},
        # Qwen legacy aliases (latest routing)
        "qwen-plus": {"input": 0.001, "output": 0.004},
        "qwen-plus-latest": {"input": 0.001, "output": 0.004},
        "qwen-turbo": {"input": 0.0003, "output": 0.0006},
        "qwen-turbo-latest": {"input": 0.0003, "output": 0.0006},
        "qwen-flash": {"input": 0.0002, "output": 0.0008},
        "qwen-flash-latest": {"input": 0.0002, "output": 0.0008},
        "qwen-long-latest": {"input": 0.0005, "output": 0.002},
        # QwQ reasoning models
        "qwq-plus": {"input": 0.001, "output": 0.004},
        "qwq-32b": {"input": 0.0003, "output": 0.0006},
        # Claude / Anthropic models (legacy fallbacks)
        "claude-opus-4-5": {"input": 0.015, "output": 0.075},
        "claude-sonnet-4-5": {"input": 0.003, "output": 0.015},
        "claude-haiku-4-5": {"input": 0.0008, "output": 0.004},
        "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
        "claude-3-5-haiku-20241022": {"input": 0.0008, "output": 0.004},
        "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
        "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
    }

    # Path to system prompt file (relative to this file)
    SYSTEM_PROMPT_PATH = os.path.join(
        _PROJECT_ROOT,
        'Resources', 'Prompts', 'system_prompt.md'
    )

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the LLM client.

        Args:
            api_key: API key (optional, can be set later)
            model: Model name to use (default: kimi-k2.5)
        """
        self.api_key = api_key
        self.model = self._normalizeModelName(model or self.DEFAULT_MODEL)
        self.base_url = self.DEFAULT_BASE_URL
        self.provider = "kimi"
        self.timeout = self.DEFAULT_TIMEOUT
        self.conversation_history: List[Dict[str, Any]] = []
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.turn_number = 1
        self.debug_suffix = ""  # e.g., "_correction" for self-correction turns
        self.debug_output_dir: Optional[str] = None
        self._system_prompt_template = self._loadSystemPromptTemplate()

    def _normalizeModelName(self, model: Optional[str]) -> str:
        """Map legacy or empty model names to supported current model names."""
        normalized_model = (model or "").strip()
        if not normalized_model:
            return self.DEFAULT_MODEL
        return self.LEGACY_MODEL_ALIASES.get(normalized_model, normalized_model)

    def setApiKey(self, api_key: str):
        """Set or update the API key."""
        self.api_key = api_key

    def setModel(self, model: str):
        """Set the model to use."""
        self.model = self._normalizeModelName(model)

    def setBaseUrl(self, base_url: str):
        """Set a custom base URL (for enterprise deployments)."""
        self.base_url = base_url.rstrip('/')

    def setProvider(self, provider: str):
        """Set the API provider ('kimi', 'deepseek', 'claude', 'openai', or 'qwen')."""
        self.provider = (provider or "kimi").lower()

    def setDebugOutputDir(self, path: Optional[str]):
        """Set directory for per-run debug artifacts."""
        self.debug_output_dir = path

    def _debugPath(self, filename: str) -> str:
        """Return a debug artifact path, creating the output directory if needed."""
        base_dir = self.debug_output_dir or _PROJECT_ROOT
        os.makedirs(base_dir, exist_ok=True)
        return os.path.join(base_dir, filename)

    def _isAnthropicNative(self) -> bool:
        """
        Return True when the wire format should be Anthropic-native (Messages API).
        This is true ONLY when the base_url points to api.anthropic.com.
        Third-party Claude proxies (e.g. api.gpt.ge) use OpenAI-compatible format
        even though the models are Claude — so they return False here.
        """
        return 'anthropic.com' in getattr(self, 'base_url', '').lower()

    def _isClaudeProvider(self) -> bool:
        """Return True when the user selected 'Claude' as the provider (model list / pricing)."""
        return getattr(self, 'provider', 'kimi').lower() == 'claude'

    def _isClaude(self) -> bool:
        """Backward-compat alias: True only for native Anthropic API."""
        return self._isAnthropicNative()

    def _isDeepSeek(self) -> bool:
        """True for DeepSeek models that support reasoning_effort."""
        return self.model.startswith("deepseek-")

    def _isQwen(self) -> bool:
        """True for Qwen models accessed via DashScope compatible API."""
        return self.model.startswith("qwen-")

    def _isOpenAIReasoningModel(self) -> bool:
        """True for OpenAI o-series and gpt-5 reasoning models that support reasoning_effort."""
        m = self.model
        # O-series reasoning models (o1, o3, o4-mini, etc.)
        if m.startswith(("o1", "o3", "o4-")):
            return True
        # GPT-5 series reasoning models (exclude chat-only variants)
        if m.startswith("gpt-5") and "-chat-latest" not in m:
            return True
        return False

    def _isClaudeAdaptive(self) -> bool:
        """True for Claude 4.6+ models that support adaptive thinking + output_config.effort."""
        return bool(re.search(r'claude-.+-4-[6-9]\d*', self.model))

    def _getChatUrl(self) -> str:
        if self._isAnthropicNative():
            return f"{self.base_url}/messages"
        return f"{self.base_url}/chat/completions"

    def _convertMessagesForClaude(self, messages: List[Dict[str, Any]]) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        """Extract system prompt and convert OpenAI-style messages to Anthropic format."""
        system_parts: List[str] = []
        claude_messages: List[Dict[str, Any]] = []
        for m in messages:
            role = m.get('role')
            content = m.get('content', '')
            if role == 'system':
                if content:
                    system_parts.append(content)
            elif role == 'tool':
                claude_messages.append({
                    'role': 'user',
                    'content': [{
                        'type': 'tool_result',
                        'tool_use_id': m.get('tool_call_id', ''),
                        'content': content,
                    }]
                })
            elif role == 'assistant':
                tool_calls = m.get('tool_calls')
                if tool_calls:
                    blocks: List[Dict[str, Any]] = []
                    if content:
                        blocks.append({'type': 'text', 'text': content})
                    for tc in tool_calls:
                        func = tc.get('function', {})
                        args_str = func.get('arguments', '{}')
                        try:
                            args = json.loads(args_str) if isinstance(args_str, str) else args_str
                        except Exception:
                            args = {}
                        blocks.append({
                            'type': 'tool_use',
                            'id': tc.get('id', ''),
                            'name': func.get('name', ''),
                            'input': args,
                        })
                    claude_messages.append({'role': 'assistant', 'content': blocks})
                else:
                    claude_messages.append({'role': 'assistant', 'content': content})
            else:
                claude_messages.append({'role': role, 'content': content})
        system = '\n\n'.join(system_parts) if system_parts else None
        return system, claude_messages

    def _convertToolsForClaude(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        claude_tools: List[Dict[str, Any]] = []
        for t in tools:
            if t.get('type') == 'function':
                func = t.get('function', {})
                claude_tools.append({
                    'name': func.get('name', ''),
                    'description': func.get('description', ''),
                    'input_schema': func.get('parameters', {}),
                })
        return claude_tools

    def _normalizeClaudeResponse(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Anthropic Messages API response to OpenAI-compatible shape."""
        content_blocks = data.get('content', [])
        text_parts: List[str] = []
        thinking_parts: List[str] = []
        tool_calls: List[Dict[str, Any]] = []
        for block in content_blocks:
            btype = block.get('type')
            if btype == 'text':
                text_parts.append(block.get('text', ''))
            elif btype == 'thinking':
                thinking_parts.append(block.get('thinking', ''))
            elif btype == 'tool_use':
                tool_calls.append({
                    'id': block.get('id', ''),
                    'type': 'function',
                    'function': {
                        'name': block.get('name', ''),
                        'arguments': json.dumps(block.get('input', {}), ensure_ascii=False)
                    }
                })
        message: Dict[str, Any] = {
            'content': ''.join(text_parts),
            'role': 'assistant',
        }
        if thinking_parts:
            message['reasoning_content'] = '\n'.join(thinking_parts)
        if tool_calls:
            message['tool_calls'] = tool_calls
        usage_data = data.get('usage', {})
        input_tokens = usage_data.get('input_tokens', 0)
        output_tokens = usage_data.get('output_tokens', 0)
        return {
            'choices': [{'message': message}],
            'usage': {
                'prompt_tokens': input_tokens,
                'completion_tokens': output_tokens,
                'total_tokens': input_tokens + output_tokens,
            }
        }

    def clearHistory(self):
        """Clear conversation history."""
        self.conversation_history = []
        self.turn_number = 1
        logger.info("Conversation history cleared")

    def getHistory(self) -> List[Dict[str, Any]]:
        """Get current conversation history."""
        return self.conversation_history.copy()

    def setHistory(self, history: List[Dict[str, Any]]):
        """Set conversation history."""
        self.conversation_history = history

    def _buildHeaders(self) -> Dict[str, str]:
        """Build HTTP headers for API requests."""
        if not self.api_key:
            raise RuntimeError("API key not configured. Please set your API key in Settings.")

        if self._isClaude():
            return {
                "content-type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2024-10-22",
            }
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _supportsThinking(self) -> bool:
        """Return True if the current model should receive the thinking parameter."""
        if self.model.startswith("kimi-k2"):
            return True
        if self.model.startswith("deepseek-"):
            return True
        if self.model.startswith("qwen-"):
            return True
        if self.model.endswith("-thinking"):
            return True
        if self.model.startswith("claude-") and ("-4-6" in self.model or "-4-5" in self.model):
            return True
        return False

    def _buildMessages(self, prompt: str, context: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Build the messages array for the API request.

        Args:
            prompt: User's input prompt
            context: Optional skill-based context

        Returns:
            List of message dictionaries
        """
        messages: List[Dict[str, Any]] = []

        system_content = self._buildSystemPrompt(context)
        messages.append({"role": "system", "content": system_content})

        # FIFO character-based history limit: keep non-system history within 100,000 chars
        history_to_include = self._trimHistoryFIFO(self.conversation_history)
        messages.extend(history_to_include)

        messages.append({"role": "user", "content": prompt})

        # DEBUG: Write the first-turn prompt to a local file for inspection
        try:
            debug_path = self._debugPath(f'{self.turn_number}_first_prompt_debug{self.debug_suffix}.txt')
            with open(debug_path, 'w', encoding='utf-8') as f:
                total_user_msgs = sum(1 for m in messages if m.get('role') == 'user')
                users_seen = 0
                for i, msg in enumerate(messages):
                    if msg.get('role') == 'user':
                        users_seen += 1
                        turn_label = self.turn_number - total_user_msgs + users_seen
                        f.write(f"\n{'-'*40}\n")
                        f.write(f"--- Turn {turn_label} ---\n")
                        f.write(f"{'-'*40}\n")
                    f.write(f"{'='*60}\n")
                    f.write(f"MESSAGE {i+1} | role: {msg.get('role', 'unknown')}\n")
                    f.write(f"{'='*60}\n")
                    if 'tool_calls' in msg:
                        f.write("[tool_calls present]\n")
                    f.write(f"{msg.get('content', '')}\n\n")
        except Exception:
            pass  # Silently ignore debug write failures

        return messages

    def _trimHistoryFIFO(self, history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Trim conversation history to stay within 500,000 total characters.
        Uses FIFO: drops the oldest messages first. All roles count toward the limit.
        """
        MAX_HISTORY_CHARS = 500_000
        trimmed = list(history)
        total_chars = sum(len(str(m.get('content', ''))) for m in trimmed)
        while total_chars > MAX_HISTORY_CHARS and trimmed:
            removed = trimmed.pop(0)
            total_chars -= len(str(removed.get('content', '')))
        return trimmed

    def _buildPayload(self, messages: List[Dict[str, Any]], stream: bool = False, tools: Optional[List[Dict]] = None, thinking: Optional[bool] = None, reasoning_effort: str = "high") -> Dict[str, Any]:
        """Build the API payload for chat completion requests.

        Args:
            thinking: Explicitly enable/disable thinking mode. If None,
                      uses the model's default capability check.
            reasoning_effort: "low", "medium", or "high" for reasoning models.
                              Applied to DeepSeek, OpenAI o-series/gpt-5, and Claude 4.6+.
        """
        enable_thinking = self._supportsThinking() if thinking is None else thinking

        if self._isClaude():
            system, claude_messages = self._convertMessagesForClaude(messages)
            payload: Dict[str, Any] = {
                "model": self.model,
                "messages": claude_messages,
                "max_tokens": 8192,
            }
            if system:
                payload["system"] = system
            if stream:
                payload["stream"] = True
            if tools:
                payload["tools"] = self._convertToolsForClaude(tools)
            if enable_thinking:
                if self._isClaudeAdaptive():
                    # Claude 4.6+ adaptive thinking with effort control
                    payload["thinking"] = {"type": "adaptive"}
                    payload["output_config"] = {"effort": reasoning_effort}
                else:
                    # Legacy Extended Thinking (4.5 and earlier): fixed token budget
                    budget = 4096
                    payload["thinking"] = {"type": "enabled", "budget_tokens": budget}
                    payload["max_tokens"] = max(payload["max_tokens"], budget + 4096)
            return payload

        payload = {
            "model": self.model,
            "messages": messages,
        }
        if stream:
            payload["stream"] = True
        if self._supportsThinking():
            # Models like kimi-k2* and deepseek-v4* require explicit disable because default is ON
            payload["thinking"] = {"type": "enabled" if enable_thinking else "disabled"}
        elif enable_thinking:
            payload["thinking"] = {"type": "enabled"}
        # Reasoning effort for supported providers
        if enable_thinking:
            if self._isDeepSeek() or self._isOpenAIReasoningModel():
                payload["reasoning_effort"] = reasoning_effort
        if tools:
            payload["tools"] = tools
        return payload

    def _loadSystemPromptTemplate(self) -> str:
        """
        Load the system prompt template from external markdown file.

        Returns:
            System prompt template string
        """
        try:
            if os.path.exists(self.SYSTEM_PROMPT_PATH):
                with open(self.SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"Loaded system prompt from {self.SYSTEM_PROMPT_PATH}")
                return content
            else:
                logger.warning(f"System prompt file not found at {self.SYSTEM_PROMPT_PATH}, using fallback")
                return self._getFallbackSystemPrompt()
        except Exception as e:
            logger.error(f"Failed to load system prompt: {e}")
            return self._getFallbackSystemPrompt()

    def _getFallbackSystemPrompt(self) -> str:
        """
        Minimal fallback system prompt when the external file cannot be loaded.
        This should never be used in normal operation — it exists only as a
        safety net to prevent the system from crashing if the prompt file is missing.
        """
        return (
            "WARNING: The external system prompt file could not be loaded. "
            "The agent is running with a minimal fallback prompt. "
            "Please check that Resources/Prompts/system_prompt.md exists.\n\n"
            "You are an expert 3D Slicer Python coding assistant. "
            "Use Grep, ReadFile, and VectorSearch tools to find API information, then output code."
        )

    def _buildSystemPrompt(self, context: Optional[Dict] = None) -> str:
        """
        Build the comprehensive system prompt with Slicer expertise.
        Loads base prompt from external file and appends dynamic context.

        Args:
            context: Skill-based context with API hints, scene information, and tool availability

        Returns:
            System prompt string
        """
        # Start with the template from file
        base_prompt = self._system_prompt_template

        # Inject dynamic platform information
        import platform
        base_prompt += f"\n\n## PLATFORM INFORMATION\n"
        base_prompt += f"Current Platform: {platform.system()}\n"
        base_prompt += "The search tools (Grep, ReadFile, VectorSearch) handle platform differences automatically.\n"
        base_prompt += "You only need to specify the relative path within the skill directory. "
        base_prompt += "Do NOT prepend 'Resources/Skills/slicer-skill-full/' to your paths — the tool handles this automatically.\n"

        base_prompt += "\n\n## ROLE-COMPOSED AGENT PROTOCOL\n"
        base_prompt += "Operate as a single LLM agent with explicit internal roles, without adding extra dialogue turns:\n"
        base_prompt += "- Observer: use the current MRML scene context to understand available nodes and state.\n"
        base_prompt += "- Retriever: use pre-retrieved snippets and tools to ground important Slicer APIs in evidence.\n"
        base_prompt += "- Planner: produce the final agent_plan with verified steps, overall confidence, optional machine-checkable expectations, risk, and assumptions.\n"
        base_prompt += "- Programmer: produce one complete Python block that implements the plan.\n"
        base_prompt += "- Safety Critic: avoid destructive, file-writing, or high-risk operations unless the plan marks requires_confirmation=true.\n"
        base_prompt += "Do not print separate role transcripts. Encode Planner output only in the agent_plan block and Programmer output only in the python block.\n"

        base_prompt += "\n\n## REQUIRED OUTPUT FORMAT\n"
        base_prompt += "When you are ready to generate executable code, output exactly two fenced blocks in this order:\n"
        base_prompt += "1. ```agent_plan containing valid JSON.\n"
        base_prompt += "2. ```python containing the complete executable code.\n"
        base_prompt += "The agent_plan is a verified execution plan, not a guess. Include task_summary, overall_confidence, steps, risk_level, requires_confirmation, and unverified_assumptions.\n"
        base_prompt += "overall_confidence is the estimated correctness confidence for the whole plan/code path: high, medium, or low. risk_level is separate safety/complexity metadata: low, medium, or high.\n"
        base_prompt += "Each step should include action, api, confidence, and evidence.\n"
        base_prompt += "For important Slicer APIs, set confidence to high only if tool or retrieved evidence supports it. If an API still needs lookup, set confidence to low and add it to unverified_assumptions instead of pretending it is verified.\n"

        # Inject dense vector retrieval results if available
        if context and context.get('retrieval_results'):
            base_prompt += "\n\n## RELEVANT KNOWLEDGE BASE SNIPPETS\n"
            base_prompt += context['retrieval_results']
            base_prompt += "\n\nUse the above snippets as a starting point. "
            base_prompt += "If you need to confirm exact API signatures, use ReadFile or Grep.\n"

        # Add dynamic scene context
        if context and context.get('scene'):
            scene = context['scene']
            base_prompt += "\n\n## CURRENT SLICER SCENE\n"
            base_prompt += (
                "The following JSON is a structured summary of all nodes currently in the Slicer scene. "
                "Each entry includes id, name, class, visibility, and a one-line brief. "
                "Use the `GetNodeProperties` tool with a node's id if you need detailed properties "
                "(dimensions, spacing, segment names/colors, control point positions, transform matrices, "
                "display color/opacity, storage filenames) before operating on it.\n"
            )
            base_prompt += "```json\n"
            try:
                base_prompt += json.dumps(scene, ensure_ascii=False, indent=2)
            except Exception:
                base_prompt += str(scene)
            base_prompt += "\n```\n"

        # Inject dynamic extension CLI prompt fragments
        from SlicerAIAgentLib.ExtensionCLILoader import get_extension_prompt_fragments
        cli_fragments = get_extension_prompt_fragments()
        if cli_fragments:
            base_prompt += "\n\n## EXTENSION CLI TOOLS\n"
            base_prompt += cli_fragments

        # Inject extension source paths so LLM can search extension source code
        from SlicerAIAgentLib.ExtensionCLILoader import get_validated_extensions
        ext_source_info = []
        for ext_name, ext_data in get_validated_extensions().items():
            source_path = ext_data["manifest"].get("source_path", "")
            logic_class = ext_data["manifest"].get("logic_class_name", "")
            if source_path and os.path.isdir(source_path):
                entry = f"- **{ext_name}**: source at `ext:{ext_name}/`, logic class `{logic_class}`"
                ext_source_info.append(entry)
        if ext_source_info:
            base_prompt += "\n\n## EXTENSION SOURCE CODE\n"
            base_prompt += "These extensions' source code is searchable via your tools (Grep, ReadFile, VectorSearch). "
            base_prompt += "Use the `ext:<ExtensionName>/` path prefix to search extension source. "
            base_prompt += "Example: `ext:VoxTell/` to search VoxTell source, `ext:VoxTell/VoxTell.py` to read a file.\n\n"
            base_prompt += "\n".join(ext_source_info)

        # Inject cookbook-guided workflow info for interactive workflow extensions
        for ext_name, ext_data in get_validated_extensions().items():
            manifest = ext_data["manifest"]
            if manifest.get("workflow_type") == "interactive":
                base_prompt += "\n\n## COOKBOOK-GUIDED WORKFLOW\n"
                base_prompt += (
                    f"The **{ext_name}** tool follows a cookbook-driven workflow. "
                    "Steps are classified by operation type:\n"
                    "- **extension_op**: Calls this extension's own Logic methods (code from local source, no KB search)\n"
                    "- **slicer_op**: Uses Slicer core API not in this extension (needs KB search)\n"
                    "- **user_interaction**: User physically acts in 3D view (draw, position, drag)\n"
                    "- **user_choice**: Agent cannot determine value, must ask user via chat\n"
                    "- **mixed**: Combination of automated + user interaction or automated + user choice\n\n"
                    "For automated steps (extension_op, slicer_op): output code, proceed immediately.\n"
                    "For interactive/mixed+interaction steps: output pre_code, relay instructions to the user. "
                    "When the user types 'done' in the chat, call the tool again with the SAME "
                    "workflow_step and user_action='proceed'. Output the returned post_code verbatim.\n"
                    "For mixed+choice steps: output pre_code, ask the question, wait for answer, "
                    "then call with user_action='choice_made' and choice_value='<selected value>'.\n"
                    "For user_choice steps: ask the question, wait for answer, then call with "
                    "user_action='choice_made' and choice_value='<selected value>'.\n"
                )
                break

        # Inject active workflow state if one is running
        if context and context.get("workflow_state"):
            base_prompt += "\n\n## ACTIVE WORKFLOW\n"
            base_prompt += context["workflow_state"]

        return base_prompt
