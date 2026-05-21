from __future__ import annotations

from agent.core.safety import SafetyPolicy
from agent.models.schemas import Action


def test_safety_policy_allows_mock_dry_run_action():
    action = Action(
        id="action-001",
        decision_id="decision-001",
        kind="mock_review_step",
        description="Would review a safe step.",
        dry_run=True,
    )

    [result] = SafetyPolicy().apply([action])

    assert result.safety_status == "allowed"
    assert result.safety_reason == "Mock dry-run action allowed by policy."


def test_safety_policy_blocks_non_dry_run_action():
    action = Action(
        id="action-001",
        decision_id="decision-001",
        kind="mock_review_step",
        description="Would mutate an external resource.",
        dry_run=False,
    )

    [result] = SafetyPolicy().apply([action])

    assert result.safety_status == "blocked"
    assert result.safety_reason == "Only dry-run actions are allowed."


def test_safety_policy_blocks_unknown_action_kind():
    action = Action(
        id="action-001",
        decision_id="decision-001",
        kind="external_write",
        description="Would write outside the dry-run scope.",
        dry_run=True,
    )

    [result] = SafetyPolicy().apply([action])

    assert result.safety_status == "blocked"
    assert "not allowed" in result.safety_reason
