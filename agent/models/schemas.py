from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class MissionTask(BaseModel):
    id: str
    description: str
    priority: Literal["low", "medium", "high"] = "medium"
    title: str | None = None
    sector: str | None = None
    requester_type: str | None = None
    submitted_documents: list[str] = Field(default_factory=list)
    document_type: str | None = None
    personal_data: list[str] = Field(default_factory=list)
    sensitive_data: list[str] = Field(default_factory=list)
    urgency: Literal["low", "medium", "high"] = "medium"
    declared_purpose: str | None = None
    contract_clauses: list[str] = Field(default_factory=list)
    missing_clauses: list[str] = Field(default_factory=list)
    missing_documents: list[str] = Field(default_factory=list)
    confidence_hint: float | None = Field(default=None, ge=0.0, le=1.0)


class MissionInput(BaseModel):
    theme: str
    goal: str
    context: dict[str, Any] = Field(default_factory=dict)
    tasks: list[MissionTask] = Field(default_factory=list)


class Decision(BaseModel):
    id: str
    task_id: str
    summary: str
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)
    item_type: str = "regulatory_triage"
    personal_data_detected: list[str] = Field(default_factory=list)
    sensitive_data_detected: list[str] = Field(default_factory=list)
    masked_data: dict[str, str] = Field(default_factory=dict)
    regulatory_risk: Literal["baixo", "medio", "alto", "critico"] = "baixo"
    missing_documents: list[str] = Field(default_factory=list)
    missing_contract_clauses: list[str] = Field(default_factory=list)
    requires_human_review: bool = False
    review_reasons: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)


class Action(BaseModel):
    id: str
    decision_id: str
    kind: str
    description: str
    dry_run: bool = True
    regulatory_risk: Literal["baixo", "medio", "alto", "critico"] = "baixo"
    requires_human_review: bool = False
    audit_details: dict[str, Any] = Field(default_factory=dict)
    safety_status: Literal["pending", "allowed", "blocked"] = "pending"
    safety_reason: str | None = None


class RunArtifacts(BaseModel):
    run_id: str
    created_at: datetime
    input: MissionInput
    decisions: list[Decision]
    actions: list[Action]
