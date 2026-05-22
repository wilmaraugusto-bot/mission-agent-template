from __future__ import annotations

from agent.models.schemas import Action, Decision


class MockActionPlanner:
    def plan(self, decisions: list[Decision]) -> list[Action]:
        actions: list[Action] = []
        counter = 1
        for decision in decisions:
            for kind in decision.recommended_actions or ["write_audit_record", "add_to_report"]:
                actions.append(
                    Action(
                        id=f"action-{counter:03d}",
                        decision_id=decision.id,
                        kind=kind,
                        description=self._description_for(kind, decision),
                        dry_run=True,
                        regulatory_risk=decision.regulatory_risk,
                        requires_human_review=decision.requires_human_review,
                        audit_details={
                            "task_id": decision.task_id,
                            "item_type": decision.item_type,
                            "risk": decision.regulatory_risk,
                            "confidence": decision.confidence,
                            "missing_documents": decision.missing_documents,
                            "missing_contract_clauses": decision.missing_contract_clauses,
                            "review_reasons": decision.review_reasons,
                        },
                    )
                )
                counter += 1
        return actions

    def _description_for(self, kind: str, decision: Decision) -> str:
        descriptions = {
            "mask_sensitive_data": (
                f"Would mask simulated personal/sensitive data for {decision.task_id} "
                "before review or reporting."
            ),
            "classify_regulatory_risk": (
                f"Would classify {decision.task_id} as regulatory risk "
                f"{decision.regulatory_risk}."
            ),
            "request_missing_documents": (
                f"Would request missing simulated documents for {decision.task_id}: "
                f"{', '.join(decision.missing_documents)}."
            ),
            "flag_missing_contract_clauses": (
                f"Would flag missing simulated contract clauses for {decision.task_id}: "
                f"{', '.join(decision.missing_contract_clauses)}."
            ),
            "create_compliance_checklist": (
                f"Would create a LGPD/compliance checklist for {decision.task_id}."
            ),
            "route_to_human_review": (
                f"Would route {decision.task_id} to human review by legal/compliance/DPO."
            ),
            "write_audit_record": (
                f"Would write an audit record for {decision.task_id} with rationale and confidence."
            ),
            "add_to_report": (
                f"Would add {decision.task_id} findings to the auditable dry-run report."
            ),
            "mock_review_step": (
                f"Would review and document the next safe step for {decision.task_id}."
            ),
        }
        return descriptions.get(kind, f"Would execute dry-run action {kind} for {decision.task_id}.")
