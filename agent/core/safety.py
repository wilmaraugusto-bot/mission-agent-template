from __future__ import annotations

from agent.models.schemas import Action


class SafetyPolicy:
    allowed_kinds = {"mock_review_step", "mock_documentation_step"}

    def apply(self, actions: list[Action]) -> list[Action]:
        safe_actions: list[Action] = []
        for action in actions:
            if not action.dry_run:
                safe_actions.append(
                    action.model_copy(
                        update={
                            "safety_status": "blocked",
                            "safety_reason": "Only dry-run actions are allowed.",
                        }
                    )
                )
                continue

            if action.kind not in self.allowed_kinds:
                safe_actions.append(
                    action.model_copy(
                        update={
                            "safety_status": "blocked",
                            "safety_reason": f"Action kind '{action.kind}' is not allowed.",
                        }
                    )
                )
                continue

            safe_actions.append(
                action.model_copy(
                    update={
                        "safety_status": "allowed",
                        "safety_reason": "Mock dry-run action allowed by policy.",
                    }
                )
            )
        return safe_actions
