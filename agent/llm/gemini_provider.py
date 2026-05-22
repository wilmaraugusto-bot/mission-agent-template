from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from agent.llm.base import BaseLLMProvider, LLMProviderError
from agent.models.schemas import Decision, MissionInput


class GeminiLLMProvider(BaseLLMProvider):
    provider = "gemini"

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
        timeout_seconds: int = 20,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._timeout_seconds = timeout_seconds

    def decide(self, mission_input: MissionInput) -> list[dict[str, Any]]:
        if not self._api_key.strip():
            raise LLMProviderError("Gemini API key is required.")

        prompt = self._build_prompt(mission_input)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }
        request = Request(
            url=f"https://generativelanguage.googleapis.com/v1beta/models/{self._model}:generateContent",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-goog-api-key": self._api_key,
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            raise LLMProviderError("Gemini request failed.") from exc

        text = self._extract_text(response_payload)
        return self._parse_decisions(text)

    def _build_prompt(self, mission_input: MissionInput) -> str:
        mission_json = mission_input.model_dump_json(indent=2)
        return (
            "You are the planning layer of a dry-run autonomous agent.\n"
            "Return only a JSON array, without Markdown or commentary.\n"
            "Create exactly one decision for each task in the mission input.\n"
            "Each decision must contain these fields: id, task_id, summary, rationale, confidence, "
            "item_type, personal_data_detected, sensitive_data_detected, masked_data, "
            "regulatory_risk, missing_documents, missing_contract_clauses, "
            "requires_human_review, review_reasons, recommended_actions.\n"
            "Use ids like decision-001, decision-002. Confidence must be a number from 0 to 1.\n\n"
            "Regulatory risk must be one of: baixo, medio, alto, critico.\n"
            "Never approve or reject contracts. Never emit a final legal opinion. "
            "Route high/critical risk, sensitive data, low confidence and critical clause gaps to human review.\n\n"
            f"Mission input:\n{mission_json}"
        )

    def _extract_text(self, payload: dict[str, Any]) -> str:
        try:
            return payload["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError("Gemini response did not include text content.") from exc

    def _parse_decisions(self, text: str) -> list[dict[str, Any]]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
            cleaned = cleaned.removesuffix("```").strip()

        try:
            decisions = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise LLMProviderError("Gemini response was not valid JSON.") from exc

        if not isinstance(decisions, list):
            raise LLMProviderError("Gemini response JSON must be a list.")

        return decisions
