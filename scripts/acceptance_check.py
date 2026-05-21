from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    "README.md",
    "Dockerfile",
    "docker-compose.yml",
    ".env",
    ".env.example",
    "requirements.txt",
    "data/sample_input.json",
    "docs/challenge_rules.md",
    "docs/theme.md",
]

FORBIDDEN_REAL_KEY_NAMES = {"OPENAI_API_KEY", "GEMINI_API_KEY"}
PLACEHOLDER_VALUES = {
    "",
    "none",
    "null",
    "changeme",
    "change-me",
    "mock",
    "your_api_key_here",
    "your-api-key-here",
    "placeholder",
    "not-set",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_env(content: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def has_required_run_artifacts(runs_dir: Path) -> bool:
    if not runs_dir.exists():
        return False
    for child in runs_dir.iterdir():
        if not child.is_dir():
            continue
        if all((child / name).exists() for name in ("decisions.json", "actions.json", "report.md")):
            return True
    return False


def looks_like_real_secret(value: str) -> bool:
    normalized = value.strip()
    if normalized.lower() in PLACEHOLDER_VALUES:
        return False
    return bool(normalized)


def main() -> int:
    failures: list[str] = []

    for relative_path in REQUIRED_PATHS:
        if not (ROOT / relative_path).exists():
            failures.append(f"Missing required path: {relative_path}")

    env_path = ROOT / ".env"
    env_example_path = ROOT / ".env.example"
    readme_path = ROOT / "README.md"

    env_content = read_text(env_path) if env_path.exists() else ""
    env_example_content = read_text(env_example_path) if env_example_path.exists() else ""
    readme_content = read_text(readme_path).lower() if readme_path.exists() else ""

    if "LLM_PROVIDER=mock" not in env_content:
        failures.append("LLM_PROVIDER=mock not found in .env")
    if "LLM_PROVIDER=mock" not in env_example_content:
        failures.append("LLM_PROVIDER=mock not found in .env.example")
    if "LLM_FALLBACK_PROVIDER=mock" not in env_content:
        failures.append("LLM_FALLBACK_PROVIDER=mock not found in .env")
    if "LLM_FALLBACK_PROVIDER=mock" not in env_example_content:
        failures.append("LLM_FALLBACK_PROVIDER=mock not found in .env.example")

    if "docker compose up --build" not in readme_content:
        failures.append("README.md must include docker compose up --build")
    if "caso de teste" not in readme_content:
        failures.append("README.md must include an explicit test case section")
    if "mock" not in readme_content or "gemini" not in readme_content or "openai" not in readme_content:
        failures.append("README.md must explain mock default and optional Gemini/OpenAI providers")

    env_values = parse_env(env_content)
    env_example_values = parse_env(env_example_content)
    if env_values.get("LLM_PROVIDER", "mock") != "mock":
        failures.append(".env must keep LLM_PROVIDER=mock as the default")
    if env_example_values.get("LLM_PROVIDER", "mock") != "mock":
        failures.append(".env.example must keep LLM_PROVIDER=mock as the documented default")

    if not has_required_run_artifacts(ROOT / "runs"):
        failures.append("No run in runs/ contains decisions.json, actions.json, and report.md")

    for env_name, content in ((".env", env_content), (".env.example", env_example_content)):
        values = parse_env(content)
        for key_name in FORBIDDEN_REAL_KEY_NAMES:
            if looks_like_real_secret(values.get(key_name, "")):
                failures.append(f"{env_name} contains a non-placeholder value for {key_name}")

    if failures:
        print("Acceptance check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Acceptance check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
