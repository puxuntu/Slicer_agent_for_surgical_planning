from .common import *


class LLMClientUtilsMixin:
    def _extractCode(self, message: str) -> Optional[str]:
        """
        Extract Python code from the assistant's message.

        Args:
            message: The full response message

        Returns:
            Extracted code string or None if no code found
        """
        code_pattern = r'```python\s*\n(.*?)\n```'
        matches = re.findall(code_pattern, message, re.DOTALL)
        if matches:
            return matches[0]  # Enforce exactly one code block

        block_pattern = r'```([A-Za-z0-9_-]*)\s*\n(.*?)\n```'
        matches = re.findall(block_pattern, message, re.DOTALL)
        for language, content in matches:
            if (language or "").strip().lower() != "agent_plan":
                return content

        return None

    def _extractAgentPlan(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Extract and parse the required agent_plan JSON block from an assistant message.
        Returns None if no valid plan block is present.
        """
        plan_pattern = r'```agent_plan\s*\n(.*?)\n```'
        matches = re.findall(plan_pattern, message or "", re.DOTALL)
        if not matches:
            return None
        raw_plan = matches[0].strip()
        try:
            plan = json.loads(raw_plan)
            return plan if isinstance(plan, dict) else None
        except Exception:
            logger.warning("Failed to parse agent_plan JSON")
            return None

    def _calculateCost(self, usage: Dict[str, Any]) -> float:
        """
        Calculate the estimated cost of the API call.

        Args:
            usage: Token usage dictionary from API response

        Returns:
            Estimated cost in USD
        """
        pricing = self.MODEL_PRICING.get(self.model)
        if pricing is None:
            # Fallback: use provider-specific default pricing
            if self._isClaudeProvider():
                pricing = self.MODEL_PRICING.get("claude-3-5-sonnet-20241022", {"input": 0.003, "output": 0.015})
            elif getattr(self, 'provider', 'kimi').lower() == 'qwen':
                pricing = self.MODEL_PRICING.get("qwen3.6-plus", {"input": 0.0015, "output": 0.006})
            else:
                pricing = self.MODEL_PRICING[self.DEFAULT_MODEL]
        input_tokens = usage.get('prompt_tokens', 0)
        output_tokens = usage.get('completion_tokens', 0)
        return (input_tokens / 1000) * pricing['input'] + (output_tokens / 1000) * pricing['output']

    def getStats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            'total_tokens': self.total_tokens_used,
            'total_cost': self.total_cost,
            'conversation_length': len(self.conversation_history),
        }

    def testConnection(self) -> Dict[str, Any]:
        """
        Test API connection.

        Strategy:
        1. Try GET /models — cheap, returns available model list (OpenAI-compatible proxies).
        2. If /models is unsupported or returns non-JSON, fall back to a minimal
           chat request via validateModel() to confirm the key + model work.

        Returns:
            Dictionary with success status and available models (if returned)
        """
        if not self.api_key:
            return {'success': False, 'error': 'API key not configured'}

        # Native Anthropic API has no /models endpoint — go straight to validateModel
        if self._isAnthropicNative():
            valid = self.validateModel()
            return {
                'success': valid,
                'models': [self.model] if valid else [],
                'message': 'Connection successful' if valid else 'Connection failed',
            }

        # Try GET /models first (OpenAI-compatible endpoint)
        try:
            url = f"{self.base_url}/models"
            request = self._buildRequest(url, payload=None, method='GET')
            with self._openRequest(request) as response:
                raw = response.read().decode('utf-8').strip()
            if not raw:
                raise ValueError("Empty response from /models")
            data = json.loads(raw)
            models = [m.get('id') for m in data.get('data', []) if m.get('id')]
            return {
                'success': True,
                'models': models,
                'message': 'Connection successful',
            }
        except (urllib.error.HTTPError, urllib.error.URLError, ValueError, json.JSONDecodeError) as models_err:
            logger.warning(f"GET /models failed ({models_err}), falling back to chat probe")

        # Fallback: send a minimal chat request to confirm key + model are valid
        try:
            logger.info(f"Testing model '{self.model}' via {self._getChatUrl()}")
            valid = self.validateModel()
            if valid:
                return {
                    'success': True,
                    'models': [],   # proxy didn't expose model list
                    'message': 'Connection successful',
                }
            else:
                return {
                    'success': False,
                    'error': f"Model '{self.model}' not found on this endpoint.",
                    'message': 'Connection failed',
                }
        except RuntimeError:
            # validateModel already raised with detailed message — re-raise to surface it
            raise
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Connection failed',
            }

    def validateModel(self, model_name: str = None) -> bool:
        """
        Test if a specific model name is valid by sending a minimal request.

        Args:
            model_name: Model name to test (default: current model)

        Returns:
            True if model is accessible, False if 404
        """
        model = self._normalizeModelName(model_name or self.model)
        if not self.api_key:
            return False

        # Temporarily swap self.model so _buildPayload uses the right model name
        original_model = self.model
        self.model = model
        http_error = None
        other_error = None
        try:
            messages = [{'role': 'user', 'content': 'Hi'}]
            payload = self._buildPayload(messages, thinking=False)
            url = self._getChatUrl()
            request = self._buildRequest(url, payload)
            with self._openRequest(request):
                return True
        except urllib.error.HTTPError as e:
            http_error = e
        except Exception as e:
            other_error = e
        finally:
            self.model = original_model

        # Handle errors after finally restores self.model
        if http_error is not None:
            error_body = http_error.read().decode('utf-8', errors='ignore')
            url_hint = ""
            if '/v1' not in self.base_url:
                url_hint = f"\n  • Try adding '/v1' to your base URL: {self.base_url}/v1"
            elif self.base_url.endswith('/v1'):
                url_hint = f"\n  • Try removing '/v1' from your base URL: {self.base_url[:-3]}"
            if http_error.code == 404:
                # Include the actual error body so user can see what the server said
                logger.warning(f"Model probe 404: {error_body[:500]}")
                raise RuntimeError(
                    f"Model '{model}' not found (HTTP 404).\n\n"
                    f"Server response: {error_body[:200] if error_body else '(empty body)'}\n\n"
                    f"This proxy may use different model names. Try:\n"
                    f"  • gpt-4 (if proxy maps OpenAI names to Claude)\n"
                    f"  • claude-3-sonnet-20240229 (alternate date format)\n"
                    f"  • anthropic/claude-3-5-sonnet-20241022 (provider-prefixed){url_hint}\n"
                    f"  • Check your proxy's documentation for exact model names"
                )
            raise RuntimeError(f"HTTP {http_error.code}: {error_body}")
        if other_error is not None:
            raise other_error
        return False

    def cleanup(self):
        """Cleanup resources."""
        self.conversation_history = []
        logger.info("LLMClient cleaned up")
