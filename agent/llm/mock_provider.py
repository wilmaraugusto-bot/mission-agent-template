from __future__ import annotations

from agent.llm.base import BaseLLMProvider
from agent.models.schemas import Decision, MissionInput, MissionTask


CRITICAL_CLAUSES = {
    "confidencialidade",
    "retencao_descarte",
    "finalidade_tratamento",
    "matriz_responsabilidades",
}


def _mask_values(values: list[str]) -> dict[str, str]:
    masked: dict[str, str] = {}
    for index, value in enumerate(values, start=1):
        key = value.split(":", 1)[0].strip().lower().replace(" ", "_") or f"dado_{index}"
        masked[key] = f"[{key.upper()}_MASCARADO]"
    return masked


def _categories(values: list[str]) -> list[str]:
    categories: list[str] = []
    for index, value in enumerate(values, start=1):
        category = value.split(":", 1)[0].strip().lower().replace(" ", "_")
        categories.append(category or f"dado_{index}")
    return categories


def _item_type(task: MissionTask) -> str:
    document_type = (task.document_type or "").lower()
    description = task.description.lower()
    if "minuta" in document_type or "contrat" in document_type or "contrat" in description:
        return "minuta_contratual_simulada"
    if "documento" in description or task.missing_documents:
        return "solicitacao_administrativa_regulada"
    return "triagem_regulatoria"


def _risk_for(task: MissionTask, missing_clauses: list[str], confidence: float) -> str:
    if task.urgency == "high" and task.sensitive_data:
        return "critico"
    if confidence < 0.6:
        return "alto"
    if task.sensitive_data or CRITICAL_CLAUSES.intersection(missing_clauses):
        return "alto"
    if task.personal_data or task.missing_documents or missing_clauses:
        return "medio"
    return "baixo"


def _review_reasons(task: MissionTask, risk: str, missing_clauses: list[str], confidence: float) -> list[str]:
    reasons: list[str] = []
    if risk in {"alto", "critico"}:
        reasons.append("Risco regulatorio alto ou critico exige revisao humana.")
    if confidence < 0.6:
        reasons.append("Baixa confianca exige revisao humana.")
    if task.sensitive_data:
        reasons.append("Dados sensiveis simulados exigem postura conservadora.")
    if CRITICAL_CLAUSES.intersection(missing_clauses):
        reasons.append("Clausula critica ausente exige revisao juridica/compliance.")
    if task.missing_documents:
        reasons.append("Pendencias documentais exigem validacao administrativa.")
    return reasons


def _recommended_actions(task: MissionTask, missing_clauses: list[str], requires_review: bool) -> list[str]:
    actions = ["write_audit_record", "add_to_report", "classify_regulatory_risk"]
    if task.personal_data or task.sensitive_data:
        actions.insert(0, "mask_sensitive_data")
    if task.missing_documents:
        actions.append("request_missing_documents")
    if missing_clauses:
        actions.append("flag_missing_contract_clauses")
        actions.append("create_compliance_checklist")
    if requires_review:
        actions.append("route_to_human_review")
    return actions


class MockLLMProvider(BaseLLMProvider):
    provider = "mock"

    def decide(self, mission_input: MissionInput) -> list[Decision]:
        decisions: list[Decision] = []
        for index, task in enumerate(mission_input.tasks, start=1):
            missing_clauses = list(dict.fromkeys(task.missing_clauses))
            confidence = task.confidence_hint if task.confidence_hint is not None else 0.82
            if task.sensitive_data or task.missing_documents or missing_clauses:
                confidence = min(confidence, 0.74)
            risk = _risk_for(task, missing_clauses, confidence)
            review_reasons = _review_reasons(task, risk, missing_clauses, confidence)
            requires_review = bool(review_reasons)
            masked_data = _mask_values(task.personal_data + task.sensitive_data)
            item_type = _item_type(task)
            recommended_actions = _recommended_actions(task, missing_clauses, requires_review)

            decisions.append(
                Decision(
                    id=f"decision-{index:03d}",
                    task_id=task.id,
                    summary=(
                        f"RegulaGuard triage for {task.id}: risco {risk}, "
                        f"revisao humana {'necessaria' if requires_review else 'nao necessaria'}."
                    ),
                    rationale=(
                        "Dry-run regulatory triage over simulated data only. "
                        "The agent identifies LGPD, confidentiality, retention, "
                        "purpose and responsibility risks without issuing a final legal opinion."
                    ),
                    confidence=confidence,
                    item_type=item_type,
                    personal_data_detected=_categories(task.personal_data),
                    sensitive_data_detected=_categories(task.sensitive_data),
                    masked_data=masked_data,
                    regulatory_risk=risk,
                    missing_documents=task.missing_documents,
                    missing_contract_clauses=missing_clauses,
                    requires_human_review=requires_review,
                    review_reasons=review_reasons,
                    recommended_actions=recommended_actions,
                )
            )
        return decisions
