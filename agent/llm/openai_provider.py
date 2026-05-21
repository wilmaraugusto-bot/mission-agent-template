from __future__ import annotations

from agent.llm.base import BaseLLMProvider, LLMProviderError
from agent.models.schemas import Decision, MissionInput


class OpenAILLMProvider(BaseLLMProvider):
    provider = "openai"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def decide(self, mission_input: MissionInput) -> list[Decision]:
        raise LLMProviderError(
            "OpenAI provider is configured but real API calls are not enabled in this template."
        )
