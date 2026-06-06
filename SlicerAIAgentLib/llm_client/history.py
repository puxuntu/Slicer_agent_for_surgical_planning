from .common import *


class LLMClientHistoryMixin:
    def _appendConversation(self, prompt: str, assistant_message: str, reasoning_content: str = ''):
        """Store user and assistant messages in local conversation history."""
        self.conversation_history.append({'role': 'user', 'content': prompt})
        assistant_entry: Dict[str, Any] = {'role': 'assistant', 'content': assistant_message}
        if reasoning_content:
            assistant_entry['reasoning_content'] = reasoning_content
        self.conversation_history.append(assistant_entry)

    def _compressReadFileResult(self, full_content: str, grep_keywords: List[str] = None) -> str:
        """ReadFile now handles slicing at the tool layer; this is a passthrough."""
        return full_content

    def _compressGrepResult(self, result_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Grep results are kept in full; no truncation is applied.
        """
        return result_data

    def _compressMessagesForGenerate(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # NOTE: This method is no longer called in _runToolLoop because
        # per-turn payload compression was removed in favor of global history trimming.
        """
        Compress ReadFile and Grep tool results in messages when conversation grows large.
        Triggered when total message length exceeds a threshold.
        """
        compressed: List[Dict[str, Any]] = []
        for msg in messages:
            if msg.get('role') == 'tool':
                try:
                    data = json.loads(msg.get('content', '{}'))
                    tool_name = data.get('tool', '')
                    if tool_name == 'ReadFile':
                        full_content = data.get('content', '')
                        data['content'] = self._compressReadFileResult(full_content)
                        data.pop('size', None)
                        new_msg = dict(msg)
                        new_msg['content'] = json.dumps(data, ensure_ascii=False)
                        compressed.append(new_msg)
                    elif tool_name == 'Grep':
                        data = self._compressGrepResult(data)
                        new_msg = dict(msg)
                        new_msg['content'] = json.dumps(data, ensure_ascii=False)
                        compressed.append(new_msg)
                    else:
                        compressed.append(msg)
                except Exception:
                    compressed.append(msg)
            else:
                compressed.append(msg)
        return compressed

    def _compressToolResultsForHistory(self, messages: List[Dict[str, Any]], user_prompt: str = '') -> List[Dict[str, Any]]:
        """
        Compress tool results before persisting them to conversation history.
        Full tool results are used within the current turn, but only a summary
        is kept for future turns to prevent context bloat.
        """
        compressed: List[Dict[str, Any]] = []
        for msg in messages:
            if msg.get('role') == 'assistant':
                # Keep assistant tool_calls messages
                compressed.append(msg)
            elif msg.get('role') == 'tool':
                try:
                    data = json.loads(msg.get('content', '{}'))
                    tool_name = data.get('tool', '')
                    if tool_name == 'ReadFile':
                        full_content = data.get('content', '')
                        # Local deterministic compression (fast, no extra API call)
                        data['content'] = self._compressReadFileResult(full_content)
                        data.pop('size', None)
                        data.pop('total_lines', None)
                        new_msg = dict(msg)
                        new_msg['content'] = json.dumps(data, ensure_ascii=False)
                        compressed.append(new_msg)
                    elif tool_name == 'Grep':
                        # Grep results are usually short; keep as-is for history
                        compressed.append(msg)
                    elif tool_name == 'VectorSearch':
                        # Drop the large formatted_context to prevent history bloat;
                        # keep the structured results list and query.
                        data.pop('formatted_context', None)
                        new_msg = dict(msg)
                        new_msg['content'] = json.dumps(data, ensure_ascii=False)
                        compressed.append(new_msg)
                    else:
                        compressed.append(msg)
                except Exception:
                    compressed.append(msg)
            else:
                # system reminders should already be excluded, but skip just in case
                if msg.get('role') != 'system':
                    compressed.append(msg)
        return compressed

    def _buildResponse(self, message: str, reasoning_content: str, usage: Dict[str, Any], raw_response: Dict[str, Any]) -> Dict[str, Any]:
        """Build the normalized response dictionary returned to callers."""
        tokens_used = usage.get('total_tokens', 0)
        self.total_tokens_used += tokens_used

        cost = self._calculateCost(usage)
        self.total_cost += cost

        code = self._extractCode(message)
        agent_plan = self._extractAgentPlan(message)

        return {
            'message': message,
            'reasoning_content': reasoning_content,
            'agent_plan': agent_plan,
            'code': code,
            'tokens': tokens_used,
            'cost': cost,
            'raw_response': raw_response,
        }
