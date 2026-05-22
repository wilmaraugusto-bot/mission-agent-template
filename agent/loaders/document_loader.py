from __future__ import annotations

from pathlib import Path
from typing import Any

from agent.loaders.docx_loader import load_docx
from agent.loaders.pdf_loader import load_pdf
from agent.loaders.txt_loader import load_txt


SUPPORTED_LOADERS = {
    ".txt": load_txt,
    ".pdf": load_pdf,
    ".docx": load_docx,
}


def load_document(path: str) -> dict[str, Any]:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    result: dict[str, Any] = {
        "source_file": str(file_path),
        "file_type": suffix.lstrip(".") or "unknown",
        "extracted_text": "",
        "warnings": [],
    }

    if not file_path.exists():
        result["warnings"].append("Arquivo inexistente.")
        return result
    if not file_path.is_file():
        result["warnings"].append("Caminho informado nao e um arquivo.")
        return result

    loader = SUPPORTED_LOADERS.get(suffix)
    if loader is None:
        result["warnings"].append(
            f"Extensao '{suffix or 'sem extensao'}' nao suportada. Use .txt, .pdf ou .docx."
        )
        return result

    extracted_text, warnings = loader(file_path)
    result["extracted_text"] = extracted_text
    result["warnings"].extend(warnings)

    if not extracted_text.strip() and not result["warnings"]:
        result["warnings"].append("Arquivo sem texto extraivel.")

    return result
