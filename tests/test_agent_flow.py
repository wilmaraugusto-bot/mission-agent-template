from __future__ import annotations

import json

from agent.config import Settings
from agent.core.runner import AgentRunner


def test_agent_flow_creates_expected_artifacts(tmp_path):
    input_path = tmp_path / "sample_input.json"
    runs_dir = tmp_path / "runs"
    input_path.write_text(
        json.dumps(
            {
                "theme": "test-theme",
                "goal": "Validate the dry-run agent flow.",
                "context": {"source": "pytest"},
                "tasks": [
                    {
                        "id": "task-001",
                        "description": "Create a safe mock decision.",
                        "priority": "high",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    settings = Settings(
        llm_provider="mock",
        dry_run=True,
        input_path=input_path,
        runs_dir=runs_dir,
    )

    run_dir = AgentRunner(settings).run()

    decisions_path = run_dir / "decisions.json"
    actions_path = run_dir / "actions.json"
    report_path = run_dir / "report.md"
    audit_log_path = run_dir / "audit_log.jsonl"

    assert decisions_path.exists()
    assert actions_path.exists()
    assert report_path.exists()
    assert audit_log_path.exists()

    decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
    actions = json.loads(actions_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")
    audit_events = [
        json.loads(line)
        for line in audit_log_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert decisions[0]["task_id"] == "task-001"
    assert actions[0]["dry_run"] is True
    assert actions[0]["safety_status"] == "allowed"
    assert "Modo dry-run nao executou alteracoes externas." in report
    assert "audit_log.jsonl" in report

    assert [event["event"] for event in audit_events] == [
        "input_loaded",
        "provider_selected",
        "decisions_generated",
        "actions_generated",
        "policy_applied",
        "artifacts_written",
        "report_generated",
    ]
    assert audit_events[0]["details"]["task_count"] == 1
    assert audit_events[1]["details"] == {
        "configured_provider": "mock",
        "fallback_provider": "mock",
        "status": "ok",
    }
    assert audit_events[2]["details"]["decision_count"] == 1
    assert audit_events[4]["details"]["allowed_action_count"] >= 1

    serialized_audit = audit_log_path.read_text(encoding="utf-8")
    assert "GEMINI_API_KEY" not in serialized_audit
    assert "OPENAI_API_KEY" not in serialized_audit
    assert "Create a safe mock decision." not in serialized_audit
