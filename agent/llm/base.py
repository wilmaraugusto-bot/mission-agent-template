from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import TypeAdapter

from agent.models.schemas import Decision, MissionInput


class LLMProviderError(RuntimeError):
    """Raised when a provider cannot produce a valid decision response."""


class BaseLLMProvider(ABC):
    provider: str

    @abstractmethod
    def decide(self, mission_input: MissionInput) -> list[Decision] | list[dict[str, Any]]:
        raise NotImplementedError

    def validated_decisions(self, mission_input: MissionInput) -> list[Decision]:
        decisions = self.decide(mission_input)
        return TypeAdapter(list[Decision]).validate_python(decisions)
