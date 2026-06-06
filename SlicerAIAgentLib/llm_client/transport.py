from .common import *


class LLMClientTransportMixin:
    def _openRequest(self, request: urllib.request.Request):
        """Open an HTTP request with optional timeout support."""
        if self.timeout is None:
            return urllib.request.urlopen(request)
        return urllib.request.urlopen(request, timeout=self.timeout)

    def _probeConnection(self, url: str) -> bool:
        """
        Quick TCP connection probe to detect network reachability before
        making a full HTTPS request. Prints diagnostics to the Python console.
        """
        try:
            parsed = urllib.parse.urlparse(url)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            if not host:
                return False
            probe_start = time.time()
            test_sock = socket.create_connection((host, port), timeout=5)
            test_sock.close()
            elapsed = time.time() - probe_start
            if elapsed > 2.0:
                print(f"[NETWORK DIAGNOSTIC] Connection probe to {host}:{port} succeeded but took {elapsed:.1f}s. "
                      f"Slow connectivity may cause long 'thinking' states.")
            return True
        except socket.timeout:
            print(f"[NETWORK DIAGNOSTIC] Connection probe to {url} TIMED OUT after 5s. "
                  f"Likely causes: firewall blocking, DNS blackhole, GFW silent drop, or API endpoint down.")
            return False
        except OSError as e:
            print(f"[NETWORK DIAGNOSTIC] Connection probe to {url} FAILED: {e}. "
                  f"Check internet connection, proxy settings, and API base URL.")
            return False
        except Exception as e:
            print(f"[NETWORK DIAGNOSTIC] Connection probe to {url} ERROR: {e}")
            return False

    def _fetchWithDiagnostics(self, request: urllib.request.Request) -> Dict[str, Any]:
        """
        Execute a full HTTP request with a watcher thread that prints
        diagnostics to the Python console if the request hangs.
        """
        import threading
        url = request.get_full_url()
        start = time.time()
        done = threading.Event()

        def _watcher():
            thresholds = [30, 60, 120, 180]
            for t in thresholds:
                if done.wait(timeout=t):
                    return
                elapsed = time.time() - start
                print(f"[NETWORK DIAGNOSTIC] LLM API request to {url} has been waiting {int(elapsed)}s. "
                      f"Possible cause: silent packet drop, firewall/GFW blocking, DNS blackhole, or stalled TCP connection. "
                      f"If this persists, check your network, proxy, or restart Slicer.")

        watcher = threading.Thread(target=_watcher, daemon=True)
        watcher.start()

        try:
            with self._openRequest(request) as response:
                data = json.loads(response.read().decode('utf-8'))
            elapsed = time.time() - start
            if elapsed > 60:
                print(f"[NETWORK DIAGNOSTIC] LLM API request to {url} finally completed after {elapsed:.1f}s. "
                      f"Unusually slow — consider investigating network stability.")
            return data
        finally:
            done.set()

    def _streamApiCall(self, request, on_reasoning_delta=None):
        """Execute a streaming API call, accumulating the full response while
        firing on_reasoning_delta for each thinking chunk in real-time.

        Returns the same dict shape as _fetchWithDiagnostics (parsed JSON).
        """
        import threading as _threading
        url = request.get_full_url()
        start = time.time()
        done = _threading.Event()

        def _watcher():
            thresholds = [30, 60, 120, 180]
            for t in thresholds:
                if done.wait(timeout=t):
                    return
                elapsed = time.time() - start
                print(f"[NETWORK DIAGNOSTIC] LLM API request to {url} has been waiting {int(elapsed)}s. "
                      f"Possible cause: silent packet drop, firewall/GFW blocking, DNS blackhole, or stalled TCP connection. "
                      f"If this persists, check your network, proxy, or restart Slicer.")

        watcher = _threading.Thread(target=_watcher, daemon=True)
        watcher.start()

        is_claude = self._isClaude()

        try:
            content_parts: List[str] = []
            reasoning_parts: List[str] = []
            oai_tool_calls: Dict[int, Dict] = {}  # index -> {id, name, arguments_str}
            usage: Dict[str, Any] = {}
            finish_reason = None

            if is_claude:
                self._initClaudeStreamState()

            with self._openRequest(request) as response:
                for event_type, data_line in self._iterSseDataLines(response):
                    if is_claude:
                        chunk = self._parseClaudeStreamEvent(event_type, data_line)
                    else:
                        chunk = self._parseStreamChunk(data_line)

                    if chunk.get('done'):
                        break

                    if chunk.get('usage'):
                        usage = chunk['usage']
                    if chunk.get('finish_reason'):
                        finish_reason = chunk['finish_reason']

                    rc = chunk.get('reasoning_content', '')
                    ct = chunk.get('content', '')
                    if rc:
                        reasoning_parts.append(rc)
                        if on_reasoning_delta:
                            try:
                                on_reasoning_delta(rc)
                            except Exception:
                                pass
                    if ct:
                        content_parts.append(ct)

                    # Accumulate OpenAI-compatible tool_call deltas
                    if not is_claude and chunk.get('raw_chunk'):
                        raw = chunk['raw_chunk']
                        choices = raw.get('choices') or [{}]
                        delta = choices[0].get('delta', {})
                        for tc_delta in delta.get('tool_calls', []):
                            idx = tc_delta.get('index', 0)
                            if idx not in oai_tool_calls:
                                oai_tool_calls[idx] = {'id': '', 'name': '', 'arguments_str': ''}
                            entry = oai_tool_calls[idx]
                            if tc_delta.get('id'):
                                entry['id'] = tc_delta['id']
                            fn = tc_delta.get('function', {})
                            if fn.get('name'):
                                entry['name'] = fn['name']
                            if fn.get('arguments'):
                                entry['arguments_str'] += fn['arguments']

            # Build the response in the same format as _fetchWithDiagnostics
            full_content = ''.join(content_parts)
            full_reasoning = ''.join(reasoning_parts)

            message = {'content': full_content}
            if full_reasoning:
                message['reasoning_content'] = full_reasoning

            if is_claude and self._claude_tool_calls:
                tc_list = []
                for idx in sorted(self._claude_tool_calls.keys()):
                    tc = self._claude_tool_calls[idx]
                    tc_list.append({
                        'id': tc['id'],
                        'type': 'function',
                        'function': {'name': tc['name'], 'arguments': tc['arguments_str'] or '{}'},
                    })
                if tc_list:
                    message['tool_calls'] = tc_list
            elif oai_tool_calls:
                tc_list = []
                for idx in sorted(oai_tool_calls.keys()):
                    tc = oai_tool_calls[idx]
                    tc_list.append({
                        'id': tc['id'],
                        'type': 'function',
                        'function': {'name': tc['name'], 'arguments': tc['arguments_str'] or '{}'},
                    })
                if tc_list:
                    message['tool_calls'] = tc_list

            elapsed = time.time() - start
            if elapsed > 60:
                print(f"[NETWORK DIAGNOSTIC] LLM API request to {url} finally completed after {elapsed:.1f}s.")

            # Normalize usage
            if is_claude:
                normalized_usage = {
                    'prompt_tokens': usage.get('input_tokens', 0),
                    'completion_tokens': usage.get('output_tokens', 0),
                    'total_tokens': usage.get('input_tokens', 0) + usage.get('output_tokens', 0),
                }
            else:
                normalized_usage = usage

            return {
                'choices': [{'message': message, 'finish_reason': finish_reason or 'stop'}],
                'usage': normalized_usage,
            }
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='replace') if hasattr(e, 'read') else str(e)
            if e.code == 401:
                raise RuntimeError("Invalid API key.")
            raise RuntimeError(f"API request failed: {e.code} - {error_body}")
        finally:
            done.set()

    def _buildRequest(self, url: str, payload: Optional[Dict[str, Any]] = None, method: str = 'POST') -> urllib.request.Request:
        """Create an HTTP request for the LLM API."""
        data = None
        if payload is not None:
            data = json.dumps(payload).encode('utf-8')
        return urllib.request.Request(
            url,
            data=data,
            headers=self._buildHeaders(),
            method=method,
        )

    def _timeoutErrorMessage(self) -> str:
        """Build a user-facing timeout error message."""
        if self.timeout is None:
            return "Request timed out. Please check your network connection and try again."
        return f"Request timed out after {self.timeout} seconds. Please check your network connection and try again."

    def _coerceText(self, value: Any) -> str:
        """Convert streamed delta values into plain text safely."""
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            parts = []
            for item in value:
                if isinstance(item, dict):
                    if 'text' in item:
                        parts.append(str(item.get('text', '')))
                    elif 'content' in item:
                        parts.append(str(item.get('content', '')))
                    else:
                        parts.append(json.dumps(item, ensure_ascii=False))
                else:
                    parts.append(str(item))
            return ''.join(parts)
        return str(value)

    def _iterSseDataLines(self, response):
        """Yield (event_type, data_payload) tuples from a streaming HTTP response.

        For OpenAI-compatible SSE, event_type is always "".
        For Anthropic native SSE, event_type is the event name (e.g. 'content_block_delta').
        Multi-line data: fields are merged into one payload string.
        """
        event_lines: List[str] = []
        event_type: str = ""
        for raw_line in response:
            line = raw_line.decode('utf-8', errors='replace').rstrip('\r\n')
            if not line:
                if event_lines:
                    yield (event_type, '\n'.join(event_lines))
                    event_lines = []
                    event_type = ""
                continue
            if line.startswith('event:'):
                event_type = line[6:].strip()
            elif line.startswith('data:'):
                event_lines.append(line[5:].strip())
        if event_lines:
            yield (event_type, '\n'.join(event_lines))

    def _parseStreamChunk(self, data_line: str) -> Dict[str, Any]:
        """Parse one SSE data payload into content and reasoning deltas."""
        if data_line == '[DONE]':
            return {
                'done': True,
                'content': '',
                'reasoning_content': '',
                'finish_reason': 'stop',
                'usage': {},
                'raw_chunk': None,
            }

        payload = json.loads(data_line)
        choice = (payload.get('choices') or [{}])[0]
        delta = choice.get('delta') or {}
        message = choice.get('message') or {}
        content = self._coerceText(delta.get('content')) or self._coerceText(message.get('content'))
        reasoning_content = self._coerceText(delta.get('reasoning_content')) or self._coerceText(message.get('reasoning_content'))
        finish_reason = choice.get('finish_reason')

        return {
            'done': False,
            'content': content,
            'reasoning_content': reasoning_content,
            'finish_reason': finish_reason,
            'usage': payload.get('usage', {}),
            'raw_chunk': payload,
        }

    def _initClaudeStreamState(self):
        """Reset internal state for parsing a new Anthropic native SSE stream."""
        self._claude_blocks = {}       # index -> block_type (thinking/text/tool_use)
        self._claude_tool_calls = {}   # index -> {id, name, arguments_str}

    def _parseClaudeStreamEvent(self, event_type: str, data_line: str) -> Dict[str, Any]:
        """Parse one Anthropic native SSE event into content and reasoning deltas.

        Returns the same shape as _parseStreamChunk: {done, content, reasoning_content, finish_reason, usage, raw_chunk}.
        """
        if data_line == '[DONE]':
            return {'done': True, 'content': '', 'reasoning_content': '', 'finish_reason': 'stop', 'usage': {}, 'raw_chunk': None}

        payload = json.loads(data_line)
        msg_type = payload.get('type', '')

        if msg_type == 'content_block_start':
            block = payload.get('content_block', {})
            idx = payload.get('index', 0)
            block_type = block.get('type', '')
            self._claude_blocks[idx] = block_type
            if block_type == 'tool_use':
                self._claude_tool_calls[idx] = {
                    'id': block.get('id', ''),
                    'name': block.get('name', ''),
                    'arguments_str': '',
                }
            return {'done': False, 'content': '', 'reasoning_content': '', 'finish_reason': None, 'usage': {}, 'raw_chunk': payload}

        if msg_type == 'content_block_delta':
            idx = payload.get('index', 0)
            delta = payload.get('delta', {})
            delta_type = delta.get('type', '')
            block_type = self._claude_blocks.get(idx, '')

            reasoning_content = ''
            content = ''
            if delta_type == 'thinking_delta':
                reasoning_content = delta.get('thinking', '')
            elif delta_type == 'text_delta':
                content = delta.get('text', '')
            elif delta_type == 'input_json_delta':
                if idx in self._claude_tool_calls:
                    self._claude_tool_calls[idx]['arguments_str'] += delta.get('partial_json', '')

            return {'done': False, 'content': content, 'reasoning_content': reasoning_content, 'finish_reason': None, 'usage': {}, 'raw_chunk': payload}

        if msg_type == 'content_block_stop':
            return {'done': False, 'content': '', 'reasoning_content': '', 'finish_reason': None, 'usage': {}, 'raw_chunk': payload}

        if msg_type == 'message_delta':
            delta = payload.get('delta', {})
            usage = payload.get('usage', {})
            stop_reason = delta.get('stop_reason')
            return {'done': stop_reason == 'end_turn', 'content': '', 'reasoning_content': '', 'finish_reason': stop_reason, 'usage': usage, 'raw_chunk': payload}

        if msg_type == 'message_stop':
            return {'done': True, 'content': '', 'reasoning_content': '', 'finish_reason': 'stop', 'usage': {}, 'raw_chunk': payload}

        if msg_type == 'message_start':
            return {'done': False, 'content': '', 'reasoning_content': '', 'finish_reason': None, 'usage': {}, 'raw_chunk': payload}

        if msg_type == 'ping':
            return {'done': False, 'content': '', 'reasoning_content': '', 'finish_reason': None, 'usage': {}, 'raw_chunk': payload}

        return {'done': False, 'content': '', 'reasoning_content': '', 'finish_reason': None, 'usage': {}, 'raw_chunk': payload}
