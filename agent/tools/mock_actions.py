from __future__ import annotations

from agent.models.schemas import Action, Decision


class MockActionPlanner:
    def plan(self, decisions: list[Decision]) -> list[Action]:
        actions: list[Action] = []
        for index, decision in enumerate(decisions, start=1):
            actions.append(
                Action(
                    id=f"action-{index:03d}",
                    decision_id=decision.id,
                    kind="mock_review_step",
                    description=(
                        f"Would review and document the next safe step for "
                        f"{decision.task_id}."
                    ),
                    dry_run=True,
                )
            )
        return actions
