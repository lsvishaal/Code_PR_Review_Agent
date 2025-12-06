"""LLM client for Ollama integration."""

from typing import Any

import httpx
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """Configuration for LLM client."""

    base_url: str = Field(default="http://ollama:11434", description="Ollama base URL")
    model: str = Field(default="qwen2.5-coder:3b", description="Model name")
    timeout: float = Field(default=60.0, description="Request timeout in seconds")


class LLMClient:
    """Client for interacting with Ollama LLM."""

    def __init__(self, config: LLMConfig) -> None:
        """Initialize LLM client.

        Args:
            config: LLM configuration
        """
        self._config = config
        self._client = httpx.AsyncClient(base_url=config.base_url, timeout=config.timeout)

    async def generate(
        self, prompt: str, temperature: float | None = None, max_tokens: int | None = None
    ) -> str:
        """Generate text from the LLM.

        Args:
            prompt: Input prompt for the model
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response

        Raises:
            httpx.HTTPError: If the request fails
        """
        payload: dict[str, Any] = {
            "model": self._config.model,
            "prompt": prompt,
            "stream": False,
        }

        # Add deterministic parameters for consistent outputs
        payload["options"] = {
            "temperature": temperature if temperature is not None else 0.0,
            "seed": 42,  # Fixed seed for reproducibility
            "top_p": 0.1,  # Low top_p for more deterministic outputs
            "repeat_penalty": 1.1,  # Prevent repetition
        }

        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens

        response = await self._client.post("/api/generate", json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()


class FakeLLMClient:
    """Fake LLM client for testing purposes."""

    def __init__(self, responses: dict[str, str] | None = None) -> None:
        """Initialize fake LLM client.

        Args:
            responses: Dictionary mapping prompts to responses
        """
        self._responses = responses or {}

    async def generate(
        self, prompt: str, temperature: float | None = None, max_tokens: int | None = None
    ) -> str:
        """Return predetermined response for testing.

        Args:
            prompt: Input prompt
            temperature: Ignored in fake client
            max_tokens: Ignored in fake client

        Returns:
            Predetermined or default mock response
        """
        return self._responses.get(prompt, "Mock response for testing")

    async def close(self) -> None:
        """No-op close for fake client."""
        pass
