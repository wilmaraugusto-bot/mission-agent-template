from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AuditLog:
    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        self._events: list[dict[str, Any]] = []

    def record(self, event: str, details: dict[str, Any]) -> None:
        self._events.append(
            {
                "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "run_id": self.run_id,
                "event": event,
                "details": details,
            }
        )

    def write(self, path: Path) -> None:
        lines = [
            json.dumps(event, ensure_ascii=False, sort_keys=True)
            for event in self._events
        ]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
