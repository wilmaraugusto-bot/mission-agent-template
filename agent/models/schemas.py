from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class MissionTask(BaseModel):
    id: str
    description: str
    priority: Literal["low", "medium", "high"] = "medium"


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


class Action(BaseModel):
    id: str
    decision_id: str
    kind: str
    description: str
    dry_run: bool = True
    safety_status: Literal["pending", "allowed", "blocked"] = "pending"
    safety_reason: str | None = None


class RunArtifacts(BaseModel):
    run_id: str
    created_at: datetime
    input: MissionInput
    decisions: list[Decision]
    actions: list[Action]
