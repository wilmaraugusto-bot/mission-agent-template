from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = Field(default="mission-agent-template")
    llm_provider: str = Field(default="mock")
    llm_fallback_provider: str = Field(default="mock")
    gemini_api_key: str = Field(default="")
    openai_api_key: str = Field(default="")
    dry_run: bool = Field(default=True)
    input_path: Path = Field(default=Path("data/sample_input.json"))
    runs_dir: Path = Field(default=Path("runs"))
    log_level: str = Field(default="INFO")


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "mission-agent-template"),
        llm_provider=os.getenv("LLM_PROVIDER", "mock"),
        llm_fallback_provider=os.getenv("LLM_FALLBACK_PROVIDER", "mock"),
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        dry_run=_get_bool("DRY_RUN", True),
        input_path=Path(os.getenv("INPUT_PATH", "data/sample_input.json")),
        runs_dir=Path(os.getenv("RUNS_DIR", "runs")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
