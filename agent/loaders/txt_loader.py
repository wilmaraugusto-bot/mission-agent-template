from __future__ import annotations

from pathlib import Path


def load_txt(path: Path) -> tuple[str, list[str]]:
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
        warnings.append("Arquivo TXT continha caracteres invalidos e foi lido com substituicoes.")

    if not text.strip():
        warnings.append("Arquivo TXT vazio ou sem texto util.")

    return text, warnings
