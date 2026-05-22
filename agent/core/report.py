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
    review_count = sum(1 for decision in decisions if decision.requires_human_review)

    lines = [
        f"# Dry-run Report: {run_id}",
        "",
        "Solution: RegulaGuard Agent",
        f"Theme: {mission_input.theme}",
        f"Goal: {mission_input.goal}",
        "",
        "## Resumo executivo",
        "",
        f"- Decisions generated: {len(decisions)}",
        f"- Actions generated: {len(actions)}",
        f"- Actions allowed: {allowed_count}",
        f"- Actions blocked: {blocked_count}",
        f"- Items routed to human review: {review_count}",
        "- Scope: simulated regulatory, LGPD and contract onboarding triage.",
        "- Limits: no real contracts, no real personal data, no final legal opinion, no automatic approval or rejection.",
        "",
        "## Itens analisados",
        "",
    ]

    for decision in decisions:
        lines.extend(
            [
                f"### {decision.id} for `{decision.task_id}`",
                "",
                f"- Summary: {decision.summary}",
                f"- Item type: {decision.item_type}",
                f"- Regulatory risk: {decision.regulatory_risk}",
                f"- Confidence: {decision.confidence:.2f}",
                f"- Human review required: {decision.requires_human_review}",
                f"- Personal data categories: {', '.join(decision.personal_data_detected) or 'none detected'}",
                f"- Sensitive data categories: {', '.join(decision.sensitive_data_detected) or 'none detected'}",
                f"- Masked data: {decision.masked_data or 'none'}",
                f"- Missing documents: {', '.join(decision.missing_documents) or 'none'}",
                f"- Missing simulated clauses: {', '.join(decision.missing_contract_clauses) or 'none'}",
                f"- Decision rationale: {decision.rationale}",
                f"- Review reasons: {'; '.join(decision.review_reasons) or 'none'}",
                f"- Recommended dry-run actions: {', '.join(decision.recommended_actions) or 'none'}",
                "",
            ]
        )

    lines.extend(["", "## Acoes em dry-run", ""])

    for action in actions:
        lines.extend(
            [
                f"- {action.id}: {action.description}",
                f"  Kind: {action.kind}",
                f"  Risk: {action.regulatory_risk}",
                f"  Human review flag: {action.requires_human_review}",
                f"  Safety: {action.safety_status} - {action.safety_reason}",
            ]
        )

    lines.extend(
        [
            "",
            "## Trilha de auditoria",
            "",
            "- Input source: local simulated JSON.",
            "- Decision validation: Pydantic schemas.",
            "- Action mode: dry-run only.",
            "- Safety policy: blocks real actions, final opinions and automatic contract approval/rejection.",
            "- Human-in-the-loop: required for high/critical risk, sensitive data, low confidence and critical clause gaps.",
            "",
            "## Limites do agente",
            "",
            "- This report is not a final legal, medical or financial decision.",
            "- The agent does not approve or reject contracts automatically.",
            "- The agent does not use real contracts or real personal data.",
            "- Gemini/OpenAI are optional; the default flow uses mock and must work without internet.",
            "",
            "## Melhorias futuras",
            "",
            "- Add configurable risk matrices approved by legal/compliance teams.",
            "- Add richer simulated clause libraries without using proprietary contracts.",
            "- Add reviewer feedback loops for calibration.",
            "- Add evidence exports for regulated audit workflows.",
            "",
            "Dry-run mode did not execute external changes.",
            "",
        ]
    )
    return "\n".join(lines)
