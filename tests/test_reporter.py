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

    assert "# Relatorio dry-run: run-001" in report
    assert "Tema: report-theme" in report
    assert "- Decisoes geradas: 1" in report
    assert "- Acoes permitidas: 1" in report
    assert "decision-001" in report
    assert "action-001" in report
    assert "Resumo executivo" in report
    assert "Matriz de criterios aplicada" in report
    assert "Guardrails aplicados" in report
    assert "Trilha de auditoria" in report
    assert "Revisao humana" in report
    assert "dry-run" in report
