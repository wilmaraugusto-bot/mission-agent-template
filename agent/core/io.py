from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import TypeAdapter

from agent.models.schemas import MissionInput


def read_mission_input(path: Path) -> MissionInput:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return TypeAdapter(MissionInput).validate_python(raw)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
