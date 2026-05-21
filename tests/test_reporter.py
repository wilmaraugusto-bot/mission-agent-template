from __future__ import annotations

from agent.core.report import build_report
from agent.models.schemas import Action, Decision, MissionInput


def test_build_report_includes_summary_decisions_actions_and_safety():
    mission_input = MissionInput(
        theme="report-theme",
        goal="Build a concise report.",
        tasks=[],
    )
    decisions = [
        Decision(
            id="decision-001",
            task_id="task-001",
            summary="Mock decision",
            rationale="Because this is a dry-run.",
            confidence=0.75,
        )
    ]
    actions = [
        Action(
            id="action-001",
            decision_id="decision-001",
            kind="mock_review_step",
            description="Would review the decision.",
            dry_run=True,
            safety_status="allowed",
            safety_reason="Mock dry-run action allowed by policy.",
        )
    ]

    report = build_report("run-001", mission_input, decisions, actions)

    assert "# Dry-run Report: run-001" in report
    assert "Theme: report-theme" in report
    assert "- Decisions generated: 1" in report
    assert "- Actions allowed: 1" in report
    assert "decision-001" in report
    assert "action-001" in report
    assert "Dry-run mode did not execute external changes." in report
