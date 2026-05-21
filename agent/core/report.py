from __future__ import annotations

from agent.models.schemas import Action, Decision, MissionInput


def build_report(
    run_id: str,
    mission_input: MissionInput,
    decisions: list[Decision],
    actions: list[Action],
) -> str:
    allowed_count = sum(1 for action in actions if action.safety_status == "allowed")
    blocked_count = sum(1 for action in actions if action.safety_status == "blocked")

    lines = [
        f"# Dry-run Report: {run_id}",
        "",
        f"Theme: {mission_input.theme}",
        f"Goal: {mission_input.goal}",
        "",
        "## Summary",
        "",
        f"- Decisions generated: {len(decisions)}",
        f"- Actions generated: {len(actions)}",
        f"- Actions allowed: {allowed_count}",
        f"- Actions blocked: {blocked_count}",
        "",
        "## Decisions",
        "",
    ]

    for decision in decisions:
        lines.extend(
            [
                f"- {decision.id} for `{decision.task_id}`: {decision.summary}",
                f"  Rationale: {decision.rationale}",
            ]
        )

    lines.extend(["", "## Actions", ""])

    for action in actions:
        lines.extend(
            [
                f"- {action.id}: {action.description}",
                f"  Safety: {action.safety_status} - {action.safety_reason}",
            ]
        )

    lines.extend(
        [
            "",
            "## Safety",
            "",
            "Dry-run mode did not execute external changes.",
            "",
        ]
    )
    return "\n".join(lines)
