from __future__ import annotations

from agent.models.schemas import Action, Decision, MissionInput


def _format_list(values: list[str], empty: str = "nenhum") -> str:
    return ", ".join(values) if values else empty


def _format_bool(value: bool) -> str:
    return "sim" if value else "nao"


def _format_masked(masked_data: dict[str, str]) -> str:
    if not masked_data:
        return "nenhum"
    return ", ".join(f"{key}: {value}" for key, value in masked_data.items())


def _specific_rationale(decision: Decision) -> str:
    reasons: list[str] = []
    personal_categories = set(decision.personal_data_detected)
    sensitive_categories = set(decision.sensitive_data_detected)
    missing_clauses = set(decision.missing_contract_clauses)

    if personal_categories.intersection({"cpf", "email", "nome"}):
        reasons.append(
            "ha CPF, email ou nome simulado, portanto o caso exige mascaramento antes de registro e revisao."
        )
    elif decision.personal_data_detected:
        reasons.append(
            "ha dados pessoais simulados, portanto o relatorio mostra categorias e valores mascarados."
        )

    if "confidencialidade" in missing_clauses:
        reasons.append(
            "a ausencia de confidencialidade cria risco contratual/compliance e exige revisao juridica."
        )
    if "retencao_descarte" in missing_clauses:
        reasons.append(
            "a ausencia de retencao/descarte cria risco no ciclo de vida dos dados."
        )
    if "finalidade_tratamento" in missing_clauses:
        reasons.append(
            "a ausencia de finalidade de tratamento dificulta avaliar minimizacao e base do tratamento."
        )
    if "matriz_responsabilidades" in missing_clauses:
        reasons.append(
            "a ausencia de matriz de responsabilidades impede identificar responsaveis por mitigacao."
        )

    if sensitive_categories.intersection({"saude", "id_paciente"}):
        reasons.append(
            "ha dado sensivel simulado de saude, entao a revisao humana e obrigatoria."
        )
    elif decision.sensitive_data_detected:
        reasons.append(
            "ha dado sensivel simulado, entao o agente adota postura conservadora."
        )

    if decision.missing_documents:
        reasons.append("ha documentos ausentes que precisam de complemento administrativo.")

    if decision.confidence < 0.6:
        reasons.append("a confianca esta baixa, exigindo revisao humana antes de qualquer encaminhamento.")

    if decision.regulatory_risk == "baixo" and not decision.requires_human_review:
        reasons.append(
            "o risco e baixo porque nao foram detectados dados sensiveis, documentos ausentes ou clausulas criticas ausentes."
        )

    if not reasons:
        reasons.append(decision.rationale)

    return " ".join(reasons)


def _action_status(status: str) -> str:
    translations = {
        "allowed": "permitida",
        "blocked": "bloqueada",
        "pending": "pendente",
    }
    return translations.get(status, status)


def _decision_summary(decision: Decision) -> str:
    review_text = "com revisao humana necessaria" if decision.requires_human_review else "sem revisao humana obrigatoria"
    return (
        f"Triagem RegulaGuard para {decision.task_id}: risco {decision.regulatory_risk}, "
        f"{review_text}."
    )


def _action_description(action: Action) -> str:
    details = action.audit_details
    task_id = details.get("task_id", action.decision_id)
    missing_documents = _format_list(details.get("missing_documents", []))
    missing_clauses = _format_list(details.get("missing_contract_clauses", []))
    descriptions = {
        "mask_sensitive_data": (
            f"Simular mascaramento de dados pessoais/sensiveis de {task_id} antes de revisao ou relatorio."
        ),
        "classify_regulatory_risk": (
            f"Registrar classificacao de risco regulatorio {action.regulatory_risk} para {task_id}."
        ),
        "request_missing_documents": (
            f"Simular solicitacao de documentos ausentes para {task_id}: {missing_documents}."
        ),
        "flag_missing_contract_clauses": (
            f"Sinalizar clausulas contratuais simuladas ausentes em {task_id}: {missing_clauses}."
        ),
        "create_compliance_checklist": (
            f"Criar checklist simulado de LGPD/compliance para {task_id}."
        ),
        "route_to_human_review": (
            f"Encaminhar {task_id} para revisao humana por juridico/compliance/DPO."
        ),
        "write_audit_record": (
            f"Registrar trilha de auditoria de {task_id} com justificativa e confianca."
        ),
        "add_to_report": (
            f"Adicionar achados de {task_id} ao relatorio auditavel em dry-run."
        ),
        "mock_review_step": (
            f"Simular revisao e documentacao do proximo passo seguro para {task_id}."
        ),
        "mock_documentation_step": (
            f"Simular documentacao de apoio para {task_id}."
        ),
    }
    return descriptions.get(action.kind, f"Registrar acao simulada {action.kind} para {task_id}.")


def _safety_reason(reason: str | None) -> str:
    if reason is None:
        return "sem justificativa registrada"
    translations = {
        "Only dry-run actions are allowed.": "Somente acoes em dry-run sao permitidas.",
        "Mock dry-run action allowed by policy.": "Acao mock em dry-run permitida pela politica.",
        "RegulaGuard dry-run action allowed with audit and human-review guardrails.": (
            "Acao RegulaGuard em dry-run permitida com auditoria e guardrails de revisao humana."
        ),
        "RegulaGuard blocks final legal/contract decisions and real actions.": (
            "RegulaGuard bloqueia decisoes finais juridicas/contratuais e acoes reais."
        ),
    }
    if reason in translations:
        return translations[reason]
    if "is not allowed" in reason:
        return "Tipo de acao nao permitido pela politica de seguranca."
    return reason


def build_report(
    run_id: str,
    mission_input: MissionInput,
    decisions: list[Decision],
    actions: list[Action],
    audit_log_path: str | None = None,
) -> str:
    allowed_count = sum(1 for action in actions if action.safety_status == "allowed")
    blocked_count = sum(1 for action in actions if action.safety_status == "blocked")
    review_count = sum(1 for decision in decisions if decision.requires_human_review)

    lines = [
        f"# Relatorio dry-run: {run_id}",
        "",
        "Solucao: RegulaGuard Agent",
        f"Tema: {mission_input.theme}",
        f"Objetivo: {mission_input.goal}",
        "",
        "## Resumo executivo",
        "",
        f"- Decisoes geradas: {len(decisions)}",
        f"- Acoes geradas: {len(actions)}",
        f"- Acoes permitidas: {allowed_count}",
        f"- Acoes bloqueadas: {blocked_count}",
        f"- Itens encaminhados para revisao humana: {review_count}",
        "- Escopo: triagem regulatoria, LGPD e onboarding contratual simulado.",
        "- Limites: sem contratos reais, sem dados reais, sem parecer juridico final e sem aprovacao ou reprovacao automatica.",
        "",
        "## Itens analisados",
        "",
    ]

    for decision in decisions:
        lines.extend(
            [
                f"### {decision.id} para `{decision.task_id}`",
                "",
                f"- Resumo: {_decision_summary(decision)}",
                f"- Tipo do item: {decision.item_type}",
                f"- Risco regulatorio: {decision.regulatory_risk}",
                f"- Confianca: {decision.confidence:.2f}",
                f"- Revisao humana necessaria: {_format_bool(decision.requires_human_review)}",
                f"- Categorias de dados pessoais: {_format_list(decision.personal_data_detected, 'nenhuma detectada')}",
                f"- Categorias de dados sensiveis: {_format_list(decision.sensitive_data_detected, 'nenhuma detectada')}",
                f"- Dados mascarados: {_format_masked(decision.masked_data)}",
                f"- Documentos ausentes: {_format_list(decision.missing_documents)}",
                f"- Clausulas simuladas ausentes: {_format_list(decision.missing_contract_clauses)}",
                f"- Justificativa da decisao: {_specific_rationale(decision)}",
                f"- Motivos da revisao: {_format_list(decision.review_reasons)}",
                f"- Acoes recomendadas em dry-run: {_format_list(decision.recommended_actions)}",
                "",
            ]
        )

    lines.extend(["", "## Matriz de criterios aplicada", ""])

    lines.extend(
        [
            "| Item | Dados pessoais detectados | Dados sensiveis detectados | Documentos ausentes | Clausulas criticas ausentes | Nivel de confianca | Risco regulatorio | Revisao humana |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for decision in decisions:
        lines.append(
            "| "
            f"{decision.task_id} | "
            f"{_format_list(decision.personal_data_detected)} | "
            f"{_format_list(decision.sensitive_data_detected)} | "
            f"{_format_list(decision.missing_documents)} | "
            f"{_format_list(decision.missing_contract_clauses)} | "
            f"{decision.confidence:.2f} | "
            f"{decision.regulatory_risk} | "
            f"{_format_bool(decision.requires_human_review)} |"
        )

    lines.extend(["", "## Acoes em dry-run", ""])

    for action in actions:
        lines.extend(
            [
                f"- {action.id}: {_action_description(action)}",
                f"  Tipo: {action.kind}",
                f"  Risco: {action.regulatory_risk}",
                f"  Revisao humana: {_format_bool(action.requires_human_review)}",
                f"  Seguranca: {_action_status(action.safety_status)} - {_safety_reason(action.safety_reason)}",
            ]
        )

    lines.extend(
        [
            "",
            "## Guardrails aplicados",
            "",
            "- Nao usar dados reais: a entrada e composta apenas por dados simulados.",
            "- Nao usar contratos reais: as minutas e clausulas sao ficticias.",
            "- Nao tomar decisao juridica, medica ou financeira final.",
            "- Nao aprovar ou reprovar contrato automaticamente.",
            "- Nao executar acoes externas fora do dry-run.",
            "- Encaminhar casos criticos, baixa confianca, dados sensiveis e clausulas criticas ausentes para Revisao humana.",
            "",
            "## Trilha de auditoria",
            "",
            "- Fonte da entrada: JSON local simulado.",
            "- Validacao das decisoes: schemas Pydantic.",
            "- Modo das acoes: somente dry-run.",
            f"- Log estruturado de auditoria: {audit_log_path or 'audit_log.jsonl'}.",
            "- Politica de seguranca: bloqueia acoes reais, pareceres finais e aprovacao/reprovacao automatica de contrato.",
            "- Human-in-the-loop: exigido para risco alto/critico, dados sensiveis, baixa confianca e clausulas criticas ausentes.",
            "",
            "## Limites do agente",
            "",
            "- Este relatorio nao e decisao juridica, medica ou financeira final.",
            "- O agente nao aprova nem reprova contratos automaticamente.",
            "- O agente nao usa contratos reais nem dados pessoais reais.",
            "- Gemini/OpenAI sao opcionais; o fluxo padrao usa mock e deve funcionar sem internet.",
            "",
            "## Melhorias futuras",
            "",
            "- Adicionar matrizes de risco configuraveis aprovadas por juridico/compliance.",
            "- Ampliar biblioteca de clausulas simuladas sem usar contratos proprietarios.",
            "- Adicionar feedback de revisores humanos para calibracao.",
            "- Exportar evidencias para fluxos de auditoria regulada.",
            "",
            "Modo dry-run nao executou alteracoes externas.",
            "",
        ]
    )
    return "\n".join(lines)
