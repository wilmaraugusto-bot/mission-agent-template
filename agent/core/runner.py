from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from agent.config import Settings
from agent.core.audit import AuditLog
from agent.core.io import read_mission_input, write_json
from agent.core.report import build_report
from agent.core.safety import SafetyPolicy
from agent.llm.router import LLMRouter
from agent.models.schemas import RunArtifacts
from agent.tools.mock_actions import MockActionPlanner

logger = logging.getLogger(__name__)


class AgentRunner:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def run(self) -> Path:
        if not self.settings.dry_run:
            raise ValueError("This base project only supports DRY_RUN=true.")

        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        run_dir = self.settings.runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        audit_log = AuditLog(run_id)

        logger.info("Reading mission input from %s", self.settings.input_path)
        mission_input = read_mission_input(self.settings.input_path)
        audit_log.record(
            "input_loaded",
            {
                "input_path": str(self.settings.input_path),
                "task_count": len(mission_input.tasks),
                "status": "ok",
            },
        )

        logger.info("Generating decisions with LLM router")
        audit_log.record(
            "provider_selected",
            {
                "configured_provider": self.settings.llm_provider,
                "fallback_provider": self.settings.llm_fallback_provider,
                "status": "ok",
            },
        )
        decisions = LLMRouter(self.settings).decide(mission_input)
        audit_log.record(
            "decisions_generated",
            {
                "decision_count": len(decisions),
                "status": "ok",
            },
        )

        logger.info("Generating mock actions")
        planned_actions = MockActionPlanner().plan(decisions)
        audit_log.record(
            "actions_generated",
            {
                "action_count": len(planned_actions),
                "status": "ok",
            },
        )

        logger.info("Applying safety policy")
        actions = SafetyPolicy().apply(planned_actions)
        allowed_count = sum(1 for action in actions if action.safety_status == "allowed")
        blocked_count = sum(1 for action in actions if action.safety_status == "blocked")
        audit_log.record(
            "policy_applied",
            {
                "action_count": len(actions),
                "allowed_action_count": allowed_count,
                "blocked_action_count": blocked_count,
                "status": "ok",
            },
        )

        artifacts = RunArtifacts(
            run_id=run_id,
            created_at=datetime.now(timezone.utc),
            input=mission_input,
            decisions=decisions,
            actions=actions,
        )

        decisions_path = run_dir / "decisions.json"
        actions_path = run_dir / "actions.json"
        report_path = run_dir / "report.md"
        audit_log_path = run_dir / "audit_log.jsonl"

        write_json(
            decisions_path,
            [decision.model_dump(mode="json") for decision in artifacts.decisions],
        )
        write_json(
            actions_path,
            [action.model_dump(mode="json") for action in artifacts.actions],
        )
        report_path.write_text(
            build_report(run_id, mission_input, decisions, actions, audit_log_path=str(audit_log_path)),
            encoding="utf-8",
        )
        audit_log.record(
            "artifacts_written",
            {
                "decisions_path": str(decisions_path),
                "actions_path": str(actions_path),
                "report_path": str(report_path),
                "audit_log_path": str(audit_log_path),
                "status": "ok",
            },
        )
        audit_log.record(
            "report_generated",
            {
                "report_path": str(report_path),
                "audit_log_path": str(audit_log_path),
                "status": "ok",
            },
        )
        audit_log.write(audit_log_path)

        logger.info("Dry-run artifacts saved to %s", run_dir)
        return run_dir
