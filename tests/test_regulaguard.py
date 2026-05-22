from __future__ import annotations

from agent.core.report import build_report
from agent.core.safety import SafetyPolicy
from agent.llm.mock_provider import MockLLMProvider
from agent.models.schemas import Action, MissionInput, MissionTask
from agent.tools.mock_actions import MockActionPlanner


def test_sensitive_simulated_data_is_masked():
    mission_input = MissionInput(
        theme="regulaguard-test",
        goal="Validate masking.",
        tasks=[
            MissionTask(
                id="case-mask",
                description="Caso simulado com dados pessoais e sensiveis.",
                personal_data=["nome: Pessoa Ficticia", "cpf: 000.000.000-00"],
                sensitive_data=["saude: condicao simulada"],
            )
        ],
    )

    [decision] = MockLLMProvider().decide(mission_input)

    assert decision.masked_data["nome"] == "[NOME_MASCARADO]"
    assert decision.masked_data["cpf"] == "[CPF_MASCARADO]"
    assert decision.masked_data["saude"] == "[SAUDE_MASCARADO]"


def test_high_risk_requires_human_review():
    mission_input = MissionInput(
        theme="regulaguard-test",
        goal="Validate high risk routing.",
        tasks=[
            MissionTask(
                id="case-high",
                description="Caso urgente com dados sensiveis simulados.",
                sensitive_data=["saude: informacao simulada"],
                urgency="high",
            )
        ],
    )

    [decision] = MockLLMProvider().decide(mission_input)

    assert decision.regulatory_risk == "critico"
    assert decision.requires_human_review is True
    assert "route_to_human_review" in decision.recommended_actions


def test_missing_critical_clause_requires_human_review():
    mission_input = MissionInput(
        theme="regulaguard-test",
        goal="Validate contract clause guardrail.",
        tasks=[
            MissionTask(
                id="case-clause",
                description="Minuta contratual simulada sem confidencialidade.",
                document_type="minuta_contratual_simulada",
                missing_clauses=["confidencialidade"],
            )
        ],
    )

    [decision] = MockLLMProvider().decide(mission_input)

    assert decision.regulatory_risk == "alto"
    assert decision.requires_human_review is True
    assert "Clausula critica ausente" in " ".join(decision.review_reasons)


def test_prohibited_contract_decision_action_is_blocked():
    action = Action(
        id="action-prohibited",
        decision_id="decision-001",
        kind="approve_contract",
        description="Would approve contract automatically.",
        dry_run=True,
    )

    [result] = SafetyPolicy().apply([action])

    assert result.safety_status == "blocked"
    assert "blocks final legal/contract decisions" in result.safety_reason


def test_report_contains_auditability_information():
    mission_input = MissionInput(
        theme="regulaguard-test",
        goal="Validate audit report.",
        tasks=[
            MissionTask(
                id="case-report",
                description="Minuta simulada com clausula critica ausente.",
                document_type="minuta_contratual_simulada",
                personal_data=["email: exemplo@example.invalid"],
                missing_clauses=["retencao_descarte"],
            )
        ],
    )
    decisions = MockLLMProvider().decide(mission_input)
    actions = SafetyPolicy().apply(MockActionPlanner().plan(decisions))

    report = build_report("run-regulaguard", mission_input, decisions, actions)

    assert "Resumo executivo" in report
    assert "Matriz de criterios aplicada" in report
    assert "Guardrails aplicados" in report
    assert "Trilha de auditoria" in report
    assert "Dados mascarados" in report
    assert "Revisao humana necessaria: sim" in report
    assert "retencao_descarte" in report
    assert "nao e decisao juridica" in report
    assert "dry-run" in report
