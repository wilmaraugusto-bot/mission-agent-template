from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from agent.llm.base import BaseLLMProvider, LLMProviderError
from agent.models.schemas import Decision, MissionInput


class GeminiLLMProvider(BaseLLMProvider):
    provider = "gemini"
    risk_values = {"baixo", "medio", "alto", "critico"}
    list_fields = {
        "personal_data_detected",
        "sensitive_data_detected",
        "missing_documents",
        "missing_contract_clauses",
        "review_reasons",
        "recommended_actions",
    }

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-3.5-flash",
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
        except HTTPError as exc:
            raise LLMProviderError(self._http_error_message(exc)) from exc
        except URLError as exc:
            reason = self._safe_text(getattr(exc, "reason", exc))
            raise LLMProviderError(f"Gemini network error ({exc.__class__.__name__}): {reason}") from exc
        except TimeoutError as exc:
            raise LLMProviderError("Gemini request timed out.") from exc
        except json.JSONDecodeError as exc:
            raise LLMProviderError("Gemini returned invalid JSON in the HTTP response body.") from exc
        except OSError as exc:
            reason = self._safe_text(exc)
            raise LLMProviderError(f"Gemini transport error ({exc.__class__.__name__}): {reason}") from exc

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
            "Use ids like decision-001, decision-002.\n\n"
            "Strict JSON types required for every decision:\n"
            '- personal_data_detected: array of strings, for example ["nome", "cpf"]. Never boolean.\n'
            '- sensitive_data_detected: array of strings, for example ["saude"]. Never boolean.\n'
            '- masked_data: JSON object mapping categories to masked values, for example '
            '{"nome": "[NOME_MASCARADO]", "cpf": "[CPF_MASCARADO]"}. Never string.\n'
            '- missing_documents: array of strings.\n'
            '- missing_contract_clauses: array of strings.\n'
            '- review_reasons: array of strings.\n'
            '- recommended_actions: array of strings.\n'
            "- requires_human_review: boolean.\n"
            "- confidence: number between 0 and 1.\n"
            '- regulatory_risk: exactly one of "baixo", "medio", "alto", "critico".\n\n'
            "Never approve or reject contracts. Never emit a final legal opinion. "
            "Route high/critical risk, sensitive data, low confidence and critical clause gaps to human review.\n\n"
            f"Mission input:\n{mission_json}"
        )

    def _extract_text(self, payload: dict[str, Any]) -> str:
        try:
            return payload["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMProviderError(
                "Gemini response had an unexpected format: missing candidates[0].content.parts[0].text."
            ) from exc

    def _parse_decisions(self, text: str) -> list[dict[str, Any]]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
            cleaned = cleaned.removesuffix("```").strip()

        try:
            decisions = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise LLMProviderError("Gemini response text was not valid JSON.") from exc

        if not isinstance(decisions, list):
            raise LLMProviderError("Gemini response schema is invalid: expected a JSON list of decisions.")

        return self._normalize_decisions(decisions)

    def _normalize_decisions(self, decisions: list[Any]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for raw_decision in decisions:
            if not isinstance(raw_decision, dict):
                raise LLMProviderError(
                    "Gemini response schema is invalid: each decision must be a JSON object."
                )
            decision = dict(raw_decision)
            for field in self.list_fields:
                decision[field] = self._normalize_list_field(field, decision.get(field))

            decision["masked_data"] = self._normalize_masked_data(decision.get("masked_data"))
            decision["confidence"] = self._normalize_confidence(decision.get("confidence"))

            risk = decision.get("regulatory_risk")
            if risk not in self.risk_values:
                decision["regulatory_risk"] = "alto"
                decision["requires_human_review"] = True
                review_reasons = decision["review_reasons"]
                review_reasons.append(
                    "Risco regulatorio invalido retornado pelo Gemini; normalizado para alto."
                )
            else:
                decision["requires_human_review"] = bool(decision.get("requires_human_review", False))

            normalized.append(decision)
        return normalized

    def _normalize_list_field(self, field: str, value: Any) -> list[str]:
        if value is None or value is False:
            return []
        if value is True:
            if field == "personal_data_detected":
                return ["dados_pessoais_detectados"]
            if field == "sensitive_data_detected":
                return ["dados_sensiveis_detectados"]
            return [field]
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [str(item) for item in value if item is not None]
        return [str(value)]

    def _normalize_masked_data(self, value: Any) -> dict[str, str]:
        if value is None or value is False:
            return {}
        if isinstance(value, dict):
            return {str(key): str(item) for key, item in value.items() if item is not None}
        if isinstance(value, str):
            return {"valor_mascarado": value}
        return {"valor_mascarado": str(value)}

    def _normalize_confidence(self, value: Any) -> float:
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            confidence = 0.0
        return min(1.0, max(0.0, confidence))

    def _http_error_message(self, exc: HTTPError) -> str:
        body = ""
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except OSError:
            body = ""
        body = self._safe_text(body)
        if len(body) > 500:
            body = f"{body[:500]}..."
        if body:
            return f"Gemini HTTP error status={exc.code}: {body}"
        return f"Gemini HTTP error status={exc.code}."

    def _safe_text(self, value: Any) -> str:
        text = str(value)
        if self._api_key:
            text = text.replace(self._api_key, "[REDACTED]")
        return text.replace("\n", " ").strip()
