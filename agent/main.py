from __future__ import annotations

import logging

from agent.config import load_settings
from agent.core.runner import AgentRunner


def main() -> None:
    settings = load_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    run_dir = AgentRunner(settings).run()
    logging.getLogger(__name__).info("Completed dry-run: %s", run_dir)


if __name__ == "__main__":
    main()
