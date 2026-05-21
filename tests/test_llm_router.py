from __future__ import annotations

import logging

from agent.config import Settings, load_settings
from agent.llm.router import LLMRouter
from agent.models.schemas import MissionInput, MissionTask


def _mission_input() -> MissionInput:
    return MissionInput(
        theme="router-test",
        goal="Validate provider fallback.",
        tasks=[MissionTask(id="task-001", description="Plan safely.")],
    )


def test_load_settings_defaults_to_mock_provider(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_FALLBACK_PROVIDER", raising=False)

    settings = load_settings()

    assert settings.llm_provider == "mock"
    assert settings.llm_fallback_provider == "mock"


def test_router_uses_mock_by_default():
    settings = Settings(llm_provider="mock")

    decisions = LLMRouter(settings).decide(_mission_input())

    assert decisions[0].task_id == "task-001"
    assert decisions[0].summary == "Mock decision for task-001"


def test_router_falls_back_to_mock_when_gemini_key_is_empty(caplog):
    settings = Settings(llm_provider="gemini", gemini_api_key="")

    with caplog.at_level(logging.WARNING):
        decisions = LLMRouter(settings).decide(_mission_input())

    assert decisions[0].summary == "Mock decision for task-001"
    assert "GEMINI_API_KEY" in caplog.text


def test_router_falls_back_to_mock_when_openai_key_is_empty(caplog):
    settings = Settings(llm_provider="openai", openai_api_key="")

    with caplog.at_level(logging.WARNING):
        decisions = LLMRouter(settings).decide(_mission_input())

    assert decisions[0].summary == "Mock decision for task-001"
    assert "OPENAI_API_KEY" in caplog.text


def test_router_falls_back_to_mock_when_real_provider_fails(caplog):
    settings = Settings(llm_provider="gemini", gemini_api_key="test-key")

    with caplog.at_level(logging.WARNING):
        decisions = LLMRouter(settings).decide(_mission_input())

    assert decisions[0].summary == "Mock decision for task-001"
    assert "falling back to 'mock'" in caplog.text
    assert "test-key" not in caplog.text
