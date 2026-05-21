from __future__ import annotations

from agent.llm.base import BaseLLMProvider
from agent.models.schemas import Decision, MissionInput


class MockLLMProvider(BaseLLMProvider):
    provider = "mock"

    def decide(self, mission_input: MissionInput) -> list[Decision]:
        decisions: list[Decision] = []
        for index, task in enumerate(mission_input.tasks, start=1):
            decisions.append(
                Decision(
                    id=f"decision-{index:03d}",
                    task_id=task.id,
                    summary=f"Mock decision for {task.id}",
                    rationale=(
                        "Dry-run mock decision based on the provided mission input "
                        "and safety-first execution constraints."
                    ),
                    confidence=0.75,
                )
            )
        return decisions
