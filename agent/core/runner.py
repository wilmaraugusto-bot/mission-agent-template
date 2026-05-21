from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

from agent.config import Settings
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

        logger.info("Reading mission input from %s", self.settings.input_path)
        mission_input = read_mission_input(self.settings.input_path)

        logger.info("Generating decisions with LLM router")
        decisions = LLMRouter(self.settings).decide(mission_input)

        logger.info("Generating mock actions")
        planned_actions = MockActionPlanner().plan(decisions)

        logger.info("Applying safety policy")
        actions = SafetyPolicy().apply(planned_actions)

        artifacts = RunArtifacts(
            run_id=run_id,
            created_at=datetime.now(timezone.utc),
            input=mission_input,
            decisions=decisions,
            actions=actions,
        )

        write_json(
            run_dir / "decisions.json",
            [decision.model_dump(mode="json") for decision in artifacts.decisions],
        )
        write_json(
            run_dir / "actions.json",
            [action.model_dump(mode="json") for action in artifacts.actions],
        )
        (run_dir / "report.md").write_text(
            build_report(run_id, mission_input, decisions, actions),
            encoding="utf-8",
        )

        logger.info("Dry-run artifacts saved to %s", run_dir)
        return run_dir
