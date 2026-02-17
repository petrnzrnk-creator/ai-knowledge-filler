#!/usr/bin/env python3
"""
Multi-LLM Provider Architecture for AI Knowledge Filler.

Supports:
- Groq (Llama 3.3 - fast inference)
- Grok (xAI)
- Claude (Anthropic)
- Gemini (Google)
- GPT-3.5 (OpenAI)
- Ollama (local models)
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Type


# ─── BASE PROVIDER ────────────────────────────────────────────────────────────


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str) -> str:
        """Generate content from user prompt with system instructions.

        Args:
            prompt: User's generation request.
            system_prompt: System instructions for the LLM.

        Returns:
            Generated markdown content.

        Raises:
            Exception: If generation fails.
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and ready to use.

        Returns:
            True if API key is set and library is installed.
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier (e.g., 'claude', 'gemini')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable provider name (e.g., 'Claude (Anthropic)')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Model identifier used by the provider."""
        pass


# ─── CLAUDE PROVIDER ──────────────────────────────────────────────────────────


class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Claude provider.

        Args:
            api_key: Anthropic API key. If None, uses ANTHROPIC_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

    def generate(self, prompt: str, system_prompt: str) -> str:
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic library not installed. Run: pip install anthropic"
            )

        client = anthropic.Anthropic(api_key=self.api_key)

        response = client.messages.create(
            model=self.model_name,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            import anthropic  # noqa: F401

            return True
        except ImportError:
            return False

    @property
    def name(self) -> str:
        return "claude"

    @property
    def display_name(self) -> str:
        return "Claude (Anthropic)"

    @property
    def model_name(self) -> str:
        return "claude-sonnet-4-20250514"


# ─── GEMINI PROVIDER ──────────────────────────────────────────────────────────


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini provider.

        Args:
            api_key: Google API key. If None, uses GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")

    def generate(self, prompt: str, system_prompt: str) -> str:
        try:
            from google import genai
            from google.genai import types
        except ImportError:
            raise ImportError(
                "google-genai library not installed. Run: pip install google-genai"
            )

        client = genai.Client(api_key=self.api_key)

        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt, temperature=0.7
            ),
        )

        return response.text

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            from google import genai  # noqa: F401

            return True
        except ImportError:
            return False

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def display_name(self) -> str:
        return "Gemini (Google)"

    @property
    def model_name(self) -> str:
        return "gemini-3-flash-preview"


# ─── OPENAI PROVIDER ──────────────────────────────────────────────────────────


class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4 provider."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key. If None, uses OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

    def generate(self, prompt: str, system_prompt: str) -> str:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai library not installed. Run: pip install openai")

        client = OpenAI(api_key=self.api_key)

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=4096,
            temperature=0.7,
        )

        return response.choices[0].message.content

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            from openai import OpenAI  # noqa: F401

            return True
        except ImportError:
            return False

    @property
    def name(self) -> str:
        return "gpt4"

    @property
    def display_name(self) -> str:
        return "GPT-3.5 (OpenAI)"

    @property
    def model_name(self) -> str:
        return "gpt-3.5-turbo"


# ─── OLLAMA PROVIDER ──────────────────────────────────────────────────────────


class OllamaProvider(LLMProvider):
    """Ollama local models provider."""

    def __init__(self, model: Optional[str] = None):
        """Initialize Ollama provider.

        Args:
            model: Ollama model name. If None, uses OLLAMA_MODEL env var or default.
        """
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def generate(self, prompt: str, system_prompt: str) -> str:
        try:
            import requests
        except ImportError:
            raise ImportError("requests library not installed. Run: pip install requests")

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": f"{system_prompt}\n\n{prompt}",
            "stream": False,
        }

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()["response"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {e}")

    def is_available(self) -> bool:
        try:
            import requests

            # Check if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def display_name(self) -> str:
        return f"Ollama ({self.model})"

    @property
    def model_name(self) -> str:
        return self.model


# ─── GROQ PROVIDER ────────────────────────────────────────────────────────


class GroqProvider(LLMProvider):
    """Groq fast inference provider."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Groq provider.

        Args:
            api_key: Groq API key. If None, uses GROQ_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

    def generate(self, prompt: str, system_prompt: str) -> str:
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("groq library not installed. Run: pip install groq")

        client = Groq(api_key=self.api_key)

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=4096,
            temperature=0.7,
        )

        return response.choices[0].message.content

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            from groq import Groq  # noqa: F401

            return True
        except ImportError:
            return False

    @property
    def name(self) -> str:
        return "groq"

    @property
    def display_name(self) -> str:
        return "Groq (Llama 3.3)"

    @property
    def model_name(self) -> str:
        return "llama-3.3-70b-versatile"


# ─── XAI PROVIDER ─────────────────────────────────────────────────────────


class XAIProvider(LLMProvider):
    """xAI Grok provider."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize xAI provider.

        Args:
            api_key: xAI API key. If None, uses XAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY")

    def generate(self, prompt: str, system_prompt: str) -> str:
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai library not installed. Run: pip install openai")

        # xAI uses OpenAI-compatible API
        client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1",
        )

        response = client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            max_tokens=4096,
            temperature=0.7,
        )

        return response.choices[0].message.content

    def is_available(self) -> bool:
        if not self.api_key:
            return False
        try:
            from openai import OpenAI  # noqa: F401

            return True
        except ImportError:
            return False

    @property
    def name(self) -> str:
        return "grok"

    @property
    def display_name(self) -> str:
        return "Grok (xAI)"

    @property
    def model_name(self) -> str:
        return "grok-beta"


# ─── PROVIDER REGISTRY ────────────────────────────────────────────────────────


PROVIDERS: Dict[str, Type[LLMProvider]] = {
    "claude": ClaudeProvider,
    "gemini": GeminiProvider,
    "gpt4": OpenAIProvider,
    "groq": GroqProvider,
    "grok": XAIProvider,
    "ollama": OllamaProvider,
}


def get_provider(name: str = "auto") -> LLMProvider:
    """Get LLM provider by name or auto-select first available.

    Args:
        name: Provider name ('claude', 'gemini', 'gpt4', 'ollama', 'auto').

    Returns:
        Initialized provider instance.

    Raises:
        ValueError: If provider not found or not available.
    """
    if name == "auto":
        # Try providers in priority order (fast and free-tier friendly first)
        for provider_name in ["groq", "grok", "claude", "gemini", "gpt4", "ollama"]:
            provider_class = PROVIDERS[provider_name]
            provider = provider_class()
            if provider.is_available():
                return provider
        raise ValueError(
            "No LLM providers available. Set API keys: "
            "GROQ_API_KEY, XAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, "
            "OPENAI_API_KEY, or run Ollama."
        )

    if name not in PROVIDERS:
        raise ValueError(
            f"Unknown provider: {name}. Available: {', '.join(PROVIDERS.keys())}"
        )

    provider_class = PROVIDERS[name]
    provider = provider_class()

    if not provider.is_available():
        raise ValueError(
            f"Provider '{name}' not available. "
            f"Check API key and dependencies for {provider.display_name}."
        )

    return provider


def list_providers() -> Dict[str, bool]:
    """List all providers and their availability status.

    Returns:
        Dict mapping provider name to availability boolean.
    """
    return {name: cls().is_available() for name, cls in PROVIDERS.items()}
