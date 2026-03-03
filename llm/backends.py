# llm/backends.py
# LLM provider abstraction layer

from typing import Optional


class LLMBackend:
    """Base class for LLM providers.

    Each provider implements call() with its own SDK.
    Subclasses should lazy-import their SDK inside call()
    for graceful error handling when the SDK is not installed.
    """

    def __init__(self, api_key: str, default_model: str):
        self.api_key = api_key
        self.default_model = default_model

    def call(self, system_prompt: str, user_prompt: str,
             model: Optional[str] = None) -> str:
        """Send prompts to the LLM and return the response text.

        Args:
            system_prompt: System/persona instructions.
            user_prompt: User message with plate data and purpose.
            model: Override model name. Uses default if None.

        Returns:
            The LLM's response text.
        """
        raise NotImplementedError


class AnthropicBackend(LLMBackend):
    """Anthropic Claude API backend."""

    def __init__(self, api_key: str,
                 default_model: str = "claude-sonnet-4-6"):
        super().__init__(api_key, default_model)

    def call(self, system_prompt: str, user_prompt: str,
             model: Optional[str] = None) -> str:
        from anthropic import Anthropic

        client = Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=model or self.default_model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text


# --- PENDING BACKENDS ---
# To add a new provider:
# 1. Create a subclass of LLMBackend
# 2. Implement call() with lazy SDK import
# 3. Register in BACKEND_REGISTRY below
# 4. Add API key name to interpreter.py KEY_NAMES

class OpenAIBackend(LLMBackend):
    """OpenAI API backend. (Pending implementation)"""

    def __init__(self, api_key: str, default_model: str = "gpt-4o"):
        super().__init__(api_key, default_model)

    def call(self, system_prompt: str, user_prompt: str,
             model: Optional[str] = None) -> str:
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=model or self.default_model,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content


class GeminiBackend(LLMBackend):
    """Google Gemini API backend. (Pending implementation)"""

    def __init__(self, api_key: str,
                 default_model: str = "gemini-2.0-flash"):
        super().__init__(api_key, default_model)

    def call(self, system_prompt: str, user_prompt: str,
             model: Optional[str] = None) -> str:
        from google import genai

        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=model or self.default_model,
            contents=user_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                max_output_tokens=4096,
            ),
        )
        return response.text


# Registry mapping provider names to (BackendClass, api_key_env_name)
BACKEND_REGISTRY = {
    'anthropic': (AnthropicBackend, 'ANTHROPIC_API_KEY'),
    'openai': (OpenAIBackend, 'OPENAI_API_KEY'),
    'gemini': (GeminiBackend, 'GEMINI_API_KEY'),
}
