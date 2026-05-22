from __future__ import annotations

from agent.models.schemas import Action


class SafetyPolicy:
    allowed_kinds = {
        "mock_review_step",
        "mock_documentation_step",
        "mask_sensitive_data",
        "classify_regulatory_risk",
        "request_missing_documents",
        "flag_missing_contract_clauses",
        "create_compliance_checklist",
        "route_to_human_review",
        "write_audit_record",
        "add_to_report",
    }
    prohibited_terms = {
        "approve_contract",
        "reject_contract",
        "final_legal_opinion",
        "emit_final_opinion",
        "execute_external_change",
    }

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

            if self._is_prohibited(action):
                safe_actions.append(
                    action.model_copy(
                        update={
                            "safety_status": "blocked",
                            "safety_reason": (
                                "RegulaGuard blocks final legal/contract decisions and real actions."
                            ),
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

            if self._requires_human_review_but_missing_route(action):
                safe_actions.append(
                    action.model_copy(
                        update={
                            "safety_status": "blocked",
                            "safety_reason": (
                                "High/critical risk, low confidence, sensitive data or critical "
                                "clause gaps require human review."
                            ),
                        }
                    )
                )
                continue

            safe_actions.append(
                action.model_copy(
                    update={
                        "safety_status": "allowed",
                        "safety_reason": self._allowed_reason(action),
                    }
                )
            )
        return safe_actions

    def _is_prohibited(self, action: Action) -> bool:
        haystack = f"{action.kind} {action.description}".lower()
        return any(term in haystack for term in self.prohibited_terms)

    def _requires_human_review_but_missing_route(self, action: Action) -> bool:
        details = action.audit_details
        low_confidence = details.get("confidence", 1.0) < 0.6
        missing_critical_clauses = bool(
            set(details.get("missing_contract_clauses", [])).intersection(
                {
                    "confidencialidade",
                    "retencao_descarte",
                    "finalidade_tratamento",
                    "matriz_responsabilidades",
                }
            )
        )
        review_required = (
            action.regulatory_risk in {"alto", "critico"}
            or action.requires_human_review
            or low_confidence
            or missing_critical_clauses
        )
        if not review_required:
            return False
        return action.kind not in {
            "route_to_human_review",
            "write_audit_record",
            "add_to_report",
            "mask_sensitive_data",
            "flag_missing_contract_clauses",
            "create_compliance_checklist",
            "request_missing_documents",
            "classify_regulatory_risk",
        }

    def _allowed_reason(self, action: Action) -> str:
        if action.kind in {"mock_review_step", "mock_documentation_step"}:
            return "Mock dry-run action allowed by policy."
        return "RegulaGuard dry-run action allowed with audit and human-review guardrails."
