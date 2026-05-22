from __future__ import annotations

import logging
import json
from urllib.error import HTTPError
from io import BytesIO

from agent.config import Settings, load_settings
from agent.llm.base import LLMProviderError
from agent.llm.gemini_provider import GeminiLLMProvider
from agent.llm.router import LLMRouter
from agent.models.schemas import Decision, MissionInput, MissionTask


def _mission_input() -> MissionInput:
    return MissionInput(
        theme="router-test",
        goal="Validate provider fallback.",
        tasks=[MissionTask(id="task-001", description="Plan safely.")],
    )


def test_load_settings_defaults_to_mock_provider(monkeypatch):
    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("LLM_FALLBACK_PROVIDER", raising=False)
    monkeypatch.delenv("GEMINI_MODEL", raising=False)

    settings = load_settings()

    assert settings.llm_provider == "mock"
    assert settings.llm_fallback_provider == "mock"
    assert settings.gemini_model == "gemini-3.5-flash"


def test_load_settings_reads_gemini_model(monkeypatch):
    monkeypatch.setenv("GEMINI_MODEL", "gemini-test-model")

    settings = load_settings()

    assert settings.gemini_model == "gemini-test-model"


def test_router_uses_mock_by_default():
    settings = Settings(llm_provider="mock")

    decisions = LLMRouter(settings).decide(_mission_input())

    assert decisions[0].task_id == "task-001"
    assert "RegulaGuard triage for task-001" in decisions[0].summary


def test_router_falls_back_to_mock_when_gemini_key_is_empty(caplog):
    settings = Settings(llm_provider="gemini", gemini_api_key="")

    with caplog.at_level(logging.WARNING):
        decisions = LLMRouter(settings).decide(_mission_input())

    assert "RegulaGuard triage for task-001" in decisions[0].summary
    assert "GEMINI_API_KEY" in caplog.text


def test_router_falls_back_to_mock_when_openai_key_is_empty(caplog):
    settings = Settings(llm_provider="openai", openai_api_key="")

    with caplog.at_level(logging.WARNING):
        decisions = LLMRouter(settings).decide(_mission_input())

    assert "RegulaGuard triage for task-001" in decisions[0].summary
    assert "OPENAI_API_KEY" in caplog.text


def test_router_falls_back_to_mock_when_real_provider_fails(caplog):
    def failing_decide(self, mission_input):
        raise LLMProviderError("simulated failure")

    settings = Settings(llm_provider="gemini", gemini_api_key="test-key")

    original_decide = GeminiLLMProvider.decide
    GeminiLLMProvider.decide = failing_decide
    try:
        with caplog.at_level(logging.WARNING):
            decisions = LLMRouter(settings).decide(_mission_input())
    finally:
        GeminiLLMProvider.decide = original_decide

    assert "RegulaGuard triage for task-001" in decisions[0].summary
    assert "falling back to 'mock'" in caplog.text
    assert "test-key" not in caplog.text


def test_gemini_provider_parses_valid_response(monkeypatch):
    class FakeResponse:
        def read(self):
            payload = {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": json.dumps(
                                        [
                                            {
                                                "id": "decision-001",
                                                "task_id": "task-001",
                                                "summary": "Gemini decision",
                                                "rationale": "Generated from mission input.",
                                                "confidence": 0.81,
                                            }
                                        ]
                                    )
                                }
                            ]
                        }
                    }
                ]
            }
            return json.dumps(payload).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

    def fake_urlopen(request, timeout):
        assert timeout == 20
        assert "models/gemini-test-model:generateContent" in request.full_url
        assert request.headers["X-goog-api-key"] == "test-key"
        return FakeResponse()

    monkeypatch.setattr("agent.llm.gemini_provider.urlopen", fake_urlopen)

    decisions = GeminiLLMProvider(
        api_key="test-key",
        model="gemini-test-model",
    ).validated_decisions(_mission_input())

    assert decisions[0].summary == "Gemini decision"
    assert decisions[0].confidence == 0.81


def test_router_logs_sanitized_gemini_error_without_key(caplog, monkeypatch):
    def fake_urlopen(request, timeout):
        raise OSError("network unavailable for test-key")

    monkeypatch.setattr("agent.llm.gemini_provider.urlopen", fake_urlopen)
    settings = Settings(llm_provider="gemini", gemini_api_key="test-key")

    with caplog.at_level(logging.WARNING):
        decisions = LLMRouter(settings).decide(_mission_input())

    assert "RegulaGuard triage for task-001" in decisions[0].summary
    assert "falling back to 'mock'" in caplog.text
    assert "Gemini transport error" in caplog.text
    assert "[REDACTED]" in caplog.text
    assert "test-key" not in caplog.text


def test_gemini_http_error_message_includes_status_and_sanitized_body(monkeypatch):
    class FakeErrorBody(BytesIO):
        def close(self):
            pass

    def fake_urlopen(request, timeout):
        raise HTTPError(
            request.full_url,
            404,
            "Not Found",
            hdrs=None,
            fp=FakeErrorBody(b'{"error":"model not found for test-key"}'),
        )

    monkeypatch.setattr("agent.llm.gemini_provider.urlopen", fake_urlopen)

    try:
        GeminiLLMProvider(api_key="test-key").decide(_mission_input())
    except LLMProviderError as exc:
        message = str(exc)
    else:
        raise AssertionError("Expected LLMProviderError")

    assert "status=404" in message
    assert "model not found" in message
    assert "[REDACTED]" in message
    assert "test-key" not in message


def test_gemini_invalid_schema_error_is_diagnostic(monkeypatch):
    class FakeResponse:
        def read(self):
            payload = {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": json.dumps({"not": "a list"})
                                }
                            ]
                        }
                    }
                ]
            }
            return json.dumps(payload).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return False

    monkeypatch.setattr("agent.llm.gemini_provider.urlopen", lambda request, timeout: FakeResponse())

    try:
        GeminiLLMProvider(api_key="test-key").decide(_mission_input())
    except LLMProviderError as exc:
        assert "schema is invalid" in str(exc)
    else:
        raise AssertionError("Expected LLMProviderError")


def test_gemini_normalizes_boolean_personal_data_to_list():
    provider = GeminiLLMProvider(api_key="test-key")

    [decision] = provider._normalize_decisions(
        [
            {
                "id": "decision-001",
                "task_id": "task-001",
                "summary": "Summary",
                "rationale": "Rationale",
                "confidence": 0.7,
                "personal_data_detected": True,
                "regulatory_risk": "medio",
            }
        ]
    )

    assert decision["personal_data_detected"] == ["dados_pessoais_detectados"]


def test_gemini_normalizes_string_masked_data_to_dict():
    provider = GeminiLLMProvider(api_key="test-key")

    [decision] = provider._normalize_decisions(
        [
            {
                "id": "decision-001",
                "task_id": "task-001",
                "summary": "Summary",
                "rationale": "Rationale",
                "confidence": 0.7,
                "masked_data": "[NOME_MASCARADO]",
                "regulatory_risk": "medio",
            }
        ]
    )

    assert decision["masked_data"] == {"valor_mascarado": "[NOME_MASCARADO]"}


def test_gemini_normalizes_string_missing_contract_clause_to_list():
    provider = GeminiLLMProvider(api_key="test-key")

    [decision] = provider._normalize_decisions(
        [
            {
                "id": "decision-001",
                "task_id": "task-001",
                "summary": "Summary",
                "rationale": "Rationale",
                "confidence": 0.7,
                "missing_contract_clauses": "confidencialidade",
                "regulatory_risk": "medio",
            }
        ]
    )

    assert decision["missing_contract_clauses"] == ["confidencialidade"]


def test_gemini_normalizes_invalid_risk_to_high_and_requires_review():
    provider = GeminiLLMProvider(api_key="test-key")

    [decision] = provider._normalize_decisions(
        [
            {
                "id": "decision-001",
                "task_id": "task-001",
                "summary": "Summary",
                "rationale": "Rationale",
                "confidence": 2,
                "regulatory_risk": "unknown",
                "requires_human_review": False,
            }
        ]
    )

    assert decision["confidence"] == 1.0
    assert decision["regulatory_risk"] == "alto"
    assert decision["requires_human_review"] is True
    assert "normalizado para alto" in decision["review_reasons"][0]


def test_gemini_keeps_correct_response_compatible_with_pydantic():
    provider = GeminiLLMProvider(api_key="test-key")

    [normalized] = provider._normalize_decisions(
        [
            {
                "id": "decision-001",
                "task_id": "task-001",
                "summary": "Summary",
                "rationale": "Rationale",
                "confidence": 0.7,
                "item_type": "minuta_contratual_simulada",
                "personal_data_detected": ["nome", "cpf"],
                "sensitive_data_detected": ["saude"],
                "masked_data": {"nome": "[NOME_MASCARADO]"},
                "regulatory_risk": "alto",
                "missing_documents": ["anexo_lgpd"],
                "missing_contract_clauses": ["retencao_descarte"],
                "requires_human_review": True,
                "review_reasons": ["risco alto"],
                "recommended_actions": ["route_to_human_review"],
            }
        ]
    )

    decision = Decision.model_validate(normalized)

    assert decision.personal_data_detected == ["nome", "cpf"]
    assert decision.masked_data == {"nome": "[NOME_MASCARADO]"}
    assert decision.regulatory_risk == "alto"
