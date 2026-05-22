from __future__ import annotations

import logging

from pydantic import ValidationError

from agent.config import Settings
from agent.llm.base import BaseLLMProvider, LLMProviderError
from agent.llm.gemini_provider import GeminiLLMProvider
from agent.llm.mock_provider import MockLLMProvider
from agent.llm.openai_provider import OpenAILLMProvider
from agent.models.schemas import Decision, MissionInput

logger = logging.getLogger(__name__)


class LLMRouter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.fallback_provider = self._build_mock_provider()

    def decide(self, mission_input: MissionInput) -> list[Decision]:
        provider_name = self.settings.llm_provider.strip().lower() or "mock"
        try:
            provider = self._provider_for(provider_name)
            if provider.provider == self.fallback_provider.provider:
                return self.fallback_provider.validated_decisions(mission_input)
            return provider.validated_decisions(mission_input)
        except (LLMProviderError, ValidationError, Exception) as exc:
            logger.warning(
                "LLM provider '%s' failed: %s; falling back to '%s'.",
                provider_name,
                self._safe_error_message(exc),
                self.fallback_provider.provider,
            )
            return self.fallback_provider.validated_decisions(mission_input)

    def _provider_for(self, provider_name: str) -> BaseLLMProvider:
        if provider_name == "mock":
            return self.fallback_provider
        if provider_name == "gemini":
            if not self.settings.gemini_api_key.strip():
                logger.warning("LLM_PROVIDER=gemini requires GEMINI_API_KEY; falling back to mock.")
                return self.fallback_provider
            return GeminiLLMProvider(
                api_key=self.settings.gemini_api_key,
                model=self.settings.gemini_model,
            )
        if provider_name == "openai":
            if not self.settings.openai_api_key.strip():
                logger.warning("LLM_PROVIDER=openai requires OPENAI_API_KEY; falling back to mock.")
                return self.fallback_provider
            return OpenAILLMProvider(api_key=self.settings.openai_api_key)

        logger.warning("Unknown LLM_PROVIDER='%s'; falling back to mock.", provider_name)
        return self.fallback_provider

    def _build_mock_provider(self) -> MockLLMProvider:
        fallback_name = self.settings.llm_fallback_provider.strip().lower() or "mock"
        if fallback_name != "mock":
            logger.warning("Only LLM_FALLBACK_PROVIDER=mock is supported; using mock.")
        return MockLLMProvider()

    def _safe_error_message(self, exc: Exception) -> str:
        message = str(exc) or exc.__class__.__name__
        secrets = [
            self.settings.gemini_api_key,
            self.settings.openai_api_key,
        ]
        for secret in secrets:
            if secret:
                message = message.replace(secret, "[REDACTED]")
        return message
