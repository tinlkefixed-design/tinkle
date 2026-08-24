from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx

from tinkle.core.config import settings
from tinkle.core.schemas import ProviderRequest, ProviderResponse


class ProviderUnavailableError(RuntimeError):
    """Raised when a configured provider cannot be used."""


class ModelProvider(ABC):
    @abstractmethod
    def generate(self, request: ProviderRequest) -> ProviderResponse:
        raise NotImplementedError


class DeferredProvider(ModelProvider):
    """Explicit compatibility provider for models without a configured adapter."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        raise ProviderUnavailableError(
            f"No executable adapter is configured for provider '{self.provider_name}'."
        )


class OpenAICompatibleProvider(ModelProvider):
    """Provider for OpenAI-compatible chat-completions APIs.

    This intentionally uses the HTTP protocol instead of a vendor SDK so that
    Tinkle can work with multiple compatible cloud or self-hosted gateways.
    """

    def __init__(
        self,
        provider_name: str,
        base_url: str,
        api_key: str,
        timeout_s: float = 120.0,
    ) -> None:
        self.provider_name = provider_name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        if not self.api_key:
            raise ProviderUnavailableError(f"API key is not configured for '{self.provider_name}'.")
        payload: dict[str, Any] = {
            "model": request.model_id,
            "messages": [{"role": "user", "content": request.prompt}],
        }
        try:
            response = httpx.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=payload,
                timeout=self.timeout_s,
            )
            response.raise_for_status()
            body = response.json()
            text = body["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as exc:
            raise ProviderUnavailableError(
                f"Provider '{self.provider_name}' request failed: {exc}"
            ) from exc
        return ProviderResponse(
            model_id=request.model_id,
            provider=self.provider_name,
            text=str(text),
            usage=body.get("usage", {}),
        )


class OllamaProvider(ModelProvider):
    """Local Ollama adapter using its native /api/chat endpoint."""

    def __init__(self, base_url: str, timeout_s: float = 120.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        payload = {
            "model": request.model_id,
            "messages": [{"role": "user", "content": request.prompt}],
            "stream": False,
        }
        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout_s,
            )
            response.raise_for_status()
            body = response.json()
            text = body["message"]["content"]
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise ProviderUnavailableError(f"Ollama request failed: {exc}") from exc
        return ProviderResponse(
            model_id=request.model_id,
            provider="local",
            text=str(text),
            usage={
                key: body[key]
                for key in ("prompt_eval_count", "eval_count")
                if key in body
            },
        )


def build_provider_map() -> dict[str, ModelProvider]:
    providers: dict[str, ModelProvider] = {
        "local": OllamaProvider(settings.local_ai_base_url),
        "cloud": OpenAICompatibleProvider(
            provider_name="cloud",
            base_url=settings.cloud_ai_base_url,
            api_key=settings.cloud_ai_api_key,
        ),
    }
    return providers
