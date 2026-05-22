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

    assert decisions_path.exists()
    assert actions_path.exists()
    assert report_path.exists()

    decisions = json.loads(decisions_path.read_text(encoding="utf-8"))
    actions = json.loads(actions_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")

    assert decisions[0]["task_id"] == "task-001"
    assert actions[0]["dry_run"] is True
    assert actions[0]["safety_status"] == "allowed"
    assert "Modo dry-run nao executou alteracoes externas." in report
